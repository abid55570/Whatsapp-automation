"""Business / workspace model — the central entity."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.crypto import EncryptedString
from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import BusinessType, GstScheme

if TYPE_CHECKING:
    from app.models.booking import Booking, Service
    from app.models.contact import Contact
    from app.models.conversation import Conversation, Message
    from app.models.fulfillment import FulfillmentConfig
    from app.models.intent import BusinessIntent
    from app.models.order import Order, Product
    from app.models.sheet import GoogleSheetSync
    from app.models.subscription import Subscription
    from app.models.user import User


class Business(Base, UUIDMixin, TimestampMixin):
    """A small business using the platform."""

    __tablename__ = "businesses"

    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    business_type: Mapped[BusinessType] = mapped_column(
        SQLEnum(BusinessType, native_enum=False, length=30),
        default=BusinessType.SHOP,
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(
        String(50), default="Asia/Kolkata", nullable=False
    )

    # Languages the business's customers use (subset of Language enum values)
    languages: Mapped[list[str]] = mapped_column(
        ARRAY(String(20)), default=list, nullable=False
    )

    # ---------- Meta WhatsApp Business credentials ----------
    whatsapp_phone_number_id: Mapped[str | None] = mapped_column(
        String(50), unique=True, nullable=True
    )
    whatsapp_business_account_id: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    whatsapp_display_phone: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )
    # Encrypted at rest via EncryptedString TypeDecorator (Fernet)
    whatsapp_access_token: Mapped[str | None] = mapped_column(
        EncryptedString(2000), nullable=True
    )

    onboarding_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # ---------- GST / Invoicing ----------
    gstin: Mapped[str | None] = mapped_column(String(15), index=True, nullable=True)
    gst_state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    gst_scheme: Mapped[GstScheme] = mapped_column(
        SQLEnum(GstScheme, native_enum=False, length=20),
        default=GstScheme.UNREGISTERED,
        nullable=False,
    )
    gst_composition_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    legal_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    business_address_line1: Mapped[str | None] = mapped_column(String(200), nullable=True)
    business_address_line2: Mapped[str | None] = mapped_column(String(200), nullable=True)
    business_city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    business_pincode: Mapped[str | None] = mapped_column(String(6), nullable=True)
    # Invoice numbering
    invoice_prefix: Mapped[str] = mapped_column(String(6), default="INV", nullable=False)
    invoice_seq: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_invoice_fy: Mapped[str | None] = mapped_column(String(7), nullable=True)
    tax_pack_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ---------- Relationships ----------
    owner: Mapped["User"] = relationship(back_populates="businesses")

    subscription: Mapped["Subscription | None"] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    intents: Mapped[list["BusinessIntent"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    products: Mapped[list["Product"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    services: Mapped[list["Service"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    sheet_syncs: Mapped[list["GoogleSheetSync"]] = relationship(
        back_populates="business", cascade="all, delete-orphan"
    )
    fulfillment_config: Mapped["FulfillmentConfig | None"] = relationship(
        back_populates="business",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin",
    )
