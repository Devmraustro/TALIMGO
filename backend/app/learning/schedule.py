"""Deterministic study schedule: turning an ordered plan into dated study days.

Why this is a separate, pure module: the roadmap is a *sequence*, but a learner lives in a
calendar. Assignment of work to days must be reproducible (same plan + same availability → same
dates), explainable (a learner can see why a task landed on Tuesday) and cheap to redo when a
learner misses days. No clock, no randomness, no I/O — ``today`` is always an argument.

Rules (documented so a reviewer can check them):

1. Items are placed **in plan order**; an item is never split across days.
2. A day holds at most ``daily_minutes`` of planned work. An item longer than a whole day gets a
   day of its own rather than being split or dropped.
3. Only days in ``available_weekdays`` receive work. An empty set means "any day".
4. Day offsets are relative to ``starts_on`` and never earlier than ``earliest_day`` (used when
   re-planning work that is already in the past).
5. The result is a list of day offsets parallel to the input entries, so callers keep their own
   identity/order and nothing depends on dictionary ordering.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Literal

ScheduleStatus = Literal["on_time", "late", "overdue", "pending"]

# A day's budget is clamped: below 15 minutes a session is not worth scheduling, above 180 the plan
# stops being realistic for a self-study product.
MIN_DAILY_MINUTES = 15
MAX_DAILY_MINUTES = 180
DEFAULT_STUDY_WEEKDAYS = (0, 1, 2, 3, 4, 5, 6)  # Monday = 0, matching date.weekday()


@dataclass(frozen=True)
class ScheduleEntry:
    """One planned piece of work. ``key`` is opaque to the scheduler."""

    key: str
    est_minutes: int


@dataclass(frozen=True)
class ScheduleRow:
    """A placed item plus what happened to it, for adherence accounting."""

    key: str
    est_minutes: int
    scheduled_day: int
    status: str
    completed_on: date | None = None


def daily_budget(weekly_minutes: int, available_weekdays: tuple[int, ...] | list[int] | None) -> int:
    """Minutes per study day implied by the learner's weekly budget and availability."""
    days = max(1, len(tuple(available_weekdays or DEFAULT_STUDY_WEEKDAYS)))
    budget = round(max(0, weekly_minutes) / days)
    return max(MIN_DAILY_MINUTES, min(MAX_DAILY_MINUTES, budget))


def _next_available_day(day: int, available: frozenset[int], earliest_day: int, start_weekday: int) -> int:
    """First day offset >= ``max(day, earliest_day)`` whose weekday the learner can study on.

    ``start_weekday`` is the weekday of ``starts_on`` (Monday = 0): an offset's weekday is
    ``(start_weekday + offset) % 7``. Bounded by construction — at most 7 steps, because an empty
    availability set is normalised to "any day".
    """
    candidate = max(day, earliest_day)
    for _ in range(8):
        if not available or ((start_weekday + candidate) % 7) in available:
            return candidate
        candidate += 1
    return candidate


def weekday_set(availability_days: list[str] | None) -> frozenset[int]:
    """``["mon", "wed"]`` → ``{0, 2}``; empty or unknown input means every day."""
    mapping = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
    days = {
        mapping[day.strip().lower()[:3]]
        for day in (availability_days or [])
        if day.strip().lower()[:3] in mapping
    }
    return frozenset(days) if days else frozenset(DEFAULT_STUDY_WEEKDAYS)


def build_schedule(
    entries: list[ScheduleEntry],
    *,
    daily_minutes: int,
    available_weekdays: frozenset[int] | None = None,
    earliest_day: int = 0,
    start_weekday: int = 0,
) -> list[int]:
    """Day offset for each entry, in input order."""
    available = available_weekdays if available_weekdays is not None else frozenset(DEFAULT_STUDY_WEEKDAYS)
    budget = max(MIN_DAILY_MINUTES, min(MAX_DAILY_MINUTES, daily_minutes))
    day = _next_available_day(earliest_day, available, earliest_day, start_weekday)
    used = 0
    offsets: list[int] = []

    for entry in entries:
        minutes = max(1, entry.est_minutes)
        if used > 0 and used + minutes > budget:
            day = _next_available_day(day + 1, available, earliest_day, start_weekday)
            used = 0
        offsets.append(day)
        used += minutes
        if used >= budget:
            day = _next_available_day(day + 1, available, earliest_day, start_weekday)
            used = 0
    return offsets


def scheduled_date(starts_on: date, day_offset: int) -> date:
    return starts_on + timedelta(days=day_offset)


def adherence(rows: list[ScheduleRow], *, starts_on: date, today: date) -> dict[str, object]:
    """How the plan is actually going, from scheduled days and completion dates.

    ``on_time``/``late``/``overdue`` are the only categories: a completed item is judged by the date
    it was completed against the day it was planned for; an unfinished item whose day has passed is
    overdue. Nothing here is a score or a streak — it is what happened, for the learner to see.
    """
    counters = {"on_time": 0, "late": 0, "overdue": 0, "pending": 0}
    planned_minutes: dict[str, int] = {"on_time": 0, "late": 0, "overdue": 0}
    for row in rows:
        due = scheduled_date(starts_on, row.scheduled_day)
        if row.completed_on is not None:
            if row.completed_on <= due:
                counters["on_time"] += 1
                planned_minutes["on_time"] += row.est_minutes
            else:
                counters["late"] += 1
                planned_minutes["late"] += row.est_minutes
        elif due < today:
            counters["overdue"] += 1
            planned_minutes["overdue"] += row.est_minutes
        else:
            counters["pending"] += 1

    total = len(rows)
    finished = counters["on_time"] + counters["late"]
    return {
        "counts": counters,
        "minutes": planned_minutes,
        "total_items": total,
        "completed_items": finished,
        "adherence_percent": round(100 * counters["on_time"] / total) if total else 0,
        "behind_schedule": counters["overdue"] > 0,
    }


def due_today(rows: list[ScheduleRow], *, starts_on: date, today: date) -> list[str]:
    """Keys that are due today, followed by keys that have slipped (oldest slip first)."""
    due = [
        row
        for row in rows
        if row.completed_on is None and scheduled_date(starts_on, row.scheduled_day) == today
    ]
    overdue = [
        row
        for row in rows
        if row.completed_on is None and scheduled_date(starts_on, row.scheduled_day) < today
    ]
    overdue.sort(key=lambda row: (row.scheduled_day, row.key))
    return [row.key for row in due] + [row.key for row in overdue]
