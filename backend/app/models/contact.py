"""Contact — an end customer of a business on WhatsApp."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.business import Business
    from app.models.conversation import Conversation, Message
    from app.models.order import Order


class Contact(Base, UUIDMixin, TimestampMixin):
    """A WhatsApp customer of a business (unique per (business, phone))."""

    __tablename__ = "contacts"
    __table_args__ = (
        UniqueConstraint(
            "business_id", "whatsapp_phone", name="uq_business_contact"
        ),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    whatsapp_phone: Mapped[str] = mapped_column(
        String(20), index=True, nullable=False
    )
    name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(50)), default=list, nullable=False
    )
    opted_out: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    first_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_seen_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="contacts")
    conversations: Mapped[list["Conversation"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="contact", cascade="all, delete-orphan"
    )
