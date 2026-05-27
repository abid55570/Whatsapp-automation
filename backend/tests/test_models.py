"""Verify all models are registered correctly with Base.metadata."""
from app.models import Base


def test_all_expected_tables_registered():
    """Every model class should produce a table in metadata."""
    expected = {
        "users",
        "otp_codes",
        "businesses",
        "subscriptions",
        "contacts",
        "conversations",
        "messages",
        "business_intents",
        "webhook_events",
        "usage_logs",
        "products",
        "orders",
        "order_items",
        "services",
        "bookings",
        "google_sheet_syncs",
    }
    actual = set(Base.metadata.tables.keys())
    missing = expected - actual
    assert not missing, f"Missing tables: {missing}"


def test_users_columns():
    """User table has required columns."""
    table = Base.metadata.tables["users"]
    columns = {col.name for col in table.columns}
    assert {"id", "phone", "email", "phone_verified", "is_active"} <= columns


def test_businesses_has_owner_fk():
    """Business links to users via owner_user_id."""
    table = Base.metadata.tables["businesses"]
    fk_columns = {fk.parent.name for fk in table.foreign_keys}
    assert "owner_user_id" in fk_columns


def test_subscription_is_one_to_one_with_business():
    """Subscription.business_id must be unique (1:1)."""
    table = Base.metadata.tables["subscriptions"]
    business_id_col = table.columns["business_id"]
    assert business_id_col.unique is True


def test_contact_uniqueness_per_business():
    """Each contact's (business_id, whatsapp_phone) is unique."""
    table = Base.metadata.tables["contacts"]
    constraint_names = {c.name for c in table.constraints if c.name}
    assert "uq_business_contact" in constraint_names


def test_message_has_required_indexes():
    """Messages must be indexed for fast inbox queries."""
    table = Base.metadata.tables["messages"]
    indexed_columns = {
        col.name for col in table.columns if col.index or col.primary_key
    }
    # business_id and conversation_id should be indexed for inbox queries
    assert "business_id" in indexed_columns
    assert "conversation_id" in indexed_columns


def test_conversation_meta_id_unique():
    """Meta's conversation ID must be unique to prevent duplicate billing."""
    table = Base.metadata.tables["conversations"]
    col = table.columns["meta_conversation_id"]
    assert col.unique is True


def test_order_number_unique():
    """Order numbers must be globally unique."""
    table = Base.metadata.tables["orders"]
    col = table.columns["order_number"]
    assert col.unique is True


def test_business_intent_unique_key_per_business():
    """A business cannot have duplicate intent_key entries."""
    table = Base.metadata.tables["business_intents"]
    constraint_names = {c.name for c in table.constraints if c.name}
    assert "uq_business_intent_key" in constraint_names
