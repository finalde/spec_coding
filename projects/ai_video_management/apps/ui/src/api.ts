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
  // `no-store`: after a delete/rename the left-nav tree must reflect the
  // current filesystem. Without it the browser can serve a cached /api/tree
  // and the deleted actor keeps showing in the sidebar.
  const response = await fetch("/api/tree", {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return readJson<TreeNode>(response);
}

export async function fetchFile(path: string): Promise<FileResult> {
  // `no-store`: after an edit/rename the viewer must show current bytes, not a
  // browser-cached stale copy (mirrors fetchTree). Without it a shot opened
  // before a rename keeps showing the old (e.g. pinyin) content.
  const response = await fetch(`/api/file?path=${encodeURIComponent(path)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
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

export interface PurgeDeletedResult {
  purged: number;
}

/** Empty the recycle bin: recursively wipe everything under
 * ai_videos/_deleted/ (every file type + folders), not just media. */
export async function purgeDeleted(): Promise<PurgeDeletedResult> {
  const response = await fetch("/api/purge-deleted", {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  return readJson<PurgeDeletedResult>(response);
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

export interface ExtractLastFrameResult {
  src: string;
  out: string;
  /** The same frame copied into the next shot as `{nextshot}_firstframe.png`,
   * or null when there is no next shot. */
  first_frame: string | null;
}

/** Extract a shot render's FINAL frame to `{shot}/{shot}_lastframe.png` — the
 * cross-shot continuity-frame source (承接 shot's first frame = previous shot's
 * last frame) — and copy it into the next shot as `{nextshot}_firstframe.png`. */
export async function extractLastFrame(path: string): Promise<ExtractLastFrameResult> {
  const response = await fetch("/api/extract-last-frame", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ExtractLastFrameResult>(response);
}

export interface ScenePlate {
  folder: string;
  direction: string;
  timestamp: number;
  path: string;
}

export interface ExtractScenePlatesResult {
  src: string;
  plates: ScenePlate[];
  skipped: string[];
  failures: { folder: string; error: string }[];
}

/** Extract per-direction background plates from a scene walk-through mp4 into
 * the sibling bg{N}_{方位}_ folders. Each plate's grab second is read from the
 * scene md「背景图系统 index」table (per-scene dwell order — keeps it in lock-step
 * with the 步骤二 walk-through timeline); the fixed 1.5/4.5/7.5/10.5/13.5s
 * compass map is only the fallback when the table is absent. */
export async function extractScenePlates(path: string): Promise<ExtractScenePlatesResult> {
  const response = await fetch("/api/extract-scene-plates", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ExtractScenePlatesResult>(response);
}

export type SubtitleLang = "zh" | "en" | "both";

export interface BurnSubtitlesResult {
  src: string;
  out: string;
  cues: number;
  lang: SubtitleLang;
}

export async function burnSubtitles(
  path: string,
  lang: SubtitleLang = "zh",
): Promise<BurnSubtitlesResult> {
  const response = await fetch("/api/burn-subtitles", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang }),
  });
  return readJson<BurnSubtitlesResult>(response);
}

export interface ScaffoldSubtitlesResult {
  path: string;
  cues: number;
  created: boolean;
}

export async function scaffoldSubtitles(path: string): Promise<ScaffoldSubtitlesResult> {
  const response = await fetch("/api/scaffold-subtitles", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ScaffoldSubtitlesResult>(response);
}

export interface BatchShotOutcome {
  episode: string;
  shot: string;
  ok: boolean;
  out: string | null;
  cues: number | null;
  reason: string | null;
}

export interface ScaffoldEpisodeSubtitlesResult {
  episode: string;
  outcomes: BatchShotOutcome[];
}

/** (Re)generate subtitles.md for every shot in one episode. `path` may be any
 * file under the episode folder. */
export async function scaffoldEpisodeSubtitles(
  path: string,
): Promise<ScaffoldEpisodeSubtitlesResult> {
  const response = await fetch("/api/scaffold-episode-subtitles", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ScaffoldEpisodeSubtitlesResult>(response);
}

export interface BurnEpisodeSubtitlesResult {
  episode: string;
  lang: SubtitleLang;
  outcomes: BatchShotOutcome[];
}

/** Burn the {lang} subtitle master for every shot in ONE episode (each shot's
 * newest render + its subtitles.md). `path` may be any file under the episode
 * folder. */
export async function burnEpisodeSubtitles(
  path: string,
  lang: SubtitleLang = "zh",
): Promise<BurnEpisodeSubtitlesResult> {
  const response = await fetch("/api/burn-episode-subtitles", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang }),
  });
  return readJson<BurnEpisodeSubtitlesResult>(response);
}

export interface BurnDramaSubtitlesResult {
  drama: string;
  lang: SubtitleLang;
  outcomes: BatchShotOutcome[];
}

/** Burn the {lang} subtitle master for every shot across ALL episodes of a
 * drama (each shot's newest render + its subtitles.md). `path` may be any file
 * under the drama folder. */
export async function burnDramaSubtitles(
  path: string,
  lang: SubtitleLang = "zh",
): Promise<BurnDramaSubtitlesResult> {
  const response = await fetch("/api/burn-drama-subtitles", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang }),
  });
  return readJson<BurnDramaSubtitlesResult>(response);
}

export interface ExportedEpisode {
  lang: "zh" | "en" | "zhen";
  folder: string;   // 中文 | 英文 | 中英
  episode: string;  // ep01
  src: string;
  out: string;
}

export interface ExportProductionResult {
  drama: string;
  production: string;
  exported: ExportedEpisode[];
  /** per-folder copied counts, keyed by 中文 / 英文 / 中英. */
  by_lang: Record<string, number>;
}

/** Copy every subtitled episode master (`ep{NN}_{zh|en|zhen}.mp4`) across ALL
 * episodes of a drama into `ai_videos/{drama}/production/{中文|英文|中英}/ep{NN}.mp4`
 * (language implied by the sub-folder, so the suffix is stripped). Overwrites;
 * nothing-to-export is a valid empty result. `path` may be any file under the
 * drama folder. */
export async function exportProduction(path: string): Promise<ExportProductionResult> {
  const response = await fetch("/api/export-production", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ExportProductionResult>(response);
}

export interface BurnIntroCardsResult {
  src: string;
  out: string;
  cards: number;
  names: string[];
}

/** Burn character intro cards (freeze-frame nameplate, ai_video.md 11d) into a
 * shot render per the episode's intro_cards.md → shot{NN}_card.mp4. */
export async function burnIntroCards(path: string): Promise<BurnIntroCardsResult> {
  const response = await fetch("/api/burn-intro-cards", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<BurnIntroCardsResult>(response);
}

export interface PerfScoreResult {
  path: string;
  validation_status: string;
  decision: string;
  verdict: string;
}

export interface RegenShotPromptResult {
  prompt: string;
  refs: string[];
  message: string;
}

export async function regenShotPrompt(
  path: string,
  selectedPerfIds?: string[],
): Promise<RegenShotPromptResult> {
  const body: { path: string; selected_perf_ids?: string[] } = { path };
  if (selectedPerfIds && selectedPerfIds.length > 0) body.selected_perf_ids = selectedPerfIds;
  const response = await fetch("/api/regen-shot-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  return readJson<RegenShotPromptResult>(response);
}

// ============================================================================
// Performance library candidate recommendation + multi-select (per follow-up:
// shot 页演技库候选推荐). The backend scores the shared performance library
// against the shot's emotion/intensity/duration and returns a top-N candidate
// list; the user multi-selects, writes the selection back as the shot's
// `表演库参考:` line, and optionally re-assembles a copy-paste regen prompt.
// ============================================================================

export interface PerformanceCandidate {
  perf_id: string;
  emotion: string;
  intensity: number;
  style: string;
  carrier: string;
  duration_s: number;
  title: string;
  preview: string;
  mp4_rel_path: string | null;
  score: number;
}

export interface PerformanceCandidatesResult {
  candidates: PerformanceCandidate[];
  shot_emotion_guess: string | null;
}

export interface PerformanceCandidatesOptions {
  emotion?: string;
  intensity?: number;
  durationS?: number;
  topN?: number;
}

export async function performanceCandidates(
  shotPath: string,
  opts: PerformanceCandidatesOptions = {},
): Promise<PerformanceCandidatesResult> {
  const body: {
    shot_path: string;
    emotion?: string;
    intensity?: number;
    duration_s?: number;
    top_n?: number;
  } = { shot_path: shotPath };
  if (opts.emotion !== undefined) body.emotion = opts.emotion;
  if (opts.intensity !== undefined) body.intensity = opts.intensity;
  if (opts.durationS !== undefined) body.duration_s = opts.durationS;
  if (opts.topN !== undefined) body.top_n = opts.topN;
  const response = await fetch("/api/performance-candidates", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  return readJson<PerformanceCandidatesResult>(response);
}

export interface SetShotPerformanceRefsResult {
  path: string;
  content: string;
  mtime: string;
}

export async function setShotPerformanceRefs(
  shotPath: string,
  perfIds: string[],
  mtime?: string,
): Promise<SetShotPerformanceRefsResult> {
  const body: { shot_path: string; perf_ids: string[]; mtime?: string } = {
    shot_path: shotPath,
    perf_ids: perfIds,
  };
  if (mtime !== undefined) body.mtime = mtime;
  const response = await fetch("/api/shot-performance-refs", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  return readJson<SetShotPerformanceRefsResult>(response);
}

export interface PerfCheckPromptResult {
  ok: boolean;
  kind: "ok" | "no_mp4" | "multiple_mp4";
  message: string;
  prompt: string;
  mp4: string;
  candidates: string[];
}

export async function perfCheckPrompt(path: string): Promise<PerfCheckPromptResult> {
  const response = await fetch("/api/perf-check-prompt", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<PerfCheckPromptResult>(response);
}

export async function perfScore(input: {
  path: string;
  who: string;
  da_yi: number | null;
  qing_xu: number | null;
  guo_huo: number | null;
  note: string;
}): Promise<PerfScoreResult> {
  const response = await fetch("/api/perf-score", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(input),
  });
  return readJson<PerfScoreResult>(response);
}

export interface ImportFromDownloadsResult {
  moved: { from: string; to: string; kind: string }[];
  // Unmatched files are NOT imported — left in Downloads, only reported (no `to`).
  unmatched: { from: string; kind: string }[];
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
  notes?: string;
  /** Per follow-up 100: optional user-locked feature descriptors. Empty
   * string / RANDOM_SENTINEL → backend samples the rich pool deterministically
   * by seed; a curated Chinese descriptor substitutes verbatim into the
   * prompt's 眼睛 / 鼻子 / 嘴巴 / 脸型 / 皮肤 / 体型 line. */
  eyes?: string;
  nose?: string;
  lips?: string;
  face?: string;
  skin?: string;
  body?: string;
  qi_zhi?: string;
}

export interface ActorInfo extends ActorAttrs {
  id: string;
  /** "" for prompt-only actors that have no rendered jpg yet. */
  image_path: string;
  mtime: number;
  /** Per follow-up 086: true iff this actor appears in any drama's
   * casting.md. Powers the ActorGrid 分配状态 filter chip. */
  is_assigned?: boolean;
  /** True iff this actor has a sidecar prompt but no image yet. Only
   * returned when listActors(includePending=true) is called. Powers the
   * ActorGrid 图片状态 filter so imageless actors can be bulk-deleted. */
  pending_import?: boolean;
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
  /** Per follow-up 082: within-batch pool-diversity coordination. Set
   * batchSeed once per generate/preview click + pass slotIndex = i +
   * batchSize on each of N parallel count=1 calls. Backend uses these
   * to resolve the 7 face/body pool draws so no two slots in the same
   * batch share an eye / nose / lips / brow / contour / skin / body
   * descriptor (bias-preferred, exhaust-then-fall-through). */
  batch_seed?: number | null;
  batch_size?: number | null;
  slot_index?: number | null;
  // eyes / skin / body come from ActorAttrs (follow-up 100).
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

/** Per follow-up 124: a prompt-only actor — its folder + sidecar were created
 * but NO Kling call fired. The user copies `face_prompt` / `body_prompt` into
 * Kling/Seedance, then imports the downloads (📥 导入演员) which routes each
 * file back by its `id{NNNN}{f|b}` tag prefix. */
export interface ActorPromptSlot {
  id: string;
  attrs: ActorAttrs;
  seed: number;
  resolution: string;
  pending_import: boolean;
  face_prompt: string;
  body_prompt: string;
}

export interface CreateActorPromptsResult {
  generated: ActorPromptSlot[];
  errors: { requested_id: string; message: string }[];
}

export async function createActorPrompts(req: GenerateActorsRequest): Promise<CreateActorPromptsResult> {
  const response = await fetch("/api/actors/create-prompts", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<CreateActorPromptsResult>(response);
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

export async function listActors(includePending = false): Promise<{ actors: ActorInfo[] }> {
  // no-store: after generate/delete the grid must reflect the current pool.
  const qs = includePending ? "?include_pending=true" : "";
  const response = await fetch(`/api/actors${qs}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
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
  resolution: ["normal", "2k", "4k"] as const,
  // Per follow-up 100: optional user-locked feature dropdowns. MUST stay in
  // sync with EYES_OPTIONS / NOSE_OPTIONS / LIPS_OPTIONS / SKIN_OPTIONS /
  // BODY_OPTIONS in libs/domain/value_objects/actor__valueobject.py.
  eyes: [
    "大眼", "细长眼", "圆眼", "杏眼", "桃花眼", "凤眼", "鹿眼",
    "小眼", "丹凤眼", "狐眼", "单眼皮", "双眼皮", "内双", "深邃眼",
  ] as const,
  nose: [
    "高挺", "挺直", "小巧", "翘鼻", "鹰钩", "蒜头", "塌鼻",
    "驼峰鼻", "朝天鼻", "宽鼻", "窄鼻", "圆鼻头", "尖鼻",
  ] as const,
  lips: [
    "樱桃小嘴", "丰唇", "薄唇", "厚唇", "嘟嘟嘴", "上翘嘴角",
    "大嘴", "小嘴", "性感唇", "苹果唇", "嘴角下垂", "棱角分明唇",
  ] as const,
  face: [
    "鹅蛋脸", "瓜子脸", "圆脸", "方脸", "长脸",
    "心形脸", "国字脸", "菱形脸", "倒三角脸",
  ] as const,
  skin: [
    "白皙", "小麦色", "古铜色", "瓷白", "象牙白", "蜜糖色",
    "黝黑", "苍白", "红润", "雪白", "焦糖色", "深棕色", "橄榄色", "麦色",
  ] as const,
  body: [
    "高挑修长", "中等匀称", "娇小玲珑", "纤瘦", "丰满", "健硕",
    "高大", "矮小", "魁梧",
    "骨感", "偏瘦", "微胖", "胖", "肥胖", "过度肥胖",
  ] as const,
  qi_zhi: [
    "阳光", "温柔", "清纯", "邻家", "楚楚动人",
    "优雅", "高冷", "冷艳", "神秘", "知性",
    "忧郁", "颓废", "沧桑", "阴鸷", "邪魅",
    "霸气", "不羁", "萌系", "俏皮", "妩媚",
  ] as const,
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
  resolution: {
    "normal": "普通 (~1024px Kling 原始)", "2k": "2K (2048px)", "4k": "4K (4096px)",
  },
  eyes: {
    "大眼": "大眼", "细长眼": "细长眼", "圆眼": "圆眼", "杏眼": "杏眼",
    "桃花眼": "桃花眼", "凤眼": "凤眼", "鹿眼": "鹿眼",
    "小眼": "小眼", "丹凤眼": "丹凤眼", "狐眼": "狐眼",
    "单眼皮": "单眼皮", "双眼皮": "双眼皮", "内双": "内双", "深邃眼": "深邃眼",
  },
  nose: {
    "高挺": "高挺", "挺直": "挺直", "小巧": "小巧", "翘鼻": "翘鼻",
    "鹰钩": "鹰钩", "蒜头": "蒜头", "塌鼻": "塌鼻",
    "驼峰鼻": "驼峰鼻", "朝天鼻": "朝天鼻", "宽鼻": "宽鼻",
    "窄鼻": "窄鼻", "圆鼻头": "圆鼻头", "尖鼻": "尖鼻",
  },
  lips: {
    "樱桃小嘴": "樱桃小嘴", "丰唇": "丰唇", "薄唇": "薄唇",
    "厚唇": "厚唇", "嘟嘟嘴": "嘟嘟嘴", "上翘嘴角": "上翘嘴角",
    "大嘴": "大嘴", "小嘴": "小嘴", "性感唇": "性感唇",
    "苹果唇": "苹果唇", "嘴角下垂": "嘴角下垂", "棱角分明唇": "棱角分明唇",
  },
  face: {
    "鹅蛋脸": "鹅蛋脸", "瓜子脸": "瓜子脸", "圆脸": "圆脸",
    "方脸": "方脸", "长脸": "长脸", "心形脸": "心形脸",
    "国字脸": "国字脸", "菱形脸": "菱形脸", "倒三角脸": "倒三角脸",
  },
  skin: {
    "白皙": "白皙", "小麦色": "小麦色", "古铜色": "古铜色",
    "瓷白": "瓷白", "象牙白": "象牙白", "蜜糖色": "蜜糖色",
    "黝黑": "黝黑", "苍白": "苍白", "红润": "红润", "雪白": "雪白",
    "焦糖色": "焦糖色", "深棕色": "深棕色", "橄榄色": "橄榄色", "麦色": "麦色",
  },
  body: {
    "高挑修长": "高挑修长", "中等匀称": "中等匀称", "娇小玲珑": "娇小玲珑",
    "纤瘦": "纤瘦", "丰满": "丰满", "健硕": "健硕",
    "高大": "高大", "矮小": "矮小", "魁梧": "魁梧",
    "骨感": "骨感", "偏瘦": "偏瘦", "微胖": "微胖",
    "胖": "胖", "肥胖": "肥胖", "过度肥胖": "过度肥胖",
  },
  qi_zhi: {
    "阳光": "阳光", "温柔": "温柔", "清纯": "清纯", "邻家": "邻家",
    "楚楚动人": "楚楚动人", "优雅": "优雅", "高冷": "高冷", "冷艳": "冷艳",
    "神秘": "神秘", "知性": "知性", "忧郁": "忧郁", "颓废": "颓废",
    "沧桑": "沧桑", "阴鸷": "阴鸷", "邪魅": "邪魅", "霸气": "霸气",
    "不羁": "不羁", "萌系": "萌系", "俏皮": "俏皮", "妩媚": "妩媚",
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

// ============================================================================
// Prompt refinement suggestions (follow-up 117). Per-dimension AI suggestions
// for a shot's video prompt: the backend forwards the shot context + clicked
// dimension to the Anthropic Messages API and returns a few candidate
// refinements the user picks from.
// ============================================================================

export interface RefinementSuggestion {
  value: string;
  rationale: string;
}

export interface SuggestRefinementsResult {
  dimension: string;
  suggestions: RefinementSuggestion[];
}

export interface SuggestRefinementsRequest {
  dimension: string;
  current_value?: string;
  shot_context?: string;
  prompt_body?: string;
  drama?: string | null;
  scene?: string | null;
  count?: number;
}

export async function suggestRefinements(
  req: SuggestRefinementsRequest,
): Promise<SuggestRefinementsResult> {
  const response = await fetch("/api/prompt/suggest", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<SuggestRefinementsResult>(response);
}

/** Build a same-origin URL for image preview, with mtime cache-buster. */
export function imageUrl(path: string, mtime: number): string {
  return `/api/file?path=${encodeURIComponent(path)}&mtime=${encodeURIComponent(String(mtime))}`;
}

/** Build a same-origin URL for raw media (image / video / audio) via /api/media.
 * Bypasses /api/file's base64 + 1 MB limit. Per follow-up 005.
 *
 * Cache busting: an mtime arg takes precedence (per-file mtime, e.g. ActorGrid).
 * Otherwise we append a module-level buster bumped on every tree refresh by
 * `bumpMediaCacheBuster()` — this evicts stale browser cache after a regen
 * (e.g. character views) where the URL path is unchanged but the bytes are not.
 */
let _mediaCacheBuster: number = Date.now();
export function bumpMediaCacheBuster(): void {
  _mediaCacheBuster = Date.now();
}
export function mediaUrl(path: string, mtime?: number): string {
  const v = mtime !== undefined ? mtime : _mediaCacheBuster;
  return `/api/media?path=${encodeURIComponent(path)}&v=${encodeURIComponent(String(v))}`;
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

export interface CharacterView {
  timestamp: number;
  role: string;
  path: string;
}

export interface CharacterAudio {
  path: string;
}

export interface CharacterTrim {
  path: string;
  duration_seconds: number;
}

export interface CharacterViewFailure {
  target: string;
  error: string;
}

export interface ExtractCharacterViewsResult {
  src: string;
  views: CharacterView[];
  audio: CharacterAudio | null;
  trim: CharacterTrim | null;
  failures: CharacterViewFailure[];
}

export async function extractCharacterViews(path: string): Promise<ExtractCharacterViewsResult> {
  const response = await fetch("/api/extract-character-views", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ExtractCharacterViewsResult>(response);
}

export interface CharacterVideoListing {
  folder: string;
  /** Newest turntable mp4 in the folder (rel path), or null when none rendered yet. */
  latest_video: string | null;
}

export async function listCharacterVideos(
  path: string,
): Promise<{ items: CharacterVideoListing[] }> {
  // no-store: after a render/import the gallery must reflect the newest mp4.
  const response = await fetch(`/api/character-videos?path=${encodeURIComponent(path)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return readJson<{ items: CharacterVideoListing[] }>(response);
}

export interface ExtractAllCharacterViewsItem {
  folder: string;
  status: "ok" | "skipped" | "error";
  result: ExtractCharacterViewsResult | null;
  reason: string;
}

export interface ExtractAllCharacterViewsResult {
  characters_dir: string;
  items: ExtractAllCharacterViewsItem[];
}

/** Batch re-extract 3 views + audio + 2s trim for every character folder under
 *  a drama's `characters/` dir (path = that dir's relative path). */
export async function extractAllCharacterViews(
  path: string,
): Promise<ExtractAllCharacterViewsResult> {
  const response = await fetch("/api/extract-all-character-views", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<ExtractAllCharacterViewsResult>(response);
}

export interface EpisodeShotUsed {
  shot: string;
  video: string;
  /** Seconds of held first-frame trimmed off this 承接 shot's seam (0 = none). */
  trimmed_s: number;
}

export interface EpisodeShotSkipped {
  shot: string;
  reason: string;
}

export type EpisodeLang = "original" | "zh" | "en" | "both";

export interface ConcatEpisodeResult {
  episode: string;
  out: string | null;
  used: EpisodeShotUsed[];
  skipped: EpisodeShotSkipped[];
  lang: EpisodeLang;
  /** RIFE motion-bridge stitch was applied at the 承接 seams. */
  rife_used: boolean;
  /** Number of 承接 seams actually bridged with synthesised motion. */
  rife_bridges: number;
  /** Sidecar ep{NN}.segments.json (each shot's final-timeline [start,end)); the
   * whole-episode subtitle burn reads it to place cues. null if unknown. */
  segments: string | null;
}

/** One shot→shot junction in the seam planner. */
export interface SeamInfo {
  index: number;
  from: string;
  to: string;
  link: "handoff" | "hardcut";   // 承接 (RIFE-eligible) | 硬切 (butt only)
  diff: number | null;           // mean-abs frame diff (handoff only)
  suggest: "butt" | "trim" | "rife";  // auto recommendation
  method: "butt" | "trim" | "rife";   // current choice (saved plan or suggestion)
  trim: number;
  depth: number | null;          // 补帧密度 override (null = auto; rife only)
  thumb_a: string;               // data-URI JPEG of predecessor tail frame
  thumb_b: string;               // data-URI JPEG of successor head frame
}

export interface EpisodeSeamsResult {
  episode: string;
  lang: EpisodeLang;
  seams: SeamInfo[];
  has_saved_plan: boolean;
}

/** One seam's choice in a build plan POSTed back to /api/concat-episode. */
export interface SeamPlanEntry {
  from: string;
  to: string;
  method: "butt" | "trim" | "rife";
  trim?: number | null;
  depth?: number | null;
}

/** Analyze every shot→shot junction of an episode for the seam planner:
 * 承接/硬切, boundary-frame thumbnails, a frame-diff suggestion, saved plan. */
export async function analyzeEpisodeSeams(
  path: string,
  lang: EpisodeLang = "original",
): Promise<EpisodeSeamsResult> {
  const response = await fetch("/api/episode-seams", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang }),
  });
  return readJson<EpisodeSeamsResult>(response);
}

/** Step ② of the concat-first flow: stitch each shot's CLEAN clip (the locked
 * `shot{NN}.mp4` from step ①, else newest renders/ mp4) into one ep{NN}.mp4 +
 * sidecar ep{NN}.segments.json (final-timeline offsets the whole-episode burn
 * needs). `lang` stays "original" in the new flow (subtitles are burned later
 * onto the clean reel by `burnEpisodeSubtitlesWhole`); zh/en/both still stitch
 * the old per-shot burned masters for back-compat. `path` may be any file under
 * the episode folder. When `rife` is true the 承接 seams are bridged with
 * RIFE-synthesised motion instead of butt-joined (slower; needs the
 * rife-ncnn-vulkan exe on the server). */
export async function concatEpisode(
  path: string,
  lang: EpisodeLang = "original",
  rife: boolean = false,
  plan: SeamPlanEntry[] | null = null,
): Promise<ConcatEpisodeResult> {
  const response = await fetch("/api/concat-episode", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang, rife, plan }),
  });
  return readJson<ConcatEpisodeResult>(response);
}

export interface SelectTake {
  shot: string;
  src: string;   // the newest renders/ take that was copied
  out: string;   // the locked shot{NN}.mp4
}

export interface SelectEpisodeTakesResult {
  episode: string;
  selected: SelectTake[];
  skipped: EpisodeShotSkipped[];
}

/** Step ① of the concat-first flow: lock each shot's chosen take by copying its
 * newest renders/ mp4 to a stable `shot{NN}.mp4` (renders/ left untouched). The
 * concat in step ② then stitches these locked takes. `path` may be any file
 * under the episode folder. */
export async function selectEpisodeTakes(
  path: string,
): Promise<SelectEpisodeTakesResult> {
  const response = await fetch("/api/select-episode-takes", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<SelectEpisodeTakesResult>(response);
}

export interface BurnEpisodeWholeResult {
  episode: string;
  out: string;
  lang: SubtitleLang;
  cues: number;
  shots: number;
}

/** Step ③ of the concat-first flow: burn ONE subtitle track onto the clean
 * stitched ep{NN}.mp4, each shot's cues placed at their TRUE offset in the final
 * reel (read from ep{NN}.segments.json) → ep{NN}_{zh|en|zhen}.mp4. This is what
 * stops subtitles drifting at the seams — they're aligned to the final timeline
 * and encoded once. Requires step ② (concat) to have written segments.json.
 * `path` may be any file under the episode folder. */
export async function burnEpisodeSubtitlesWhole(
  path: string,
  lang: SubtitleLang = "zh",
): Promise<BurnEpisodeWholeResult> {
  const response = await fetch("/api/burn-episode-subtitles-whole", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang }),
  });
  return readJson<BurnEpisodeWholeResult>(response);
}

// ============================================================================
// Drama-level production console (main page DramaDashboard).
// ============================================================================

/** One episode's status in the drama production console. `episode_rel` is the
 * ep folder path — pass it straight to `concatEpisode` for per-episode 拼接. */
export interface DramaEpisodeInfo {
  episode: string;       // "ep04"
  episode_rel: string;   // ai_videos/{drama}/.../episodes/ep04
  shots: number;
  locked: number;        // shots already 定版-locked (shot{NN}.mp4 present)
  has_master: boolean;   // stitched ep{NN}.mp4 exists
}

export interface DramaEpisodesResult {
  drama: string;
  episodes: DramaEpisodeInfo[];
}

/** List a drama's episodes (shot count, 定版-locked count, master flag) to drive
 * the dashboard's per-episode 拼接成片 rows. `path` may be any file/folder under
 * the drama. */
export async function listDramaEpisodes(path: string): Promise<DramaEpisodesResult> {
  const response = await fetch("/api/list-drama-episodes", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<DramaEpisodesResult>(response);
}

/** One episode's outcome from a drama-wide 定版 pass. */
export interface DramaTakesOutcome {
  episode: string;
  episode_rel: string;
  ok: boolean;
  selected: number;       // shots locked (ok only)
  skipped: number;        // shots without a render (ok only)
  reason: string | null;  // failure kind (ok=false only)
}

export interface DramaTakesResult {
  drama: string;
  outcomes: DramaTakesOutcome[];
}

/** 全局定版: lock every episode's newest takes to shot{NN}.mp4 in one pass
 * (drama-wide counterpart to selectEpisodeTakes). Does NOT concat. `path` may be
 * any file/folder under the drama. */
export async function selectDramaTakes(path: string): Promise<DramaTakesResult> {
  const response = await fetch("/api/select-drama-takes", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<DramaTakesResult>(response);
}

// ============================================================================
// Voice pool (follow-up 115). Mirrors the actor API surface above but
// targets local-composition voice profile prompts — no provider envs, no
// 429 retries client-side, no preview-then-confirm in v1 (the preview
// endpoint exists; the UI calls it inline for the prompt cards).
// ============================================================================

export const VOICE_ARCHETYPE_OPTIONS = [
  "effeminate_eunuch",
  "mighty_general",
  "gentle_palace_mistress",
  "aged_master",
  "young_jianghu_swordsman",
  "noble_emperor",
  "cold_assassin",
  "coquettish_concubine",
  "wise_elder_monk",
  "cunning_advisor",
] as const;

export const VOICE_ARCHETYPE_LABELS_ZH: Record<string, string> = {
  effeminate_eunuch: "陰柔太監音",
  mighty_general: "雄壯將軍音",
  gentle_palace_mistress: "柔美宮主音",
  aged_master: "蒼老掌門音",
  young_jianghu_swordsman: "年輕江湖俠音",
  noble_emperor: "威嚴帝王音",
  cold_assassin: "冷峻刺客音",
  coquettish_concubine: "嬌媚妃嬪音",
  wise_elder_monk: "慈悲高僧音",
  cunning_advisor: "陰險謀士音",
};

export const VOICE_GENDER_OPTIONS = ["male", "female", "neutral"] as const;
export const VOICE_AGE_OPTIONS = [
  "child",
  "teen",
  "young_adult",
  "middle_aged",
  "elderly",
] as const;
export const VOICE_PACE_OPTIONS = ["slow", "medium", "fast"] as const;
export const VOICE_PITCH_OPTIONS = ["low", "mid", "high"] as const;
export const VOICE_EMOTION_OPTIONS = [
  "calm",
  "authoritative",
  "playful",
  "menacing",
  "mournful",
  "flirtatious",
  "solemn",
  "whimsical",
] as const;

export const VOICE_AGE_LABELS_ZH: Record<string, string> = {
  child: "儿童",
  teen: "少年",
  young_adult: "青年",
  middle_aged: "中年",
  elderly: "老年",
};
export const VOICE_GENDER_LABELS_ZH: Record<string, string> = {
  male: "男声",
  female: "女声",
  neutral: "中性",
};
export const VOICE_EMOTION_LABELS_ZH: Record<string, string> = {
  calm: "平静",
  authoritative: "威严",
  playful: "俏皮",
  menacing: "阴狠",
  mournful: "哀婉",
  flirtatious: "撩拨",
  solemn: "庄重",
  whimsical: "随性",
};
export const VOICE_PACE_LABELS_ZH: Record<string, string> = {
  slow: "慢",
  medium: "中速",
  fast: "快",
};
export const VOICE_PITCH_LABELS_ZH: Record<string, string> = {
  low: "低音",
  mid: "中音",
  high: "高音",
};

export interface VoiceAttrs {
  archetype: string;
  gender: string;
  age_impression: string;
  pace?: string;
  pitch_register?: string;
  emotion_default?: string;
  tone?: string;
  signature_inflection?: string;
  notes?: string;
}

export interface VoiceInfo extends VoiceAttrs {
  id: string;
  sidecar_path: string;
  audio_path: string | null;
  mtime: number;
  archetype_label: string;
  is_assigned: boolean;
}

export interface GenerateVoicesRequest extends VoiceAttrs {
  count: number;
  seeds?: number[] | null;
}

export interface GenerateDiverseVoicesRequest {
  count: number;
  gender: string;
  age_impression?: string | null;
  notes?: string;
}

export interface VoicePreviewSlot {
  seed: number;
  prompt: string;
  archetype?: string;
  archetype_label?: string;
  attrs?: Record<string, unknown>;
}

export interface VoicePreviewResult {
  prompts: VoicePreviewSlot[];
}

export interface GenerateVoicesResult {
  generated: Array<{ id: string; sidecar_path: string; seed: number; archetype_label: string }>;
  errors: Array<{ requested_id: string; message: string }>;
}

export interface DeleteVoiceResult {
  from: string;
  to: string;
}

export interface VoiceAssignment {
  drama: string;
  role: string;
  notes: string;
  character_folder: string;
  character_folder_exists: boolean;
}

export interface VoiceAssignmentsResult {
  voice_id: string;
  assignments: VoiceAssignment[];
}

export interface UploadVoiceAudioResult {
  voice_id: string;
  audio_path: string;
  byte_size: number;
}

export interface ExtractVoiceAudioResult {
  voice_id: string;
  audio_path: string;
  extracted: Array<{ source: string; mp3_path: string; byte_size: number }>;
  failures: Array<{ source: string; error: string }>;
}

export async function listVoices(): Promise<{ voices: VoiceInfo[] }> {
  const response = await fetch("/api/voices", {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<{ voices: VoiceInfo[] }>(response);
}

export async function previewVoicePrompts(req: GenerateVoicesRequest): Promise<VoicePreviewResult> {
  const response = await fetch("/api/voices/preview-prompts", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<VoicePreviewResult>(response);
}

export async function previewDiverseVoicePrompts(
  req: GenerateDiverseVoicesRequest,
): Promise<VoicePreviewResult> {
  const response = await fetch("/api/voices/preview-diverse", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<VoicePreviewResult>(response);
}

export async function generateVoices(req: GenerateVoicesRequest): Promise<GenerateVoicesResult> {
  const response = await fetch("/api/voices/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<GenerateVoicesResult>(response);
}

export async function generateDiverseVoices(
  req: GenerateDiverseVoicesRequest,
): Promise<GenerateVoicesResult> {
  const response = await fetch("/api/voices/generate-diverse", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<GenerateVoicesResult>(response);
}

export async function deleteVoice(voiceId: string): Promise<DeleteVoiceResult> {
  const response = await fetch("/api/voices/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ voice_id: voiceId }),
  });
  return readJson<DeleteVoiceResult>(response);
}

export async function fetchVoiceAssignments(voiceId: string): Promise<VoiceAssignmentsResult> {
  const response = await fetch(
    `/api/voices/assignments?voice_id=${encodeURIComponent(voiceId)}`,
    {
      method: "GET",
      headers: { Accept: "application/json" },
    },
  );
  return readJson<VoiceAssignmentsResult>(response);
}

export async function uploadVoiceAudio(
  voiceId: string,
  file: File,
): Promise<UploadVoiceAudioResult> {
  const form = new FormData();
  form.append("audio", file, file.name);
  const response = await fetch(`/api/voices/${encodeURIComponent(voiceId)}/audio`, {
    method: "POST",
    body: form,
  });
  return readJson<UploadVoiceAudioResult>(response);
}

export async function extractVoiceAudio(
  voiceId: string,
): Promise<ExtractVoiceAudioResult> {
  const response = await fetch(
    `/api/voices/${encodeURIComponent(voiceId)}/extract-audio`,
    {
      method: "POST",
      headers: { Accept: "application/json" },
    },
  );
  return readJson<ExtractVoiceAudioResult>(response);
}

export async function castingAssignVoice(
  path: string,
  role: string,
  voiceId: string,
  notes?: string | null,
): Promise<CastingResult> {
  const response = await fetch("/api/casting/assign-voice", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, role, voice_id: voiceId, notes: notes ?? null }),
  });
  return readJson<CastingResult>(response);
}

export async function castingUnassignVoice(path: string, role: string): Promise<CastingResult> {
  const response = await fetch("/api/casting/assign-voice", {
    method: "DELETE",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, role }),
  });
  return readJson<CastingResult>(response);
}

// ============================================================================
// BGM pool (shared background-music library). Mirrors the voice API surface
// above but targets Stable Audio track prompts + rendered mp3s. Generation is
// SLOW (GPU subprocess) — callers must surface an in-progress state. Delete is
// refused (HTTP 409) when a drama's bgm.md still references the track; the
// references endpoint reports who references it (read-only).
// ============================================================================

/** The 12 emotion categories, in canonical order (slug → 中文 label). */
export const BGM_CATEGORY_OPTIONS = [
  "tension",
  "combat",
  "climax_hype",
  "faceslap",
  "tragic",
  "warm",
  "romance_pain",
  "suspense",
  "daily",
  "flashback",
  "theme_open",
  "system_cue",
] as const;

export const BGM_CATEGORY_LABELS_ZH: Record<string, string> = {
  tension: "紧张对峙",
  combat: "打斗",
  climax_hype: "高燃爽点",
  faceslap: "打脸爽感",
  tragic: "悲情",
  warm: "温情",
  romance_pain: "虐恋",
  suspense: "悬疑",
  daily: "日常",
  flashback: "回忆",
  theme_open: "片头主题",
  system_cue: "系统提示音",
};

// Curated free-text presets for the generation form. The backend accepts any
// free text (≤ 200 chars) for mood / instruments; these are convenience
// dropdowns so the user picks a common value first, then optionally overrides
// with the free-text box beside it. Pure UI vocabulary — no backend enum.
export const BGM_MOOD_PRESETS = [
  "阴森压抑",
  "紧张悬疑",
  "热血激昂",
  "悲伤凄凉",
  "温暖治愈",
  "甜蜜浪漫",
  "诡异不安",
  "轻松愉快",
  "怀旧感伤",
  "史诗恢弘",
  "空灵神秘",
] as const;

export const BGM_INSTRUMENT_PRESETS = [
  "弦乐 + 低音鼓",
  "钢琴独奏",
  "古筝 + 笛",
  "电子合成器",
  "管弦乐团",
  "大提琴独奏",
  "二胡",
  "鼓点打击乐",
  "氛围 pad + 长音",
  "钢琴 + 弦乐",
] as const;

export interface BgmInfo {
  id: string;
  category: string;
  category_label: string;
  sidecar_path: string;
  audio_path: string | null;
  seed: number;
  mtime: number;
  mood: string;
  bpm: number;
  duration: number;
  loopable: boolean;
  intensity: number;
  instruments: string;
  notes: string;
  is_referenced: boolean;
}

export interface GenerateBgmsRequest {
  count: number;
  category: string;
  mood?: string;
  bpm?: number;
  duration?: number;
  loopable?: boolean;
  intensity?: number;
  instruments?: string;
  notes?: string;
}

export interface BgmPreviewSlot {
  seed: number;
  prompt: string;
  category: string;
  category_label: string;
  attrs?: Record<string, unknown>;
}

export interface BgmPreviewResult {
  prompts: BgmPreviewSlot[];
}

export interface GenerateBgmsResult {
  generated: Array<{
    id: string;
    category: string;
    category_label: string;
    sidecar_path: string;
    audio_path: string | null;
    attrs?: Record<string, unknown>;
    seed: number;
  }>;
  errors: Array<{ requested_id: string; message: string }>;
}

export interface DeleteBgmResult {
  from: string;
  to: string;
}

export interface BgmReference {
  drama: string;
  location: string;
  cue_file: string;
  cue_lines: string[];
}

export interface BgmReferencesResult {
  bgm_id: string;
  references: BgmReference[];
}

export async function listBgms(): Promise<{ bgms: BgmInfo[] }> {
  const response = await fetch("/api/bgms", {
    method: "GET",
    headers: { Accept: "application/json" },
  });
  return readJson<{ bgms: BgmInfo[] }>(response);
}

export async function previewBgmPrompts(req: GenerateBgmsRequest): Promise<BgmPreviewResult> {
  const response = await fetch("/api/bgms/preview-prompts", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<BgmPreviewResult>(response);
}

export async function generateBgms(req: GenerateBgmsRequest): Promise<GenerateBgmsResult> {
  const response = await fetch("/api/bgms/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<GenerateBgmsResult>(response);
}

// Step 1: allocate tracks + write prompt-only sidecars (no audio rendered).
export async function createBgmPrompts(req: GenerateBgmsRequest): Promise<GenerateBgmsResult> {
  const response = await fetch("/api/bgms/create-prompts", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(req),
  });
  return readJson<GenerateBgmsResult>(response);
}

export interface BgmAudioResult {
  id: string;
  audio_path: string;
  imported_from?: string;
}

// Step 2a: render audio locally on GPU for an existing prompt-only track.
export async function generateBgmAudio(bgmId: string): Promise<BgmAudioResult> {
  const response = await fetch(`/api/bgms/${encodeURIComponent(bgmId)}/generate-audio`, {
    method: "POST",
    headers: { Accept: "application/json" },
  });
  return readJson<BgmAudioResult>(response);
}


export async function deleteBgm(bgmId: string): Promise<DeleteBgmResult> {
  const response = await fetch("/api/bgms/delete", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ bgm_id: bgmId }),
  });
  return readJson<DeleteBgmResult>(response);
}

export async function fetchBgmReferences(bgmId: string): Promise<BgmReferencesResult> {
  const response = await fetch(
    `/api/bgms/references?bgm_id=${encodeURIComponent(bgmId)}`,
    {
      method: "GET",
      headers: { Accept: "application/json" },
    },
  );
  return readJson<BgmReferencesResult>(response);
}

// Episode BGM arrangement: a sparse per-episode cue timeline
// (episodes/epNN/bgm/bgm.md). The user assigns a library bgm_NNNN to each cue
// slot (by emotion category), then burns the assigned cues onto the subtitled
// episode master ep{NN}_zh.mp4 → ep{NN}_zh_bgm.mp4 (re-burn overwrites).
export interface BgmCueInfo {
  start: number;
  end: number;
  category: string;
  bgm_id: string | null;
  assigned: boolean;
  vol: number;
  duck: boolean;
  fade_in: boolean;
  fade_out: boolean;
  comment: string;
}

export interface EpisodeBgmRead {
  episode: string;
  cue_file: string;
  cue_file_exists: boolean;
  source: string;
  source_exists: boolean;
  output: string;
  output_exists: boolean;
  cues: BgmCueInfo[];
}

export interface BurnEpisodeBgmResult {
  episode: string;
  out: string;
  used: Array<{ window: string; bgm_id: string; duck: boolean }>;
  skipped: Array<{ window: string; reason: string }>;
}

export async function readEpisodeBgm(path: string): Promise<EpisodeBgmRead> {
  const response = await fetch(`/api/episode-bgm?path=${encodeURIComponent(path)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  return readJson<EpisodeBgmRead>(response);
}

export async function assignBgmCue(
  path: string, start: number, end: number, bgmId: string,
): Promise<EpisodeBgmRead> {
  const response = await fetch("/api/episode-bgm/assign", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, start, end, bgm_id: bgmId }),
  });
  return readJson<EpisodeBgmRead>(response);
}

export async function unassignBgmCue(
  path: string, start: number, end: number,
): Promise<EpisodeBgmRead> {
  const response = await fetch("/api/episode-bgm/assign", {
    method: "DELETE",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, start, end }),
  });
  return readJson<EpisodeBgmRead>(response);
}

export async function burnEpisodeBgm(path: string): Promise<BurnEpisodeBgmResult> {
  const response = await fetch("/api/episode-bgm/burn", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path }),
  });
  return readJson<BurnEpisodeBgmResult>(response);
}

/** One scored metric within a seam method's result (M1–M4). */
export interface SeamMetric {
  score: number;
  [k: string]: number; // raw measurement fields (vel_break_pxf, min_ratio, peak_ratio, ssim…)
}

/** One method's score for a seam (chosen plan or a panel candidate). */
export interface SeamMethodScore {
  score?: number;
  floor_pass?: boolean;   // every metric ≥ 80 (the tiered-rule primary key)
  min_metric?: number;    // the lowest of M1–M4 (which metric is the laggard)
  label?: string;
  method?: string;
  trim?: number;
  depth?: number | null;
  M1_velocity?: SeamMetric;
  M2_no_freeze?: SeamMetric;
  M3_no_jump?: SeamMetric;
  M4_junction_ssim?: SeamMetric;
  frames?: number;
  error?: string;
}

/** Where a seam lands in the final ep timeline (for scrubbing to it). */
export interface SeamTime {
  at_s: number;
  start_s: number;
  end_s: number;
}

export interface SeamScored {
  seam: string;
  time?: SeamTime | null;
  chosen: SeamMethodScore;
  panel: SeamMethodScore[];
}

export interface SeamMetricDef {
  id: string;
  key: string;
  name: string;
  en: string;
  weight: number;
  unit: string;
  desc: string;
  good: string;
  bad: string;
}

/** Full seam-quality scorecard from /api/episode-seam-metrics. */
export interface SeamMetricsResult {
  episode: string;
  lang: EpisodeLang;
  weights: Record<string, number>;
  metric_defs: SeamMetricDef[];
  seams: SeamScored[];
  overall: number | null;
  overall_grade: string | null;
  ceiling: number | null;
  ceiling_grade: string | null;
  weakest: number | null;
  n_seams: number;
  metric_floor?: number;     // the per-metric floor (80) used by the tiered rule
  all_floor_pass?: boolean;  // every chosen seam clears the floor on every metric
  generated_at?: string;     // ISO time the sidecar was persisted (last build)
  persisted?: false;         // present (false) only when no sidecar exists yet
}

/** Read the PERSISTED scorecard from the last build — instant, no recompute. The
 * dashboard auto-loads this on page open. Returns {persisted:false} if not scored yet. */
export async function readEpisodeSeamScores(
  path: string,
  lang: EpisodeLang = "original",
): Promise<SeamMetricsResult> {
  const response = await fetch("/api/episode-seam-scores", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang }),
  });
  return readJson<SeamMetricsResult>(response);
}

/** Score every 承接 seam (optical-flow + SSIM metrics) and, when `compare`, rank a
 * standard method panel. Heavy (decodes + flow per seam) — call on demand. */
export async function scoreEpisodeSeams(
  path: string,
  lang: EpisodeLang = "original",
  compare: boolean = true,
): Promise<SeamMetricsResult> {
  const response = await fetch("/api/episode-seam-metrics", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ path, lang, compare }),
  });
  return readJson<SeamMetricsResult>(response);
}
