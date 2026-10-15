import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Markdown } from "./Markdown";

describe("Markdown renderer", () => {
  it("renders headings, paragraphs, code fences and lists", () => {
    const source = [
      "## What a variable is",
      "",
      "A variable is a **name** for a value.",
      "",
      "```python",
      "age = 17",
      "```",
      "",
      "- first item",
      "- second item",
      "",
      "| Row | Meaning |",
      "|---|---|",
      "| Runs | Works correctly |",
    ].join("\n");

    render(<Markdown source={source} />);

    expect(screen.getByRole("heading", { name: "What a variable is" })).toBeInTheDocument();
    expect(screen.getByText("name")).toBeInTheDocument();
    expect(screen.getByText("age = 17")).toBeInTheDocument();
    expect(screen.getByText("first item")).toBeInTheDocument();
    expect(screen.getByRole("columnheader", { name: "Meaning" })).toBeInTheDocument();
  });

  it("renders inline code without interpreting it", () => {
    render(<Markdown source={"Use `len(text)` to measure."} />);
    expect(screen.getByText("len(text)")).toBeInTheDocument();
  });

  it("never interprets HTML from lesson content", () => {
    const hostile = [
      "## Careful",
      "",
      "<script>window.__pwned = true;</script>",
      "",
      "<img src=x onerror='window.__pwned = true' />",
    ].join("\n");

    const { container } = render(<Markdown source={hostile} />);

    expect(container.querySelector("script")).toBeNull();
    expect(container.querySelector("img")).toBeNull();
    expect(
      screen.getByText("<script>window.__pwned = true;</script>"),
    ).toBeInTheDocument();
    expect((window as unknown as { __pwned?: boolean }).__pwned).toBeUndefined();
  });

  it("renders Arabic content and preserves its direction", () => {
    render(<Markdown source={"## المتغيرات\n\nالمتغير **اسم** لقيمة."} />);
    expect(screen.getByRole("heading", { name: "المتغيرات" })).toBeInTheDocument();
    expect(screen.getByText("اسم")).toBeInTheDocument();
  });

  it("keeps code blocks inside a pre element for horizontal scrolling", () => {
    const { container } = render(<Markdown source={"```python\nprint('x')\n```"} />);
    expect(container.querySelector("pre code")?.textContent).toBe("print('x')");
  });
});
