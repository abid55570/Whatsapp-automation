"""Pick the best reply text for a given detected customer language.

`BusinessIntent.reply_text`          = default (English fallback)
`BusinessIntent.reply_translations`  = per-locale overrides, e.g. {"hi": "..."}

Matching engine returns detected_language as one of:
  english | hindi | hinglish | bengali | urdu | bhojpuri | None

These map to locale codes stored in reply_translations:
  en | hi | hinglish | bn | ur | bho
"""

# Map matching engine output → locale code
DETECTED_LANG_TO_LOCALE: dict[str, str] = {
    "english": "en",
    "hindi": "hi",
    "hinglish": "hinglish",
    "bengali": "bn",
    "urdu": "ur",
    "bhojpuri": "bho",
}

# For each locale, ordered preference chain
# (first available reply_translations key wins, falls back to reply_text)
LOCALE_FALLBACK_CHAIN: dict[str, list[str]] = {
    "en": ["en"],
    "hi": ["hi", "hinglish", "en"],
    "hinglish": ["hinglish", "hi", "en"],
    "bn": ["bn", "en"],
    "ur": ["ur", "hinglish", "hi", "en"],
    "bho": ["bho", "hi", "hinglish", "en"],
}


def pick_reply(
    reply_text: str,
    reply_translations: dict[str, str] | None,
    detected_language: str | None,
) -> str:
    """Return the best reply for a given detected customer language.

    Args:
        reply_text: Default/fallback reply (mandatory)
        reply_translations: Optional dict of locale code → translated text
        detected_language: Output from language_detector

    Returns:
        Best matching reply string.
    """
    if not reply_translations:
        return reply_text

    locale = DETECTED_LANG_TO_LOCALE.get(detected_language or "english", "en")
    chain = LOCALE_FALLBACK_CHAIN.get(locale, ["en"])

    for code in chain:
        text = reply_translations.get(code)
        if text and text.strip():
            return text

    return reply_text
