import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { translator } from "../lib/i18n";
import { ProjectsPanel } from "./ProjectsPanel";

const { get, post } = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));

vi.mock("../lib/api", () => ({
  api: { get, post },
  ApiError: class ApiError extends Error {},
}));

const t = translator("en");

const SUMMARY = {
  id: "py:project:wordcount",
  objective_id: "py:project",
  title: "Word-frequency counter",
  est_minutes: 90,
};
const DETAIL = {
  ...SUMMARY,
  brief_md: "Write and run a program.",
  rubric: [
    { id: "reads_safely", label: "File opened with with and UTF-8", required: true },
    { id: "tested", label: "Ran on two samples", required: false },
  ],
  min_artifact_chars: 200,
  min_reflection_chars: 40,
};

describe("ProjectsPanel", () => {
  it("walks list → submit → needs_work gaps → accepted, reporting evidence", async () => {
    get.mockImplementation((url: string) => {
      if (url === "/api/projects") return Promise.resolve([SUMMARY]);
      if (url === `/api/projects/${SUMMARY.id}`) return Promise.resolve(DETAIL);
      if (url === `/api/projects/${SUMMARY.id}/submissions`) return Promise.resolve([]);
      return Promise.reject(new Error(url));
    });
    post.mockResolvedValueOnce({
      id: "psb_1",
      project_id: SUMMARY.id,
      objective_id: "py:project",
      status: "needs_work",
      rubric_checks: {},
      missing: ["rubric:reads_safely", "artifact:minimum_length"],
      artifact_chars: 10,
      reflection_chars: 50,
      created_at: "2026-10-27T00:00:00Z",
    });
    post.mockResolvedValueOnce({
      id: "psb_2",
      project_id: SUMMARY.id,
      objective_id: "py:project",
      status: "accepted",
      rubric_checks: { reads_safely: true },
      missing: [],
      artifact_chars: 500,
      reflection_chars: 80,
      evidence_recorded: true,
      plan_item_completed: true,
      created_at: "2026-10-27T01:00:00Z",
    });

    const onAccepted = vi.fn();
    render(
      <ProjectsPanel t={t} goalId="gol_1" objectiveId={null} planItemId="pli_9" onAccepted={onAccepted} />,
    );
    await userEvent.click(await screen.findByRole("button", { name: /open project/i }));
    await screen.findByText("Write and run a program.");

    await userEvent.type(screen.getByLabelText(/your work/i), "short");
    await userEvent.type(screen.getByLabelText(/reflection/i), "x".repeat(50));
    await userEvent.click(screen.getByRole("button", { name: /submit for checking/i }));

    await screen.findAllByText(/needs work/i);
    // The unmet criterion appears in the "still to fix" list as well as on its checkbox.
    expect(screen.getAllByText("File opened with with and UTF-8")).toHaveLength(2);
    expect(onAccepted).not.toHaveBeenCalled();

    await userEvent.click(screen.getByLabelText(/file opened with with/i));
    await userEvent.type(screen.getByLabelText(/your work/i), "y".repeat(400));
    await userEvent.click(screen.getByRole("button", { name: /submit for checking/i }));

    await screen.findByText(/recorded as evidence/i);
    expect(onAccepted).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(post).toHaveBeenCalledTimes(2));
    expect(post.mock.calls[1][1]).toMatchObject({ plan_item_id: "pli_9", goal_id: "gol_1" });
  });
});
