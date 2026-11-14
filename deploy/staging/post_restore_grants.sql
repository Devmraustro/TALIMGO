-- TALIMGO staging — grants to (re)apply after a restore from backup.
-- Purpose: a restore with --no-owner --no-acl (or a provider-managed restore) does not carry the
-- runtime role's DML rights. Run this INSIDE the restored database as the migration owner:
--   psql -h <host> -U talimgo_staging_migrate -d talimgo_restore_test -v ON_ERROR_STOP=1 \
--        -f deploy/staging/post_restore_grants.sql
-- Idempotent. Contains no secrets and never grants beyond the restored database.

\set ON_ERROR_STOP on

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO talimgo_staging_migrate;
GRANT USAGE ON SCHEMA public TO talimgo_staging_app;

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO talimgo_staging_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO talimgo_staging_app;

ALTER DEFAULT PRIVILEGES FOR ROLE talimgo_staging_migrate IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO talimgo_staging_app;
ALTER DEFAULT PRIVILEGES FOR ROLE talimgo_staging_migrate IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO talimgo_staging_app;

REVOKE CREATE ON SCHEMA public FROM talimgo_staging_app;
