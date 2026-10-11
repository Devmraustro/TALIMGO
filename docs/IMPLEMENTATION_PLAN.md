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

### 7.2 Practice-session lifecycle: an explicit completion target

**Defects.** (a) `POST /api/practice/sessions/{id}/complete` completed the session and marked its
roadmap item done unconditionally — the practice interface's *Back* action called it, so a learner
who answered nothing could tick a roadmap step off. (b) `PracticeStartIn.size` was never applied to
item selection and was passed per request to the read-only state builder, so a session started with
`size=2` reported `total=5` on the next `GET` and the "next question" could change between calls.
(c) There was no way to leave a session as distinct from completing it.

**Fix.** The session now carries its completion target as persisted state:

* `practice_sessions.target_items` (requested, clamped) and `practice_sessions.item_ids` (the
  resolved plan) are written once, when the session is created. The plan is the requested size
  clamped to the objective's item pool, ordered deterministically
  (`|difficulty - band|`, `difficulty`, `id`), so the session length and question order cannot move.
* `next_practice_item()` serves only the next unanswered question of that plan; answering a question
  that is not in the plan, or out of order, is refused (409) without recording anything.
* `complete_practice()` refuses (409) a session that is already finished or has unanswered planned
  questions, and an empty-pool session is refused at creation. Only a session that meets the target
  completes, and only then is the linked roadmap item marked `completed` (still ownership-checked).
* `abandon_practice()` + `POST /api/practice/sessions/{id}/abandon` leave a session: recorded answers
  and evidence are kept, the roadmap item stays `pending`, and the session can never be answered or
  completed afterwards.
* Answering the last question no longer auto-completes anything; completion is explicit and validated.
* `PracticeSessionOut` gained `status` and `target_items` (additive); the interface now shows
  *Finish session* only when the target is met, and its *Leave* action calls `abandon`.

**Evidence.** `backend/tests/test_practice_lifecycle.py` (9 tests): target persisted and stable across
`GET`; a target larger than the pool clamped to the pool; out-of-plan answers refused without
recording; untouched and partially answered sessions refused 409 with the roadmap item still
`pending`; a fully answered session completing exactly once; completion not establishing mastery;
abandonment preserving answers and leaving the item pending; completed sessions refusing further
answers and abandonment. Updated deliberately: `tests/test_api_journey.py` (a 1-of-3 completion is
now refused, then all questions are answered), `tests/test_authorisation_practice.py` (the positive
control answers the whole target; the foreign-plan-item test now satisfies the completion condition
so the ownership check is the only thing preventing the write). Frontend:
`frontend/src/components/PracticePanel.test.tsx` (2 tests) pins *leave → abandon* and
*finish → complete only when the target is met*.

Full suite after the change: **219 passed, 1 skipped**; `alembic upgrade head` + `alembic check` clean
with the new revision `8f1c2d4e6a70`.

### 7.3 Practice context: the goal ↔ path ↔ objective ↔ plan-item chain

**Gap.** `_resolve_practice_context()` checked ownership (goal, plan item) and objective agreement but
never that the goal and the plan item were on the **same learning path** as the objective. A caller
supplying one of this learner's own goals for a different path was accepted.

**Fix.** The resolver now walks the whole chain before anything is created: the goal must be the
learner's own *and* on the objective's path; the plan item must belong to the learner's plan, to that
goal and to the objective being practised; a plan item's own goal must also match the objective's
path. Foreign references keep answering with one 404 message per kind (existence is never disclosed),
inconsistencies inside the learner's own data stay 409, and every check runs before a session row or
evidence row exists.

**Evidence.** `backend/tests/test_practice_context_paths.py` (6 tests) builds a **synthetic second
path** — objective, item, goal, plan, plan item — because the authored curriculum still has one path:
a cross-path objective with this learner's goal is refused, a cross-path plan item is refused, a
consistent context on the synthetic path is accepted (positive control), a plan item whose own goal
belongs to the objective's path is accepted, foreign and never-existing identifiers are
indistinguishable, and a rejected context leaves zero sessions and zero evidence.

**Honest limit: multi-path support is UNVERIFIED.** The repository still contains a single authored
path (`python-foundations`). These tests pin the *validation* a second path will depend on; they do
not demonstrate that curriculum loading, roadmap generation, diagnostics or the interface behave
correctly with two or more paths. That remains work for when a second path is authored.

Full suite after the change: **225 passed, 1 skipped**.

### 7.4 Locale: educational content, not just chrome

