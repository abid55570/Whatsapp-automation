"""Service catalog and Booking (Growth-plan feature)."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import BookingStatus

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.contact import Contact


class Service(Base, UUIDMixin, TimestampMixin):
    """A bookable service (haircut, consultation, etc.)."""

    __tablename__ = "services"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    price_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    sheet_row_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="services")
    bookings: Mapped[list["Booking"]] = relationship(back_populates="service")


class Booking(Base, UUIDMixin, TimestampMixin):
    """A scheduled appointment with a customer."""

    __tablename__ = "bookings"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    booking_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )
    # Denormalized for history
    service_name: Mapped[str] = mapped_column(String(200), nullable=False)

    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    status: Mapped[BookingStatus] = mapped_column(
        SQLEnum(BookingStatus, native_enum=False, length=20),
        default=BookingStatus.PENDING,
        index=True,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="bookings")
    contact: Mapped["Contact"] = relationship(back_populates="bookings")
    service: Mapped["Service | None"] = relationship(back_populates="bookings")
