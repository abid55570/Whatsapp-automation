"""Webhook signature verification for Meta WhatsApp Cloud API."""
import hashlib
import hmac


def verify_webhook_signature(payload: bytes, signature: str, app_secret: str) -> bool:
    """Verify Meta's `X-Hub-Signature-256` header against the raw payload.

    Meta signs every webhook body with HMAC-SHA256 using the app secret.
    The header looks like: `X-Hub-Signature-256: sha256=<hex digest>`
    """
    if not signature or not app_secret or not payload:
        return False

    # Strip "sha256=" prefix if present
    if signature.startswith("sha256="):
        signature = signature[len("sha256=") :]

    expected = hmac.new(
        app_secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, signature)


def verify_webhook_challenge(mode: str, token: str, expected_token: str) -> bool:
    """Verify Meta's GET challenge during webhook subscription setup."""
    return mode == "subscribe" and token == expected_token
