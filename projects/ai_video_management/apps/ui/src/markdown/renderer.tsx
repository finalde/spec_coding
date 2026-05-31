import { Children, createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import { useNavigate } from "react-router-dom";
import { resolveLink } from "../lib/linkResolver";
import { BrokenLink } from "../components/BrokenLink";
import { findAllFencedCode, replaceFencedCodeAt } from "../lib/promptEdit";
import { blockKindFromHeading, type BlockKind } from "../lib/promptSchema";
import { putFile } from "../api";
import { ApiError } from "../types";
import { PromptStructuredEditor } from "../components/PromptStructuredEditor";

export interface RendererProps {
  content: string;
  currentPath: string;
  knownPaths: string[];
  /** When set, every fenced code block under `currentPath` gets an inline ✏ Edit button
   * that replaces just that block (not the whole file) via PUT /api/file with concurrency.
   * Typically set true for files under `ai_videos/`. Requires `mtimeHttp` + `onSaved`. */
  editEnabled?: boolean;
  /** `mtime_http` of the loaded file — used for If-Unmodified-Since concurrency guard. */
  mtimeHttp?: string;
  /** Called after a successful per-block save so the parent can refetch + refresh `content`. */
  onSaved?: () => void;
  /** Character display names for the 人物 multi-select in shot prompt blocks. */
  characterOptions?: string[];
  /** Scene display names for the 场景 picker in shot prompt blocks. */
  sceneOptions?: string[];
}

/** For each fenced block (by source-order index), classify it by the nearest
 *  preceding `## ` heading into a shot block kind, or null. */
function computeIndexToKind(content: string): Map<number, BlockKind | null> {
  const blocks = findAllFencedCode(content);
  const headings: { pos: number; text: string }[] = [];
  const headingRe = /^#{1,6}[ \t]+(.+)$/gm;
  let hm: RegExpExecArray | null;
  while ((hm = headingRe.exec(content)) !== null) {
    headings.push({ pos: hm.index, text: hm[1] });
  }
  const out = new Map<number, BlockKind | null>();
  blocks.forEach((b, i) => {
    let nearest: string | null = null;
    for (const h of headings) {
      if (h.pos < b.start) nearest = h.text;
      else break;
    }
    out.set(i, nearest ? blockKindFromHeading(nearest) : null);
  });
  return out;
}

/** Pre-render regex pass wrapping locked-descriptor blocks in <span class="locked-block">.
 * Pattern is GENERAL across characters: `【.+ · .+ · 锁定描述符 v\d+】 ... 禁用 ...。`
 */
const LOCKED_BLOCK_RE = /(【.+? · .+? · 锁定描述符 v\d+】[\s\S]*?禁用 [^\n]*?。)/g;

/** Pre-render regex pass wrapping `{ref_xxx}` placeholders in <span class="ref-placeholder">.
 * Match Chinese / ASCII identifier inside {ref_...}. Skip any inside fenced code blocks
 * by leveraging a state-machine pass.
 */
const REF_PLACEHOLDER_RE = /\{ref_([一-鿿\w-]+)\}/g;

function applyLockedBlockPill(source: string): string {
  return source.replace(LOCKED_BLOCK_RE, (m) => {
    return `<span class="locked-block" title="byte-equality contract — see characters/main.md" aria-describedby="locked-block-desc">${m}</span>`;
  });
}

/** Apply ref-placeholder pill only OUTSIDE fenced code blocks.
 * Inside code fences (the prompt body), placeholders MUST stay raw `{ref_xxx}` so the copy
 * button copies verbatim text. The reference table above each code fence (rendered as markdown
 * outside fences) gets the visual pill for review.
 */
function applyRefPlaceholderPill(source: string): string {
  const segments = source.split(/(```[\s\S]*?```)/g);
  return segments
    .map((seg, i) => {
      if (i % 2 === 1) return seg; // odd index = fenced code block, skip
      return seg.replace(REF_PLACEHOLDER_RE, (_, name) => {
        return `<span class="ref-placeholder" title="reference placeholder — replace with actual reference path when pasting to model">{ref_${name}}</span>`;
      });
    })
    .join("");
}

/** Field labels in prompt body that get highlighted as markdown-style key headers.
 * Per rule #12.4 v4 / follow-up 013 visual contract.
 */
const FIELD_LABEL_RE = /^(角色|场景|镜头|动作|台词 ?\/ ?字幕|节奏|光线 ?\/ ?色调|渲染样式|比例|时长|负向|主体定义|姿态(（[^）]*）)?|参考|画幅)([:：])(\s*)/;

/** Walk a React node tree to extract its plain text content (used to render highlighted spans
 * while preserving the original text shape for `innerText` clipboard reads).
 */
function extractText(node: ReactNode): string {
  if (node === null || node === undefined || typeof node === "boolean") return "";
  if (typeof node === "string" || typeof node === "number") return String(node);
  if (Array.isArray(node)) return node.map(extractText).join("");
  if (typeof node === "object" && "props" in node) {
    return extractText((node as { props: { children?: ReactNode } }).props.children);
  }
  return "";
}

/** Render plain code-block text with per-line field-label highlighting.
 * The output is a sequence of React nodes whose innerText equals the original plain text,
 * so the copy button still reads cleanly via `preRef.current.innerText`.
 */
function renderHighlightedLines(text: string): ReactNode {
  const lines = text.split("\n");
  return lines.map((line, idx) => {
    const m = line.match(FIELD_LABEL_RE);
    let content: ReactNode;
    if (m) {
      const label = m[1];
      const colon = m[m.length - 2];
      const spaces = m[m.length - 1] ?? "";
      const rest = line.slice(m[0].length);
      content = (
        <>
          <span className="field-label">{label}</span>
          {colon}
          {spaces}
          {rest}
        </>
      );
    } else {
      content = line;
    }
    return (
      <span key={idx}>
        {content}
        {idx < lines.length - 1 ? "\n" : null}
      </span>
    );
  });
}

/** Highlight novel-prose quotes: dialogue (「…」 or "…") and inner monologue
 * (『…』, added during the prose-marking sweep). Applied to <p> text only, so
 * it hits 小说原文 / Chapter excerpt paragraphs + my_novel chapters but NOT
 * shot-context <li> metadata or fenced prompt blocks. Per follow-up
 * "把小说原文的对话和内心独白都标注出来".
 */
const PROSE_QUOTE_RE = /「[^」]*」|『[^』]*』|"[^"]*"/g;

