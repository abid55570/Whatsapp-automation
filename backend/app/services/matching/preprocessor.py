"""Text preprocessing: normalize and tokenize.

Preserves Devanagari, Bengali, Arabic scripts and emojis;
only lowercases ASCII letters.
"""
import re

# Split on whitespace, punctuation, and Hindi/Bengali sentence terminators
_TOKEN_SPLIT = re.compile(r"[\s,;.!?।॥।]+")


def normalize(text: str) -> str:
    """Lowercase ASCII letters; leave everything else untouched."""
    if not text:
        return ""
    out: list[str] = []
    for ch in text:
        if "A" <= ch <= "Z":
            out.append(ch.lower())
        else:
            out.append(ch)
    return "".join(out).strip()


def tokenize(text: str) -> list[str]:
    """Split normalized text into tokens, preserving non-ASCII scripts."""
    if not text:
        return []
    return [t for t in _TOKEN_SPLIT.split(text) if t]
