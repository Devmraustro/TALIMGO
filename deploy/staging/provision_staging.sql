-- TALIMGO staging provisioning — idempotent. NO secrets in this file.
-- Usage (as a PostgreSQL superuser or a role permitted to CREATE ROLE/DATABASE;
--        NEVER as talimgo_staging_app):
--   psql -h <host> -p 5432 -U <admin> -d postgres \
--        -v migrate_password='...' -v app_password='...' \
--        -v ON_ERROR_STOP=1 -f deploy/staging/provision_staging.sql
--
-- Creates ONLY:  role talimgo_staging_migrate (DDL/migration identity),
--                role talimgo_staging_app     (DML/runtime identity),
--                database talimgo_staging      (owned by talimgo_staging_migrate).
--
-- On AlwaysData, per-database grants are all-or-read-only and roles are created through the
-- administration panel. In that case: create database talimgo_staging + a dedicated login in
-- the panel, and use the in-database sections (schema grants, default privileges, revokes)
-- as the SQL reference for what the panel + this file achieve together. The CREATE ROLE /
-- CREATE DATABASE statements are for self-managed PostgreSQL (e.g. a disposable local cluster).
--
-- NOT for production. NOT for AUSTRO-adjacent scopes. Review before real use.

\set ON_ERROR_STOP on

-- 1) Roles ---------------------------------------------------------------
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'talimgo_staging_migrate') THEN
    CREATE ROLE talimgo_staging_migrate LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'talimgo_staging_app') THEN
    CREATE ROLE talimgo_staging_app LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE;
  END IF;
END
$$;

-- Passwords come from psql variables and are never stored in this file.
-- Re-running with the same variables is idempotent; rotating = re-run with new values.
ALTER ROLE talimgo_staging_migrate PASSWORD :'migrate_password';
ALTER ROLE talimgo_staging_app PASSWORD :'app_password';

-- 2) Database --------------------------------------------------------------
SELECT format('CREATE DATABASE talimgo_staging OWNER talimgo_staging_migrate')
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'talimgo_staging') \gexec

-- Hard check: if the database exists but is NOT owned by the migrate role, stop.
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_database
             WHERE datname = 'talimgo_staging'
               AND pg_get_userbyid(datdba) <> 'talimgo_staging_migrate') THEN
    RAISE EXCEPTION 'talimgo_staging exists but is not owned by talimgo_staging_migrate — STOP and investigate';
  END IF;
END
$$;

-- 3) Database-level access --------------------------------------------------
REVOKE ALL ON DATABASE talimgo_staging FROM PUBLIC;
GRANT CONNECT ON DATABASE talimgo_staging TO talimgo_staging_migrate;
GRANT CONNECT ON DATABASE talimgo_staging TO talimgo_staging_app;

-- 4) In-database hardening --------------------------------------------------
\c talimgo_staging

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO talimgo_staging_migrate;
GRANT USAGE ON SCHEMA public TO talimgo_staging_app;

-- Tables/sequences created later by the migrate role are DML-visible to the app role.
ALTER DEFAULT PRIVILEGES FOR ROLE talimgo_staging_migrate IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO talimgo_staging_app;
ALTER DEFAULT PRIVILEGES FOR ROLE talimgo_staging_migrate IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO talimgo_staging_app;

-- Explicit grants for objects that already exist (idempotent).
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO talimgo_staging_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO talimgo_staging_app;

-- 5) App role must have NO DDL rights ---------------------------------------
REVOKE CREATE ON SCHEMA public FROM talimgo_staging_app;

-- 6) Proof summary -----------------------------------------------------------
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole FROM pg_roles
WHERE rolname IN ('talimgo_staging_migrate', 'talimgo_staging_app') ORDER BY 1;
SELECT datname, pg_get_userbyid(datdba) AS owner FROM pg_database
WHERE datname = 'talimgo_staging';
