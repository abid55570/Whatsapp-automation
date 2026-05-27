"""Authentication and WhatsApp deep-link verification."""
from app.services.auth.verification import (
    VERIFICATION_PREFIX,
    build_deep_link,
    consume_verification_code,
    create_verification,
    extract_verification_code,
    generate_verification_code,
    looks_like_verification_message,
)

__all__ = [
    "VERIFICATION_PREFIX",
    "build_deep_link",
    "consume_verification_code",
    "create_verification",
    "extract_verification_code",
    "generate_verification_code",
    "looks_like_verification_message",
]
