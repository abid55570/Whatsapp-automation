"""Celery billing tasks: trial expiry, usage rollups."""
import asyncio
import logging
from typing import Any

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="billing.freeze_expired_trials", bind=True, acks_late=True,
                 autoretry_for=(Exception,), retry_backoff=60, max_retries=3)
def freeze_expired_trials_task(self) -> dict[str, Any]:
    """Hourly task → flip TRIALING → FROZEN when trial_ends_at passed."""
    return asyncio.run(_run_freeze())


@celery_app.task(name="billing.reset_monthly_usage", bind=True, acks_late=True,
                 autoretry_for=(Exception,), retry_backoff=60, max_retries=3)
def reset_monthly_usage_task(self) -> dict[str, Any]:
    """Hourly task → reset conversations_used when billing period ends."""
    return asyncio.run(_run_reset())


async def _run_freeze() -> dict[str, Any]:
    from app.core.database import AsyncSessionLocal
    from app.services.billing import freeze_expired_trials

    async with AsyncSessionLocal() as db:
        count = await freeze_expired_trials(db)
    return {"frozen": count}


async def _run_reset() -> dict[str, Any]:
    from app.core.database import AsyncSessionLocal
    from app.services.billing import reset_monthly_usage

    async with AsyncSessionLocal() as db:
        count = await reset_monthly_usage(db)
    return {"reset": count}
