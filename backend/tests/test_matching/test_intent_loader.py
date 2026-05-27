"""Tests for the IntentLibrary loader."""
import json
from pathlib import Path

import pytest

from app.services.matching.intent_loader import IntentLibrary


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "intents"


def test_loads_at_least_12_intents():
    lib = IntentLibrary(DATA_DIR)
    assert lib.count() >= 12, f"Expected ≥12 intents, got {lib.count()}"


def test_all_expected_intents_present():
    lib = IntentLibrary(DATA_DIR)
    keys = set(lib.list_keys())
    expected = {
        "greeting",
        "thanks",
        "ask_price",
        "ask_timing",
        "ask_location",
        "ask_menu",
        "ask_services",
        "book_appointment",
        "order_status",
        "delivery_inquiry",
        "payment_inquiry",
        "contact_info",
    }
    missing = expected - keys
    assert not missing, f"Missing intents: {missing}"


def test_get_returns_intent():
    lib = IntentLibrary(DATA_DIR)
    intent = lib.get("ask_price")
    assert intent is not None
    assert intent.key == "ask_price"
    assert "english" in intent.languages
    assert "hindi" in intent.languages
    assert "hinglish" in intent.languages


def test_get_unknown_returns_none():
    lib = IntentLibrary(DATA_DIR)
    assert lib.get("nonexistent_xyz_intent") is None


def test_empty_directory(tmp_path):
    lib = IntentLibrary(tmp_path)
    assert lib.count() == 0
    assert lib.list_keys() == []


def test_skip_malformed_json(tmp_path):
    """Loader should skip bad files without crashing."""
    bad = tmp_path / "bad.json"
    bad.write_text("{not valid")

    good = tmp_path / "good.json"
    good.write_text(json.dumps({
        "key": "good_test",
        "name": "Good Test",
        "languages": {"english": ["test"]},
    }))

    lib = IntentLibrary(tmp_path)
    assert lib.count() == 1
    assert lib.get("good_test") is not None


def test_all_intents_have_required_fields():
    """Every shipped intent must have languages and a default reply."""
    lib = IntentLibrary(DATA_DIR)
    for intent in lib.list_all():
        assert intent.languages, f"{intent.key} has no languages"
        assert intent.default_reply_template, f"{intent.key} has no default reply"


def test_all_intents_have_english_keywords():
    """English is the universal language — must be present."""
    lib = IntentLibrary(DATA_DIR)
    for intent in lib.list_all():
        assert "english" in intent.languages, (
            f"{intent.key} missing English keywords"
        )
        assert len(intent.languages["english"]) >= 3
