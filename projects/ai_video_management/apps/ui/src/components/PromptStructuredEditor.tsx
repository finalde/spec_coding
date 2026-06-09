/** PromptStructuredEditor: form-based editor for a single fenced code block.
 *
 * Replaces the raw textarea in VoiceView / ActorView / ShotPairView / ImageRefView
 * edit mode. Detects `label: value` lines in the code block body and renders
 * each as an input / textarea / dropdown (per `fieldWidget(label)`); freeform
 * prefix lines (reference-handle headers, blank separators) sit in a
 * read-only banner so the structure survives save/load round-trips.
 *
 * Save semantics: serialize current field state via `serializePrompt`, hand
 * the resulting body to the caller's `onSave(newBody)`. The caller is still
 * responsible for `replaceFirstFencedCode` / `putFile` / 409 handling.
 *
 * A "raw mode" toggle lets the user fall back to plain-text editing when
 * the body is too unstructured for the form (e.g. video prompts with many
 * timed-beat lines under 动作:).
 */
import { useEffect, useMemo, useState } from "react";
import {
  dropdownOptions,
  fieldWidget,
  joinMulti,
  mergeWithCanonical,
  parsePrompt,
  serializePrompt,
  splitMulti,
  type BlockKind,
  type FieldDef,
  type ParsedPrompt,
} from "../lib/promptSchema";
import { suggestRefinements, type RefinementSuggestion } from "../api";
import { ApiError } from "../types";

export interface PromptStructuredEditorProps {
  /** Initial code-block body (no fences). */
  initialBody: string;
  /** Called when the user clicks ✓ Save. */
  onSave: (newBody: string) => void | Promise<void>;
  /** Called when the user clicks ✕ Cancel. */
  onCancel: () => void;
  /** True while a save is in flight; disables the form. */
  saving?: boolean;
  /** Inline error to render below the form (e.g. 409 stale-mtime). */
  errorMessage?: string | null;
  /** Optional context label rendered in the header (e.g. "起始帧" / "结束帧" / "video prompt"). */
  blockLabel?: string;
  /** Shot block kind. When set, the structured form merges in the fixed
   *  canonical field set so 人物 / 场景 / etc. always appear. */
  blockKind?: BlockKind | null;
  /** Character display names for the 人物 multi-select (drama-scoped). */
  characterOptions?: string[];
  /** Scene display names for the 场景 picker (drama-scoped). */
  sceneOptions?: string[];
  /** Follow-up 117: surrounding shot markdown (小说原文 + Shot context + frames)
   *  used as context for per-dimension AI refinement suggestions. When present
   *  AND blockKind === "video", each canonical dimension field gets a ✨ 推荐
   *  button. */
  shotContext?: string;
  /** File path of the shot being edited — drama is derived from it for the
   *  suggestion request. */
  currentPath?: string;
}

type Mode = "structured" | "raw";

