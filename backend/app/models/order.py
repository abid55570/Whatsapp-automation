"""Product, Order, and OrderItem (Growth-plan feature)."""
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.models.enums import (
    FulfillmentType,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
)

if TYPE_CHECKING:
    from app.models.business import Business
    from app.models.contact import Contact


class Product(Base, UUIDMixin, TimestampMixin):
    """A product (menu item, retail SKU, etc.)."""

    __tablename__ = "products"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    sku: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # ---------- GST fields ----------
    hsn_code: Mapped[str | None] = mapped_column(String(8), nullable=True)
    gst_rate: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_service: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    unit: Mapped[str] = mapped_column(String(10), default="pc", nullable=False)

    # Tracks origin row if synced from Google Sheet
    sheet_row_id: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="products")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")


class Order(Base, UUIDMixin, TimestampMixin):
    """An order placed by a customer through WhatsApp."""

    __tablename__ = "orders"

    business_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("contacts.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    order_number: Mapped[str] = mapped_column(
        String(50), unique=True, index=True, nullable=False
    )

    status: Mapped[OrderStatus] = mapped_column(
        SQLEnum(OrderStatus, native_enum=False, length=20),
        default=OrderStatus.NEW,
        index=True,
        nullable=False,
    )
    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus, native_enum=False, length=20),
        default=PaymentStatus.PENDING,
        index=True,
        nullable=False,
    )

    total_paise: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    items_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ---------- Fulfillment ----------
    fulfillment_type: Mapped[FulfillmentType] = mapped_column(
        SQLEnum(FulfillmentType, native_enum=False, length=20),
        default=FulfillmentType.PICKUP,
        index=True,
        nullable=False,
    )

    # Pickup-specific
    pickup_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    pickup_landmark: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pickup_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Delivery-specific
    delivery_address: Mapped[dict[str, Any]] = mapped_column(
        JSONB, default=dict, nullable=False
    )
    delivery_estimated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ---------- Payment ----------
    payment_method: Mapped[PaymentMethod | None] = mapped_column(
        SQLEnum(PaymentMethod, native_enum=False, length=30),
        nullable=True,
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    razorpay_payment_link_id: Mapped[str | None] = mapped_column(
        String(100), index=True, nullable=True
    )
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    business: Mapped["Business"] = relationship(back_populates="orders")
    contact: Mapped["Contact"] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(Base, UUIDMixin, TimestampMixin):
    """Single line item within an order."""

    __tablename__ = "order_items"

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("products.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Denormalized so we keep history even if product is deleted
    product_name: Mapped[str] = mapped_column(String(200), nullable=False)
    price_paise: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    subtotal_paise: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product | None"] = relationship(back_populates="order_items")
