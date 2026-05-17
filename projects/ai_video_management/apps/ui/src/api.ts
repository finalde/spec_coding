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
  /** Per follow-up 064: optional archetype slug forwarded by per-slot
   * confirm calls so each actor's sidecar carries the slug from first
   * write. Standard callers pass null/omitted. */
  archetype?: string | null;
}

/** Per follow-up 059 / 064: per-slot preview entry. `body_prompt` is the
 * follow-up 052 dual-shot companion; `attrs` is the rolled per-slot attrs
 * that the confirm step forwards to `generateActors`. */
export interface PromptPreviewSlot {
  seed: number;
  prompt: string;
  body_prompt?: string;
  attrs?: ActorAttrs;
}

export interface PromptPreviewResult {
  prompts: PromptPreviewSlot[];
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
  // Per follow-up 064: 5 character-archetype-flavored values appended after the original 8 physical-appearance values.
  look: ["handsome", "beautiful", "cute", "mature", "rugged", "soft", "aristocratic", "fierce", "righteous", "sinister", "seductive", "cunning", "innocent"] as const,
  style: ["modern-casual", "period-ancient-china", "period-western", "business", "streetwear", "sci-fi", "fantasy"] as const,
  resolution: ["normal", "2k", "4k"] as const,
};

/** Per follow-up 063: Chinese display labels for ATTR_OPTIONS slugs. */
export const ATTR_LABELS_ZH: { [K in keyof typeof ATTR_OPTIONS]: Record<string, string> } = {
  ethnicity: {
    "asian": "亚洲", "east-asian": "东亚", "south-asian": "南亚",
    "caucasian": "白人", "african": "非洲裔", "latino": "拉丁裔",
    "middle-eastern": "中东", "mixed": "混血",
  },
  gender: { "male": "男", "female": "女" },
  age_range: {
    "18-25": "18-25 岁", "26-35": "26-35 岁", "36-50": "36-50 岁",
    "51-65": "51-65 岁", "65+": "65 岁以上",
  },
  look: {
    "handsome": "俊朗", "beautiful": "美丽", "cute": "可爱", "mature": "成熟",
    "rugged": "粗犷", "soft": "温柔", "aristocratic": "贵族气质", "fierce": "凌厉",
    "righteous": "正义", "sinister": "阴邪", "seductive": "妩媚",
    "cunning": "狡诈", "innocent": "天真",
  },
  style: {
    "modern-casual": "现代休闲", "period-ancient-china": "古装仙侠",
    "period-western": "西方古装", "business": "商务",
    "streetwear": "街头潮流", "sci-fi": "科幻", "fantasy": "奇幻",
  },
  resolution: {
    "normal": "普通 (~1024px Kling 原始)", "2k": "2K (2048px)", "4k": "4K (4096px)",
  },
};

/** Per follow-up 064: random sentinel value for dropdowns. Frontend
 * resolves this to a random pick from `ATTR_OPTIONS[field]` per slot
 * before any preview / generate call — backend never sees the sentinel. */
export const RANDOM_SENTINEL = "__random__";

export function rollRandomAttr<K extends keyof typeof ATTR_OPTIONS>(field: K): typeof ATTR_OPTIONS[K][number] {
  const opts = ATTR_OPTIONS[field];
  return opts[Math.floor(Math.random() * opts.length)];
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

export interface TruncateCharacterVideoResult {
  src: string;
  out: string;
  duration_seconds: number;
}

export async function truncateCharacterVideo(path: string): Promise<TruncateCharacterVideoResult> {
  const response = await fetch("/api/truncate-character-video", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<TruncateCharacterVideoResult>(response);
}

export interface ShotConcatCharacterUsed {
  role: string;
  character_folder: string;
  rel_path: string;
}

export interface ShotConcatCharacterSkipped {
  role: string;
  character_folder: string;
  reason: string;
}

export interface ConcatShotCharactersResult {
  shot_path: string;
  out: string | null;
  used: ShotConcatCharacterUsed[];
  skipped: ShotConcatCharacterSkipped[];
}

export async function concatShotCharacters(path: string): Promise<ConcatShotCharactersResult> {
  const response = await fetch("/api/concat-shot-characters", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ConcatShotCharactersResult>(response);
}
