"""GST safety nets: invoice immutability, purchase bill uniqueness, restrict cascade

Revision ID: 0010_gst_safety
Revises: 0009_gst_invoicing
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa


revision = "0010_gst_safety"
down_revision = "0009_gst_invoicing"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Prevent duplicate supplier bills per (business, supplier_gstin, bill_number)
    #    Postgres allows multiple NULLs in unique constraints, so unregistered
    #    suppliers can repeat bill numbers — that's acceptable.
    op.create_index(
        "uq_purchase_invoice_business_supplier_bill",
        "purchase_invoices",
        ["business_id", "supplier_gstin", "bill_number"],
        unique=True,
        postgresql_where=sa.text("supplier_gstin IS NOT NULL"),
    )

    # 2. Index purchase invoices by bill_date for monthly purchase register queries
    op.create_index(
        "ix_purchase_invoices_business_id_bill_date",
        "purchase_invoices",
        ["business_id", "bill_date"],
        unique=False,
    )

    # 3. Add Postgres-level check: invoice line quantity > 0
    op.create_check_constraint(
        "ck_invoice_lines_qty_positive",
        "invoice_lines",
        "quantity > 0",
    )

    # 4. Add Postgres-level check: invoice total >= 0
    op.create_check_constraint(
        "ck_invoices_total_non_negative",
        "invoices",
        "total_paise >= 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_invoices_total_non_negative", "invoices", type_="check")
    op.drop_constraint(
        "ck_invoice_lines_qty_positive", "invoice_lines", type_="check"
    )
    op.drop_index(
        "ix_purchase_invoices_business_id_bill_date", table_name="purchase_invoices"
    )
    op.drop_index(
        "uq_purchase_invoice_business_supplier_bill",
        table_name="purchase_invoices",
    )
