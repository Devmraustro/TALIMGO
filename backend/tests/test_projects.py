"""Projects: deterministic acceptance, one-shot evidence, ownership (ADR 0008)."""

from __future__ import annotations

from tests.conftest import create_goal, register

PROJECT_ID = "py:project:wordcount"
ARTIFACT = (
    "import sys\n\n\n"
    "def count_words(text):\n"
    "    counts = {}\n"
    "    for word in text.lower().split():\n"
    "        counts[word] = counts.get(word, 0) + 1\n"
    "    return counts\n\n\n"
    "def main():\n"
    "    path = sys.argv[1]\n"
    "    try:\n"
    "        text = open(path, encoding='utf-8').read()\n"
    "    except OSError:\n"
    "        print('file not found:', path)\n"
    "        raise SystemExit(1)\n"
    "    counts = count_words(text)\n"
    "    print(len(text.splitlines()), sum(counts.values()))\n"
    "    print(sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:5])\n\n\n"
    "if __name__ == '__main__':\n"
    "    main()\n"
)
REFLECTION = (
    "First version crashed on an empty file because max() ran on an empty dict; I fixed it by "
    "letting sorted() handle the empty case."
)
ALL_CRITERIA = {
    "runs_correctly": True,
    "handles_errors": True,
    "structure": True,
    "explanation": True,
}


def _submit(
    client, *, goal_id=None, plan_item_id=None, checks=None, artifact=ARTIFACT, reflection=REFLECTION
):
    payload = {
        "artifact_text": artifact,
        "reflection_text": reflection,
        "rubric_checks": ALL_CRITERIA if checks is None else checks,
    }
    if goal_id is not None:
        payload["goal_id"] = goal_id
    if plan_item_id is not None:
        payload["plan_item_id"] = plan_item_id
    return client.post(f"/api/projects/{PROJECT_ID}/submissions", json=payload)


def test_project_is_listed_with_rubric_and_no_attempts(client) -> None:
    register(client)
    response = client.get("/api/projects", params={"path_id": "python-foundations"})
    assert response.status_code == 200, response.text
    (project,) = response.json()
    assert project["id"] == PROJECT_ID
    assert project["objective_id"] == "py:project"
    assert [row["id"] for row in project["rubric"]] == [
        "runs_correctly",
        "handles_errors",
        "structure",
        "explanation",
    ]
    assert project["my_status"] is None and project["attempts"] == 0


def test_complete_submission_is_accepted_and_records_project_evidence(client) -> None:
    register(client)
    goal = create_goal(client)
    response = _submit(client, goal_id=goal["id"])
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "accepted"
    assert body["missing_criteria"] == []
    assert sorted(body["met_criteria"]) == sorted(ALL_CRITERIA)
    assert body["evidence_recorded"] is True

    evidence = client.get("/api/practice/progress/evidence").json()
    project_rows = [row for row in evidence if row["kind"] == "project"]
    assert len(project_rows) == 1
    assert project_rows[0]["objective_id"] == "py:project"
    assert project_rows[0]["outcome"] == "success"


def test_second_acceptance_cannot_farm_evidence(client) -> None:
    register(client)
    first = _submit(client)
    assert first.json()["evidence_recorded"] is True
    second = _submit(client)
    assert second.status_code == 201, second.text
    assert second.json()["status"] == "accepted"
    assert second.json()["evidence_recorded"] is False
    evidence = client.get("/api/practice/progress/evidence").json()
    assert len([row for row in evidence if row["kind"] == "project"]) == 1


def test_incomplete_submission_is_needs_work_with_named_gaps_and_no_evidence(client) -> None:
    register(client)
    response = _submit(
        client,
        checks={"runs_correctly": True},
        artifact="print('hi')",
        reflection="ok",
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "needs_work"
    assert "handles_errors" in body["missing_criteria"]
    assert "artifact:minimum_length" in body["missing_criteria"]
    assert "reflection:minimum_length" in body["missing_criteria"]
    assert body["evidence_recorded"] is False
    assert client.get("/api/practice/progress/evidence").json() == []


def test_unknown_project_and_foreign_goal_are_404(client) -> None:
    register(client)
    other = register(client, email="other@example.com")
    assert _submit(client, goal_id="gol_unknown").status_code == 404
    # The second registration signed the client in as the other learner; submitting against a
    # made-up project id must not confirm existence either.
    assert client.post("/api/projects/nope/submissions", json={"artifact_text": "x" * 50}).status_code == 404
    assert client.get(f"/api/projects/{PROJECT_ID}").status_code == 200  # brief is content
    assert other  # (registration helper returns the account payload; the session switched)


def test_portfolio_lists_my_attempts_and_status_is_tracked(client) -> None:
    register(client)
    _submit(client, checks={})
    _submit(client)
    mine = client.get("/api/projects/submissions/mine").json()
    assert [row["status"] for row in mine] == ["accepted", "needs_work"]  # latest first
    (project,) = client.get("/api/projects", params={"path_id": "python-foundations"}).json()
    assert project["my_status"] == "accepted" and project["attempts"] == 2
