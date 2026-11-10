# D.12 — Ownership and isolation: TALIMGO is fully independent from AUSTRO (2026-11-10)

**Decision owner:** the TALIMGO project owner, explicitly recorded in the Phase D.12 brief
(2026-11-10):

> "The owner has explicitly approved complete infrastructure and operational isolation between
> TALIMGO and AUSTRO. This is a binding architectural decision."

This document is the canonical record of that binding decision and the resource boundary it
imposes. It is referenced by `docs/D12_ALWAYSDATA_ACCOUNT_VERIFICATION.md`,
`docs/D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md` and `docs/D12_FINAL_REPORT.md`.
Every D.12+ phase must comply; changing the boundary requires a new explicit owner decision, in
writing, first.

## 1. Mandatory separation statement

TALIMGO must be completely independent from AUSTRO. The components below must never be shared.
No AUSTRO infrastructure may be modified, repurposed, interrogated from this repository, or used as
a TALIMGO dependency — including "temporarily", "for the preview", or "until the real thing is
ready". If any TALIMGO task appears to require one of these, the task stops and the owner is asked
for a TALIMGO-dedicated alternative.

## 2. Resource ownership matrix

Legend: **TALIMGO-only** = owned/controlled by the TALIMGO project owner, used only by TALIMGO ·
**AUSTRO** = belongs to the AUSTRO project · **FORBIDDEN** = sharing is prohibited.

| # | Resource class | TALIMGO (required state) | AUSTRO (forbidden source) | Shared? |
|---|---|---|---|---|
| 1 | Hosting account / application runtime (AlwaysData site, VPS, container, serverless project) | TALIMGO-dedicated account or proven-dedicated TALIMGO scope; owner-controlled | Any AUSTRO account/scope; any site serving AUSTRO content | **FORBIDDEN** |
| 2 | Database instances | TALIMGO-dedicated PostgreSQL (own database `talimgo`; own server account on AlwaysData) | AUSTRO databases/servers/instances, any `austro_*` resources (already documented) | **FORBIDDEN** |
| 3 | Database roles/logins | `talimgo_staging_app` (staging) · a production login **separate** from any migration identity; never `talimgo_runtime` (compromised, rotation deferred) | AUSTRO logins, shared personal logins | **FORBIDDEN** |
| 4 | Runtime credentials & secrets | Generated per TALIMGO environment (`TALIMGO_SESSION_SECRET`, DB URL); stored owner-side only | Any AUSTRO env file, `.env`, secret store entry, CI secret | **FORBIDDEN** |
| 5 | Session stores & auth state | TALIMGO session cookies/tokens signed by TALIMGO secrets; no shared session store | AUSTRO session data, signing keys, cookie domains | **FORBIDDEN** |
| 6 | User data (learners) | PostgreSQL `talimgo(_staging)` only; synthetic data in staging | AUSTRO user data, or vice versa | **FORBIDDEN** |
| 7 | Uploaded files / storage | None today (JSON-only API). If ever implemented: TALIMGO-dedicated storage path | AUSTRO buckets/directories | **FORBIDDEN** |
| 8 | Background workers & scheduled tasks | `python -m app.maintenance` as a TALIMGO scheduled task in the TALIMGO scope | AUSTRO cron/services | **FORBIDDEN** |
| 9 | Logs (app/proxy/access) | TALIMGO `…/admin/logs/…` under the TALIMGO scope; retention per TALIMGO policy | AUSTRO log files/pipelines | **FORBIDDEN** |
| 10 | AI inference & model data | Local-only inference on TALIMGO-controlled resources; no hosted LLM API; AI disabled until provisioned (D.11 §7) | AUSTRO model runtimes, gateways, API keys | **FORBIDDEN** |
| 11 | Production vs staging environments | Separate databases, logins, env files, domains (or clearly separated SSH-only paths) inside the TALIMGO scope | Cross-use of production for experiments | **FORBIDDEN** |
| 12 | Backup destinations & recovery credentials | TALIMGO backup destination (owner-decided off-host storage + plan-native backups); recovery credentials owner-held | AUSTRO backup stores, shared recovery keys | **FORBIDDEN** |
| 13 | DNS/domains | A TALIMGO-controlled domain/subdomain (owner-owned) for any public site | AUSTRO domains/subdomains | **FORBIDDEN** |
| 14 | CI/CD systems | This repository's GitHub Actions (public repo, owner Devmraustro) — no AUSTRO credentials in it; Vercel projects `talimgo-api`/`talimgo-preview` remain TALIMGO's, untouched by D.12 | AUSTRO pipelines/secrets | **FORBIDDEN** |
| 15 | Code & content | TALIMGO repository (`Devmraustro/TALIMGO`), authored curriculum, ADRs | AUSTRO source code, or copying TALIMGO into AUSTRO products without licence decision | **FORBIDDEN** (absent explicit owner decision; none assumed) |

