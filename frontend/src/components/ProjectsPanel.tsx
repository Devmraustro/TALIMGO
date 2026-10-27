import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api, ApiError, type Project, type ProjectSubmission } from "../lib/api";
import type { StringKey } from "../lib/i18n";
import { Markdown } from "./Markdown";

interface ProjectsPanelProps {
  t: (key: StringKey, values?: Record<string, string | number>) => string;
  goalId: string | null;
  /** Objective to open directly (from a build step); the learner can always go back to the list. */
  objectiveId?: string | null;
  planItemId?: string | null;
  onAccepted: () => void;
}

/**
 * The BUILD step of the learning loop: authored brief + rubric self-check. The server decides
 * acceptance deterministically (ADR 0008); this component only collects the artefact, the
 * reflection and the rubric attestations, and shows the exact gaps when work is not accepted yet.
 */
export function ProjectsPanel({ t, goalId, objectiveId, planItemId, onAccepted }: ProjectsPanelProps) {
  const [projects, setProjects] = useState<Project[] | null>(null);
  const [detail, setDetail] = useState<Project | null>(null);
  const [history, setHistory] = useState<ProjectSubmission[]>([]);
  const [checks, setChecks] = useState<Record<string, boolean>>({});
  const [artifact, setArtifact] = useState("");
  const [reflection, setReflection] = useState("");
  const [lastResult, setLastResult] = useState<ProjectSubmission | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadList = useCallback(async () => {
    try {
      const list = await api.get<Project[]>("/api/projects");
      setProjects(list);
    } catch {
      setProjects([]);
    }
  }, []);

  const open = useCallback(
    async (projectId: string) => {
      setBusy(true);
      setError(null);
      try {
        const [loadedDetail, mine] = await Promise.all([
          api.get<Project>(`/api/projects/${projectId}`),
          api.get<ProjectSubmission[]>("/api/projects/submissions/mine?limit=200"),
        ]);
        setDetail(loadedDetail);
        // Portfolio is latest-first; history reads oldest-first like a work log.
        setHistory(mine.filter((row) => row.project_id === projectId).reverse());
        setChecks({});
        setLastResult(null);
      } catch (cause) {
        setError(cause instanceof ApiError ? cause.message : t("auth.error"));
      } finally {
        setBusy(false);
      }
    },
    [t],
  );

  useEffect(() => {
    void loadList();
  }, [loadList]);

  useEffect(() => {
    if (!objectiveId || !projects) return;
    const match = projects.find((project) => project.objective_id === objectiveId);
    if (match) void open(match.id);
  }, [objectiveId, projects, open]);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!detail) return;
    setBusy(true);
    setError(null);
    try {
      const result = await api.post<ProjectSubmission>(`/api/projects/${detail.id}/submissions`, {
        artifact_text: artifact,
        reflection_text: reflection,
        rubric_checks: checks,
        goal_id: goalId,
        plan_item_id: planItemId ?? null,
      });
      setLastResult(result);
      setHistory((previous) => [...previous, result]);
      if (result.status === "accepted") onAccepted();
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : t("auth.error"));
    } finally {
      setBusy(false);
    }
  }

  if (projects === null) {
    return (
      <section className="card">
        <p>{t("common.loading")}</p>
      </section>
    );
  }

  if (!detail) {
    return (
      <section className="card" aria-labelledby="projects-heading">
        <h2 id="projects-heading">{t("projects.title")}</h2>
        <p className="muted">{t("projects.intro")}</p>
        {error ? (
          <div className="error-banner" role="alert">
            {error}
          </div>
        ) : null}
        {projects.length === 0 ? <p className="muted">{t("projects.empty")}</p> : null}
        <ul className="plan-items">
          {projects.map((project) => (
            <li key={project.id}>
              <span className="pill">build</span>
              <span>{project.title}</span>
              <span className="muted">{t("plan.minutes", { n: project.est_minutes })}</span>
              {project.my_status === "accepted" ? (
                <span className="pill success">{t("projects.accepted")}</span>
              ) : null}
              <button type="button" className="secondary" onClick={() => void open(project.id)}>
                {t("projects.open")}
              </button>
            </li>
          ))}
        </ul>
      </section>
    );
  }

  const missingLabel = (code: string): string => {
    const keyed = `projects.missing.${code}` as StringKey;
    const translated = t(keyed);
    if (translated !== keyed) return translated;
    const criterion = detail.rubric.find((entry) => entry.id === code);
    return criterion ? criterion.label : code;
  };

  return (
    <section className="card" aria-labelledby="project-heading">
      <button type="button" className="secondary" onClick={() => setDetail(null)}>
        {t("projects.back")}
      </button>
      <h2 id="project-heading">{detail.title}</h2>
      <p className="muted">
        {detail.objective_title} · {t("plan.minutes", { n: detail.est_minutes })}
      </p>

      <h3>{t("projects.brief")}</h3>
      <Markdown source={detail.brief_md} />

      {error ? (
        <div className="error-banner" role="alert">
          {error}
        </div>
      ) : null}

      {lastResult ? (
        <div role="status">
          <p>
            <span className={`pill ${lastResult.status === "accepted" ? "success" : "warning"}`}>
              {lastResult.status === "accepted" ? t("projects.accepted") : t("projects.needsWork")}
            </span>
          </p>
          {lastResult.status === "accepted" && lastResult.evidence_recorded ? (
            <p className="muted">{t("projects.evidenceRecorded")}</p>
          ) : null}
          {lastResult.status === "accepted" && lastResult.plan_item_id ? (
            <p className="muted">{t("projects.planCompleted")}</p>
          ) : null}
          {lastResult.missing_criteria.length > 0 ? (
            <>
              <p>
                <strong>{t("projects.missing")}</strong>
              </p>
              <ul>
                {lastResult.missing_criteria.map((code) => (
                  <li key={code}>{missingLabel(code)}</li>
                ))}
              </ul>
            </>
          ) : null}
        </div>
      ) : null}

      <form onSubmit={submit}>
        <h3>{t("projects.rubric")}</h3>
        <fieldset>
          <legend className="visually-hidden">{t("projects.rubric")}</legend>
          {detail.rubric.map((criterion) => (
            <label key={criterion.id} className="radio-row">
              <input
                type="checkbox"
                checked={checks[criterion.id] ?? false}
                onChange={(event) =>
                  setChecks((previous) => ({ ...previous, [criterion.id]: event.target.checked }))
                }
                disabled={busy}
              />
              <span>
                {criterion.label}{" "}
                <span className="muted">
                  ({criterion.required ? t("projects.required") : t("projects.optional")})
                </span>
              </span>
            </label>
          ))}
        </fieldset>

        <label htmlFor="artifact">{t("projects.artifact")}</label>
        <textarea
          id="artifact"
          rows={10}
          value={artifact}
          onChange={(event) => setArtifact(event.target.value)}
          disabled={busy}
        />
        <p className="muted">
          {t("projects.artifactMin", { n: detail.min_artifact_chars })} ·{" "}
          {t("projects.characters", { n: artifact.trim().length })}
        </p>

        <label htmlFor="reflection">{t("projects.reflection")}</label>
        <textarea
          id="reflection"
          rows={4}
          value={reflection}
          onChange={(event) => setReflection(event.target.value)}
          disabled={busy}
        />
        <p className="muted">
          {t("projects.artifactMin", { n: detail.min_reflection_chars })} ·{" "}
          {t("projects.characters", { n: reflection.trim().length })}
        </p>

        <button type="submit" disabled={busy || artifact.trim() === "" || reflection.trim() === ""}>
          {t("projects.submit")}
        </button>
      </form>

      {history.length > 0 ? (
        <>
          <h3>{t("projects.history")}</h3>
          <ul className="plan-items">
            {history.map((submission) => (
              <li key={submission.id}>
                <span className={`pill ${submission.status === "accepted" ? "success" : "warning"}`}>
                  {submission.status === "accepted"
                    ? t("projects.accepted")
                    : t("projects.needsWork")}
                </span>
                <span className="muted">
                  {new Date(submission.submitted_at).toLocaleDateString()} ·{" "}
                  {t("projects.characters", { n: submission.artifact_text.trim().length })}
                </span>
              </li>
            ))}
          </ul>
        </>
      ) : null}
    </section>
  );
}