**Gap.** The profile has supported `ar` since the first slice, but the API returned English content:
`objective_public`/`lesson_public`/`item_public` were called without a locale, both feedback paths
asked the serialiser for `"en"` explicitly, plan themes were generated with an empty `theme_ar`, and
every dashboard sentence the server composes (next action, evidence basis, blockers) was English-only.
An Arabic learner therefore read Arabic navigation around English lessons, questions, explanations and
rationales.

**Fix.** One documented rule, applied at the API boundary: *authenticated routes use the learner's
saved locale; public routes use `?locale=` then `Accept-Language` then English; a missing translation
falls back to English, never to an empty string.*

* `app/i18n.py` (new): locale normalisation (`ar-DZ` → `ar`), `Accept-Language` parsing with q-weights,
  `request_locale()`, and the server-side phrase table (EN/AR) for every sentence the backend writes —
  next-action titles, rationales, evidence explanations, blockers, and the placement note and rule.
* `app/deps.py`: `CurrentLocale` (authenticated) and `ContentLocale` (public, profile-aware when
  signed in) dependencies.
* Routers `curriculum`, `diagnostic`, `practice`, `plans`, `dashboard` pass the resolved locale to the
  serialisers and to the services; `assessment.answer_diagnostic`/`answer_practice` take a `locale` and
  localise feedback explanations and objective titles; the placement payload carries both the rendered
  sentence and a `rule_code`, so one stored placement can be shown in either language.
* `plans.generate_roadmap` now writes a real Arabic week theme (per-objective title fallback to
  English); `PathSummary` gained locale-resolved `title`/`summary` alongside the `_en`/`_ar` pairs.
* `progress.build_dashboard` localises the chosen next action through its `reason_code` (added to
  `NextAction`, which stays pure and translation-free) and composes the evidence basis in the
  learner's language.

**Evidence.** `backend/tests/test_localisation.py` (13 tests) asserts *actual returned values*, not
`dir="rtl"`: lesson title **and body**, every objective title and summary, public path summaries via
`?locale=ar` and via `Accept-Language`, diagnostic prompts and feedback explanation + objective title,
practice prompts and feedback, plan week themes, objective titles and rationales (generated, active and
by-id), the dashboard next action in both locales, an English learner still receiving English, the
documented fallback on a synthetic objective/lesson with empty `ar` columns, tutor grounding in Arabic
with language-independent citation ids, and answer keys still absent from item payloads in both
locales. Live walk (dev stack, Arabic profile): lesson, diagnostic prompt, placement note, plan theme,
rationale, dashboard action and public path titles all Arabic, while the reasoning above shows the
English path unchanged. The frontend already renders Arabic chrome and RTL from the profile locale; a
locale switcher in the interface is still missing (see the gaps list at the end of this section).

### 7.5 The study schedule: dated work, today's missions, and re-planning

**Gap.** The roadmap was an ordered list with no dates. A learner could not see what to do *today*,
could not tell whether they were behind, and days they missed simply disappeared: `PlanItem` had no
day, no completion timestamp, and nothing derived a calendar from the weekly budget or the learner's
available days.

**Fix.** A pure scheduler plus dates derived, never duplicated:

* `app/learning/schedule.py` (new, pure): `build_schedule()` places items in plan order into days of at
  most `daily_budget()` minutes (derived from the weekly budget and availability, clamped 15–180),
  never splits an item across days, only uses available weekdays (offset → weekday via the plan's start
  weekday), never schedules before `earliest_day` (so re-planning cannot place work in the past), and
  is deterministic — same inputs, same dates. `adherence()` classifies every item as on time, late,
  overdue or pending from `scheduled_day` + `completed_at`, and `due_today()` returns today's work
  followed by the oldest slips.
* Model/migration `9b2e4f6a8c10`: `Plan.starts_on`, `PlanItem.scheduled_day`, `PlanItem.completed_at`.
  Dates are derived (`starts_on + scheduled_day`) rather than stored per item, which is what makes
  re-planning a recomputation instead of a rewrite.
* `generate_roadmap()` computes the schedule at publication time; the practice-completion path records
  `completed_at` so adherence means something.
* API: `GET /api/plans/active/schedule` (weeks with dates, `today`, adherence counts, planned vs
  **actual** recorded minutes) and `POST /api/plans/active/reschedule` (re-place unfinished work from
  today; completed work keeps its date and is never touched; audited in `audit_log`; idempotent when
  nothing changed).
