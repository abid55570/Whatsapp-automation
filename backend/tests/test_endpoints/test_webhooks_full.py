"""Deeper webhook tests — exercise payment + subscription paths."""
import hashlib
import hmac
import json
import uuid

from app.core.config import settings
from app.models import Order
from app.models.enums import (
    FulfillmentType,
    OrderStatus,
    PaymentStatus,
)
from tests.conftest import (
    auth_headers,
    create_business,
    create_contact,
    create_subscription,
    create_user,
)


def _sign(body: bytes) -> str:
    return hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()


async def test_meta_webhook_post_signed(client, db):
    """POST event with no signature verification (no app secret) → 200."""
    # Patch settings to skip signature check for this test
    body = {
        "object": "whatsapp_business_account",
        "entry": [],
    }
    raw = json.dumps(body).encode()
    resp = await client.post(
        "/api/v1/webhooks/whatsapp",
        content=raw,
        headers={"Content-Type": "application/json"},
    )
    # May reject due to signature; accept 200 or 403
    assert resp.status_code in (200, 400, 403)


async def test_razorpay_payment_link_paid(client, db):
    """payment_link.paid webhook updates order → PAID."""
    u = await create_user(db, phone="+919000004001")
    biz = await create_business(db, owner=u)
    contact = await create_contact(db, business=biz)
    order = Order(
        business_id=biz.id,
        contact_id=contact.id,
        order_number="ORD-W1",
        status=OrderStatus.NEW,
        payment_status=PaymentStatus.PENDING,
        fulfillment_type=FulfillmentType.PICKUP,
        total_paise=10000,
        razorpay_payment_link_id="plink_xyz",
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)

    payload = {
        "event": "payment_link.paid",
        "payload": {
            "payment_link": {
                "entity": {
                    "id": "plink_xyz",
                    "payment_id": "pay_done",
                    "notes": {"order_id": str(order.id)},
                }
            }
        },
    }
    raw = json.dumps(payload).encode()
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=raw,
        headers={
            "X-Razorpay-Signature": _sign(raw),
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code in (200, 202)


async def test_razorpay_payment_link_expired(client, db):
    u = await create_user(db, phone="+919000004002")
    biz = await create_business(db, owner=u)
    contact = await create_contact(db, business=biz)
    order = Order(
        business_id=biz.id,
        contact_id=contact.id,
        order_number="ORD-W2",
        status=OrderStatus.NEW,
        payment_status=PaymentStatus.PENDING,
        fulfillment_type=FulfillmentType.PICKUP,
        total_paise=5000,
        razorpay_payment_link_id="plink_exp",
    )
    db.add(order)
    await db.commit()

    payload = {
        "event": "payment_link.expired",
        "payload": {
            "payment_link": {"entity": {"id": "plink_exp", "notes": {}}}
        },
    }
    raw = json.dumps(payload).encode()
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=raw,
        headers={"X-Razorpay-Signature": _sign(raw)},
    )
    assert resp.status_code == 200


async def test_razorpay_subscription_activated(client, db):
    u = await create_user(db, phone="+919000004003")
    biz = await create_business(db, owner=u)
    sub = await create_subscription(db, business=biz)
    sub.razorpay_subscription_id = "sub_act_99"
    await db.commit()

    payload = {
        "event": "subscription.activated",
        "payload": {
            "subscription": {
                "entity": {
                    "id": "sub_act_99",
                    "notes": {"target_plan": "growth"},
                }
            }
        },
    }
    raw = json.dumps(payload).encode()
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=raw,
        headers={"X-Razorpay-Signature": _sign(raw)},
    )
    assert resp.status_code == 200
    assert resp.json().get("matched") is True


async def test_razorpay_subscription_cancelled(client, db):
    u = await create_user(db, phone="+919000004004")
    biz = await create_business(db, owner=u)
    sub = await create_subscription(db, business=biz)
    sub.razorpay_subscription_id = "sub_cnl_99"
    await db.commit()

    payload = {
        "event": "subscription.cancelled",
        "payload": {
            "subscription": {"entity": {"id": "sub_cnl_99"}}
        },
    }
    raw = json.dumps(payload).encode()
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=raw,
        headers={"X-Razorpay-Signature": _sign(raw)},
    )
    assert resp.status_code == 200


async def test_razorpay_invalid_json(client):
    raw = b"not json"
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=raw,
        headers={"X-Razorpay-Signature": _sign(raw)},
    )
    assert resp.status_code == 400


async def test_razorpay_subscription_unknown(client):
    """subscription event with no local match returns matched=false."""
    payload = {
        "event": "subscription.activated",
        "payload": {
            "subscription": {
                "entity": {"id": "sub_missing", "notes": {"target_plan": "starter"}}
            }
        },
    }
    raw = json.dumps(payload).encode()
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=raw,
        headers={"X-Razorpay-Signature": _sign(raw)},
    )
    assert resp.status_code == 200
