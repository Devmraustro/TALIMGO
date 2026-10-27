import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type FlashcardDeck } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface FlashcardsPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
}

type Rating = "again" | "good";

/**
 * Self-rated recall for items the learner has already met (the server restricts the pool to seen
 * items). Rating a card schedules the next review but never records mastery evidence — the copy
 * says so, and the server enforces it (flashcard ratings write no evidence at all; ADR 0009).
 */
export function FlashcardsPanel({ t }: FlashcardsPanelProps) {
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api.get<FlashcardDeck>("/api/practice/flashcards?limit=20");
      setDeck(data);
      setRevealed(false);
    } catch {
      setDeck({ cards: [], due_count: 0 });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const current = deck?.cards.find((card) => card.is_due) ?? null;

  async function rate(rating: Rating) {
    if (!current) return;
    setBusy(true);
    setError(null);
    try {
      await api.post(`/api/practice/flashcards/${current.item_id}/rate`, { rating });
      await load();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card" aria-labelledby="flashcards-heading">
      <h2 id="flashcards-heading">{t("flashcards.title")}</h2>
      <p className="muted">{t("flashcards.intro")}</p>
      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}
      {!deck ? (
        <p>{t("common.loading")}</p>
      ) : deck.cards.length === 0 ? (
        <p className="muted">{t("flashcards.empty")}</p>
      ) : !current ? (
        <p className="muted">{t("flashcards.done")}</p>
      ) : (
        <>
          <p className="muted">
            {current.objective_title} · {t("flashcards.due", { n: deck.due_count })}
          </p>
          <p>
            <strong>{current.prompt}</strong>
          </p>
          {!revealed ? (
            <button type="button" onClick={() => setRevealed(true)} disabled={busy}>
              {t("flashcards.showAnswer")}
            </button>
          ) : (
            <>
              <p aria-live="polite">
                <strong>{t("diagnostic.correctAnswer")}</strong>: {current.answer} —{" "}
                {current.explanation}
              </p>
              <div className="choice-row" role="group" aria-label={t("flashcards.title")}>
                {(["again", "good"] as Rating[]).map((rating) => (
                  <button
                    key={rating}
                    type="button"
                    className="secondary"
                    onClick={() => void rate(rating)}
                    disabled={busy}
                  >
                    {t(`flashcards.rate.${rating}`)}
                  </button>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </section>
  );
}
