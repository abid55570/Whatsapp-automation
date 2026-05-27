"""Parse sheet rows into structured dicts based on sheet type.

Each parser is tolerant of:
  - Column order variations (uses fuzzy header matching)
  - Missing optional columns
  - Empty rows
"""
import re
from typing import Any


def _find_col(headers: list[str], *aliases: str) -> int | None:
    """Find first column whose header contains any of the alias strings."""
    for alias in aliases:
        alias_lower = alias.lower()
        for i, h in enumerate(headers):
            if alias_lower in h.lower():
                return i
    return None


def _safe_get(row: list, idx: int | None) -> str:
    """Get cell value safely, return empty string if out of bounds."""
    if idx is None or idx >= len(row):
        return ""
    return str(row[idx]).strip() if row[idx] is not None else ""


def _parse_money_to_paise(value: str) -> int:
    """Parse '₹399', '399.00', '1,250', 'Rs. 999' into paise (399 -> 39900)."""
    if not value:
        return 0
    # Strip alpha chars first (Rs., INR, etc.) — keeps any '.' attached to digits
    no_alpha = re.sub(r"[A-Za-z]+", "", value)
    cleaned = re.sub(r"[^\d.]", "", no_alpha)
    # Collapse multiple dots (e.g. ".999" → "999", "1.2.3" → first valid number)
    if cleaned.count(".") > 1:
        # Keep only first dot; treat as decimal separator
        first = cleaned.index(".")
        cleaned = cleaned[:first + 1] + cleaned[first + 1:].replace(".", "")
    cleaned = cleaned.lstrip(".")
    if not cleaned:
        return 0
    try:
        rupees = float(cleaned)
        return int(round(rupees * 100))
    except ValueError:
        return 0


def _parse_bool(value: str, default: bool = True) -> bool:
    """Parse various truthy/falsy strings."""
    if not value:
        return default
    v = value.strip().lower()
    if v in ("yes", "true", "y", "1", "in stock", "available", "active", "enabled"):
        return True
    if v in ("no", "false", "n", "0", "out of stock", "unavailable", "inactive", "disabled"):
        return False
    return default


# ============================================================
# FAQs parser
# ============================================================


def parse_faqs(rows: list[list[str]]) -> list[dict[str, Any]]:
    """Parse FAQs sheet.

    Expected columns (case-insensitive, fuzzy matching):
      - Keywords / Triggers / Question Keywords (REQUIRED)
      - Reply / Answer / Response (REQUIRED)
      - Category (optional)
      - Media URL / Image (optional)

    Returns: list of {row_number, keywords, reply, category, media_url}
    """
    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    kw_idx = _find_col(headers, "keyword", "trigger", "question")
    reply_idx = _find_col(headers, "reply", "answer", "response")
    cat_idx = _find_col(headers, "category", "type", "topic")
    media_idx = _find_col(headers, "media", "image", "attachment", "url")

    if kw_idx is None or reply_idx is None:
        raise ValueError(
            "FAQs sheet must have a 'Keywords' column and a 'Reply' column"
        )

    parsed: list[dict[str, Any]] = []
    for i, row in enumerate(rows[1:], start=2):
        kw_raw = _safe_get(row, kw_idx)
        reply = _safe_get(row, reply_idx)
        if not kw_raw or not reply:
            continue

        # Split keywords by comma, semicolon, or pipe
        keywords = [
            k.strip()
            for k in re.split(r"[,;|]", kw_raw)
            if k.strip()
        ]
        if not keywords:
            continue

        parsed.append(
            {
                "row_number": i,
                "keywords": keywords,
                "reply": reply,
                "category": _safe_get(row, cat_idx) or None,
                "media_url": _safe_get(row, media_idx) or None,
            }
        )

    return parsed


# ============================================================
# Products parser
# ============================================================


def parse_products(rows: list[list[str]]) -> list[dict[str, Any]]:
    """Parse products / menu sheet.

    Expected columns:
      - Name / Item / Title (REQUIRED)
      - Price / Cost / Rate (REQUIRED)
      - Description (optional)
      - SKU / Code (optional)
      - Category (optional)
      - Image / Photo URL (optional)
      - In Stock / Available (optional, default true)
    """
    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    name_idx = _find_col(headers, "name", "item", "title", "product")
    price_idx = _find_col(headers, "price", "cost", "rate")
    desc_idx = _find_col(headers, "description", "desc", "info")
    sku_idx = _find_col(headers, "sku", "code")
    cat_idx = _find_col(headers, "category", "type", "group")
    img_idx = _find_col(headers, "image", "img", "photo", "picture")
    stock_idx = _find_col(headers, "stock", "available")

    if name_idx is None or price_idx is None:
        raise ValueError(
            "Products sheet must have a 'Name' column and a 'Price' column"
        )

    parsed: list[dict[str, Any]] = []
    for i, row in enumerate(rows[1:], start=2):
        name = _safe_get(row, name_idx)
        if not name:
            continue

        parsed.append(
            {
                "row_number": i,
                "name": name,
                "price_paise": _parse_money_to_paise(_safe_get(row, price_idx)),
                "description": _safe_get(row, desc_idx) or None,
                "sku": _safe_get(row, sku_idx) or None,
                "category": _safe_get(row, cat_idx) or None,
                "image_url": _safe_get(row, img_idx) or None,
                "in_stock": _parse_bool(_safe_get(row, stock_idx), default=True),
            }
        )

    return parsed


# ============================================================
# Services parser
# ============================================================


def parse_services(rows: list[list[str]]) -> list[dict[str, Any]]:
    """Parse bookable services sheet.

    Expected columns:
      - Name / Service / Title (REQUIRED)
      - Duration / Time / Minutes (optional, default 30)
      - Price / Cost (optional, default 0)
      - Description (optional)
      - Active / Enabled (optional, default true)
    """
    if not rows or len(rows) < 2:
        return []

    headers = rows[0]
    name_idx = _find_col(headers, "name", "service", "title")
    dur_idx = _find_col(headers, "duration", "time", "minute")
    price_idx = _find_col(headers, "price", "cost", "rate")
    desc_idx = _find_col(headers, "description", "desc", "info")
    active_idx = _find_col(headers, "active", "enabled", "available")

    if name_idx is None:
        raise ValueError("Services sheet must have a 'Name' column")

    parsed: list[dict[str, Any]] = []
    for i, row in enumerate(rows[1:], start=2):
        name = _safe_get(row, name_idx)
        if not name:
            continue

        dur_str = _safe_get(row, dur_idx)
        duration = 30
        if dur_str:
            dur_clean = re.sub(r"\D", "", dur_str)
            if dur_clean:
                duration = int(dur_clean)

        parsed.append(
            {
                "row_number": i,
                "name": name,
                "duration_minutes": duration,
                "price_paise": _parse_money_to_paise(_safe_get(row, price_idx)),
                "description": _safe_get(row, desc_idx) or None,
                "is_active": _parse_bool(_safe_get(row, active_idx), default=True),
            }
        )

    return parsed
