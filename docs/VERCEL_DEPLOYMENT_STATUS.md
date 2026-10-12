# Vercel deployment — verified state and owner actions

Status date: **2026-10-11** (re-checked at the end of the release-preparation round). This file records
what was actually observed about the Vercel deployment from outside, what it can and cannot do, and the
exact owner actions that remain. It is a snapshot: re-verify before relying on it.

**Nothing on the Vercel side was changed in either round.** No project setting, deployment, alias,
domain or environment variable was touched through any API or dashboard: the observations below come
from fetching the public URLs, and no Vercel credential was used because none is available to this
session. The re-check confirmed the same state as before — the alias serves the interface shell, the
bundle it serves still shows `Request failed (404).` for its boot call (so it predates the messaging fix
in this branch), and `/api/health` on that host is still Vercel's 404 page.

## What exists

| Item | Value |
| --- | --- |
| Vercel project | `talimgo-preview` (ID `prj_RX2NmJBTcZTkygGNgZKcbhqBk7aA`, as recorded in the owner's snapshot) |
| Deployment | `dpl_6ozG5iAjTRRekGW68JQPsvJyTp5d` (as recorded in the owner's snapshot) |
| Public alias | `https://talimgo-preview.vercel.app` |
| Immutable deployment URL | `https://talimgo-preview-ft71txd8s-devmraustros-projects.vercel.app` |
| Source | `Devmraustro/TALIMGO`, branch `arena/c22f9408-talimgo`, commit `fa421ab` |
| Framework / root | Vite, root directory `frontend`, build `npm run build`, install `npm ci`, output `dist` |

The frontend source has not changed since `fa421ab` (verified with `git diff fa421ab..HEAD -- frontend/src`
= empty), so the deployed bundle corresponds to the current interface code.

## What was verified, and how

No Vercel API access exists in this session (the Vercel connector is not available here, and the
sandbox cannot open a TCP connection to `vercel.app`), so every observation below comes from fetching
the public URLs over the internet. Response *headers* could not be read this way; that limitation is
recorded rather than guessed at.

| Observation | Result |
| --- | --- |
| Public alias, `/` | **200**, interface shell renders ("TALIMGO — learn with a plan"), sign-up form visible |
| Public alias, in-app behaviour | The interface's own error banner reads **"Request failed (404)."** — its boot call `GET /api/auth/me` was answered by the static host, not by an API |
| Public alias, `/api/health` | **404** (Vercel's `404: NOT_FOUND` page) — **no API is deployed behind this host** |
| Public alias, `/today` | **404** (Vercel's page). Not a defect: the interface has no URL routes (views switch in memory), so it never requests this path. No rewrite is required |
| Deployment protection | The **immutable** deployment URL redirects to `vercel.com/login?sso-api…` ("Protected Deployment – Vercel"), while the **public alias** is reachable without authentication. Deployment protection therefore covers the per-deployment host, not the alias |
| Response headers of the alias | **Not verifiable** from this session (see above). `frontend/vercel.json` was added to supply the interface policy on the next deployment |
| Release tooling for the interface | **Available in this branch** (`deploy/stage-frontend.sh`, `frontend/scripts/check-bundle.mjs`): a release must pass a gate that refuses a bundle with an insecure or local/private back-end address. The Vercel deployment predates it |

## What this means

* The Vercel deployment is a **frontend shell with no API**. It is reachable, but no account can be
  created, no plan can be produced, and no learner data can be stored there. It is not a working
  TALIMGO.
* Vercel cannot host the TALIMGO backend as-is: the API needs a long-lived process (startup checks,
  migrations, the in-process generation gate), a persistent PostgreSQL database, and — for tutoring —
  a **local** model runtime on TALIMGO-controlled infrastructure. Hosted AI providers are excluded by
  product rule, and no hosted provider may be introduced to make the deployment "work".
* Pushing to the branch may or may not build a new Vercel deployment; that could not be confirmed
  without Vercel access. It is an owner check (see below).

## Owner actions, shortest path first

1. **Grant inspection access** (or read it in the dashboard): confirm Git integration, whether pushes
   to `arena/c22f9408-talimgo` build, and the deployment-protection setting. Nothing in the repository
   can substitute for this.
2. **Choose the topology** (see `docs/DEPLOYMENT.md`, "Where the built interface is hosted"):
   * single host: FastAPI + PostgreSQL + Nginx serving the built interface on the same origin — the
     supported, tested path, and the only one that needs no Vercel involvement;
   * Vercel for the interface with a Vercel rewrite of `/api/*` to the API host — keeps the browser
     same-origin, so cookies and CORS are unchanged; needs the API host and one `vercel.json` entry.
3. **Provision the backend** (Python host + PostgreSQL + secrets named in `docs/DEPLOYMENT.md`). Until
   this exists, the Vercel deployment cannot work regardless of configuration.
4. **Deploy and re-verify**: run `backend/scripts/verify_deployment.py` against whichever URL serves
   the product, and record the result. The existing Vercel deployment will keep showing
   "TALIMGO's API did not answer this request" until an API is reachable from the page's origin.
5. **Decide about the current deployment**: keep it as a preview of the interface, or delete it. It
   must not be presented as a working product.

## Deployment report (labels follow `AGENTS.md` §3)

| Area | State | Evidence |
| --- | --- | --- |
| Vercel project/build | **UNVERIFIED here** — project, deployment ID and build settings come from the owner's snapshot; this session has no Vercel access to confirm the build log, commit, or protection settings | The connector is unavailable in this session and the sandbox has no TCP egress to `vercel.app` |
| Deployed interface (frontend) | **CONFIRMED reachable, but non-functional as a product** — alias returns the interface shell over HTTPS; no API behind it | Public fetches: `/` renders; `/api/health` → 404; in-app banner "Request failed (404)." |
| Backend/API | **CONFIRMED not deployed** on that host; **UNVERIFIED** anywhere else (no authorised target exists) | `/api/health` → 404 on the alias |
| PostgreSQL/migrations | **CONFIRMED not deployed** for that host; migrations are **TESTED** in CI and locally against PostgreSQL 16.2 (upgrade to head, drift check, legacy-plan rehearsal, dump/restore with row-count and revision comparison) | `postgres-integration` CI job; local rehearsals in this session |
| Local AI runtime | **NOT PROVISIONED** — no runtime anywhere; the optional model test skips with a stated reason. No hosted AI is used or added | CI `local-only-ai` gate passes; `TALIMGO_AI_ENABLED=false` documented for production |
| Security posture | **CONFIRMED for the application and the Nginx example** (headers, docs 404 in production, edge rate limits, forwarding-header trust, cookie flags) — **UNVERIFIED for the live Vercel host** (response headers were not readable from here) | CI `proxy-tls-smoke`, `backend` job; local edge run against the real API |
| Accessibility | **TESTED in CI** — Chromium journey plus axe WCAG A/AA scans on representative screens; **NOT a conformance claim** and not a substitute for manual screen-reader, contrast and zoom/reflow checks | `browser-smoke` CI job |
| Secrets | **CONFIRMED** — no production values exist in the repository; the production preflight prints names and verdicts only | `backend/scripts/check_production_config.py`; tests assert no value is echoed |

## What this file does not claim

* No production readiness, no completed staging, no working backend, no database, no model runtime.
* No header, TLS or routing guarantee for the live Vercel host: those were not measurable from here,
  and `frontend/vercel.json` only takes effect on a new deployment.
* No browser-level verification performed locally in this session: the Chromium journey runs in CI
  (`browser-smoke` job); the browser download is unavailable in this sandbox, and the environment lacks
  the shared libraries a Chromium build needs.
