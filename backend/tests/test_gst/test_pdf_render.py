"""Tests for the HTML rendering layer (no WeasyPrint required)."""
from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.models.enums import GstScheme
from app.services.gst.pdf_generator import render_invoice_html


def _line(n=1, **kw):
    base = dict(
        line_number=n,
        description=f"Item {n}",
        hsn_code="1001",
        quantity=Decimal("1"),
        unit="pc",
        rate_paise=10000,
        discount_pct=Decimal("0"),
        gst_rate=18,
        taxable_paise=10000,
        cgst_paise=900,
        sgst_paise=900,
        igst_paise=0,
        cess_paise=0,
        total_paise=11800,
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _invoice(**kw):
    base = dict(
        invoice_number="INV-26-0001",
        invoice_date=date(2026, 5, 20),
        fiscal_year="2026-27",
        cx_name="ACME Pvt Ltd",
        cx_phone="+919876543210",
        cx_gstin="27AAPFU0939F1ZV",
        cx_address="123 Main St",
        cx_state_code="27",
        subtotal_paise=10000,
        discount_paise=0,
        taxable_paise=10000,
        cgst_paise=900,
        sgst_paise=900,
        igst_paise=0,
        cess_paise=0,
        round_off_paise=0,
        total_paise=11800,
        place_of_supply="Maharashtra",
        reverse_charge=False,
        notes=None,
        irn=None,
        signed_qr_code=None,
        created_at=datetime(2026, 5, 20, 10, 30, tzinfo=timezone.utc),
        lines=[_line(1)],
    )
    base.update(kw)
    return SimpleNamespace(**base)


def _business(scheme=GstScheme.REGULAR, **kw):
    base = dict(
        name="Sharma Kirana",
        legal_name="Sharma Kirana Stores LLP",
        gstin="27AAPFU0939F1ZV",
        gst_state_code="27",
        gst_scheme=scheme,
        pan="AAPFU0939F",
        business_address_line1="Shop 5, Main Road",
        business_address_line2="Near Bus Stand",
        business_city="Pune",
        business_state="Maharashtra",
        business_pincode="411001",
    )
    base.update(kw)
    return SimpleNamespace(**base)


class TestRenderRegular:
    def test_basic_render(self):
        html = render_invoice_html(_invoice(), _business())
        assert "Tax Invoice" in html
        assert "INV-26-0001" in html
        assert "Sharma Kirana" in html
        assert "27AAPFU0939F1ZV" in html
        assert "ACME Pvt Ltd" in html

    def test_includes_intra_state_split(self):
        html = render_invoice_html(_invoice(), _business())
        assert "CGST" in html
        assert "SGST" in html
        # IGST column should not appear in intra-state invoice
        assert ">IGST<" not in html

    def test_amount_in_words(self):
        html = render_invoice_html(_invoice(total_paise=11800), _business())
        assert "Rupees" in html
        assert "Only" in html

    def test_inter_state_uses_igst(self):
        inv = _invoice(
            cx_state_code="07",
            place_of_supply="Delhi",
            cgst_paise=0,
            sgst_paise=0,
            igst_paise=1800,
            lines=[_line(1, cgst_paise=0, sgst_paise=0, igst_paise=1800)],
        )
        html = render_invoice_html(inv, _business())
        assert "IGST" in html

    def test_terms_includes_jurisdiction(self):
        html = render_invoice_html(_invoice(), _business())
        assert "Pune" in html
        assert "jurisdiction" in html.lower()

    def test_computer_generated_footer(self):
        html = render_invoice_html(_invoice(), _business())
        assert "computer-generated" in html.lower()


class TestRenderComposition:
    def test_uses_bill_of_supply_template(self):
        html = render_invoice_html(_invoice(), _business(scheme=GstScheme.COMPOSITION))
        assert "Bill of Supply" in html
        assert "Composition" in html
        # Composition: no CGST/SGST/IGST columns
        assert ">CGST<" not in html
        assert ">SGST<" not in html
        assert ">IGST<" not in html


class TestRenderEdgeCases:
    def test_missing_buyer_address(self):
        inv = _invoice(cx_address=None, cx_state_code=None)
        html = render_invoice_html(inv, _business())
        # Should render without throwing
        assert "INV-26-0001" in html

    def test_b2c_no_gstin(self):
        inv = _invoice(cx_gstin=None)
        html = render_invoice_html(inv, _business())
        # GSTIN row in buyer block should not crash; just absent
        assert "Cash Customer" not in html  # we DO have cx_name="ACME..."
        # Try a true cash-customer invoice
        cash = _invoice(cx_name=None, cx_gstin=None)
        html2 = render_invoice_html(cash, _business())
        assert "Cash Customer" in html2

    def test_with_irn(self):
        inv = _invoice(irn="abc123def456" * 5)
        html = render_invoice_html(inv, _business())
        assert "IRN" in html
        assert inv.irn in html

    def test_notes_included(self):
        inv = _invoice(notes="Thank you for your business!")
        html = render_invoice_html(inv, _business())
        assert "Thank you for your business!" in html

    def test_html_escaped(self):
        inv = _invoice(cx_name="<script>alert(1)</script>")
        html = render_invoice_html(inv, _business())
        assert "<script>" not in html
        assert "&lt;script&gt;" in html
