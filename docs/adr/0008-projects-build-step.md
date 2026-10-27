# ADR 0008: Projects — the BUILD step is an artefact checked against an authored rubric

Status: **accepted** (2026-10-27). Extends ADR 0004/0006 (evidence) and ADR 0005 (planning).

## Context

The learning loop promises five moves — learn, practise, check, **build**, review — but only four
existed. Objectives authored with `kind: "project"` produced a `build` step in the roadmap and
then nothing: no brief to work from, no place to submit, no way for the step to complete, and no
evidence. A build objective could also be quietly downgraded by the planner into a 10-minute
confirmation quiz when the starting check suggested the learner already knew the material — the
exact opposite of the product claim that capability is demonstrated by producing something.

Two shortcuts were rejected. LLM grading of free-form artefacts would put a non-deterministic
judge inside the mastery loop (and the local model is optional infrastructure, not a dependency
of the evidence model). Pure self-certification ("I did it" tick-box) would make `project`
evidence meaningless next to unassisted quiz success.

## Decision

**A project is authored curriculum data: a brief plus a rubric, checked deterministically.**

* Curriculum objectives with `kind: "project"` may carry a `project` spec: stable id,
  bilingual title/brief, a rubric of criteria (each `required` or optional), minimum artefact
  and reflection lengths, estimated minutes. The spec is loaded into the `projects` table by the
  curriculum loader exactly like lessons and items.
* A submission (`project_submissions`) carries the artefact text, a reflection, and the
  learner's rubric attestations. Acceptance is a pure rule: **every required criterion
  attested, artefact length ≥ minimum, reflection length ≥ minimum**. The response lists the
  exact gaps with stable codes (`rubric:<criterion-id>`, `artifact:minimum_length`,
  `reflection:minimum_length`) so "needs work" is actionable, never a judgement.
* `needs_work` records **no mastery evidence**. The **first** acceptance per (user, objective)
  records exactly one `kind="project"` success (ADR 0006 already reserves the kind); later
  acceptances record none, so resubmitting cannot farm mastery. An acceptance also completes
  the matching pending `build` plan item when one is named.
* **The planner never downgrades a build objective to a quiz.** Provisional knowledge and
  partial practice evidence keep the step a `build` until the objective is confirmed; only then
  does ordinary spaced review apply. The artefact is the demonstration.
* Honesty boundary: v1 verifies *that* the learner produced a substantial artefact and attests
  each criterion; it does not semantically verify the artefact. That limitation is stated in the
  learner-facing copy and here. Stronger checks (running learner code, model-assisted rubric
  review) are future, separately-reviewed changes — any model involvement stays advisory and
  local-only (ADR 0002), never the acceptance rule.

## Consequences

* The full loop is implemented end-to-end; both authored paths end in a project objective.
* Submissions are part of the account export and are erased on account deletion.
* Self-attestation can be gamed by a determined learner; the mitigation is structural (one
  evidence event, minimum lengths, reflection requirement, and mastery still needing a second,
  spaced, unassisted success of another kind) rather than a promise of semantic verification
  the system does not make.
