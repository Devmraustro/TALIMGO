"""per-IP registration decision guards

Revision ID: b7e4f1a93c28
Revises: a3f8c2d94b17
Create Date: 2026-10-24 05:40:00

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "b7e4f1a93c28"
down_revision: str | None = "a3f8c2d94b17"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "registration_ip_guards",
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("ip"),
    )


def downgrade() -> None:
    op.drop_table("registration_ip_guards")
