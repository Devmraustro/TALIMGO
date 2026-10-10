import { useCallback, useEffect, useState } from "react";
import { api, ApiError, type Dashboard, type Goal, type Me, type Plan } from "./lib/api";
import { direction, translator, type Locale, type StringKey } from "./lib/i18n";
import { AuthPanel } from "./components/AuthPanel";
import { DashboardPanel } from "./components/DashboardPanel";
import { DiagnosticPanel } from "./components/DiagnosticPanel";
import { GoalPanel } from "./components/GoalPanel";
import { PracticePanel } from "./components/PracticePanel";
import { ProgressPanel } from "./components/ProgressPanel";
import { RoadmapPanel } from "./components/RoadmapPanel";
import { SettingsPanel } from "./components/SettingsPanel";

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
    const data = await api.get<Dashboard>("/api/dashboard");
    setDashboard(data);
    setGoal(data.goal);
    return data;
  }, []);

  useEffect(() => {
    void (async () => {
      try {
        const current = await api.get<Me>("/api/auth/me");
        applyMe(current);
        await refreshDashboard();
        const activePlan = await api.get<Plan | null>("/api/plans/active");
        setPlan(activePlan);
        try {
          setAiStatus(await api.get<AiStatus>("/api/health/ai"));
        } catch {
          setAiStatus({ ai_enabled: false });
        }
      } catch (cause) {
        if (!(cause instanceof ApiError && cause.status === 401)) {
          setError(cause instanceof Error ? cause.message : "Unexpected error");
        }
      } finally {
        setBooting(false);
      }
    })();
  }, [applyMe, refreshDashboard]);

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
          objectiveId={dashboard?.next_action.objective_id ?? null}
          lessonId={dashboard?.next_action.lesson_id ?? null}
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
