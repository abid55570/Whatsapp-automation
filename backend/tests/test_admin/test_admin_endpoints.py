"""Integration tests for /api/v1/admin endpoints (superuser-only)."""
from datetime import datetime, timezone

import pytest

from app.models import WebhookEvent
from tests.conftest import (
    auth_headers,
    create_business,
    create_subscription,
    create_user,
)


# ============================================================
# Auth guard
# ============================================================


async def test_admin_requires_authentication(client):
    """No bearer token → 401."""
    resp = await client.get("/api/v1/admin/stats")
    assert resp.status_code == 401


async def test_admin_requires_superuser(client, authed_user):
    """Regular user → 403."""
    resp = await client.get(
        "/api/v1/admin/stats", headers=auth_headers(authed_user)
    )
    assert resp.status_code == 403
    assert "Superuser" in resp.json()["detail"]


async def test_admin_grants_superuser_access(client, superuser):
    resp = await client.get(
        "/api/v1/admin/stats", headers=auth_headers(superuser)
    )
    assert resp.status_code == 200


# ============================================================
# /admin/stats
# ============================================================


async def test_stats_empty(client, superuser):
    resp = await client.get(
        "/api/v1/admin/stats", headers=auth_headers(superuser)
    )
    assert resp.status_code == 200
    data = resp.json()
    # superuser fixture itself is counted
    assert data["total_users"] >= 1
    assert data["superusers"] >= 1
    assert data["total_businesses"] == 0
    assert data["plan_breakdown"] == {}


async def test_stats_with_data(client, superuser, db):
    """Stats aggregate users, businesses, subscriptions, orders."""
    from app.models import Order
    from app.models.enums import OrderStatus, PaymentStatus, PlanType, SubscriptionStatus

    u = await create_user(db, phone="+919876511111")
    biz = await create_business(db, owner=u, onboarding_completed=True)
    await create_subscription(
        db,
        business=biz,
        plan=PlanType.GROWTH,
        status=SubscriptionStatus.ACTIVE,
        conversations_included=3000,
    )

    # add a paid order
    from app.models import Contact
    contact = Contact(
        business_id=biz.id, whatsapp_phone="+919999000000", name="X"
    )
    db.add(contact)
    await db.commit()
    await db.refresh(contact)

    order = Order(
        business_id=biz.id,
        contact_id=contact.id,
        order_number="ORD-1",
        status=OrderStatus.COMPLETED,
        payment_status=PaymentStatus.PAID,
        total_paise=50000,
    )
    db.add(order)
    await db.commit()

    resp = await client.get(
        "/api/v1/admin/stats", headers=auth_headers(superuser)
    )
    data = resp.json()
    assert data["total_businesses"] == 1
    assert data["onboarded_businesses"] == 1
    assert data["active_subs"] == 1
    assert data["plan_breakdown"].get("growth") == 1
    assert data["total_orders"] == 1
    assert data["paid_orders"] == 1
    assert data["total_revenue_paise"] == 50000


# ============================================================
# /admin/users
# ============================================================


