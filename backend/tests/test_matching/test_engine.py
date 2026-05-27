"""End-to-end matching engine tests across all supported languages."""
from pathlib import Path

import pytest

from app.services.matching.engine import MatchingEngine
from app.services.matching.intent_loader import IntentLibrary


DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "intents"


@pytest.fixture(scope="module")
def engine() -> MatchingEngine:
    library = IntentLibrary(DATA_DIR)
    return MatchingEngine(library)


# =====================================================================
# English
# =====================================================================

class TestEnglish:
    def test_price_inquiry(self, engine):
        result = engine.match("what is the price?")
        assert result is not None
        assert result.intent_key == "ask_price"

    def test_how_much(self, engine):
        result = engine.match("how much does this cost?")
        assert result.intent_key == "ask_price"

    def test_timing(self, engine):
        result = engine.match("what time do you open?")
        assert result.intent_key == "ask_timing"

    def test_location(self, engine):
        result = engine.match("where are you located?")
        assert result.intent_key == "ask_location"

    def test_greeting(self, engine):
        result = engine.match("hi there")
        assert result.intent_key == "greeting"

    def test_thanks(self, engine):
        result = engine.match("thank you so much")
        assert result.intent_key == "thanks"

    def test_menu(self, engine):
        result = engine.match("can I see the menu?")
        assert result.intent_key == "ask_menu"

    def test_booking(self, engine):
        result = engine.match("I want to book an appointment")
        assert result.intent_key == "book_appointment"

    def test_order_status(self, engine):
        result = engine.match("where is my order?")
        assert result.intent_key == "order_status"

    def test_delivery(self, engine):
        result = engine.match("do you do home delivery?")
        assert result.intent_key == "delivery_inquiry"


# =====================================================================
# Hinglish (Roman Hindi) — most common in Indian SMB chats
# =====================================================================

class TestHinglish:
    def test_kitna(self, engine):
        result = engine.match("kitne ka hai bhai")
        assert result.intent_key == "ask_price"

    def test_rate_kya(self, engine):
        result = engine.match("rate kya hai")
        assert result.intent_key == "ask_price"

    def test_daam_btao(self, engine):
        result = engine.match("daam btao yaar")
        assert result.intent_key == "ask_price"

    def test_kab_khulta(self, engine):
        result = engine.match("kab khulta hai dukan")
        assert result.intent_key == "ask_timing"

    def test_namaste(self, engine):
        result = engine.match("namaste bhai")
        assert result.intent_key == "greeting"

    def test_dhanyawad(self, engine):
        result = engine.match("bahut dhanyawad")
        assert result.intent_key == "thanks"

    def test_address_bhejo(self, engine):
        result = engine.match("address bhejo")
        assert result.intent_key == "ask_location"

    def test_slot_chahiye(self, engine):
        result = engine.match("slot chahiye kal ka")
        assert result.intent_key == "book_appointment"

    def test_order_kahan(self, engine):
        result = engine.match("mera order kaha hai")
        assert result.intent_key == "order_status"

    def test_payment_kaise(self, engine):
        result = engine.match("payment kaise karu")
        assert result.intent_key == "payment_inquiry"


# =====================================================================
# Hindi (Devanagari script)
# =====================================================================

class TestHindiDevanagari:
    def test_price(self, engine):
        result = engine.match("कीमत क्या है?")
        assert result.intent_key == "ask_price"

    def test_namaste(self, engine):
        result = engine.match("नमस्ते")
        assert result.intent_key == "greeting"

    def test_timing(self, engine):
        result = engine.match("कब खुलता है?")
        assert result.intent_key == "ask_timing"

    def test_pata(self, engine):
        result = engine.match("पता बताओ")
        assert result.intent_key == "ask_location"

    def test_dhanyavad(self, engine):
        result = engine.match("धन्यवाद")
        assert result.intent_key == "thanks"


# =====================================================================
# Urdu
# =====================================================================

class TestUrdu:
    def test_qeemat(self, engine):
        result = engine.match("qeemat kya hai")
        assert result.intent_key == "ask_price"

    def test_salaam(self, engine):
        result = engine.match("salaam alaikum")
        assert result.intent_key == "greeting"

    def test_shukriya(self, engine):
        result = engine.match("bohot shukriya")
        assert result.intent_key == "thanks"


