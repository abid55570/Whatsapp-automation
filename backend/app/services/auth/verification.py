"""WhatsApp deep-link verification logic.

Flow:
  1. Frontend POSTs phone → we generate a code, store hashed, return deep link
  2. User taps deep link → WhatsApp opens with "verify-XXX" pre-filled
  3. User sends message → Meta webhook → processor detects "verify-*"
  4. Processor calls consume_verification_code() → User row marked verified
  5. Frontend (polling) sees status=verified, gets JWT, logs in
"""
import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import hash_secret, verify_secret
from app.models import OTPCode, User
from app.models.enums import OTPPurpose
from app.utils.phone import normalize_phone

logger = logging.getLogger(__name__)

# Prefix for verification messages — anything else is treated as a normal customer message
VERIFICATION_PREFIX = "verify-"

# Avoid visually ambiguous chars (0/O, 1/I/l) in the code
_CODE_ALPHABET = "23456789abcdefghjkmnpqrstuvwxyz"
_CODE_LENGTH = 8

# Max wrong attempts per OTP row before we lock it out (mark consumed)
_MAX_ATTEMPTS = 5


# ============================================================
# Code generation
# ============================================================


def generate_verification_code() -> str:
    """Cryptographically random 8-char code, no ambiguous characters."""
    return "".join(secrets.choice(_CODE_ALPHABET) for _ in range(_CODE_LENGTH))


def build_deep_link(code: str, platform_phone: str) -> str:
    """Build a wa.me deep link with the verification message pre-filled."""
    phone_clean = platform_phone.lstrip("+").replace(" ", "")
    text = f"{VERIFICATION_PREFIX}{code}"
    return f"https://wa.me/{phone_clean}?text={quote(text)}"


def looks_like_verification_message(body: str | None) -> bool:
    """Quick check used by the webhook processor to detect verification msgs."""
    if not body:
        return False
    return body.strip().lower().startswith(VERIFICATION_PREFIX)


def extract_verification_code(body: str | None) -> str | None:
    """Pull the code out of a 'verify-XXX' message body."""
    if not looks_like_verification_message(body):
        return None
    return body.strip().lower()[len(VERIFICATION_PREFIX):]


# ============================================================
# DB operations
# ============================================================


async def create_verification(
    db: AsyncSession,
    phone: str,
    full_name: str | None = None,
) -> tuple[OTPCode, str, str]:
    """Create a verification challenge for a phone number.

    Invalidates any prior unconsumed codes for the same phone to ensure
    only one active code at a time.

    Returns: (otp_row, plain_code, deep_link)
    """
    phone = normalize_phone(phone)
    now = datetime.now(timezone.utc)

    # Invalidate prior pending codes for this phone
    stmt = select(OTPCode).where(
        OTPCode.phone == phone,
        OTPCode.consumed_at.is_(None),
        OTPCode.expires_at > now,
    )
    for old in (await db.execute(stmt)).scalars().all():
        old.consumed_at = now

    code = generate_verification_code()
    otp = OTPCode(
        phone=phone,
        code_hash=hash_secret(code),
        purpose=OTPPurpose.SIGNUP,
        expires_at=now + timedelta(minutes=settings.VERIFICATION_CODE_TTL_MINUTES),
        attempts=0,
    )
    db.add(otp)
    await db.flush()

    # If a User already exists for this phone, optionally update their pending name
    if full_name:
        user_stmt = select(User).where(User.phone == phone)
        user = (await db.execute(user_stmt)).scalar_one_or_none()
        if user is not None and not user.full_name:
            user.full_name = full_name

    deep_link = build_deep_link(code, settings.PLATFORM_WHATSAPP_PHONE_NUMBER)
    return otp, code, deep_link


async def consume_verification_code(
    db: AsyncSession,
    phone: str,
    code: str,
    full_name: str | None = None,
) -> User | None:
    """Verify the code → mark consumed → return User (creating if needed).

    Called from the WhatsApp webhook processor when a 'verify-XXX' message
    arrives from `phone`.

    Returns None if no matching active code exists.
    """
    phone = normalize_phone(phone)
    code = (code or "").strip().lower()
    now = datetime.now(timezone.utc)

    # Look at the 5 most-recent unconsumed codes for this phone
    stmt = (
        select(OTPCode)
        .where(
            OTPCode.phone == phone,
            OTPCode.consumed_at.is_(None),
            OTPCode.expires_at > now,
        )
        .order_by(OTPCode.created_at.desc())
        .limit(5)
    )
    candidates = (await db.execute(stmt)).scalars().all()

    matched: OTPCode | None = None
    for otp in candidates:
        # Already locked out due to brute-force attempts
        if otp.attempts >= _MAX_ATTEMPTS:
            otp.consumed_at = now  # mark dead so it stops returning in queries
            continue
        if verify_secret(code, otp.code_hash):
            matched = otp
            break
        otp.attempts += 1
        if otp.attempts >= _MAX_ATTEMPTS:
            # Reached the cap — burn the code so no further tries succeed
            otp.consumed_at = now

    if matched is None:
        await db.commit()
        return None

    matched.consumed_at = now

    # Find or create user
    user_stmt = select(User).where(User.phone == phone)
    user = (await db.execute(user_stmt)).scalar_one_or_none()
    if user is None:
        user = User(
            phone=phone,
            full_name=full_name,
            phone_verified=True,
            is_active=True,
            last_login_at=now,
        )
        db.add(user)
    else:
        user.phone_verified = True
        user.last_login_at = now
        if full_name and not user.full_name:
            user.full_name = full_name

    await db.flush()
    await db.commit()
    logger.info("User %s verified via WhatsApp deep link", user.id)
    return user
