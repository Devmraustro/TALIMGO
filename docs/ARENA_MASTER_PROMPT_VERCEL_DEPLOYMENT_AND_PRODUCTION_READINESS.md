# TALIMGO — Arena Master Prompt: Deployment Verification and Production Readiness

**Priority:** High  
**Repository:** https://github.com/Devmraustro/TALIMGO  
**Required working branch:** `arena/c22f9408-talimgo`  
**Never modify or merge into `main` unless the owner explicitly approves it.**  
**Read first:** `AGENTS.md`, `TALIMGO_MASTER_REFERENCE.md`, `docs/IMPLEMENTATION_PLAN.md`, `docs/DEPLOYMENT.md`, `docs/LOCAL_AI_ARCHITECTURE.md`, `docs/SECURITY_THREAT_MODEL.md`, and relevant ADRs.

## Mission

Continue the actual engineering work needed to turn the current Vercel frontend deployment into a verified, honestly documented TALIMGO deployment. Do not stop after writing a plan. Inspect the live repository and Vercel state, execute every safe task available with the permissions actually granted, add tests, run checks, commit changes only to the required branch, and provide a factual report. If a step requires an owner-only authorization, production secret, domain/DNS action, paid resource, or an inaccessible account scope, isolate that exact blocker and give the owner the shortest safe action to unblock it. Do not fabricate access or results.

## Verified starting state (re-check before acting)

- A Vercel deployment exists:
  - Deployment ID: `dpl_6ozG5iAjTRRekGW68JQPsvJyTp5d`
  - Project ID: `prj_RX2NmJBTcZTkygGNgZKcbhqBk7aA`
  - Project name: `talimgo-preview`
  - Deployment URL: `https://talimgo-preview-ft71txd8s-devmraustros-projects.vercel.app`
  - Alias returned by Vercel: `https://talimgo-preview.vercel.app`
  - Vercel reported `state=READY`, `readyState=READY`, target `production`
  - Source: `Devmraustro/TALIMGO`, branch `arena/c22f9408-talimgo`, commit `fa421ab4f82ae93404a3475702a3f6e157a4fcd8`
  - Framework Vite; root directory was set to `frontend`; build command `npm run build`; install command `npm ci`; output directory `dist`; Node `22.x`.
- The Vercel connector has previously returned HTTP 403 for deployment events, project details/domains, and the protection-bypass fetch endpoint with scope `devmraustros-projects` / team ID `team_iubQ9zIhIVUMqAj1vvq59Dk9`. The deployment record itself was readable and reported READY. Do not interpret the 403 as proof that the deployment failed; it means those protected operations were not authorized through that connector.
- The repository README states the product is pre-MVP and not production-ready. CI has exercised tests and a simulated reverse-proxy/TLS setup, but not a real externally managed production environment.
- `frontend/vite.config.ts` proxies `/api` only in Vite's development server. Do not assume this proxy exists on Vercel's static production deployment.
- Backend is FastAPI under `backend/`; production requires PostgreSQL and migrations. Local AI is a strict product constraint: only TALIMGO-controlled infrastructure and locally hosted open-weight models. Never add OpenAI, Gemini, Anthropic, hosted AI gateways, hosted embeddings/speech, or a hidden remote fallback.
- No actual production credentials or secret values should be committed. “Secrets can be changed later” does not authorize committing or exposing them.

## Non-negotiable constraints

1. Follow `AGENTS.md` and the owner’s no-cloud-AI rule.
2. Preserve current architecture and existing work; use minimal, focused changes. Before adding a major component, search GitHub, inspect source/tests/activity/licence, document reuse or rejection, and preserve notices.
3. Never print, request in chat, or commit credentials, session secrets, database URLs with passwords, Vercel bypass secrets, or personal data. Use platform secret stores and environment-variable names only.
4. Never disable authentication, deployment protection, CORS, CSP, TLS verification, rate limits, or security middleware merely to make a test pass. If a public demo requires a protection-setting change, inspect the exact setting and report the effect; do not silently weaken protection.
5. Do not create repeated deployments until the existing deployment/project configuration and status have been checked. Prefer reusing the current project.
6. Do not claim “production-ready” based on a successful frontend build, a green CI run, or Vercel READY alone.
7. Keep `main` unchanged. Do not merge or close the existing PR unless explicitly authorized.

## Work plan — execute in order

### A. Reconcile deployment state
- Inspect the Vercel project and deployment by the exact IDs above, and confirm source commit, root directory, build settings, deployment target, assigned aliases/domains, and deployment-protection configuration.
- Check deployment/build events and logs if access permits.
- Test the public URL from an independent HTTP client/browser. Record status, redirect chain, content type, page title, critical asset responses, browser console errors, and whether the site is protected by Vercel authentication.
- Test the canonical alias `https://talimgo-preview.vercel.app` and the immutable deployment URL separately.
- If the connector cannot access project scope, do not retry identical unauthorized calls endlessly. Use only a legitimate already-authorized route. Otherwise document the exact scope/permission blocker and the precise owner action required in Vercel/ChatGPT connection settings.
- Confirm whether pushes to the branch trigger deployments. If Git integration is not configured, link the existing project to the existing repository using the least disruptive supported path; do not create another project with a duplicate name.

