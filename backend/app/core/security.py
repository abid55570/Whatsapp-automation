"""JWT token + bcrypt hashing utilities."""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


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
    """Hash a secret (OTP code, password) with bcrypt."""
    return _pwd_context.hash(plaintext)


def verify_secret(plaintext: str, hashed: str) -> bool:
    """Verify a plaintext secret against its hash."""
    try:
        return _pwd_context.verify(plaintext, hashed)
    except Exception:
        return False
