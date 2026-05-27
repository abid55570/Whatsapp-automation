"""Invoice endpoints: CRUD + PDF + WhatsApp share."""
import logging
from datetime import date as date_cls
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_db
from app.core.rate_limit import limiter
from app.core.storage import (
    StorageError,
    build_invoice_object_key,
    signed_url,
    upload_pdf,
)
from app.models import Business, Invoice, User
from app.models.enums import InvoiceStatus
from app.schemas.invoice import (
    GstSettingsResponse,
    GstSettingsUpdate,
    InvoiceCancelRequest,
    InvoiceCreate,
    InvoiceResponse,
    InvoiceShareRequest,
    PaginatedInvoices,
)
from app.services.gst import einvoice as einvoice_svc
from app.services.gst import hsn_lookup
from app.services.gst.einvoice import EInvoiceError, EInvoiceNotApplicable
from app.services.gst.pdf_generator import generate_invoice_pdf
from app.services.gst.service import (
    attach_pdf_to_invoice,
    cancel_invoice,
    create_invoice,
)
from app.services.gst.share import send_invoice_via_whatsapp
from app.services.gst.state_codes import is_valid_state_code
from app.services.gst.validation import gstin_state_code
from app.services.onboarding import get_my_business_or_404

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/businesses/me", tags=["invoices"])


# ============================================================
# GST settings (owner profile fields used in invoice PDF)
# ============================================================


@router.get("/gst-settings", response_model=GstSettingsResponse)
async def get_gst_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GstSettingsResponse:
    business = await get_my_business_or_404(db, current_user)
    return GstSettingsResponse(
        gstin=business.gstin,
        gst_state_code=business.gst_state_code,
        gst_scheme=(
            business.gst_scheme.value
            if hasattr(business.gst_scheme, "value")
            else str(business.gst_scheme)
        ),
        gst_composition_rate=business.gst_composition_rate,
        legal_name=business.legal_name,
        pan=business.pan,
        business_address_line1=business.business_address_line1,
        business_address_line2=business.business_address_line2,
        business_city=business.business_city,
        business_state=business.business_state,
        business_pincode=business.business_pincode,
        invoice_prefix=business.invoice_prefix,
        invoice_seq=business.invoice_seq,
        current_invoice_fy=business.current_invoice_fy,
        tax_pack_enabled=business.tax_pack_enabled,
    )


