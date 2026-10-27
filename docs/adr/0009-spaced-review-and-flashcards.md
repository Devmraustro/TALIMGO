# ADR 0009: Spaced review reuses the mastery forgetting model; flashcards never claim evidence

Status: **accepted** (2026-10-27). Extends ADR 0004 (mastery) and ADR 0006 (evidence boundary).

## Context

Mastery v1 already models forgetting (stability → retrievability decay) and flags objectives
whose recall has dropped, but the learner had no review surface: fading objectives showed up as
a dashboard count with nowhere to act. Meanwhile, "spaced repetition" products train with
self-graded flashcards — a useful study aid that must not be confused with the unassisted,
server-graded evidence this product's mastery claims rest on.

An external scheduler library was evaluated first, per the reuse rule in AGENTS.md:
`open-spaced-repetition/py-fsrs` (MIT, actively maintained). It was **not** adopted: FSRS ships
weights fitted on other populations' review logs; with no TALIMGO calibration data its advantage
over the existing stability model is unprovable, and running two forgetting models (one for
mastery, one for review) guarantees they eventually disagree about the same objective.
Revisit when real review logs exist to fit or at least validate weights against.

## Decision

**One forgetting model, two surfaces with different evidential weight.**

* **Review queue** (`GET /api/practice/review-queue`): derived from the same estimates as
  mastery. Confirmed objectives whose retrievability fell below threshold are `fading`;
  objectives with a single unassisted success whose stability window has elapsed are
  `confirmation_spaced`. Fading always outranks confirmation candidates; within a reason, the
  most-forgotten comes first. The ordering is a pure function in `app/learning/review.py`.
* **Review sessions** are ordinary practice sessions with `mode="review"` stored on the session.
  Answers record `kind="practice"` evidence exactly as before — review is a *reason* for the
  session, not a new evidence kind, so ADR 0006's boundary is untouched.
* **Flashcards** are a study aid over items the learner has already answered (seen-only is
  enforced server-side; rating an unseen item is an indistinguishable 404). Scheduling is a
  small SM-2-style ladder (`app/learning/review.py`, pure): again → 10 minutes, then 1/3/7/16/35
  day rungs scaled by rating. **A flashcard rating writes no evidence and cannot move mastery**;
  the UI says so in plain language. Ratings only schedule the next card showing.
* Flashcard state is part of the account export and is erased on account deletion.

## Consequences

* "What should I review?" and "what have I mastered?" can never contradict each other.
* The SM-2-lite ladder is deliberately simple and inspectable; if FSRS is adopted later, this
  ADR is superseded with calibration evidence attached, and the pure-module boundary keeps the
  swap local.
* Because flashcards carry no evidence, a learner cannot inflate mastery by self-rating — the
  failure mode that makes flashcard-first products' "mastery" claims untrustworthy.
