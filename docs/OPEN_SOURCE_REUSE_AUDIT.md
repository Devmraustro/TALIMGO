# Open-source reuse audit

**Method.** Each candidate was inspected on **2026-10-10** by reading its repository metadata through
the GitHub API, downloading and reading its actual source where licence and size permitted, and reading
its licence file **as a file** (not as a badge). Where a project was downloaded, the exact commit is
recorded. Nothing in this document is a substitute for legal advice.

**Binding outcome summary**

| Candidate | Licence (verified) | Revision inspected | Decision |
|---|---|---|---|
| `braivo/braivo` | **AGPL-3.0-only** (LICENSE + `REUSE.toml` + per-file SPDX headers) | `9f16d8508c4d1e4966254cc0f4418f9b36a3e233` (2026-10-10) | **Architecture studied. No code copied, adapted, or vendored.** Reasons in §1.4 |
| `tripathiji1312/learn_buddy` | **MIT** (LICENSE file, © 2025 Swarnam Tripathi and Sohini Banerjee) | `eae376ce01087627efd8d79f31ab37c4a58bd94f` (2025-06-23) | **Audited. No code copied.** Defects in §2.3 |
| `FlameEducation/FlameEducation` | **Personal, non-commercial licence** (LICENSE file) | `38382e5c97e9a03102c959da2bc20e38774e8de6` (2025-12-19) | **Excluded from a commercial product.** No code copied; studied at a high level only |
| Tested Python/JS libraries (FastAPI, SQLAlchemy, Pydantic, Alembic, pytest, httpx, bcrypt; React, Vite, Vitest, Testing Library) | MIT / Apache-2.0 / BSD / PSF | versions pinned in manifests | **Reused as dependencies** (not vendored). Notices in `THIRD_PARTY_NOTICES.md` |
| CI-only browser tooling (`playwright@1.64.0`, `axe-core@4.10.3`) | Apache-2.0 / MPL-2.0 (verified at `microsoft/playwright` v1.64.0 and `dequelabs/axe-core` v4.10.3) | versions pinned directly in `.github/workflows/ci.yml` and installed under `$RUNNER_TEMP` | **Test-only, not included in the product bundle, frontend manifest or lockfile.** Notices below |

---

## 1. Braivo — closest architectural match, deliberately not adopted

### 1.1 What it is

Repository description: *"Open-source adaptive learning platform for turning existing educational
content into personalized, white-label AI tutors."* Created 2026-09-20, last push 2026-10-10, 0 stars,
2 forks, 10 open issues. TypeScript/Bun monorepo: `apps/{server,console,learn,storybook}`,
`packages/{db,ui,i18n,auth-client}`.

### 1.2 Verified licence position

- `LICENSE` = **GNU AFFERO GENERAL PUBLIC LICENSE Version 3**, `Copyright (C) 2026 Konstantin Tarkus`.
- `REUSE.toml` declares `SPDX-License-Identifier = "AGPL-3.0-only"` for the paths that cannot carry a
  header, and states that source files carry a two-line SPDX header instead (`AGPL-3.0-only`), so the
  repository is REUSE-compliant per-file, not multi-licensed.
- `docs/adr/0001-licensing.md` (status: *superseded*) records an earlier split into AGPL core +
  Apache-2.0 SDK. `docs/adr/0002-agpl-only.md` (status: *accepted*) supersedes it: **every file Braivo
  writes is AGPL-3.0-only**, the Apache-2.0 SDK package was removed, and a commercial licence is
  available separately from the copyright holder (not granted by the repository files).
- Third-party code inside the repo keeps its upstream licence: shadcn/ui components remain MIT
  (`LICENSES/MIT.txt`).

### 1.3 What the AGPL means for TALIMGO (consequence, stated plainly)

If TALIMGO copied, adapted or vendored Braivo code and then operated a modified version as a network
service — which is exactly what TALIMGO is — the AGPL's network-use clause would require offering the
**complete corresponding source of the modified version** to every user interacting with it over the
network. That is incompatible with TALIMGO's current plan to keep its implementation private and to
consider a commercial offering, unless the owner deliberately adopts AGPL for the whole derived work or
buys a commercial licence from Braivo's copyright holder. **No such decision has been made, so no Braivo
code may enter this repository.** Reading its documentation for design understanding is permitted and is
what was done; copying its expression is not.

