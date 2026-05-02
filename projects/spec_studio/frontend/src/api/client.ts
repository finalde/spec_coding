import type {
  Adjustments,
  Artifact,
  ArtifactKind,
  ArtifactSaveResult,
  CreateTaskInput,
  EditableArtifactKind,
  InputBundle,
  InterviewAnswers,
  InterviewQA,
  RunHandle,
  Task,
  TaskSummary,
} from "@/types";

const BASE = "/api";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init.headers ?? {}),
    },
  });
  if (!res.ok) {
    const text = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${text}`);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  rootFolders: () => request<string[]>("/enums/root-folders"),
  listTasks: () => request<TaskSummary[]>("/tasks"),
  createTask: (input: CreateTaskInput) =>
    request<Task>("/tasks", { method: "POST", body: JSON.stringify(input) }),
  getTask: (taskId: string) => request<Task>(`/tasks/${taskId}`),

  startPhase: (taskId: string, phase: string) =>
    request<RunHandle>(`/tasks/${taskId}/${phase}/start`, { method: "POST" }),

  submitInterviewAnswers: (taskId: string, body: InterviewAnswers) =>
    request<Task>(`/tasks/${taskId}/interview/answers`, {
      method: "POST",
      body: JSON.stringify(body),
    }),
  saveAdjustments: (taskId: string, body: Adjustments) =>
    request<Task>(`/tasks/${taskId}/adjustments`, {
      method: "POST",
      body: JSON.stringify(body),
    }),

  getArtifact: (taskId: string, kind: ArtifactKind) =>
    request<Artifact>(`/tasks/${taskId}/artifacts/${kind}`),
  putArtifact: (
    taskId: string,
    kind: EditableArtifactKind,
    content: string,
    ifMatch?: string,
  ) =>
    request<ArtifactSaveResult>(`/tasks/${taskId}/artifacts/${kind}`, {
      method: "PUT",
      body: JSON.stringify({ content, if_match: ifMatch ?? null }),
    }),

  getInputs: (taskId: string) => request<InputBundle>(`/tasks/${taskId}/inputs`),

  putInput: (
    name: "claude_md" | "skill_md",
    content: string,
    confirm: boolean,
    ifMatch?: string,
  ) =>
    request<ArtifactSaveResult>(`/inputs/${name}`, {
      method: "PUT",
      body: JSON.stringify({ content, confirm, if_match: ifMatch ?? null }),
    }),

  putAgent: (
    agentName: string,
    content: string,
    confirm: boolean,
    ifMatch?: string,
  ) =>
    request<ArtifactSaveResult>(`/agents/${agentName}`, {
      method: "PUT",
      body: JSON.stringify({ content, confirm, if_match: ifMatch ?? null }),
    }),

  getInterview: (taskId: string) => request<InterviewQA>(`/tasks/${taskId}/interview`),
  putInterview: (taskId: string, body: InterviewQA) =>
    request<ArtifactSaveResult>(`/tasks/${taskId}/interview`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
};
