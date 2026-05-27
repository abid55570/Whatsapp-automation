"""Multi-layer intent matching engine.

Layer pipeline (each layer's score combines into a final confidence):
  1. Exact keyword match (word-boundary aware) - highest confidence
  2. Emoji match
  3. Regex pattern match
  4. Transliteration (Roman ↔ Devanagari) - fallback
  5. Fuzzy similarity (rapidfuzz) - last resort

The intent with the highest confidence above MIN_CONFIDENCE wins.

Supports:
  - Global intents (loaded from data/intents/*.json)
  - Custom intents (per-business, e.g., synthesized from Google Sheets)
"""
from __future__ import annotations

import re
from collections.abc import Iterable

from rapidfuzz import fuzz

from app.services.matching.intent_loader import IntentLibrary
from app.services.matching.language_detector import detect_language
from app.services.matching.preprocessor import normalize, tokenize
from app.services.matching.schemas import IntentDefinition, MatchResult

WEIGHT_EXACT: float = 0.90
WEIGHT_EMOJI: float = 0.70
WEIGHT_PATTERN: float = 0.65
WEIGHT_TRANSLITERATION: float = 0.55
WEIGHT_FUZZY_MAX: float = 0.50

MIN_CONFIDENCE: float = 0.30
FUZZY_THRESHOLD: int = 78  # 78 catches "prise"~"price" (1-edit on short token)


class MatchingEngine:
    """Match WhatsApp text against configured intents."""

    def __init__(self, library: IntentLibrary) -> None:
        self.library = library

    def match(
        self,
        text: str,
        enabled_intents: Iterable[str] | None = None,
        custom_keywords: dict[str, list[str]] | None = None,
        custom_intents: dict[str, IntentDefinition] | None = None,
    ) -> MatchResult | None:
        """Return the best matching intent for `text`, or None if no match.

        Args:
            text: Raw inbound message
            enabled_intents: Subset of intent keys to consider (None = all globals)
            custom_keywords: Per-intent extra keywords (e.g., owner-added synonyms)
            custom_intents: Fully synthetic intents (e.g., from Google Sheets)
                            Map from intent_key to IntentDefinition. Considered
                            alongside global intents.
        """
        if not text or not text.strip():
            return None

        normalized_text = normalize(text)
        token_list = tokenize(normalized_text)
        language = detect_language(text)

        # Build candidate set: globals + custom intents
        candidate_keys: list[str] = []
        if enabled_intents is not None:
            candidate_keys = list(enabled_intents)
        else:
            candidate_keys = self.library.list_keys()
            if custom_intents:
                candidate_keys.extend(custom_intents.keys())

        candidates: list[MatchResult] = []
        for key in candidate_keys:
            intent = self.library.get(key)
            if intent is None and custom_intents:
                intent = custom_intents.get(key)
            if intent is None:
                continue

            extras = (custom_keywords or {}).get(key, [])
            result = self._match_one(
                original=text,
                normalized=normalized_text,
                tokens=token_list,
                intent=intent,
                extra_keywords=extras,
                language=language,
            )
            if result is not None and result.confidence >= MIN_CONFIDENCE:
                candidates.append(result)

        if not candidates:
            return None

        # Highest confidence wins; ties broken by intent priority
        def sort_key(r: MatchResult) -> tuple[float, int]:
            intent = self.library.get(r.intent_key) or (
                (custom_intents or {}).get(r.intent_key)
            )
            return (r.confidence, intent.priority if intent else 0)

        candidates.sort(key=sort_key, reverse=True)
        return candidates[0]

    # ------------------------------------------------------------------
    # Per-intent matching pipeline
    # ------------------------------------------------------------------

    def _match_one(
        self,
        original: str,
        normalized: str,
        tokens: list[str],
        intent: IntentDefinition,
        extra_keywords: list[str],
        language: str,
    ) -> MatchResult | None:
        score = 0.0
        matched_kw: list[str] = []
        matched_layer: str | None = None

        all_keywords: list[str] = []
        for kws in intent.languages.values():
            all_keywords.extend(kws)
        all_keywords.extend(extra_keywords)

        # ---------- Layer 1: Exact keyword with word boundary ----------
        for kw in all_keywords:
            kw_norm = normalize(kw)
            if not kw_norm:
                continue
            try:
                pattern = r"\b" + re.escape(kw_norm) + r"\b"
                if re.search(pattern, normalized, re.UNICODE):
                    score = max(score, WEIGHT_EXACT)
                    if kw not in matched_kw:
                        matched_kw.append(kw)
                    matched_layer = matched_layer or "exact"
            except re.error:
                continue

        # ---------- Layer 2: Emoji ----------
        for emoji in intent.emojis:
            if emoji and emoji in original:
                score = max(score, WEIGHT_EMOJI)
                if emoji not in matched_kw:
                    matched_kw.append(emoji)
                matched_layer = matched_layer or "emoji"

        # ---------- Layer 3: Regex pattern ----------
        for pat in intent.patterns:
            try:
                if re.search(pat, original):
                    score = max(score, WEIGHT_PATTERN)
                    matched_layer = matched_layer or "pattern"
                    break
            except re.error:
                continue

        # ---------- Layer 4: Transliteration (only if nothing matched) ----------
        if matched_layer is None:
            translit_score, translit_kw = self._try_transliteration(
                normalized, intent
            )
            if translit_kw is not None:
                score = max(score, translit_score)
                if translit_kw not in matched_kw:
                    matched_kw.append(translit_kw)
                matched_layer = "transliteration"

        # ---------- Layer 5: Fuzzy (only if nothing matched) ----------
        if matched_layer is None:
            fuzzy_score, fuzzy_kw = self._try_fuzzy(tokens, all_keywords)
            if fuzzy_kw is not None:
                score = max(score, fuzzy_score)
                if fuzzy_kw not in matched_kw:
                    matched_kw.append(fuzzy_kw)
                matched_layer = "fuzzy"

        if score == 0.0:
            return None

        return MatchResult(
            intent_key=intent.key,
            confidence=min(score, 1.0),
            matched_layer=matched_layer or "unknown",
            matched_keywords=matched_kw[:5],
            detected_language=language,
        )

    @staticmethod
    def _try_transliteration(
        normalized: str, intent: IntentDefinition
    ) -> tuple[float, str | None]:
        try:
            from indic_transliteration import sanscript
            from indic_transliteration.sanscript import transliterate
        except ImportError:
            return (0.0, None)

        try:
            deva = transliterate(normalized, sanscript.ITRANS, sanscript.DEVANAGARI)
        except Exception:
            return (0.0, None)

        for kw in intent.languages.get("hindi", []):
            if kw and kw in deva:
                return (WEIGHT_TRANSLITERATION, kw)
        return (0.0, None)

    @staticmethod
    def _try_fuzzy(
        tokens: list[str], all_keywords: list[str]
    ) -> tuple[float, str | None]:
        best_similarity = 0
        best_kw: str | None = None
        for token in tokens:
            if len(token) < 4:
                continue
            for kw in all_keywords:
                kw_norm = normalize(kw)
                if len(kw_norm) < 4:
                    continue
                similarity = fuzz.ratio(token, kw_norm)
                if similarity >= FUZZY_THRESHOLD and similarity > best_similarity:
                    best_similarity = similarity
                    best_kw = kw
        if best_kw is None:
            return (0.0, None)
        return (WEIGHT_FUZZY_MAX * (best_similarity / 100), best_kw)
