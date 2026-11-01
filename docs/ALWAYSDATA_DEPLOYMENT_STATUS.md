# TALIMGO — Alwaysdata Deployment Status

**Status date: 2026-11-01**

This document records the verified state of the Alwaysdata deployment preparation, what has been confirmed locally, and what requires owner action before the deployment can go live.

## 1. Verified baseline (local, CI-verified)

| Item | Status | Evidence |
|------|--------|----------|
| PR #9 merged into `main` | CI-verified | GitHub Actions run `41314061952` — 7/7 jobs passed; squash-merge commit `765eed71ce967540491814fdb88dfae042fdea6b` |
| Local `main` updated to match origin | Completed | Fast-forwarded local `main` `ffe5ccc` → `765eed71ce967540491814fdb88dfae042fdea6b` |
| Ruff config fix (exclude migrations) | Merged (PR #7) | `backend/pyproject.toml` has `extend-exclude` and `per-file-ignores` for `migrations/versions/*.py` |
| Backend tests | Passed | `454 passed, 1 skipped` on merged `main` |
| Ruff check | Passed | "All checks passed!" |
| Ruff format check | Passed | "109 files already formatted" |
| Bandit security scan | Passed | Exit code 0 |
| Alembic migrations | Passed | Head `d5b8e0f13a72`, upgrade + check clean |
| Production preflight | Passed | All 6 checks pass (PostgreSQL URL accepted; SQLite correctly rejected) |
| Frontend tests | 74 passed, 1 skipped, 1 flaky | `ProjectsPanel.test.tsx` times out at 15s under system load; passes in isolation at ~8.2s |
| Frontend typecheck | Passed | `tsc --noEmit` clean |
| Frontend build | Passed | `vite build` succeeds |
| Bundle gate | Passed | `check-bundle.mjs` — same-origin assets, no local/insecure host |
| Licence check | Passed | 184 packages inspected |
| npm audit | Passed | 0 vulnerabilities after Vite update to 6.4.5 (GHSA-8g5g-mxqh-grgj resolved) |
| Local-only AI gate | Passed | `check_no_external_ai.py` — no hosted providers |
| Vite security fix | Fixed | Vite updated from 6.4.4 to 6.4.5; dev/preview binding changed from `0.0.0.0` to `127.0.0.1`; `npm audit` reports 0 vulnerabilities |

## 2. What has NOT been deployed

- No Alwaysdata account has been accessed or provisioned.
- No dedicated PostgreSQL database has been confirmed for TALIMGO.
- No production environment variables have been set.
- No migrations have been run against a production database.
- No site, domain, or TLS has been configured.
- No live deployment exists.
- Local AI remains disabled (`TALIMGO_AI_ENABLED=false`); no local model runtime has been provisioned or evaluated.

## 3. Owner actions required (in order)

Per `docs/ALWAYSDATA_DEPLOYMENT_RUNBOOK.md`:

| # | Action | Owner decision needed? |
|---|--------|------------------------|
| 1 | Confirm Alwaysdata account is TALIMGO-only, dedicated | Yes |
| 2 | Confirm web site + PostgreSQL database/login are TALIMGO-only | Yes |
| 3 | Confirm account quotas support process/RAM/storage/uptime | Yes |
| 4 | Confirm domain/subdomain controlled by owner with DNS/TLS path | Yes |
| 5 | Create dedicated PostgreSQL database and least-privilege login | Yes (via Alwaysdata admin) |
| 6 | Checkout `main` on Alwaysdata account, create Python 3.11 venv, install deps | No (can be done by operator) |
| 7 | Create private production env file with strong secrets | Yes (secrets never in chat/Git) |
| 8 | Run `scripts/check_production_config.py` — must exit 0 | No (verification) |
| 9 | Run `alembic upgrade head` + `alembic check` — must report no drift | Yes (against production DB) |
| 10 | Configure Alwaysdata User Program (Uvicorn on `$IP`/`$PORT`, 1 worker) | No (can be done by operator) |
| 11 | Prove same-origin `/api` routing works (single host or Vercel rewrite) | Yes (topology decision) |
| 12 | Build and stage frontend via `deploy/stage-frontend.sh` | No (can be done by operator) |
| 13 | Run `scripts/verify_deployment.py` against confirmed host | Yes (authorization for disposable account) |
| 14 | Configure backup/restore and maintenance schedule | Yes (retention policy decision) |

## 4. Deployment topology

The supported topology is **single-host**: Alwaysdata site serves `frontend/dist` and proxies `/api` to the FastAPI User Program on the same origin. This preserves the `SameSite=Lax` session cookie model.

Alternative: Vercel frontend with server-side `/api/*` rewrite to Alwaysdata API host. Not yet verified on a real project.

**Not supported:** Browser calling a separate API origin directly (would break `SameSite=Lax` cookies).

## 5. Known findings

- **ProjectsPanel test timeout**: Passes in isolation (~8.5s) but can time out at 15s under system load when running the full suite. Environment-related, not a code defect.
- **No local AI runtime**: AI is explicitly disabled (`TALIMGO_AI_ENABLED=false`). Local model selection, installation, and evaluation is a separate owner decision.

## 6. Definition of completion

The Alwaysdata deployment phase is complete only when every item in the acceptance checklist (`docs/DEPLOYMENT.md` §12 and §11) has verified evidence against the live host. No item may be marked complete based on configuration files alone — actual live verification is required.

## 7. Git state

| Branch | SHA | Status |
|--------|-----|--------|
| `main` (local) | `765eed71ce967540491814fdb88dfae042fdea6b` | Synced with PR #9 merge |
| `origin/main` (remote) | `765eed71ce967540491814fdb88dfae042fdea6b` | PR #9 merged |
| `fix/ruff-config-migration-files` | `367e4d0` | Contains ruff fix (merged as PR #7) + PR #9 docs + verification commits |

The working tree has two untracked files: `git-ssh-sign-wrapper.cmd` and `git-ssh-sign-wrapper.ps1` (SSH signing helper scripts, not part of the deployment).