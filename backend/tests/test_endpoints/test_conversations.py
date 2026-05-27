"""Tests for /api/v1/conversations."""
from tests.conftest import (
    auth_headers,
    create_contact,
    create_conversation,
    create_message,
)


async def test_list_conversations(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    conv = await create_conversation(db, business=business, contact=c)
    await create_message(db, business=business, conversation=conv)

    resp = await client.get(
        "/api/v1/conversations", headers=auth_headers(authed_user)
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


async def test_get_conversation(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    conv = await create_conversation(db, business=business, contact=c)
    resp = await client.get(
        f"/api/v1/conversations/{conv.id}",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == str(conv.id)


async def test_get_messages(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    conv = await create_conversation(db, business=business, contact=c)
    await create_message(db, business=business, conversation=conv, body="hello")
    resp = await client.get(
        f"/api/v1/conversations/{conv.id}/messages",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


async def test_mark_read(client, authed_user, business, db):
    c = await create_contact(db, business=business)
    conv = await create_conversation(db, business=business, contact=c)
    resp = await client.post(
        f"/api/v1/conversations/{conv.id}/mark-read",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code in (200, 204)
