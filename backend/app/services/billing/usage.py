"""Usage tracking + plan limit enforcement.

Increments `Subscription.conversations_used` when a new 24-hour Meta
conversation window opens for a business. Checks vs `conversations_included`
before allowing sends.
"""
import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Business, Subscription
from app.models.enums import PlanType, SubscriptionStatus

logger = logging.getLogger(__name__)


async def increment_conversation_usage(
    db: AsyncSession, business_id, count: int = 1
) -> None:
    """Bump conversations_used for the business's subscription."""
    await db.execute(
        update(Subscription)
        .where(Subscription.business_id == business_id)
        .values(conversations_used=Subscription.conversations_used + count)
    )


async def try_consume_conversation_quota(
    db: AsyncSession, business_id, count: int = 1
) -> bool:
    """Atomic check-and-increment for the conversation quota.

    Performs a single conditional UPDATE: bumps `conversations_used` only if
    the post-increment value still fits within `conversations_included`. This
    closes the read-then-act race where two concurrent webhooks would both
    pass the quota gate at N-1 and overshoot to N+1.

    Returns True if quota was reserved (and incremented), False if exhausted.
    """
    result = await db.execute(
        update(Subscription)
        .where(
            Subscription.business_id == business_id,
            Subscription.status.in_(
                (SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE)
            ),
            (Subscription.conversations_used + count) <= Subscription.conversations_included,
        )
        .values(conversations_used=Subscription.conversations_used + count)
        .returning(Subscription.id)
    )
    return result.first() is not None


async def increment_ai_usage(
    db: AsyncSession, business_id, count: int = 1
) -> None:
    """Bump ai_replies_used."""
    await db.execute(
        update(Subscription)
        .where(Subscription.business_id == business_id)
        .values(ai_replies_used=Subscription.ai_replies_used + count)
    )


def has_conversation_quota(sub: Subscription | None) -> bool:
    """True if subscription has remaining conversations within plan limit.

    Trial gets `conversations_included` (100). Paid plans get their tier limit.
    Returns False if frozen/canceled.
    """
    if sub is None:
        return False
    if sub.status not in (SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE):
        return False
    return sub.conversations_used < sub.conversations_included


def has_ai_quota(sub: Subscription | None) -> bool:
    """True if AI add-on enabled AND quota remaining."""
    if sub is None or not sub.ai_addon_enabled:
        return False
    if sub.status not in (SubscriptionStatus.TRIALING, SubscriptionStatus.ACTIVE):
        return False
    return sub.ai_replies_used < sub.ai_replies_included


async def reset_monthly_usage(db: AsyncSession) -> int:
    """Reset conversations_used = 0 for all subscriptions where the
    `current_period_start` rolls into a new month.

    For TRIAL subs, no reset (trial usage is cumulative until expiry).
    Returns number of rows reset.
    """
    now = datetime.now(timezone.utc)
    # Reset paid subs whose current_period_end has passed
    stmt = (
        update(Subscription)
        .where(
            Subscription.status == SubscriptionStatus.ACTIVE,
            Subscription.current_period_end.is_not(None),
            Subscription.current_period_end < now,
        )
        .values(
            conversations_used=0,
            ai_replies_used=0,
            # Roll period forward by 30 days (simplified — Razorpay will set exact)
        )
        .returning(Subscription.id)
    )
    result = await db.execute(stmt)
    reset_ids = [r[0] for r in result.fetchall()]
    await db.commit()
    if reset_ids:
        logger.info("Reset usage for %d subscriptions", len(reset_ids))
    return len(reset_ids)


PLAN_LIMITS: dict[PlanType, int] = {
    PlanType.TRIAL: 100,
    PlanType.STARTER: 1000,
    PlanType.GROWTH: 3000,
    PlanType.PRO: 6000,
}


def conversation_limit_for_plan(plan: PlanType) -> int:
    return PLAN_LIMITS.get(plan, 100)
