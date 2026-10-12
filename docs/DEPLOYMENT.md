# Deploying TALIMGO

This guide describes what a real deployment needs. It is written against the code in this repository
and is deliberately explicit about which parts have been exercised here and which have **not**: the
full API behaviour suite uses isolated SQLite databases; CI also applies the migration chain and runs a
focused startup/account/goal persistence smoke check against PostgreSQL 16. No externally managed
PostgreSQL server, reverse proxy, container runtime or TLS certificate has been used for a real deployment.

> Status: **draft for owner review.** Deploying is an owner action (hosting, domain, TLS, secrets).
> Nothing in this document has been executed in production.

## 1. Requirements

| Component | Requirement | Notes |
|---|---|---|
| Python | 3.11+ | `backend/pyproject.toml`; CI uses 3.11 |
| Database | PostgreSQL 14+ | SQLite is a development convenience only |
| Local model runtime | Ollama (dev) or a vLLM-class OpenAI-compatible server (production) | Optional: the app runs and degrades explicitly without it |
| Reverse proxy | nginx/Caddy/Traefik with TLS | Terminates HTTPS, sets `X-Forwarded-Proto`, caps body size and rate |
| CPU/RAM | Sizing depends on the model, not on the API | The API process itself is small (single worker is enough for a class-sized pilot) |
| Disk | Database + model weights + backups | Model weights are large: keep them off the database volume |

## 2. Configuration and validated startup

1. `cp backend/.env.example backend/.env` and edit it. The file next to the package is authoritative; a
   repository-root `.env` is also read as a fallback, and `TALIMGO_ENV_FILE` overrides both.
2. Set at minimum: `TALIMGO_ENV=production`, a `TALIMGO_SESSION_SECRET` of ≥32 random bytes,
   `TALIMGO_DATABASE_URL` (PostgreSQL), `TALIMGO_ALLOWED_ORIGINS` (the interface's exact origin(s) —
   wildcards are refused at startup).
3. Start the API **after** applying migrations:

```bash
cd backend
.venv/bin/alembic upgrade head          # creates/updates the schema
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1
```

### Production preflight

Run this against the *same* environment the API will start in, before starting it (and again on every
configuration change). It reads the application's settings and checks the production requirements in
this document, prints only names and verdicts — never values, so its output is safe to share — and
exits non-zero if anything is wrong:

```bash
cd backend && .venv/bin/python scripts/check_production_config.py
```

It also covers the one requirement the application itself does not enforce:

* `TALIMGO_ENV=production`, and the API then serves no interactive docs;
* `TALIMGO_SESSION_SECRET` of 32+ characters without a placeholder marker (the application refuses a
  weak or development secret in production, so the preflight reports that refusal);
* `TALIMGO_DATABASE_URL` on PostgreSQL. **The application will start on SQLite in production mode** —
  the deployment requirement is PostgreSQL 14+, and this check is what enforces it;
* at least one explicit `TALIMGO_ALLOWED_ORIGINS` entry, with no wildcard (the application refuses a
  wildcard at startup);
* tutoring off, or enabled with a model name and a local endpoint.

Startup is validated and fails closed:

* production refuses to start without a strong session secret;
* production refuses to create schema implicitly — if the `objectives` table is missing it raises with
  the exact command to run;
* if `TALIMGO_AI_ENABLED=true`, the endpoint must be loopback/private or the process refuses to start
  (`app/ai/policy.py`), so a typo cannot silently send learner content to a hosted provider;
* `TALIMGO_AI_MODEL` must name a model when AI is enabled.

Bind the API to loopback and let the proxy publish it. The interactive API docs are disabled
automatically in production (`/api/docs`, `/api/openapi.json` return 404).

## 3. Database

* Use PostgreSQL: `TALIMGO_DATABASE_URL=postgresql+psycopg://user:password@127.0.0.1:5432/talimgo`.
* Migrations are the only schema authority in production (`alembic upgrade head`); `alembic check`
  must report no drift before a deploy.
