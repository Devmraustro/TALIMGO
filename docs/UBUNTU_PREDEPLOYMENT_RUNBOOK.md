# TALIMGO — Ubuntu Single-Host Pre-Deployment Runbook

This runbook is grounded in the existing repository sources:
- `docs/DEPLOYMENT.md`
- `deploy/nginx/talimgo.conf.example`
- `deploy/systemd/talimgo-api.service.example`
- `deploy/systemd/talimgo-maintenance.service.example`
- `deploy/systemd/talimgo-maintenance.timer.example`
- `deploy/health-check.sh`
- `deploy/stage-frontend.sh`
- `backend/scripts/check_production_config.py`
- `backend/scripts/verify_deployment.py`
- `backend/scripts/postgres_backup_restore.py`

No command in this document creates infrastructure, modifies production, or exposes secrets. All placeholders (with `<...>`) must be supplied by the owner on the target host.

---

## 1. Host requirements

| Item | Requirement |
|------|-------------|
| **OS** | Ubuntu 22.04 LTS or 24.04 LTS (matches CI `ubuntu-latest`). |
| **CPU** | ≥ 2 vCPU (API is small; 1 core is enough on stressed single-tenant deployments) |
| **RAM** | ≥ 2 GiB for API + database. Model weights need separate provisioning (see §10). |
| **Disk** | ≥ 20 GiB (OS, `apt-get`, weights, daily `pg_dump` snapshots). Model weights kept **off DB volume**. |
| **Ports** | 443 public, SSH owner-restricted, PostgreSQL loopback only. |
| **Resources** | `systemd` units set `MemoryMax=512M` for API. |
| **External dependencies** | Elected: domain name, TLS certificate (Let’s Encrypt or CA), DB backup target outside host. |

---

## 2. Base OS and service accounts

```bash
# root only
apt-get update
apt-get install -y git curl openssl ca-certificates ufw
adduser --system --group --home /srv/talimgo talimgo
mkdir -p /srv/talimgo /var/lib/talimgo /etc/talimgo
chown -R talimgo:talimgo /srv/talimgo /var/lib/talimgo /etc/talimgo
chmod 750 /etc/talimgo
```

Owner-only quick policy guard (optional but recommended, edge cases):  
`sudo ufw default deny incoming`, then `sudo ufw allow 22/tcp`, `sudo ufw allow 443/tcp`; finally `sudo ufw enable`.

---

## 3. Install runtime (Python 3.11+)

