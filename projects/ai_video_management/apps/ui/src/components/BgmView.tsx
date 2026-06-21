import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BGM_CATEGORY_LABELS_ZH,
  deleteBgm,
  fetchBgmReferences,
  generateBgmAudio,
  mediaUrl,
  type BgmReference,
} from "../api";
import { ApiError, type FileResult } from "../types";

export interface BgmViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
  onSaved?: () => void;
}

const BGM_ID_RE = /^ai_videos\/_bgm\/[^/]+\/(bgm_\d{4,})\/bgm_\d{4,}\.md$/;
const AUDIO_EXT_RE = /\.(mp3|wav|m4a)$/i;

export function BgmView({ primaryFile, primaryPath, knownPaths, onSaved }: BgmViewProps): JSX.Element {
  const navigate = useNavigate();
  const bgmId = useMemo<string | null>(() => {
    const m = BGM_ID_RE.exec(primaryPath);
    return m ? m[1] : null;
  }, [primaryPath]);

  const audioPath = useMemo<string | null>(() => {
    if (!bgmId) return null;
    // Sidecar lives at ai_videos/_bgm/<category>/bgm_NNNN/bgm_NNNN.md; the mp3 is
    // a sibling inside the same bgm_NNNN/ folder.
    const dir = primaryPath.slice(0, primaryPath.lastIndexOf("/") + 1);
    for (const p of knownPaths) {
      if (p.startsWith(dir) && AUDIO_EXT_RE.test(p)) return p;
    }
    return null;
  }, [bgmId, primaryPath, knownPaths]);

  const promptText = useMemo<string | null>(() => extractFencedCode(primaryFile.content), [primaryFile.content]);
  const metadata = useMemo(
    () => localizeMetadata(parseMetadataTable(primaryFile.content)),
    [primaryFile.content],
  );

  const [references, setReferences] = useState<BgmReference[] | null>(null);
  const [referencesError, setReferencesError] = useState<string | null>(null);
  const [copyTick, setCopyTick] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  // Audio rendered/imported this session (sidecar's knownPaths won't refresh
  // until the parent re-fetches the tree); used to show the player immediately.
  const [localAudioPath, setLocalAudioPath] = useState<string | null>(null);
  const [audioBusy, setAudioBusy] = useState<"gpu" | null>(null);
  const effectiveAudio = audioPath ?? localAudioPath;

  const onGenerateAudio = useCallback(async () => {
    if (!bgmId || audioBusy) return;
    setAudioBusy("gpu");
    setToast(null);
    try {
      const r = await generateBgmAudio(bgmId);
      setLocalAudioPath(r.audio_path);
      setToast({ kind: "ok", text: `已本地生成音频：${r.audio_path.split("/").pop()}` });
      if (onSaved) onSaved();
    } catch (err) {
      const msg = err instanceof ApiError
        ? `本地生成失败: ${String(err.detail?.message ?? err.detail?.kind ?? err.status)}`
        : `本地生成失败: ${err instanceof Error ? err.message : String(err)}`;
      setToast({ kind: "err", text: msg });
    } finally {
      setAudioBusy(null);
    }
  }, [bgmId, audioBusy, onSaved]);

  useEffect(() => {
    if (!bgmId) return;
    let cancelled = false;
    (async () => {
      try {
        const result = await fetchBgmReferences(bgmId);
        if (!cancelled) setReferences(result.references);
      } catch (err) {
        if (!cancelled) setReferencesError(err instanceof Error ? err.message : String(err));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [bgmId]);

  const onCopy = useCallback(async () => {
    if (!promptText) return;
    try {
      await navigator.clipboard.writeText(promptText);
      setCopyTick(true);
      setTimeout(() => setCopyTick(false), 1500);
    } catch {
      setToast({ kind: "err", text: "复制失败 — 浏览器拒绝了剪贴板访问" });
    }
  }, [promptText]);

  const onDelete = useCallback(async () => {
    if (!bgmId || deleting) return;
    const ok = window.confirm(`删除 ${bgmId}？将把文件夹移到 _deleted/_bgm/。`);
    if (!ok) return;
    setDeleting(true);
    try {
      await deleteBgm(bgmId);
      setToast({ kind: "ok", text: `已删除 ${bgmId}` });
      if (onSaved) onSaved();
      navigate("/");
    } catch (err) {
      let msg: string;
      if (err instanceof ApiError && err.status === 409 && err.detail?.kind === "bgm_is_referenced") {
        msg = "该 BGM 被剧本引用，无法删除";
      } else if (err instanceof ApiError) {
        msg = `删除失败: ${err.detail?.kind ?? err.status}`;
      } else {
        msg = `删除失败: ${err instanceof Error ? err.message : String(err)}`;
      }
      setToast({ kind: "err", text: msg });
    } finally {
      setDeleting(false);
    }
  }, [bgmId, deleting, onSaved, navigate]);

  if (!bgmId) {
    return <div className="voice-view-error">无法识别的 BGM 路径：{primaryPath}</div>;
  }

  const referenced = (references?.length ?? 0) > 0;

  return (
    <div className="voice-view">
      <header className="voice-view-header">
        <div className="voice-view-title">
          <span className="voice-view-title-icon" aria-hidden="true">🎵</span>
          <h1>{bgmId}</h1>
        </div>
        <div className="voice-view-header-actions">
          <button
            type="button"
            className="voice-delete-btn voice-delete-btn-large"
            disabled={referenced || deleting}
            title={referenced
              ? `BGM 当前被 ${references!.length} 处剧本引用，无法删除（请先在 bgm.md 中移除引用）`
              : "软删除 — 移到 _deleted/_bgm/"}
            onClick={onDelete}
          >
            🗑 删除
          </button>
        </div>
      </header>

      {toast ? <div className={`voice-toast voice-toast-${toast.kind}`} role="status">{toast.text}</div> : null}

      <section className="voice-section">
        <h2 className="voice-section-title">🔊 音乐样本</h2>
        {effectiveAudio ? (
          <div className="voice-audio-panel">
            <audio controls src={mediaUrl(effectiveAudio)} preload="metadata" className="voice-audio-player" />
            <div className="voice-audio-actions">
              <span className="voice-audio-filename">{effectiveAudio.split("/").pop()}</span>
            </div>
          </div>
        ) : (
          <div className="voice-audio-panel">
            <p className="voice-empty-inline">尚未渲染音频。把下方提示词复制到 ElevenLabs 出音乐，下载后到左侧导航 <strong>_bgm</strong> 的「📥 导入下载音乐」一键全局导入（按 bgm 编号自动归位）。也可本地 GPU 生成。</p>
            <div className="voice-audio-actions">
              <button type="button" className="voice-btn voice-btn-primary" disabled={audioBusy !== null} onClick={() => void onGenerateAudio()}>
                {audioBusy === "gpu" ? "⏳ 本地生成中…（数分钟）" : "🎧 本地 GPU 生成"}
              </button>
            </div>
          </div>
        )}
      </section>

      <div className="voice-grid-layout">
        <section className="voice-section voice-section-meta">
          <h2 className="voice-section-title">🪪 属性</h2>
          <dl className="voice-meta">
            {metadata.map(({ key, label, value }) => (
              <div key={key} className="voice-meta-row">
                <dt>{label}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="voice-section voice-section-prompt">
          <h2 className="voice-section-title">📝 生成提示词</h2>
          {promptText !== null ? (
            <div className="voice-prompt-card">
              <div className="voice-prompt-actions">
                <button type="button" className="voice-copy-btn" onClick={onCopy}>
                  {copyTick ? "✓ 已复制" : "📋 复制"}
                </button>
              </div>
              <pre className="voice-prompt-pre">{promptText}</pre>
            </div>
          ) : (
            <p className="voice-empty-inline">未找到提示词代码块。</p>
          )}
        </section>
      </div>

      <section className="voice-section">
        <h2 className="voice-section-title">🎬 剧本引用 ({references?.length ?? 0})</h2>
        {referencesError ? (
          <div className="voice-toast voice-toast-err">加载引用失败: {referencesError}</div>
        ) : null}
        {references === null ? (
          <p className="voice-loading">加载中…</p>
        ) : references.length === 0 ? (
          <p className="voice-empty-inline">当前没有任何剧本引用这条 BGM，可以安全删除。</p>
        ) : (
          <ul className="voice-assignments">
            {references.map((r, i) => (
              <li key={`${r.drama}/${r.location}/${r.cue_file}/${i}`} className="voice-assignment-row">
                <span className="voice-assignment-drama">{r.drama}</span>
                <span className="voice-assignment-sep">/</span>
                <span className="voice-assignment-role">{r.location}</span>
                <span className="voice-assignment-notes">{r.cue_file}</span>
                {r.cue_lines.length > 0 ? (
                  <details className="voice-bulk-errlog">
                    <summary>引用行 ({r.cue_lines.length})</summary>
                    <ul>{r.cue_lines.map((line, j) => <li key={j}>{line}</li>)}</ul>
                  </details>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

function extractFencedCode(content: string): string | null {
  const re = /```[\w-]*\n([\s\S]*?)```/m;
  const m = re.exec(content);
  return m ? m[1].trim() : null;
}

function parseMetadataTable(content: string): Array<[string, string]> {
  const out: Array<[string, string]> = [];
  for (const line of content.split(/\r?\n/)) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("|") || !trimmed.endsWith("|")) continue;
    const cells = trimmed.slice(1, -1).split("|").map((c) => c.trim());
    if (cells.length !== 2) continue;
    const [k, v] = cells;
    if (!k || k === "字段" || /^-+$/.test(k)) continue;
    out.push([k, v]);
  }
  return out;
}

const META_FIELD_LABELS_ZH: Record<string, string> = {
  category: "情绪分类",
  mood: "氛围",
  bpm: "BPM",
  duration: "时长(秒)",
  loopable: "可循环",
  intensity: "强度",
  instruments: "配器",
  notes: "备注",
  seed: "随机种子",
};

const META_VALUE_LOOKUP_ZH: Record<string, Record<string, string>> = {
  category: BGM_CATEGORY_LABELS_ZH,
};

function localizeMetadata(
  rows: Array<[string, string]>,
): Array<{ key: string; label: string; value: string }> {
  const out: Array<{ key: string; label: string; value: string }> = [];
  for (const [k, v] of rows) {
    if (k === "category_label") continue;
    const label = META_FIELD_LABELS_ZH[k] ?? k;
    const lookup = META_VALUE_LOOKUP_ZH[k];
    const value = lookup && lookup[v] ? lookup[v] : v;
    out.push({ key: k, label, value });
  }
  return out;
}
