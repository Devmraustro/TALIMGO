# Zero-cost local AI setup (TALIMGO)

Status: proposed operating guide; not proof that a real model has been installed or benchmarked.
Repository policy: local/self-hosted open-weight models only. No hosted generative-AI APIs or hidden fallback.

## What “free” can and cannot mean

- No paid AI API subscription: achievable by running open-weight model weights on hardware controlled by the project owner.
- No paid hosting bill: achievable for local development and demos on the owner's own computer.
- A public 24/7 service for many students with zero cost and guaranteed uptime: cannot be promised. It needs a device that stays online, electricity, internet, capacity, security, and a reachable service. Free cloud tiers have limits and may sleep or change.
- Hosting the website on a free tier does not make inference free or available. The local model must be reachable by the backend, and the repository's security rules prohibit hidden hosted-AI fallbacks.

## Recommended phases

### Phase 1 — local demo (no hosting subscription)

1. Use a computer you control; keep the model and app on the same machine.
2. Install Python and Node.js versions supported by the repo; follow README.md.
3. Create the backend virtual environment, install dependencies, run migrations and tests.
4. Install Ollama locally, then choose a small open-weight instruct model only after checking its current licence, memory needs, language support, and model card. Do not assume the example qwen2.5:7b-instruct is suitable for every computer.
5. Configure the adapter to use a loopback endpoint such as http://127.0.0.1:11434; set the model name to the model actually installed.
6. Start backend and frontend locally. Test the tutor with Arabic, Algerian Arabic, French, and English examples.
7. If the model is unavailable, show the repository's explicit offline response. Do not route learner text to a cloud provider.

### Phase 2 — verify quality and resource limits

- Record CPU/RAM, model version and licence, first-token latency, full response latency, concurrent requests, and memory usage.
- Test grounding against known lesson material, false citations, Arabic grammar, French terminology, prompt injection in uploaded files, and malformed model output.
- Keep daily quotas and concurrency limits enabled so the computer cannot be overwhelmed.
- Never describe the model as production-ready until real-weight tests have been run and results recorded.

### Phase 3 — private pilot

- Keep the pilot private while the model runs on the owner's computer.
- Do not expose Ollama or the model port directly to the public internet.
- Do not configure router port forwarding for the model API.
- If remote testers are necessary, use a properly authenticated private access layer and restrict users; review TLS, authentication, rate limits, abuse handling, and data retention first.
- A free tunnel is not a substitute for access control and can expose personal infrastructure if misconfigured.

### Phase 4 — public service

Before opening public access, decide who operates the machine, how it stays online, the maximum concurrent users, backup/restore, monitoring, abuse response, and expected latency. Measure actual hardware capacity first. If the machine cannot support the expected load, pause public AI access or limit it to scheduled demos; never silently switch to a hosted provider.

## Existing repository facts to preserve

- AGENTS.md is binding: local/self-hosted open-weight models only.
- docs/LOCAL_AI_ARCHITECTURE.md says the adapter and tests are implemented, but real-weight integration is blocked until a local runtime is configured; model-quality evaluation remains future work.
- docs/IMPLEMENTATION_PLAN.md distinguishes mock-endpoint tests from real model verification.
- The current README states no model weights are bundled and tutoring needs a runtime installed by the operator.
- Do not commit model weights, credentials, personal learner data, or production secrets to Git.

## Definition of ready for a private demo

- [ ] App starts with no paid AI account and no provider API key.
- [ ] python scripts/check_no_external_ai.py passes.
- [ ] Backend unit/API tests and frontend typecheck/build pass.
- [ ] A real local model is installed and configured; model-specific tests are executed and results recorded.
- [ ] External AI endpoints are rejected and local-model outage yields an explicit error.
- [ ] No model port is publicly exposed; authenticated app access and per-user limits are verified.
- [ ] The operator explains that demo uptime depends on their computer and internet connection.

## User-facing copy

“يعمل المساعد الذكي على نموذج محلي تابع للمنصة. أثناء التجربة، قد يتوقف إذا كان جهاز التشغيل غير متصل أو غير متاح. لا نرسل أسئلتك إلى مزود ذكاء اصطناعي خارجي. بعض الميزات قد تكون محدودة حسب قدرة الجهاز.”

This guide does not claim that BaridPay, public hosting, or real-model quality has been implemented or verified.