### 1.4 Technical reasons it would be rejected even with a permissive licence

| Finding | Evidence | Consequence for TALIMGO |
|---|---|---|
| Its default model integration is a **hosted provider call** | `apps/server/ai/model.ts` line 62 posts to `https://api.anthropic.com/v1/messages` (with `anthropic-version: 2023-06-01`) | Directly violates TALIMGO's hard local-only-AI rule (`AGENTS.md` §2). TALIMGO could not adopt this module at all; it must build its own adapter |
| Self-declared as pre-release | `README` (per the task brief and repository state; project created 2026-09-20) | Not a stable base; a moving target for a small team |
| Architecture is designed for **organisations and cohorts** (organisation-scoped content, invitations, shareable learner history per organisation) | `docs/architecture.md`, `docs/adr/0018`, `docs/adr/0032` | TALIMGO's first release is individual-learner only; this is a different tenancy model |
| Full monorepo with its own toolchain (Bun, Vitest on Bun, Drizzle, Hono, Better Auth) | `package.json`, `docs/architecture.md` | Adopting it means adopting its whole stack — a stack decision TALIMGO should make on its own merits |

### 1.5 What was learned from it (design-level, non-copied, credited)

These are widely practised architectural patterns; TALIMGO implemented them independently, but the
reading sharpened the specification, and that is recorded here honestly:

1. **Evidence is the source of truth; estimates are derived and disposable.** Persist what actually
   happened so mastery can be recomputed when the model changes. (TALIMGO: `learner_evidence` table +
   `learning/mastery.py` replay.)
2. **One active, versioned learning model — replaced, not selected at runtime.** No registry, no
   per-tenant model choice; a stale `model_version` is rejected input, not silently mixed. (TALIMGO:
   `MODEL_VERSION = "mastery-v1"` with an explicit rejection path and a test asserting it.)
3. **Separate "never learned" from "learned and fading"** instead of collapsing both into one low score.
   (TALIMGO: `acquiring` → `retaining` phases plus a derived `needs_review` condition.)
4. **Keep the learning module pure** — no I/O, clock or randomness inside; pass `now` in. This is what
   makes replay, testing and model replacement possible. (TALIMGO: `app/learning/*` takes `now` as a
   parameter and performs no I/O; an import test enforces that it never imports the web/DB/AI layers.)
5. **Treat model output as untrusted and validate before it affects state**, and keep prompts version
   controlled next to the code that uses them.
6. **Binary, normalized evidence at the grading boundary** rather than raw scores, because a 0.8 from
   one grader does not mean what a 0.8 from another means.

### 1.6 Decision

**Rejected for code reuse; accepted as a design reference.** Recorded in
`docs/adr/0003-licence-policy-and-reuse-decisions.md`. If the owner ever wishes to reuse Braivo code,
the prerequisites are: (a) a documented licence decision accepting AGPL obligations for the derived
work or a purchased commercial licence, and (b) a rewritten AI module that cannot reach any hosted
provider.

---

## 2. LearnBuddy — MIT, audited, no code copied

### 2.1 What it is

*"LearnBuddy is a free, open-source, AI-driven adaptive learning platform…"* FastAPI + PostgreSQL +
a static frontend, plus `sentence-transformers`/`torch` for similarity. Created 2025-06-05, **last push
2025-06-23** (≈16 months dormant at the time of audit), 3 stars, 1 fork, 0 open issues, 82 MB repository
(includes a `model_cache/`).

### 2.2 Licence position

`LICENSE` is the standard **MIT** text, `Copyright (c) 2025 Swarnam Tripathi and Sohini Banerjee`.
MIT is compatible with TALIMGO. **Licence is not the reason for rejection.**

### 2.3 Defects found by reading the actual source

