import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

describe("App shell", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the sign-in form when there is no session", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url === "/api/auth/me") {
          return Promise.resolve(jsonResponse({ detail: "Authentication required." }, 401));
        }
        return Promise.resolve(jsonResponse({}, 404));
      }),
    );

    render(<App />);

    expect(await screen.findByRole("heading", { name: "Create your account" })).toBeInTheDocument();
    expect(screen.getByLabelText("Email")).toBeInTheDocument();
    expect(screen.getByText(/Your study content is never sent/i)).toBeInTheDocument();
  });

  it("renders the learner's next action for an authenticated session", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url === "/api/auth/me") {
          return Promise.resolve(
            jsonResponse({
              user: {
                id: "usr_1",
                email: "learner@example.com",
                display_name: "Learner",
                role: "learner",
                created_at: "2026-01-01T00:00:00Z",
              },
              profile: {
                locale: "en",
                weekly_minutes: 240,
                availability_days: [],
                target_date: null,
                low_bandwidth: false,
                reduced_motion: false,
                onboarding_completed_at: null,
              },
              consents: [],
            }),
          );
        }
        if (url === "/api/dashboard") {
          return Promise.resolve(
            jsonResponse({
              goal: {
                id: "gol_1",
                path_id: "python-foundations",
                statement: "Learn Python",
                motivation: "",
                target_date: null,
                weekly_minutes: 240,
                status: "active",
                created_at: "2026-01-01T00:00:00Z",
              },
              next_action: {
                kind: "learn",
                title: "Variables, values and types",
                objective_id: "py:values",
                lesson_id: "py:values:lesson",
                plan_item_id: null,
                est_minutes: 25,
                rationale: "It is the next unfinished step in your plan.",
                evidence_basis: "No evidence recorded for this objective yet.",
              },
              mastery_summary: { acquiring: 0, retaining: 0, needs_review: 0, recorded: 0 },
              recent_evidence: [],
              blockers: [],
            }),
          );
        }
        if (url === "/api/plans/active") return Promise.resolve(jsonResponse(null));
        if (url === "/api/health/ai") {
          return Promise.resolve(jsonResponse({ ai_enabled: false, policy: "local-only" }));
        }
        return Promise.resolve(jsonResponse({}, 404));
      }),
    );

    render(<App />);

    expect(await screen.findByText("Variables, values and types")).toBeInTheDocument();
    expect(screen.getByText("It is the next unfinished step in your plan.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /start practising/i })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: "Sections" })).toBeInTheDocument();
  });

  it("asks for a goal when the learner has none", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url === "/api/auth/me") {
          return Promise.resolve(
            jsonResponse({
              user: {
                id: "usr_2",
                email: "learner2@example.com",
                display_name: "Learner",
                role: "learner",
                created_at: "2026-01-01T00:00:00Z",
              },
              profile: {
                locale: "ar",
                weekly_minutes: 180,
                availability_days: [],
                target_date: null,
                low_bandwidth: false,
                reduced_motion: false,
                onboarding_completed_at: null,
              },
              consents: [],
            }),
          );
        }
        if (url === "/api/dashboard") {
          return Promise.resolve(
            jsonResponse({
              goal: null,
              next_action: {
                kind: "idle",
                title: "Define your learning goal",
                objective_id: null,
                lesson_id: null,
                plan_item_id: null,
                est_minutes: 3,
                rationale: "TALIMGO plans from a goal.",
                evidence_basis: "No active goal on this account.",
              },
              mastery_summary: {},
              recent_evidence: [],
              blockers: [],
            }),
          );
        }
        if (url === "/api/plans/active") return Promise.resolve(jsonResponse(null));
        if (url === "/api/curriculum/paths") {
          return Promise.resolve(
            jsonResponse([
              {
                id: "python-foundations",
                title_en: "Python programming foundations",
                title_ar: "أساسيات البرمجة بلغة بايثون",
                summary_en: "Start from zero.",
                summary_ar: "ابدأ من الصفر.",
                objective_count: 12,
                estimated_hours: 8.5,
              },
            ]),
          );
        }
        if (url === "/api/health/ai") {
          return Promise.resolve(jsonResponse({ ai_enabled: false, policy: "local-only" }));
        }
        return Promise.resolve(jsonResponse({}, 404));
      }),
    );

    render(<App />);

    expect(await screen.findByRole("heading", { name: "ما الذي تريد أن تكون قادراً عليه؟" })).toBeInTheDocument();
    await waitFor(() => {
      expect(document.documentElement.dir).toBe("rtl");
    });
    expect(document.documentElement.lang).toBe("ar");
    expect(screen.getByRole("navigation", { name: "الأقسام" })).toBeInTheDocument();
  });

  it("returns the learner to sign-in when the session expires mid-use", async () => {
    // The learner is signed in and has no goal yet, so the API answers 401 to the dashboard refresh
    // that follows setting a goal: the classic expired-cookie case.
    let dashboardCalls = 0;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        if (url === "/api/auth/me") {
          return Promise.resolve(
            jsonResponse({
              user: {
                id: "usr_9",
                email: "expiring@example.com",
                display_name: "Learner",
                role: "learner",
                created_at: "2026-01-01T00:00:00Z",
              },
              profile: {
                locale: "en",
                weekly_minutes: 180,
                availability_days: [],
                target_date: null,
                low_bandwidth: false,
                reduced_motion: false,
                onboarding_completed_at: null,
              },
              consents: [],
            }),
          );
        }
        if (url === "/api/dashboard") {
          dashboardCalls += 1;
          if (dashboardCalls > 1) {
            return Promise.resolve(jsonResponse({ detail: "Authentication required." }, 401));
          }
          return Promise.resolve(
            jsonResponse({
              goal: null,
              next_action: {
                kind: "idle",
                title: "Define your learning goal",
                objective_id: null,
                lesson_id: null,
                plan_item_id: null,
                est_minutes: 3,
                rationale: "TALIMGO plans from a goal.",
                evidence_basis: "No active goal on this account.",
              },
              mastery_summary: {},
              recent_evidence: [],
              blockers: [],
            }),
          );
        }
        if (url === "/api/plans/active") return Promise.resolve(jsonResponse(null));
        if (url === "/api/curriculum/paths") {
          return Promise.resolve(
            jsonResponse([
              {
                id: "python-foundations",
                title_en: "Python programming foundations",
                title_ar: "أساسيات البرمجة بلغة بايثون",
                summary_en: "Start from zero.",
                summary_ar: "ابدأ من الصفر.",
                objective_count: 12,
                estimated_hours: 8.5,
              },
            ]),
          );
        }
        if (url === "/api/goals") {
          return Promise.resolve(
            jsonResponse(
              {
                id: "gol_9",
                path_id: "python-foundations",
                statement: "Learn Python",
                motivation: "",
                target_date: null,
                weekly_minutes: 180,
                status: "active",
                created_at: "2026-01-01T00:00:00Z",
              },
              201,
            ),
          );
        }
        if (url === "/api/health/ai") {
          return Promise.resolve(jsonResponse({ ai_enabled: false, policy: "local-only" }));
        }
        return Promise.resolve(jsonResponse({}, 404));
      }),
    );

    render(<App />);

    // The goal form is up, which means the dashboard read succeeded and the session listener is live.
    const statement = await screen.findByLabelText(/your goal, in your own words/i);
    await waitFor(() =>
      expect((screen.getByLabelText(/learning path/i) as HTMLSelectElement).value).toBe(
        "python-foundations",
      ),
    );
    fireEvent.change(statement, { target: { value: "Learn Python" } });
    fireEvent.click(screen.getByRole("button", { name: /set this goal/i }));

    expect(await screen.findByText(/your session has ended/i)).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Create your account" })).toBeInTheDocument();
    expect(screen.queryByText(/your goal, in your own words/i)).not.toBeInTheDocument();
  });

  it("starts independent startup reads concurrently after session resolution", async () => {
    const calls: string[] = [];
    let resolveDashboard!: (response: Response) => void;
    let rejectSchedule!: (reason?: unknown) => void;
    let resolvePlan!: (response: Response) => void;
    let resolveAi!: (response: Response) => void;
    const dashboardPending = new Promise<Response>((resolve) => {
      resolveDashboard = resolve;
    });
    const schedulePending = new Promise<Response>((_resolve, reject) => {
      rejectSchedule = reject;
    });
    const planPending = new Promise<Response>((resolve) => {
      resolvePlan = resolve;
    });
    const aiPending = new Promise<Response>((resolve) => {
      resolveAi = resolve;
    });

    vi.stubGlobal(
      "fetch",
      vi.fn().mockImplementation((url: string) => {
        calls.push(url);
        if (url === "/api/auth/me") {
          return Promise.resolve(
            jsonResponse({
              user: {
                id: "usr_parallel",
                email: "parallel@example.com",
                display_name: "Learner",
                role: "learner",
                created_at: "2026-01-01T00:00:00Z",
              },
              profile: {
                locale: "en",
                weekly_minutes: 180,
                availability_days: [],
                target_date: null,
                low_bandwidth: false,
                reduced_motion: false,
                onboarding_completed_at: null,
              },
              consents: [],
            }),
          );
        }
        if (url === "/api/dashboard") return dashboardPending;
        if (url === "/api/plans/active/schedule") return schedulePending;
        if (url === "/api/plans/active") return planPending;
        if (url === "/api/health/ai") return aiPending;
        return Promise.resolve(jsonResponse({}, 404));
      }),
    );

    render(<App />);

    await waitFor(() => {
      expect(calls).toContain("/api/dashboard");
      expect(calls).toContain("/api/plans/active/schedule");
      expect(calls).toContain("/api/plans/active");
      expect(calls).toContain("/api/health/ai");
    });

    // The main dashboard should render even while schedule, plan and AI-health remain pending.
    resolveDashboard(
      jsonResponse({
        goal: null,
        next_action: {
          kind: "idle",
          title: "Define your learning goal",
          objective_id: null,
          lesson_id: null,
          plan_item_id: null,
          est_minutes: 3,
          rationale: "TALIMGO plans from a goal.",
          evidence_basis: "No active goal on this account.",
        },
        mastery_summary: {},
        recent_evidence: [],
        blockers: [],
      }),
    );
    expect(await screen.findByRole("heading", { name: "What do you want to be able to do?" })).toBeInTheDocument();

    // Complete all pending requests to avoid leaking work beyond this test.
    resolvePlan(jsonResponse(null));
    resolveAi(jsonResponse({ ai_enabled: false, policy: "local-only" }));
    rejectSchedule(new Error("No active schedule"));
  });

});
