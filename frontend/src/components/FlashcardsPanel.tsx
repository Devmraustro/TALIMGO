import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type Flashcard, type FlashcardDeck } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface FlashcardsPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
}

type Rating = "again" | "hard" | "good" | "easy";

/**
 * Self-rated recall for items the learner has already met. Rating a card schedules the next
 * review but never records mastery evidence — the copy says so, and the server enforces it
 * (flashcard ratings write no evidence at all; see the review service).
 */
export function FlashcardsPanel({ t }: FlashcardsPanelProps) {
  const [deck, setDeck] = useState<FlashcardDeck | null>(null);
  const [revealed, setRevealed] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const data = await api.get<FlashcardDeck>("/api/practice/flashcards?limit=10");
      setDeck(data);
      setRevealed(false);
    } catch {
      setDeck({ due: [], due_count: 0, total_cards: 0 });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const current: Flashcard | null = deck?.due[0] ?? null;

  function reveal() {
    // The answer itself is fetched by AnswerReveal; the key never travels with the question.
    setRevealed(true);
  }

  async function rate(rating: Rating) {
    if (!current) return;
    setBusy(true);
    setError(null);
    try {
      await api.post(`/api/practice/flashcards/${current.item.id}/rate`, { rating });
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
      ) : deck.total_cards === 0 ? (
        <p className="muted">{t("flashcards.empty")}</p>
      ) : !current ? (
        <p className="muted">{t("flashcards.done")}</p>
      ) : (
        <>
          <p className="muted">{t("flashcards.due", { n: deck.due_count })}</p>
          <p>
            <strong>{current.item.prompt}</strong>
          </p>
          {!revealed ? (
            <button type="button" onClick={() => void reveal()} disabled={busy}>
              {t("flashcards.showAnswer")}
            </button>
          ) : (
            <AnswerReveal t={t} itemId={current.item.id} />
          )}
          {revealed ? (
            <div className="choice-row" role="group" aria-label={t("flashcards.title")}>
              {(["again", "hard", "good", "easy"] as Rating[]).map((rating) => (
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
          ) : null}
        </>
      )}
    </section>
  );
}

function AnswerReveal({
  t,
  itemId,
}: {
  t: FlashcardsPanelProps["t"];
  itemId: string;
}) {
  const [answer, setAnswer] = useState<string | null>(null);
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const data = await api.get<{ answer: string; explanation: string }>(
          `/api/practice/flashcards/${itemId}/answer`,
        );
        if (!cancelled) setAnswer(`${data.answer} — ${data.explanation}`);
      } catch {
        if (!cancelled) setAnswer(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [itemId]);
  return answer ? (
    <p aria-live="polite">
      <strong>{t("diagnostic.correctAnswer")}</strong>: {answer}
    </p>
  ) : (
    <p>{t("common.loading")}</p>
  );
}
