"""Subscription status helpers: trial expiry, active checks."""
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Business, Subscription
from app.models.enums import PlanType, SubscriptionStatus

logger = logging.getLogger(__name__)


def is_active(sub: Subscription | None) -> bool:
    """True if subscription allows automation (auto-replies, manual sends)."""
    if sub is None:
        return False
    if sub.status == SubscriptionStatus.ACTIVE:
        return True
    if sub.status == SubscriptionStatus.TRIALING:
        # Trial still within window?
        if sub.trial_ends_at is None:
            return True
        return sub.trial_ends_at > datetime.now(timezone.utc)
    return False


def is_frozen(sub: Subscription | None) -> bool:
    """True if subscription is FROZEN (trial expired w/o upgrade)."""
    return sub is not None and sub.status == SubscriptionStatus.FROZEN


async def business_can_send(db: AsyncSession, business: Business) -> bool:
    """Quick check: can this business send WhatsApp messages right now?"""
    sub = business.subscription
    if sub is None:
        # Lazy load if not loaded
        stmt = select(Subscription).where(
            Subscription.business_id == business.id
        )
        sub = (await db.execute(stmt)).scalar_one_or_none()
    return is_active(sub)


async def freeze_expired_trials(db: AsyncSession) -> int:
    """Find trial subs past expiry → set status=FROZEN. Returns count frozen."""
    now = datetime.now(timezone.utc)

    stmt = (
        update(Subscription)
        .where(
            Subscription.status == SubscriptionStatus.TRIALING,
            Subscription.trial_ends_at.is_not(None),
            Subscription.trial_ends_at < now,
        )
        .values(status=SubscriptionStatus.FROZEN)
        .returning(Subscription.id)
    )
    result = await db.execute(stmt)
    frozen_ids = [row[0] for row in result.fetchall()]
    await db.commit()
    if frozen_ids:
        logger.info("Froze %d expired trials", len(frozen_ids))
    return len(frozen_ids)
