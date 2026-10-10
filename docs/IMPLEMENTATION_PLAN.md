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
| Backend vertical slice (auth → goal → diagnostic → roadmap → dashboard) | IN PROGRESS | see checkpoint table |
| Frontend slice | IN PROGRESS | see checkpoint table |
| Real local-model integration verified | BLOCKED (environment) | no local runtime installed in this sandbox; the adapter is tested against a mock local endpoint and a skip-if-unavailable integration test |

---

## 1. Checkpoint table

| # | Checkpoint | Status | Acceptance criteria | Evidence |
|---|---|---|---|---|
| 1 | Repository foundation | IMPLEMENTED | Reference committed unchanged; `AGENTS.md`; stack ADR; reuse audit; local-AI architecture; threat model; CI workflow | commit `docs: foundation` |
| 2 | Core application skeleton | see below | App boots, config validated at startup, migrations apply, auth works, tests pass | `pytest -q` |
| 3 | Learning journey slice | see below | Goal → diagnostic → validated roadmap → dashboard next action, end to end via API and UI | `pytest -q`, `npm test` |
| 4 | Local AI tutor | see below | Tutor is grounded in curriculum, output validated, local-only enforced, explicit failure when unavailable | `pytest -q -k ai` |
| 5 | Learning outcomes | PARTIAL | Quizzes with deterministic grading, evidence persistence, mastery estimates, adaptive next action | `pytest -q -k mastery` |
| 6 | Hardening | NOT STARTED | Security review, dependency/licence audit, accessibility, performance, deployment docs | — |

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
