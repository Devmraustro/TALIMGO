# TALIMGO recovery verification — 2026-11-09

Working branch: `arena/244ad13e-talimgo` @ `9cbf05711b24e5c243b4ea02ffb2929ead14415f` (depth-1 clone; the
`reconcile/90d8ed9-talimgo-deployment` branch referenced in the master prompt is not reachable in this
clone — see the final report, "Repository", for the full discrepancy). Alembic head: `d5b8e0f13a72` (unchanged).

## Defects fixed (application code)

1. **Admin router unreachable (422 for everyone).** `APIRouter(dependencies=[Depends(AdminUser)])` passed an
   `Annotated` alias instead of the dependency callable; FastAPI modelled the alias itself as a parameter
   with `*args/**kwargs`, so every `/api/admin/*` route failed validation before authorisation ran — for
   learners *and* for admins. Fixed: `dependencies=[Depends(get_admin_user)]`. Regression coverage:
   `tests/test_authz_cross_user.py::test_admin_routes_are_invisible_to_learners` (404) and
   `::test_admin_routes_are_visible_to_admins` (200).

2. **Logout did not revoke Bearer-authenticated sessions.** Logout read only the session cookie; a client
   using `Authorization: Bearer <token>` stayed signed in after logout. Fixed: logout resolves the presented
   credential exactly the way `get_optional_user` does (cookie first, then Bearer) via the shared
   `app.deps.session_token_from_request`. Regression: `tests/test_auth_regression.py::test_logout_revokes_the_bearer_credential_too`.

3. **Sessions returned to the pool with an open transaction on error.** `get_db` previously only closed the
   session; uncommitted state now rolls back explicitly on exception (`app/db.py`). Routes still commit
   explicitly on success; intentional independent commits (write-rate claim, registration guard) are unaffected.

## Tests added

- `tests/test_authz_cross_user.py` — two-client cross-user matrix over every learner-owned object-ID route
  (goals, plans, diagnostic attempts, practice sessions, projects, tutor, account surface, admin), foreign
  vs. missing non-disclosure, no-mutation-after-foreign-attempt, D.7 full-sequence regression.
- `tests/test_auth_regression.py` — session lifecycle: independence, hashing at rest, tampered/expired/revoked
  tokens, deactivated accounts, logout cookie+bearer revocation, TTL, cookie shape.
- `tests/test_config_isolation.py` — production defaults intact, hard ceilings refuse test-grade overrides,
  cache reset, 429/401 contracts under a tightened test configuration.
- `tests/test_learning_workflow.py` — full workflow with database persistence asserted at each step; malformed
  input handling; deterministic recompute; AI-disabled explicitness.

## Verification (all on this checkout)

- `pytest`: 502 passed, 4 skipped (local-model marker) — exit 0.
- `ruff check app tests scripts` / `ruff format --check`: clean. `bandit -q -r app`: clean (exit 0).
- Alembic on a fresh isolated database: `upgrade head` → `d5b8e0f13a72`; `downgrade base` → `upgrade head`
  clean; `alembic check`: "No new upgrade operations detected."
- `scripts/check_production_config.py`: PASS with throwaway production env; correctly REFUSES SQLite (exit 1).
- `scripts/check_no_external_ai.py`: PASS (92 files, 7 URL literals, no hosted providers).
- `scripts/check_licences.py`: PASS (49 distributions). `pip-audit`: no known vulnerabilities.
- Frontend (unchanged): `tsc --noEmit`, `vite build`, `check-bundle.mjs`, `vitest --run` → 75 passed, 1 skipped.
- Live uvicorn smoke: register 201 → goal 201 → dashboard 200 (own goal) → logout 204 → `/api/auth/me` 401.

## Not implemented / external actions (owners)

- Goal-by-id GET/DELETE (`/api/goals/{id}`) does not exist in frontend or backend — "goal deletion" is NOT
  IMPLEMENTED as a feature; the account-deletion flow exists instead.
- No deployment, push, merge, production migration or environment change was performed.
- The `talimgo_runtime` database password must still be rotated by the owner via Neon Console; this
  checkout contains no occurrence of that credential.
- Verification against the `reconcile/90d8ed9-talimgo-deployment` branch and its CI evidence could not be
  performed in this clone (not reachable); the above evidence is for this branch only.
