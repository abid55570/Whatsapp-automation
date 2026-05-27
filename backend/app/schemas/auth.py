"""Pydantic schemas for the auth endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.utils.phone import is_valid_phone, normalize_phone


# ============================================================
# Requests
# ============================================================


class StartVerificationRequest(BaseModel):
    """Body for POST /auth/start-verification."""

    phone: str = Field(..., description="Phone number (any common format)")
    full_name: str | None = Field(None, max_length=120)

    @field_validator("phone")
    @classmethod
    def _normalize(cls, v: str) -> str:
        normalized = normalize_phone(v)
        if not is_valid_phone(normalized):
            raise ValueError("Invalid phone number")
        return normalized


# ============================================================
# Responses
# ============================================================


class StartVerificationResponse(BaseModel):
    """Returned to client after starting verification."""

    verification_id: UUID
    deep_link: str
    expires_at: datetime
    platform_whatsapp_number: str
    # In development we leak the code for easy local testing
    dev_code: str | None = None


class UserPublic(BaseModel):
    """Safe-to-expose user fields."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    email: str | None = None
    full_name: str | None = None
    phone_verified: bool
    preferred_language: str = "en"
    is_superuser: bool = False


class VerificationStatusResponse(BaseModel):
    """Polled by the frontend to check if WhatsApp verification completed."""

    status: str  # "pending" | "verified" | "expired"
    access_token: str | None = None
    token_type: str | None = None
    user: UserPublic | None = None


class MeResponse(BaseModel):
    """GET /auth/me — current authenticated user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    email: str | None
    full_name: str | None
    phone_verified: bool
    preferred_language: str = "en"
    is_superuser: bool = False


class UpdateMeRequest(BaseModel):
    """PATCH /auth/me — update current user's settings."""

    full_name: str | None = Field(None, max_length=120)
    email: EmailStr | None = None
    preferred_language: str | None = Field(
        None,
        pattern="^(en|hi|hinglish|bn|ur|bho)$",
        description="Platform UI language",
    )

    @field_validator("email")
    @classmethod
    def _normalize_email(cls, v: EmailStr | None) -> str | None:
        # Normalize to lowercase so functional unique index is consistent
        return v.lower() if v else None
