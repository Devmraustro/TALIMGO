# TALIMGO — Alwaysdata deployment runbook

**Status: PREPARATION ONLY — not executed against an Alwaysdata account.**

This runbook adapts the repository's production contract to Alwaysdata's documented Python ASGI
and PostgreSQL capabilities. It does not assert that an account, site, database, domain, DNS record,
or production credential has been provisioned.

## 0. Ownership and isolation gate — mandatory

Before any provisioning or database command, the owner must confirm all of the following in the
Alwaysdata administration interface:

- The account is owned/controlled by the TALIMGO project owner and is dedicated to TALIMGO.
- The web site and PostgreSQL database/login are newly created or explicitly confirmed as TALIMGO-only.
- The account's quota/plan supports the expected long-running user program, process count, CPU/RAM,
  storage, PostgreSQL capacity and required uptime.
- A domain/subdomain is controlled by the owner and its DNS/TLS path is understood.

**Hard stop:** never reuse an account, database, role, environment file, backup or host that may
belong to AUSTRO. Do not connect to any previously mentioned `austro_*` PostgreSQL resources.
Do not read or copy an AUSTRO environment file. If isolation cannot be proved, stop before
connecting or migrating.

## 1. Platform fit

Alwaysdata documents Python ASGI applications as a **Web > Sites > User program** using Uvicorn.
The User program receives the site's `$IP` and `$PORT` values and must listen on them; the Python
configuration documentation explicitly shows this deployment model.

Alwaysdata also documents PostgreSQL connection details as account-specific, normally on port
5432. Retrieve the exact hostname, database, user and permissions from the account's
**Databases > PostgreSQL** administration screen; do not derive them from another account.

Official platform references:

- [Python / ASGI configuration](https://help.alwaysdata.com/en/docs/web-hosting/languages/python/configuration/)
- [Using User Program type](https://help.alwaysdata.com/en/docs/web-hosting/sites/http-servers/user-program/)
- [Adding a site](https://help.alwaysdata.com/en/docs/web-hosting/sites/add-a-site/)
- [PostgreSQL connection and permissions](https://help.alwaysdata.com/en/docs/web-hosting/databases/postgresql/)

## 2. Code checkout and Python environment

Use an owner-controlled Git checkout and deploy a reviewed commit from `main`. Do not store a
GitHub token in the repository or paste credentials into chat.

Example layout (replace the path with the account's actual home directory):

```bash
mkdir -p "$HOME/apps/talimgo"
cd "$HOME/apps/talimgo"
git clone --branch main --single-branch https://github.com/Devmraustro/TALIMGO.git current
cd current/backend

PYTHON_VERSION=3.11 python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/pip install .
```

The backend declares Python `>=3.11` and includes Uvicorn and the PostgreSQL Psycopg driver.
Install development extras only when running tests; the production runtime does not need pytest,
Ruff or Bandit.

Record the exact deployed commit and keep the previous release available for rollback.

## 3. Create a dedicated PostgreSQL database

In Alwaysdata administration, open **Databases > PostgreSQL** and create a TALIMGO-only database
and a dedicated least-privilege login with the schema/table/sequence rights required by Alembic.
Do not use a shared personal account login or an existing database whose ownership is uncertain.

Alwaysdata's docs list PostgreSQL on port 5432 and state that the exact hostname is account-specific.
Use the hostname and port shown by the Alwaysdata account screen; encode reserved characters in the
database URL username/password correctly. The application expects SQLAlchemy's Psycopg URL form:

```text
postgresql+psycopg://<dedicated-user>:<url-encoded-password>@<account-host>:5432/<dedicated-database>
```

Do not publish this URL, put it in Git, or include it in support messages.

## 4. Production environment — store securely

Create a private environment file outside the Git checkout, readable only by the account user,
or set the same variables in the Alwaysdata site's environment field. Do not echo the file or run
commands that print its contents.

Required production values:

```dotenv
TALIMGO_ENV=production
TALIMGO_SESSION_SECRET=<generate-a-unique-random-secret-of-at-least-32-characters>
TALIMGO_DATABASE_URL=<dedicated-TALIMGO-PostgreSQL-URL>
TALIMGO_ALLOWED_ORIGINS=<exact-https-browser-origin>
TALIMGO_AI_ENABLED=false
TALIMGO_AI_STRICT=true
TALIMGO_SEED_ON_STARTUP=false
```

Generate the session secret on the Alwaysdata account using a cryptographic random generator,
for example `openssl rand -base64 48`. Never reuse development or preview secrets. If using
`TALIMGO_ENV_FILE`, point it to the private file's absolute path. Confirm the User Program can
read it without exposing it in the process command line or logs.

Production configuration is fail-closed: `TALIMGO_ENV=production` requires a sufficiently long
non-development session secret and a valid PostgreSQL database URL. Wildcard origins are rejected.
Keep AI disabled until a real local runtime has been provisioned, evaluated and approved.

## 5. Apply migrations — only after the ownership gate

SSH into the isolated TALIMGO account. Load the environment from the private file without printing
it, then execute:

```bash
cd "$HOME/apps/talimgo/current/backend"

# The file must be private and contain only the approved production variables.
set -a
. "$HOME/.config/talimgo/production.env"
set +a

.venv/bin/python scripts/check_production_config.py
.venv/bin/alembic upgrade head
.venv/bin/alembic check
```

Expected final Alembic check: `No new upgrade operations detected.`

**Do not run these commands until the owner has verified that the database is newly provisioned,
empty, exclusively TALIMGO-owned, and backed up according to the owner's policy.** Do not run them
against any shared, legacy, AUSTRO or guessed endpoint.

## 6. Configure the ASGI User Program

In Alwaysdata **Web > Sites > Add a site**:

- Type: **User program**.
- Working directory: absolute path to `$HOME/apps/talimgo/current/backend`.
- Command (no development reload):

```bash
.venv/bin/uvicorn app.main:app --host "$IP" --port "$PORT" --workers 1
```

- Environment: provide `TALIMGO_ENV_FILE` if using the protected env file, or the explicit
  production variables listed above. Preserve Alwaysdata's `IP` and `PORT` values.
- Address: use a TALIMGO-controlled hostname/subdomain with TLS configured.

Alwaysdata requires the User Program to listen on the supplied IP and port. Do not hard-code
`127.0.0.1` or an arbitrary port for the public site.

The program runs Uvicorn with one worker initially, matching the repository's documented
process-local concurrency gate. Multi-process deployment needs a separate review of aggregate
model limits (AI stays off in this runbook).

## 7. Same-origin frontend/API routing — deployment blocker until proven

The current browser client requests relative `/api/...` paths and uses same-origin credentials.
The session cookie is `SameSite=Lax`. Therefore the production browser must see the frontend and
API through **one origin**, either:

1. a single host serving the built frontend and proxying `/api` to the FastAPI User Program; or
2. the Vercel frontend with a server-side `/api/*` rewrite to the Alwaysdata API host.

A browser-side call from one origin directly to a separate API origin is **not supported** by the
current client and cookie configuration. Do not change cookie policy, disable CSRF-related request
guards, add permissive CORS, or expose a private model port to work around it.

The exact Alwaysdata path-based proxy configuration has not been tested on the owner's account.
Before enabling public traffic, prove that the selected site topology routes `/api` without changing
the browser-visible origin, preserves cookies and security headers, and passes the deployment
verifier. If the platform plan/site type cannot provide that topology, stop and record the owner
decision rather than deploying a broken split-origin interface.

## 8. Frontend build and release checks

From `frontend/`:

```bash
npm ci --no-audit --no-fund
npm run typecheck
npm test -- --run
npm run build
node scripts/check-bundle.mjs --dist dist
node scripts/check-licences.mjs
npm audit
```

Serve the resulting `frontend/dist` through the same-origin site/reverse proxy selected above.
Keep the deployment headers aligned with `frontend/vercel.json` and
`deploy/nginx/talimgo.conf.example`. Do not serve an API endpoint as an HTML fallback or let a
static host answer `/api` with an HTML 404 page.

## 9. Verify the real site

Only after the account, database, domain and same-origin routing are confirmed:

1. Check TLS and HTTP-to-HTTPS redirect.
2. Check `GET /api/health` returns TALIMGO JSON, not a static-host HTML page.
3. In production, check `/api/docs` and `/api/openapi.json` return 404.
4. Inspect the required hardening headers and cookie flags.
5. Run the existing disposable-account verifier against the exact owner-controlled HTTPS origin:

```bash
.venv/bin/python scripts/verify_deployment.py --base-url https://<verified-host> --host <verified-host>
```

The verifier creates and deletes a disposable account. Run it only against the isolated TALIMGO
production/staging database after owner approval; verify the account is removed and its session
is invalidated. Never test against a public third-party system or any AUSTRO resource.

## 10. Maintenance, backup and rollback

- Use Alwaysdata's **Scheduled tasks** feature only after reviewing task overlap, account quotas and
  its exact execution environment. A dry run first:

  ```bash
  cd "$HOME/apps/talimgo/current/backend"
  .venv/bin/python -m app.maintenance --dry-run
  ```

- Schedule the normal maintenance command only after its report is reviewed and a retention policy
  is approved. The application intentionally does not prune audit logs.
- Configure and test PostgreSQL backups and a restore to a separate disposable TALIMGO database.
  Never test restore over the live database.
- Keep the previous code release. For rollback, restore the previous application release and restart
  the User Program; prefer a forward-only database correction over destructive downgrades.

## 11. Current readiness checklist

- [ ] Dedicated TALIMGO Alwaysdata account confirmed by owner.
- [ ] Dedicated PostgreSQL database and login created; no AUSTRO/shared resource involved.
- [ ] Domain/DNS/TLS and Alwaysdata plan capabilities confirmed.
- [ ] Python venv and package install tested.
- [ ] Production config preflight passes against the dedicated DB settings.
- [ ] Alembic migrations and drift check pass against that dedicated database.
- [ ] ASGI User Program starts on Alwaysdata's supplied `$IP` and `$PORT`.
- [ ] Same-origin `/api` routing is proved; session cookie and headers verified in browser.
- [ ] Health check and disposable deployment verifier pass; test account cleanup confirmed.
- [ ] Backup/restore rehearsal and maintenance schedule verified.
- [ ] Real local model separately selected, licensed, installed and evaluated before AI is enabled.

**No box is checked by this document alone.** This runbook is preparation, not evidence of a live
deployment.
