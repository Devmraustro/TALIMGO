import { useState, type FormEvent } from "react";
import { api, ApiError, type TutorReply } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface TutorBoxProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  objectiveId: string;
  lessonId: string | null;
  aiAvailable: boolean;
}

/**
 * Tutor panel.
 *
 * The panel never hides a failure: when the local model is unavailable the learner is told plainly
 * (the backend answers 503 and there is no fallback). The lesson and practice keep working.
 */
export function TutorBox({ t, objectiveId, lessonId, aiAvailable }: TutorBoxProps) {
  const [question, setQuestion] = useState("");
  const [replies, setReplies] = useState<TutorReply[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function ask(event: FormEvent) {
    event.preventDefault();
    if (!question.trim()) return;
    setBusy(true);
    setError(null);
    try {
      const reply = await api.post<TutorReply>("/api/tutor/ask", {
        objective_id: objectiveId,
        lesson_id: lessonId,
        question: question.trim(),
      });
      setReplies((current) => [reply, ...current]);
      setQuestion("");
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 503) {
        setError(t("tutor.offline"));
      } else {
        setError(cause instanceof ApiError ? cause.message : t("auth.error"));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card" aria-labelledby="tutor-heading">
      <h2 id="tutor-heading">{t("tutor.title")}</h2>
      <p className="muted">{t("tutor.intro")}</p>

      {!aiAvailable ? <p className="notice">{t("tutor.offline")}</p> : null}

      <form onSubmit={ask}>
        <label htmlFor="tutor-question" className="sr-only">
          {t("tutor.title")}
        </label>
        <textarea
          id="tutor-question"
          rows={3}
          placeholder={t("tutor.placeholder")}
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <div style={{ marginTop: "var(--space-3)" }}>
          <button type="submit" disabled={busy || !question.trim()}>
            {t("tutor.send")}
          </button>
        </div>
      </form>

      {error ? (
        <div className="error-banner" role="alert" style={{ marginTop: "var(--space-3)" }}>
          {error}
        </div>
      ) : null}

      {replies.map((reply) => (
        <div className="feedback" key={reply.thread_id + reply.duration_ms + reply.reply.slice(0, 8)}>
          <p style={{ marginTop: 0 }}>{reply.reply}</p>
          <p className="muted" style={{ margin: 0 }}>
            <span className="pill">hint {reply.hint_level}/3</span>
            {reply.citations.map((citation) => (
              <span className="pill" key={citation}>
                {citation}
              </span>
            ))}
            <span className="pill">{reply.model}</span>
            <span className="pill">{reply.duration_ms} ms</span>
          </p>
        </div>
      ))}
    </section>
  );
}
