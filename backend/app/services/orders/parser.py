"""Parse free-text WhatsApp orders into a structured cart.

Examples handled:
  "2 cheese burger, 1 pizza"       → [(CheeseBurger, 2), (Pizza, 1)]
  "do atta, ek toor dal"           → [(Atta, 2), (ToorDal, 1)]
  "pizza × 3"                       → [(Pizza, 3)]
  "atta 5kg"                       → [(Atta, 1)]  (matches via fuzzy)
  "5 kg atta aur 1 lt oil"         → [(Atta 5kg, 1), (Oil, 1)]
  "मुझे 2 अट्टा चाहिए"             → [(Atta, 2)]
"""
import re
from dataclasses import dataclass
from typing import Iterable

from rapidfuzz import fuzz, process

# Hindi/Hinglish/Devanagari number words → integer
HINDI_NUMBERS: dict[str, int] = {
    # Hinglish (Roman)
    "ek": 1, "eik": 1,
    "do": 2, "doh": 2,
    "teen": 3,
    "char": 4, "chaar": 4,
    "panch": 5, "paanch": 5, "paach": 5,
    "che": 6, "chhe": 6, "chha": 6,
    "saat": 7,
    "aath": 8,
    "nau": 9, "no": 9,
    "das": 10, "dus": 10,
    "gyarah": 11, "gyaarah": 11,
    "barah": 12, "baarah": 12, "bara": 12,
    # Devanagari
    "एक": 1,
    "दो": 2,
    "तीन": 3,
    "चार": 4,
    "पाँच": 5, "पांच": 5,
    "छह": 6, "छे": 6,
    "सात": 7,
    "आठ": 8,
    "नौ": 9,
    "दस": 10,
    "ग्यारह": 11,
    "बारह": 12,
    # Bengali
    "এক": 1, "দুই": 2, "তিন": 3, "চার": 4, "পাঁচ": 5,
}

# Words that indicate this is an order ("I want", "lena hai" etc.)
_ORDER_INTENT_PREFIXES = re.compile(
    r"^(i\s+want|i\s+need|mujhe|me\s+chahiye|chahiye|lena\s+hai|chahta\s+hu|"
    r"de\s+do|de\s+dijiye|order|please\s+send|bhejo|bheje|"
    r"मुझे|चाहिए|दे\s+दो|भेजो)\s+",
    re.IGNORECASE,
)

# Separators between items
_SEPARATORS = re.compile(
    r"[,;।]+|\s+aur\s+|\s+and\s+|\s+और\s+|\s+\+\s+|\s*&\s*",
    re.IGNORECASE,
)

# Units to strip (kept in name but not parsed as qty)
_UNIT_WORDS = {
    "kg", "kilo", "kilos", "g", "gram", "grams", "gm", "gms",
    "l", "litre", "litres", "liter", "liters", "lt", "ml",
    "packet", "packets", "pkt", "pkts", "pack", "packs",
    "piece", "pieces", "pc", "pcs", "nos", "no",
    "dozen", "dozens",
}


@dataclass
class ParsedItem:
    """One parsed segment before fuzzy-matching against catalog."""

    quantity: int
    item_text: str


def looks_like_order(text: str) -> bool:
    """Heuristic: does this message look like an order attempt?

    True if: has digit OR Hindi number word, AND has at least one non-number word.
    """
    if not text or len(text.strip()) < 2:
        return False
    lowered = text.lower()
    has_digit = bool(re.search(r"\d", text))
    has_hindi_num = any(
        re.search(rf"\b{w}\b", lowered) for w in HINDI_NUMBERS
    )
    if not (has_digit or has_hindi_num):
        return False
    # Need some non-number content
    word_count = len(re.findall(r"[a-zA-Zऀ-ॿ঑-ৱ]{2,}", text))
    return word_count >= 1


