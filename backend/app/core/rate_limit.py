"""Rate limiting using slowapi.

Two key functions:
  - `get_user_key`: per-user limiter for authenticated endpoints
  - `get_ip_key`: per-IP limiter for public endpoints

Apply via `@limiter.limit(...)` decorator on routes.
"""
import logging
from typing import Any

from fastapi import Request

from app.core.config import settings
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)


def get_ip_key(request: Request) -> str:
    """Limiter key: client IP (handles X-Forwarded-For)."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "anonymous"


def get_user_key(request: Request) -> str:
    """Limiter key: user_id from JWT, falls back to IP if not authed."""
    auth = request.headers.get("authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        payload = decode_access_token(token)
        if payload and payload.get("sub"):
            return f"user:{payload['sub']}"
    return f"ip:{get_ip_key(request)}"


def _build_limiter() -> Any:
    """Build a slowapi Limiter. Returns None if slowapi unavailable."""
    try:
        from slowapi import Limiter
    except ImportError:
        logger.warning("slowapi not installed — rate limiting disabled")
        return None

    return Limiter(
        key_func=get_user_key,
        default_limits=[settings.RATE_LIMIT_DEFAULT]
        if settings.RATE_LIMIT_ENABLED
        else [],
        storage_uri=settings.REDIS_URL,  # Redis-backed (shared across workers)
        strategy="fixed-window",
    )


# Singleton — imported by main.py and route modules
limiter = _build_limiter()
