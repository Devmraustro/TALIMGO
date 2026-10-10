# Security threat model

Status: **initial, pre-MVP.** Written before the first release so that mitigations are designed in
rather than retrofitted. Every mitigation marked `IMPLEMENTED` has code in this repository; everything
else is honest about being absent. Nothing here is a compliance certification.

Last reviewed: 2026-10-10.

---

## 1. Assets

| Asset | Why it matters | Where it lives |
|---|---|---|
| Learner credentials (password verifiers, session tokens) | Account takeover | `users`, `sessions` tables (SQLite/PostgreSQL) |
| Learner evidence (answers, attempts, mastery estimates) | The product's core record; sensitive personal data | `learner_evidence`, `mastery_estimates` |
| Learner profile and preferences (locale, accessibility flags, availability) | Personal data; inference about the person | `profiles` |
| Consent records | Legal proof | `consent_records` |
| Curriculum content and answer keys | Intellectual property + assessment integrity | `objectives`, `items` (keys never returned to clients before submission) |
| Local model runtime and weights | Infrastructure; a compromise enables prompt/data exfiltration | The host running Ollama/vLLM |
| Configuration and secrets (session secret, DB URL) | Full compromise if leaked | Environment only, never committed |

## 2. Actors

| Actor | Motivation |
|---|---|
| Opportunistic attacker | Credential stuffing, scraping, defacement |
| Curious authenticated learner | Read another learner's data; see answer keys |
| Malicious learner input | Prompt injection to make the tutor misbehave or leak context |
| Insider/operator error | Misconfiguration, leaking learner content into logs |
| Automated bot | Registration spam, resource exhaustion of the local model |
| Third-party supply chain | Malicious or vulnerable dependency |

## 3. Threats and mitigations

