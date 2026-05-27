"""Tests for invoice share template builder."""
import pytest
from types import SimpleNamespace

from app.services.gst.share import build_invoice_message


def _inv(**kw):
    base = dict(
        invoice_number="INV-26-0042",
        total_paise=11800,
        taxable_paise=10000,
        cgst_paise=900,
        sgst_paise=900,
        igst_paise=0,
        razorpay_payment_link=None,
    )
    base.update(kw)
    return SimpleNamespace(**base)


@pytest.mark.parametrize("lang", [
    "english", "hindi", "hinglish", "bengali", "urdu", "bhojpuri",
])
def test_renders_in_all_languages(lang):
    msg = build_invoice_message(_inv(), "https://r2/test.pdf", language=lang)
    assert "INV-26-0042" in msg
    assert "118.00" in msg
    assert "https://r2/test.pdf" in msg


def test_intra_state_shows_gst_total():
    msg = build_invoice_message(_inv(), "https://x", language="english")
    # 900 + 900 = 1800 paise = ₹18.00
    assert "GST" in msg
    assert "18.00" in msg


def test_inter_state_shows_igst():
    inv = _inv(cgst_paise=0, sgst_paise=0, igst_paise=1800)
    msg = build_invoice_message(inv, "https://x", language="english")
    assert "IGST" in msg


def test_zero_tax_no_tax_line():
    inv = _inv(cgst_paise=0, sgst_paise=0, igst_paise=0, taxable_paise=10000, total_paise=10000)
    msg = build_invoice_message(inv, "https://x", language="english")
    assert "GST" not in msg
    assert "IGST" not in msg


def test_payment_link_included():
    inv = _inv(razorpay_payment_link="https://rzp.io/i/abc")
    msg = build_invoice_message(inv, "https://x", language="english")
    assert "Pay now" in msg
    assert "rzp.io/i/abc" in msg


def test_payment_link_hindi():
    inv = _inv(razorpay_payment_link="https://rzp.io/i/abc")
    msg = build_invoice_message(inv, "https://x", language="hindi")
    assert "अभी पे करें" in msg


def test_unknown_language_falls_back_to_english():
    msg = build_invoice_message(_inv(), "https://x", language="klingon")
    assert "Total" in msg
