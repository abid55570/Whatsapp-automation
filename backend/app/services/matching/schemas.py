"""Pydantic schemas for the matching engine."""
from pydantic import BaseModel, Field


class IntentDefinition(BaseModel):
    """A global intent definition (loaded from data/intents/*.json).

    Each intent describes:
      - A semantic action (ask_price, greeting, etc.)
      - Trigger keywords in multiple languages
      - Optional regex patterns and emojis
      - A default reply template
    """

    key: str
    name: str
    description: str = ""
    default_reply_template: str = ""
    languages: dict[str, list[str]] = Field(default_factory=dict)
    patterns: list[str] = Field(default_factory=list)
    emojis: list[str] = Field(default_factory=list)
    priority: int = 0
    category: str = "general"


class MatchResult(BaseModel):
    """Result of matching a piece of text against intents."""

    intent_key: str
    confidence: float
    matched_layer: str
    matched_keywords: list[str] = Field(default_factory=list)
    detected_language: str | None = None