* CI runs the full Alembic migration chain and `alembic check` on PostgreSQL 16, including a
  dedicated populated-legacy-data rehearsal: it creates an account, goal, plan, week and plan item
  under revision `8f1c2d4e6a70`, upgrades to head, and verifies the plan's `starts_on` is backfilled
  to the database's current date, is non-nullable, and that the existing plan item survives with its
  optional schedule fields null. The API smoke test then checks account/session creation and goal
  write/read. The full API behaviour suite still uses per-test SQLite databases, so this is not a
  claim of complete PostgreSQL parity. Before production, rehearse backup/restore against the target
  PostgreSQL version and run the full pilot acceptance checklist.
* The AI usage counter uses a conditional `UPDATE ... WHERE count < limit` (atomic per row on both
  SQLite and PostgreSQL) rather than a read-then-write; that is what makes the per-learner budget
  safe under concurrency (see `backend/tests/test_ai_quota.py`).
* Authenticated mutating API requests are limited per learner by `TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE`
  (default 120 per UTC minute, fixed window). This is a per-account application guard, not a substitute
  for edge-level limits on unauthenticated routes or abusive distributed traffic.
* The local-model generation gate is per worker process: `TALIMGO_AI_MAX_CONCURRENT_REQUESTS`
  (default 1) with a bounded wait of `TALIMGO_AI_QUEUE_TIMEOUT_SECONDS` (default 2 seconds).
  A saturated request receives 503 before its daily AI allowance is claimed. Multi-worker deployments
  must also set a matching aggregate cap at the model host or proxy; the application gate is not
  a distributed semaphore.

## 4. HTTPS, reverse proxy and HSTS

Use the checked-in standalone example at `deploy/nginx/talimgo.conf.example` as the starting point.
Before deployment, replace `talimgo.example` with the actual hostname, provision the referenced
certificate/key, and ensure the frontend build is available at `/srv/talimgo/frontend/dist`. The API
is expected to listen on `127.0.0.1:8000`; it must not be published directly to the internet.

The example includes HTTP-to-HTTPS redirection (while allowing ACME challenges), TLS 1.2/1.3,
a 256 KiB request-body cap, static SPA routing, separate per-IP rate limits for authentication and
other API traffic, HSTS, and explicit replacement of forwarded headers. CI runs `nginx -t` against
this configuration and smoke-tests the redirect, TLS/static response, HSTS, the interface document
headers, spoofed forwarding headers, the pass-through of an API refusal, and the authentication rate
limit using an ephemeral test certificate and a fake local upstream. That validates the example
configuration and edge behaviour in CI, **not** the live domain, real certificate renewal, firewall,
or production routing. The same sequence is a usable pre-deployment rehearsal: run it locally with
the ports changed to unprivileged ones if you are not root, then repeat it against the real hostname
once DNS and the certificate exist.

HSTS intent in the example is one year for this host only: `includeSubDomains` and `preload` are
deliberately absent, because they commit every current and future subdomain to HTTPS. Add them only
when that is true for the whole domain, and record the decision.

The application sends `Strict-Transport-Security` only when the request arrives over HTTPS, which
means the proxy must set `X-Forwarded-Proto: https`. In the checked-in example, Nginx owns the public
HSTS header and hides the upstream copy to avoid duplicate values.

Two different surfaces need headers, and the example handles both:

* **API responses** get their policy from the application (`backend/app/http_hardening.py`):
  `nosniff`, `Referrer-Policy`, `X-Frame-Options`/`frame-ancestors`, `Permissions-Policy` and a
  `default-src 'none'` CSP. Proxied responses are passed through untouched.
* **The interface document** is served from disk by Nginx, so the application's headers never apply to
  it. `location /` in the example sets its own policy for HTML/JS/CSS: `nosniff`, `X-Frame-Options`,
  `Referrer-Policy`, the same `Permissions-Policy`, and a CSP that allows only this origin's own
  bundles. `style-src` includes `'unsafe-inline'` because the components use style attributes.
  Declaring `add_header` in that block cancels inheritance of the server-level HSTS header, which is
  why HSTS is repeated there — if you edit the block, keep it. CI asserts the headers are present; it
  cannot check that a browser *enforces* the CSP without breaking the interface, so load the deployed
  interface in a browser and check the console after the first deployment.

Edge refusals are shaped for the same clients as the API's own:

