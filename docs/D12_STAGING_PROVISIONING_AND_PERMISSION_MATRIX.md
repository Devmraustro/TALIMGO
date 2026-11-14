# D.12 — PostgreSQL staging provisioning & permission matrix (2026-11-10)

**Design target (binding):** a staging scope completely separate from production **and** from
AUSTRO. Logical resources: database `talimgo_staging`; dedicated runtime login
`talimgo_staging_app`; a separate migration identity `talimgo_staging_migrate`; synthetic data
only; independent env vars; independent backup destination. The runtime role must not reach
production or AUSTRO databases; the runtime role is never the migration owner; the compromised
`talimgo_runtime` credential is never used (rotation remains **DEFERRED BY OWNER**).

**Authorization boundary honoured in D.12:** account isolation was approved, but **paid
provisioning, account changes and database creation on the real account were NOT authorized and
NOT performed.** D.12 therefore (a) ships the exact provisioning artifacts, (b) validates them
against a **disposable local PostgreSQL 16.2** cluster (never production, never AUSTRO, zero
cost), and (c) marks every AlwaysData-side step **BLOCKED** pending the owner's actions in §6.

## 1. Permission matrix (target state)

| Capability | `talimgo_staging_migrate` | `talimgo_staging_app` | PUBLIC/others |
|---|---|---|---|
| LOGIN | yes | yes | — |
| SUPERUSER / CREATEROLE / CREATEDB | **no / no / no** | **no / no / no** | no |
| Owns `talimgo_staging` DB | **yes** (DDL scope) | no | — |
| CONNECT `talimgo_staging` | yes (owner) | yes (granted) | **revoked** |
| CREATE SCHEMA / TABLE / indexes / ALTER | **yes (owner)** | **NO** (revoked) | no |
| SELECT / INSERT / UPDATE / DELETE tables | yes (owner) | **yes** (granted DML; default privileges for future tables) | no |
| Sequences USAGE/SELECT | yes | **yes** | no |
| `SET ROLE talimgo_staging_migrate` | n/a | **denied** (verified) | — |
| MEMBER OF any other role | no | **no** (verified: 0 rows) | — |
| CONNECT any other database (`postgres`, `template*`, `talimgo_prod_like`, `austro_prod_like`, …) | only what admin grants — owner/migrate has none by default; verified denial on decoys | **denied** on decoys (verified) | as per each DB |
| DATABASE CREATE/DROP | **no** | **no** | no |
| RESET/ALTER anything outside own DB | **no** (owned DB only) | no | — |

