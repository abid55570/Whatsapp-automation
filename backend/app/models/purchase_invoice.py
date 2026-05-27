"""PurchaseInvoice — inward supplies for ITC claim (V2 feature).

Owner enters supplier bills here so we can:
  - Compute ITC available
  - Generate purchase register for GSTR-3B
  - Reconcile against GSTR-2A (supplier-side data from GST portal)
"""
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import PurchaseInvoiceStatus

if TYPE_CHECKING:
    from app.models.business import Business


class PurchaseInvoice(Base, UUIDMixin, TimestampMixin):
    """A supplier's invoice the business received (B2B inward)."""

    __tablename__ = "purchase_invoices"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    # ---------- Supplier details (denormalized) ----------
    supplier_name: Mapped[str] = mapped_column(String(200), nullable=False)
    supplier_gstin: Mapped[str | None] = mapped_column(
        String(15), index=True, nullable=True
    )
    supplier_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # ---------- Bill identification ----------
    bill_number: Mapped[str] = mapped_column(String(50), nullable=False)
    bill_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)

    # ---------- Amounts (paise) ----------
    taxable_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cgst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sgst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    igst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cess_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ---------- Categorization ----------
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_capital_goods: Mapped[bool] = mapped_column(
        default=False, server_default="false", nullable=False
    )
    is_itc_eligible: Mapped[bool] = mapped_column(
        default=True, server_default="true", nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[PurchaseInvoiceStatus] = mapped_column(
        SQLEnum(PurchaseInvoiceStatus, native_enum=False, length=20),
        default=PurchaseInvoiceStatus.RECORDED,
        index=True,
        nullable=False,
    )

    business: Mapped["Business"] = relationship()
