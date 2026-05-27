"""Tests for app.services.ai.client + smart_reply + translator."""
import pytest

from app.services.ai import client as ai_client
from app.services.ai.client import AIError


async def test_generate_raises_without_key(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_PROVIDER", "anthropic")
    monkeypatch.setattr(ai_client.settings, "ANTHROPIC_API_KEY", "")
    with pytest.raises(AIError):
        await ai_client.generate("hi")


async def test_generate_openai_no_key(monkeypatch):
    monkeypatch.setattr(ai_client.settings, "AI_PROVIDER", "openai")
    monkeypatch.setattr(ai_client.settings, "OPENAI_API_KEY", "")
    with pytest.raises(AIError):
        await ai_client.generate("hi")


async def test_anthropic_success(monkeypatch):
    import httpx

    monkeypatch.setattr(ai_client.settings, "AI_PROVIDER", "anthropic")
    monkeypatch.setattr(ai_client.settings, "ANTHROPIC_API_KEY", "test_key")

    def handler(req):
        return httpx.Response(
            200,
            json={"content": [{"type": "text", "text": "hello reply"}]},
        )

    transport = httpx.MockTransport(handler)
    orig_init = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig_init(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    out = await ai_client.generate("ping")
    assert "hello reply" in out


async def test_openai_success(monkeypatch):
    import httpx

    monkeypatch.setattr(ai_client.settings, "AI_PROVIDER", "openai")
    monkeypatch.setattr(ai_client.settings, "OPENAI_API_KEY", "test_key")

    def handler(req):
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": "from openai"}}]},
        )

    transport = httpx.MockTransport(handler)
    orig_init = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig_init(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    out = await ai_client.generate("ping", system="be helpful")
    assert "from openai" in out


async def test_anthropic_http_error(monkeypatch):
    import httpx

    monkeypatch.setattr(ai_client.settings, "AI_PROVIDER", "anthropic")
    monkeypatch.setattr(ai_client.settings, "ANTHROPIC_API_KEY", "k")

    def handler(req):
        return httpx.Response(500, text="server fail")

    transport = httpx.MockTransport(handler)
    orig_init = httpx.AsyncClient.__init__

    def patched(self, *args, **kw):
        kw["transport"] = transport
        orig_init(self, *args, **kw)

    monkeypatch.setattr(httpx.AsyncClient, "__init__", patched)
    with pytest.raises(AIError):
        await ai_client.generate("ping")
