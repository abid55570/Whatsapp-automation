"""Pydantic schemas for owner-dashboard order endpoints."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OrderItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_name: str
    price_paise: int
    quantity: int
    subtotal_paise: int


class OrderContactSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    whatsapp_phone: str
    name: str | None = None


class OrderListItem(BaseModel):
    """Compact view for the orders list page."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    status: str
    payment_status: str
    fulfillment_type: str
    payment_method: str | None = None
    total_paise: int
    items_count: int
    pickup_time: datetime | None = None
    created_at: datetime
    contact: OrderContactSummary


class OrderDetail(BaseModel):
    """Full order detail."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    order_number: str
    status: str
    payment_status: str
    fulfillment_type: str
    payment_method: str | None = None
    total_paise: int
    items_count: int
    pickup_time: datetime | None = None
    pickup_landmark: str | None = None
    pickup_confirmed_at: datetime | None = None
    delivery_estimated_at: datetime | None = None
    delivery_address: dict = Field(default_factory=dict)
    notes: str | None = None
    razorpay_payment_link_id: str | None = None
    razorpay_payment_id: str | None = None
    created_at: datetime
    updated_at: datetime
    contact: OrderContactSummary
    items: list[OrderItemResponse] = Field(default_factory=list)


class OrderStatusUpdate(BaseModel):
    """PATCH body — owner transitions order state."""

    status: str = Field(
        ...,
        pattern="^(new|confirmed|preparing|ready_for_pickup|picked_up|"
        "packed|out_for_delivery|delivered|completed|canceled)$",
    )
    notes: str | None = None


class PaginatedOrders(BaseModel):
    items: list[OrderListItem]
    total: int
    limit: int
    offset: int
    has_more: bool
