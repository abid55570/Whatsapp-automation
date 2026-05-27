"""Tax calculator — CGST/SGST/IGST split per invoice line.

All money is in paise (integer). All percentages are integer GST rates
(0/5/12/18/28). Rounding is "banker's" via Python round-half-even, applied
at the LINE level then totals are summed exactly. This matches what the
GST portal expects: per-line tax → sum, not (sum of bases) × rate.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import ROUND_HALF_EVEN, Decimal


# Quantize to whole paise (1 paise == 0.01 INR)
_PAISE = Decimal("1")


def _paise(value: Decimal) -> int:
    """Round Decimal to nearest paise using banker's rounding → int paise."""
    return int(value.quantize(_PAISE, rounding=ROUND_HALF_EVEN))


# ============================================================
# Public data shapes
# ============================================================


@dataclass(frozen=True)
class LineInput:
    """Owner-provided line item before tax."""

    quantity: Decimal       # Decimal so fractional kg/L works
    unit_price_paise: int   # per-unit price
    discount_pct: float = 0.0
    gst_rate: int = 0       # 0/5/12/18/28


@dataclass(frozen=True)
class LineTax:
    """Computed tax breakdown for one invoice line."""

    taxable_paise: int      # (qty × unit_price) − discount
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    total_paise: int        # taxable + all taxes

    def gross(self) -> int:
        return self.total_paise


@dataclass(frozen=True)
class InvoiceTotals:
    """Aggregated invoice totals after summing every LineTax."""

    subtotal_paise: int     # before discount, before tax (sum of qty × rate)
    discount_paise: int     # total absolute discount
    taxable_paise: int      # subtotal − discount
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    round_off_paise: int    # rounding adjustment to whole rupee
    total_paise: int        # taxable + all taxes + round_off


# ============================================================
# Per-line calc
# ============================================================


def compute_line_tax(
    line: LineInput,
    *,
    interstate: bool,
    cess_rate: float = 0.0,
) -> LineTax:
    """Compute tax for a single line.

    Args:
        line:         the LineInput
        interstate:  True → IGST (single combined rate)
                     False → CGST + SGST (split half/half)
        cess_rate:   optional cess percent (rare, only for sin goods/luxury)

    Returns: LineTax with all amounts in paise.
    """
    if line.quantity < 0:
        raise ValueError("quantity must be >= 0")
    if line.unit_price_paise < 0:
        raise ValueError("unit_price_paise must be >= 0")
    if not (0 <= line.discount_pct <= 100):
        raise ValueError("discount_pct must be in [0, 100]")
    if line.gst_rate not in (0, 5, 12, 18, 28):
        raise ValueError(f"gst_rate {line.gst_rate} not in (0,5,12,18,28)")

    gross_no_disc = Decimal(str(line.quantity)) * Decimal(line.unit_price_paise)
    discount = gross_no_disc * Decimal(str(line.discount_pct)) / Decimal(100)
    taxable_d = gross_no_disc - discount
    taxable = _paise(taxable_d)

    rate = Decimal(line.gst_rate)
    tax_d = taxable_d * rate / Decimal(100)

    if interstate:
        igst = _paise(tax_d)
        cgst = sgst = 0
    else:
        # Round total tax first, then half it; second half = total - first half
        # so the sum is guaranteed to equal the rounded total tax exactly.
        total_tax = _paise(tax_d)
        cgst = _paise(tax_d / Decimal(2))
        sgst = total_tax - cgst
        igst = 0

    cess = _paise(taxable_d * Decimal(str(cess_rate)) / Decimal(100)) if cess_rate else 0

    total = taxable + cgst + sgst + igst + cess
    return LineTax(
        taxable_paise=taxable,
        cgst_paise=cgst,
        sgst_paise=sgst,
        igst_paise=igst,
        cess_paise=cess,
        total_paise=total,
    )


# ============================================================
# Invoice-level rollup
# ============================================================


def is_interstate(
    seller_state_code: str | None,
    buyer_state_code: str | None,
) -> bool:
    """Determine if a transaction crosses state lines.

    Default to intra-state when buyer state is unknown — safer for B2C.
    Export (no buyer state code at all) is handled by caller separately.
    """
    if not seller_state_code:
        # Seller has no GSTIN — treat as intra-state, no tax actually applies
        return False
    if not buyer_state_code:
        return False
    return seller_state_code.strip()[:2] != buyer_state_code.strip()[:2]