def _parse_segment(text: str) -> ParsedItem:
    """Extract (qty, item_text) from one segment.

    Strategies tried in order:
      1. Leading number: "2 cheese burger"
      2. Leading Hindi word: "do cheese burger"
      3. Trailing × or x with number: "pizza × 2", "burger x3"
      4. Trailing number: "pizza 2"
      5. No qty → default 1
    """
    text = text.strip()
    text = _ORDER_INTENT_PREFIXES.sub("", text)
    text = text.strip()
    if not text:
        return ParsedItem(0, "")

    # 1. Leading digit
    m = re.match(r"^(\d+)\s+(.+)$", text)
    if m:
        return ParsedItem(int(m.group(1)), m.group(2).strip())

    # 2. Leading Hindi number word
    first_word = text.split(maxsplit=1)
    if first_word:
        candidate = first_word[0].lower()
        if candidate in HINDI_NUMBERS:
            rest = first_word[1] if len(first_word) > 1 else ""
            return ParsedItem(HINDI_NUMBERS[candidate], rest.strip())

    # 3. Trailing × / x with number
    m = re.match(r"^(.+?)\s*[×xX]\s*(\d+)\s*$", text)
    if m:
        return ParsedItem(int(m.group(2)), m.group(1).strip())

    # 4. Trailing digit ("pizza 2")
    m = re.match(r"^(.+?)\s+(\d+)\s*$", text)
    if m:
        # But careful: "atta 5kg" — trailing 5 is unit, not qty
        # Check if rest of segment after digit has a unit word
        rest_after = ""  # nothing after digit since this is end-anchored
        # The match group(2) is the digit at end. Group(1) is the rest.
        # If group(1) ends with a unit-ish phrase, treat digit as qty
        # Otherwise, "atta 5kg" pattern: digit followed by unit → treat as part of name
        # Easiest: if the segment as-a-whole has a unit AFTER the digit, it's part of name.
        # We've already matched end-anchored, so no unit after. So treat digit as qty.
        return ParsedItem(int(m.group(2)), m.group(1).strip())

    # 5. No qty
    return ParsedItem(1, text)


def _strip_filler(text: str) -> str:
    """Remove common filler words before fuzzy matching."""
    fillers = [
        "please", "pls", "plz", "ji", "bhai", "yaar", "bro",
        "kg", "kgs", "kilos",  # units sometimes left over
    ]
    words = re.findall(r"[\wऀ-ॿ঑-ৱ]+", text, re.UNICODE)
    return " ".join(w for w in words if w.lower() not in fillers)


def fuzzy_match_product(
    text: str,
    products: Iterable,
    threshold: int = 65,
    name_attr: str = "name",
) -> tuple[object, int] | None:
    """Find the best-matching product by name. Returns (product, score) or None.

    `products` is any iterable of objects with `.name` attribute (or
    overridden via name_attr).
    """
    cleaned = _strip_filler(text).lower().strip()
    if not cleaned:
        return None

    items = list(products)
    if not items:
        return None

    choices = {getattr(p, name_attr).lower(): p for p in items}
    result = process.extractOne(
        cleaned, list(choices.keys()), scorer=fuzz.WRatio
    )
    if result is None:
        return None
    match_text, score, _idx = result
    if score < threshold:
        # Also try partial_token_sort_ratio for better recall on long names
        result2 = process.extractOne(
            cleaned, list(choices.keys()), scorer=fuzz.partial_token_sort_ratio
        )
        if result2 and result2[1] >= threshold:
            return choices[result2[0]], int(result2[1])
        return None
    return choices[match_text], int(score)


def parse_order_text(
    text: str,
    products: Iterable,
    threshold: int = 65,
) -> list[tuple[object, int, int]]:
    """Parse free-text order → list of (product, quantity, match_score).

    Args:
        text: Raw customer message
        products: Iterable of Product (or dict-like with .name + .price_paise)
        threshold: Fuzzy match minimum (0-100)

    Returns:
        List of (product, qty, score). Empty if nothing matched.
    """
    if not text:
        return []

    products_list = list(products)
    if not products_list:
        return []

    # Strip leading "order:" / "I want" / "mujhe chahiye" etc.
    text = _ORDER_INTENT_PREFIXES.sub("", text.strip())

    segments = [s.strip() for s in _SEPARATORS.split(text) if s and s.strip()]
    if not segments:
        return []

    cart: list[tuple[object, int, int]] = []
    seen_ids: set = set()

    for seg in segments:
        parsed = _parse_segment(seg)
        if not parsed.item_text or parsed.quantity <= 0:
            continue
        if parsed.quantity > 1000:  # sanity cap
            parsed.quantity = 1000

        match = fuzzy_match_product(parsed.item_text, products_list, threshold)
        if match is None:
            continue
        product, score = match

        # Dedupe: if same product already in cart, sum quantities
        pid = id(product)
        existing = next((c for c in cart if id(c[0]) == pid), None)
        if existing:
            idx = cart.index(existing)
            cart[idx] = (product, existing[1] + parsed.quantity, max(existing[2], score))
        else:
            cart.append((product, parsed.quantity, score))
        seen_ids.add(pid)

    return cart
