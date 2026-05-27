"""Tests for FY-aware invoice numbering."""
from datetime import date
from types import SimpleNamespace

import pytest

from app.services.gst.invoice_number import (
    fiscal_year_for,
    fiscal_year_short,
    format_invoice_number,
    next_invoice_number,
)


class TestFiscalYear:
    @pytest.mark.parametrize("d,expected", [
        (date(2026, 4, 1), "2026-27"),
        (date(2026, 12, 31), "2026-27"),
        (date(2027, 3, 31), "2026-27"),
        (date(2027, 4, 1), "2027-28"),
        (date(2026, 1, 1), "2025-26"),
        (date(2025, 3, 15), "2024-25"),
    ])
    def test_known(self, d, expected):
        assert fiscal_year_for(d) == expected


class TestFiscalYearShort:
    @pytest.mark.parametrize("d,expected", [
        (date(2026, 4, 1), "26"),
        (date(2027, 3, 31), "26"),
        (date(2027, 4, 1), "27"),
        (date(2026, 1, 1), "25"),
    ])
    def test_known(self, d, expected):
        assert fiscal_year_short(d) == expected


class TestFormat:
    def test_default_prefix(self):
        assert format_invoice_number("", "26", 1) == "INV-26-0001"

    def test_custom_prefix(self):
        assert format_invoice_number("INV", "26", 42) == "INV-26-0042"

    def test_prefix_uppercased_and_truncated(self):
        assert format_invoice_number("sharma123", "26", 1) == "SHARMA-26-0001"

    def test_seq_padding(self):
        assert format_invoice_number("INV", "26", 1).endswith("-0001")
        assert format_invoice_number("INV", "26", 9999).endswith("-9999")
        # Beyond 9999 — number still formats but won't pad
        assert format_invoice_number("INV", "26", 10000).endswith("-10000")


class TestNextInvoiceNumber:
    def _biz(self, prefix="INV", seq=0, current_fy=None):
        return SimpleNamespace(
            invoice_prefix=prefix, invoice_seq=seq, current_invoice_fy=current_fy
        )

    def test_first_invoice_of_fy(self):
        biz = self._biz()
        num, seq, fy = next_invoice_number(biz, invoice_date=date(2026, 4, 1))
        assert num == "INV-26-0001"
        assert seq == 1
        assert fy == "2026-27"
        assert biz.invoice_seq == 1
        assert biz.current_invoice_fy == "2026-27"

    def test_increments_within_fy(self):
        biz = self._biz(seq=5, current_fy="2026-27")
        num, seq, _ = next_invoice_number(biz, invoice_date=date(2026, 6, 1))
        assert num == "INV-26-0006"
        assert seq == 6

    def test_fy_rollover_resets(self):
        biz = self._biz(seq=999, current_fy="2025-26")
        num, seq, fy = next_invoice_number(biz, invoice_date=date(2026, 4, 1))
        assert num == "INV-26-0001"  # reset to 1 in new FY
        assert seq == 1
        assert fy == "2026-27"

    def test_custom_prefix(self):
        biz = self._biz(prefix="SHM", seq=0)
        num, _, _ = next_invoice_number(biz, invoice_date=date(2026, 4, 1))
        assert num.startswith("SHM-")