| # | Threat | Likelihood | Impact | Mitigation | Status |
|---|---|---|---|---|---|
| T1 | Credential stuffing / brute force on login | High | High | bcrypt (cost 12) with SHA-256 pre-hash; per-IP and per-account login attempt limiting with lockout window; generic error messages; constant-shape responses | IMPLEMENTED |
| T2 | Session theft / fixation | Medium | High | Server-side sessions: 256-bit random token, only its SHA-256 hash stored, expiry, revocation on logout, `HttpOnly` + `SameSite=Lax` cookie, `Secure` in production, token rotated on login | IMPLEMENTED |
| T3 | Plaintext or weakly stored secrets | Medium | High | No secrets in the repository (`.gitignore` + review); config validated at startup; startup fails on missing/weak session secret outside development | IMPLEMENTED |
| T4 | Horizontal privilege escalation (read/modify another learner's data) | Medium | High | Every query is scoped by the authenticated learner ID resolved server-side from the session; an explicit cross-account negative test exists; client-supplied IDs are never trusted | IMPLEMENTED |
| T5 | Answer-key disclosure before submission | Medium | Medium | Keys are excluded from API response schemas (`ItemPublic` has no key field); a test asserts the key never appears in diagnostic/practice payloads | IMPLEMENTED |
| T6 | Prompt injection through learner input or (future) documents | High | Medium | Untrusted text is placed in a delimited data section, never in the instruction position; the model is instructed to treat it as data; suspicious outputs are refused and logged; documents remain FUTURE | IMPLEMENTED (input), FUTURE (documents) |
| T7 | Data exfiltration through a hosted AI provider | Low (policy) | Critical | No provider SDKs, no provider endpoints; endpoint policy refuses non-local hosts; repository scan test; no fallback path exists in code | IMPLEMENTED |
| T8 | Local runtime reachable from outside the host | Medium | High | Deployment guidance binds the runtime to loopback or a private interface; the app treats the endpoint as trusted-local and never proxies arbitrary URLs; egress blocking recommended and documented | PARTIAL (deployment doc TODO) |
| T9 | Model resource exhaustion / DoS via expensive requests | Medium | Medium | Request timeouts, per-learner daily AI request cap, token ceilings, rate limiting; lesson/practice paths continue without the model | IMPLEMENTED (caps), PARTIAL (load tested?) |
| T10 | Learner content leaking into logs or error responses | Medium | High | Structured logging of metadata only (route, status, error class, duration); prompt/answer content is never logged; error responses are generic with a correlation reference | IMPLEMENTED |
| T11 | CSRF against state-changing endpoints | Medium | Medium | `SameSite=Lax` cookies; `Origin`/`Referer` validation on unsafe methods; JSON-only request bodies; no cookie-based cross-site embeds | IMPLEMENTED |
| T12 | SQL injection | Low | High | SQLAlchemy parameterised queries only; no string-built SQL; identifiers are ORM-mapped | IMPLEMENTED |
| T13 | XSS in learner-visible content | Medium | High | React escapes by default; no `dangerouslySetInnerHTML` in the codebase; a lint rule/test guards it | IMPLEMENTED |
| T14 | Dependency compromise / known CVE | Medium | High | Pinned versions; dependency + licence scan in CI; small dependency surface; no vendored code | PARTIAL |
| T15 | Mass registration / cost abuse | Medium | Medium | Rate limiting on registration; optional email verification before AI-consuming features; per-account AI caps | PARTIAL |
| T16 | Insufficient account recovery abuse | Medium | Medium | Not implemented yet: recovery flow requires a design that avoids account-takeover patterns (single-use, short-lived, hashed tokens) | FUTURE (explicitly absent; no recovery flow exists to abuse) |
| T17 | Unauthorised admin action | Low | High | Role stored server-side; every admin route depends on a role check; audit record for admin mutations | PARTIAL (roles + checks IMPLEMENTED; admin audit log TODO) |
| T18 | Learner requests deletion/export and the platform fails to comply | Medium | Medium | Export endpoint (JSON) implemented; deletion implemented with a documented retention exception list | IMPLEMENTED (export + delete), PARTIAL (backup purge policy) |
| T19 | Inference runtime compromised and used to read other learners' prompts | Low | High | Single-tenant deployment per instance; no cross-tenant prompt batching; runtime isolated from the application database | PARTIAL (architecture), FUTURE (hardening) |
| T20 | Log/error detail exposing internal structure | Medium | Low | Controlled error contract; internal details only in server logs | IMPLEMENTED |

## 4. Explicit non-goals for this phase

- No claims of SOC 2, ISO 27001, GDPR compliance certification, or any audit result. None has been performed.
- No multi-tenant isolation guarantees beyond per-learner scoping (institutional tenancy is FUTURE).
- No protection against a determined attacker with sustained local network access.
- No encrypted-at-rest claims: SQLite/PostgreSQL encryption depends entirely on the deployment.

## 5. Verification status (what was actually done)

| Check | Command / method | Result |
|---|---|---|
| Cross-account access test | `pytest -q -k authorization` | See the evidence line in the implementation plan |
| Answer-key non-disclosure test | `pytest -q -k item_key` | See above |
| External AI host rejected | `pytest -q -k non_local` | See above |
| No forbidden SDK/host in repository | `pytest -q -k forbidden` | See above |
| Dependency/licence scan | CI job | See CI run record |
| Static analysis | CI job (ruff + bandit where available) | See CI run record |
| Penetration test | — | **Not performed.** Required before any public launch (master reference §11.3.2) |
| Accessibility audit | Automated checks only | Manual audit and external review pending |

## 6. Residual risks we are knowingly carrying

1. **No external security review yet.** The threat model is a design document written by the same team that wrote the code.
2. **Local runtime hardening is a deployment responsibility** that is currently documented rather than automated. Shipping without an egress-blocked runtime fails the intent of the local-AI policy at the infrastructure layer, even if the code is correct.
3. **Session secret management in development** is convenience-first; production configuration requirements are documented but not enforced by tooling beyond a startup check.
4. **Model output quality is a safety surface**, not only a quality surface. Grounding and validation reduce but do not eliminate harmful or wrong answers; the human-reporting path and the evaluation harness are the mitigations, and the evaluation harness against real weights is not yet running.
