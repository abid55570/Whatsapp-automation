"""Business creation and onboarding helpers."""
import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Business, BusinessIntent, User
from app.services.matching import get_matching_engine

logger = logging.getLogger(__name__)


async def get_my_business(
    db: AsyncSession,
    user: User,
    *,
    with_subscription: bool = True,
) -> Business | None:
    """Return the user's business (None if not created yet)."""
    stmt = select(Business).where(Business.owner_user_id == user.id)
    if with_subscription:
        stmt = stmt.options(selectinload(Business.subscription))
    return (await db.execute(stmt)).scalar_one_or_none()


async def get_my_business_or_404(
    db: AsyncSession,
    user: User,
    *,
    with_subscription: bool = True,
) -> Business:
    """Like get_my_business but raises 404 if not found."""
    biz = await get_my_business(db, user, with_subscription=with_subscription)
    if biz is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No business found for this user. Create one first.",
        )
    return biz


async def initialize_default_intents(
    db: AsyncSession,
    business: Business,
) -> int:
    """Pre-populate BusinessIntent rows for all global intents.

    Each intent is enabled by default with the global default_reply_template
    (with business name substituted). The owner customizes from the dashboard.
    """
    engine = get_matching_engine()
    intents = engine.library.list_all()

    created = 0
    for intent_def in intents:
        reply = intent_def.default_reply_template
        # Light placeholder substitution — owners can edit freely later
        reply = (
            reply.replace("[Your Business]", business.name)
            .replace("[Business Name]", business.name)
            .replace("{{business_name}}", business.name)
        )

        bi = BusinessIntent(
            business_id=business.id,
            intent_key=intent_def.key,
            enabled=True,
            reply_text=reply,
            priority=intent_def.priority,
            custom_keywords=[],
        )
        db.add(bi)
        created += 1

    await db.flush()
    logger.info(
        "Initialized %d default intents for business %s",
        created,
        business.id,
    )
    return created
