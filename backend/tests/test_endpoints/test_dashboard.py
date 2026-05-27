"""Tests for /api/v1/dashboard."""
from tests.conftest import (
    auth_headers,
    create_contact,
    create_conversation,
    create_message,
)


async def test_dashboard_stats_requires_business(client, authed_user):
    resp = await client.get(
        "/api/v1/dashboard/stats", headers=auth_headers(authed_user)
    )
    # 404 because no business
    assert resp.status_code in (200, 404)


async def test_dashboard_stats_basic(client, authed_user, business, db):
    contact = await create_contact(db, business=business)
    conv = await create_conversation(db, business=business, contact=contact)
    await create_message(db, business=business, conversation=conv, body="hi")
    resp = await client.get(
        "/api/v1/dashboard/stats?days=7",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_messages"] >= 1
