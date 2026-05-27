"""Tests for webhook signature verification."""
import hashlib
import hmac

from app.services.whatsapp.verifier import (
    verify_webhook_challenge,
    verify_webhook_signature,
)


def _sign(payload: bytes, secret: str) -> str:
    """Generate a valid signature for testing."""
    return hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()


class TestSignatureVerification:
    def test_valid_signature_with_prefix(self):
        secret = "test_secret_xyz"
        payload = b'{"object":"whatsapp_business_account"}'
        sig = _sign(payload, secret)
        assert verify_webhook_signature(payload, f"sha256={sig}", secret) is True

    def test_valid_signature_without_prefix(self):
        secret = "test_secret_xyz"
        payload = b'{"hello":"world"}'
        sig = _sign(payload, secret)
        assert verify_webhook_signature(payload, sig, secret) is True

    def test_invalid_signature(self):
        assert (
            verify_webhook_signature(b"data", "sha256=wrong_sig_here", "secret")
            is False
        )

    def test_missing_signature(self):
        assert verify_webhook_signature(b"data", "", "secret") is False

    def test_missing_secret(self):
        assert verify_webhook_signature(b"data", "sha256=anything", "") is False

    def test_empty_payload(self):
        assert verify_webhook_signature(b"", "sha256=anything", "secret") is False

    def test_tampered_payload(self):
        """Signature for one payload should not verify against modified payload."""
        secret = "secret"
        original = b'{"amount":100}'
        tampered = b'{"amount":9999}'
        sig = _sign(original, secret)
        assert verify_webhook_signature(tampered, f"sha256={sig}", secret) is False


class TestChallengeVerification:
    def test_valid_challenge(self):
        assert verify_webhook_challenge("subscribe", "tok123", "tok123") is True

    def test_wrong_mode(self):
        assert verify_webhook_challenge("unsubscribe", "tok", "tok") is False

    def test_wrong_token(self):
        assert verify_webhook_challenge("subscribe", "tok1", "tok2") is False
