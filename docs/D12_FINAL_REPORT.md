# D.12 — Strict isolation, AlwaysData verification & PostgreSQL staging readiness — final report

**Phase classification: PARTIALLY VERIFIED** — the isolation decision is recorded and binding,
the staging procedure is proven against a disposable local PostgreSQL 16.2, all runnable gates
pass; the actual AlwaysData account is **unverified** (no credentials/access in this environment)
and the hosted staging, backup/restore and topology work is **BLOCKED** on owner action.
**TALIMGO is not production-ready and D.12 does not make it so.** Nothing was pushed, deployed,
purchased, changed, or rotated.

## 1. Repository baseline and exact SHA

Branch `arena/244ad13e-talimgo`; HEAD `0583a0a999f3b8c461615df5eaf6d158f4533fe9`; parent
`9cbf05711b24e5c243b4ea02ffb2929ead14415f` (= `origin/main`); `origin` =
`github.com/Devmraustro/TALIMGO`; **no upstream**; **0583a0a present and intact**; `main`
unchanged; no commits made in D.12; working tree = untracked docs + `deploy/staging/` only
(pre-existing untracked D.10/D.11 reports preserved). 8 dangling blobs in the object store —
all pre-edit intermediates of documentation (verified by size+first-line), none committed, no
history rewritten, benign. `git fsck` exits 0. No branches created/deleted.

## 2. Isolation decision and ownership matrix (recorded)

`docs/D12_OWNERSHIP_AND_ISOLATION.md` — **binding owner decision**: TALIMGO is completely
independent from AUSTRO (hosting, DB instances/roles, credentials/secrets, session state/data,
storage, workers/scheduled tasks, logs, AI inference/model data, prod vs staging, backups/recovery
credentials). Matrix of 15 resource classes + 8 explicitly prohibited cross-project dependencies +
enforcement rules for every future phase. **Code/config/CI audit: zero AUSTRO references**
(grep over code, tests, CI, manifests — empty). Infrastructure-level proof remains OPEN (no
AlwaysData scope exists yet). `talimgo_runtime` never used/accessed/rotated (rotation DEFERRED BY
OWNER).

## 3. Actual AlwaysData account verification

