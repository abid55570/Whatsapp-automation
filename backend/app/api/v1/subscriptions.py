"""SaaS subscription endpoints: upgrade plan, cancel."""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import User
from app.models.enums import PlanType
from app.schemas.subscription_upgrade import UpgradeRequest, UpgradeResponse
from app.services.billing.subscriptions import start_upgrade
from app.services.onboarding import get_my_business_or_404
from app.services.payments import RazorpayError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses/me/subscription", tags=["subscription"])


@router.post(
    "/upgrade",
    response_model=UpgradeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upgrade_plan(
    body: UpgradeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UpgradeResponse:
    """Create a Razorpay subscription for the target plan.

    Returns a checkout URL — frontend redirects user there to pay.
    """
    business = await get_my_business_or_404(db, current_user)
    if body.plan == PlanType.TRIAL:
        raise HTTPException(400, "Cannot upgrade to trial")

    try:
        result = await start_upgrade(
            db,
            business=business,
            contact_phone=current_user.phone,
            contact_name=current_user.full_name,
            target_plan=body.plan,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RazorpayError as exc:
        logger.error("Razorpay upgrade failed: %s", exc)
        raise HTTPException(503, "Payment provider unavailable. Try later.") from exc

    return UpgradeResponse(
        razorpay_subscription_id=result.get("id", ""),
        short_url=result.get("short_url", ""),
        status=result.get("status", "created"),
        plan=body.plan.value,
    )


@router.post(
    "/cancel",
    status_code=status.HTTP_200_OK,
)
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Cancel active subscription at end of current billing period."""
    business = await get_my_business_or_404(db, current_user)
    sub = business.subscription
    if sub is None or not sub.razorpay_subscription_id:
        raise HTTPException(400, "No active subscription to cancel")

    from datetime import datetime, timezone
    from app.services.payments import RazorpayClient
    client = RazorpayClient()
    try:
        await client.cancel_subscription(
            sub.razorpay_subscription_id, cancel_at_cycle_end=True
        )
    except RazorpayError as exc:
        raise HTTPException(503, str(exc)) from exc

    # Mark canceled locally so UI updates immediately; webhook will confirm
    sub.canceled_at = datetime.now(timezone.utc)
    await db.commit()

    return {"status": "cancel_scheduled"}


# ============================================================
# Tax Pack add-on (₹299/mo) — GST invoicing, GSTR exports, ITR
# ============================================================


@router.post("/tax-pack/enable", status_code=status.HTTP_200_OK)
async def enable_tax_pack(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Toggle on the Tax Pack add-on for this business.

    In production this would trigger a Razorpay add-on subscription charge.
    For MVP we just flip the flag — billing reconciliation happens via webhook
    when integrated.
    """
    business = await get_my_business_or_404(db, current_user)
    business.tax_pack_enabled = True
    await db.commit()
    return {"tax_pack_enabled": True}


@router.post("/tax-pack/disable", status_code=status.HTTP_200_OK)
async def disable_tax_pack(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    business = await get_my_business_or_404(db, current_user)
    business.tax_pack_enabled = False
    await db.commit()
    return {"tax_pack_enabled": False}
