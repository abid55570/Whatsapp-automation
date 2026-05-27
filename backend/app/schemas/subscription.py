"""Subscription response schema."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionResponse(BaseModel):
    """Public view of a Subscription. Internal fields (Razorpay IDs) excluded."""

    model_config = ConfigDict(from_attributes=True)

    plan: str  # trial | starter | growth | pro
    status: str  # trialing | active | past_due | canceled | frozen
    ai_addon_enabled: bool

    # Trial window
    trial_started_at: datetime | None = None
    trial_ends_at: datetime | None = None
    days_remaining_in_trial: int | None = None

    # Billing cycle (paid plans)
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None

    # Usage counters
    conversations_included: int
    conversations_used: int
    conversations_remaining: int = 0

    ai_replies_included: int
    ai_replies_used: int
    ai_replies_remaining: int = 0
