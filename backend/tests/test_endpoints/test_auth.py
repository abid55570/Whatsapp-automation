"""Integration tests for /api/v1/auth endpoints."""
from tests.conftest import auth_headers


async def test_start_verification(client):
    resp = await client.post(
        "/api/v1/auth/start-verification",
        json={"phone": "+919876543210", "full_name": "Test"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "verification_id" in data
    assert data["deep_link"].startswith("https://wa.me/")
    assert data["dev_code"] is not None  # development mode


async def test_start_verification_invalid_phone(client):
    resp = await client.post(
        "/api/v1/auth/start-verification",
        json={"phone": "12345"},
    )
    assert resp.status_code == 422


async def test_verification_status_pending(client):
    r1 = await client.post(
        "/api/v1/auth/start-verification",
        json={"phone": "+919876544321"},
    )
    vid = r1.json()["verification_id"]
    r2 = await client.get(f"/api/v1/auth/verification-status/{vid}")
    assert r2.status_code == 200
    assert r2.json()["status"] == "pending"


async def test_verification_status_not_found(client):
    fake = "00000000-0000-0000-0000-000000000000"
    resp = await client.get(f"/api/v1/auth/verification-status/{fake}")
    assert resp.status_code == 404


async def test_dev_simulate_verify_completes_flow(client):
    """End-to-end: start → simulate → status returns verified + token."""
    r1 = await client.post(
        "/api/v1/auth/start-verification",
        json={"phone": "+919876500077"},
    )
    code = r1.json()["dev_code"]
    vid = r1.json()["verification_id"]

    r2 = await client.post(
        "/api/v1/auth/dev/simulate-whatsapp-verify",
        params={"phone": "+919876500077", "code": code},
    )
    assert r2.status_code == 200
    assert r2.json()["status"] == "verified"

    r3 = await client.get(f"/api/v1/auth/verification-status/{vid}")
    assert r3.json()["status"] == "verified"
    assert r3.json()["access_token"]
    assert r3.json()["user"]["phone"] == "+919876500077"


async def test_dev_simulate_bad_code(client):
    await client.post(
        "/api/v1/auth/start-verification",
        json={"phone": "+919876500088"},
    )
    r = await client.post(
        "/api/v1/auth/dev/simulate-whatsapp-verify",
        params={"phone": "+919876500088", "code": "wrong"},
    )
    assert r.json()["status"] == "failed"


async def test_get_me_requires_auth(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


async def test_get_me_returns_user(client, authed_user):
    resp = await client.get("/api/v1/auth/me", headers=auth_headers(authed_user))
    assert resp.status_code == 200
    assert resp.json()["phone"] == authed_user.phone


async def test_update_me(client, authed_user):
    resp = await client.patch(
        "/api/v1/auth/me",
        json={"full_name": "New Name", "preferred_language": "hi"},
        headers=auth_headers(authed_user),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["full_name"] == "New Name"
    assert body["preferred_language"] == "hi"


async def test_logout(client, authed_user):
    resp = await client.post(
        "/api/v1/auth/logout", headers=auth_headers(authed_user)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "logged_out"


async def test_invalid_token_rejected(client):
    resp = await client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer garbage"}
    )
    assert resp.status_code == 401
