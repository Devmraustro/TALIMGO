"""practice session target and lifecycle

Revision ID: 8f1c2d4e6a70
Revises: 1236a568ff99
Create Date: 2026-10-11 00:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "8f1c2d4e6a70"
down_revision: str | None = "1236a568ff99"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("practice_sessions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("target_items", sa.Integer(), nullable=False, server_default="0"))
        batch_op.add_column(sa.Column("item_ids", sa.JSON(), nullable=False, server_default="[]"))
        batch_op.add_column(sa.Column("abandoned_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("practice_sessions", schema=None) as batch_op:
        batch_op.drop_column("abandoned_at")
        batch_op.drop_column("item_ids")
        batch_op.drop_column("target_items")
