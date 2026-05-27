"""AI fallback when matching engine has no good match.

Generates a brief reply in the customer's detected language. Used only when
business has AI add-on enabled + quota remaining.
"""
import logging

from app.services.ai.client import AIError, generate

logger = logging.getLogger(__name__)


_SYSTEM_PROMPT = """You are a customer service assistant for a small business in India.
You reply to customer WhatsApp messages.

CRITICAL RULES:
1. Reply in the SAME language the customer used (Hindi/Hinglish/English/Bengali/Urdu/Bhojpuri).
2. Keep it brief: 1-2 sentences MAX.
3. Use natural local phrasing — like a friendly shopkeeper.
4. If you don't know the answer (price, hours, address, etc.), respond:
   "Let me check and get back to you" — in the customer's language.
5. NEVER fabricate prices, timings, addresses, or product details.
6. Use ✅ ❌ 📞 ⏰ emojis sparingly when natural.
7. Always polite. No corporate-speak.
"""


async def generate_smart_reply(
    business_name: str,
    business_type: str,
    customer_message: str,
    detected_language: str | None,
    enabled_intent_names: list[str] | None = None,
) -> str | None:
    """Generate a fallback reply via AI. Returns None on failure."""
    if not customer_message.strip():
        return None

    lines: list[str] = [
        f"Business: {business_name} (type: {business_type})",
        f"Customer message language: {detected_language or 'unknown'}",
        f"Customer wrote: {customer_message!r}",
    ]
    if enabled_intent_names:
        lines.append(
            f"FAQs already covered (don't duplicate): {', '.join(enabled_intent_names[:12])}"
        )
    lines.append("")
    lines.append(
        "Write ONE brief friendly reply in the customer's language. "
        "Just the reply text, no preamble."
    )
    prompt = "\n".join(lines)

    try:
        reply = await generate(prompt, system=_SYSTEM_PROMPT, max_tokens=200)
    except AIError as exc:
        logger.warning("Smart reply AI call failed: %s", exc)
        return None

    text = (reply or "").strip()
    # Guardrail: skip if AI returned nothing useful
    if len(text) < 3:
        return None
    return text
