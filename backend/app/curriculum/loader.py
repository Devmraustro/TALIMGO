"""Copy authored curriculum data into the database, idempotently.

The repository is the source of truth for content; this loader mirrors it into tables the
application queries. Running it twice must not duplicate or corrupt anything, so every record is
matched by its stable identifier.

Ordering note: objectives, lessons and items are written in three passes with a flush between them.
Items and lessons carry foreign keys to objectives, and the ORM only orders pending inserts when it
can see a relationship — plain foreign keys do not give it that information.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.curriculum.registry import PATHS
from app.models import Item, Lesson, Objective, Project


def _upsert_objectives(db: Session, path: dict) -> int:
    count = 0
    for objective_data in path["objectives"]:
        objective = db.get(Objective, objective_data["id"])
        if objective is None:
            objective = Objective(id=objective_data["id"])
            db.add(objective)
        objective.path_id = path["id"]
        objective.title_en = objective_data["title_en"]
        objective.title_ar = objective_data.get("title_ar", "")
        objective.summary_en = objective_data.get("summary_en", "")
        objective.summary_ar = objective_data.get("summary_ar", "")
        objective.kind = objective_data.get("kind", "concept")
        objective.bloom_level = objective_data.get("bloom_level", "understand")
        objective.difficulty = int(objective_data.get("difficulty", 1))
        objective.prerequisite_ids = list(objective_data.get("prerequisites", []))
        objective.sequence = int(objective_data.get("sequence", 0))
        count += 1
    db.flush()
    return count


def _upsert_lessons(db: Session, path: dict) -> int:
    count = 0
    for objective_data in path["objectives"]:
        lesson_data = objective_data.get("lesson")
        if not lesson_data:
            continue
        lesson = db.get(Lesson, lesson_data["id"])
        if lesson is None:
            lesson = Lesson(id=lesson_data["id"])
            db.add(lesson)
        lesson.path_id = path["id"]
        lesson.objective_id = objective_data["id"]
        lesson.title_en = lesson_data["title_en"]
        lesson.title_ar = lesson_data.get("title_ar", "")
        lesson.body_md_en = lesson_data.get("body_md_en", "")
        lesson.body_md_ar = lesson_data.get("body_md_ar", "")
        lesson.est_minutes = int(lesson_data.get("est_minutes", 20))
        lesson.sequence = int(objective_data.get("sequence", 0))
        count += 1
    db.flush()
    return count


def _upsert_items(db: Session, path: dict) -> int:
    count = 0
    for objective_data in path["objectives"]:
        for item_data in objective_data.get("items", []):
            item = db.get(Item, item_data["id"])
            if item is None:
                item = Item(id=item_data["id"])
                db.add(item)
            item.objective_id = objective_data["id"]
            item.kind = item_data["kind"]
            item.prompt_en = item_data["prompt_en"]
            item.prompt_ar = item_data.get("prompt_ar", "")
            item.options = item_data.get("options")
            item.answer_key = item_data["answer_key"]
            item.explanation_en = item_data.get("explanation_en", "")
            item.explanation_ar = item_data.get("explanation_ar", "")
            item.difficulty = int(item_data.get("difficulty", 1))
            item.is_diagnostic = bool(item_data.get("is_diagnostic", False))
            count += 1
    db.flush()
    return count


def _upsert_projects(db: Session, path: dict) -> int:
    count = 0
    for objective_data in path["objectives"]:
        project_data = objective_data.get("project")
        if not project_data:
            continue
        project = db.get(Project, project_data["id"])
        if project is None:
            project = Project(id=project_data["id"])
            db.add(project)
        project.path_id = path["id"]
        project.objective_id = objective_data["id"]
        project.title_en = project_data["title_en"]
        project.title_ar = project_data.get("title_ar", "")
        project.brief_md_en = project_data.get("brief_md_en", "")
        project.brief_md_ar = project_data.get("brief_md_ar", "")
        project.rubric = list(project_data.get("rubric", []))
        project.min_artifact_chars = int(project_data.get("min_artifact_chars", 200))
        project.min_reflection_chars = int(project_data.get("min_reflection_chars", 40))
        project.est_minutes = int(project_data.get("est_minutes", 60))
        project.sequence = int(objective_data.get("sequence", 0))
        count += 1
    db.flush()
    return count


def load_path(db: Session, path: dict) -> dict[str, int]:
    """Upsert one path; returns counts written."""
    return {
        "objectives": _upsert_objectives(db, path),
        "lessons": _upsert_lessons(db, path),
        "items": _upsert_items(db, path),
        "projects": _upsert_projects(db, path),
    }


def load_all(db: Session) -> dict[str, int]:
    totals = {"paths": 0, "objectives": 0, "lessons": 0, "items": 0, "projects": 0}
    for path in PATHS.values():
        counts = load_path(db, path)
        totals["paths"] += 1
        for key, value in counts.items():
            totals[key] += value
    db.commit()
    return totals