| # | Finding | File / lines (as inspected) | Severity |
|---|---|---|---|
| 1 | **Weak default JWT secret committed in source**: `SECRET_KEY = os.getenv("SECRET_KEY", "a_very_secret_key_for_your_hackathon")`. If the environment variable is unset in production, every token is forgeable by anyone who reads the repository. | `src/security.py` | Critical |
| 2 | **Permissive CORS with credentials**: `allow_origins=["*"]`, `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`. A wildcard origin with credentials is both an insecure combination and, per the CORS specification, not honoured as written — a sign the security model was not reviewed. | `src/main.py` | High |
| 3 | **Model loaded at import time, duplicated**: `SentenceTransformer(...)` is instantiated in `src/main.py`, while the code comments record that the same import previously lived in `learning_models.py`. Import-time heavyweight initialisation and duplicate loading inflate memory and make the service fragile under a worker-per-process server. | `src/main.py`, `src/learning_models.py` | Medium |
| 4 | **Connection-per-query, no pooling, `ORDER BY RANDOM()`**: each item selection opens a raw `psycopg2` connection and closes it; random ordering is evaluated on an unindexed expression. | `src/adaptive_engine.py` | Medium (performance) |
| 5 | **No environment/secret validation, no startup validation**: configuration is read ad hoc with silent defaults. | `src/security.py`, `src/adaptive_engine.py` | High |
| 6 | Bibliographic dependency risk: `python-jose` and `passlib[bcrypt]` (both pinned versions, and passlib is effectively unmaintained vs modern `bcrypt`). | `requirements.txt` | Medium |
| 7 | Repository hygiene: vendored `__pycache__`, a committed `model_cache/` directory, no CI workflow visible that runs the tests. | repository root | Low |
| 8 | Documentation contains demonstration credentials and a public demo link. | `README.md` | Low (but a pattern TALIMGO must not copy: `AGENTS.md` §6 forbids demo credentials in production) |

### 2.4 What it contains that is worth *studying* (not copying)

- A bandit-style difficulty selector (`select_difficulty_ultra_responsive`, `update_bandit_state_enhanced`)
  — a plausible thin-data approach to item difficulty, but it is database-coupled, randomised, and not
  separately unit-tested. TALIMGO instead keeps item selection deterministic first (difficulty band from
  mastery phase) and records difficulty adaptation as a **FUTURE** experiment to be introduced only with
  measured evidence (see `docs/adr/0004-mastery-model-v1.md`).
- A plain FastAPI + PostgreSQL shape that confirms the stack family is workable for this product class.

### 2.5 Decision

**MIT permits reuse, but no code was copied.** The authentication, configuration, deployment and
application code are not safe to adopt (findings 1, 2, 5). The adaptive-engine idea was considered and
replaced with a deterministic, tested design. If any single algorithm from this project is ever reused,
the requirement is: isolate it, re-implement with tests, record the source commit and MIT notice in
`THIRD_PARTY_NOTICES.md`, and review it as new code.

---

## 3. FlameEducation — excluded

`LICENSE` is a **"Flame Education Personal Use License"**: use is limited to personal, non-commercial
purposes; selling, paid services, commercial deployment, and distribution of modified versions are
expressly prohibited without prior written consent. TALIMGO is intended to be a commercial product.
**Therefore no code from this project may be copied, adapted or vendored.** It was reviewed only at the
level of its public description (an LLM-based tutoring platform with TTS/ASR, Vue-based client).

If the owner ever wants to reuse it, the only acceptable path is a written licence from its authors;
licence-fee terms, attribution, and the applicability of its bundled dependencies would all need review.

---

## 4. Platforms and libraries considered, and the standing decision

| Candidate | Licence (per earlier research, GitHub metadata 2026-10-10) | Decision for TALIMGO |
|---|---|---|
| Open edX (`openedx/openedx-platform`) | AGPL-3.0 | Rejected as a base (AGPL + course-centric model + large operational surface) |
| Moodle | GPL-3.0 | Rejected as a base; question-type taxonomy studied conceptually |
| Canvas LMS | AGPL-3.0 | Rejected as a base; rubric/outcomes concepts studied |
| Kolibri (`learningequality/kolibri`) | MIT | **Reference for future offline/low-bandwidth work.** No code copied yet |
| Oppia | Apache-2.0 | Candidate for future lesson-interaction study |
| Frappe LMS | AGPL-3.0 | Watch list only |
| FSRS (`open-spaced-repetition/ts-fsrs`, `fsrs4anki`) | MIT | Planned scheduler reference for the spaced-review milestone (not yet integrated) |
| `litellm`, `langfuse`, `promptfoo`, `vllm` | mixed (`NOASSERTION` for two) | `vllm` (Apache-2.0) is the evaluation candidate for production local serving. `litellm`/`langfuse` are **excluded under the current policy** because a "gateway" that can route to hosted providers conflicts with the local-only rule; `promptfoo` (MIT) is a candidate for the local evaluation harness after a licence re-read |

