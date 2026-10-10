"""The first MVP journey, end to end, through the HTTP API.

GOAL → ASSESS → PLAN → LEARN/PRACTICE → MEASURE, plus the isolation guarantees that make it safe to
run for more than one learner.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import answer_diagnostic_until_done, create_goal, register


def test_goal_creation_validates_the_path_and_time_budget(client) -> None:
    register(client)
    unknown = client.post(
        "/api/goals",
        json={"path_id": "does-not-exist", "statement": "Learn something unknown", "weekly_minutes": 200},
    )
    assert unknown.status_code == 404

    too_short = client.post(
        "/api/goals",
        json={"path_id": "python-foundations", "statement": "Learn Python properly", "weekly_minutes": 5},
    )
    assert too_short.status_code == 422


def test_full_journey_goal_to_measured_progress(client) -> None:
    register(client)
    goal = create_goal(client)

    # --- ASSESS ---
    diagnostic = answer_diagnostic_until_done(client, goal["id"], correct=True)
    state = client.get(f"/api/diagnostic/{diagnostic['attempt_id']}").json()
    assert state["status"] == "completed"
    assert state["current_item"] is None
    placement = state["placement"]
    assert placement["summary"]["assumed_known"] >= 1
    assert "provisional" in placement["note"].lower()

    # --- PLAN ---
    roadmap = client.post(f"/api/plans/goals/{goal['id']}")
    assert roadmap.status_code == 200, roadmap.text
    body = roadmap.json()
    assert body["validation"]["ok"] is True
    assert body["plan"]["weeks"], "a roadmap must contain weeks"
    order = [item["order_index"] for week in body["plan"]["weeks"] for item in week["items"]]
    assert order == sorted(order)
    assert body["plan"]["validation_report"]["checked"]

    # A learner who answered hard items correctly gets short confirmation checks rather than
    # full first-time lessons. Mastery still requires unassisted, spaced success afterwards.
    kinds = [item["kind"] for week in body["plan"]["weeks"] for item in week["items"]]
    assert "assess" in kinds, f"expected confirmation checks for known objectives, got {sorted(set(kinds))}"
    assert "skipped_objectives" in body

    # --- MEASURE (dashboard) ---
    dashboard = client.get("/api/dashboard")
    assert dashboard.status_code == 200
    data = dashboard.json()
    assert data["goal"]["id"] == goal["id"]
    action = data["next_action"]
    assert action["kind"] in {"learn", "practice", "review", "assess", "build", "diagnostic", "idle"}
    assert action["rationale"]
    assert action["evidence_basis"]
    assert data["mastery_summary"]["recorded"] >= 1

    # --- LEARN + PRACTICE ---
    objective_id = action["objective_id"] or "py:values"
    session = client.post(
        "/api/practice/sessions",
        json={"objective_id": objective_id, "size": 3, "goal_id": goal["id"]},
    )
    assert session.status_code == 201, session.text
    session_body = session.json()
    assert session_body["item"] is not None
    assert "answer_key" not in session_body["item"]
    assert "explanation" not in str(session_body["item"])

    # A wrong answer produces a failure evidence record and feedback with the correct answer.
    first_item = session_body["item"]
    wrong = _wrong_response(first_item)
    answered = client.post(
        f"/api/practice/sessions/{session_body['session_id']}/answers",
        json={"item_id": first_item["id"], "response": wrong, "used_hint": False},
    )
    assert answered.status_code == 200, answered.text
    feedback = answered.json()["feedback"]
    assert feedback["is_correct"] is False
    assert feedback["correct_answer"]

    evidence = client.get("/api/practice/progress/evidence").json()
    assert any(row["outcome"] == "failure" for row in evidence)

    mastery = client.get("/api/practice/progress/mastery").json()
    entry = next(row for row in mastery if row["objective_id"] == objective_id)
    assert entry["phase"] in {"acquiring", "retaining"}
    assert entry["evidence_count"] >= 1

    # Completing the session marks the plan item done, so the dashboard moves on.
    completed = client.post(f"/api/practice/sessions/{session_body['session_id']}/complete")
    assert completed.status_code == 200
    assert completed.json()["session_id"] == session_body["session_id"]


def test_mastery_is_recomputable_and_deterministic(client) -> None:
    register(client)
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"], correct=True)

    first = client.get("/api/practice/progress/mastery").json()
    recomputed = client.post("/api/practice/progress/recompute").json()
    assert recomputed == first, "replaying evidence must reproduce identical estimates"


def test_regenerating_a_roadmap_supersedes_the_previous_version(client) -> None:
    register(client)
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"], correct=True)

    first = client.post(f"/api/plans/goals/{goal['id']}").json()["plan"]
    second = client.post(f"/api/plans/goals/{goal['id']}").json()["plan"]
    assert second["version"] == first["version"] + 1
    assert second["id"] != first["id"]

    superseded = client.get(f"/api/plans/{first['id']}").json()
    assert superseded["status"] == "superseded"
    active = client.get("/api/plans/active").json()
    assert active["id"] == second["id"]


def test_diagnostic_answers_are_graded_and_cannot_be_replayed(client) -> None:
    register(client)
    goal = create_goal(client)
    start = client.post(f"/api/diagnostic/goals/{goal['id']}").json()
    item = start["current_item"]

    first = client.post(
        f"/api/diagnostic/{start['attempt_id']}/answers",
        json={"item_id": item["id"], "response": _wrong_response(item)},
    )
    assert first.status_code == 200
    second = client.post(
        f"/api/diagnostic/{start['attempt_id']}/answers",
        json={"item_id": item["id"], "response": _wrong_response(item)},
    )
    assert second.status_code == 409, "an item cannot be answered twice in one attempt"


def test_item_payloads_never_include_answer_keys_or_explanations(client) -> None:
    register(client)
    goal = create_goal(client)
    seen_payloads: list[str] = []

    start = client.post(f"/api/diagnostic/goals/{goal['id']}").json()
    attempt_id = start["attempt_id"]
    seen_payloads.append(str(start))

    state = start
    guard = 0
    while state["current_item"] is not None and guard < 15:
        guard += 1
        item = state["current_item"]
        response = client.post(
            f"/api/diagnostic/{attempt_id}/answers",
            json={"item_id": item["id"], "response": _correct_response(item)},
        )
        assert response.status_code == 200
        seen_payloads.append(response.text)
        state = {
            "current_item": response.json()["next_item"],
            "status": "completed" if response.json()["completed"] else "in_progress",
        }

    blob = " ".join(seen_payloads)
    assert "answer_key" not in blob
    assert "accepted" not in blob
    assert "explanation_en" not in blob


def test_learners_cannot_reach_each_others_objects(client) -> None:
    register(client, email="first@example.com")
    goal = create_goal(client)
    diagnostic = answer_diagnostic_until_done(client, goal["id"], correct=True)
    plan = client.post(f"/api/plans/goals/{goal['id']}").json()["plan"]
    session = client.post("/api/practice/sessions", json={"objective_id": "py:values"}).json()

    other = TestClient(client.app)
    register(other, email="second@example.com")

    assert other.get(f"/api/diagnostic/{diagnostic['attempt_id']}").status_code == 404
    assert other.get(f"/api/plans/{plan['id']}").status_code == 404
    assert other.get(f"/api/practice/sessions/{session['session_id']}").status_code == 404
    assert other.get("/api/plans/active").json() is None
    assert other.get("/api/dashboard").json()["goal"] is None

    # And the first learner still sees their own data.
    assert client.get(f"/api/plans/{plan['id']}").status_code == 200


def test_goal_creation_is_capped_so_plans_stay_meaningful(client) -> None:
    register(client)
    for index in range(3):
        response = client.post(
            "/api/goals",
            json={
                "path_id": "python-foundations",
                "statement": f"Goal number {index} to learn Python well",
                "weekly_minutes": 200,
            },
        )
        assert response.status_code == 201
    overflow = client.post(
        "/api/goals",
        json={"path_id": "python-foundations", "statement": "One goal too many", "weekly_minutes": 200},
    )
    assert overflow.status_code == 409


def test_dashboard_without_a_goal_is_explicit_and_actionable(client) -> None:
    register(client)
    data = client.get("/api/dashboard").json()
    assert data["goal"] is None
    assert data["next_action"]["kind"] == "idle"
    assert "goal" in data["next_action"]["title"].lower()


def _correct_response(item: dict) -> dict:
    from app.curriculum.registry import item_index

    key = item_index("python-foundations")[item["id"]]["answer_key"]
    if item["kind"] == "mcq_single":
        return {"option_id": key["option_id"]}
    return {"text": key["accepted"][0]}


def _wrong_response(item: dict) -> dict:
    if item["kind"] == "mcq_single":
        from app.curriculum.registry import item_index

        key = item_index("python-foundations")[item["id"]]["answer_key"]
        wrong = [option["id"] for option in item["options"] if option["id"] != key["option_id"]]
        return {"option_id": wrong[0]}
    return {"text": "an answer that is definitely wrong"}