* a request refused by the Nginx limits is answered by Nginx with the API's JSON error shape
  (`{"detail": "..."}`) rather than an HTML error page. It carries no `Retry-After`, because the edge
  cannot state the exact refill time. The sentence is English-only, like the API's own limit messages;
* an API-generated 429/4xx/5xx is **not** intercepted: `proxy_intercept_errors` stays off, so the
  API's specific message and its `Retry-After` header reach the client unchanged. CI asserts this with
  a fake API refusal, so enabling interception later fails the build.

Proxy rules the application assumes but does not enforce itself:

* set `X-Forwarded-Proto`, `X-Forwarded-For` and `X-Real-IP` from trusted connection values, and
  discard the client-supplied `Forwarded` header; do not forward the request's untrusted versions;
* strip or replace `Server`/`X-Powered-By` at the edge if that is your policy;
* rate-limit at the edge as well as in the app: the example has stricter limits for `/api/auth/*`
  plus a broader API policy. Tune them to expected traffic before production;
* cap request bodies at the proxy (the example uses 256 KiB; the API also applies its own limit);
* keep session cookies intact: `HttpOnly`, `SameSite=Lax`, `Path=/`, and `Secure` in production.

The interface is a static build (`frontend/dist`) served by Nginx from the same origin. It calls the API
through `/api/...`, so this avoids adding a separate interface origin to `TALIMGO_ALLOWED_ORIGINS`.

### Where the built interface is hosted

TALIMGO's session cookie is `HttpOnly`, `Secure` in production and **`SameSite=Lax`**
(`backend/app/routers/auth.py`). That single fact decides which hostings work, because a `Lax` cookie
is not sent on cross-site requests:

1. **One host (supported, tested).** Nginx serves `frontend/dist` and proxies `/api` to FastAPI on the
   same origin — the checked-in `deploy/nginx/talimgo.conf.example`. Cookies are first-party, CORS is
   not involved, and CI exercises exactly this shape (edge smoke test, and the post-deployment
   verifier against a real edge and API).
