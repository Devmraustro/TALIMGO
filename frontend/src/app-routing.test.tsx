import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "./App";

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json" },
  });
}

function stubSignedIn() {
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
              plan_item_id: "pli_1",
              rationale: "New objective",
              est_minutes: 20,
              evidence_basis: "No evidence yet",
            },
            mastery_summary: {},
            recent_evidence: [],
            blockers: [],
          }),
        );
      }
      if (url === "/api/practice/review-queue") {
        return Promise.resolve(jsonResponse({ items: [], due_count: 0 }));
      }
      if (url === "/api/projects") return Promise.resolve(jsonResponse([]));
      return Promise.resolve(jsonResponse({}, 404));
    }),
  );
}

describe("hash routing", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    window.location.hash = "";
  });

  it("opens the view named by the hash so destinations are deep-linkable", async () => {
    stubSignedIn();
    window.location.hash = "#/help";
    render(<App />);
    expect(
      await screen.findByRole("heading", { name: /help & how talimgo works/i }),
    ).toBeInTheDocument();
    expect(window.location.hash).toBe("#/help");
  });

  it("keeps the URL in sync when navigating and follows back/forward hash changes", async () => {
    stubSignedIn();
    render(<App />);
    const projects = await screen.findByRole("button", { name: "Projects" });
    fireEvent.click(projects);
    await waitFor(() => expect(window.location.hash).toBe("#/projects"));
    expect(await screen.findByRole("heading", { name: "Projects" })).toBeInTheDocument();

    window.location.hash = "#/help";
    fireEvent(window, new HashChangeEvent("hashchange"));
    expect(
      await screen.findByRole("heading", { name: /help & how talimgo works/i }),
    ).toBeInTheDocument();
  });
});
