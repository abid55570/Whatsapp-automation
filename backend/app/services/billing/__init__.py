"""Billing service — trial setup, plan upgrades, Razorpay integration."""
from app.services.billing.status import (
    business_can_send,
    freeze_expired_trials,
    is_active,
    is_frozen,
)
from app.services.billing.trial import create_trial_subscription
from app.services.billing.usage import (
    PLAN_LIMITS,
    conversation_limit_for_plan,
    has_ai_quota,
    has_conversation_quota,
    increment_ai_usage,
    increment_conversation_usage,
    reset_monthly_usage,
)

__all__ = [
    "PLAN_LIMITS",
    "business_can_send",
    "conversation_limit_for_plan",
    "create_trial_subscription",
    "freeze_expired_trials",
    "has_ai_quota",
    "has_conversation_quota",
    "increment_ai_usage",
    "increment_conversation_usage",
    "is_active",
    "is_frozen",
    "reset_monthly_usage",
]
