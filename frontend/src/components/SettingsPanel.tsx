import { useState } from "react";
import { api, ApiError, type Consent, type Me, type Profile } from "../lib/api";
import type { StringKey } from "../lib/i18n";

interface SettingsPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  me: Me;
  onProfile: (profile: Profile, consents: Consent[]) => void;
  onLocale: (locale: "en" | "ar") => void;
  onDelete: () => void;
}

export function SettingsPanel({ t, me, onProfile, onLocale, onDelete }: SettingsPanelProps) {
  const [weekly, setWeekly] = useState(me.profile.weekly_minutes);
  const [lowBandwidth, setLowBandwidth] = useState(me.profile.low_bandwidth);
  const [reducedMotion, setReducedMotion] = useState(me.profile.reduced_motion);
  const [aiConsent, setAiConsent] = useState(
    me.consents.find((consent) => consent.kind === "ai_processing")?.granted ?? false,
  );
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [password, setPassword] = useState("");

  async function save() {
    setError(null);
    try {
      const profile = await api.patch<Profile>("/api/me/profile", {
        weekly_minutes: weekly,
        low_bandwidth: lowBandwidth,
        reduced_motion: reducedMotion,
      });
      const consent = await api.post<Consent>("/api/me/consents", {
        kind: "ai_processing",
        granted: aiConsent,
      });
      const others = me.consents.filter((entry) => entry.kind !== "ai_processing");
      onProfile(profile, [...others, consent]);
      setStatus(t("settings.saved"));
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    }
  }

  async function changeLocale(locale: "en" | "ar") {
    try {
      const profile = await api.patch<Profile>("/api/me/profile", { locale });
      onProfile(profile, me.consents);
      onLocale(locale);
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    }
  }

  async function removeAccount() {
    setError(null);
    try {
      await api.post("/api/me/delete", { password, confirmation: "DELETE" });
      onDelete();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    }
  }

  return (
    <section className="card" aria-labelledby="settings-heading">
      <h2 id="settings-heading">{t("settings.title")}</h2>
      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}
      {status ? <p className="notice">{status}</p> : null}

      <label htmlFor="locale">{t("settings.locale")}</label>
      <select
        id="locale"
        value={me.profile.locale}
        onChange={(event) => void changeLocale(event.target.value as "en" | "ar")}
      >
        <option value="en">English</option>
        <option value="ar">العربية</option>
      </select>

      <label htmlFor="weekly">{t("settings.weeklyMinutes")}</label>
      <input
        id="weekly"
        type="number"
        min={30}
        max={3000}
        step={30}
        value={weekly}
        onChange={(event) => setWeekly(Number(event.target.value))}
      />

      <div className="option-row" style={{ marginTop: "var(--space-4)" }}>
        <input
          type="checkbox"
          id="low-bandwidth"
          checked={lowBandwidth}
          onChange={(event) => setLowBandwidth(event.target.checked)}
        />
        <label htmlFor="low-bandwidth">{t("settings.lowBandwidth")}</label>
      </div>

      <div className="option-row">
        <input
          type="checkbox"
          id="reduced-motion"
          checked={reducedMotion}
          onChange={(event) => setReducedMotion(event.target.checked)}
        />
        <label htmlFor="reduced-motion">{t("settings.reducedMotion")}</label>
      </div>

      <div className="option-row">
        <input
          type="checkbox"
          id="ai-consent-settings"
          checked={aiConsent}
          onChange={(event) => setAiConsent(event.target.checked)}
        />
        <label htmlFor="ai-consent-settings">{t("settings.aiConsent")}</label>
      </div>

      <div style={{ display: "flex", gap: "var(--space-3)", marginTop: "var(--space-4)" }}>
        <button type="button" onClick={() => void save()}>
          {t("settings.save")}
        </button>
        <a className="button secondary" href="/api/me/export" download="talimgo-data.json">
          {t("settings.export")}
        </a>
      </div>

      <hr style={{ margin: "var(--space-5) 0", border: "none", borderTop: "1px solid var(--border)" }} />

      <h3>{t("settings.delete")}</h3>
      <p className="muted">{t("settings.deleteWarning")}</p>
      <label htmlFor="delete-password">{t("auth.password")}</label>
      <input
        id="delete-password"
        type="password"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
        autoComplete="current-password"
      />
      <div style={{ marginTop: "var(--space-3)" }}>
        <button type="button" className="secondary" onClick={() => void removeAccount()} disabled={!password}>
          {t("settings.delete")}
        </button>
      </div>
    </section>
  );
}
