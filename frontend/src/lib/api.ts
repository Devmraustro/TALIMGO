/**
 * API client.
 *
 * Rules kept here centrally:
 *  - every request is same-origin (`/api/...`), so session cookies work and no CORS dance is needed;
 *  - errors surface as `ApiError` with the server's message, never a stack trace;
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

const JSON_HEADERS = { "content-type": "application/json" };

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: init.body ? { ...JSON_HEADERS, ...(init.headers ?? {}) } : init.headers,
    ...init,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const text = await response.text();
  const payload = text ? safeJson(text) : null;

  if (!response.ok) {
    throw new ApiError(extractMessage(payload, response.status), response.status);
  }
  return payload as T;
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

export interface Item {
  id: string;
  objective_id: string;
  kind: "mcq_single" | "short_answer";
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
  item: Item | null;
  answered: number;
  /** The completion target frozen when the session was created; `total` is its display alias. */
  target_items: number;
  total: number;
  feedback: AnswerFeedback | null;
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
