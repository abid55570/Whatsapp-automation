"""Authentication endpoints — WhatsApp deep-link verification."""
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.core.security import create_access_token
from app.models import OTPCode, User
from app.schemas.auth import (
    MeResponse,
    StartVerificationRequest,
    StartVerificationResponse,
    UpdateMeRequest,
    UserPublic,
    VerificationStatusResponse,
)
from app.services.auth.verification import (
    consume_verification_code,
    create_verification,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


# ============================================================
# Start verification
# ============================================================


@router.post(
    "/start-verification",
    response_model=StartVerificationResponse,
    status_code=status.HTTP_201_CREATED,
)
@(limiter.limit(settings.RATE_LIMIT_AUTH) if limiter else (lambda f: f))
async def start_verification(
    request: Request,
    body: StartVerificationRequest,
    db: AsyncSession = Depends(get_db),
) -> StartVerificationResponse:
    """Begin a WhatsApp deep-link verification.

    Returns a `deep_link` (`https://wa.me/...?text=verify-XXX`) the frontend
    presents as the "Verify via WhatsApp" button.
    """
    otp, code, deep_link = await create_verification(
        db, phone=body.phone, full_name=body.full_name
    )
    await db.commit()
    await db.refresh(otp)

    return StartVerificationResponse(
        verification_id=otp.id,
        deep_link=deep_link,
        expires_at=otp.expires_at,
        platform_whatsapp_number=settings.PLATFORM_WHATSAPP_PHONE_NUMBER,
        dev_code=code if settings.APP_ENV != "production" else None,
    )


# ============================================================
# Poll verification status
# ============================================================


@router.get(
    "/verification-status/{verification_id}",
    response_model=VerificationStatusResponse,
)
async def verification_status(
    verification_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> VerificationStatusResponse:
    """Frontend polls this every ~2 seconds.

    Returns:
      - status=pending   → not yet verified
      - status=verified  → includes access_token + user (one-shot, then poll stops)
      - status=expired   → code TTL elapsed, ask user to restart
    """
    otp = await db.get(OTPCode, verification_id)
    if otp is None:
        raise HTTPException(404, "Verification not found")

    now = datetime.now(timezone.utc)

    if otp.consumed_at is None:
        if otp.expires_at < now:
            return VerificationStatusResponse(status="expired")
        return VerificationStatusResponse(status="pending")

    # Consumed — look up the user
    user_stmt = select(User).where(User.phone == otp.phone)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    if user is None:
        # Shouldn't happen, but be safe
        return VerificationStatusResponse(status="pending")

    token = create_access_token(user.id)
    return VerificationStatusResponse(
        status="verified",
        access_token=token,
        token_type="bearer",
        user=UserPublic.model_validate(user),
    )


# ============================================================
# DEV-ONLY: simulate WhatsApp verification (skips real Meta webhook)
# ============================================================


@router.post(
    "/dev/simulate-whatsapp-verify",
    include_in_schema=False,
)
@(limiter.limit(settings.RATE_LIMIT_AUTH) if limiter else (lambda f: f))
async def dev_simulate_verify(
    request: Request,
    phone: str,
    code: str,
    db: AsyncSession = Depends(get_db),
):
    """Skip the WhatsApp round-trip when testing locally.

    Disabled in production.
    """
    if settings.APP_ENV == "production":
        raise HTTPException(403, "Not available in production")

    user = await consume_verification_code(db, phone=phone, code=code)
    if user is None:
        return {"status": "failed", "reason": "code not found or expired"}
    return {"status": "verified", "user_id": str(user.id)}


# ============================================================
# Get current user
# ============================================================


@router.get("/me", response_model=MeResponse)
async def get_me(current_user: User = Depends(get_current_user)) -> MeResponse:
    """Return the authenticated user."""
    return MeResponse.model_validate(current_user)


@router.patch("/me", response_model=MeResponse)
async def update_me(
    body: UpdateMeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeResponse:
    """Update name / preferred UI language."""
    if body.full_name is not None:
        current_user.full_name = body.full_name
    if body.email is not None:
        current_user.email = body.email
    if body.preferred_language is not None:
        current_user.preferred_language = body.preferred_language
    await db.commit()
    await db.refresh(current_user)
    return MeResponse.model_validate(current_user)


# ============================================================
# Logout (stateless — JWT lives client-side)
# ============================================================


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout() -> dict[str, str]:
    """Logout. With stateless JWT, this is purely informational — the
    client discards the token.
    """
    return {"status": "logged_out"}
