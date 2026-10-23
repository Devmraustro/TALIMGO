# Vercel deployment — verified state and owner actions

Status date: **2026-10-22**. Earlier public-host observations are preserved below with their original dates. The 2026-10-15 access denial recorded in the next paragraph no longer applies: on 2026-10-22 the connected Vercel integration answered project, deployment, domain and environment-variable reads (see the re-check after it).
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

### 2026-10-22 re-check (edge-smoke CI recovery session)

**Nothing on the Vercel side was changed by hand in this session.** No project setting, deployment,
alias, domain, rewrite or environment variable was created or modified. What changed on its own is
Git-triggered: pushes created the deployment attempts listed below. All Vercel API observations are
read-only results from the connected integration on this date; public-host observations were made
through a page fetcher because direct HTTPS from the sandbox to `*.vercel.app` is blocked by sandbox
egress (`SSL_ERROR_SYSCALL`, curl code 000), so **response headers remain unverified** and
`deploy/health-check.sh` cannot be run against the alias from here (its exit 1 in this sandbox means
"unreachable from here", not a verdict on the host).

| Check | Observed (2026-10-22) |
| --- | --- |
| Project `talimgo-preview` (`prj_RX2NmJBTcZTkygGNgZKcbhqBk7aA`) | Vite, Hobby plan, production branch `main`, `requireVerifiedCommits: true`, SSO protection `all_except_custom_domains` |
| Environment variables on the project | **None** (empty list) |
| Project domains | Only `talimgo-preview.vercel.app`; no custom domain, no API host |
| Production target (the public alias) | Still deployment `dpl_D4SuhSmqF2fDuTnbhoM2AecQCWfL` of commit `fa421ab` (`PROMOTED`) — the stale bundle below |
| Preview for `a7bb749` (signed) | `dpl_DzeV5iwfoXdNxXgUb3KMr1A67gYD`, **READY**/**STAGED**, branch alias `talimgo-preview-git-arena-c22f9408-67b2e9-devmraustros-projects.vercel.app`; the signing remediation in this file worked |
| Preview attempt for `4609b81` (unsigned CI fix) | `dpl_DF5jdTRtgS9PYTyVavdHKANDf5jb`, **CANCELED** — "The deployment was canceled because the commit signature couldn't be verified." The sandbox has no signing key; see the owner action below |
| `https://talimgo-preview.vercel.app/` | **200** shell, banner still `Request failed (404).` — the production alias does **not** serve the `a7bb749` preview |
| `https://talimgo-preview.vercel.app/api/health` | **404** `NOT_FOUND` — still no API behind the alias |
| Branch preview alias `/api/health` | Redirects to Vercel SSO login (Protected Deployment) — not inspectable without an owner session, and no bypass was attempted |

**Owner action added by this session:** commit `4609b81` (the edge-smoke CI fix, on
`arena/cd207ad5-talimgo`) must be signed before Vercel will build it — for example
`git cherry-pick 4609b81` onto `arena/c22f9408-talimgo` with the local SSH signing setup recorded
below, then push. Everything else about the deployment gap is unchanged: **no backend hostname or
PostgreSQL instance exists**, so no `/api` rewrite was configured (the root `vercel.json` keeps its
intentional `/api` → 404), no database write has ever reached a deployed environment, and the
checklist in `docs/DEPLOYMENT.md` §11 remains the path to a real deployment.

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
| Deployment protection | The **immutable** deployment URL redirects to `vercel.com/login?sso-api...` ("Protected Deployment – Vercel"), while the **public alias** is reachable without authentication. Deployment protection therefore covers the per-deployment host, not the alias |
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
* Choose the topology (see `docs/DEPLOYMENT.md`, "Where the built interface is hosted"):
  * single host: FastAPI + PostgreSQL + Nginx serving the built interface on the same origin — the
    supported, tested path, and the only one that needs no Vercel involvement;
  * Vercel for the interface with a Vercel rewrite of `/api/*` to the API host — keeps the browser
    same-origin, so cookies and CORS are unchanged; needs the API host and one `vercel.json` entry.
* **Provision the backend** (Python host + PostgreSQL + secrets named in `docs/DEPLOYMENT.md`). Until
  this exists, the Vercel deployment cannot work regardless of configuration.
* **Deploy and re-verify**: run `backend/scripts/verify_deployment.py` against whichever URL serves
  the product, and record the result. The existing Vercel deployment will keep showing
  "TALIMGO's API did not answer this request" until an API is reachable from the page's origin.
* **Decide about the current deployment**: keep it as a preview of the interface, or delete it. It
  must not be presented as a working product.

## SSH commit signing fix (2026-10-22)

The Vercel "Require Verified Commits" setting blocked preview deployments because commits on this branch
were not cryptographically verified by GitHub.

**Root cause:**
- Local signing key (Ed25519, `SHA256:vWuBK+/6g+aGup6KKUQSAec+C5pcD/bmh3CQTE7aRKM`) was not registered
  as a **Signing Key** on GitHub — only an Authentication Key existed.
- The `allowed_signers` file used an incorrect principal format, causing local verification to fail with
  `invalid key` and `No principal matched`.
- Git author identity used `audit@talimgo.local` instead of the verified GitHub email `mraustro@gmail.com`.

**Remediation (2026-10-22):**
1. Registered the local Ed25519 public key as a GitHub **Signing Key** (title: `TALIMGO dz`), fingerprint
   verified to match `SHA256:vWuBK+/6g+aGup6KKUQSAec+C5pcD/bmh3CQTE7aRKM`.
2. Repaired `allowed_signers` to use the correct format:
   `mraustro@gmail.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBm7sK6lGVqqYW/ner1+WtH+jBIZzpV/CX+TxCAIU2U/`
3. Configured Git identity: `TALIMGO Audit Agent <mraustro@gmail.com>` (local repo config).
4. Local signature verification now succeeds: `Good "git" signature for mraustro@gmail.com with
   ED25519 key SHA256:vWuBK+/6g+aGup6KKUQSAec+C5pcD/bmh3CQTE7aRKM`.

**Status:** Resolved for signed pushes — the signed commits `6d1859c` and `a7bb749` each produced a
READY preview deployment (see the 2026-10-22 re-check above). The public alias's production target
remains at commit `fa421ab` (stale); only the branch preview alias moved. Unsigned commits are still
cancelled, most recently `4609b81`.

---

## What this file does not claim

* No production readiness, no completed staging, no working backend, no database, no model runtime.
* No current header, TLS or routing guarantee for the live Vercel host: those were not re-measurable on 2026-10-15, and `frontend/vercel.json` only takes effect on a new deployment.
* No browser-level verification performed locally in this session: the Chromium journey runs in CI
  (`browser-smoke` job); the browser download is unavailable in this sandbox, and the environment lacks
  the shared libraries a Chromium build needs.