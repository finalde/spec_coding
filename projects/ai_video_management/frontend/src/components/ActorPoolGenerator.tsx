import { useCallback, useEffect, useState } from "react";
import { ATTR_OPTIONS, generateActors } from "../api";
import { ApiError } from "../types";

export interface ActorPoolGeneratorProps {
  open: boolean;
  onClose: () => void;
  onGenerated: () => void;
}

export function ActorPoolGenerator({ open, onClose, onGenerated }: ActorPoolGeneratorProps): JSX.Element | null {
  const [ethnicity, setEthnicity] = useState<string>(ATTR_OPTIONS.ethnicity[0]);
  const [gender, setGender] = useState<string>(ATTR_OPTIONS.gender[0]);
  const [ageRange, setAgeRange] = useState<string>(ATTR_OPTIONS.age_range[0]);
  const [look, setLook] = useState<string>(ATTR_OPTIONS.look[0]);
  const [style, setStyle] = useState<string>(ATTR_OPTIONS.style[0]);
  const [notes, setNotes] = useState<string>("");
  const [count, setCount] = useState<number>(5);
  const [busy, setBusy] = useState<boolean>(false);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  useEffect(() => {
    if (!open) {
      setToast(null);
      setBusy(false);
    }
  }, [open]);

  const onSubmit = useCallback(async () => {
    if (busy) return;
    setBusy(true);
    setToast(null);
    try {
      const result = await generateActors({
        count,
        ethnicity,
        gender,
        age_range: ageRange,
        look,
        style,
        notes,
      });
      const ok = result.generated.length;
      const err = result.errors.length;
      setToast({
        kind: err > 0 ? "err" : "ok",
        text: `已生成 ${ok} / 失败 ${err}`,
      });
      onGenerated();
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? `生成失败: ${err.detail?.kind ?? err.status}`
          : `生成失败: ${err instanceof Error ? err.message : String(err)}`;
      setToast({ kind: "err", text: msg });
    } finally {
      setBusy(false);
    }
  }, [ageRange, busy, count, ethnicity, gender, look, notes, onGenerated, style]);

  if (!open) return null;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="生成演员人脸" onClick={onClose}>
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🎭 生成演员人脸</h2>
          <button
            type="button"
            className="modal-close"
            onClick={onClose}
            aria-label="关闭"
            disabled={busy}
          >
            ×
          </button>
        </div>
        <div className="modal-body">
          <div className="form-grid">
            <Field label="民族" id="ethnicity">
              <select value={ethnicity} onChange={(e) => setEthnicity(e.target.value)} disabled={busy}>
                {ATTR_OPTIONS.ethnicity.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="性别" id="gender">
              <select value={gender} onChange={(e) => setGender(e.target.value)} disabled={busy}>
                {ATTR_OPTIONS.gender.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="年龄段" id="age_range">
              <select value={ageRange} onChange={(e) => setAgeRange(e.target.value)} disabled={busy}>
                {ATTR_OPTIONS.age_range.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="外貌气质" id="look">
              <select value={look} onChange={(e) => setLook(e.target.value)} disabled={busy}>
                {ATTR_OPTIONS.look.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="风格" id="style">
              <select value={style} onChange={(e) => setStyle(e.target.value)} disabled={busy}>
                {ATTR_OPTIONS.style.map((o) => <option key={o} value={o}>{o}</option>)}
              </select>
            </Field>
            <Field label="数量 (1–20)" id="count">
              <input
                type="number"
                min={1}
                max={20}
                value={count}
                onChange={(e) => setCount(Math.max(1, Math.min(20, Number(e.target.value) || 1)))}
                disabled={busy}
              />
            </Field>
          </div>
          <Field label="备注 (可选)" id="notes">
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={busy}
              maxLength={500}
              placeholder="例如：用于古装仙侠剧主角"
            />
          </Field>
          {toast ? (
            <div role="status" aria-live="polite" className={`modal-toast modal-toast-${toast.kind}`}>
              {toast.text}
            </div>
          ) : null}
        </div>
        <div className="modal-footer">
          <button type="button" onClick={onClose} disabled={busy}>取消</button>
          <button
            type="button"
            className="modal-primary"
            onClick={onSubmit}
            disabled={busy}
          >
            {busy ? `生成中… (${count} 张)` : "生成"}
          </button>
        </div>
      </div>
    </div>
  );
}

function Field({ label, id, children }: { label: string; id: string; children: React.ReactNode }): JSX.Element {
  return (
    <label className="form-field" htmlFor={id}>
      <span className="form-field-label">{label}</span>
      {children}
    </label>
  );
}
