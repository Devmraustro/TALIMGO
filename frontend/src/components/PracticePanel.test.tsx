import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { PracticePanel } from "./PracticePanel";
import { translator } from "../lib/i18n";

const t = translator("en");

const post = vi.fn();
const get = vi.fn();

vi.mock("../lib/api", async () => {
  const actual = await vi.importActual<typeof import("../lib/api")>("../lib/api");
  return {
    ...actual,
    api: {
      get: (...args: unknown[]) => get(...args),
      post: (...args: unknown[]) => post(...args),
    },
  };
});

function session(overrides: Record<string, unknown> = {}) {
  return {
    session_id: "prs_1",
    objective_id: "py:values",
    status: "in_progress",
    item: null,
    answered: 0,
    target_items: 2,
    total: 2,
    feedback: null,
    ...overrides,
  };
}

describe("PracticePanel session lifecycle", () => {
  it("offers leaving — not completing — while questions remain", async () => {
    post.mockReset();
    post.mockResolvedValueOnce(
      session({
        item: {
          id: "py:values:q1",
          objective_id: "py:values",
          kind: "mcq_single",
          prompt: "What is the type of 3?",
          options: [
            { id: "a", text: "int" },
            { id: "b", text: "text" },
          ],
        },
        answered: 1,
      }),
    );
    post.mockResolvedValueOnce(session({ status: "abandoned" }));

    render(<PracticePanel t={t} objectiveId="py:values" lessonId={null} aiAvailable={false} onFinished={() => {}} />);
    await userEvent.click(screen.getByRole("button", { name: /start practising/i }));

    expect(screen.getByText(/answer every question/i)).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /finish session/i })).toBeNull();

    await userEvent.click(screen.getByRole("button", { name: /leave session/i }));

    await waitFor(() => expect(post).toHaveBeenCalledTimes(2));
    expect(post.mock.calls[0][0]).toBe("/api/practice/sessions");
    expect(post.mock.calls[1][0]).toBe("/api/practice/sessions/prs_1/abandon");
    expect(post.mock.calls.some((call) => String(call[0]).endsWith("/complete"))).toBe(false);
  });

  it("offers completion once every planned question is answered", async () => {
    post.mockReset();
    post.mockResolvedValueOnce(session({ answered: 2, item: null }));
    post.mockResolvedValueOnce(session({ status: "completed", answered: 2 }));

    const onFinished = vi.fn();
    render(
      <PracticePanel t={t} objectiveId="py:values" lessonId={null} aiAvailable={false} onFinished={onFinished} />,
    );
    await userEvent.click(screen.getByRole("button", { name: /start practising/i }));

    const complete = screen.getByRole("button", { name: /finish session/i });
    await userEvent.click(complete);

    await waitFor(() => expect(onFinished).toHaveBeenCalled());
    expect(post.mock.calls[1][0]).toBe("/api/practice/sessions/prs_1/complete");
  });

  it("threads the plan item, goal and mode into the session it creates", async () => {
    // Regression: the UI used to drop plan_item_id, so finishing a session from Today/Dashboard
    // never ticked the roadmap step off even though the API supported it.
    post.mockReset();
    post.mockResolvedValueOnce(session({ answered: 0, item: null }));
    render(
      <PracticePanel
        t={t}
        objectiveId="py:values"
        lessonId={null}
        planItemId="pli_42"
        goalId="gol_7"
        mode="review"
        aiAvailable={false}
        onFinished={() => {}}
      />,
    );
    await userEvent.click(screen.getByRole("button", { name: /start practising/i }));
    await waitFor(() => expect(post).toHaveBeenCalledTimes(1));
    expect(post.mock.calls[0][1]).toMatchObject({
      objective_id: "py:values",
      plan_item_id: "pli_42",
      goal_id: "gol_7",
      mode: "review",
    });
  });
});
