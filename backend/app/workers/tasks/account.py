"""Account-lifecycle Celery tasks: DPDP 30-day deletion, OTP cleanup."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from app.core.database import AsyncSessionLocal
from app.models import OTPCode, User
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


# Retention: 30 days after `is_active=False` then we hard-delete.
ACCOUNT_RETENTION_DAYS = 30

# Drop OTPCode rows older than 7 days regardless of state — they're either
# consumed, expired, or abandoned. Saves ~MBs/year.
OTP_RETENTION_DAYS = 7


@celery_app.task(name="account.purge_soft_deleted", bind=True, acks_late=True,
                 autoretry_for=(Exception,), retry_backoff=60, max_retries=3)
def purge_soft_deleted_users(self) -> dict:
    """Hard-delete users soft-deleted more than 30 days ago.

    Cascade removes business, conversations, messages, orders, etc.
    Run daily.
    """
    return asyncio.run(_run_purge())


async def _run_purge() -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=ACCOUNT_RETENTION_DAYS)
    async with AsyncSessionLocal() as db:
        # Soft-deleted users are marked is_active=False and have ".d." in phone.
        # Use updated_at as the soft-delete timestamp (set by `await db.commit()` on delete).
        stmt = select(User.id, User.phone).where(
            User.is_active.is_(False),
            User.phone.like("%.d.%"),
            User.updated_at < cutoff,
        )
        rows = (await db.execute(stmt)).all()
        if not rows:
            return {"purged": 0}

        ids = [r[0] for r in rows]
        await db.execute(delete(User).where(User.id.in_(ids)))
        await db.commit()

    logger.warning("Hard-deleted %d soft-deleted user(s) past retention", len(ids))
    return {"purged": len(ids), "user_ids": [str(i) for i in ids]}


@celery_app.task(name="account.cleanup_expired_otps", bind=True, acks_late=True,
                 autoretry_for=(Exception,), retry_backoff=60, max_retries=3)
def cleanup_expired_otps(self) -> dict:
    """Delete OTP rows older than the retention window."""
    return asyncio.run(_run_otp_cleanup())


async def _run_otp_cleanup() -> dict:
    cutoff = datetime.now(timezone.utc) - timedelta(days=OTP_RETENTION_DAYS)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            delete(OTPCode).where(OTPCode.created_at < cutoff)
        )
        await db.commit()
        deleted = result.rowcount or 0
    if deleted:
        logger.info("Cleaned up %d expired OTP rows", deleted)
    return {"deleted": deleted}
