"""Admin endpoints — superuser only. Platform-wide oversight."""
import logging
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_superuser, get_db
from app.models import (
    Business,
    Order,
    Subscription,
    User,
    WebhookEvent,
)
from app.models.enums import (
    OrderStatus,
    PaymentStatus,
    PlanType,
    SubscriptionStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_current_superuser)],
)


# ============================================================
# Schemas
# ============================================================


class AdminStats(BaseModel):
    total_users: int
    active_users: int
    superusers: int
    total_businesses: int
    onboarded_businesses: int
    trialing_subs: int
    active_subs: int
    frozen_subs: int
    canceled_subs: int
    plan_breakdown: dict[str, int]
    total_orders: int
    paid_orders: int
    total_revenue_paise: int
    webhook_events_24h: int


class AdminUserRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    phone: str
    email: str | None = None
    full_name: str | None = None
    is_active: bool
    is_superuser: bool
    phone_verified: bool
    preferred_language: str
    last_login_at: datetime | None = None
    created_at: datetime


class AdminBusinessRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    business_type: str
    owner_user_id: UUID
    whatsapp_connected: bool
    whatsapp_display_phone: str | None = None
    onboarding_completed: bool
    created_at: datetime
    plan: str | None = None
    sub_status: str | None = None


class AdminSubscriptionRow(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_id: UUID
    plan: str
    status: str
    ai_addon_enabled: bool
    trial_ends_at: datetime | None = None
    current_period_end: datetime | None = None
    conversations_used: int
    conversations_included: int
    razorpay_subscription_id: str | None = None
    created_at: datetime


class AdminUserUpdate(BaseModel):
    is_active: bool | None = None
    is_superuser: bool | None = None


class Paginated[T](BaseModel):
    items: list
    total: int
    limit: int
    offset: int
    has_more: bool


# ============================================================
# Stats
# ============================================================


@router.get("/stats", response_model=AdminStats)
async def admin_stats(db: AsyncSession = Depends(get_db)) -> AdminStats:
    """Platform-wide stats for superusers."""
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)

    total_users = await db.scalar(select(func.count(User.id))) or 0
    active_users = (
        await db.scalar(select(func.count(User.id)).where(User.is_active.is_(True)))
        or 0
    )
    superusers = (
        await db.scalar(
            select(func.count(User.id)).where(User.is_superuser.is_(True))
        )
        or 0
    )

    total_biz = await db.scalar(select(func.count(Business.id))) or 0
    onboarded = (
        await db.scalar(
            select(func.count(Business.id)).where(
                Business.onboarding_completed.is_(True)
            )
        )
        or 0
    )

    trialing = (
        await db.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.status == SubscriptionStatus.TRIALING
            )
        )
        or 0
    )
    active_subs = (
        await db.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.status == SubscriptionStatus.ACTIVE
            )
        )
        or 0
    )
    frozen = (
        await db.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.status == SubscriptionStatus.FROZEN
            )
        )
        or 0
    )
    canceled = (
        await db.scalar(
            select(func.count(Subscription.id)).where(
                Subscription.status == SubscriptionStatus.CANCELED
            )
        )
        or 0
    )

    plan_rows = await db.execute(
        select(Subscription.plan, func.count(Subscription.id))
        .where(Subscription.status == SubscriptionStatus.ACTIVE)
        .group_by(Subscription.plan)
    )
    plan_breakdown = {
        (p.value if hasattr(p, "value") else str(p)): c
        for p, c in plan_rows.all()
    }

    total_orders = await db.scalar(select(func.count(Order.id))) or 0
    paid_orders = (
        await db.scalar(
            select(func.count(Order.id)).where(
                Order.payment_status == PaymentStatus.PAID
            )
        )
        or 0
    )
    total_revenue = (
        await db.scalar(
            select(func.coalesce(func.sum(Order.total_paise), 0)).where(
                Order.payment_status == PaymentStatus.PAID
            )
        )
        or 0
    )

    webhooks_24h = (
        await db.scalar(
            select(func.count(WebhookEvent.id)).where(
                WebhookEvent.received_at >= day_ago
            )
        )
        or 0
    )

    return AdminStats(
        total_users=total_users,
        active_users=active_users,
        superusers=superusers,
        total_businesses=total_biz,
        onboarded_businesses=onboarded,
        trialing_subs=trialing,
        active_subs=active_subs,
        frozen_subs=frozen,
        canceled_subs=canceled,
        plan_breakdown=plan_breakdown,
        total_orders=total_orders,
        paid_orders=paid_orders,
        total_revenue_paise=total_revenue,
        webhook_events_24h=webhooks_24h,
    )


# ============================================================
# Users
# ============================================================