* Interface: a *Today's missions* card on the dashboard with a start button per item and an explicit
  count of slipped work rather than a streak or a scolding, plus per-item planned dates, adherence and
  re-planning in the roadmap view (EN/AR strings, RTL-safe markup).

**Evidence.** `backend/tests/test_schedule.py` (14 tests): the nine pure scheduler/adherence
properties and five API tests covering dates on the plan, availability respected in the dates (every
scheduled date falls on a chosen weekday), today's missions moving on after a completed item,
re-planning that leaves completed work and is idempotent, and a deliberately aged plan reporting
overdue work and offering it today. Frontend `src/components/TodayPanel.test.tsx` (5 tests).
Live walk: the Arabic learner's plan is scheduled at 70 minutes/day from 2026-10-11, completing one
mission flips adherence to `on_time: 1`, a re-plan moves 4 unfinished items and leaves the completed
one alone, and the recorded actual minutes come from the sessions themselves.

### 7.6 What this sprint did **not** do (honest gaps)

* Localisation: no interface language switcher yet (the profile can be changed through the API and the
  UI then follows); `tutor.reply` text depends on the local model honouring the prompt's language —
  unverifiable here (no runtime) and therefore unclaimed.
* Learning economy: no onboarding wizard beyond the existing profile fields, no lesson player with
  typed steps, no collaboration, no mobile app work (the interface is responsive and keyboard
  usable, but no device testing has been performed).
* Content: no automated curriculum import/migration path and no authoring review queue; the authored
  curriculum is still the single `python-foundations` path, so none of this sprint's work can be
  described as validated for multi-path or large-course operation.
* Security and performance: no formal penetration test, no load test, and no review by a human
  other than the automated gates listed below.

### 7.7 Baseline HTTP hardening

**Gap.** The API sent no hardening headers at all, and the test suite *documented* that as current
behaviour ("headers are absent") instead of asserting a policy.

**Fix.** `app/http_hardening.py` (pure header function + one middleware) registered as the outermost
layer, so successful responses, error responses and CORS preflight replies all carry the same policy:
`X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer`, frame-embedding protection twice
over (`X-Frame-Options: DENY` and CSP `frame-ancestors 'none'`), a considered CSP
(`default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; sandbox`), an
explicit `Permissions-Policy` switching off 23 unused browser features, and `Strict-Transport-Security`
**only on requests that arrived over HTTPS** — so local development over plain HTTP is unaffected and
HSTS is never sent where a browser would ignore it. The development-only Swagger UI keeps a separate,
minimal policy (it needs a CDN bundle); production serves no interactive docs at all, which the tests
assert rather than assume.

**Evidence.** `backend/tests/test_http_hardening.py` (11 tests, all passing) plus the replacement of the
old "header absent" test with a tripwire. The threat model's new section maps every header to the risk
it addresses and states what is *not* covered.

**Honest limit.** This is a checklist enforced by tests. It is not a penetration test, and it says
nothing about the reverse proxy, TLS configuration or rate limiting at the edge — those are deployment
items (`docs/DEPLOYMENT.md`).

### 7.8 Deployment, configuration and data maintenance

**Gaps.** No deployment guide existed. The README told a contributor to `cp ../.env.example ../.env`,
but `SettingsConfigDict(env_file=".env")` resolved against the *process working directory*, so a
backend started from `backend/` ignored the file the instructions created. Login attempts and sessions
accumulated with no documented way to prune them.

**Changes.**

* `docs/DEPLOYMENT.md` (new): production requirements, validated startup, PostgreSQL and migration
  expectations, HTTPS/reverse-proxy configuration (including the `X-Forwarded-Proto` that HSTS
  depends on), secrets, backup/restore, local-model isolation and egress restrictions, health checks,
  logs, per-limit resource table, systemd sketch, rollback and a first-deployment checklist. It states
  plainly that no PostgreSQL, proxy or TLS deployment has been exercised here.
* `app/config.py`: settings files are now read from **absolute** paths — `backend/.env` is
  authoritative, a repository-root `.env` is still merged (the previous layout keeps working), and
  `TALIMGO_ENV_FILE` overrides both. `.env.example` moved to `backend/.env.example`, documents every
  setting including the new ones, and a test fails if any `Settings` field is missing from it.
* `app/maintenance.py` (new): `python -m app.maintenance [--dry-run]` prunes login attempts (30 days)
  and sessions (30 days past expiry), idempotently, with retention as named constants and a report.
  Audit rows are deliberately **not** pruned — their retention is an owner policy decision, and the
  test suite asserts maintenance leaves them alone.

