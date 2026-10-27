"""Project briefs and submissions — the BUILD step (ADR 0008).

Acceptance is deterministic rubric checking in ``app.services.projects``; nothing here judges
quality, and the response carries ``evidence_recorded`` so the interface can say exactly what a
submission did (and did not) do to the learner's record.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.deps import CurrentLocale, CurrentUser, Db
from app.models import Objective, Project, ProjectSubmission
from app.schemas import ProjectOut, ProjectSubmissionIn, ProjectSubmissionOut
from app.services import projects as project_service
from app.services.assessment import AssessmentConflict, AssessmentError
from app.services.progress import objective_title
from app.services.projects import ProjectError

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(
    user: CurrentUser, db: Db, locale: CurrentLocale, path_id: str | None = None
) -> list[ProjectOut]:
    """All authored projects, or one path's when ``path_id`` is given."""
    return [
        ProjectOut(**row) for row in project_service.list_projects(db, user, path_id=path_id, locale=locale)
    ]


@router.get("/submissions/mine", response_model=list[ProjectSubmissionOut])
def my_submissions(user: CurrentUser, db: Db, limit: int = 50) -> list[ProjectSubmissionOut]:
    """The learner's portfolio history: every attempt, latest first."""
    rows = db.scalars(
        select(ProjectSubmission)
        .where(ProjectSubmission.user_id == user.id)
        .order_by(ProjectSubmission.submitted_at.desc(), ProjectSubmission.id.desc())
        .limit(min(max(limit, 1), 200))
    ).all()
    return [ProjectSubmissionOut(**project_service.submission_public(row)) for row in rows]


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, user: CurrentUser, db: Db, locale: CurrentLocale) -> ProjectOut:
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.")
    mine = list(
        db.scalars(
            select(ProjectSubmission).where(
                ProjectSubmission.user_id == user.id,
                ProjectSubmission.project_id == project.id,
            )
        ).all()
    )
    latest = max(mine, key=lambda row: (row.submitted_at, row.id), default=None)
    return ProjectOut(
        **project_service.project_public(
            project,
            locale=locale,
            objective_title=objective_title(
                db.get(Objective, project.objective_id), locale, project.objective_id
            ),
            latest=latest,
            attempts=len(mine),
        )
    )


@router.post(
    "/{project_id}/submissions",
    response_model=ProjectSubmissionOut,
    status_code=status.HTTP_201_CREATED,
)
def submit(project_id: str, payload: ProjectSubmissionIn, user: CurrentUser, db: Db) -> ProjectSubmissionOut:
    try:
        submission = project_service.submit_project(
            db,
            user,
            project_id=project_id,
            artifact_text=payload.artifact_text,
            reflection_text=payload.reflection_text,
            rubric_checks=payload.rubric_checks,
            goal_id=payload.goal_id,
            plan_item_id=payload.plan_item_id,
        )
    except (ProjectError, AssessmentError) as exc:
        if isinstance(exc, AssessmentConflict):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    db.commit()
    return ProjectSubmissionOut(**project_service.submission_public(submission))
