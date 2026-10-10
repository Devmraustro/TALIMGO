import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { DashboardPanel } from "./DashboardPanel";
import type { Dashboard } from "../lib/api";
import { translator } from "../lib/i18n";

const t = translator("en");
const tAr = translator("ar");

const dashboard: Dashboard = {
  goal: {
    id: "gol_1",
    path_id: "python-foundations",
    statement: "I want to write small Python tools",
    motivation: "",
    target_date: null,
    weekly_minutes: 240,
    status: "active",
    created_at: "2026-01-01T00:00:00Z",
  },
  next_action: {
    kind: "practice",
    title: "Making decisions",
    objective_id: "py:conditionals",
    lesson_id: "py:conditionals:lesson",
    plan_item_id: "pit_1",
    est_minutes: 15,
    rationale: "It is the next unfinished step in your plan.",
    evidence_basis: "No evidence recorded for this objective yet.",
  },
  mastery_summary: { unseen: 0, acquiring: 2, retaining: 1, needs_review: 1, recorded: 3 },
  recent_evidence: [
    {
      objective_id: "py:values",
      objective_title: "Variables, values and types",
      outcome: "success",
      assisted: false,
      kind: "practice",
      occurred_at: "2026-01-02T10:00:00Z",
    },
  ],
  blockers: [],
};

describe("DashboardPanel", () => {
  it("shows exactly one action, with its reason and evidence", () => {
    render(<DashboardPanel t={t} data={dashboard} onPrimaryAction={() => {}} />);

    expect(screen.getByText("It is the next unfinished step in your plan.")).toBeInTheDocument();
    expect(screen.getByText("No evidence recorded for this objective yet.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /start practising/i })).toBeInTheDocument();
  });

  it("does not offer a button when there is nothing to do", () => {
    const idle: Dashboard = {
      ...dashboard,
      next_action: { ...dashboard.next_action, kind: "idle", title: "Your plan is complete" },
    };
    render(<DashboardPanel t={t} data={idle} onPrimaryAction={() => {}} />);
    expect(screen.getByText("Your plan is complete")).toBeInTheDocument();
    expect(screen.queryByRole("button")).toBeNull();
  });

  it("calls the primary action when the learner starts", async () => {
    const onPrimaryAction = vi.fn();
    render(<DashboardPanel t={t} data={dashboard} onPrimaryAction={onPrimaryAction} />);
    await userEvent.click(screen.getByRole("button", { name: /start practising/i }));
    expect(onPrimaryAction).toHaveBeenCalledOnce();
  });

  it("renders the same structure in Arabic", () => {
    render(<DashboardPanel t={tAr} data={dashboard} onPrimaryAction={() => {}} />);
    expect(screen.getByRole("heading", { name: "التقدّم والإتقان" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ابدأ التدريب" })).toBeInTheDocument();
  });
});
