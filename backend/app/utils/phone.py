"""Phone number normalization.

We standardize on E.164 format (+<country><number>) everywhere internally:
- User input may be: "9876543210", "+91 98765 43210", "919876543210", "0091..."
- Meta webhook delivers: "919876543210" (no + prefix)
- Display formats vary

`normalize_phone()` is the single source of truth.
"""
import re

_NON_DIGIT_OR_PLUS = re.compile(r"[^\d+]")
_INDIAN_MOBILE_PREFIX = ("6", "7", "8", "9")


def normalize_phone(phone: str | None) -> str:
    """Return phone in E.164 format with leading '+'.

    Best-effort: handles Indian mobile numbers without a country code.
    For other countries, the caller must include the country code.
    """
    if not phone:
        return ""

    cleaned = _NON_DIGIT_OR_PLUS.sub("", phone.strip())
    if not cleaned:
        return ""

    # Already has +
    if cleaned.startswith("+"):
        return cleaned

    # 00-prefix international (e.g., "0091...")
    if cleaned.startswith("00") and len(cleaned) > 4:
        return "+" + cleaned[2:]

    # Bare 10-digit Indian mobile → prepend +91
    if len(cleaned) == 10 and cleaned[0] in _INDIAN_MOBILE_PREFIX:
        return "+91" + cleaned

    # 12-digit starting with 91 (Indian, no +)
    if len(cleaned) == 12 and cleaned.startswith("91"):
        return "+" + cleaned

    # 11-digit starting with 0 (e.g., "09876543210") — strip leading 0, add +91
    if len(cleaned) == 11 and cleaned.startswith("0") and cleaned[1] in _INDIAN_MOBILE_PREFIX:
        return "+91" + cleaned[1:]

    # Generic fallback: prepend +
    return "+" + cleaned


def is_valid_phone(phone: str) -> bool:
    """Quick sanity check on an E.164 phone (8-15 digits)."""
    if not phone or not phone.startswith("+"):
        return False
    digits = phone[1:]
    return digits.isdigit() and 8 <= len(digits) <= 15
