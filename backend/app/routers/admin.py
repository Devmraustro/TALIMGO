"""Admin endpoints: curriculum workflow and operational visibility.

Every route depends on :data:`app.deps.AdminUser`, which resolves the role server-side from the
session. Unauthorised callers receive 404, not a description of what exists.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from app.curriculum.loader import load_all
from app.deps import AdminUser, Db
from app.models import AuditLog, Evidence, Item, Lesson, Objective, Project, User

router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(AdminUser)])


@router.post("/curriculum/reload")
def reload_curriculum(admin: AdminUser, db: Db) -> dict:
    counts = load_all(db)
    db.add(AuditLog(actor_user_id=admin.id, action="curriculum.reload", detail=counts))
    db.commit()
    return {"reloaded": counts}


@router.get("/curriculum/inventory")
def curriculum_inventory(db: Db) -> dict:
    return {
        "objectives": db.scalar(select(func.count()).select_from(Objective)) or 0,
        "lessons": db.scalar(select(func.count()).select_from(Lesson)) or 0,
        "items": db.scalar(select(func.count()).select_from(Item)) or 0,
        "diagnostic_items": db.scalar(
            select(func.count()).select_from(Item).where(Item.is_diagnostic.is_(True))
        )
        or 0,
        "projects": db.scalar(select(func.count()).select_from(Project)) or 0,
    }


@router.get("/audit-log")
def audit_log(db: Db, limit: int = 50) -> dict:
    """Recent accountability records (threat model T17).

    Audit rows carry actions and counts, never learner content; rows belonging to deleted
    accounts were anonymised at deletion time (``actor_user_id`` is null there by design).
    """
    rows = db.scalars(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
        .limit(min(max(limit, 1), 200))
    ).all()
    return {
        "entries": [
            {
                "id": row.id,
                "actor_user_id": row.actor_user_id,
                "action": row.action,
                "target": row.target,
                "detail": row.detail,
                "created_at": row.created_at,
            }
            for row in rows
        ]
    }


@router.get("/stats")
def stats(db: Db) -> dict:
    return {
        "learners": db.scalar(select(func.count()).select_from(User)) or 0,
        "evidence_records": db.scalar(select(func.count()).select_from(Evidence)) or 0,
    }
