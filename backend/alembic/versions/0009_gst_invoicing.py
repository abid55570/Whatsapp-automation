"""GST + invoicing — Business GST fields, Product HSN/rate, Invoice+lines, PurchaseInvoice

Revision ID: 0009_gst_invoicing
Revises: 0008_audit_indexes
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa


revision = "0009_gst_invoicing"
down_revision = "0008_audit_indexes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ---- Business GST fields ----
    op.add_column("businesses", sa.Column("gstin", sa.String(15), nullable=True))
    op.add_column("businesses", sa.Column("gst_state_code", sa.String(2), nullable=True))
    op.add_column(
        "businesses",
        sa.Column(
            "gst_scheme",
            sa.String(20),
            server_default="unregistered",
            nullable=False,
        ),
    )
    op.add_column("businesses", sa.Column("gst_composition_rate", sa.Integer, nullable=True))
    op.add_column("businesses", sa.Column("legal_name", sa.String(200), nullable=True))
    op.add_column("businesses", sa.Column("pan", sa.String(10), nullable=True))
    op.add_column("businesses", sa.Column("business_address_line1", sa.String(200), nullable=True))
    op.add_column("businesses", sa.Column("business_address_line2", sa.String(200), nullable=True))
    op.add_column("businesses", sa.Column("business_city", sa.String(100), nullable=True))
    op.add_column("businesses", sa.Column("business_state", sa.String(100), nullable=True))
    op.add_column("businesses", sa.Column("business_pincode", sa.String(6), nullable=True))
    op.add_column(
        "businesses",
        sa.Column("invoice_prefix", sa.String(6), server_default="INV", nullable=False),
    )
    op.add_column(
        "businesses",
        sa.Column("invoice_seq", sa.Integer, server_default="0", nullable=False),
    )
    op.add_column("businesses", sa.Column("current_invoice_fy", sa.String(7), nullable=True))
    op.add_column(
        "businesses",
        sa.Column("tax_pack_enabled", sa.Boolean, server_default="false", nullable=False),
    )
    op.create_index("ix_businesses_gstin", "businesses", ["gstin"], unique=False)

    # ---- Product GST fields ----
    op.add_column("products", sa.Column("hsn_code", sa.String(8), nullable=True))
    op.add_column(
        "products",
        sa.Column("gst_rate", sa.Integer, server_default="0", nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("is_service", sa.Boolean, server_default="false", nullable=False),
    )
    op.add_column(
        "products",
        sa.Column("unit", sa.String(10), server_default="pc", nullable=False),
    )

    # ---- invoices table ----
    op.create_table(
        "invoices",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "order_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("orders.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column(
            "contact_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("contacts.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        ),
        sa.Column("invoice_number", sa.String(20), nullable=False, index=True),
        sa.Column("invoice_date", sa.Date, nullable=False, index=True),
        sa.Column("fiscal_year", sa.String(7), nullable=False),
        sa.Column("cx_name", sa.String(200), nullable=True),
        sa.Column("cx_phone", sa.String(20), nullable=True),
        sa.Column("cx_gstin", sa.String(15), nullable=True),
        sa.Column("cx_address", sa.Text, nullable=True),
        sa.Column("cx_state_code", sa.String(2), nullable=True),
        sa.Column("subtotal_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("discount_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("taxable_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cgst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sgst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("igst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cess_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("round_off_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("place_of_supply", sa.String(100), nullable=True),
        sa.Column("reverse_charge", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("invoice_type", sa.String(20), nullable=False, server_default="b2c", index=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft", index=True),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancellation_reason", sa.Text, nullable=True),
        sa.Column("pdf_object_key", sa.String(500), nullable=True),
        sa.Column("pdf_url", sa.String(1000), nullable=True),
        sa.Column("razorpay_payment_link", sa.String(500), nullable=True),
        sa.Column("irn", sa.String(100), nullable=True),
        sa.Column("signed_qr_code", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("business_id", "fiscal_year", "invoice_number", name="uq_invoice_business_fy_number"),
        sa.UniqueConstraint("irn", name="uq_invoice_irn"),
    )

    # ---- invoice_lines table ----
    op.create_table(
        "invoice_lines",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "invoice_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("invoices.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("line_number", sa.Integer, nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("hsn_code", sa.String(8), nullable=True),
        sa.Column("quantity", sa.Numeric(precision=12, scale=3), nullable=False),
        sa.Column("unit", sa.String(10), nullable=False, server_default="pc"),
        sa.Column("rate_paise", sa.Integer, nullable=False),
        sa.Column("discount_pct", sa.Numeric(precision=5, scale=2), nullable=False, server_default="0"),
        sa.Column("gst_rate", sa.Integer, nullable=False, server_default="0"),
        sa.Column("taxable_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cgst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sgst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("igst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cess_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )

    # ---- purchase_invoices table ----
    op.create_table(
        "purchase_invoices",
        sa.Column("id", sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "business_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("supplier_name", sa.String(200), nullable=False),
        sa.Column("supplier_gstin", sa.String(15), nullable=True, index=True),
        sa.Column("supplier_state_code", sa.String(2), nullable=True),
        sa.Column("bill_number", sa.String(50), nullable=False),
        sa.Column("bill_date", sa.Date, nullable=False, index=True),
        sa.Column("taxable_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cgst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("sgst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("igst_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("cess_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_paise", sa.Integer, nullable=False, server_default="0"),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("is_capital_goods", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("is_itc_eligible", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="recorded", index=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("purchase_invoices")
    op.drop_table("invoice_lines")
    op.drop_table("invoices")

    op.drop_column("products", "unit")
    op.drop_column("products", "is_service")
    op.drop_column("products", "gst_rate")
    op.drop_column("products", "hsn_code")

    op.drop_index("ix_businesses_gstin", table_name="businesses")
    op.drop_column("businesses", "tax_pack_enabled")
    op.drop_column("businesses", "current_invoice_fy")
    op.drop_column("businesses", "invoice_seq")
    op.drop_column("businesses", "invoice_prefix")
    op.drop_column("businesses", "business_pincode")
    op.drop_column("businesses", "business_state")
    op.drop_column("businesses", "business_city")
    op.drop_column("businesses", "business_address_line2")
    op.drop_column("businesses", "business_address_line1")
    op.drop_column("businesses", "pan")
    op.drop_column("businesses", "legal_name")
    op.drop_column("businesses", "gst_composition_rate")
    op.drop_column("businesses", "gst_scheme")
    op.drop_column("businesses", "gst_state_code")
    op.drop_column("businesses", "gstin")
