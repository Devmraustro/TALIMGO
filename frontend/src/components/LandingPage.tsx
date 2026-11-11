import { LogoMark } from "./LogoMark";
import type { Locale, StringKey } from "../lib/i18n";

/**
 * Public pre-launch landing page (master reference §20.1 messaging, MVP surface #1 in §15.3.2).
 *
 * Every claim here is defensible today: no user counts, no prices (DEC-008 open), no accreditation,
 * no invented testimonials. The Karim journey is labelled illustrative. The TALIMGO symbol is a
 * provisional mark pending DEC-001 clearance — it is not a released logo.
 *
 * The page is bilingual (EN/AR), RTL-native via logical properties in styles.css, and makes no
 * network calls: CTAs only switch views in the shell. `#how`/`#faq` are plain fragment links.
 */
interface LandingPageProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  locale: Locale;
  onLocale: (next: Locale) => void;
  onGetStarted: () => void;
  onSignIn: () => void;
}

const FAQ_KEYS = [
  ["landing.faq1Q", "landing.faq1A"],
  ["landing.faq2Q", "landing.faq2A"],
  ["landing.faq3Q", "landing.faq3A"],
  ["landing.faq4Q", "landing.faq4A"],
  ["landing.faq5Q", "landing.faq5A"],
  ["landing.faq6Q", "landing.faq6A"],
  ["landing.faq7Q", "landing.faq7A"],
  ["landing.faq8Q", "landing.faq8A"],
  ["landing.faq9Q", "landing.faq9A"],
  ["landing.faq10Q", "landing.faq10A"],
] as const satisfies readonly (readonly [StringKey, StringKey])[];

const STEP_KEYS = [
  ["landing.how1Title", "landing.how1Body"],
  ["landing.how2Title", "landing.how2Body"],
  ["landing.how3Title", "landing.how3Body"],
  ["landing.how4Title", "landing.how4Body"],
  ["landing.how5Title", "landing.how5Body"],
  ["landing.how6Title", "landing.how6Body"],
] as const satisfies readonly (readonly [StringKey, StringKey])[];