```bash
# root only
apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

---

## 4. PostgreSQL provisioning (Postgres 14+)

Install post remote repo (owner can add official apt repo first; these examples assume min 14).  
If possible, use `apt-get install -y postgresql` or `postgresql-16` or equivalent.

```bash
# root only
apt-get install -y postgresql
```

Create OS role + db in psql:

```bash
# executed as postgres user
sudo -u postgres psql <<'SQL'
CREATE USER talimgo_app WITH PASSWORD '<OWNER_PROVIDED_DB_PASSWORD>';
CREATE DATABASE talimgo OWNER talimgo_app ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';
REVOKE ALL ON DATABASE talimgo FROM PUBLIC;
GRANT CONNECT ON DATABASE talimgo TO talimgo_app;
\c talimgo
REVOKE ALL ON SCHEMA public FROM PUBLIC;
GRANT ALL ON SCHEMA public TO talimgo_app;
SQL
```

Ensure DB listen posture is localhost only (default). If production BYO volume uses UNIX socket.  
Reload/restart Postgres when all changes are done (`systemctl restart postgresql`).

---

## 5. Deploy (code) — host layout

Retrieve code (owner must provide a host-neutral checkout mechanism, e.g. `git clone` ssh, without disclosing credentials):

```bash
# root or talimgo user (ensure ownership)
cd /srv/talimgo
git clone --branch arena/c22f9408-talimgo --single-branch https://github.com/Devmraustro/TALIMGO.git current
chown -R talimgo:talimgo current
```

Owner-only inspect a particular commit (recommended for releases):

```bash
cd /srv/talimgo/current && git fetch origin && git checkout <SHA>
```

---

## 6. Python virtual environment

Find absolute path; adapt if repository is moved.

```bash
# as talimgo user
cd /srv/talimgo/current/backend
python3.11 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"
```

---

## 7. Environment file — secrets outside repository

Owner generates secrets on the host with maximum secrecy (never in repo, never chat):

```bash
# owner on the shell
openssl rand -base64 48 > /tmp/secret.raw
```

Create the environment file. Ownership `root:root`, permissions `0640`, directory `/etc/talimgo`.

```bash
# root only - example (edit all fields)
cat <<'EOF' > /etc/talimgo/talimgo.env
TALIMGO_ENV=production
TALIMGO_SESSION_SECRET=<OWNER_GENERATED_32_PLUS_BYTES>
TALIMGO_DATABASE_URL=postgresql+psycopg://talimgo_app:<OWNER_DB_PASSWORD>@127.0.0.1:5432/talimgo
TALIMGO_ALLOWED_ORIGINS=https://<HOSTNAME>
TALIMGO_AI_ENABLED=false
TALIMGO_AI_STRICT=true
TALIMGO_MAX_REQUEST_BYTES=131072
TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE=120
TALIMGO_REGISTRATIONS_PER_IP_PER_HOUR=10
EOF
chown root:talimgo /etc/talimgo/talimgo.env
chmod 640 /etc/talimgo/talimgo.env
```

The final file must preserve the exact mode properties. Never log secret values.

---

## 8. Production preflight (fail-closed)

Order matters (1: secrets/config, 2: database, 3: service). Before starting FastAPI:

```bash
cd /srv/talimgo/current/backend
TALIMGO_ENV_FILE=/etc/talimgo/talimgo.env \
.venv/bin/python scripts/check_production_config.py
```

**It passes only if:**
- `TALIMGO_ENV=production`
- session secret ≥ 32 chars, no placeholder marker
- database is `postgresql` scheme (not sqlite)
- at least one explicit origin, no wildcard
- AI unchecked or pointing at a local endpoint with a named model

---

## 9. Migrations + first check

```bash
cd /srv/talimgo/current/backend
TALIMGO_ENV_FILE=/etc/talimgo/talimgo.env .venv/bin/alembic upgrade head
TALIMGO_ENV_FILE=/etc/talimgo/talimgo.env .venv/bin/alembic check  # shows "No ... upgrade ops detected"
```

A second check after any migration takes a `pg_dump` (optional but strongly recommended).

---

## 10. Local AI (offline unless explicitly decided)

- Keep `TALIMGO_AI_ENABLED=false` until a local runtime is installed and the owner consents after evaluating a versioned dataset.  
  Local-only runtime is Ollama (dev) or vLLM-class (production), bound to loopback.  
  Never forward learner data remotely. Keep egress firewall blocks for public Internet from API host.

---

## 11. Nginx configuration (HTTPS termination)

The example edge config at `deploy/nginx/talimgo.conf.example` requires hostname and certificate replacement.  
Owner must run **before `nginx -t`**:

```bash
# root only
HOSTNAME=<CERT_HOST>
sudo mkdir -p "/etc/letsencrypt/live/${HOSTNAME}" /srv/talimgo/frontend/dist /var/www/certbot
sudo chown -R talimgo:talimgo /srv/talimgo /var/www/certbot
```

Obtain TLS (for example Let’s Encrypt) per the CA's website or an owner-issued workflow. Once the certificate files exist, secret paths may be modified to match `/etc/letsencrypt/live/${HOSTNAME}/`.

Configure `deploy/nginx/talimgo.conf.example`: replace `talimgo.example` with `<HOSTNAME>` in server_name, root, fullchain, privkey. Then:

```bash
# root only
sudo nginx -t -c /srv/talimgo/current/deploy/nginx/talimgo.conf.example
```

Copy as `/etc/nginx/sites-available/talimgo.conf` (Owner's decision). Then `sudo nginx -t && sudo systemctl reload nginx`.

Also note the reminder text embedded in the example: update `add_header` blocks; keep a HSTS repetition in `location /` because `add_header` resets inheritance.

No nginx reload occurs before a successful `nginx -t`.

---

## 12. Frontend build and stage

To produce the final artifact, run either internally or out-of-band:

Preferred (on the host or in controlled build context):

```bash
# as talimgo or build user
cd /srv/talimgo/current/deploy
chmod +x stage-frontend.sh health-check.sh
./stage-frontend.sh --target /srv/talimgo/frontend/dist
```

`stage-frontend.sh` runs `npm ci` + `npm run build` then runs `frontend/scripts/check-bundle.mjs`, then atomically swaps. It keeps the previous release at `<target>.previous` automatically. Keep the previous release for a rollback within minutes.

Health check before serving content:

```bash
/srv/talimgo/current/deploy/health-check.sh --url http://127.0.0.1:8000 --wait 30
```

Exit 0 = healthy, 1 = API unhealthy or a static-file fake, 2 = CLI misuse.

---

## 13. systemd service installation

Copy provided example units from `deploy/systemd/` (not from external sources). Edit absolute paths, user/group as they differ, then validate unit syntax.

```bash
# root only - owned by docs/DEPLOYMENT.md prepare
install -o root -g root -m 0644 /srv/talimgo/current/deploy/systemd/talimgo-api.service.example /etc/systemd/system/talimgo-api.service
install -o root -g root -m 0644 /srv/talimgo/current/deploy/systemd/talimgo-maintenance.service.example /etc/systemd/system/talimgo-maintenance.service
install -o root -g root -m 0644 /srv/talimgo/current/deploy/systemd/talimgo-maintenance.timer.example /etc/systemd/system/talimgo-maintenance.timer
sed -i 's#/srv/talimgo/current#/srv/talimgo/current#g' /etc/systemd/system/talimgo-api.service /etc/systemd/system/talimgo-maintenance.service
# (review lines marked with example-specific paths if directories diverge)
systemctl daemon-reload
systemctl enable --now talimgo-api.service
systemctl enable --now talimgo-maintenance.timer
```

The unit enforces:
- `ExecStartPre`: preflight command (archives weak secrets, SQLite DBs).
- `ExecStart`: `uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 1` (no public bind).
- `ExecStartPost`: readiness probe via `health-check.sh`.
- no restart loop with max 3 attempts; `Restart=on-failure`.

Least-privilege<rfl:parameter name="ements: the unit hardening set limits memory 512 MiB, systemd `ProtectSystem=strict`, `PrivateTmp`, `NoNewPrivileges`, 14 `aud-to` files.

---

## 14. Start and live health check

```bash
sudo systemctl restart talimgo-api.service
sudo /srv/talimgo/current/deploy/health-check.sh --url http://127.0.0.1:8000 --wait 30 --ai
```

`--ai` only if tutoring will be on (it must return 0 **and** 0 errors in logs).

---

## 15. Post-deployment live verification

Use the project's disposable test pattern **only against an isolated HTTPS domain**:

```bash
/srv/talimgo/current/backend/.venv/bin/python \
  /srv/talimgo/current/backend/scripts/verify_deployment.py \
  --base-url https://<HOSTNAME> --host <HOSTNAME>
