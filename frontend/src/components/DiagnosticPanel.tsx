import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type DiagnosticAnswerResult, type DiagnosticState } from "../lib/api";
import type { StringKey } from "../lib/i18n";
import { ItemForm } from "./ItemForm";
import { Feedback } from "./Feedback";

interface DiagnosticPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  goalId: string;
  onCompleted: () => void;
}

export function DiagnosticPanel({ t, goalId, onCompleted }: DiagnosticPanelProps) {
  const [state, setState] = useState<DiagnosticState | null>(null);
  const [feedback, setFeedback] = useState<DiagnosticAnswerResult["feedback"] | null>(null);
  const [placement, setPlacement] = useState<DiagnosticState["placement"]>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const start = useCallback(async () => {
    setError(null);
    try {
      const next = await api.post<DiagnosticState>(`/api/diagnostic/goals/${goalId}`);
      setState(next);
      setPlacement(next.placement ?? null);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    }
  }, [goalId, t]);

  useEffect(() => {
    void start();
  }, [start]);

  async function answer(response: Record<string, unknown>) {
    if (!state?.current_item) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.post<DiagnosticAnswerResult>(
        `/api/diagnostic/${state.attempt_id}/answers`,
        { item_id: state.current_item.id, response, confidence: "unsure" },
      );
      setFeedback(result.feedback);
      setPlacement(result.placement ?? null);
      setState({
        ...state,
        status: result.completed ? "completed" : "in_progress",
        current_item: result.next_item,
        answered_items: result.answered_items,
      });
      if (result.completed) onCompleted();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  if (error) {
    return (
      <section className="card">
        <div className="error-banner" role="alert">
          {error}
        </div>
        <button type="button" onClick={() => void start()}>
          {t("common.retry")}
        </button>
      </section>
    );
  }

  if (!state) {
    return (
      <section className="card">
        <p>{t("common.loading")}</p>
      </section>
    );
  }

  return (
    <section className="card" aria-labelledby="diagnostic-heading">
      <h2 id="diagnostic-heading">{t("diagnostic.title")}</h2>
      {state.answered_items === 0 ? <p className="muted">{t("diagnostic.intro")}</p> : null}

      <p className="muted">
        {t("diagnostic.progress", {
          done: Math.min(state.answered_items + (state.status === "in_progress" ? 1 : 0), state.total_items),
          total: state.total_items,
        })}
      </p>

      {feedback ? <Feedback t={t} feedback={feedback} /> : null}

      {state.status === "in_progress" && state.current_item ? (
        <ItemForm
          key={state.current_item.id}
          item={state.current_item}
          disabled={busy}
          submitLabel={t("diagnostic.submit")}
          shortAnswerLabel={t("diagnostic.shortAnswer")}
          numericLabel={t("item.numericLabel")}
          chooseAllLabel={t("item.chooseAll")}
          trueLabel={t("item.true")}
          falseLabel={t("item.false")}
          orderingTitle={t("item.orderingTitle")}
          orderingHint={t("item.orderingHint")}
          orderingChosenLabel={t("item.orderingChosen")}
          orderingResetLabel={t("item.orderingReset")}
          onSubmit={(response) => void answer(response)}
        />
      ) : (
        <div>
          <h3>{t("diagnostic.placement")}</h3>
          {placement?.summary ? (
            <dl className="summary">
              <dt>assumed known</dt>
              <dd>{placement.summary.assumed_known ?? 0}</dd>
              <dt>likely known</dt>
              <dd>{placement.summary.likely_known ?? 0}</dd>
              <dt>needs work</dt>
              <dd>{placement.summary.needs_work ?? 0}</dd>
            </dl>
          ) : null}
          <p className="muted">{t("diagnostic.placementNote")}</p>
        </div>
      )}
    </section>
  );
}
