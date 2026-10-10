# Local AI architecture

**Policy (binding, from `AGENTS.md` §2):** TALIMGO runs generative AI **only** on
TALIMGO-controlled infrastructure using locally hosted, open-weight models. No hosted provider API,
no third-party AI gateway, no hidden remote fallback. If the local model is unavailable, the feature
fails explicitly.

Status: **IMPLEMENTED (adapter, prompts, validation, tests)** · real-weights integration: **BLOCKED in
this sandbox** (no runtime installed) · model-quality evaluation: **FUTURE**.

---

## 1. Why local only (product and legal reasoning)

1. **Learner data.** Prompts, lesson context, learner questions, answers and uploaded documents are the
   most sensitive material the product holds. Keeping them on our own infrastructure removes an entire
   class of data-processing risk and vendor-term risk.
2. **Regional legal context.** Algeria's Law 18-07 requires prior declaration/authorisation and
   conditions cross-border transfers; Morocco's Law 09-08 requires CNDP authorisation for transfers
   abroad. A design with no cross-border AI transfer is materially simpler to defend in the target
   markets (see the master reference §11.3.3, §22.4).
3. **Cost predictability.** Per-token pricing for hosted models is a variable cost that scales with
   success; owned inference is a fixed-cost asset with a known ceiling.
4. **Continuity.** A hosted provider can change pricing, deprecate a model, or refuse a category of
   content mid-term. Local weights cannot be withdrawn.
5. **Differentiation.** TALIMGO's value is the surrounding system (curriculum graph, evidence,
   validation, tutoring behaviour). Owning the model layer makes that system reproducible and auditable.

**Honest trade-offs accepted:** lower raw capability than the largest hosted models; real operational
work (GPU/CPU capacity, model updates, evaluation); slower cold starts on CPU-only hosts; a genuine
quality risk in Arabic that must be measured, not assumed.

---

## 2. Shape of the subsystem

```
Leaner UI / API
      │
      ▼
app/routers/tutor.py ──▶ app/ai/tutor.py ─────────────▶ app/curriculum (retrieval, read-only)
                               │                              ▲
                               │  builds grounded prompt      │ objective/lesson context by ID
                               ▼                              │
                        app/ai/adapter.py ──▶ HTTP ──▶ LOCAL runtime (Ollama / vLLM / llama.cpp)
                               │                             127.0.0.1 or a private address only
                               ▼
                        app/ai/schemas.py  (Pydantic validation — invalid output is rejected)
                               │
                               ▼
                     validated reply + provenance  →  returned to the learner, never written to mastery
```

Design rules:

- **One internal interface.** `LocalModelClient.generate(...)` is the only way the application talks to a
  model. Business logic never imports a provider SDK, and there are no provider adapters in the codebase.
  Swapping weights or runtimes is a configuration change.
- **Fail closed.** `assert_local_endpoint()` runs at configuration time and again before every request.
  A non-local host raises `NonLocalEndpointError`; the app refuses to start with `TALIMGO_AI_STRICT=1`
  (default) rather than silently allowing an external call.
- **Explicit unavailability.** `LocalModelUnavailable` → HTTP 503 with a plain message telling the
  learner that tutoring is offline while the rest of the lesson still works. **No fallback of any kind.**
- **Structured output.** Tutor replies are validated against a Pydantic schema (JSON mode). Anything
  that fails validation is rejected and logged; it is never shown as authoritative.
- **Grounding.** The prompt contains only the retrieved curriculum context for the current objective or
  lesson. The model is instructed to answer within that context, to flag uncertainty, and to refuse
  claims that violate TALIMGO's prohibited-claims list (master reference §11.1.1). Citations are only
  accepted when they resolve to material already in the context.
- **Untrusted input handling.** Learner messages, pasted text and future uploaded documents are placed
  in an explicitly delimited *data* section. They are never concatenated into the instruction section.
  Prompt-injection attempts are logged as security events.
- **No learner content elsewhere.** Request logging stores metadata (model, duration, token counts,
  objective ID) and never the prompt or the learner's text. Optional telemetry on the runtime is
  disabled where the runtime allows it.

---

## 3. Runtime options and the selection criteria

| Runtime | Role | Notes |
|---|---|---|
| **Ollama** | Development default | Simple local HTTP API (`POST /api/chat`), easy model pulls, runs on CPU, single-user friendly, no external calls once weights are present |
| **vLLM** | Production candidate | High-throughput GPU serving with an OpenAI-compatible local endpoint (`/v1/chat/completions`); supports continuous batching for concurrency |
| llama.cpp server | Fallback/edge option | Very small footprint, CPU-friendly, GGUF quantisation |
| Hosted provider APIs | **Prohibited** | Not supported by the adapter, and rejected by configuration validation and by the repository scan test |

