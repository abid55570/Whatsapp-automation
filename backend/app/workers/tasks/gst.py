"""GST-related Celery tasks.

Currently:
  - `gst.send_monthly_ca_email` — daily beat, fires on day 1 of each month for
    every business that has tax_pack_enabled + a configured CA email. Bundles
    last-month's GSTR-1 JSON + GSTR-3B summary xlsx + sales register and emails
    them to the owner's CA.
"""
import asyncio
import logging
import smtplib
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models import Business, Invoice, PurchaseInvoice
from app.workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="gst.send_monthly_ca_email",
    bind=True,
    acks_late=True,
    autoretry_for=(Exception,),
    retry_backoff=120,
    max_retries=3,
)
def send_monthly_ca_email_task(self) -> dict[str, Any]:
    """Fan-out task. Run on day 1 of each month — sends last month's pack to
    each Tax-Pack-enabled business owner's CA email.
    """
    return asyncio.run(_run_send_monthly())


async def _run_send_monthly() -> dict[str, Any]:
    """Lookup eligible businesses, build their bundles, send via SMTP.

    Returns a dict with `sent` count + `errors` list. Failures don't halt
    the batch — each business is tried independently.

    Idempotency: only sends on day-1 of the month. The daily beat schedule
    is a safety net for missed firings; it short-circuits on other days.
    """
    today = datetime.now(timezone.utc).date()
    if today.day != 1:
        return {"sent": 0, "skipped": "only runs on day 1 of month"}

    # Last completed month
    last_month_end = today.replace(day=1) - timedelta(days=1)
    month_start = last_month_end.replace(day=1)
    month_end = last_month_end
    period_label = month_start.strftime("%B %Y")

    sent = 0
    errors: list[dict] = []

    async with AsyncSessionLocal() as db:
        # All businesses with Tax Pack enabled
        biz_rows = (
            await db.execute(
                select(Business).where(Business.tax_pack_enabled.is_(True))
            )
        ).scalars().all()

        for business in biz_rows:
            # Owner email — fall back to skipping silently if missing
            owner = business.owner if hasattr(business, "owner") else None
            owner_email = getattr(owner, "email", None) if owner else None
            if not owner_email:
                logger.info("Skipping %s — no owner email", business.id)
                continue

            try:
                attachments = await _build_attachments(
                    db, business, month_start, month_end
                )
                _send_email(
                    to_email=owner_email,
                    business_name=business.name,
                    period_label=period_label,
                    attachments=attachments,
                )
                sent += 1
            except Exception as exc:
                logger.exception(
                    "CA email failed for business=%s: %s", business.id, exc
                )
                errors.append({"business_id": str(business.id), "error": str(exc)})

    logger.info("Monthly CA email: sent=%d errors=%d", sent, len(errors))
    return {"sent": sent, "errors": errors, "period": period_label}


async def _build_attachments(
    db, business: Business, period_from: date, period_to: date
) -> list[tuple[str, str, bytes]]:
    """Return [(filename, mime_type, bytes), ...] for the email."""
    from app.services.gst.exporters import (
        gstr1 as gstr1_exporter,
        gstr3b_summary as gstr3b_exporter,
        sales_register as sr_exporter,
    )

    inv_stmt = (
        select(Invoice)
        .where(
            Invoice.business_id == business.id,
            Invoice.invoice_date >= period_from,
            Invoice.invoice_date <= period_to,
        )
        .options(selectinload(Invoice.lines))
    )
    invoices = (await db.execute(inv_stmt)).scalars().all()

    purch_stmt = select(PurchaseInvoice).where(
        PurchaseInvoice.business_id == business.id,
        PurchaseInvoice.bill_date >= period_from,
        PurchaseInvoice.bill_date <= period_to,
    )
    purchases = (await db.execute(purch_stmt)).scalars().all()

    period_tag = period_from.strftime("%Y-%m")
    xlsx_mime = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    out: list[tuple[str, str, bytes]] = []

    # Sales register
    sales_xlsx = sr_exporter.build_sales_register(
        business, invoices, period_from, period_to
    )
    out.append((f"sales-register-{period_tag}.xlsx", xlsx_mime, sales_xlsx))

    # GSTR-3B summary
    gstr3b_xlsx = gstr3b_exporter.build_gstr3b_summary(
        business, invoices, purchases, period_from
    )
    out.append((f"gstr3b-summary-{period_tag}.xlsx", xlsx_mime, gstr3b_xlsx))

    # GSTR-1 JSON (only if GSTIN set)
    if business.gstin:
        import json
        gstr1_payload = gstr1_exporter.build_gstr1_json(business, invoices, period_from)
        out.append((
            f"gstr1-{period_tag}.json",
            "application/json",
            json.dumps(gstr1_payload, ensure_ascii=False, indent=2).encode("utf-8"),
        ))

    return out


def _send_email(
    *,
    to_email: str,
    business_name: str,
    period_label: str,
    attachments: list[tuple[str, str, bytes]],
) -> None:
    """Send the bundle via SMTP (MailHog in dev, real SMTP in prod).

    Uses MailHog defaults (`smtp:1025`) if no SMTP_* env vars set.
    """
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM or "noreply@example.com"
    msg["To"] = to_email
    msg["Subject"] = f"GST filing pack — {business_name} ({period_label})"
    msg.set_content(
        f"Hi,\n\n"
        f"Attached are the auto-generated GST filing documents for "
        f"{business_name} for {period_label}:\n\n"
        + "\n".join(f"  · {fn}" for fn, _, _ in attachments)
        + "\n\nPlease review each file and verify totals before filing on "
        "gst.gov.in.\n\n"
        "— WhatsApp Auto\n"
    )
    for filename, mime, data in attachments:
        maintype, subtype = mime.split("/", 1)
        msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=filename)

    # Prefer explicit SMTP_HOST/SMTP_PORT envs in prod; fall back to MailHog (dev)
    smtp_host = getattr(settings, "SMTP_HOST", "") or "mailhog"
    smtp_port = int(getattr(settings, "SMTP_PORT", 0) or 1025)
    smtp_user = getattr(settings, "SMTP_USER", "")
    smtp_password = getattr(settings, "SMTP_PASSWORD", "")
    smtp_tls = bool(getattr(settings, "SMTP_USE_TLS", False))

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as s:
        if smtp_tls:
            s.starttls()
        if smtp_user and smtp_password:
            s.login(smtp_user, smtp_password)
        s.send_message(msg)
    logger.info("Sent CA email to %s for %s", to_email, business_name)
