"""Owner-dashboard order endpoints (list / get / status update)."""
import logging
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.models import Order, OrderItem, User
from app.models.enums import OrderStatus
from app.schemas.order import (
    OrderContactSummary,
    OrderDetail,
    OrderItemResponse,
    OrderListItem,
    OrderStatusUpdate,
    PaginatedOrders,
)
from app.services.onboarding import get_my_business_or_404

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses/me/orders", tags=["orders"])


def _to_list_item(o: Order) -> OrderListItem:
    return OrderListItem(
        id=o.id,
        order_number=o.order_number,
        status=o.status.value if hasattr(o.status, "value") else str(o.status),
        payment_status=(
            o.payment_status.value
            if hasattr(o.payment_status, "value")
            else str(o.payment_status)
        ),
        fulfillment_type=(
            o.fulfillment_type.value
            if hasattr(o.fulfillment_type, "value")
            else str(o.fulfillment_type)
        ),
        payment_method=(
            o.payment_method.value
            if o.payment_method and hasattr(o.payment_method, "value")
            else (str(o.payment_method) if o.payment_method else None)
        ),
        total_paise=o.total_paise,
        items_count=o.items_count,
        pickup_time=o.pickup_time,
        created_at=o.created_at,
        contact=OrderContactSummary(
            id=o.contact.id,
            whatsapp_phone=o.contact.whatsapp_phone,
            name=o.contact.name,
        ),
    )


def _to_detail(o: Order) -> OrderDetail:
    return OrderDetail(
        id=o.id,
        order_number=o.order_number,
        status=o.status.value if hasattr(o.status, "value") else str(o.status),
        payment_status=(
            o.payment_status.value
            if hasattr(o.payment_status, "value")
            else str(o.payment_status)
        ),
        fulfillment_type=(
            o.fulfillment_type.value
            if hasattr(o.fulfillment_type, "value")
            else str(o.fulfillment_type)
        ),
        payment_method=(
            o.payment_method.value
            if o.payment_method and hasattr(o.payment_method, "value")
            else (str(o.payment_method) if o.payment_method else None)
        ),
        total_paise=o.total_paise,
        items_count=o.items_count,
        pickup_time=o.pickup_time,
        pickup_landmark=o.pickup_landmark,
        pickup_confirmed_at=o.pickup_confirmed_at,
        delivery_estimated_at=o.delivery_estimated_at,
        delivery_address=dict(o.delivery_address or {}),
        notes=o.notes,
        razorpay_payment_link_id=o.razorpay_payment_link_id,
        razorpay_payment_id=o.razorpay_payment_id,
        created_at=o.created_at,
        updated_at=o.updated_at,
        contact=OrderContactSummary(
            id=o.contact.id,
            whatsapp_phone=o.contact.whatsapp_phone,
            name=o.contact.name,
        ),
        items=[
            OrderItemResponse(
                id=it.id,
                product_name=it.product_name,
                price_paise=it.price_paise,
                quantity=it.quantity,
                subtotal_paise=it.subtotal_paise,
            )
            for it in o.items
        ],
    )


# ============================================================
# List
# ============================================================