## 3. Explicit prohibited cross-project dependencies

1. Using any AUSTRO account, database, role, host, port, bucket, directory, secret, env file,
   pipeline, domain, log or credential — directly or as a "temporary" step.
2. Importing, building on, or proxying through AUSTRO infrastructure (e.g., serving TALIMGO's API
   behind an AUSTRO reverse proxy, or hosting TALIMGO's model behind an AUSTRO inference service).
3. Copying secrets, connection strings, dumps or learner data from one project to the other in
   either direction.
4. Sharing session state, SSO deployments, cookies or auth domains between TALIMGO and AUSTRO
   surfaces.
5. Reusing the historically compromised `talimgo_runtime` credential anywhere — production,
   staging, local rehearsal, or tooling. Rotation remains **DEFERRED BY OWNER**; D.12 does not
   authorise it, and this document does not touch it.
6. Pointing TALIMGO CI at AUSTRO-controlled resources (it does not; D.12 preserves that).
7. Treating "same owner operates both projects" as isolation — isolation is per-resource, not
   per-person.
8. Merging TALIMGO into an AUSTRO deployment to satisfy a hosting requirement — the correct answer
   is a TALIMGO-dedicated scope, not consolidation.

## 4. Proof obligations

| Claim | Where proven / case |
|---|---|
| No TALIMGO code, config or CI references AUSTRO infrastructure | This repository: D.8 sweep found no AUSTRO hostnames or credentials; D.11/D.12 re-verified (`grep -ri austro` returns only historical documentation references; no hostnames, no credentials — see D12_FINAL_REPORT §11) |
| No AUSTRO resource is used as a TALIMGO dependency | None exists in the tree; nothing referenced at runtime (all endpoints local/loopback or owner-configured) |
| TALIMGO-dedicated hosting scope | **UNKNOWN / NOT VERIFIED** — AlwaysData account not accessible in D.12; see D12_ALWAYSDATA_ACCOUNT_VERIFICATION.md. The binding gate before any provisioning |
| TALIMGO-dedicated database scope | **NOT EXECUTED** — staging database not provisioned (authorization boundary unmet); see D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md |
| Backups independent | **NOT EXECUTED** — backup destination undecided by owner; plan in D12_STAGING_BACKUP_RESTORE_VERIFICATION.md |

## 5. Enforcement rules for all future phases

- Any environment variable, URL, host or account name introduced in TALIMGO must resolve to the
  TALIMGO scope listed in the matrix above; reviewers reject otherwise.
- Any plan to touch AUSTRO for "convenience" requires an explicit owner decision overriding this
  document — documented, not implied.
- "Same password used in both projects" is a finding, not a convenience; secrets are per-project.
- Verification commands must show scope (which account/host/database) — a passing test against the
  wrong scope is a failure, not a pass.

## 6. Current compliance position (2026-11-10)

| Area | Position |
|---|---|
| Codebase / CI / Vercel (TALIMGO projects) | No AUSTRO dependency found; Vercel settings unchanged and out of scope |
| AlwaysData | **UNAUTHENTICATED — not verified**; no TALIMGO scope proven; nothing provisioned |
| PostgreSQL | No database connected in D.12 except disposable local validation (see final report); production NEVER connected from this workstation |
| AI | Disabled by configuration; no runtime anywhere |
| Docs | This document + D12 series record the binding decision and its unmet proof obligations |

**Compliance verdict for D.12: the isolation *policy* is now explicit and binding; the isolation
*infrastructure* is UNVERIFIED/NOT EXECUTED until the owner provisions and authorises the
TALIMGO-dedicated AlwaysData scope.**
