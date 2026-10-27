/**
 * API client.
 *
 * Rules kept here centrally:
 *  - every request is same-origin (`/api/...`), so session cookies work and no CORS dance is needed;
 *    the session cookie is `SameSite=Lax`, so a cross-origin API origin cannot work by configuration
 *    alone — the production interface must be served from the same origin as the API, or from a host
 *    that proxies `/api` to it (see docs/DEPLOYMENT.md, "Frontend hosting topologies");
 *  - errors surface as `ApiError` with the server's message, never a stack trace;
 *  - a failure that is *not* a TALIMGO API response (network error, or a static host answering the
 *    path itself) is reported as such instead of as a bare status code, because that is what an
 *    interface deployed without its API looks like from the learner's side;
 *  - nothing in the frontend ever calls a model or an external host: the backend owns inference.
 */

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Status used when no HTTP response arrived at all (DNS/TLS/offline). */
export const NO_RESPONSE = 0;

const JSON_HEADERS = { "content-type": "application/json" };

/**
 * Called when an authenticated request answers 401, so the app can return the learner to the sign-in
 * screen instead of leaving a stale dashboard on screen. Registered by `App` while signed in; a 401
 * from the sign-in form itself is therefore never treated as an expired session.
 */
type UnauthorizedHandler = () => void;
let unauthorizedHandler: UnauthorizedHandler | null = null;

export function onUnauthorized(handler: UnauthorizedHandler): () => void {
  unauthorizedHandler = handler;
  return () => {
    if (unauthorizedHandler === handler) unauthorizedHandler = null;
  };
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(path, {
      credentials: "same-origin",
      headers: init.body ? { ...JSON_HEADERS, ...(init.headers ?? {}) } : init.headers,
      ...init,
    });
  } catch {
    // The request never produced a response: offline, blocked, or no server on this origin.
    throw new ApiError(NETWORK_MESSAGE, NO_RESPONSE);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const payload = text ? safeJson(text) : null;

  if (!response.ok) {
    if (!payload) {
      // A TALIMGO API error is always JSON. Anything else on an `/api/...` path means the request did
      // not reach TALIMGO: a static host, a proxy or an error page answered it instead.
      throw new ApiError(notTheApiMessage(response.status), response.status);
    }
    if (response.status === 401) unauthorizedHandler?.();
    throw new ApiError(extractMessage(payload, response.status), response.status);
  }
  return payload as T;
}

const NETWORK_MESSAGE =
  "TALIMGO's API could not be reached from this browser. Check your connection and try again.";

function notTheApiMessage(status: number): string {
  return (
    `TALIMGO's API did not answer this request (HTTP ${status}). This interface may be deployed ` +
    "without an API behind it, in which case no account action can work here."
  );
}

function safeJson(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function extractMessage(payload: unknown, status: number): string {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (detail && typeof detail === "object" && "problems" in detail) {
      const problems = (detail as { problems: unknown }).problems;
      if (Array.isArray(problems)) return problems.join(" ");
    }
    if (detail && typeof detail === "object" && "errors" in detail) {
      return "The generated plan did not pass validation and was not saved.";
    }
  }
  return `Request failed (${status}).`;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body === undefined ? undefined : JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    request<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
};

// --------------------------------------------------------------------------------------
// Types shared with the backend schemas (kept minimal on purpose)
// --------------------------------------------------------------------------------------

export interface User {
  id: string;
  email: string;
  display_name: string;
  role: string;
  created_at: string;
}

export interface Profile {
  locale: "en" | "ar";
  weekly_minutes: number;
  availability_days: string[];
  target_date: string | null;
  low_bandwidth: boolean;
  reduced_motion: boolean;
  onboarding_completed_at: string | null;
}

export interface Consent {
  kind: string;
  granted: boolean;
  recorded_at: string;
}

export interface Me {
  user: User;
  profile: Profile;
  consents: Consent[];
}

export interface PathSummary {
  id: string;
  title_en: string;
  title_ar: string;
  summary_en: string;
  summary_ar: string;
  objective_count: number;
  estimated_hours: number;
}

export interface Goal {
  id: string;
  path_id: string;
  statement: string;
  motivation: string;
  target_date: string | null;
  weekly_minutes: number;
  status: string;
  created_at: string;
}

export interface ItemOption {
  id: string;
  text: string;
}

export type ItemKind =
  | "mcq_single"
  | "mcq_multi"
  | "short_answer"
  | "numeric"
  | "ordering"
  | "true_false";

export interface Item {
  id: string;
  objective_id: string;
  kind: ItemKind;
  prompt: string;
  options: ItemOption[] | null;
  difficulty: number;
}

export interface AnswerFeedback {
  is_correct: boolean;
  correct_answer: string;
  explanation: string;
  objective_id: string;
  objective_title: string;
}

