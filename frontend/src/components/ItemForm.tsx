import { useState, type FormEvent } from "react";
import type { Item } from "../lib/api";

interface ItemFormProps {
  item: Item;
  disabled?: boolean;
  submitLabel: string;
  shortAnswerLabel: string;
  numericLabel?: string;
  chooseAllLabel?: string;
  trueLabel?: string;
  falseLabel?: string;
  orderingTitle?: string;
  orderingHint?: string;
  orderingChosenLabel?: string;
  orderingResetLabel?: string;
  hintLabel?: string;
  allowHintFlag?: boolean;
  onSubmit: (response: Record<string, unknown>, usedHint: boolean) => void;
}

/**
 * Renders one assessment item. The component is deliberately knowledge-free: it never sees the
 * answer key, it only collects a response in the shape the server's deterministic grader expects
 * per item kind (`mcq_single`, `mcq_multi`, `ordering`, `true_false`, `numeric`, `short_answer`).
 */
export function ItemForm({
  item,
  disabled = false,
  submitLabel,
  shortAnswerLabel,
  numericLabel = "Your number",
  chooseAllLabel = "Select every option that applies",
  trueLabel = "True",
  falseLabel = "False",
  orderingTitle = "Put these in order",
  orderingHint = "Select the steps in the right order. Select a chosen step again to remove it.",
  orderingChosenLabel = "Your order",
  orderingResetLabel = "Clear order",
  hintLabel,
  allowHintFlag = false,
  onSubmit,
}: ItemFormProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [multi, setMulti] = useState<string[]>([]);
  const [order, setOrder] = useState<string[]>([]);
  const [boolAnswer, setBoolAnswer] = useState<boolean | null>(null);
  const [text, setText] = useState("");
  const [usedHint, setUsedHint] = useState(false);

  const options = item.options ?? [];
  const canSubmit =
    disabled === false &&
    (item.kind === "mcq_single"
      ? selected !== null
      : item.kind === "mcq_multi"
        ? multi.length > 0
        : item.kind === "ordering"
          ? order.length === options.length && options.length > 0
          : item.kind === "true_false"
            ? boolAnswer !== null
            : item.kind === "numeric"
              ? text.trim() !== ""
              : true);

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!canSubmit) return;
    if (item.kind === "mcq_single") {
      onSubmit({ option_id: selected }, usedHint);
    } else if (item.kind === "mcq_multi") {
      onSubmit({ option_ids: multi }, usedHint);
    } else if (item.kind === "ordering") {
      onSubmit({ option_ids: order }, usedHint);
    } else if (item.kind === "true_false") {
      onSubmit({ value: boolAnswer }, usedHint);
    } else {
      // numeric and short_answer both travel as free text; the server parses numbers itself.
      onSubmit({ text }, usedHint);
    }
  }

  function toggleMulti(optionId: string) {
    setMulti((previous) =>
      previous.includes(optionId)
        ? previous.filter((candidate) => candidate !== optionId)
        : [...previous, optionId],
    );
  }

  function pickForOrder(optionId: string) {
    setOrder((previous) =>
      previous.includes(optionId)
        ? previous.filter((candidate) => candidate !== optionId)
        : [...previous, optionId],
    );
  }

  const optionText = (optionId: string) =>
    options.find((option) => option.id === optionId)?.text ?? optionId;

  return (
    <form onSubmit={handleSubmit} aria-describedby={item.kind === "ordering" ? "ordering-hint" : undefined}>
      <p>
        <strong>{item.prompt}</strong>{" "}
        <span className="pill" aria-label={`difficulty ${item.difficulty} of 5`}>
          {item.difficulty}/5
        </span>
      </p>

      {item.kind === "mcq_single" ? (
        <fieldset>
          <legend className="visually-hidden">Choose one answer</legend>
          {options.map((option) => (
            <label key={option.id} className="radio-row">
              <input
                type="radio"
                name={item.id}
                value={option.id}
                checked={selected === option.id}
                onChange={() => setSelected(option.id)}
                disabled={disabled}
              />
              <span>{option.text}</span>
            </label>
          ))}
        </fieldset>
      ) : null}

      {item.kind === "mcq_multi" ? (
        <fieldset>
          <legend className="visually-hidden">{chooseAllLabel}</legend>
          <p className="muted">{chooseAllLabel}</p>
          {options.map((option) => (
            <label key={option.id} className="radio-row">
              <input
                type="checkbox"
                name={`${item.id}-${option.id}`}
                value={option.id}
                checked={multi.includes(option.id)}
                onChange={() => toggleMulti(option.id)}
                disabled={disabled}
              />
              <span>{option.text}</span>
            </label>
          ))}
        </fieldset>
      ) : null}

      {item.kind === "ordering" ? (
        <div>
          <p className="muted" id="ordering-hint">
            {orderingTitle}. {orderingHint}
          </p>
          <div className="choice-row" role="group" aria-label={orderingTitle}>
            {options.map((option) => {
              const position = order.indexOf(option.id);
              return (
                <button
                  key={option.id}
                  type="button"
                  className="secondary"
                  aria-pressed={position >= 0}
                  onClick={() => pickForOrder(option.id)}
                  disabled={disabled}
                >
                  {position >= 0 ? `${position + 1}. ` : ""}
                  {option.text}
                </button>
              );
            })}
          </div>
          <h4>{orderingChosenLabel}</h4>
          <ol aria-live="polite">
            {order.map((optionId) => (
              <li key={optionId}>{optionText(optionId)}</li>
            ))}
          </ol>
          {order.length > 0 ? (
            <button
              type="button"
              className="secondary"
              onClick={() => setOrder([])}
              disabled={disabled}
            >
              {orderingResetLabel}
            </button>
          ) : null}
        </div>
      ) : null}

      {item.kind === "true_false" ? (
        <fieldset>
          <legend className="visually-hidden">True or false?</legend>
          <label className="radio-row">
            <input
              type="radio"
              name={item.id}
              value="true"
              checked={boolAnswer === true}
              onChange={() => setBoolAnswer(true)}
              disabled={disabled}
            />
            <span>{trueLabel}</span>
          </label>
          <label className="radio-row">
            <input
              type="radio"
              name={item.id}
              value="false"
              checked={boolAnswer === false}
              onChange={() => setBoolAnswer(false)}
              disabled={disabled}
            />
            <span>{falseLabel}</span>
          </label>
        </fieldset>
      ) : null}

      {item.kind === "short_answer" || item.kind === "numeric" ? (
        <div>
          <label htmlFor={`short-${item.id}`}>
            {item.kind === "numeric" ? numericLabel : shortAnswerLabel}
          </label>
          <input
            id={`short-${item.id}`}
            type="text"
            inputMode={item.kind === "numeric" ? "decimal" : "text"}
            value={text}
            onChange={(event) => setText(event.target.value)}
            disabled={disabled}
            autoComplete="off"
          />
        </div>
      ) : null}

      {allowHintFlag && hintLabel ? (
        <label className="radio-row">
          <input
            type="checkbox"
            checked={usedHint}
            onChange={(event) => setUsedHint(event.target.checked)}
            disabled={disabled}
          />
          <span>{hintLabel}</span>
        </label>
      ) : null}

      <div style={{ marginTop: "var(--space-3)" }}>
        <button type="submit" disabled={!canSubmit}>
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
