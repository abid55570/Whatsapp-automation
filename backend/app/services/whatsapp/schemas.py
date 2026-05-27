"""Pydantic schemas for Meta WhatsApp webhook payloads.

Reference:
https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks/payload-examples
"""
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WAProfile(BaseModel):
    name: str | None = None


class WAContact(BaseModel):
    model_config = ConfigDict(extra="allow")

    profile: WAProfile | None = None
    wa_id: str


class WAText(BaseModel):
    body: str


class WAMessage(BaseModel):
    """A single inbound message from a customer."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    id: str  # wamid.XXX
    from_: str = Field(alias="from")
    timestamp: str
    type: str  # text, image, audio, document, video, sticker, location, button, interactive, contacts

    text: WAText | None = None
    image: dict[str, Any] | None = None
    audio: dict[str, Any] | None = None
    document: dict[str, Any] | None = None
    video: dict[str, Any] | None = None
    sticker: dict[str, Any] | None = None
    location: dict[str, Any] | None = None
    button: dict[str, Any] | None = None
    interactive: dict[str, Any] | None = None
    contacts: list[dict[str, Any]] | None = None
    reaction: dict[str, Any] | None = None


class WAStatus(BaseModel):
    """A delivery status update from Meta."""

    model_config = ConfigDict(extra="allow")

    id: str  # wamid of the original outbound message
    status: str  # sent, delivered, read, failed
    timestamp: str
    recipient_id: str
    conversation: dict[str, Any] | None = None
    pricing: dict[str, Any] | None = None
    errors: list[dict[str, Any]] | None = None


class WAMetadata(BaseModel):
    display_phone_number: str
    phone_number_id: str


class WAChangeValue(BaseModel):
    model_config = ConfigDict(extra="allow")

    messaging_product: str = "whatsapp"
    metadata: WAMetadata
    contacts: list[WAContact] = Field(default_factory=list)
    messages: list[WAMessage] = Field(default_factory=list)
    statuses: list[WAStatus] = Field(default_factory=list)


class WAChange(BaseModel):
    value: WAChangeValue
    field: str


class WAEntry(BaseModel):
    id: str
    changes: list[WAChange]


class WebhookPayload(BaseModel):
    """Top-level webhook envelope from Meta."""

    model_config = ConfigDict(extra="allow")

    object: str
    entry: list[WAEntry]
