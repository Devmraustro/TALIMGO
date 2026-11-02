# TALIMGO — Alwaysdata Deployment Status

**Status date: 2026-11-02**

This document records an evidence snapshot of the Alwaysdata deployment preparation, what has been confirmed locally, and what requires owner action before the deployment can go live.

## 0. Repository baseline for this documentation revision

| Item | Status | Evidence |
|------|--------|----------|
| PR #11 merged | Confirmed | Squash-merge commit `e21366cd430837772edcae3a4349439c1761d3a5`; GitHub reports the merge commit signature as verified. |
| PR #10 closed | Confirmed | Closed as superseded by PR #11; do not merge the duplicate Vite/documentation branch. |
| Post-merge `main` CI | Passed | [Run 41517171892](https://github.com/Devmraustro/TALIMGO/actions/runs/41517171892) — 7/7 jobs on `e21366cd430837772edcae3a4349439c1761d3a5`. |
| Vercel status on that merge commit | Successful status contexts | `talimgo-preview` and `talimgo-api` both report `success`; these are not production-readiness evidence. |
| Old PR #11 branch after the merge | Historical only | `979f259c2272fe6516ad72ec72c7926795218853` and run `41519616464` belong to the old PR branch, not to `main`. Do not use that branch as the next deployment baseline. |

`e21366cd430837772edcae3a4349439c1761d3a5` is the code baseline preceding this documentation-only
revision, not a permanent assertion of the current `main` HEAD. Re-read `origin/main`, open PRs and
CI before any subsequent work.

## 1. Historical PR #9 baseline (evidence snapshot, before PR #11)

| Item | Status | Evidence |
|------|--------|----------|
| PR #9 merged into `main` | CI-verified | GitHub Actions run `41314061952` — 7/7 jobs passed; squash-merge commit `765eed71ce967540491814fdb88dfae042fdea6b` |
| Local `main` at verified SHA | Confirmed | `765eed71ce967540491814fdb88dfae042fdea6b` |
| `origin/main` tracking ref | Updated | Fast-forwarded from stale `cf0a13e` to `765eed71ce967540491814fdb88dfae042fdea6b` |
| Backend test baseline (clean main) | Passed | `449 passed, 1 skipped` (pytest on `765eed7`) |
| Ruff check | Passed | "All checks passed!" |
| Ruff format check | Passed | "107 files already formatted" |
| Bandit security scan | Passed | Exit code 0 |
| Alembic migrations | Passed | Head `d5b8e0f13a72`, upgrade + check clean |
| Production preflight | Passed | All 6 checks pass (PostgreSQL URL accepted; SQLite correctly rejected) |
| Frontend tests | Passed | 75 passed, 1 skipped (full suite run twice; ProjectsPanel test passed in three isolated runs; one earlier timeout observed but not reproduced; cause not established) |
| Frontend typecheck | Passed | `tsc --noEmit` clean |
| Frontend build | Passed | `vite build` succeeds (Vite 6.4.5) |
| Bundle gate | Passed | `check-bundle.mjs` — same-origin assets, no local/insecure host |
| Licence check | Passed | 184 packages inspected |
| npm audit | Passed | 0 vulnerabilities after Vite update to 6.4.5 |
| Local-only AI gate | Passed | `check_no_external_ai.py` — no hosted providers |
| PostgreSQL 16 disposable Docker test | Passed | Migrations applied; `alembic check` clean; backend tests 449 passed, 1 skipped |
| GitHub Actions Run #233 | Passed | 7/7 jobs passed on unsigned PR #10 commit `94313bd` |
| GitHub Actions Run #237 | Passed | 7/7 jobs passed on signed PR #11 commit `b888e570838caaafad35021de8f10faa726544b6`; https://github.com/Devmraustro/TALIMGO/actions/runs/41358309523 |
| GitHub Actions Run #239 | Passed | 7/7 jobs passed on signed PR #11 commit `1ecfd4cc634875681146690004dd7363409f8fa6`; https://github.com/Devmraustro/TALIMGO/actions/runs/41488205784 |

**Note:** This table is a historical PR #9 evidence snapshot, not a live assertion of branch state. For the later PR #11 baseline see §0; always re-check the live `main` head, CI and Vercel state on GitHub.

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

- **ProjectsPanel test timeout**: Passes in isolation (~8.5s) in three isolated runs; did not time out in two full-suite runs. One earlier timeout was observed but not reproduced; cause not established.
- **No local AI runtime**: AI is explicitly disabled (`TALIMGO_AI_ENABLED=false`). Local model selection, installation, and evaluation is a separate owner decision.

## 6. Definition of completion

The Alwaysdata deployment phase is complete only when every item in the acceptance checklist (`docs/DEPLOYMENT.md` §12 and §11) has verified evidence against the live host. No item may be marked complete based on configuration files alone — actual live verification is required.

## 7. Git state

| Reference | SHA | Status |
|--------|-----|--------|
| `main` code baseline before this documentation revision | `e21366cd430837772edcae3a4349439c1761d3a5` | PR #11 squash merge; post-merge CI run `41517171892` passed 7/7. Re-check the live head before reuse. |
| Old PR #11 branch after the merge | `979f259c2272fe6516ad72ec72c7926795218853` | Historical branch-only commit; not merged into `main` and not a deployment baseline. |

PR #11 is merged and PR #10 is closed. Do not resume the old PR branch or infer the current `main`
head from any historical table. Historical commit SHAs from prior documentation snapshots are listed below for reference only.

Historical commit SHAs (not part of current work):
| Branch | SHA | Status |
|--------|-----|--------|
| `fix/frontend-vite-security-and-deployment-status-signed-v2` (historical) | `b888e570838caaafad35021de8f10faa726544b6` | Previous PR #11 commit; Vercel previews READY for this SHA |
| `fix/frontend-vite-security-and-deployment-status-signed-v2` (historical) | `1ecfd4cc634875681146690004dd7363409f8fa6` | Previous PR #11 commit; Vercel previews READY for this SHA |
| `fix/frontend-vite-security-and-deployment-status-signed-v2` (historical) | `6f713462b9d9fd77a0fcd50f4e66d7fdc08c799d` | Previous PR #11 commit; pull-request CI run `41490792120` passed 7/7, not post-merge CI |
| `fix/frontend-vite-security-and-deployment-status-signed-v2` (historical) | `1e25ffe76a065a10348c58ed1ea3e6ec75317a4b` | Previous PR #11 commit; push CI run `41506736016` passed 7/7 and both Vercel status contexts succeeded for this exact SHA |
| `fix/frontend-vite-security-and-deployment-status-signed-v2` (historical) | `13c73881dbd356127047a0c2189e635935a4d30f` | PR #11 head at merge; push CI run `41509516797` passed 7/7 |
| `fix/ruff-config-migration-files` (historical) | `367e4d036baf00c2d1f35e72e9abf1b9189e793e` | Ruff fix merged as PR #7 |

**Important:** Local tests were executed on the development machine. GitHub CI results (Run #233 for PR #10, Run #237 for PR #11 commit `b888e57`, Run #239 for PR #11 commit `1ecfd4c`) are recorded separately. Vercel Preview states are observed independently and do not constitute production readiness.
