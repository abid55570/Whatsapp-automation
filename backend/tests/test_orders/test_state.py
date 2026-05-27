"""Tests for affirmative/negative detection."""
import pytest

from app.services.orders.state import is_affirmative, is_negative


class TestAffirmative:
    @pytest.mark.parametrize(
        "text",
        [
            "yes", "Yes", "YES",
            "y", "yeah", "yep", "ok", "okay", "okk",
            "haan", "han", "ha", "haanji", "haan ji",
            "ji", "ji haan",
            "thik", "theek hai", "thik hai",
            "pakka", "bilkul",
            "confirm", "confirmed",
            "हाँ", "जी", "ठीक है",
            "ok ji",
            "yes please",
            "haan bhai",
        ],
    )
    def test_positive(self, text):
        assert is_affirmative(text) is True

    @pytest.mark.parametrize(
        "text",
        [
            "no", "nahi", "nope",
            "cancel", "रद्द",
            "hello",
            "menu please",
            "",
            None,
        ],
    )
    def test_negative_input(self, text):
        assert is_affirmative(text) is False


class TestNegative:
    @pytest.mark.parametrize(
        "text",
        [
            "no", "nope", "nah",
            "nahi", "nahin", "na", "nai",
            "cancel", "cancel karo",
            "नहीं", "नही", "रद्द",
            "abort", "stop",
            "no thanks",
        ],
    )
    def test_positive(self, text):
        assert is_negative(text) is True

    @pytest.mark.parametrize(
        "text",
        [
            "yes", "haan", "ok",
            "menu", "hi",
            "",
            None,
        ],
    )
    def test_negative_input(self, text):
        assert is_negative(text) is False


class TestEdgeCases:
    def test_affirmative_in_longer_sentence(self):
        # "yes please send" — first word is yes
        assert is_affirmative("yes please send") is True

    def test_negative_in_longer_sentence(self):
        assert is_negative("nahi please cancel") is True

    def test_ambiguous_returns_false(self):
        # If text has no yes/no marker
        assert is_affirmative("send me menu") is False
        assert is_negative("send me menu") is False