2. **Vercel for the interface, API on another host, joined by a Vercel rewrite (supported,
   configuration not yet verified here).** Vercel proxies `/api/*` to the API host, so the *browser*
   still sees one origin and the `Lax` cookie keeps working. Add to `frontend/vercel.json` (the file
   already carries the interface's security headers) after replacing the API host:

   ```json
   "rewrites": [{ "source": "/api/(.*)", "destination": "https://<api-host>/api/$1" }]
   ```

   The API must then accept that traffic: `TALIMGO_ALLOWED_ORIGINS` still only needs the browser-facing
   origin (`https://<vercel-host>`), because the rewrite is server-side. This topology was **not**
   exercised in a real Vercel project during this work — no authorised API host existed — so treat it
   as documented-but-unverified until the post-deployment verifier passes on it.
3. **A separate API origin called directly by the browser (not supported).** With `SameSite=Lax` the
   session cookie would not be sent, so sign-in would silently fail. Supporting it needs a
   security-reviewed change (`SameSite=None; Secure` plus a CSRF re-review) and an exact
   `TALIMGO_ALLOWED_ORIGINS` entry; do not "fix" it by disabling cookie protections. If the browser
   origin and the API origin differ and no rewrite is in place, the interface now says so plainly
   instead of showing a bare status code.

Hosting the FastAPI backend *on* Vercel is out of scope: it needs a long-lived process, a persistent
PostgreSQL database, and (for tutoring) a local model runtime on TALIMGO-controlled infrastructure.

The current state of the existing Vercel project, and what only the owner can check there, is recorded
in [`VERCEL_DEPLOYMENT_STATUS.md`](./VERCEL_DEPLOYMENT_STATUS.md).

## 5. Secrets

* `TALIMGO_SESSION_SECRET` — 32+ random bytes, generated on the server (`openssl rand -base64 48`),
  never committed, never reused between environments. Rotating it invalidates every session.
* Database credentials live in the service environment (systemd `EnvironmentFile=`, Docker secret, or
  your platform's secret store), not in the repository and not in the same file as application code.
* Model runtime credentials (if the local server uses an API key) stay on the model host; the API
  process needs only the endpoint URL.
* `.gitignore` already excludes `.env`, `*.db`, `data/`, `secrets/`, `model_cache/` and weight files.

### Environment variable checklist (names, never values)

Values are created by the owner in the platform's secret store; nothing here is a value, and no value
belongs in the repository, an issue, a chat message or a log. `backend/.env.example` documents the same
names with non-production placeholders.

| Variable | Purpose | Where it is set | Notes |
| --- | --- | --- | --- |
| `TALIMGO_ENV` | Selects production validation | API service | `production` on a real deployment; the app then refuses weak secrets, serves no API docs and requires the schema to exist |
| `TALIMGO_DATABASE_URL` | PostgreSQL connection | API service (secret) | Must be a `postgresql+psycopg://` URL on PostgreSQL |
| `TALIMGO_SESSION_SECRET` | Signs/stores sessions | API service (secret) | Generate on the server; rotating it ends every session |
| `TALIMGO_ALLOWED_ORIGINS` | CORS allow-list | API service | Comma-separated exact origins; wildcards are rejected at startup. Not needed when the interface is same-origin |
| `TALIMGO_AI_ENABLED` | Turns tutoring on | API service | Keep `false` until a local runtime is provisioned and evaluated |
| `TALIMGO_AI_BASE_URL` | Local model endpoint | API service | Local-only by policy; startup refuses a non-local endpoint while `TALIMGO_AI_STRICT=true` |
| `TALIMGO_AI_MODEL` | Local model name | API service | Required when AI is enabled |
| `TALIMGO_AI_DIALECT` | Runtime protocol | API service | `ollama` or `openai_compatible` |
| `TALIMGO_SESSION_TTL_HOURS`, `TALIMGO_MAX_LOGIN_ATTEMPTS`, `TALIMGO_LOGIN_LOCKOUT_MINUTES`, `TALIMGO_MIN_PASSWORD_LENGTH`, `TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE`, `TALIMGO_MAX_REQUEST_BYTES` | Abuse and size limits | API service | Defaults are documented in `backend/.env.example`; change deliberately |
| `TALIMGO_AI_TIMEOUT_SECONDS`, `TALIMGO_AI_MAX_OUTPUT_TOKENS`, `TALIMGO_AI_MAX_CONCURRENT_REQUESTS`, `TALIMGO_AI_QUEUE_TIMEOUT_SECONDS`, `TALIMGO_AI_DAILY_REQUESTS_PER_LEARNER` | Model resource bounds | API service | Concurrency is per worker process; cap the aggregate at the model host |
| `TALIMGO_SEED_ON_STARTUP` | Loads the authored curriculum at boot | API service | Leave `false` in production and load content deliberately |
| `TALIMGO_ENV_FILE` | Points settings at an env file | API service | Optional; uses an absolute path |

The interface itself needs **no** build-time variables: it always calls `/api` on its own origin, which
is what keeps the `Lax` session cookie usable (see "Where the built interface is hosted"). If you
configure a hosting provider, do not add an "API base URL" variable to it — put the routing in the
provider's proxy/rewrite configuration instead.

## 6. Local model isolation and outbound restrictions

* Run the model runtime on the same host (or a private network the API can reach) and bind it to
  loopback where possible; the API only talks to the configured local endpoint.
* Apply egress policy at the host/firewall level: the API host should have **no** outbound access to
  the public internet. `backend/scripts/check_no_external_ai.py` and `app/ai/policy.py` are code-level
  guarantees; network egress rules are the deployment-level backstop that actually makes them
  enforceable.
* Give the model directory its own volume and resource limits (see §8). Learner content is sent to the
  local model only — never to a hosted provider; there is no provider SDK or key in this repository.

## 7. Health checks, logs, observability

* `GET /api/health` → `{"status": "ok", "version": ...}` — use it for liveness/readiness.
* `GET /api/health/ai` → AI policy state (`ai_enabled`, dialect, endpoint host class, policy
  `local-only`) without secrets.
* Logs go to stderr as structured lines from the `talimgo` logger (`%(asctime)s %(levelname)s
  %(name)s %(message)s`). Ship them to your collector; keep them free of learner content (the app never
  logs request bodies).
* Audit events (`audit_log`) record account, consent and plan changes for accountability; retention of
  audit rows is an owner policy decision (see §9).

### Post-deployment verification

`backend/scripts/verify_deployment.py` checks a real, authorised HTTPS target end to end. It is not a
penetration test or a load test, and a pass says nothing about the local model runtime:

```bash
backend/.venv/bin/python scripts/verify_deployment.py \
  --base-url https://talimgo.example --host talimgo.example
```

It refuses a plain-HTTP target and refuses a `--host` that does not match `--base-url`, so a typo
cannot point a run of account-creating requests at the wrong service. Certificate verification is on;
`--insecure-tls` exists for a rehearsal host whose certificate is not trusted yet and must never be
used for a real deployment. `--http-port` exists only to rehearse on a non-privileged port. It checks:

1. the plain-HTTP entry point redirects to HTTPS, keeping path and query;
2. `/api/health` answers `status: ok`, with HSTS, `nosniff`, `Referrer-Policy` and a framing refusal
   present on the response;
3. `/api/docs` is not served (a production deployment must set `TALIMGO_ENV=production`);
4. one **disposable** account is created with a fresh random password for that run, its
   session survives a new request, a goal is written and read back, then the account is deleted and its
   session is refused. If the registration response is lost or returns a server error after account
   creation, the verifier attempts to log in with the same in-memory credentials and remove the account.
   The email is printed only if cleanup cannot be confirmed; inspect the target database if that happens.

The same command is available as a manual GitHub workflow (`.github/workflows/deploy-verify.yml`,
`workflow_dispatch` only). That workflow never deploys anything and holds no credentials: it just runs
these checks from a clean runner. A target reachable only from your own network must be verified with
the command above from inside that network instead.

### Browser smoke in CI

The `browser-smoke` CI job installs pinned Playwright/Chromium and `axe-core` into a temporary
runner directory (not the application bundle or the frontend dependency manifest). It exercises the real
FastAPI backend through the Vite same-origin proxy in a disposable SQLite environment. It creates an
account, sets a goal, submits a real diagnostic answer, switches the interface to Arabic and verifies
`lang=ar` and `dir=rtl`, checks that a 390-pixel viewport has no horizontal overflow, deletes the account,
verifies the session is rejected, and fails on uncaught page errors, API 5xx responses, or requests to
another host/port. Failure screenshots and server logs are retained as a short-lived CI artifact.

The same Chromium job runs `axe-core 4.10.3` against WCAG 2.0/2.1/2.2 Level A and AA rules on the English
registration, goal and diagnostic forms in light mode, and on Arabic RTL settings plus registration
after deletion in dark mode. This catches common machine-detectable issues (including many contrast and
naming errors) in those representative states. It is **not** a full accessibility audit: automated checks
cannot establish meaningful screen-reader operation, all keyboard focus order, or every content-dependent
contrast case. The job uses Vite's development server and a disposable database, so it does not prove that
the production Nginx CSP permits the built app while blocking disallowed sources. The deployed HTTPS build
still needs a browser and console check.

What CI does **not** cover, and what remains manual: screen-reader behaviour, a human contrast review in
the actual deployed theme, 200–400% zoom and reflow, complete focus order after dynamic updates, the local
model's answers, backup/restore durability outside the host, and DNS/certificate issuance or renewal
beyond trusting the certificate the runner sees.

## 8. Resource limits

| Limit | Where | Value |
|---|---|---|
| Request body | application | `TALIMGO_MAX_REQUEST_BYTES` (default 128 KiB; hard maximum 8 MiB) |
| Model output | application | `TALIMGO_AI_MAX_OUTPUT_TOKENS` (default 800; maximum 8192) |
| Model requests per learner per day | application | `TALIMGO_AI_DAILY_REQUESTS_PER_LEARNER` (default 100) |
| In-flight model generations | application worker | `TALIMGO_AI_MAX_CONCURRENT_REQUESTS` (default 1 per worker) |
| Model queue wait | application | `TALIMGO_AI_QUEUE_TIMEOUT_SECONDS` (default 2 seconds; then 503 before quota claim) |
| Authenticated mutating requests | application | `TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE` (default 120 per learner per UTC minute) |
| Model call timeout | application | `TALIMGO_AI_TIMEOUT_SECONDS` (default 60; maximum 600) |
| Session lifetime | application | `TALIMGO_SESSION_TTL_HOURS` (default 336) |
| Login attempts | application | `TALIMGO_MAX_LOGIN_ATTEMPTS` per email and per IP per window |
| Process memory/CPU | systemd/Docker | give the API a modest cap (e.g. 512 MiB); give the model runtime its own |
| Body size and request rate | reverse proxy | see §4 |

### systemd units (checked in, not sketched here)

`deploy/systemd/` holds complete, installable units rather than a fragment to be re-typed:

| File | What it runs |
|---|---|
| `talimgo-api.service.example` | The API: preflight → migrations → `uvicorn` on `127.0.0.1:8000` → readiness probe, under a non-root user, with `Restart=on-failure`, `MemoryMax=512M` and the hardening set (`ProtectSystem=strict`, `ProtectHome`, `PrivateTmp`, `NoNewPrivileges`, `RestrictAddressFamilies`, …) |
| `talimgo-maintenance.service.example` | `python -m app.maintenance` as a `oneshot`, separate so housekeeping never restarts the serving process |
| `talimgo-maintenance.timer.example` | Daily 03:30 with a randomised delay and `Persistent=true` (a run missed during downtime is not skipped silently) |

Installation, start order and inspection commands are at the top of the API unit. Two properties are
worth knowing before you install it:

* **A failed preflight or migration stops the start.** `ExecStartPre` runs
  `scripts/check_production_config.py` and then `alembic upgrade head`, so a weak secret, a wildcard
  origin, a SQLite database or a non-local AI endpoint never becomes a running service;
* **readiness is asserted, not assumed.** `ExecStartPost` runs `deploy/health-check.sh --wait 30`, so a
  process that starts but cannot answer `/api/health` is reported as a failed start. `TimeoutStartSec`
  is larger than the probe's wait for that reason.

The units are examples: check the paths, user and group against your host before installing. Binding
the API to `127.0.0.1` (as above) is what keeps it non-public; the only public entry point is the proxy
in §4.

## 9. Data maintenance, backup and restore

* Housekeeping (login attempts 30 days, sessions 30 days past expiry):

```bash
backend/.venv/bin/python -m app.maintenance --dry-run   # report only
backend/.venv/bin/python -m app.maintenance             # apply; safe from cron, idempotent
```

* Backups: `pg_dump` on a schedule to storage outside the host, plus the model directory if you have
  customised it (weights are re-downloadable; learner data is not). CI performs a format-custom
  `pg_dump`/ `pg_restore` rehearsal into a separate scratch database, compares the public table set,
  per-table row counts and Alembic revision, then runs the API health/account/session/goal smoke against
  the restored copy. This checks the backup/restore path on a disposable PostgreSQL 16 database; it
  does not test your off-host backup storage, encryption/key custody, retention, or recovery-time target.
  Configure and rehearse those owner-operated controls before real learner data is stored.
* The rehearsal script (`backend/scripts/postgres_backup_restore.py`) refuses to run unless the source
  is the database `talimgo` on `127.0.0.1`/`localhost` reached through `postgresql+psycopg` with a
  username and password present, so it cannot be pointed at a production host or an unrelated database.
  It writes its dump into a temporary directory, restores only into the scratch database
  `talimgo_restore`, and drops that scratch database on the way out whether the run succeeded or
  failed. If the drop itself fails the run ends non-zero and says the scratch database is still there;
  a cleanup failure never replaces the error that stopped the rehearsal. The other two scripts
  (`postgres_smoke.py`, `postgres_legacy_migration.py`) likewise refuse any non-`postgresql+psycopg`
  URL. Tests for these refusals and for the cleanup reporting live in
  `backend/tests/test_postgres_scripts.py`.
* Retention: learner data is kept until the learner deletes the account; deletion removes tutor
  messages, practice and diagnostic history, plans, evidence, consents and sessions, and anonymises
  audit rows (verified end to end in `backend/tests/test_account_lifecycle.py`). Audit retention and
  database backup retention are owner policy decisions — document them before onboarding real learners.
* Export: `GET /api/me/export` returns a machine-readable copy of everything held about the learner;
  exercise it as part of the pilot acceptance test.

## 10. Release procedure and rollback

### Ordered release (one host)

Run these in order, from the release checkout. Every step is a command that exists in this repository;
nothing here is a script you have to write on the host.

```bash
# 1. Interface: build, gate the artifact, stage it beside the served directory.
#    The gate refuses a bundle containing an insecure or local/private back-end address, and the
#    staging step swaps the release in with renames, keeping the previous one for rollback.
deploy/stage-frontend.sh --target /srv/talimgo/frontend

# 2. API configuration: the preflight reads the production environment and prints names, not values.
cd backend && .venv/bin/python scripts/check_production_config.py

# 3. Database: back up before a release that contains a migration, then apply migrations.
pg_dump --format=custom --no-owner --no-acl --file ~/talimgo-pre-release.dump "$PGDATABASE"
.venv/bin/alembic upgrade head && .venv/bin/alembic check

# 4. Service: restart under the unit, which re-runs the preflight, the migrations and the readiness
#    probe (see §8). A failed probe makes the start fail rather than leaving a half-served service.
sudo systemctl restart talimgo-api.service
deploy/health-check.sh --url http://127.0.0.1:8000 --wait 30 --ai

# 5. From outside: verify the deployment through the real edge and TLS (disposable account, removed
#    by the same run).
.venv/bin/python scripts/verify_deployment.py --base-url https://<host> --host <host>
```

`deploy/health-check.sh` is deliberately read-only: it never writes, never needs credentials and never
creates an account, so it is safe in a supervisor, a timer or a monitoring agent. Exit code 0 means
healthy, 1 unhealthy, 2 called wrongly. Bare `GET /api/health` wiring is acceptable for a load
balancer, but it will also accept a static host answering `200` with HTML — the script rejects that,
which is why it is the check to use for "is TALIMGO really up".

### Logging on a systemd host

* `journalctl -u talimgo-api -f` follows the API; `journalctl -u talimgo-api --since '1 hour ago'` looks
  back. `SyslogIdentifier=talimgo-api` keeps the unit's lines separable in a shared journal.
* The application logs one structured line per event from the `talimgo` logger and never logs request
  bodies or learner content (§7). Startup logs the environment and the local-only AI state, which is the
  first thing to read when tutoring is disabled.
* `uvicorn`'s own access log is off by default in the unit (access logging belongs at the proxy, which
  already records the request line). Add `--log-level info` or `--access-log` to `ExecStart` if you want
  it from the application too.
* Rotate and retain the journal per your policy: `journald` limits are host configuration and are **not**
  managed by this repository.

### Rollback

1. Application: `deploy/stage-frontend.sh` keeps the previous interface as `<target>.previous`; swap the
   two directories back (the exact commands are printed at the end of a staging run). The API is
   stateless apart from the database and the model runtime, so rolling the code back is a checkout plus
   a `systemctl restart talimgo-api.service`.
2. Database: migrations are additive so far, and `alembic downgrade -1` exists for every revision, but
   a downgrade that drops a column loses that column's data. Take a `pg_dump` **before** every deploy
   that includes a migration, and prefer rolling forward with a fix over rolling back.
3. Model runtime: pin the model and its version; if a model change degrades tutoring, revert the model
   tag — the application has no dependency on a specific model beyond the configured name.
4. After any rollback: re-run `GET /api/health`, one authenticated dashboard read, one practice answer
   and the migration drift check (`alembic check`).

## 11. Owner-only launch checklist

These steps need owner access, money or a decision. Nothing in the repository can do them, and no
deployment can be called verified until they are done and their results recorded.

| # | Owner action | Done when |
|---|---|---|
| 1 | **Authorise the production host** (a Python-capable VM/container on TALIMGO-controlled infrastructure) | You have a hostname and SSH/service access, and you have accepted that the API and PostgreSQL are no longer local development services |
| 2 | **DNS and TLS**: point the hostname at the host, obtain a certificate for it | `curl -I https://<host>` answers over TLS with a valid chain for that name |
| 3 | **Create the service user and directories**: `talimgo` user, `/srv/talimgo`, `/var/lib/talimgo`, `/etc/talimgo` | `systemctl start talimgo-api` can read its code and write only where it should |
| 4 | **Generate secrets on the host**: `TALIMGO_SESSION_SECRET` (`openssl rand -base64 48`), the PostgreSQL password, and the environment file at `/etc/talimgo/talimgo.env` (root-owned, mode 0600) | `scripts/check_production_config.py` passes on the host; no secret exists anywhere in the repository or in chat |
| 5 | **Provision PostgreSQL**: database and role for TALIMGO, reachable only from the API host, with your backup tooling pointed at it | `alembic upgrade head` runs on the host | 
| 6 | **Firewall/network**: 443 public, SSH restricted to the owner, PostgreSQL **not** reachable from the internet | An external port scan shows only 443 (and your SSH port) open |
| 7 | **Install the units** from `deploy/systemd/`, enable the API service and the maintenance timer | `systemctl status talimgo-api` is active and `systemctl list-timers talimgo-maintenance` shows the next run |
| 8 | **First release** by the procedure in §10, ending with `verify_deployment.py` against the real hostname | The verifier passes and its output is recorded (date, host, result) |
| 9 | **Backups**: schedule `pg_dump` to storage outside the host; decide retention; rehearse a restore with `backend/scripts/postgres_backup_restore.py` against a disposable copy | A restore has been performed from a real backup, and the retention decision is written down |
| 10 | **Local model runtime** (only when you want tutoring): provision it on TALIMGO-controlled infrastructure, evaluate it, then set `TALIMGO_AI_ENABLED=true` with a named model | `health-check.sh --ai` passes on the host, and no learner content leaves TALIMGO infrastructure |
| 11 | **Decide the fate of the Vercel preview** (`docs/VERCEL_DEPLOYMENT_STATUS.md`): keep it as an interface preview or delete it | No preview is presented as a working product |
| 12 | **Monitoring**: wire `deploy/health-check.sh` into your supervisor/monitoring and confirm an alert arrives when the API is stopped | You have seen a real alert from a deliberately stopped service |

## 12. First-deployment checklist

- [ ] `python backend/scripts/check_production_config.py` passes against the production environment.
- [ ] PostgreSQL running; `alembic upgrade head` applied; `alembic check` clean.
- [ ] `TALIMGO_ENV=production`, strong `TALIMGO_SESSION_SECRET`, exact `TALIMGO_ALLOWED_ORIGINS`.
- [ ] TLS terminated by the proxy; HTTP redirects; `X-Forwarded-Proto` set by the proxy.
- [ ] `/api/docs` returns 404; hardening headers present on `/api/health` (see the threat model).
- [ ] Egress from the API host blocked; model runtime reachable only on the private path.
- [ ] `python -m app.maintenance --dry-run` runs; production backup and restore rehearsed against off-host storage.
- [ ] `nginx -t` succeeds with the real hostname/certificate paths; HTTP redirect, HSTS, forwarding-header trust and edge rate limits verified.
- [ ] Interface hosting decided and the matching configuration applied: one host with Nginx, or a provider rewrite that keeps the browser same-origin (see "Where the built interface is hosted").
- [ ] Interface released with `deploy/stage-frontend.sh` (its bundle gate passed and `<target>.previous` exists for rollback).
- [ ] API installed from `deploy/systemd/talimgo-api.service.example`; the maintenance timer enabled and its first run inspected.
- [ ] Release procedure in §10 followed in order, and the owner-only checklist in §11 completed.
- [ ] No API base URL or API key is baked into the interface build; the interface was built from the current `frontend/` and served with the headers in `frontend/vercel.json` when hosted on Vercel.
- [ ] Interface loaded in a real browser: it renders, its requests succeed, and the console reports no CSP violations (CI cannot check browser enforcement).
- [ ] An API-generated 429 still arrives with its own message and `Retry-After` (not replaced by the edge page).
- [ ] Post-deployment verification passes against the real hostname: `python backend/scripts/verify_deployment.py --base-url https://<host> --host <host>`
- [ ] Pilot account created, export downloaded, deletion performed and verified on a throwaway account.
- [ ] Logs shipped, health check wired into the supervisor, resource limits applied.
