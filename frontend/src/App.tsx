import { useCallback, useEffect, useState } from "react";
import {
  api,
  ApiError,
  onUnauthorized,
  type Dashboard,
  type Goal,
  type Me,
  type Plan,
  type Schedule,
} from "./lib/api";
import { direction, translator, type Locale, type StringKey } from "./lib/i18n";
import { AuthPanel } from "./components/AuthPanel";
import { DashboardPanel } from "./components/DashboardPanel";
import { DiagnosticPanel } from "./components/DiagnosticPanel";
import { GoalPanel } from "./components/GoalPanel";
import { PracticePanel } from "./components/PracticePanel";
import { ProgressPanel } from "./components/ProgressPanel";
import { RoadmapPanel } from "./components/RoadmapPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { TodayPanel } from "./components/TodayPanel";

type View = "dashboard" | "plan" | "practice" | "progress" | "settings";

interface AiStatus {
  ai_enabled: boolean;
  runtime_reachable?: boolean;
}

/**
 * Application shell: loads the session, then renders the learner's current step.
 *
 * The view is a small explicit state machine rather than a router library — there are five
 * destinations and one flow, and a dependency-free shell keeps the first release auditable.
 */
export function App() {
  const [locale, setLocale] = useState<Locale>("en");
  const [me, setMe] = useState<Me | null>(null);
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [plan, setPlan] = useState<Plan | null>(null);
  const [schedule, setSchedule] = useState<Schedule | null>(null);
  const [practiceTarget, setPracticeTarget] = useState<{ objectiveId: string; lessonId: string | null } | null>(
    null,
  );
  const [goal, setGoal] = useState<Goal | null>(null);
  const [view, setView] = useState<View>("dashboard");
  const [aiStatus, setAiStatus] = useState<AiStatus>({ ai_enabled: false });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [booting, setBooting] = useState(true);

  const t = useCallback(
    (key: StringKey, values?: Record<string, string | number>) => translator(locale)(key, values),
    [locale],
  );

  const applyMe = useCallback((next: Me) => {
    setMe(next);
    setLocale(next.profile.locale);
    document.documentElement.dataset.locale = next.profile.locale;
    document.documentElement.dataset.reducedMotion = String(next.profile.reduced_motion);
    document.documentElement.dir = direction(next.profile.locale);
    document.documentElement.lang = next.profile.locale;
  }, []);

  const refreshDashboard = useCallback(async () => {
    // The schedule is useful secondary context, but it must not hold the dashboard hostage on a
    // slow connection. Start the request immediately and let it update independently.
    void api
      .get<Schedule>("/api/plans/active/schedule")
      .then(setSchedule)
      .catch(() => setSchedule(null));

    try {
      const data = await api.get<Dashboard>("/api/dashboard");
      setDashboard(data);
      setGoal(data.goal);
      return data;
    } catch (cause) {
      // An expired session is handled once, by the `onUnauthorized` listener below; every other
      // failure belongs in the banner rather than in an unhandled promise rejection.
      if (!(cause instanceof ApiError && cause.status === 401)) {
        setError(cause instanceof Error ? cause.message : "Unexpected error");
      }
      return null;
    }
  }, []);

  useEffect(() => {
    void (async () => {
      try {
        const current = await api.get<Me>("/api/auth/me");
        applyMe(current);

        // Load the dashboard first. Plan and AI health are useful secondary reads and update
        // the UI independently, so neither can delay the first usable screen.
        void api
          .get<Plan | null>("/api/plans/active")
          .then(setPlan)
          .catch((cause: unknown) => {
            setPlan(null);
            if (!(cause instanceof ApiError && cause.status === 401)) {
              setError(cause instanceof Error ? cause.message : "Unexpected error");
            }
          });
        void api
          .get<AiStatus>("/api/health/ai")
          .then(setAiStatus)
          .catch(() => setAiStatus({ ai_enabled: false }));

        await refreshDashboard();
      } catch (cause) {
        if (!(cause instanceof ApiError && cause.status === 401)) {
          setError(cause instanceof Error ? cause.message : "Unexpected error");
        }
      } finally {
        setBooting(false);
      }
    })();
  }, [applyMe, refreshDashboard]);

  // Session expiry mid-use: the API answers 401 to a request the learner made while signed in. Return
  // to the sign-in screen with an explanation instead of leaving a screen whose actions all fail. The
  // listener only exists while a learner is signed in, so a 401 from the sign-in form (wrong password)
  // is never mistaken for an expired session.
  useEffect(() => {
    if (!me) return;
    return onUnauthorized(() => {
      setMe(null);
      setDashboard(null);
      setPlan(null);
      setGoal(null);
      setSchedule(null);
      setPracticeTarget(null);
      setView("dashboard");
      setError(t("auth.sessionExpired"));
    });
  }, [me, t]);

  async function signOut() {
    await api.post("/api/auth/logout");
    setMe(null);
    setDashboard(null);
    setPlan(null);
    setGoal(null);
    setView("dashboard");
  }

  function handlePrimaryAction() {
    const action = dashboard?.next_action;
    if (!action) return;
    // The diagnostic runs inline on the dashboard; everything else is practice-shaped.
    setPracticeTarget(
      action.objective_id ? { objectiveId: action.objective_id, lessonId: action.lesson_id } : null,
    );
    setView(action.kind === "diagnostic" ? "dashboard" : "practice");
  }

  if (booting) {
    return (
      <main className="app-shell" id="main">
        <p>{t("common.loading")}</p>
      </main>
    );
  }

  if (!me) {
    return (
      <main className="app-shell" id="main">
        <header className="site">
          <div className="brand">
            TALIMGO<span>{t("app.tagline")}</span>
          </div>
        </header>
        {error ? (
          <div className="error-banner" role="alert">
            {error}
          </div>
        ) : null}
        <AuthPanel
          t={t}
          onAuthenticated={(next) => {
            // A message left over from an expired session must not survive a fresh sign-in.
            setError(null);
            applyMe(next);
            void refreshDashboard();
          }}
        />
        <p className="notice">
          AI tutoring in TALIMGO runs only on TALIMGO&rsquo;s own servers using openly available models.
          Your study content is never sent to an external AI provider, and tutoring fails openly if the
          local model is unavailable.
        </p>
      </main>
    );
  }

  const needsGoal = !goal;
  const needsDiagnostic = Boolean(goal) && dashboard?.next_action.kind === "diagnostic";

  return (
    <main className="app-shell" id="main">
      <header className="site">
        <div className="brand">
          TALIMGO<span>{t("app.tagline")}</span>
        </div>
        <nav aria-label="Sections">
          {(["dashboard", "plan", "practice", "progress", "settings"] as View[]).map((target) => (
            <button
              key={target}
              type="button"
              className={view === target ? "button" : "ghost"}
              aria-current={view === target ? "page" : undefined}
              onClick={() => setView(target)}
            >
              {target === "dashboard"
                ? t("nav.dashboard")
                : target === "plan"
                  ? t("nav.plan")
                  : target === "practice"
                    ? t("nav.tutor")
                    : target === "progress"
                      ? t("nav.progress")
                      : t("nav.settings")}
            </button>
          ))}
          <button type="button" className="ghost" onClick={() => void signOut()}>
            {t("auth.logout")}
          </button>
        </nav>
      </header>

      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}

      {needsGoal && view !== "settings" ? (
        <GoalPanel
          t={t}
          onGoal={(created) => {
            setGoal(created);
            void refreshDashboard();
            setView("dashboard");
          }}
        />
      ) : null}

      {view === "dashboard" && !needsGoal ? (
        <>
          {needsDiagnostic ? (
            <DiagnosticPanel
              t={t}
              goalId={goal?.id ?? ""}
              onCompleted={() => {
                void refreshDashboard();
              }}
            />
          ) : (
            dashboard && (
              <DashboardPanel
                t={t}
                data={dashboard}
                busy={busy}
                onPrimaryAction={handlePrimaryAction}
              />
            )
          )}
          {!needsDiagnostic ? (
            <TodayPanel
              t={t}
              schedule={schedule}
              busy={busy}
              onStart={(item) => {
                setPracticeTarget({ objectiveId: item.objective_id, lessonId: item.lesson_id });
                setView("practice");
              }}
            />
          ) : null}
          {dashboard?.next_action.kind === "idle" && !needsDiagnostic ? (
            <RoadmapPanel
              t={t}
              goalId={goal?.id ?? null}
              plan={plan}
              onPlan={setPlan}
            />
          ) : null}
        </>
      ) : null}

      {view === "plan" && !needsGoal ? (
        <>
          {needsDiagnostic ? <div className="notice">{t("dashboard.startDiagnostic")}</div> : null}
          <RoadmapPanel t={t} goalId={goal?.id ?? null} plan={plan} onPlan={setPlan} />
        </>
      ) : null}

      {view === "practice" && !needsGoal ? (
        <PracticePanel
          t={t}
          objectiveId={practiceTarget?.objectiveId ?? dashboard?.next_action.objective_id ?? null}
          lessonId={practiceTarget?.lessonId ?? dashboard?.next_action.lesson_id ?? null}
          aiAvailable={Boolean(aiStatus.ai_enabled && aiStatus.runtime_reachable !== false)}
          onFinished={() => {
            setBusy(true);
            void refreshDashboard().finally(() => setBusy(false));
          }}
        />
      ) : null}

      {view === "progress" && !needsGoal ? <ProgressPanel t={t} /> : null}

      {view === "settings" ? (
        <SettingsPanel
          t={t}
          me={me}
          onProfile={(profile, consents) => {
            applyMe({ ...me, profile, consents });
          }}
          onLocale={(next) => {
            setLocale(next);
            document.documentElement.dir = direction(next);
          }}
          onDelete={() => {
            setMe(null);
            setDashboard(null);
          }}
        />
      ) : null}
    </main>
  );
}
