"""Integration tests for HSN-suggest + e-invoice + ITR-4 endpoints."""
from app.models.enums import GstScheme
from tests.conftest import auth_headers


# ============================================================
# HSN suggest endpoint
# ============================================================


async def test_hsn_suggest_endpoint(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/hsn-suggest?q=atta",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "atta"
    assert len(data["results"]) >= 1
    assert data["results"][0]["code"] == "1101"


async def test_hsn_suggest_unknown(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/hsn-suggest?q=xyz_nothing_matches_123",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["results"] == [] or all(r["score"] >= 60 for r in data["results"])


async def test_hsn_suggest_requires_auth(client):
    resp = await client.get("/api/v1/businesses/me/hsn-suggest?q=rice")
    assert resp.status_code == 401


# ============================================================
# e-invoice endpoint
# ============================================================


async def test_einvoice_not_applicable_for_b2c(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    business.gstin = "27AAPFU0939F1ZV"
    business.gst_state_code = "27"
    await db.commit()

    # Create a B2C invoice
    r1 = await client.post(
        "/api/v1/businesses/me/invoices",
        json={
            "cx_state_code": "27",
            "lines": [
                {"description": "x", "quantity": "1", "rate_paise": 1000, "gst_rate": 18},
            ],
        },
        headers=auth_headers(authed_user),
    )
    invoice_id = r1.json()["id"]

    r2 = await client.post(
        f"/api/v1/businesses/me/invoices/{invoice_id}/einvoice",
        headers=auth_headers(authed_user),
    )
    assert r2.status_code == 400
    assert "not eligible" in r2.json()["detail"].lower()


async def test_einvoice_not_found(client, authed_user, business):
    fake = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(
        f"/api/v1/businesses/me/invoices/{fake}/einvoice",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 404


# ============================================================
# ITR-4 endpoint
# ============================================================


async def test_itr4_endpoint(client, authed_user, business, db):
    business.gst_scheme = GstScheme.REGULAR
    await db.commit()

    resp = await client.get(
        "/api/v1/businesses/me/reports/itr4?fy=2026-27",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"
    assert resp.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument"
    )


async def test_itr4_invalid_fy(client, authed_user, business):
    resp = await client.get(
        "/api/v1/businesses/me/reports/itr4?fy=not-a-fy",
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 400


async def test_itr4_requires_auth(client):
    resp = await client.get("/api/v1/businesses/me/reports/itr4?fy=2026-27")
    assert resp.status_code == 401
