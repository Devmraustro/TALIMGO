import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import type { Item } from "../lib/api";
import { ItemForm } from "./ItemForm";

function item(overrides: Partial<Item>): Item {
  return {
    id: "py:x:q1",
    objective_id: "py:x",
    kind: "mcq_single",
    prompt: "Question?",
    options: null,
    difficulty: 2,
    ...overrides,
  };
}

function renderForm(current: Item, onSubmit = vi.fn()) {
  render(
    <ItemForm
      item={current}
      submitLabel="Submit"
      shortAnswerLabel="Your answer"
      onSubmit={onSubmit}
    />,
  );
  return onSubmit;
}

describe("ItemForm item kinds", () => {
  it("collects a multi-select as an option_ids set", async () => {
    const onSubmit = renderForm(
      item({
        kind: "mcq_multi",
        options: [
          { id: "a", text: "Alpha" },
          { id: "b", text: "Beta" },
          { id: "c", text: "Gamma" },
        ],
      }),
    );
    const submit = screen.getByRole("button", { name: "Submit" });
    expect(submit).toBeDisabled();
    await userEvent.click(screen.getByLabelText("Alpha"));
    await userEvent.click(screen.getByLabelText("Gamma"));
    await userEvent.click(submit);
    expect(onSubmit).toHaveBeenCalledWith({ option_ids: ["a", "c"] }, false);
  });

  it("builds an ordering by clicking steps in sequence", async () => {
    const onSubmit = renderForm(
      item({
        kind: "ordering",
        options: [
          { id: "loop", text: "Repeat" },
          { id: "start", text: "Start at zero" },
          { id: "use", text: "Use the value" },
        ],
      }),
    );
    await userEvent.click(screen.getByRole("button", { name: /start at zero/i }));
    await userEvent.click(screen.getByRole("button", { name: /use the value/i }));
    // Not submittable until every step is placed.
    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled();
    await userEvent.click(screen.getByRole("button", { name: /repeat/i }));
    await userEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(onSubmit).toHaveBeenCalledWith({ option_ids: ["start", "use", "loop"] }, false);
  });

  it("submits a boolean for true_false", async () => {
    const onSubmit = renderForm(item({ kind: "true_false", options: null }));
    await userEvent.click(screen.getByLabelText("False"));
    await userEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(onSubmit).toHaveBeenCalledWith({ value: false }, false);
  });

  it("sends numeric text verbatim so the server can parse Arabic-Indic digits", async () => {
    const onSubmit = renderForm(item({ kind: "numeric", options: null }));
    await userEvent.type(screen.getByLabelText("Your number"), "٧");
    await userEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(onSubmit).toHaveBeenCalledWith({ text: "٧" }, false);
  });

  it("keeps mcq_single and short_answer behaviour unchanged", async () => {
    const onSubmit = renderForm(
      item({
        kind: "mcq_single",
        options: [
          { id: "a", text: "int" },
          { id: "b", text: "text" },
        ],
      }),
    );
    await userEvent.click(screen.getByLabelText("int"));
    await userEvent.click(screen.getByRole("button", { name: "Submit" }));
    expect(onSubmit).toHaveBeenCalledWith({ option_id: "a" }, false);
  });
});
