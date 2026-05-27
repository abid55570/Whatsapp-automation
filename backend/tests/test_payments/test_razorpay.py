"""Tests for Razorpay signature verification + client."""
import hashlib
import hmac
import json

import httpx
import pytest

from app.services.payments.razorpay_client import (
    RazorpayClient,
    RazorpayError,
    verify_razorpay_signature,
)


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


class TestSignature:
    def test_valid(self):
        secret = "test_secret"
        body = b'{"event":"payment_link.paid"}'
        sig = _sign(body, secret)
        assert verify_razorpay_signature(body, sig, secret) is True

    def test_invalid_signature(self):
        body = b'{"event":"payment_link.paid"}'
        assert verify_razorpay_signature(body, "wrong", "secret") is False

    def test_missing_signature(self):
        body = b'{"x":1}'
        assert verify_razorpay_signature(body, "", "secret") is False

    def test_missing_secret(self):
        body = b'{"x":1}'
        assert verify_razorpay_signature(body, "anysig", "") is False

    def test_tampered_payload(self):
        secret = "s"
        original = b'{"amount":100}'
        tampered = b'{"amount":9999}'
        sig = _sign(original, secret)
        assert verify_razorpay_signature(tampered, sig, secret) is False


@pytest.mark.asyncio
class TestCreatePaymentLink:
    async def test_constructs_correct_request(self):
        captured: dict = {}

        def handler(request: httpx.Request) -> httpx.Response:
            captured["url"] = str(request.url)
            captured["auth"] = request.headers.get("authorization")
            captured["body"] = json.loads(request.content)
            return httpx.Response(
                200,
                json={
                    "id": "plink_xyz",
                    "short_url": "https://rzp.io/abc",
                    "status": "created",
                },
            )

        client = RazorpayClient(
            key_id="rzp_test_xxx",
            key_secret="secretxxx",
            transport=httpx.MockTransport(handler),
        )
        result = await client.create_payment_link(
            amount_paise=70000,
            customer_name="Ramesh",
            customer_phone="+919876543210",
            description="Order #ORD-123",
            order_id="uuid-1",
            business_id="uuid-2",
        )
        assert captured["url"].endswith("/payment_links")
        assert captured["auth"].startswith("Basic ")
        assert captured["body"]["amount"] == 70000
        assert captured["body"]["currency"] == "INR"
        assert captured["body"]["customer"]["name"] == "Ramesh"
        assert captured["body"]["customer"]["contact"] == "+919876543210"
        assert captured["body"]["notes"]["order_id"] == "uuid-1"
        assert result["id"] == "plink_xyz"

    async def test_raises_on_error(self):
        def handler(request):
            return httpx.Response(400, json={"error": "bad request"})

        client = RazorpayClient(
            key_id="x",
            key_secret="y",
            transport=httpx.MockTransport(handler),
        )
        with pytest.raises(RazorpayError):
            await client.create_payment_link(
                amount_paise=100,
                customer_name=None,
                customer_phone="+91999",
                description="x",
                order_id="x",
                business_id="y",
            )

    async def test_requires_credentials(self):
        client = RazorpayClient(key_id="", key_secret="")
        with pytest.raises(RazorpayError):
            await client.create_payment_link(
                amount_paise=100,
                customer_name=None,
                customer_phone="+91999",
                description="x",
                order_id="x",
                business_id="y",
            )
