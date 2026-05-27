"""Per-business intent configuration (toggle + customize global intents)."""
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.business import Business


class BusinessIntent(Base, UUIDMixin, TimestampMixin):
    """A business's customization of a global intent.

    Global intent DEFINITIONS (keywords, language patterns) live in
    `data/intents/*.json` and are loaded into memory at startup.
    This table only stores the per-business toggle + custom reply text.
    """

    __tablename__ = "business_intents"
    __table_args__ = (
        UniqueConstraint(
            "business_id", "intent_key", name="uq_business_intent_key"
        ),
    )

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    intent_key: Mapped[str] = mapped_column(String(100), index=True, nullable=False)

    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Default reply (English / fallback)
    reply_text: Mapped[str] = mapped_column(Text, nullable=False)
    # Per-language overrides keyed by locale code:
    # {"hi": "हमारी कीमतें...", "hinglish": "Hamare rates...", "bn": "...", "ur": "...", "bho": "..."}
    reply_translations: Mapped[dict[str, str]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    media_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Owner can extend the built-in keyword bank
    custom_keywords: Mapped[list[str]] = mapped_column(
        ARRAY(String(100)), default=list, nullable=False
    )

    # Higher priority intents are checked first when multiple match
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="intents")
