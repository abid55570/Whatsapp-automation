"""Webhook endpoints for Meta WhatsApp Cloud API + Razorpay."""
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.models import Order, WebhookEvent
from app.models.enums import OrderStatus, PaymentStatus
from app.services.payments import verify_razorpay_signature
from app.services.whatsapp.verifier import verify_webhook_signature

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

# Reject Webhook bodies > 1 MB — Meta/Razorpay never legitimately send that much
_MAX_WEBHOOK_BYTES = 1 * 1024 * 1024

_SENSITIVE_HEADER_KEYS = {
    "authorization", "cookie", "set-cookie", "x-api-key", "proxy-authorization",
}


def _safe_headers(headers) -> dict[str, str]:
    """Strip sensitive headers before persisting raw webhook payload."""
    return {
        k: v for k, v in headers.items() if k.lower() not in _SENSITIVE_HEADER_KEYS
    }


@router.get("/whatsapp")
async def verify_whatsapp_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
):
    """Meta's GET challenge during webhook subscription setup.

    Meta sends:
        GET /webhooks/whatsapp?hub.mode=subscribe
                              &hub.verify_token=YOUR_TOKEN
                              &hub.challenge=RANDOM_STRING

    We must echo back `hub.challenge` as plain text if the token matches.
    """
    if hub_mode != "subscribe":
        raise HTTPException(status_code=403, detail="Invalid hub.mode")
    if hub_verify_token != settings.META_WEBHOOK_VERIFY_TOKEN:
        logger.warning("Webhook verify token mismatch")
        raise HTTPException(status_code=403, detail="Invalid verify token")
    return Response(content=hub_challenge, media_type="text/plain")


@router.post("/whatsapp")
async def receive_whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive Meta webhook events (messages, statuses).

    Per Meta's docs we must return 2xx within 5 seconds, otherwise Meta retries.
    So we:
      1. Verify signature
      2. Persist raw event to DB (idempotency / audit)
      3. Queue async processing via Celery
      4. Return 200 immediately
    """
    body = await request.body()
    if len(body) > _MAX_WEBHOOK_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    signature = request.headers.get("x-hub-signature-256", "")

    # Verify signature (only if app secret configured)
    sig_ok = False
    if settings.META_APP_SECRET:
        sig_ok = verify_webhook_signature(body, signature, settings.META_APP_SECRET)
        if not sig_ok:
            logger.warning("Invalid Meta webhook signature")
            raise HTTPException(status_code=403, detail="Invalid signature")

    try:
        payload = await request.json()
    except Exception as exc:
        logger.error("Failed to parse webhook JSON: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    # Persist raw event for audit + replay
    event = WebhookEvent(
        source="meta_whatsapp",
        event_type=payload.get("object", "unknown"),
        payload=payload,
        headers=_safe_headers(request.headers),
        signature_verified=sig_ok,
        received_at=datetime.now(timezone.utc),
    )
    db.add(event)
    await db.commit()

    # Queue async processing (don't block the webhook response)
    try:
        from app.workers.tasks.whatsapp import process_webhook_task
        process_webhook_task.delay(payload)
    except Exception as exc:
        logger.exception("Failed to enqueue webhook task: %s", exc)

    return {"status": "received"}


# ============================================================
# Razorpay webhook
# ============================================================


@router.post("/razorpay")
async def receive_razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Razorpay payment events (payment_link.paid, etc.).

    Updates Order.payment_status when payment_link.paid fires.
    """
    body = await request.body()
    if len(body) > _MAX_WEBHOOK_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large")
    signature = request.headers.get("x-razorpay-signature", "")

    sig_ok = False
    if settings.RAZORPAY_WEBHOOK_SECRET:
        sig_ok = verify_razorpay_signature(
            body, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
        if not sig_ok:
            logger.warning("Invalid Razorpay signature")
            raise HTTPException(403, "Invalid signature")

    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(400, "Invalid JSON") from exc

    event_type = payload.get("event", "")
    payload_root = payload.get("payload", {})

    # Idempotency: Razorpay events have a unique `id` — skip if already seen
    razorpay_event_id = payload.get("id")
    if razorpay_event_id:
        existing = await db.execute(
            select(WebhookEvent).where(
                WebhookEvent.source == "razorpay",
                WebhookEvent.payload["id"].astext == razorpay_event_id,
            ).limit(1)
        )
        if existing.scalar_one_or_none() is not None:
            return {"status": "received", "matched": True, "duplicate": True}

    # Persist raw
    db.add(
        WebhookEvent(
            source="razorpay",
            event_type=event_type,
            payload=payload,
            headers=_safe_headers(request.headers),
            signature_verified=sig_ok,
            received_at=datetime.now(timezone.utc),
        )
    )
    await db.commit()

    # ========================================
    # Subscription events (SaaS plans)
    # ========================================
    if event_type.startswith("subscription."):
        sub_entity = payload_root.get("subscription", {}).get("entity", {})
        sub_id = sub_entity.get("id")
        if not sub_id:
            return {"status": "received", "matched": False}

        from app.services.billing.subscriptions import (
            apply_subscription_activation,
            apply_subscription_cancel,
        )

        if event_type in ("subscription.activated", "subscription.authenticated"):
            sub = await apply_subscription_activation(db, sub_id, sub_entity)
            return {"status": "received", "matched": sub is not None}
        if event_type in ("subscription.cancelled", "subscription.completed"):
            sub = await apply_subscription_cancel(db, sub_id)
            return {"status": "received", "matched": sub is not None}
        # subscription.charged → renewal — just record raw event for now
        return {"status": "received", "matched": True}

    # ========================================
    # Payment link events (customer orders)
    # ========================================
    entity = payload_root.get("payment_link", {}).get("entity", {})
    link_id = entity.get("id")
    notes = entity.get("notes") or {}
    order_id_str = notes.get("order_id")

    order: Order | None = None
    if order_id_str:
        from uuid import UUID

        try:
            order_uuid = UUID(order_id_str)
            order = await db.get(Order, order_uuid)
        except ValueError:
            order = None
    if order is None and link_id:
        stmt = select(Order).where(Order.razorpay_payment_link_id == link_id)
        order = (await db.execute(stmt)).scalar_one_or_none()

    if order is None:
        logger.warning("Razorpay webhook: no matching order for link=%s", link_id)
        return {"status": "received", "matched": False}

    if event_type == "payment_link.paid":
        if order.payment_status == PaymentStatus.PAID:
            # Idempotent — already processed, ignore replay
            return {"status": "received", "matched": True, "idempotent": True}
        order.payment_status = PaymentStatus.PAID
        order.razorpay_payment_id = entity.get("payment_id") or entity.get("id")
        if order.status == OrderStatus.NEW:
            order.status = OrderStatus.CONFIRMED
    elif event_type in ("payment_link.expired", "payment_link.cancelled"):
        if order.payment_status == PaymentStatus.PENDING:
            order.payment_status = PaymentStatus.FAILED

    await db.commit()
    return {"status": "received", "matched": True}
