# ADR 0004: Deterministic evidence-based mastery model v1

Status: **accepted** (2026-10-10). Parameters are **placeholders to be validated**, not tuned values.

## Context

Mastery drives the learner's next action, so it must be explainable, testable, recomputable, and never
delegated to a language model. The reference requires that lesson completion never counts as mastery,
that self-reported confidence never places a learner, and that estimates are provisional and revisable
(master reference §6.2, §6.6). The ITS/retrieval literature supports evidence from unassisted, delayed
and transfer performance rather than exposure (master reference §4.2, §22.3).

## Decision

**Model version:** `mastery-v1`. One active model, identified together with its parameters. An estimate
carrying any other version is **rejected** as stale input rather than mixed.

**Unit of knowledge:** an *objective* — a stable, assessable learning target that content references
rather than owns. A material change in what must be learned creates a new objective.

**Evidence** (persisted; the source of truth):

```
(learner_id, objective_id, outcome ∈ {success, failure}, assisted: bool,
 kind ∈ {diagnostic, practice, assessment, project}, occurred_at, source_ref)
```

**Replay:** evidence is folded per objective in `(occurred_at, id)` order, so the result never depends
on arrival order and late evidence is absorbed correctly.

**Derived state per (learner, objective):**

| Field | Meaning |
|---|---|
| `phase` | `unseen` (no estimate) · `acquiring` · `retaining` |
| `unassisted_successes` | Count of unassisted successes (the only kind that can promote) |
| `has_delayed_success` | A success with a gap ≥ 3 days from the previous unassisted success |
| `stability_days` | `retaining` only: days until recall probability is expected to fall to 0.9 |
| `retrievability(now)` | `exp(-elapsed_days / stability_days)`, derived, never stored |
| `needs_review` | `retaining` and `retrievability(now) < 0.9` |

**Transitions (deterministic):**

1. `success` + not assisted → increments `unassisted_successes`; if ≥ 3 **and** a delayed success exists →
   `retaining`; else `acquiring`.
2. `success` + assisted → recorded, does **not** promote; keeps the current phase.
3. `success` while `retaining` → stability extended from the observed gap since the previous unassisted
   success: `stability = clamp(max(previous_stability, gap_days) * 1.5, 0.5, 365)`.
4. `failure` while `acquiring` → stays `acquiring`; the failure is evidence of *not yet learned*, not a
   lapse (a failed first attempt is not decaying knowledge).
5. `failure` while `retaining` → `stability = max(0.5, stability / 2)` and `failures_while_retaining` is
   incremented; **two** such failures demote the objective to `acquiring` with a recorded reason.
6. Self-reported confidence is stored separately and **never** changes phase or placement.

**Purity:** the model takes `now` as an argument, performs no I/O, uses no randomness, and imports
nothing from the web, database or AI layers (enforced by an import test).

**Mastery states exposed to the learner** follow the reference vocabulary (§6.6.2) and are always shown
with the evidence that produced them.

## Alternatives rejected

| Alternative | Why |
|---|---|
| Let an LLM judge mastery from conversation | Non-deterministic, unexplainable, untestable, and it would make the tutor the system of record |
| Completion-based percentages | Explicitly prohibited by the reference: completion is not capability |
| Bayesian knowledge tracing or a bandit-based difficulty model now | Attractive but requires calibration data we do not have; a wrong prior is worse than an explainable rule. Revisit with recorded evidence (FUTURE) |
| Direct FSRS stability for objectives | FSRS targets flashcards; objectives are coarser and include transfer requirements. Revisit for the review scheduler with its own ADR |

## Consequences and limits (honest)

- The thresholds (3 unassisted successes, 3-day delay, 0.9 retrievability, ×1.5 extension, ÷2 on failure)
  are **placeholders** awaiting validation against real learner evidence; changing any of them is a
  model-version change requiring recomputation of stored estimates.
- The model cannot detect guessing; a fast, correct answer with no working shown counts as unassisted
  success. Mitigated by item pools, delayed checks and transfer requirements — not eliminated.
- Estimates are stored for read performance but are always recomputable from evidence; if they disagree,
  evidence wins and the estimate is rebuilt.
