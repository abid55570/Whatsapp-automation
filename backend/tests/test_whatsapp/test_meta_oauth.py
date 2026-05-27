"""Tests for app.services.whatsapp.meta_oauth."""
import httpx
import pytest

from app.services.whatsapp import meta_oauth
from app.services.whatsapp.meta_oauth import (
    MetaOAuthError,
    exchange_code_for_token,
    fetch_phone_number_display,
)


async def test_exchange_requires_credentials(monkeypatch):
    monkeypatch.setattr(meta_oauth.settings, "META_APP_ID", "")
    monkeypatch.setattr(meta_oauth.settings, "META_APP_SECRET", "")
    with pytest.raises(MetaOAuthError):
        await exchange_code_for_token("code")


async def test_exchange_requires_code(monkeypatch):
    monkeypatch.setattr(meta_oauth.settings, "META_APP_ID", "id")
    monkeypatch.setattr(meta_oauth.settings, "META_APP_SECRET", "secret")
    with pytest.raises(MetaOAuthError):
        await exchange_code_for_token("")


async def test_exchange_success(monkeypatch):
    monkeypatch.setattr(meta_oauth.settings, "META_APP_ID", "id")
    monkeypatch.setattr(meta_oauth.settings, "META_APP_SECRET", "s")
    monkeypatch.setattr(meta_oauth.settings, "META_GRAPH_API_VERSION", "v21.0")

    def handler(req):
        return httpx.Response(200, json={"access_token": "EAATEST_TOKEN"})

    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    token = await exchange_code_for_token("auth_code", redirect_uri="https://x")
    assert token == "EAATEST_TOKEN"


async def test_exchange_no_token_in_response(monkeypatch):
    monkeypatch.setattr(meta_oauth.settings, "META_APP_ID", "id")
    monkeypatch.setattr(meta_oauth.settings, "META_APP_SECRET", "s")

    def handler(req):
        return httpx.Response(200, json={"error": "no token"})

    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    with pytest.raises(MetaOAuthError):
        await exchange_code_for_token("code")


async def test_exchange_http_error(monkeypatch):
    monkeypatch.setattr(meta_oauth.settings, "META_APP_ID", "id")
    monkeypatch.setattr(meta_oauth.settings, "META_APP_SECRET", "s")

    def handler(req):
        return httpx.Response(400, text="bad code")

    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    with pytest.raises(MetaOAuthError):
        await exchange_code_for_token("code")


async def test_fetch_phone_display_success(monkeypatch):
    def handler(req):
        return httpx.Response(
            200, json={"display_phone_number": "+919876543210"}
        )

    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    out = await fetch_phone_number_display("phid", "tok")
    assert out == "+919876543210"


async def test_fetch_phone_empty_inputs():
    assert await fetch_phone_number_display("", "tok") is None
    assert await fetch_phone_number_display("phid", "") is None


async def test_fetch_phone_http_error(monkeypatch):
    def handler(req):
        return httpx.Response(404, text="not found")

    transport = httpx.MockTransport(handler)
    orig = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    assert await fetch_phone_number_display("phid", "tok") is None
