"""Inbox / conversation / message endpoints."""
import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models import Business, Contact, Conversation, Message, User
from app.models.enums import MessageDirection, MessageStatus, MessageType
from app.schemas.conversation import (
    ContactSummary,
    ConversationDetail,
    ConversationListItem,
    MessageDetail,
    MessagePreview,
    PaginatedConversations,
    PaginatedMessages,
    SendMessageRequest,
)
from app.services.onboarding import get_my_business_or_404
from app.services.whatsapp.client import WhatsAppClient, WhatsAppClientError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


# ============================================================
# Helpers
# ============================================================


def _msg_to_preview(m: Message) -> MessagePreview:
    return MessagePreview(
        id=m.id,
        direction=m.direction.value if hasattr(m.direction, "value") else str(m.direction),
        body=m.body,
        type=m.type.value if hasattr(m.type, "value") else str(m.type),
        is_auto_reply=m.is_auto_reply,
        created_at=m.created_at,
    )


def _msg_to_detail(m: Message) -> MessageDetail:
    return MessageDetail(
        id=m.id,
        conversation_id=m.conversation_id,
        direction=m.direction.value if hasattr(m.direction, "value") else str(m.direction),
        type=m.type.value if hasattr(m.type, "value") else str(m.type),
        status=m.status.value if hasattr(m.status, "value") else str(m.status),
        body=m.body,
        media_url=m.media_url,
        media_mime_type=m.media_mime_type,
        template_name=m.template_name,
        is_auto_reply=m.is_auto_reply,
        matched_intent_key=m.matched_intent_key,
        matched_confidence=m.matched_confidence,
        matched_layer=m.matched_layer,
        detected_language=m.detected_language,
        sent_at=m.sent_at,
        delivered_at=m.delivered_at,
        read_at=m.read_at,
        failed_reason=m.failed_reason,
        created_at=m.created_at,
    )


def _contact_summary(c: Contact) -> ContactSummary:
    return ContactSummary(
        id=c.id,
        whatsapp_phone=c.whatsapp_phone,
        name=c.name,
        profile_picture_url=c.profile_picture_url,
        tags=list(c.tags),
    )


async def _load_last_message(
    db: AsyncSession, conversation_id: UUID
) -> Message | None:
    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(1)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _get_conversation_or_404(
    db: AsyncSession, conversation_id: UUID, business: Business
) -> Conversation:
    stmt = (
        select(Conversation)
        .where(
            Conversation.id == conversation_id,
            Conversation.business_id == business.id,
        )
        .options(selectinload(Conversation.contact))
    )
    conv = (await db.execute(stmt)).scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


# ============================================================
# List conversations
# ============================================================


