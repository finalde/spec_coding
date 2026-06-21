/** Reader: render-mode dispatch by file extension + path pattern. */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Breadcrumb } from "./Breadcrumb";
import { ParseFallback } from "./ParseFallback";
import { Editor } from "./Editor";
import { ShotPairView } from "./ShotPairView";
import { ShotlistTableView } from "./ShotlistTableView";
import { ImageRefView } from "./ImageRefView";
import { CastingView } from "./CastingView";
import { ActorView } from "./ActorView";
import { VoiceView } from "./VoiceView";
import { BgmView } from "./BgmView";
import { BgmEpisodePanel } from "./BgmEpisodePanel";
import { PerfScorePanel } from "./PerfScorePanel";
import { ShotRegenButton } from "./ShotRegenButton";
import { PerformanceSelector } from "./PerformanceSelector";
import { Renderer } from "../markdown/renderer";
import { CodeView } from "../markdown/CodeView";
import { JsonlView } from "../markdown/JsonlView";
import { SiblingMedia, isCharacterVideoPath, isSceneVideoPath } from "./SiblingMedia";
import { detectShotPair } from "../lib/shotPairing";
import { extractDramaAssets } from "../lib/dramas";
import { episodeDirOf, extractVideoPromptBody, shotMdPathsInEpisode } from "../lib/videoPrompts";
import { announceToast } from "../lib/announce";
import {
  archiveMedia,
  burnDramaSubtitles,
  burnEpisodeSubtitles,
  concatEpisode,
  concatShotCharacters,
  deleteMedia,
  extractCharacterViews,
  extractFrames,
  extractScenePlates,
  fetchFile,
  mediaUrl,
  putFile,
  scaffoldEpisodeSubtitles,
  unarchiveMedia,
} from "../api";
import type { EpisodeLang, SubtitleLang } from "../api";
import { ApiError, type FileResult, type TreeNode } from "../types";

const IMAGE_EXTS = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"]);
const VIDEO_EXTS = new Set([".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"]);
const AUDIO_EXTS = new Set([".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"]);
const SHOT_MD_RE = /^ai_videos\/[^_][^/]*\/(?:episodes\/ep\d+\/)?prompts\/shot\d+\/shot\d+\.md$/;

export interface ReaderProps {
  tree: TreeNode | null;
  knownPaths: string[];
  onSaved: () => void;
}

