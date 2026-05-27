"""SaaS subscription flow: create Razorpay subscription, handle upgrades."""
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Business, Subscription
from app.models.enums import PlanType, SubscriptionStatus
from app.services.payments import RazorpayClient
from app.services.billing.usage import conversation_limit_for_plan

logger = logging.getLogger(__name__)


def plan_id_for(plan: PlanType) -> str:
    """Map PlanType → configured Razorpay plan_id."""
    mapping = {
        PlanType.STARTER: settings.RAZORPAY_PLAN_ID_STARTER,
        PlanType.GROWTH: settings.RAZORPAY_PLAN_ID_GROWTH,
        PlanType.PRO: settings.RAZORPAY_PLAN_ID_PRO,
    }
    return mapping.get(plan, "")


PLAN_PRICE_PAISE: dict[PlanType, int] = {
    PlanType.STARTER: settings.PLAN_STARTER_PRICE_PAISE,
    PlanType.GROWTH: settings.PLAN_GROWTH_PRICE_PAISE,
    PlanType.PRO: settings.PLAN_PRO_PRICE_PAISE,
}


async def start_upgrade(
    db: AsyncSession,
    business: Business,
    contact_phone: str,
    contact_name: str | None,
    target_plan: PlanType,
) -> dict[str, Any]:
    """Create a Razorpay subscription for the target plan.

    Returns dict with `short_url` for checkout. Subscription state stays
    pending until Razorpay webhook fires `subscription.activated`.
    """
    if target_plan == PlanType.TRIAL:
        raise ValueError("Cannot upgrade to trial")

    plan_id = plan_id_for(target_plan)
    if not plan_id:
        raise ValueError(
            f"Razorpay plan_id not configured for {target_plan.value}"
        )

    client = RazorpayClient()
    result = await client.create_subscription(
        plan_id=plan_id,
        customer_phone=contact_phone,
        customer_name=contact_name,
        total_count=12,  # 12 months
        notes={
            "business_id": str(business.id),
            "target_plan": target_plan.value,
        },
    )

    # Persist the pending subscription_id so webhook can match later
    sub = business.subscription
    if sub is not None:
        sub.razorpay_subscription_id = result.get("id")
        await db.commit()

    return result


async def apply_subscription_activation(
    db: AsyncSession,
    razorpay_subscription_id: str,
    razorpay_sub_data: dict[str, Any],
) -> Subscription | None:
    """Called from webhook when subscription.activated fires.

    Promotes the local Subscription to ACTIVE with the target plan.
    """
    from sqlalchemy import select

    stmt = select(Subscription).where(
        Subscription.razorpay_subscription_id == razorpay_subscription_id
    )
    sub = (await db.execute(stmt)).scalar_one_or_none()
    if sub is None:
        logger.warning(
            "No local sub for razorpay_id=%s", razorpay_subscription_id
        )
        return None

    notes = razorpay_sub_data.get("notes") or {}
    target_plan_str = notes.get("target_plan")
    try:
        target_plan = PlanType(target_plan_str)
    except (ValueError, TypeError):
        logger.error("Invalid target_plan in notes: %s", target_plan_str)
        return sub

    now = datetime.now(timezone.utc)
    sub.plan = target_plan
    sub.status = SubscriptionStatus.ACTIVE
    sub.conversations_included = conversation_limit_for_plan(target_plan)
    sub.conversations_used = 0
    sub.current_period_start = now
    # Razorpay tells us next period; for V1 set 30 days
    from datetime import timedelta
    sub.current_period_end = now + timedelta(days=30)
    sub.canceled_at = None

    await db.commit()
    await db.refresh(sub)
    logger.info("Activated subscription %s → %s", sub.id, target_plan.value)
    return sub


async def apply_subscription_cancel(
    db: AsyncSession,
    razorpay_subscription_id: str,
) -> Subscription | None:
    """Called when subscription.cancelled webhook fires."""
    from sqlalchemy import select

    stmt = select(Subscription).where(
        Subscription.razorpay_subscription_id == razorpay_subscription_id
    )
    sub = (await db.execute(stmt)).scalar_one_or_none()
    if sub is None:
        return None

    sub.status = SubscriptionStatus.CANCELED
    sub.canceled_at = datetime.now(timezone.utc)
    await db.commit()
    return sub
