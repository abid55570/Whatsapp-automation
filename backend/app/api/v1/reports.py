"""Tax-filing report endpoints — xlsx / JSON exports for GSTR-1, GSTR-3B, etc."""
import calendar
import json
import logging
from datetime import date as date_cls
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.rate_limit import limiter
from app.models import Invoice, PurchaseInvoice, User
from app.models.enums import (
    InvoiceStatus,
    InvoiceType,
    PaymentStatus,
    PurchaseInvoiceStatus,
)
from app.models import Order
from app.services.gst import hsn_lookup
from app.services.gst.exporters import (
    gstr1 as gstr1_exporter,
    gstr3b_summary as gstr3b_exporter,
    itr4_pnl as itr4_exporter,
    purchase_register as pr_exporter,
    sales_register as sr_exporter,
)
from app.services.onboarding import get_my_business_or_404

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses/me/reports", tags=["reports"])


# ============================================================
# Helpers
# ============================================================


def _parse_month(month: str) -> date_cls:
    """Parse 'YYYY-MM' → first day of that month."""
    try:
        y, m = month.split("-")
        return date_cls(int(y), int(m), 1)
    except (ValueError, AttributeError):
        raise HTTPException(400, "month must be 'YYYY-MM'")


def _month_range(month_start: date_cls) -> tuple[date_cls, date_cls]:
    """Return (first, last) day of the given month."""
    last_day = calendar.monthrange(month_start.year, month_start.month)[1]
    return month_start, date_cls(month_start.year, month_start.month, last_day)


def _parse_fy(fy: str) -> tuple[date_cls, date_cls, str]:
    """Parse 'YYYY-YY' → (Apr 1 start, Mar 31 end, normalized label)."""
    try:
        start_year_str, end_short = fy.split("-")
        start_year = int(start_year_str)
        # Tolerate "2026-2027" or "2026-27" — normalize to "2026-27"
        expected_short = (start_year + 1) % 100
        label = f"{start_year}-{expected_short:02d}"
        return date_cls(start_year, 4, 1), date_cls(start_year + 1, 3, 31), label
    except (ValueError, AttributeError):
        raise HTTPException(400, "fy must be 'YYYY-YY' (e.g. 2026-27)")


async def _fetch_invoices(
    db: AsyncSession, business_id, period_from: date_cls, period_to: date_cls
) -> list[Invoice]:
    stmt = (
        select(Invoice)
        .where(
            Invoice.business_id == business_id,
            Invoice.invoice_date >= period_from,
            Invoice.invoice_date <= period_to,
        )
        .options(selectinload(Invoice.lines))
        .order_by(Invoice.invoice_date, Invoice.invoice_number)
    )
    return (await db.execute(stmt)).scalars().all()


async def _fetch_purchase_invoices(
    db: AsyncSession, business_id, period_from: date_cls, period_to: date_cls
) -> list[PurchaseInvoice]:
    stmt = (
        select(PurchaseInvoice)
        .where(
            PurchaseInvoice.business_id == business_id,
            PurchaseInvoice.bill_date >= period_from,
            PurchaseInvoice.bill_date <= period_to,
        )
        .order_by(PurchaseInvoice.bill_date)
    )
    return (await db.execute(stmt)).scalars().all()


# ============================================================
# Sales register (xlsx)
# ============================================================


