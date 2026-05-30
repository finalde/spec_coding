import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  castingAssignVoice,
  deleteVoice,
  listVoices,
  mediaUrl,
  VOICE_AGE_LABELS_ZH,
  VOICE_AGE_OPTIONS,
  VOICE_ARCHETYPE_LABELS_ZH,
  VOICE_ARCHETYPE_OPTIONS,
  VOICE_EMOTION_LABELS_ZH,
  VOICE_EMOTION_OPTIONS,
  VOICE_GENDER_LABELS_ZH,
  VOICE_GENDER_OPTIONS,
  type VoiceInfo,
} from "../api";
import { extractDramas, type DramaChoice } from "../lib/dramas";
import { ApiError, type TreeNode } from "../types";

const PAGE_SIZE = 50;

export interface VoiceGridProps {
  tree: TreeNode | null;
  onChange: () => void;
}

export function VoiceGrid({ tree, onChange }: VoiceGridProps): JSX.Element {
  const navigate = useNavigate();
  const [voices, setVoices] = useState<VoiceInfo[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState<number>(0);
  const [filterArchetype, setFilterArchetype] = useState<string>("");
  const [filterGender, setFilterGender] = useState<string>("");
  const [filterAge, setFilterAge] = useState<string>("");
  const [filterEmotion, setFilterEmotion] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  const [selectMode, setSelectMode] = useState<boolean>(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [assignModalOpen, setAssignModalOpen] = useState<boolean>(false);

  const dramas = useMemo<DramaChoice[]>(() => extractDramas(tree), [tree]);

  useEffect(() => {
    let cancelled = false;
    const load = async (): Promise<void> => {
      setError(null);
      try {
        const result = await listVoices();
        if (!cancelled) setVoices(result.voices);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    };
    void load();
    return () => {
      cancelled = true;
    };
  }, [reloadKey]);

  useEffect(() => () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
  }, []);

  const filtered = useMemo(() => {
    if (!voices) return [];
    return voices.filter((v) => {
      if (filterArchetype && v.archetype !== filterArchetype) return false;
      if (filterGender && v.gender !== filterGender) return false;
      if (filterAge && v.age_impression !== filterAge) return false;
      if (filterEmotion && v.emotion_default !== filterEmotion) return false;
      return true;
    });
  }, [voices, filterArchetype, filterGender, filterAge, filterEmotion]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageStart = page * PAGE_SIZE;
  const pageEnd = pageStart + PAGE_SIZE;
  const visible = filtered.slice(pageStart, pageEnd);

  const playSample = useCallback((voiceId: string, audioPath: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    const audio = new Audio(mediaUrl(audioPath));
    audio.onended = () => setPlayingId(null);
    audio.onpause = () => setPlayingId((cur) => (cur === voiceId ? null : cur));
    audioRef.current = audio;
    setPlayingId(voiceId);
    void audio.play().catch((err) => {
      setToast({ kind: "err", text: `播放失败: ${err instanceof Error ? err.message : String(err)}` });
      setPlayingId(null);
    });
  }, []);

  const onDelete = useCallback(
    async (voiceId: string) => {
      if (deletingId) return;
      const ok = window.confirm(
        `Delete ${voiceId}? Moves folder to _deleted/_voices/. Refuses if assigned.`,
      );
      if (!ok) return;
      setDeletingId(voiceId);
      try {
        await deleteVoice(voiceId);
        setToast({ kind: "ok", text: `已删除 ${voiceId}` });
        setReloadKey((k) => k + 1);
        onChange();
      } catch (err) {
        const msg = err instanceof ApiError
          ? `删除失败: ${err.detail?.kind ?? err.status}`
          : `删除失败: ${err instanceof Error ? err.message : String(err)}`;
        setToast({ kind: "err", text: msg });
      } finally {
        setDeletingId(null);
      }
    },
    [deletingId, onChange],
  );

  return (
    <div className="voice-page">
      <header className="voice-page-header">
        <div className="voice-page-title">
          <h1>🎙 配音池</h1>
          <span className="voice-page-count">
            {filtered.length} <span className="voice-page-count-sep">/</span> {voices?.length ?? 0}
          </span>
        </div>
        <div className="voice-filters">
          <select value={filterArchetype} onChange={(e) => { setFilterArchetype(e.target.value); setPage(0); }}>
            <option value="">原型（全部）</option>
            {VOICE_ARCHETYPE_OPTIONS.map((slug) => (
              <option key={slug} value={slug}>{VOICE_ARCHETYPE_LABELS_ZH[slug]}</option>
            ))}
          </select>
          <select value={filterGender} onChange={(e) => { setFilterGender(e.target.value); setPage(0); }}>
            <option value="">性别（全部）</option>
            {VOICE_GENDER_OPTIONS.map((g) => (
              <option key={g} value={g}>{VOICE_GENDER_LABELS_ZH[g]}</option>
            ))}
          </select>
          <select value={filterAge} onChange={(e) => { setFilterAge(e.target.value); setPage(0); }}>
            <option value="">年龄段（全部）</option>
            {VOICE_AGE_OPTIONS.map((a) => (
              <option key={a} value={a}>{VOICE_AGE_LABELS_ZH[a]}</option>
            ))}
          </select>
          <select value={filterEmotion} onChange={(e) => { setFilterEmotion(e.target.value); setPage(0); }}>
            <option value="">情绪（全部）</option>
            {VOICE_EMOTION_OPTIONS.map((em) => (
              <option key={em} value={em}>{VOICE_EMOTION_LABELS_ZH[em]}</option>
            ))}
          </select>
          <button
            type="button"
            className={`voice-btn ${selectMode ? "voice-btn-primary" : "voice-btn-secondary"}`}
            onClick={() => {
              setSelectMode((m) => !m);
              setSelectedIds(new Set());
            }}
          >
            {selectMode ? "✕ 退出选择" : "✅ 选择"}
          </button>
        </div>
      </header>

      {toast ? (
        <div className={`voice-toast voice-toast-${toast.kind}`} role="status">{toast.text}</div>
      ) : null}

      {error ? (
        <div className="voice-toast voice-toast-err" role="alert">
          加载失败: {error}
          <button type="button" className="voice-btn voice-btn-secondary" onClick={() => setReloadKey((k) => k + 1)} style={{ marginLeft: 12 }}>
            重试
          </button>
        </div>
      ) : null}

      {voices === null && !error ? <p className="voice-loading">加载中…</p> : null}
      {voices !== null && voices.length === 0 ? (
        <div className="voice-empty">
          <div className="voice-empty-icon">🎙</div>
          <p>配音池为空。</p>
          <p className="voice-empty-hint">
            点击侧边栏 <code>_voices/</code> 旁的「🎙 生成配音」按钮开始。
          </p>
        </div>
      ) : null}

      <div className="voice-grid">
        {visible.map((v) => {
          const isSelected = selectedIds.has(v.id);
          const tileClass =
            "voice-tile" +
            (playingId === v.id ? " voice-tile-playing" : "") +
            (isSelected ? " voice-tile-selected" : "");
          const onTileClick = (): void => {
            if (selectMode) {
              setSelectedIds((cur) => {
                const next = new Set(cur);
                if (next.has(v.id)) next.delete(v.id);
                else next.add(v.id);
                return next;
              });
            } else {
              navigate(`/file/${encodeURIComponent(v.sidecar_path)}`);
            }
          };
          return (
          <article key={v.id} className={tileClass}>
            <button
              type="button"
              className="voice-tile-cover"
              onClick={onTileClick}
              aria-label={selectMode ? `${isSelected ? "取消选择" : "选择"} ${v.id}` : `查看 ${v.id} 详情`}
              aria-pressed={selectMode ? isSelected : undefined}
            >
              {selectMode ? (
                <span className="voice-tile-checkbox" aria-hidden="true">{isSelected ? "✓" : ""}</span>
              ) : null}
              <span className="voice-tile-icon" aria-hidden="true">🎙</span>
              <span className="voice-tile-archetype">{v.archetype_label}</span>
            </button>
            <div className="voice-tile-body">
              <div className="voice-tile-id-row">
                <span className="voice-tile-id">{v.id}</span>
                {v.is_assigned ? <span className="voice-tile-badge" title="已分配到角色">已分配</span> : null}
              </div>
              <div className="voice-tile-chips">
                <span className="voice-chip">{VOICE_GENDER_LABELS_ZH[v.gender] ?? v.gender}</span>
                <span className="voice-chip">{VOICE_AGE_LABELS_ZH[v.age_impression] ?? v.age_impression}</span>
                <span className="voice-chip">{VOICE_EMOTION_LABELS_ZH[v.emotion_default ?? "calm"] ?? ""}</span>
              </div>
              <div className="voice-tile-actions">
                {v.audio_path ? (
                  <button
                    type="button"
                    className="voice-play-btn"
                    aria-label={`播放 ${v.id} 配音样本`}
                    title="试听配音样本"
                    onClick={(e) => { e.stopPropagation(); playSample(v.id, v.audio_path as string); }}
                  >
                    {playingId === v.id ? "⏸" : "▶"}
                  </button>
                ) : (
                  <span className="voice-chip voice-chip-muted" title="尚未上传配音样本">无样本</span>
                )}
                <button
                  type="button"
                  className="voice-delete-btn"
                  aria-label={`软删除 ${v.id}`}
                  title="软删除 voice — 移到 _deleted/_voices/（已分配的会拒绝）"
                  disabled={deletingId !== null}
                  onClick={(e) => { e.stopPropagation(); void onDelete(v.id); }}
                >
                  {deletingId === v.id ? "…" : "🗑"}
                </button>
              </div>
            </div>
          </article>
          );
        })}
      </div>

      {filtered.length > PAGE_SIZE ? (
        <nav className="voice-pagination" aria-label="分页">
          <button type="button" onClick={() => setPage(0)} disabled={page === 0}>«</button>
          <button type="button" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>‹</button>
          <span className="voice-pagination-indicator" aria-live="polite">第 {page + 1} / {totalPages} 页</span>
          <button type="button" onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}>›</button>
          <button type="button" onClick={() => setPage(totalPages - 1)} disabled={page >= totalPages - 1}>»</button>
        </nav>
      ) : null}

      {selectMode ? (
        <div className="voice-select-bar" role="region" aria-label="批量操作">
          <span className="voice-select-count">已选 <strong>{selectedIds.size}</strong> / {filtered.length}</span>
          <button
            type="button"
            className="voice-btn voice-btn-secondary"
            onClick={() => setSelectedIds(new Set(filtered.map((v) => v.id)))}
          >
            全选
          </button>
          <button
            type="button"
            className="voice-btn voice-btn-secondary"
            onClick={() => setSelectedIds(new Set())}
            disabled={selectedIds.size === 0}
          >
            全清
          </button>
          <button
            type="button"
            className="voice-btn voice-btn-primary"
            onClick={() => setAssignModalOpen(true)}
            disabled={selectedIds.size === 0 || dramas.length === 0}
            title={dramas.length === 0 ? "ai_videos/ 下没有 drama 可分配" : "把选中的 voice 批量分配到某剧的某角色"}
          >
            🎬 分配角色 ({selectedIds.size})
          </button>
          <button
            type="button"
            className="voice-btn voice-btn-secondary"
            onClick={() => { setSelectMode(false); setSelectedIds(new Set()); }}
          >
            ✕ 退出
          </button>
        </div>
      ) : null}

      {assignModalOpen ? (
        <BulkAssignVoiceModal
          voiceIds={Array.from(selectedIds)}
          dramas={dramas}
          onClose={() => setAssignModalOpen(false)}
          onDone={(ok, fail) => {
            setAssignModalOpen(false);
            setSelectMode(false);
            setSelectedIds(new Set());
            setReloadKey((k) => k + 1);
            onChange();
            setToast({
              kind: fail > 0 ? "err" : "ok",
              text: `批量分配完成 — 成功 ${ok} / 失败 ${fail}`,
            });
          }}
        />
      ) : null}
    </div>
  );
}

interface BulkAssignVoiceModalProps {
  voiceIds: string[];
  dramas: DramaChoice[];
  onClose: () => void;
  onDone: (ok: number, fail: number) => void;
}

function BulkAssignVoiceModal({ voiceIds, dramas, onClose, onDone }: BulkAssignVoiceModalProps): JSX.Element {
  const [dramaPath, setDramaPath] = useState<string>(dramas[0]?.path ?? "");
  const currentDrama = useMemo(
    () => dramas.find((d) => d.path === dramaPath) ?? dramas[0] ?? null,
    [dramaPath, dramas],
  );
  const characters = currentDrama?.characters ?? [];
  const [role, setRole] = useState<string>(characters[0] ?? "");
  const [notes, setNotes] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [progress, setProgress] = useState<{ done: number; failed: number } | null>(null);
  const [errorLog, setErrorLog] = useState<string[]>([]);

  useEffect(() => { setRole(characters[0] ?? ""); }, [characters]);

  const onSubmit = async (): Promise<void> => {
    if (!currentDrama || !role || busy || voiceIds.length === 0) return;
    setBusy(true);
    setProgress({ done: 0, failed: 0 });
    setErrorLog([]);
    let ok = 0;
    let fail = 0;
    const errs: string[] = [];
    for (const voiceId of voiceIds) {
      try {
        await castingAssignVoice(currentDrama.path, role, voiceId, notes || null);
        ok += 1;
      } catch (err) {
        fail += 1;
        const msg = err instanceof ApiError
          ? `${voiceId}: ${err.detail?.kind ?? err.status}`
          : `${voiceId}: ${err instanceof Error ? err.message : String(err)}`;
        errs.push(msg);
      }
      setProgress({ done: ok, failed: fail });
    }
    setErrorLog(errs);
    setBusy(false);
    if (fail === 0) {
      onDone(ok, fail);
    }
  };

  const allDone = progress !== null && progress.done + progress.failed === voiceIds.length;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="批量分配配音到角色">
      <div className="modal-panel voice-gen-panel">
        <header className="modal-header">
          <h2>🎬 批量分配配音 — {voiceIds.length} 条</h2>
          <button type="button" className="modal-close" aria-label="关闭" onClick={onClose} disabled={busy}>✕</button>
        </header>
        <div className="modal-body voice-gen-body">
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
            <span className="voice-gen-label">备注（可选，会写入每条 row）</span>
            <textarea rows={2} value={notes} onChange={(e) => setNotes(e.target.value)} disabled={busy} maxLength={500} />
          </label>
          <p className="voice-empty-inline">
            将依次为 <strong>{voiceIds.length}</strong> 条 voice 写入 <code>{currentDrama?.name ?? "—"}/casting.md</code> 的 <code>{role || "—"}</code> 行。
            后写入的会覆盖前者 — 通常只在选一条 voice 时有意义；多条选择多用于演示统一备注。
          </p>
          {progress ? (
            <div className={`voice-toast voice-toast-${progress.failed > 0 ? "err" : "ok"}`} role="status">
              进度: 已完成 {progress.done} / 失败 {progress.failed} / 总 {voiceIds.length}
            </div>
          ) : null}
          {errorLog.length > 0 ? (
            <details className="voice-bulk-errlog">
              <summary>失败详情 ({errorLog.length})</summary>
              <ul>{errorLog.map((line) => <li key={line}>{line}</li>)}</ul>
            </details>
          ) : null}
        </div>
        <footer className="modal-footer">
          <button type="button" className="voice-btn voice-btn-secondary" onClick={onClose} disabled={busy}>
            {allDone ? "关闭" : "取消"}
          </button>
          {!allDone ? (
            <button
              type="button"
              className="voice-btn voice-btn-primary"
              onClick={() => void onSubmit()}
              disabled={busy || !currentDrama || !role}
            >
              {busy ? "分配中…" : `✓ 确认分配 (${voiceIds.length})`}
            </button>
          ) : (
            <button
              type="button"
              className="voice-btn voice-btn-primary"
              onClick={() => onDone(progress!.done, progress!.failed)}
            >
              完成
            </button>
          )}
        </footer>
      </div>
    </div>
  );
}
