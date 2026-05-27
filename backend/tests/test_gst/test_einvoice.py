"""Tests for IRP e-invoice integration (mocked HTTP)."""
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

import httpx
import pytest

from app.models.enums import GstScheme, InvoiceStatus, InvoiceType
from app.services.gst import einvoice
from app.services.gst.einvoice import (
    EInvoiceError,
    EInvoiceNotApplicable,
    generate_irn,
    is_einvoice_applicable,
)


def _line(**kw):
    base = dict(
        line_number=1, description="Item", hsn_code="1001",
        quantity=Decimal("1"), unit="pc", rate_paise=10000,
        discount_pct=Decimal("0"), gst_rate=18,
        taxable_paise=10000, cgst_paise=900, sgst_paise=900,
        igst_paise=0, cess_paise=0, total_paise=11800,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _inv(**kw):
    base = dict(
        id="id-1", invoice_number="INV-26-0001", invoice_date=date(2026, 5, 1),
        fiscal_year="2026-27",
        cx_name="ACME Pvt Ltd", cx_phone="+919876543210",
        cx_gstin="27AAPFU0939F1ZV", cx_address="Mumbai", cx_state_code="27",
        subtotal_paise=10000, discount_paise=0, taxable_paise=10000,
        cgst_paise=900, sgst_paise=900, igst_paise=0, cess_paise=0,
        round_off_paise=0, total_paise=11800, reverse_charge=False,
        invoice_type=InvoiceType.B2B, lines=[_line()],
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _biz(**kw):
    base = dict(
        name="Sharma Kirana", legal_name="Sharma Kirana LLP",
        gstin="29AAGCB7383J1Z4", gst_state_code="29",
        gst_scheme=GstScheme.REGULAR,
        pan="AAGCB7383J",
        business_address_line1="Shop 5", business_address_line2=None,
        business_city="Bengaluru", business_state="Karnataka",
        business_pincode="560001",
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _patch_settings(monkeypatch):
    monkeypatch.setattr(einvoice.settings, "EINVOICE_USERNAME", "user")
    monkeypatch.setattr(einvoice.settings, "EINVOICE_PASSWORD", "pw")
    monkeypatch.setattr(einvoice.settings, "EINVOICE_CLIENT_ID", "client_id")
    monkeypatch.setattr(einvoice.settings, "EINVOICE_CLIENT_SECRET", "secret")
    monkeypatch.setattr(einvoice.settings, "EINVOICE_GSTIN", "29AAGCB7383J1Z4")
    monkeypatch.setattr(einvoice.settings, "EINVOICE_BASE", "https://sandbox.test")
    einvoice.clear_token_cache()


# ============================================================
# Applicability
# ============================================================


class TestApplicability:
    def test_b2b_regular(self):
        assert is_einvoice_applicable(_biz(), _inv(invoice_type=InvoiceType.B2B)) is True

    def test_b2c_not_applicable(self):
        assert is_einvoice_applicable(_biz(), _inv(invoice_type=InvoiceType.B2C)) is False

    def test_composition_not_applicable(self):
        assert is_einvoice_applicable(
            _biz(gst_scheme=GstScheme.COMPOSITION), _inv()
        ) is False

    def test_unregistered_not_applicable(self):
        assert is_einvoice_applicable(
            _biz(gst_scheme=GstScheme.UNREGISTERED, gstin=None), _inv()
        ) is False

    def test_export_applicable(self):
        assert is_einvoice_applicable(_biz(), _inv(invoice_type=InvoiceType.EXPORT)) is True


# ============================================================
# Generate IRN
# ============================================================


class TestGenerateIRN:
    async def test_missing_credentials_raises(self, monkeypatch):
        # Ensure all creds empty
        monkeypatch.setattr(einvoice.settings, "EINVOICE_USERNAME", "")
        monkeypatch.setattr(einvoice.settings, "EINVOICE_GSTIN", "")
        einvoice.clear_token_cache()
        with pytest.raises(EInvoiceError, match="not configured"):
            await generate_irn(_biz(), _inv())

    async def test_b2c_raises_not_applicable(self, monkeypatch):
        _patch_settings(monkeypatch)
        with pytest.raises(EInvoiceNotApplicable):
            await generate_irn(_biz(), _inv(invoice_type=InvoiceType.B2C))

    async def test_successful_round_trip(self, monkeypatch):
        _patch_settings(monkeypatch)

        # Mock IRP responses: 1st call = auth, 2nd = invoice submission
        call_count = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            call_count["n"] += 1
            if "auth" in request.url.path:
                return httpx.Response(
                    200,
                    json={"Data": {"AuthToken": "TOKEN123", "TokenExpiry": "..."}},
                )
            # Invoice submission
            return httpx.Response(
                200,
                json={
                    "Status": 1,
                    "Data": {
                        "Irn": "abc123def456",
                        "SignedQRCode": "QRPAYLOAD",
                        "SignedInvoice": "SIGNED",
                        "AckNo": "112324567",
                        "AckDt": "2026-05-20 11:00:00",
                    },
                },
            )

        transport = httpx.MockTransport(handler)
        result = await generate_irn(_biz(), _inv(), transport=transport)
        assert result["irn"] == "abc123def456"
        assert result["signed_qr_code"] == "QRPAYLOAD"
        assert call_count["n"] == 2

    async def test_token_cached_across_calls(self, monkeypatch):
        _patch_settings(monkeypatch)

        auth_calls = {"n": 0}

        def handler(request: httpx.Request) -> httpx.Response:
            if "auth" in request.url.path:
                auth_calls["n"] += 1
                return httpx.Response(
                    200, json={"Data": {"AuthToken": "CACHED_TOKEN"}}
                )
            return httpx.Response(
                200,
                json={"Data": {"Irn": "irn1", "SignedQRCode": "QR"}},
            )

        transport = httpx.MockTransport(handler)
        await generate_irn(_biz(), _inv(), transport=transport)
        await generate_irn(_biz(), _inv(invoice_number="INV-26-0002"), transport=transport)
        assert auth_calls["n"] == 1  # token reused

    async def test_irp_error_response(self, monkeypatch):
        _patch_settings(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            if "auth" in request.url.path:
                return httpx.Response(200, json={"Data": {"AuthToken": "T"}})
            return httpx.Response(
                200,
                json={
                    "Status": 0,
                    "ErrorDetails": [
                        {"ErrorCode": "2150", "ErrorMessage": "Invoice already exists"}
                    ],
                },
            )

        transport = httpx.MockTransport(handler)
        with pytest.raises(EInvoiceError, match="did not return an IRN"):
            await generate_irn(_biz(), _inv(), transport=transport)

    async def test_auth_http_failure(self, monkeypatch):
        _patch_settings(monkeypatch)

        def handler(request: httpx.Request) -> httpx.Response:
            return httpx.Response(401, json={"error": "bad creds"})

        transport = httpx.MockTransport(handler)
        with pytest.raises(EInvoiceError, match="auth failed"):
            await generate_irn(_biz(), _inv(), transport=transport)


# ============================================================
# Payload builder
# ============================================================


class TestPayloadBuilder:
    def test_basic_payload(self):
        payload = einvoice._build_irn_payload(_biz(), _inv())
        assert payload["Version"] == "1.1"
        assert payload["TranDtls"]["SupTyp"] == "B2B"
        assert payload["DocDtls"]["No"] == "INV-26-0001"
        assert payload["SellerDtls"]["Gstin"] == "29AAGCB7383J1Z4"
        assert payload["BuyerDtls"]["Gstin"] == "27AAPFU0939F1ZV"
        assert payload["ValDtls"]["TotInvVal"] == 118.0

    def test_unregistered_buyer_uses_urp(self):
        payload = einvoice._build_irn_payload(_biz(), _inv(cx_gstin=None))
        assert payload["BuyerDtls"]["Gstin"] == "URP"
        assert payload["TranDtls"]["SupTyp"] == "EXPWP"

    def test_line_items_present(self):
        payload = einvoice._build_irn_payload(_biz(), _inv())
        assert len(payload["ItemList"]) == 1
        item = payload["ItemList"][0]
        assert item["HsnCd"] == "1001"
        assert item["AssAmt"] == 100.0  # taxable
        assert item["GstRt"] == 18.0
