"""Tests for app.services.billing.subscriptions."""
import pytest

from app.models.enums import PlanType, SubscriptionStatus
from app.services.billing.subscriptions import (
    apply_subscription_activation,
    apply_subscription_cancel,
    plan_id_for,
    start_upgrade,
)
from tests.conftest import create_business, create_subscription, create_user


def test_plan_id_for_known_plans():
    assert plan_id_for(PlanType.STARTER) != ""
    assert plan_id_for(PlanType.GROWTH) != ""
    assert plan_id_for(PlanType.PRO) != ""


def test_plan_id_for_trial_is_empty():
    assert plan_id_for(PlanType.TRIAL) == ""


async def test_start_upgrade_rejects_trial(db):
    u = await create_user(db, phone="+919000003001")
    biz = await create_business(db, owner=u)
    with pytest.raises(ValueError):
        await start_upgrade(
            db, business=biz, contact_phone=u.phone, contact_name=None,
            target_plan=PlanType.TRIAL,
        )


async def test_start_upgrade_success(db):
    """Razorpay client mocked → returns sub id."""
    u = await create_user(db, phone="+919000003002")
    biz = await create_business(db, owner=u)
    await create_subscription(db, business=biz)
    result = await start_upgrade(
        db,
        business=biz,
        contact_phone=u.phone,
        contact_name="Owner",
        target_plan=PlanType.STARTER,
    )
    assert "id" in result


async def test_apply_activation_no_match(db):
    out = await apply_subscription_activation(
        db, "sub_not_found", {"notes": {"target_plan": "starter"}}
    )
    assert out is None


async def test_apply_activation_promotes_to_active(db):
    u = await create_user(db, phone="+919000003003")
    biz = await create_business(db, owner=u)
    sub = await create_subscription(db, business=biz)
    sub.razorpay_subscription_id = "sub_xyz"
    await db.commit()

    out = await apply_subscription_activation(
        db, "sub_xyz", {"notes": {"target_plan": "growth"}}
    )
    assert out is not None
    assert out.status == SubscriptionStatus.ACTIVE
    assert out.plan == PlanType.GROWTH


async def test_apply_activation_invalid_target_plan(db):
    u = await create_user(db, phone="+919000003004")
    biz = await create_business(db, owner=u)
    sub = await create_subscription(db, business=biz)
    sub.razorpay_subscription_id = "sub_abc"
    await db.commit()
    out = await apply_subscription_activation(
        db, "sub_abc", {"notes": {"target_plan": "bogus"}}
    )
    assert out is not None  # returns sub unchanged


async def test_apply_cancel_marks_canceled(db):
    u = await create_user(db, phone="+919000003005")
    biz = await create_business(db, owner=u)
    sub = await create_subscription(db, business=biz)
    sub.razorpay_subscription_id = "sub_cancel_me"
    await db.commit()

    out = await apply_subscription_cancel(db, "sub_cancel_me")
    assert out is not None
    assert out.status == SubscriptionStatus.CANCELED


async def test_apply_cancel_no_match(db):
    assert await apply_subscription_cancel(db, "sub_missing") is None
