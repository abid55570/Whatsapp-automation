"""Celery application instance and configuration."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "whatsapp_saas",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    result_expires=3600,
)

# ============================================================
# Beat schedule — cron-style recurring tasks
# ============================================================
celery_app.conf.beat_schedule = {
    "sync-google-sheets-every-15-min": {
        "task": "sheets.sync_all_due",
        "schedule": 900.0,  # 15 minutes
    },
    "freeze-expired-trials-hourly": {
        "task": "billing.freeze_expired_trials",
        "schedule": 3600.0,  # 1 hour — quick reaction to expiry
    },
    "reset-monthly-usage-hourly": {
        "task": "billing.reset_monthly_usage",
        "schedule": 3600.0,
    },
    "purge-soft-deleted-daily": {
        "task": "account.purge_soft_deleted",
        "schedule": 86400.0,
    },
    "cleanup-expired-otps-daily": {
        "task": "account.cleanup_expired_otps",
        "schedule": 86400.0,
    },
}


@celery_app.task
def health_check() -> str:
    """Sanity-check task for Celery worker connectivity."""
    return "ok"


# Import task modules so they register with the celery_app instance
from app.workers.tasks import account as _account_tasks  # noqa: E402, F401
from app.workers.tasks import billing as _billing_tasks  # noqa: E402, F401
from app.workers.tasks import sheets as _sheets_tasks  # noqa: E402, F401
from app.workers.tasks import whatsapp as _whatsapp_tasks  # noqa: E402, F401
