# TALIMGO staging — provisioning scripts (review, do not execute blindly)

Purpose: create the isolated staging scope designed in `docs/D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md`.
**Not executed against any real account.** Validated against a disposable local PostgreSQL 16.2
cluster during Phase D.12; validation evidence is summarized in `docs/D12_FINAL_REPORT.md` §6–§8.

Files:
- `provision_staging.sql` — idempotent roles/database/grants/revokes. No secrets (passwords via psql `-v`).
- `verify_staging.sql` — permission probes run as the app role (DDL refusal, DML allowed, roles/membership).

Order of operations (production or AlwaysData — after owner gates in `docs/D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md`):

1. Owner provisions the dedicated TALIMGO scope + ≥ Small plan (AlwaysData panel actions, listed in the matrix).
2. Admin runs `provision_staging.sql` (or panel equivalents on AlwaysData).
3. Operator applies `alembic upgrade head` as `talimgo_staging_migrate`.
4. Operator runs `alembic check` (expect: No new upgrade operations detected.).
5. Operator loads synthetic curriculum: `python scripts/load_curriculum.py` (as migrate role).
6. Operator verifies: `verify_staging.sql` as `talimgo_staging_app`; smoke tests; backup/restore rehearsal (`docs/D12_STAGING_BACKUP_RESTORE_VERIFICATION.md`).
7. Application connects as `talimgo_staging_app` only. The migrate role is never used at runtime.

Non-goals: creating production objects, dropping anything, granting beyond `talimgo_staging`, touching AUSTRO scopes.