@router.get("", response_model=PaginatedConversations)
async def list_conversations(
    filter: Literal["all", "unread"] = "all",
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedConversations:
    """List conversations for the user's business.

    Sorted by last message time (most recent first).
    """
    business = await get_my_business_or_404(db, current_user)

    base_filters = [Conversation.business_id == business.id]
    if filter == "unread":
        base_filters.append(Conversation.unread_count > 0)

    total = await db.scalar(
        select(func.count(Conversation.id)).where(*base_filters)
    )

    stmt = (
        select(Conversation)
        .where(*base_filters)
        .options(selectinload(Conversation.contact))
        .order_by(Conversation.last_message_at.desc().nulls_last())
        .limit(limit)
        .offset(offset)
    )
    conversations = (await db.execute(stmt)).scalars().all()

    # Batch-load the latest message per conversation in ONE query (kills N+1)
    last_msg_by_conv: dict[UUID, Message] = {}
    if conversations:
        conv_ids = [c.id for c in conversations]
        from sqlalchemy import tuple_

        # Subquery: max created_at per conversation among those we care about
        latest_sq = (
            select(
                Message.conversation_id,
                func.max(Message.created_at).label("max_ts"),
            )
            .where(Message.conversation_id.in_(conv_ids))
            .group_by(Message.conversation_id)
            .subquery()
        )
        latest_stmt = select(Message).join(
            latest_sq,
            (Message.conversation_id == latest_sq.c.conversation_id)
            & (Message.created_at == latest_sq.c.max_ts),
        )
        for msg in (await db.execute(latest_stmt)).scalars().all():
            # If ties on created_at (rare), keep the first we see
            last_msg_by_conv.setdefault(msg.conversation_id, msg)

    items: list[ConversationListItem] = []
    for conv in conversations:
        last_msg = last_msg_by_conv.get(conv.id)
        items.append(
            ConversationListItem(
                id=conv.id,
                contact=_contact_summary(conv.contact),
                last_message=_msg_to_preview(last_msg) if last_msg else None,
                unread_count=conv.unread_count,
                status=(
                    conv.status.value
                    if hasattr(conv.status, "value")
                    else str(conv.status)
                ),
                category=(
                    conv.category.value
                    if hasattr(conv.category, "value")
                    else str(conv.category)
                ),
                started_at=conv.started_at,
                last_message_at=conv.last_message_at,
                expires_at=conv.expires_at,
            )
        )

    return PaginatedConversations(
        items=items,
        total=total or 0,
        limit=limit,
        offset=offset,
        has_more=(offset + len(items)) < (total or 0),
    )


# ============================================================
# Single conversation
# ============================================================


@router.get("/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationDetail:
    business = await get_my_business_or_404(db, current_user)
    conv = await _get_conversation_or_404(db, conversation_id, business)
    return ConversationDetail(
        id=conv.id,
        contact=_contact_summary(conv.contact),
        status=(
            conv.status.value
            if hasattr(conv.status, "value")
            else str(conv.status)
        ),
        category=(
            conv.category.value
            if hasattr(conv.category, "value")
            else str(conv.category)
        ),
        started_at=conv.started_at,
        expires_at=conv.expires_at,
        last_message_at=conv.last_message_at,
        unread_count=conv.unread_count,
    )


# ============================================================
# Messages in a conversation
# ============================================================


@router.get(
    "/{conversation_id}/messages",
    response_model=PaginatedMessages,
)
async def list_messages(
    conversation_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedMessages:
    """List messages in a conversation, newest first."""
    business = await get_my_business_or_404(db, current_user)
    await _get_conversation_or_404(db, conversation_id, business)

    total = await db.scalar(
        select(func.count(Message.id)).where(
            Message.conversation_id == conversation_id,
        )
    )

    stmt = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    msgs = (await db.execute(stmt)).scalars().all()

    return PaginatedMessages(
        items=[_msg_to_detail(m) for m in msgs],
        total=total or 0,
        limit=limit,
        offset=offset,
        has_more=(offset + len(msgs)) < (total or 0),
    )


# ============================================================
# Send manual reply
# ============================================================


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageDetail,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    conversation_id: UUID,
    body: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageDetail:
    """Send a manual reply from the business owner."""
    business = await get_my_business_or_404(db, current_user)
    conv = await _get_conversation_or_404(db, conversation_id, business)

    if not (business.whatsapp_phone_number_id and business.whatsapp_access_token):
        raise HTTPException(
            status_code=400,
            detail="WhatsApp not connected. Connect from Settings.",
        )

    # Block sends if subscription not active or over quota
    from app.services.billing import business_can_send, has_conversation_quota
    if not await business_can_send(db, business):
        raise HTTPException(
            status_code=402,
            detail="Subscription not active. Upgrade to send messages.",
        )
    if not has_conversation_quota(business.subscription):
        raise HTTPException(
            status_code=402,
            detail="Conversation quota exhausted for this billing period.",
        )

    # Check 24h window — Meta only allows free-form text within session
    now = datetime.now(timezone.utc)
    if conv.expires_at and conv.expires_at < now:
        raise HTTPException(
            status_code=400,
            detail=(
                "24-hour session expired. Use a template message to re-engage "
                "this customer (coming soon)."
            ),
        )

    client = WhatsAppClient(
        phone_number_id=business.whatsapp_phone_number_id,
        access_token=business.whatsapp_access_token,
    )

    wamid: str | None = None
    msg_status = MessageStatus.SENT
    failed_reason: str | None = None

    try:
        response = await client.send_text(
            to=conv.contact.whatsapp_phone.lstrip("+"),
            body=body.body,
        )
        try:
            wamid = response.get("messages", [{}])[0].get("id")
        except (AttributeError, IndexError, TypeError):
            wamid = None
    except WhatsAppClientError as exc:
        msg_status = MessageStatus.FAILED
        failed_reason = str(exc)[:500]
        logger.error("Manual send failed: %s", exc)

    outbound = Message(
        conversation_id=conv.id,
        business_id=business.id,
        contact_id=conv.contact_id,
        whatsapp_message_id=wamid,
        direction=MessageDirection.OUTBOUND,
        type=MessageType.TEXT,
        status=msg_status,
        body=body.body,
        is_auto_reply=False,
        sent_at=now if msg_status == MessageStatus.SENT else None,
        failed_reason=failed_reason,
    )
    db.add(outbound)

    conv.last_message_at = now
    conv.unread_count = 0  # owner saw + replied

    await db.commit()
    await db.refresh(outbound)
    return _msg_to_detail(outbound)


# ============================================================
# Mark as read
# ============================================================


@router.post(
    "/{conversation_id}/mark-read",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def mark_conversation_read(
    conversation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    business = await get_my_business_or_404(db, current_user)
    conv = await _get_conversation_or_404(db, conversation_id, business)
    if conv.unread_count > 0:
        conv.unread_count = 0
        await db.commit()
