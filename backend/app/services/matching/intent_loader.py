"""Load intent definitions from JSON files into an in-memory library."""
import json
import logging
from pathlib import Path

from app.services.matching.schemas import IntentDefinition

logger = logging.getLogger(__name__)


class IntentLibrary:
    """In-memory store of all loaded global intents."""

    def __init__(self, intents_dir: Path):
        self._intents: dict[str, IntentDefinition] = {}
        self._load(intents_dir)

    def _load(self, intents_dir: Path) -> None:
        if not intents_dir.exists():
            logger.warning("Intents directory does not exist: %s", intents_dir)
            return

        for json_file in sorted(intents_dir.glob("*.json")):
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))
                intent = IntentDefinition(**data)
                if intent.key in self._intents:
                    logger.warning("Duplicate intent key: %s", intent.key)
                self._intents[intent.key] = intent
            except (json.JSONDecodeError, ValueError, TypeError) as exc:
                logger.error("Failed to load intent %s: %s", json_file.name, exc)

    def get(self, key: str) -> IntentDefinition | None:
        return self._intents.get(key)

    def list_keys(self) -> list[str]:
        return list(self._intents.keys())

    def list_all(self) -> list[IntentDefinition]:
        return list(self._intents.values())

    def count(self) -> int:
        return len(self._intents)
