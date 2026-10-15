# Third-party notices

This file lists third-party components used by TALIMGO, their licences, and the attributions they
require. **No third-party source code is vendored in this repository** — components are consumed as
pinned dependencies. Where a licence requires attribution in documentation, it is reproduced or
referenced here.

Last updated: 2026-10-11.

---

## 1. Vendored source code

**None.** The open-source review (see `docs/OPEN_SOURCE_REUSE_AUDIT.md`) concluded with **no code copied**
from `braivo/braivo` (AGPL-3.0-only), `tripathiji1312/learn_buddy` (MIT, security-defective),
or `FlameEducation/FlameEducation` (personal, non-commercial licence — excluded).

---

## 2. Backend dependencies (Python)

| Component | Licence | Used for | Notes |
|---|---|---|---|
| FastAPI | MIT | HTTP framework | — |
| Starlette | BSD-3-Clause | ASGI toolkit (FastAPI dependency) | — |
| Uvicorn | BSD-3-Clause | ASGI server | — |
| Pydantic / pydantic-settings | MIT | Validation and configuration | — |
| SQLAlchemy | MIT | ORM and schema | — |
| Alembic | MIT | Database migrations | — |
| bcrypt | Apache-2.0 | Password hashing | OWASP-preferred slow hash |
| httpx | BSD-3-Clause | HTTP client for the local model endpoint and tests | — |
| pytest | MIT | Test runner | Development only |
| Ruff | MIT | Linting / formatting | Development only |
| Bandit | Apache-2.0 | Static security analysis | Development only |
| pytest-cov / coverage.py | MIT / Apache-2.0 | Coverage measurement | Development only |

Dependency versions are pinned in `backend/pyproject.toml`. Exact licence texts ship with each installed
package; the authoritative list for a given build is produced by the CI licence scan
(`docs/IMPLEMENTATION_PLAN.md`, checkpoint 6).

---

## 3. Frontend dependencies (Node/JS)

| Component | Licence | Used for | Notes |
|---|---|---|---|
| React / React DOM | MIT | UI library | — |
| Vite | MIT | Build tool and dev server | — |
| TypeScript | Apache-2.0 | Type checking | — |
| Vitest | MIT | Unit test runner | Development only |
| @testing-library/react, @testing-library/jest-dom | MIT | Component tests | Development only |
| jsdom | MIT | DOM environment for tests | Development only |
| @vitejs/plugin-react | MIT | React plugin for Vite | Development only |

Versions are pinned in `frontend/package.json`.

Versions used by the CI browser smoke test are pinned in `.github/workflows/ci.yml` and installed
only beneath the runner's temporary directory. They are not application dependencies and are not shipped:

| Component | Licence | Used for | Source |
|---|---|---|---|
| Playwright 1.64.0 | Apache-2.0 | Chromium browser journey | [microsoft/playwright v1.64.0](https://github.com/microsoft/playwright/tree/v1.64.0) |
| axe-core 4.10.3 | MPL-2.0 | Automated WCAG A/AA scans in CI only | [dequelabs/axe-core v4.10.3](https://github.com/dequelabs/axe-core/tree/v4.10.3) |


---

## 4. Local AI runtimes and model weights

| Component | Licence | Status | Notes |
|---|---|---|---|
| Ollama (runtime) | MIT | **Not bundled.** Optional development runtime the operator installs | Runs locally; TALIMGO contacts it over a local address only |
| vLLM (runtime) | Apache-2.0 | **Not bundled.** Evaluation candidate for production serving | — |
| Model weights | **Provider-specific — not yet selected** | **Not bundled, not downloaded by this repository** | Weight licences vary (some permit commercial use, some restrict redistribution or acceptable use). The licence of the selected weights must be read in full and recorded here **before** any weights are used, per `docs/LOCAL_AI_ARCHITECTURE.md` §4.1 criterion 7 |

---

## 5. Standards referenced (not code)

| Standard | Owner | Use in TALIMGO |
|---|---|---|
| WCAG 2.2 | W3C | Accessibility target for the design system (master reference §9.5.3) |
| QTI 3.0 | 1EdTech | Planned export format for assessment items |
| xAPI 1.0.3 | ADL | Planned export format for learning records |
| LTI 1.3 | 1EdTech | Planned institutional integration (FUTURE) |
| FSRS | open-spaced-repetition (MIT) | Algorithm reference for the spaced-review milestone |

---

## 6. Architectural credit

TALIMGO's learning-engine design was informed by reading the public documentation and architecture of
`braivo/braivo` (AGPL-3.0-only, © 2026 Konstantin Tarkus). The specific patterns credited — evidence as
the source of truth, derived/disposable estimates, one versioned learning model replaced rather than
selected, separating "never learned" from "learned and fading", and keeping the learning module pure —
are recorded in `docs/OPEN_SOURCE_REUSE_AUDIT.md` §1.5. **No Braivo code, text, schema, or test was
copied into this repository.** All implementations here are independently written against TALIMGO's own
specification (`TALIMGO_MASTER_REFERENCE.md` §6.2, §6.6).
