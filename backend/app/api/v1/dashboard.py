"""Dashboard stats endpoint."""
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import Conversation, Message, User
from app.models.enums import ConversationStatus, MessageDirection
from app.schemas.stats import DashboardStats
from app.services.onboarding import get_my_business_or_404

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    """Aggregated stats for the dashboard home.

    All counts scoped to the user's business.
    `days` controls the lookback window (default 7).

    Internally we collapse what used to be 7+ separate `await db.scalar`
    round-trips into 3 grouped queries.
    """
    business = await get_my_business_or_404(db, current_user)

    now = datetime.now(timezone.utc)
    period_start = now - timedelta(days=days)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # ---- 1) All message aggregates (period-scoped) in one row ----
    msg_stmt = select(
        func.count(Message.id).label("total"),
        func.sum(
            case((Message.direction == MessageDirection.INBOUND, 1), else_=0)
        ).label("inbound"),
        func.sum(
            case((Message.is_auto_reply.is_(True), 1), else_=0)
        ).label("auto_replied"),
        func.count(func.distinct(Message.contact_id)).label("unique_contacts"),
    ).where(
        Message.business_id == business.id,
        Message.created_at >= period_start,
    )
    msg_row = (await db.execute(msg_stmt)).one()
    total = int(msg_row.total or 0)
    inbound = int(msg_row.inbound or 0)
    outbound = max(0, total - inbound)
    auto_replied = int(msg_row.auto_replied or 0)
    unique_contacts = int(msg_row.unique_contacts or 0)

    # ---- 2) Conversation aggregates in one row ----
    conv_stmt = select(
        func.sum(
            case((Conversation.unread_count > 0, 1), else_=0)
        ).label("needs_attention"),
        func.sum(
            case(
                (
                    (Conversation.status == ConversationStatus.OPEN)
                    & (Conversation.expires_at > now),
                    1,
                ),
                else_=0,
            )
        ).label("active_convs"),
        func.sum(
            case((Conversation.started_at >= today_start, 1), else_=0)
        ).label("convs_today"),
    ).where(Conversation.business_id == business.id)
    conv_row = (await db.execute(conv_stmt)).one()
    needs_attention = int(conv_row.needs_attention or 0)
    active_convs = int(conv_row.active_convs or 0)
    convs_today = int(conv_row.convs_today or 0)

    auto_rate = (auto_replied / inbound * 100.0) if inbound > 0 else 0.0

    # ---- 3) Language breakdown ----
    lang_stmt = (
        select(Message.detected_language, func.count(Message.id))
        .where(
            Message.business_id == business.id,
            Message.created_at >= period_start,
            Message.detected_language.is_not(None),
        )
        .group_by(Message.detected_language)
    )
    lang_rows = (await db.execute(lang_stmt)).all()
    languages = {lang: count for lang, count in lang_rows if lang}

    return DashboardStats(
        period_days=days,
        period_start=period_start,
        period_end=now,
        total_messages=total,
        inbound_messages=inbound,
        outbound_messages=outbound,
        auto_replied_count=auto_replied,
        needs_attention_count=needs_attention,
        unique_contacts=unique_contacts,
        active_conversations=active_convs,
        conversations_today=convs_today,
        auto_reply_rate=round(auto_rate, 1),
        matched_languages=languages,
    )