export function PromptStructuredEditor({
  initialBody,
  onSave,
  onCancel,
  saving = false,
  errorMessage = null,
  blockLabel,
  blockKind = null,
  characterOptions = [],
  sceneOptions = [],
  shotContext,
  currentPath,
}: PromptStructuredEditorProps): JSX.Element {
  const initialParsed = useMemo<ParsedPrompt>(
    () => mergeWithCanonical(parsePrompt(initialBody), blockKind),
    [initialBody, blockKind],
  );
  const [parsed, setParsed] = useState<ParsedPrompt>(initialParsed);
  const [rawBuffer, setRawBuffer] = useState<string>(initialBody);
  // Default to RAW (direct text) editing for every prompt — clicking ✏ Edit
  // immediately shows the prompt's text in an editable textarea so users can
  // tweak the wording directly. The 🪜 结构化 toggle remains for per-field form
  // editing. (Per follow-up: "每个 prompt 给我一个 edit mode, 直接修改里面的文字".)
  const [mode, setMode] = useState<Mode>("raw");

  // Follow-up 117: AI refinement is offered only for the video block, and only
  // when we have the surrounding shot context to feed the model.
  const refineEnabled = blockKind === "video" && typeof shotContext === "string" && shotContext.trim().length > 0;
  const drama = useMemo(() => dramaFromPath(currentPath), [currentPath]);
  const sceneHint = useMemo(() => sceneFromFields(parsed.fields), [parsed.fields]);
  const refineCtx = useMemo<RefineContext | null>(
    () =>
      refineEnabled
        ? {
            shotContext: shotContext as string,
            drama,
            scene: sceneHint,
            getPromptBody: () => serializePrompt(parsed),
          }
        : null,
    [refineEnabled, shotContext, drama, sceneHint, parsed],
  );

  const updateField = (order: number, newValue: string): void => {
    setParsed((cur) => ({
      ...cur,
      fields: cur.fields.map((f) => (f.order === order ? { ...f, value: newValue } : f)),
    }));
  };

  const handleSave = async (): Promise<void> => {
    const body = mode === "structured" ? serializePrompt(parsed) : rawBuffer;
    await onSave(body);
  };

  const switchToRaw = (): void => {
    // Capture current structured state into the raw buffer so toggling
    // doesn't lose user edits.
    setRawBuffer(serializePrompt(parsed));
    setMode("raw");
  };
  const switchToStructured = (): void => {
    // Re-parse the raw buffer so structured fields reflect the latest text.
    setParsed(parsePrompt(rawBuffer));
    setMode("structured");
  };

  return (
    <div className="prompt-structured-editor">
      <header className="prompt-editor-header">
        <span className="prompt-editor-title">
          {blockLabel ? `编辑：${blockLabel}` : "编辑 prompt"}
        </span>
        <div className="prompt-editor-toolbar">
          <button
            type="button"
            className={`prompt-editor-mode-btn${mode === "structured" ? " prompt-editor-mode-active" : ""}`}
            onClick={switchToStructured}
            disabled={saving}
            title="逐字段表单编辑"
          >
            🪜 结构化
          </button>
          <button
            type="button"
            className={`prompt-editor-mode-btn${mode === "raw" ? " prompt-editor-mode-active" : ""}`}
            onClick={switchToRaw}
            disabled={saving}
            title="原始文本编辑"
          >
            📝 原文
          </button>
        </div>
      </header>

      {mode === "structured" ? (
        <StructuredForm
          parsed={parsed}
          onChangeField={updateField}
          disabled={saving}
          characterOptions={characterOptions}
          sceneOptions={sceneOptions}
          refineCtx={refineCtx}
        />
      ) : (
        <textarea
          className="prompt-editor-raw-textarea"
          value={rawBuffer}
          onChange={(e) => setRawBuffer(e.target.value)}
          spellCheck={false}
          rows={Math.min(50, Math.max(12, rawBuffer.split("\n").length + 1))}
          disabled={saving}
        />
      )}

      {errorMessage ? (
        <div role="alert" className="prompt-editor-error">{errorMessage}</div>
      ) : null}

      <footer className="prompt-editor-footer">
        <button
          type="button"
          className="voice-btn voice-btn-primary prompt-editor-save"
          onClick={() => void handleSave()}
          disabled={saving}
        >
          {saving ? "保存中…" : "✓ Save"}
        </button>
        <button
          type="button"
          className="voice-btn voice-btn-secondary"
          onClick={onCancel}
          disabled={saving}
        >
          ✕ Cancel
        </button>
      </footer>
    </div>
  );
}

/** Follow-up 117: context passed down so each dimension field can request
 *  AI refinement suggestions. `getPromptBody` is read lazily at click time so
 *  the request reflects the latest edits to the other fields. */
interface RefineContext {
  shotContext: string;
  drama: string | null;
  scene: string | null;
  getPromptBody: () => string;
}

interface StructuredFormProps {
  parsed: ParsedPrompt;
  onChangeField: (order: number, value: string) => void;
  disabled: boolean;
  characterOptions: string[];
  sceneOptions: string[];
  refineCtx: RefineContext | null;
}

