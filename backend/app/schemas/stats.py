"""Dashboard stats schema."""
from datetime import datetime

from pydantic import BaseModel, Field


class DashboardStats(BaseModel):
    """Aggregated stats for the dashboard home page."""

    period_days: int
    period_start: datetime
    period_end: datetime

    total_messages: int = 0
    inbound_messages: int = 0
    outbound_messages: int = 0

    auto_replied_count: int = 0
    needs_attention_count: int = 0

    unique_contacts: int = 0
    active_conversations: int = 0
    conversations_today: int = 0

    auto_reply_rate: float = 0.0  # percentage
    matched_languages: dict[str, int] = Field(default_factory=dict)
