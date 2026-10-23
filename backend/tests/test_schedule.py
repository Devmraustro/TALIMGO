"""The study schedule: deterministic day assignment, today's missions, and re-planning.

Regression: the roadmap was an ordered list of steps with no dates at all, so a learner could not see
what to do today, could not tell whether they were behind, and missed days silently piled up.
"""

from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient

from app.learning.schedule import (
    ScheduleEntry,
    ScheduleRow,
    adherence,
    build_schedule,
    daily_budget,
    due_today,
    scheduled_date,
    weekday_set,
)
from tests.conftest import _correct_response, answer_diagnostic_until_done, create_goal, register

MONDAY = date(2026, 3, 2)  # a Monday, so weekday availability is easy to reason about


# --------------------------------------------------------------------------------------
# Pure scheduler
# --------------------------------------------------------------------------------------


def test_schedule_packs_items_into_days_in_order() -> None:
    entries = [ScheduleEntry(key=f"i{n}", est_minutes=30) for n in range(5)]
    offsets = build_schedule(entries, daily_minutes=60)
    assert offsets == [0, 0, 1, 1, 2]
    assert build_schedule(entries, daily_minutes=60) == offsets, "the schedule is deterministic"


def test_an_item_is_never_split_across_days() -> None:
    entries = [ScheduleEntry(key="short", est_minutes=40), ScheduleEntry(key="long", est_minutes=40)]
    offsets = build_schedule(entries, daily_minutes=60)
    assert offsets == [0, 1], "40 + 40 does not fit in a 60-minute day"


def test_a_very_long_item_gets_its_own_day() -> None:
    entries = [ScheduleEntry(key="big", est_minutes=240)]
    assert build_schedule(entries, daily_minutes=60) == [0]


def test_unavailable_weekdays_receive_no_work() -> None:
    entries = [ScheduleEntry(key=f"i{n}", est_minutes=60) for n in range(6)]
    available = weekday_set(["mon", "fri"])  # 0 and 4
    offsets = build_schedule(
        entries, daily_minutes=60, available_weekdays=available, start_weekday=MONDAY.weekday()
    )
    weekdays = {(MONDAY + timedelta(days=offset)).weekday() for offset in offsets}
    assert weekdays <= {0, 4}, weekdays
    assert offsets == sorted(offsets)


def test_replanning_never_schedules_work_in_the_past() -> None:
    entries = [ScheduleEntry(key=f"i{n}", est_minutes=30) for n in range(4)]
    offsets = build_schedule(entries, daily_minutes=60, earliest_day=5, start_weekday=MONDAY.weekday())
    assert min(offsets) >= 5
    assert offsets == sorted(offsets)


def test_daily_budget_derives_from_weekly_minutes_and_availability() -> None:
    assert daily_budget(210, ["mon", "wed", "sat"]) == 70
    assert daily_budget(0, None) == 15, "the floor keeps a session worth doing"
    assert daily_budget(3000, None) == 180, "the ceiling keeps a plan realistic"


def test_adherence_counts_on_time_late_and_overdue() -> None:
    rows = [
        ScheduleRow(key="a", est_minutes=30, scheduled_day=0, status="completed", completed_on=MONDAY),
        ScheduleRow(
            key="b",
            est_minutes=30,
            scheduled_day=1,
            status="completed",
            completed_on=MONDAY + timedelta(days=3),
        ),
        ScheduleRow(key="c", est_minutes=30, scheduled_day=2, status="pending"),
        ScheduleRow(key="d", est_minutes=30, scheduled_day=8, status="pending"),
    ]
    report = adherence(rows, starts_on=MONDAY, today=MONDAY + timedelta(days=4))

    assert report["counts"] == {"on_time": 1, "late": 1, "overdue": 1, "pending": 1}
    assert report["completed_items"] == 2
    assert report["behind_schedule"] is True
    assert report["adherence_percent"] == 25


def test_due_today_lists_today_then_oldest_slips() -> None:
    rows = [
        ScheduleRow(key="slipped_late", est_minutes=30, scheduled_day=1, status="pending"),
        ScheduleRow(key="today", est_minutes=30, scheduled_day=4, status="pending"),
        ScheduleRow(key="slipped_early", est_minutes=30, scheduled_day=2, status="pending"),
        ScheduleRow(key="done", est_minutes=30, scheduled_day=3, status="completed", completed_on=MONDAY),
    ]
    assert due_today(rows, starts_on=MONDAY, today=MONDAY + timedelta(days=4)) == [
        "today",
        "slipped_late",
        "slipped_early",
    ]


def test_scheduled_date_is_derived_not_stored() -> None:
    assert scheduled_date(MONDAY, 3) == date(2026, 3, 5)


# --------------------------------------------------------------------------------------
# API: dates, today's missions, re-planning
# --------------------------------------------------------------------------------------


def _learner_with_plan(client: TestClient, **profile: object) -> dict:
    register(client)
    goal = create_goal(client)
    answer_diagnostic_until_done(client, goal["id"])
    if profile:
        updated = client.patch("/api/me/profile", json=profile)
        assert updated.status_code == 200, updated.text
    generated = client.post(f"/api/plans/goals/{goal['id']}")
    assert generated.status_code == 200, generated.text
    return {"goal": goal, "plan": generated.json()["plan"]}


