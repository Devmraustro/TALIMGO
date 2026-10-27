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
import { FlashcardsPanel } from "./components/FlashcardsPanel";
import { GoalPanel } from "./components/GoalPanel";
import { HelpPanel } from "./components/HelpPanel";
import { PracticePanel } from "./components/PracticePanel";
import { ProgressPanel } from "./components/ProgressPanel";
import { ProjectsPanel } from "./components/ProjectsPanel";
import { ReviewPanel } from "./components/ReviewPanel";
import { RoadmapPanel } from "./components/RoadmapPanel";
import { SettingsPanel } from "./components/SettingsPanel";
import { TodayPanel } from "./components/TodayPanel";

type View = "dashboard" | "plan" | "practice" | "projects" | "progress" | "settings" | "help";

const VIEWS: View[] = ["dashboard", "plan", "practice", "projects", "progress", "settings", "help"];

/** Hash routes (`#/projects`) make every destination deep-linkable and back-button friendly
 * without a router dependency or any server rewrite rule. */
function viewFromHash(): View {
  const candidate = window.location.hash.replace(/^#\/?/, "") as View;
  return VIEWS.includes(candidate) ? candidate : "dashboard";
}

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
  const [practiceTarget, setPracticeTarget] = useState<{
    objectiveId: string;
    lessonId: string | null;
    planItemId?: string | null;
    mode?: "practice" | "review";
  } | null>(null);
  const [projectTarget, setProjectTarget] = useState<{
    objectiveId: string;
    planItemId: string | null;
  } | null>(null);
  const [goal, setGoal] = useState<Goal | null>(null);
  const [view, setView] = useState<View>(() => viewFromHash());
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

  const navigate = useCallback((target: View) => {
    setView(target);
    if (viewFromHash() !== target) window.location.hash = `#/${target}`;
  }, []);

  useEffect(() => {
    const onHashChange = () => setView(viewFromHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

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
      setProjectTarget(null);
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
    setPracticeTarget(null);
    setProjectTarget(null);
    navigate("dashboard");
  }

  function startOnObjective(
    kind: string,
    objectiveId: string,
    lessonId: string | null,
    planItemId: string | null,
  ) {
    // A build step is done in the project workspace, never as a quiz; everything else opens
    // practice, carrying the plan item so finishing the session ticks the roadmap step off.
    if (kind === "build") {
      setProjectTarget({ objectiveId, planItemId });
      navigate("projects");
      return;
    }
    setPracticeTarget({
      objectiveId,
      lessonId,
      planItemId,
      mode: kind === "review" ? "review" : "practice",
    });
    navigate("practice");
  }

  function handlePrimaryAction() {
    const action = dashboard?.next_action;
    if (!action?.objective_id) return;
    // The diagnostic runs inline on the dashboard; everything else routes by kind.
    if (action.kind === "diagnostic") {
      navigate("dashboard");
      return;
    }
    startOnObjective(action.kind, action.objective_id, action.lesson_id, action.plan_item_id);
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

  // Opening the practice view directly (nav, bookmark) falls back to the recommended action,
  // including its plan item, so a finished session still completes the roadmap step.
  const activePractice =
    practiceTarget ??
    (dashboard?.next_action.objective_id
      ? {
          objectiveId: dashboard.next_action.objective_id,
          lessonId: dashboard.next_action.lesson_id,
          planItemId: dashboard.next_action.plan_item_id,
          mode: (dashboard.next_action.kind === "review" ? "review" : "practice") as
            | "practice"
            | "review",
        }
      : null);

  return (
    <main className="app-shell" id="main">
      <header className="site">
        <div className="brand">
          TALIMGO<span>{t("app.tagline")}</span>
        </div>
        <nav aria-label={t("nav.sections")}>
          {VIEWS.map((target) => (
            <button
              key={target}
              type="button"
              className={view === target ? "button" : "ghost"}
              aria-current={view === target ? "page" : undefined}
              onClick={() => navigate(target)}
            >
              {target === "dashboard"
                ? t("nav.dashboard")
                : target === "plan"
                  ? t("nav.plan")
                  : target === "practice"
                    ? t("nav.tutor")
                    : target === "projects"
                      ? t("nav.projects")
                      : target === "progress"
                        ? t("nav.progress")
                        : target === "settings"
                          ? t("nav.settings")
                          : t("nav.help")}
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
            navigate("dashboard");
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
                startOnObjective(item.kind, item.objective_id, item.lesson_id, item.id);
              }}
            />
          ) : null}
          {!needsDiagnostic ? (
            <ReviewPanel
              t={t}
              onReview={(objectiveId, lessonId) => {
                setPracticeTarget({ objectiveId, lessonId, mode: "review" });
                navigate("practice");
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
        <>
          <PracticePanel
            t={t}
            objectiveId={activePractice?.objectiveId ?? null}
            lessonId={activePractice?.lessonId ?? null}
            planItemId={activePractice?.planItemId ?? null}
            goalId={goal?.id ?? null}
            mode={activePractice?.mode ?? "practice"}
            aiAvailable={Boolean(aiStatus.ai_enabled && aiStatus.runtime_reachable !== false)}
            onFinished={() => {
              setBusy(true);
              void refreshDashboard().finally(() => setBusy(false));
            }}
          />
          <FlashcardsPanel t={t} />
        </>
      ) : null}

      {view === "projects" && !needsGoal ? (
        <ProjectsPanel
          t={t}
          goalId={goal?.id ?? null}
          objectiveId={projectTarget?.objectiveId ?? null}
          planItemId={projectTarget?.planItemId ?? null}
          onAccepted={() => {
            setBusy(true);
            void refreshDashboard().finally(() => setBusy(false));
          }}
        />
      ) : null}

      {view === "progress" && !needsGoal ? <ProgressPanel t={t} /> : null}

      {view === "help" ? <HelpPanel t={t} /> : null}

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
