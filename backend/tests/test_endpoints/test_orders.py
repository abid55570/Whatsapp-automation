"""Tests for /api/v1/businesses/me/orders."""
from app.models import Order
from app.models.enums import (
    FulfillmentType,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)
from tests.conftest import auth_headers, create_contact


async def _make_order(db, business, contact, *, status=OrderStatus.NEW):
    order = Order(
        business_id=business.id,
        contact_id=contact.id,
        order_number=f"ORD-{status.value}",
        status=status,
        payment_status=PaymentStatus.PENDING,
        fulfillment_type=FulfillmentType.PICKUP,
        payment_method=PaymentMethod.CASH_ON_PICKUP,
        total_paise=10000,
        items_count=1,
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order


async def test_list_orders(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    await _make_order(db, business, c)
    resp = await client.get(
        "/api/v1/businesses/me/orders",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


async def test_get_order(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    order = await _make_order(db, business, c)
    resp = await client.get(
        f"/api/v1/businesses/me/orders/{order.id}",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == str(order.id)


async def test_update_order_status(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    order = await _make_order(db, business, c, status=OrderStatus.NEW)
    resp = await client.patch(
        f"/api/v1/businesses/me/orders/{order.id}",
        json={"status": "confirmed", "notes": "Approved"},
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"


async def test_orders_filter(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    await _make_order(db, business, c, status=OrderStatus.COMPLETED)
    resp = await client.get(
        "/api/v1/businesses/me/orders?filter=completed",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