function highlightProseString(text: string, keyPrefix: string): ReactNode[] {
  const out: ReactNode[] = [];
  const re = new RegExp(PROSE_QUOTE_RE.source, "g");
  let last = 0;
  let i = 0;
  let m: RegExpExecArray | null;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(text.slice(last, m.index));
    const seg = m[0];
    const cls = seg.charAt(0) === "『" ? "prose-monologue" : "prose-dialogue";
    out.push(
      <span key={`${keyPrefix}-${i++}`} className={cls}>
        {seg}
      </span>,
    );
    last = m.index + seg.length;
  }
  if (last < text.length) out.push(text.slice(last));
  return out;
}

function highlightProseChildren(children: ReactNode): ReactNode {
  return Children.map(children, (child, idx) =>
    typeof child === "string" ? highlightProseString(child, `pq${idx}`) : child,
  );
}

interface EditPromptContextValue {
  editEnabled: boolean;
  currentPath: string;
  mtimeHttp: string | undefined;
  /** Body → first matching block index (0-indexed). Duplicate bodies resolve to first occurrence. */
  bodyToIndex: Map<string, number>;
  /** Current file content; refreshed by parent on save (so freshly-keyed lookups stay correct). */
  fileContent: string;
  /** Triggers parent refetch after a successful save. */
  onSaved: (() => void) | undefined;
  /** Block index → shot block kind (start/end/video) or null for non-shot blocks. */
  indexToKind: Map<number, BlockKind | null>;
  /** Character display names for the 人物 multi-select. */
  characterOptions: string[];
  /** Scene display names for the 场景 picker. */
  sceneOptions: string[];
}

const EditPromptContext = createContext<EditPromptContextValue | null>(null);

