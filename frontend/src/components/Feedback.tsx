import type { AnswerFeedback } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface FeedbackProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  feedback: AnswerFeedback;
}

/**
 * Answer feedback. Wrong answers are information, never a judgement: the correct answer and the
 * reasoning are always shown, and no score or streak is displayed for its own sake.
 */
export function Feedback({ t, feedback }: FeedbackProps) {
  return (
    <div
      className={`feedback ${feedback.is_correct ? "correct" : "incorrect"}`}
      role="status"
      aria-live="polite"
    >
      <p style={{ margin: "0 0 var(--space-2)" }}>
        <strong>{feedback.is_correct ? t("diagnostic.correct") : t("diagnostic.incorrect")}</strong>{" "}
        <span className="muted">{feedback.objective_title}</span>
      </p>
      {feedback.correct_answer ? (
        <p style={{ margin: "0 0 var(--space-2)" }}>
          {t("diagnostic.correctAnswer")}: <code>{feedback.correct_answer}</code>
        </p>
      ) : null}
      {feedback.explanation ? <p style={{ margin: 0 }}>{feedback.explanation}</p> : null}
    </div>
  );
}

interface ExplainedProps {
  title: string;
  why: string;
  evidence: string;
}

/** Small helper for showing a recommendation together with its reason. */
export function Explained({ title, why, evidence }: ExplainedProps) {
  return (
    <div className="notice">
      <p style={{ margin: "0 0 var(--space-1)" }}>
        <strong>{title}</strong>
      </p>
      <p style={{ margin: "0 0 var(--space-1)" }}>{why}</p>
      <p style={{ margin: 0 }}>{evidence}</p>
    </div>
  );
}
