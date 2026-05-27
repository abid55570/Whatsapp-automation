"""Tests for the multi-language reply picker."""
import pytest

from app.services.intents.reply_picker import (
    DETECTED_LANG_TO_LOCALE,
    LOCALE_FALLBACK_CHAIN,
    pick_reply,
)


DEFAULT = "Our prices start at ₹300"

TRANSLATIONS = {
    "hi": "हमारी कीमतें ₹300 से शुरू होती हैं",
    "hinglish": "Hamare rates ₹300 se shuru hote hain",
    "bn": "আমাদের দাম ৳৩০০ থেকে শুরু",
    "ur": "Hamari qeematein ₹300 se shuru",
    "bho": "Hamre rate ₹300 se shuru ba",
}


class TestPickReply:
    def test_no_translations_returns_default(self):
        assert pick_reply(DEFAULT, None, "hindi") == DEFAULT
        assert pick_reply(DEFAULT, {}, "hindi") == DEFAULT

    def test_hindi_customer_gets_hindi(self):
        assert pick_reply(DEFAULT, TRANSLATIONS, "hindi") == TRANSLATIONS["hi"]

    def test_hinglish_customer_gets_hinglish(self):
        assert (
            pick_reply(DEFAULT, TRANSLATIONS, "hinglish")
            == TRANSLATIONS["hinglish"]
        )

    def test_bengali_customer_gets_bengali(self):
        assert pick_reply(DEFAULT, TRANSLATIONS, "bengali") == TRANSLATIONS["bn"]

    def test_urdu_customer_gets_urdu(self):
        assert pick_reply(DEFAULT, TRANSLATIONS, "urdu") == TRANSLATIONS["ur"]

    def test_bhojpuri_customer_gets_bhojpuri(self):
        assert (
            pick_reply(DEFAULT, TRANSLATIONS, "bhojpuri") == TRANSLATIONS["bho"]
        )

    def test_english_customer_gets_default(self):
        assert pick_reply(DEFAULT, TRANSLATIONS, "english") == DEFAULT

    def test_none_language_gets_default(self):
        assert pick_reply(DEFAULT, TRANSLATIONS, None) == DEFAULT


class TestFallbackChain:
    def test_hindi_falls_to_hinglish_if_no_hindi(self):
        partial = {"hinglish": TRANSLATIONS["hinglish"]}
        assert pick_reply(DEFAULT, partial, "hindi") == TRANSLATIONS["hinglish"]

    def test_hinglish_falls_to_hindi_if_no_hinglish(self):
        partial = {"hi": TRANSLATIONS["hi"]}
        assert pick_reply(DEFAULT, partial, "hinglish") == TRANSLATIONS["hi"]

    def test_bhojpuri_falls_to_hindi(self):
        partial = {"hi": TRANSLATIONS["hi"]}
        assert pick_reply(DEFAULT, partial, "bhojpuri") == TRANSLATIONS["hi"]

    def test_bengali_no_fallback_returns_default(self):
        partial = {"hi": TRANSLATIONS["hi"]}
        # bn chain is [bn, en] — no hindi fallback
        assert pick_reply(DEFAULT, partial, "bengali") == DEFAULT

    def test_urdu_falls_to_hinglish_then_hindi(self):
        partial = {"hi": TRANSLATIONS["hi"]}
        assert pick_reply(DEFAULT, partial, "urdu") == TRANSLATIONS["hi"]

    def test_empty_string_in_translations_skipped(self):
        partial = {"hi": "", "hinglish": TRANSLATIONS["hinglish"]}
        # hi empty → falls through to hinglish
        assert pick_reply(DEFAULT, partial, "hindi") == TRANSLATIONS["hinglish"]

    def test_whitespace_only_skipped(self):
        partial = {"hi": "   ", "hinglish": TRANSLATIONS["hinglish"]}
        assert pick_reply(DEFAULT, partial, "hindi") == TRANSLATIONS["hinglish"]


class TestMappings:
    def test_all_detected_langs_map_to_locale(self):
        assert DETECTED_LANG_TO_LOCALE["english"] == "en"
        assert DETECTED_LANG_TO_LOCALE["hindi"] == "hi"
        assert DETECTED_LANG_TO_LOCALE["hinglish"] == "hinglish"
        assert DETECTED_LANG_TO_LOCALE["bengali"] == "bn"
        assert DETECTED_LANG_TO_LOCALE["urdu"] == "ur"
        assert DETECTED_LANG_TO_LOCALE["bhojpuri"] == "bho"

    def test_all_locales_have_fallback_chain(self):
        for locale in ["en", "hi", "hinglish", "bn", "ur", "bho"]:
            assert locale in LOCALE_FALLBACK_CHAIN
            assert len(LOCALE_FALLBACK_CHAIN[locale]) >= 1

    def test_chains_end_in_english(self):
        for locale, chain in LOCALE_FALLBACK_CHAIN.items():
            assert chain[-1] == "en", f"{locale} chain must end with 'en'"
