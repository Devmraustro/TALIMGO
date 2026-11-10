# D.12 — Security posture and release-gate status (2026-11-10)

Status labels: **VERIFIED** · **PARTIALLY VERIFIED** · **BLOCKED** · **NOT EXECUTED**.
Nothing in this document relaxes an invariant to obtain a pass.

## 1. Security invariants (re-verified in D.12)

| Invariant | Evidence | Status |
|---|---|---|
| Local-AI-only; no hosted provider | `check_no_external_ai.py` passed (92 files, 7 URL literals) | VERIFIED (static/config) |
| AI explicitly disabled end-to-end | `TALIMGO_AI_ENABLED=false` in all D.12 runs; `/api/health/ai` reports disabled state; no runtime installed | VERIFIED |
| Fail-closed production config | Preflight exit 0 (correct) / 1 (SQLite refused); boot against unreachable DB exits 3 pre-serving; missing schema → RuntimeError | VERIFIED |
| Docs/OpenAPI off in production | code path + CI expectation unchanged | VERIFIED |
| Auth/authz/session regression matrix | 14 + 23 + 6 = 43 passed (D.12 run) | VERIFIED |
| Cross-user isolation | `test_authz_cross_user.py` 23 passed (D.12 run) | VERIFIED |
| Full backend suite | 502 passed / 4 skipped (D.12 run; 3 Windows shims + 1 local_model) | VERIFIED |
| Frontend suite / build / types | 76 passed / 1 skipped; tsc clean; build ✓ (291.86 kB, gzip 88.45 kB) | VERIFIED |
| Dependency & licence hygiene | pip-audit: no known vulnerabilities; npm audit: 0; licences 73 py / 185 npm — **both pass** (73 because the D.12 venv gained `pgserver`, `fasteners`, `psutil` — dev-only validation tooling, recorded; project dependencies unchanged) | VERIFIED |
| Same-origin cookie topology / CSP | client `/api`-relative; `connect-src 'self'`; build-time bundle check passed; no `VITE_*` hosts | VERIFIED |
| Rate limits & request guards | suite green incl. `test_write_rate_limits.py` (tracked, untouched) | VERIFIED |
| Secrets in tree (incl. new D.12 docs + SQL) | re-scanned (keys/tokens/JWTs/Neon hosts/high-entropy) — clean; SQL carries no credentials; `talimgo_runtime` appears only as the deferred-rotation name | VERIFIED |
| Isolation TALIMGO ↔ AUSTRO | binding policy recorded (`docs/D12_OWNERSHIP_AND_ISOLATION.md`); zero AUSTRO references in code/config/CI; **infrastructure isolation NOT VERIFIED** (no AlwaysData scope exists yet) | PARTIALLY VERIFIED |
| `test_write_rate_limits.py` preserved | tracked, unmodified | VERIFIED |
| Git usage | no commit/push/merge/amend in D.12; `0583a0a` intact | VERIFIED |

## 2. Release gates (D.11 G1–G14, re-baselined for D.12)

| # | Gate | D.11 | D.12 status | Evidence / remaining |
|---|---|---|---|---|
| G1 | Repository baseline documented | VERIFIED | **VERIFIED** | D11/D12 baseline docs; `0583a0a` intact |
| G2 | Dependency/build hygiene | VERIFIED | **VERIFIED** | D.12 battery re-run (§3) |
| G3 | AlwaysData capabilities understood | PARTIALLY VERIFIED | **PARTIALLY VERIFIED** | Docs verified; account unknown (no access) |
| G4 | Dedicated TALIMGO-only scope + DB + login | BLOCKED | **BLOCKED** | Requirement R-1 in D12_ALWAYSDATA_ACCOUNT_VERIFICATION.md §2; owner must prove scope |
| G5 | PostgreSQL staging migrated & checked | BLOCKED | **PARTIALLY VERIFIED** — procedure VERIFIED on disposable PG 16.2 (empty→head, drift clean, least-privilege); **AlwaysData staging NOT EXECUTED** | D12_STAGING_PROVISIONING_AND_PERMISSION_MATRIX.md §3–5 |
| G6 | Backup created + restore rehearsed | BLOCKED | **PARTIALLY VERIFIED** — rehearsed twice on disposable PG 16.2 (repo script PASS; custom dump/restore, parity 7/7, `alembic check` clean, app-role smoke PASS, scratch dropped; ~0.05 s dump / ~0.15–0.19 s restore); **AlwaysData rehearsal BLOCKED** | D12_STAGING_BACKUP_RESTORE_VERIFICATION.md |
| G7 | Same-origin topology proven on account | BLOCKED | **BLOCKED** — Option A fully reviewed (D12_OPTION_A_STATIC_SERVING_REVIEW.md); not implemented; account unverified | review doc |
| G8 | TLS + docs 404 + cookies live-tested | BLOCKED | **BLOCKED** — needs deployed staging | — |
| G9 | Runtime credential rotation + least-priv runtime role | BLOCKED — DEFERRED BY OWNER | **BLOCKED — still DEFERRED BY OWNER**; never accessed/rotated | D.10/D.11/D.12 unchanged |
| G10 | Local AI provisioned & evaluated, or off | BLOCKED/DISABLED | **DISABLED (correct)** — Public Cloud cannot host compliant inference; keep `TALIMGO_AI_ENABLED=false` | D11_DEPLOYMENT_ARCHITECTURE.md §7 |
| G11 | Vercel vs AlwaysData decision | BLOCKED | **BLOCKED** — Vercel untouched (read-only checks only) | — |
| G12 | Monitoring wired | BLOCKED | **BLOCKED** | needs deployed host |
| G13 | Rollback rehearsal | BLOCKED | **BLOCKED** (procedure documented; needs staging) | DEPLOYMENT.md §10/11 (systemd path) |
| G14 | Post-deploy verifier | BLOCKED | **BLOCKED** | needs deployed host + owner authorisation (creates disposable account) |

