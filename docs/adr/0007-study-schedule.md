# ADR 0007: The study schedule — dates are derived from a deterministic placement rule

Status: **accepted** (2026-10-11). Extends ADR 0005 (planning) and ADR 0004 (evidence).

## Context

The roadmap produced by `generate_roadmap()` was an ordered list of items grouped into weeks, with no
dates at all. Three consequences showed up as soon as the product was used:

* the dashboard could answer "what is next?" but not "what do I do **today**?" — the reference's daily
  missions (§6.7) had no data to stand on;
* a learner could not tell whether they were behind, because nothing recorded what was planned for
  when, or when it was actually finished;
* missed days were invisible. Work that should have happened last Tuesday stayed indistinguishable
  from work planned for next week, so "catch up" was not expressible.

The tempting shortcut — asking a model to schedule the plan — is wrong for the same reason the roadmap
itself is deterministic: a schedule decides what a learner does with their time, must be explainable
("this is on Wednesday because you chose Wednesdays"), and must be recomputable without drift.

## Decision

**Placement is a pure function; dates are derived, never stored twice.**

`app/learning/schedule.build_schedule(entries, daily_minutes, available_weekdays, earliest_day,
start_weekday)` assigns each item a day offset under five rules:

1. items keep plan order, and an item is never split across days;
2. a day holds at most `daily_minutes`; an item longer than a whole day gets a day of its own;
3. only the learner's available weekdays receive work (the offset → weekday mapping uses the plan's
   start weekday, so `["mon", "wed"]` is honoured for any start date);
4. no work is ever placed before `earliest_day`, which is how re-planning after missed days cannot
   silently schedule tasks in the past;
5. identical inputs produce identical offsets.

`daily_minutes` itself is derived: `weekly_minutes / number of available days`, clamped to 15–180
minutes so a budget can neither produce a two-minute session nor an unrealistic six-hour one.

**Storage.** `plans.starts_on` (the calendar anchor), `plan_items.scheduled_day` (offset),
`plan_items.completed_at` (when the learner actually finished it). The display date is
`starts_on + scheduled_day`. Nothing stores an absolute date per item, because re-planning would then
have to rewrite every row and could drift from the anchor.

**Re-planning** (`POST /api/plans/active/reschedule`) keeps completed items exactly where they are,
re-places the unfinished ones from today in plan order, and is idempotent: running it twice without
new activity changes nothing. It is recorded in `audit_log`, because "the plan changed" is something
the learner did and the system should be able to explain later.

**Adherence, not gamification.** Every item is classified as on time / late / overdue / pending from
`scheduled_day` and `completed_at`. The interface shows counts and the amount of slipped work; there
are no streaks, scores or penalties. A learner who misses a week sees what slipped and can re-plan —
the reference explicitly forbids shaming learners for breaks (§6.9).

**Calibration.** The schedule payload reports planned minutes alongside **actual** minutes recorded
from completed practice sessions attached to the plan, so the estimates the planner produces can be
compared with reality instead of being trusted forever.

## Alternatives rejected

| Alternative | Why |
|---|---|
| Let the model schedule the week | Non-deterministic, unexplainable, and it would put a language model in charge of the learner's time — the same reason the roadmap is deterministic |
| Store an absolute `scheduled_for` date per item | Re-planning becomes a rewrite of every row; derivation from one anchor keeps the calendar consistent by construction |
| Let items span multiple days | Partial completion of a lesson/step is not meaningful here, and "1.4 items done" is not explainable |
| Assume the learner studies every day | The profile already asks which days are available; ignoring it made plans that are impossible to follow |
| Streaks, guilt copy, or an "overdue" badge with a penalty colour | Explicitly rejected by the reference: breaks are normal, and the product must not punish them |

## Consequences and limits (honest)

* The 15–180 minute clamps and the equal split of the weekly budget across available days are
  **placeholders**, not tuned values; they change how a plan feels and should be revisited with real
  usage.
* Adherence assumes a learner completes an item on the day they answer its last question; it cannot
  see partial work spread over several days, and it does not model holidays or breaks.
* Re-planning moves unfinished work forward, which can make a long-neglected plan look deceptively
  comfortable. The interface must therefore keep showing what slipped rather than only the new dates.
* The schedule is per plan. Two goals (when a second path exists) would produce two independent
  calendars that do not know about each other's study minutes — multi-path scheduling is FUTURE and
  must not be claimed from this single-path implementation.
