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
