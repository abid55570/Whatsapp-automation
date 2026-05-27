"""AI add-on: smart reply fallback + multi-lang translation."""
from app.services.ai.client import AIError, generate
from app.services.ai.smart_reply import generate_smart_reply
from app.services.ai.translator import translate_to

__all__ = [
    "AIError",
    "generate",
    "generate_smart_reply",
    "translate_to",
]