interface CopyableCodeProps {
  children: ReactNode;
}

function CopyableCode({ children }: CopyableCodeProps): JSX.Element {
  const [copied, setCopied] = useState(false);
  const preRef = useRef<HTMLPreElement>(null);

  // Extract the plain text of children, then re-render with field-label highlighting
  // (per rule #12.4 v4 / follow-up 013). Copy uses the raw `trimmedBody` below
  // (NOT innerText), so the copied prompt keeps whitespace/newlines verbatim.
  const plain = useMemo(() => extractText(children), [children]);
  const trimmedBody = useMemo(() => plain.replace(/\n+$/, ""), [plain]);
  const highlighted = useMemo(() => renderHighlightedLines(plain), [plain]);

  const ctx = useContext(EditPromptContext);
  // Resolve this block's index by matching its body text against the pre-computed map.
  const blockIndex = ctx ? (ctx.bodyToIndex.get(trimmedBody) ?? -1) : -1;
  const canEdit = ctx?.editEnabled === true && blockIndex >= 0 && ctx.mtimeHttp !== undefined;

  const [editing, setEditing] = useState(false);
  const [buffer, setBuffer] = useState<string>("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCopy = useCallback(async () => {
    // Copy the code block's EXACT source text — every space and newline
    // preserved verbatim. We deliberately do NOT read `preRef.innerText`:
    // innerText is layout-normalized and can collapse runs of whitespace /
    // alter newlines depending on CSS + the per-line <span> highlighting,
    // which garbles the prompt's structure for downstream models (observed:
    // Kling mis-reading speaker/section boundaries). `trimmedBody` is the
    // raw fenced-block body reconstructed from the source.
    const text = trimmedBody;
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      // clipboard API unavailable — graceful fallback: nothing to do
    }
  }, [trimmedBody]);

  const onEditStart = useCallback(() => {
    if (!canEdit) return;
    setBuffer(trimmedBody);
    setError(null);
    setEditing(true);
  }, [canEdit, trimmedBody]);

  const onEditCancel = useCallback(() => {
    setEditing(false);
    setBuffer("");
    setError(null);
  }, []);

  // Note: save semantics now live inline in the `if (editing)` branch so the
  // structured editor can hand the canonical body back without round-tripping
  // through our `buffer` state. See onStructuredSave below.

  if (editing) {
    // The structured editor owns its own state — wire its onSave callback
    // back to our onEditSave with the body the editor produced.
    const onStructuredSave = async (newBody: string): Promise<void> => {
      if (!ctx || !canEdit || saving) return;
      setSaving(true);
      setError(null);
      try {
        const newContent = replaceFencedCodeAt(ctx.fileContent, blockIndex, newBody);
        await putFile(ctx.currentPath, newContent, { ifUnmodifiedSince: ctx.mtimeHttp });
        setEditing(false);
        setBuffer("");
        ctx.onSaved?.();
      } catch (err) {
        if (err instanceof ApiError && err.status === 409) {
          setError("文件已被外部修改，请刷新后重试（你的编辑保留在 textarea 中）");
        } else if (err instanceof ApiError) {
          setError(`保存失败: ${err.detail?.kind ?? err.status}`);
        } else {
          setError(`保存失败: ${err instanceof Error ? err.message : String(err)}`);
        }
      } finally {
        setSaving(false);
      }
    };
    const kind = ctx?.indexToKind.get(blockIndex) ?? null;
    const kindLabel = kind === "start" ? "起始帧" : kind === "end" ? "结束帧" : kind === "video" ? "视频 prompt" : `prompt block #${blockIndex + 1}`;
    return (
      <div className="code-block-wrapper code-block-wrapper-editing">
        <PromptStructuredEditor
          initialBody={buffer}
          onSave={onStructuredSave}
          onCancel={onEditCancel}
          saving={saving}
          errorMessage={error}
          blockLabel={kindLabel}
          blockKind={kind}
          characterOptions={ctx?.characterOptions ?? []}
          sceneOptions={ctx?.sceneOptions ?? []}
          shotContext={ctx?.fileContent}
          currentPath={ctx?.currentPath}
        />
      </div>
    );
  }

  return (
    <div className="code-block-wrapper">
      <div className="code-block-actions">
        <button
          type="button"
          className={`copy-btn${copied ? " copied" : ""}`}
          onClick={handleCopy}
          aria-label={copied ? "已复制" : "复制 prompt"}
        >
          {copied ? "已复制 ✓" : "复制 Copy"}
        </button>
        {canEdit ? (
          <button
            type="button"
            className="copy-btn code-block-edit-btn"
            onClick={onEditStart}
            title="直接编辑此 prompt 代码块（不影响文件其他部分）"
            aria-label="Edit prompt block"
          >
            ✏ Edit
          </button>
        ) : null}
      </div>
      <pre ref={preRef}><code>{highlighted}</code></pre>
    </div>
  );
}

