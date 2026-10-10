"""Curriculum integrity: structure, prerequisite graph, and *verified answer keys*.

The `verify_expr` mechanism executes a Python expression and requires its result to equal an
accepted answer for that item. This is how a wrong key fails the build instead of reaching a learner.
"""

from __future__ import annotations

from app.curriculum.python_foundations import PATH
from app.curriculum.registry import PATHS, all_items, all_lessons, all_objectives, item_index, lesson_index

PATH_ID = "python-foundations"


def test_every_path_has_unique_ids_and_localised_titles() -> None:
    seen: set[str] = set()
    for path in PATHS.values():
        assert path["id"] not in seen
        seen.add(path["id"])
        assert path["title_en"] and path["title_ar"]
        assert path["summary_en"] and path["summary_ar"], "Arabic summary is required, not a placeholder"


def test_objective_ids_are_unique_and_namespaced() -> None:
    ids = [objective["id"] for objective in all_objectives()]
    assert len(ids) == len(set(ids))
    assert all(objective_id.startswith("py:") for objective_id in ids)


def test_prerequisite_graph_is_acyclic_and_complete() -> None:
    objectives = {objective["id"]: objective for objective in all_objectives()}
    for objective in objectives.values():
        for prerequisite in objective.get("prerequisites", []):
            assert prerequisite in objectives, f"{objective['id']} requires unknown {prerequisite}"

    # Kahn's algorithm: every node must be reachable, so no cycle can survive.
    indegree = {oid: len(obj.get("prerequisites", [])) for oid, obj in objectives.items()}
    ready = [oid for oid, count in indegree.items() if count == 0]
    visited = 0
    while ready:
        current = ready.pop()
        visited += 1
        for oid, obj in objectives.items():
            if current in obj.get("prerequisites", []):
                indegree[oid] -= 1
                if indegree[oid] == 0:
                    ready.append(oid)
    assert visited == len(objectives), "the curriculum graph contains a cycle"


def test_every_objective_has_a_lesson_with_content_in_both_languages() -> None:
    lessons = lesson_index(PATH_ID)
    for objective in PATH["objectives"]:
        lesson = objective.get("lesson")
        assert lesson, f"{objective['id']} has no lesson"
        assert lesson["id"] in lessons
        assert lesson.get("body_md_en"), f"{lesson['id']} has no English body"
        assert lesson.get("body_md_ar"), f"{lesson['id']} has no Arabic body"


def test_item_keys_match_their_kind() -> None:
    for item in all_items():
        key = item["answer_key"]
        if item["kind"] == "mcq_single":
            assert "option_id" in key, f"{item['id']} missing option_id"
            option_ids = {option["id"] for option in item.get("options") or []}
            assert key["option_id"] in option_ids, f"{item['id']} key points at a non-existent option"
            assert len(option_ids) >= 2, f"{item['id']} needs at least two options"
        elif item["kind"] == "short_answer":
            assert item.get("options") in (None, []), f"{item['id']} must not carry options"
            accepted = key.get("accepted")
            assert isinstance(accepted, list) and accepted, f"{item['id']} has no accepted answers"
        else:
            raise AssertionError(f"{item['id']} has unsupported kind {item['kind']!r}")


def test_every_item_explains_its_answer_in_both_languages() -> None:
    for item in all_items():
        assert item["explanation_en"].strip(), f"{item['id']} has no English explanation"
        assert item["explanation_ar"].strip(), f"{item['id']} has no Arabic explanation"


def test_verify_expressions_match_their_answer_keys() -> None:
    """Executes the declared expression. A wrong key fails here."""
    checked = 0
    for item in all_items():
        expression = item.get("verify_expr")
        if not expression:
            continue
        produced = eval(  # expressions are authored constants in this repository
            expression,
            {"__builtins__": {}},
            {
                "len": len,
                "sum": sum,
                "int": int,
                "str": str,
                "float": float,
                "range": range,
                "min": min,
                "max": max,
            },
        )
        accepted = item["answer_key"]["accepted"]
        as_text = str(produced)
        matches = as_text in accepted or (as_text.endswith(".0") and as_text[:-2] in accepted)
        assert matches, (
            f"{item['id']}: expression {expression!r} produced {as_text!r}, "
            f"which is not among the accepted answers {accepted!r}"
        )
        checked += 1
    assert checked >= 5, "expected several mechanically verified items"


def test_each_objective_has_at_least_two_items_and_a_diagnostic_item() -> None:
    for objective in PATH["objectives"]:
        items = objective.get("items", [])
        assert len(items) >= 2, f"{objective['id']} needs at least two items"
        assert any(item.get("is_diagnostic") for item in items), (
            f"{objective['id']} has no diagnostic item, so it can never be placed"
        )


def test_difficulty_is_within_range() -> None:
    for item in all_items():
        assert 1 <= item["difficulty"] <= 5
    for objective in all_objectives():
        assert 1 <= objective["difficulty"] <= 5


def test_time_estimates_are_plausible() -> None:
    for objective in all_objectives():
        assert 5 <= objective["est_minutes"] <= 240
    for lesson in all_lessons():
        assert 5 <= lesson["est_minutes"] <= 120


def test_no_item_contains_a_hosted_ai_provider_reference() -> None:
    text = str(PATH).lower()
    for token in ("openai", "anthropic", "gemini", "chatgpt"):
        assert token not in text, f"curriculum content mentions a hosted provider: {token}"


def test_registry_lookups_agree_with_the_data() -> None:
    index = item_index(PATH_ID)
    assert len(index) == len(all_items()) == sum(len(obj.get("items", [])) for obj in PATH["objectives"])
    assert "py:project" in {objective["id"] for objective in PATH["objectives"]}
