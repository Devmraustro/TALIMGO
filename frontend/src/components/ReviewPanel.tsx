import { useEffect, useState } from "react";
import { api, type ReviewQueue } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface ReviewPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  /** Starts a review-mode practice session on the objective (handled by the app shell). */
  onReview: (objectiveId: string, lessonId: string | null) => void;
}

/**
 * The spaced-review surface: the same retrievability model that decides mastery also decides what
 * is fading, and this panel simply lists it, most-forgotten first. Review answers are recorded as
 * ordinary practice evidence in review mode — no separate scheduler to disagree with mastery.
 */
export function ReviewPanel({ t, onReview }: ReviewPanelProps) {
  const [queue, setQueue] = useState<ReviewQueue | null>(null);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const data = await api.get<ReviewQueue>("/api/practice/review-queue");
        if (!cancelled) setQueue(data);
      } catch {
        if (!cancelled) setQueue({ items: [], due_count: 0 });
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  if (!queue || queue.due_count === 0) return null;

  return (
    <section className="card" aria-labelledby="review-heading">
      <h2 id="review-heading">
        {t("review.title")}{" "}
        <span className="pill warning">{t("review.dueCount", { n: queue.due_count })}</span>
      </h2>
      <p className="muted">{t("review.intro")}</p>
      <ul className="plan-items">
        {queue.items.slice(0, 5).map((entry) => (
          <li key={entry.objective_id}>
            <span className="pill warning">{t(`review.reason.${entry.reason}`)}</span>
            <span>{entry.objective_title}</span>
            {entry.retrievability !== null ? (
              <span className="muted">
                {t("progress.recall", { n: Math.round(entry.retrievability * 100) })}
              </span>
            ) : null}
            <button
              type="button"
              className="secondary"
              onClick={() => onReview(entry.objective_id, null)}
            >
              {t("review.start")}
            </button>
          </li>
        ))}
      </ul>
    </section>
  );
}