export function Renderer({
  content,
  currentPath,
  knownPaths,
  editEnabled,
  mtimeHttp,
  onSaved,
  characterOptions = [],
  sceneOptions = [],
}: RendererProps): JSX.Element {
  const navigate = useNavigate();
  const known = useMemo(() => new Set(knownPaths), [knownPaths]);
  const isKnown = (p: string): boolean => known.has(p);
  const processed = useMemo(() => applyRefPlaceholderPill(applyLockedBlockPill(content)), [content]);

  const blocks = useMemo(() => findAllFencedCode(content), [content]);
  const bodyToIndex = useMemo(() => {
    const m = new Map<string, number>();
    blocks.forEach((b, i) => {
      const key = b.body.replace(/\n+$/, "");
      if (!m.has(key)) m.set(key, i);
    });
    return m;
  }, [blocks]);

  const indexToKind = useMemo(() => computeIndexToKind(content), [content]);

  const ctxValue = useMemo<EditPromptContextValue>(() => ({
    editEnabled: editEnabled === true,
    currentPath,
    mtimeHttp,
    bodyToIndex,
    fileContent: content,
    onSaved,
    indexToKind,
    characterOptions,
    sceneOptions,
  }), [editEnabled, currentPath, mtimeHttp, bodyToIndex, content, onSaved, indexToKind, characterOptions, sceneOptions]);

  const hasFences = blocks.length > 0;
  return (
    <div className="markdown-view" lang="zh-Hans">
      <span id="locked-block-desc" className="visually-hidden">
        锁定描述符块 — byte-equality contract; do not edit
      </span>
      {editEnabled === true && hasFences ? (
        <div className="renderer-edit-hint" role="status">
          <strong>💡 编辑 prompt：</strong>
          每个 <code>```text</code> 代码块右上角都有一个 <span className="renderer-edit-hint-chip">✏ Edit</span> 按钮。
          点它进入<strong>结构化表单编辑</strong>（仅修改该 prompt 块，不影响其他段落）。
          整篇 markdown 的「编辑全文」按钮已隐藏，避免误开 page-level edit。
        </div>
      ) : null}
      <EditPromptContext.Provider value={ctxValue}>
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize, rehypeHighlight]}
          components={{
            a: ({ href, children, ...rest }) => {
              if (typeof href !== "string") return <span>{children}</span>;
              const resolved = resolveLink({ currentFile: currentPath, href, isKnown });
              if (resolved.kind === "external") return <a href={resolved.href} target="_blank" rel="noopener noreferrer" {...rest}>{children}</a>;
              if (resolved.kind === "anchor") return <a href={resolved.hash} {...rest}>{children}</a>;
              if (resolved.kind === "internal") {
                const target = `/file/${encodeURIComponent(resolved.path)}${resolved.hash ?? ""}`;
                return <a href={target} onClick={(e) => { e.preventDefault(); navigate(target); }}>{children}</a>;
              }
              return <BrokenLink href={resolved.href} title={resolved.title}>{children}</BrokenLink>;
            },
            pre: ({ children }) => <CopyableCode>{children}</CopyableCode>,
            p: ({ children, ...rest }) => <p {...rest}>{highlightProseChildren(children)}</p>,
          }}
        >
          {processed}
        </ReactMarkdown>
      </EditPromptContext.Provider>
    </div>
  );
}
