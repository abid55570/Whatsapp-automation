"""Parse pickup time from free-text Hindi/Hinglish/English.

Examples:
  "abhi"                        → now
  "30 minute mein"              → now + 30 min
  "1 hour"                      → now + 1 hour
  "5 baje"                      → 5 PM today (heuristic: <8 → PM)
  "5 PM"                        → 17:00 today
  "shaam ko 7"                  → 19:00 today
  "kal subah 10"                → 10:00 tomorrow
  "evening 6"                   → 18:00 today
"""
import re
from datetime import datetime, timedelta, timezone


HINDI_TIME_NUMBERS: dict[str, int] = {
    "ek": 1, "do": 2, "teen": 3, "char": 4, "chaar": 4,
    "panch": 5, "paanch": 5,
    "che": 6, "chhe": 6,
    "saat": 7, "aath": 8, "nau": 9, "das": 10,
    "gyarah": 11, "gyaarah": 11,
    "barah": 12, "baarah": 12,
    "एक": 1, "दो": 2, "तीन": 3, "चार": 4,
    "पाँच": 5, "पांच": 5, "छह": 6, "छे": 6,
    "सात": 7, "आठ": 8, "नौ": 9, "दस": 10,
    "ग्यारह": 11, "बारह": 12,
}

# Words that mark AM
_AM_MARKERS = ("am", "subah", "morning", "सुबह", "सबेरे")

# Words that mark PM
_PM_MARKERS = (
    "pm", "shaam", "evening", "raat", "night",
    "dopahar", "afternoon",
    "शाम", "रात", "दोपहर",
)

# Words that mean tomorrow
_TOMORROW_MARKERS = ("kal", "tomorrow", "next day", "कल")

# Words that mean now / ASAP
_NOW_MARKERS = (
    "abhi", "now", "right now", "right away", "asap",
    "turant", "अभी", "तुरंत",
)


def _has_any(text: str, markers: tuple[str, ...]) -> bool:
    return any(m in text for m in markers)


def _word_to_number(token: str) -> int | None:
    token = token.lower().strip()
    if token.isdigit():
        return int(token)
    return HINDI_TIME_NUMBERS.get(token)


def parse_pickup_time(
    text: str | None,
    now: datetime,
    default_open: str = "10:00",
) -> datetime | None:
    """Parse a customer-requested pickup time. Returns None if can't parse.

    `now` should be in the business's local timezone for sensible defaults.
    """
    if not text:
        return None
    text = text.lower().strip()
    if not text:
        return None

    # ---------- "abhi" / "now" ----------
    if any(text == m or text.startswith(m + " ") for m in _NOW_MARKERS):
        return now

    # ---------- "X minute(s) mein" ----------
    m = re.search(
        r"(\d+)\s*(?:min|mins|minute|minutes|मिनट)\b", text, re.IGNORECASE
    )
    if m:
        return now + timedelta(minutes=int(m.group(1)))

    # ---------- "X hour(s) / ghante" ----------
    m = re.search(
        r"(\d+)\s*(?:hour|hours|hr|hrs|ghanta|ghante|घंटा|घंटे)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        return now + timedelta(hours=int(m.group(1)))

    # ---------- "5 baje" / "5 PM" / "five o'clock" ----------
    # Try digit first
    m = re.search(
        r"\b(\d{1,2})(?::(\d{2}))?\s*(?:baje|बजे|o'?clock|pm|am)?", text
    )
    hour: int | None = None
    minute: int = 0
    if m:
        hour = int(m.group(1))
        if m.group(2):
            minute = int(m.group(2))
    else:
        # Try Hindi word
        for token in text.split():
            num = _word_to_number(token)
            if num is not None and 1 <= num <= 12:
                hour = num
                break

    if hour is None:
        return None

    # Determine AM/PM
    is_pm = _has_any(text, _PM_MARKERS)
    is_am = _has_any(text, _AM_MARKERS)

    if hour > 12:
        # already 24h
        target_hour = hour
    elif is_pm and hour < 12:
        target_hour = hour + 12
    elif is_am and hour == 12:
        target_hour = 0
    elif is_am:
        target_hour = hour
    else:
        # Heuristic: if hour is in 1..7, assume PM (common SMB pickup)
        # else use as-is (8..12 = AM/PM ambiguous, prefer same-period)
        if 1 <= hour <= 7:
            target_hour = hour + 12
        else:
            target_hour = hour

    if not 0 <= target_hour <= 23:
        return None

    is_tomorrow = _has_any(text, _TOMORROW_MARKERS)

    target = now.replace(hour=target_hour, minute=minute, second=0, microsecond=0)
    if is_tomorrow:
        target += timedelta(days=1)
    elif target <= now:
        # Past today's time → tomorrow
        target += timedelta(days=1)

    return target
