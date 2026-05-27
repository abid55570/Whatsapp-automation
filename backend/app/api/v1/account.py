"""Account management — data export, deletion (DPDP rights)."""
import io
import json
import logging
import uuid
import zipfile
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.models import (
    Business,
    Contact,
    Conversation,
    Message,
    Order,
    OrderItem,
    User,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/account", tags=["account"])


def _to_dict(obj: Any, fields: list[str]) -> dict:
    """Pick fields off an ORM object and JSON-serialize."""
    out: dict = {}
    for f in fields:
        val = getattr(obj, f, None)
        if isinstance(val, datetime):
            out[f] = val.isoformat()
        elif hasattr(val, "value"):  # enum
            out[f] = val.value
        elif val is None or isinstance(val, (str, int, float, bool, list, dict)):
            out[f] = val
        else:
            out[f] = str(val)
    return out


# ============================================================
# Data export (DPDP portability right)
# ============================================================


@router.get("/export", response_class=Response)
@(limiter.limit("5/hour") if limiter else (lambda f: f))
async def export_my_data(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Export all data belonging to the user as a ZIP of JSON files.

    Includes: user profile, business, contacts, conversations,
    messages, orders. Excludes encrypted secrets (access tokens).
    """
    # User
    user_dict = _to_dict(
        current_user,
        ["id", "phone", "email", "full_name", "phone_verified",
         "email_verified", "is_active", "preferred_language",
         "last_login_at", "created_at"],
    )

    # Business (if any)
    biz_stmt = (
        select(Business)
        .where(Business.owner_user_id == current_user.id)
        .options(selectinload(Business.subscription))
    )
    business = (await db.execute(biz_stmt)).scalar_one_or_none()
    biz_dict: dict | None = None
    if business is not None:
        biz_dict = _to_dict(
            business,
            ["id", "name", "business_type", "timezone", "languages",
             "whatsapp_display_phone", "onboarding_completed", "created_at"],
        )
        if business.subscription:
            biz_dict["subscription"] = _to_dict(
                business.subscription,
                ["plan", "status", "ai_addon_enabled", "trial_started_at",
                 "trial_ends_at", "current_period_start", "current_period_end",
                 "conversations_included", "conversations_used",
                 "ai_replies_included", "ai_replies_used"],
            )

    contacts_list: list[dict] = []
    conversations_list: list[dict] = []
    messages_list: list[dict] = []
    orders_list: list[dict] = []

    if business is not None:
        # Contacts
        c_stmt = select(Contact).where(Contact.business_id == business.id)
        for c in (await db.execute(c_stmt)).scalars().all():
            contacts_list.append(
                _to_dict(
                    c,
                    ["id", "whatsapp_phone", "name", "tags", "opted_out",
                     "first_seen_at", "last_seen_at", "created_at"],
                )
            )

        # Conversations
        conv_stmt = select(Conversation).where(
            Conversation.business_id == business.id
        )
        for conv in (await db.execute(conv_stmt)).scalars().all():
            conversations_list.append(
                _to_dict(
                    conv,
                    ["id", "contact_id", "category", "status", "started_at",
                     "expires_at", "last_message_at", "is_billable",
                     "meta_cost_paise", "unread_count"],
                )
            )

        # Messages
        m_stmt = select(Message).where(Message.business_id == business.id)
        for m in (await db.execute(m_stmt)).scalars().all():
            messages_list.append(
                _to_dict(
                    m,
                    ["id", "conversation_id", "contact_id", "direction",
                     "type", "status", "body", "is_auto_reply",
                     "matched_intent_key", "detected_language",
                     "sent_at", "delivered_at", "read_at", "created_at"],
                )
            )

        # Orders with items
        o_stmt = (
            select(Order)
            .where(Order.business_id == business.id)
            .options(selectinload(Order.items))
        )
        for o in (await db.execute(o_stmt)).scalars().all():
            o_dict = _to_dict(
                o,
                ["id", "order_number", "contact_id", "status",
                 "payment_status", "fulfillment_type", "payment_method",
                 "total_paise", "items_count", "pickup_time",
                 "delivery_address", "notes", "created_at"],
            )
            o_dict["items"] = [
                _to_dict(
                    it,
                    ["id", "product_name", "price_paise", "quantity",
                     "subtotal_paise"],
                )
                for it in o.items
            ]
            orders_list.append(o_dict)

    # Build ZIP in memory
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "user.json", json.dumps(user_dict, indent=2, ensure_ascii=False)
        )
        if biz_dict is not None:
            zf.writestr(
                "business.json",
                json.dumps(biz_dict, indent=2, ensure_ascii=False),
            )
        zf.writestr(
            "contacts.json",
            json.dumps(contacts_list, indent=2, ensure_ascii=False),
        )
        zf.writestr(
            "conversations.json",
            json.dumps(conversations_list, indent=2, ensure_ascii=False),
        )
        zf.writestr(
            "messages.json",
            json.dumps(messages_list, indent=2, ensure_ascii=False),
        )
        zf.writestr(
            "orders.json",
            json.dumps(orders_list, indent=2, ensure_ascii=False),
        )
        zf.writestr(
            "README.txt",
            "WhatsApp Auto — your data export\n"
            f"Exported at: {datetime.now(timezone.utc).isoformat()}\n\n"
            "Files:\n"
            "- user.json: your account profile\n"
            "- business.json: business profile + subscription\n"
            "- contacts.json: your customers\n"
            "- conversations.json: 24-hour billing windows\n"
            "- messages.json: every message in/out\n"
            "- orders.json: orders + items\n\n"
            "Sensitive credentials (WhatsApp access token, payment IDs)\n"
            "are intentionally excluded.\n",
        )

    buf.seek(0)
    filename = f"whatsapp-auto-export-{datetime.now(timezone.utc).strftime('%Y%m%d')}.zip"
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


# ============================================================
# Account deletion (DPDP erasure right)
# ============================================================


@router.delete("/me", status_code=status.HTTP_200_OK)
async def delete_my_account(
    confirm: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Soft-delete account. Data wiped after 30-day retention period.

    Requires `?confirm=DELETE` query param to prevent accidents.
    Cascades to business → conversations → messages → orders.
    """
    if confirm != "DELETE":
        raise HTTPException(
            status_code=400,
            detail="Pass ?confirm=DELETE to confirm. This action is irreversible.",
        )

    # Mark inactive; actual wipe happens via Celery task (30-day retention)
    current_user.is_active = False
    current_user.email = None  # release email for re-signup
    # Truncate phone to free up the unique slot (column is String(20))
    # Format: ".d.<8-hex-suffix>" (10 chars) → leaves up to 10 chars of original
    if ".d." not in current_user.phone:
        suffix = f".d.{uuid.uuid4().hex[:8]}"
        original = current_user.phone[: 20 - len(suffix)]
        current_user.phone = (original + suffix)[:20]

    await db.commit()
    logger.warning("User %s soft-deleted account", current_user.id)
    return {
        "status": "soft_deleted",
        "retention_until": (
            datetime.now(timezone.utc).timestamp() + 30 * 86400
        ),
        "message": "Account deactivated. Data permanently deleted in 30 days.",
    }
