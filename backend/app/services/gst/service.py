"""Invoice creation + state transitions — the orchestration layer.

Pure functions / async DB operations live here so endpoints stay thin.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Business, Contact, Invoice, InvoiceLine, Order
from app.models.enums import InvoiceStatus, InvoiceType
from app.services.gst.calculator import (
    LineInput,
    compute_invoice_totals,
    is_interstate,
)
from app.services.gst.invoice_number import next_invoice_number
from app.services.gst.validation import gstin_state_code

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# B2C invoice value above which the invoice goes in GSTR-1 "B2CL" section
_B2CL_THRESHOLD_PAISE = 2_50_000_00   # ₹2.5 lakh


def determine_invoice_type(
    *,
    cx_gstin: str | None,
    cx_state_code: str | None,
    seller_state_code: str | None,
    total_paise: int,
    scheme: str,
) -> InvoiceType:
    """Classify an invoice for GST reporting purposes."""
    if scheme == "composition":
        return InvoiceType.BILL_OF_SUPPLY
    if cx_gstin:
        return InvoiceType.B2B
    interstate = (
        seller_state_code is not None
        and cx_state_code is not None
        and seller_state_code[:2] != cx_state_code[:2]
    )
    if interstate and total_paise >= _B2CL_THRESHOLD_PAISE:
        return InvoiceType.B2C_LARGE
    return InvoiceType.B2C


async def create_invoice(
    db: AsyncSession,
    *,
    business: Business,
    lines_input: list[dict],
    cx_name: str | None = None,
    cx_phone: str | None = None,
    cx_gstin: str | None = None,
    cx_address: str | None = None,
    cx_state_code: str | None = None,
    place_of_supply: str | None = None,
    reverse_charge: bool = False,
    notes: str | None = None,
    invoice_date_override: date | None = None,
    issue_now: bool = True,
    contact: Contact | None = None,
    order: Order | None = None,
) -> Invoice:
    """Create + persist a new Invoice with computed taxes.

    `lines_input` is a list of dicts with keys matching InvoiceLineCreate.
    The function:
      1. Reserves the next FY-sequential invoice number.
      2. Computes per-line tax + invoice totals.
      3. Persists Invoice + InvoiceLine rows in one transaction.
      4. Optionally flips status to ISSUED with timestamp.
    """
    if not lines_input:
        raise ValueError("Invoice must have at least one line")

    invoice_date = invoice_date_override or datetime.now(timezone.utc).date()
    seller_state = (
        business.gst_state_code
        or (gstin_state_code(business.gstin) if business.gstin else None)
    )

    # Infer buyer state from cx_gstin if not explicit
    buyer_state = cx_state_code or (gstin_state_code(cx_gstin) if cx_gstin else None)

    # Composition-scheme businesses can't collect tax — force every line to 0%.
    scheme_raw = (
        business.gst_scheme.value
        if hasattr(business.gst_scheme, "value")
        else str(business.gst_scheme)
    )
    if scheme_raw == "composition":
        for item in lines_input:
            item["gst_rate"] = 0

    # Convert input dicts to LineInput for the calculator
    calc_lines = [
        LineInput(
            quantity=Decimal(str(item["quantity"])),
            unit_price_paise=int(item["rate_paise"]),
            discount_pct=float(item.get("discount_pct", 0.0)),
            gst_rate=int(item.get("gst_rate", 0)),
        )
        for item in lines_input
    ]
    line_taxes, totals = compute_invoice_totals(
        calc_lines,
        seller_state_code=seller_state,
        buyer_state_code=buyer_state,
        round_to_rupee=True,
    )

    # Reserve invoice number — acquire row-level lock to prevent concurrent
    # invoice_seq increments racing for the same number.
    locked = (
        await db.execute(
            select(Business).where(Business.id == business.id).with_for_update()
        )
    ).scalar_one()
    invoice_number, _seq, fiscal_year = next_invoice_number(
        locked, invoice_date=invoice_date
    )
    business = locked   # use the row-locked instance going forward

    scheme = scheme_raw
    invoice_type = determine_invoice_type(
        cx_gstin=cx_gstin,
        cx_state_code=buyer_state,
        seller_state_code=seller_state,
        total_paise=totals.total_paise,
        scheme=scheme,
    )

    now = datetime.now(timezone.utc)
    invoice = Invoice(
        business_id=business.id,
        order_id=order.id if order else None,
        contact_id=contact.id if contact else None,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        fiscal_year=fiscal_year,
        cx_name=cx_name or (contact.name if contact else None),
        cx_phone=cx_phone or (contact.whatsapp_phone if contact else None),
        cx_gstin=cx_gstin,
        cx_address=cx_address,
        cx_state_code=buyer_state,
        subtotal_paise=totals.subtotal_paise,
        discount_paise=totals.discount_paise,
        taxable_paise=totals.taxable_paise,
        cgst_paise=totals.cgst_paise,
        sgst_paise=totals.sgst_paise,
        igst_paise=totals.igst_paise,
        cess_paise=totals.cess_paise,
        round_off_paise=totals.round_off_paise,
        total_paise=totals.total_paise,
        place_of_supply=place_of_supply,
        reverse_charge=reverse_charge,
        invoice_type=invoice_type,
        notes=notes,
        status=InvoiceStatus.ISSUED if issue_now else InvoiceStatus.DRAFT,
        issued_at=now if issue_now else None,
    )
    db.add(invoice)
    await db.flush()  # populate invoice.id

    for idx, (item, line_tax) in enumerate(zip(lines_input, line_taxes, strict=True), start=1):
        db.add(
            InvoiceLine(
                invoice_id=invoice.id,
                line_number=idx,
                description=item["description"],
                hsn_code=item.get("hsn_code"),
                quantity=Decimal(str(item["quantity"])),
                unit=item.get("unit", "pc"),
                rate_paise=int(item["rate_paise"]),
                discount_pct=Decimal(str(item.get("discount_pct", 0))),
                gst_rate=int(item.get("gst_rate", 0)),
                taxable_paise=line_tax.taxable_paise,
                cgst_paise=line_tax.cgst_paise,
                sgst_paise=line_tax.sgst_paise,
                igst_paise=line_tax.igst_paise,
                cess_paise=line_tax.cess_paise,
                total_paise=line_tax.total_paise,
            )
        )

    await db.commit()
    await db.refresh(invoice, attribute_names=["status", "issued_at", "id"])
    # Reload with lines for response building
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice.id)
        .options(selectinload(Invoice.lines))
    )
    invoice = (await db.execute(stmt)).scalar_one()
    logger.info(
        "Created invoice %s for business=%s total=%d type=%s",
        invoice.invoice_number, business.id, invoice.total_paise, invoice_type.value,
    )
    return invoice


async def cancel_invoice(
    db: AsyncSession, invoice: Invoice, reason: str
) -> Invoice:
    """Cancel an already-issued invoice. Number is NOT reused."""
    if invoice.status == InvoiceStatus.CANCELLED:
        return invoice
    if invoice.status not in (InvoiceStatus.ISSUED, InvoiceStatus.PAID, InvoiceStatus.DRAFT):
        raise ValueError(f"Cannot cancel invoice in status {invoice.status}")
    invoice.status = InvoiceStatus.CANCELLED
    invoice.cancelled_at = datetime.now(timezone.utc)
    invoice.cancellation_reason = reason
    await db.commit()
    await db.refresh(invoice, attribute_names=["status", "cancelled_at", "cancellation_reason"])
    logger.warning("Cancelled invoice %s — %s", invoice.invoice_number, reason)
    return invoice


async def mark_invoice_paid(
    db: AsyncSession, invoice: Invoice, razorpay_payment_id: str | None = None
) -> Invoice:
    """Flip invoice to PAID. Idempotent."""
    if invoice.status == InvoiceStatus.PAID:
        return invoice
    invoice.status = InvoiceStatus.PAID
    invoice.paid_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(invoice, attribute_names=["status", "paid_at"])
    return invoice


async def attach_pdf_to_invoice(
    db: AsyncSession,
    invoice: Invoice,
    object_key: str,
    pdf_url: str,
) -> Invoice:
    """Persist R2 object key + signed URL after PDF generation."""
    invoice.pdf_object_key = object_key
    invoice.pdf_url = pdf_url
    await db.commit()
    await db.refresh(invoice, attribute_names=["pdf_object_key", "pdf_url"])
    return invoice