function StructuredForm({
  parsed,
  onChangeField,
  disabled,
  characterOptions,
  sceneOptions,
  refineCtx,
}: StructuredFormProps): JSX.Element {
  // Only one dimension's suggestion panel is open at a time.
  const [openOrder, setOpenOrder] = useState<number | null>(null);
  if (parsed.fields.length === 0) {
    return (
      <div className="prompt-editor-no-fields">
        未检测到 `label: value` 字段 — 请切换到「原文」模式编辑。
      </div>
    );
  }
  return (
    <div className="prompt-editor-form">
      {parsed.freeform ? (
        <details className="prompt-editor-freeform">
          <summary>引用 / 表头 (保持原样, 不可编辑)</summary>
          <pre>{parsed.freeform}</pre>
        </details>
      ) : null}
      {parsed.fields.map((f) => (
        <FieldRow
          key={f.order}
          field={f}
          onChange={(v) => onChangeField(f.order, v)}
          disabled={disabled}
          characterOptions={characterOptions}
          sceneOptions={sceneOptions}
          refineCtx={refineCtx && isRefinableDimension(f.label) ? refineCtx : null}
          refineOpen={openOrder === f.order}
          onToggleRefine={() => setOpenOrder((cur) => (cur === f.order ? null : f.order))}
          onCloseRefine={() => setOpenOrder(null)}
        />
      ))}
    </div>
  );
}

interface FieldRowProps {
  field: FieldDef;
  onChange: (value: string) => void;
  disabled: boolean;
  characterOptions: string[];
  sceneOptions: string[];
  refineCtx: RefineContext | null;
  refineOpen: boolean;
  onToggleRefine: () => void;
  onCloseRefine: () => void;
}

function FieldRow({
  field,
  onChange,
  disabled,
  characterOptions,
  sceneOptions,
  refineCtx,
  refineOpen,
  onToggleRefine,
  onCloseRefine,
}: FieldRowProps): JSX.Element {
  const widget = fieldWidget(field.label);

  // Smart merge per follow-up 117: empty field → fill; non-empty → append on
  // a new line so existing content is preserved.
  const applySuggestion = (value: string): void => {
    const cur = field.value;
    onChange(cur.trim() === "" ? value : `${cur.replace(/\n+$/, "")}\n${value}`);
    onCloseRefine();
  };

  return (
    <label className="prompt-editor-field">
      <span className="prompt-editor-field-label">
        {field.label}
        {refineCtx ? (
          <button
            type="button"
            className={`prompt-refine-btn${refineOpen ? " prompt-refine-btn-active" : ""}`}
            onClick={onToggleRefine}
            disabled={disabled}
            title="让 AI 根据本镜剧情推荐细化选项"
          >
            ✨ 推荐
          </button>
        ) : null}
      </span>
      {refineCtx && refineOpen ? (
        <RefinePanel
          dimension={field.label}
          currentValue={field.value}
          refineCtx={refineCtx}
          onApply={applySuggestion}
          onClose={onCloseRefine}
        />
      ) : null}
      {widget === "multiselect" ? (
        <MultiSelectInput value={field.value} options={characterOptions} onChange={onChange} disabled={disabled} />
      ) : widget === "select" ? (
        <SelectInput value={field.value} options={sceneOptions} onChange={onChange} disabled={disabled} />
      ) : widget === "dropdown" ? (
        <DropdownInput label={field.label} value={field.value} onChange={onChange} disabled={disabled} />
      ) : widget === "textarea" ? (
        <textarea
          className="prompt-editor-field-textarea"
          value={field.value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
          rows={Math.min(20, Math.max(2, field.value.split("\n").length + 1))}
          disabled={disabled}
        />
      ) : (
        <input
          type="text"
          className="prompt-editor-field-input"
          value={field.value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
          disabled={disabled}
        />
      )}
    </label>
  );
}

interface DropdownInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  disabled: boolean;
}

interface MultiSelectInputProps {
  value: string;
  options: string[];
  onChange: (value: string) => void;
  disabled: boolean;
}

/** 人物 multi-select: checkbox group over the drama's characters. Selected
 *  names not present in `options` (ad-hoc / cross-drama) render as extra
 *  checked rows so they survive a round-trip; a free input adds new names. */
function MultiSelectInput({ value, options, onChange, disabled }: MultiSelectInputProps): JSX.Element {
  const selected = useMemo(() => splitMulti(value), [value]);
  const [draft, setDraft] = useState("");
  const selectedSet = new Set(selected);
  const extras = selected.filter((s) => !options.includes(s));
  const allRows = [...options, ...extras];

  const toggle = (name: string): void => {
    const next = selectedSet.has(name)
      ? selected.filter((s) => s !== name)
      : [...selected, name];
    onChange(joinMulti(next));
  };

  const addDraft = (): void => {
    const name = draft.trim();
    if (name && !selectedSet.has(name)) onChange(joinMulti([...selected, name]));
    setDraft("");
  };

  return (
    <div className="prompt-editor-multiselect">
      {allRows.length === 0 ? (
        <span className="prompt-editor-multiselect-empty muted">本剧暂无角色文件夹 — 可在下方手动输入</span>
      ) : (
        <div className="prompt-editor-multiselect-options">
          {allRows.map((name) => (
            <label key={name} className="prompt-editor-checkbox">
              <input
                type="checkbox"
                checked={selectedSet.has(name)}
                onChange={() => toggle(name)}
                disabled={disabled}
              />
              <span>{name}</span>
            </label>
          ))}
        </div>
      )}
      <div className="prompt-editor-multiselect-add">
        <input
          type="text"
          className="prompt-editor-field-input"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              e.preventDefault();
              addDraft();
            }
          }}
          placeholder="+ 添加角色"
          spellCheck={false}
          disabled={disabled}
        />
        <button type="button" className="voice-btn voice-btn-secondary" onClick={addDraft} disabled={disabled || !draft.trim()}>
          添加
        </button>
      </div>
    </div>
  );
}