**Evidence.** `backend/tests/test_config_env_files.py` (5 tests: cwd-independence, precedence,
override, example/setting parity, placeholder-not-secret) and `backend/tests/test_maintenance.py`
(5 tests: exact retention, scope, dry run, idempotency, audit untouched).

### 7.9 Security review of session, request and resource handling

`app/request_guards.py` (new) adds two controls: mutating requests carrying a body must be
`application/json` (415 otherwise — a cross-site HTML form cannot produce that content type, so CSRF
does not rest solely on `SameSite=Lax`), and bodies are refused above `TALIMGO_MAX_REQUEST_BYTES`
(413; hard maximum 8 MiB) with chunked bodies on mutating methods refused (411) rather than read
unbounded. Session cookie flags are now asserted by tests (HttpOnly, SameSite=Lax, Path=/, Secure in
production). The per-learner model allowance became an atomic claim made **before** the model call
instead of a read-then-write check, closing a check-then-act race; the claim is deliberately not
refunded when a call fails, because the limit exists to bound resource use and retry pressure. (That
claim was only *half* true until §7.13 below: the reservation was durable against concurrency but not
against failure.) The
full review — including what was found, what changed and what remains owned by the deployment — is in
`docs/SECURITY_THREAT_MODEL.md`, "Security review of session, request and resource handling".

**Evidence.** `tests/test_request_guards.py` (8 tests), `tests/test_ai_quota.py` (5 tests including a
10-thread concurrency test asserting exactly the limit is granted), and three cookie tests in
`tests/test_security_basics.py`.

### 7.10 Export and deletion, verified end to end

`tests/test_account_lifecycle.py` (6 tests) builds a learner with a real history — profile, consent,
goal, completed diagnostic, generated plan, completed practice session and a tutor thread produced
through the actual tutor path with a mocked local transport — then asserts the export contains each
category and that deletion leaves zero rows in sixteen learner-owned tables while the curriculum is
untouched and still served publicly. Deletion was also checked to anonymise audit rows rather than
delete them, to refuse inexact confirmation phrases, and to leave a replayed cookie and a fresh sign-in
useless.

**A real bug was found and fixed by this work:** `delete_account()` iterated `select(TutorThread.id)`
(and three sibling queries) and accessed `.id` on each scalar, so **deleting an account that had ever
used the tutor raised `AttributeError` and returned HTTP 500** — the account was not deleted. The
existing test only deleted accounts without tutor history, which is why it passed. All four comprehensions
now use the scalar ids directly, and the regression test covers the tutor-history case.

### 7.11 Measurements (2026-10-11, this machine)

`backend/scripts/bench.py` builds a learner through the real API, then times the endpoints a learner
touches and counts SQL statements per request. Environment: Python 3.11.2, SQLite 3.40.1, Linux
x86_64, single process through `TestClient` (no network, no proxy), 12 samples per endpoint.

| Endpoint | median ms | p95 ms | SQL statements/request |
|---|---|---|---|
| `GET /api/dashboard` | 9.4 | 10.6 | 12 |
| `GET /api/plans/active` | 8.6 | 9.1 | 7 |
| `GET /api/plans/active/schedule` | 10.3 | 13.1 | 10 |
| `GET /api/curriculum/paths` | 5.9 | 6.5 | 3 |
| `GET /api/curriculum/lessons/{id}` | 6.6 | 6.8 | 4 |
| `GET /api/practice/sessions/{id}` | 7.8 | 8.1 | 7 |
| `GET /api/practice/progress/mastery` | 6.3 | 6.9 | 7 |
| `POST /api/practice/sessions/{id}/answers` (accepted) | 13.7 | — | 19 |
| `POST /api/practice/sessions/{id}/answers` (replayed item → 409) | 7.2 | — | 6 |

Database after one learner's full journey: **400 KiB across 22 tables** (largest: `items` 36 — the
authored curriculum, `learner_evidence` 15, `objectives` 12, `lessons` 12, `diagnostic_responses` 12).

Reading: there is no N+1 explosion (the dashboard is the heaviest at 12 statements for a summary,
next action, evidence list and mastery counts) and write-path cost is dominated by grading plus
evidence and estimate updates. Model request handling could **not** be measured: no local runtime
exists in this environment, so local-inference latency, tokens/second and concurrency behaviour remain
unmeasured and are not claimed. These are single-process SQLite figures on a development machine and
must not be presented as production capacity.

### 7.12 Accessibility: automated checks and what still needs a human

