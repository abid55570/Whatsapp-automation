"""add fulfillment fields to orders + fulfillment_configs table

Revision ID: 0005_fulfillment
Revises: 0004_conv_state
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0005_fulfillment"
down_revision: Union[str, None] = "0004_conv_state"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---------- Order: new fields ----------
    op.add_column(
        "orders",
        sa.Column(
            "fulfillment_type",
            sa.String(length=20),
            nullable=False,
            server_default="pickup",
        ),
    )
    op.add_column(
        "orders",
        sa.Column("pickup_time", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("pickup_landmark", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column(
            "pickup_confirmed_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.add_column(
        "orders",
        sa.Column(
            "delivery_estimated_at", sa.DateTime(timezone=True), nullable=True
        ),
    )
    op.add_column(
        "orders",
        sa.Column("payment_method", sa.String(length=30), nullable=True),
    )
    op.create_index("ix_orders_fulfillment_type", "orders", ["fulfillment_type"])
    op.create_index("ix_orders_pickup_time", "orders", ["pickup_time"])

    # ---------- New table fulfillment_configs ----------
    op.create_table(
        "fulfillment_configs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("business_id", postgresql.UUID(as_uuid=True), nullable=False),
        # pickup
        sa.Column(
            "pickup_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("pickup_address", sa.String(length=500), nullable=True),
        sa.Column("pickup_landmark", sa.String(length=500), nullable=True),
        sa.Column(
            "pickup_hours_start",
            sa.String(length=5),
            nullable=False,
            server_default="10:00",
        ),
        sa.Column(
            "pickup_hours_end",
            sa.String(length=5),
            nullable=False,
            server_default="21:00",
        ),
        sa.Column(
            "pickup_closed_days",
            postgresql.ARRAY(sa.Integer()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "pickup_prep_strategy",
            sa.String(length=20),
            nullable=False,
            server_default="fixed",
        ),
        sa.Column(
            "pickup_fixed_minutes",
            sa.Integer(),
            nullable=False,
            server_default="30",
        ),
        sa.Column(
            "pickup_per_item_minutes",
            sa.Integer(),
            nullable=False,
            server_default="5",
        ),
        sa.Column(
            "pickup_slots",
            postgresql.ARRAY(sa.String(length=5)),
            nullable=False,
            server_default="{}",
        ),
        # delivery
        sa.Column(
            "delivery_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "delivery_fee_paise",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "delivery_minimum_order_paise",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "delivery_radius_km",
            sa.Integer(),
            nullable=False,
            server_default="3",
        ),
        sa.Column(
            "delivery_estimate_minutes",
            sa.Integer(),
            nullable=False,
            server_default="45",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["business_id"],
            ["businesses.id"],
            name="fk_fulfillment_configs_business_id_businesses",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_fulfillment_configs"),
        sa.UniqueConstraint(
            "business_id", name="uq_fulfillment_configs_business_id"
        ),
    )


def downgrade() -> None:
    op.drop_table("fulfillment_configs")
    op.drop_index("ix_orders_pickup_time", table_name="orders")
    op.drop_index("ix_orders_fulfillment_type", table_name="orders")
    op.drop_column("orders", "payment_method")
    op.drop_column("orders", "delivery_estimated_at")
    op.drop_column("orders", "pickup_confirmed_at")
    op.drop_column("orders", "pickup_landmark")
    op.drop_column("orders", "pickup_time")
    op.drop_column("orders", "fulfillment_type")
