"""All enum types used across models.

Stored as strings (`native_enum=False`) for easy migrations.
"""
import enum


class BusinessType(str, enum.Enum):
    RESTAURANT = "restaurant"
    SALON = "salon"
    CLINIC = "clinic"
    SHOP = "shop"
    GYM = "gym"
    COACHING = "coaching"
    AGENCY = "agency"
    D2C = "d2c"
    HOME_BUSINESS = "home_business"
    CUSTOM = "custom"


class Language(str, enum.Enum):
    """Languages we support out-of-the-box (V1)."""

    ENGLISH = "english"
    HINDI = "hindi"               # Devanagari script
    HINGLISH = "hinglish"         # Romanized Hindi
    URDU = "urdu"
    BHOJPURI = "bhojpuri"
    BENGALI = "bengali"


class PlanType(str, enum.Enum):
    TRIAL = "trial"
    STARTER = "starter"      # ₹399
    GROWTH = "growth"        # ₹999
    PRO = "pro"              # ₹1999


class SubscriptionStatus(str, enum.Enum):
    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    FROZEN = "frozen"        # trial expired without payment


class ConversationCategory(str, enum.Enum):
    """Meta's billing categories."""

    SERVICE = "service"
    MARKETING = "marketing"
    UTILITY = "utility"
    AUTHENTICATION = "authentication"
    UNKNOWN = "unknown"


class ConversationStatus(str, enum.Enum):
    OPEN = "open"
    CLOSED = "closed"


class MessageDirection(str, enum.Enum):
    INBOUND = "inbound"      # from customer to business
    OUTBOUND = "outbound"    # from business to customer


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    STICKER = "sticker"
    LOCATION = "location"
    CONTACTS = "contacts"
    TEMPLATE = "template"
    INTERACTIVE = "interactive"
    BUTTON = "button"
    UNKNOWN = "unknown"


class MessageStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class OTPPurpose(str, enum.Enum):
    SIGNUP = "signup"
    LOGIN = "login"
    PHONE_CHANGE = "phone_change"


class OrderStatus(str, enum.Enum):
    NEW = "new"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    PICKED_UP = "picked_up"
    PACKED = "packed"
    OUT_FOR_DELIVERY = "out_for_delivery"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELED = "canceled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class FulfillmentType(str, enum.Enum):
    PICKUP = "pickup"
    DELIVERY = "delivery"
    DINE_IN = "dine_in"


class PaymentMethod(str, enum.Enum):
    UPI = "upi"
    CARD = "card"
    NET_BANKING = "net_banking"
    CASH_ON_PICKUP = "cash_on_pickup"
    CASH_ON_DELIVERY = "cash_on_delivery"
    ONLINE = "online"


class PickupPrepStrategy(str, enum.Enum):
    FIXED = "fixed"
    PER_ITEM = "per_item"
    SLOTS = "slots"
    AUTO = "auto"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELED = "canceled"
    NO_SHOW = "no_show"


class UsageType(str, enum.Enum):
    CONV_SERVICE = "conv_service"
    CONV_UTILITY = "conv_utility"
    CONV_MARKETING = "conv_marketing"
    CONV_AUTH = "conv_auth"
    AI_REPLY = "ai_reply"


class SheetType(str, enum.Enum):
    FAQS = "faqs"
    PRODUCTS = "products"
    SERVICES = "services"
    CUSTOMERS = "customers"


# ============================================================
# GST / Invoicing
# ============================================================


class GstScheme(str, enum.Enum):
    """Business's GST registration status."""

    UNREGISTERED = "unregistered"   # < ₹20L turnover, no GSTIN
    REGULAR = "regular"             # standard registration
    COMPOSITION = "composition"     # flat rate, no ITC, "Bill of Supply" format


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    ISSUED = "issued"
    PAID = "paid"
    CANCELLED = "cancelled"


class InvoiceType(str, enum.Enum):
    B2C = "b2c"                       # consumer, no buyer GSTIN
    B2B = "b2b"                       # business buyer with GSTIN → ITC eligible
    B2C_LARGE = "b2c_large"           # B2C > ₹2.5L (separate GSTR-1 section)
    EXPORT = "export"                 # out of India (0% IGST)
    BILL_OF_SUPPLY = "bill_of_supply" # composition scheme / exempt goods


class PurchaseInvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    RECORDED = "recorded"
    CANCELLED = "cancelled"