**No gate moved to VERIFIED by assertion; G5/G6 moved only on the strength of real executed
evidence — and only for the disposable local scope, never for AlwaysData.**

## 3. D.12 test & gate battery — exact results (2026-11-10, this tree)

| Check | Command | Result |
|---|---|---|
| Backend suite | `pytest --tb=no -q` (isolated SQLite) | exit 0 — **502 passed, 4 skipped** |
| Auth regression | `pytest tests/test_auth_regression.py` | **14 passed** |
| Cross-user isolation | `pytest tests/test_authz_cross_user.py` | **23 passed** |
| Config fail-closed | `pytest tests/test_config_isolation.py` | **6 passed** |
| Ruff lint / format | `ruff check app tests scripts` / `ruff format --check` | All checks passed / 114 files |
| Bandit | `bandit -q -r app` | clean (exit 0) |
| Local-only-AI | `check_no_external_ai.py` | passed (92 files) |
| Licences (py) | `check_licences.py` | passed (73; +3 dev tools, noted) |
| pip-audit | `pip-audit` | no known vulnerabilities |
| Alembic (empty isolated SQLite) | `upgrade head` + `check` | clean / "No new upgrade operations detected." |
| Production preflight | correct env / SQLite | exit 0 / exit 1 |
| Disposable PG 16.2 battery (D12) | provision → migrate → curriculum → app-role DML/DDL matrix → cross-DB denial → smoke → maintenance dry-run → dump/restore ×2 → parity → teardown | all PASS (details in §1–§3 of the staging/backup docs) |
| Frontend suite | `vitest run` | **76 passed / 1 skipped** |
| Type check | `tsc --noEmit` | clean |
| Build | `npm run build` | ✓ 1.34 s |
| Bundle gate / licences / audit | `check-bundle.mjs` / `check-licences.mjs` / `npm audit --omit=dev` | pass / 185 pkgs / 0 vulns |

## 4. Security findings (D.12)

1. **Isolation policy gap closed at the document level** (binding decision + matrix), and
   **open at the infrastructure level** (G4) — by design of the authorization boundary; the
   owner's proof-of-scope checklist is the closing action.
2. **Restore path needed a post-restore grants step** — without it, `--no-owner --no-acl`
   restores leave the app role locked out (found in rehearsal; fixed via
   `deploy/staging/post_restore_grants.sql`). This is exactly the class of issue staging exists
   to catch before production.
3. **CI has never run `0583a0a`** (branch unpushed) — first push triggers the full 7-job CI;
   treat any red as a release stop.
4. **Dev-venv tooling drift**: `pgserver` (+ deps) installed for D.12 validation — not a project
   dependency; recorded; licence check covers it (73 pkgs, passing).
5. **Dangling blobs** (3, unchanged by D.12): stale intermediates, unreferenced, never part of a
   commit — benign; no history rewrite permitted.
6. No new code paths, no new dependencies in the product, no CSP/cookie/CORS/auth changes.

## 5. What D.12 refuses to certify

Production readiness of this branch; existence of any AlwaysData staging; any restore executed on
AlwaysData or production; AI availability; safe deployment of Option A (unreviewed merge);
isolation of the AUSTRO-candidate account; rotation of `talimgo_runtime`.
