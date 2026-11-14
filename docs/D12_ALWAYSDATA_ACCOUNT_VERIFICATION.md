# D.12 — AlwaysData account verification (2026-11-10)

**Method rule (binding for this document):** account capabilities must be verified against the
**actual account** — never inferred from public documentation alone. This environment has **no
AlwaysData credentials, no AlwaysData connector, no SSH key or config for AlwaysData hosts**
(verified by name-only scans: `env` excerpt lists only `E2B_*` and `GH_TOKEN` beyond standard
sandbox vars; `~/.ssh` and `~/.config` do not exist). The one connected app (Vercel) holds no
AlwaysData data and is out of scope for changes. **No AlwaysData account was accessed, probed or
modified in D.12. No resource was created, purchased or upgraded.**

Status labels: **VERIFIED** (evidenced) · **PARTIALLY VERIFIED** · **BLOCKED** (needs owner
access/authorisation) · **UNKNOWN** (cannot be determined from here) · **NOT EXECUTED**.

## 1. Item-by-item verification

| # | Item | Status | Evidence / note |
|---|---|---|---|
| 1 | Account identity and ownership (TALIMGO) | **BLOCKED** | No credentials/account name in environment; no access granted |
| 2 | Account dedicated exclusively to TALIMGO (not shared with AUSTRO/other) | **BLOCKED** | Cannot inspect; the documented runbook risk ("possibly AUSTRO-adjacent account") can only be closed by the owner in the admin panel |
| 3 | Active plan and billing status | **UNKNOWN** | Not inspectable; plan determines Services availability, backups retention, quotas (docs: Free … X-Large) |
| 4 | Python 3.11 availability | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs list 3.11 among supported versions; actual account default/`Environment > Python` must be checked on the account. Local validation of the app on Python 3.11.x ✓ |
| 5 | ASGI User Program support | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs: User program site type runs arbitrary servers incl. uvicorn on `$IP:$PORT` (IPv6); no account test possible |
| 6 | PostgreSQL availability and version | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs: PG 16/17/18; host `postgresql-[account].alwaysdata.net`; actual version/instance per account unknown. Local disposable **PostgreSQL 16.2** used for D.12 validation (same major as CI) |
| 7 | Database connection limits | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs: max 50 simultaneous connections per user on Public Cloud (Private Cloud on request). App peak ≈ 15 (1 worker × pool 5 + overflow 10) — compatible if limit applies to this account |
| 8 | Storage quotas | **UNKNOWN** | Plan-dependent (1 GB Free → 500 GB X-Large; disk quota includes files+databases); account value unknown |
| 9 | Scheduled task availability | **VERIFIED (documentation)** | Docs: Advanced > Scheduled tasks (crontab; skip-if-overlapping; non-zero-exit mail; logs `…/admin/logs/jobs/`); not yet created for TALIMGO (would be a change → needs owner authorisation) |
| 10 | SSH access and deployment permissions | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs: SSH all plans, port 22, `ssh-[account].alwaysdata.net`, no root; actual SSH user/keys unknown here |
| 11 | HTTPS and domain support | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs: automatic Let's Encrypt per site address; TALIMGO domain/subdomain not selected or owned yet (owner decision) |
| 12 | Runtime memory/CPU/disk/process limits | **UNKNOWN** | Plan-dependent; e.g. Free 256 MB/¼ CPU vs Small 1 GB/1 CPU; "processes using too much CPU/RAM/IO are killed"; account limits unknown |
| 13 | Application logs and restart behavior | **VERIFIED (documentation)** / **UNVERIFIED (account)** | Docs: `…/admin/logs/{http,sites,jobs}/`; sites auto-restart per AlwaysData service management; actual log retention for the account unknown |
| 14 | Database backups (provider-managed) | **VERIFIED (documentation)** | Daily backups; off-site (different datacenter/provider); read-only; rolling 3–30 d by plan; `pg_dump`-based; restore via admin or `zstdcat \| psql` |

## 2. What this means concretely

Every runtime-affecting capability is at best **documentation-verified**. **Zero items are
account-verified**, because no credentials exist in this environment. This is not a technology
assumption problem — it is an access/authorization fact, recorded as such. The correct, binding
requirement (from the D.12 brief and consistent with the isolation decision) is:

**Requirement R-1 — dedicated TALIMGO-only AlwaysData scope, proven by the owner, before ANY
provisioning:**

1. The owner identifies (or creates) an AlwaysData account **exclusively for TALIMGO** — not the
   AUSTRO-adjacent candidate account, not a shared personal account.
2. Proof to record in the admin panel (and attach to the release ticket): account name;
   plan & price; owner of record; dedicated login created **only** for TALIMGO; a
   TALIMGO-only PostgreSQL database + login; the TALIMGO domain/subdomain in **Web > Sites** with
   its automatically issued certificate; the SSH user(s) authorized for deployment.
3. Explicit written authorization to: create `talimgo_staging` + `talimgo_staging_app` (staging
   database and login); run the SQL provisioning script; apply migrations; load synthetic
   curriculum; perform the backup/restore rehearsal into a disposable scratch database; and
   afterwards drop that scratch database.
4. Decision (owner): plan ≥ **Small** (256 MB Free is not viable; no Services there anyway).
   No purchase or upgrade is to be performed by this agent — see §4.

## 3. If the account proves shared (with AUSTRO or anyone)

Per the binding isolation decision (`docs/D12_OWNERSHIP_AND_ISOLATION.md`): **no TALIMGO resource
may be created there.** The owner must instead provision a separate TALIMGO-only account (or a
contractually dedicated Private Cloud scope) and re-run this verification against it.

## 4. Explicitly NOT done (out of scope / unauthorized)

- No account access attempts, no credential requests, no plan purchases or upgrades,
  no site/database/DNS/TLS changes, no scheduled task creation, no SSO/protection changes,
  no production or staging object created on AlwaysData.
- This document's existence does **not** satisfy G4/G5/G8/G12–G14 of
  `docs/D11_SECURITY_AND_RELEASE_GATES.md` (or their D.12 successors) — those need a live,
  authorized staging environment.

## 5. Checklist the owner can use on the account (to flip items to VERIFIED)

- [ ] Administration panel screenshot/export: account name, plan, billing status, renewal date.
- [ ] **Environment > Python**: 3.11 selected; `python --version` over SSH prints 3.11.x.
- [ ] **Databases > PostgreSQL**: version (expect 16/17/18); host string; database list showing a
      TALIMGO-only empty database (to become `talimgo_staging`) and no AUSTRO databases;
      logins: a dedicated TALIMGO staging login, no shared logins.
- [ ] **Databases**: connection limit (50 on Public Cloud); disk usage of the account.
- [ ] **Web > Sites**: target domain(s) added; certificate issued for them (automatic).
- [ ] **Advanced > Scheduled tasks**: empty or TALIMGO-only; none yet created for TALIMGO.
- [ ] **Advanced > Services**: none yet; none required while AI is disabled.
- [ ] SSH fingerprint confirmed with the owner; password/keys only in owner custody.
- [ ] Backup section: confirm daily backups active for the account and retention (plan-dependent).
