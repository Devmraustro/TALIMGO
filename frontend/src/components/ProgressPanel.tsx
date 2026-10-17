import { useEffect, useState } from "react";
import { api, type MasteryRow } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface ProgressPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
}

/**
 * Mastery view. Every row shows the state *and* the evidence behind it, because the estimate is
 * derived (see ADR 0004) and the learner is entitled to see how it was formed.
 */
export function ProgressPanel({ t }: ProgressPanelProps) {
  const [rows, setRows] = useState<MasteryRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const data = await api.get<MasteryRow[]>("/api/practice/progress/mastery");
        if (!cancelled) setRows(data);
      } catch {
        if (!cancelled) setError(t("auth.error"));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [t]);

  if (error) {
    return (
      <section className="card">
        <div className="error-banner" role="alert">
          {error}
        </div>
      </section>
    );
  }

  if (!rows) {
    return (
      <section className="card">
        <p>{t("common.loading")}</p>
      </section>
    );
  }

  return (
    <section className="card" aria-labelledby="progress-heading">
      <h2 id="progress-heading">{t("progress.title")}</h2>
      {rows.length === 0 ? <p className="muted">{t("dashboard.empty")}</p> : null}
      <ul className="plan-items">
        {rows.map((row) => (
          <li key={row.objective_id}>
            <span className={`pill ${row.needs_review ? "warning" : row.phase === "retaining" ? "success" : ""}`}>
              {row.phase === "retaining" ? t("progress.phase.retaining") : t("progress.phase.acquiring")}
            </span>
            <span>{row.title}</span>
            <span className="muted">
              {row.unassisted_successes} unassisted · {t("progress.evidence", { n: row.evidence_count })}
            </span>
            {row.retrievability !== null ? (
              <span className="muted">
                · {t("progress.recall", { n: Math.round(row.retrievability * 100) })}
              </span>
            ) : null}
            {row.needs_review ? <span className="pill warning">{t("progress.needsReview")}</span> : null}
          </li>
        ))}
      </ul>
    </section>
  );
}
