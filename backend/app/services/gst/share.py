"""Send an invoice link to the customer via WhatsApp."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.services.whatsapp.client import WhatsAppClient, WhatsAppClientError

if TYPE_CHECKING:
    from app.models import Business, Invoice

logger = logging.getLogger(__name__)


# Per-language invoice share template. Keep it short — WA renders <text> only.
_TEMPLATES: dict[str, str] = {
    "english": (
        "🧾 Invoice {number} — Total ₹{total}\n\n"
        "Subtotal: ₹{subtotal}\n"
        "{tax_line}"
        "📄 Download: {url}\n"
        "{payment_line}"
    ),
    "hindi": (
        "🧾 इनवॉइस {number} — कुल ₹{total}\n\n"
        "उप-योग: ₹{subtotal}\n"
        "{tax_line}"
        "📄 डाउनलोड करें: {url}\n"
        "{payment_line}"
    ),
    "hinglish": (
        "🧾 Invoice {number} — Total ₹{total}\n\n"
        "Subtotal: ₹{subtotal}\n"
        "{tax_line}"
        "📄 Download karein: {url}\n"
        "{payment_line}"
    ),
    "bengali": (
        "🧾 ইনভয়েস {number} — মোট ₹{total}\n\n"
        "সাবটোটাল: ₹{subtotal}\n"
        "{tax_line}"
        "📄 ডাউনলোড: {url}\n"
        "{payment_line}"
    ),
    "urdu": (
        "🧾 Invoice {number} — Total ₹{total}\n\n"
        "Subtotal: ₹{subtotal}\n"
        "{tax_line}"
        "📄 Download: {url}\n"
        "{payment_line}"
    ),
    "bhojpuri": (
        "🧾 Invoice {number} — Total ₹{total}\n\n"
        "Subtotal: ₹{subtotal}\n"
        "{tax_line}"
        "📄 Download kari: {url}\n"
        "{payment_line}"
    ),
}


def build_invoice_message(
    invoice: "Invoice",
    pdf_url: str,
    *,
    language: str = "english",
) -> str:
    """Compose the WhatsApp message body."""
    template = _TEMPLATES.get(language) or _TEMPLATES["english"]

    total_inr = f"{invoice.total_paise / 100:,.2f}"
    subtotal_inr = f"{invoice.taxable_paise / 100:,.2f}"

    if invoice.igst_paise > 0:
        tax_line = f"IGST: ₹{invoice.igst_paise / 100:,.2f}\n"
    elif invoice.cgst_paise > 0 or invoice.sgst_paise > 0:
        tax_total = invoice.cgst_paise + invoice.sgst_paise
        tax_line = f"GST: ₹{tax_total / 100:,.2f}\n"
    else:
        tax_line = ""

    payment_line = ""
    if invoice.razorpay_payment_link:
        if language == "hindi":
            payment_line = f"💳 अभी पे करें: {invoice.razorpay_payment_link}\n"
        elif language in ("hinglish", "urdu", "bhojpuri"):
            payment_line = f"💳 Abhi pay karein: {invoice.razorpay_payment_link}\n"
        else:
            payment_line = f"💳 Pay now: {invoice.razorpay_payment_link}\n"

    return template.format(
        number=invoice.invoice_number,
        total=total_inr,
        subtotal=subtotal_inr,
        tax_line=tax_line,
        url=pdf_url,
        payment_line=payment_line,
    )


async def send_invoice_via_whatsapp(
    business: "Business",
    invoice: "Invoice",
    pdf_url: str,
    *,
    to_phone: str | None = None,
    language: str = "english",
) -> bool:
    """Send invoice link to the customer's WhatsApp.

    Returns True on success, False if business isn't connected or send failed.
    """
    if not (business.whatsapp_phone_number_id and business.whatsapp_access_token):
        logger.info("Skipping invoice share — business %s has no WA connected", business.id)
        return False

    phone = (to_phone or invoice.cx_phone or "").lstrip("+").replace(" ", "")
    if not phone:
        logger.warning("No phone to send invoice %s to", invoice.invoice_number)
        return False

    body = build_invoice_message(invoice, pdf_url, language=language)
    client = WhatsAppClient(
        phone_number_id=business.whatsapp_phone_number_id,
        access_token=business.whatsapp_access_token,
    )
    try:
        await client.send_text(to=phone, body=body)
    except WhatsAppClientError as exc:
        logger.warning("Failed to share invoice %s: %s", invoice.invoice_number, exc)
        return False

    logger.info("Shared invoice %s to %s", invoice.invoice_number, phone)
    return True
