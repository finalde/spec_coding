import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  castingAssignVoice,
  castingUnassignVoice,
  deleteVoice,
  extractVoiceAudio,
  fetchFile,
  fetchVoiceAssignments,
  mediaUrl,
  putFile,
  uploadVoiceAudio,
  VOICE_AGE_LABELS_ZH,
  VOICE_ARCHETYPE_LABELS_ZH,
  VOICE_EMOTION_LABELS_ZH,
  VOICE_GENDER_LABELS_ZH,
  VOICE_PACE_LABELS_ZH,
  VOICE_PITCH_LABELS_ZH,
  type VoiceAssignment,
} from "../api";
import { extractDramas, type DramaChoice } from "../lib/dramas";
import { replaceFirstFencedCode } from "../lib/promptEdit";
import { ApiError, type FileResult, type TreeNode } from "../types";
import { PromptStructuredEditor } from "./PromptStructuredEditor";

export interface VoiceViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
  tree: TreeNode | null;
  onSaved?: () => void;
}

const VOICE_ID_RE = /^ai_videos\/_voices\/(voice_\d{4,})\/voice_\d{4,}\.md$/;
const AUDIO_EXT_RE = /\.(mp3|wav|m4a)$/i;

export function VoiceView({ primaryFile, primaryPath, knownPaths, tree, onSaved }: VoiceViewProps): JSX.Element {
  const navigate = useNavigate();
  const voiceId = useMemo<string | null>(() => {
    const m = VOICE_ID_RE.exec(primaryPath);
    return m ? m[1] : null;
  }, [primaryPath]);

  const audioPath = useMemo<string | null>(() => {
    if (!voiceId) return null;
    const prefix = `ai_videos/_voices/${voiceId}/`;
    for (const p of knownPaths) {
      if (p.startsWith(prefix) && AUDIO_EXT_RE.test(p)) return p;
    }
    return null;
  }, [voiceId, knownPaths]);

  const promptText = useMemo<string | null>(() => extractFencedCode(primaryFile.content), [primaryFile.content]);
  const metadata = useMemo(
    () => localizeMetadata(parseMetadataTable(primaryFile.content)),
    [primaryFile.content],
  );

  const [assignments, setAssignments] = useState<VoiceAssignment[] | null>(null);
  const [assignmentsError, setAssignmentsError] = useState<string | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [extracting, setExtracting] = useState<boolean>(false);
  const [copyTick, setCopyTick] = useState<boolean>(false);
  const [deleting, setDeleting] = useState<boolean>(false);
  const [dragOver, setDragOver] = useState<boolean>(false);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const [assignFormOpen, setAssignFormOpen] = useState<boolean>(false);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editBuffer, setEditBuffer] = useState<string>("");
  const [editSaving, setEditSaving] = useState<boolean>(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const assignSectionRef = useRef<HTMLElement>(null);

  const onEditStart = useCallback((): void => {
    if (promptText === null) return;
    setEditBuffer(promptText);
    setEditMode(true);
  }, [promptText]);

  const onEditCancel = useCallback((): void => {
    setEditMode(false);
    setEditBuffer("");
  }, []);

  const onEditSave = useCallback(async (newBody?: string): Promise<void> => {
    if (editSaving) return;
    const bodyToWrite = newBody ?? editBuffer;
    setEditSaving(true);
    setToast(null);
    try {
      const newContent = replaceFirstFencedCode(primaryFile.content, bodyToWrite);
      await putFile(primaryPath, newContent, { ifUnmodifiedSince: primaryFile.mtime_http });
      setEditMode(false);
      setEditBuffer("");
      setToast({ kind: "ok", text: "已保存 prompt" });
      if (onSaved) onSaved();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setToast({
          kind: "err",
          text: "文件已被外部修改，请刷新后重试（你的编辑保留在编辑器中）",
        });
        // Best-effort refetch so the next save attempt has a fresh mtime.
        try {
          await fetchFile(primaryPath);
        } catch {
          /* swallow */
        }
      } else {
        const msg = err instanceof ApiError
          ? `保存失败: ${err.detail?.kind ?? err.status}`
          : `保存失败: ${err instanceof Error ? err.message : String(err)}`;
        setToast({ kind: "err", text: msg });
      }
    } finally {
      setEditSaving(false);
    }
  }, [editBuffer, editSaving, primaryFile.content, primaryFile.mtime_http, primaryPath, onSaved]);

  const openAssignForm = useCallback((): void => {
    setAssignFormOpen(true);
    requestAnimationFrame(() => {
      assignSectionRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }, []);

  const dramas = useMemo<DramaChoice[]>(() => extractDramas(tree), [tree]);

  const refreshAssignments = useCallback(async (): Promise<void> => {
    if (!voiceId) return;
    try {
      const result = await fetchVoiceAssignments(voiceId);
      setAssignments(result.assignments);
      setAssignmentsError(null);
    } catch (err) {
      setAssignmentsError(err instanceof Error ? err.message : String(err));
    }
  }, [voiceId]);

  useEffect(() => {
    if (!voiceId) return;
    let cancelled = false;
    (async () => {
      try {
        const result = await fetchVoiceAssignments(voiceId);
        if (!cancelled) setAssignments(result.assignments);
      } catch (err) {
        if (!cancelled) setAssignmentsError(err instanceof Error ? err.message : String(err));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [voiceId]);

  const onCopy = useCallback(async () => {
    if (!promptText) return;
    try {
      await navigator.clipboard.writeText(promptText);
      setCopyTick(true);
      setTimeout(() => setCopyTick(false), 1500);
    } catch {
      setToast({ kind: "err", text: "复制失败 — 浏览器拒绝了 clipboard 访问" });
    }
  }, [promptText]);

  const onUpload = useCallback(
    async (file: File) => {
      if (!voiceId || uploading) return;
      setUploading(true);
      setToast(null);
      try {
        await uploadVoiceAudio(voiceId, file);
        setToast({ kind: "ok", text: `已上传 ${file.name}` });
        if (onSaved) onSaved();
      } catch (err) {
        const msg = err instanceof ApiError
          ? `上传失败: ${err.detail?.kind ?? err.status}`
          : `上传失败: ${err instanceof Error ? err.message : String(err)}`;
        setToast({ kind: "err", text: msg });
      } finally {
        setUploading(false);
      }
    },
    [voiceId, uploading, onSaved],
  );

  const onExtract = useCallback(async () => {
    if (!voiceId || extracting) return;
    setExtracting(true);
    setToast(null);
    try {
      const res = await extractVoiceAudio(voiceId);
      const okCount = res.extracted.length;
      const failCount = res.failures.length;
      const head =
        okCount === 1
          ? `已从 ${res.extracted[0].source} 提取音频`
          : `已从 ${okCount} 个 mp4 提取音频 (按字典序最后一个保留为样本)`;
      const tail = failCount > 0 ? `; ${failCount} 个失败` : "";
      setToast({ kind: failCount > 0 && okCount === 0 ? "err" : "ok", text: head + tail });
      if (onSaved) onSaved();
    } catch (err) {
      let msg: string;
      if (err instanceof ApiError) {
        const kind = err.detail?.kind ?? `HTTP ${err.status}`;
        if (kind === "mp4_missing") {
          msg = "未发现 mp4 文件 — 请先把生成的 mp4 拖入此文件夹";
        } else if (kind === "ffmpeg_missing") {
          msg = "找不到 ffmpeg — 请检查 imageio-ffmpeg 是否安装";
        } else if (kind === "audio_extract_failed") {
          msg = `提取失败: ${err.detail?.message ?? "ffmpeg 异常"}`;
        } else {
          msg = `提取失败: ${kind}`;
        }
      } else {
        msg = `提取失败: ${err instanceof Error ? err.message : String(err)}`;
      }
      setToast({ kind: "err", text: msg });
    } finally {
      setExtracting(false);
    }
  }, [voiceId, extracting, onSaved]);

  const onUnassign = useCallback(
    async (a: VoiceAssignment) => {
      const ok = window.confirm(`取消 ${a.drama}/${a.role} 的配音绑定?`);
      if (!ok) return;
      try {
        await castingUnassignVoice(`ai_videos/${a.drama}`, a.role);
        setAssignments((cur) => (cur ?? []).filter((x) => !(x.drama === a.drama && x.role === a.role)));
        setToast({ kind: "ok", text: `已取消 ${a.drama}/${a.role}` });
        if (onSaved) onSaved();
      } catch (err) {
        const msg = err instanceof ApiError
          ? `取消失败: ${err.detail?.kind ?? err.status}`
          : `取消失败: ${err instanceof Error ? err.message : String(err)}`;
        setToast({ kind: "err", text: msg });
      }
    },
    [onSaved],
  );

  const onDelete = useCallback(async () => {
    if (!voiceId || deleting) return;
    const ok = window.confirm(`Delete ${voiceId}? Moves folder to _deleted/_voices/.`);
    if (!ok) return;
    setDeleting(true);
    try {
      await deleteVoice(voiceId);
      setToast({ kind: "ok", text: `已删除 ${voiceId}` });
      if (onSaved) onSaved();
      navigate("/");
    } catch (err) {
      const msg = err instanceof ApiError
        ? `删除失败: ${err.detail?.kind ?? err.status}`
        : `删除失败: ${err instanceof Error ? err.message : String(err)}`;
      setToast({ kind: "err", text: msg });
    } finally {
      setDeleting(false);
    }
  }, [voiceId, deleting, onSaved, navigate]);

  if (!voiceId) {
    return <div className="voice-view-error">无法识别的 voice 路径：{primaryPath}</div>;
  }

  const assignmentsBlocked = (assignments?.length ?? 0) > 0;

  return (
    <div className="voice-view">
      <header className="voice-view-header">
        <div className="voice-view-title">
          <span className="voice-view-title-icon" aria-hidden="true">🎙</span>
          <h1>{voiceId}</h1>
        </div>
        <div className="voice-view-header-actions">
          <button
            type="button"
            className="voice-btn voice-btn-primary"
            onClick={openAssignForm}
            disabled={dramas.length === 0 || assignFormOpen}
            title={dramas.length === 0
              ? "ai_videos/ 下没有 drama 可分配"
              : "把这个 voice 分配到某一部剧的某个角色"}
          >
            🎬 分配角色
          </button>
          <button
            type="button"
            className="voice-delete-btn voice-delete-btn-large"
            disabled={assignmentsBlocked || deleting}
            title={assignmentsBlocked
              ? `voice 当前已分配到 ${assignments!.length} 个角色，无法删除（请先取消所有分配）`
              : "软删除 — 移到 _deleted/_voices/"}
            onClick={onDelete}
          >
            🗑 删除
          </button>
        </div>
      </header>

      {toast ? <div className={`voice-toast voice-toast-${toast.kind}`} role="status">{toast.text}</div> : null}

      <section className="voice-section">
        <h2 className="voice-section-title">🔊 配音样本</h2>
        {audioPath ? (
          <div className="voice-audio-panel">
            <audio controls src={mediaUrl(audioPath)} preload="metadata" className="voice-audio-player" />
            <div className="voice-audio-actions">
              <button type="button" className="voice-btn voice-btn-secondary" onClick={() => inputRef.current?.click()} disabled={uploading || extracting}>
                {uploading ? "上传中…" : "📎 替换样本"}
              </button>
              <button
                type="button"
                className="voice-btn voice-btn-secondary"
                onClick={() => void onExtract()}
                disabled={uploading || extracting}
                title="从此 voice 文件夹中的 *.mp4 提取音频，覆盖当前样本"
              >
                {extracting ? "提取中…" : "🎬→🔊 从 mp4 提取"}
              </button>
              <span className="voice-audio-filename">{audioPath.split("/").pop()}</span>
            </div>
          </div>
        ) : (
          <div
            className={`voice-dropzone${dragOver ? " voice-dropzone-active" : ""}`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              const file = e.dataTransfer.files[0];
              if (file) void onUpload(file);
            }}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                inputRef.current?.click();
              }
            }}
            role="button"
            tabIndex={0}
          >
            <div className="voice-dropzone-icon" aria-hidden="true">⬆</div>
            <div className="voice-dropzone-headline">尚未上传配音样本</div>
            <div className="voice-dropzone-sub">拖入 <code>.mp3</code> / <code>.wav</code> / <code>.m4a</code> 或点击选择文件</div>
            <div className="voice-dropzone-hint">上限 10 MiB；先把生成的 prompt 拷给外部 AI 配音模型渲染后上传</div>
          </div>
        )}
        {!audioPath ? (
          <div className="voice-audio-actions" style={{ marginTop: 12 }}>
            <button
              type="button"
              className="voice-btn voice-btn-secondary"
              onClick={(e) => {
                e.stopPropagation();
                void onExtract();
              }}
              disabled={extracting}
              title="从此 voice 文件夹中的 *.mp4 提取音频"
            >
              {extracting ? "提取中…" : "🎬→🔊 从 mp4 提取"}
            </button>
            <span className="voice-audio-filename">把生成的 mp4 放进 <code>ai_videos/_voices/{voiceId}/</code> 后点击</span>
          </div>
        ) : null}
        <input
          ref={inputRef}
          type="file"
          accept=".mp3,.wav,.m4a,audio/mpeg,audio/wav,audio/mp4"
          style={{ display: "none" }}
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (file) void onUpload(file);
            e.target.value = "";
          }}
        />
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
          <h2 className="voice-section-title">📝 生成 prompt</h2>
          {promptText !== null ? (
            <div className={`voice-prompt-card${editMode ? " voice-prompt-card-editing" : ""}`}>
              {!editMode ? (
                <>
                  <div className="voice-prompt-actions">
                    <button type="button" className="voice-copy-btn" onClick={onCopy}>
                      {copyTick ? "✓ Copied" : "📋 Copy"}
                    </button>
                    <button type="button" className="voice-copy-btn" onClick={onEditStart} title="直接编辑 prompt 内容">
                      ✏ Edit
                    </button>
                  </div>
                  <pre className="voice-prompt-pre">{promptText}</pre>
                </>
              ) : (
                <PromptStructuredEditor
                  initialBody={editBuffer}
                  onSave={(newBody) => onEditSave(newBody)}
                  onCancel={onEditCancel}
                  saving={editSaving}
                  blockLabel="voice prompt"
                />
              )}
            </div>
          ) : (
            <p className="voice-empty-inline">未找到 prompt 代码块。</p>
          )}
        </section>
      </div>

      <section className="voice-section" ref={assignSectionRef}>
        <h2 className="voice-section-title">🎬 角色分配 ({assignments?.length ?? 0})</h2>
        {assignmentsError ? (
          <div className="voice-toast voice-toast-err">加载分配失败: {assignmentsError}</div>
        ) : null}
        {assignments === null ? (
          <p className="voice-loading">加载中…</p>
        ) : assignments.length === 0 ? (
          <p className="voice-empty-inline">当前未绑定任何角色。点击顶部「🎬 分配角色」或下方「＋ 添加分配」绑定到某剧的某个角色。</p>
        ) : (
          <ul className="voice-assignments">
            {assignments.map((a) => (
              <li key={`${a.drama}/${a.role}`} className="voice-assignment-row">
                <span className="voice-assignment-drama">{a.drama}</span>
                <span className="voice-assignment-sep">/</span>
                <span className="voice-assignment-role">{a.role}</span>
                {!a.character_folder_exists ? <span className="voice-assignment-warn" title="角色文件夹不存在">⚠</span> : null}
                {a.notes ? <span className="voice-assignment-notes">{a.notes}</span> : null}
                <button type="button" className="voice-btn voice-btn-secondary voice-assignment-unassign" onClick={() => onUnassign(a)}>
                  ✕ 取消
                </button>
              </li>
            ))}
          </ul>
        )}
        {voiceId ? (
          assignFormOpen ? (
            <AssignVoiceForm
              voiceId={voiceId}
              dramas={dramas}
              existing={assignments ?? []}
              onClose={() => setAssignFormOpen(false)}
              onAssigned={async () => {
                setAssignFormOpen(false);
                setToast({ kind: "ok", text: "已分配" });
                await refreshAssignments();
                if (onSaved) onSaved();
              }}
            />
          ) : (
            <button
              type="button"
              className="voice-btn voice-btn-primary voice-assign-btn"
              onClick={openAssignForm}
              disabled={dramas.length === 0}
              title={dramas.length === 0 ? "ai_videos/ 下没有 drama 可分配" : "把这个 voice 分配给某一部剧的某个角色"}
            >
              ＋ 添加分配
            </button>
          )
        ) : null}
      </section>
    </div>
  );
}

