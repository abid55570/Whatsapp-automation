"""Schemas for SaaS subscription upgrade endpoints."""
from pydantic import BaseModel, Field

from app.models.enums import PlanType


class UpgradeRequest(BaseModel):
    plan: PlanType = Field(..., description="Target plan to upgrade to")


class UpgradeResponse(BaseModel):
    razorpay_subscription_id: str
    short_url: str
    status: str
    plan: str
