import { useId, useState, type FormEvent } from "react";
import type { Item } from "../lib/api";

interface ItemFormProps {
  item: Item;
  disabled?: boolean;
  allowHintFlag?: boolean;
  submitLabel: string;
  hintLabel?: string;
  shortAnswerLabel: string;
  onSubmit: (response: Record<string, unknown>, usedHint: boolean) => void;
}

/**
 * One question, one answer. The client only ever sends `{option_id}` or `{text}`; the answer key
 * stays on the server and feedback arrives with the result.
 */
export function ItemForm({
  item,
  disabled,
  allowHintFlag,
  submitLabel,
  hintLabel,
  shortAnswerLabel,
  onSubmit,
}: ItemFormProps) {
  const [selected, setSelected] = useState("");
  const [text, setText] = useState("");
  const [usedHint, setUsedHint] = useState(false);
  const groupName = useId();

  const ready = item.kind === "mcq_single" ? selected !== "" : text.trim() !== "";

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!ready) return;
    onSubmit(item.kind === "mcq_single" ? { option_id: selected } : { text: text.trim() }, usedHint);
    setSelected("");
    setText("");
    setUsedHint(false);
  }

  return (
    <form onSubmit={handleSubmit}>
      <p>
        <span className="pill">difficulty {item.difficulty}/5</span>
        {item.prompt}
      </p>

      {item.kind === "mcq_single" && item.options ? (
        <fieldset>
          <legend className="sr-only">Choose one answer</legend>
          {item.options.map((option) => (
            <div className="option-row" key={option.id}>
              <input
                type="radio"
                id={`${groupName}-${option.id}`}
                name={groupName}
                value={option.id}
                checked={selected === option.id}
                onChange={() => setSelected(option.id)}
                disabled={disabled}
              />
              <label htmlFor={`${groupName}-${option.id}`}>{option.text}</label>
            </div>
          ))}
        </fieldset>
      ) : (
        <>
          <label htmlFor={`${groupName}-text`}>{shortAnswerLabel}</label>
          <input
            id={`${groupName}-text`}
            type="text"
            value={text}
            onChange={(event) => setText(event.target.value)}
            disabled={disabled}
            autoComplete="off"
          />
        </>
      )}

      {allowHintFlag ? (
        <div className="option-row" style={{ marginTop: "var(--space-3)" }}>
          <input
            type="checkbox"
            id={`${groupName}-hint`}
            checked={usedHint}
            onChange={(event) => setUsedHint(event.target.checked)}
            disabled={disabled}
          />
          <label htmlFor={`${groupName}-hint`}>{hintLabel}</label>
        </div>
      ) : null}

      <div style={{ marginTop: "var(--space-4)" }}>
        <button type="submit" disabled={disabled || !ready}>
          {submitLabel}
        </button>
      </div>
    </form>
  );
}
