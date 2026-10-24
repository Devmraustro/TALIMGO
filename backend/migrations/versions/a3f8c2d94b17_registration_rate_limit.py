"""per-IP registration rate limit attempts

Revision ID: a3f8c2d94b17
Revises: c4a7d9e12f60
Create Date: 2026-10-24 01:55:00

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "a3f8c2d94b17"
down_revision: str | None = "c4a7d9e12f60"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "registration_attempts",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_registration_attempts_ip"), "registration_attempts", ["ip"])
    op.create_index(
        op.f("ix_registration_attempts_attempted_at"), "registration_attempts", ["attempted_at"]
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_registration_attempts_attempted_at"), table_name="registration_attempts")
    op.drop_index(op.f("ix_registration_attempts_ip"), table_name="registration_attempts")
    op.drop_table("registration_attempts")
