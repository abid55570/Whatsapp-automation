"""On-the-fly AI translation for replies.

Used when owner has only one reply variant (English) but customer wrote
in Hindi/Bengali/etc. The reply_picker.py fallback chain handles owner-
authored translations; this module handles AI-generated translations
when the owner has the AI add-on enabled.
"""
import logging

from app.services.ai.client import AIError, generate

logger = logging.getLogger(__name__)


_LANG_DESC: dict[str, str] = {
    "english": "natural English",
    "hindi": "Hindi using Devanagari script (हिन्दी)",
    "hinglish": "Hinglish — Hindi words written in Roman script, mixed with English where natural",
    "bengali": "Bengali using Bengali script (বাংলা)",
    "urdu": "Urdu in Roman script (the way North-Indian Muslims often text)",
    "bhojpuri": "Bhojpuri — informal Roman script with some Devanagari OK",
}


async def translate_to(
    text: str,
    target_language: str | None,
) -> str | None:
    """Translate `text` into target language. Returns None on error.

    No-op for English (returns original).
    """
    if not text or not text.strip():
        return None
    lang = (target_language or "english").lower()
    if lang in ("english", "en"):
        return text

    target_desc = _LANG_DESC.get(lang, "the customer's language")

    prompt = (
        f"Translate the following business reply into {target_desc}.\n"
        f"Keep the meaning, tone (friendly, brief), and any emoji + price.\n"
        f"Reply with ONLY the translation, no preamble.\n\n"
        f"Original:\n{text}"
    )

    try:
        result = await generate(prompt, max_tokens=400)
    except AIError as exc:
        logger.warning("Translation AI call failed: %s", exc)
        return None

    out = (result or "").strip()
    return out if len(out) >= 3 else None
