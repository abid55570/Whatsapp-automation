"""Tests for smart_reply + translator."""
import pytest

from app.services.ai import smart_reply, translator
from app.services.ai.client import AIError


async def test_smart_reply_empty_message():
    assert await smart_reply.generate_smart_reply(
        business_name="X", business_type="shop",
        customer_message="   ",
        detected_language="english",
    ) is None


async def test_smart_reply_success(monkeypatch):
    async def fake_gen(*a, **kw):
        return "Hello there!"
    monkeypatch.setattr(smart_reply, "generate", fake_gen)
    out = await smart_reply.generate_smart_reply(
        business_name="X", business_type="shop",
        customer_message="hi",
        detected_language="english",
        enabled_intent_names=["greeting", "menu"],
    )
    assert out == "Hello there!"


async def test_smart_reply_ai_error(monkeypatch):
    async def fake_gen(*a, **kw):
        raise AIError("boom")
    monkeypatch.setattr(smart_reply, "generate", fake_gen)
    out = await smart_reply.generate_smart_reply(
        "X", "shop", "hi", "english",
    )
    assert out is None


async def test_smart_reply_tiny_output(monkeypatch):
    async def fake_gen(*a, **kw):
        return "ok"  # too short
    monkeypatch.setattr(smart_reply, "generate", fake_gen)
    out = await smart_reply.generate_smart_reply("X", "shop", "hi", "english")
    assert out is None


async def test_translator_passthrough_english():
    assert await translator.translate_to("hello", "english") == "hello"
    assert await translator.translate_to("hi", "en") == "hi"


async def test_translator_empty():
    assert await translator.translate_to("", "hindi") is None
    assert await translator.translate_to("   ", "hindi") is None


async def test_translator_success(monkeypatch):
    async def fake_gen(*a, **kw):
        return "नमस्ते"
    monkeypatch.setattr(translator, "generate", fake_gen)
    out = await translator.translate_to("hello", "hindi")
    assert out == "नमस्ते"


async def test_translator_ai_error(monkeypatch):
    async def fake_gen(*a, **kw):
        raise AIError("fail")
    monkeypatch.setattr(translator, "generate", fake_gen)
    out = await translator.translate_to("hello", "bengali")
    assert out is None


async def test_translator_tiny_output(monkeypatch):
    async def fake_gen(*a, **kw):
        return "a"
    monkeypatch.setattr(translator, "generate", fake_gen)
    assert await translator.translate_to("hello", "hindi") is None
