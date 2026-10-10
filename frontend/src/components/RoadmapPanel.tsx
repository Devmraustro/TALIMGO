import { useState } from "react";
import { api, ApiError, type Plan } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface RoadmapPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  goalId: string | null;
  plan: Plan | null;
  onPlan: (plan: Plan) => void;
}

export function RoadmapPanel({ t, goalId, plan, onPlan }: RoadmapPanelProps) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [skipped, setSkipped] = useState<number | null>(null);

  async function generate() {
    if (!goalId) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.post<{ plan: Plan; skipped_objectives: unknown[] }>(
        `/api/plans/goals/${goalId}`,
      );
      onPlan(result.plan);
      setSkipped(result.skipped_objectives.length);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card" aria-labelledby="plan-heading">
      <h2 id="plan-heading">{t("plan.title")}</h2>

      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}

      {goalId ? (
        <button type="button" onClick={() => void generate()} disabled={busy}>
          {plan ? t("plan.regenerate") : t("plan.generate")}
        </button>
      ) : (
        <p className="muted">{t("dashboard.empty")}</p>
      )}

      {plan ? (
        <>
          <p className="muted" style={{ marginTop: "var(--space-4)" }}>
            {t("plan.validated")} {t("plan.minutes", { n: plan.total_estimated_minutes })}
            {plan.validation_report?.checked?.length
              ? ` · ${plan.validation_report.checked.length} checks`
              : ""}
          </p>
          {skipped !== null ? (
            <p className="muted">{t("plan.skipped", { n: skipped })}</p>
          ) : null}

          {plan.weeks.map((week) => (
            <article className="week" key={week.week_number}>
              <h3>
                {t("plan.week", { n: week.week_number })} — {week.theme}
              </h3>
              <p className="muted">{t("plan.minutes", { n: week.total_minutes })}</p>
              <ul className="plan-items">
                {week.items.map((item) => (
                  <li key={item.id}>
                    <span className={`pill ${item.status === "completed" ? "success" : ""}`}>
                      {t(`plan.kind.${item.kind}` as StringKey)}
                    </span>
                    <span>{item.objective_title}</span>
                    <span className="muted">{t("plan.minutes", { n: item.est_minutes })}</span>
                    {item.rationale ? <span className="muted">— {item.rationale}</span> : null}
                  </li>
                ))}
              </ul>
            </article>
          ))}
        </>
      ) : null}
    </section>
  );
}
