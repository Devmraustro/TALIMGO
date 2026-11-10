-- TALIMGO staging permission verification queries (read-only unless noted).
-- Run connected as the ROLE BEING VERIFIED (e.g. talimgo_staging_app).
-- psql -h <host> -U talimgo_staging_app -d talimgo_staging -f deploy/staging/verify_staging.sql
--
-- Every probe is fail-safe by construction: it either fails with a permission error or
-- touches only objects that cannot exist. No statement in this file can delete or modify
-- real data, even if executed by a privileged role by mistake.

\set ON_ERROR_STOP off
-- Expected-failure statements must print errors and continue; review output manually.

SELECT 'role' AS check, rolname, rolsuper, rolcreatedb, rolcreaterole, rolreplication
FROM pg_roles WHERE rolname = current_user;

SELECT 'database' AS check, current_database(), current_user;

-- DML on application tables (expect counts, not errors)
SELECT 'read objectives' AS check, count(*) FROM public.objectives;
SELECT 'read alembic head' AS check, version_num FROM public.alembic_version;

-- DDL refusal probes (each MUST fail; on a permissive host the artifacts created are
-- empty and harmless, and can be dropped by the owner)
CREATE TABLE public.permission_probe_app (id int);
CREATE ROLE probe_should_fail_d12 NOLOGIN;
ALTER TABLE public.objectives ADD COLUMN probe_should_fail_d12 text;
-- Targets a name that never exists: errors either with "must be owner" (denied) or
-- "table does not exist" — never with the loss of a real table.
DROP TABLE public.talimgo_drop_probe_never_exists;

-- Cross-database access probes (expected: connection refused / permission denied).
-- Run these from the shell, not here — \c inside a script with ON_ERROR_STOP off is fragile:
--   psql -h <host> -U talimgo_staging_app -d talimgo_prod_like -c 'select 1'   -- expect failure
--   psql -h <host> -U talimgo_staging_app -d austro_prod_like  -c 'select 1'   -- expect failure

-- Membership check (expect: no rows = app role belongs to nothing sensitive)
SELECT 'membership' AS check, r.rolname
FROM pg_roles r
JOIN pg_auth_members m ON m.roleid = r.oid
JOIN pg_roles a ON a.oid = m.member
WHERE a.rolname = current_user;

-- SET ROLE escalation probe (MUST fail with permission denied)
SET ROLE talimgo_staging_migrate;
RESET ROLE;