### 4.1 Deployment tooling search (2026-10-11): nothing adopted

Before writing the release helpers, GitHub was searched through the API for ready-made deployment
tooling: systemd units for `uvicorn`, health-check scripts, and atomic "deploy a built SPA through a
symlink with rollback" scripts. Filters were applied server-side (stars, licence presence, language).

**Result: nothing usable.** The only near-match was a personal server-template repository with zero
stars and **no licence file at all**, which the standing rules exclude. Consequences, recorded honestly:

* The four helpers in `deploy/` and `frontend/scripts/check-bundle.mjs` are first-party, small and
  auditable. No third-party deployment code, unit file or script was copied, so **no new attribution or
  licence obligation was created** by this round;
* There is no upstream project to track, patch or upgrade for these files;
* The search is recorded here as the evidence for the "search before adopting" rule, not as a claim that
  no such project exists anywhere.

**Rules applied to every future dependency:** read the licence file (not the badge); check transitive
dependencies and their licences; record the version; add notices; run the dependency scan in CI; and
record the decision here with evidence.

### 4.2 Cross-platform shell discovery for the deployment tests (2026-10-21): nothing adopted

The deployment artifacts under `deploy/` are Linux programs, and `backend/tests/test_deploy_artifacts.py`
executes them. A Windows developer has no `bash` on `PATH` (Git for Windows installs one that is not
added to `PATH`), so the suite needs to find a POSIX shell, translate paths for it and supply the
`python3` the health check requires. Before writing that, the web (GitHub, PyPI) was searched for a
maintained, permissively licensed component that already does it.

| Candidate | Licence (verified) | Revision inspected | Decision |
|---|---|---|---|
| `sarugaku/shellingham` (PyPI `shellingham`) | **ISC** (PyPI metadata: "OSI Approved :: ISC License (ISCL)") | 1.5.4 (2023-10-24) | **Rejected — wrong job.** It detects the shell the *current process* is running in (the parent process on Windows), so it would report PowerShell or `cmd.exe`; it does not locate a Git for Windows installation. Adding a runtime dependency for a test-only concern, that would still have to be wrapped, was not justified |
| `CS-SI/pytest-executable` (PyPI `pytest-executable`) | **Apache-2.0** (PyPI metadata; `LICENSE.txt` referenced by the project) | 0.5.6 (2023-10-07) | Rejected on suitability: it runs a *runner script* through a configured interpreter and organises black-box test cases from YAML; it neither locates nor adapts a POSIX shell, its own classifiers list only Linux and macOS, and it would add a plugin to the whole suite for two test files |
| Ad-hoc recipes for Git Bash discovery (blog posts, Stack Overflow answers) | n/a | n/a | Rejected: not licensed source code, and the locations they hard-code are one machine's paths |

**Consequence, recorded honestly:** `backend/tests/deploy_shell.py` is **first-party** — a small module
that resolves the shell (`TALIMGO_TEST_BASH`, then the Git for Windows locations derived from
`ProgramFiles`/`LOCALAPPDATA`, then `PATH`), translates a Windows path into the MSYS2 form the
scripts require, and provides the `python3` the health check asks for. No third-party code was
copied, so **no new attribution or licence obligation** was created; `THIRD_PARTY_NOTICES.md` is
unchanged. The Linux CI run remains the authority on the scripts themselves.

### 4.3 Vitest 3 to 4, for two published advisories (2026-10-21): upgraded, nothing adopted

`npm audit` reported three advisories, all in the **development** dependency set, all reached
through one package: `vitest@3.2.7`.

