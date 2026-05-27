"""Cart data class + WhatsApp-formatted summary builder."""
from dataclasses import dataclass


@dataclass
class CartItem:
    """One line in an in-progress order."""

    product_id: str  # UUID as str (for JSON serialization in conversation.state)
    name: str
    quantity: int
    unit_price_paise: int

    @property
    def subtotal_paise(self) -> int:
        return self.unit_price_paise * self.quantity

    def to_dict(self) -> dict:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price_paise": self.unit_price_paise,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "CartItem":
        return cls(
            product_id=d["product_id"],
            name=d["name"],
            quantity=int(d["quantity"]),
            unit_price_paise=int(d["unit_price_paise"]),
        )


def _format_rupees(paise: int) -> str:
    rupees = paise / 100
    if rupees == int(rupees):
        return f"₹{int(rupees)}"
    return f"₹{rupees:.2f}"


# ============================================================
# Localized strings
# ============================================================

_SUMMARY_HEADER: dict[str, str] = {
    "english": "📝 *Order Summary*",
    "hindi": "📝 *ऑर्डर सारांश*",
    "hinglish": "📝 *Order Summary*",
    "bengali": "📝 *অর্ডার সারাংশ*",
    "urdu": "📝 *آرڈر کا خلاصہ*",
    "bhojpuri": "📝 *Order Summary*",
}

_TOTAL_LABEL: dict[str, str] = {
    "english": "Total",
    "hindi": "कुल",
    "hinglish": "Total",
    "bengali": "মোট",
    "urdu": "Total",
    "bhojpuri": "Kul",
}

_ITEMS_LABEL: dict[str, str] = {
    "english": "items",
    "hindi": "आइटम",
    "hinglish": "items",
    "bengali": "আইটেম",
    "urdu": "items",
    "bhojpuri": "item",
}

_CONFIRM_PROMPT: dict[str, str] = {
    "english": "Reply *YES* to confirm or *cancel* to start over.",
    "hindi": "*YES* लिखें कन्फर्म करने के लिए, या *cancel* फिर से शुरू करने के लिए।",
    "hinglish": "*YES* likhein confirm karne ke liye, ya *cancel* phir se shuru karne ke liye.",
    "bengali": "*YES* লিখুন কনফার্ম করতে, বা *cancel* আবার শুরু করতে।",
    "urdu": "*YES* likhein confirm karne ke liye, ya *cancel* phir se shuru karne ke liye.",
    "bhojpuri": "*YES* likhi confirm khatir, ya *cancel* phir se shuru khatir.",
}


def _t(table: dict[str, str], lang: str | None) -> str:
    return table.get(lang or "english", table["english"])


def format_order_summary(
    items: list[CartItem],
    detected_language: str | None = None,
) -> str:
    """Render a WhatsApp-friendly order summary."""
    if not items:
        return ""

    lang = detected_language or "english"
    lines: list[str] = [_t(_SUMMARY_HEADER, lang), ""]

    total_qty = 0
    total_paise = 0
    for it in items:
        subtotal = it.subtotal_paise
        total_paise += subtotal
        total_qty += it.quantity
        lines.append(
            f"• {it.name} × {it.quantity} - {_format_rupees(subtotal)}"
        )

    lines.append("")
    lines.append(
        f"{total_qty} {_t(_ITEMS_LABEL, lang)} · *{_t(_TOTAL_LABEL, lang)}: {_format_rupees(total_paise)}*"
    )
    lines.append("")
    lines.append(_t(_CONFIRM_PROMPT, lang))
    return "\n".join(lines)


def cart_total_paise(items: list[CartItem]) -> int:
    return sum(it.subtotal_paise for it in items)


def cart_total_quantity(items: list[CartItem]) -> int:
    return sum(it.quantity for it in items)
