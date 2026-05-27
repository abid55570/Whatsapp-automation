"""add is_superuser to users

Revision ID: 0007_superuser
Revises: 0006_enc_token
Create Date: 2026-05-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_superuser"
down_revision: Union[str, None] = "0006_enc_token"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index("ix_users_is_superuser", "users", ["is_superuser"])


def downgrade() -> None:
    op.drop_index("ix_users_is_superuser", table_name="users")
    op.drop_column("users", "is_superuser")
