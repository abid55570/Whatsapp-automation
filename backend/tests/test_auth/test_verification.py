"""Tests for the deep-link verification helpers (unit, no DB)."""
from urllib.parse import unquote

from app.services.auth.verification import (
    VERIFICATION_PREFIX,
    build_deep_link,
    extract_verification_code,
    generate_verification_code,
    looks_like_verification_message,
)


class TestCodeGeneration:
    def test_length(self):
        for _ in range(50):
            assert len(generate_verification_code()) == 8

    def test_alphabet(self):
        """Codes must not contain ambiguous chars (0, O, 1, I, l)."""
        forbidden = set("0O1Il")
        for _ in range(100):
            code = generate_verification_code()
            assert not (set(code) & forbidden), f"Bad char in {code}"

    def test_randomness(self):
        """Generate 200 codes — at least 195 should be unique."""
        codes = {generate_verification_code() for _ in range(200)}
        assert len(codes) >= 195


class TestDeepLink:
    def test_format(self):
        link = build_deep_link("abc123", "+919999999999")
        assert link.startswith("https://wa.me/919999999999?text=")
        assert "verify-abc123" in unquote(link)

    def test_strips_plus(self):
        link = build_deep_link("xyz", "+911111111111")
        assert "/911111111111?" in link
        assert "/+91" not in link

    def test_strips_spaces(self):
        link = build_deep_link("xyz", "+91 99 999 99999")
        assert " " not in link.split("?")[0]


class TestLooksLikeVerification:
    def test_positive(self):
        assert looks_like_verification_message("verify-abc12345") is True
        assert looks_like_verification_message("Verify-ABC12345") is True
        assert looks_like_verification_message("  verify-xyz  ") is True

    def test_negative(self):
        assert looks_like_verification_message("hi") is False
        assert looks_like_verification_message("verifyabc") is False
        assert looks_like_verification_message("") is False
        assert looks_like_verification_message(None) is False
        assert looks_like_verification_message("kitne ka hai?") is False


class TestExtractCode:
    def test_extract(self):
        assert extract_verification_code("verify-abc123") == "abc123"
        assert extract_verification_code("Verify-XYZ789") == "xyz789"

    def test_extract_with_whitespace(self):
        assert extract_verification_code("  verify-code  ") == "code"

    def test_non_verification_returns_none(self):
        assert extract_verification_code("hello") is None
        assert extract_verification_code("") is None
        assert extract_verification_code(None) is None
