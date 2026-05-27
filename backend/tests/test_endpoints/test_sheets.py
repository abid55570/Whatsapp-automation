"""Tests for /api/v1/businesses/me/sheets."""
from tests.conftest import auth_headers


async def test_list_sheets_empty(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/sheets",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.json() == []


async def test_create_sheet_bad_url(client, authed_user, business):
    resp = await client.post(
        "/api/v1/businesses/me/sheets",
        json={
            "sheet_url": "not a url",
            "sheet_type": "faqs",
        },
        headers=auth_headers(authed_user),
    )
    # validation OR 400 depending on implementation
    assert resp.status_code in (400, 422)
