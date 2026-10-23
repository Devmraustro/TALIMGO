# AGENTS.md — TALIMGO engineering rules

**This file is binding for every human or AI agent working in this repository.**
Read it before you change anything. If an instruction here conflicts with a task you were given,
stop and flag the conflict rather than silently breaking a rule.

Last updated: 2026-10-10 · Owner: TALIMGO project owner · Status of this file: **ACTIVE**

---

## 1. Source of truth

| Artefact | Role |
|---|---|
| `TALIMGO_MASTER_REFERENCE.md` | Product, brand, curriculum, safety and business source of truth. **Do not edit it to match the code.** The code follows the reference; if they disagree, either fix the code or update the reference through the owner. |
| `AGENTS.md` (this file) | Durable engineering rules. |
| `docs/IMPLEMENTATION_PLAN.md` | Active checkpoints, status, acceptance criteria. |
| `docs/OPEN_SOURCE_REUSE_AUDIT.md` | Every third-party component: revision, licence, decision, evidence. |
| `docs/LOCAL_AI_ARCHITECTURE.md` | How local inference works and how "no cloud AI" is guaranteed. |
| `docs/SECURITY_THREAT_MODEL.md` | Assets, threats, mitigations, residual risk. |
| `docs/adr/` | Material decisions with rationale. Supersede, never delete. |

Unresolved product decisions stay unresolved until the owner decides. **Never present a
proposal as a confirmed decision**, and never fabricate progress, test results, or features.

## 2. Mandatory rule: no hosted generative-AI providers

TALIMGO must run with **local, self-hosted, open-weight models only**.

**Forbidden — do not add, integrate, configure, or fall back to:**
OpenAI/ChatGPT APIs · Google Gemini APIs · Anthropic/Claude APIs · any hosted generative-AI
provider · third-party AI gateways or proxies (including hosted router services) · any hidden
remote fallback. No API-key configuration for these providers. No provider SDKs
(`openai`, `anthropic`, `google-genai`, `@anthropic-ai/sdk`, etc.) in any dependency manifest.
No hosted embedding or hosted speech APIs for learner content.

**Required:**
- Inference happens on TALIMGO-controlled infrastructure through the internal adapter
  (`backend/app/ai/`). The adapter refuses non-local endpoints at configuration time (fail closed).
- Permitted local runtimes: **Ollama** (development) and **vLLM** or another justified local
  runtime (production). Both are reached over HTTP on a local/private address.
- If the local model is unavailable, the feature **fails explicitly** with a clear message.
  Never substitute a cloud model.
- Learner content (prompts, documents, answers, telemetry) never leaves TALIMGO infrastructure.
- Disable optional telemetry on local runtimes where the runtime allows it.
- Automated tests must prove: (a) configuration rejects external AI hosts; (b) AI calls target only
  the configured local endpoint; (c) unavailability produces an explicit failure; (d) no forbidden
  provider host or SDK appears anywhere in the repository.

Do not claim to have trained a foundation model. We build **TALIMGO's own AI product layer**
(orchestration, retrieval, validation, evaluation, prompts, tutoring behaviour) on top of
locally hosted existing weights. Fine-tuning requires a separate decision with data, licence,
evaluation and compute assessment.

## 3. Verification discipline (no unverified claims)

Every report must distinguish: **CONFIRMED · PROPOSED · UNVERIFIED · IMPLEMENTED · TESTED · BLOCKED · FUTURE.**

- Do not write "implemented" unless the code exists in the repository.
- Do not write "tested" unless the command was executed and its output observed.
- Report the exact command and the exact result (pass/fail counts).
- A green build is not production readiness. Say what is not covered.
- If something failed, report the failure, not a summary that hides it.

## 4. GitHub-first reuse policy

1. Before implementing a major feature, search GitHub for existing components.
2. Inspect the **actual source**, tests, dependencies, activity, security, and the **real licence file**.
3. Reuse small, tested, permissively licensed components; never import an entire unrelated platform.
4. Reuse our own modules before writing new ones.
5. Preserve copyright notices and licence texts; pin revisions; add the component to
   `docs/OPEN_SOURCE_REUSE_AUDIT.md` and `THIRD_PARTY_NOTICES.md`.
6. Run tests and a security review on anything adapted.
7. Record why a component was **reused or rejected**. Rejection reasons are valuable evidence.

