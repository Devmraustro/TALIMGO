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

## Baseline HTTP hardening (implemented, 2026-10-11)

The API is JSON; the interface is a separate static app. The policy in `backend/app/http_hardening.py`
is therefore deliberately small, and each header answers a named risk rather than a checklist box.

| Header | Value | Risk it addresses | Notes and limits |
|---|---|---|---|
| `X-Content-Type-Options` | `nosniff` | A browser re-interpreting a JSON error body as HTML/script (content-type confusion) | Applies to every response, including errors and preflights |
| `Referrer-Policy` | `no-referrer` | TALIMGO URLs leaking to third-party sites through the `Referer` header | — |
| `X-Frame-Options` + CSP `frame-ancestors` | `DENY` / `'none'` | Clickjacking of any HTML this service might serve (currently only the development docs UI) | Belt and braces: older browsers read the header, modern ones the directive |
| `Content-Security-Policy` | `default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'; sandbox` | Any injected script/style/frame/plugin on an API response; also blocks `base`-tag and form hijacking | The development docs UI gets its own policy (Swagger UI loads a CDN bundle); production serves no HTML from this service at all |
| `Permissions-Policy` | 23 features set to `()` | Silent use of camera, microphone, geolocation, USB, payment, etc. by injected or future code | The list is explicit; enabling a feature requires a product decision and a code change |
| `Strict-Transport-Security` | `max-age=31536000` | Protocol downgrade and cookie theft on a later plain-HTTP request | **Only ever sent when the request arrived over HTTPS** (directly, or via `X-Forwarded-Proto` set by the proxy). `includeSubDomains`/`preload` are deliberately omitted — they need a domain inventory the owner has not provided |

Verified by `backend/tests/test_http_hardening.py` (12 tests) and the tripwire in
`tests/test_security_basics.py`: the baseline on success/error/preflight responses, frame-embedding
blocked twice over, the unused-feature list, HSTS only over HTTPS (and tolerating the shapes a proxy
sends), the docs policy staying separate from the API policy, and production serving no interactive
docs while keeping the policy.

**What this is not.** It is a header and behaviour checklist enforced by tests. No penetration test,
no TLS termination review, no browser-driven security testing and no review by a second human has been
performed. TLS configuration, certificate management, proxy hardening, header-stripping at the edge and
rate limiting upstream are deployment concerns documented in `docs/DEPLOYMENT.md`, not properties this
repository can demonstrate by itself. `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy` and
`Cross-Origin-Resource-Policy` were considered and are deliberately not set: the first two govern
documents (this service returns JSON) and the third restricts no-CORS embedding that the CORS check
already covers, while risking breakage of the legitimate cross-origin development frontend.

## Security review of session, request and resource handling (2026-10-11)

A code review of the areas the deployment depends on, with what was changed and what remains. This is
a review by the same engineer who wrote the code — it is **not** an independent audit, and it says
nothing about the reverse proxy, the host OS or the model runtime's own hardening.

| Area | What the code does | Change made | Residual risk / who owns it |
|---|---|---|---|
| Session cookies | `HttpOnly`, `SameSite=Lax`, `Path=/`, `Secure` when `TALIMGO_ENV=production` | Flags had no regression test; three tests added | A deployment that claims production but runs with `TALIMGO_ENV=development` loses `Secure`. Deployment-guide requirement |
| CSRF | No CSRF token. Relies on `SameSite=Lax` **and** a JSON-only API: mutating requests with a body must be `application/json`, which a cross-site HTML form cannot send | New request guard rejects form/text/multipart bodies with 415 (bodyless requests such as logout still work) | Browsers without SameSite support and same-site subdomain attackers are out of scope; a reverse proxy should also set `Origin` checks if it terminates auth |
| Login rate limiting | Failed attempts are rows in `login_attempts`, counted per email **and** per IP inside `TALIMGO_LOGIN_LOCKOUT_MINUTES`; works across workers because it is in the database | Unchanged (reviewed) | Lockout is also a denial-of-service lever against a known email; the proxy's `limit_req` is the cheaper first line. Owner: tune the thresholds |
| Model request limits | Daily allowance per learner, claimed **before** inference with a conditional `UPDATE ... WHERE count < limit` and a dedicated committed transaction (`reserve_usage_committed`) | The previous request-session claim rolled back on inference failures. It is now committed before the call, so failures consume the attempt without persisting an unvalidated exchange | A separate process-local generation gate bounds in-flight calls; it is not a distributed semaphore. Multi-worker deployments still need an aggregate cap at the model host/proxy |
| Local-model error responses | The adapter distinguishes *unreachable* (`LocalModelUnavailable` → 503) from *answered but unusable* (HTTP error status, non-JSON body, empty completion → `LocalModelResponseError`) | `LocalModelResponseError` had no handler and surfaced as an unhandled 500. It now maps to 502 with a fixed sentence; the 503 sentence was made equally generic. Upstream status lines, response bodies, the configured endpoint address and exception class names appear in the server log only — never in a learner-facing response | The log must be protected like any operational log: it holds no learner content, but it does hold the model runtime's error text and the endpoint address |
| Concurrent model generations | `TALIMGO_AI_MAX_CONCURRENT_REQUESTS` (default 1) slots per worker process, with a bounded wait (`TALIMGO_AI_QUEUE_TIMEOUT_SECONDS`, default 2 seconds) | Added a condition-based gate that releases in `finally`, returns 503 when saturated, and waits **before** claiming the daily allowance | Process-local only, not a distributed/global-across-hosts lock. PostgreSQL, multi-worker deployments and real model-host limits remain untested here; enforce the aggregate cap at the model host or proxy |
| Input bounds and write rate | Pydantic field limits, body-size guard (default 128 KiB, hard max 8 MiB), JSON-only mutations and `TALIMGO_WRITE_RATE_LIMIT_PER_MINUTE` (default 120 authenticated writes per learner per UTC minute) | Added an atomic conditional update on the learner row; the counter rolls over by minute and is committed in its own session, so concurrent workers share one per-learner allowance | Fixed-window boundary bursts are possible; login/registration still need edge limits, and this does not impose a per-IP or unauthenticated write limit. Keep reverse-proxy rate controls enabled |
| Output bounds | Model output capped by `TALIMGO_AI_MAX_OUTPUT_TOKENS` (default 800, max 8192) and validated against a strict JSON schema with citation allow-listing | Reviewed, unchanged | A local model can still emit long outputs up to the cap; the timeout bounds latency |
| Data growth | `login_attempts` and `sessions` pruned by `python -m app.maintenance` (30-day retention, dry-run available, audited); evidence and audit rows grow by design | Maintenance command documented and tested (retention boundaries, dry run, idempotency, audit rows untouched) | Evidence/audit retention is an owner policy decision — documented in `docs/DEPLOYMENT.md` §9, not silently applied |
| Learner data deletion | Deletes tutor messages/threads, practice+diagnostic history, plans, evidence, consent, sessions, profile and the user; anonymises audit rows; keeps curriculum | **Bug found and fixed**: four `select(Model.id)` comprehensions treated scalar ids as ORM rows, so deleting an account that had ever used the tutor raised `AttributeError` (HTTP 500) instead of deleting | Verified end to end against a learner with real history (`tests/test_account_lifecycle.py`); automated backups may still hold deleted data — backup retention is owner policy |
