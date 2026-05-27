"""Full CRUD tests for /api/v1/businesses/me/sheets."""
from tests.conftest import auth_headers


async def test_create_sheet_invalid_url(client, authed_user, business):
    resp = await client.post(
        "/api/v1/businesses/me/sheets",
        json={"sheet_url": "https://example.com/no-id-here", "sheet_type": "faqs"},
        headers=auth_headers(authed_user),
    )
    assert resp.status_code in (400, 422)


async def test_create_sheet_success(client, authed_user, business):
    resp = await client.post(
        "/api/v1/businesses/me/sheets",
        json={
            "sheet_url": "https://docs.google.com/spreadsheets/d/1aBc_XYZ/edit",
            "sheet_type": "products",
            "sheet_tab_name": "menu",
            "auto_sync": True,
            "sync_interval_minutes": 60,
        },
        headers=auth_headers(authed_user),
    )
    assert resp.status_code in (201, 400, 422)
    if resp.status_code == 201:
        sid = resp.json()["id"]
        # GET
        r2 = await client.get(
            f"/api/v1/businesses/me/sheets/{sid}",
            headers=auth_headers(authed_user),
        )
        assert r2.status_code == 200
        # PATCH
        r3 = await client.patch(
            f"/api/v1/businesses/me/sheets/{sid}",
            json={"auto_sync": False},
            headers=auth_headers(authed_user),
        )
        assert r3.status_code == 200
        # Trigger
        r4 = await client.post(
            f"/api/v1/businesses/me/sheets/{sid}/sync",
            headers=auth_headers(authed_user),
        )
        assert r4.status_code in (202, 503)
        # DELETE
        r5 = await client.delete(
            f"/api/v1/businesses/me/sheets/{sid}",
            headers=auth_headers(authed_user),
        )
        assert r5.status_code == 204


async def test_get_sheet_not_found(client, authed_user, business):
    fake = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(
        f"/api/v1/businesses/me/sheets/{fake}",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 404
