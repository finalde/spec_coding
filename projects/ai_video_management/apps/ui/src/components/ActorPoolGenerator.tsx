/** ActorPoolGenerator: enum dropdowns + count + resolution → preview prompts
 * → user confirms → 9-worker pool fires the actual gen with the previewed
 * seeds (so the Kling-bound prompt is byte-equal to what the user reviewed).
 *
 * follow-up 014: initial modal + dropdowns
 * follow-up 017: progress visibility
 * follow-up 027: 9-way concurrent worker pool
 * follow-up 029: resolution dropdown (normal/2K/4K)
 * follow-up 032: pre-fire preview step + seeds round-trip
 */
import { useCallback, useEffect, useRef, useState } from "react";
import {
  ATTR_LABELS_ZH,
  ATTR_OPTIONS,
  generateActors,
  previewPrompts,
  RANDOM_SENTINEL,
  rollRandomAttr,
  type PromptPreviewResult,
  type PromptPreviewSlot,
} from "../api";
import { ApiError } from "../types";

export interface ActorPoolGeneratorProps {
  open: boolean;
  onClose: () => void;
  onGenerated: () => void;
}

interface Progress {
  done: number;
  failed: number;
  total: number;
  inFlight: number;
  phase: "idle" | "generating";
  errors: { i: number; message: string }[];
  generatedIds: string[];
}

const CONCURRENCY = 9;
const MAX_BATCH_COUNT = 50;

