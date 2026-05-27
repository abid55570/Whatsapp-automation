"""Google Sheets sync configuration."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import SheetType

if TYPE_CHECKING:
    from app.models.business import Business


class GoogleSheetSync(Base, UUIDMixin, TimestampMixin):
    """Sync config for one Google Sheet → DB pipeline."""

    __tablename__ = "google_sheet_syncs"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    sheet_url: Mapped[str] = mapped_column(String(500), nullable=False)
    sheet_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sheet_tab_name: Mapped[str] = mapped_column(
        String(100), default="Sheet1", nullable=False
    )

    sheet_type: Mapped[SheetType] = mapped_column(
        SQLEnum(SheetType, native_enum=False, length=20),
        index=True,
        nullable=False,
    )

    auto_sync: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sync_interval_minutes: Mapped[int] = mapped_column(
        Integer, default=15, nullable=False
    )

    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_sync_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_sync_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    rows_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="sheet_syncs")
