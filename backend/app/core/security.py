"""JWT token + bcrypt hashing utilities."""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

# bcrypt only hashes the first 72 BYTES of input and (since 4.1) raises if
# given more. OTP codes are tiny, but truncate defensively so any caller is
# safe. We call bcrypt directly rather than via passlib — passlib 1.7.4 is
# unmaintained and its backend self-check breaks against bcrypt >= 5.0.
_BCRYPT_MAX_BYTES = 72


def _to_bcrypt_bytes(plaintext: str) -> bytes:
    return plaintext.encode("utf-8")[:_BCRYPT_MAX_BYTES]


# ============================================================
# JWT
# ============================================================


def create_access_token(
    subject: str | UUID,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """Sign a JWT for the given subject (user_id)."""
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Decode and verify a JWT. Returns payload dict, or None if invalid."""
    if not token:
        return None
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError:
        return None


# ============================================================
# Bcrypt hashing (for OTP codes)
# ============================================================


def hash_secret(plaintext: str) -> str:
    """Hash a secret (OTP code, password) with bcrypt. Returns a $2b$ hash."""
    return bcrypt.hashpw(_to_bcrypt_bytes(plaintext), bcrypt.gensalt()).decode("utf-8")


def verify_secret(plaintext: str, hashed: str) -> bool:
    """Verify a plaintext secret against its bcrypt hash. False on any error."""
    try:
        return bcrypt.checkpw(_to_bcrypt_bytes(plaintext), hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False
