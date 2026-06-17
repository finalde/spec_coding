import { useState } from "react";
import {
  BGM_CATEGORY_LABELS_ZH,
  BGM_CATEGORY_OPTIONS,
  BGM_INSTRUMENT_PRESETS,
  BGM_MOOD_PRESETS,
  createBgmPrompts,
  previewBgmPrompts,
  type BgmPreviewSlot,
  type GenerateBgmsRequest,
} from "../api";
import { ApiError } from "../types";

export interface BgmPoolGeneratorProps {
  open: boolean;
  onClose: () => void;
  onGenerated: () => void;
}

export function BgmPoolGenerator({ open, onClose, onGenerated }: BgmPoolGeneratorProps): JSX.Element | null {
  const [count, setCount] = useState<string>("3");
  const [category, setCategory] = useState<string>(BGM_CATEGORY_OPTIONS[0]);
  const [bpm, setBpm] = useState<string>("120");
  const [duration, setDuration] = useState<string>("30");
  const [intensity, setIntensity] = useState<string>("3");
  const [loopable, setLoopable] = useState<boolean>(true);
  const [moodPreset, setMoodPreset] = useState<string>("");
  const [moodCustom, setMoodCustom] = useState<string>("");
  const [instrumentsPreset, setInstrumentsPreset] = useState<string>("");
  const [instrumentsCustom, setInstrumentsCustom] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [previewing, setPreviewing] = useState<boolean>(false);
  const [busy, setBusy] = useState<boolean>(false);
  const [prompts, setPrompts] = useState<BgmPreviewSlot[] | null>(null);
  const [errors, setErrors] = useState<Array<{ requested_id: string; message: string }>>([]);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  if (!open) return null;

  const countNum = Math.max(1, Math.min(50, parseInt(count || "1", 10) || 1));
  const bpmNum = Math.max(40, Math.min(220, parseInt(bpm || "120", 10) || 120));
  const durationNum = Math.max(5, Math.min(300, parseInt(duration || "30", 10) || 30));
  const intensityNum = Math.max(1, Math.min(5, parseInt(intensity || "3", 10) || 3));

  // Free-text override wins over the dropdown preset; fall back to the preset.
  const mood = moodCustom.trim() || moodPreset;
  const instruments = instrumentsCustom.trim() || instrumentsPreset;

  const buildBody = (): GenerateBgmsRequest => ({
    count: countNum,
    category,
    mood,
    bpm: bpmNum,
    duration: durationNum,
    loopable,
    intensity: intensityNum,
    instruments,
    notes,
  });

  const onPreview = async (): Promise<void> => {
    if (previewing || busy) return;
    setPreviewing(true);
    setToast(null);
    try {
      const result = await previewBgmPrompts(buildBody());
      setPrompts(result.prompts);
    } catch (err) {
      const msg = err instanceof ApiError
        ? `预览失败: ${err.detail?.kind ?? err.status}`
        : `预览失败: ${err instanceof Error ? err.message : String(err)}`;
      setToast({ kind: "err", text: msg });
    } finally {
      setPreviewing(false);
    }
  };

  const onSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setToast(null);
    setErrors([]);
    try {
      const result = await createBgmPrompts(buildBody());
      setErrors(result.errors);
      const errs = result.errors.length;
      setToast({
        kind: errs > 0 ? "err" : "ok",
        text: `已创建 ${result.generated.length} 条 prompt（待出音频）/ 失败 ${errs}`,
      });
      onGenerated();
    } catch (err) {
      const msg = err instanceof ApiError
        ? `生成失败: ${err.detail?.kind ?? err.status}`
        : `生成失败: ${err instanceof Error ? err.message : String(err)}`;
      setToast({ kind: "err", text: msg });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="生成 BGM 音乐">
      <div className="modal-panel voice-gen-panel">
        <header className="modal-header">
          <h2>🎵 生成 BGM prompt</h2>
          <button type="button" className="modal-close" aria-label="关闭" onClick={onClose} disabled={busy}>✕</button>
        </header>
        <form onSubmit={onSubmit} className="modal-body voice-gen-body">
          <div className="voice-gen-row">
            <label className="voice-gen-field">
              <span className="voice-gen-label">情绪分类</span>
              <select value={category} onChange={(e) => setCategory(e.target.value)} disabled={busy}>
                {BGM_CATEGORY_OPTIONS.map((slug) => (
                  <option key={slug} value={slug}>{BGM_CATEGORY_LABELS_ZH[slug] ?? slug}</option>
                ))}
              </select>
            </label>
            <label className="voice-gen-field voice-gen-field-narrow">
              <span className="voice-gen-label">数量 (1-50)</span>
              <input type="number" min={1} max={50} value={count} onChange={(e) => setCount(e.target.value)} disabled={busy} />
            </label>
          </div>

          <div className="voice-gen-row">
            <label className="voice-gen-field voice-gen-field-narrow">
              <span className="voice-gen-label">BPM (40-220)</span>
              <input type="number" min={40} max={220} value={bpm} onChange={(e) => setBpm(e.target.value)} disabled={busy} />
            </label>
            <label className="voice-gen-field voice-gen-field-narrow">
              <span className="voice-gen-label">时长秒 (5-300)</span>
              <input type="number" min={5} max={300} value={duration} onChange={(e) => setDuration(e.target.value)} disabled={busy} />
            </label>
            <label className="voice-gen-field voice-gen-field-narrow">
              <span className="voice-gen-label">强度 (1-5)</span>
              <input type="number" min={1} max={5} value={intensity} onChange={(e) => setIntensity(e.target.value)} disabled={busy} />
            </label>
            <label className="voice-gen-field voice-gen-field-narrow">
              <span className="voice-gen-label">可循环</span>
              <input type="checkbox" checked={loopable} onChange={(e) => setLoopable(e.target.checked)} disabled={busy} aria-label="可循环" />
            </label>
          </div>

          <div className="voice-gen-row">
            <label className="voice-gen-field">
              <span className="voice-gen-label">氛围 mood（选填）</span>
              <select value={moodPreset} onChange={(e) => setMoodPreset(e.target.value)} disabled={busy}>
                <option value="">（不限）</option>
                {BGM_MOOD_PRESETS.map((m) => <option key={m} value={m}>{m}</option>)}
              </select>
            </label>
            <label className="voice-gen-field">
              <span className="voice-gen-label">或自定义 mood（优先，可空）</span>
              <input type="text" value={moodCustom} onChange={(e) => setMoodCustom(e.target.value)} disabled={busy} placeholder="自由中文，留空则用左侧" />
            </label>
          </div>
          <div className="voice-gen-row">
            <label className="voice-gen-field">
              <span className="voice-gen-label">配器 instruments（选填）</span>
              <select value={instrumentsPreset} onChange={(e) => setInstrumentsPreset(e.target.value)} disabled={busy}>
                <option value="">（不限）</option>
                {BGM_INSTRUMENT_PRESETS.map((it) => <option key={it} value={it}>{it}</option>)}
              </select>
            </label>
            <label className="voice-gen-field">
              <span className="voice-gen-label">或自定义配器（优先，可空）</span>
              <input type="text" value={instrumentsCustom} onChange={(e) => setInstrumentsCustom(e.target.value)} disabled={busy} placeholder="自由中文，留空则用左侧" />
            </label>
          </div>
          <label className="voice-gen-field voice-gen-field-block">
            <span className="voice-gen-label">备注 notes（可空，≤ 500 字）</span>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} disabled={busy} maxLength={500} rows={2} />
          </label>

          <p className="voice-empty-inline">
            ① 这一步只<strong>生成 prompt</strong>，不渲染音频（很快）。② 之后到每条 BGM 详情页，选择「本地 GPU 生成」或把 prompt 复制到外部平台出音乐、下载后「导入下载」。
          </p>

          {prompts ? (
            <div className="voice-gen-row voice-gen-field-block">
              <details className="voice-bulk-errlog" open>
                <summary>预览 prompt ({prompts.length})</summary>
                <ul>
                  {prompts.map((p) => (
                    <li key={p.seed}>
                      <strong>seed {p.seed}</strong> · {p.category_label}
                      <pre className="voice-prompt-pre">{p.prompt}</pre>
                    </li>
                  ))}
                </ul>
              </details>
            </div>
          ) : null}

          {errors.length > 0 ? (
            <details className="voice-bulk-errlog" open>
              <summary>生成失败详情 ({errors.length})</summary>
              <ul>{errors.map((e, i) => <li key={i}>{e.requested_id}: {e.message}</li>)}</ul>
            </details>
          ) : null}

          {busy ? (
            <div className="voice-toast voice-toast-ok" role="status">⏳ 正在创建 prompt…</div>
          ) : null}
          {toast ? (
            <div className={`voice-toast voice-toast-${toast.kind}`} role="status">{toast.text}</div>
          ) : null}
        </form>
        <footer className="modal-footer">
          <button type="button" className="voice-btn voice-btn-secondary" onClick={onClose} disabled={busy}>取消</button>
          <button
            type="button"
            className="voice-btn voice-btn-secondary"
            onClick={() => void onPreview()}
            disabled={busy || previewing}
          >
            {previewing ? "预览中…" : "👁 预览 prompt"}
          </button>
          <button
            type="button"
            className="voice-btn voice-btn-primary"
            onClick={onSubmit as unknown as React.MouseEventHandler<HTMLButtonElement>}
            disabled={busy}
          >
            {busy ? "生成中…" : `🎵 生成 ${countNum} 条 prompt`}
          </button>
        </footer>
      </div>
    </div>
  );
}
