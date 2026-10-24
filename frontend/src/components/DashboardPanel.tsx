import type { Dashboard } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface DashboardPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  data: Dashboard;
  onPrimaryAction: () => void;
  busy?: boolean;
}

/**
 * Today's view. One action, its reason, and the evidence behind it — deliberately not a wall of
 * charts (master reference §8.3.1: the dashboard answers "what do I do now?" and nothing else first).
 */
export function DashboardPanel({ t, data, onPrimaryAction, busy }: DashboardPanelProps) {
  const action = data.next_action;
  const actionLabel =
    action.kind === "diagnostic"
      ? t("dashboard.startDiagnostic")
      : action.kind === "review"
        ? t("practice.start")
        : t("practice.start");

  return (
    <>
      <section className="card" aria-labelledby="next-action-heading">
        <h2 id="next-action-heading">{t("dashboard.next")}</h2>
        <p style={{ fontSize: "var(--step-2)", margin: "0 0 var(--space-2)" }}>
          <span className="pill">{action.kind}</span>
          {action.title}
        </p>
        <p className="muted" style={{ marginBottom: "var(--space-2)" }}>
          <strong>{t("dashboard.why")}</strong> {action.rationale}
        </p>
        <p className="muted">
          <strong>{t("dashboard.evidence")}</strong> {action.evidence_basis}
        </p>
        <p className="muted">
          <span className="pill">{t("plan.minutes", { n: action.est_minutes })}</span>
        </p>
        {action.kind !== "idle" ? (
          <button type="button" onClick={onPrimaryAction} disabled={busy}>
            {actionLabel}
          </button>
        ) : null}
      </section>

      <div className="grid two">
        <section className="card" aria-labelledby="mastery-heading">
          <h2 id="mastery-heading">{t("progress.title")}</h2>
          {data.goal ? null : <p className="muted">{t("dashboard.empty")}</p>}
          <dl className="summary">
            <dt>{t("progress.phase.acquiring")}</dt>
            <dd>{data.mastery_summary.acquiring ?? 0}</dd>
            <dt>{t("progress.phase.retaining")}</dt>
            <dd>{data.mastery_summary.retaining ?? 0}</dd>
            <dt>{t("progress.needsReview")}</dt>
            <dd>{data.mastery_summary.needs_review ?? 0}</dd>
          </dl>
        </section>

        <section className="card" aria-labelledby="evidence-heading">
          <h2 id="evidence-heading">{t("progress.evidence", { n: data.recent_evidence.length })}</h2>
          {data.recent_evidence.length === 0 ? (
            <p className="muted">{t("dashboard.empty")}</p>
          ) : (
            <ul className="plan-items">
              {data.recent_evidence.map((row, index) => (
                <li key={`${row.objective_id}-${index}`}>
                  <span
                    className={`pill ${row.outcome === "success" ? "success" : "danger"}`}
                  >
                    {row.outcome === "success" ? "✓" : "✗"}
                  </span>
                  <span>{row.objective_title}</span>
                  <span className="muted">
                    {row.kind}
                    {row.assisted ? " · assisted" : ""}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>

      {data.blockers.length > 0 ? (
        <section className="card" aria-labelledby="blockers-heading">
          <h2 id="blockers-heading">{t("dashboard.blockers")}</h2>
          <ul>
            {data.blockers.map((blocker) => (
              <li key={blocker}>{blocker}</li>
            ))}
          </ul>
        </section>
      ) : null}
    </>
  );
}
