"""Add hot-path indexes + case-insensitive email uniqueness

Revision ID: 0008_audit_indexes
Revises: 0007_superuser
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa


revision = "0008_audit_indexes"
down_revision = "0007_superuser"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Index hot-path columns flagged in audit
    op.create_index(
        "ix_orders_razorpay_payment_link_id",
        "orders",
        ["razorpay_payment_link_id"],
        unique=False,
    )
    op.create_index(
        "ix_conversations_status",
        "conversations",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_orders_business_id_status",
        "orders",
        ["business_id", "status"],
        unique=False,
    )

    # Case-insensitive unique email — replaces SQL-level uniqueness with
    # a functional index so "User@A.com" and "user@a.com" collide.
    op.drop_constraint("uq_users_email", "users", type_="unique")
    op.create_index(
        "uq_users_email_lower",
        "users",
        [sa.text("LOWER(email)")],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_users_email_lower", table_name="users")
    op.create_unique_constraint("uq_users_email", "users", ["email"])
    op.drop_index("ix_orders_business_id_status", table_name="orders")
    op.drop_index("ix_conversations_status", table_name="conversations")
    op.drop_index("ix_orders_razorpay_payment_link_id", table_name="orders")