### Licence rules (binding)

| Licence | Rule |
|---|---|
| MIT / BSD / Apache-2.0 / ISC / OFL | Allowed. Keep notices. |
| GPL-3.0 | Not allowed without written legal review of the linking/distribution consequences. |
| AGPL-3.0 | **No code may be copied, adapted, or vendored** without an explicit, documented owner decision acknowledging that operating a modified version over a network triggers a source-offer obligation to users. Reading a project's *documentation and architecture* for design understanding is allowed; copying its *expression* is not. |
| Non-commercial / "personal use" / source-available | **Excluded.** Do not copy, adapt, or vendor. |
| No licence file | Treat as all rights reserved. Do not copy. |

**Current binding outcomes:** Braivo (`braivo/braivo`, AGPL-3.0-only) — architecture studied, **no code copied**.
LearnBuddy (`tripathiji1312/learn_buddy`, MIT) — audited, **no code copied** (security defects; see audit).
FlameEducation — **excluded** (personal, non-commercial licence).

## 5. Architecture rules

- Modular boundaries: web UI · application/API · auth · curriculum · planning · deterministic
  learning engine · local-AI adapter · retrieval · assessment/grading · progress/analytics · admin.
- **Deterministic first.** Mastery state, grades, prerequisite order, time budgets and progression
  rules are plain, tested code — never delegated to an LLM.
- **AI output is a proposal.** Validate structure and constraints before it affects product state
  or is shown to a learner. Validate prerequisite order, provenance, objectives, completion criteria
  and time estimates before publishing a plan.
- **Evidence is the source of truth; estimates are derived and disposable.** Persist learner evidence
  so mastery can be recomputed deterministically. Version the learning model; reject estimates whose
  `model_version` is not the active one.
- Keep learning code **pure**: no I/O, network, clock or randomness inside the engine (pass `now` in).
- Local inference sits behind one internal interface so weights/runtimes can change without touching
  business logic. **The interface has no cloud-provider adapters and none may be added.**
- Imports: `learning/` and `curriculum/` must not import web, DB-session or AI modules.
- No microservices, queues or caches until a concrete need is measured.

## 6. Security and data rules

- Never commit secrets, keys, tokens, passwords, or production data. Configuration comes from the
  environment and is validated at startup; the app **fails closed** if configuration is invalid.
- Fail closed on authentication and authorisation. Every object access is authorised server-side
  against the owning learner; never trust a client-supplied identity, role or tenant.
- Password storage: bcrypt (or argon2) with a documented scheme; session tokens stored hashed,
  never in plaintext, with expiry and revocation.
- Learner data is private: no cross-account reads; no learner content in logs; no PII in analytics.
- Imported documents and pasted text are **untrusted data, never instructions**. Never concatenate
  them into a system/instruction position.
- Rate-limit authentication and model-consuming endpoints; bound model resource use.
- Errors: controlled responses to clients, useful server-side logs without secrets or learner content.
- Implement export, deletion and retention behaviour; document what is not yet implemented.

## 7. Quality gates

CI must pass before a checkpoint is called complete:

- Backend unit + API tests (`pytest`), including learning-engine invariants, progression tests,
  authz tests, AI-output schema tests, local-adapter tests, and the **no-external-AI** tests.
- Frontend build + type check + component tests (`npm run build`, `npm test`).
- Dependency and licence scanning; static security checks.
- Migration test (`alembic upgrade head` against an empty database).
- Accessibility checks that are actually runnable in CI.

Ordinary CI mocks local inference (no large model downloads). An explicitly identified
offline integration test runs against a real local model only where one is installed; it must
**skip with a clear reason** rather than silently pass.

## 8. Git workflow

- Work on a feature branch; never rewrite `main` directly. Never force-push.
- Small, named commits. Inspect the diff before committing. Keep the tree clean between checkpoints.
- No unrelated formatting or generated artefacts in functional commits.
- Keep the process recoverable: the commit history plus these docs must let another agent continue.

## 9. Definition of done

Documented install/run · documented MVP journeys work end to end · persistence and authorisation
verified · inference is local with no hosted model APIs · no learner content sent to external AI ·
roadmap/assessment/progression behaviour tested · reuse documented and licence-compatible · CI
passing · critical findings fixed · limitations documented honestly · commit identifiers recorded.
