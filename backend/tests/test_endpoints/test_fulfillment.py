"""Tests for /api/v1/businesses/me/fulfillment-config."""
from tests.conftest import auth_headers


async def test_get_fulfillment_config(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/fulfillment-config",
        headers=auth_headers(authed_user),
    )
    # 200 if auto-created, 404 if not
    assert resp.status_code in (200, 404)


async def test_update_fulfillment_config(client, authed_user, business):
    resp = await client.put(
        "/api/v1/businesses/me/fulfillment-config",
        json={
            "pickup_enabled": True,
            "pickup_hours_start": "09:00",
            "pickup_hours_end": "21:00",
            "pickup_prep_strategy": "fixed",
            "pickup_fixed_minutes": 30,
            "delivery_enabled": False,
        },
        headers=auth_headers(authed_user),
    )
    assert resp.status_code in (200, 201)
    if resp.status_code in (200, 201):
        data = resp.json()
        assert data["pickup_enabled"] is True
        assert data["pickup_prep_strategy"] == "fixed"
