"""Raw webhook event log (Meta, Razorpay) for debugging + idempotency."""
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class WebhookEvent(Base, UUIDMixin, TimestampMixin):
    """Persists every inbound webhook for replay/debugging."""

    __tablename__ = "webhook_events"

    business_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    event_type: Mapped[str | None] = mapped_column(String(100), index=True, nullable=True)

    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    headers: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    signature_verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    processed: Mapped[bool] = mapped_column(
        Boolean, default=False, index=True, nullable=False
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
