"""Conversation (24h billing window) and Message models."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import (
    ConversationCategory,
    ConversationStatus,
    MessageDirection,
    MessageStatus,
    MessageType,
)

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.contact import Contact


class Conversation(Base, UUIDMixin, TimestampMixin):
    """A 24-hour WhatsApp conversation window (Meta's billing unit)."""

    __tablename__ = "conversations"

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

    # Meta's conversation ID (used for billing reconciliation)
    meta_conversation_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, nullable=True
    )

    category: Mapped[ConversationCategory] = mapped_column(
        SQLEnum(ConversationCategory, native_enum=False, length=20),
        default=ConversationCategory.SERVICE,
        index=True,
        nullable=False,
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus, native_enum=False, length=20),
        default=ConversationStatus.OPEN,
        index=True,
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_message_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )

    is_billable: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    meta_cost_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    unread_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Multi-turn conversation state machine (for order flow, etc.)
    # Shape: {"stage": "ordering"|"confirming"|"complete", "cart": [...], "draft_order_id": "uuid"}
    state: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="conversations")
    contact: Mapped["Contact"] = relationship(back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base, UUIDMixin, TimestampMixin):
    """A single WhatsApp message (inbound or outbound)."""

    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
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

    whatsapp_message_id: Mapped[str | None] = mapped_column(
        String(100), unique=True, index=True, nullable=True
    )

    direction: Mapped[MessageDirection] = mapped_column(
        SQLEnum(MessageDirection, native_enum=False, length=10),
        index=True,
        nullable=False,
    )
    type: Mapped[MessageType] = mapped_column(
        SQLEnum(MessageType, native_enum=False, length=20),
        default=MessageType.TEXT,
        nullable=False,
    )
    status: Mapped[MessageStatus] = mapped_column(
        SQLEnum(MessageStatus, native_enum=False, length=20),
        default=MessageStatus.QUEUED,
        nullable=False,
    )

    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    media_mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    template_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ---------- Auto-reply metadata (set by matching engine) ----------
    is_auto_reply: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    matched_intent_key: Mapped[str | None] = mapped_column(
        String(100), index=True, nullable=True
    )
    matched_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    matched_layer: Mapped[str | None] = mapped_column(String(30), nullable=True)
    detected_language: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # ---------- Delivery tracking ----------
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    delivered_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)

    extra_data: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )

    # Relationships
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
    business: Mapped["Business"] = relationship(back_populates="messages")
    contact: Mapped["Contact"] = relationship(back_populates="messages")
