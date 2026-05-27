"""HSN/SAC auto-suggest service.

When the owner types a product name in the invoice builder we suggest the
most likely HSN code + default GST rate. Powered by:
  1. Exact keyword match (fast, used first)
  2. RapidFuzz token-set ratio (handles typos / partial matches)
  3. Fallback to "9999" (unclassified) — owner can manually set later.

Dataset: `backend/data/hsn_common.json` — curated list of ~50 most common
codes for kirana, restaurant, salon, clinic. Full GST master is ~5000 entries;
we keep memory small by loading this subset eagerly.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from rapidfuzz import fuzz, process

logger = logging.getLogger(__name__)

_DATA_FILE = Path(__file__).parent.parent.parent.parent / "data" / "hsn_common.json"


@lru_cache(maxsize=1)
def _load_entries() -> list[dict[str, Any]]:
    """Load the HSN master once per process."""
    if not _DATA_FILE.exists():
        logger.warning("HSN master file not found at %s", _DATA_FILE)
        return []
    with open(_DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("entries", [])


@lru_cache(maxsize=1)
def _keyword_index() -> dict[str, dict[str, Any]]:
    """Build a flat keyword → entry index for exact-match path."""
    index: dict[str, dict[str, Any]] = {}
    for entry in _load_entries():
        for kw in entry.get("keywords", []):
            index[kw.lower().strip()] = entry
        # Also index the description and the code itself
        index[entry["desc"].lower().strip()] = entry
        index[entry["code"]] = entry
    return index


def suggest(product_name: str, *, limit: int = 5, min_score: int = 60) -> list[dict[str, Any]]:
    """Return up to `limit` HSN suggestions for a product name.

    Each suggestion: {code, desc, rate, unit, score}.
    Sorted by descending score. Returns empty list if nothing matches.
    """
    if not product_name or not product_name.strip():
        return []

    needle = product_name.lower().strip()
    entries = _load_entries()
    if not entries:
        return []

    # 1) Exact keyword hit — instant 100 score, return immediately
    index = _keyword_index()
    if needle in index:
        e = index[needle]
        return [{
            "code": e["code"],
            "desc": e["desc"],
            "rate": e["rate"],
            "unit": e["unit"],
            "score": 100,
        }]

    # 2) Substring containment — high confidence
    contains: list[tuple[dict, int]] = []
    for entry in entries:
        for kw in entry.get("keywords", []):
            kw_l = kw.lower()
            if kw_l in needle or needle in kw_l:
                contains.append((entry, 90))
                break
    if contains:
        seen: set[str] = set()
        out: list[dict[str, Any]] = []
        for entry, score in contains:
            if entry["code"] in seen:
                continue
            seen.add(entry["code"])
            out.append({
                "code": entry["code"],
                "desc": entry["desc"],
                "rate": entry["rate"],
                "unit": entry["unit"],
                "score": score,
            })
        return out[:limit]

    # 3) Fuzzy match against all keywords + descriptions
    haystack: list[tuple[str, dict]] = []
    for entry in entries:
        haystack.append((entry["desc"], entry))
        for kw in entry.get("keywords", []):
            haystack.append((kw, entry))

    choices = [text for text, _ in haystack]
    matches = process.extract(
        needle, choices, scorer=fuzz.token_set_ratio, limit=limit * 4
    )

    # Dedup by code, take best score per code
    by_code: dict[str, dict[str, Any]] = {}
    for text, score, idx in matches:
        if score < min_score:
            continue
        _, entry = haystack[idx]
        code = entry["code"]
        if code in by_code and by_code[code]["score"] >= score:
            continue
        by_code[code] = {
            "code": code,
            "desc": entry["desc"],
            "rate": entry["rate"],
            "unit": entry["unit"],
            "score": int(score),
        }

    return sorted(by_code.values(), key=lambda x: -x["score"])[:limit]


def best_match(product_name: str, *, min_score: int = 80) -> dict[str, Any] | None:
    """Return the single best HSN suggestion, or None if nothing crosses threshold."""
    suggestions = suggest(product_name, limit=1, min_score=min_score)
    return suggestions[0] if suggestions else None
