"""Per-business fulfillment configuration (pickup + delivery settings)."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import PickupPrepStrategy

if TYPE_CHECKING:
    from app.models.business import Business


class FulfillmentConfig(Base, UUIDMixin, TimestampMixin):
    """One config per business — controls pickup + delivery behavior."""

    __tablename__ = "fulfillment_configs"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # ============================================================
    # Pickup
    # ============================================================
    pickup_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    pickup_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pickup_landmark: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Stored as HH:MM strings for simplicity
    pickup_hours_start: Mapped[str] = mapped_column(
        String(5), default="10:00", nullable=False
    )
    pickup_hours_end: Mapped[str] = mapped_column(
        String(5), default="21:00", nullable=False
    )

    # 0 = Monday ... 6 = Sunday
    pickup_closed_days: Mapped[list[int]] = mapped_column(
        ARRAY(Integer), default=list, nullable=False
    )

    pickup_prep_strategy: Mapped[PickupPrepStrategy] = mapped_column(
        SQLEnum(PickupPrepStrategy, native_enum=False, length=20),
        default=PickupPrepStrategy.FIXED,
        nullable=False,
    )
    pickup_fixed_minutes: Mapped[int] = mapped_column(
        Integer, default=30, nullable=False
    )
    pickup_per_item_minutes: Mapped[int] = mapped_column(
        Integer, default=5, nullable=False
    )
    # For SLOTS strategy: ["11:00", "14:00", "17:00", "20:00"]
    pickup_slots: Mapped[list[str]] = mapped_column(
        ARRAY(String(5)), default=list, nullable=False
    )

    # ============================================================
    # Delivery
    # ============================================================
    delivery_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    delivery_fee_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    delivery_minimum_order_paise: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    delivery_radius_km: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    delivery_estimate_minutes: Mapped[int] = mapped_column(
        Integer, default=45, nullable=False
    )

    # Relationships
    business: Mapped["Business"] = relationship(
        back_populates="fulfillment_config", uselist=False
    )
