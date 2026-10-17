import { useState, type FormEvent } from "react";
import { api, ApiError, type Me } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface AuthPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  onAuthenticated: (me: Me) => void;
}

export function AuthPanel({ t, onAuthenticated }: AuthPanelProps) {
  const [mode, setMode] = useState<"register" | "login">("register");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [aiConsent, setAiConsent] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const me =
        mode === "register"
          ? await api.post<Me>("/api/auth/register", {
              email,
              password,
              display_name: displayName,
              accept_terms: acceptTerms,
              accept_ai_processing: aiConsent,
            })
          : await api.post<Me>("/api/auth/login", { email, password });
      onAuthenticated(me);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <h2>{mode === "register" ? t("auth.title") : t("auth.loginTitle")}</h2>
      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}

      <form onSubmit={submit}>
        <label htmlFor="email">{t("auth.email")}</label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(event) => setEmail(event.target.value)}
        />

        <label htmlFor="password">{t("auth.password")}</label>
        <input
          id="password"
          type="password"
          autoComplete={mode === "register" ? "new-password" : "current-password"}
          required
          minLength={mode === "register" ? 10 : 1}
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          aria-describedby={mode === "register" ? "password-help" : undefined}
        />
        {mode === "register" ? (
          <p className="muted" id="password-help">
            {t("auth.passwordHelp")}
          </p>
        ) : null}

        {mode === "register" ? (
          <>
            <label htmlFor="displayName">{t("auth.displayName")}</label>
            <input
              id="displayName"
              type="text"
              autoComplete="nickname"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
            />

            <div className="option-row" style={{ marginTop: "var(--space-4)" }}>
              <input
                type="checkbox"
                id="terms"
                checked={acceptTerms}
                onChange={(event) => setAcceptTerms(event.target.checked)}
                required
              />
              <label htmlFor="terms">{t("auth.terms")}</label>
            </div>
            <div className="option-row">
              <input
                type="checkbox"
                id="ai-consent"
                checked={aiConsent}
                onChange={(event) => setAiConsent(event.target.checked)}
              />
              <label htmlFor="ai-consent">{t("auth.aiConsent")}</label>
            </div>
          </>
        ) : null}

        <div style={{ marginTop: "var(--space-4)", display: "flex", gap: "var(--space-3)" }}>
          <button type="submit" disabled={busy}>
            {mode === "register" ? t("auth.submit") : t("auth.login")}
          </button>
          <button
            type="button"
            className="ghost"
            onClick={() => {
              setMode(mode === "register" ? "login" : "register");
              setError(null);
            }}
          >
            {mode === "register" ? t("auth.switchToLogin") : t("auth.switchToRegister")}
          </button>
        </div>
      </form>
    </div>
  );
}
