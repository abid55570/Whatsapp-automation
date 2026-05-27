"""V1 API router — aggregates all v1 endpoint modules."""
from fastapi import APIRouter

from app.api.v1 import (
    account,
    admin,
    auth,
    businesses,
    conversations,
    dashboard,
    fulfillment,
    intents,
    invoices,
    orders,
    purchase_invoices,
    reports,
    sheets,
    subscriptions,
    webhooks,
)

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(account.router)
api_router.include_router(businesses.router)
api_router.include_router(intents.router)
api_router.include_router(conversations.router)
api_router.include_router(dashboard.router)
api_router.include_router(orders.router)
api_router.include_router(sheets.router)
api_router.include_router(fulfillment.router)
api_router.include_router(subscriptions.router)
api_router.include_router(invoices.router)
api_router.include_router(purchase_invoices.router)
api_router.include_router(reports.router)
api_router.include_router(webhooks.router)
api_router.include_router(admin.router)
