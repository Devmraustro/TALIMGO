# Vercel deployment — verified state and owner actions

Status date: **2026-10-15**. Earlier public-host observations are preserved below with their original dates; this session could not re-fetch the public alias because the connected Vercel integration denied access.
This file records what was actually observed about the Vercel deployment from outside, what it can and
cannot do, and the exact owner actions that remain. It is a snapshot: re-verify before relying on it.

**Nothing on the Vercel side was changed in this round.** No project setting, deployment, alias, domain,
or environment variable was modified.

**Access check on 2026-10-15:** the connected Vercel integration can list projects and returned `talimgo-preview`
(project ID `prj_RX2NmJBTcZTkygGNgZKcbhqBk7aA`, account ID `team_iubQ9zIhIVUMqAj1vvq59Dk9`). However,
`get_project` and `list_deployments` were denied with **403 Forbidden** under scope `devmraustros-projects`;
`list_teams` and the Git deployment context returned no teams. The deployment-fetch helper also failed while
requesting Vercel's protection-bypass endpoint with 403. Therefore, project settings, deployment history,
current public responses, and response headers could not be freshly verified in this session. No deployment
or protection bypass was attempted beyond those read-only inspection calls.

### 2026-10-12 re-check (unchanged)

| URL | Observed |
| --- | --- |
| `https://talimgo-preview.vercel.app/` | **200**, interface shell renders, banner reads `Request failed (404).` |
| `https://talimgo-preview.vercel.app/api/auth/me` | **404** — Vercel's `NOT_FOUND` page, i.e. the static host answers, no API is behind it |
| `https://talimgo-preview.vercel.app/api/health` | **404** — same (checked in the previous round; the pattern is unchanged) |

The bare `Request failed (404).` string is itself evidence about *which* bundle is deployed: the current
branch reports a non-JSON API answer as "TALIMGO's API did not answer this request", and this host does
not say that. The deployed bundle therefore still predates that fix, exactly as in the previous round.
`deploy/health-check.sh` was also pointed at this host and returned **exit 1 ("unhealthy")**, which is
the correct verdict: it refuses a host that answers `200` with HTML instead of the recorded
`/api/health` contract.

Response headers remain **unverified**. The 2026-10-12 observation could not be refreshed on 2026-10-15 because the Vercel integration denied access to the deployment.

## What exists

| Item | Value |
| --- | --- |
| Vercel project | `talimgo-preview` (ID `prj_RX2NmJBTcZTkygGNgZKcbhqBk7aA`, as recorded in the owner's snapshot) |
| Deployment | `dpl_6ozG5iAjTRRekGW68JQPsvJyTp5d` (as recorded in the owner's snapshot) |
| Public alias | `https://talimgo-preview.vercel.app` |
| Immutable deployment URL | `https://talimgo-preview-ft71txd8s-devmraustros-projects.vercel.app` |
| Source | `Devmraustro/TALIMGO`, branch `arena/c22f9408-talimgo`, commit `fa421ab` |
| Framework / root | Vite, root directory `frontend`, build `npm run build`, install `npm ci`, output `dist` |

The deployed bundle corresponds to commit `fa421ab` and is now **stale relative to this branch**: three
shipped interface files have changed since (`frontend/src/lib/api.ts`, `frontend/src/App.tsx`,
`frontend/src/lib/i18n.ts` — the API-failure messaging and session-expiry handling added in `7d7edb3`),
plus `frontend/vercel.json`. That is why the live banner still reads `Request failed (404).` while the
current source would say "TALIMGO's API did not answer this request". Nothing here implies the host was
redeployed; the next deployment of this branch would pick the fixes up.

## What was verified, and how

The Vercel integration is present but only partially authorized. Project listing succeeded; project details and deployment listing returned 403, and the deployment fetch helper was denied at the protection-bypass endpoint. The URL observations below are historical public-host observations from 2026-10-11/12, not a fresh check on 2026-10-15. Response *headers* could not be read this way; that limitation is
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
* Pushing to the branch may or may not build a new Vercel deployment; the current Git integration and deployment history could not be inspected because the Vercel API returned 403. It remains an owner check (see below).

## Owner actions, shortest path first

1. **Restore Vercel inspection access** for the `devmraustros-projects` scope (or inspect the same values in the dashboard): confirm Git integration, whether pushes to `arena/c22f9408-talimgo` build, and deployment-protection settings. Then re-check the public alias and `/api/health`. Nothing in the repository can substitute for this.
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
| Vercel project/build | **PARTIALLY CONFIRMED** — project listing returns `talimgo-preview` and its ID; details and deployments remain **UNVERIFIED** due to 403 | `list_projects` succeeds; `get_project`, `list_deployments`, and deployment fetch fail with 403 under the Vercel scope |
| Deployed interface (frontend) | **CONFIRMED reachable, but non-functional as a product** — alias returns the interface shell over HTTPS; no API behind it | Public fetches: `/` renders; `/api/health` → 404; in-app banner "Request failed (404)." |
| Backend/API | **CONFIRMED not deployed** on that host; **UNVERIFIED** anywhere else (no authorised target exists) | `/api/health` → 404 on the alias |
| PostgreSQL/migrations | **CONFIRMED not deployed** for that host; migrations are **TESTED** in CI and locally against PostgreSQL 16.2 (upgrade to head, drift check, legacy-plan rehearsal, dump/restore with row-count and revision comparison) | `postgres-integration` CI job; local rehearsals in this session |
| Local AI runtime | **NOT PROVISIONED** — no runtime anywhere; the optional model test skips with a stated reason. No hosted AI is used or added | CI `local-only-ai` gate passes; `TALIMGO_AI_ENABLED=false` documented for production |
| Security posture | **CONFIRMED for the application and the Nginx example** (headers, docs 404 in production, edge rate limits, forwarding-header trust, cookie flags) — **UNVERIFIED for the live Vercel host** (response headers were not readable from here) | CI `proxy-tls-smoke`, `backend` job; local edge run against the real API |
| Accessibility | **TESTED in CI** — Chromium journey plus axe WCAG A/AA scans on representative screens; **NOT a conformance claim** and not a substitute for manual screen-reader, contrast and zoom/reflow checks | `browser-smoke` CI job |
| Secrets | **CONFIRMED** — no production values exist in the repository; the production preflight prints names and verdicts only | `backend/scripts/check_production_config.py`; tests assert no value is echoed |

## What this file does not claim

* No production readiness, no completed staging, no working backend, no database, no model runtime.
* No current header, TLS or routing guarantee for the live Vercel host: those were not re-measurable on 2026-10-15, and `frontend/vercel.json` only takes effect on a new deployment.
* No browser-level verification performed locally in this session: the Chromium journey runs in CI
  (`browser-smoke` job); the browser download is unavailable in this sandbox, and the environment lacks
  the shared libraries a Chromium build needs.
