"""Fulfillment config endpoints (per-business pickup/delivery settings)."""
import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import FulfillmentConfig, User
from app.schemas.fulfillment import (
    FulfillmentConfigResponse,
    FulfillmentConfigUpdate,
)
from app.services.onboarding import get_my_business_or_404

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses/me/fulfillment-config", tags=["fulfillment"])


def _to_response(c: FulfillmentConfig) -> FulfillmentConfigResponse:
    return FulfillmentConfigResponse(
        id=c.id,
        pickup_enabled=c.pickup_enabled,
        pickup_address=c.pickup_address,
        pickup_landmark=c.pickup_landmark,
        pickup_hours_start=c.pickup_hours_start,
        pickup_hours_end=c.pickup_hours_end,
        pickup_closed_days=list(c.pickup_closed_days or []),
        pickup_prep_strategy=(
            c.pickup_prep_strategy.value
            if hasattr(c.pickup_prep_strategy, "value")
            else str(c.pickup_prep_strategy)
        ),
        pickup_fixed_minutes=c.pickup_fixed_minutes,
        pickup_per_item_minutes=c.pickup_per_item_minutes,
        pickup_slots=list(c.pickup_slots or []),
        delivery_enabled=c.delivery_enabled,
        delivery_fee_paise=c.delivery_fee_paise,
        delivery_minimum_order_paise=c.delivery_minimum_order_paise,
        delivery_radius_km=c.delivery_radius_km,
        delivery_estimate_minutes=c.delivery_estimate_minutes,
        created_at=c.created_at,
        updated_at=c.updated_at,
    )


async def _get_or_create(
    db: AsyncSession, business_id
) -> FulfillmentConfig:
    """Return the FulfillmentConfig row, creating with defaults if missing."""
    stmt = select(FulfillmentConfig).where(
        FulfillmentConfig.business_id == business_id
    )
    config = (await db.execute(stmt)).scalar_one_or_none()
    if config is None:
        config = FulfillmentConfig(business_id=business_id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.get("", response_model=FulfillmentConfigResponse)
async def get_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FulfillmentConfigResponse:
    business = await get_my_business_or_404(db, current_user)
    config = await _get_or_create(db, business.id)
    return _to_response(config)


@router.put("", response_model=FulfillmentConfigResponse)
async def update_config(
    body: FulfillmentConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FulfillmentConfigResponse:
    business = await get_my_business_or_404(db, current_user)
    config = await _get_or_create(db, business.id)

    # Patch fields that were sent
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(config, field, value)

    await db.commit()
    await db.refresh(config)
    return _to_response(config)