export function ActorPoolGenerator({ open, onClose, onGenerated }: ActorPoolGeneratorProps): JSX.Element | null {
  // Per follow-up 064: every attr dropdown defaults to RANDOM_SENTINEL. The
  // frontend rolls a concrete value per slot before each preview / generate
  // call. resolution defaults to "normal" (fixed) so users don't get a
  // surprise mix of 1024px / 2K / 4K outputs.
  const [ethnicity, setEthnicity] = useState<string>(RANDOM_SENTINEL);
  const [gender, setGender] = useState<string>(RANDOM_SENTINEL);
  const [ageRange, setAgeRange] = useState<string>(RANDOM_SENTINEL);
  const [look, setLook] = useState<string>(RANDOM_SENTINEL);
  // Per follow-up 100: 眼睛 / 鼻子 / 嘴巴 / 皮肤 / 体型 are first-class dropdown
  // locks. Default RANDOM_SENTINEL → backend samples the rich pool
  // deterministically.
  const [eyes, setEyes] = useState<string>(RANDOM_SENTINEL);
  const [nose, setNose] = useState<string>(RANDOM_SENTINEL);
  const [lips, setLips] = useState<string>(RANDOM_SENTINEL);
  const [face, setFace] = useState<string>(RANDOM_SENTINEL);
  const [skin, setSkin] = useState<string>(RANDOM_SENTINEL);
  const [body, setBody] = useState<string>(RANDOM_SENTINEL);
  // Per multi-select redesign: qi_zhi is the only multi-select feature.
  // Empty array = random (backend falls back to look-derived overlay).
  // 1 entry = locked verbatim. N entries = each slot rolls one of the N.
  const [qiZhi, setQiZhi] = useState<string[]>([]);
  const [notes, setNotes] = useState<string>("");
  const [resolution, setResolution] = useState<string>(ATTR_OPTIONS.resolution[0]);
  // Per follow-up 055 + 057: split string-state for the input from the
  // clamped numeric `count` so typing is never re-clamped mid-keystroke
  // (old controlled `<input type="number" value={count}>` snapped "51" →
  // "50" after the cap and made the input look "stuck at 50").
  const [countText, setCountText] = useState<string>("5");
  const count = (() => {
    const n = Number(countText);
    if (!Number.isFinite(n)) return 1;
    const intN = Math.trunc(n);
    if (intN < 1) return 1;
    if (intN > MAX_BATCH_COUNT) return MAX_BATCH_COUNT;
    return intN;
  })();
  const [busy, setBusy] = useState<boolean>(false);
  const [previewBusy, setPreviewBusy] = useState<boolean>(false);
  const [preview, setPreview] = useState<PromptPreviewResult | null>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [toast, setToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const cancelledRef = useRef<boolean>(false);
  // Per follow-up 082: stash the preview's batch-coordination metadata so
  // the confirm path forwards identical batch_seed + batch_size to every
  // generate call — same coordination that fired during preview.
  const previewBatchRef = useRef<{ batchSeed: number; batchSize: number } | null>(null);

  useEffect(() => {
    if (!open) {
      setToast(null);
      setProgress(null);
      setBusy(false);
      setPreview(null);
      setPreviewError(null);
      setPreviewBusy(false);
      cancelledRef.current = false;
    }
  }, [open]);

  const onPreview = useCallback(async () => {
    if (busy || previewBusy) return;
    setPreviewBusy(true);
    setPreviewError(null);
    setToast(null);
    try {
      // Per follow-up 064: resolve RANDOM_SENTINEL → random roll per slot,
      // independently for each field. Then fan out to N parallel
      // previewPrompts(count=1, seeds=[base+i]) calls so each slot's prompt
      // is genuinely distinct (explicit seeds prevent the millisecond-
      // precision base_seed collision when calls fire in the same tick).
      const baseSeed = Date.now();
      // Per follow-up 082: one batch_seed per click; passed to each parallel
      // count=1 call along with batch_size + slot_index so the backend can
      // resolve within-batch-distinct face/body pool draws deterministically.
      const batchSeed = baseSeed;
      const batchSize = count;
      // Per follow-up 100: eyes / skin / body stay un-rolled at the frontend.
      // Backend deterministically samples the rich pool off the slot seed when
      // the value is RANDOM_SENTINEL — frontend doesn't pick a slug from the
      // 6-7 dropdown options because that would lose the richer multi-trait
      // pool descriptors users get from "random".
      const slotPlans = Array.from({ length: count }, (_, i) => ({
        seed: baseSeed + i,
        ethnicity: ethnicity === RANDOM_SENTINEL ? rollRandomAttr("ethnicity") : ethnicity,
        gender: gender === RANDOM_SENTINEL ? rollRandomAttr("gender") : gender,
        age_range: ageRange === RANDOM_SENTINEL ? rollRandomAttr("age_range") : ageRange,
        look: look === RANDOM_SENTINEL ? rollRandomAttr("look") : look,
        eyes: eyes === RANDOM_SENTINEL ? "" : eyes,
        nose: nose === RANDOM_SENTINEL ? "" : nose,
        lips: lips === RANDOM_SENTINEL ? "" : lips,
        face: face === RANDOM_SENTINEL ? "" : face,
        skin: skin === RANDOM_SENTINEL ? "" : skin,
        body: body === RANDOM_SENTINEL ? "" : body,
        // qi_zhi multi-select: empty subset → send "" so backend falls back to
        // look-derived overlay; non-empty subset → roll one per slot now so
        // the previewed value matches what gets sent on confirm.
        qi_zhi: qiZhi.length === 0 ? "" : qiZhi[Math.floor(Math.random() * qiZhi.length)],
      }));
      const responses = await Promise.all(
        slotPlans.map((plan, i) =>
          previewPrompts({
            count: 1,
            ethnicity: plan.ethnicity,
            gender: plan.gender,
            age_range: plan.age_range,
            look: plan.look,
            notes,
            resolution,
            seeds: [plan.seed],
            batch_seed: batchSeed,
            batch_size: batchSize,
            slot_index: i,
            eyes: plan.eyes,
            nose: plan.nose,
            lips: plan.lips,
            face: plan.face,
            skin: plan.skin,
            body: plan.body,
            qi_zhi: plan.qi_zhi,
          }),
        ),
      );
      const prompts: PromptPreviewSlot[] = responses.map((res, i) => {
        const inner = res.prompts[0] ?? { seed: slotPlans[i].seed, prompt: "(empty)" };
        const plan = slotPlans[i];
        return {
          seed: inner.seed,
          prompt: inner.prompt,
          body_prompt: inner.body_prompt,
          attrs: {
            ethnicity: plan.ethnicity,
            gender: plan.gender,
            age_range: plan.age_range,
            look: plan.look,
            notes,
            eyes: plan.eyes,
            nose: plan.nose,
            lips: plan.lips,
            face: plan.face,
            skin: plan.skin,
            body: plan.body,
            qi_zhi: plan.qi_zhi,
          },
        };
      });
      previewBatchRef.current = { batchSeed, batchSize };
      setPreview({ prompts, resolution });
    } catch (err) {
      const msg =
        err instanceof ApiError
          ? `${err.status} ${err.detail?.kind ?? err.message}`
          : err instanceof Error
            ? err.message
            : String(err);
      setPreviewError(`预览失败: ${msg}`);
    } finally {
      setPreviewBusy(false);
    }
  }, [ageRange, body, busy, count, ethnicity, eyes, face, gender, lips, look, nose, notes, previewBusy, qiZhi, resolution, skin]);

  const onConfirmGenerate = useCallback(async () => {
    if (!preview || busy) return;
    // Per follow-up 062: close the preview modal before starting workers so
    // the ProgressPanel below becomes visible instead of being hidden by
    // the preview overlay (gave a "nothing happens" perception in 059).
    const previewSnapshot = preview;
    setPreview(null);
    setBusy(true);
    setToast(null);
    cancelledRef.current = false;
    const seedsList = previewSnapshot.prompts.map((p) => p.seed);
    const total = seedsList.length;
    const errors: { i: number; message: string }[] = [];
    const generatedIds: string[] = [];
    let done = 0;
    let failed = 0;
    let inFlight = 0;
    setProgress({ done, failed, total, inFlight: 0, phase: "idle", errors, generatedIds });

    let nextSlot = 1;
    const claimSlot = (): number | null => {
      if (cancelledRef.current) return null;
      if (nextSlot > total) return null;
      const slot = nextSlot;
      nextSlot += 1;
      return slot;
    };

    const flush = (): void => {
      setProgress({
        done,
        failed,
        total,
        inFlight,
        phase: "generating",
        errors: [...errors],
        generatedIds: [...generatedIds],
      });
    };

    const worker = async (): Promise<void> => {
      while (true) {
        const slot = claimSlot();
        if (slot === null) return;
        inFlight += 1;
        flush();
        try {
          // Per follow-up 064: preview entries carry per-slot resolved
          // attrs (after rolling RANDOM_SENTINEL). Forward those instead
          // of the form fields so each generated actor matches its
          // reviewed prompt 1:1.
          const entry = previewSnapshot.prompts[slot - 1];
          const slotAttrs = entry?.attrs;
          // Per follow-up 082: forward the same batch_seed + batch_size +
          // per-slot slot_index used during preview so each Kling-fired
          // prompt matches the previewed one byte-for-byte (pool draws
          // come from the same _resolve_batch_picks resolution).
          const batchMeta = previewBatchRef.current;
          const result = await generateActors({
            count: 1,
            ethnicity: slotAttrs?.ethnicity ?? ethnicity,
            gender: slotAttrs?.gender ?? gender,
            age_range: slotAttrs?.age_range ?? ageRange,
            look: slotAttrs?.look ?? look,
            notes: slotAttrs?.notes ?? notes,
            resolution,
            seeds: [seedsList[slot - 1]],
            batch_seed: batchMeta?.batchSeed ?? null,
            batch_size: batchMeta?.batchSize ?? null,
            slot_index: slot - 1,
            eyes: slotAttrs?.eyes ?? (eyes === RANDOM_SENTINEL ? "" : eyes),
            nose: slotAttrs?.nose ?? (nose === RANDOM_SENTINEL ? "" : nose),
            lips: slotAttrs?.lips ?? (lips === RANDOM_SENTINEL ? "" : lips),
            face: slotAttrs?.face ?? (face === RANDOM_SENTINEL ? "" : face),
            skin: slotAttrs?.skin ?? (skin === RANDOM_SENTINEL ? "" : skin),
            body: slotAttrs?.body ?? (body === RANDOM_SENTINEL ? "" : body),
            // qi_zhi: always trust the previewed per-slot value (slotAttrs).
            // The frontend already rolled one of the user-selected subset
            // during preview, so confirm replays the exact previewed string.
            qi_zhi: slotAttrs?.qi_zhi ?? "",
          });
          if (result.generated.length > 0) {
            done += 1;
            generatedIds.push(result.generated[0].id);
          }
          for (const e of result.errors) {
            failed += 1;
            errors.push({ i: slot, message: `${e.requested_id}: ${e.message}` });
          }
        } catch (err) {
          failed += 1;
          const msg =
            err instanceof ApiError
              ? `${err.status} ${err.detail?.kind ?? err.message}`
              : err instanceof Error
                ? err.message
                : String(err);
          errors.push({ i: slot, message: msg });
        } finally {
          inFlight -= 1;
        }
        onGenerated();
        flush();
      }
    };

    const workerCount = Math.min(CONCURRENCY, total);
    await Promise.all(Array.from({ length: workerCount }, () => worker()));

    setProgress((p) => (p ? { ...p, inFlight: 0, phase: "idle" } : null));
    const wasCancelled = cancelledRef.current;
    setToast({
      kind: failed > 0 || wasCancelled ? "err" : "ok",
      text: wasCancelled
        ? `已中断 — 已生成 ${done} / 失败 ${failed} / 跳过 ${total - done - failed}`
        : `已生成 ${done} / 失败 ${failed}`,
    });
    setBusy(false);
    setPreview(null);
  }, [ageRange, body, busy, ethnicity, eyes, face, gender, lips, look, nose, notes, onGenerated, preview, qiZhi, resolution, skin]);

  const requestCancel = useCallback(() => {
    cancelledRef.current = true;
  }, []);

  const onCloseRequest = useCallback(() => {
    if (busy) {
      cancelledRef.current = true;
      return;
    }
    onClose();
  }, [busy, onClose]);

  const cancelPreview = useCallback(() => {
    setPreview(null);
  }, []);

  if (!open) return null;

  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="生成演员人脸">
      <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>🎭 生成演员人脸</h2>
          <button
            type="button"
            className="modal-close"
            onClick={onCloseRequest}
            aria-label={busy ? "中断后关闭" : "关闭"}
          >
            ×
          </button>
        </div>
        <div className="modal-body">
          <p className="muted" style={{ marginTop: 0 }}>
            每个字段可选 🎲 随机（默认）或具体值；点 "预览" 后端会按你选的（已固定的字段）+ 每槽随机滚剩下字段，给你 N 份独立 prompt 供 review。
          </p>
          <div className="form-grid">
            <Field label="民族" id="ethnicity">
              <select value={ethnicity} onChange={(e) => setEthnicity(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.ethnicity.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.ethnicity[o]}</option>)}
              </select>
            </Field>
            <Field label="性别" id="gender">
              <select value={gender} onChange={(e) => setGender(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.gender.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.gender[o]}</option>)}
              </select>
            </Field>
            <Field label="年龄段" id="age_range">
              <select value={ageRange} onChange={(e) => setAgeRange(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.age_range.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.age_range[o]}</option>)}
              </select>
            </Field>
            <Field label="角色原型" id="look">
              <select value={look} onChange={(e) => setLook(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.look.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.look[o]}</option>)}
              </select>
            </Field>
            <Field label="眼睛" id="eyes">
              <select value={eyes} onChange={(e) => setEyes(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.eyes.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.eyes[o]}</option>)}
              </select>
            </Field>
            <Field label="鼻子" id="nose">
              <select value={nose} onChange={(e) => setNose(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.nose.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.nose[o]}</option>)}
              </select>
            </Field>
            <Field label="嘴巴" id="lips">
              <select value={lips} onChange={(e) => setLips(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.lips.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.lips[o]}</option>)}
              </select>
            </Field>
            <Field label="脸型" id="face">
              <select value={face} onChange={(e) => setFace(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.face.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.face[o]}</option>)}
              </select>
            </Field>
            <Field label="皮肤" id="skin">
              <select value={skin} onChange={(e) => setSkin(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.skin.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.skin[o]}</option>)}
              </select>
            </Field>
            <Field label="体型" id="body">
              <select value={body} onChange={(e) => setBody(e.target.value)} disabled={busy || previewBusy}>
                <option value={RANDOM_SENTINEL}>🎲 随机</option>
                {ATTR_OPTIONS.body.map((o) => <option key={o} value={o}>{ATTR_LABELS_ZH.body[o]}</option>)}
              </select>
            </Field>
            <Field
              label={`气质（${qiZhi.length === 0 ? "🎲 随机" : `已选 ${qiZhi.length}`}）`}
              id="qi_zhi"
            >
              <div className="qi-zhi-chips" role="group" aria-label="气质多选 (留空 = 随机；选多个 = 每个 actor 随机取其一)">
                {ATTR_OPTIONS.qi_zhi.map((o) => {
                  const sel = qiZhi.includes(o);
                  return (
                    <button
                      type="button"
                      key={o}
                      className={`qi-zhi-chip ${sel ? "qi-zhi-chip-selected" : ""}`}
                      aria-pressed={sel}
                      disabled={busy || previewBusy}
                      onClick={() =>
                        setQiZhi((prev) =>
                          prev.includes(o) ? prev.filter((x) => x !== o) : [...prev, o],
                        )
                      }
                    >
                      {ATTR_LABELS_ZH.qi_zhi[o]}
                    </button>
                  );
                })}
                {qiZhi.length > 0 ? (
                  <button
                    type="button"
                    className="qi-zhi-chip-clear"
                    onClick={() => setQiZhi([])}
                    disabled={busy || previewBusy}
                    title="清除选择 → 改回随机"
                  >
                    ✕ 清空
                  </button>
                ) : null}
              </div>
            </Field>
            <Field label={`数量 (1–${MAX_BATCH_COUNT})`} id="count">
              <input
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                value={countText}
                onChange={(e) => setCountText(e.target.value.replace(/[^0-9]/g, ""))}
                onBlur={() => setCountText(String(count))}
                onKeyDown={(e) => {
                  e.stopPropagation();
                  if (e.key === "Enter") e.preventDefault();
                }}
                onClick={(e) => e.stopPropagation()}
                onMouseDown={(e) => e.stopPropagation()}
                disabled={busy || previewBusy}
              />
            </Field>
            <Field label="画质" id="resolution">
              <select value={resolution} onChange={(e) => setResolution(e.target.value)} disabled={busy || previewBusy}>
                {ATTR_OPTIONS.resolution.map((o) => (
                  <option key={o} value={o}>{ATTR_LABELS_ZH.resolution[o]}</option>
                ))}
              </select>
            </Field>
          </div>
          <Field label="备注 (可选)" id="notes">
            <textarea
              rows={2}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              disabled={busy || previewBusy}
              maxLength={500}
              placeholder="例如：用于古装仙侠剧主角"
            />
          </Field>

          {previewError ? (
            <div role="alert" className="modal-toast modal-toast-err">{previewError}</div>
          ) : null}

          {progress ? (
            <ProgressPanel progress={progress} busy={busy} />
          ) : null}

          {toast ? (
            <div role="status" aria-live="polite" className={`modal-toast modal-toast-${toast.kind}`}>
              {toast.text}
            </div>
          ) : null}
        </div>
        <div className="modal-footer">
          {busy ? (
            <button type="button" onClick={requestCancel} disabled={cancelledRef.current}>
              {cancelledRef.current ? "正在停止…" : "停止"}
            </button>
          ) : null}
          <button
            type="button"
            className="modal-primary"
            onClick={onPreview}
            disabled={busy || previewBusy}
          >
            {busy && progress
              ? `生成中… (${progress.done + progress.failed} / ${progress.total})`
              : previewBusy
                ? "计算预览中…"
                : `预览 ${count} 个 prompt`}
          </button>
        </div>
      </div>
      {preview ? (
        <PromptPreviewModal
          preview={preview}
          onCancel={cancelPreview}
          onConfirm={onConfirmGenerate}
        />
      ) : null}
    </div>
  );
}

