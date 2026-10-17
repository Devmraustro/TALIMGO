# ADR 0006: The mastery evidence boundary — only practice, assessment and project evidence counts

Status: **accepted** (2026-10-11). Extends ADR 0004 and ADR 0005. Model version: `mastery-v2`.

## Context

ADR 0005 decided that the starting check produces **planning** evidence and must not touch the
mastery model. The implementation did not enforce that boundary: `replay()` folded every evidence
record it was given, so diagnostic answers — written with `kind="diagnostic"` — counted as ordinary
unassisted successes and failures.

Independent review confirmed the defect and its consequences:

* three correct starting-check answers spaced ≥ 3 days apart promoted an objective to `retaining`
  with a stability of 3+ days and a retrievability curve, without the learner ever practising it;
* two wrong starting-check answers demoted a genuinely `retaining` objective to `acquiring`;
* a correct starting-check answer *extended* stability and pushed the review date back;
* because the estimate is cached in `mastery_estimates`, every learner who had taken the check held
  a wrong projection computed by the buggy fold.

A starting check is a single, unannounced probe at the very beginning of a path. It is weak evidence
even when answered correctly — the learner has no history with the system, may guess, and the items
are a fixed authored set. It is decisive for *where to start*, which is why ADR 0005 keeps it, and
worthless for *how well something is known*, which is why it must not move mastery.

## Decision

**One rule, at one boundary.** The mastery fold consumes only evidence whose kind is
*an attempt at the objective itself*:

```python
MASTERY_EVIDENCE_KINDS = {"practice", "assessment", "project"}
```

`diagnostic` is recorded, reported and used for placement and planning, and is **excluded from the
fold entirely**:

1. it cannot increment `unassisted_successes`;
2. it cannot establish `has_delayed_success`;
3. it cannot create, extend or shrink `stability_days`;
4. it cannot refresh `last_evidence_at` (so it cannot delay a review that is due);
5. it cannot cause demotion;
6. consequently, an objective whose only evidence is the starting check has **no estimate at all**,
   and `phase_for()` reports it as `unseen`.

The exclusion is implemented once, in `mastery.replay()`, so every caller — the API, the planner,
the recompute endpoint, scripts and tests — inherits it. `mastery.affects_mastery(kind)` is the
single predicate; callers that need to reason about the boundary (cache completeness, reporting)
call it rather than re-implementing the rule.

**Version bump to `mastery-v2`.** The parameters are unchanged; the fold's input is not. ADR 0004
requires that a change in the algorithm be identifiable, and cached rows must never be trusted across
it. Any row whose `model_version` is not `mastery-v2` is stale and is rebuilt by replaying evidence
(`load_estimates`), and a full recompute **prunes** rows the new fold no longer produces — otherwise
a diagnostic-only objective would keep a phantom `retaining` cache row and force a rebuild on every
read.

**What is deliberately preserved:**

* every diagnostic answer is still persisted as `Evidence` with `kind="diagnostic"` and remains
  visible in `/api/practice/progress/evidence`, the dashboard's recent-evidence list, and reporting;
* placement (`_placement`) still reads `DiagnosticResponse` rows and is unchanged;
* the provisional-known planning rule (ADR 0005) still turns a hard correct starting-check answer
  into a short `assess` confirmation check with no lesson attached;
* the confirmation check is *not* mastery either: it produces `assessment` evidence, which is
  mastery-bearing, but promotion still requires three unassisted successes including a ≥ 3-day gap.

## Alternatives rejected

| Alternative | Why |
|---|---|
| Keep folding diagnostics but cap their weight (e.g. count as 0.5 success) | A fractional "success" is not explainable to a learner and has no evidence behind it. Counters are integers for a reason. |
| Record diagnostic evidence with `assisted=True` to neutralise it | Abuses a field that means "the learner used a hint"; it would corrupt reporting and the evidence model. |
| Create an `acquiring` estimate so the objective appears in mastery listings | Conflates "we saw an answer" with "there is something to measure". The dashboard already shows diagnostic evidence separately, and the roadmap shows the confirmation check. |
| Delete diagnostic evidence to keep the fold clean | Destroys the placement and planning signal ADR 0005 depends on, and violates "evidence is the source of truth". |
| Bump the version but patch cached rows in place | Patching derived state contradicts ADR 0004: estimates are rebuilt from evidence or they are wrong. |

## Consequences and limits (honest)

* Learners who completed a starting check under `mastery-v1` see their first mastery estimate appear
  only after real practice — which is the intended behaviour, but it *is* a visible change and must
  be described in the release notes rather than slipped in.
* The boundary is a policy on a string field. A future kind (say `transfer` or `self_report`) is
  excluded by default and must be added deliberately, with a test; that is the safe direction.
* Diagnostic items remain a small, fixed authored pool. Nothing here fixes guessing; it only prevents
  guessing from being stored as mastery.
* `mastery_estimates` rows for diagnostic-only objectives are deleted on recompute. Evidence rows are
  never deleted.
