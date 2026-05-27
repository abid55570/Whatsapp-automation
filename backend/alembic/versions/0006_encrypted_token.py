"""widen whatsapp_access_token column for Fernet ciphertext

Revision ID: 0006_enc_token
Revises: 0005_fulfillment
Create Date: 2026-05-20

Fernet ciphertext is ~30% larger than plaintext + base64-encoded.
Bump column from VARCHAR(500) → VARCHAR(2000) to fit encrypted values.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0006_enc_token"
down_revision: Union[str, None] = "0005_fulfillment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "businesses",
        "whatsapp_access_token",
        existing_type=sa.String(length=500),
        type_=sa.String(length=2000),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "businesses",
        "whatsapp_access_token",
        existing_type=sa.String(length=2000),
        type_=sa.String(length=500),
        existing_nullable=True,
    )
