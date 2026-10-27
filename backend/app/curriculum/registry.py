"""Lookup helpers over the authored curriculum."""

from __future__ import annotations

from typing import Any

from app.curriculum.frontend_foundations import PATH as FRONTEND_FOUNDATIONS
from app.curriculum.python_foundations import PATH as PYTHON_FOUNDATIONS

PATHS: dict[str, dict[str, Any]] = {
    PYTHON_FOUNDATIONS["id"]: PYTHON_FOUNDATIONS,
    FRONTEND_FOUNDATIONS["id"]: FRONTEND_FOUNDATIONS,
}


class UnknownPathError(KeyError):
    pass


def get_path(path_id: str) -> dict[str, Any]:
    try:
        return PATHS[path_id]
    except KeyError as exc:
        raise UnknownPathError(f"Unknown learning path {path_id!r}") from exc


def list_path_summaries() -> list[dict[str, Any]]:
    summaries = []
    for path in PATHS.values():
        objectives = path["objectives"]
        total_minutes = sum(objective.get("est_minutes", 20) for objective in objectives)
        summaries.append(
            {
                "id": path["id"],
                "title_en": path["title_en"],
                "title_ar": path["title_ar"],
                "summary_en": path["summary_en"],
                "summary_ar": path["summary_ar"],
                "objective_count": len(objectives),
                "estimated_hours": round(total_minutes / 60, 1),
            }
        )
    return sorted(summaries, key=lambda summary: summary["id"])


def objective_index(path_id: str) -> dict[str, dict[str, Any]]:
    path = get_path(path_id)
    return {objective["id"]: objective for objective in path["objectives"]}


def lesson_index(path_id: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for objective in get_path(path_id)["objectives"]:
        lesson = objective.get("lesson")
        if lesson:
            index[lesson["id"]] = {**lesson, "objective_id": objective["id"], "path_id": path_id}
    return index


def project_index(path_id: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for objective in get_path(path_id)["objectives"]:
        project = objective.get("project")
        if project:
            index[project["id"]] = {**project, "objective_id": objective["id"], "path_id": path_id}
    return index


def item_index(path_id: str) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for objective in get_path(path_id)["objectives"]:
        for item in objective.get("items", []):
            index[item["id"]] = {**item, "objective_id": objective["id"]}
    return index


def all_objectives() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for path in PATHS.values():
        for objective in path["objectives"]:
            result.append({**objective, "path_id": path["id"]})
    return result


def all_lessons() -> list[dict[str, Any]]:
    return [lesson for path_id in PATHS for lesson in lesson_index(path_id).values()]


def all_items() -> list[dict[str, Any]]:
    return [item for path_id in PATHS for item in item_index(path_id).values()]


def all_projects() -> list[dict[str, Any]]:
    return [project for path_id in PATHS for project in project_index(path_id).values()]


def localised(record: dict[str, Any], field: str, locale: str) -> str:
    """Return the ``<field>_<locale>`` value with a documented English fallback."""
    value = record.get(f"{field}_{locale}") or record.get(f"{field}_en") or ""
    return value
