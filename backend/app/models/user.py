"""User account and OTP code models."""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import OTPPurpose

if TYPE_CHECKING:
    from app.models.business import Business


class User(Base, UUIDMixin, TimestampMixin):
    """Business owner account. Phone is the primary identifier."""

    __tablename__ = "users"

    phone: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )
    full_name: Mapped[str | None] = mapped_column(String(120), nullable=True)

    phone_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Platform UI language preference (en | hi | hinglish | bn | ur | bho)
    preferred_language: Mapped[str] = mapped_column(
        String(20), default="en", nullable=False
    )

    # Relationships — `select` (not selectin) avoids an extra query on every
    # authenticated request via get_current_user. Endpoints that need the
    # business should `.options(selectinload(User.businesses))` explicitly.
    businesses: Mapped[list["Business"]] = relationship(
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="select",
    )


class OTPCode(Base, UUIDMixin, TimestampMixin):
    """Hashed OTP for phone verification/login. No passwords."""

    __tablename__ = "otp_codes"

    phone: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    purpose: Mapped[OTPPurpose] = mapped_column(
        SQLEnum(OTPPurpose, native_enum=False, length=20),
        default=OTPPurpose.SIGNUP,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
