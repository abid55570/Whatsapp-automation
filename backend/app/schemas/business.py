"""Pydantic schemas for business endpoints."""
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BusinessType, Language
from app.schemas.subscription import SubscriptionResponse


# ============================================================
# Requests
# ============================================================


class BusinessCreateRequest(BaseModel):
    """Body for POST /businesses — create the user's business profile."""

    name: str = Field(..., min_length=2, max_length=200)
    business_type: BusinessType
    languages: list[Language] = Field(..., min_length=1, max_length=10)
    timezone: str = "Asia/Kolkata"


class BusinessUpdateRequest(BaseModel):
    """Body for PATCH /businesses/me — partial update."""

    name: str | None = Field(None, min_length=2, max_length=200)
    business_type: BusinessType | None = None
    languages: list[Language] | None = Field(None, min_length=1, max_length=10)
    timezone: str | None = None


class WhatsAppConnectRequest(BaseModel):
    """Body for POST /businesses/me/whatsapp/connect.

    These come from Meta's Embedded Signup callback or manual entry.
    """

    phone_number_id: str = Field(..., min_length=1, max_length=50)
    business_account_id: str | None = Field(None, max_length=50)
    display_phone: str | None = Field(None, max_length=20)
    access_token: str = Field(..., min_length=10)


class MetaExchangeRequest(BaseModel):
    """Body for /whatsapp/meta-exchange — from Meta Embedded Signup."""

    code: str = Field(..., min_length=5, description="OAuth code from FB.login")
    phone_number_id: str = Field(..., min_length=1, max_length=50)
    business_account_id: str | None = Field(None, max_length=50)


# ============================================================
# Responses
# ============================================================


class BusinessResponse(BaseModel):
    """Safe view of a Business (no access tokens)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    business_type: str
    timezone: str
    languages: list[str]
    whatsapp_connected: bool
    whatsapp_display_phone: str | None = None
    onboarding_completed: bool
    created_at: datetime
    subscription: SubscriptionResponse | None = None
    intent_count: int = 0


class OnboardingStatus(BaseModel):
    """Used by the frontend to know which onboarding screen to show."""

    user_exists: bool
    business_created: bool
    whatsapp_connected: bool
    intents_configured: bool
    onboarding_completed: bool
    next_step: Literal[
        "create_business",
        "connect_whatsapp",
        "configure_intents",
        "done",
    ]
