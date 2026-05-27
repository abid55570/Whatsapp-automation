"""Tests for app.services.billing.trial."""
from app.models.enums import PlanType, SubscriptionStatus
from app.services.billing.trial import create_trial_subscription
from tests.conftest import create_business, create_user


async def test_create_trial_subscription(db):
    user = await create_user(db, phone="+919000005001")
    biz = await create_business(db, owner=user)
    sub = await create_trial_subscription(db, biz)
    await db.commit()
    assert sub.plan == PlanType.TRIAL
    assert sub.status == SubscriptionStatus.TRIALING
    assert sub.trial_ends_at is not None
    assert sub.conversations_included > 0
