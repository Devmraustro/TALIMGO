import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError, type Goal, type PathSummary } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface GoalPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  onGoal: (goal: Goal) => void;
}

export function GoalPanel({ t, onGoal }: GoalPanelProps) {
  const [paths, setPaths] = useState<PathSummary[]>([]);
  const [pathId, setPathId] = useState("");
  const [statement, setStatement] = useState("");
  const [motivation, setMotivation] = useState("");
  const [minutes, setMinutes] = useState(240);
  const [targetDate, setTargetDate] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    void (async () => {
      try {
        const list = await api.get<PathSummary[]>("/api/curriculum/paths");
        setPaths(list);
        if (list.length > 0) setPathId(list[0].id);
      } catch {
        setPaths([]);
      }
    })();
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const goal = await api.post<Goal>("/api/goals", {
        path_id: pathId,
        statement,
        motivation,
        weekly_minutes: minutes,
        target_date: targetDate || null,
      });
      onGoal(goal);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  const selected = paths.find((path) => path.id === pathId);
  const locale = document.documentElement.dataset.locale === "ar" ? "ar" : "en";

  return (
    <section className="card" aria-labelledby="goal-heading">
      <h2 id="goal-heading">{t("goal.title")}</h2>
      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}

      <form onSubmit={submit}>
        <label htmlFor="path">{t("goal.path")}</label>
        <select id="path" value={pathId} onChange={(event) => setPathId(event.target.value)} required>
          {paths.map((path) => (
            <option value={path.id} key={path.id}>
              {locale === "ar" ? path.title_ar : path.title_en} · {path.estimated_hours}h
            </option>
          ))}
        </select>
        {selected ? (
          <p className="muted">{locale === "ar" ? selected.summary_ar : selected.summary_en}</p>
        ) : null}

        <label htmlFor="statement">{t("goal.statement")}</label>
        <textarea
          id="statement"
          rows={2}
          required
          minLength={8}
          maxLength={500}
          value={statement}
          onChange={(event) => setStatement(event.target.value)}
        />

        <label htmlFor="motivation">{t("goal.motivation")}</label>
        <textarea
          id="motivation"
          rows={2}
          value={motivation}
          onChange={(event) => setMotivation(event.target.value)}
        />

        <label htmlFor="minutes">{t("goal.minutes")}</label>
        <input
          id="minutes"
          type="number"
          min={30}
          max={3000}
          step={30}
          value={minutes}
          onChange={(event) => setMinutes(Number(event.target.value))}
        />

        <label htmlFor="target-date">{t("goal.targetDate")}</label>
        <input
          id="target-date"
          type="date"
          value={targetDate}
          onChange={(event) => setTargetDate(event.target.value)}
        />

        <div style={{ marginTop: "var(--space-4)" }}>
          <button type="submit" disabled={busy || !pathId}>
            {t("goal.create")}
          </button>
        </div>
      </form>
    </section>
  );
}
