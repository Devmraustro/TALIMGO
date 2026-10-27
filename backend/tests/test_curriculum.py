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


NAMESPACES = {"python-foundations": "py:", "frontend-foundations": "fe:"}


def test_objective_ids_are_unique_and_namespaced() -> None:
    objectives = all_objectives()
    ids = [objective["id"] for objective in objectives]
    assert len(ids) == len(set(ids))
    for objective in objectives:
        prefix = NAMESPACES[objective["path_id"]]
        assert objective["id"].startswith(prefix), (
            f"{objective['id']} must live in the {prefix!r} namespace of {objective['path_id']}"
        )


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
    for path in PATHS.values():
        lessons = lesson_index(path["id"])
        for objective in path["objectives"]:
            lesson = objective.get("lesson")
            assert lesson, f"{objective['id']} has no lesson"
            assert lesson["id"] in lessons
            assert lesson.get("body_md_en"), f"{lesson['id']} has no English body"
            assert lesson.get("body_md_ar"), f"{lesson['id']} has no Arabic body"


def test_item_keys_match_their_kind() -> None:
    for item in all_items():
        key = item["answer_key"]
        option_ids = {option["id"] for option in item.get("options") or []}
        if item["kind"] == "mcq_single":
            assert "option_id" in key, f"{item['id']} missing option_id"
            assert key["option_id"] in option_ids, f"{item['id']} key points at a non-existent option"
            assert len(option_ids) >= 2, f"{item['id']} needs at least two options"
        elif item["kind"] == "mcq_multi":
            keyed = key.get("option_ids")
            assert isinstance(keyed, list) and keyed, f"{item['id']} needs keyed option_ids"
            assert set(keyed) <= option_ids, f"{item['id']} key points at a non-existent option"
            assert len(option_ids) >= 3, f"{item['id']} needs at least three options"
        elif item["kind"] == "ordering":
            keyed = key.get("option_ids")
            assert isinstance(keyed, list), f"{item['id']} needs an ordered option_ids key"
            assert sorted(keyed) == sorted(option_ids), (
                f"{item['id']} key must be a permutation of its options"
            )
            assert len(option_ids) >= 3, f"{item['id']} needs at least three steps to order"
        elif item["kind"] == "numeric":
            assert item.get("options") in (None, []), f"{item['id']} must not carry options"
            float(key["value"])  # raises unless the keyed value is a number
            if "tolerance" in key:
                assert float(key["tolerance"]) >= 0, f"{item['id']} tolerance must not be negative"
        elif item["kind"] == "true_false":
            assert isinstance(key.get("value"), bool), f"{item['id']} key must be a boolean"
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
        if item["kind"] == "numeric":
            expected = float(item["answer_key"]["value"])
            tolerance = float(item["answer_key"].get("tolerance", 0))
            assert abs(float(produced) - expected) <= tolerance, (
                f"{item['id']}: expression {expression!r} produced {produced!r}, key says {expected!r}"
            )
            checked += 1
            continue
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
    for path in PATHS.values():
        for objective in path["objectives"]:
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
    text = str(PATHS).lower()
    for token in ("openai", "anthropic", "gemini", "chatgpt"):
        assert token not in text, f"curriculum content mentions a hosted provider: {token}"


def test_project_objectives_carry_a_complete_project_spec() -> None:
    from app.curriculum.registry import all_projects

    projects = all_projects()
    assert projects, "at least one authored project must exist (the BUILD step)"
    ids = [project["id"] for project in projects]
    assert len(ids) == len(set(ids)), "project ids must be unique"
    objective_ids = {objective["id"] for objective in all_objectives()}
    for project in projects:
        assert project["objective_id"] in objective_ids
        assert project["title_en"] and project["title_ar"]
        assert project["brief_md_en"].strip() and project["brief_md_ar"].strip()
        rubric = project["rubric"]
        assert len(rubric) >= 3, f"{project['id']} rubric needs at least three criteria"
        criterion_ids = [criterion["id"] for criterion in rubric]
        assert len(criterion_ids) == len(set(criterion_ids))
        for criterion in rubric:
            assert criterion["label_en"].strip() and criterion["label_ar"].strip()
        assert any(criterion.get("required", True) for criterion in rubric)
        assert 50 <= project["min_artifact_chars"] <= 5000
        assert 10 <= project["min_reflection_chars"] <= 1000
    # And the reverse: an objective declared as a project must actually carry its spec.
    for path in PATHS.values():
        for objective in path["objectives"]:
            if objective.get("kind") == "project":
                assert objective.get("project"), f"{objective['id']} is a project without a brief"


def test_registry_lookups_agree_with_the_data() -> None:
    for path_id, path in PATHS.items():
        index = item_index(path_id)
        assert len(index) == sum(len(obj.get("items", [])) for obj in path["objectives"])
    assert len(all_items()) == sum(
        len(obj.get("items", [])) for path in PATHS.values() for obj in path["objectives"]
    )
    assert "py:project" in {objective["id"] for objective in PATH["objectives"]}