export function Reader({ tree, knownPaths, onSaved }: ReaderProps): JSX.Element {
  const location = useLocation();
  const navigate = useNavigate();
  const path = useMemo<string | null>(() => {
    if (!location.pathname.startsWith("/file/")) return null;
    const encoded = location.pathname.slice("/file/".length);
    try { return decodeURIComponent(encoded); } catch { return null; }
  }, [location.pathname]);

  const dramaAssets = useMemo(() => extractDramaAssets(tree, path), [tree, path]);

  const [file, setFile] = useState<FileResult | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [editing, setEditing] = useState<boolean>(false);
  const [saveError, setSaveError] = useState<Error | null>(null);
  const [conflict, setConflict] = useState<{ current_mtime: string } | null>(null);
  const [archiving, setArchiving] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [extracting, setExtracting] = useState<boolean>(false);
  const [extractingViews, setExtractingViews] = useState<boolean>(false);
  const [extractingPlates, setExtractingPlates] = useState<boolean>(false);
  const [concatBusy, setConcatBusy] = useState<boolean>(false);
  const [episodeConcatBusy, setEpisodeConcatBusy] = useState<boolean>(false);
  const [copyingPrompts, setCopyingPrompts] = useState<boolean>(false);
  const [scaffoldEpBusy, setScaffoldEpBusy] = useState<boolean>(false);
  const [burnDramaBusy, setBurnDramaBusy] = useState<boolean>(false);
  const [burnEpisodeBusy, setBurnEpisodeBusy] = useState<boolean>(false);

  const ext = path ? extOf(path) : "";
  const isPerfEntry = path ? /_performances\/[^/]+\/perf_\d{4}\/perf_\d{4}\.md$/.test(path) : false;
  const isShotEntry = path ? /\/shots\/[^/]+\/shot[^/]*\.md$/.test(path) : false;
  const isShotMdEntry = path ? /\/shot\d+\/shot\d+\.md$/.test(path) : false;
  const isMediaImage = IMAGE_EXTS.has(ext);
  const isMediaVideo = VIDEO_EXTS.has(ext);
  const isMediaAudio = AUDIO_EXTS.has(ext);
  const isMediaOnly = isMediaVideo || isMediaImage || isMediaAudio;

  const load = useCallback(async () => {
    if (!path) return;
    if (isMediaOnly) {
      // Media files (video / non-png-jpg images) are streamed via /api/media —
      // skip /api/file fetch entirely (videos can exceed the 1 MB limit).
      setFile({ path, content: "", encoding: "media", bytes: 0, mtime: 0, mtime_http: "" });
      setError(null);
      return;
    }
    try {
      const f = await fetchFile(path);
      setFile(f);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
    }
  }, [path, isMediaOnly]);

  useEffect(() => {
    setFile(null); setError(null); setEditing(false); setSaveError(null); setConflict(null);
    void load();
  }, [load]);

  const onSave = useCallback(async (newContent: string): Promise<void> => {
    if (!file || !path) return;
    try {
      const result = await putFile(path, newContent, { ifUnmodifiedSince: file.mtime_http });
      setFile({ ...file, content: newContent, ...result });
      setSaveError(null); setConflict(null);
      onSaved();
    } catch (err) {
      if (err instanceof ApiError) {
        if (err.status === 409 && err.detail?.kind === "stale_write") {
          const cm = (err.detail as { current_mtime?: string }).current_mtime;
          setConflict({ current_mtime: cm ?? "" });
        } else { setSaveError(err); }
      } else if (err instanceof Error) { setSaveError(err); }
      throw err;
    }
  }, [file, onSaved, path]);

  const setDocumentTitle = useCallback((dirty: boolean) => {
    if (!path) return;
    const base = path.split("/").pop() ?? path;
    document.title = dirty ? `* ${base} — ai_video_management` : `${base} — ai_video_management`;
  }, [path]);

  const onArchiveToggle = useCallback(async () => {
    if (!path) return;
    const parts = path.split("/");
    const inArchive = parts.length >= 2 && parts[parts.length - 2] === "archive";
    setArchiving(true);
    try {
      const result = inArchive ? await unarchiveMedia(path) : await archiveMedia(path);
      announceToast(`${inArchive ? "Unarchived" : "Archived"} ${parts[parts.length - 1] ?? path}`);
      onSaved();
      navigate(`/file/${encodeURIComponent(result.to)}`);
    } catch (err) {
      announceToast(`${inArchive ? "Unarchive" : "Archive"} failed: ${archiveErrorKind(err)}`);
    } finally {
      setArchiving(false);
    }
  }, [path, onSaved, navigate]);

  const onDeleteClick = useCallback(async () => {
    if (!path) return;
    const name = path.split("/").pop() ?? path;
    if (!window.confirm(`Move ${name} to _deleted/?`)) return;
    setDeleting(true);
    try {
      const result = await deleteMedia(path);
      announceToast(`Deleted ${name}`);
      onSaved();
      navigate(`/file/${encodeURIComponent(result.to)}`);
    } catch (err) {
      announceToast(`Delete failed: ${archiveErrorKind(err)}`);
    } finally {
      setDeleting(false);
    }
  }, [path, onSaved, navigate]);

  const onConcatShotCharactersClick = useCallback(async () => {
    if (!path) return;
    setConcatBusy(true);
    try {
      const result = await concatShotCharacters(path);
      const usedNames = result.used.map((u) => u.role || u.character_folder).join(", ");
      const skippedNames = result.skipped.map((s) => `${s.role || s.character_folder} (${s.reason})`).join(", ");
      let summary: string;
      if (result.out) {
        summary = `已合成 ${result.out.split("/").pop()} — 使用 ${result.used.length} 个角色`;
        if (usedNames) summary += ` [${usedNames}]`;
        if (result.skipped.length > 0) summary += ` · 跳过 ${result.skipped.length}: ${skippedNames}`;
      } else {
        summary = `未生成 — 没有角色文件夹包含 mp4`;
        if (result.skipped.length > 0) summary += ` · 跳过 ${result.skipped.length}: ${skippedNames}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`生成角色合辑失败: ${archiveErrorKind(err)}`);
    } finally {
      setConcatBusy(false);
    }
  }, [path, onSaved]);

  const onConcatEpisodeClick = useCallback(async (lang: EpisodeLang) => {
    if (!path) return;
    setEpisodeConcatBusy(true);
    try {
      const result = await concatEpisode(path, lang);
      const skippedNames = result.skipped.map((s) => `${s.shot} (${s.reason})`).join(", ");
      let summary: string;
      if (result.out) {
        summary = `已合成 ${result.out.split("/").pop()} — 拼接 ${result.used.length} 个镜头`;
        if (result.skipped.length > 0) summary += ` · 跳过 ${result.skipped.length}: ${skippedNames}`;
      } else {
        const noun = lang === "original" ? "renders/ mp4" : `shot{NN}_${lang === "both" ? "zhen" : lang}.mp4`;
        summary = `未生成 — 没有镜头包含 ${noun}`;
        if (result.skipped.length > 0) summary += ` · 跳过 ${result.skipped.length}: ${skippedNames}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`合成本集视频失败: ${archiveErrorKind(err)}`);
    } finally {
      setEpisodeConcatBusy(false);
    }
  }, [path, onSaved]);

  const onScaffoldEpisodeSubtitlesClick = useCallback(async () => {
    if (!path) return;
    setScaffoldEpBusy(true);
    try {
      const result = await scaffoldEpisodeSubtitles(path);
      const ok = result.outcomes.filter((o) => o.ok).length;
      const skipped = result.outcomes.filter((o) => !o.ok);
      let summary = `已重生 ${ok} 个镜头的字幕`;
      if (skipped.length > 0) {
        const names = skipped.map((s) => `${s.shot} (${s.reason})`).join(", ");
        summary += ` · 跳过 ${skipped.length}: ${names}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`重生本集字幕失败: ${archiveErrorKind(err)}`);
    } finally {
      setScaffoldEpBusy(false);
    }
  }, [path, onSaved]);

  const onBurnDramaSubtitlesClick = useCallback(async (lang: SubtitleLang) => {
    if (!path) return;
    setBurnDramaBusy(true);
    try {
      const result = await burnDramaSubtitles(path, lang);
      const ok = result.outcomes.filter((o) => o.ok).length;
      const skipped = result.outcomes.filter((o) => !o.ok);
      let summary = `已为 ${ok} 个镜头烧入${lang === "both" ? "中英" : lang === "en" ? "英文" : "中文"}字幕`;
      if (skipped.length > 0) {
        const names = skipped.map((s) => `${s.episode}/${s.shot} (${s.reason})`).join(", ");
        summary += ` · 跳过 ${skipped.length}: ${names}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`全剧烧字幕失败: ${archiveErrorKind(err)}`);
    } finally {
      setBurnDramaBusy(false);
    }
  }, [path, onSaved]);

  const onBurnEpisodeSubtitlesClick = useCallback(async (lang: SubtitleLang) => {
    if (!path) return;
    setBurnEpisodeBusy(true);
    try {
      const result = await burnEpisodeSubtitles(path, lang);
      const ok = result.outcomes.filter((o) => o.ok).length;
      const skipped = result.outcomes.filter((o) => !o.ok);
      let summary = `已为本集 ${ok} 个镜头烧入${lang === "both" ? "中英" : lang === "en" ? "英文" : "中文"}字幕`;
      if (skipped.length > 0) {
        const names = skipped.map((s) => `${s.shot} (${s.reason})`).join(", ");
        summary += ` · 跳过 ${skipped.length}: ${names}`;
      }
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`本集烧字幕失败: ${archiveErrorKind(err)}`);
    } finally {
      setBurnEpisodeBusy(false);
    }
  }, [path, onSaved]);

  const onCopyAllVideoPromptsClick = useCallback(async () => {
    if (!path) return;
    const epDir = episodeDirOf(path);
    if (!epDir) { announceToast("无法定位本集文件夹"); return; }
    const shotPaths = shotMdPathsInEpisode(knownPaths, epDir);
    if (shotPaths.length === 0) { announceToast("本集未找到 shot prompt"); return; }
    setCopyingPrompts(true);
    try {
      const bodies: string[] = [];
      let missing = 0;
      for (const sp of shotPaths) {
        try {
          const f = await fetchFile(sp);
          const body = extractVideoPromptBody(f.content);
          if (body) bodies.push(body);
          else missing += 1;
        } catch {
          missing += 1;
        }
      }
      if (bodies.length === 0) { announceToast("未提取到任何视频 prompt"); return; }
      try {
        await navigator.clipboard.writeText(bodies.join("\n\n"));
        announceToast(
          `已复制 ${bodies.length} 个视频 prompt${missing > 0 ? `（${missing} 个缺失/跳过）` : ""}`,
        );
      } catch {
        announceToast("剪贴板不可用（浏览器拒绝）");
      }
    } finally {
      setCopyingPrompts(false);
    }
  }, [path, knownPaths]);

  const onExtractFramesClick = useCallback(async () => {
    if (!path) return;
    const name = path.split("/").pop() ?? path;
    setExtracting(true);
    try {
      const result = await extractFrames(path);
      const okCount = result.frames.length;
      const failCount = result.failures.length;
      const noun = okCount === 1 ? "frame" : "frames";
      const summary =
        failCount === 0
          ? `Extracted ${okCount} ${noun} from ${name} → frames/`
          : `Extracted ${okCount} ${noun} from ${name} (${failCount} failed)`;
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`Extract frames failed: ${archiveErrorKind(err)}`);
    } finally {
      setExtracting(false);
    }
  }, [path, onSaved]);

  const onExtractCharacterViewsClick = useCallback(async () => {
    if (!path) return;
    const name = path.split("/").pop() ?? path;
    setExtractingViews(true);
    try {
      const result = await extractCharacterViews(path);
      const okCount = result.views.length + (result.audio ? 1 : 0) + (result.trim ? 1 : 0);
      const failCount = result.failures.length;
      const summary =
        failCount === 0
          ? `Extracted ${okCount} 文件 (三视图 + 音频 + 前3s) from ${name} → views/`
          : `Extracted ${okCount} from ${name} (${failCount} failed)`;
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`Extract views failed: ${archiveErrorKind(err)}`);
    } finally {
      setExtractingViews(false);
    }
  }, [path, onSaved]);

  const onExtractScenePlatesClick = useCallback(async () => {
    if (!path) return;
    setExtractingPlates(true);
    try {
      const result = await extractScenePlates(path);
      const okCount = result.plates.length;
      const dirs = result.plates.map((p) => p.direction).join("/");
      const failCount = result.failures.length;
      const summary =
        failCount === 0
          ? `已截取 ${okCount} 张方向背景图（${dirs}）→ 各 bg 文件夹`
          : `已截取 ${okCount} 张（${dirs}），${failCount} 张失败`;
      announceToast(summary);
      onSaved();
    } catch (err) {
      announceToast(`截取方向背景图失败: ${archiveErrorKind(err)}`);
    } finally {
      setExtractingPlates(false);
    }
  }, [path, onSaved]);

  if (!path) return <div className="muted">No file selected.</div>;
  if (error) {
    return (
      <div className="reader">
        <div role="alert" className="save-error-banner">
          {error instanceof ApiError ? `${error.status} ${apiErrorLabel(error)}` : error.message}
        </div>
      </div>
    );
  }
  if (!file) return <div className="muted">Loading…</div>;

  const isImage = isMediaImage;
  const isVideo = isMediaVideo;
  const isAudio = isMediaAudio;
  const isMarkdown = ext === ".md";
  const isJsonl = ext === ".jsonl";
  const isCode = ext === ".json" || ext === ".yaml" || ext === ".yml";
  const isTxt = ext === ".txt";

  const shotPair = isMarkdown ? detectShotPair(path) : null;
  const isShotPair = shotPair !== null;
  const isShotlistTable = path.startsWith("ai_videos/") && path.endsWith("/shotlist.md");
  // Any markdown file sitting directly in an episode folder (episode.md /
  // shotlist.md / script.md / dialogue.md / publish.md) — NOT the per-shot
  // shots/shotNN/shotNN.md (extra path segment). Anchors the episode-concat button
  // so it's reachable from anywhere "inside the episode".
  // episode-level md: `…/episodes/ep{NN}/{file}.md`, where `episodes/` is at
  // the drama root (legacy) OR under a stage folder (`4_剧本/episodes/`).
  const isEpisodeFile = isMarkdown && /^ai_videos\/[^_][^/]+\/(?:[^/]+\/)?episodes\/ep\d+\/[^/]+\.md$/.test(path);
  const isImageRef = (isMarkdown && /\/ref_images\/[^/]+_seedream\.md$/.test(path));
  // casting.md sits at the drama root (legacy) OR under a stage folder
  // (staged pipeline: `2_世界观人设/casting.md`). Match it anywhere under a
  // (non-`_`) drama so CastingView renders in both layouts.
  const isCasting = isMarkdown && /^ai_videos\/[^_][^/]*\/(?:[^/]+\/)*casting\.md$/.test(path);
  const isActor = isMarkdown && /^ai_videos\/_actors\/actor_[^/]+\/actor_[^/]+\.md$/.test(path);
  const isVoice = isMarkdown && /^ai_videos\/_voices\/voice_[^/]+\/voice_[^/]+\.md$/.test(path);
  const isBgm = isMarkdown && /^ai_videos\/_bgm\/[^/]+\/bgm_[^/]+\/bgm_[^/]+\.md$/.test(path);
  // Episode BGM cue timeline: `…/episodes/ep{NN}/bgm/bgm.md` (the extra `bgm/`
  // segment keeps it distinct from the episode-level `isEpisodeFile` files).
  const isEpisodeBgm = isMarkdown && /^ai_videos\/[^_][^/]+\/(?:[^/]+\/)*episodes\/ep\d+\/bgm\/bgm\.md$/.test(path);
  const isShotMd = isMarkdown && SHOT_MD_RE.test(path);
  // Drama homepage (`ai_videos/{drama}/README.md`) — anchors the drama-wide
  // "burn subtitles into every shot of every episode" action.
  const isDramaReadme = isMarkdown && /^ai_videos\/[^_][^/]+\/README\.md$/i.test(path);

  const filename = path.split("/").pop() ?? path;
  const pathParts = path.split("/");
  const isArchivedFile = pathParts.length >= 2 && pathParts[pathParts.length - 2] === "archive";
  const isDeletedFile = path.startsWith("ai_videos/_deleted/");
  const mediaActionsBusy = archiving || deleting || extracting || extractingViews || extractingPlates;
  const archiveLabel = isArchivedFile
    ? (archiving ? "Unarchiving…" : "↺ Unarchive")
    : (archiving ? "Archiving…" : "📦 Archive");
  const deleteLabel = deleting ? "Deleting…" : "🗑 Delete";
  const extractLabel = extracting ? "⏳ Extracting…" : "🎞 Extract Frames";
  const viewsExtractLabel = extractingViews ? "⏳ 提取中…" : "🖼 提取三视图+音频+前3s";
  const showViewsBtn = isVideo && !isArchivedFile && !isDeletedFile && isCharacterVideoPath(path);
  const platesExtractLabel = extractingPlates ? "⏳ 截取中…" : "🧭 截取方向背景图";
  const showPlatesBtn = isVideo && !isArchivedFile && !isDeletedFile && isSceneVideoPath(path);

  return (
    <div className="reader">
      <div className="reader-toolbar" role="toolbar" aria-label="File toolbar">
        <Breadcrumb
          path={path}
          knownPaths={knownPaths}
          onNavigate={(target) => navigate(`/file/${encodeURIComponent(target)}`)}
        />
        {isShotMd ? (
          <button type="button" className="reader-shot-concat-btn"
            onClick={onConcatShotCharactersClick} disabled={concatBusy}
            aria-label="Build a character reel by concatenating the first mp4 found in each involved character's folder"
            title="Parse the 出场角色 table, take the alphabetically-first mp4 inside each character folder (skipping only folders that have no mp4), trim each to 2s, and ffmpeg-concat them into <shotNN>_chars.mp4 next to this shot md.">
            {concatBusy ? "⏳ 生成中…" : "🎬 生成角色合辑"}
          </button>
        ) : null}
        {isEpisodeFile ? (
          <button type="button" className="reader-copy-prompts-btn"
            onClick={onCopyAllVideoPromptsClick} disabled={copyingPrompts}
            aria-label="Copy every shot's video prompt for this episode to the clipboard"
            title="把本集每个 shot 的【视频 prompt】代码块按 shot 顺序依次拼接、一次复制到剪贴板（只含视频 prompt，不含台词配音；块间空行分隔）。">
            {copyingPrompts ? "⏳ 复制中…" : "📋 复制全部视频 prompt"}
          </button>
        ) : null}
        {isEpisodeFile ? (
          <button type="button" className="reader-scaffold-ep-btn"
            onClick={onScaffoldEpisodeSubtitlesClick} disabled={scaffoldEpBusy}
            aria-label="Regenerate subtitles.md for every shot in this episode"
            title="为本集每个 shot 从 shot.md 重新生成 subtitles.md 台词时间轴（按标点拆句、按字数估算时间窗、覆盖旧文件；无台词的镜头自动跳过）。生成后逐镜微调，再用各 render 的「💬」烧字幕。">
            {scaffoldEpBusy ? "⏳ 重生中…" : "📝 重生本集字幕"}
          </button>
        ) : null}
        {isDramaReadme ? (
          <span className="reader-episode-concat-group" role="group" aria-label="全剧烧字幕（按语言）">
            {([
              ["zh", "💬 全剧·中文字幕", "为全剧每集每镜取最新 render + subtitles.md 烧中文字幕 → shot{NN}_zh.mp4"],
              ["en", "💬 全剧·EN", "为全剧每集每镜烧英文字幕 → shot{NN}_en.mp4"],
              ["both", "💬 全剧·中英", "为全剧每集每镜烧中英字幕 → shot{NN}_zhen.mp4"],
            ] as [SubtitleLang, string, string][]).map(([lang, label, title]) => (
              <button key={lang} type="button" className="reader-episode-concat-btn"
                onClick={() => onBurnDramaSubtitlesClick(lang)} disabled={burnDramaBusy}
                aria-label={`Burn ${lang} subtitles into every shot of every episode`}
                title={`遍历全剧所有 episodes/ep*/shots/shot*，每镜取最新 render 烧入字幕（已存在则覆盖）。缺 render 或缺 subtitles.md 的镜头自动跳过。${title}`}>
                {burnDramaBusy ? "⏳" : label}
              </button>
            ))}
          </span>
        ) : null}
        {isShotlistTable ? (
          <span className="reader-episode-concat-group" role="group" aria-label="本集烧字幕（按语言）">
            {([
              ["zh", "💬 本集·中文字幕", "为本集每镜取最新 render + subtitles.md 烧中文字幕 → shot{NN}_zh.mp4"],
              ["en", "💬 本集·EN", "为本集每镜烧英文字幕 → shot{NN}_en.mp4"],
              ["both", "💬 本集·中英", "为本集每镜烧中英字幕 → shot{NN}_zhen.mp4"],
            ] as [SubtitleLang, string, string][]).map(([lang, label, title]) => (
              <button key={lang} type="button" className="reader-episode-concat-btn"
                onClick={() => onBurnEpisodeSubtitlesClick(lang)} disabled={burnEpisodeBusy}
                aria-label={`Burn ${lang} subtitles into every shot of this episode only`}
                title={`只遍历本集 episodes/ep{NN}/shots/shot*，每镜取最新 render 烧入字幕（已存在则覆盖）。缺 render 或缺 subtitles.md 的镜头自动跳过。${title}`}>
                {burnEpisodeBusy ? "⏳" : label}
              </button>
            ))}
          </span>
        ) : null}
        {isEpisodeFile ? (
          <span className="reader-episode-concat-group" role="group" aria-label="合成本集视频（按语言）">
            {([
              ["original", "🎬 合成(原片)", "无字幕：每镜取 renders/ 最新 mp4 → ep{NN}.mp4"],
              ["zh", "🎬 中文", "每镜取 shot{NN}_zh.mp4 → ep{NN}_zh.mp4"],
              ["en", "🎬 EN", "每镜取 shot{NN}_en.mp4 → ep{NN}_en.mp4"],
              ["both", "🎬 中英", "每镜取 shot{NN}_zhen.mp4 → ep{NN}_zhen.mp4"],
            ] as [EpisodeLang, string, string][]).map(([lang, label, title]) => (
              <button key={lang} type="button" className="reader-episode-concat-btn"
                onClick={() => onConcatEpisodeClick(lang)} disabled={episodeConcatBusy}
                aria-label={`Concatenate episode (${lang})`}
                title={`按镜头顺序 ffmpeg 拼接成整集放在本集文件夹下（已存在则覆盖）。缺该片源的镜头自动跳过。${title}`}>
                {episodeConcatBusy ? "⏳" : label}
              </button>
            ))}
          </span>
        ) : null}
        {/* Per follow-up 2026-05-30: hide whole-file Edit for ai_videos paths.
            Users must edit prompts via the per-code-block ✏ Edit affordance
            inside Renderer / CopyableCode (which opens PromptStructuredEditor).
            This prevents accidental "整個page edit" when the goal is to edit a
            single prompt block.  Other markdown files (specs, README, etc.)
            still get the whole-file editor. */}
        {!isImage && !isVideo && !isAudio && !path.startsWith("ai_videos/") ? (
          <button type="button" className="reader-edit-toggle"
            onClick={() => setEditing((e) => !e)}
            aria-label={editing ? "Stop editing" : "Edit file"} aria-pressed={editing}>
            ✎ {editing ? "Editing" : "Edit"}
          </button>
        ) : null}
      </div>
      {editing && !isImage && !isVideo && !isAudio && !isShotPair && !isImageRef && !isCasting && !isActor ? (
        <Editor
          initialContent={file.content} filename={filename}
          onSave={onSave} onClose={() => setEditing(false)}
          onReload={async () => { await load(); }}
          saveError={saveError} conflict={conflict}
          onClearConflict={() => setConflict(null)}
          onDirtyChange={setDocumentTitle}
        />
      ) : (
        <div className="reader-body">
          {isVideo ? (
            <div className="media-view">
              <video controls preload="metadata" src={mediaUrl(path)} />
              {!isDeletedFile ? (
                <div className="reader-media-actions">
                  {!isArchivedFile ? (
                    <button type="button" className="reader-media-extract-btn"
                      onClick={onExtractFramesClick} disabled={mediaActionsBusy}
                      aria-label={`Extract 5 reference frames from ${filename}`}
                      title="Extract 5 canonical reference frames (hero / reverse / vert / mid / detail) into ./frames/ — overwrites previous extraction from this scene folder">
                      {extractLabel}
                    </button>
                  ) : null}
                  {showViewsBtn ? (
                    <button type="button" className="reader-media-views-btn"
                      onClick={onExtractCharacterViewsClick} disabled={mediaActionsBusy}
                      aria-label={`Extract 3 views, audio and first-3s trim from ${filename}`}
                      title="一键提取 5 个文件到 ./views/：三视图 (front / side / back .png) + 音频 (.mp3) + 原片前 3 秒 (_trim3s.mp4) — 适用于 v10 character turntable (7s locked-framing + 180° slow orbit)">
                      {viewsExtractLabel}
                    </button>
                  ) : null}
                  {showPlatesBtn ? (
                    <button type="button" className="reader-media-plates-btn"
                      onClick={onExtractScenePlatesClick} disabled={mediaActionsBusy}
                      aria-label={`Extract per-direction bg plates from ${filename}`}
                      title="从场景 walk-through mp4 按各 bg 朝向的截帧时点抽帧，写入对应 bg{N}_{方位}/ 文件夹。截帧秒数读自本场景 md「背景图系统 index」表（与 步骤二 walk-through 时间轴一致）。">
                      {platesExtractLabel}
                    </button>
                  ) : null}
                  <button type="button" className="reader-media-archive-btn"
                    onClick={onArchiveToggle} disabled={mediaActionsBusy}
                    aria-label={isArchivedFile ? `Unarchive ${filename}` : `Archive ${filename}`}>
                    {archiveLabel}
                  </button>
                  <button type="button" className="reader-media-delete-btn"
                    onClick={onDeleteClick} disabled={mediaActionsBusy}
                    aria-label={`Delete ${filename}`}>
                    {deleteLabel}
                  </button>
                </div>
              ) : null}
            </div>
          ) : isMediaImage ? (
            <div className="media-view">
              <img src={mediaUrl(path)} alt={filename} />
              {!isDeletedFile ? (
                <div className="reader-media-actions">
                  <button type="button" className="reader-media-archive-btn"
                    onClick={onArchiveToggle} disabled={mediaActionsBusy}
                    aria-label={isArchivedFile ? `Unarchive ${filename}` : `Archive ${filename}`}>
                    {archiveLabel}
                  </button>
                  <button type="button" className="reader-media-delete-btn"
                    onClick={onDeleteClick} disabled={mediaActionsBusy}
                    aria-label={`Delete ${filename}`}>
                    {deleteLabel}
                  </button>
                </div>
              ) : null}
            </div>
          ) : isAudio ? (
            <div className="media-view">
              <audio controls preload="metadata" src={mediaUrl(path)} />
              {!isDeletedFile ? (
                <div className="reader-media-actions">
                  <button type="button" className="reader-media-archive-btn"
                    onClick={onArchiveToggle} disabled={mediaActionsBusy}
                    aria-label={isArchivedFile ? `Unarchive ${filename}` : `Archive ${filename}`}>
                    {archiveLabel}
                  </button>
                  <button type="button" className="reader-media-delete-btn"
                    onClick={onDeleteClick} disabled={mediaActionsBusy}
                    aria-label={`Delete ${filename}`}>
                    {deleteLabel}
                  </button>
                </div>
              ) : null}
            </div>
          ) : isCasting ? (
            <CastingView castingPath={path} onChange={onSaved} />
          ) : isActor ? (
            <ActorView primaryFile={file} primaryPath={path} knownPaths={knownPaths} tree={tree} onSaved={onSaved} />
          ) : isVoice ? (
            <VoiceView primaryFile={file} primaryPath={path} knownPaths={knownPaths} tree={tree} onSaved={onSaved} />
          ) : isBgm ? (
            <BgmView primaryFile={file} primaryPath={path} knownPaths={knownPaths} onSaved={onSaved} />
          ) : isEpisodeBgm ? (
            <BgmEpisodePanel path={path} onSaved={onSaved} />
          ) : isImageRef ? (
            <>
              <ImageRefView primaryFile={file} primaryPath={path} knownPaths={knownPaths} onSaved={onSaved} />
              <SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />
            </>
          ) : isShotPair ? (
            <>
              <ShotPairView primaryFile={file} primaryPath={path} knownPaths={knownPaths} onSaved={onSaved} />
              <SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />
            </>
          ) : isShotlistTable ? (
            <ParseFallback rawText={file.content} componentName="ShotlistTableView">
              <ShotlistTableView content={file.content} shotlistPath={path} />
            </ParseFallback>
          ) : isJsonl ? (
            <ParseFallback rawText={file.content} componentName="JsonlView">
              <JsonlView content={file.content} />
            </ParseFallback>
          ) : isCode ? (
            <ParseFallback rawText={file.content} componentName="CodeView">
              <CodeView content={file.content} filename={filename} />
            </ParseFallback>
          ) : isMarkdown ? (
            <ParseFallback rawText={file.content} componentName="MarkdownView">
              {isPerfEntry ? (
                <PerfScorePanel path={path} content={file.content} onScored={async () => { await load(); onSaved(); }} />
              ) : null}
              {isShotEntry ? <ShotRegenButton path={path} content={file.content} /> : null}
              {isShotMdEntry ? (
                <PerformanceSelector shotPath={path} mtime={file.mtime_http} content={file.content} />
              ) : null}
              <Renderer
                content={file.content}
                currentPath={path}
                knownPaths={knownPaths}
                editEnabled={path.startsWith("ai_videos/")}
                mtimeHttp={file.mtime_http}
                onSaved={async () => { await load(); onSaved(); }}
                characterOptions={dramaAssets.characters}
                sceneOptions={dramaAssets.scenes}
              />
              <SiblingMedia currentPath={path} knownPaths={knownPaths} onChange={onSaved} />
            </ParseFallback>
          ) : isTxt ? (
            <pre className="text-view">{file.content}</pre>
          ) : (
            <pre className="text-view">{file.content}</pre>
          )}
        </div>
      )}
    </div>
  );
}

function apiErrorLabel(err: ApiError): string {
  if (err.status === 404) return "not found";
  if (err.status === 400) return err.detail?.kind ?? "bad request";
  if (err.status === 413) return "file too large";
  if (err.status === 403) return "forbidden";
  if (err.status === 409) return "stale write";
  return err.detail?.kind ?? err.message;
}

function extOf(path: string): string {
  const dot = path.lastIndexOf(".");
  if (dot < 0) return "";
  return path.slice(dot).toLowerCase();
}

function archiveErrorKind(err: unknown): string {
  if (err instanceof ApiError) return err.detail?.kind ?? `HTTP ${err.status}`;
  if (err instanceof Error) return err.message;
  return "unknown_error";
}
