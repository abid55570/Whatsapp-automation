"""Pydantic schemas for purchase invoice endpoints."""
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.gst.validation import is_valid_gstin, normalize_gstin


class PurchaseInvoiceCreate(BaseModel):
    supplier_name: str = Field(..., min_length=1, max_length=200)
    supplier_gstin: str | None = Field(None, max_length=15)
    supplier_state_code: str | None = Field(None, max_length=2)
    bill_number: str = Field(..., min_length=1, max_length=50)
    bill_date: date

    taxable_paise: int = Field(..., ge=0)
    cgst_paise: int = Field(0, ge=0)
    sgst_paise: int = Field(0, ge=0)
    igst_paise: int = Field(0, ge=0)
    cess_paise: int = Field(0, ge=0)
    total_paise: int = Field(..., ge=0)

    category: str | None = Field(None, max_length=100)
    is_capital_goods: bool = False
    is_itc_eligible: bool = True
    notes: str | None = None

    @field_validator("supplier_gstin")
    @classmethod
    def _gstin(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        n = normalize_gstin(v)
        if not is_valid_gstin(n):
            raise ValueError("Invalid supplier GSTIN")
        return n


class PurchaseInvoiceUpdate(BaseModel):
    supplier_name: str | None = Field(None, max_length=200)
    supplier_gstin: str | None = Field(None, max_length=15)
    supplier_state_code: str | None = Field(None, max_length=2)
    bill_number: str | None = Field(None, max_length=50)
    bill_date: date | None = None
    taxable_paise: int | None = Field(None, ge=0)
    cgst_paise: int | None = Field(None, ge=0)
    sgst_paise: int | None = Field(None, ge=0)
    igst_paise: int | None = Field(None, ge=0)
    cess_paise: int | None = Field(None, ge=0)
    total_paise: int | None = Field(None, ge=0)
    category: str | None = Field(None, max_length=100)
    is_capital_goods: bool | None = None
    is_itc_eligible: bool | None = None
    notes: str | None = None
    status: str | None = Field(None, pattern="^(draft|recorded|cancelled)$")

    @field_validator("supplier_gstin")
    @classmethod
    def _gstin(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        n = normalize_gstin(v)
        if not is_valid_gstin(n):
            raise ValueError("Invalid supplier GSTIN")
        return n


class PurchaseInvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    supplier_name: str
    supplier_gstin: str | None
    supplier_state_code: str | None
    bill_number: str
    bill_date: date
    taxable_paise: int
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    total_paise: int
    category: str | None
    is_capital_goods: bool
    is_itc_eligible: bool
    notes: str | None
    status: str
    created_at: datetime


class PaginatedPurchaseInvoices(BaseModel):
    items: list[PurchaseInvoiceResponse]
    total: int
    limit: int
    offset: int
    has_more: bool
