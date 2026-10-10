# TALIMGO implementation plan

**Status labels:** CONFIRMED · PROPOSED · UNVERIFIED · IMPLEMENTED · TESTED · BLOCKED · FUTURE
**Rule:** an item is only `IMPLEMENTED` when the code exists, and only `TESTED` when the check was
executed and its result observed. Evidence lines record the command actually run.

Last updated: 2026-10-10.

---

## 0. Where the project stands

| Item | Status | Evidence |
|---|---|---|
| Product reference committed to the repository | IMPLEMENTED | `TALIMGO_MASTER_REFERENCE.md`, sha256 `d9c337d38ab0a5dbeaef206273c0619821b7874908a18e71657ce4439a84eace` |
| Engineering rules recorded | IMPLEMENTED | `AGENTS.md` |
| Third-party audit of the three named candidates | IMPLEMENTED | `docs/OPEN_SOURCE_REUSE_AUDIT.md` |
| Stack decision | CONFIRMED (owner-delegated) | `docs/adr/0001-stack-and-repository-layout.md` |
| Local-only AI policy | CONFIRMED | `AGENTS.md` §2, `docs/adr/0002-local-ai-only.md` |
| Backend vertical slice (auth → goal → diagnostic → roadmap → dashboard) | TESTED | `pytest` 175 passed, 1 skipped; `ruff check app tests scripts` clean; `bandit -r app` clean; `alembic check` reports no drift — see §5 |
| Frontend slice | TESTED | `tsc --noEmit` clean; `vitest run` 16 passed, 1 skipped; `vite build` 259 kB JS (80 kB gzip); live-stack UI smoke test passes — see §5 |
| Local-only AI gate in CI | TESTED | `python scripts/check_no_external_ai.py` (66 files, 3 URL literals); proven to fail on a planted violation |
| Real local-model integration verified | BLOCKED (environment) | no local runtime installed in this sandbox; the adapter is tested against a mock local endpoint and a skip-if-unavailable offline integration test (`pytest -m local_model`), which skips with an explicit reason here |

---

## 1. Checkpoint table

| # | Checkpoint | Status | Acceptance criteria | Evidence |
|---|---|---|---|---|
| 1 | Repository foundation | TESTED | Reference committed unchanged; `AGENTS.md`; stack ADR; reuse audit; local-AI architecture; threat model | commit `086ba5f`; `TALIMGO_MASTER_REFERENCE.md` sha256 unchanged |
| 2 | Core application skeleton | TESTED | App boots, config validated at startup, migrations apply and match the models, auth works | commit `e30baea`; `tests/test_migrations.py`; `alembic upgrade head` + `alembic check` |
| 3 | Learning journey slice | TESTED | Goal → diagnostic → validated roadmap → dashboard next action, end to end through the API and the real interface | commit `1008a52`; `tests/test_api_journey.py`; live journey + UI smoke test (§5) |
| 4 | Local AI tutor | TESTED (mock endpoint), BLOCKED (real runtime) | Tutor grounded in retrieved curriculum, strict JSON validated, citation allow-list, local-only enforced, explicit failure when unavailable; no fallback path exists | commit `14c0be3`; `tests/test_ai_local_only.py`, `tests/test_tutor_local.py` |
| 5 | Learning outcomes | PARTIAL | Quizzes with deterministic grading, evidence persistence, mastery estimates, adaptive next action, confirmation checks for provisional knowledge; no project/portfolio work yet | `tests/test_grading.py`, `tests/test_mastery_model.py`, ADR 0005 |
| 6 | Hardening | PARTIAL | Lint, static security, dependency and licence gates, migration drift check, automated a11y linting; no manual accessibility audit, no penetration test, deployment docs still to write | `ci.yml`; `scripts/check_licences.py`; `scripts/check-licences.mjs` |

Each checkpoint is developed as: define observable behaviour and tests → smallest coherent change →
run focused tests → run lint/type/build/security → inspect the UI for UI changes → independent review
of the diff → fix findings → record commit and evidence.

---

## 2. Checkpoint 2–3 details (current work)

### Scope of the first vertical slice (CONFIRMED for this iteration)

In scope:

1. **Accounts and sessions** — register, login, logout, session introspection; bcrypt password hashing
   with SHA-256 pre-hash; server-side sessions stored hashed with expiry; login rate limiting;
   authorisation checks on every object access.
2. **Profile and preferences** — display name, interface locale, text direction, session length,
   weekly availability, accessibility flags (reduced motion, low bandwidth).
3. **Consent records** — separate records for account/learning, AI processing, analytics, marketing.
4. **Curriculum as data** — one authored path (Python programming foundations) with objectives,
   prerequisites, modules, lessons, practice items with verified keys, milestones and projects.
