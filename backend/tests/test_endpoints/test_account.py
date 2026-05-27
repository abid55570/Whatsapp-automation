"""Tests for /api/v1/account (DPDP: export, delete)."""
from tests.conftest import auth_headers


async def test_export_returns_zip(client, authed_user, business):
    resp = await client.get(
        "/api/v1/account/export", headers=auth_headers(authed_user)
    )
    assert resp.status_code == 200
    assert (
        resp.headers.get("content-type", "").startswith("application/")
    )


async def test_delete_account_requires_confirm(client, authed_user):
    resp = await client.delete(
        "/api/v1/account/me", headers=auth_headers(authed_user)
    )
    assert resp.status_code in (400, 422)


async def test_delete_account_with_confirm(client, authed_user):
    resp = await client.delete(
        "/api/v1/account/me",
        params={"confirm": "DELETE"},
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "soft_deleted"
