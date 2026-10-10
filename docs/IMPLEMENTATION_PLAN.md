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