# =====================================================================
# Bhojpuri
# =====================================================================

class TestBhojpuri:
    def test_ka_rate(self, engine):
        result = engine.match("ka rate ba")
        assert result.intent_key == "ask_price"

    def test_ketna(self, engine):
        result = engine.match("ketna ke ba")
        assert result.intent_key == "ask_price"

    def test_ram_ram(self, engine):
        result = engine.match("ram ram bhaiya")
        assert result.intent_key == "greeting"


# =====================================================================
# Bengali
# =====================================================================

class TestBengali:
    def test_dam_roman(self, engine):
        result = engine.match("dam koto")
        assert result.intent_key == "ask_price"

    def test_bengali_script(self, engine):
        result = engine.match("দাম কত?")
        assert result.intent_key == "ask_price"

    def test_namaskar(self, engine):
        result = engine.match("নমস্কার")
        assert result.intent_key == "greeting"


# =====================================================================
# Code-switching (mixed languages in one message)
# =====================================================================

class TestCodeSwitching:
    def test_english_hindi_mix_timing(self, engine):
        result = engine.match("bhai today open hai kya")
        # 'open' is in English timing keywords
        assert result is not None
        assert result.intent_key == "ask_timing"

    def test_hindi_english_price(self, engine):
        result = engine.match("price kya hai please?")
        assert result.intent_key == "ask_price"


# =====================================================================
# Emoji-only / minimal text
# =====================================================================

class TestEmojis:
    def test_money_emoji(self, engine):
        result = engine.match("💰 ?")
        assert result is not None
        assert result.intent_key == "ask_price"

    def test_clock_emoji(self, engine):
        result = engine.match("⏰?")
        assert result is not None
        assert result.intent_key == "ask_timing"

    def test_pin_emoji(self, engine):
        result = engine.match("📍?")
        assert result is not None
        assert result.intent_key == "ask_location"


# =====================================================================
# Fuzzy / typos
# =====================================================================

class TestFuzzy:
    def test_typo_price(self, engine):
        # 'prise' is a typo of 'price' — fuzzy should catch it
        result = engine.match("whats the prise plzz")
        assert result is not None
        assert result.intent_key == "ask_price"

    def test_typo_address(self, engine):
        result = engine.match("addres bhejo")
        assert result is not None
        # Either address or location keyword should hit
        assert result.intent_key == "ask_location"


# =====================================================================
# No match / edge cases
# =====================================================================

class TestNoMatch:
    def test_random_text(self, engine):
        result = engine.match("xyz qwerty asdf zzz")
        assert result is None

    def test_empty_string(self, engine):
        assert engine.match("") is None

    def test_whitespace(self, engine):
        assert engine.match("   \n  ") is None


# =====================================================================
# Result quality
# =====================================================================

class TestResultQuality:
    def test_exact_high_confidence(self, engine):
        result = engine.match("what is the price?")
        assert result.confidence >= 0.85
        assert result.matched_layer == "exact"

    def test_returns_detected_language(self, engine):
        result = engine.match("नमस्ते")
        assert result.detected_language == "hindi"

    def test_returns_matched_keywords(self, engine):
        result = engine.match("price kya hai")
        assert "price" in result.matched_keywords or "price kya" in result.matched_keywords


# =====================================================================
# Custom keywords (per-business)
# =====================================================================

class TestCustomKeywords:
    def test_custom_keyword_matches(self, engine):
        # Business adds their own slang for "price"
        custom = {"ask_price": ["bhav", "bhaav"]}
        result = engine.match("bhav kya hai?", custom_keywords=custom)
        assert result is not None
        assert result.intent_key == "ask_price"


# =====================================================================
# Filtering: only match enabled intents
# =====================================================================

class TestEnabledFiltering:
    def test_disabled_intent_not_matched(self, engine):
        # Restrict to only timing — even though message asks price, won't match
        result = engine.match(
            "what is the price?",
            enabled_intents=["ask_timing"],
        )
        assert result is None
