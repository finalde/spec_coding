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

export interface ArchiveMediaResult {
  from: string;
  to: string;
}

export async function archiveMedia(path: string): Promise<ArchiveMediaResult> {
  const response = await fetch("/api/archive-media", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ArchiveMediaResult>(response);
}

export async function unarchiveMedia(path: string): Promise<ArchiveMediaResult> {
  const response = await fetch("/api/unarchive-media", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ArchiveMediaResult>(response);
}

export async function deleteMedia(path: string): Promise<ArchiveMediaResult> {
  const response = await fetch("/api/delete-media", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ArchiveMediaResult>(response);
}

export interface HardDeleteMediaResult {
  deleted: string;
}

export async function hardDeleteMedia(path: string): Promise<HardDeleteMediaResult> {
  const response = await fetch("/api/hard-delete-media", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<HardDeleteMediaResult>(response);
}

export interface ExtractedFrame {
  timestamp: number;
  role: string;
  shot_size: string;
  rank: number;
  path: string;
}

export interface ExtractFramesResult {
  src: string;
  frames: ExtractedFrame[];
  failures: { timestamp: number; role: string; error: string }[];
}

export async function extractFrames(path: string): Promise<ExtractFramesResult> {
  const response = await fetch("/api/extract-frames", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ExtractFramesResult>(response);
}

export interface ImportFromDownloadsResult {
  moved: { from: string; to: string; kind: string }[];
  unmatched: { from: string; to: string; kind: string }[];
  errors: { path: string; message: string }[];
  rename: RenameMediaResult;
}

export async function importFromDownloads(path: string): Promise<ImportFromDownloadsResult> {
  const response = await fetch("/api/import-from-downloads", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ImportFromDownloadsResult>(response);
}

export interface ActorAttrs {
  ethnicity: string;
  gender: string;
  age_range: string;
  look: string;
  style: string;
  notes?: string;
}

export interface ActorInfo extends ActorAttrs {
  id: string;
  image_path: string;
  mtime: number;
}

export interface GenerateActorsResult {
  generated: { id: string; image_path: string; attrs: ActorAttrs; seed: number }[];
  errors: { requested_id: string; message: string }[];
}

export interface GenerateActorsRequest extends ActorAttrs {
  count: number;
  resolution?: string;
  seeds?: number[];
}

export interface PromptPreviewResult {
  prompts: { seed: number; prompt: string }[];
  resolution: string;
}

export async function previewPrompts(req: GenerateActorsRequest): Promise<PromptPreviewResult> {
  const response = await fetch("/api/actors/preview-prompts", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<PromptPreviewResult>(response);
}

export async function generateActors(req: GenerateActorsRequest): Promise<GenerateActorsResult> {
  const response = await fetch("/api/actors/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<GenerateActorsResult>(response);
}

export interface DeleteActorResult {
  from: string;
  to: string;
  unassigned: { drama: string; role: string }[];
}

export async function deleteActor(actorId: string): Promise<DeleteActorResult> {
  const response = await fetch("/api/actors/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ actor_id: actorId }),
  });
  return readJson<DeleteActorResult>(response);
}

export async function listActors(): Promise<{ actors: ActorInfo[] }> {
  const response = await fetch("/api/actors", {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<{ actors: ActorInfo[] }>(response);
}

export interface ActorAssignment {
  drama: string;
  role: string;
  notes: string;
  character_folder: string;
  character_folder_exists: boolean;
}

export interface ActorAssignmentsResult {
  actor_id: string;
  assignments: ActorAssignment[];
}

export async function fetchActorAssignments(actorId: string): Promise<ActorAssignmentsResult> {
  const response = await fetch(`/api/actors/assignments?actor_id=${encodeURIComponent(actorId)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<ActorAssignmentsResult>(response);
}

export interface CastEntry {
  role: string;
  actor_id: string;
  notes: string;
}

export interface CastingResult {
  path: string;
  entries: CastEntry[];
}

export async function fetchCasting(path: string): Promise<CastingResult> {
  const response = await fetch(`/api/casting?path=${encodeURIComponent(path)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<CastingResult>(response);
}

export async function castingAssign(
  path: string,
  role: string,
  actor_id: string,
  notes = "",
): Promise<CastingResult> {
  const response = await fetch("/api/casting/assign", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, role, actor_id, notes }),
  });
  return readJson<CastingResult>(response);
}

export async function castingUnassign(path: string, role: string): Promise<CastingResult> {
  const response = await fetch("/api/casting/assign", {
    method: "DELETE",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, role }),
  });
  return readJson<CastingResult>(response);
}

export const ATTR_OPTIONS = {
  ethnicity: ["asian", "east-asian", "south-asian", "caucasian", "african", "latino", "middle-eastern", "mixed"] as const,
  gender: ["male", "female"] as const,
  age_range: ["18-25", "26-35", "36-50", "51-65", "65+"] as const,
  look: ["handsome", "beautiful", "cute", "mature", "rugged", "soft", "aristocratic", "fierce"] as const,
  style: ["modern-casual", "period-ancient-china", "period-western", "business", "streetwear", "sci-fi", "fantasy"] as const,
  resolution: ["normal", "2k", "4k"] as const,
};

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
