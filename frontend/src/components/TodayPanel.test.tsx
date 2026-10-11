import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { TodayPanel } from "./TodayPanel";
import type { Schedule, ScheduleItem } from "../lib/api";
import { translator } from "../lib/i18n";

const t = translator("en");
const tAr = translator("ar");

function item(overrides: Partial<ScheduleItem> = {}): ScheduleItem {
  return {
    id: "pit_1",
    order_index: 0,
    objective_id: "py:values",
    objective_title: "Variables, values and types",
    kind: "learn",
    lesson_id: "py:values:lesson",
    est_minutes: 25,
    status: "pending",
    scheduled_day: 0,
    scheduled_for: "2026-10-11",
    completed_at: null,
    rationale: "It is the next unfinished step in your plan.",
    ...overrides,
  };
}

const schedule: Schedule = {
  plan_id: "pln_1",
  version: 1,
  starts_on: "2026-10-11",
  daily_minutes: 70,
  total_estimated_minutes: 250,
  weeks: [{ week_number: 1, theme: "Variables", items: [item()] }],
  today: { date: "2026-10-11", items: [item()], minutes_planned: 25 },
  adherence: {
    counts: { on_time: 1, late: 0, overdue: 1, pending: 3 },
    minutes: { on_time: 25, late: 0, overdue: 30, actual: 18 },
    total_items: 5,
    completed_items: 1,
    adherence_percent: 20,
    behind_schedule: true,
  },
};

describe("TodayPanel", () => {
  it("lists today's missions with their planned minutes", () => {
    render(<TodayPanel t={t} schedule={schedule} onStart={() => {}} />);

    expect(screen.getByRole("heading", { name: "Today's missions" })).toBeInTheDocument();
    expect(screen.getByText("Variables, values and types")).toBeInTheDocument();
    expect(screen.getByText(/25 minutes/)).toBeInTheDocument();
    expect(screen.getByText(/1 mission\(s\) slipped/)).toBeInTheDocument();
  });

  it("starts the mission the learner picks", async () => {
    const onStart = vi.fn();
    render(<TodayPanel t={t} schedule={schedule} onStart={onStart} />);

    await userEvent.click(screen.getByRole("button", { name: /start/i }));
    expect(onStart).toHaveBeenCalledWith(expect.objectContaining({ id: "pit_1", objective_id: "py:values" }));
  });

  it("marks finished work instead of offering it again", () => {
    const done: Schedule = {
      ...schedule,
      today: { ...schedule.today, items: [item({ status: "completed" })] },
    };
    render(<TodayPanel t={t} schedule={done} onStart={() => {}} />);

    expect(screen.getByText("Done")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /start/i })).toBeNull();
  });

  it("says so plainly when nothing is scheduled", () => {
    const empty: Schedule = { ...schedule, today: { date: "2026-10-11", items: [], minutes_planned: 0 } };
    render(<TodayPanel t={t} schedule={empty} onStart={() => {}} />);
    expect(screen.getByText(/Nothing is scheduled for today/)).toBeInTheDocument();
  });

  it("renders in Arabic, right to left", () => {
    render(<TodayPanel t={tAr} schedule={schedule} onStart={() => {}} />);
    expect(screen.getByRole("heading", { name: "مهام اليوم" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "ابدأ" })).toBeInTheDocument();
  });
});