@router.get("/users", response_model=dict)
async def list_users(
    q: str | None = Query(None, description="Search by phone/email/name"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all users with optional search."""
    base = select(User)
    if q:
        like = f"%{q.lower()}%"
        base = base.where(
            (func.lower(User.phone).like(like))
            | (func.lower(User.email).like(like))
            | (func.lower(User.full_name).like(like))
        )

    total = await db.scalar(
        select(func.count()).select_from(base.subquery())
    )

    stmt = base.order_by(User.created_at.desc()).limit(limit).offset(offset)
    rows = (await db.execute(stmt)).scalars().all()

    return {
        "items": [AdminUserRow.model_validate(u).model_dump() for u in rows],
        "total": total or 0,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(rows)) < (total or 0),
    }


@router.patch("/users/{user_id}", response_model=AdminUserRow)
async def update_user(
    user_id: UUID,
    body: AdminUserUpdate,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(get_current_superuser),
) -> AdminUserRow:
    """Grant/revoke superuser, activate/deactivate user."""
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(404, "User not found")
    if user.id == current.id and body.is_superuser is False:
        raise HTTPException(400, "Cannot revoke your own superuser role")
    if user.id == current.id and body.is_active is False:
        raise HTTPException(400, "Cannot deactivate your own account")

    # Guard: refuse to remove the last remaining active superuser
    if body.is_superuser is False or body.is_active is False:
        active_supers = await db.scalar(
            select(func.count(User.id)).where(
                User.is_superuser.is_(True),
                User.is_active.is_(True),
                User.id != user.id,
            )
        )
        if (active_supers or 0) == 0 and user.is_superuser:
            raise HTTPException(
                400,
                "Cannot remove the last active superuser — promote another user first.",
            )

    changes: dict[str, dict] = {}
    if body.is_active is not None and user.is_active != body.is_active:
        changes["is_active"] = {"from": user.is_active, "to": body.is_active}
        user.is_active = body.is_active
    if body.is_superuser is not None and user.is_superuser != body.is_superuser:
        changes["is_superuser"] = {"from": user.is_superuser, "to": body.is_superuser}
        user.is_superuser = body.is_superuser

    await db.commit()
    await db.refresh(user)

    if changes:
        logger.warning(
            "admin_action user_update actor=%s target=%s changes=%s",
            current.id, user.id, changes,
        )
    return AdminUserRow.model_validate(user)


# ============================================================
# Businesses
# ============================================================


@router.get("/businesses", response_model=dict)
async def list_businesses(
    q: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all businesses with subscription info."""
    base = select(Business).options(selectinload(Business.subscription))
    if q:
        like = f"%{q.lower()}%"
        base = base.where(func.lower(Business.name).like(like))

    total = await db.scalar(
        select(func.count(Business.id)).where(
            *([func.lower(Business.name).like(f"%{q.lower()}%")] if q else [])
        )
    )

    stmt = (
        base.order_by(Business.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await db.execute(stmt)).scalars().all()

    items = []
    for b in rows:
        items.append(
            AdminBusinessRow(
                id=b.id,
                name=b.name,
                business_type=(
                    b.business_type.value
                    if hasattr(b.business_type, "value")
                    else str(b.business_type)
                ),
                owner_user_id=b.owner_user_id,
                whatsapp_connected=bool(
                    b.whatsapp_phone_number_id and b.whatsapp_access_token
                ),
                whatsapp_display_phone=b.whatsapp_display_phone,
                onboarding_completed=b.onboarding_completed,
                created_at=b.created_at,
                plan=(
                    b.subscription.plan.value
                    if b.subscription and hasattr(b.subscription.plan, "value")
                    else None
                ),
                sub_status=(
                    b.subscription.status.value
                    if b.subscription
                    and hasattr(b.subscription.status, "value")
                    else None
                ),
            ).model_dump()
        )

    return {
        "items": items,
        "total": total or 0,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(rows)) < (total or 0),
    }


# ============================================================
# Subscriptions
# ============================================================


@router.get("/subscriptions", response_model=dict)
async def list_subscriptions(
    status_filter: str | None = Query(None, alias="status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """List all subscriptions filtered by status."""
    base = select(Subscription)
    if status_filter:
        try:
            base = base.where(Subscription.status == SubscriptionStatus(status_filter))
        except ValueError:
            raise HTTPException(400, f"Invalid status: {status_filter}")

    total = await db.scalar(
        select(func.count()).select_from(base.subquery())
    )
    stmt = (
        base.order_by(Subscription.created_at.desc()).limit(limit).offset(offset)
    )
    rows = (await db.execute(stmt)).scalars().all()

    items = [
        AdminSubscriptionRow(
            id=s.id,
            business_id=s.business_id,
            plan=s.plan.value if hasattr(s.plan, "value") else str(s.plan),
            status=(
                s.status.value if hasattr(s.status, "value") else str(s.status)
            ),
            ai_addon_enabled=s.ai_addon_enabled,
            trial_ends_at=s.trial_ends_at,
            current_period_end=s.current_period_end,
            conversations_used=s.conversations_used,
            conversations_included=s.conversations_included,
            razorpay_subscription_id=s.razorpay_subscription_id,
            created_at=s.created_at,
        ).model_dump()
        for s in rows
    ]

    return {
        "items": items,
        "total": total or 0,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(rows)) < (total or 0),
    }


# ============================================================
# Webhook events (audit log)
# ============================================================


@router.get("/webhook-events", response_model=dict)
async def list_webhook_events(
    source: str | None = Query(None, description="meta_whatsapp / razorpay"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Recent webhook events for debugging."""
    base = select(WebhookEvent)
    if source:
        base = base.where(WebhookEvent.source == source)

    total = await db.scalar(
        select(func.count()).select_from(base.subquery())
    )
    stmt = (
        base.order_by(WebhookEvent.received_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await db.execute(stmt)).scalars().all()

    items = [
        {
            "id": str(e.id),
            "source": e.source,
            "event_type": e.event_type,
            "signature_verified": e.signature_verified,
            "processed": e.processed,
            "error": e.error,
            "received_at": e.received_at.isoformat(),
        }
        for e in rows
    ]

    return {
        "items": items,
        "total": total or 0,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + len(rows)) < (total or 0),
    }
