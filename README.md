# TALIMGO

**AI-powered personalised learning platform.** TALIMGO turns a stated goal into a structured,
adaptable learning journey and measures demonstrated capability.

> **Status: pre-MVP, active development.** The product reference is
> [`TALIMGO_MASTER_REFERENCE.md`](./TALIMGO_MASTER_REFERENCE.md). Nothing in this repository is
> production-ready. See `docs/IMPLEMENTATION_PLAN.md` for what actually works today.

Core cycle: **GOAL → ASSESS → PLAN → LEARN → PRACTICE → BUILD → MEASURE → ADAPT**

## Hard constraint: local AI only

TALIMGO does **not** use hosted generative-AI providers. There is no OpenAI, Gemini, Anthropic,
hosted-gateway or hidden remote fallback in this codebase, and none may be added
(see [`AGENTS.md`](./AGENTS.md) §2). Inference runs on TALIMGO-controlled infrastructure through an
internal adapter that refuses non-local endpoints. If the local model is unavailable, the feature
fails explicitly instead of silently reaching for a cloud model. Details:
[`docs/LOCAL_AI_ARCHITECTURE.md`](./docs/LOCAL_AI_ARCHITECTURE.md).

## Repository layout

```
backend/                 FastAPI application (Python 3.11+)
  app/
    ai/                  Local-only model adapter, prompts, output validation
    curriculum/          Authored curriculum (content as data)
    learning/            Deterministic engine: mastery, roadmap, grading, selection
    routers/             HTTP endpoints (auth, goals, assessment, roadmap, tutor, admin…)
    models.py, schemas.py, security.py, config.py, db.py, main.py
  migrations/            Alembic migrations
  tests/                 pytest suite (unit, API, invariants, no-external-AI)
frontend/                React + TypeScript (Vite) learner UI, RTL-aware
docs/                    Plan, reuse audit, AI architecture, threat model, ADRs
.github/workflows/       CI quality gates
```

## Quick start (development)

```bash
# --- Backend ---
cd backend
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env                  # then edit if needed (read from backend/.env)
alembic upgrade head                  # creates the database schema
pytest -q                             # run the test suite
uvicorn app.main:app --reload --port 8000

# --- Frontend (second terminal) ---
cd frontend
npm install
npm run dev                           # http://localhost:5173, proxies /api to :8000
```

A local model is optional for development; the app runs and degrades explicitly without one.
To enable tutoring locally:

```bash
# Ollama is the recommended development runtime (local, no external requests)
ollama pull qwen2.5:7b-instruct      # example only — see docs/LOCAL_AI_ARCHITECTURE.md
export TALIMGO_AI_BASE_URL=http://127.0.0.1:11434
export TALIMGO_AI_MODEL=qwen2.5:7b-instruct
```

> **Windows:** the commands above are POSIX, but the backend suite also runs on Windows. One part of
> it — the tests that execute the checked-in deployment scripts — needs a POSIX shell: Git for
> Windows' Bash is found automatically, and `TALIMGO_TEST_BASH` selects another one. See
> [`docs/DEPLOYMENT.md`](./docs/DEPLOYMENT.md) §8.

## Documentation map

| Document | Purpose |
|---|---|
| [`AGENTS.md`](./AGENTS.md) | Binding engineering rules for humans and agents |
| [`TALIMGO_MASTER_REFERENCE.md`](./TALIMGO_MASTER_REFERENCE.md) | Product, brand, curriculum, safety, business |
| [`docs/IMPLEMENTATION_PLAN.md`](./docs/IMPLEMENTATION_PLAN.md) | Checkpoints, status, acceptance criteria |
| [`docs/OPEN_SOURCE_REUSE_AUDIT.md`](./docs/OPEN_SOURCE_REUSE_AUDIT.md) | Every candidate/component, licence, decision |
| [`docs/LOCAL_AI_ARCHITECTURE.md`](./docs/LOCAL_AI_ARCHITECTURE.md) | Local inference, model choice, no-cloud guarantees |
| [`docs/SECURITY_THREAT_MODEL.md`](./docs/SECURITY_THREAT_MODEL.md) | Assets, threats, mitigations, residual risk |
| [`docs/adr/`](./docs/adr/) | Architecture decision records |
| [`THIRD_PARTY_NOTICES.md`](./THIRD_PARTY_NOTICES.md) | Attributions for reused third-party code |

## Honest limitations (as of the current commit)

- The learner UI covers the first vertical slice only; many sections of the master reference (projects,
  spaced review, billing, institutional features) are **not built**.
- No local model weights are bundled or downloaded by this repository; tutoring requires a runtime you
  install yourself.
- Automated accessibility checks are partial; a full WCAG 2.2 AA audit has **not** been performed.
- Trademark/domain clearance is unresolved (`TALIMGO_MASTER_REFERENCE.md` §21). Use this repository
  name in development; do not assume the brand is clear for public launch.
