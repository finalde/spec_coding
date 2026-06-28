/** Schema-driven parsing / serializing for prompt code-block bodies.
 *
 * Prompt code blocks follow a recognizable convention: a sequence of
 * `<label>: <value>` lines (label may contain CJK + slashes, value may be a
 * single line or wrap onto a few continuation lines). The structured editor
 * (PromptStructuredEditor.tsx) renders each label/value pair as a form
 * field whose widget is chosen by `fieldWidget(label)`:
 *
 *   - dropdown: enum-typed fields (时长, 比例, 节奏, ...)
 *   - textarea: long-value fields (动作, 台词 / 字幕, ...)
 *   - input:    everything else
 *
 * Free-form lines (lines that don't match `^<label>:`) are preserved
 * verbatim and rendered as a single "其他内容" textarea below the labelled
 * fields, so reference-handle headers, blank separators, and ad-hoc notes
 * survive a round-trip without being moved or mutated.
 */

export type FieldWidget = "input" | "textarea" | "dropdown" | "multiselect" | "select";

/** Block kind for a shot file's three canonical prompt code blocks. `null`
 *  for any other fenced block (scene archive / character bible / actor /
 *  voice), which keeps the parse-only behavior. */
export type BlockKind = "start" | "end" | "video";

export interface FieldDef {
  /** Canonical label as it appears in the prompt (with full-width or
   *  half-width colon as authored). */
  label: string;
  /** Multi-line value text, possibly empty. Trailing newlines stripped. */
  value: string;
  /** Source-order index — used to preserve ordering on serialization. */
  order: number;
}

export interface ParsedPrompt {
  /** Labelled fields in source order. */
  fields: FieldDef[];
  /** Lines that didn't match the label pattern (e.g. reference-handle
   *  header, blank lines, prose). Joined back as `freeform` on serialize. */
  freeform: string;
  /** Where the freeform block sat relative to the fields. "before" =
   *  freeform lines appeared before the first labelled field (the common
   *  case — the reference-handle header is the freeform prefix). "after"
   *  is unused for now but reserved. */
  freeformPosition: "before" | "after";
}

const _LABEL_LINE_RE = /^([一-鿿A-Za-z_/ ]{1,20}?)\s*[:：]\s*(.*)$/;

/** Heuristic: a "field-label" line is one whose label is a short CJK / ASCII
 *  word followed by `:` or `：`. We require the label to be ≤ 20 chars and
 *  not contain weird characters. */
function _isLabelLine(line: string): { label: string; valueStart: string } | null {
  const m = _LABEL_LINE_RE.exec(line);
  if (!m) return null;
  const label = m[1].trim();
  if (!label) return null;
  // Reject lines that look like reference-handle headers
  // (`<X>請參考: ...` or `<scene>:<scene>_handle`).
  if (label.endsWith("請參考") || label.includes("請參考")) return null;
  return { label, valueStart: m[2] };
}

export function parsePrompt(body: string): ParsedPrompt {
  const lines = body.split("\n");
  // First pass: find where labelled fields start. Everything before the
  // first labelled field is "freeform prefix" (reference handles + blank).
  let firstFieldIdx = -1;
  for (let i = 0; i < lines.length; i++) {
    if (_isLabelLine(lines[i])) {
      firstFieldIdx = i;
      break;
    }
  }
  if (firstFieldIdx === -1) {
    // No labelled fields — return everything as freeform.
    return { fields: [], freeform: body.replace(/\n+$/, ""), freeformPosition: "before" };
  }
  const freeformLines = lines.slice(0, firstFieldIdx);
  const fieldLines = lines.slice(firstFieldIdx);

  const fields: FieldDef[] = [];
  let current: FieldDef | null = null;
  let order = 0;
  for (const raw of fieldLines) {
    const head = _isLabelLine(raw);
    if (head) {
      if (current) fields.push(current);
      current = {
        label: head.label,
        value: head.valueStart,
        order: order++,
      };
    } else {
      // Continuation line.
      if (current) {
        current.value = current.value === "" ? raw : current.value + "\n" + raw;
      } else {
        freeformLines.push(raw);
      }
    }
  }
  if (current) fields.push(current);

  // Trim trailing blank lines off each value.
  for (const f of fields) {
    f.value = f.value.replace(/\n+$/, "");
  }

  return {
    fields,
    freeform: freeformLines.join("\n").replace(/\n+$/, ""),
    freeformPosition: "before",
  };
}

export function serializePrompt(p: ParsedPrompt): string {
  const fieldLines = p.fields
    .slice()
    .sort((a, b) => a.order - b.order)
    .map((f) => {
      const vlines = f.value.split("\n");
      // Field head: `label: <first line of value>`.
      // Continuation lines: re-emit as-is (preserving their leading indent).
      const head = `${f.label}: ${vlines[0] ?? ""}`;
      return [head, ...vlines.slice(1)].join("\n");
    })
    .join("\n\n");
  if (p.freeform) {
    return p.freeform + "\n\n" + fieldLines;
  }
  return fieldLines;
}

