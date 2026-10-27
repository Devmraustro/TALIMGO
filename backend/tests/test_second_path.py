"""The second launch path runs the whole engine: goal → diagnostic → plan → project.

This is the generality proof for the front-end path: none of the machinery may be secretly
Python-shaped (master reference §15.3.1). It also exercises the new item kinds through the
adaptive diagnostic, which is where response-shape mistakes would surface.
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.learning.roadmap import generate_plan
from app.services.plans import curriculum_nodes
from tests.conftest import answer_diagnostic_until_done, create_goal, register


def test_frontend_path_is_offered_alongside_python(client) -> None:
    paths = client.get("/api/curriculum/paths").json()
    ids = [path["id"] for path in paths]
    assert ids == ["frontend-foundations", "python-foundations"]  # sorted by id
    frontend = paths[0]
    assert frontend["objective_count"] == 8
    assert frontend["title_ar"] and frontend["summary_ar"]


def test_frontend_journey_goal_diagnostic_plan(client) -> None:
    register(client)
    goal = create_goal(client, path_id="frontend-foundations")
    answer_diagnostic_until_done(client, goal["id"], correct=True)

    generated = client.post(f"/api/plans/goals/{goal['id']}")
    assert generated.status_code == 200, generated.text
    plan = generated.json()["plan"]
    kinds = [item["kind"] for week in plan["weeks"] for item in week["items"]]
    assert "build" in kinds, "the fe:project objective must appear as a build step"


def test_build_objectives_are_never_downgraded_to_a_quiz() -> None:
    # Even when the starting check suggests the learner already knows the material, a project
    # objective stays a build step: the artefact is the demonstration (ADR 0008).
    nodes = curriculum_nodes("frontend-foundations")
    weeks, _skipped = generate_plan(
        nodes,
        estimates={},
        now=datetime(2026, 10, 27, tzinfo=UTC),
        weekly_minutes=240,
        provisional_known=frozenset({"fe:project", "fe:css-box"}),
    )
    by_objective = {step.objective_id: step.kind for week in weeks for step in week.steps}
    assert by_objective["fe:project"] == "build"
    assert by_objective["fe:css-box"] == "assess", "ordinary objectives still get a confirmation check"


def test_frontend_project_accepts_a_real_submission(client) -> None:
    register(client)
    goal = create_goal(client, path_id="frontend-foundations")
    artifact = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>Amina — profile</title>\n<style>*{box-sizing:border-box}"
        ".cards{display:flex;flex-wrap:wrap;gap:1rem}.card{flex:1 1 200px}"
        "body.dark{background:#111;color:#eee}</style>\n</head>\n<body>\n"
        '<header><h1>Amina</h1></header>\n<main>\n<section class="cards">\n'
        '<article class="card"><h2>Skills</h2><p>HTML, CSS, JavaScript.</p></article>\n'
        '<article class="card"><h2>Projects</h2><p>This very page.</p></article>\n</section>\n'
        '<form><label for="email">Email</label><input id="email" type="email">'
        '<button type="submit">Send</button></form>\n'
        '<button id="theme" type="button">Toggle dark</button>\n</main>\n'
        "<footer><p>Built with TALIMGO lessons.</p></footer>\n"
        "<script>document.querySelector('#theme').addEventListener('click',"
        "()=>document.body.classList.toggle('dark'));</script>\n</body>\n</html>\n"
    )
    response = client.post(
        "/api/projects/fe:project:profile-page/submissions",
        json={
            "artifact_text": artifact,
            "reflection_text": (
                "Cards overflowed at 360px because each card had a fixed 320px width plus gap; "
                "switching to flex-basis with wrap fixed it."
            ),
            "rubric_checks": {
                "semantic_structure": True,
                "responsive": True,
                "layout": True,
                "interaction": True,
            },
            "goal_id": goal["id"],
        },
    )
    assert response.status_code == 201, response.text
    assert response.json()["status"] == "accepted"
    assert response.json()["evidence_recorded"] is True
