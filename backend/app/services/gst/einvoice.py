"""e-invoice (IRN) integration with the GST Invoice Registration Portal (IRP).

Mandatory for businesses with FY turnover > ₹5 crore (as of 2024). Process:
  1. Generate invoice locally (already done by `service.create_invoice`).
  2. Build the schema-compliant payload.
  3. Authenticate to IRP (JWT token, 6-hour TTL — cache it).
  4. POST /eivital/v1.04/Invoice → returns IRN + signed QR code.
  5. Persist IRN + QR back on the Invoice row → render on PDF.

Sandbox: https://einv-apisandbox.nic.in (manual test creds)
Production: https://einvoice1.gst.gov.in (requires platform GSTIN onboarding)

This module is intentionally defensive — it raises clear errors if credentials
aren't configured, and ALL HTTP work is mockable for tests via the same
httpx transport pattern used by `services.payments.razorpay_client`.
"""
from __future__ import annotations

import json
import logging
import time
from typing import TYPE_CHECKING, Any

import httpx

from app.core.config import settings
from app.services.gst.state_codes import is_valid_state_code
from app.services.gst.validation import gstin_state_code, is_valid_gstin

if TYPE_CHECKING:
    from app.models import Business, Invoice

logger = logging.getLogger(__name__)


class EInvoiceError(Exception):
    """Failed to generate or fetch an IRN."""


class EInvoiceNotApplicable(Exception):
    """e-invoice is not required (composition / unregistered / under threshold)."""


# In-memory token cache; reset per process. For multi-replica, use Redis.
_TOKEN_CACHE: dict[str, dict[str, Any]] = {}
_TOKEN_TTL_SECONDS = 5 * 3600   # IRP tokens last 6h; refresh after 5h


# ============================================================
# Eligibility check
# ============================================================


def is_einvoice_applicable(business: "Business", invoice: "Invoice") -> bool:
    """Return True iff this invoice MUST have an IRN.

    Conditions (per latest CBIC notification):
      - Business is GST-regular (not composition / unregistered)
      - Annual turnover > ₹5 crore (caller verifies; we don't track turnover here)
      - Invoice is B2B, exports, or SEZ (not B2C)

    NOTE: Caller should determine turnover threshold separately and only call
    this when applicable. Here we just check the invoice-side conditions.
    """
    scheme = getattr(business, "gst_scheme", None)
    scheme_val = scheme.value if scheme and hasattr(scheme, "value") else str(scheme)
    if scheme_val != "regular":
        return False
    if not business.gstin:
        return False
    # Only B2B + exports require IRN; B2C is exempt
    inv_type = getattr(invoice, "invoice_type", None)
    type_val = inv_type.value if inv_type and hasattr(inv_type, "value") else str(inv_type)
    return type_val in ("b2b", "export")


# ============================================================
# Authentication
# ============================================================


def _cache_key() -> str:
    """Token cache key that includes username + client_id so rotation invalidates."""
    return f"{settings.EINVOICE_GSTIN}|{settings.EINVOICE_USERNAME}|{settings.EINVOICE_CLIENT_ID}"


