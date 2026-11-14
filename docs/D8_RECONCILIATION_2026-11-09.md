# D.8 — Reconciliation of the Arena implementation with the original deployment-branch work (2026-11-09)

## What the "original branch" actually is

- The expected branch `reconcile/90d8ed9-talimgo-deployment` **does not exist**: `git ls-remote origin`
  (all 15 heads + PR refs checked) lists no such ref, and the GitHub branches API returns 404 for it.
- The expected commit `90d8ed9626bbfd0cf92c83f3f4276e9fd32ee5f4` **does exist**: it is
  `origin/fix/frontend-vite-security-and-deployment-status-signed-v2`, the signed PR #11 branch
  ("chore: trigger verified TALIMGO preview deployment"), signed with `ssh-ed25519`.
- It is **not** an ancestor of `main` and `main` is not its ancestor: both descend from
  `765eed71ce967540491814fdb88dfae042fdea6b` (PR #9 squash merge) via different (signed unsquashed vs.
  squash-merged) paths.
- **Tree diff `9cbf057…90d8ed9` (exhaustive, 8 files):** `.github/workflows/ci.yml` (+3 lines: curriculum-load
  step), `backend/scripts/load_curriculum.py` (+57), `backend/tests/test_curriculum_load_script.py` (+140),
  and six documentation files refreshed by PR #12/#13. `backend/app` is **byte-identical** between the two
  trees. **90d8ed9 contributes zero unique content**; nothing was merged, overwritten, or discarded.
- **The named "original" artifacts exist nowhere reachable**: no `backend/Dockerfile`, `docker-compose.yml`,
  `frontend/Dockerfile`, `git-ssh-sign-wrapper.{cmd,ps1}`, `backend/tests/test_auth_regression.py`, or
  `backend/tests/test_authz_cross_user.py` — not on any of the 16 remote refs inspected, not on PR #7's
  head, not in any fork (empty fork list). These files were expected to exist on the missing reconciliation
  branch (presumably a local working branch on the D.5–D.7 machine). They were **re-created fresh** in D.7
  recovery (`backend/tests/test_auth_regression.py`, `test_authz_cross_user.py`), which is the coverage that
  stands behind HEAD today.

## D.7 against the actual code (not the missing branch)

- 90d8ed9 (and main, and this branch) contain **no** `GET/POST/DELETE /api/goals/{goal_id}` routes — only
  `POST /api/diagnostic/goals/{goal_id}` and `POST /api/plans/goals/{goal_id}`. No goal-by-ID read/delete
  exists for the D.7 scenario to have targeted there either.
- In-history corroboration of the mechanism class: `be3c2c66f59c1cafed46466b7e87e58d048cace0`
  "test(security): isolate learner sessions in rate limit test" — two users registered on one client in
  `test_write_rate_limits.py` overwrote the shared `talimgo_session` cookie; fixed by `client.cookies.clear()`
  before swapping jars (now in `main`). This is the same shared-cookie-jar failure mode as D.7's
  "User A's goal vanishes after User B registers" report.
- Consistent with the D.7 signature (foreign request → 404, row persists, owner then gets 404) being a
  **test-harness credential conflation**, not an application defect: current code returns 404 for
  foreign-owned objects with zero side effects, verified over HTTP with two independent clients and direct
  SQL (`tests/test_authz_cross_user.py`).

## D.8 verification (this working tree = `main` + Arena fixes)

- Backend: **502 passed, 4 skipped** (exit 0); focused security modules 64/64; `ruff check`/`ruff format --check`
  clean; `bandit -q -r app` clean; `pip-audit`: no known vulnerabilities; licence check passed.
- Alembic on a fresh isolated database: head `d5b8e0f13a72`; `alembic check` → no new operations.
- Production preflight: PASS; correctly refuses SQLite (exit 1).
- Frontend (unchanged code): typecheck ✅, `vite build` ✅, bundle check ✅, vitest **75 passed, 1 skipped** ✅.
- Live uvicorn smoke: register 201 → goal 201 → dashboard 200 → logout 204 → `/api/auth/me` 401.
- PostgreSQL staging verification: **BLOCKED** (no authorized isolated Postgres/Neon staging environment in
  this sandbox — no docker, no psql, no binaries). CI's postgres-integration job covers this on the next run.
- Real local-model inference: **NOT VERIFIED** (no Ollama runtime; `localhost:11434` refused). AI stays
  disabled; hosted-provider policy gate passes.
- `talimgo_runtime` credential: **compromised, rotation not confirmed**; never reproduced, printed or used.

No push, merge, PR, deployment, environment change, or production migration was performed. `.git/shallow`
deepened only through authorized `git fetch` calls used for inspection.
