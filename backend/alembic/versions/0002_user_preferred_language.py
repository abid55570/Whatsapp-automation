"""add preferred_language to users

Revision ID: 0002_user_lang
Revises: 0001_initial
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_user_lang"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "preferred_language",
            sa.String(length=20),
            nullable=False,
            server_default="en",
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "preferred_language")
