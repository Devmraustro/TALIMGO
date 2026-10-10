import { useEffect, useState } from "react";
import { api, ApiError, type Lesson, type PracticeSession } from "../lib/api";
import type { StringKey } from "../lib/i18n";
import { Feedback } from "./Feedback";
import { ItemForm } from "./ItemForm";
import { Markdown } from "./Markdown";
import { TutorBox } from "./TutorBox";

interface PracticePanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  objectiveId: string | null;
  lessonId: string | null;
  aiAvailable: boolean;
  onFinished: () => void;
}

export function PracticePanel({ t, objectiveId, lessonId, aiAvailable, onFinished }: PracticePanelProps) {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [session, setSession] = useState<PracticeSession | null>(null);
  const [feedback, setFeedback] = useState<PracticeSession["feedback"]>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLesson(null);
    setSession(null);
    setFeedback(null);
    if (!lessonId) return;
    let cancelled = false;
    void (async () => {
      try {
        const loaded = await api.get<Lesson>(`/api/curriculum/lessons/${lessonId}`);
        if (!cancelled) setLesson(loaded);
      } catch {
        if (!cancelled) setLesson(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [lessonId]);

  async function start() {
    if (!objectiveId) return;
    setBusy(true);
    setError(null);
    try {
      const created = await api.post<PracticeSession>("/api/practice/sessions", {
        objective_id: objectiveId,
        size: 5,
      });
      setSession(created);
      setFeedback(null);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  async function answer(response: Record<string, unknown>, usedHint: boolean) {
    if (!session?.item) return;
    setBusy(true);
    setError(null);
    try {
      const updated = await api.post<PracticeSession>(
        `/api/practice/sessions/${session.session_id}/answers`,
        { item_id: session.item.id, response, used_hint: usedHint },
      );
      setSession(updated);
      setFeedback(updated.feedback);
      if (!updated.item) onFinished();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  async function finish() {
    if (!session) return;
    setBusy(true);
    try {
      await api.post(`/api/practice/sessions/${session.session_id}/complete`);
      setSession(null);
      onFinished();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  if (!objectiveId) {
    return (
      <section className="card">
        <h2>{t("practice.title")}</h2>
        <p className="muted">{t("dashboard.empty")}</p>
      </section>
    );
  }

  return (
    <div className="grid two">
      <section className="card">
        {error ? (
          <div className="error-banner" role="alert">
            {error}
          </div>
        ) : null}

        {lesson ? (
          <>
            <h2>
              {t("lesson.title")}: {lesson.title}
            </h2>
            <p className="muted">{t("plan.minutes", { n: lesson.est_minutes })}</p>
            <Markdown source={lesson.body_md} />
          </>
        ) : (
          <h2>{t("practice.title")}</h2>
        )}

        <h3>{t("practice.title")}</h3>
        {!session ? (
          <button type="button" onClick={() => void start()} disabled={busy}>
            {t("practice.start")}
          </button>
        ) : (
          <>
            <p className="muted">
              {t("practice.question", {
                n: session.answered + (session.item ? 1 : 0),
                total: session.total,
              })}
            </p>
            {feedback ? <Feedback t={t} feedback={feedback} /> : null}
            {session.item ? (
              <ItemForm
                key={session.item.id}
                item={session.item}
                disabled={busy}
                allowHintFlag
                hintLabel={t("practice.hintUsed")}
                submitLabel={t("practice.submit")}
                shortAnswerLabel={t("diagnostic.shortAnswer")}
                onSubmit={(response, usedHint) => void answer(response, usedHint)}
              />
            ) : (
              <p>
                <strong>{t("practice.done")}</strong>
              </p>
            )}
            <button type="button" className="secondary" onClick={() => void finish()} disabled={busy}>
              {t("common.back")}
            </button>
          </>
        )}
      </section>

      <TutorBox t={t} objectiveId={objectiveId} lessonId={lessonId} aiAvailable={aiAvailable} />
    </div>
  );
}
