"""Conversation state helpers: affirmative / negative detection.

Used by the order flow state machine to know when a customer confirms
(`yes/haan/ji/ठीक`) or cancels (`no/nahi/नहीं`).
"""
import re

AFFIRMATIVE_WORDS: frozenset[str] = frozenset({
    # English
    "yes", "y", "yeah", "yep", "yup", "yaa", "yas",
    "ok", "okay", "okk", "okie", "okies",
    "sure", "absolutely", "definitely",
    "confirm", "confirmed", "confirmm",
    "go", "go ahead", "do it",
    # Hinglish
    "haan", "han", "haa", "ha", "haanji",
    "ji", "jee", "ji haan", "ji han",
    "thik", "theek", "thik hai", "theek hai", "tik",
    "pakka", "pucca", "bilkul", "zaroor",
    "kar do", "karo", "send karo",
    "ok ji", "haan ji",
    # Devanagari
    "हाँ", "हां", "जी", "जी हाँ", "ठीक", "ठीक है", "बिल्कुल", "पक्का",
    # Bengali
    "হ্যাঁ", "হা", "ঠিক", "ঠিক আছে",
    # Urdu
    "ji han", "haan ji",
    "ہاں", "جی",
})

NEGATIVE_WORDS: frozenset[str] = frozenset({
    # English
    "no", "n", "nope", "nah", "naah", "naa",
    "cancel", "abort", "stop", "exit", "quit",
    "remove", "delete",
    # Hinglish
    "nahi", "nahin", "nai", "na",
    "mat", "mat karo", "mat bhejo",
    "cancel karo", "rok do",
    # Devanagari
    "नहीं", "नही", "मत", "रद्द", "रोको",
    # Bengali
    "না", "নয়",
    # Urdu
    "نہیں",
})


_WORD_SPLIT = re.compile(r"[^\wऀ-ॿ঑-ৱ؀-ۿ]+", re.UNICODE)


def _tokens(text: str) -> list[str]:
    """Lowercase tokens, preserve Devanagari/Bengali/Arabic."""
    if not text:
        return []
    out: list[str] = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(ch.lower())
        else:
            out.append(ch)
    normalized = "".join(out).strip()
    return [t for t in _WORD_SPLIT.split(normalized) if t]


def _matches_any(text: str, words: frozenset[str]) -> bool:
    if not text:
        return False
    norm = text.strip().lower()
    if norm in words:
        return True
    # Match whole tokens
    tokens = _tokens(text)
    if any(t in words for t in tokens):
        return True
    # Match multi-word phrases ("haan ji", "thik hai")
    multi = {w for w in words if " " in w}
    for phrase in multi:
        if phrase in norm:
            return True
    return False


def is_affirmative(text: str | None) -> bool:
    """True if customer is saying yes / confirm."""
    return _matches_any(text or "", AFFIRMATIVE_WORDS)


def is_negative(text: str | None) -> bool:
    """True if customer is saying no / cancel."""
    return _matches_any(text or "", NEGATIVE_WORDS)