5. **Goal creation** — free-text goal plus outcome statement, target date (optional), constraints.
6. **Diagnostic assessment** — adaptive-by-difficulty item selection from the objective pool,
   deterministic grading, evidence emission, provisional placement with confidence labels.
7. **Roadmap generation and validation** — deterministic topological planning from the curriculum
   graph, filtered by evidenced mastery and constrained by the time budget; a validation gate that
   rejects prerequisite-order violations, missing objectives, cycle-breaking plans and time budgets
   outside tolerance; persisted plan version with a validation record.
8. **Dashboard** — current goal, single next action with rationale, recent evidenced progress, blockers.
9. **Practice and mastery** — practice sessions generating evidence; a deterministic, replayable
   mastery model with phases and stability; explainable evidence log per objective.
10. **Local AI tutor** — grounded in the retrieved objective/lesson context, structured output
    validated against a schema, local-endpoint-only, explicit failure when unavailable.

Explicitly **out of scope** for this iteration (FUTURE): spaced-repetition scheduling UI, project
workspace, billing, institutional features, spaced review analytics, multi-language content beyond
EN/AR strings, file upload for source material, fine-tuning.

### Acceptance criteria for the slice

| ID | Criterion | How it is checked |
|---|---|---|
| AC-1 | A new learner can register, sign in, and read their own session; another learner cannot read it | API tests including a negative cross-account test |
| AC-2 | Onboarding produces a stored goal and profile | API test |
| AC-3 | A diagnostic yields deterministic grading and per-objective evidence | Unit + API tests |
| AC-4 | A generated roadmap passes validation and is rejected when a prerequisite is violated | Unit test with a deliberately broken graph + API test asserting 422 |
| AC-5 | The dashboard returns exactly one primary next action with a rationale | API test |
| AC-6 | Practice answers create evidence; mastery is recomputable from evidence alone | Unit tests replaying evidence |
| AC-7 | Mastery rejects estimates with a stale `model_version` | Unit test |
| AC-8 | Tutor output is schema-validated; invalid output is rejected, never stored | Unit test with malformed model output |
| AC-9 | AI configuration rejects external hosts (e.g. `api.openai.com`) at startup | Config tests |
| AC-10 | AI calls go only to the configured local endpoint; unavailability produces an explicit error and no fallback | Adapter tests with a mocked transport |
| AC-11 | No forbidden provider host/SDK appears in the repository | Repository scan test |
| AC-12 | Migrations apply cleanly to an empty database | `alembic upgrade head` in CI |
| AC-13 | Frontend builds, type-checks, and renders the dashboard/next-action and RTL switch | `npm run build`, `npm test` |

---

## 3. Sequencing and dependencies

```
reference + rules  ──▶  stack decision  ──▶  backend skeleton ──▶  curriculum data
                                                                        │
   local-AI policy ──────────────────────────────▶ AI adapter ◀──────────┤
                                                                        ▼
                          auth ──▶ profile/goal ──▶ diagnostic ──▶ roadmap ──▶ dashboard
                                                              │
                                                              ▼
                                                    practice ──▶ evidence ──▶ mastery
                                                                        │
                                                                        ▼
                                                              tutor (grounded, local)
```

### Checkpoint 3 evidence — the probe that changed the product

Walking the journey against the running stack (script recorded in §5) showed that a learner who
answered **every** starting-check item correctly still received twelve full first-time lessons. The
planner had no concept of "already shown this". The fix — provisional knowledge yields a short
confirmation check, never mastery, and an `assess` step never carries lesson text — is recorded in
`docs/adr/0005-starting-check-evidence-not-mastery.md` and covered by two tests. This is the kind of
defect that only a real walk-through finds; unit tests around the old behaviour were all green.

Known dependencies and risks for this iteration:

| Risk | Impact | Handling |
|---|---|---|
| No local model runtime in the development sandbox | Cannot demonstrate real inference here | Adapter tested against a mock local endpoint; `pytest -m local_model` skips with a clear reason unless a real endpoint is configured; the policy guarantees are enforced by config/adapter tests instead |
| Curriculum authoring is the long pole | Slice could look thin | One complete path (Python foundations) authored as data with verified item keys; more paths are FUTURE |
| Breadth creep | Nothing finishes | Out-of-scope list above is binding for this iteration |

---

## 4. What remains incomplete (honest list)

- Only one curriculum path exists; it is small and needs subject review before any learner sees it.
- Mastery model parameters are **placeholders** to be validated against real evidence, not tuned inputs.
- Arabic content strings exist for the interface; the full RTL and Arabic typography audit is FUTURE.
- No spaced-repetition scheduler beyond due-date computation; no flashcards UI.
- No project workspace, rubrics editor, or portfolio export.
- No billing, subscription, or institutional features.
- Accessibility: automated checks only; no manual screen-reader pass, no external audit.
- No penetration test; the threat model lists what is untested.
- Real-model quality evaluation (accuracy, hallucination, Arabic quality) is FUTURE and requires a
  local runtime plus a versioned evaluation set.

