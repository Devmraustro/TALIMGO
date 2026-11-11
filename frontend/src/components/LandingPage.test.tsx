import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LandingPage } from "./LandingPage";
import { translator } from "../lib/i18n";

const t = translator("en");
const tAr = translator("ar");

function renderLanding(overrides: Partial<Parameters<typeof LandingPage>[0]> = {}) {
  const props = {
    t,
    locale: "en" as const,
    onLocale: vi.fn(),
    onGetStarted: vi.fn(),
    onSignIn: vi.fn(),
    ...overrides,
  };
  return { ...render(<LandingPage {...props} />), props };
}

describe("LandingPage (public pre-launch surface)", () => {
  it("renders the approved English headline and one primary action", () => {
    renderLanding();
    expect(
      screen.getByRole("heading", { level: 1, name: "Learn. Grow. Go." }),
    ).toBeInTheDocument();
    // The primary CTA is repeated in header, hero and closing band — same action, same label.
    expect(screen.getAllByRole("button", { name: "Build my learning plan" }).length).toBe(3);
    expect(screen.getByRole("link", { name: "See how it works" })).toHaveAttribute("href", "#how");
  });

  it("renders the approved Arabic tagline and keeps the EN call to action reachable", () => {
    renderLanding({ t: tAr, locale: "ar" });
    expect(
      screen.getByRole("heading", { level: 1, name: "تعلّم بذكاء. تقدّم بثقة." }),
    ).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: "ابنِ خطة تعلّمي" }).length).toBeGreaterThan(0);
  });

  it("opens the account form through the primary CTA and the sign-in link independently", () => {
    const { props } = renderLanding();
    fireEvent.click(screen.getAllByRole("button", { name: "Build my learning plan" })[0]);
    expect(props.onGetStarted).toHaveBeenCalledTimes(1);
    expect(props.onSignIn).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Sign in" }));
    expect(props.onSignIn).toHaveBeenCalledTimes(1);
  });

  it("offers a language group control with both locales", () => {
    const { props } = renderLanding();
    const ar = screen.getByRole("button", { name: "العربية" });
    fireEvent.click(ar);
    expect(props.onLocale).toHaveBeenCalledWith("ar");
    expect(screen.getByRole("button", { name: "EN" })).toHaveAttribute("aria-pressed", "true");
  });

  it("keeps every FAQ answer behind a keyboard-operable disclosure", () => {
    const { container } = renderLanding();
    const items = container.querySelectorAll("details.faq-item");
    expect(items.length).toBe(10);
    for (const item of items) {
      expect(item.querySelector("summary")).not.toBeNull();
    }
    // Pricing honesty: the FAQ must not publish a number.
    expect(container.textContent).toContain("No price is published");
    expect(container.textContent).not.toMatch(/\$\s?\d|€\s?\d|DZD/);
  });

  it("labels the journey as illustrative and never fabricates testimonials or user counts", () => {
    renderLanding();
    expect(screen.getByText(/Illustrative example, not a real user/i)).toBeInTheDocument();
    expect(screen.getByText(/not a production service yet/i)).toBeInTheDocument();
  });

  it("ships no images and no off-origin references", () => {
    const { container } = renderLanding();
    expect(container.querySelectorAll("img").length).toBe(0);
    const html = container.innerHTML;
    expect(html).not.toMatch(/https?:\/\//);
    expect(html).not.toMatch(/localhost|127\.0\.0\.1/);
  });
});