@router.put("/gst-settings", response_model=GstSettingsResponse)
async def update_gst_settings(
    body: GstSettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GstSettingsResponse:
    business = await get_my_business_or_404(db, current_user)

    # Auto-derive state code from GSTIN if present
    if body.gstin is not None:
        business.gstin = body.gstin
        derived = gstin_state_code(body.gstin)
        if derived and is_valid_state_code(derived):
            business.gst_state_code = derived

    if body.gst_scheme is not None:
        business.gst_scheme = body.gst_scheme  # SQLAlchemy enum accepts str value
    if body.gst_composition_rate is not None:
        business.gst_composition_rate = body.gst_composition_rate
    if body.legal_name is not None:
        business.legal_name = body.legal_name
    if body.pan is not None:
        business.pan = body.pan
    if body.business_address_line1 is not None:
        business.business_address_line1 = body.business_address_line1
    if body.business_address_line2 is not None:
        business.business_address_line2 = body.business_address_line2
    if body.business_city is not None:
        business.business_city = body.business_city
    if body.business_state is not None:
        business.business_state = body.business_state
    if body.business_pincode is not None:
        business.business_pincode = body.business_pincode
    if body.invoice_prefix is not None:
        business.invoice_prefix = body.invoice_prefix.strip().upper()[:6]

    await db.commit()
    await db.refresh(business)
    return await get_gst_settings(current_user, db)


# ============================================================
# Invoice CRUD
# ============================================================


@router.get("/invoices", response_model=PaginatedInvoices)
async def list_invoices(
    status_filter: Literal["all", "draft", "issued", "paid", "cancelled"] = Query(
        "all", alias="status"
    ),
    from_date: date_cls | None = Query(None, alias="from"),
    to_date: date_cls | None = Query(None, alias="to"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PaginatedInvoices:
    business = await get_my_business_or_404(db, current_user)

    base = (
        select(Invoice)
        .where(Invoice.business_id == business.id)
        .options(selectinload(Invoice.lines))
    )
    if status_filter != "all":
        base = base.where(Invoice.status == InvoiceStatus(status_filter))
    if from_date:
        base = base.where(Invoice.invoice_date >= from_date)
    if to_date:
        base = base.where(Invoice.invoice_date <= to_date)

    total = await db.scalar(select(func.count()).select_from(base.subquery())) or 0
    rows = (
        await db.execute(
            base.order_by(Invoice.invoice_date.desc(), Invoice.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).scalars().all()

    return PaginatedInvoices(
        items=[InvoiceResponse.model_validate(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + len(rows)) < total,
    )


@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_invoice_endpoint(
    body: InvoiceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    business = await get_my_business_or_404(db, current_user)

    invoice = await create_invoice(
        db,
        business=business,
        lines_input=[line.model_dump() for line in body.lines],
        cx_name=body.cx_name,
        cx_phone=body.cx_phone,
        cx_gstin=body.cx_gstin,
        cx_address=body.cx_address,
        cx_state_code=body.cx_state_code,
        place_of_supply=body.place_of_supply,
        reverse_charge=body.reverse_charge,
        notes=body.notes,
        invoice_date_override=body.invoice_date,
        issue_now=body.issue_now,
    )
    return InvoiceResponse.model_validate(invoice)


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.business_id == business.id)
        .options(selectinload(Invoice.lines))
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if invoice is None:
        raise HTTPException(404, "Invoice not found")
    return InvoiceResponse.model_validate(invoice)


@router.post("/invoices/{invoice_id}/cancel", response_model=InvoiceResponse)
async def cancel_invoice_endpoint(
    invoice_id: UUID,
    body: InvoiceCancelRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvoiceResponse:
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.business_id == business.id)
        .options(selectinload(Invoice.lines))
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if invoice is None:
        raise HTTPException(404, "Invoice not found")
    try:
        await cancel_invoice(db, invoice, body.reason)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    return InvoiceResponse.model_validate(invoice)


# ============================================================
# PDF generation + download + share
# ============================================================


async def _ensure_pdf(invoice: Invoice, business: Business, db: AsyncSession) -> str:
    """Generate (or reuse) PDF and return a download URL."""
    if invoice.pdf_url and invoice.pdf_object_key:
        # Re-sign URL since the old one may have expired
        try:
            url = signed_url(invoice.pdf_object_key)
            if url != invoice.pdf_url:
                invoice.pdf_url = url
                await db.commit()
                await db.refresh(invoice, attribute_names=["pdf_url"])
            return url
        except StorageError:
            # Fall through to regeneration
            pass

    pdf_bytes = generate_invoice_pdf(invoice, business)
    object_key = build_invoice_object_key(
        str(invoice.business_id), invoice.fiscal_year, invoice.invoice_number
    )
    upload_pdf(
        object_key,
        pdf_bytes,
        content_disposition=f'inline; filename="{invoice.invoice_number}.pdf"',
    )
    url = signed_url(object_key)
    await attach_pdf_to_invoice(db, invoice, object_key, url)
    return url


@router.get("/invoices/{invoice_id}/pdf")
async def get_invoice_pdf(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate (if needed) + stream the invoice PDF.

    Returns the PDF bytes inline. If R2 is configured we cache there; if not,
    we serve the freshly-generated bytes directly.
    """
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.business_id == business.id)
        .options(selectinload(Invoice.lines))
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if invoice is None:
        raise HTTPException(404, "Invoice not found")

    # If we already cached the PDF in R2, redirect there instead of regenerating
    if invoice.pdf_object_key:
        try:
            url = signed_url(invoice.pdf_object_key)
            if url != invoice.pdf_url:
                invoice.pdf_url = url
                await db.commit()
            return Response(
                status_code=307,
                headers={"Location": url},
            )
        except StorageError:
            # Cached key but storage now misconfigured — fall through to regen
            pass

    try:
        pdf_bytes = generate_invoice_pdf(invoice, business)
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc

    # Cache to R2 if configured — best-effort
    try:
        object_key = build_invoice_object_key(
            str(invoice.business_id), invoice.fiscal_year, invoice.invoice_number
        )
        upload_pdf(
            object_key,
            pdf_bytes,
            content_disposition=f'inline; filename="{invoice.invoice_number}.pdf"',
        )
        url = signed_url(object_key)
        await attach_pdf_to_invoice(db, invoice, object_key, url)
    except StorageError:
        # Storage not configured — that's OK, still serve the bytes
        pass

    filename = f"{invoice.invoice_number}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{filename}"',
            "Cache-Control": "private, max-age=300",
        },
    )


# ============================================================
# HSN auto-suggest
# ============================================================


@router.get("/hsn-suggest")
@(limiter.limit("60/minute") if limiter else (lambda f: f))
async def suggest_hsn(
    request: Request,
    q: str = Query(..., min_length=1, max_length=120),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Suggest HSN/SAC codes + default GST rate for a product name."""
    results = hsn_lookup.suggest(q, limit=limit)
    return {"query": q, "results": results}


# ============================================================
# e-invoice (IRN/IRP)
# ============================================================


@router.post("/invoices/{invoice_id}/einvoice", status_code=status.HTTP_200_OK)
async def generate_einvoice_irn(
    invoice_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit the invoice to IRP and persist the returned IRN + QR code."""
    business = await get_my_business_or_404(db, current_user)
    # Row-lock the invoice so two concurrent IRN requests don't double-submit
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.business_id == business.id)
        .options(selectinload(Invoice.lines))
        .with_for_update()
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if invoice is None:
        raise HTTPException(404, "Invoice not found")
    if invoice.irn:
        return {
            "irn": invoice.irn,
            "signed_qr_code": invoice.signed_qr_code,
            "idempotent": True,
        }

    try:
        result = await einvoice_svc.generate_irn(business, invoice)
    except EInvoiceNotApplicable as exc:
        raise HTTPException(400, str(exc)) from exc
    except EInvoiceError as exc:
        raise HTTPException(503, str(exc)) from exc

    invoice.irn = result["irn"]
    invoice.signed_qr_code = result.get("signed_qr_code") or None
    await db.commit()
    return {
        "irn": invoice.irn,
        "signed_qr_code": invoice.signed_qr_code,
        "ack_no": result.get("ack_no"),
        "ack_dt": result.get("ack_dt"),
        "idempotent": False,
    }


@router.post("/invoices/{invoice_id}/share", status_code=status.HTTP_202_ACCEPTED)
async def share_invoice_endpoint(
    invoice_id: UUID,
    body: InvoiceShareRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    business = await get_my_business_or_404(db, current_user)
    stmt = (
        select(Invoice)
        .where(Invoice.id == invoice_id, Invoice.business_id == business.id)
        .options(selectinload(Invoice.lines))
    )
    invoice = (await db.execute(stmt)).scalar_one_or_none()
    if invoice is None:
        raise HTTPException(404, "Invoice not found")

    try:
        url = await _ensure_pdf(invoice, business, db)
    except StorageError as exc:
        raise HTTPException(503, f"Storage not configured: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(503, str(exc)) from exc

    sent = await send_invoice_via_whatsapp(
        business,
        invoice,
        url,
        to_phone=body.to_phone,
        language=current_user.preferred_language or "english",
    )
    return {"sent": sent, "pdf_url": url}
