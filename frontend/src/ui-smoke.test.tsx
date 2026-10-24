/**
 * Real-interface smoke test: drives the actual TALIMGO screens in jsdom against a **running** stack.
 *
 * The sandbox has no browser installed, so this is the closest available substitute for a manual
 * click-through: it renders the real components, types into the real forms and lets the real API
 * answer through the real dev-server proxy. It is skipped unless TALIMGO_UI_SMOKE=1, so ordinary CI
 * stays hermetic.
 *
 *   # terminal 1
 *   cd backend && TALIMGO_ENV=development TALIMGO_DATABASE_URL=sqlite:////tmp/smoke.db \
 *     TALIMGO_SESSION_SECRET=development-only-secret-not-for-production-use \
 *     .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
 *   # terminal 2
 *   cd frontend && npm run dev
 *   # terminal 3
 *   cd frontend && TALIMGO_UI_SMOKE=1 npx vitest run src/ui-smoke.test.tsx
 *
 * It proves: sign-up and goal creation work through the real forms, the dashboard then asks for the
 * starting check, and the interface never contacts anything except the local stack.
 */

import { beforeEach, expect, test, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { App } from "./App";

const ENABLED = process.env.TALIMGO_UI_SMOKE === "1";
const PROXY = process.env.TALIMGO_UI_BASE ?? "http://127.0.0.1:5173";
const PROXY_ORIGIN = new URL(PROXY).origin;
const requests: string[] = [];
let cookie = "";

function installFetch(): void {
  const real = globalThis.fetch;
  vi.stubGlobal("fetch", async (input: RequestInfo | URL, init?: RequestInit) => {
    const raw = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    const absolute = new URL(raw, PROXY);
    if (absolute.origin !== PROXY_ORIGIN) {
      throw new Error(`the interface must never contact ${absolute.origin}`);
    }
    const headers = new Headers(init?.headers);
    if (cookie) headers.set("cookie", cookie);
    const response = await real(new Request(absolute.href, { ...init, headers }));
    const set = response.headers.get("set-cookie");
    if (set) cookie = set.split(";")[0];
    requests.push(`${init?.method ?? "GET"} ${absolute.pathname}`);
    return response;
  });
}

beforeEach(() => {
  requests.length = 0;
  cookie = "";
  installFetch();
});

test.skipIf(!ENABLED)("a new learner registers, sets a goal and is asked to take the check", async () => {
  const email = `ui-${Date.now()}@example.com`;
  render(<App />);

  // 1. The real sign-up form, including the local-AI statement the learner must accept.
  expect(await screen.findByRole("heading", { name: /create your account/i })).toBeTruthy();
  expect(screen.getByText(/tutoring fails openly if the local model is unavailable/i)).toBeVisible();
  fireEvent.change(screen.getByLabelText("Email"), { target: { value: email } });
  fireEvent.change(screen.getByLabelText("Password"), { target: { value: "ui-smoke-password-123" } });
  fireEvent.change(screen.getByLabelText("What should we call you?"), { target: { value: "Smoke" } });
  fireEvent.click(screen.getByLabelText(/I accept the terms/i));
  fireEvent.click(screen.getByLabelText(/I agree that TALIMGO may process/i));
  fireEvent.click(screen.getByRole("button", { name: /create account/i }));

  // 2. Registration succeeds and the goal form appears (the real GoalPanel).
  expect(await screen.findByRole("heading", { name: /what do you want to be able to do/i })).toBeTruthy();
  fireEvent.change(screen.getByLabelText(/your goal, in your own words/i), {
    target: { value: "Automate my weekly reports with Python" },
  });
  // The submit button stays disabled until the learning paths have loaded from the API.
  await waitFor(() => {
    const select = screen.getByLabelText(/learning path/i) as HTMLSelectElement;
    expect(select.value).toBe("python-foundations");
  });
  fireEvent.click(screen.getByRole("button", { name: /set this goal/i }));

  // 3. The engine's next action is the starting check, so the diagnostic opens by itself and the
  //    first question is served by the real API.
  expect(
    await screen.findByRole("heading", { name: /starting check/i }, { timeout: 15000 }),
  ).toBeTruthy();
  expect(await screen.findByText(/question 1 of up to/i, {}, { timeout: 15000 })).toBeTruthy();
  expect(requests.some((entry) => /^POST \/api\/diagnostic\/goals\//.test(entry))).toBe(true);

  // 4. Everything the interface asked for stayed on the local stack.
  expect(requests.length).toBeGreaterThan(4);
  for (const entry of requests) expect(entry).toMatch(/^(GET|POST|PATCH|DELETE) \/api\//);
}, 30000);