export function LandingPage({ t, locale, onLocale, onGetStarted, onSignIn }: LandingPageProps) {
  return (
    <>
      <header className="site landing-header">
        <div className="brand brand--lockup">
          <LogoMark size={30} className="brand-mark" />
          <span>TALIMGO</span>
        </div>
        <nav aria-label={t("landing.navLabel")}>
          <a className="ghost" href="#how">
            {t("landing.navHow")}
          </a>
          <a className="ghost" href="#faq">
            {t("landing.navFaq")}
          </a>
          <button type="button" className="ghost" onClick={onSignIn}>
            {t("landing.signin")}
          </button>
          <button type="button" onClick={onGetStarted}>
            {t("landing.cta")}
          </button>
          <div className="locale-toggle" role="group" aria-label={t("landing.language")}>
            <button
              type="button"
              aria-pressed={locale === "en"}
              onClick={() => onLocale("en")}
            >
              EN
            </button>
            <button
              type="button"
              aria-pressed={locale === "ar"}
              onClick={() => onLocale("ar")}
            >
              العربية
            </button>
          </div>
        </nav>
      </header>

      <main className="app-shell app-shell--landing" id="main">
        {/* Hero — one primary action, one supporting link (§9.1, principle 1) */}
        <section className="landing-hero" aria-labelledby="hero-title">
          <div>
            <p className="landing-eyebrow">{t("landing.status")}</p>
            <h1 className="hero-title" id="hero-title">
              {t("landing.headline")}
            </h1>
            <p className="hero-sub">{t("landing.subhead")}</p>
            <p className="hero-lede">{t("landing.lede")}</p>
            <div className="cta-row">
              <button type="button" onClick={onGetStarted}>
                {t("landing.cta")}
              </button>
              <a className="button secondary" href="#how">
                {t("landing.secondary")}
              </a>
            </div>
          </div>

          {/* Decorative, non-functional preview; aria-hidden — the journey section below carries the
              accessible equivalent. No fabricated metrics: 62% is the illustration, labelled as such. */}
          <div>
            <div className="plan-preview" aria-hidden="true">
              <div className="plan-preview-head">{t("landing.previewGoal")}</div>
              <p className="plan-preview-goal">{t("landing.previewGoalValue")}</p>
              <div className="pp-row">
                <span className="pill success">✓</span>
                <span>{t("landing.previewMilestone1")}</span>
              </div>
              <div className="pp-row">
                <span className="pill warning">●</span>
                <span>{t("landing.previewMilestone2")}</span>
              </div>
              <div className="pp-bar">
                <div className="pp-bar-fill" />
              </div>
              <div className="pp-row">
                <span className="pill">○</span>
                <span>{t("landing.previewMilestone3")}</span>
              </div>
              <p className="pp-evidence">{t("landing.previewEvidence")}</p>
            </div>
            <p className="preview-caption">{t("landing.previewCaption")}</p>
          </div>
        </section>

        {/* Three defensible value propositions (§20.1.1) */}
        <section className="landing-section" aria-labelledby="value-title">
          <h2 id="value-title">{t("landing.valueTitle")}</h2>
          <div className="value-grid">
            {[
              ["01", "landing.value1Title", "landing.value1Body"],
              ["02", "landing.value2Title", "landing.value2Body"],
              ["03", "landing.value3Title", "landing.value3Body"],
            ].map(([index, titleKey, bodyKey]) => (
              <article className="value-card" key={index}>
                <div className="value-index">{index}</div>
                <h3>{t(titleKey as StringKey)}</h3>
                <p>{t(bodyKey as StringKey)}</p>
              </article>
            ))}
          </div>
        </section>

        {/* Six-step mechanism, plain language (§20.1.1) */}
        <section className="landing-section" id="how" aria-labelledby="how-title">
          <h2 id="how-title">{t("landing.howTitle")}</h2>
          <ol className="how-steps">
            {STEP_KEYS.map(([titleKey, bodyKey]) => (
              <li className="how-step" key={titleKey}>
                <div>
                  <h3>{t(titleKey)}</h3>
                  <p>{t(bodyKey)}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>

        {/* Labelled illustrative journey (§20.1.1 — never presented as a real user) */}
        <section className="landing-section" aria-labelledby="journey-title">
          <h2 id="journey-title">{t("landing.journeyTitle")}</h2>
          <blockquote className="journey-quote">{t("landing.journeyBody")}</blockquote>
          <p className="caption">{t("landing.journeyLabel")}</p>
        </section>

        {/* Trust statement: what we won't do / what you control (§20.1.1) */}
        <section className="landing-section" aria-labelledby="trust-title">
          <h2 id="trust-title">{t("landing.trustTitle")}</h2>
          <div className="trust-grid">
            <div className="trust-card">
              <h3>{t("landing.trustWontTitle")}</h3>
              <ul>
                <li>{t("landing.trustWont")}</li>
              </ul>
            </div>
            <div className="trust-card">
              <h3>{t("landing.trustControlTitle")}</h3>
              <ul>
                <li>{t("landing.trustControl")}</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Honest answers — no price until DEC-008 closes (§20.1.1) */}
        <section className="landing-section" id="faq" aria-labelledby="faq-title">
          <h2 id="faq-title">{t("landing.faqTitle")}</h2>
          <div className="faq-list">
            {FAQ_KEYS.map(([q, a]) => (
              <details className="faq-item" key={q}>
                <summary>{t(q)}</summary>
                <p>{t(a)}</p>
              </details>
            ))}
          </div>
        </section>

        {/* Repeat the one primary action; nothing else competes (§9.1) */}
        <div className="landing-cta-band">
          <h2>{t("landing.ctaBandTitle")}</h2>
          <p>{t("landing.ctaBandBody")}</p>
          <button type="button" onClick={onGetStarted}>
            {t("landing.cta")}
          </button>
        </div>

        <footer className="landing-footer">
          <p>{t("landing.localAi")}</p>
          <p>{t("landing.devNote")}</p>
          <p>{t("landing.rights")}</p>
        </footer>
      </main>
    </>
  );
}
