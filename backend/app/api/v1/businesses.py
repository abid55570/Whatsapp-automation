"""Business profile, WhatsApp connection, intent CRUD endpoints."""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import Business, BusinessIntent, Subscription, User
from app.schemas.business import (
    BusinessCreateRequest,
    BusinessResponse,
    BusinessUpdateRequest,
    MetaExchangeRequest,
    OnboardingStatus,
    WhatsAppConnectRequest,
)
from app.schemas.intent import (
    BusinessIntentResponse,
    BusinessIntentsBulkRequest,
    BusinessIntentUpdate,
)
from app.schemas.subscription import SubscriptionResponse
from app.services.billing import create_trial_subscription
from app.services.matching import MatchingEngine, get_matching_engine
from app.services.onboarding import (
    get_my_business,
    get_my_business_or_404,
    initialize_default_intents,
)

router = APIRouter(prefix="/businesses", tags=["businesses"])


# ============================================================
# Response builders
# ============================================================


def _build_subscription_response(
    sub: Subscription | None,
) -> SubscriptionResponse | None:
    if sub is None:
        return None
    now = datetime.now(timezone.utc)
    days_remaining = None
    if sub.trial_ends_at:
        days_remaining = max(0, (sub.trial_ends_at - now).days)

    return SubscriptionResponse(
        plan=sub.plan.value if hasattr(sub.plan, "value") else str(sub.plan),
        status=(
            sub.status.value if hasattr(sub.status, "value") else str(sub.status)
        ),
        ai_addon_enabled=sub.ai_addon_enabled,
        trial_started_at=sub.trial_started_at,
        trial_ends_at=sub.trial_ends_at,
        days_remaining_in_trial=days_remaining,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        conversations_included=sub.conversations_included,
        conversations_used=sub.conversations_used,
        conversations_remaining=max(
            0, sub.conversations_included - sub.conversations_used
        ),
        ai_replies_included=sub.ai_replies_included,
        ai_replies_used=sub.ai_replies_used,
        ai_replies_remaining=max(
            0, sub.ai_replies_included - sub.ai_replies_used
        ),
    )


async def _build_business_response(
    db: AsyncSession, business: Business
) -> BusinessResponse:
    intent_count = await db.scalar(
        select(func.count(BusinessIntent.id)).where(
            BusinessIntent.business_id == business.id,
            BusinessIntent.enabled.is_(True),
        )
    )
    return BusinessResponse(
        id=business.id,
        name=business.name,
        business_type=(
            business.business_type.value
            if hasattr(business.business_type, "value")
            else str(business.business_type)
        ),
        timezone=business.timezone,
        languages=list(business.languages),
        whatsapp_connected=bool(
            business.whatsapp_phone_number_id and business.whatsapp_access_token
        ),
        whatsapp_display_phone=business.whatsapp_display_phone,
        onboarding_completed=business.onboarding_completed,
        created_at=business.created_at,
        subscription=_build_subscription_response(business.subscription),
        intent_count=intent_count or 0,
    )


def _intent_to_response(
    bi: BusinessIntent, engine: MatchingEngine
) -> BusinessIntentResponse:
    global_def = engine.library.get(bi.intent_key)
    return BusinessIntentResponse(
        id=bi.id,
        intent_key=bi.intent_key,
        enabled=bi.enabled,
        reply_text=bi.reply_text,
        reply_translations=dict(bi.reply_translations or {}),
        media_url=bi.media_url,
        custom_keywords=list(bi.custom_keywords),
        priority=bi.priority,
        name=global_def.name if global_def else None,
        description=global_def.description if global_def else None,
        category=global_def.category if global_def else None,
    )


# ============================================================
# Business CRUD
# ============================================================


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_business(
    body: BusinessCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    """Create the user's business profile. One per user."""
    existing = await get_my_business(db, current_user, with_subscription=False)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Business already exists. Use PATCH /businesses/me to update.",
        )

    business = Business(
        owner_user_id=current_user.id,
        name=body.name,
        business_type=body.business_type,
        languages=[lang.value for lang in body.languages],
        timezone=body.timezone,
    )
    db.add(business)
    await db.flush()

    # Set up trial subscription + default intents
    await create_trial_subscription(db, business)
    await initialize_default_intents(db, business)

    await db.commit()
    await db.refresh(business, attribute_names=["subscription"])

    return await _build_business_response(db, business)


