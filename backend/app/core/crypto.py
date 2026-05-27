"""Fernet symmetric encryption for sensitive columns (access tokens, etc.).

Key comes from `settings.ENCRYPTION_KEY` (32-byte URL-safe base64).
Generate one with:  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

If `ENCRYPTION_KEY` is empty/missing, encryption is a no-op (dev fallback).
In production, always set it.
"""
from __future__ import annotations

import base64
import logging

from sqlalchemy.types import String, TypeDecorator

from app.core.config import settings

logger = logging.getLogger(__name__)

_FERNET_PREFIX = "fernet:"  # marks encrypted ciphertext in DB


def _get_fernet():
    """Return a Fernet instance or None if no key configured."""
    if not settings.ENCRYPTION_KEY:
        return None
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        logger.error("cryptography package not installed — encryption disabled")
        return None
    try:
        # Validate / decode key
        key = settings.ENCRYPTION_KEY.encode()
        return Fernet(key)
    except Exception as exc:
        logger.error("Invalid ENCRYPTION_KEY: %s", exc)
        return None


def encrypt_str(plaintext: str | None) -> str | None:
    """Encrypt a string. Returns prefixed ciphertext, or plaintext if no key."""
    if plaintext is None or plaintext == "":
        return plaintext
    f = _get_fernet()
    if f is None:
        return plaintext  # dev fallback — store plaintext
    token = f.encrypt(plaintext.encode("utf-8"))
    return _FERNET_PREFIX + token.decode("utf-8")


def decrypt_str(ciphertext: str | None) -> str | None:
    """Decrypt a Fernet-prefixed string. Returns plaintext if not encrypted."""
    if ciphertext is None or ciphertext == "":
        return ciphertext
    if not ciphertext.startswith(_FERNET_PREFIX):
        # Legacy plaintext — return as-is
        return ciphertext
    f = _get_fernet()
    if f is None:
        logger.error("Got encrypted token but no ENCRYPTION_KEY set")
        return None
    try:
        token = ciphertext[len(_FERNET_PREFIX) :].encode("utf-8")
        return f.decrypt(token).decode("utf-8")
    except Exception as exc:
        logger.error("Decryption failed: %s", exc)
        return None


class EncryptedString(TypeDecorator):
    """SQLAlchemy column type that auto-encrypts on write, decrypts on read.

    Backed by a varchar column. Encrypted values are prefixed with
    'fernet:' to distinguish from legacy plaintext (allows lazy migration).

    Usage:
        whatsapp_access_token: Mapped[str | None] = mapped_column(
            EncryptedString(2000), nullable=True
        )
    """

    impl = String
    cache_ok = True

    def __init__(self, length: int = 2000, **kwargs):
        # Fernet output is ~30% larger than input — keep length generous
        super().__init__(length=length, **kwargs)

    def process_bind_param(self, value, dialect):
        return encrypt_str(value)

    def process_result_value(self, value, dialect):
        return decrypt_str(value)
