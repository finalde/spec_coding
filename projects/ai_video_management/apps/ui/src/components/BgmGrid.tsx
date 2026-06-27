import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  BGM_CATEGORY_LABELS_ZH,
  BGM_CATEGORY_OPTIONS,
  deleteBgm,
  importFromDownloads,
  listBgms,
  mediaUrl,
  type BgmInfo,
} from "../api";
import { ApiError } from "../types";
import { BgmPoolGenerator } from "./BgmPoolGenerator";
import { announceToast } from "../lib/announce";

const PAGE_SIZE = 50;
const BGM_LIBRARY_PATH = "ai_videos/_bgm";

export interface BgmGridProps {
  onChange: () => void;
}

export function BgmGrid({ onChange }: BgmGridProps): JSX.Element {
  const navigate = useNavigate();
  const [bgms, setBgms] = useState<BgmInfo[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState<number>(0);
  const [filterCategory, setFilterCategory] = useState<string>("");
  const [page, setPage] = useState<number>(0);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [playingId, setPlayingId] = useState<string | null>(null);
  // Library toolbar (relocated off the left nav, follow-up): generate-pool modal
  // + import-from-Downloads.
  const [generatorOpen, setGeneratorOpen] = useState<boolean>(false);
  const [importBusy, setImportBusy] = useState<boolean>(false);

  const onImportClick = useCallback(async () => {
    if (importBusy) return;
    setImportBusy(true);
    try {
      const result = await importFromDownloads(BGM_LIBRARY_PATH);
      const errorCount = result.errors.length + result.rename.errors.length;
      announceToast(
        `已导入 ${result.moved.length} / 未导入 ${result.unmatched.length} / 失败 ${errorCount}`,
      );
      setReloadKey((k) => k + 1);
      onChange();
    } catch (err) {
      const kind = err instanceof ApiError ? (err.detail?.kind ?? `HTTP ${err.status}`) : String(err);
      announceToast(`导入音乐失败: ${kind}`);
    } finally {
      setImportBusy(false);
    }
  }, [importBusy, onChange]);

  useEffect(() => {
    let cancelled = false;
    const load = async (): Promise<void> => {
      setError(null);
      try {
        const result = await listBgms();
        if (!cancelled) setBgms(result.bgms);
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
    if (!bgms) return [];
    return bgms.filter((b) => {
      if (filterCategory && b.category !== filterCategory) return false;
      return true;
    });
  }, [bgms, filterCategory]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageStart = page * PAGE_SIZE;
  const pageEnd = pageStart + PAGE_SIZE;
  const visible = filtered.slice(pageStart, pageEnd);

  const playSample = useCallback((bgmId: string, audioPath: string) => {
    if (audioRef.current) {
      audioRef.current.pause();
    }
    const audio = new Audio(mediaUrl(audioPath));
    audio.onended = () => setPlayingId(null);
    audio.onpause = () => setPlayingId((cur) => (cur === bgmId ? null : cur));
    audioRef.current = audio;
    setPlayingId(bgmId);
    void audio.play().catch((err) => {
      setToast({ kind: "err", text: `播放失败: ${err instanceof Error ? err.message : String(err)}` });
      setPlayingId(null);
    });
  }, []);

  const onDelete = useCallback(
    async (bgmId: string) => {
      if (deletingId) return;
      const ok = window.confirm(
        `删除 ${bgmId}？将把文件夹移到 _deleted/_bgm/；被剧本引用时会拒绝。`,
      );
      if (!ok) return;
      setDeletingId(bgmId);
      try {
        await deleteBgm(bgmId);
        setToast({ kind: "ok", text: `已删除 ${bgmId}` });
        setReloadKey((k) => k + 1);
        onChange();
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
        setDeletingId(null);
      }
    },
    [deletingId, onChange],
  );

  return (
    <div className="voice-page">
      <header className="voice-page-header">
        <div className="voice-page-title">
          <h1>🎵 背景音乐库</h1>
          <span className="voice-page-count">
            {filtered.length} <span className="voice-page-count-sep">/</span> {bgms?.length ?? 0}
          </span>
        </div>
        <div className="voice-page-actions">
          <button type="button" className="voice-btn" onClick={() => setGeneratorOpen(true)}
            title="调用 Stable Audio 生成一批背景音乐（耗时较长），按情绪分类入库">
            🎵 生成 BGM
          </button>
          <button type="button" className="voice-btn" onClick={onImportClick} disabled={importBusy}
            title="ElevenLabs 出乐后用：从 Downloads 按 bgm_编号 tag 导入近 7 天的音频，归位到对应 bgm 文件夹">
            {importBusy ? "⏳ 导入中…" : "📥 导入下载音乐"}
          </button>
        </div>
        <div className="voice-filters">
          <label className="voice-gen-field voice-gen-field-narrow">
            <span className="voice-gen-label">情绪分类</span>
            <select value={filterCategory} onChange={(e) => { setFilterCategory(e.target.value); setPage(0); }}>
              <option value="">分类（全部）</option>
              {BGM_CATEGORY_OPTIONS.map((slug) => (
                <option key={slug} value={slug}>{BGM_CATEGORY_LABELS_ZH[slug]}</option>
              ))}
            </select>
          </label>
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

      {bgms === null && !error ? <p className="voice-loading">加载中…</p> : null}
      {bgms !== null && bgms.length === 0 ? (
        <div className="voice-empty">
          <div className="voice-empty-icon">🎵</div>
          <p>背景音乐库为空。</p>
          <p className="voice-empty-hint">
            点上方「🎵 生成 BGM」生成第一批，或「📥 导入下载音乐」从 Downloads 导入。
          </p>
        </div>
      ) : null}

      <div className="voice-grid">
        {visible.map((b) => {
          const tileClass =
            "voice-tile" + (playingId === b.id ? " voice-tile-playing" : "");
          const accName = `${b.id} ${b.category_label} ${b.bpm} BPM`;
          return (
          <article key={b.id} className={tileClass}>
            <button
              type="button"
              className="voice-tile-cover"
              onClick={() => navigate(`/file/${encodeURIComponent(b.sidecar_path)}`)}
              aria-label={`查看 ${accName} 详情`}
            >
              <span className="voice-tile-icon" aria-hidden="true">🎵</span>
              <span className="voice-tile-archetype">{b.category_label}</span>
            </button>
            <div className="voice-tile-body">
              <div className="voice-tile-id-row">
                <span className="voice-tile-id">{b.id}</span>
                {b.is_referenced ? <span className="voice-tile-badge" title="被剧本引用">被引用</span> : null}
              </div>
              <div className="voice-tile-chips">
                <span className="voice-chip">{b.bpm} BPM</span>
                <span className="voice-chip">强度 {b.intensity}</span>
                <span className="voice-chip">{b.duration}s</span>
                {b.loopable ? <span className="voice-chip">可循环</span> : null}
              </div>
              <div className="voice-tile-actions">
                {b.audio_path ? (
                  <button
                    type="button"
                    className="voice-play-btn"
                    aria-label={`播放 ${b.id} ${b.category_label} 音乐样本`}
                    title="试听 BGM 样本"
                    onClick={(e) => { e.stopPropagation(); playSample(b.id, b.audio_path as string); }}
                  >
                    {playingId === b.id ? "⏸" : "▶"}
                  </button>
                ) : (
                  <span className="voice-chip voice-chip-muted" title="尚未渲染音频">无样本</span>
                )}
                <button
                  type="button"
                  className="voice-delete-btn"
                  aria-label={`软删除 ${b.id} ${b.category_label}`}
                  title="软删除 BGM — 移到 _deleted/_bgm/（被引用的会拒绝）"
                  disabled={deletingId !== null}
                  onClick={(e) => { e.stopPropagation(); void onDelete(b.id); }}
                >
                  {deletingId === b.id ? "…" : "🗑"}
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

      {generatorOpen ? (
        <BgmPoolGenerator
          open={generatorOpen}
          onClose={() => setGeneratorOpen(false)}
          onGenerated={() => { setReloadKey((k) => k + 1); onChange(); }}
        />
      ) : null}
    </div>
  );
}
