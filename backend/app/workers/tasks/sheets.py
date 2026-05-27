"""Celery tasks for Google Sheets sync."""
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="sheets.sync_one",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    max_retries=3,
)
def sync_one_sheet_task(self, sync_id: str) -> dict[str, Any]:
    """Sync one Google Sheet by ID (UUID as string)."""
    try:
        return asyncio.run(_sync_one(sync_id))
    except Exception as exc:
        logger.exception("sync_one_sheet_task failed for %s: %s", sync_id, exc)
        raise


@celery_app.task(name="sheets.sync_all_due")
def sync_all_due_task() -> dict[str, Any]:
    """Find all auto-sync sheets whose interval has elapsed, sync them.

    Scheduled by Celery Beat (see celery_app.py).
    """
    return asyncio.run(_sync_all_due())


# ============================================================
# Async implementations
# ============================================================


async def _sync_one(sync_id: str) -> dict[str, Any]:
    from app.core.database import AsyncSessionLocal
    from app.models import GoogleSheetSync
    from app.services.sheets.syncer import sync_sheet

    try:
        sid = UUID(sync_id)
    except ValueError:
        return {"status": "error", "reason": "invalid_uuid"}

    async with AsyncSessionLocal() as db:
        sync = await db.get(GoogleSheetSync, sid)
        if sync is None:
            return {"status": "error", "reason": "not_found"}

        count, error = await sync_sheet(db, sync)
        return {
            "status": "ok" if error is None else "error",
            "rows_synced": count,
            "error": error,
            "sync_id": sync_id,
        }


async def _sync_all_due() -> dict[str, Any]:
    from sqlalchemy import select

    from app.core.database import AsyncSessionLocal
    from app.models import GoogleSheetSync
    from app.services.sheets.syncer import sync_sheet

    now = datetime.now(timezone.utc)
    triggered = 0
    succeeded = 0
    errors = 0

    async with AsyncSessionLocal() as db:
        stmt = select(GoogleSheetSync).where(
            GoogleSheetSync.auto_sync.is_(True)
        )
        all_syncs = (await db.execute(stmt)).scalars().all()

        for sync in all_syncs:
            # Skip if not yet due
            if sync.last_synced_at is not None:
                next_due = sync.last_synced_at + timedelta(
                    minutes=sync.sync_interval_minutes
                )
                if now < next_due:
                    continue

            triggered += 1
            _, error = await sync_sheet(db, sync)
            if error:
                errors += 1
            else:
                succeeded += 1

    return {
        "triggered": triggered,
        "succeeded": succeeded,
        "errors": errors,
    }
