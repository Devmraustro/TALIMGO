"""Projections from database rows to API shapes.

The security-relevant projection is :func:`item_public`: it is the only way an item reaches a
client, and it deliberately has no field for the answer key or the explanation.
"""

from __future__ import annotations

import hashlib

from app.curriculum.registry import localised
from app.models import Item, Lesson, Objective, PlanItem, PlanWeek


def _presentation_order(item: Item, options: list[dict]) -> list[dict]:
    """The order options are shown in. For ``ordering`` items the authored order IS the answer.

    Serving authored order would hand the learner the key, so ordering options are presented in a
    deterministic pseudo-random order derived from the item and option ids: stable across
    requests (a refresh cannot reshuffle mid-answer), independent per item, and — by the rotate
    guard — never accidentally the authored sequence itself. Every other kind keeps authored
    order, which is how the bank has always been presented.
    """
    if item.kind != "ordering" or len(options) < 2:
        return options
    shuffled = sorted(
        options,
        key=lambda option: hashlib.sha256(f"{item.id}:{option.get('id', '')}".encode()).hexdigest(),
    )
    if [option.get("id") for option in shuffled] == [option.get("id") for option in options]:
        shuffled = shuffled[1:] + shuffled[:1]
    return shuffled


def item_public(item: Item, locale: str = "en") -> dict:
    return {
        "id": item.id,
        "objective_id": item.objective_id,
        "kind": item.kind,
        "prompt": localised({"prompt_en": item.prompt_en, "prompt_ar": item.prompt_ar}, "prompt", locale),
        "options": [
            {
                "id": option.get("id", ""),
                "text": option.get(locale) or option.get("en") or "",
            }
            for option in _presentation_order(item, list(item.options or []))
        ]
        or None,
        "difficulty": item.difficulty,
    }


def objective_public(objective: Objective, locale: str = "en") -> dict:
    return {
        "id": objective.id,
        "path_id": objective.path_id,
        "title": localised({"title_en": objective.title_en, "title_ar": objective.title_ar}, "title", locale),
        "summary": localised(
            {"summary_en": objective.summary_en, "summary_ar": objective.summary_ar}, "summary", locale
        ),
        "bloom_level": objective.bloom_level,
        "difficulty": objective.difficulty,
        "prerequisite_ids": list(objective.prerequisite_ids or []),
    }


def lesson_public(lesson: Lesson, locale: str = "en") -> dict:
    return {
        "id": lesson.id,
        "objective_id": lesson.objective_id,
        "title": localised({"title_en": lesson.title_en, "title_ar": lesson.title_ar}, "title", locale),
        "body_md": localised(
            {"body_md_en": lesson.body_md_en, "body_md_ar": lesson.body_md_ar}, "body_md", locale
        ),
        "est_minutes": lesson.est_minutes,
    }


def plan_public(
    plan,
    weeks: list[PlanWeek],
    items_by_week: dict[str, list[PlanItem]],
    objectives: dict[str, Objective],
    locale: str = "en",
) -> dict:
    return {
        "id": plan.id,
        "goal_id": plan.goal_id,
        "version": plan.version,
        "status": plan.status,
        "generator": plan.generator,
        "total_estimated_minutes": plan.total_estimated_minutes,
        "validation_report": plan.validation_report or {},
        "created_at": plan.created_at,
        "weeks": [
            {
                "week_number": week.week_number,
                "theme": localised({"theme_en": week.theme_en, "theme_ar": week.theme_ar}, "theme", locale)
                or f"Week {week.week_number}",
                "items": [
                    {
                        "id": item.id,
                        "order_index": item.order_index,
                        "objective_id": item.objective_id,
                        "objective_title": localised(
                            {
                                "title_en": objectives[item.objective_id].title_en
                                if item.objective_id in objectives
                                else item.objective_id,
                                "title_ar": objectives[item.objective_id].title_ar
                                if item.objective_id in objectives
                                else "",
                            },
                            "title",
                            locale,
                        ),
                        "lesson_id": item.lesson_id,
                        "kind": item.kind,
                        "est_minutes": item.est_minutes,
                        "status": item.status,
                        "rationale": localised(
                            {"rationale_en": item.rationale_en, "rationale_ar": item.rationale_ar},
                            "rationale",
                            locale,
                        ),
                    }
                    for item in items_by_week.get(week.id, [])
                ],
                "total_minutes": sum(entry.est_minutes for entry in items_by_week.get(week.id, [])),
            }
            for week in weeks
        ],
    }