def compute_invoice_totals(
    lines: list[LineInput],
    *,
    seller_state_code: str | None,
    buyer_state_code: str | None = None,
    cess_rates: list[float] | None = None,
    round_to_rupee: bool = True,
) -> tuple[list[LineTax], InvoiceTotals]:
    """Compute every line's tax + the aggregate totals.

    `cess_rates` is parallel to `lines`; pass None for no cess on any line.
    `round_to_rupee` rounds final total to nearest rupee (standard for India).
    """
    if not lines:
        empty = InvoiceTotals(0, 0, 0, 0, 0, 0, 0, 0, 0)
        return [], empty

    inter = is_interstate(seller_state_code, buyer_state_code)
    cess_rates = cess_rates or [0.0] * len(lines)
    if len(cess_rates) != len(lines):
        raise ValueError("cess_rates length must match lines length")

    line_taxes: list[LineTax] = []
    subtotal = Decimal(0)
    discount = Decimal(0)
    for line, cess in zip(lines, cess_rates, strict=True):
        gross = Decimal(str(line.quantity)) * Decimal(line.unit_price_paise)
        subtotal += gross
        discount += gross * Decimal(str(line.discount_pct)) / Decimal(100)
        line_taxes.append(compute_line_tax(line, interstate=inter, cess_rate=cess))

    taxable = sum(lt.taxable_paise for lt in line_taxes)
    cgst = sum(lt.cgst_paise for lt in line_taxes)
    sgst = sum(lt.sgst_paise for lt in line_taxes)
    igst = sum(lt.igst_paise for lt in line_taxes)
    cess_total = sum(lt.cess_paise for lt in line_taxes)
    pre_round_total = taxable + cgst + sgst + igst + cess_total

    round_off = 0
    final_total = pre_round_total
    if round_to_rupee:
        # Round to nearest whole rupee (100 paise). round_off can be negative.
        final_total = int(round(pre_round_total / 100)) * 100
        round_off = final_total - pre_round_total

    totals = InvoiceTotals(
        subtotal_paise=_paise(subtotal),
        discount_paise=_paise(discount),
        taxable_paise=taxable,
        cgst_paise=cgst,
        sgst_paise=sgst,
        igst_paise=igst,
        cess_paise=cess_total,
        round_off_paise=round_off,
        total_paise=final_total,
    )
    return line_taxes, totals


# ============================================================
# Composition scheme — flat percent on turnover, no buyer tax
# ============================================================


def composition_tax_paise(turnover_paise: int, rate_pct: int) -> int:
    """Composition dealers pay flat % of turnover to govt. Buyer pays nothing extra.

    Rates: 1% (traders), 5% (restaurants), 6% (services).
    """
    if turnover_paise < 0:
        raise ValueError("turnover_paise must be >= 0")
    if rate_pct not in (1, 5, 6):
        raise ValueError(f"composition rate {rate_pct} not in (1,5,6)")
    return _paise(Decimal(turnover_paise) * Decimal(rate_pct) / Decimal(100))


# ============================================================
# Amount in words (for invoice PDF) — Indian English numbering
# ============================================================


_ONES = [
    "Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
    "Sixteen", "Seventeen", "Eighteen", "Nineteen",
]
_TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
    "Eighty", "Ninety",
]


def _below_hundred(n: int) -> str:
    if n < 20:
        return _ONES[n]
    tens, ones = divmod(n, 10)
    return _TENS[tens] + ("" if ones == 0 else " " + _ONES[ones])


def _below_thousand(n: int) -> str:
    if n < 100:
        return _below_hundred(n)
    hundreds, rest = divmod(n, 100)
    out = _ONES[hundreds] + " Hundred"
    if rest:
        out += " " + _below_hundred(rest)
    return out


def amount_in_words(paise: int) -> str:
    """Indian-English number-to-words. e.g. 50050 → 'Five Hundred Rupees and Fifty Paise Only'.

    Uses Indian numbering: Crore (10M), Lakh (100K), Thousand.
    """
    if paise < 0:
        return "Minus " + amount_in_words(-paise)
    rupees, paise_part = divmod(paise, 100)

    parts: list[str] = []
    crore, rest = divmod(rupees, 10_000_000)
    if crore:
        parts.append(_below_hundred(crore) + " Crore")
        rupees = rest
    lakh, rest = divmod(rupees, 100_000)
    if lakh:
        parts.append(_below_hundred(lakh) + " Lakh")
        rupees = rest
    thousand, rest = divmod(rupees, 1_000)
    if thousand:
        parts.append(_below_thousand(thousand) + " Thousand")
        rupees = rest
    if rupees:
        parts.append(_below_thousand(rupees))

    if not parts:
        parts = ["Zero"]

    out = " ".join(parts) + " Rupees"
    if paise_part:
        out += " and " + _below_hundred(paise_part) + " Paise"
    return out + " Only"
