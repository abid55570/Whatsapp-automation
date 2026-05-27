"""Tests for RazorpayClient methods that hit external API (mocked)."""
import httpx
import pytest

from app.services.payments.razorpay_client import (
    RazorpayClient,
    RazorpayError,
)


def _make_client_with_handler(monkeypatch, handler):
    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)


async def test_create_payment_link_success(monkeypatch):
    def handler(req):
        return httpx.Response(
            200,
            json={
                "id": "plink_test123",
                "short_url": "https://rzp.io/i/test",
                "status": "created",
            },
        )

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="rzp_id", key_secret="rzp_sec")
    result = await client.create_payment_link(
        amount_paise=10000,
        customer_name="Test",
        customer_phone="+919876543210",
        description="Order",
        order_id="order_uuid",
        business_id="biz_uuid",
        callback_url="https://example.com/cb",
    )
    assert result["id"] == "plink_test123"


async def test_create_payment_link_no_credentials(monkeypatch):
    from app.services.payments import razorpay_client as rc
    monkeypatch.setattr(rc.settings, "RAZORPAY_KEY_ID", "")
    monkeypatch.setattr(rc.settings, "RAZORPAY_KEY_SECRET", "")
    client = RazorpayClient(key_id="", key_secret="")
    with pytest.raises(RazorpayError):
        await client.create_payment_link(
            amount_paise=100,
            customer_name="X",
            customer_phone="9999999999",
            description="d",
            order_id="o",
            business_id="b",
        )


async def test_create_subscription_no_plan():
    client = RazorpayClient(key_id="k", key_secret="s")
    with pytest.raises(RazorpayError):
        await client.create_subscription(
            plan_id="", customer_phone="+91999", customer_name=None
        )


async def test_create_subscription_success(monkeypatch):
    def handler(req):
        return httpx.Response(
            200,
            json={
                "id": "sub_xxx",
                "short_url": "https://rzp.io/i/sub",
                "status": "created",
            },
        )

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="k", key_secret="s")
    result = await client.create_subscription(
        plan_id="plan_starter",
        customer_phone="+919999999999",
        customer_name="X",
        notes={"biz": "1"},
    )
    assert result["id"] == "sub_xxx"


async def test_cancel_payment_link(monkeypatch):
    def handler(req):
        return httpx.Response(200, json={"id": "plink_abc", "status": "cancelled"})

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="k", key_secret="s")
    out = await client.cancel_payment_link("plink_abc")
    assert out["status"] == "cancelled"


async def test_cancel_subscription(monkeypatch):
    def handler(req):
        return httpx.Response(200, json={"id": "sub_x", "status": "cancelled"})

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="k", key_secret="s")
    out = await client.cancel_subscription("sub_x", cancel_at_cycle_end=False)
    assert out["status"] == "cancelled"


async def test_fetch_payment_link(monkeypatch):
    def handler(req):
        return httpx.Response(200, json={"id": "plink_xxx", "status": "paid"})

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="k", key_secret="s")
    out = await client.fetch_payment_link("plink_xxx")
    assert out["id"] == "plink_xxx"


async def test_fetch_subscription(monkeypatch):
    def handler(req):
        return httpx.Response(200, json={"id": "sub_y", "status": "active"})

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="k", key_secret="s")
    out = await client.fetch_subscription("sub_y")
    assert out["status"] == "active"


async def test_http_error_on_post_raises(monkeypatch):
    """POST path catches HTTPStatusError → RazorpayError."""
    def handler(req):
        return httpx.Response(400, text="bad request")

    _make_client_with_handler(monkeypatch, handler)
    client = RazorpayClient(key_id="k", key_secret="s")
    with pytest.raises(RazorpayError):
        await client.create_payment_link(
            amount_paise=100,
            customer_name="X",
            customer_phone="+919999999999",
            description="d",
            order_id="o",
            business_id="b",
        )