@router.get("", response_model=PaginatedOrders)
async def list_orders(
    status_filter: Literal[
        "all", "active", "completed", "canceled"
    ] = Query("all", alias="filter"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedOrders:
    business = await get_my_business_or_404(db, current_user)

    filters = [Order.business_id == business.id]
    if status_filter == "active":
        filters.append(
            Order.status.notin_(
                [
                    OrderStatus.PICKED_UP,
                    OrderStatus.DELIVERED,
                    OrderStatus.COMPLETED,
                    OrderStatus.CANCELED,
                ]
            )
        )
    elif status_filter == "completed":
        filters.append(
            Order.status.in_(
                [
                    OrderStatus.PICKED_UP,
                    OrderStatus.DELIVERED,
                    OrderStatus.COMPLETED,
                ]
            )
        )
    elif status_filter == "canceled":
        filters.append(Order.status == OrderStatus.CANCELED)

    total = await db.scalar(select(func.count(Order.id)).where(*filters))

    stmt = (
        select(Order)
        .where(*filters)
        .options(selectinload(Order.contact))
        .order_by(Order.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    orders = (await db.execute(stmt)).scalars().all()

    return PaginatedOrders(
        items=[_to_list_item(o) for o in orders],
        total=total or 0,
        limit=limit,
        offset=offset,
        has_more=(offset + len(orders)) < (total or 0),
    )


# ============================================================
# Detail
# ============================================================


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(
    order_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderDetail:
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.business_id == business.id)
        .options(selectinload(Order.contact), selectinload(Order.items))
    )
    order = (await db.execute(stmt)).scalar_one_or_none()
    if order is None:
        raise HTTPException(404, "Order not found")
    return _to_detail(order)


# ============================================================
# Status update (also sends WhatsApp notification to customer)
# ============================================================


@router.patch("/{order_id}", response_model=OrderDetail)
async def update_order_status(
    order_id: UUID,
    body: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OrderDetail:
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(Order)
        .where(Order.id == order_id, Order.business_id == business.id)
        .options(selectinload(Order.contact), selectinload(Order.items))
    )
    order = (await db.execute(stmt)).scalar_one_or_none()
    if order is None:
        raise HTTPException(404, "Order not found")

    old_status = order.status
    try:
        new_status = OrderStatus(body.status)
    except ValueError as exc:
        raise HTTPException(400, f"Invalid status: {body.status}") from exc

    order.status = new_status
    if body.notes is not None:
        order.notes = body.notes
    if new_status == OrderStatus.PICKED_UP:
        order.pickup_confirmed_at = datetime.now(timezone.utc)
    await db.commit()
    # Only refresh scalar columns — leave relationships (contact, items) intact
    # so subsequent _notify_customer_status_change doesn't trigger lazy load.
    await db.refresh(
        order,
        attribute_names=[
            "status", "notes", "pickup_confirmed_at",
            "payment_status", "fulfillment_type", "payment_method",
            "total_paise", "items_count", "pickup_time",
            "updated_at",
        ],
    )

    # Notify customer (best-effort)
    try:
        await _notify_customer_status_change(business, order, old_status, new_status)
    except Exception as exc:
        logger.warning("Failed to notify customer: %s", exc)

    return _to_detail(order)


async def _notify_customer_status_change(
    business,
    order: Order,
    old_status,
    new_status: OrderStatus,
) -> None:
    """Send a WhatsApp message to the customer when status changes."""
    if not (business.whatsapp_phone_number_id and business.whatsapp_access_token):
        return

    msg = _status_change_message(order, new_status)
    if not msg:
        return

    from app.services.whatsapp.client import WhatsAppClient

    client = WhatsAppClient(
        phone_number_id=business.whatsapp_phone_number_id,
        access_token=business.whatsapp_access_token,
    )
    try:
        await client.send_text(
            to=order.contact.whatsapp_phone.lstrip("+"),
            body=msg,
        )
    except Exception as exc:
        logger.warning("WhatsApp notify failed: %s", exc)


def _status_change_message(order: Order, new_status: OrderStatus) -> str | None:
    """Build a customer-facing message for status transitions."""
    num = order.order_number
    table = {
        OrderStatus.CONFIRMED: f"✅ Order #{num} confirmed. We're getting it ready.",
        OrderStatus.PREPARING: f"👨‍🍳 Order #{num} — we're preparing it now.",
        OrderStatus.READY_FOR_PICKUP: (
            f"🔔 Order #{num} is ready for pickup! Come collect anytime."
        ),
        OrderStatus.PICKED_UP: (
            f"✨ Thanks for picking up Order #{num}! Hope to see you again. ⭐⭐⭐⭐⭐"
        ),
        OrderStatus.OUT_FOR_DELIVERY: f"🛵 Order #{num} is out for delivery!",
        OrderStatus.DELIVERED: (
            f"✨ Order #{num} delivered. Hope you enjoyed!"
        ),
        OrderStatus.COMPLETED: f"✓ Order #{num} completed. Thank you!",
        OrderStatus.CANCELED: f"❌ Order #{num} canceled.",
    }
    return table.get(new_status)
