"""Trial subscription setup."""
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Business, Subscription
from app.models.enums import PlanType, SubscriptionStatus


async def create_trial_subscription(
    db: AsyncSession,
    business: Business,
) -> Subscription:
    """Create a 14-day trial subscription for a new business.

    Trial includes 100 conversations and NO auto-conversion to paid.
    After expiry, status moves to FROZEN unless owner picks a plan.
    """
    now = datetime.now(timezone.utc)
    sub = Subscription(
        business_id=business.id,
        plan=PlanType.TRIAL,
        status=SubscriptionStatus.TRIALING,
        ai_addon_enabled=False,
        trial_started_at=now,
        trial_ends_at=now + timedelta(days=settings.TRIAL_DAYS),
        conversations_included=settings.TRIAL_CONVERSATIONS,
        conversations_used=0,
        ai_replies_included=0,
        ai_replies_used=0,
    )
    db.add(sub)
    await db.flush()
    return sub
