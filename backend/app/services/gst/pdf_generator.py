"""Invoice PDF generation via Jinja2 → WeasyPrint.

Two-stage design:
  1. `render_invoice_html(invoice)` — pure Jinja2 templating, no native deps.
     Easy to unit-test: assert on the produced HTML string.
  2. `generate_invoice_pdf(invoice)` — invokes WeasyPrint to turn the HTML into
     a PDF bytestring. Requires Cairo/Pango/GObject system libs (in Docker).

For composition-scheme businesses we use a different template
(`bill_of_supply.html`) since by law they cannot collect tax on the invoice.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.services.gst.calculator import amount_in_words
from app.services.gst.state_codes import state_name

if TYPE_CHECKING:
    from app.models import Business, Invoice

logger = logging.getLogger(__name__)

_TEMPLATE_DIR = Path(__file__).parent / "templates"
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATE_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
    trim_blocks=True,
    lstrip_blocks=True,
)
_env.filters["paise_to_rupees"] = lambda paise: f"₹{paise / 100:,.2f}"
_env.filters["paise_to_inr"] = lambda paise: f"{paise / 100:,.2f}"
_env.filters["amount_in_words"] = amount_in_words


def _build_context(invoice: "Invoice", business: "Business") -> dict[str, Any]:
    """Marshal the ORM Invoice into a flat dict for the template.

    Doing it here (not in template) keeps the template logic-free.
    """
    interstate = (invoice.cgst_paise == 0 and invoice.sgst_paise == 0 and invoice.igst_paise > 0)
    composition = getattr(business, "gst_scheme", None)
    composition_flag = (
        composition.value if hasattr(composition, "value") else str(composition or "")
    ) == "composition"

    seller_state = state_name(business.gst_state_code or "") or business.business_state or ""
    buyer_state = state_name(invoice.cx_state_code or "") or ""

    return {
        "doc_title": "Bill of Supply" if composition_flag else "Tax Invoice",
        "is_bill_of_supply": composition_flag,
        "interstate": interstate,
        # Seller
        "seller": {
            "name": business.legal_name or business.name,
            "gstin": business.gstin or "",
            "pan": business.pan or "",
            "address_line1": business.business_address_line1 or "",
            "address_line2": business.business_address_line2 or "",
            "city": business.business_city or "",
            "state": seller_state,
            "pincode": business.business_pincode or "",
        },
        # Buyer
        "buyer": {
            "name": invoice.cx_name or "",
            "gstin": invoice.cx_gstin or "",
            "phone": invoice.cx_phone or "",
            "address": invoice.cx_address or "",
            "state": buyer_state,
            "state_code": invoice.cx_state_code or "",
        },
        # Invoice meta
        "invoice": {
            "number": invoice.invoice_number,
            "date": invoice.invoice_date.strftime("%d %b %Y") if invoice.invoice_date else "",
            "fiscal_year": invoice.fiscal_year,
            "place_of_supply": invoice.place_of_supply or buyer_state or seller_state,
            "reverse_charge": invoice.reverse_charge,
            "irn": invoice.irn or "",
            "signed_qr_code": invoice.signed_qr_code or "",
            "notes": invoice.notes or "",
        },
        # Lines
        "lines": [
            {
                "n": line.line_number,
                "description": line.description,
                "hsn": line.hsn_code or "",
                "quantity": str(line.quantity),
                "unit": line.unit,
                "rate_paise": line.rate_paise,
                "discount_pct": float(line.discount_pct),
                "gst_rate": line.gst_rate,
                "taxable_paise": line.taxable_paise,
                "cgst_paise": line.cgst_paise,
                "sgst_paise": line.sgst_paise,
                "igst_paise": line.igst_paise,
                "total_paise": line.total_paise,
            }
            for line in invoice.lines
        ],
        # Totals
        "totals": {
            "subtotal_paise": invoice.subtotal_paise,
            "discount_paise": invoice.discount_paise,
            "taxable_paise": invoice.taxable_paise,
            "cgst_paise": invoice.cgst_paise,
            "sgst_paise": invoice.sgst_paise,
            "igst_paise": invoice.igst_paise,
            "cess_paise": invoice.cess_paise,
            "round_off_paise": invoice.round_off_paise,
            "total_paise": invoice.total_paise,
            "total_in_words": amount_in_words(invoice.total_paise),
        },
        # Generated-at footer
        "generated_at": invoice.created_at.strftime("%d %b %Y %H:%M") if invoice.created_at else "",
    }


def render_invoice_html(invoice: "Invoice", business: "Business") -> str:
    """Render the invoice template to an HTML string. No native deps."""
    template_name = "bill_of_supply.html" if (
        getattr(business, "gst_scheme", None)
        and (getattr(business.gst_scheme, "value", str(business.gst_scheme)) == "composition")
    ) else "invoice.html"
    template = _env.get_template(template_name)
    return template.render(**_build_context(invoice, business))


def generate_invoice_pdf(invoice: "Invoice", business: "Business") -> bytes:
    """Render to HTML then convert to PDF bytes via WeasyPrint."""
    html = render_invoice_html(invoice, business)
    try:
        # Lazy import so test suites without weasyprint can still load this module
        from weasyprint import HTML  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "WeasyPrint not installed. `pip install weasyprint` (+ system Cairo/Pango on host) "
            "or run via docker compose where the image has it baked in."
        ) from exc

    pdf_bytes = HTML(string=html, base_url=str(_TEMPLATE_DIR)).write_pdf()
    return pdf_bytes