@router.get("/sales-register")
@(limiter.limit("10/hour") if limiter else (lambda f: f))
async def sales_register(
    request: Request,
    from_date: date_cls | None = Query(None, alias="from"),
    to_date: date_cls | None = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Multi-sheet xlsx — sales register for the period."""
    business = await get_my_business_or_404(db, current_user)

    if not to_date:
        to_date = datetime.now(timezone.utc).date()
    if not from_date:
        from_date = (to_date.replace(day=1))

    invoices = await _fetch_invoices(db, business.id, from_date, to_date)
    xlsx_bytes = sr_exporter.build_sales_register(business, invoices, from_date, to_date)

    fn = f"sales-register-{from_date.isoformat()}-to-{to_date.isoformat()}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


# ============================================================
# GSTR-1 JSON
# ============================================================


@router.get("/gstr1")
@(limiter.limit("10/hour") if limiter else (lambda f: f))
async def gstr1(
    request: Request,
    month: str = Query(..., description="YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GSTR-1 JSON payload — upload-ready for gst.gov.in offline tool."""
    business = await get_my_business_or_404(db, current_user)
    if not business.gstin:
        raise HTTPException(400, "GSTIN not set — configure in Settings → GST")

    month_start = _parse_month(month)
    period_from, period_to = _month_range(month_start)
    invoices = await _fetch_invoices(db, business.id, period_from, period_to)
    payload = gstr1_exporter.build_gstr1_json(business, invoices, month_start)

    fn = f"gstr1-{business.gstin}-{month_start.strftime('%m%Y')}.json"
    return Response(
        content=json.dumps(payload, indent=2, ensure_ascii=False),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


# ============================================================
# GSTR-3B summary (xlsx)
# ============================================================


@router.get("/gstr3b-summary")
@(limiter.limit("10/hour") if limiter else (lambda f: f))
async def gstr3b(
    request: Request,
    month: str = Query(..., description="YYYY-MM"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """GSTR-3B summary xlsx — owner fills in numbers on gst.gov.in."""
    business = await get_my_business_or_404(db, current_user)

    month_start = _parse_month(month)
    period_from, period_to = _month_range(month_start)
    invoices = await _fetch_invoices(db, business.id, period_from, period_to)
    purchases = await _fetch_purchase_invoices(db, business.id, period_from, period_to)
    xlsx_bytes = gstr3b_exporter.build_gstr3b_summary(
        business, invoices, purchases, month_start
    )

    fn = f"gstr3b-summary-{month_start.strftime('%Y-%m')}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


# ============================================================
# Purchase register (xlsx)
# ============================================================


@router.get("/itr4")
@(limiter.limit("10/hour") if limiter else (lambda f: f))
async def itr4_pnl(
    request: Request,
    fy: str = Query(..., description="Fiscal year 'YYYY-YY' (e.g. 2026-27)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Annual P&L worksheet for ITR-4 (presumptive scheme) filing."""
    business = await get_my_business_or_404(db, current_user)
    fy_start, fy_end, fy_label = _parse_fy(fy)

    invoices = await _fetch_invoices(db, business.id, fy_start, fy_end)
    purchases = await _fetch_purchase_invoices(db, business.id, fy_start, fy_end)

    # Optionally pull linked orders for cash/digital classification
    orders_by_invoice: dict = {}
    invoice_ids_with_orders = [i.order_id for i in invoices if i.order_id]
    if invoice_ids_with_orders:
        order_rows = (
            await db.execute(
                select(Order).where(Order.id.in_(invoice_ids_with_orders))
            )
        ).scalars().all()
        order_by_id = {o.id: o for o in order_rows}
        for inv in invoices:
            if inv.order_id and inv.order_id in order_by_id:
                orders_by_invoice[inv.id] = order_by_id[inv.order_id]

    xlsx_bytes = itr4_exporter.build_itr4_pnl(
        business, invoices, purchases, fy_label, fy_start, fy_end,
        orders_by_invoice=orders_by_invoice,
    )

    fn = f"itr4-pnl-{fy_label}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


@router.get("/purchase-register")
@(limiter.limit("10/hour") if limiter else (lambda f: f))
async def purchase_register(
    request: Request,
    from_date: date_cls | None = Query(None, alias="from"),
    to_date: date_cls | None = Query(None, alias="to"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    business = await get_my_business_or_404(db, current_user)
    if not to_date:
        to_date = datetime.now(timezone.utc).date()
    if not from_date:
        from_date = to_date.replace(day=1)

    purchases = await _fetch_purchase_invoices(db, business.id, from_date, to_date)
    xlsx_bytes = pr_exporter.build_purchase_register(business, purchases, from_date, to_date)

    fn = f"purchase-register-{from_date.isoformat()}-to-{to_date.isoformat()}.xlsx"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{fn}"'},
    )


# ============================================================
# Reports overview — for the Tax Filing Center dashboard
# ============================================================


@router.get("/overview")
@(limiter.limit("60/minute") if limiter else (lambda f: f))
async def reports_overview(
    request: Request,
    month: str | None = Query(None, description="YYYY-MM, defaults to current month"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Aggregate KPIs for the Tax Filing Center page."""
    business = await get_my_business_or_404(db, current_user)

    if month:
        month_start = _parse_month(month)
    else:
        now = datetime.now(timezone.utc)
        month_start = date_cls(now.year, now.month, 1)
    period_from, period_to = _month_range(month_start)

    # Use SQL aggregates for speed
    inv_agg = (
        await db.execute(
            select(
                func.count(Invoice.id).label("count"),
                func.coalesce(func.sum(Invoice.taxable_paise), 0).label("taxable"),
                func.coalesce(func.sum(Invoice.cgst_paise), 0).label("cgst"),
                func.coalesce(func.sum(Invoice.sgst_paise), 0).label("sgst"),
                func.coalesce(func.sum(Invoice.igst_paise), 0).label("igst"),
                func.coalesce(func.sum(Invoice.cess_paise), 0).label("cess"),
                func.coalesce(func.sum(Invoice.total_paise), 0).label("total"),
            ).where(
                Invoice.business_id == business.id,
                Invoice.invoice_date >= period_from,
                Invoice.invoice_date <= period_to,
                Invoice.status != InvoiceStatus.CANCELLED,
            )
        )
    ).one()

    purch_agg = (
        await db.execute(
            select(
                func.count(PurchaseInvoice.id).label("count"),
                func.coalesce(func.sum(PurchaseInvoice.taxable_paise), 0).label("taxable"),
                func.coalesce(func.sum(PurchaseInvoice.cgst_paise), 0).label("cgst"),
                func.coalesce(func.sum(PurchaseInvoice.sgst_paise), 0).label("sgst"),
                func.coalesce(func.sum(PurchaseInvoice.igst_paise), 0).label("igst"),
                func.coalesce(func.sum(PurchaseInvoice.cess_paise), 0).label("cess"),
                func.coalesce(func.sum(PurchaseInvoice.total_paise), 0).label("total"),
            ).where(
                PurchaseInvoice.business_id == business.id,
                PurchaseInvoice.bill_date >= period_from,
                PurchaseInvoice.bill_date <= period_to,
                PurchaseInvoice.status != PurchaseInvoiceStatus.CANCELLED,
                PurchaseInvoice.is_itc_eligible.is_(True),
            )
        )
    ).one()

    tax_to_pay = max(
        0,
        (inv_agg.cgst + inv_agg.sgst + inv_agg.igst + inv_agg.cess)
        - (purch_agg.cgst + purch_agg.sgst + purch_agg.igst + purch_agg.cess),
    )

    return {
        "period": {
            "month": month_start.strftime("%Y-%m"),
            "label": month_start.strftime("%B %Y"),
            "from": period_from.isoformat(),
            "to": period_to.isoformat(),
        },
        "sales": {
            "invoices": int(inv_agg.count or 0),
            "taxable_paise": int(inv_agg.taxable or 0),
            "cgst_paise": int(inv_agg.cgst or 0),
            "sgst_paise": int(inv_agg.sgst or 0),
            "igst_paise": int(inv_agg.igst or 0),
            "cess_paise": int(inv_agg.cess or 0),
            "total_paise": int(inv_agg.total or 0),
        },
        "purchases": {
            "bills": int(purch_agg.count or 0),
            "taxable_paise": int(purch_agg.taxable or 0),
            "itc_available_paise": int(
                purch_agg.cgst + purch_agg.sgst + purch_agg.igst + purch_agg.cess
            ),
        },
        "tax_to_pay_paise": int(tax_to_pay),
        "gstin_set": bool(business.gstin),
        "tax_pack_enabled": business.tax_pack_enabled,
    }
