"""authenticated write rate limit counters

Revision ID: c4a7d9e12f60
Revises: 9b2e4f6a8c10
Create Date: 2026-10-11 01:45:00

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "c4a7d9e12f60"
down_revision: str | None = "9b2e4f6a8c10"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("write_rate_window", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.add_column(
            sa.Column("write_rate_count", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("write_rate_count")
        batch_op.drop_column("write_rate_window")