**NOT VERIFIED — no account access exists or was used.** Verified by name-only scans (env, `~/.ssh`,
`~/.config`: nothing AlwaysData; only `E2B_*` and `GH_TOKEN` present; Vercel connected but scoped
out, and it is not AlwaysData). All 14 requested items classified (`docs/D12_ALWAYSDATA_ACCOUNT_VERIFICATION.md`):
documentation-verified where a doc exists (Python 3.11, ASGI user program, PG 16–18, 50-conn cap,
daily off-site backups, HTTPS/Let's Encrypt, SSH no-root, scheduled tasks), **account-unverified
all** — including the AUSTRO-adjacency question. Requirement **R-1** (dedicated, owner-proven
TALIMGO-only scope; plan ≥ Small; explicit authorizations enumerated) is the exact blocker.
No account was accessed, probed, purchased or changed.

## 4. Hosting plan and resource limits

Plan = **UNKNOWN** (uninspectable). Documentation limits recorded: Public Cloud availability
99.7%, GRT 1 h, MTTR 4 h; Free plan 1 GB/256 MB/¼ CPU — **disqualified for TALIMGO**; Small
(€5/mo annual, 50 GB, 1 GB RAM, 1 CPU, 7 d backups) = minimum viable; X-Large → 8 CPU.
Application footprint: 1 uvicorn worker + SQLAlchemy pool (5+10) ≈ ≤ 15 connections — compatible
with the 50-connection cap. Process-kill behavior for oversized consumers noted. No plan purchase
or upgrade authorized or performed.

## 5. PostgreSQL staging status

**Design + artifacts: DONE. Execution vs AlwaysData: BLOCKED (authorization boundary).**
Deliverables: `deploy/staging/{provision_staging.sql, verify_staging.sql, post_restore_grants.sql,
README.md}` (idempotent, secret-free, reviewed) + `docs/D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md`
(permission matrix, exact owner actions R-list, hard stops). Local validation: disposable loopback
**PostgreSQL 16.2** cluster (same major as CI/AlwaysData PG16), synthetic data only.

## 6. Database identity and permission evidence (disposable local PG 16.2)

PROVISION (roles `talimgo_staging_migrate`/`talimgo_staging_app`, both NOSUPERUSER/NOCREATEDB/NOCREATEROLE;
DB `talimgo_staging` owned by migrate; PUBLIC connect revoked; re-run idempotent) → MIGRATE as migrate
(empty → head `d5b8e0f13a72`) → curriculum (20/20/68/2) → APP role: DML ✓, sequence usage ✓,
CREATE TABLE/ROLE ✗ denied, ALTER/DROP ✗ denied, `SET ROLE` ✗ denied, role memberships: none →
CONNECT denied on decoy `talimgo_prod_like` (app **and** migrate) and `austro_prod_like` (app);
decoys dropped at end of rehearsal; nothing else touched. Full table in
`docs/D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md` §3–4.

## 7. Migration results

Empty → head: clean; `alembic check` → "No new upgrade operations detected." (staging **and**
restored scratch); head remains `d5b8e0f13a72`; no migration files edited; isolated SQLite
`upgrade+check` clean; CI's PG16 rehearsal remains the CI-side evidence (not re-run; no push).

## 8. Backup/restore results

Repository's own `scripts/postgres_backup_restore.py` (loopback-gated): **PASS (exit 0)** —
dump→restore→row counts match→revision match→restored-API smoke→scratch dropped (2.263 s).
Manual custom-format rehearsal on the staging DB: dump **0.053 s** (95 435 B), restore **0.187 s**,
post-restore grants applied (mandatory after `--no-owner --no-acl`), 7/7 tables byte-equal counts
**before** any post-restore traffic, `alembic check` clean, app-role smoke PASS, scratch DB dropped
(verified absent). RPO/RTO assumptions + owner retention decisions documented in
`docs/D12_STAGING_BACKUP_RESTORE_VERIFICATION.md` — they are assumptions until the owner authorizes
an AlwaysData rehearsal. **Nothing was dumped from or restored to production.**

## 9. Option A review findings (not implemented)

`docs/D12_OPTION_A_STATIC_SERVING_REVIEW.md`: technically sound, isolated, low-risk **as
specified** (optional `TALIMGO_STATIC_DIR`, inert by default; StaticFiles on `/assets` immutable;
no-store index.html + SPA fallback GET/HEAD-only; `/assets/*` misses → 404 never HTML;
containment+traversal+dotfile refusals; API precedence; fail-closed startup; no auth/CSP/cookie/
CSRF/CORS changes; rollback = flag off). 10-test pre-merge suite specified. **Not implemented,
not merged, not committed** — awaits owner approval; D.12 does not authorize a product change.

## 10. Tests and exact results (2026-11-10, this tree)

Backend `pytest -q`: **502 passed, 4 skipped** (3 Windows deploy-shell shims; 1 `local_model`).
Auth regression **14 passed**; cross-user **23 passed**; config fail-closed **6 passed** (43/43).
ruff/format/bandit/no-external-AI/licences clean (73 py lic. incl. 3 dev-only tools — recorded);
pip-audit **no known vulnerabilities**; Alembic isolated upgrade+check clean; preflight 0/1.
Frontend: **76 passed / 1 skipped**; tsc clean; build ✓ 1.34 s (gzip 88.45 kB); bundle ✓;
licences 185 ✓; npm audit 0. Disposable PG 16.2 battery (§6–8): all PASS. Records in
`docs/D12_SECURITY_AND_RELEASE_GATE_STATUS.md` §3.

## 11. Security findings

No code/secret/dependency regression; docs+SQL re-scanned — clean; the only heuristic hit was the
documented `<url-encoded-password>` placeholder. Binding isolation decision recorded; AUSTRO zero
references in repo. Rehearsal surfaced and fixed a real gap (`--no-owner --no-acl` restore ⇒ app
role locked out ⇒ `post_restore_grants.sql`). CI has never executed `0583a0a` (unpushed) — red CI
= release stop. Dev-venv gained pgserver/fasteners/psutil (validation only; not product deps;
licensed, audited, recorded). 8 dangling blobs — documentation intermediates, benign.

## 12. Files changed (D.12 deliverables)

New: `deploy/staging/{provision_staging.sql, verify_staging.sql, post_restore_grants.sql, README.md}`;
`docs/D12_{OWNERSHIP_AND_ISOLATION, ALWAYSDATA_ACCOUNT_VERIFICATION,
STAGING_PROVISIONING_AND_PERMISSION_MATRIX, STAGING_BACKUP_RESTORE_VERIFICATION,
OPTION_A_STATIC_SERVING_REVIEW, SECURITY_AND_RELEASE_GATE_STATUS, FINAL_REPORT}.md`.
The D.10 and D.11 documents (`docs/D10_LOCAL_COMMIT_REPORT.md`, seven `docs/D11_*.md`) remain
**untracked and outside the D.12 commit** by design (preserved, not staged). Tracked application
files unchanged; `backend/tests/test_write_rate_limits.py` tracked and unmodified.

## 13. Git status and commit details

D.12 was executed first as a reviewable working tree (nothing committed during the phase). At
close-out the owner explicitly authorized **ONE local commit** containing only the reviewed D.12
paths above; application code and D.10/D.11 files were not touched. That commit uses the message
`docs(talimgo): finalize D.12 isolation and staging preparation`; its SHA, parent, exact file list
and post-commit verification are reported in the phase-closing verification message and are
reproducible with `git show --stat HEAD` and `git log --oneline -3`. No push, merge, PR, tag or
deployment was performed; the D.10 checkpoint `0583a0a` remains the parent of the D.12 commit and
the preserved stable base.

## 14. All owner actions still required

1. **R-1**: dedicated TALIMGO-only AlwaysData scope proven (account name, plan ≥ Small, billing,
   AUSTRO-adjacency disproved) — gates everything.
2. Authorize staging provisioning: run `provision_staging.sql` (or panel equivalent) with
   owner-generated passwords; authorize `alembic upgrade head` + synthetic curriculum on
   `talimgo_staging`; authorize rehearsal into scratch `talimgo_restore_test` + its drop.
3. Decide staging exposure (subdomain vs SSH-only) and the private env-file location.
4. Decide backup storage/retention (weekly dump + off-host copy cadence) and the restore runbook
   sign-off (twice-yearly rehearsal + pre-migration).
5. Decide Vercel vs AlwaysData (with the SSO implications if Vercel) — D.9/D.11 blocker, untouched.
6. Approve Option A implementation (then merge → re-run full gates incl. browser-level staging checks) — or reject it and pick the Option B path.
7. Decide on local AI runtime provisioning (or permanently AI-off) — disabled regardless today.
8. Decide `talimgo_runtime` rotation timing (deferred) + post-rotation least-privilege verification.
9. Approve publishing/PR of the working tree (branch currently holds `0583a0a` + all uncommitted docs/scripts).

## 15. Explicit deployment readiness classification

**NOT PRODUCTION READY — DO NOT DEPLOY.** Isolation policy **VERIFIED (documented)**;
infrastructure isolation **NOT VERIFIED**; staging procedure **VERIFIED (disposable local PG 16.2)**;
AlwaysData staging/topology/backups **BLOCKED** on owner actions §14; production release work
(rotation, live TLS/cookies/DNS verification, monitoring, rollback, post-deploy verification) =
**NOT STARTED / BLOCKED** by explicit authorization boundary. Next highest-priority action: the
owner's R-1 proof + written staging authorizations (§14.1–2) — everything else in D.12 is ready to
execute the moment those exist.
