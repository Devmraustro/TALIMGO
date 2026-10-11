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

## 5. Secrets

* `TALIMGO_SESSION_SECRET` — 32+ random bytes, generated on the server (`openssl rand -base64 48`),
  never committed, never reused between environments. Rotating it invalidates every session.
* Database credentials live in the service environment (systemd `EnvironmentFile=`, Docker secret, or
  your platform's secret store), not in the repository and not in the same file as application code.
* Model runtime credentials (if the local server uses an API key) stay on the model host; the API
  process needs only the endpoint URL.
* `.gitignore` already excludes `.env`, `*.db`, `data/`, `secrets/`, `model_cache/` and weight files.

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

The `browser-smoke` CI job installs pinned Playwright/Chromium and exercises the real FastAPI backend
through the Vite same-origin proxy in a disposable SQLite environment. It creates an account, sets a
goal, submits a real diagnostic answer, switches the interface to Arabic and verifies `lang=ar` and
`dir=rtl`, checks that a 390-pixel viewport has no horizontal overflow, deletes the account, verifies
the session is rejected, and fails on uncaught page errors, API 5xx responses, or requests to another
host/port. Failure screenshots and server logs are retained as a short-lived CI artifact.

This is an automated journey smoke test, **not** a full accessibility audit or a test of the production
Nginx CSP: it uses Vite's development server and a disposable database. A real deployment still needs a
browser pass against the actual HTTPS host, especially to confirm that the production CSP allows the
built app while blocking disallowed sources.

What CI does **not** cover, and what remains manual: screen-reader behaviour, contrast, 200–400% zoom
and reflow, complete focus order, the local model's answers, backup/restore durability outside the host,
and DNS/certificate issuance or renewal beyond trusting the certificate the runner sees.

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

A systemd unit sketch:

```ini
[Service]
EnvironmentFile=/etc/talimgo/talimgo.env
WorkingDirectory=/srv/talimgo/backend
ExecStartPre=/srv/talimgo/backend/.venv/bin/alembic upgrade head
ExecStart=/srv/talimgo/backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
MemoryMax=512M
Restart=on-failure
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/var/lib/talimgo
```

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

## 10. Rollback

1. Application: keep the previous release directory (or image tag) and switch the symlink; the API is
   stateless apart from the database and the model runtime.
2. Database: migrations are additive so far, and `alembic downgrade -1` exists for every revision, but
   a downgrade that drops a column loses that column's data. Take a `pg_dump` **before** every deploy
   that includes a migration, and prefer rolling forward with a fix over rolling back.
3. Model runtime: pin the model and its version; if a model change degrades tutoring, revert the model
   tag — the application has no dependency on a specific model beyond the configured name.
4. After any rollback: re-run `GET /api/health`, one authenticated dashboard read, one practice answer
   and the migration drift check (`alembic check`).

## 11. First-deployment checklist

- [ ] PostgreSQL running; `alembic upgrade head` applied; `alembic check` clean.
- [ ] `TALIMGO_ENV=production`, strong `TALIMGO_SESSION_SECRET`, exact `TALIMGO_ALLOWED_ORIGINS`.
- [ ] TLS terminated by the proxy; HTTP redirects; `X-Forwarded-Proto` set by the proxy.
- [ ] `/api/docs` returns 404; hardening headers present on `/api/health` (see the threat model).
- [ ] Egress from the API host blocked; model runtime reachable only on the private path.
- [ ] `python -m app.maintenance --dry-run` runs; production backup and restore rehearsed against off-host storage.
- [ ] `nginx -t` succeeds with the real hostname/certificate paths; HTTP redirect, HSTS, forwarding-header trust and edge rate limits verified.
- [ ] Interface loaded in a real browser: it renders, its requests succeed, and the console reports no CSP violations (CI cannot check browser enforcement).
- [ ] An API-generated 429 still arrives with its own message and `Retry-After` (not replaced by the edge page).
- [ ] Post-deployment verification passes against the real hostname: `python backend/scripts/verify_deployment.py --base-url https://<host> --host <host>`
- [ ] Pilot account created, export downloaded, deletion performed and verified on a throwaway account.
- [ ] Logs shipped, health check wired into the supervisor, resource limits applied.
