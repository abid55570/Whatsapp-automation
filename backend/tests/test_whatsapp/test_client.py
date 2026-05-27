"""Tests for the WhatsApp Cloud API client (using httpx MockTransport)."""
import json

import httpx
import pytest

from app.services.whatsapp.client import WhatsAppClient, WhatsAppClientError


def _success_response(message_id: str = "wamid.outbound_test") -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "messaging_product": "whatsapp",
            "contacts": [{"input": "919876543210", "wa_id": "919876543210"}],
            "messages": [{"id": message_id}],
        },
    )


# ======================================================================
# URL + headers
# ======================================================================


def test_messages_url_includes_phone_id():
    client = WhatsAppClient("PHONE_123", "TOKEN_XYZ", api_version="v21.0")
    assert client.messages_url.endswith("/v21.0/PHONE_123/messages")


def test_headers_have_bearer_token():
    client = WhatsAppClient("P", "MY_SECRET_TOKEN")
    assert client.headers["Authorization"] == "Bearer MY_SECRET_TOKEN"
    assert client.headers["Content-Type"] == "application/json"


# ======================================================================
# Sending — request construction
# ======================================================================


@pytest.mark.asyncio
async def test_send_text_posts_correct_payload():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["method"] = request.method
        captured["auth"] = request.headers.get("authorization")
        captured["body"] = json.loads(request.content)
        return _success_response()

    transport = httpx.MockTransport(handler)
    client = WhatsAppClient("PHONE_ID", "TOKEN", transport=transport)

    result = await client.send_text(to="919876543210", body="Hello!")

    assert captured["method"] == "POST"
    assert "/PHONE_ID/messages" in captured["url"]
    assert captured["auth"] == "Bearer TOKEN"
    assert captured["body"]["messaging_product"] == "whatsapp"
    assert captured["body"]["to"] == "919876543210"
    assert captured["body"]["type"] == "text"
    assert captured["body"]["text"]["body"] == "Hello!"
    assert result["messages"][0]["id"] == "wamid.outbound_test"


@pytest.mark.asyncio
async def test_send_image_with_url():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return _success_response()

    client = WhatsAppClient(
        "PHONE", "TOKEN", transport=httpx.MockTransport(handler)
    )
    await client.send_image(
        to="919999999999",
        image_url="https://example.com/img.jpg",
        caption="Check this out",
    )
    assert captured["body"]["type"] == "image"
    assert captured["body"]["image"]["link"] == "https://example.com/img.jpg"
    assert captured["body"]["image"]["caption"] == "Check this out"


@pytest.mark.asyncio
async def test_send_image_requires_url_or_id():
    client = WhatsAppClient("PHONE", "TOKEN")
    with pytest.raises(ValueError):
        await client.send_image(to="919999999999")


@pytest.mark.asyncio
async def test_send_template():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return _success_response()

    client = WhatsAppClient(
        "PHONE", "TOKEN", transport=httpx.MockTransport(handler)
    )
    await client.send_template(
        to="919999999999",
        template_name="order_confirmation",
        language_code="en_US",
    )
    assert captured["body"]["type"] == "template"
    assert captured["body"]["template"]["name"] == "order_confirmation"
    assert captured["body"]["template"]["language"]["code"] == "en_US"


@pytest.mark.asyncio
async def test_mark_as_read():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        return _success_response()

    client = WhatsAppClient(
        "PHONE", "TOKEN", transport=httpx.MockTransport(handler)
    )
    await client.mark_as_read("wamid.inbound_test")
    assert captured["body"]["status"] == "read"
    assert captured["body"]["message_id"] == "wamid.inbound_test"


# ======================================================================
# Error handling
# ======================================================================


@pytest.mark.asyncio
async def test_raises_on_api_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            400,
            json={
                "error": {
                    "message": "Invalid phone number",
                    "type": "OAuthException",
                    "code": 100,
                }
            },
        )

    client = WhatsAppClient(
        "PHONE", "TOKEN", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(WhatsAppClientError) as exc_info:
        await client.send_text(to="bad", body="hi")
    assert "400" in str(exc_info.value)


@pytest.mark.asyncio
async def test_raises_on_unauthorized():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "Invalid token"})

    client = WhatsAppClient(
        "PHONE", "EXPIRED_TOKEN", transport=httpx.MockTransport(handler)
    )
    with pytest.raises(WhatsAppClientError):
        await client.send_text(to="919999999999", body="hi")
