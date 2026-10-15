# ADR 0003: Licence policy and reuse decisions for the named candidates

Status: **accepted** (2026-10-10). Full evidence: `docs/OPEN_SOURCE_REUSE_AUDIT.md`.

## Context

Three projects were named for evaluation before implementation, each with a different licence posture:
Braivo (AGPL-3.0-only, closest architectural match), LearnBuddy (MIT, security defects found on
inspection), FlameEducation (personal, non-commercial licence).

## Decision

1. **Braivo — study, do not copy.** Its AGPL network clause would require offering the complete
   corresponding source of any modified version served to users; TALIMGO has made no such decision and
   does not intend to publish its implementation. Independently, its AI module calls a hosted provider,
   which the local-only policy prohibits. Reading its documentation for design understanding is
   permitted and recorded with attribution; copying expression is not.
2. **LearnBuddy — do not copy.** MIT permits reuse, but the source contains a committed weak default JWT
   secret, wildcard CORS with credentials, import-time duplicate model loading, connection-per-query
   database access without pooling, and ad-hoc configuration. Its adaptive-engine idea is replaced by a
   deterministic, tested design.
3. **FlameEducation — exclude.** Its licence limits use to personal, non-commercial purposes; TALIMGO is
   intended to be commercial. No code may be copied or adapted.
4. **General policy for every future dependency:** permissive licences (MIT/BSD/Apache/ISC/OFL) allowed
   with notices; GPL requires written legal review; AGPL requires an explicit, documented owner decision
   about source-offer obligations; non-commercial and unlicensed code is excluded. Read the licence file,
   not the badge. Record version, licence and decision in the audit; add notices.
5. **No vendoring.** Dependencies are consumed as pinned packages.

## Consequences

- TALIMGO implements its own learning engine and AI layer rather than adopting either candidate.
- The design credit to Braivo is recorded in `THIRD_PARTY_NOTICES.md` §6 to avoid any ambiguity about
  provenance.
- The AI-tooling ecosystem must be reviewed carefully: projects whose purpose is routing to hosted
  providers are excluded even when permissively licensed.
