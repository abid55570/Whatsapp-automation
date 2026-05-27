"""GST identifier validation: GSTIN, PAN, HSN, SAC.

GSTIN structure (15 chars):
    Positions 1-2  : State code (digits, e.g. "27" = Maharashtra)
    Positions 3-12 : PAN (10 chars)
    Position 13    : Entity code (1-9, A-Z) — defaults to "1" for first registration
    Position 14    : Default "Z" (reserved)
    Position 15    : Checksum (digit or letter, computed)

PAN structure (10 chars):
    Positions 1-3  : Letters (random)
    Position 4     : Entity letter (P=person, C=company, F=firm, H=HUF, etc.)
    Position 5     : First letter of holder's surname (for individuals)
    Positions 6-9  : Digits
    Position 10    : Checksum letter

HSN: numeric, 2-8 digits.
SAC: numeric, 6 digits, starts with "99".
"""
from __future__ import annotations

import re

from app.services.gst.state_codes import is_valid_state_code

# ============================================================
# GSTIN
# ============================================================

_GSTIN_RE = re.compile(
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z][Z][0-9A-Z]$"
)
_CHECKSUM_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"  # base-36


def _gstin_checksum(first_14: str) -> str:
    """Compute the 15th-char checksum of a GSTIN from the first 14 chars.

    Algorithm (per GSTN):
      - Map each char to its base-36 value (0..35).
      - Multiply alternate positions by 1 and 2 (starting with 1 at position 1).
      - If product > 36, sum its digits (i.e., digit-sum on base-36).
      - Sum all values, then checksum = (36 - sum mod 36) mod 36.
      - Return base-36 char for that value.
    """
    if len(first_14) != 14:
        raise ValueError("Need 14 chars for GSTIN checksum input")
    total = 0
    for i, ch in enumerate(first_14):
        val = _CHECKSUM_ALPHABET.index(ch)
        factor = 2 if (i % 2 == 1) else 1
        product = val * factor
        if product >= 36:
            product = (product // 36) + (product % 36)
        total += product
    checksum_val = (36 - (total % 36)) % 36
    return _CHECKSUM_ALPHABET[checksum_val]


def is_valid_gstin(gstin: str | None) -> bool:
    """Strict GSTIN validator: format + state code + checksum."""
    if not gstin:
        return False
    g = gstin.strip().upper()
    if not _GSTIN_RE.match(g):
        return False
    if not is_valid_state_code(g[:2]):
        return False
    expected = _gstin_checksum(g[:14])
    return expected == g[14]


def normalize_gstin(gstin: str | None) -> str | None:
    """Uppercase + strip whitespace. Returns None if input falsy."""
    if not gstin:
        return None
    out = gstin.strip().upper().replace(" ", "")
    return out or None


def gstin_state_code(gstin: str | None) -> str | None:
    """Return the 2-digit state code embedded in a GSTIN, or None."""
    g = normalize_gstin(gstin)
    if not g or len(g) < 2:
        return None
    return g[:2]


def gstin_pan(gstin: str | None) -> str | None:
    """Return the 10-char PAN embedded in positions 3-12 of a GSTIN."""
    g = normalize_gstin(gstin)
    if not g or len(g) < 12:
        return None
    return g[2:12]


# ============================================================
# PAN
# ============================================================

_PAN_RE = re.compile(r"^[A-Z]{3}[ABCFGHLJPTE][A-Z][0-9]{4}[A-Z]$")


def is_valid_pan(pan: str | None) -> bool:
    """Format-only PAN validator (no checksum — gov't doesn't publish algo)."""
    if not pan:
        return False
    return bool(_PAN_RE.match(pan.strip().upper()))


def normalize_pan(pan: str | None) -> str | None:
    if not pan:
        return None
    out = pan.strip().upper().replace(" ", "")
    return out or None


# ============================================================
# HSN / SAC codes
# ============================================================

_HSN_RE = re.compile(r"^[0-9]{2,8}$")
_SAC_RE = re.compile(r"^99[0-9]{4}$")


def is_valid_hsn(code: str | None) -> bool:
    """HSN is 2-8 digits. We accept any digit string in that range."""
    if not code:
        return False
    return bool(_HSN_RE.match(code.strip()))


def is_valid_sac(code: str | None) -> bool:
    """SAC is 6 digits starting with '99'."""
    if not code:
        return False
    return bool(_SAC_RE.match(code.strip()))


def is_valid_hsn_or_sac(code: str | None) -> bool:
    return is_valid_hsn(code) or is_valid_sac(code)


# ============================================================
# Tax rate
# ============================================================

VALID_GST_RATES: frozenset[int] = frozenset({0, 5, 12, 18, 28})


def is_valid_gst_rate(rate: int | None) -> bool:
    return rate is not None and rate in VALID_GST_RATES


# ============================================================
# Pincode (Indian)
# ============================================================

_PINCODE_RE = re.compile(r"^[1-9][0-9]{5}$")


def is_valid_pincode(pin: str | None) -> bool:
    if not pin:
        return False
    return bool(_PINCODE_RE.match(pin.strip()))
