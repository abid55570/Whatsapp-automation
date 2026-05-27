"""Schemas for fulfillment config endpoint."""
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import PickupPrepStrategy


class FulfillmentConfigResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    # Pickup
    pickup_enabled: bool
    pickup_address: str | None = None
    pickup_landmark: str | None = None
    pickup_hours_start: str
    pickup_hours_end: str
    pickup_closed_days: list[int] = Field(default_factory=list)
    pickup_prep_strategy: str
    pickup_fixed_minutes: int
    pickup_per_item_minutes: int
    pickup_slots: list[str] = Field(default_factory=list)
    # Delivery
    delivery_enabled: bool
    delivery_fee_paise: int
    delivery_minimum_order_paise: int
    delivery_radius_km: int
    delivery_estimate_minutes: int
    created_at: datetime
    updated_at: datetime


class FulfillmentConfigUpdate(BaseModel):
    """PUT body — all fields optional, replaces current values."""

    pickup_enabled: bool | None = None
    pickup_address: str | None = Field(None, max_length=500)
    pickup_landmark: str | None = Field(None, max_length=500)
    pickup_hours_start: str | None = Field(None, pattern=r"^[0-2]\d:[0-5]\d$")
    pickup_hours_end: str | None = Field(None, pattern=r"^[0-2]\d:[0-5]\d$")
    pickup_closed_days: list[int] | None = Field(None, max_length=7)
    pickup_prep_strategy: PickupPrepStrategy | None = None
    pickup_fixed_minutes: int | None = Field(None, ge=5, le=480)
    pickup_per_item_minutes: int | None = Field(None, ge=1, le=60)
    pickup_slots: list[str] | None = Field(None, max_length=20)

    delivery_enabled: bool | None = None
    delivery_fee_paise: int | None = Field(None, ge=0, le=100000)
    delivery_minimum_order_paise: int | None = Field(None, ge=0, le=1000000)
    delivery_radius_km: int | None = Field(None, ge=1, le=50)
    delivery_estimate_minutes: int | None = Field(None, ge=10, le=480)