def _schedule(client: TestClient) -> dict:
    response = client.get("/api/plans/active/schedule")
    assert response.status_code == 200, response.text
    return response.json()


def test_the_plan_carries_dates_and_a_today_view(client: TestClient) -> None:
    _learner_with_plan(client, weekly_minutes=210, availability_days=["mon", "wed", "sat"])
    schedule = _schedule(client)

    assert schedule["starts_on"]
    items = schedule["weeks"][0]["items"] + schedule["weeks"][-1]["items"]
    assert items, "the schedule must expose the plan's items"
    assert all(item["scheduled_for"] for item in items)
    assert all(item["scheduled_for"] >= schedule["starts_on"] for item in items)

    # Items are placed in plan order and never before the plan's start date.
    ordered = [item for week in schedule["weeks"] for item in week["items"]]
    dates = [item["scheduled_for"] for item in ordered]
    assert dates == sorted(dates)

    assert "today" in schedule
    assert schedule["today"]["date"]
    assert isinstance(schedule["today"]["items"], list)
    assert schedule["adherence"]["counts"]


def test_availability_days_are_respected_in_dates(client: TestClient) -> None:
    _learner_with_plan(client, weekly_minutes=180, availability_days=["tue", "thu"])
    schedule = _schedule(client)
    for week in schedule["weeks"]:
        for item in week["items"]:
            day = date.fromisoformat(item["scheduled_for"])
            assert day.weekday() in {1, 3}, (item["objective_id"], item["scheduled_for"])


def test_today_lists_the_next_unfinished_missions(client: TestClient) -> None:
    _learner_with_plan(client)
    schedule = _schedule(client)
    assert schedule["today"]["items"], "a fresh plan must give the learner something to do today"

    first = schedule["today"]["items"][0]
    started = client.post(
        "/api/practice/sessions",
        json={
            "objective_id": first["objective_id"],
            "plan_item_id": first["id"],
            "size": 3,
        },
    )
    assert started.status_code == 201, started.text
    session = started.json()
    while session["item"] is not None:
        answered = client.post(
            f"/api/practice/sessions/{session['session_id']}/answers",
            json={"item_id": session["item"]["id"], "response": _correct_response(session["item"])},
        )
        assert answered.status_code == 200, answered.text
        session = answered.json()
    completed = client.post(f"/api/practice/sessions/{session['session_id']}/complete")
    assert completed.status_code == 200, completed.text

    after = _schedule(client)
    assert first["id"] not in [item["id"] for item in after["today"]["items"]]
    assert after["adherence"]["counts"]["on_time"] + after["adherence"]["counts"]["late"] >= 1


def test_rescheduling_moves_only_unfinished_work_and_is_idempotent(client: TestClient) -> None:
    _learner_with_plan(client)
    before = _schedule(client)
    items = [item for week in before["weeks"] for item in week["items"]]
    done_id = items[0]["id"]

    started = client.post(
        "/api/practice/sessions",
        json={"objective_id": items[0]["objective_id"], "plan_item_id": done_id, "size": 1},
    ).json()
    while started["item"] is not None:
        answered = client.post(
            f"/api/practice/sessions/{started['session_id']}/answers",
            json={"item_id": started["item"]["id"], "response": _correct_response(started["item"])},
        ).json()
        started = answered
    assert client.post(f"/api/practice/sessions/{started['session_id']}/complete").status_code == 200

    rescheduled = client.post("/api/plans/active/reschedule")
    assert rescheduled.status_code == 200, rescheduled.text
    body = rescheduled.json()
    assert body["moved"] >= 0

    after = _schedule(client)
    by_id = {item["id"]: item for week in after["weeks"] for item in week["items"]}
    assert by_id[done_id]["scheduled_for"] == next(i for i in items if i["id"] == done_id)["scheduled_for"]
    assert by_id[done_id]["status"] == "completed"

    second = client.post("/api/plans/active/reschedule")
    assert second.status_code == 200, second.text
    again = _schedule(client)
    assert [(i["id"], i["scheduled_for"]) for w in again["weeks"] for i in w["items"]] == [
        (i["id"], i["scheduled_for"]) for w in after["weeks"] for i in w["items"]
    ], "re-planning an unchanged plan must not keep shifting dates"


def test_missing_days_are_visible_rather_than_hidden(client: TestClient) -> None:
    """A plan whose dates have all passed reports overdue work — the learner is told, not shamed."""
    from app.db import session_scope
    from app.models import Plan

    _learner_with_plan(client)
    with session_scope() as db:
        plan = db.query(Plan).order_by(Plan.created_at.desc()).first()
        assert plan is not None
        plan.starts_on = plan.starts_on - timedelta(days=30)
        db.commit()

    schedule = _schedule(client)
    assert schedule["adherence"]["counts"]["overdue"] >= 1
    assert schedule["adherence"]["behind_schedule"] is True
    assert schedule["today"]["items"], "slipped work is offered today rather than skipped"
