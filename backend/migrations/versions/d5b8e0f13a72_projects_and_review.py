"""projects, project submissions, flashcard states, practice session mode

Adds the BUILD step (authored project briefs + learner submissions, ADR 0008) and the spaced
review study data (flashcard schedules + the practice session mode, ADR 0009). All additions are
new tables plus one column with a server default, so existing rows stay valid untouched.

Revision ID: d5b8e0f13a72
Revises: b7e4f1a93c28
Create Date: 2026-10-27 00:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d5b8e0f13a72"
down_revision: str | None = "b7e4f1a93c28"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.String(length=80), nullable=False),
        sa.Column("path_id", sa.String(length=64), nullable=False),
        sa.Column("objective_id", sa.String(length=80), nullable=False),
        sa.Column("title_en", sa.String(length=200), nullable=False),
        sa.Column("title_ar", sa.String(length=200), nullable=False),
        sa.Column("brief_md_en", sa.Text(), nullable=False),
        sa.Column("brief_md_ar", sa.Text(), nullable=False),
        sa.Column("rubric", sa.JSON(), nullable=False),
        sa.Column("min_artifact_chars", sa.Integer(), nullable=False),
        sa.Column("min_reflection_chars", sa.Integer(), nullable=False),
        sa.Column("est_minutes", sa.Integer(), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["objective_id"], ["objectives.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_projects_objective_id", "projects", ["objective_id"])
    op.create_index("ix_projects_path_id", "projects", ["path_id"])

    op.create_table(
        "project_submissions",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.String(length=64), nullable=True),
        sa.Column("plan_item_id", sa.String(length=64), nullable=True),
        sa.Column("project_id", sa.String(length=80), nullable=False),
        sa.Column("objective_id", sa.String(length=80), nullable=False),
        sa.Column("artifact_text", sa.Text(), nullable=False),
        sa.Column("reflection_text", sa.Text(), nullable=False),
        sa.Column("rubric_checks", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("met_criteria", sa.JSON(), nullable=False),
        sa.Column("missing_criteria", sa.JSON(), nullable=False),
        sa.Column("evidence_recorded", sa.Boolean(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["goal_id"], ["goals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_submissions_objective_id", "project_submissions", ["objective_id"])
    op.create_index("ix_project_submissions_project_id", "project_submissions", ["project_id"])
    op.create_index("ix_project_submissions_user_id", "project_submissions", ["user_id"])

    op.create_table(
        "flashcard_states",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("item_id", sa.String(length=80), nullable=False),
        sa.Column("objective_id", sa.String(length=80), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("interval_days", sa.Float(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_rating", sa.String(length=10), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "item_id", name="uq_flashcard_user_item"),
    )
    op.create_index("ix_flashcard_states_item_id", "flashcard_states", ["item_id"])
    op.create_index("ix_flashcard_states_objective_id", "flashcard_states", ["objective_id"])
    op.create_index("ix_flashcard_states_user_id", "flashcard_states", ["user_id"])

    with op.batch_alter_table("practice_sessions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("mode", sa.String(length=20), nullable=False, server_default="practice")
        )


def downgrade() -> None:
    with op.batch_alter_table("practice_sessions", schema=None) as batch_op:
        batch_op.drop_column("mode")
    op.drop_index("ix_flashcard_states_user_id", table_name="flashcard_states")
    op.drop_index("ix_flashcard_states_objective_id", table_name="flashcard_states")
    op.drop_index("ix_flashcard_states_item_id", table_name="flashcard_states")
    op.drop_table("flashcard_states")
    op.drop_index("ix_project_submissions_user_id", table_name="project_submissions")
    op.drop_index("ix_project_submissions_project_id", table_name="project_submissions")
    op.drop_index("ix_project_submissions_objective_id", table_name="project_submissions")
    op.drop_table("project_submissions")
    op.drop_index("ix_projects_path_id", table_name="projects")
    op.drop_index("ix_projects_objective_id", table_name="projects")
    op.drop_table("projects")
