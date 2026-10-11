# Deploying TALIMGO

This guide describes what a real deployment needs. It is written against the code in this repository
and is deliberately explicit about which parts have been exercised here and which have **not**: the
schema and tests have only ever run on SQLite in this development environment, no PostgreSQL instance,
reverse proxy, container runtime or TLS certificate has been used while writing it.

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
* **Not verified here:** no PostgreSQL server has been run in this environment. Before the first real
  deployment, run the full test suite and the migration chain against PostgreSQL, and confirm the
  batch-alter migration that sets `plans.starts_on NOT NULL` behaves on a populated table.
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

The application sends `Strict-Transport-Security` **only** when the request arrives over HTTPS, which
means the proxy must set `X-Forwarded-Proto: https` (a header the app only reads to *add* HSTS).

```nginx
server {
    listen 443 ssl http2;
    server_name talimgo.example;
    ssl_certificate     /etc/letsencrypt/live/talimgo.example/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/talimgo.example/privkey.pem;
    client_max_body_size 256k;          # the API refuses larger bodies anyway (TALIMGO_MAX_REQUEST_BYTES)

    # Redirect all plain HTTP to HTTPS; never serve credentials over http.
    location / { return 301 https://$host$request_uri; }
}
server {
    listen 80;
    server_name talimgo.example;
    location /.well-known/acme-challenge/ { root /var/www/certbot; }
    location / { return 301 https://$host$request_uri; }
}
```

Proxy rules that the application assumes but does not enforce itself:

* set `X-Forwarded-Proto`, `X-Forwarded-For` (or `Forwarded`) and **do not** pass client-supplied
  values through (`proxy_set_header` overwrites them);
* strip or replace `Server`/`X-Powered-By` at the edge if that is your policy;
* rate-limit at the edge as well as in the app: `limit_req` for `/api/auth/*` and an appropriate
  broader API policy. The in-app write cap only applies after authentication and is per learner; it
  does not replace IP/edge limits or protect public registration/login routes;
* cap request body size (the app rejects oversized bodies on the declared `Content-Length`, which a
  proxy is expected to have already bounded);
* keep the `Set-Cookie` flags intact: sessions are `HttpOnly`, `SameSite=Lax`, `Path=/`, and `Secure`
  in production.

The interface is a static build (`frontend/dist`) served by the proxy from a separate path or host.
It calls the API same-origin (`/api/...`), so serve it behind the same origin or add the interface
origin to `TALIMGO_ALLOWED_ORIGINS`.

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
  customised it (weights are re-downloadable; learner data is not). Test a restore into a scratch
  database before you need it, and verify the app starts and serves `/api/health` against the restored
  copy.
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
- [ ] `python -m app.maintenance --dry-run` runs; backup and restore rehearsed.
- [ ] Pilot account created, export downloaded, deletion performed and verified on a throwaway account.
- [ ] Logs shipped, health check wired into the supervisor, resource limits applied.
