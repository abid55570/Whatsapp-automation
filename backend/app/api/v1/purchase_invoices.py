"""Purchase invoice (supplier bill) CRUD endpoints — for ITC tracking."""
import logging
from datetime import date as date_cls
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models import PurchaseInvoice, User
from app.models.enums import PurchaseInvoiceStatus
from app.schemas.purchase_invoice import (
    PaginatedPurchaseInvoices,
    PurchaseInvoiceCreate,
    PurchaseInvoiceResponse,
    PurchaseInvoiceUpdate,
)
from app.services.gst.validation import gstin_state_code
from app.services.onboarding import get_my_business_or_404

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/businesses/me/purchase-invoices",
    tags=["purchase-invoices"],
)


@router.get("", response_model=PaginatedPurchaseInvoices)
async def list_purchase_invoices(
    from_date: date_cls | None = Query(None, alias="from"),
    to_date: date_cls | None = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedPurchaseInvoices:
    business = await get_my_business_or_404(db, current_user)
    base = select(PurchaseInvoice).where(PurchaseInvoice.business_id == business.id)
    if from_date:
        base = base.where(PurchaseInvoice.bill_date >= from_date)
    if to_date:
        base = base.where(PurchaseInvoice.bill_date <= to_date)

    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = (
        await db.execute(
            base.order_by(PurchaseInvoice.bill_date.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()
    return PaginatedPurchaseInvoices(
        items=[PurchaseInvoiceResponse.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(rows)) < total,
    )


@router.post(
    "",
    response_model=PurchaseInvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_purchase_invoice(
    body: PurchaseInvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseInvoiceResponse:
    business = await get_my_business_or_404(db, current_user)

    state = body.supplier_state_code
    if not state and body.supplier_gstin:
        state = gstin_state_code(body.supplier_gstin)

    pi = PurchaseInvoice(
        business_id=business.id,
        supplier_name=body.supplier_name,
        supplier_gstin=body.supplier_gstin,
        supplier_state_code=state,
        bill_number=body.bill_number,
        bill_date=body.bill_date,
        taxable_paise=body.taxable_paise,
        cgst_paise=body.cgst_paise,
        sgst_paise=body.sgst_paise,
        igst_paise=body.igst_paise,
        cess_paise=body.cess_paise,
        total_paise=body.total_paise,
        category=body.category,
        is_capital_goods=body.is_capital_goods,
        is_itc_eligible=body.is_itc_eligible,
        notes=body.notes,
        status=PurchaseInvoiceStatus.RECORDED,
    )
    db.add(pi)
    await db.commit()
    await db.refresh(pi)
    return PurchaseInvoiceResponse.model_validate(pi)


@router.get("/{pi_id}", response_model=PurchaseInvoiceResponse)
async def get_purchase_invoice(
    pi_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseInvoiceResponse:
    business = await get_my_business_or_404(db, current_user)
    pi = await db.get(PurchaseInvoice, pi_id)
    if pi is None or pi.business_id != business.id:
        raise HTTPException(404, "Purchase invoice not found")
    return PurchaseInvoiceResponse.model_validate(pi)


@router.patch("/{pi_id}", response_model=PurchaseInvoiceResponse)
async def update_purchase_invoice(
    pi_id: UUID,
    body: PurchaseInvoiceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PurchaseInvoiceResponse:
    business = await get_my_business_or_404(db, current_user)
    pi = await db.get(PurchaseInvoice, pi_id)
    if pi is None or pi.business_id != business.id:
        raise HTTPException(404, "Purchase invoice not found")

    for field, value in body.model_dump(exclude_unset=True).items():
        if value is None and field != "status":
            continue
        if field == "status":
            pi.status = PurchaseInvoiceStatus(value)
        else:
            setattr(pi, field, value)

    await db.commit()
    await db.refresh(pi)
    return PurchaseInvoiceResponse.model_validate(pi)


@router.delete("/{pi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_purchase_invoice(
    pi_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    business = await get_my_business_or_404(db, current_user)
    pi = await db.get(PurchaseInvoice, pi_id)
    if pi is None or pi.business_id != business.id:
        raise HTTPException(404, "Purchase invoice not found")
    await db.delete(pi)
    await db.commit()
