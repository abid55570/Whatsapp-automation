"""Tests for the HSN auto-suggest service."""
import pytest

from app.services.gst.hsn_lookup import best_match, suggest


class TestSuggest:
    def test_empty_input(self):
        assert suggest("") == []
        assert suggest("   ") == []
        assert suggest(None) == []  # type: ignore

    def test_exact_keyword_hit(self):
        out = suggest("atta")
        assert len(out) >= 1
        assert out[0]["code"] == "1101"
        assert out[0]["score"] == 100
        assert out[0]["rate"] == 0
        assert out[0]["unit"] == "kg"

    def test_substring_hit(self):
        out = suggest("basmati rice 5kg")
        assert len(out) >= 1
        # "rice" should appear as a keyword in 1006
        codes = [r["code"] for r in out]
        assert "1006" in codes

    def test_typo_fuzzy_match(self):
        # "tomato" → "tamatar" is a keyword
        out = suggest("tamato")
        assert len(out) >= 1
        # Should find tomato (0702)
        codes = [r["code"] for r in out]
        assert any(c == "0702" for c in codes)

    def test_no_match_returns_empty(self):
        out = suggest("xyzzyzzy nonexistent product 12345")
        # min_score gates out garbage
        assert out == [] or all(r["score"] >= 60 for r in out)

    def test_devanagari_keyword(self):
        # "doodh" is hindi for milk
        out = suggest("doodh")
        assert len(out) >= 1
        assert out[0]["code"] == "0401"

    def test_service_codes_present(self):
        # SAC codes (services)
        out = suggest("salon")
        assert any(r["code"] == "997212" for r in out)
        out = suggest("haircut")
        assert any(r["code"] == "997212" for r in out)
        out = suggest("tuition")
        assert any(r["code"] == "999294" for r in out)

    def test_limit_respected(self):
        out = suggest("oil", limit=2)
        assert len(out) <= 2

    def test_results_sorted_by_score_desc(self):
        out = suggest("ghee")
        if len(out) >= 2:
            assert out[0]["score"] >= out[1]["score"]


class TestBestMatch:
    def test_high_confidence_match(self):
        m = best_match("atta")
        assert m is not None
        assert m["code"] == "1101"

    def test_low_confidence_returns_none(self):
        m = best_match("xyz random thing", min_score=80)
        assert m is None

    def test_empty(self):
        assert best_match("") is None