`frontend/src/accessibility.test.tsx` (13 tests, run by CI) covers what jsdom can check: every form
control has a programmatic label, every dashboard region is named by a heading, errors are announced in
a live region (`role="alert"`), the primary action is a real button reachable from the keyboard and the
form submits from the keyboard, `prefers-reduced-motion` and the in-app reduced-motion flag both
disable animation, a visible `:focus-visible` outline exists, Arabic flips direction to RTL, and the
Arabic string table covers every English key with every placeholder interpolated.

**Still requires manual/browser/screen-reader testing (not done, not claimed):** focus *order* across a
whole page and after dynamic updates; colour contrast against the real rendered theme; zoom and reflow
at 200–400%; virtual-cursor reading order and numeral/date presentation in Arabic; behaviour with an
actual screen reader (NVDA, VoiceOver, TalkBack); touch target sizes on a phone; and the teacher/admin
flows, which have no interface yet.

### 7.13 Making the model-allowance reservation actually durable (review round)

**Bug found by review.** The allowance was claimed on the *request* session, but the router commits
that session only after a fully validated reply has been stored. Every failure after the claim —
local runtime unreachable, HTTP error from the runtime, non-JSON or empty completion, a reply that
failed validation — ended in `Session.close()`, which rolls back. The slot therefore came *back*, and
the documented policy ("an attempted request counts") was untrue. Two tests had certified it: the
integration tests never asserted usage after a failure, and the unit test named
`test_a_failed_model_call_still_consumes_its_slot` never called a model at all.

**Fix.** `answer()` now (1) checks configuration, (2) builds grounding — so an unknown objective or a
lesson from another objective is refused before any quota is spent, (3) claims the slot through
`reserve_usage_committed()`, which uses its **own short session and commits it** before inference
starts, and only then (4) calls the local model and (5) persists the exchange on success. A dedicated
session is used precisely so the reservation cannot drag unrelated request state into a commit, and so
the request session can still roll back cleanly when the call fails. Concurrency safety is unchanged:
the claim is still a single conditional `UPDATE ... WHERE count < limit`.

Unvalidated exchanges remain unpersisted — nothing is written to `tutor_threads`/`tutor_messages`
until the reply has passed validation, so a failed attempt leaves no thread, no learner message and no
model output behind. A refused request (no consent, unknown objective, mismatched lesson, exhausted
allowance) consumes nothing; a *failed* request consumes one slot, which is the documented policy.

**Error mapping (P2).** `LocalModelResponseError` — HTTP error status, non-JSON body, empty
completion — had no handler in the tutor router, so it surfaced as an unhandled 500. It is now mapped
to **502** with a fixed, safe sentence: the upstream status line, response body, model output and any
credential-shaped string in it never reach the learner, while the detail goes to the server log. The
sibling 503 ("runtime did not answer") sentence was made equally generic, so neither branch discloses
the configured endpoint address or the transport exception class any more; tests assert that both
strings are free of internal detail.

**Feedback localisation (P4).** `_canonical_answer()` asked for the option label with a hard-coded
`"en"`, so an Arabic learner read an Arabic prompt, Arabic options and an Arabic explanation, then an
English "correct answer" line. The authored choices are code literals (`int`, `float`) that are
identical in both languages, which is why nothing caught it. The label is now resolved per locale with
an English fallback, while short-answer canonical values (`"15"`) and literal code tokens are returned
unchanged — translating those would change what the learner is told is correct.

**Evidence.** `tests/test_tutor_quota_durability.py` (11 tests) drives six genuine failure paths
through the real tutor API (unreachable runtime, HTTP 500 from the runtime including a
credential-shaped body that must not leak, non-JSON output, empty completion, a citation outside the
context, a prohibited claim). Each asserts the HTTP status, that no tutor exchange or thread was
stored, that `GET /api/tutor/usage` reports the slot as consumed, and that a follow-up with a limit of
one is refused with 429; plus the happy-path count, the "refused before the claim" cases (unknown
objective, mismatched lesson, missing consent consume nothing and never reach the model) and an
API-level concurrency test (two interleaved requests, limit 1 → exactly one 200, one 429, exactly one
model call). All six failure cases fail against the previous implementation and pass against this one.
`tests/test_feedback_localisation.py` (12 tests) covers the canonical answer in both locales —
including a synthetic item with genuinely different Arabic and English labels, because the authored
data cannot distinguish the bug — and asserts that short answers and code tokens pass through
untouched. The item-payload test in `tests/test_localisation.py` no longer contains a vacuous
`or True`: it now asserts the exact public field set, that no internal marker is serialised, and that
options expose only an id and a label.