// ---------------------------------------------------------------------------
// Widget hints — which field labels render as which widget type.
// ---------------------------------------------------------------------------

const _DROPDOWN_OPTIONS: Record<string, string[]> = {
  时长: ["3s", "4s", "5s", "6s", "7s", "8s", "10s", "12s", "15s"],
  比例: ["9:16", "16:9", "1:1", "4:3", "3:4"],
  节奏: ["慢", "中等", "快", "缓慢", "顿挫", "急促"],
};

const _TEXTAREA_LABELS = new Set([
  "动作",
  "台词",
  "台词 / 字幕",
  "光线/色调",
  "光线 / 色调",
  "渲染样式",
  "镜头",
  "运镜",
  "音频",
  "角色姿态",
  "位置/构图",
]);

/** Labels rendered as a multi-select (checkbox group) whose options are the
 *  drama's characters, injected by the caller. */
const _MULTISELECT_LABELS = new Set(["人物", "角色"]);
/** Labels rendered as a single-select picker whose options are the drama's
 *  scenes, injected by the caller. */
const _SELECT_LABELS = new Set(["场景", "場景"]);

function _norm(label: string): string {
  return label.replace(/\s+/g, "");
}

export function fieldWidget(label: string): FieldWidget {
  const normalized = _norm(label);
  for (const k of _MULTISELECT_LABELS) {
    if (normalized === _norm(k)) return "multiselect";
  }
  for (const k of _SELECT_LABELS) {
    if (normalized === _norm(k)) return "select";
  }
  for (const k of Object.keys(_DROPDOWN_OPTIONS)) {
    if (normalized === _norm(k)) return "dropdown";
  }
  for (const k of _TEXTAREA_LABELS) {
    if (normalized === _norm(k)) return "textarea";
  }
  return "input";
}

// ---------------------------------------------------------------------------
// Multi-select value (de)serialization. A multi-select field stores its value
// as a single `label: a、b、c` line; the widget edits the list, we round-trip
// through 、-joined text so serializePrompt stays line-based and unchanged.
// ---------------------------------------------------------------------------

export function splitMulti(value: string): string[] {
  return value
    .split(/[、,，\s]+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

export function joinMulti(items: string[]): string {
  return items.map((s) => s.trim()).filter((s) => s.length > 0).join("、");
}

// ---------------------------------------------------------------------------
// Canonical block schemas — the fixed, guaranteed field set per shot block.
// Editing a block merges these in (missing fields appended empty) so 人物 /
// 场景 / etc. always appear regardless of what the file currently contains.
// ---------------------------------------------------------------------------

const _FRAME_FIELDS: string[] = ["角色姿态", "位置/构图", "表情", "道具"];
const _VIDEO_FIELDS: string[] = [
  "人物",
  "场景",
  "镜头",
  "动作",
  "台词 / 字幕",
  "光线 / 色调",
  "节奏",
  "渲染样式",
  "比例",
  "时长",
];

const _CANONICAL: Record<BlockKind, string[]> = {
  start: _FRAME_FIELDS,
  end: _FRAME_FIELDS,
  video: _VIDEO_FIELDS,
};

/** Classify a `## ` heading line into one of the three shot block kinds, or
 *  null if it isn't a recognized prompt block heading. */
export function blockKindFromHeading(heading: string): BlockKind | null {
  const h = heading.replace(/^#+\s*/, "");
  if (h.includes("起始帧")) return "start";
  if (h.includes("结束帧")) return "end";
  if (h.startsWith("视频") || h.includes("视频 prompt") || h.includes("视频prompt")) return "video";
  return null;
}

/** Merge parsed fields with the canonical schema for `kind`. Canonical fields
 *  come first in canonical order (reusing the parsed value when present,
 *  matched whitespace-insensitively; empty otherwise), then any extra parsed
 *  fields that aren't part of the schema, in their original order. `freeform`
 *  is preserved. When `kind` is null, returns `parsed` unchanged. */
export function mergeWithCanonical(parsed: ParsedPrompt, kind: BlockKind | null): ParsedPrompt {
  if (kind === null) return parsed;
  const canonical = _CANONICAL[kind];
  const byNorm = new Map<string, FieldDef>();
  for (const f of parsed.fields) byNorm.set(_norm(f.label), f);

  const merged: FieldDef[] = [];
  let order = 0;
  const usedNorms = new Set<string>();
  for (const label of canonical) {
    const existing = byNorm.get(_norm(label));
    usedNorms.add(_norm(label));
    merged.push({ label, value: existing ? existing.value : "", order: order++ });
  }
  for (const f of parsed.fields) {
    if (usedNorms.has(_norm(f.label))) continue;
    merged.push({ label: f.label, value: f.value, order: order++ });
  }
  return { ...parsed, fields: merged };
}

export function dropdownOptions(label: string): string[] {
  const normalized = label.replace(/\s+/g, "");
  for (const [k, v] of Object.entries(_DROPDOWN_OPTIONS)) {
    if (normalized === k.replace(/\s+/g, "")) return v;
  }
  return [];
}
