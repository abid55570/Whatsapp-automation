"""Celery tasks for asynchronous WhatsApp message processing."""
import asyncio
import logging
from typing import Any

from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="whatsapp.process_webhook",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=300,
    max_retries=3,
    acks_late=True,
)
def process_webhook_task(self, payload: dict[str, Any]) -> dict[str, Any]:
    """Top-level Celery task for an inbound Meta webhook payload."""
    try:
        return asyncio.run(_process_async(payload))
    except Exception as exc:
        logger.exception("process_webhook_task failed: %s", exc)
        raise


async def _process_async(payload_dict: dict[str, Any]) -> dict[str, Any]:
    """Async portion: parse → persist → match → reply."""
    # Imports here to avoid Celery import-cycle issues
    from app.core.database import AsyncSessionLocal
    from app.services.whatsapp.parser import extract_messages, extract_statuses
    from app.services.whatsapp.processor import process_inbound_message
    from app.services.whatsapp.schemas import WebhookPayload

    try:
        payload = WebhookPayload(**payload_dict)
    except Exception as exc:
        logger.error("Failed to parse webhook payload: %s", exc)
        return {"status": "error", "reason": "parse_failed", "detail": str(exc)}

    msg_events = extract_messages(payload)
    status_events = extract_statuses(payload)

    processed_messages = 0
    processed_statuses = 0
    errors: list[str] = []

    async with AsyncSessionLocal() as db:
        for phone_number_id, msg, contact in msg_events:
            try:
                await process_inbound_message(db, phone_number_id, msg, contact)
                processed_messages += 1
            except Exception as exc:
                logger.exception(
                    "Failed processing message %s: %s", msg.id, exc
                )
                errors.append(f"{msg.id}: {exc}")

        for _pnid, status in status_events:
            # Status updates handled here in future (delivered/read timestamps)
            processed_statuses += 1

    return {
        "status": "ok",
        "processed_messages": processed_messages,
        "processed_statuses": processed_statuses,
        "errors": errors,
    }
