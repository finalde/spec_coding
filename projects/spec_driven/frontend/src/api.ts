import type { FileResult, RegenResult, Stage, TreeNode, WriteResult } from "./types";

const ORIGIN_HEADERS = { "Content-Type": "application/json" };

export async function fetchTree(): Promise<TreeNode> {
  const resp = await fetch("/api/tree");
  if (!resp.ok) throw new Error(`tree: ${resp.status}`);
  return resp.json();
}

export interface FetchFileError {
  status: number;
  detail: unknown;
}

export async function fetchFile(path: string): Promise<FileResult> {
  const resp = await fetch(`/api/file?path=${encodeURIComponent(path)}`);
  if (!resp.ok) {
    const detail = await resp.json().catch(() => null);
    throw { status: resp.status, detail } satisfies FetchFileError;
  }
  return resp.json();
}

export async function putFile(path: string, content: string): Promise<WriteResult> {
  const resp = await fetch("/api/file", {
    method: "PUT",
    headers: ORIGIN_HEADERS,
    body: JSON.stringify({ path, content }),
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => null);
    throw { status: resp.status, detail } satisfies FetchFileError;
  }
  return resp.json();
}

export async function fetchStages(projectType: string, projectName: string): Promise<Stage[]> {
  const resp = await fetch(
    `/api/stages?project_type=${encodeURIComponent(projectType)}&project_name=${encodeURIComponent(projectName)}`,
  );
  if (!resp.ok) throw new Error(`stages: ${resp.status}`);
  const body = await resp.json();
  return body.stages;
}

export interface RegenRequest {
  project_type: string;
  project_name: string;
  stages: string[];
  modules: Record<string, string[]>;
  autonomous: boolean;
}

export async function postRegenPrompt(req: RegenRequest): Promise<RegenResult> {
  const resp = await fetch("/api/regen-prompt", {
    method: "POST",
    headers: ORIGIN_HEADERS,
    body: JSON.stringify(req),
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => null);
    throw { status: resp.status, detail } satisfies FetchFileError;
  }
  return resp.json();
}

export interface PromoteRequest {
  project_type: string;
  project_name: string;
  stage_folder: string;
  source_file: string;
  item_id: string;
  item_text: string;
}

export async function postPromote(req: PromoteRequest): Promise<{ status: string; item_id: string }> {
  const resp = await fetch("/api/promote", {
    method: "POST",
    headers: ORIGIN_HEADERS,
    body: JSON.stringify(req),
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => null);
    throw { status: resp.status, detail } satisfies FetchFileError;
  }
  return resp.json();
}

export async function deletePromote(req: {
  project_type: string;
  project_name: string;
  stage_folder: string;
  item_id: string;
}): Promise<{ status: string; item_id: string }> {
  const resp = await fetch("/api/promote", {
    method: "DELETE",
    headers: ORIGIN_HEADERS,
    body: JSON.stringify(req),
  });
  if (!resp.ok) {
    const detail = await resp.json().catch(() => null);
    throw { status: resp.status, detail } satisfies FetchFileError;
  }
  return resp.json();
}
