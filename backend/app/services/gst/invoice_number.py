"""Invoice number generator — FY-aware sequential.

GST rule: invoice numbers must be:
  - Unique within a fiscal year (April 1 – March 31 in India)
  - Sequential — gaps allowed only for cancelled invoices (we leave them, never reuse)
  - Format: any alphanumeric + dash + slash, max 16 chars
  - Reset every fiscal year is allowed (and conventional)

We use:  PREFIX-YY-NNNN   e.g. "INV-26-0042" for FY 2026-27.
Per-business prefix + per-business sequence stored on Business model.
"""
from __future__ import annotations

from datetime import date, datetime, timezone


def fiscal_year_for(d: date) -> str:
    """Return Indian FY label for a date.

    April 1 starts the FY. e.g. 2026-05-20 → "2026-27".
    """
    if d.month >= 4:
        start = d.year
    else:
        start = d.year - 1
    end_short = (start + 1) % 100
    return f"{start}-{end_short:02d}"


def fiscal_year_short(d: date) -> str:
    """Two-digit FY suffix for invoice number. e.g. 2026-05-20 → '26' (FY start year)."""
    if d.month >= 4:
        return f"{d.year % 100:02d}"
    return f"{(d.year - 1) % 100:02d}"


def format_invoice_number(prefix: str, fy_short: str, seq: int) -> str:
    """Build the invoice number string.

    prefix: business.invoice_prefix (default "INV")
    fy_short: 2-digit FY start year ("26")
    seq: per-(business, FY) sequence number
    """
    if not prefix:
        prefix = "INV"
    prefix = prefix.strip().upper()[:6]  # cap prefix length
    return f"{prefix}-{fy_short}-{seq:04d}"


def next_invoice_number(
    business,
    *,
    invoice_date: date | None = None,
) -> tuple[str, int, str]:
    """Compute the next invoice number for a business on a given date.

    Mutates business.invoice_seq + (if FY rolled FORWARD only) resets it.
    Back-dating an invoice into an older FY does NOT reset the live counter —
    that would corrupt the current-FY sequence. For back-dated invoices we
    raise; caller must use a separate explicit path if they ever need this.

    Returns: (full_invoice_number, new_seq, fiscal_year_label)
    """
    invoice_date = invoice_date or datetime.now(timezone.utc).date()
    new_fy = fiscal_year_for(invoice_date)
    current_fy = getattr(business, "current_invoice_fy", None)

    if current_fy is None or new_fy > current_fy:
        # First-ever invoice OR FY rolled forward — reset sequence
        business.invoice_seq = 1
        business.current_invoice_fy = new_fy
    elif new_fy < current_fy:
        # Back-dated into a previous FY — refuse rather than corrupt counter
        raise ValueError(
            f"Cannot create invoice in past FY {new_fy} when current FY is "
            f"{current_fy}. Use today's date or contact support."
        )
    else:
        # Same FY — just increment
        business.invoice_seq = (business.invoice_seq or 0) + 1

    fy_short = fiscal_year_short(invoice_date)
    number = format_invoice_number(
        business.invoice_prefix or "INV", fy_short, business.invoice_seq
    )
    return number, business.invoice_seq, new_fy
