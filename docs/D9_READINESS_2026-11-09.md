# D.9 — Final stabilization, integration and production readiness (2026-11-09)

Status date: 2026-11-09. This report is the D.9 deliverable. It records what was executed in this
phase, what was verified, what is blocked, and what remains for the owner. It deliberately does not
claim production readiness: see §13 and §16.

---

## 1. Repository identity, branch, HEAD, git state

- Repository: `Devmraustro/TALIMGO` — https://github.com/Devmraustro/TALIMGO
- Working branch: `arena/244ad13e-talimgo` (session branch; Arena tracks it)
- HEAD: `9cbf05711b24e5c243b4ea02ffb2929ead14415f` (`9cbf057`, "feat: add deliberate production
  curriculum loading (#13)") — identical to `origin/main`; nothing is ahead of or behind `main`.
- `git ls-remote origin arena/244ad13e-talimgo` returns **empty** — the session branch has never been
  pushed, and D.9 pushed nothing either.
- Working tree (uncommitted, preserved exactly as found plus the D.9 changes in §5):
  - modified: `backend/app/db.py`, `backend/app/deps.py`, `backend/app/routers/admin.py`,
    `backend/app/routers/auth.py` (D.7 defects + fixes),
    `frontend/src/App.tsx`, `frontend/src/App.test.tsx`, `frontend/src/lib/i18n.ts` (D.9)
  - untracked: `backend/tests/test_auth_regression.py`, `test_authz_cross_user.py`,
    `test_config_isolation.py`, `test_learning_workflow.py` (D.7),
    `docs/D8_RECONCILIATION_2026-11-09.md`, `docs/RECOVERY_VERIFICATION_2026-11-09.md` (D.8),
    `docs/D9_READINESS_2026-11-09.md` (this file)
- No commits were made in D.9. The D.7/D.8 and D.9 changes remain in the working tree for the owner
  to review and commit (or not) at their discretion.

**Baseline claim vs. actual state (per the D.9 brief):** HEAD matches (`9cbf057`). Backend tests
**502 passed, 4 skipped** — matches. Frontend tests **76 passed, 1 skipped** (baseline 75/1 plus the
one D.9 regression test added). See §6/§7.

## 2. Initial audit findings

Read-only audit performed before any change, this phase:

- **Deployment configs:** root `vercel.json` (vite; `npm ci`/`npm run build` with `--prefix frontend`;
  `connect-src 'self'` CSP, `X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`,
  `Permissions-Policy`; SPA rewrite to `/index.html` for non-`/api` paths) and `frontend/vercel.json`
  (same security headers). `deploy/` contains `health-check.sh`, an nginx example + CI upstream
  (`deploy/nginx/`), systemd units and `stage-frontend.sh`. **There is no Dockerfile or
  docker-compose in this repository** (confirmed; recorded honestly — the repo previously expected
  Docker artifacts that do not exist on any reachable ref, see `docs/D8_RECONCILIATION_2026-11-09.md`).
- **CI (`.github/workflows/ci.yml`):** 7 jobs — backend (ruff/format/bandit/alembic/preflight/tests),
  PostgreSQL 16 integration (migrations, `postgres_smoke.py`, legacy-data rehearsal, **backup/restore
  rehearsal**), nginx TLS edge smoke, local-only AI gate, frontend (typecheck/build/bundle/vitest),
  Chromium browser journey + axe accessibility, dependency & licence audit. For `main` @ `9cbf057`,
  run `41536208912` (push) concluded **success — all 7 jobs** (verified read-only via `gh`).
- **Backend architecture:** routers are thin; logic in `app/services`, `app/learning` (pure, no I/O,
  no clock/randomness — invariants enforced by `tests/test_learning_purity.py`), `app/curriculum`
  (two validated paths: `python-foundations`, `frontend-foundations`), `app/ai` (local-only adapter +
  policy). Security-relevant modules: `app/http_hardening.py` (headers), `app/request_guards.py`
  (JSON-only mutations, declared-size caps), `app/serializers.py` (answer keys never serialised;
  ordering items deterministically shuffled).
- **Frontend architecture:** dependency-free shell; hash routing; `src/lib/api.ts` (same-origin
  relative `/api`, `credentials: "same-origin"`, honest "API not reachable" message); every panel
  calls real endpoints — **no mock data anywhere in `src/`**; empty states, loading states and error
  banners are implemented per panel (Dashboard/Flashcards/Practice/Progress/Projects/Roadmap/Today);
  shared `Feedback.tsx` renders grading feedback with `aria-live="polite"`.
- **API surface vs. frontend:** all 50 operations from the OpenAPI schema were inventoried; every
  `/api/...` URL the frontend calls resolves to a real operation (see §5 for the per-file mapping).
  No dead frontend calls, no dead frontend-only endpoints.
- **TODO/FIXME scan:** exactly one TODO-class comment in the whole repository —
  `backend/app/services/assessment.py:5`, adaptive bandit-style item selection, recorded as FUTURE
  in `docs/IMPLEMENTATION_PLAN.md` (deliberate; it needs calibration data that does not exist yet).
- **Module test-import scan:** every backend module is exercised either by a test module or by the
  HTTP API tests (routers are covered through `TestClient`, which is why direct imports read 0).
- **`AGENTS.md` rules honoured:** deterministic-first learning engine; AI output is a proposal;
  no hosted AI anywhere; licence policy (Braivo AGPL-3.0 — studied, not copied; LearnBuddy MIT —
  audited, not copied; FlameEducation — excluded); reuse policy.
- **Licence review for new work:** nothing third-party was introduced in D.9; the new code has no
  licence implications. No code was copied from anywhere.

## 3. Work completed this phase (D.9)

1. **Audit completion** (initial findings, above; API inventory; deployment audit — §12).
2. **Frontend logout defect fixed** — previously `signOut()` awaited `api.post("/api/auth/logout")`
   and then cleared local state. On a network failure or non-2xx the promise rejected **before** the
   local sign-out, leaving the learner on a screen whose actions all failed with an unhandled
   rejection (the D.7/D.8 fixed backend 204s, but the client never got there offline). Local sign-out
   now always happens; the server call is best-effort and a failure surfaces a clear, translated
   notice (`auth.logoutLocal`) instead of a crash. Regression test added.
3. **Full backend gate battery re-run with exit codes recorded** (ruff, format, bandit, licences,
   AI-policy, alembic on isolated SQLite, production preflight both directions, full pytest,
   local-model marker) — all green (§6).
4. **Full frontend gate battery re-run** (`npm ci` earlier; `tsc`, production build, bundle checks,
   vitest) — green, 76/1 (§7).
5. **Live end-to-end verification over real HTTP** — real uvicorn + isolated, migrated SQLite +
   curriculum loaded: 22/22 journey checks passed, including register → goal → diagnostic (idempotent
   restart) → placement → validated plan → practice ×2 → completion → evidence (14 rows, 12 diagnostic
   + 2 practice) → mastery read → logout → 401 (§10). Direct database assertions confirmed sessions
   revoked, plan validation `ok=1`, consents recorded.
6. **Local preview stack stood up** — API (`:8000`, isolated SQLite, AI disabled, random session
   secret in `/tmp`) and Vite dev server (`:5173`, `/api` proxied, `allowedHosts: true`). Not a
   deployment; ephemeral; for the owner to click through.
7. **Vercel read-only audit** performed with the connected integration (list_projects, get_project,
   list_deployments — §12). No settings, environment variables, domains, SSO or deployments were
   changed.

## 4. Bugs found and fixed (with root cause)

| # | Symptom | Root cause | Fix | Regression coverage |
|---|---|---|---|---|
| D9-1 | Clicking "Sign out" offline/on API failure left the learner stuck with an unhandled promise rejection; local session state not cleared | `App.signOut()` awaited the server call before clearing local state; no `catch` | Local sign-out in `finally`; best-effort server revoke; translated notice on failure (`auth.logoutLocal`, EN+AR) | `src/App.test.tsx` — "still signs the learner out of this device when the logout request fails" (asserts sign-in screen returns and the notice is shown) |
| — | (inherited, D.7) admin routes unreachable | `dependencies=[Depends(AdminUser)]` passed the `Annotated` alias, which FastAPI modelled as `*args/**kwargs` parameters → 422 before authorisation ran | Router-level `Depends(get_admin_user)` (`backend/app/routers/admin.py`) | `backend/tests/test_authz_cross_user.py`, `test_auth_regression.py` |
| — | (inherited, D.7) bearer-authenticated caller stayed signed in after logout | logout read only the cookie | Logout revokes the presented credential (cookie **or** Bearer) via `session_token_from_request` | `backend/tests/test_auth_regression.py` |
| — | (inherited, D.7) open transactions returned to pool on handler exceptions | `get_db()` yielded without rollback | Rollback on exception, always close | covered by suite + cross-user DB assertions |

No other functional defect was found this phase: panels correctly disable while busy, disable destructive
actions without input (account delete), deep-link via hash, and keep drafts in `localStorage`.
Repeated completion of a practice session is refused (409), abandon is final, and the diagnostic
start is idempotent — all re-verified live (§10).

## 5. Files modified / created this phase

Modified (D.9): `frontend/src/App.tsx`, `frontend/src/lib/i18n.ts`, `frontend/src/App.test.tsx`.
Created (D.9): `docs/D9_READINESS_2026-11-09.md` (this file).

Unchanged but load-bearing in the working tree (D.7/D.8, uncommitted, preserved):
`backend/app/db.py`, `backend/app/deps.py`, `backend/app/routers/admin.py`, `backend/app/routers/auth.py`,
`backend/tests/test_auth_regression.py`, `backend/tests/test_authz_cross_user.py`,
`backend/tests/test_config_isolation.py`, `backend/tests/test_learning_workflow.py`,
`docs/D8_RECONCILIATION_2026-11-09.md`, `docs/RECOVERY_VERIFICATION_2026-11-09.md`.

## 6. Backend verification results (commands actually executed)

| Gate | Command | Result |
|---|---|---|
| Lint | `ruff check app tests scripts` | All checks passed! |
| Format | `ruff format --check app tests scripts` | 114 files already formatted |
| Bandit | `bandit -q -r app` | clean |
| AI policy scan | `python scripts/check_no_external_ai.py` | passed (92 source files, 7 URL literals, no hosted providers imported or declared) |
| Licence policy | `python scripts/check_licences.py` | passed (50 distributions) |
| Migrations (isolated SQLite) | `alembic upgrade head` | clean to `d5b8e0f13a72` |
| Model/migration drift | `alembic check` | No new upgrade operations detected |
| Production preflight (correct config) | `scripts/check_production_config.py` | PASS (all 6 checks), exit 0 |
| Production preflight (SQLite) | same, `TALIMGO_DATABASE_URL=sqlite://…` | refused, exit 1 (expected) |
| Full suite | `TALIMGO_ENV=test TALIMGO_DATABASE_URL=sqlite:///./ci-test.db pytest --tb=no` | **502 passed, 4 skipped** in 155.00s (exit 0) |
| Skips honesty | `pytest -rs tests/test_deploy_shell.py tests/test_local_model_integration.py` | 3 Windows-only shims + 1 `local_model` (`TALIMGO_TEST_LOCAL_MODEL=1` not set) |
| pip-audit | `pip-audit --progress-spinner off` | No known vulnerabilities found |

Per-domain classification (all exercised by the suite; TEST evidence above):
auth/registration/session lifecycle (register, login, cookie+Bearer logout, expiry, revocation) —
Implemented+verified; RBAC/admin (`/api/admin/*`) — Implemented+verified (in-workflow fix);
profile/settings/consents/export/delete — Implemented+verified; goals — Implemented+verified;
diagnostic (idempotent start, deterministic adaptive selection, grading, placement provisional) —
Implemented+verified; plans (deterministic generation, validation, supersede, reschedule, adherence) —
Implemented+verified; lessons — Implemented+verified; practice/grading/completion/abandon —
Implemented+verified; flashcards/spaced review — Implemented+verified; projects/submissions —
Implemented+verified; evidence/mastery (replayable, model-versioned) — Implemented+verified;
dashboard/next-action (deterministic, localised) — Implemented+verified; tutor/AI consent/quotas/
grounding/schema validation — Implemented+verified (against a mock local endpoint and a fake local
HTTP server; real inference NOT VERIFIED); rate limiting (write, registration IP), request guards,
HTTP hardening, error handling — Implemented+verified. Nothing is missing at the API level for the
documented MVP journey.

## 7. Frontend verification results

| Gate | Command | Result |
|---|---|---|
| Type check | `npm run typecheck` (`tsc --noEmit`) | clean |
| Production build | `npm run build` | ✓ built in 1.40s — `dist/assets/index-*.js` 291.86 kB (gzip 88.45 kB), CSS 7.00 kB |
| Bundle integrity | `node scripts/check-bundle.mjs` + `src/bundle-check.test.ts` (10 tests) | passed (same-origin assets, no local/insecure host) |
| Component/unit tests | `npx vitest run` | **76 passed, 1 skipped** (the skip is the live-stack UI smoke test: requires the real API+web stack; CI's Chromium job covers it) |
| Licence policy | `node scripts/check-licences.mjs` | passed (185 packages) |
| npm audit (prod deps) | `npm audit --omit=dev` | 0 vulnerabilities |
| Live preview smoke | `curl` through Vite proxy | `/` 200; `/api/health` 200; `/api/auth/login` wrong-credentials 401 |
| Browser journey + axe | (CI only this phase) | **NOT EXECUTED locally** — Playwright Chromium download is blocked by the sandbox egress policy (`playwright install chromium` fails) and no system Chromium exists. CI job "Chromium browser journey and axe accessibility checks" is green on `main` @ `9cbf057` (run 41536208912). Local browser verification of D.9's logout change is covered instead by the new jsdom test |

Per-surface review (all pages: dashboard, goals, diagnostic, roadmap, lessons/practice, projects,
progress/mastery, flashcards, review, settings, help, admin — the last is not surfaced in the
interface by design and is exercised via the API/RBAC tests): every visible control calls a real,
tested endpoint; no mock data; no dead buttons found. RTL: `document.documentElement.dir` is driven
by the profile locale (`en`/`ar`), Arabic strings exist for the whole interface (parity is enforced
by `src/accessibility.test.tsx` — 13 tests including the STRINGS coverage check), `dir` switching is
tested. The full Arabic typography/RTL audit remains documented as FUTURE in `docs/IMPLEMENTATION_PLAN.md`
— it is a design programme, not a missing wire. Keyboard/`aria-live` behaviour: error banners use
`role="alert"`, feedback uses `aria-live="polite"`, forms have labels, busy states disable submits.
No manual screen-reader pass was performed (documented limitation).

## 8. Security checks

Attack-surface review against the D.9 brief: authn/authz and session handling (cookie attributes
`HttpOnly`, `SameSite=Lax`, `Path=/`, `Secure` in production — asserted by
`tests/test_security_basics.py` / cookie tests; sessions stored hashed, revocable); RBAC
(admin 422 defect found and fixed in D.7, re-verified); cross-user isolation (independent authenticated
clients + direct SQL assertions — `tests/test_authz_cross_user.py` 23 tests, `test_auth_regression.py`,
`test_learning_workflow.py`); CSRF (SameSite=Lax + JSON-only mutating methods + declared-size caps,
`app/request_guards.py`); CORS (explicit allow-list; wildcards refused at startup); rate limits
(per-account writes 120/min, registration 10/IP/hour, lockouts — `tests/test_registration_rate_limits.py`,
`test_write_rate_limits.py`); SQLi (SQLAlchemy parameterised throughout; no raw SQL f-strings — reviewed);
XSS (React text-only rendering; lesson Markdown is a hand-rolled safe subset with no
`dangerouslySetInnerHTML` — `src/components/Markdown.tsx`, tested); SSRF/local-AI boundary
(`app/ai/policy.py` refuses non-local endpoints at config time, fail closed); path traversal (no
file-serving endpoints; curriculum is packaged data); uploads (none — documented); IDOR (ownership
checks with 404-not-403 non-disclosure everywhere; consistent between routes); disclosure
(answer keys never serialised — `app/serializers.py`, asserted in `tests/test_api_journey.py`;
production preflight output never prints values; Vercel audit printed names only); password handling
(bcrypt, policy messages); secrets (none committed; `.gitignore` excludes; preflight refuses placeholders);
dependency vulns (pip-audit clean; npm audit clean; licences clean); admin exposure (RBAC enforced;
`/api/admin/*` invisible to non-admins — 404/403 behaviour covered by tests); AI prompt injection
(learner content is never instructions; grounded prompts with schema validation; invalid output is
rejected, never stored); AI cannot write mastery/evidence (mastery is replay-derived from evidence only;
tutor writes are validated and cannot elevate phases — `tests/test_mastery_evidence_boundary.py`);
no hosted-LLM fallback anywhere (`scripts/check_no_external_ai.py` green; refuse-non-local policy).
**This is a review, not a penetration test.** The threat model documents what is untested.

## 9. Database & migration verification

- Models + Alembic chain: verified on **isolated SQLite** — `alembic upgrade head` clean to
  `d5b8e0f13a72`; `alembic check` reports no drift (command above). FKs, unique constraints, indexes,
  cascades and ownership FKs are declared in `app/models.py`; migration tests
  (`tests/test_migrations.py`) and the learning-workflow/authz suites exercise them.
- Transaction boundaries: explicit commits on success paths; D.7 fix rolls back on exception.
- **PostgreSQL: BLOCKED/unavailable in this sandbox** — no `docker`, `psql`, `pg_dump` or `pg_ctl`
  exists here, and production Neon must not be used. What exists as evidence elsewhere: CI job
  "PostgreSQL (migrations, startup and persistence)" on `main` @ `9cbf057` (run 41536208912, success)
  — migrations, legacy-data rehearsal, `postgres_smoke.py`, and a **dump/restore backup rehearsal**
  against postgres:16. That is CI verification, not local verification, and not full parity; the
  suite itself runs per-test SQLite. Before production, the owner must rehearse backup/restore on the
  target PostgreSQL and run the pilot checklist (`docs/DEPLOYMENT.md` §3).
- No destructive migration was run; no migration file was edited.

## 10. Learning-journey verification

Automated (SQLite-backed, in-process): `tests/test_api_journey.py` (9 tests: full goal→assess→plan→
learn→practice→measure journey, determinism, replay, replay-protection of diagnostic answers,
answer-key isolation, cross-learner isolation, goal caps, explicit empty dashboard),
`tests/test_learning_workflow.py`, `tests/test_learning_purity.py`, `tests/test_mastery_*`,
`tests/test_placement_aggregation.py`, `tests/test_diagnostic_integrity.py`, `tests/test_review_*`,
`tests/test_practice_*` — all green within the 502.

Live over HTTP (this phase, real uvicorn + isolated migrated SQLite + `load_curriculum.py`): **22/22
checks passed** — health, anonymous 401, register 201, session cookie, me 200 with consents,
explicit AI-disabled health, paths, goal 201, diagnostic 201, **idempotent diagnostic restart**,
diagnostic completed, placement stored (rule recorded), plan 200 with `validation.ok=true`, 12 items
in 3 weeks, dashboard next action `kind=learn`, practice 201, practice complete 200, **practice
re-complete 409**, evidence recorded (**14 rows: 12 diagnostic + 2 practice**, all `success`),
mastery endpoint 200 (1 row, `acquiring`, 2 unassisted successes), logout 204, me-after-logout 401.
Direct SQL: `sessions.revoked_at` set; `plans.validation_report.ok = 1`; consents `account`+
`ai_processing` recorded; `audit_log` 1 row; `alembic_version = d5b8e0f13a72`.

Not done in-process against PostgreSQL (see §9). Not done in a real browser here (see §7). No mastery
is producible from AI text (evidence boundary replay-verified). Curriculum is authored data
(`python-foundations`, `frontend-foundations`), **not** presented as field-validated content; the
reference requires subject review before any learner sees it (documented).

## 11. AI runtime verification

- Policy enforcement: `TALIMGO_AI_ENABLED=false` is the default; `/api/health/ai` reports the explicit
  disabled state (observed live: `{"ai_enabled":false,...,"policy":"local-only"...}` shape). When AI
  is enabled, `app/ai/policy.py` refuses non-local endpoints **at configuration time** (fail closed);
  strict mode also rejects a missing model name. Adapter tests prove calls target only the configured
  local endpoint and that unavailability yields an explicit 503 with a user-visible message — never a
  hosted fallback (there is no provider SDK anywhere in manifests; `check_no_external_ai.py` green).
- Consent: tutoring requires the `ai_processing` consent; settings surface the toggle; the consent
  record is asserted in the journey tests.
- Quotas: per-learner daily allowance with atomic conditional update (`tests/test_ai_quota.py`,
  durable across restarts — `tests/test_tutor_quota_durability.py`); concurrency cap (default 1,
  bounded wait) — `tests/test_tutor_local.py`.
- Output validation: grounding retrieved from the learner's objective/lesson context; structured
  output schema-validated; invalid output rejected, never stored (`tests/test_tutor_local.py` —
  validator accepts/rejects cases including citation-not-in-context and prohibited-claim blocks;
  `tests/test_tutor_grounding.py`).
- **Real inference: NOT VERIFIED — no local model runtime exists in this sandbox** (`127.0.0.1:11434`
  refused; `ollama`/`vllm` absent). `pytest -m local_model` skips with the explicit reason. Tutoring
  stays disabled until the owner provisions a local runtime and evaluates it (`docs/LOCAL_AI_ARCHITECTURE.md`).
  No fake inference results are claimed anywhere.

## 12. Deployment audit findings (Vercel + AlwaysData) — read-only; nothing changed

**Vercel (connected integration; read-only calls only):**

- `talimgo-preview` (`prj_RX2NmJBTcZTkygGNgZKcbhqBk7aA`, framework `vite`, GitHub `Devmraustro/TALIMGO`,
  production branch `main`, SSO `all_except_custom_domains`, Ignored Build Step skips `main` by
  design). Latest **production** deployment `dpl_2VdW944PetWftnNRnmNc2JMenZuB`
  (main @ `9cbf057`, 2026-11-02-ish) is **CANCELED — by design**, not a build failure. Latest preview
  deployment `dpl_DNh5qHxpyuMSLkzVJcbRLKJgULt8` (branch `fix/frontend-vite-security-and-deployment-status-signed-v2`
  @ `90d8ed9`, **READY**).
- `talimgo-api` (`prj_kRQpwUxAcSvOkiUHxRlkyO5plKwk`, framework `fastapi`, root directory `backend`,
  `iad1`, **SSO protection for `all`**, `live: false`, Git create-deployments disabled). Environment
  variables exist **only for preview targets** (two branches: `experiment/vercel-fastapi-preview-20261031`
  — development mode, ephemeral SQLite, AI disabled; and `fix/frontend-vite-security-and-deployment-status-signed-v2`
  — `TALIMGO_ENV=production`, generated session secret, a least-privilege Neon PostgreSQL role URL
  [secret, not decrypted or displayed], `TALIMGO_ALLOWED_ORIGINS` limited to `talimgo-preview.vercel.app`,
  AI disabled, no seed). **No Production-target environment variables exist.** The promoted
  **production** deployment `dpl_9zgFoCpkHHZAUEzkFPZsmickt4ZJ` (main @ `9cbf057`) is `READY`/`PROMOTED`
  and aliased (`talimgo-api.vercel.app`), **but with `VERCEL_ENV=production` inherited and no
  `TALIMGO_ENV`** the application fails closed at startup (`app/config.py` refuses a Vercel production
  deployment without explicit `TALIMGO_ENV=production`), and SSO blocks all visitors. Per
  `docs/VERCEL_DEPLOYMENT_STATUS.md`, this fail-closed state is the intended safety behaviour and
  must not be "fixed" by adding placeholder variables, disabling SSO, or promoting anything — and it
  was not. The repository also documents that hosting FastAPI on Vercel is out of scope (no long-lived
  process, no local model, ephemeral filesystem) — the intended API host is Alwaysdata.
- **Neither deployment serves this working tree.** The promoted `talimgo-api` production build runs
  `main` @ `9cbf057`, which does **not** contain the working-tree fixes (§4). No deployment was
  triggered, promoted, re-aliased, or modified.
- Headers claim from earlier audits: root `vercel.json` modernised (headers+rewrites) with a CI guard
  (`src/vercel-services.test.ts`) — that fix is in `main`; it takes effect only on the next deployment,
  which is an owner action.

**Alwaysdata:** not accessed this phase (no credentials; nothing to verify). The runbook
(`docs/ALWAYSDATA_DEPLOYMENT_RUNBOOK.md`), the nginx example, the systemd units, and the
post-deployment verifier (`backend/scripts/verify_deployment.py`) are present and consistent with the
code as audited. Until the owner provisions the Alwaysdata service and runs the verifier, the
deployment path is **unverified**.

**Architecture consistency:** `SameSite=Lax` session cookie ⇒ the interface and API must be one browser
origin (same-origin nginx proxy, or a server-side Vercel rewrite). A direct cross-origin browser→API
call cannot work with the current cookie design — this is documented, intentional, and enforced by
`frontend/src/lib/api.ts`. The current Vercel static host has **no API behind it** (`/api/*` → 404 by
rewrite), which is precisely what the interface's honest "API could not be reached" message is for.

**Do-not-deploy invariants (reiterated):** no production environment changes, no env-var changes, no
SSO/protection changes, no promotion, no new deployment — none were performed.

## 13. Remaining blockers (external / owner)

1. **`talimgo_runtime` credential rotation — BLOCKED — DEFERRED BY OWNER.** Not attempted, not
   requested, never printed. Until the owner rotates it, updates the runtime environment securely,
   and verifies the actual runtime identity and least-privilege permissions with the managed database,
   **no production deployment, public release, or production-readiness approval may proceed**, and
   this report claims none. It does not block development.
2. **PostgreSQL staging verification** — no isolated PostgreSQL exists in this sandbox (CI-only
   evidence; see §9). Owner must rehearse backup/restore on the target PG and run the pilot checklist.
3. **Real local AI inference** — no Ollama/vLLM runtime provisioned or evaluated here; tutoring stays
   disabled until then. NOT VERIFIED (§11).
4. **Vercel topology** — `talimgo-api` cannot serve production as-is (fail-closed, SSO, no Production
   env); the Alwaysdata path is documented but unprovisioned. Owner decision required.
5. **External approvals** — subject-matter review of the curriculum before any learner use; manual
   accessibility pass; penetration test; content validation — all documented, none performed.
6. **Commit/release of the working tree** — the D.7/D.8/D.9 changes are uncommitted. No push, merge,
   release, or deploy has been made; the owner decides.

## 14. Exact commands executed (abridged to what produced evidence above)

Environment rebuild: `python3 -m venv /home/user/talimgo-venv && /home/user/talimgo-venv/bin/pip install -e '/home/user/TALIMGO/backend[dev]'`; `npm ci` (node_modules/.bin: 17).
Backend: `ruff check app tests scripts`; `ruff format --check app tests scripts`; `bandit -q -r app`;
`python scripts/check_no_external_ai.py`; `python scripts/check_licences.py`;
`TALIMGO_ENV=test TALIMGO_DATABASE_URL=sqlite:///./ci-test.db alembic upgrade head|check|current`;
`TALIMGO_ENV=production … TALIMGO_DATABASE_URL=postgresql+psycopg://… scripts/check_production_config.py` (exit 0);
same with SQLite (exit 1); `pytest --tb=no` (502 passed, 4 skipped, 155.00s); `pytest -rs -q tests/test_deploy_shell.py tests/test_local_model_integration.py`; `pip-audit --progress-spinner off`.
Frontend: `npx tsc --noEmit`; `npm run build`; `npx vitest run` (76 passed, 1 skipped, 13.95s);
`node scripts/check-bundle.mjs`; `node scripts/check-licences.mjs`; `npm audit --omit=dev`.
Live journey: isolated DB at `/tmp/talimgo-d9-smoke.db`; `alembic upgrade head`; `python scripts/load_curriculum.py`;
`uvicorn app.main:app --host 127.0.0.1 --port 8011`; `/tmp/talimgo_live_smoke.py` (22 checks); direct SQL assertions.
Preview stack: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (env=test, AI disabled, random dev secret); `npx vite --port 5173`; `curl` checks.
Vercel: read-only `list_projects(search=talimgo)`, `get_project(talimgo-api)`, `get_project(talimgo-preview)`, `list_deployments(target=production)` — no other Vercel calls.
GitHub: read-only `gh run list --branch main`, `gh run view 41536208912 --json jobs`.

## 15. GitHub / infrastructure / production changes confirmation

- **Nothing was pushed, merged, released, or deployed.** No PRs opened/closed, no issues created, no
  branches created, no force operations, no history rewrites, no `reset`/`clean`.
- **No production environment, SSO, environment variables, DNS, database, permissions or data were
  modified.** The Vercel integration was used for read-only inspection only; the Alwaysdata service
  was not accessed; no secrets were read, decrypted, printed or stored anywhere.
- **No credential rotation was attempted** (deferred by owner, §13.1).
- The working tree preserves the pre-existing D.7/D.8 uncommitted work, untouched in content except
  where the D.9 changes are listed in §5.
- `.git/shallow` was deepened in an earlier phase only by the authorized `git fetch --depth 400`;
  no fetches were needed in D.9.

## 16. Overall classification

Capability summary (detailed per-row classifications are in §4–§13):

| Capability | Classification |
|---|---|
| Accounts, auth, sessions, RBAC, admin | VERIFIED |
| Cross-user isolation (API + DB assertions) | VERIFIED |
| Full learning journey (goal→diagnostic→plan→practice→evidence→mastery) | VERIFIED (incl. live HTTP 22/22) |
| Dashboard / next-action / scheduling | VERIFIED |
| Practice idempotency & repeated-submission handling | VERIFIED |
| Diagnostic idempotency | VERIFIED |
| In-process rate limits & request guards | VERIFIED |
| Migration chain on SQLite (+ drift check) | VERIFIED |
| PostgreSQL (CI backup/restore rehearsal) | PARTIALLY VERIFIED — CI evidence only; not this sandbox; owner staging rehearsal outstanding |
| Frontend wired to real API; loading/empty/error states | VERIFIED |
| Arabic interface + RTL direction switching | PARTIALLY VERIFIED — interface strings + direction verified; full Arabic typography/RTL audit is FUTURE by design |
| Browser journey + axe locally | NOT EXECUTED (egress-blocked); green in CI on `main` @ `9cbf057` |
| Local AI policy enforcement / 503 fail-explicit | VERIFIED (tests + config gates) |
| Real local AI inference | BLOCKED — no runtime available; NOT VERIFIED |
| Vercel deployment | PARTIALLY VERIFIED — audited read-only; topology unresolved (fail-closed by design; Alwaysdata preferred) |
| Alwaysdata deployment | NOT EXECUTED — runbook present; not provisioned |
| `talimgo_runtime` rotation | BLOCKED — DEFERRED BY OWNER |
| Production readiness | **NOT CLAIMED** |

**OVERALL: DEVELOPMENT COMPLETE — PENDING EXTERNAL RELEASE GATES.**

Every development-phase criterion that can be satisfied in this environment is satisfied and verified
(gates green, journey verified live, no known critical defects, docs accurate for what exists). The
classification is *not* production readiness and never is while §13 stands: credential rotation and
post-rotation least-privilege verification, PostgreSQL staging/backup-restore evidence on the target,
local AI provisioning and evaluation, the Vercel→Alwaysdata hosting decision and verifier run, and the
owner's commit/release authorization are all outstanding owner actions. No production release, deploy,
or public announcement is authorized or implied by this report.
