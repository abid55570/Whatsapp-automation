"""Usage log for billing reconciliation."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import UsageType


class UsageLog(Base, UUIDMixin, TimestampMixin):
    """One row per billable event.

    Used to:
    - Count conversations per billing cycle
    - Calculate overage charges
    - Reconcile against Meta's billing
    """

    __tablename__ = "usage_logs"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
    )

    usage_type: Mapped[UsageType] = mapped_column(
        SQLEnum(UsageType, native_enum=False, length=30),
        index=True,
        nullable=False,
    )

    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    meta_cost_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    charged_to_customer_paise: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    billing_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
