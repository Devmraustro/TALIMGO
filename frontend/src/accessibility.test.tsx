/**
 * Automated accessibility checks (jsdom). These run in CI with the rest of the component tests.
 *
 * They cover what can be checked without a browser: accessible names on form controls, one labelled
 * heading per region, error announcements, keyboard reachability of the primary action, the
 * reduced-motion and focus-visibility rules, and Arabic/RTL rendering with full string coverage.
 *
 * What they cannot check — and what therefore still needs a real browser and a screen reader — is
 * listed at the bottom of this file and in docs/IMPLEMENTATION_PLAN.md §7.12: focus *order* across a
 * full page, contrast ratios against the rendered theme, zoom/reflow at 200–400%, virtual-cursor
 * reading order for Arabic, and behaviour with a native screen reader (NVDA/VoiceOver/TalkBack).
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { AuthPanel } from "./components/AuthPanel";
import { DashboardPanel } from "./components/DashboardPanel";
import { TodayPanel } from "./components/TodayPanel";
import type { Dashboard, Schedule } from "./lib/api";
import { STRINGS, direction, translator } from "./lib/i18n";

const t = translator("en");
const tAr = translator("ar");
const styles = readFileSync(resolve(__dirname, "styles.css"), "utf-8");

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
  mastery_summary: { unseen: 3, acquiring: 1, retaining: 0, needs_review: 0 },
  recent_evidence: [],
  blockers: [],
};

const schedule: Schedule = {
  plan_id: "pln_1",
  version: 1,
  starts_on: "2026-10-11",
  daily_minutes: 70,
  total_estimated_minutes: 250,
  weeks: [],
  today: { date: "2026-10-11", items: [], minutes_planned: 0 },
  adherence: {
    counts: { on_time: 1, late: 0, overdue: 0, pending: 2 },
    minutes: { on_time: 25, late: 0, overdue: 0, actual: 25 },
    total_items: 3,
    completed_items: 1,
    adherence_percent: 33,
    behind_schedule: false,
  },
};

describe("accessible labelling", () => {
  it("gives every form control a programmatic label", () => {
    render(<AuthPanel t={t} onAuthenticated={vi.fn()} />);
    // getByLabelText fails when a control has no associated <label>, so this is the assertion.
    expect(screen.getByLabelText(t("auth.email"))).toBeInTheDocument();
    expect(screen.getByLabelText(t("auth.password"))).toBeInTheDocument();
    expect(screen.getByLabelText(t("auth.displayName"))).toBeInTheDocument();
  });

  it("names every region of the dashboard with a heading", () => {
    const { container } = render(
      <DashboardPanel t={t} data={dashboard} onPrimaryAction={vi.fn()} />,
    );
    const sections = Array.from(container.querySelectorAll("section"));
    expect(sections.length).toBeGreaterThan(0);
    for (const section of sections) {
      const labelledBy = section.getAttribute("aria-labelledby");
      expect(labelledBy, "every section must be named by a heading").toBeTruthy();
      expect(container.querySelector(`#${labelledBy}`)).not.toBeNull();
    }
  });

  it("renders exactly one top-level heading per panel", () => {
    render(<TodayPanel t={t} schedule={schedule} onStart={vi.fn()} />);
    expect(screen.getAllByRole("heading", { level: 2 })).toHaveLength(1);
  });
});

describe("errors are announced, not just coloured", () => {
  it("announces a failed sign-in attempt in a live region", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(
        async () =>
          new Response(JSON.stringify({ detail: "Invalid email or password." }), { status: 401 }),
      ),
    );
    render(<AuthPanel t={t} onAuthenticated={vi.fn()} />);
    // Login mode has no required consent checkboxes, so the submit path is the plain one.
    await userEvent.click(screen.getByRole("button", { name: t("auth.switchToLogin") }));
    await userEvent.type(screen.getByLabelText(t("auth.email")), "learner@example.com");
    await userEvent.type(screen.getByLabelText(t("auth.password")), "correct-horse-battery");
    await userEvent.click(screen.getByRole("button", { name: t("auth.login") }));
    const alert = await screen.findByRole("alert");
    expect(alert).toHaveTextContent(/invalid email or password/i);
    vi.unstubAllGlobals();
  });
});

describe("keyboard operation", () => {
  it("submits the form from the keyboard", async () => {
    const fetched = vi.fn(
      async () =>
        new Response(JSON.stringify({ detail: "Invalid email or password." }), { status: 401 }),
    );
    vi.stubGlobal("fetch", fetched);
    render(<AuthPanel t={t} onAuthenticated={vi.fn()} />);
    await userEvent.click(screen.getByRole("button", { name: t("auth.switchToLogin") }));

    await userEvent.type(screen.getByLabelText(t("auth.email")), "learner@example.com");
    await userEvent.type(screen.getByLabelText(t("auth.password")), "correct-horse-battery{Enter}");

    expect(fetched).toHaveBeenCalled();
    vi.unstubAllGlobals();
  });

  it("offers the primary action as a real button, not a clickable div", () => {
    const { container } = render(
      <DashboardPanel t={t} data={dashboard} onPrimaryAction={vi.fn()} />,
    );
    const clickable = Array.from(container.querySelectorAll("div")).filter(
      (node) => node.getAttribute("onclick") !== null,
    );
    expect(clickable).toHaveLength(0);
    expect(screen.getByRole("button")).toBeInTheDocument();
  });
});

describe("motion and focus styling", () => {
  it("honours prefers-reduced-motion", () => {
    expect(styles).toMatch(/@media \(prefers-reduced-motion: reduce\)/);
    const block = styles.slice(styles.indexOf("@media (prefers-reduced-motion: reduce)"));
    expect(block).toMatch(/animation-duration|transition-duration/);
  });

  it("also honours the in-app reduced-motion preference", () => {
    expect(styles).toMatch(/\[data-reduced-motion="true"\]/);
  });

  it("keeps a visible focus indicator", () => {
    expect(styles).toMatch(/:focus-visible/);
    const rule = styles.slice(styles.indexOf(":focus-visible"));
    expect(rule).toMatch(/outline/);
  });
});

describe("Arabic and right-to-left rendering", () => {
  it("flips direction for Arabic and back for English", () => {
    expect(direction("ar")).toBe("rtl");
    expect(direction("en")).toBe("ltr");
  });

  it("has an Arabic string for every English string", () => {
    const english = Object.keys(STRINGS.en);
    const missing = english.filter((key) => !(key in STRINGS.ar));
    expect(missing).toEqual([]);
    expect(english.length).toBeGreaterThan(100);
  });

  it("never leaves a placeholder unfilled by accident in Arabic", () => {
    const keys = Object.keys(STRINGS.ar) as (keyof typeof STRINGS.ar)[];
    for (const key of keys) {
      const template = STRINGS.ar[key];
      const params = template.match(/\{[a-z_]+\}/g) ?? [];
      for (const param of params) {
        const name = param.slice(1, -1);
        const filled = tAr(key, { [name]: "X" });
        expect(filled, `${key} did not interpolate ${param}`).not.toContain(param);
      }
    }
  });

  it("renders the Arabic interface right-to-left with Arabic copy", () => {
    const { container } = render(<TodayPanel t={tAr} schedule={schedule} onStart={vi.fn()} />);
    expect(screen.getByRole("heading", { name: "مهام اليوم" })).toBeInTheDocument();
    expect(container.textContent).toMatch(/[\u0600-\u06ff]/);
  });
});