interface PreviewModalProps {
  preview: PromptPreviewResult;
  onCancel: () => void;
  onConfirm: () => void;
}

function PromptPreviewModal({ preview, onCancel, onConfirm }: PreviewModalProps): JSX.Element {
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-label="预览将发送到 Kling 的 prompt" onClick={onCancel}>
      <div className="modal-panel prompt-preview-panel" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📝 预览 prompt ({preview.prompts.length} 张) — 画质 {preview.resolution}</h2>
          <button type="button" className="modal-close" onClick={onCancel} aria-label="关闭预览">×</button>
        </div>
        <div className="modal-body">
          <p className="prompt-preview-hint">
            以下是将发送给 Kling API 的 final prompt，每张图片一份（含 variance + anti-wax + camera cue）。确认后立即开始 9 路并发生成。
          </p>
          <ol className="prompt-preview-list">
            {preview.prompts.map((p, idx) => (
              <li key={p.seed} className="prompt-preview-card">
                <div className="prompt-preview-meta">
                  <strong>第 {idx + 1} 张</strong>
                  <span className="prompt-preview-seed">seed: {p.seed}</span>
                  <span className="prompt-preview-seed">{p.prompt.length} 字符</span>
                </div>
                {p.attrs ? (
                  <div className="prompt-preview-attrs">
                    {p.attrs.ethnicity} / {p.attrs.gender} / {p.attrs.age_range} / {p.attrs.look}
                  </div>
                ) : null}
                <details>
                  <summary className="prompt-preview-toggle">
                    {p.prompt.slice(0, 180)}{p.prompt.length > 180 ? "…" : ""}
                  </summary>
                  <pre className="prompt-preview-body">{p.prompt}</pre>
                </details>
              </li>
            ))}
          </ol>
        </div>
        <div className="modal-footer">
          <button type="button" onClick={onCancel}>取消</button>
          <button type="button" className="modal-primary" onClick={onConfirm}>
            ✓ 确认发送 ({preview.prompts.length})
          </button>
        </div>
      </div>
    </div>
  );
}

