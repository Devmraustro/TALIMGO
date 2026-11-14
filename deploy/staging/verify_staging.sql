-- TALIMGO staging permission verification (read-only).
-- Run connected as the role being verified, normally talimgo_staging_app:
-- psql -h <host> -U talimgo_staging_app -d talimgo_staging -f deploy/staging/verify_staging.sql
--
-- This file intentionally contains SELECT statements only. It does not create, alter,
-- drop, grant, revoke, change roles, or change session authorization. Run any DDL-denial
-- experiments only against a disposable staging database using a separate test procedure.

SELECT
    'role attributes' AS check_name,
    rolname,
    rolsuper,
    rolcreatedb,
    rolcreaterole,
    rolreplication
FROM pg_roles
WHERE rolname = current_user;

SELECT
    'database context' AS check_name,
    current_database() AS database_name,
    current_user AS role_name;

-- Read access used by the application.
SELECT 'read objectives' AS check_name, count(*) AS row_count
FROM public.objectives;

SELECT 'read alembic head' AS check_name, version_num
FROM public.alembic_version;

-- Privilege inventory. The application role should not have schema/database creation
-- rights or DDL-capable table privileges. Review the boolean values against the runbook.
SELECT
    'schema/database privileges' AS check_name,
    has_database_privilege(current_user, current_database(), 'CREATE') AS can_create_database_objects,
    has_schema_privilege(current_user, 'public', 'CREATE') AS can_create_in_public_schema;

SELECT
    'objectives table privileges' AS check_name,
    has_table_privilege(current_user, 'public.objectives', 'SELECT') AS can_select,
    has_table_privilege(current_user, 'public.objectives', 'INSERT') AS can_insert,
    has_table_privilege(current_user, 'public.objectives', 'UPDATE') AS can_update,
    has_table_privilege(current_user, 'public.objectives', 'DELETE') AS can_delete,
    has_table_privilege(current_user, 'public.objectives', 'TRUNCATE') AS can_truncate,
    has_table_privilege(current_user, 'public.objectives', 'REFERENCES') AS can_references,
    has_table_privilege(current_user, 'public.objectives', 'TRIGGER') AS can_trigger;

-- Membership inventory. Investigate any membership in migration, owner, or privileged roles.
SELECT
    'role memberships' AS check_name,
    granted_role.rolname AS granted_role,
    membership.admin_option
FROM pg_roles AS granted_role
JOIN pg_auth_members AS membership ON membership.roleid = granted_role.oid
JOIN pg_roles AS member_role ON member_role.oid = membership.member
WHERE member_role.rolname = current_user
ORDER BY granted_role.rolname;

-- Cross-database isolation cannot be proven from a query inside this database.
-- Verify from the deployment operator's shell, without changing any resources:
--   psql -h <host> -U talimgo_staging_app -d <talimgo_prod_like> -c 'select 1'
--   psql -h <host> -U talimgo_staging_app -d <austro_prod_like> -c 'select 1'
-- Both connections must be denied. Never substitute production or AUSTRO credentials here.
