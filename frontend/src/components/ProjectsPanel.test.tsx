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

// Shapes mirror the real API contract (backend/app/schemas.py ProjectOut/ProjectSubmissionOut).
const PROJECT = {
  id: "py:project:wordcount",
  path_id: "python-foundations",
  objective_id: "py:project",
  objective_title: "Capstone project",
  title: "Word-frequency counter",
  brief_md: "Write and run a program.",
  rubric: [
    { id: "reads_safely", label: "File opened with with and UTF-8", required: true },
    { id: "tested", label: "Ran on two samples", required: false },
  ],
  min_artifact_chars: 200,
  min_reflection_chars: 40,
  est_minutes: 90,
  my_status: null,
  attempts: 0,
};

function submission(overrides: Record<string, unknown>) {
  return {
    id: "psb_1",
    project_id: PROJECT.id,
    objective_id: "py:project",
    goal_id: "gol_1",
    plan_item_id: "pli_9",
    status: "needs_work",
    met_criteria: [],
    missing_criteria: [],
    artifact_text: "",
    reflection_text: "",
    evidence_recorded: false,
    submitted_at: "2026-10-27T00:00:00Z",
    ...overrides,
  };
}

describe("ProjectsPanel", () => {
  it("walks list → submit → needs_work gaps → accepted, reporting evidence", async () => {
    get.mockImplementation((url: string) => {
      if (url === "/api/projects") return Promise.resolve([PROJECT]);
      if (url === `/api/projects/${PROJECT.id}`) return Promise.resolve(PROJECT);
      if (url.startsWith("/api/projects/submissions/mine")) return Promise.resolve([]);
      return Promise.reject(new Error(url));
    });
    post.mockResolvedValueOnce(
      submission({
        missing_criteria: ["reads_safely", "artifact:minimum_length"],
        artifact_text: "short",
      }),
    );
    post.mockResolvedValueOnce(
      submission({
        id: "psb_2",
        status: "accepted",
        met_criteria: ["reads_safely"],
        artifact_text: "y".repeat(400),
        evidence_recorded: true,
      }),
    );

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
