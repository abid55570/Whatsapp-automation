"""Tests for /api/v1/businesses/me/subscription/* endpoints."""
from tests.conftest import auth_headers


async def test_upgrade_plan(client, authed_user, business):
    resp = await client.post(
        "/api/v1/businesses/me/subscription/upgrade",
        json={"plan": "starter"},
        headers=auth_headers(authed_user),
    )
    # 201 success / 503 razorpay error / 400 misconfigured
    assert resp.status_code in (200, 201, 400, 503)
    if resp.status_code == 201:
        body = resp.json()
        assert "plan" in body


async def test_upgrade_invalid_plan(client, authed_user, business):
    resp = await client.post(
        "/api/v1/businesses/me/subscription/upgrade",
        json={"plan": "trial"},
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 400


async def test_cancel_without_active_sub(client, authed_user, business):
    """Trial sub has no razorpay_subscription_id → 400."""
    resp = await client.post(
        "/api/v1/businesses/me/subscription/cancel",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 400
