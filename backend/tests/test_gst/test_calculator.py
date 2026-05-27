"""Tax calculator tests — line-level + invoice-level + composition + words."""
from decimal import Decimal

import pytest

from app.services.gst.calculator import (
    InvoiceTotals,
    LineInput,
    amount_in_words,
    composition_tax_paise,
    compute_invoice_totals,
    compute_line_tax,
    is_interstate,
)


# ============================================================
# is_interstate
# ============================================================


class TestIsInterstate:
    def test_same_state(self):
        assert is_interstate("27", "27") is False

    def test_different_state(self):
        assert is_interstate("27", "07") is True

    def test_uses_first_two_chars(self):
        # GSTIN can be passed in full; we only look at first 2
        assert is_interstate("27AAPFU0939F1ZV", "27AAACH7409R1ZV") is False
        assert is_interstate("27AAPFU0939F1ZV", "07AAACH7409R1ZV") is True

    def test_buyer_unknown_defaults_intra(self):
        assert is_interstate("27", None) is False
        assert is_interstate("27", "") is False

    def test_seller_unknown_defaults_intra(self):
        assert is_interstate(None, "27") is False


# ============================================================
# compute_line_tax — single line
# ============================================================


class TestLineTax:
    def test_zero_rate(self):
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=0)
        out = compute_line_tax(line, interstate=False)
        assert out.taxable_paise == 10000
        assert out.cgst_paise == 0
        assert out.sgst_paise == 0
        assert out.igst_paise == 0
        assert out.total_paise == 10000

    def test_intra_state_18pct(self):
        # ₹100 @ 18% intra → ₹9 CGST + ₹9 SGST = ₹118 total
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=18)
        out = compute_line_tax(line, interstate=False)
        assert out.taxable_paise == 10000
        assert out.cgst_paise == 900   # ₹9
        assert out.sgst_paise == 900
        assert out.igst_paise == 0
        assert out.total_paise == 11800  # ₹118

    def test_inter_state_18pct(self):
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=18)
        out = compute_line_tax(line, interstate=True)
        assert out.taxable_paise == 10000
        assert out.cgst_paise == 0
        assert out.sgst_paise == 0
        assert out.igst_paise == 1800
        assert out.total_paise == 11800

    def test_fractional_quantity(self):
        # 0.5 kg @ ₹200/kg = ₹100, 5% GST → ₹105
        line = LineInput(
            quantity=Decimal("0.5"), unit_price_paise=20000, gst_rate=5
        )
        out = compute_line_tax(line, interstate=False)
        assert out.taxable_paise == 10000
        assert out.cgst_paise == 250
        assert out.sgst_paise == 250
        assert out.total_paise == 10500

    def test_discount(self):
        # 1 × ₹100, 10% discount = ₹90 taxable, 18% = ₹16.20 tax
        line = LineInput(
            quantity=Decimal("1"), unit_price_paise=10000,
            discount_pct=10.0, gst_rate=18,
        )
        out = compute_line_tax(line, interstate=False)
        assert out.taxable_paise == 9000  # ₹90
        # 18% of 9000 = 1620; half = 810 each
        assert out.cgst_paise == 810
        assert out.sgst_paise == 810
        assert out.total_paise == 10620

    def test_negative_quantity_rejected(self):
        with pytest.raises(ValueError):
            compute_line_tax(
                LineInput(quantity=Decimal("-1"), unit_price_paise=100, gst_rate=18),
                interstate=False,
            )

    def test_negative_price_rejected(self):
        with pytest.raises(ValueError):
            compute_line_tax(
                LineInput(quantity=Decimal("1"), unit_price_paise=-1, gst_rate=18),
                interstate=False,
            )

    def test_invalid_discount_rejected(self):
        with pytest.raises(ValueError):
            compute_line_tax(
                LineInput(
                    quantity=Decimal("1"), unit_price_paise=100,
                    discount_pct=101.0, gst_rate=18,
                ),
                interstate=False,
            )

    def test_invalid_rate_rejected(self):
        with pytest.raises(ValueError):
            compute_line_tax(
                LineInput(quantity=Decimal("1"), unit_price_paise=100, gst_rate=10),
                interstate=False,
            )

    def test_odd_rupee_cgst_sgst_sum_equals_total(self):
        """If tax is odd paise, CGST+SGST must still sum exactly to total tax."""
        # ₹101 @ 18% = ₹18.18 tax → 9.09 CGST + 9.09 SGST = 18.18
        # But 909 paise + 909 paise = 1818 ✓
        # Try a tricky case: ₹103.51 (10351 paise) @ 18% = 1863.18 paise
        # half = 931.59 → rounded 932; other half = 1863 - 932 = 931
        line = LineInput(
            quantity=Decimal("1"), unit_price_paise=10351, gst_rate=18
        )
        out = compute_line_tax(line, interstate=False)
        assert out.cgst_paise + out.sgst_paise == 1863  # 18% of 10351 ≈ 1863.18, rounded


