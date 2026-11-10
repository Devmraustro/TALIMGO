# D.12 — Option A (FastAPI same-origin static serving) — technical review (2026-11-10)

**Review scope:** the change proposed in `docs/D11_DEPLOYMENT_ARCHITECTURE.md` §2 (Option A):
the FastAPI process serves the built `frontend/dist` on the same origin as `/api/*`, with SPA
fallback, API taking precedence. **D.12 implements nothing** — the brief permits implementation
only if the review proves a safe, isolated design *and* the owner wants it now; the owner has not
approved code changes in this phase, and the stable checkpoint must remain reviewable. This
document is the review the owner asked for; the implementation sketch is §7.

## 1. Requirements restated (from the D.12 brief + repository contract)

R1 API routes take precedence over any frontend fallback. R2 SPA fallback serves the interface
for non-API GET routes. R3 SameSite=Lax session cookie behavior unchanged. R4 CSP
`connect-src 'self'` remains valid. R5 Static layer must never expose `.env`, source code,
secrets or uploads. R6 Missing assets must produce an explicit error, not silently serve
`index.html`. R7 Cache headers distinguish immutable `/assets/*` from `index.html`. R8 Path
traversal prevented. R9 Authentication/authorization behavior unchanged. R10 CSP, cookies, CSRF,
CORS not weakened. R11 Rollback is trivial (flag off → current behavior byte-identical).

## 2. Current state (verified)

- Backend serves **no static files**; `create_app()` registers routers only; JSON 404s.
- Frontend build → `frontend/dist/index.html` + fingerprinted `assets/`; no `VITE_*` URLs;
  client is same-origin `/api/...` with `credentials: "same-origin"` (`frontend/src/lib/api.ts`).
- Security headers set on **every** response via `apply_hardening_headers`
  (HSTS/X-Content-Type-Options/X-Frame-Options/Referrer-Policy/CSP with `connect-src 'self'`),
  outermost middleware → static responses would inherit them automatically.
- `vercel.json` headers mirror the same policy for the static-only preview deployment.
- CI `proxy-tls-smoke` asserts edge behavior incl. HSTS and rate-limit passthrough.

## 3. Proposed design (precise)

1. New optional setting `TALIMGO_STATIC_DIR: Path | None = None` (default None → **the feature is
   inert**, current behavior unchanged).
2. On startup, if set: validate the directory exists and contains `index.html` and `assets/`;
   fail closed (raise) otherwise — a misconfigured deployment must not half-serve.
3. Mount `StaticFiles` at `/assets` (and only `/assets`) with
   `Cache-Control: public, max-age=31536000, immutable` for fingerprinted files.
4. Serve `index.html` at `/` (`Cache-Control: no-store`).
5. SPA fallback: GET/HEAD requests **not** matching `/api/*` and **not** matching a file under
   the dist root return `index.html` (`no-store`). Non-`/api` **missing file** under `/assets/*`
   returns **404** (never index.html) — satisfies R6. All error bodies stay JSON or plain text,
   never HTML for `/api/*` (API 404s already JSON via exception handlers).
6. Path handling: resolve the request path against the dist root with `Path.resolve()` and verify
   containment (`is_relative_to`), reject `..`/encoded traversal (`%2e%2e`) and dotfiles
   (`.env`, `.git`) with 404/404-equivalent — StaticFiles already normalizes, the containment
   check is defense-in-depth and is unit-tested.
7. `index.html` and SPA fallback are read once per request (small file) or cached in-process;
   `If-None-Match`/`ETag` handled by StaticFiles for `/assets`.
8. No change to auth, cookies, CORS, CSRF, CSP values — `connect-src 'self'` is *strengthened*
   coverage-wise because interface and API share the origin (exactly what the client assumes).

## 4. Threat model review

