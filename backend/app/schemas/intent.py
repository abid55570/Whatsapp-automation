"""Pydantic schemas for intent endpoints."""
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ============================================================
# Global intent catalog
# ============================================================


class GlobalIntentResponse(BaseModel):
    """A global intent (loaded from data/intents/*.json), for picker UI."""

    key: str
    name: str
    description: str
    default_reply_template: str
    category: str
    priority: int
    languages_covered: list[str]
    keyword_counts: dict[str, int]
    emoji_preview: list[str]


# ============================================================
# Business intent configuration
# ============================================================


class BusinessIntentConfigure(BaseModel):
    """One intent entry in a bulk-configure request."""

    intent_key: str = Field(..., min_length=1, max_length=100)
    enabled: bool = True
    reply_text: str = Field(..., min_length=1, max_length=4000)
    reply_translations: dict[str, str] = Field(default_factory=dict)
    media_url: str | None = Field(None, max_length=1000)
    custom_keywords: list[str] = Field(default_factory=list, max_length=50)
    priority: int = 0


class BusinessIntentsBulkRequest(BaseModel):
    intents: list[BusinessIntentConfigure] = Field(
        ..., min_length=1, max_length=50
    )


class BusinessIntentUpdate(BaseModel):
    """PATCH /businesses/me/intents/{key} — all fields optional."""

    enabled: bool | None = None
    reply_text: str | None = Field(None, min_length=1, max_length=4000)
    reply_translations: dict[str, str] | None = None
    media_url: str | None = Field(None, max_length=1000)
    custom_keywords: list[str] | None = Field(None, max_length=50)
    priority: int | None = None


class BusinessIntentResponse(BaseModel):
    """Per-business intent config (with joined global metadata)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    intent_key: str
    enabled: bool
    reply_text: str
    reply_translations: dict[str, str] = Field(default_factory=dict)
    media_url: str | None = None
    custom_keywords: list[str]
    priority: int
    # Joined from global library for the UI
    name: str | None = None
    description: str | None = None
    category: str | None = None
