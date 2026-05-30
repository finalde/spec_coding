import { useState } from "react";
import {
  generateDiverseVoices,
  generateVoices,
  VOICE_AGE_LABELS_ZH,
  VOICE_AGE_OPTIONS,
  VOICE_ARCHETYPE_LABELS_ZH,
  VOICE_ARCHETYPE_OPTIONS,
  VOICE_EMOTION_LABELS_ZH,
  VOICE_EMOTION_OPTIONS,
  VOICE_GENDER_LABELS_ZH,
  VOICE_GENDER_OPTIONS,
  VOICE_PACE_LABELS_ZH,
  VOICE_PACE_OPTIONS,
  VOICE_PITCH_LABELS_ZH,
  VOICE_PITCH_OPTIONS,
} from "../api";
import { ApiError } from "../types";

export interface VoicePoolGeneratorProps {
  open: boolean;
  onClose: () => void;
  onGenerated: () => void;
}

type Mode = "unified" | "diverse";

export function VoicePoolGenerator({ open, onClose, onGenerated }: VoicePoolGeneratorProps): JSX.Element | null {
  const [mode, setMode] = useState<Mode>("unified");
  const [count, setCount] = useState<string>("5");
  const [archetype, setArchetype] = useState<string>(VOICE_ARCHETYPE_OPTIONS[0]);
  const [gender, setGender] = useState<string>("male");
  const [ageImpression, setAgeImpression] = useState<string>("middle_aged");
  const [pace, setPace] = useState<string>("medium");
  const [pitch, setPitch] = useState<string>("mid");
  const [emotion, setEmotion] = useState<string>("calm");
  const [tone, setTone] = useState<string>("");
  const [signature, setSignature] = useState<string>("");
  const [notes, setNotes] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  if (!open) return null;

  const countNum = Math.max(1, Math.min(50, parseInt(count || "1", 10) || 1));

  const onSubmit = async (e: React.FormEvent): Promise<void> => {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setToast(null);
    try {
      if (mode === "unified") {
        const result = await generateVoices({
          count: countNum,
          archetype,
          gender,
          age_impression: ageImpression,
          pace,
          pitch_register: pitch,
          emotion_default: emotion,
          tone,
          signature_inflection: signature,
          notes,
        });
        const errs = result.errors.length;
        setToast({
          kind: errs > 0 ? "err" : "ok",
          text: `已生成 ${result.generated.length} / 失败 ${errs}`,
        });
      } else {
        const result = await generateDiverseVoices({
          count: countNum,
          gender,
          age_impression: ageImpression || null,
          notes,
        });
        const errs = result.errors.length;
        setToast({
          kind: errs > 0 ? "err" : "ok",
          text: `多样模式生成 ${result.generated.length} / 失败 ${errs}`,
        });
      }
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
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="生成配音 profile">
      <div className="modal-panel voice-gen-panel">
        <header className="modal-header">
          <h2>🎙 生成配音 profile</h2>
          <button type="button" className="modal-close" aria-label="关闭" onClick={onClose}>✕</button>
        </header>
        <form onSubmit={onSubmit} className="modal-body voice-gen-body">
          <div className="voice-gen-row">
            <label className="voice-gen-field">
              <span className="voice-gen-label">生成模式</span>
              <select value={mode} onChange={(e) => setMode(e.target.value as Mode)}>
                <option value="unified">统一（手动选 archetype）</option>
                <option value="diverse">多样（10 archetype 均匀分布）</option>
              </select>
            </label>
            <label className="voice-gen-field voice-gen-field-narrow">
              <span className="voice-gen-label">数量 (1-50)</span>
              <input type="number" min={1} max={50} value={count} onChange={(e) => setCount(e.target.value)} />
            </label>
          </div>

          {mode === "unified" ? (
            <>
              <div className="voice-gen-row">
                <label className="voice-gen-field">
                  <span className="voice-gen-label">角色原型</span>
                  <select value={archetype} onChange={(e) => setArchetype(e.target.value)}>
                    {VOICE_ARCHETYPE_OPTIONS.map((slug) => (
                      <option key={slug} value={slug}>
                        {VOICE_ARCHETYPE_LABELS_ZH[slug] ?? slug}
                      </option>
                    ))}
                  </select>
                </label>
                <label className="voice-gen-field voice-gen-field-narrow">
                  <span className="voice-gen-label">性别</span>
                  <select value={gender} onChange={(e) => setGender(e.target.value)}>
                    {VOICE_GENDER_OPTIONS.map((g) => (
                      <option key={g} value={g}>{VOICE_GENDER_LABELS_ZH[g] ?? g}</option>
                    ))}
                  </select>
                </label>
                <label className="voice-gen-field voice-gen-field-narrow">
                  <span className="voice-gen-label">年龄段</span>
                  <select value={ageImpression} onChange={(e) => setAgeImpression(e.target.value)}>
                    {VOICE_AGE_OPTIONS.map((a) => (
                      <option key={a} value={a}>{VOICE_AGE_LABELS_ZH[a] ?? a}</option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="voice-gen-row">
                <label className="voice-gen-field voice-gen-field-narrow">
                  <span className="voice-gen-label">语速</span>
                  <select value={pace} onChange={(e) => setPace(e.target.value)}>
                    {VOICE_PACE_OPTIONS.map((p) => (
                      <option key={p} value={p}>{VOICE_PACE_LABELS_ZH[p] ?? p}</option>
                    ))}
                  </select>
                </label>
                <label className="voice-gen-field voice-gen-field-narrow">
                  <span className="voice-gen-label">音区</span>
                  <select value={pitch} onChange={(e) => setPitch(e.target.value)}>
                    {VOICE_PITCH_OPTIONS.map((p) => (
                      <option key={p} value={p}>{VOICE_PITCH_LABELS_ZH[p] ?? p}</option>
                    ))}
                  </select>
                </label>
                <label className="voice-gen-field voice-gen-field-narrow">
                  <span className="voice-gen-label">默认情绪</span>
                  <select value={emotion} onChange={(e) => setEmotion(e.target.value)}>
                    {VOICE_EMOTION_OPTIONS.map((em) => (
                      <option key={em} value={em}>{VOICE_EMOTION_LABELS_ZH[em] ?? em}</option>
                    ))}
                  </select>
                </label>
              </div>

              <label className="voice-gen-field voice-gen-field-block">
                <span className="voice-gen-label">音色描述（自由中文，可空）</span>
                <input type="text" value={tone} onChange={(e) => setTone(e.target.value)} placeholder="如：沉稳浑厚 / 嘶哑略带磁性" />
              </label>
              <label className="voice-gen-field voice-gen-field-block">
                <span className="voice-gen-label">标志性发声（自由中文，可空）</span>
                <input type="text" value={signature} onChange={(e) => setSignature(e.target.value)} placeholder="如：句尾上扬 / 喉音偏重" />
              </label>
            </>
          ) : (
            <div className="voice-gen-row">
              <label className="voice-gen-field">
                <span className="voice-gen-label">性别（多样模式只需一个）</span>
                <select value={gender} onChange={(e) => setGender(e.target.value)}>
                  {VOICE_GENDER_OPTIONS.map((g) => (
                    <option key={g} value={g}>{VOICE_GENDER_LABELS_ZH[g] ?? g}</option>
                  ))}
                </select>
              </label>
              <label className="voice-gen-field">
                <span className="voice-gen-label">年龄段（可选 — 留空时按 archetype 默认）</span>
                <select value={ageImpression} onChange={(e) => setAgeImpression(e.target.value)}>
                  <option value="">（按 archetype 默认）</option>
                  {VOICE_AGE_OPTIONS.map((a) => (
                    <option key={a} value={a}>{VOICE_AGE_LABELS_ZH[a] ?? a}</option>
                  ))}
                </select>
              </label>
            </div>
          )}

          <label className="voice-gen-field voice-gen-field-block">
            <span className="voice-gen-label">备注（可空，≤ 500 字）</span>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} maxLength={500} rows={2} />
          </label>

          {toast ? (
            <div className={`voice-toast voice-toast-${toast.kind}`} role="status">{toast.text}</div>
          ) : null}
        </form>
        <footer className="modal-footer">
          <button type="button" className="voice-btn voice-btn-secondary" onClick={onClose} disabled={busy}>取消</button>
          <button type="button" className="voice-btn voice-btn-primary" onClick={onSubmit as unknown as React.MouseEventHandler<HTMLButtonElement>} disabled={busy}>
            {busy ? "生成中…" : `🎙 生成 ${countNum} 条`}
          </button>
        </footer>
      </div>
    </div>
  );
}