| Threat | Mitigation | Residual |
|---|---|---|
| Static layer leaks `.env`/source/secrets | Serve ONLY `TALIMGO_STATIC_DIR` (the dist folder, which contains built assets); never the repo root; dotfiles refused; dist contains no secrets (bundle check proves no hosts; no `VITE_*` exist) | LOW |
| Path traversal (`/../config.py`, `%2e%2e`) | StaticFiles normalization + containment check + tests for `/assets/../`, `/%2e%2e%2f`, double-encoding | LOW |
| SPA fallback masks missing assets | Explicit rule: `/assets/*` and any path with a file extension that does not resolve → 404; fallback only for extensionless/GET navigation routes | LOW |
| Cached `index.html` pins old releases | `Cache-Control: no-store` on `/` and fallback responses | LOW |
| Stale fingerprinted assets after deploy | new hashes per build; `immutable` is safe only for `/assets/*` — never for `index.html` | LOW |
| CSP breakage | none — policy is `'self'`; no external origins introduced; keep `style-src 'unsafe-inline'` as already deployed | LOW |
| API precedence regression | mount order: API routers registered first; fallback is a pure GET/HEAD catch-all that only sees what routers didn't match; test proves `/api/health` and a deliberately unmapped `/api/x` return JSON | LOW |
| Range/HEAD handling | StaticFiles implements both; keep defaults; `GET` fallback returns 200 with index.html | LOW |
| Storage/DoS via static | small dist (~300 KB); Basic DoS surface unchanged; alwaysdata edge applies its own limits | LOW |
| Open redirect via fallback | fallback never redirects; always serves index.html for navigation GETs | LOW |
| Session fixation/cookie issues | unchanged; Secure+HttpOnly+SameSite=Lax as today | LOW |

## 5. Failure modes and explicit errors

- `TALIMGO_STATIC_DIR` set but missing/invalid → **startup RuntimeError** (fail closed), never a
  silently degraded site.
- `/api/*` unmatched → JSON 404 (existing). `/assets/typo.js` → **404 plain text**, never HTML.
- HEAD on `/` → headers only. POST to any frontend route → **405** (fallback is GET/HEAD only).
- Oversized/wrong-method requests → existing request guards (128 KiB cap, JSON-only for API
  mutations) unchanged.

## 6. Test plan (required before any merge — not run here; change not made)

Backend unit tests (to add under `tests/test_static_serving.py`): (1) static disabled by default
and behavior identical to today; (2) `/` returns index.html `no-store`; (3) fingerprinted asset
returns immutable cache headers; (4) SPA fallback serves index.html for `/goals/plan`;
(5) `/assets/definitely-missing.js` → 404, not index.html; (6) `/api/health` still 200 JSON and
precedes any fallback; unmapped `/api/nope` → JSON 404; (7) traversal suite (`/../`, `%2e%2e`,
double-encoded, backslashes) → 404 and never file contents; (8) dotfile (`/.env`,
`/assets/.git/config`) → 404; (9) auth flow through the mounted app unchanged (register/login via
same TestClient); (10) HEAD/405 behavior. Frontend: no changes expected; `check-bundle.mjs`
continues to pass. CI: existing `proxy-tls-smoke` gains no new dependency; add the new test file
to the backend job (it discovers `tests/` automatically).

## 7. Implementation sketch (for owner review; NOT applied in D.12)

- `app/config.py`: add `static_dir: Path | None = None` (env `TALIMGO_STATIC_DIR`), validated at
  startup when set (must contain `index.html`).
- `app/main.py`: in `create_app()`, after router registration and before the SPA fallback
  middleware, mount `/assets` → `StaticFiles(...)`; add an `@app.exception_handler(404)`-adjacent
  lightweight fallback route `GET /{full_path:path}` guarded by method and path rules returning
  FileResponse(index.html, headers={"Cache-Control": "no-store"}).
- New `app/staticfiles.py` (~60 lines) with containment check helper used by tests.
- Docs: README/DEPLOYMENT note; no secret or env file is added to the tree.
- Estimated: ~120 lines incl. tests; isolated behind the setting; zero dependency additions.

## 8. Verdict

**Option A is technically sound, isolated, and low-risk as specified. It remains NOT IMPLEMENTED
and NOT MERGED.** Merge requires: owner approval of the §7 sketch; the §6 test suite green in CI;
CSP/cookie regression review (none expected); a staging deploy proving browser-level behavior
(fresh login through the same-origin path, deep-link refresh, 404 for a missing asset, CSP report
absence of violations). Until those exist, the correct artifact is this review plus the current
checkpoint, and the Vercel/AlwaysData topology decision remains open (D.9 blocker).