async def test_list_users_pagination(client, superuser, db):
    for i in range(3):
        await create_user(db, phone=f"+9198000000{i:02d}")

    resp = await client.get(
        "/api/v1/admin/users?limit=10",
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 4  # 3 + superuser
    assert len(data["items"]) >= 4


async def test_list_users_search(client, superuser, db):
    await create_user(db, phone="+919876549999", full_name="Findable Person")
    await create_user(db, phone="+919876548888", full_name="Other")

    resp = await client.get(
        "/api/v1/admin/users?q=findable",
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 200
    names = [u["full_name"] for u in resp.json()["items"]]
    assert "Findable Person" in names


async def test_update_user_grant_superuser(client, superuser, db):
    target = await create_user(db, phone="+919876510101")
    resp = await client.patch(
        f"/api/v1/admin/users/{target.id}",
        json={"is_superuser": True},
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 200
    assert resp.json()["is_superuser"] is True


async def test_update_user_deactivate(client, superuser, db):
    target = await create_user(db, phone="+919876510202")
    resp = await client.patch(
        f"/api/v1/admin/users/{target.id}",
        json={"is_active": False},
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


async def test_update_user_not_found(client, superuser):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.patch(
        f"/api/v1/admin/users/{fake_id}",
        json={"is_active": False},
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 404


async def test_update_user_cannot_revoke_self(client, superuser):
    resp = await client.patch(
        f"/api/v1/admin/users/{superuser.id}",
        json={"is_superuser": False},
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 400


async def test_update_user_cannot_deactivate_self(client, superuser):
    resp = await client.patch(
        f"/api/v1/admin/users/{superuser.id}",
        json={"is_active": False},
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 400


# ============================================================
# /admin/businesses
# ============================================================


async def test_list_businesses(client, superuser, db):
    u = await create_user(db, phone="+919876500099")
    biz = await create_business(db, owner=u, name="My Kirana")
    await create_subscription(db, business=biz)

    resp = await client.get(
        "/api/v1/admin/businesses", headers=auth_headers(superuser)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "My Kirana"
    # plan may be None depending on relationship load
    assert data["items"][0]["plan"] in (None, "trial")


async def test_list_businesses_search(client, superuser, db):
    u1 = await create_user(db, phone="+919876511110")
    u2 = await create_user(db, phone="+919876511111")
    await create_business(db, owner=u1, name="Sharma Kirana")
    await create_business(db, owner=u2, name="Other Shop")

    resp = await client.get(
        "/api/v1/admin/businesses?q=sharma",
        headers=auth_headers(superuser),
    )
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Sharma Kirana"


# ============================================================
# /admin/subscriptions
# ============================================================


async def test_list_subscriptions(client, superuser, db):
    from app.models.enums import PlanType, SubscriptionStatus

    u = await create_user(db, phone="+919876522222")
    biz = await create_business(db, owner=u)
    await create_subscription(
        db, business=biz, plan=PlanType.STARTER, status=SubscriptionStatus.ACTIVE
    )

    resp = await client.get(
        "/api/v1/admin/subscriptions", headers=auth_headers(superuser)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["plan"] == "starter"


async def test_list_subscriptions_filter(client, superuser, db):
    from app.models.enums import PlanType, SubscriptionStatus

    u1 = await create_user(db, phone="+919876533331")
    u2 = await create_user(db, phone="+919876533332")
    b1 = await create_business(db, owner=u1)
    b2 = await create_business(db, owner=u2)
    await create_subscription(db, business=b1, status=SubscriptionStatus.ACTIVE)
    await create_subscription(db, business=b2, status=SubscriptionStatus.FROZEN)

    resp = await client.get(
        "/api/v1/admin/subscriptions?status=frozen",
        headers=auth_headers(superuser),
    )
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["status"] == "frozen"


async def test_list_subscriptions_invalid_status(client, superuser):
    resp = await client.get(
        "/api/v1/admin/subscriptions?status=bogus",
        headers=auth_headers(superuser),
    )
    assert resp.status_code == 400


# ============================================================
# /admin/webhook-events
# ============================================================


async def test_list_webhook_events(client, superuser, db):
    ev = WebhookEvent(
        source="razorpay",
        event_type="subscription.activated",
        signature_verified=True,
        processed=True,
        received_at=datetime.now(timezone.utc),
        payload={"foo": "bar"},
    )
    db.add(ev)
    await db.commit()

    resp = await client.get(
        "/api/v1/admin/webhook-events", headers=auth_headers(superuser)
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["source"] == "razorpay"


async def test_list_webhook_events_source_filter(client, superuser, db):
    db.add_all([
        WebhookEvent(
            source="razorpay",
            event_type="payment.captured",
            signature_verified=True,
            processed=True,
            received_at=datetime.now(timezone.utc),
            payload={},
        ),
        WebhookEvent(
            source="meta_whatsapp",
            event_type="messages",
            signature_verified=True,
            processed=True,
            received_at=datetime.now(timezone.utc),
            payload={},
        ),
    ])
    await db.commit()

    resp = await client.get(
        "/api/v1/admin/webhook-events?source=meta_whatsapp",
        headers=auth_headers(superuser),
    )
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["source"] == "meta_whatsapp"
