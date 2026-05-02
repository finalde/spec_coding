import type {
  TreeResponse,
  FileResponse,
  FileError,
  Pin,
  PromotionsResponse,
} from "./types";

export async function fetchTree(): Promise<TreeResponse> {
  const res = await fetch("/api/tree", { headers: { Accept: "application/json" } });
  if (!res.ok) {
    throw new Error(`tree fetch failed: ${res.status}`);
  }
  return (await res.json()) as TreeResponse;
}

export type FetchFileResult =
  | { ok: true; data: FileResponse }
  | { ok: false; status: number; error: FileError };

export async function fetchFile(path: string): Promise<FetchFileResult> {
  const res = await fetch(`/api/file?path=${encodeURIComponent(path)}`, {
    headers: { Accept: "application/json" },
  });
  if (res.ok) {
    const data = (await res.json()) as FileResponse;
    return { ok: true, data };
  }
  let body: FileError = { error: `http_${res.status}` };
  try {
    body = (await res.json()) as FileError;
  } catch {
    // keep default
  }
  return { ok: false, status: res.status, error: body };
}

export type SaveFileResult =
  | { ok: true; bytes: number }
  | { ok: false; status: number; error: FileError };

export async function saveFile(path: string, text: string): Promise<SaveFileResult> {
  const res = await fetch("/api/file", {
    method: "PUT",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, text }),
  });
  if (res.ok) {
    const data = (await res.json()) as { bytes: number };
    return { ok: true, bytes: data.bytes };
  }
  let body: FileError = { error: `http_${res.status}` };
  try {
    body = (await res.json()) as FileError;
  } catch {
    // keep default
  }
  return { ok: false, status: res.status, error: body };
}

export interface StageModule {
  id: string;
  label: string;
  relative_path: string;
  description: string;
}

export interface StageDef {
  id: string;
  label: string;
  folder: string;
  invocation: string;
  modules: StageModule[];
}

export interface StagesResponse {
  project_type: string;
  project_name: string;
  stages: StageDef[];
}

export async function fetchStages(
  project_type: string,
  project_name: string,
): Promise<StagesResponse> {
  const params = new URLSearchParams({ project_type, project_name });
  const res = await fetch(`/api/stages?${params.toString()}`, {
    headers: { Accept: "application/json" },
  });
  if (!res.ok) {
    throw new Error(`stages fetch failed: ${res.status}`);
  }
  return (await res.json()) as StagesResponse;
}

export interface RegenPromptResponse {
  prompt: string;
  warning: string | null;
  selected_stages_count: number;
  follow_ups_count: number;
  autonomous: boolean;
  bytes: number;
}

export interface RegenPromptRequest {
  project_type: string;
  project_name: string;
  stages: string[];
  modules: Record<string, string[]>;
  autonomous: boolean;
}

export class RegenPromptError extends Error {
  status: number;
  body: FileError;
  constructor(status: number, body: FileError) {
    super(body.error || `regen_prompt_failed_${status}`);
    this.status = status;
    this.body = body;
  }
}

export async function buildRegenPrompt(
  req: RegenPromptRequest,
): Promise<RegenPromptResponse> {
  const res = await fetch("/api/regen-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  if (res.ok) {
    return (await res.json()) as RegenPromptResponse;
  }
  let body: FileError = { error: `http_${res.status}` };
  try {
    body = (await res.json()) as FileError;
  } catch {
    // keep default
  }
  throw new RegenPromptError(res.status, body);
}

export async function fetchPromotions(stagePath: string): Promise<PromotionsResponse> {
  const res = await fetch(
    `/api/promotions?stage_path=${encodeURIComponent(stagePath)}`,
    { headers: { Accept: "application/json" } },
  );
  if (!res.ok) {
    throw new Error(`promotions fetch failed: ${res.status}`);
  }
  return (await res.json()) as PromotionsResponse;
}

export async function addPromotion(
  stagePath: string,
  location: string,
  body: string,
): Promise<Pin> {
  const res = await fetch("/api/promote", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ stage_path: stagePath, location, body }),
  });
  if (!res.ok) {
    throw new Error(`promote failed: ${res.status}`);
  }
  return (await res.json()) as Pin;
}

export async function removePromotion(
  stagePath: string,
  pinId: string,
): Promise<void> {
  const res = await fetch("/api/promote", {
    method: "DELETE",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ stage_path: stagePath, pin_id: pinId }),
  });
  if (!res.ok) {
    throw new Error(`unpromote failed: ${res.status}`);
  }
}