| Advisory | Package | Severity | Route to TALIMGO |
|---|---|---|---|
| [GHSA-82fw-gwwq-j7x9](https://github.com/advisories/GHSA-82fw-gwwq-j7x9) — path traversal / arbitrary file read via a mocker redirect | `@vitest/mocker` 2.1.0 – 4.1.10 | moderate | `vitest@3.2.7` → `@vitest/mocker@3.2.7` |
| [GHSA-5gmw-xhrv-c9v3](https://github.com/advisories/GHSA-5gmw-xhrv-c9v3) and [GHSA-85c8-ppgw-ccpr](https://github.com/advisories/GHSA-85c8-ppgw-ccpr) — prototype pollution gadget leading to remote code execution | `tinypool` ≤ 2.1.1 | critical | `vitest@3.2.7` → `tinypool@1.1.1` |

CI's gate is `npm audit --omit=dev` (production dependencies only) and it was, and remains, **0
vulnerabilities**. These three never blocked a build. They were still fixed, because the
advisories are real, the packages are installed on every developer machine and on every CI
runner, and the fix is cheap. **No new package was adopted**: Vitest was already a recorded
dependency (MIT), so this is a version change, not a new third-party component, and
`THIRD_PARTY_NOTICES.md` needs no new entry.

**Why `4.1.12` and not what `npm audit fix --force` offers.** The forced fix installs
`vitest@5.0.5` — two major versions — and was **not** used. The evidence for the version chosen:

* `@vitest/mocker` is fixed from 4.1.11; `vitest@4.1.12` ships `@vitest/mocker@4.1.12`, outside the
  affected range.
* Vitest 4 **removed `tinypool` entirely** (the pool rewrite described in its migration guide),
  so the critical advisory's package is no longer in the tree at all — verified by `npm ls tinypool`,
  which now reports nothing.
* Vitest 5 changes behaviour that this suite would have to re-audit: `clearMocks` becomes `true` by
  default (it would change mock call counts between tests) and unawaited asynchronous assertions
  start failing. Vitest 4 introduces neither.
* The peer ranges are satisfied **without touching any other dependency**: `vite@6.4.4` satisfies
  `^6.0.0 || ^7.0.0 || ^8.0.0`, `@types/node@^22.5.0` satisfies `^20 || ^22 || >=24`, and `jsdom`
  is unconstrained.

**One source change was required, and it is recorded here because it is not obvious.** Vitest 4 no
longer augments Vite's `UserConfig` with the `test` property unless its types are referenced, so
`tsc --noEmit` failed with `TS2769: 'test' does not exist in type 'UserConfigExport'`. The fix in
`frontend/vite.config.ts` is a **types-only** reference:

```ts
/// <reference types="vitest/config" />
```

Importing `defineConfig` from `vitest/config` would also work, but it would make the production
build load the test runner at runtime. The reference costs nothing at runtime and keeps
`vite build` independent of `vitest`.

**Verified after the change:** `npm run typecheck` exit 0; `npm test -- --run` → 59 passed,
1 skipped (the pre-existing opt-in live-stack smoke test); `npm run build` exit 0;
`node scripts/check-bundle.mjs` exit 0; `npm ci` reproducible from the committed lockfile;
`npm audit` **0 vulnerabilities** (was 3); `node scripts/check-licences.mjs` → 184 packages inspected,
none blocked and none GPL. The dependency path changed as expected: `tinypool`, `vite-node`, `loupe`,
`tinyspy` and the `chai` internals were dropped, and `obug` and `@standard-schema/spec` were added.

**The licence gate could not be run on Windows until it was fixed.** `scripts/check-licences.mjs`
resolved the directory to inspect with `new URL("../node_modules/", import.meta.url).pathname`, which on
Windows yields `/C:/...` — a URL component, not a path any filesystem call can open. The read failed,
the failure was swallowed, and the script reported `no packages inspected — run npm install first` and
exited 1. The gate is therefore now run with `fileURLToPath` from `node:url`, and a directory it cannot
list is reported as an error instead of being skipped. `frontend/src/licence-check.test.ts` covers this.
The change is first-party and creates no attribution obligation.

---

## 5. Attribution obligations currently in force

- No third-party **source code** is vendored in this repository.
- Runtime dependencies keep their own licences and are listed in `THIRD_PARTY_NOTICES.md`.
- The design concepts credited in §1.5 are used with attribution in this document. No Braivo code,
  text, schema or test was copied. Braivo's own documentation states its architecture is AGPL-3.0-only;
  TALIMGO's independently written implementation of general patterns (evidence-as-truth, versioned
  single model, pure learning module) does not incorporate its expression.
