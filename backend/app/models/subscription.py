"""Subscription state per business."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import PlanType, SubscriptionStatus

if TYPE_CHECKING:
    from app.models.business import Business


class Subscription(Base, UUIDMixin, TimestampMixin):
    """One subscription per business (1:1)."""

    __tablename__ = "subscriptions"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    plan: Mapped[PlanType] = mapped_column(
        SQLEnum(PlanType, native_enum=False, length=20),
        default=PlanType.TRIAL,
        nullable=False,
    )
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLEnum(SubscriptionStatus, native_enum=False, length=20),
        default=SubscriptionStatus.TRIALING,
        index=True,
        nullable=False,
    )
    ai_addon_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # ---------- Trial window ----------
    trial_started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )

    # ---------- Billing cycle ----------
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    canceled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ---------- Razorpay references ----------
    razorpay_customer_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    razorpay_subscription_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    # ---------- Denormalized usage counters (reset every billing cycle) ----------
    conversations_included: Mapped[int] = mapped_column(
        Integer, default=100, nullable=False
    )
    conversations_used: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    ai_replies_included: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    ai_replies_used: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="subscription")
