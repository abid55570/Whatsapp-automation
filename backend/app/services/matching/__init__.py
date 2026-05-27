"""Multi-layer intent matching engine for WhatsApp messages."""
from pathlib import Path

from app.services.matching.engine import MatchingEngine
from app.services.matching.intent_loader import IntentLibrary
from app.services.matching.schemas import IntentDefinition, MatchResult

# Default intents directory (backend/data/intents/)
_DEFAULT_INTENTS_DIR = Path(__file__).resolve().parents[3] / "data" / "intents"

_engine: MatchingEngine | None = None


def get_matching_engine(intents_dir: Path | None = None) -> MatchingEngine:
    """Return the singleton matching engine.

    On first call, loads all JSON intents from `intents_dir`
    (defaults to `backend/data/intents/`).
    """
    global _engine
    if _engine is None:
        directory = intents_dir or _DEFAULT_INTENTS_DIR
        library = IntentLibrary(directory)
        _engine = MatchingEngine(library)
    return _engine


def reset_matching_engine() -> None:
    """Reset the singleton (for tests)."""
    global _engine
    _engine = None


__all__ = [
    "IntentDefinition",
    "IntentLibrary",
    "MatchResult",
    "MatchingEngine",
    "get_matching_engine",
    "reset_matching_engine",
]
