"""add reply_translations JSONB to business_intents

Revision ID: 0003_intent_translations
Revises: 0002_user_lang
Create Date: 2026-05-20

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_intent_translations"
down_revision: Union[str, None] = "0002_user_lang"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "business_intents",
        sa.Column(
            "reply_translations",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
    )


def downgrade() -> None:
    op.drop_column("business_intents", "reply_translations")
