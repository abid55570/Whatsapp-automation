"""Detect the primary language of inbound text.

Returns one of: hindi, hinglish, bengali, urdu, english.
"""
import re

_DEVANAGARI = re.compile(r"[ऀ-ॿ]")
_BENGALI = re.compile(r"[ঀ-৿]")
_ARABIC = re.compile(r"[؀-ۿ]")

# Common Hinglish-only words (Roman Hindi)
_HINGLISH_MARKERS = frozenset({
    "hai", "hain", "ho", "ho gaya", "ka", "ke", "ki", "ko", "kya", "kab",
    "kaha", "kaise", "kese", "kitna", "kitne", "kitnaa", "yaar", "bhai",
    "behen", "matlab", "namaste", "namaskar", "shukriya", "dhanyawad",
    "btao", "bata", "batao", "bhejo", "kar", "karo", "karna", "krna",
    "milta", "milega", "chahiye", "chahta", "chahti", "dijiye", "do na",
    "abhi", "kal", "aaj", "subah", "shaam", "raat", "wala", "wali",
    "kitnaa", "ka rate", "rate kya", "kya rate",
})


def detect_language(text: str) -> str:
    """Return the most likely language of `text`.

    Detection order:
      1. Devanagari script → hindi
      2. Bengali script → bengali
      3. Arabic script (Urdu shares this) → urdu
      4. Roman text with Hinglish markers → hinglish
      5. Otherwise → english
    """
    if not text:
        return "english"
    if _DEVANAGARI.search(text):
        return "hindi"
    if _BENGALI.search(text):
        return "bengali"
    if _ARABIC.search(text):
        return "urdu"

    lowered = text.lower()
    tokens = set(re.split(r"\W+", lowered))
    if tokens & _HINGLISH_MARKERS:
        return "hinglish"

    return "english"
