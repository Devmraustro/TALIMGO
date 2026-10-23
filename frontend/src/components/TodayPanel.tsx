import type { Schedule, ScheduleItem } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface TodayPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  schedule: Schedule | null;
  onStart: (item: ScheduleItem) => void;
  busy?: boolean;
}

/**
 * Today's missions: the dated view of the roadmap.
 *
 * The roadmap is a sequence of work; this card answers "what do I do today?" using the dates the
 * server derived from the plan, the learner's weekly time budget and their available days. Work that
 * slipped from earlier days is shown here too, with a count rather than a reprimand (master
 * reference §6.7, §6.9).
 */
export function TodayPanel({ t, schedule, onStart, busy }: TodayPanelProps) {
  if (!schedule) return null;

  const overdue = schedule.adherence.counts.overdue;
  const items = schedule.today.items;

  return (
    <section className="card" aria-labelledby="today-heading">
      <h2 id="today-heading">{t("today.title")}</h2>
      <p className="muted">
        {schedule.today.date} · {t("today.minutes", { n: schedule.today.minutes_planned })}
      </p>
      {overdue > 0 ? <p className="muted">{t("today.overdue", { n: overdue })}</p> : null}

      {items.length === 0 ? (
        <p className="muted">{t("today.empty")}</p>
      ) : (
        <ul className="plan-items">
          {items.map((item) => {
            const done = item.status === "completed";
            return (
              <li key={item.id}>
                <span className={`pill ${done ? "success" : ""}`}>
                  {t(`plan.kind.${item.kind}` as StringKey)}
                </span>
                <span>{item.objective_title}</span>
                <span className="muted">{t("plan.minutes", { n: item.est_minutes })}</span>
                {done ? (
                  <span className="muted">{t("today.done")}</span>
                ) : (
                  <button type="button" onClick={() => onStart(item)} disabled={busy}>
                    {t("today.start")}
                  </button>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </section>
  );
}