function ProgressPanel({ progress, busy }: { progress: Progress; busy: boolean }): JSX.Element {
  const pct = progress.total > 0 ? Math.round(((progress.done + progress.failed) / progress.total) * 100) : 0;
  const phaseLabel = progress.phase === "generating" ? "🔄 生成中…" : "";
  return (
    <div className="progress-panel" role="status" aria-live="polite">
      <div className="progress-summary">
        <span>
          {busy ? `${phaseLabel} ${progress.done + progress.failed} / ${progress.total}` : `✓ 完成: ${progress.done + progress.failed} / ${progress.total}`}
          {" · "}
          <span className="progress-ok">✓ {progress.done}</span>
          {" · "}
          <span className="progress-err">✗ {progress.failed}</span>
          {busy && progress.inFlight > 0 ? (
            <> {" · "} <span className="progress-inflight">⚡ 并发 {progress.inFlight}</span></>
          ) : null}
          {" · "}
          {pct}%
        </span>
      </div>
      <div className="progress-bar" aria-label={`进度 ${pct}%`}>
        <div className="progress-bar-fill" style={{ width: `${pct}%` }} />
      </div>
      {progress.generatedIds.length > 0 ? (
        <details className="progress-details">
          <summary>已生成 {progress.generatedIds.length} 张</summary>
          <code>{progress.generatedIds.join(", ")}</code>
        </details>
      ) : null}
      {progress.errors.length > 0 ? (
        <details className="progress-details progress-details-err" open>
          <summary>失败 {progress.errors.length} 张 — 查看原因</summary>
          <ul>
            {progress.errors.map((e, idx) => (
              <li key={idx}><strong>#{e.i}</strong>: {e.message}</li>
            ))}
          </ul>
        </details>
      ) : null}
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