async def _get_auth_token(
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> str:
    """Fetch (or reuse cached) JWT auth token from IRP."""
    key = _cache_key()
    cached = _TOKEN_CACHE.get(key)
    if cached and (time.time() - cached["fetched_at"]) < _TOKEN_TTL_SECONDS:
        return cached["token"]

    if not all([
        settings.EINVOICE_USERNAME, settings.EINVOICE_PASSWORD,
        settings.EINVOICE_CLIENT_ID, settings.EINVOICE_CLIENT_SECRET,
        settings.EINVOICE_GSTIN,
    ]):
        raise EInvoiceError(
            "IRP credentials not configured. Set EINVOICE_USERNAME, "
            "EINVOICE_PASSWORD, EINVOICE_CLIENT_ID, EINVOICE_CLIENT_SECRET, "
            "EINVOICE_GSTIN in env."
        )

    url = f"{settings.EINVOICE_BASE.rstrip('/')}/eivital/v1.04/auth"
    payload = {
        "UserName": settings.EINVOICE_USERNAME,
        "Password": settings.EINVOICE_PASSWORD,
        "AppKey": settings.EINVOICE_CLIENT_ID,
        "ForceRefreshAccessToken": False,
    }
    headers = {
        "client_id": settings.EINVOICE_CLIENT_ID,
        "client_secret": settings.EINVOICE_CLIENT_SECRET,
        "gstin": settings.EINVOICE_GSTIN,
        "Content-Type": "application/json",
    }
    kwargs: dict[str, Any] = {"timeout": 25.0}
    if transport is not None:
        kwargs["transport"] = transport

    async with httpx.AsyncClient(**kwargs) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EInvoiceError(
                f"IRP auth failed {exc.response.status_code}: {exc.response.text[:200]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise EInvoiceError(f"IRP auth HTTP error: {exc}") from exc

    body = resp.json()
    token = body.get("Data", {}).get("AuthToken")
    if not token:
        raise EInvoiceError(f"No AuthToken in IRP response: {body}")

    _TOKEN_CACHE[key] = {"token": token, "fetched_at": time.time()}
    return token


def clear_token_cache() -> None:
    """Test helper — force re-auth on next call."""
    _TOKEN_CACHE.clear()


# ============================================================
# Payload builder
# ============================================================


def _build_irn_payload(business: "Business", invoice: "Invoice") -> dict[str, Any]:
    """Construct the JSON payload per IRP Schema v1.1.

    https://einvoice1.gst.gov.in/Others/EInvoiceSchemaJSON
    """
    seller_state = (
        business.gst_state_code
        or (gstin_state_code(business.gstin or "") or "00")
    )

    # Exports → buyer Pos = "96" (foreign / outside India) per IRP schema
    is_export = not invoice.cx_gstin
    if is_export:
        buyer_state = "96"
        supply_type = "EXPWP"   # Export With Payment (or EXPWOP — caller can override)
    else:
        buyer_state = invoice.cx_state_code or gstin_state_code(invoice.cx_gstin or "") or seller_state
        supply_type = "B2B"

    transaction_type = "1"  # 1 = invoice

    items = []
    for line in invoice.lines:
        items.append({
            "SlNo": str(line.line_number),
            "PrdDesc": line.description[:300],
            "IsServc": "Y" if line.unit in ("hr", "service") else "N",
            "HsnCd": line.hsn_code or "9999",
            "Qty": float(line.quantity),
            "Unit": (line.unit or "OTH").upper()[:3],
            "UnitPrice": round(line.rate_paise / 100, 3),
            "TotAmt": round((line.rate_paise * float(line.quantity)) / 100, 2),
            "Discount": 0,
            "AssAmt": round(line.taxable_paise / 100, 2),
            "GstRt": float(line.gst_rate),
            "IgstAmt": round(line.igst_paise / 100, 2),
            "CgstAmt": round(line.cgst_paise / 100, 2),
            "SgstAmt": round(line.sgst_paise / 100, 2),
            "CesAmt": round(line.cess_paise / 100, 2),
            "TotItemVal": round(line.total_paise / 100, 2),
        })

    return {
        "Version": "1.1",
        "TranDtls": {
            "TaxSch": "GST",
            "SupTyp": supply_type,
            "RegRev": "Y" if invoice.reverse_charge else "N",
            "IgstOnIntra": "N",
        },
        "DocDtls": {
            "Typ": "INV",
            "No": invoice.invoice_number,
            "Dt": invoice.invoice_date.strftime("%d/%m/%Y"),
        },
        "SellerDtls": {
            "Gstin": business.gstin or "",
            "LglNm": (business.legal_name or business.name)[:100],
            "Addr1": (business.business_address_line1 or "—")[:100],
            "Loc": (business.business_city or "—")[:50],
            "Pin": int(business.business_pincode) if business.business_pincode else 0,
            "Stcd": seller_state,
        },
        "BuyerDtls": {
            "Gstin": invoice.cx_gstin or "URP",   # URP = Unregistered
            "LglNm": (invoice.cx_name or "Cash Customer")[:100],
            "Pos": buyer_state,
            "Addr1": (invoice.cx_address or "—")[:100],
            "Loc": "—",
            "Pin": 0,
            "Stcd": buyer_state,
        },
        "ItemList": items,
        "ValDtls": {
            "AssVal": round(invoice.taxable_paise / 100, 2),
            "CgstVal": round(invoice.cgst_paise / 100, 2),
            "SgstVal": round(invoice.sgst_paise / 100, 2),
            "IgstVal": round(invoice.igst_paise / 100, 2),
            "CesVal": round(invoice.cess_paise / 100, 2),
            "RndOffAmt": round(invoice.round_off_paise / 100, 2),
            "TotInvVal": round(invoice.total_paise / 100, 2),
        },
    }


# ============================================================
# Generate IRN
# ============================================================


async def generate_irn(
    business: "Business",
    invoice: "Invoice",
    *,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, str]:
    """Submit an invoice to IRP → receive IRN + signed QR code.

    Returns dict with keys: irn, signed_qr_code, ack_no, ack_dt.
    Raises EInvoiceError on failure or EInvoiceNotApplicable for ineligible.
    """
    if not is_einvoice_applicable(business, invoice):
        raise EInvoiceNotApplicable(
            f"Invoice {invoice.invoice_number} not eligible for IRN "
            "(composition / B2C / no GSTIN)"
        )
    if not is_valid_gstin(business.gstin):
        raise EInvoiceError("Seller GSTIN missing or invalid")

    seller_state = business.gst_state_code or gstin_state_code(business.gstin or "")
    if not is_valid_state_code(seller_state):
        raise EInvoiceError(f"Seller state code {seller_state!r} not recognised")

    token = await _get_auth_token(transport=transport)
    payload = _build_irn_payload(business, invoice)

    url = f"{settings.EINVOICE_BASE.rstrip('/')}/eicore/v1.03/Invoice"
    headers = {
        "client_id": settings.EINVOICE_CLIENT_ID,
        "client_secret": settings.EINVOICE_CLIENT_SECRET,
        "gstin": settings.EINVOICE_GSTIN,
        "authtoken": token,
        "user_name": settings.EINVOICE_USERNAME,
        "Content-Type": "application/json",
    }

    kwargs: dict[str, Any] = {"timeout": 25.0}
    if transport is not None:
        kwargs["transport"] = transport

    async with httpx.AsyncClient(**kwargs) as client:
        try:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise EInvoiceError(
                f"IRP rejected invoice {invoice.invoice_number}: "
                f"{exc.response.status_code} — {exc.response.text[:400]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise EInvoiceError(f"IRP HTTP error: {exc}") from exc

    body = resp.json()
    data = body.get("Data", {}) if isinstance(body, dict) else {}
    irn = data.get("Irn")
    if not irn:
        # IRP returns ErrorDetails on validation failure
        err = body.get("ErrorDetails") or body
        raise EInvoiceError(f"IRP did not return an IRN: {json.dumps(err)[:400]}")

    return {
        "irn": irn,
        "signed_qr_code": data.get("SignedQRCode", ""),
        "signed_invoice": data.get("SignedInvoice", ""),
        "ack_no": str(data.get("AckNo", "")),
        "ack_dt": data.get("AckDt", ""),
    }