interface AssignVoiceFormProps {
  voiceId: string;
  dramas: DramaChoice[];
  existing: VoiceAssignment[];
  onClose: () => void;
  onAssigned: () => void | Promise<void>;
}

function AssignVoiceForm({ voiceId, dramas, existing, onClose, onAssigned }: AssignVoiceFormProps): JSX.Element {
  const [dramaPath, setDramaPath] = useState<string>(dramas[0]?.path ?? "");
  const currentDrama = useMemo(
    () => dramas.find((d) => d.path === dramaPath) ?? dramas[0] ?? null,
    [dramaPath, dramas],
  );
  const characters = currentDrama?.characters ?? [];
  const [role, setRole] = useState<string>(characters[0] ?? "");
  const [notes, setNotes] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { setRole(characters[0] ?? ""); }, [characters]);

  const alreadyAssignedHere = useMemo<boolean>(() => {
    if (!currentDrama || !role) return false;
    return existing.some((a) => a.drama === currentDrama.name && a.role === role);
  }, [currentDrama, role, existing]);

  const onSubmit = async (): Promise<void> => {
    if (!currentDrama || !role || busy) return;
    setBusy(true);
    setError(null);
    try {
      await castingAssignVoice(currentDrama.path, role, voiceId, notes || null);
      await onAssigned();
    } catch (err) {
      const msg = err instanceof ApiError
        ? `分配失败: ${err.detail?.kind ?? err.status}`
        : `分配失败: ${err instanceof Error ? err.message : String(err)}`;
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="voice-assign-form" role="group" aria-label="新分配角色">
      <div className="voice-gen-row">
        <label className="voice-gen-field">
          <span className="voice-gen-label">短剧</span>
          <select value={dramaPath} onChange={(e) => setDramaPath(e.target.value)} disabled={busy}>
            {dramas.map((d) => (
              <option key={d.path} value={d.path}>{d.name}</option>
            ))}
          </select>
        </label>
        <label className="voice-gen-field">
          <span className="voice-gen-label">角色</span>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            disabled={busy || characters.length === 0}
          >
            {characters.length === 0 ? (
              <option value="">（这个短剧下没有 c*/ 角色目录）</option>
            ) : (
              characters.map((c) => <option key={c} value={c}>{c}</option>)
            )}
          </select>
        </label>
      </div>
      <label className="voice-gen-field voice-gen-field-block">
        <span className="voice-gen-label">备注（可选，≤ 500 字）</span>
        <textarea
          rows={2}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={busy}
          maxLength={500}
          placeholder="如：第二集开始改用这条 voice"
        />
      </label>
      {alreadyAssignedHere ? (
        <p className="voice-empty-inline">⚠ 该角色已绑定本 voice — 重复提交会覆写原 row（upsert）。</p>
      ) : null}
      {error ? <div role="alert" className="voice-toast voice-toast-err">{error}</div> : null}
      <div className="voice-assign-form-actions">
        <button
          type="button"
          className="voice-btn voice-btn-primary"
          onClick={() => void onSubmit()}
          disabled={busy || !currentDrama || !role}
        >
          {busy ? "分配中…" : "✓ 确认分配"}
        </button>
        <button type="button" className="voice-btn voice-btn-secondary" onClick={onClose} disabled={busy}>
          取消
        </button>
      </div>
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
  archetype: "角色原型",
  gender: "性别",
  age_impression: "年龄段",
  pace: "语速",
  pitch_register: "音区",
  emotion_default: "默认情绪",
  tone: "音色描述",
  signature_inflection: "标志性发声",
  notes: "备注",
  seed: "随机种子",
  audio_sample: "配音样本",
};

const META_VALUE_LOOKUP_ZH: Record<string, Record<string, string>> = {
  archetype: VOICE_ARCHETYPE_LABELS_ZH,
  gender: VOICE_GENDER_LABELS_ZH,
  age_impression: VOICE_AGE_LABELS_ZH,
  pace: VOICE_PACE_LABELS_ZH,
  pitch_register: VOICE_PITCH_LABELS_ZH,
  emotion_default: VOICE_EMOTION_LABELS_ZH,
};

function localizeMetadata(
  rows: Array<[string, string]>,
): Array<{ key: string; label: string; value: string }> {
  const out: Array<{ key: string; label: string; value: string }> = [];
  for (const [k, v] of rows) {
    if (k === "archetype_label") continue;
    const label = META_FIELD_LABELS_ZH[k] ?? k;
    const lookup = META_VALUE_LOOKUP_ZH[k];
    const value = lookup && lookup[v] ? lookup[v] : v;
    out.push({ key: k, label, value });
  }
  return out;
}
