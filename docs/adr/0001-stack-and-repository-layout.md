# ADR 0001: Stack and repository layout

Status: **accepted** (2026-10-10) · Owner-delegated to the implementation directive.

## Context

The stack had to be chosen after inspecting the environment, not before. Verified facts
(2026-10-10, this workspace):

- Python 3.11.2 with `venv` available; `pip install` from PyPI **works**
  (FastAPI 0.143.0, Pydantic 2.14.0, SQLAlchemy 2.1.4, Alembic 1.20.0, pytest 9.1.1, httpx 0.28.1,
  bcrypt 5.0.0).
- Node 22.22.3 with npm 10.9.8; `npm install` from the public registry **works**
  (React 19.3.0 installed in ~1 s in a scratch project).
- No local model runtime is installed (`ollama`, `vllm`, `llama-server` all absent), and pulling
  weights is not possible in this sandbox.
- Master reference §13.4 set criteria: Arabic/RTL maturity, hiring pool, slow-network performance,
  cost, AI-orchestration ecosystem, type safety, operational simplicity, licence clarity — with
  PostgreSQL recommended as the system of record and no premature polyglot persistence.

## Decision

- **Backend:** Python 3.11+ with **FastAPI**, **Pydantic v2** for all input/output and AI-output
  validation, **SQLAlchemy 2.x** with **Alembic** migrations. SQLite for development and tests,
  PostgreSQL for production via `DATABASE_URL` (the models avoid SQLite-only types).
- **Frontend:** **Vite + React 19 + TypeScript**, plain CSS with design tokens from the master
  reference §9 (no heavy UI framework yet, so RTL and Arabic typography can be controlled directly).
- **Tests:** `pytest` (+ `httpx` transport for API tests) on the backend; `Vitest` +
  Testing Library on the frontend.
- **Layout:** `backend/` and `frontend/` as siblings; the frontend dev server proxies `/api` to the
  backend so the browser only ever talks to one origin (master reference §13.1 principle 6 and the
  same-origin reasoning observed in comparable platforms).
- **Local inference:** HTTP to a local runtime, abstracted behind `app/ai/adapter.py`
  (see ADR 0002).

## Why not the alternatives

| Alternative | Why rejected |
|---|---|
| TypeScript/Bun monorepo (as the closest comparable project uses) | Bun is not installed here; adopting another toolchain adds risk without evidence of benefit; Python gives direct access to the evaluation/retrieval tooling the AI layer will need |
| Node/NestJS backend | Weaker fit for the eventual evaluation, dataset and embedding work; no compensating advantage for this team size |
| Server-rendered templates instead of React | Faster to first render, but the reference specifies a component-driven design system with RTL switching and a roadmapped application surface; React is the better long-term fit and was verified installable |
| A full LMS as the foundation (Open edX, Moodle, Canvas) | Licence constraints (AGPL/GPL), course-centric rather than goal→mastery-centric, and an operational surface many times larger than the product needs |
| A component library (MUI/Ant/shadcn) now | Deferred deliberately: RTL and Arabic typography must be validated against whatever is chosen (master reference ADR-style DEC-012); adding one now would lock in unverified assumptions |

## Consequences

- The core learning logic stays pure Python with no framework dependency, so it is testable and
  portable.
- Two toolchains (Python + Node) exist in the repository; CI runs both. Accepted cost.
- SQLite development parity with PostgreSQL is imperfect (concurrency, types, indexes). Mitigated by
  keeping models portable and running the migration test against both where CI allows.
- Choosing React defers the framework-level RTL decision to our own CSS tokens, which is more work but
  removes an unverified dependency.
