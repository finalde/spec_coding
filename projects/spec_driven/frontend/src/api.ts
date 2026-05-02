import type { FileError, FileResponse, TreeResponse } from "./types";

export async function fetchTree(): Promise<TreeResponse> {
  const resp = await fetch("/api/tree");
  if (!resp.ok) {
    throw new Error(`tree fetch failed: ${resp.status}`);
  }
  return (await resp.json()) as TreeResponse;
}

export type FileResult =
  | { ok: true; data: FileResponse }
  | { ok: false; status: number; error: FileError };

export async function fetchFile(path: string): Promise<FileResult> {
  const resp = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  if (resp.ok) {
    return { ok: true, data: (await resp.json()) as FileResponse };
  }
  let body: FileError;
  try {
    body = (await resp.json()) as FileError;
  } catch {
    body = { error: "unknown" };
  }
  return { ok: false, status: resp.status, error: body };
}

export type SaveResult =
  | { ok: true; bytes: number }
  | { ok: false; status: number; error: FileError };

export async function saveFile(path: string, text: string): Promise<SaveResult> {
  const resp = await fetch("/api/file", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, text }),
  });
  if (resp.ok) {
    const data = (await resp.json()) as { bytes: number };
    return { ok: true, bytes: data.bytes };
  }
  let body: FileError;
  try {
    body = (await resp.json()) as FileError;
  } catch {
    body = { error: "unknown" };
  }
  return { ok: false, status: resp.status, error: body };
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
  projectType: string,
  projectName: string,
): Promise<StagesResponse> {
  const resp = await fetch(
    `/api/stages?project_type=${encodeURIComponent(projectType)}&project_name=${encodeURIComponent(projectName)}`,
  );
  if (!resp.ok) {
    throw new Error(`stages fetch failed: ${resp.status}`);
  }
  return (await resp.json()) as StagesResponse;
}

export interface RegenPromptRequest {
  project_type: string;
  project_name: string;
  stages: string[];
  modules: Record<string, string[]>;
  autonomous: boolean;
}

export async function buildRegenPrompt(req: RegenPromptRequest): Promise<string> {
  const resp = await fetch("/api/regen-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!resp.ok) {
    throw new Error(`regen-prompt fetch failed: ${resp.status}`);
  }
  const data = (await resp.json()) as { prompt: string };
  return data.prompt;
}
