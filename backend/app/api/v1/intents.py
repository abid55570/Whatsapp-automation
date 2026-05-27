"""Global intent catalog (read-only) — for the picker UI."""
from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models import User
from app.schemas.intent import GlobalIntentResponse
from app.services.matching import get_matching_engine

router = APIRouter(prefix="/intents", tags=["intents"])


@router.get("", response_model=list[GlobalIntentResponse])
async def list_global_intents(
    _user: User = Depends(get_current_user),
) -> list[GlobalIntentResponse]:
    """Return all available global intents.

    Returned info lets the picker UI render rich cards with:
      - intent name + description
      - language coverage badges (English, Hindi, etc.)
      - keyword counts per language
      - default reply template (pre-filled in editor)
      - emoji preview icons
    """
    engine = get_matching_engine()
    return [
        GlobalIntentResponse(
            key=i.key,
            name=i.name,
            description=i.description,
            default_reply_template=i.default_reply_template,
            category=i.category,
            priority=i.priority,
            languages_covered=list(i.languages.keys()),
            keyword_counts={
                lang: len(kws) for lang, kws in i.languages.items()
            },
            emoji_preview=i.emojis[:3],
        )
        for i in engine.library.list_all()
    ]
