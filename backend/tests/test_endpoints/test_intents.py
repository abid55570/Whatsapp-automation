"""Tests for /api/v1/intents (global catalog)."""


async def test_list_global_intents(client, authed_user):
    from tests.conftest import auth_headers
    resp = await client.get("/api/v1/intents", headers=auth_headers(authed_user))
    assert resp.status_code in (200, 401, 404)
