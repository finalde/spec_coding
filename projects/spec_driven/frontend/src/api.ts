import {
  ApiError,
  type ApiErrorDetail,
  type FileResult,
  type PromoteRequest,
  type PromoteResult,
  type RegenRequest,
  type RegenResult,
  type Stage,
  type TreeNode,
  type UnpromoteRequest,
  type WriteResult,
} from "./types";

async function readJson<T>(response: Response): Promise<T> {
  const text = await response.text();
  if (!response.ok) {
    let detail: ApiErrorDetail | null = null;
    try {
      const parsed = text ? JSON.parse(text) : null;
      if (parsed && typeof parsed === "object" && "detail" in parsed) {
        const d = (parsed as { detail: unknown }).detail;
        if (d && typeof d === "object") detail = d as ApiErrorDetail;
        else if (typeof d === "string") detail = { kind: d };
      }
    } catch {
      // body wasn't JSON
    }
    throw new ApiError(response.status, `HTTP ${response.status}`, detail);
  }
  if (!text) return undefined as unknown as T;
  return JSON.parse(text) as T;
}

export async function fetchTree(): Promise<TreeNode> {
  const response = await fetch("/api/tree", {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<TreeNode>(response);
}

export async function fetchFile(path: string): Promise<FileResult> {
  const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<FileResult>(response);
}

export interface PutFileOptions {
  ifUnmodifiedSince?: string;
}

export async function putFile(
  path: string,
  content: string,
  options: PutFileOptions = {},
): Promise<WriteResult> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
  };
  if (options.ifUnmodifiedSince) {
    headers["If-Unmodified-Since"] = options.ifUnmodifiedSince;
  }
  const response = await fetch("/api/file", {
    method: "PUT",
    headers,
    body: JSON.stringify({ path, content }),
  });
  return readJson<WriteResult>(response);
}

export async function fetchStages(
  projectType: string,
  projectName: string,
): Promise<Stage[]> {
  const url = `/api/stages?project_type=${encodeURIComponent(projectType)}&project_name=${encodeURIComponent(projectName)}`;
  const response = await fetch(url, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  const result = await readJson<{ stages: Stage[] } | Stage[]>(response);
  if (Array.isArray(result)) return result;
  return result.stages;
}

export async function postRegenPrompt(req: RegenRequest): Promise<RegenResult> {
  const response = await fetch("/api/regen-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<RegenResult>(response);
}

export async function postPromote(req: PromoteRequest): Promise<PromoteResult> {
  const response = await fetch("/api/promote", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<PromoteResult>(response);
}

export async function deletePromote(req: UnpromoteRequest): Promise<PromoteResult> {
  const response = await fetch("/api/promote", {
    method: "DELETE",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<PromoteResult>(response);
}