export interface DiagnosticState {
  attempt_id: string;
  goal_id: string;
  status: string;
  total_items: number;
  answered_items: number;
  current_item: Item | null;
  placement: { summary?: Record<string, number>; note?: string } | null;
}

export interface DiagnosticAnswerResult {
  feedback: AnswerFeedback;
  completed: boolean;
  placement: { summary?: Record<string, number>; note?: string } | null;
  next_item: Item | null;
  answered_items: number;
  total_items: number;
}

export interface PlanItem {
  id: string;
  order_index: number;
  objective_id: string;
  objective_title: string;
  lesson_id: string | null;
  kind: string;
  est_minutes: number;
  status: string;
  rationale: string;
}

export interface PlanWeek {
  week_number: number;
  theme: string;
  items: PlanItem[];
  total_minutes: number;
}

export interface Plan {
  id: string;
  goal_id: string;
  version: number;
  status: string;
  generator: string;
  total_estimated_minutes: number;
  validation_report: { ok?: boolean; checked?: string[] };
  created_at: string;
  weeks: PlanWeek[];
}

export interface ScheduleItem {
  id: string;
  order_index: number;
  objective_id: string;
  objective_title: string;
  kind: "learn" | "practice" | "assess" | "review" | "build";
  lesson_id: string | null;
  est_minutes: number;
  status: string;
  scheduled_day: number;
  scheduled_for: string;
  completed_at: string | null;
  rationale: string;
}

export interface Schedule {
  plan_id: string;
  version: number;
  starts_on: string;
  daily_minutes: number;
  total_estimated_minutes: number;
  weeks: { week_number: number; theme: string; items: ScheduleItem[] }[];
  today: { date: string; items: ScheduleItem[]; minutes_planned: number };
  adherence: {
    counts: { on_time: number; late: number; overdue: number; pending: number };
    minutes: { on_time: number; late: number; overdue: number; actual?: number };
    total_items: number;
    completed_items: number;
    adherence_percent: number;
    behind_schedule: boolean;
  };
}

export interface NextAction {
  kind: "learn" | "practice" | "assess" | "review" | "build" | "diagnostic" | "idle";
  title: string;
  objective_id: string | null;
  lesson_id: string | null;
  plan_item_id: string | null;
  est_minutes: number;
  rationale: string;
  evidence_basis: string;
}

export interface Dashboard {
  goal: Goal | null;
  next_action: NextAction;
  mastery_summary: Record<string, number>;
  recent_evidence: {
    objective_id: string;
    objective_title: string;
    outcome: string;
    assisted: boolean;
    kind: string;
    occurred_at: string;
  }[];
  blockers: string[];
}

export interface Lesson {
  id: string;
  objective_id: string;
  title: string;
  body_md: string;
  est_minutes: number;
}

export interface PracticeSession {
  session_id: string;
  objective_id: string;
  status: "in_progress" | "completed" | "abandoned";
  mode: "practice" | "review";
  item: Item | null;
  answered: number;
  /** The completion target frozen when the session was created; `total` is its display alias. */
  target_items: number;
  total: number;
  feedback: AnswerFeedback | null;
}

export interface ProjectRubricCriterion {
  id: string;
  label: string;
  required: boolean;
}

export interface ProjectSummary {
  id: string;
  objective_id: string;
  title: string;
  est_minutes: number;
}

export interface ProjectDetail extends ProjectSummary {
  brief_md: string;
  rubric: ProjectRubricCriterion[];
  min_artifact_chars: number;
  min_reflection_chars: number;
}

export interface ProjectSubmission {
  id: string;
  project_id: string;
  objective_id: string;
  status: string;
  rubric_checks: Record<string, boolean>;
  missing: string[];
  artifact_chars: number;
  reflection_chars: number;
  /** Only present on the POST response. */
  evidence_recorded?: boolean;
  plan_item_completed?: boolean;
  created_at: string;
}

export interface ReviewQueueEntry {
  objective_id: string;
  title: string;
  lesson_id: string | null;
  reason: "fading" | "confirmation_spaced";
  retrievability: number;
  next_due_at: string | null;
}

export interface ReviewQueue {
  due: ReviewQueueEntry[];
  due_count: number;
  confirmed_count: number;
}

export interface Flashcard {
  item: Item;
  objective_id: string;
  repetitions: number;
  interval_days: number;
  due_at: string | null;
  last_rating: string;
}

export interface FlashcardDeck {
  due: Flashcard[];
  due_count: number;
  total_cards: number;
}

export interface TutorReply {
  thread_id: string;
  reply: string;
  hint_level: number;
  citations: string[];
  model: string;
  duration_ms: number;
  validation: Record<string, unknown>;
}

export interface MasteryRow {
  objective_id: string;
  title: string;
  phase: "acquiring" | "retaining";
  unassisted_successes: number;
  retrievability: number | null;
  stability_days: number | null;
  needs_review: boolean;
  last_evidence_at: string | null;
  evidence_count: number;
}