The adapter speaks two local dialects so the runtime can change without touching application code:
`ollama` (`/api/chat`) and `openai_compatible` (`/v1/chat/completions`, for vLLM/llama.cpp). Both are
**local protocols**; the second is a wire format, not a hosted service. The endpoint policy — not the
dialect — is what enforces the guarantee.

---

## 4. Model selection: required comparison before weights are chosen

Weights are **not** selected in this repository. Selection is a documented, evidence-based step with the
following criteria and measured results. Until it is completed, the default configuration points at a
placeholder model name and the tutor reports itself as unconfigured rather than guessing.

### 4.1 Criteria

| # | Criterion | How it will be measured |
|---|---|---|
| 1 | Arabic, French and English quality | 150-item human-graded set per language (explanation, correction, tone); native-speaker raters |
| 2 | Instruction following and **structured JSON** reliability | % of schema-valid responses over 200 prompts, including adversarial ones |
| 3 | Educational tutoring quality | Rubric-scored samples: hint ladder compliance, level appropriateness, refusal quality, absence of invented citations |
| 4 | Coding, mathematics and reasoning for the first launch path | Executable code benchmarks where possible (answers checked by running them) and maths items with verified keys |
| 5 | Quantised inference requirements | Measured VRAM/RAM at Q4_K_M / Q5 / Q8; tokens/second on the reference host; cold-start time |
| 6 | Throughput and concurrency | Tokens/second at 1, 4 and 16 concurrent requests on the reference host |
| 7 | **Weight licence and redistribution** | Licence file read in full; commercial use, redistribution and derivative-weight terms recorded; “open weights” ≠ “permissive” |
| 8 | Fully offline operation after install | Air-gapped run with network egress blocked; no runtime call to any external host |

### 4.2 Candidate families to evaluate (unranked, no selection made)

Instruction-tuned, openly licensed small/medium models in the 7–30 B range are the realistic operating
band for a small team; the evaluation list should include, at minimum, one strong multilingual family
with documented Arabic support, one coding-strong family, and one small model (≈3 B) as the
cheap-routing candidate. **Names are deliberately omitted here:** listing concrete model tags without
the licence and benchmark evidence would create exactly the false confidence this document forbids.
The evaluation record will name the weights, their licence, and the measured results.

### 4.3 Reference hosting plan (PROPOSED)

| Environment | Hardware assumption | Runtime | Model size |
|---|---|---|---|
| Development | CPU-only workstation, 16 GB RAM | Ollama, single request at a time | 3–8 B quantised |
| Staging | 1 GPU (≥16 GB VRAM) | vLLM | 8–14 B quantised |
| Production (initial) | 1 GPU per node, horizontal scale-out | vLLM with prefix caching | 8–14 B quantised; escalation path to a larger model if evaluation demands it |

Cost control: request-level token ceilings, per-learner daily caps, prompt-size discipline (retrieve the
smallest sufficient context), response caching keyed by (objective, hint level, question hash), and
graceful degradation that keeps lesson/practice paths working with no model at all.

---

## 5. Data flow, and what never leaves

| Data | Where it goes | Stored? |
|---|---|---|
| Learner message to the tutor | Local runtime over loopback/private network | Not stored beyond the session unless the learner saves it (FUTURE); metadata logged |
| Curriculum context sent to the model | Local runtime only | Not stored |
| Model output | Validated in-process, shown to the learner | Not stored as mastery evidence — AI output never sets mastery state |
| Uploaded documents (FUTURE) | Local extraction only | Storage policy defined before the feature ships |
| Telemetry | Not sent externally; runtime telemetry disabled where configurable | — |

**Guarantees enforced by tests** (see `backend/tests/test_ai_local_only.py`):

1. External endpoints (`api.openai.com`, `generativelanguage.googleapis.com`, `api.anthropic.com`, any
   non-local host) raise at configuration time.
2. A tutor request issues exactly one HTTP call, to the configured local endpoint.
3. With no local model answering, the API returns 503 and no other host is contacted.
4. A repository-wide scan fails if any forbidden provider host or SDK import appears in source or
   manifests.

---

## 6. Failure behaviour

| Failure | Behaviour |
|---|---|
| Local runtime not running / unreachable | HTTP 503, message: tutoring is temporarily unavailable; lessons, practice, review and progress keep working |
| Model returns invalid JSON or fails schema validation | Rejected, logged as a quality event, learner sees a graceful “couldn’t produce a usable answer” message; **nothing is stored** |
| Model returns a prohibited claim (job/income/mastery guarantee) | Blocked by the claim filter, replaced with a safe restatement, logged |
| Model is slow | Per-request timeout with a clear message; learning paths never block on the tutor |
| Suspected prompt injection | Instruction-following attempt refused, logged with the offending section hash (not the content) |

There is **no third option where the request silently goes somewhere else** — that is the whole point
of the design.
