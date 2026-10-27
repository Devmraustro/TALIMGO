"""Project work — the BUILD step of the learning cycle (ADR 0008).

Rules kept here, deliberately mechanical:

  * Acceptance is **deterministic**: every required rubric criterion attested by the learner, an
    artifact of at least the authored minimum length, and a reflection of at least the authored
    minimum. No model judges project work, and the checklist is the learner's own attestation —
    the interface says exactly that (``self_checked`` in the result).
  * A ``needs_work`` submission records **no evidence**: it is formative feedback on completeness,
    not a demonstrated failure at the objective.
  * An ``accepted`` submission records **one** ``project`` success evidence record — the first
    acceptance only, per (learner, project). Resubmitting accepted work cannot farm the three
    unassisted successes the mastery model requires; later acceptances are kept as portfolio
    history with ``evidence_recorded=False``.
  * Ownership is the practice chain: goal and plan item are resolved with the same resolver
    practice sessions use, so foreign identifiers are 404 and internal inconsistencies 409.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session as DbSession

from app.curriculum.registry import localised
from app.models import Evidence, Objective, Project, ProjectSubmission, User
from app.services.assessment import _resolve_practice_context, plan_item_for_user
from app.services.progress import recompute_mastery, record_evidence
from app.utils import utcnow


class ProjectError(RuntimeError):
    """The requested object is unknown, or belongs to somebody else (reported as 404)."""


class ProjectConflict(ProjectError):
    """The request is well-formed but contradicts recorded state (reported as 409)."""


def evaluate_submission(
    project: Project, *, artifact_text: str, reflection_text: str, rubric_checks: dict
) -> tuple[str, list[str], list[str]]:
    """``(status, met, missing)`` — stable criterion ids; minima use ``artifact:``/``reflection:`` codes."""
    met: list[str] = []
    missing: list[str] = []
    for criterion in project.rubric or []:
        criterion_id = str(criterion.get("id", ""))
        if not criterion_id:
            continue
        checked = rubric_checks.get(criterion_id) is True
        if checked:
            met.append(criterion_id)
        elif criterion.get("required", True):
            missing.append(criterion_id)
    if len(artifact_text.strip()) < project.min_artifact_chars:
        missing.append("artifact:minimum_length")
    if len(reflection_text.strip()) < project.min_reflection_chars:
        missing.append("reflection:minimum_length")
    return ("accepted" if not missing else "needs_work", met, missing)


def submit_project(
    db: DbSession,
    user: User,
    *,
    project_id: str,
    artifact_text: str,
    reflection_text: str,
    rubric_checks: dict,
    goal_id: str | None = None,
    plan_item_id: str | None = None,
    now: datetime | None = None,
) -> ProjectSubmission:
    project = db.get(Project, project_id)
    if project is None:
        raise ProjectError("Unknown project.")
    objective = db.get(Objective, project.objective_id)
    if objective is None:  # curriculum integrity makes this unreachable; refuse rather than guess
        raise ProjectError("Unknown project.")

    # The exact ownership chain practice uses: the goal is the learner's and on this path, the
    # plan item belongs to the learner's plan for this objective (AssessmentError→404 upstream).
    resolved_goal_id = _resolve_practice_context(
        db, user, objective=objective, goal_id=goal_id, plan_item_id=plan_item_id
    )

    status, met, missing = evaluate_submission(
        project,
        artifact_text=artifact_text,
        reflection_text=reflection_text,
        rubric_checks=rubric_checks,
    )
    moment = now or utcnow()
    submission = ProjectSubmission(
        user_id=user.id,
        goal_id=resolved_goal_id,
        plan_item_id=plan_item_id,
        project_id=project.id,
        objective_id=project.objective_id,
        artifact_text=artifact_text,
        reflection_text=reflection_text,
        rubric_checks=dict(rubric_checks),
        status=status,
        met_criteria=met,
        missing_criteria=missing,
        evidence_recorded=False,
        submitted_at=moment,
    )
    db.add(submission)
    db.flush()

    if status == "accepted":
        already_evidenced = db.scalar(
            select(Evidence.id).where(
                Evidence.user_id == user.id,
                Evidence.objective_id == project.objective_id,
                Evidence.kind == "project",
                Evidence.source_ref == project.id,
                Evidence.outcome == "success",
            )
        )
        if already_evidenced is None:
            record_evidence(
                db,
                user_id=user.id,
                objective_id=project.objective_id,
                outcome="success",
                assisted=False,
                kind="project",
                source_ref=project.id,
                occurred_at=moment,
                meta={"submission_id": submission.id, "self_checked": True},
            )
            submission.evidence_recorded = True
            recompute_mastery(db, user.id, objective_id=project.objective_id)

        if plan_item_id:
            # Ownership re-verified at the point of the write, exactly as practice completion does.
            plan_item = plan_item_for_user(db, plan_item_id, user.id)
            if plan_item is not None and plan_item.status != "completed":
                plan_item.status = "completed"
                plan_item.completed_at = moment

    db.flush()
    return submission


def _latest_statuses(db: DbSession, user_id: str) -> dict[str, ProjectSubmission]:
    """Latest submission per project for this learner (attempts are append-only history)."""
    rows = db.scalars(
        select(ProjectSubmission)
        .where(ProjectSubmission.user_id == user_id)
        .order_by(ProjectSubmission.submitted_at, ProjectSubmission.id)
    ).all()
    latest: dict[str, ProjectSubmission] = {}
    for row in rows:
        latest[row.project_id] = row
    return latest


def _attempt_counts(db: DbSession, user_id: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for project_id in db.scalars(
        select(ProjectSubmission.project_id).where(ProjectSubmission.user_id == user_id)
    ).all():
        counts[project_id] = counts.get(project_id, 0) + 1
    return counts


def project_public(
    project: Project,
    *,
    locale: str,
    objective_title: str,
    latest: ProjectSubmission | None,
    attempts: int,
) -> dict:
    return {
        "id": project.id,
        "path_id": project.path_id,
        "objective_id": project.objective_id,
        "objective_title": objective_title,
        "title": localised({"title_en": project.title_en, "title_ar": project.title_ar}, "title", locale),
        "brief_md": localised(
            {"brief_md_en": project.brief_md_en, "brief_md_ar": project.brief_md_ar},
            "brief_md",
            locale,
        ),
        "rubric": [
            {
                "id": str(criterion.get("id", "")),
                "label": localised(
                    {"label_en": criterion.get("label_en", ""), "label_ar": criterion.get("label_ar", "")},
                    "label",
                    locale,
                ),
                "required": bool(criterion.get("required", True)),
            }
            for criterion in project.rubric or []
        ],
        "min_artifact_chars": project.min_artifact_chars,
        "min_reflection_chars": project.min_reflection_chars,
        "est_minutes": project.est_minutes,
        "my_status": latest.status if latest is not None else None,
        "attempts": attempts,
    }


def list_projects(db: DbSession, user: User, *, path_id: str | None, locale: str) -> list[dict]:
    query = select(Project).order_by(Project.path_id, Project.sequence, Project.id)
    if path_id is not None:
        query = query.where(Project.path_id == path_id)
    projects = list(db.scalars(query).all())
    titles = {
        row.id: (row.title_ar if locale == "ar" and row.title_ar.strip() else row.title_en)
        for row in db.scalars(select(Objective)).all()
    }
    latest = _latest_statuses(db, user.id)
    counts = _attempt_counts(db, user.id)
    return [
        project_public(
            project,
            locale=locale,
            objective_title=titles.get(project.objective_id, project.objective_id),
            latest=latest.get(project.id),
            attempts=counts.get(project.id, 0),
        )
        for project in projects
    ]


def submission_public(submission: ProjectSubmission) -> dict:
    return {
        "id": submission.id,
        "project_id": submission.project_id,
        "objective_id": submission.objective_id,
        "goal_id": submission.goal_id,
        "plan_item_id": submission.plan_item_id,
        "status": submission.status,
        "met_criteria": list(submission.met_criteria or []),
        "missing_criteria": list(submission.missing_criteria or []),
        "artifact_text": submission.artifact_text,
        "reflection_text": submission.reflection_text,
        "evidence_recorded": submission.evidence_recorded,
        "submitted_at": submission.submitted_at,
    }


__all__ = [
    "ProjectConflict",
    "ProjectError",
    "evaluate_submission",
    "list_projects",
    "project_public",
    "submission_public",
    "submit_project",
]
