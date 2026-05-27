"""Tests for /api/v1/webhooks (Meta + Razorpay)."""
import hashlib
import hmac
import json

from app.core.config import settings


async def test_meta_webhook_verify_challenge(client):
    """Meta verify challenge — GET with hub.challenge."""
    resp = await client.get(
        "/api/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": settings.META_WEBHOOK_VERIFY_TOKEN,
            "hub.challenge": "1234567890",
        },
    )
    assert resp.status_code == 200
    assert resp.text == "1234567890"


async def test_meta_webhook_wrong_token(client):
    resp = await client.get(
        "/api/v1/webhooks/whatsapp",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong",
            "hub.challenge": "abc",
        },
    )
    assert resp.status_code == 403


async def test_razorpay_webhook_unsigned(client):
    """No signature header → reject."""
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        json={"event": "payment.captured"},
    )
    assert resp.status_code in (400, 401, 403)


async def test_razorpay_webhook_valid_signature(client):
    body = json.dumps({"event": "payment.captured", "payload": {}}).encode()
    sig = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256,
    ).hexdigest()
    resp = await client.post(
        "/api/v1/webhooks/razorpay",
        content=body,
        headers={
            "X-Razorpay-Signature": sig,
            "Content-Type": "application/json",
        },
    )
    assert resp.status_code in (200, 202)