---

## 5. Verification log — 2026-10-10

Every command below was executed in this workspace; the output shown is the observed output.

| Check | Command | Observed |
|---|---|---|
| Backend tests | `cd backend && .venv/bin/python -m pytest` | `175 passed, 1 skipped, 8 warnings in 27.75s` (the skip is the offline local-model test, with an explicit reason) |
| Determinism of ordering | `PYTHONHASHSEED=0/12345/999 pytest tests/test_api_auth.py tests/test_api_journey.py` | `25 passed` in each run (a weekday-ordering bug that only appeared under some hash seeds was found and fixed) |
| Backend lint / format | `ruff check app tests scripts`; `ruff format --check app tests scripts` | `All checks passed!`; `58 files already formatted` |
| Static security | `bandit -q -r app` | `0` issues (a bidirectional-control-character finding in authored Arabic content and two `assert`-as-validation findings were fixed, not suppressed) |
| Migrations | `alembic upgrade head` then `alembic check` on a fresh database | upgrade creates 23 tables; `No new upgrade operations detected.`; `tests/test_migrations.py` also covers downgrade → upgrade |
| Frontend type check | `cd frontend && npx tsc --noEmit` | clean |
| Frontend tests | `npx vitest run` | 4 files passed, 1 skipped; 16 tests passed, 1 skipped |
| Frontend production build | `npx vite build` | `dist/index.html` 0.71 kB, CSS 6.36 kB, JS 259.42 kB (gzip 80.07 kB) |
| Live API journey | register → goal → 12-item adaptive diagnostic → plan → practice through the Vite proxy | `201, 201, placement {assumed_known: 5, likely_known: 7, needs_work: 0}, plan 200, validation ok: true`; 12 steps: 6 `practice`, 6 `assess` |
| Real-interface smoke test | `TALIMGO_UI_SMOKE=1 npx vitest run src/ui-smoke.test.tsx` against the running stack | `1 passed` (667 ms): the real sign-up form, the real goal form, then the engine's next action opens the starting check and the first question is served |
| Local-only AI gate | `python scripts/check_no_external_ai.py` | `passed (66 source files, 3 URL literals, no hosted providers imported or declared)`; planted `https://api.openai.com/...` + `import openai` → exit 1 with two violations |
| Dependency licences | `python scripts/check_licences.py`; `node scripts/check-licences.mjs` | `passed (47 distributions)`; `passed (186 packages)` |
| CI, first executed run | GitHub Actions run [`38093542327`](https://github.com/Devmraustro/TALIMGO/actions/runs/38093542327) on PR #1 | Frontend **pass** (20s), local-only AI gate **pass** (5s), backend **fail** (21s), dependency audit **fail** (22s) |
| CI after fixing what the run exposed | run [`38093832336`](https://github.com/Devmraustro/TALIMGO/actions/runs/38093832336) | **all four jobs pass**: backend 51s, dependency/licence audit 24s, frontend 19s, local-only AI gate 5s |

The first CI run failed for two reasons that local execution could not show, and both were fixed
rather than worked around: the suite imported shared helpers as `tests.conftest`, which only resolves
when `python -m pytest` puts the working directory on `sys.path` (the `pytest` console script CI uses
does not — `pythonpath` in `pyproject.toml` now makes it explicit); and `pip-audit` reported the
interpreter's seeded `pip`/`setuptools` instead of TALIMGO's dependencies, so the job now upgrades the
build tooling first and still fails on any real finding. The migration test also no longer hard-codes a
virtualenv path that cannot exist on a CI runner.

### Honest limitations of this evidence

* **No browser in the sandbox.** The UI walk-through is a jsdom *real-stack* test (real components,
  real forms, real API through the real proxy). It is not a substitute for a human review of layout,
  RTL rendering and screen-reader behaviour, which remains outstanding.
* **No local model runtime installed here**, so no real inference was executed in this environment.
  Everything around the model (endpoint policy, prompt construction, retrieval, schema validation,
  rejection paths, explicit failure) is tested against a mock local endpoint; quality evaluation
  against a versioned item set is FUTURE.
* **The skipped test is reported, not hidden**: CI runs `pytest -m local_model -rs` and shows the skip
  reason.
* Coverage percentages are not cited as evidence of correctness; no coverage number was measured.

---

## 6. Code-review round — four integrity findings (2026-10-10)

A review of the merged slice found four defects. Each was reproduced by a failing regression test
before being fixed; the tests stay in the suite.

| # | Finding | Fix | Regression tests |
|---|---|---|---|
| 1 | `start_practice()` accepted any `goal_id`/`plan_item_id`, so learner B could attach a session to learner A's plan item, and completion then ticked A's roadmap item off | ownership and consistency are validated before the session is created (`_resolve_practice_context`, `plan_item_for_user`); foreign references are reported as unknown (404) so existence is not disclosed, and inconsistent references inside the learner's own data as conflicts (409); completion re-checks ownership at the point of the write | `tests/test_authorisation_practice.py` (5 tests, including a pre-existing-session row pointing at a foreign item) |
| 2 | `answer_diagnostic()` graded and recorded any item, in any order, from any path | the submitted item must be the exact next item for the attempt, belong to the path of the attempt's goal and be diagnostic-eligible; all checks run before grading or writing, so a rejection leaves no response row, no evidence and no cursor movement | `tests/test_diagnostic_integrity.py` (6 tests; each asserts the database is byte-for-byte unchanged) |
| 3 | `build_grounding()` quoted any lesson id under any objective, corrupting the citation allow-list | a lesson belonging to another objective raises `GroundingMismatchError` before a prompt is built, and the endpoint answers 400; an *unknown* id still falls back to the requested objective's own lesson so a stale link cannot break tutoring | `tests/test_tutor_grounding.py` (5 tests, incl. proof the model is never called and no allowance is consumed) |
| 4 | `_placement()` only upgraded statuses, so an incorrect answer after a correct one was silently ignored | one explicit rule in `aggregate_placement()`: every answer is counted, any incorrect answer leaves the objective at `needs_work`, otherwise `assumed_known` when the hardest correct item was difficulty >= 3 and `likely_known` for easy-only; counts and the hardest difficulty are reported, and the rule text is returned with the placement | `tests/test_placement_aggregation.py` (9 tests: correct-then-incorrect, incorrect-then-correct, mixed difficulty, independent objectives, determinism, stored attempt) |

Committed as `fc361c9` (fixes and regression tests) and `504ec3a` (this record); CI run
`38095252098` on that head passed all four jobs (backend 59 s, dependency and licence audit 23 s,
frontend 16 s, local-only AI 6 s).

Verification after the fixes: backend **200 passed, 1 skipped** (the skip is still the offline
local-model test); `ruff check`/`ruff format --check` clean over `app tests scripts`; `bandit -r app`
0 findings; `alembic upgrade head` + `alembic check` report no drift; `scripts/check_no_external_ai.py`
and both licence checkers pass; frontend `tsc --noEmit` clean, 16 tests pass, production build
unchanged; and the live stack was re-walked through the dev proxy, where an out-of-order item now
returns 409 with the attempt unchanged and the completed check reports the new placement rule.

Still true: no local model runtime exists in this environment, so no real inference and no Arabic
model-quality evaluation has been performed here.

---

## 7. Hardening sprint (2026-10-11)

Each entry below follows the same protocol: failing regression test first, smallest correct fix,
focused tests, then the full battery. Nothing here is claimed as reviewed by a human; it is what the
automated gates and the recorded runs prove.

### 7.1 The mastery evidence boundary (ADR 0006, model `mastery-v2`)

**Defect.** `mastery.replay()` folded every evidence record, so `kind="diagnostic"` starting-check
answers counted as unassisted successes and failures. Three spaced correct starting-check answers
promoted an objective to `retaining` (with stability and a retrievability curve) and two wrong ones
demoted a genuinely retaining objective — a direct contradiction of ADR 0005, visible to learners
through `/api/practice/progress/mastery` and the dashboard.

**Fix.** One predicate, one boundary: `MASTERY_EVIDENCE_KINDS = {"practice", "assessment",
"project"}`; `replay()` drops every other kind before the fold, so a diagnostic can neither count,
establish a delayed success, touch stability, refresh `last_evidence_at` nor demote. Diagnostic-only
objectives therefore have no estimate at all. Model version bumped to `mastery-v2`; `load_estimates`
rebuilds any row carrying another version, and a full recompute prunes rows the new fold no longer
produces.

**Evidence.** `backend/tests/test_mastery_evidence_boundary.py` (10 tests): the declared boundary;
three spaced diagnostic successes producing no estimate; the fold being byte-identical with and
without diagnostic records; diagnostic failures unable to demote a retaining objective; a diagnostic
success unable to extend stability or delay review; determinism under shuffling; a diagnostic-only
learner having zero recorded mastery while diagnostic evidence is still listed; the provisional
confirmation check surviving on a plan with zero retaining objectives; a cached `v1` retaining row
being rebuilt away and pruned; and a practice-backed estimate being restamped `mastery-v2` with the
recomputed values. `tests/test_api_journey.py` was updated deliberately: `mastery_summary.recorded`
is now 0 after the starting check and ≥ 1 after the first practice answer.

Full suite after the change: **210 passed, 1 skipped**.
