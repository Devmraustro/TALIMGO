# ADR 0002: Local, self-hosted AI only — no hosted providers

Status: **accepted** (2026-10-10). Binding beyond this repository: restated in `AGENTS.md` §2.

## Context

The implementation directive forbids hosted generative-AI providers. Independent evidence gathered
during the audit supports the rule on product and legal grounds:

- The closest comparable open-source project calls a hosted provider by default
  (`apps/server/ai/model.ts` posts to `https://api.anthropic.com/v1/messages`), which demonstrates how
  easily a cloud dependency becomes structural.
- The target markets have data-protection regimes with transfer conditions (Algeria's Law 18-07,
  Morocco's Law 09-08; master reference §11.3.3, §22.4), so a design with no cross-border AI transfer
  is materially simpler to defend.
- Hosted per-token pricing converts success into variable cost, and provider deprecations can break a
  product mid-term.

## Decision

1. All generative inference runs on TALIMGO-controlled infrastructure using locally hosted,
   open-weight models, reached over HTTP on a loopback or private address.
2. Two local dialects are supported by the adapter: Ollama `/api/chat` (development) and an
   OpenAI-compatible `/v1/chat/completions` (vLLM, llama.cpp server) for production. The wire format is
   irrelevant to the guarantee; the **endpoint policy** is what enforces it.
3. `assert_local_endpoint()` runs at configuration time and before every request. A non-local host
   raises `NonLocalEndpointError`; with `TALIMGO_AI_STRICT=1` (default) the application refuses to
   start rather than degrade into an external call.
4. No provider SDKs, no provider API keys, no gateway services, no embedding/speech APIs for learner
   content. Third-party AI-tooling projects that exist to route to hosted providers are excluded
   (recorded in the reuse audit).
5. Unavailability yields an explicit `503` and a clear learner-facing message. There is no fallback path
   in the code, and no configuration option can create one.
6. Learner content is never logged and never leaves TALIMGO infrastructure. Runtime telemetry is
   disabled where configurable.
7. AI output is a proposal: it is schema-validated, claim-filtered, and never writes mastery state.

## Consequences

- We accept lower raw capability than the largest hosted models and must **measure** Arabic quality
  rather than assume it.
- The team owns capacity planning, model updates and evaluation (see `docs/LOCAL_AI_ARCHITECTURE.md`).
- Tests must prove the guarantee: configuration rejection, single-endpoint calls, explicit failure on
  unavailability, and a repository scan for forbidden hosts/SDKs.
- Any future fine-tuning decision requires a separate ADR covering data rights, licence, evaluation and
  compute. We do not claim to have trained a foundation model.
