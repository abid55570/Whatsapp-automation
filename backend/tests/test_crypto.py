"""Tests for app.core.crypto (Fernet encryption)."""
import os

from app.core import crypto


def test_no_key_is_passthrough(monkeypatch):
    """Without ENCRYPTION_KEY set, encrypt/decrypt are identity."""
    monkeypatch.setattr(crypto.settings, "ENCRYPTION_KEY", "")
    assert crypto.encrypt_str("hello") == "hello"
    assert crypto.decrypt_str("hello") == "hello"
    assert crypto.encrypt_str(None) is None
    assert crypto.encrypt_str("") == ""


def test_with_key_roundtrip(monkeypatch):
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    monkeypatch.setattr(crypto.settings, "ENCRYPTION_KEY", key)
    ct = crypto.encrypt_str("EAATESTTOKEN")
    assert ct.startswith("fernet:")
    assert crypto.decrypt_str(ct) == "EAATESTTOKEN"


def test_legacy_plaintext_passthrough(monkeypatch):
    from cryptography.fernet import Fernet

    key = Fernet.generate_key().decode()
    monkeypatch.setattr(crypto.settings, "ENCRYPTION_KEY", key)
    # Non-prefixed value (legacy plaintext) → returned as-is
    assert crypto.decrypt_str("legacy_plaintext_token") == "legacy_plaintext_token"


def test_invalid_key_returns_none(monkeypatch):
    monkeypatch.setattr(crypto.settings, "ENCRYPTION_KEY", "not-a-valid-fernet-key")
    # No Fernet → encrypt returns plaintext
    assert crypto.encrypt_str("x") == "x"
    # Decrypt of 'fernet:'-prefixed without key returns None
    assert crypto.decrypt_str("fernet:gibberish") is None