@router.get("/me", response_model=BusinessResponse)
async def get_my_business_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    business = await get_my_business_or_404(db, current_user)
    return await _build_business_response(db, business)


@router.patch("/me", response_model=BusinessResponse)
async def update_my_business(
    body: BusinessUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    business = await get_my_business_or_404(db, current_user)

    if body.name is not None:
        business.name = body.name
    if body.business_type is not None:
        business.business_type = body.business_type
    if body.languages is not None:
        business.languages = [lang.value for lang in body.languages]
    if body.timezone is not None:
        business.timezone = body.timezone

    await db.commit()
    await db.refresh(business)
    return await _build_business_response(db, business)


# ============================================================
# WhatsApp connection
# ============================================================


@router.post("/me/whatsapp/connect", response_model=BusinessResponse)
async def connect_whatsapp(
    body: WhatsAppConnectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    """Save Meta WhatsApp Business credentials for this business.

    Called after Meta Embedded Signup completes on the frontend.
    """
    business = await get_my_business_or_404(db, current_user)

    # Conflict: same phone_number_id can't be used by two businesses
    stmt = select(Business).where(
        Business.whatsapp_phone_number_id == body.phone_number_id,
        Business.id != business.id,
    )
    other = (await db.execute(stmt)).scalar_one_or_none()
    if other is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This WhatsApp phone number is already connected to another account.",
        )

    business.whatsapp_phone_number_id = body.phone_number_id
    business.whatsapp_business_account_id = body.business_account_id
    business.whatsapp_display_phone = body.display_phone
    business.whatsapp_access_token = body.access_token  # auto-encrypted (EncryptedString TypeDecorator)

    await db.commit()
    await db.refresh(business)
    return await _build_business_response(db, business)


@router.post(
    "/me/whatsapp/disconnect",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def disconnect_whatsapp(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    business = await get_my_business_or_404(db, current_user)
    business.whatsapp_phone_number_id = None
    business.whatsapp_business_account_id = None
    business.whatsapp_display_phone = None
    business.whatsapp_access_token = None
    await db.commit()


# ============================================================
# Meta Embedded Signup — exchange OAuth code → access token
# ============================================================


@router.post("/me/whatsapp/meta-exchange", response_model=BusinessResponse)
async def connect_whatsapp_via_meta_signup(
    body: MetaExchangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessResponse:
    """Called after Meta Embedded Signup completes on the frontend.

    Frontend sends the OAuth code + phone_number_id from Meta.
    Backend exchanges code for a long-lived access token, saves everything.
    """
    from app.services.whatsapp.meta_oauth import (
        MetaOAuthError,
        exchange_code_for_token,
        fetch_phone_number_display,
    )

    business = await get_my_business_or_404(db, current_user)

    # Conflict check
    stmt = select(Business).where(
        Business.whatsapp_phone_number_id == body.phone_number_id,
        Business.id != business.id,
    )
    if (await db.execute(stmt)).scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This WhatsApp number is already connected to another account.",
        )

    try:
        access_token = await exchange_code_for_token(body.code)
    except MetaOAuthError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # Best-effort fetch of display number
    display = await fetch_phone_number_display(body.phone_number_id, access_token)

    business.whatsapp_phone_number_id = body.phone_number_id
    business.whatsapp_business_account_id = body.business_account_id
    business.whatsapp_access_token = access_token  # auto-encrypted (EncryptedString)
    if display:
        business.whatsapp_display_phone = display

    await db.commit()
    await db.refresh(business)
    return await _build_business_response(db, business)


# ============================================================
# Onboarding status (tells FE which screen to render)
# ============================================================


@router.get("/me/onboarding-status", response_model=OnboardingStatus)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OnboardingStatus:
    business = await get_my_business(db, current_user, with_subscription=False)

    if business is None:
        return OnboardingStatus(
            user_exists=True,
            business_created=False,
            whatsapp_connected=False,
            intents_configured=False,
            onboarding_completed=False,
            next_step="create_business",
        )

    wa_connected = bool(
        business.whatsapp_phone_number_id and business.whatsapp_access_token
    )

    intent_count = await db.scalar(
        select(func.count(BusinessIntent.id)).where(
            BusinessIntent.business_id == business.id,
            BusinessIntent.enabled.is_(True),
        )
    )
    intents_configured = (intent_count or 0) >= 1

    onboarding_completed = wa_connected and intents_configured
    if onboarding_completed and not business.onboarding_completed:
        business.onboarding_completed = True
        await db.commit()

    if not wa_connected:
        next_step = "connect_whatsapp"
    elif not intents_configured:
        next_step = "configure_intents"
    else:
        next_step = "done"

    return OnboardingStatus(
        user_exists=True,
        business_created=True,
        whatsapp_connected=wa_connected,
        intents_configured=intents_configured,
        onboarding_completed=onboarding_completed,
        next_step=next_step,
    )


# ============================================================
# Per-business intent CRUD
# ============================================================


@router.get("/me/intents", response_model=list[BusinessIntentResponse])
async def list_my_intents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BusinessIntentResponse]:
    """List all intents configured for the user's business."""
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(BusinessIntent)
        .where(BusinessIntent.business_id == business.id)
        .order_by(BusinessIntent.priority.desc(), BusinessIntent.intent_key)
    )
    rows = (await db.execute(stmt)).scalars().all()
    engine = get_matching_engine()
    return [_intent_to_response(bi, engine) for bi in rows]


@router.post(
    "/me/intents",
    response_model=list[BusinessIntentResponse],
)
async def bulk_configure_intents(
    body: BusinessIntentsBulkRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[BusinessIntentResponse]:
    """Bulk create or update intent configurations.

    Used during onboarding when the user picks which intents to enable and
    customizes the replies.
    """
    business = await get_my_business_or_404(db, current_user)
    engine = get_matching_engine()

    # Validate every intent_key exists in the global library
    for cfg in body.intents:
        if engine.library.get(cfg.intent_key) is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown intent key: {cfg.intent_key}",
            )

    stmt = select(BusinessIntent).where(BusinessIntent.business_id == business.id)
    existing = {
        bi.intent_key: bi for bi in (await db.execute(stmt)).scalars().all()
    }

    result: list[BusinessIntent] = []
    for cfg in body.intents:
        bi = existing.get(cfg.intent_key)
        if bi is None:
            bi = BusinessIntent(
                business_id=business.id,
                intent_key=cfg.intent_key,
                enabled=cfg.enabled,
                reply_text=cfg.reply_text,
                reply_translations=cfg.reply_translations or {},
                media_url=cfg.media_url,
                custom_keywords=cfg.custom_keywords,
                priority=cfg.priority,
            )
            db.add(bi)
        else:
            bi.enabled = cfg.enabled
            bi.reply_text = cfg.reply_text
            bi.reply_translations = cfg.reply_translations or {}
            bi.media_url = cfg.media_url
            bi.custom_keywords = cfg.custom_keywords
            bi.priority = cfg.priority
        result.append(bi)

    await db.commit()
    for bi in result:
        await db.refresh(bi)
    return [_intent_to_response(bi, engine) for bi in result]


@router.patch(
    "/me/intents/{intent_key}",
    response_model=BusinessIntentResponse,
)
async def update_single_intent(
    intent_key: str,
    body: BusinessIntentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> BusinessIntentResponse:
    business = await get_my_business_or_404(db, current_user)
    stmt = select(BusinessIntent).where(
        BusinessIntent.business_id == business.id,
        BusinessIntent.intent_key == intent_key,
    )
    bi = (await db.execute(stmt)).scalar_one_or_none()
    if bi is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intent not configured for this business",
        )

    if body.enabled is not None:
        bi.enabled = body.enabled
    if body.reply_text is not None:
        bi.reply_text = body.reply_text
    if body.reply_translations is not None:
        bi.reply_translations = body.reply_translations
    if body.media_url is not None:
        bi.media_url = body.media_url
    if body.custom_keywords is not None:
        bi.custom_keywords = body.custom_keywords
    if body.priority is not None:
        bi.priority = body.priority

    await db.commit()
    await db.refresh(bi)
    return _intent_to_response(bi, get_matching_engine())


@router.delete(
    "/me/intents/{intent_key}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_intent(
    intent_key: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    business = await get_my_business_or_404(db, current_user)
    stmt = select(BusinessIntent).where(
        BusinessIntent.business_id == business.id,
        BusinessIntent.intent_key == intent_key,
    )
    bi = (await db.execute(stmt)).scalar_one_or_none()
    if bi is None:
        raise HTTPException(status_code=404, detail="Intent not found")
    await db.delete(bi)
    await db.commit()