# ============================================================
# compute_invoice_totals — multi-line aggregation
# ============================================================


class TestInvoiceTotals:
    def test_empty_lines(self):
        line_taxes, totals = compute_invoice_totals(
            [], seller_state_code="27", buyer_state_code="27"
        )
        assert line_taxes == []
        assert totals.total_paise == 0

    def test_single_line_intra_no_round(self):
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=18)
        _, totals = compute_invoice_totals(
            [line], seller_state_code="27", buyer_state_code="27",
            round_to_rupee=False,
        )
        assert totals.taxable_paise == 10000
        assert totals.cgst_paise == 900
        assert totals.sgst_paise == 900
        assert totals.igst_paise == 0
        assert totals.total_paise == 11800
        assert totals.round_off_paise == 0

    def test_inter_state(self):
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=18)
        _, totals = compute_invoice_totals(
            [line], seller_state_code="27", buyer_state_code="07",
            round_to_rupee=False,
        )
        assert totals.cgst_paise == 0
        assert totals.sgst_paise == 0
        assert totals.igst_paise == 1800

    def test_mixed_rates(self):
        lines = [
            LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=5),   # 105
            LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=18),  # 118
            LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=28),  # 128
        ]
        _, totals = compute_invoice_totals(
            lines, seller_state_code="27", buyer_state_code="27",
            round_to_rupee=False,
        )
        assert totals.taxable_paise == 30000
        # CGST: 250 + 900 + 1400 = 2550; same SGST
        assert totals.cgst_paise == 2550
        assert totals.sgst_paise == 2550
        assert totals.total_paise == 35100

    def test_round_to_rupee(self):
        # 1 × ₹101 @ 18% = ₹119.18 → rounds to ₹119
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10100, gst_rate=18)
        _, totals = compute_invoice_totals(
            [line], seller_state_code="27", buyer_state_code="27",
            round_to_rupee=True,
        )
        assert totals.total_paise == 11900  # rounded to ₹119
        assert totals.round_off_paise == 11900 - (10100 + 909 + 909)

    def test_cess_rates_length_mismatch(self):
        line = LineInput(quantity=Decimal("1"), unit_price_paise=100, gst_rate=18)
        with pytest.raises(ValueError):
            compute_invoice_totals(
                [line], seller_state_code="27", cess_rates=[0.0, 0.0],
            )

    def test_export_no_buyer_state(self):
        # No buyer state → default intra (still 0 tax for export, but we calc honestly)
        line = LineInput(quantity=Decimal("1"), unit_price_paise=10000, gst_rate=0)
        _, totals = compute_invoice_totals(
            [line], seller_state_code="27", buyer_state_code=None,
        )
        assert totals.total_paise == 10000


# ============================================================
# Composition scheme
# ============================================================


class TestComposition:
    @pytest.mark.parametrize("turnover,rate,expected", [
        (100_000_00, 1, 100_000),   # ₹1 lakh × 1% = ₹1,000
        (100_000_00, 5, 500_000),   # ₹1 lakh × 5% = ₹5,000
        (100_000_00, 6, 600_000),   # ₹1 lakh × 6% = ₹6,000
        (50_000_00, 1, 50_000),
        (0, 1, 0),
    ])
    def test_known(self, turnover, rate, expected):
        assert composition_tax_paise(turnover, rate) == expected

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            composition_tax_paise(10000, 2)
        with pytest.raises(ValueError):
            composition_tax_paise(10000, 10)

    def test_negative_turnover(self):
        with pytest.raises(ValueError):
            composition_tax_paise(-1, 1)


# ============================================================
# amount_in_words — Indian English
# ============================================================


class TestAmountInWords:
    @pytest.mark.parametrize("paise,words", [
        (0, "Zero Rupees Only"),
        (100, "One Rupees Only"),
        (10000, "One Hundred Rupees Only"),
        (10050, "One Hundred Rupees and Fifty Paise Only"),
        (123450, "One Thousand Two Hundred Thirty Four Rupees and Fifty Paise Only"),
        (10000000, "One Lakh Rupees Only"),
        (1000000000, "One Crore Rupees Only"),
    ])
    def test_known(self, paise, words):
        assert amount_in_words(paise) == words

    def test_negative(self):
        assert amount_in_words(-10000).startswith("Minus")

    def test_complex(self):
        # ₹1,23,45,678.50 = 1234567850 paise
        out = amount_in_words(1234567850)
        assert "Crore" in out
        assert "Lakh" in out
        assert "Thousand" in out
        assert "Paise" in out
