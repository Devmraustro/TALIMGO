"""plan schedule dates

Revision ID: 9b2e4f6a8c10
Revises: 8f1c2d4e6a70
Create Date: 2026-10-11 00:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "9b2e4f6a8c10"
down_revision: str | None = "8f1c2d4e6a70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("plans", schema=None) as batch_op:
        batch_op.add_column(sa.Column("starts_on", sa.Date(), nullable=True))
    with op.batch_alter_table("plan_items", schema=None) as batch_op:
        batch_op.add_column(sa.Column("scheduled_day", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.create_index("ix_plan_items_scheduled_day", ["scheduled_day"], unique=False)
    # Existing plans start today; the next re-plan (or a plan regeneration) fills in the day offsets.
    op.execute("UPDATE plans SET starts_on = CURRENT_DATE WHERE starts_on IS NULL")
    # Every plan must have an anchor, so the column is NOT NULL once the backfill is done. Declared
    # here (and mirrored in the model) because a nullable anchor would let the calendar drift.
    with op.batch_alter_table("plans", schema=None) as batch_op:
        batch_op.alter_column("starts_on", existing_type=sa.Date(), nullable=False)


def downgrade() -> None:
    with op.batch_alter_table("plan_items", schema=None) as batch_op:
        batch_op.drop_index("ix_plan_items_scheduled_day")
        batch_op.drop_column("completed_at")
        batch_op.drop_column("scheduled_day")
    with op.batch_alter_table("plans", schema=None) as batch_op:
        batch_op.drop_column("starts_on")
