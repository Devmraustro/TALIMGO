# D.12 — Staging backup & restore verification (2026-11-10)

**Scope:** prove the dump → restore → verify path for the staging database. Nothing ran against
production (no production contact exists anywhere in D.12). Everything below executed on a
**disposable loopback PostgreSQL 16.2** cluster (see D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md
§3) — it validates the *procedure*; the AlwaysData-hosted rehearsal remains **BLOCKED** until the
owner provisions/authorizes the staging scope (§6 of that document). Provider-managed daily backups
are **not** treated as application-level recovery evidence; they are listed as defense-in-depth only.

## 1. What was executed (all 2026-11-10, synthetic data)

| # | Step | Tooling | Result |
|---|---|---|---|
| 1 | Seed disposable `talimgo` (migrated to head, synthetic curriculum loaded, one synthetic account+goal) | `alembic upgrade head`, `scripts/load_curriculum.py`, `scripts/postgres_smoke.py` | PASS (20/20/68/2; users=goals=1) |
| 2 | **Repository-native rehearsal**: `scripts/postgres_backup_restore.py` (loopback-only by design; refuses other targets) | `pg_dump --format=custom` → restore into `talimgo_restore` → compare every public-table row count → compare Alembic revision → run smoke against the **restored** DB → drop scratch | **PASS (exit 0, 2.263s wall)** — "all public table row counts and Alembic revision match, and restored API health/account/session/goal smoke passed" |
| 3 | Independent custom-format dump of the staging-shaped DB (`talimgo_staging`, 28 tables, 95 435 bytes) | `pg_dump --format=custom --no-owner --no-acl` | **PASS — dump 0.053 s** |
| 4 | Restore into separate disposable DB `talimgo_restore_test` (owner = migration role) | `pg_restore --exit-on-error --no-owner --no-acl` | **PASS — restore 0.187 s** |
| 5 | Post-restore grants re-applied (`deploy/staging/post_restore_grants.sql`) — required because `--no-owner --no-acl` restores no runtime rights | psql as migration role | **PASS** |
| 6 | Migration/version consistency on restored DB | `alembic check` as migration role against `talimgo_restore_test` | **"No new upgrade operations detected."** (head `d5b8e0f13a72`) |
| 7 | Row parity (BEFORE any post-restore app traffic) | psql counts, 7 tables (objectives, users, lessons, goals, items, plans, projects) | **7/7 exact match** (20/1/20/1/68/0/2) |
| 8 | Application smoke against restored DB **as the runtime role** (`talimgo_staging_app`) | `scripts/postgres_smoke.py` (TestClient boot: /api/health → register → session read-back → goal create+read) | **PASS** |
| 9 | Maintenance command against staging DB as runtime role | `python -m app.maintenance --dry-run` | **PASS** (0 rows pruned; dry run only) |
| 10 | Scratch teardown | `DROP DATABASE talimgo_restore_test` | **PASS** (verified 0 rows in pg_database) |

**Dump artifacts:** `/tmp/d12-staging-backup.dump`, `/tmp/d12-staging-backup2.dump` (96 KB each,
synthetic only, ephemeral sandbox `/tmp`, never left this machine, never committed).

## 2. Measured recovery characteristics (this rehearsal)

- **Dump:** ~0.05 s · **Restore:** ~0.14–0.19 s · full rehearsal incl. smoke: ~2.3 s.
- **RPO** (assumed, this topology): bounded by the owner's chosen dump frequency — weekly dump
  ⇒ ≤ 7 days; AlwaysData native daily backup ⇒ ≤ 24 h provider-side. No WAL archiving is
  configured (none offered as a self-managed primitive on shared AlwaysData plans; do not assume it).
- **RTO** (measured, synthetic 95 KB): seconds, dominated by client start, not I/O. **Not** a
  production RTO promise — production dump volume, locks and panel operations will be slower and
  are unmeasured until the owner authorizes G6 on the real scope.
- Data-loss assumption: any restore point loses writes since the last dump; see retention decision
  (owner) in §4.

## 3. Verification after an AlwaysData-side restore (procedure recorded, NOT executed)

1. Admin: create or clean the disposable scratch DB (owner authorizes both).
2. Restore (`zstdcat <platform dump>.sql.zst | psql … -d talimgo_restore_test`) **or**
   `pg_restore` of an owner-taken dump.
3. As `talimgo_staging_migrate`: `psql -f deploy/staging/post_restore_grants.sql`.
4. `alembic check` → expect "No new upgrade operations detected." (head will be whatever the dump contains).
5. Runtime-role smoke (`postgres_smoke.py`) against scratch → expect pass.
6. Compare counts (objectives/items/users/goals/plans/projects) vs pre-dump snapshot.
7. **Drop `talimgo_restore_test`. Only with owner authorization.**
8. Record times, dump size, operator, date in the release ticket.

## 4. Owner decisions required (open questions with defaults)

| Decision | Default proposal (not applied) |
|---|---|
| Dump frequency for staging/production | weekly owner `pg_dump` + plan-native daily backups (belt and braces) |
| Off-host storage location & retention | 4 weekly + 3 monthly, owner-controlled machine or encrypted object storage; never inside the app host only |
| Scratch rehearsal cadence | twice yearly, plus before every production release containing a migration |
| Drop authorization for scratch DBs | explicit owner "yes" per rehearsal, attached to the release record |
| Who runs restores | owner or operator under owner supervision at the time |

## 5. Explicit status

| Claim | Status |
|---|---|
| Backup/restore procedure works (dump → restore → parity → smoke → clean teardown) | **VERIFIED (local disposable PG 16.2)** |
| Repository's own rehearsal script passes end-to-end | **VERIFIED (local)** |
| AlwaysData-hosted backup/restore rehearsal | **NOT EXECUTED — BLOCKED** (no scope/credentials/authorization) |
| Production backup/restore | **NOT EXECUTED — prohibited** in D.12 and out of scope until release phase |
| Provider-managed daily backups count as DR | **REJECTED as sole evidence** — useful, but restore must be rehearsed, which this document rehearses (locally) and sets up (remotely) |

**Bottom line:** the recovery path is real and rehearsed, but only against a disposable local
cluster. It becomes deployment-grade when the owner opens the AlwaysData staging scope and the
same runbook is executed there with the same outputs.
