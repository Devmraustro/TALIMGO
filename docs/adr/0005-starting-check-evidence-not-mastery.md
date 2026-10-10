# ADR 0005: The starting check produces evidence, never mastery

Status: **accepted** (2026-10-10). Supersedes nothing; extends ADR 0004.

## Context

The first vertical slice was walked end to end against the running stack and produced a real product
defect: a learner who answered **every** starting-check item correctly still received twelve full
first-time lessons. The diagnostic had recorded correct answers, but the roadmap planner only knew two
things — "no evidence" and "retaining" — so a correct diagnostic answer was treated as no better than
a blank slate.

That wastes the learner's time, which the reference explicitly calls out as a failure mode (master
reference §6.4, §24.1: "the diagnostic exists to avoid re-teaching what is already known"). Simply
promoting diagnostic successes to mastery would be worse: mastery follows unassisted, spaced success
(ADR 0004), and a single item answered once proves recall, not retention. It also risks placing a
learner past material they only guessed.

## Decision

A correct starting-check answer on a **hard** item (item difficulty ≥ 3) marks that objective as
*provisionally known* for planning purposes only:

1. The objective stays in the plan — it is never silently dropped.
2. Its roadmap step becomes a short `assess` confirmation check (~10 minutes) instead of a full lesson
   or a full practice set.
3. That step deliberately carries **no lesson id**: a confirmation check must not be displayed next to
   the text that answers it. The plan validator enforces this (`E_ASSESS_WITH_LESSON`).
4. The mastery model is not touched. The objective still has to earn `retaining` through unassisted,
   spaced success, exactly like any other objective. A failed confirmation check simply routes the
   learner back to the lesson. *(Follow-up: this was intended but not enforced until **ADR 0006**
   excluded `diagnostic` evidence from the mastery fold and bumped the model to `mastery-v2`.)*
5. A correct answer on an **easy** item (difficulty ≤ 2) grants nothing: weak evidence is not
   evidence. Those objectives are planned as practice.

The same walk surfaced the interface consequence: practice sessions on an objective with no lesson
attached (including every `assess` step) show only the items, and the API therefore never attaches a
lesson to `assess` steps at all.

## Consequences

* A knowledgeable learner can move through material they already know without being re-taught, while
  still having to demonstrate it.
* Planning and mastery stay separate concerns: the plan uses provisional signals, the mastery model
  uses only durable evidence. Both remain deterministic and testable.
* `E_ASSESS_WITH_LESSON` fails the publication gate if a future change tries to attach lesson text to a
  confirmation check.
* The threshold (difficulty ≥ 3) and the check length (10 minutes) are **parameters of the planner, not
  tuned values**, recorded here so they can be revisited with real learner data.

## Evidence

* `backend/app/learning/roadmap.py` — `provisional_known` handling, `lesson_id=None`, validation errors.
* `backend/app/services/plans.py` — `_provisionally_known()` derives the set from recorded diagnostic
  answers (correct and difficulty ≥ 3).
* `backend/app/learning/mastery.py` — `MASTERY_EVIDENCE_KINDS`, `affects_mastery()`, the fold itself
  (ADR 0006).
* `backend/tests/test_mastery_evidence_boundary.py` — the boundary, the provisional check surviving
  it, and rebuild/prune of cached `v1` estimates.
* `backend/tests/test_roadmap_validation.py::test_provisionally_known_objectives_become_confirmation_checks`
* `backend/tests/test_api_journey.py::test_full_journey_goal_to_measured_progress` — a full-marks
  diagnostic must yield confirmation checks, not first-time lessons.
* Frontend: `plan.kind.assess` labels in `frontend/src/lib/i18n.ts` (EN/AR).