```

The script:
- refuses plain HTTP and host/base mismatch;
- verifies `/api/health` still has required headers (never checks production secrets);
- registers a disposable account with unpredictable password per run;
- reads and writes a test goal;
- issues a login, confirms session persistence, deletes the user;
- proves that the deleted session is refused.

Data removal: each run tries to delete the account automatically; the email is only printed if cleanup fails (then the target DB must be inspected manually).

Allowed hosts: only instances you control. Never run against public systems.

---

## 16. Backup and rollback

From `docs/DEPLOYMENT.md` §10 and §9.  
Backup:

```bash
pg_dump --format=custom --no-owner --no-acl --file ~/talimgo-pre-release.dump "$PGDATABASE"
# recommended one-off before every release
```

Before migrations that modify the schema.

Restore (disaster only):

```bash
# owner-only, new blank database
pg_restore -d talimgo_restore -v ~/talimgo-pre-release.dump
```

The rehearsal tool `backend/scripts/postgres_backup_restore.py` is strictly guards:
- source DB must be `talimgo` on `127.0.0.1` or localhost
- URL must be `postgresql+psycopg`
- credentials must be present, non-empty, valid
- scratch db `talimgo_restore` automatically dropped, unless drop fails → non-zero exit
- writes temp dumps into a temp directory cleaned even on failure
- compares public table set, table row counts, and the alembic revision before vs restored

Rollback (app):
```bash
sudo mv /srv/talimgo/frontend/dist /srv/talimgo/frontend/dist.failed
sudo mv /srv/talimgo/frontend/dist.previous /srv/talimgo/frontend/dist
sudo systemctl restart talimgo-api.service
```

Rollback (db):  
`alembic downgrade -1`, but note that when migrations drop columns that removal **loses** the column values. Prefer "roll forward with a fix" over rolling the database–healed only when accompanied by a verified fresh `pg_dump`.

Rollback (model): pin model tag/version; revert tag only and no app restart required (only required configuration change).

Audit events (retention) and `start_on` backfill migration notes in §3.

---

## 17. Global security boundaries (explicit)
- **AI: disabled** until owner-provisioned runtime is explicitly authorized.
- `TALIMGO_ALLOWED_ORIGINS` defaults to empty, requires literal names.
- write rate limit: 120 / UTC minute / user.
- model concurrency: 1/worker, 2 s queue timeout → 503.
- request body cap (Nginx + app) default 128 KiB, hard max 8 MiB. 256 KiB edge.
- Interactive docs (`/api/docs`, `/api/openapi.json`): automatically 404 when `TALIMGO_ENV=production`; tests assert it.
- `TALIMGO_SEED_ON_STARTUP=false`.
- learners only allow 128 KiB body unless high (8 MiB theoretical).
- no learner content in logs.
- error handling uses controlled error shape (`{"detail": "..."}`).
- edge ensures spoofed forwarding headers do **not** reach the API.

---

## 18. Owner actions summary (do not mark done until performed)
1. Authorize the production host + firewall (SSH limited owner).  
2. DNS/TLS for production hostname (check `curl -I -k https://<PUT_HOST>` returns 200 with valid chain).  
3. Create service user dirs.  
4. Generate secrets on host: `.env` file `0640`, no values in repo.  
5. PostgreSQL role + backup schedule + retention policy.  
6. Install systemd units, timer, activate maintenance.  
7. Release: use `deploy/stage-frontend.sh`; keep `previous` for rollback.  
8. Decide Vercel fate: preview or delete; keep it non-functional until an API is reachable from it.  
9. Monitoring (`health-check.sh`), alert verification via deliberate stop.  
10. Run migration rehearsals in target PG version.  
11. Final `verify_deployment.py` against **verified** hostname; dispose the test account and verify cleanup.  
12. Allow local model runtime after evaluation.

---

## 19. Post-install verification matrix (exact values)

- `python scripts/check_production_config.py` (post secrets, postgres); **exit 0** before *before* any `systemctl restart talimgo-api`.
- `alembic upgrade head`, `alembic check`, fresh plan weekly `subjects`.
- Nginx `sudo nginx -t` and `deploy/health-check.sh` on 127.0.0.1:8000.
- `verify_deployment.py ...` on real hostname.
- `deploy/stage-frontend.sh` output prints "done" and keeps `<target>.previous`.
- Capture actual exit codes, don't claim success from command text alone.
- CI is still **green** for all seven jobs; actual infra health is not audited beyond that.

*Status: **DOCUMENTED ONLY.** No runbook command was executed because there is no authorized host provided. Once owner obtains access, operate as above with no ad-hoc secrets.*