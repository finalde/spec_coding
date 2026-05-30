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
import { useMemo, useState } from "react";
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
}: PromptStructuredEditorProps): JSX.Element {
  const initialParsed = useMemo<ParsedPrompt>(
    () => mergeWithCanonical(parsePrompt(initialBody), blockKind),
    [initialBody, blockKind],
  );
  const [parsed, setParsed] = useState<ParsedPrompt>(initialParsed);
  const [rawBuffer, setRawBuffer] = useState<string>(initialBody);
  const [mode, setMode] = useState<Mode>(initialParsed.fields.length > 0 ? "structured" : "raw");

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

interface StructuredFormProps {
  parsed: ParsedPrompt;
  onChangeField: (order: number, value: string) => void;
  disabled: boolean;
  characterOptions: string[];
  sceneOptions: string[];
}

function StructuredForm({
  parsed,
  onChangeField,
  disabled,
  characterOptions,
  sceneOptions,
}: StructuredFormProps): JSX.Element {
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
}

function FieldRow({ field, onChange, disabled, characterOptions, sceneOptions }: FieldRowProps): JSX.Element {
  const widget = fieldWidget(field.label);
  return (
    <label className="prompt-editor-field">
      <span className="prompt-editor-field-label">{field.label}</span>
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
