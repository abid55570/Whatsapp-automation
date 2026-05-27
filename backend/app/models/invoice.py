"""Invoice + InvoiceLine — GST-compliant tax invoice."""
import logging
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    event,
    inspect,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import InvoiceStatus, InvoiceType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.contact import Contact
    from app.models.order import Order


class Invoice(Base, UUIDMixin, TimestampMixin):
    """A GST tax invoice (or Bill of Supply for composition dealers).

    Once `status` is `ISSUED`, the row is effectively immutable. Cancellation
    keeps the row but flips `status` to `CANCELLED` — sequence numbers must
    never be reused or deleted (GST rule).
    """

    __tablename__ = "invoices"
    __table_args__ = (
        UniqueConstraint(
            "business_id", "fiscal_year", "invoice_number",
            name="uq_invoice_business_fy_number",
        ),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    contact_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    # ---------- Numbering ----------
    invoice_number: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False
    )
    invoice_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    fiscal_year: Mapped[str] = mapped_column(String(7), nullable=False)  # "2026-27"

    # ---------- Customer snapshot (denormalized, immutable post-issue) ----------
    cx_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    cx_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    cx_gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    cx_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    cx_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # ---------- Amounts (paise, integer) ----------
    subtotal_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    discount_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    taxable_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cgst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sgst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    igst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cess_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    round_off_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ---------- Meta ----------
    place_of_supply: Mapped[str | None] = mapped_column(String(100), nullable=True)
    reverse_charge: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    invoice_type: Mapped[InvoiceType] = mapped_column(
        SQLEnum(InvoiceType, native_enum=False, length=20),
        default=InvoiceType.B2C,
        index=True,
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- Status ----------
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus, native_enum=False, length=20),
        default=InvoiceStatus.DRAFT,
        index=True,
        nullable=False,
    )
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancellation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- PDF / payment ----------
    pdf_object_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pdf_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    razorpay_payment_link: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ---------- e-invoice (V3) ----------
    irn: Mapped[str | None] = mapped_column(String(100), unique=True, nullable=True)
    signed_qr_code: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ---------- Relationships ----------
    business: Mapped["Business"] = relationship()
    order: Mapped["Order | None"] = relationship()
    contact: Mapped["Contact | None"] = relationship()
    lines: Mapped[list["InvoiceLine"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceLine.line_number",
    )


class InvoiceLine(Base, UUIDMixin, TimestampMixin):
    """A single line item on an Invoice."""

    __tablename__ = "invoice_lines"

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    description: Mapped[str] = mapped_column(String(500), nullable=False)
    hsn_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=3), nullable=False
    )
    unit: Mapped[str] = mapped_column(String(10), default="pc", nullable=False)
    rate_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    discount_pct: Mapped[float] = mapped_column(
        Numeric(precision=5, scale=2), default=0, nullable=False
    )
    gst_rate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    taxable_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cgst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sgst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    igst_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cess_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    invoice: Mapped["Invoice"] = relationship(back_populates="lines")


# ============================================================
# Immutability guard — ISSUED / PAID / CANCELLED invoices are read-only
# ============================================================
# These fields are allowed to change post-issue (payment + cancellation
# state-machine transitions + PDF cache fields).
_MUTABLE_POST_ISSUE = frozenset({
    "status", "paid_at", "cancelled_at", "cancellation_reason",
    "pdf_object_key", "pdf_url", "razorpay_payment_link",
    "irn", "signed_qr_code", "updated_at",
})


@event.listens_for(Invoice, "before_update", propagate=True)
def _block_invoice_mutation(mapper, connection, target: "Invoice") -> None:
    """Refuse ORM mutations to immutable fields once an invoice is issued.

    The check looks at SQLAlchemy's attribute history — if any *non-mutable*
    column has unsaved changes AND the prior status was ISSUED/PAID/CANCELLED,
    we raise. Newly-created invoices flow through `before_insert` so they're
    unaffected.
    """
    state = inspect(target)
    prev_status = state.attrs.status.history.deleted
    if not prev_status:
        # No status change yet — check current value
        prior = (target.status.value if hasattr(target.status, "value")
                 else str(target.status))
    else:
        prior = (prev_status[0].value if hasattr(prev_status[0], "value")
                 else str(prev_status[0]))

    if prior in ("issued", "paid", "cancelled"):
        for attr in state.attrs:
            if attr.key in _MUTABLE_POST_ISSUE:
                continue
            if attr.history.has_changes():
                raise ValueError(
                    f"Invoice {target.invoice_number} is {prior!r} and "
                    f"immutable. Cannot change field {attr.key!r}."
                )

