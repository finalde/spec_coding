import { ApiError, type ApiErrorDetail, type FileResult, type TreeNode, type WriteResult } from "./types";

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

export interface RenameMediaResult {
  renamed: { from: string; to: string }[];
  skipped: string[];
  errors: { path: string; message: string }[];
}

export async function renameMedia(path: string): Promise<RenameMediaResult> {
  const response = await fetch("/api/rename-media", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<RenameMediaResult>(response);
}

/** Build a same-origin URL for image preview, with mtime cache-buster. */
export function imageUrl(path: string, mtime: number): string {
  return `/api/file?path=${encodeURIComponent(path)}&mtime=${encodeURIComponent(String(mtime))}`;
}

/** Build a same-origin URL for raw media (image / video) via /api/media route.
 * Bypasses /api/file's base64 + 1 MB limit. Per follow-up 005.
 */
export function mediaUrl(path: string, mtime?: number): string {
  const cb = mtime !== undefined ? `&mtime=${encodeURIComponent(String(mtime))}` : "";
  return `/api/media?path=${encodeURIComponent(path)}${cb}`;
}
