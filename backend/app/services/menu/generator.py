"""Build menu / services text from Product + Service rows.

Used by the WhatsApp processor when `ask_menu` or `ask_services` intents
fire AND the business has populated catalog data (typically synced from
their Google Sheet).

Output is plain-text formatted for WhatsApp (uses *bold*, emojis).
"""
from typing import Iterable

from app.models import Product, Service


# ============================================================
# Localized strings
# ============================================================

_MENU_HEADER: dict[str, str] = {
    "english": "🍽️ *{name} - Menu*",
    "hindi": "🍽️ *{name} - मेन्यू*",
    "hinglish": "🍽️ *{name} - Menu*",
    "bengali": "🍽️ *{name} - মেনু*",
    "urdu": "🍽️ *{name} - مینو*",
    "bhojpuri": "🍽️ *{name} - मेन्यू*",
}

_MENU_FOOTER: dict[str, str] = {
    "english": "💬 Reply with item + quantity to order\nExample: \"2 cheese burger\"",
    "hindi": "💬 ऑर्डर: 'item + quantity' लिखें\nजैसे: \"2 cheese burger\"",
    "hinglish": "💬 Order: 'item + quantity' likhein\nJaise: \"2 cheese burger\"",
    "bengali": "💬 অর্ডার: 'item + পরিমাণ' লিখুন",
    "urdu": "💬 Order: 'item + quantity' likhein",
    "bhojpuri": "💬 Order: 'item + quantity' likhi",
}

_SERVICES_HEADER: dict[str, str] = {
    "english": "✨ *{name} - Services*",
    "hindi": "✨ *{name} - सेवाएं*",
    "hinglish": "✨ *{name} - Services*",
    "bengali": "✨ *{name} - পরিষেবা*",
    "urdu": "✨ *{name} - خدمات*",
    "bhojpuri": "✨ *{name} - सेवा*",
}

_SERVICES_FOOTER: dict[str, str] = {
    "english": "💬 Reply with the service name to book",
    "hindi": "💬 बुक करने के लिए service का नाम लिखें",
    "hinglish": "💬 Book karne ke liye service ka naam likhein",
    "bengali": "💬 বুক করতে service-এর নাম লিখুন",
    "urdu": "💬 Book karne ke liye service ka naam likhein",
    "bhojpuri": "💬 Book ke liye service ke naam likhi",
}

_SOLD_OUT: dict[str, str] = {
    "english": "Sold out",
    "hindi": "खत्म",
    "hinglish": "Khatam",
    "bengali": "শেষ",
    "urdu": "Khatam",
    "bhojpuri": "Khatam",
}


def _t(table: dict[str, str], lang: str | None, **kw: str) -> str:
    key = lang if lang in table else "english"
    return table[key].format(**kw) if kw else table[key]


# ============================================================
# Category → emoji mapping (auto-pick by keyword)
# ============================================================

_CATEGORY_EMOJI_RULES: list[tuple[tuple[str, ...], str]] = [
    (("pizza",), "🍕"),
    (("burger",), "🍔"),
    (("sandwich", "wrap"), "🥪"),
    (("drink", "beverage", "juice", "lassi", "tea", "coffee", "soda"), "🥤"),
    (("dessert", "sweet", "cake", "ice cream", "kulfi"), "🍰"),
    (("rice", "biryani", "pulao"), "🍚"),
    (("noodle", "pasta", "maggi"), "🍜"),
    (("flour", "atta", "grain", "maida"), "🌾"),
    (("dal", "pulse", "lentil"), "🫘"),
    (("spice", "masala", "salt", "haldi"), "🧂"),
    (("oil", "ghee"), "🛢️"),
    (("snack", "namkeen", "chips"), "🍪"),
    (("soap", "toiletries", "shampoo", "detergent"), "🧼"),
    (("vegetable", "veg", "sabzi"), "🥬"),
    (("fruit",), "🍎"),
    (("dairy", "milk", "paneer", "curd"), "🥛"),
    (("hair", "haircut", "cut"), "💇"),
    (("skin", "facial", "spa"), "🧖"),
    (("massage", "therapy"), "💆"),
    (("nail", "manicure", "pedicure"), "💅"),
    (("makeup",), "💄"),
    (("consultation", "doctor", "appointment"), "🩺"),
    (("class", "course", "tuition"), "📚"),
    (("gym", "fitness", "yoga"), "💪"),
]


def category_emoji(category: str | None) -> str:
    """Pick an emoji for a category by keyword match."""
    if not category:
        return "•"
    c = category.lower()
    for keywords, emoji in _CATEGORY_EMOJI_RULES:
        if any(k in c for k in keywords):
            return emoji
    return "•"


# ============================================================
# Formatters
# ============================================================


def _format_price(paise: int) -> str:
    if not paise:
        return ""
    rupees = paise / 100
    if rupees == int(rupees):
        return f"₹{int(rupees)}"
    return f"₹{rupees:.2f}"


def _group_by_category(
    items: Iterable[Product | Service], category_attr: str = "category"
) -> dict[str, list]:
    grouped: dict[str, list] = {}
    for item in items:
        cat = getattr(item, category_attr, None) or "Items"
        grouped.setdefault(cat, []).append(item)
    return grouped


# ============================================================
# Menu generator (Products)
# ============================================================


def generate_menu_text(
    business_name: str,
    products: list[Product],
    detected_language: str | None = None,
    include_out_of_stock: bool = True,
) -> str:
    """Build a formatted menu text from Product rows.

    Returns empty string if no products provided.
    """
    if not products:
        return ""

    visible = (
        products if include_out_of_stock else [p for p in products if p.in_stock]
    )
    if not visible:
        return ""

    grouped = _group_by_category(visible, "category")

    # Sort: in-stock first, then by name
    for cat in grouped:
        grouped[cat].sort(key=lambda p: (not p.in_stock, p.name.lower()))

    lang = detected_language or "english"
    lines: list[str] = [_t(_MENU_HEADER, lang, name=business_name), ""]

    # Sort categories — "Items" (default) last
    cat_names = sorted(grouped.keys(), key=lambda c: (c == "Items", c.lower()))

    for cat in cat_names:
        items = grouped[cat]
        emoji = category_emoji(cat)
        lines.append(f"{emoji} *{cat}*")
        for p in items:
            price = _format_price(p.price_paise)
            if p.in_stock:
                line = f"• {p.name} - {price} ✅"
            else:
                sold = _t(_SOLD_OUT, lang)
                line = f"• {p.name} - {price} ❌ _{sold}_"
            lines.append(line)
        lines.append("")

    lines.append(_t(_MENU_FOOTER, lang))
    return "\n".join(lines).rstrip()


# ============================================================
# Services generator
# ============================================================


def generate_services_text(
    business_name: str,
    services: list[Service],
    detected_language: str | None = None,
) -> str:
    """Build a formatted services list."""
    if not services:
        return ""

    visible = [s for s in services if s.is_active]
    if not visible:
        return ""

    lang = detected_language or "english"
    lines: list[str] = [_t(_SERVICES_HEADER, lang, name=business_name), ""]

    for s in sorted(visible, key=lambda x: x.name.lower()):
        price = _format_price(s.price_paise)
        duration = f"{s.duration_minutes} min" if s.duration_minutes else ""
        bits = [s.name]
        if duration:
            bits.append(duration)
        if price:
            bits.append(price)
        lines.append(f"• {' · '.join(bits)}")

    lines.append("")
    lines.append(_t(_SERVICES_FOOTER, lang))
    return "\n".join(lines).rstrip()
