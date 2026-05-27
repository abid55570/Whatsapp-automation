"""Import all models so they're registered with Base.metadata.

This module is imported by `alembic/env.py` so autogenerate detects
every table.
"""
from app.models.base import Base
from app.models.booking import Booking, Service
from app.models.business import Business
from app.models.contact import Contact
from app.models.conversation import Conversation, Message
from app.models.fulfillment import FulfillmentConfig
from app.models.intent import BusinessIntent
from app.models.invoice import Invoice, InvoiceLine
from app.models.order import Order, OrderItem, Product
from app.models.purchase_invoice import PurchaseInvoice
from app.models.sheet import GoogleSheetSync
from app.models.subscription import Subscription
from app.models.usage import UsageLog
from app.models.user import OTPCode, User
from app.models.webhook import WebhookEvent

__all__ = [
    "Base",
    "Booking",
    "Business",
    "BusinessIntent",
    "Contact",
    "Conversation",
    "FulfillmentConfig",
    "GoogleSheetSync",
    "Invoice",
    "InvoiceLine",
    "Message",
    "OTPCode",
    "Order",
    "OrderItem",
    "Product",
    "PurchaseInvoice",
    "Service",
    "Subscription",
    "UsageLog",
    "User",
    "WebhookEvent",
]
