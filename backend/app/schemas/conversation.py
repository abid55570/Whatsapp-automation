"""Pydantic schemas for inbox/conversation endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Contact
# ============================================================


class ContactSummary(BaseModel):
    """Minimal contact info for list/thread views."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    whatsapp_phone: str
    name: str | None = None
    profile_picture_url: str | None = None
    tags: list[str] = Field(default_factory=list)


# ============================================================
# Message
# ============================================================


class MessagePreview(BaseModel):
    """Compact message info for conversation list."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    direction: str
    body: str | None = None
    type: str
    is_auto_reply: bool
    created_at: datetime


class MessageDetail(BaseModel):
    """Full message info for thread view."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    conversation_id: UUID
    direction: str
    type: str
    status: str
    body: str | None = None
    media_url: str | None = None
    media_mime_type: str | None = None
    template_name: str | None = None

    is_auto_reply: bool
    matched_intent_key: str | None = None
    matched_confidence: float | None = None
    matched_layer: str | None = None
    detected_language: str | None = None

    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    failed_reason: str | None = None

    created_at: datetime


class SendMessageRequest(BaseModel):
    """Manual reply from owner."""

    body: str = Field(..., min_length=1, max_length=4000)


# ============================================================
# Conversation
# ============================================================


class ConversationListItem(BaseModel):
    """One row in the inbox list."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contact: ContactSummary
    last_message: MessagePreview | None = None
    unread_count: int
    status: str
    category: str
    started_at: datetime
    last_message_at: datetime | None = None
    expires_at: datetime | None = None


class ConversationDetail(BaseModel):
    """Conversation header info for thread page."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    contact: ContactSummary
    status: str
    category: str
    started_at: datetime
    expires_at: datetime | None = None
    last_message_at: datetime | None = None
    unread_count: int


class PaginatedConversations(BaseModel):
    items: list[ConversationListItem]
    total: int
    limit: int
    offset: int
    has_more: bool


class PaginatedMessages(BaseModel):
    items: list[MessageDetail]
    total: int
    limit: int
    offset: int
    has_more: bool