interface SelectInputProps {
  value: string;
  options: string[];
  onChange: (value: string) => void;
  disabled: boolean;
}

/** 场景 picker: single-select over the drama's scenes, with a 自定义… escape
 *  hatch whose free input preserves any variant suffix (e.g. "无寿崖 渡劫态 …"). */
function SelectInput({ value, options, onChange, disabled }: SelectInputProps): JSX.Element {
  const inList = options.includes(value.trim());
  return (
    <div className="prompt-editor-dropdown-wrapper">
      <select
        className="prompt-editor-field-select"
        value={inList ? value.trim() : "__custom__"}
        onChange={(e) => {
          if (e.target.value === "__custom__") return;
          onChange(e.target.value);
        }}
        disabled={disabled}
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
        <option value="__custom__">自定义…</option>
      </select>
      {!inList ? (
        <input
          type="text"
          className="prompt-editor-field-input prompt-editor-dropdown-custom"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
          disabled={disabled}
          placeholder="场景描述 (可含变体状态)"
        />
      ) : null}
    </div>
  );
}

function DropdownInput({ label, value, onChange, disabled }: DropdownInputProps): JSX.Element {
  const options = dropdownOptions(label);
  const inList = options.includes(value.trim());
  // Always offer a custom-value option so authors can drop in arbitrary
  // 时长 like `4.5s` without us blocking them.
  return (
    <div className="prompt-editor-dropdown-wrapper">
      <select
        className="prompt-editor-field-select"
        value={inList ? value.trim() : "__custom__"}
        onChange={(e) => {
          if (e.target.value === "__custom__") return;
          onChange(e.target.value);
        }}
        disabled={disabled}
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
        {!inList ? <option value="__custom__">自定义…</option> : null}
      </select>
      {!inList ? (
        <input
          type="text"
          className="prompt-editor-field-input prompt-editor-dropdown-custom"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          spellCheck={false}
          disabled={disabled}
          placeholder="自定义值"
        />
      ) : null}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Follow-up 117: per-dimension AI refinement.
// ---------------------------------------------------------------------------

/** Dimensions worth refining via the LLM — the descriptive video-prompt
 *  fields. 人物 / 场景 are picker-backed and 比例 is a fixed enum, so they're
 *  excluded; 时长 is a plot-beat decision left to the dropdown. */
const _REFINABLE = new Set([
  "镜头",
  "运镜",
  "动作",
  "台词/字幕",
  "光线/色调",
  "节奏",
  "渲染样式",
]);

function isRefinableDimension(label: string): boolean {
  return _REFINABLE.has(label.replace(/\s+/g, ""));
}

/** `ai_videos/{drama}/episodes/...` → drama, or null. */
function dramaFromPath(path: string | undefined): string | null {
  if (!path) return null;
  const parts = path.split("/");
  const i = parts.indexOf("ai_videos");
  return i >= 0 && parts.length > i + 1 ? parts[i + 1] : null;
}

/** Pull the current 场景 field value (if any) to hint the suggestion request. */
function sceneFromFields(fields: FieldDef[]): string | null {
  const f = fields.find((x) => x.label.replace(/\s+/g, "") === "场景" || x.label.replace(/\s+/g, "") === "場景");
  const v = f?.value.trim();
  return v ? v : null;
}

interface RefinePanelProps {
  dimension: string;
  currentValue: string;
  refineCtx: RefineContext;
  onApply: (value: string) => void;
  onClose: () => void;
}

/** Fetches suggestions for one dimension on open, lists them as selectable
 *  cards, and applies the chosen one on 确认. */
function RefinePanel({ dimension, currentValue, refineCtx, onApply, onClose }: RefinePanelProps): JSX.Element {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<RefinementSuggestion[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    setSelected(null);
    suggestRefinements({
      dimension,
      current_value: currentValue,
      shot_context: refineCtx.shotContext,
      prompt_body: refineCtx.getPromptBody(),
      drama: refineCtx.drama,
      scene: refineCtx.scene,
      count: 4,
    })
      .then((res) => {
        if (cancelled) return;
        setSuggestions(res.suggestions);
        if (res.suggestions.length === 0) setError("模型没有返回可用的建议，请重试。");
      })
      .catch((err) => {
        if (cancelled) return;
        setError(refineErrorMessage(err));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // reloadKey lets 「重新生成」 re-run; other deps are stable for an open panel.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [dimension, reloadKey]);

  return (
    <div className="prompt-refine-panel" role="group" aria-label={`${dimension} AI 推荐`}>
      <div className="prompt-refine-panel-header">
        <span>✨ AI 推荐 · {dimension}</span>
        <div className="prompt-refine-panel-tools">
          <button type="button" className="prompt-refine-link" onClick={() => setReloadKey((k) => k + 1)} disabled={loading}>
            重新生成
          </button>
          <button type="button" className="prompt-refine-link" onClick={onClose}>
            收起
          </button>
        </div>
      </div>

      {loading ? (
        <div className="prompt-refine-loading">正在根据本镜剧情生成建议…</div>
      ) : error ? (
        <div className="prompt-refine-error" role="alert">{error}</div>
      ) : (
        <>
          <div className="prompt-refine-cards">
            {suggestions.map((s, i) => (
              <button
                type="button"
                key={i}
                className={`prompt-refine-card${selected === i ? " prompt-refine-card-selected" : ""}`}
                onClick={() => setSelected(i)}
                aria-pressed={selected === i}
              >
                <span className="prompt-refine-card-value">{s.value}</span>
                {s.rationale ? <span className="prompt-refine-card-rationale">{s.rationale}</span> : null}
              </button>
            ))}
          </div>
          <div className="prompt-refine-actions">
            <button
              type="button"
              className="voice-btn voice-btn-primary"
              disabled={selected === null}
              onClick={() => {
                if (selected !== null) onApply(suggestions[selected].value);
              }}
              title={currentValue.trim() === "" ? "填入该字段" : "追加到该字段已有内容之后"}
            >
              {currentValue.trim() === "" ? "✓ 填入" : "✓ 追加"}
            </button>
            <button type="button" className="voice-btn voice-btn-secondary" onClick={onClose}>
              取消
            </button>
          </div>
        </>
      )}
    </div>
  );
}

function refineErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    const kind = err.detail?.kind;
    if (kind === "suggestion_unavailable") return "未配置 ANTHROPIC_API_KEY — 后端无法生成建议。";
    if (kind === "suggestion_failed") return "AI 生成失败，请重试。";
    if (kind === "invalid_suggestion_request") return "请求无效。";
    return `请求失败（${err.status}）。`;
  }
  return `请求失败：${err instanceof Error ? err.message : String(err)}`;
}