### B. Make frontend deployment behaviour correct
- Verify all SPA routes load on direct refresh and return appropriate content; add Vercel routing configuration only if required by the actual app and supported by the current framework.
- Inspect frontend API calls and auth-cookie behaviour. The current Vite `server.proxy` is development-only; determine the intended production API origin/routing and implement a robust, explicit configuration without leaking secrets.
- Preferred same-origin `/api` architecture is already documented. If a separate backend host is required, configure a single documented public API base URL and exact CORS origins; preserve HttpOnly/Secure/SameSite cookie behaviour and credentials mode. Never hardcode a private or localhost API URL into production.
- Add automated tests for URL selection, failed API connectivity, session expiry, and important navigation only where those tests fit the existing structure.
- Verify accessibility and responsive behaviour using existing browser-smoke tooling; don't claim full WCAG conformance.

### C. Decide and document the real hosting topology
- Vercel is currently a frontend deployment. Do not assume it hosts FastAPI, PostgreSQL, or a persistent local model.
- Inspect existing Docker/deploy files and docs before proposing a service. Choose the minimum viable topology that preserves the repository's same-origin security model where practical:
  - Vercel for the static React/Vite frontend is acceptable.
  - FastAPI requires a Python-capable service/container or an intentionally designed serverless adaptation; do not blindly port the whole API to serverless.
  - PostgreSQL must be persistent, backed up, migration-managed, and reachable only by the API.
  - Local inference must run on TALIMGO-controlled/private infrastructure (for example a private Ollama/vLLM/llama.cpp host); never route learner data to a hosted AI provider.
- Do not buy a domain, enable paid resources, deploy a public database, or create paid GPU services without explicit owner approval.
- If no authorized hosting credentials or infrastructure are available, implement and test deployment manifests, health checks, documentation, and CI checks in the repo; leave only the genuinely owner-dependent action blocked.

### D. Environment and security audit
- Inspect all required production environment variables from `backend/.env.example` and application settings. Ensure the app refuses weak/missing production secrets, non-PostgreSQL production DBs, wildcard CORS, and non-local AI endpoints as intended.
- Do not add fake production values to Vercel or the repository. Add an environment-variable checklist that lists names, purpose, environment scope, and how the owner securely creates the value, without including values.
- Verify `TALIMGO_ENV=production`, a strong unique `TALIMGO_SESSION_SECRET`, exact `TALIMGO_ALLOWED_ORIGINS`, PostgreSQL connection, and `TALIMGO_AI_ENABLED=false` until a private local runtime is genuinely provisioned and evaluated. Do not enable AI with a placeholder model.
- Confirm API docs are disabled in production, security headers are correct, unauthenticated routes are rate-limited at the edge, errors do not leak internals, and logs never include learner content or secrets.
- Review privacy/retention, backup/restore, migrations, deletion/export flows, and deployment rollback requirements.

### E. Verification and CI
- Run all relevant checks using commands already documented by the project:
  - Frontend: `npm ci --no-audit --no-fund`, `npm run typecheck`, `npm run build`, `npm test -- --run`.
  - Backend: `pip install -e ".[dev]"`, `ruff check app tests scripts`, `ruff format --check app tests scripts`, `bandit -q -r app`, `alembic upgrade head`, `alembic check`, `pytest -q`, and `python scripts/check_no_external_ai.py`.
  - PostgreSQL integration, dependency/licence audit, browser smoke, and proxy/TLS smoke as appropriate.
- Do not run destructive tests against real user/production data. Any live verification that creates an account must use disposable credentials, guarantee cleanup, and verify cleanup; prefer the existing `backend/scripts/verify_deployment.py` safeguards.
- Add only useful regression tests. Fix real failures rather than skipping or weakening assertions.
- Re-check the Git diff for secrets, generated files, accidental lockfile churn, licence omissions, and unrelated edits.
- Commit the focused changes to `arena/c22f9408-talimgo`, then verify the resulting commit and CI status. Never say CI passed until the observed run is complete and green.

### F. Required deliverables
1. A verified deployment report separating:
   - frontend URL status,
   - Vercel build status,
   - API/backend status,
   - PostgreSQL/migration status,
   - local AI runtime status,
   - security/accessibility status,
   - remaining owner-only blockers.
2. Updated `docs/DEPLOYMENT.md` and/or a focused deployment checklist with the actual topology, exact required variable names (never values), reproducible steps, health checks, rollback, and clear labels for tested vs untested.
3. Tests/CI changes for any implementation changes.
4. A concise change summary with exact commit SHA, CI run URL/results, URLs tested, observed HTTP status codes, and remaining limitations.
5. If a step is blocked, provide the exact reason and smallest owner action. Do not label blocked work as complete.

## Completion criteria

This task is complete only when:
- the deployed frontend is independently reachable (or the protection/access blocker is evidenced exactly);
- production API routing is intentionally configured and tested rather than accidentally relying on Vite dev proxy;
- the backend/database deployment status is explicitly verified or clearly marked unprovisioned;
- no hosted AI provider has been introduced;
- all relevant tests and CI results are recorded accurately;
- documentation matches the implementation;
- changes are committed only to the required working branch;
- every uncompleted owner-dependent action is listed explicitly.

Begin by re-reading the current branch and deployment state. The state above is a starting snapshot, not a substitute for fresh verification.
