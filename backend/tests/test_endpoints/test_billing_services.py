"""Tests for billing services (status, usage, trial)."""
from datetime import datetime, timedelta, timezone

from app.models.enums import PlanType, SubscriptionStatus
from app.services.billing import status as billing_status
from app.services.billing.usage import (
    has_conversation_quota,
    increment_conversation_usage,
)
from tests.conftest import create_business, create_subscription, create_user


async def test_is_active_during_trial(db):
    user = await create_user(db, phone="+919000002001")
    biz = await create_business(db, owner=user)
    sub = await create_subscription(
        db, business=biz, status=SubscriptionStatus.TRIALING
    )
    assert billing_status.is_active(sub) is True


async def test_is_active_for_active_sub(db):
    user = await create_user(db, phone="+919000002002")
    biz = await create_business(db, owner=user)
    sub = await create_subscription(
        db, business=biz, status=SubscriptionStatus.ACTIVE
    )
    assert billing_status.is_active(sub) is True


async def test_is_not_active_for_frozen(db):
    user = await create_user(db, phone="+919000002003")
    biz = await create_business(db, owner=user)
    sub = await create_subscription(
        db, business=biz, status=SubscriptionStatus.FROZEN
    )
    assert billing_status.is_active(sub) is False


async def test_quota_check(db):
    user = await create_user(db, phone="+919000002004")
    biz = await create_business(db, owner=user)
    sub = await create_subscription(
        db, business=biz, conversations_included=2, conversations_used=0
    )
    assert has_conversation_quota(sub) is True
    sub.conversations_used = 2
    assert has_conversation_quota(sub) is False


async def test_increment_usage(db):
    user = await create_user(db, phone="+919000002005")
    biz = await create_business(db, owner=user)
    sub = await create_subscription(
        db, business=biz, conversations_used=0
    )
    await increment_conversation_usage(db, biz.id)
    await db.commit()
    await db.refresh(sub)
    assert sub.conversations_used == 1


async def test_freeze_expired_trials(db):
    user = await create_user(db, phone="+919000002006")
    biz = await create_business(db, owner=user)
    sub = await create_subscription(
        db, business=biz, status=SubscriptionStatus.TRIALING
    )
    # backdate the trial_ends_at
    sub.trial_ends_at = datetime.now(timezone.utc) - timedelta(days=1)
    await db.commit()
    n = await billing_status.freeze_expired_trials(db)
    assert n >= 1
    await db.refresh(sub)
    assert sub.status == SubscriptionStatus.FROZEN
