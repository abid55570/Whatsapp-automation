"""initial schema — all 16 tables

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-19 00:00:00

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ============================================================
    # users
    # ============================================================
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("full_name", sa.String(length=120), nullable=True),
        sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("phone", name="uq_users_phone"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_phone", "users", ["phone"])
    op.create_index("ix_users_email", "users", ["email"])

    # ============================================================
    # otp_codes
    # ============================================================
    op.create_table(
        "otp_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("code_hash", sa.String(length=255), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=False, server_default="signup"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("attempts", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_otp_codes"),
    )
    op.create_index("ix_otp_codes_phone", "otp_codes", ["phone"])

    # ============================================================
    # businesses
    # ============================================================
    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("business_type", sa.String(length=30), nullable=False, server_default="shop"),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="Asia/Kolkata"),
        sa.Column("languages", postgresql.ARRAY(sa.String(length=20)), nullable=False, server_default="{}"),
        sa.Column("whatsapp_phone_number_id", sa.String(length=50), nullable=True),
        sa.Column("whatsapp_business_account_id", sa.String(length=50), nullable=True),
        sa.Column("whatsapp_display_phone", sa.String(length=20), nullable=True),
        sa.Column("whatsapp_access_token", sa.String(length=500), nullable=True),
        sa.Column("onboarding_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], name="fk_businesses_owner_user_id_users", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_businesses"),
        sa.UniqueConstraint("whatsapp_phone_number_id", name="uq_businesses_whatsapp_phone_number_id"),
    )
    op.create_index("ix_businesses_owner_user_id", "businesses", ["owner_user_id"])

    # ============================================================
    # subscriptions
    # ============================================================
    op.create_table(
        "subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("plan", sa.String(length=20), nullable=False, server_default="trial"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="trialing"),
        sa.Column("ai_addon_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("trial_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trial_ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("current_period_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("canceled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("razorpay_customer_id", sa.String(length=100), nullable=True),
        sa.Column("razorpay_subscription_id", sa.String(length=100), nullable=True),
        sa.Column("conversations_included", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("conversations_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ai_replies_included", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ai_replies_used", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_subscriptions_business_id_businesses", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_subscriptions"),
        sa.UniqueConstraint("business_id", name="uq_subscriptions_business_id"),
    )
    op.create_index("ix_subscriptions_status", "subscriptions", ["status"])
    op.create_index("ix_subscriptions_trial_ends_at", "subscriptions", ["trial_ends_at"])
    op.create_index("ix_subscriptions_current_period_end", "subscriptions", ["current_period_end"])

    # ============================================================
    # contacts
    # ============================================================
    op.create_table(
        "contacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("whatsapp_phone", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("profile_picture_url", sa.String(length=500), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String(length=50)), nullable=False, server_default="{}"),
        sa.Column("opted_out", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_contacts_business_id_businesses", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_contacts"),
        sa.UniqueConstraint("business_id", "whatsapp_phone", name="uq_business_contact"),
    )
    op.create_index("ix_contacts_business_id", "contacts", ["business_id"])
    op.create_index("ix_contacts_whatsapp_phone", "contacts", ["whatsapp_phone"])
    op.create_index("ix_contacts_last_seen_at", "contacts", ["last_seen_at"])

    # ============================================================
    # conversations
    # ============================================================
    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meta_conversation_id", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=20), nullable=False, server_default="service"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_billable", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("meta_cost_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("unread_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_conversations_business_id_businesses", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], name="fk_conversations_contact_id_contacts", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_conversations"),
        sa.UniqueConstraint("meta_conversation_id", name="uq_conversations_meta_conversation_id"),
    )
    op.create_index("ix_conversations_business_id", "conversations", ["business_id"])
    op.create_index("ix_conversations_contact_id", "conversations", ["contact_id"])
    op.create_index("ix_conversations_category", "conversations", ["category"])
    op.create_index("ix_conversations_started_at", "conversations", ["started_at"])
    op.create_index("ix_conversations_last_message_at", "conversations", ["last_message_at"])

    # ============================================================
    # messages
    # ============================================================
    op.create_table(
        "messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("whatsapp_message_id", sa.String(length=100), nullable=True),
        sa.Column("direction", sa.String(length=10), nullable=False),
        sa.Column("type", sa.String(length=20), nullable=False, server_default="text"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="queued"),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("media_url", sa.String(length=1000), nullable=True),
        sa.Column("media_mime_type", sa.String(length=100), nullable=True),
        sa.Column("template_name", sa.String(length=100), nullable=True),
        sa.Column("is_auto_reply", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("matched_intent_key", sa.String(length=100), nullable=True),
        sa.Column("matched_confidence", sa.Float(), nullable=True),
        sa.Column("matched_layer", sa.String(length=30), nullable=True),
        sa.Column("detected_language", sa.String(length=20), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_reason", sa.String(length=500), nullable=True),
        sa.Column("extra_data", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], name="fk_messages_conversation_id_conversations", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_messages_business_id_businesses", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], name="fk_messages_contact_id_contacts", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_messages"),
        sa.UniqueConstraint("whatsapp_message_id", name="uq_messages_whatsapp_message_id"),
    )
    op.create_index("ix_messages_conversation_id", "messages", ["conversation_id"])
    op.create_index("ix_messages_business_id", "messages", ["business_id"])
    op.create_index("ix_messages_contact_id", "messages", ["contact_id"])
    op.create_index("ix_messages_whatsapp_message_id", "messages", ["whatsapp_message_id"])
    op.create_index("ix_messages_direction", "messages", ["direction"])
    op.create_index("ix_messages_matched_intent_key", "messages", ["matched_intent_key"])

    # ============================================================
    # business_intents
    # ============================================================
    op.create_table(
        "business_intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("intent_key", sa.String(length=100), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("reply_text", sa.Text(), nullable=False),
        sa.Column("media_url", sa.String(length=1000), nullable=True),
        sa.Column("custom_keywords", postgresql.ARRAY(sa.String(length=100)), nullable=False, server_default="{}"),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_business_intents_business_id_businesses", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_business_intents"),
        sa.UniqueConstraint("business_id", "intent_key", name="uq_business_intent_key"),
    )
    op.create_index("ix_business_intents_business_id", "business_intents", ["business_id"])
    op.create_index("ix_business_intents_intent_key", "business_intents", ["intent_key"])

    # ============================================================
    # webhook_events
    # ============================================================
    op.create_table(
        "webhook_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False),
        sa.Column("event_type", sa.String(length=100), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("headers", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("signature_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("processed", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_webhook_events_business_id_businesses", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_webhook_events"),
    )
    op.create_index("ix_webhook_events_business_id", "webhook_events", ["business_id"])
    op.create_index("ix_webhook_events_source", "webhook_events", ["source"])
    op.create_index("ix_webhook_events_event_type", "webhook_events", ["event_type"])
    op.create_index("ix_webhook_events_processed", "webhook_events", ["processed"])
    op.create_index("ix_webhook_events_received_at", "webhook_events", ["received_at"])

    # ============================================================
    # usage_logs
    # ============================================================
    op.create_table(
        "usage_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("usage_type", sa.String(length=30), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("meta_cost_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("charged_to_customer_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("billing_period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_usage_logs_business_id_businesses", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], name="fk_usage_logs_conversation_id_conversations", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_usage_logs"),
    )
    op.create_index("ix_usage_logs_business_id", "usage_logs", ["business_id"])
    op.create_index("ix_usage_logs_usage_type", "usage_logs", ["usage_type"])
    op.create_index("ix_usage_logs_billing_period_start", "usage_logs", ["billing_period_start"])

    # ============================================================
    # products
    # ============================================================
    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("price_paise", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("sku", sa.String(length=100), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("in_stock", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sheet_row_id", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_products_business_id_businesses", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_products"),
    )
    op.create_index("ix_products_business_id", "products", ["business_id"])

    # ============================================================
    # orders
    # ============================================================
    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_number", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="new"),
        sa.Column("payment_status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("total_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("delivery_address", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("razorpay_payment_link_id", sa.String(length=100), nullable=True),
        sa.Column("razorpay_payment_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_orders_business_id_businesses", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], name="fk_orders_contact_id_contacts", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_orders"),
        sa.UniqueConstraint("order_number", name="uq_orders_order_number"),
    )
    op.create_index("ix_orders_business_id", "orders", ["business_id"])
    op.create_index("ix_orders_contact_id", "orders", ["contact_id"])
    op.create_index("ix_orders_order_number", "orders", ["order_number"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_payment_status", "orders", ["payment_status"])

    # ============================================================
    # order_items
    # ============================================================
    op.create_table(
        "order_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("subtotal_paise", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], name="fk_order_items_order_id_orders", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], name="fk_order_items_product_id_products", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_order_items"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    # ============================================================
    # services
    # ============================================================
    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("price_paise", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sheet_row_id", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_services_business_id_businesses", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_services"),
    )
    op.create_index("ix_services_business_id", "services", ["business_id"])

    # ============================================================
    # bookings
    # ============================================================
    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contact_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("booking_number", sa.String(length=50), nullable=False),
        sa.Column("service_name", sa.String(length=200), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("reminder_sent", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_bookings_business_id_businesses", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["contact_id"], ["contacts.id"], name="fk_bookings_contact_id_contacts", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["service_id"], ["services.id"], name="fk_bookings_service_id_services", ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name="pk_bookings"),
        sa.UniqueConstraint("booking_number", name="uq_bookings_booking_number"),
    )
    op.create_index("ix_bookings_business_id", "bookings", ["business_id"])
    op.create_index("ix_bookings_contact_id", "bookings", ["contact_id"])
    op.create_index("ix_bookings_service_id", "bookings", ["service_id"])
    op.create_index("ix_bookings_booking_number", "bookings", ["booking_number"])
    op.create_index("ix_bookings_scheduled_at", "bookings", ["scheduled_at"])
    op.create_index("ix_bookings_status", "bookings", ["status"])

    # ============================================================
    # google_sheet_syncs
    # ============================================================
    op.create_table(
        "google_sheet_syncs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("sheet_url", sa.String(length=500), nullable=False),
        sa.Column("sheet_id", sa.String(length=100), nullable=False),
        sa.Column("sheet_tab_name", sa.String(length=100), nullable=False, server_default="Sheet1"),
        sa.Column("sheet_type", sa.String(length=20), nullable=False),
        sa.Column("auto_sync", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sync_interval_minutes", sa.Integer(), nullable=False, server_default="15"),
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_sync_status", sa.String(length=20), nullable=True),
        sa.Column("last_sync_error", sa.Text(), nullable=True),
        sa.Column("rows_synced", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["business_id"], ["businesses.id"], name="fk_google_sheet_syncs_business_id_businesses", ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name="pk_google_sheet_syncs"),
    )
    op.create_index("ix_google_sheet_syncs_business_id", "google_sheet_syncs", ["business_id"])
    op.create_index("ix_google_sheet_syncs_sheet_type", "google_sheet_syncs", ["sheet_type"])


def downgrade() -> None:
    # Drop in reverse dependency order
    op.drop_table("google_sheet_syncs")
    op.drop_table("bookings")
    op.drop_table("services")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("products")
    op.drop_table("usage_logs")
    op.drop_table("webhook_events")
    op.drop_table("business_intents")
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("contacts")
    op.drop_table("subscriptions")
    op.drop_table("businesses")
    op.drop_table("otp_codes")
    op.drop_table("users")
