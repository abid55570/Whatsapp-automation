"""Pydantic schemas for invoice endpoints."""
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.gst.validation import (
    is_valid_gstin,
    is_valid_hsn_or_sac,
    normalize_gstin,
)


# ============================================================
# Input — create invoice
# ============================================================


class InvoiceLineCreate(BaseModel):
    description: str = Field(..., min_length=1, max_length=500)
    hsn_code: str | None = Field(None, max_length=8)
    quantity: Decimal = Field(..., gt=0)
    unit: str = Field("pc", max_length=10)
    rate_paise: int = Field(..., ge=0)
    discount_pct: float = Field(0.0, ge=0, le=100)
    gst_rate: int = Field(0)

    @field_validator("gst_rate")
    @classmethod
    def _rate(cls, v: int) -> int:
        if v not in (0, 5, 12, 18, 28):
            raise ValueError("gst_rate must be one of 0/5/12/18/28")
        return v

    @field_validator("hsn_code")
    @classmethod
    def _hsn(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not is_valid_hsn_or_sac(v):
            raise ValueError("hsn_code must be 2-8 digits (HSN) or 6 digits starting 99 (SAC)")
        return v.strip()


class InvoiceCreate(BaseModel):
    """Owner-driven create body."""

    invoice_date: date | None = None     # defaults to today
    cx_name: str | None = Field(None, max_length=200)
    cx_phone: str | None = Field(None, max_length=20)
    cx_gstin: str | None = Field(None, max_length=15)
    cx_address: str | None = None
    cx_state_code: str | None = Field(None, max_length=2)
    place_of_supply: str | None = Field(None, max_length=100)
    reverse_charge: bool = False
    notes: str | None = None
    lines: list[InvoiceLineCreate] = Field(..., min_length=1, max_length=100)
    # If true, issue immediately (status=ISSUED). Else stays DRAFT.
    issue_now: bool = True

    @field_validator("cx_gstin")
    @classmethod
    def _gstin(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        n = normalize_gstin(v)
        if not is_valid_gstin(n):
            raise ValueError("Invalid GSTIN — check format + checksum")
        return n


class InvoiceCancelRequest(BaseModel):
    reason: str = Field(..., min_length=1, max_length=500)


class InvoiceShareRequest(BaseModel):
    # Optional override; defaults to invoice.cx_phone
    to_phone: str | None = Field(None, max_length=20)


# ============================================================
# Output
# ============================================================


class InvoiceLineRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    line_number: int
    description: str
    hsn_code: str | None
    quantity: Decimal
    unit: str
    rate_paise: int
    discount_pct: float
    gst_rate: int
    taxable_paise: int
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    total_paise: int


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    order_id: UUID | None = None
    contact_id: UUID | None = None
    invoice_number: str
    invoice_date: date
    fiscal_year: str

    cx_name: str | None
    cx_phone: str | None
    cx_gstin: str | None
    cx_address: str | None
    cx_state_code: str | None

    subtotal_paise: int
    discount_paise: int
    taxable_paise: int
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    round_off_paise: int
    total_paise: int

    place_of_supply: str | None
    reverse_charge: bool
    invoice_type: str
    notes: str | None

    status: str
    issued_at: datetime | None
    paid_at: datetime | None
    cancelled_at: datetime | None
    cancellation_reason: str | None

    pdf_url: str | None
    razorpay_payment_link: str | None
    irn: str | None

    created_at: datetime
    lines: list[InvoiceLineRow] = []


class PaginatedInvoices(BaseModel):
    items: list[InvoiceResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


# ============================================================
# GST settings
# ============================================================


class GstSettingsUpdate(BaseModel):
    gstin: str | None = Field(None, max_length=15)
    gst_scheme: str | None = Field(None, pattern="^(unregistered|regular|composition)$")
    gst_composition_rate: int | None = Field(None, ge=1, le=6)
    legal_name: str | None = Field(None, max_length=200)
    pan: str | None = Field(None, max_length=10)
    business_address_line1: str | None = Field(None, max_length=200)
    business_address_line2: str | None = Field(None, max_length=200)
    business_city: str | None = Field(None, max_length=100)
    business_state: str | None = Field(None, max_length=100)
    business_pincode: str | None = Field(None, max_length=6)
    invoice_prefix: str | None = Field(None, max_length=6)

    @field_validator("gstin")
    @classmethod
    def _gstin(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        n = normalize_gstin(v)
        if not is_valid_gstin(n):
            raise ValueError("Invalid GSTIN — check format + checksum")
        return n


class GstSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gstin: str | None
    gst_state_code: str | None
    gst_scheme: str
    gst_composition_rate: int | None
    legal_name: str | None
    pan: str | None
    business_address_line1: str | None
    business_address_line2: str | None
    business_city: str | None
    business_state: str | None
    business_pincode: str | None
    invoice_prefix: str
    invoice_seq: int
    current_invoice_fy: str | None
    tax_pack_enabled: bool
