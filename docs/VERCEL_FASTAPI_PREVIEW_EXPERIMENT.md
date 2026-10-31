# Vercel FastAPI Preview Experiment

Status: isolated preview experiment; not production.

## Scope
- Project: `talimgo-api` (Vercel FastAPI project).
- Branch: `experiment/vercel-fastapi-preview-20261031`.
- Base commit: `cf0a13e70c9e70e1ffaa2f2eda9c8b8e263044df`.
- Purpose: verify that Vercel can import and execute the existing FastAPI application as a Python Function.

## Preview-only configuration
- `TALIMGO_ENV=development`.
- `TALIMGO_DATABASE_URL=sqlite:////tmp/talimgo-vercel-experiment.db`.
- `TALIMGO_AI_ENABLED=false`.
- `TALIMGO_SEED_ON_STARTUP=false`.
- Strong random preview-only session secret stored as a Vercel sensitive environment variable.
- Explicit Vercel frontend preview origins only.

## Safety boundaries
- Environment variables are scoped to Preview and this branch only.
- No Production environment variables are created or modified.
- No Alwaysdata or PostgreSQL production connection is configured.
- The `/tmp` SQLite database is ephemeral and is not suitable for persistence or real learner data.
- AI remains disabled.
- Vercel SSO/deployment protection remains enabled.
- No AUSTRO resources are involved.

## Acceptance
1. Preview build succeeds.
2. Protected preview runtime answers `GET /api/health` with the expected JSON.
3. Startup logs show no SQLite, import, or lifespan error.
4. The deployment remains Preview-only and protected.
5. No production database writes, migrations, or deployment promotion occur.

A successful result proves only that Vercel can host the current FastAPI app for a protected technical preview. It does not prove production persistence, durable storage, external database connectivity, backup/restore, or full learner journeys.