On AlwaysData specifically, the panel grants per-database `all privileges` or `read only` only.
Mapping: create database `talimgo_staging` + dedicated login with **all privileges on that
database only** (this is the panel's least-privilege boundary), then apply the in-database section
(schema revokes + default privileges + explicit grants in `deploy/staging/provision_staging.sql`)
to approximate the finer-grained split above. A separate migration login on AlwaysData is optional
for a staging scope; if the owner accepts one dedicated login owning staging, use it for both
alembic and runtime but never for anything else, and re-create the script's grants after any
python/pip upgrade that recreates objects (default privileges already cover future tables).

## 2. Provisioning artifacts (authored in D.12; reviewed; no secrets)

| File | Purpose |
|---|---|
| `deploy/staging/provision_staging.sql` | Idempotent: create roles (migrate/app) with safe defaults; create `talimgo_staging` owned by migrate (hard-fails if ownership mismatches); revoke PUBLIC connect; schema revokes; default privileges; explicit DML grants; proof summary |
| `deploy/staging/verify_staging.sql` | Read-mostly probes run as `talimgo_staging_app`: role attrs, current db, DML read, DDL refusals (CREATE TABLE/ROLE, ALTER/DROP), membership, `SET ROLE` refusal |
| `deploy/staging/post_restore_grants.sql` | Re-apply schema/table/sequence/default grants **after any `--no-owner --no-acl` restore** (the missing piece that otherwise leaves the app role locked out of restored tables) |
| `deploy/staging/README.md` | Order of operations + non-goals |

No file contains credentials; passwords enter only via `psql -v` at execution time and are never
written to disk or logs by these scripts.

## 3. Validation performed in D.12 (disposable local PostgreSQL 16.2 — NOT AlwaysData)

Cluster: `initdb`-created throwaway in `/tmp` (deleted-cluster semantics; data synthetic);
port 55432 on loopback; never networked. PostgreSQL **16.2** (same major as CI and AlwaysData
PG16). Results (all 2026-11-10):

| Step | Result |
|---|---|
| Provision script (first run) | clean: roles created (NOSUPERUSER/NOCREATEDB/NOCREATEROLE), DB `talimgo_staging` owned by `talimgo_staging_migrate`, PUBLIC connect revoked, summary printed |
| Provision script (immediate re-run) | idempotent: 0 CREATE statements re-executed, exit 0 |
| `alembic upgrade head` on empty DB **as migrate** (ENV=production preflight env) | clean to head `d5b8e0f13a72` |
| `alembic check` | "No new upgrade operations detected." |
| `scripts/load_curriculum.py` (synthetic content) | `paths=2 objectives=20 lessons=20 items=68 projects=2` |
| App-role DML probe (`INSERT/UPDATE/DELETE`) | permitted on migrate-owned table incl. sequence default |
| App-role DDL refusal probes | CREATE TABLE/ROLE, ALTER, DROP → all **permission denied / must be owner** ✓ |
| `SET ROLE talimgo_staging_migrate` as app | **denied** ✓ |
| Cross-database denial | CONNECT to `talimgo_prod_like` (app **and** migrate) and `austro_prod_like` (app) → **FATAL: permission denied for database** ✓; decoys subsequently dropped |
| App-role membership in migrate/superuser roles | **0 rows** ✓ |
| Least-privilege end-to-end smoke (`scripts/postgres_smoke.py`) as app role | registration/session/goals/goal-read PASS |
| `python -m app.maintenance --dry-run` as app role | PASS |

## 4. The 10-step validation matrix from the D.12 brief — status

| # | Check | Status |
|---|---|---|
| 1 | Database identity and server version | **VERIFIED (local PG 16.2)** / **BLOCKED (AlwaysData)** |
| 2 | Staging DB is not production/AUSTRO | **VERIFIED** — disposable cluster; decoy denial proved the boundary; no AUSTRO resource existed anywhere in this work |
| 3 | Migrations from empty DB | **VERIFIED (local)** / **BLOCKED (AlwaysData)** |
| 4 | Alembic head == `d5b8e0f13a72` | **VERIFIED (local)** |
| 5 | Alembic drift check | **VERIFIED (local)** — "No new upgrade operations detected." |
| 6 | Staging runtime permissions (DML yes, DDL no) | **VERIFIED (local)** |
| 7 | Staging runtime cannot create roles/access unrelated DBs | **VERIFIED (local)** |
| 8 | App startup + health vs staging (uvicorn → `/api/health`) | **VERIFIED (local)** via `postgres_smoke.py` (TestClient boot) / full uvicorn boot **NOT EXECUTED** against a real staging URL |
| 9 | Auth/authz/cross-user regression tests | **VERIFIED** — 43 passed (14 auth-regression + 23 cross-user + 6 config-isolation); full suite 502p/4s; **PostgreSQL-pinned run of the API matrix: NOT EXECUTED** (suite is SQLite-per-test by design; PG path covered by smoke + CI) |
| 10 | No synthetic data leaks outside staging | **VERIFIED** — data only in disposable DB (dropped at end of rehearsal context); dumps in `/tmp`, 96 KB each, ephemeral; nothing copied off-host |

## 5. Staging environment variables (exact set; owner creates, never this agent)

```
TALIMGO_ENV=production
TALIMGO_SESSION_SECRET=<owner-generated, 48+ random bytes>
TALIMGO_DATABASE_URL=postgresql+psycopg://talimgo_staging_app:<url-encoded-password>@postgresql-<account>.alwaysdata.net:5432/talimgo_staging
TALIMGO_ALLOWED_ORIGINS=https://staging.<talimgo-domain>     # exact origin, no wildcard
TALIMGO_AI_ENABLED=false
TALIMGO_AI_STRICT=true
TALIMGO_SEED_ON_STARTUP=false
```
Written by the owner to a private file (mode 0600, outside git) or injected via the site's
environment field; never echoed; `TALIMGO_ENV_FILE` may point at it.

## 6. Owner actions required to finish staging (in order)

1. Provide/confirm dedicated TALIMGO-only AlwaysData scope (see D12_ALWAYSDATA_ACCOUNT_VERIFICATION.md R-1) and plan ≥ Small.
2. Create database `talimgo_staging` (admin panel) — or approve running `provision_staging.sql` (§2) with two strong, owner-generated passwords.
3. Confirm the dedicated staging login (panel: all privileges on `talimgo_staging` only) — migration identity may be the same login for staging; never for anything else.
4. Authorize in writing: running `alembic upgrade head` + `load_curriculum.py` (synthetic only) against `talimgo_staging`; the backup/restore rehearsal into a scratch DB `talimgo_restore_test`; its subsequent drop.
5. Provide the staging domain decision (or SSH-only path) and the staging env file location.
6. After (1–5): the operator (with owner present) executes §3 order of operations and records outputs; nothing proceeds to production until every row of §4 is VERIFIED on the real account.

## 7. Hard stops (no exceptions in D.12)

No creation/modification of any AlwaysData resource; no production database contact; no
`talimgo_runtime` usage in any form; no migration history edits; no SQLite-as-PostgreSQL claims;
no scratch/production database dropped without owner authorization; no secrets in files, logs or
chat (D.10 scan carried forward; D.12 docs and SQL re-scanned — clean).
