/** ActorView: dedicated read-only view for actor sidecar markdown
 * (`ai_videos/_actors/actor_NNNN/actor_NNNN.md`).
 *
 * - follow-up 034: initial face / metadata / prompt rendering.
 * - follow-up 036: header 🗑 delete button (collapsed-leaf sidebar entry point).
 * - follow-up 043: assignments section + drama/role dropdown form; delete
 *   disabled when assignments exist (server-enforced via 409).
 */
import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  castingAssign,
  castingUnassign,
  deleteActor,
  fetchActorAssignments,
  mediaUrl,
  putFile,
  type ActorAssignment,
} from "../api";
import { extractDramas, type DramaChoice } from "../lib/dramas";
import { findAllFencedCode, replaceFencedCodeAt } from "../lib/promptEdit";
import { ApiError } from "../types";
import type { FileResult, TreeNode } from "../types";

const IMG_EXTS = [".jpg", ".jpeg", ".png", ".webp"];

export interface ActorViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
  tree: TreeNode | null;
  onSaved?: () => void;
}

interface ParsedActorPrompt {
  /** Trimmed body of this fenced code block. */
  body: string;
  /** Block index in source order (0-indexed), used by replaceFencedCodeAt for save. */
  blockIndex: number;
  /** Heading text immediately preceding this code block (e.g. "生成 prompt (face shot)"). */
  heading: string;
}

interface ParsedActor {
  fields: Array<{ key: string; value: string }>;
  prompts: ParsedActorPrompt[];
}

export function ActorView({ primaryFile, primaryPath, knownPaths, tree, onSaved }: ActorViewProps): JSX.Element {
  const navigate = useNavigate();
  const parsed = useMemo<ParsedActor>(() => parseActorMd(primaryFile.content), [primaryFile.content]);
  const facePath = useMemo<string | null>(() => findFaceImage(primaryPath, knownPaths), [primaryPath, knownPaths]);
  const actorId = useMemo<string>(() => deriveActorId(primaryPath), [primaryPath]);
  const dramas = useMemo<DramaChoice[]>(() => extractDramas(tree), [tree]);

  const [deleting, setDeleting] = useState<boolean>(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  const [assignments, setAssignments] = useState<ActorAssignment[]>([]);
  const [assignLoading, setAssignLoading] = useState<boolean>(false);
  const [assignError, setAssignError] = useState<string | null>(null);
  const [unassigning, setUnassigning] = useState<string | null>(null);
  const [formOpen, setFormOpen] = useState<boolean>(false);

  const loadAssignments = useCallback(async (): Promise<void> => {
    setAssignLoading(true);
    setAssignError(null);
    try {
      const result = await fetchActorAssignments(actorId);
      setAssignments(result.assignments);
    } catch (err) {
      setAssignError(formatError(err));
    } finally {
      setAssignLoading(false);
    }
  }, [actorId]);

  useEffect(() => { void loadAssignments(); }, [loadAssignments]);

  const onDelete = async (): Promise<void> => {
    if (deleting) return;
    const ok = window.confirm(
      `Delete ${actorId}? Moves folder to _deleted/_actors/. Refused if any role is currently assigned.`,
    );
    if (!ok) return;
    setDeleting(true);
    setDeleteError(null);
    try {
      await deleteActor(actorId);
      if (onSaved) onSaved();
      navigate("/");
    } catch (err) {
      setDeleteError(formatError(err));
    } finally {
      setDeleting(false);
    }
  };

  const onUnassign = async (a: ActorAssignment): Promise<void> => {
    const key = `${a.drama}/${a.role}`;
    if (unassigning) return;
    setUnassigning(key);
    setAssignError(null);
    try {
      await castingUnassign(`ai_videos/${a.drama}`, a.role);
      if (onSaved) onSaved();
      await loadAssignments();
    } catch (err) {
      setAssignError(`取消分配失败 (${key}): ${formatError(err)}`);
    } finally {
      setUnassigning(null);
    }
  };

  const onAssigned = async (): Promise<void> => {
    setFormOpen(false);
    if (onSaved) onSaved();
    await loadAssignments();
  };

  const deleteDisabledReason: string | null = assignments.length > 0
    ? `actor 当前已分配到 ${assignments.length} 个角色，无法删除（请先取消所有分配）`
    : null;

  return (
    <div className="actor-view">
      <header className="actor-view-header">
        <h2 className="actor-view-title">{actorId}</h2>
        <button
          type="button"
          className="actor-view-delete-btn"
          onClick={onDelete}
          disabled={deleting || deleteDisabledReason !== null}
          aria-label={`软删除 ${actorId}`}
          title={deleteDisabledReason ?? "软删除 actor — 移到 _deleted/_actors/"}
        >
          {deleting ? "删除中…" : "🗑 删除"}
        </button>
      </header>
      {deleteError ? (
        <div role="alert" className="actor-view-delete-error">{deleteError}</div>
      ) : null}

      <div className="actor-view-body">
        <section className="actor-view-image-pane" aria-label="Actor face">
          {facePath ? (
            <img src={mediaUrl(facePath)} alt={`${actorId} face`} className="actor-view-image" />
          ) : (
            <div className="actor-view-image-missing">尚未生成 face 图片</div>
          )}
        </section>

        <section className="actor-view-meta-pane" aria-label="Actor attributes">
          <h3 className="actor-view-section-title">属性</h3>
          {parsed.fields.length > 0 ? (
            <dl className="actor-view-meta">
              {parsed.fields.map((f) => (
                <div key={f.key} className="actor-view-meta-row">
                  <dt>{f.key}</dt>
                  <dd>{f.value}</dd>
                </div>
              ))}
            </dl>
          ) : (
            <div className="muted">无元数据</div>
          )}

          {parsed.prompts.length > 0 ? (
            <>
              {parsed.prompts.map((p) => (
                <ActorPromptCard
                  key={p.blockIndex}
                  prompt={p}
                  fileContent={primaryFile.content}
                  filePath={primaryPath}
                  mtimeHttp={primaryFile.mtime_http}
                  onSaved={onSaved}
                />
              ))}
            </>
          ) : null}
        </section>
      </div>

      <section className="actor-view-assignments" aria-label="Role assignments">
        <h3 className="actor-view-section-title">
          🎬 角色分配 {assignLoading ? "(加载中…)" : `(${assignments.length})`}
        </h3>
        {assignError ? (
          <div role="alert" className="actor-view-delete-error">{assignError}</div>
        ) : null}
        {assignments.length === 0 && !assignLoading ? (
          <p className="muted">尚未分配到任何角色</p>
        ) : (
          <ul className="actor-view-assignment-list">
            {assignments.map((a) => {
              const key = `${a.drama}/${a.role}`;
              const isUnassigningThis = unassigning === key;
              return (
                <li key={key} className="actor-view-assignment-row">
                  <span className="actor-view-assignment-drama">{a.drama}</span>
                  <span className="actor-view-assignment-sep">/</span>
                  <span className="actor-view-assignment-role">{a.role}</span>
                  {!a.character_folder_exists ? (
                    <span className="actor-view-assignment-warn" title="角色 folder 不存在 — casting.md 仍有此条记录">⚠</span>
                  ) : null}
                  {a.notes ? (
                    <span className="actor-view-assignment-notes">— {a.notes}</span>
                  ) : null}
                  <button
                    type="button"
                    className="actor-view-unassign-btn"
                    onClick={() => void onUnassign(a)}
                    disabled={unassigning !== null}
                    aria-label={`取消分配 ${key}`}
                  >
                    {isUnassigningThis ? "取消中…" : "✕ 取消"}
                  </button>
                </li>
              );
            })}
          </ul>
        )}
        {formOpen ? (
          <AssignForm
            actorId={actorId}
            dramas={dramas}
            existing={assignments}
            onClose={() => setFormOpen(false)}
            onAssigned={() => void onAssigned()}
          />
        ) : (
          <button
            type="button"
            className="actor-view-assign-btn"
            onClick={() => setFormOpen(true)}
            disabled={dramas.length === 0}
            title={dramas.length === 0 ? "ai_videos/ 下没有 drama 可分配" : "添加新的角色分配"}
          >
            ＋ 添加分配
          </button>
        )}
      </section>
    </div>
  );
}

interface AssignFormProps {
  actorId: string;
  dramas: DramaChoice[];
  existing: ActorAssignment[];
  onClose: () => void;
  onAssigned: () => void;
}

function AssignForm({ actorId, dramas, existing, onClose, onAssigned }: AssignFormProps): JSX.Element {
  const [dramaPath, setDramaPath] = useState<string>(dramas[0]?.path ?? "");
  const currentDrama = useMemo(() => dramas.find((d) => d.path === dramaPath) ?? dramas[0] ?? null, [dramaPath, dramas]);
  const characters = currentDrama?.characters ?? [];
  const [role, setRole] = useState<string>(characters[0] ?? "");
  const [notes, setNotes] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { setRole(characters[0] ?? ""); }, [characters]);

  const alreadyAssignedHere = useMemo<boolean>(() => {
    if (!currentDrama || !role) return false;
    return existing.some((a) => a.drama === currentDrama.name && a.role === role);
  }, [currentDrama, role, existing]);

  const onSubmit = async (): Promise<void> => {
    if (!currentDrama || !role || busy) return;
    setBusy(true);
    setError(null);
    try {
      await castingAssign(currentDrama.path, role, actorId, notes);
      onAssigned();
    } catch (err) {
      setError(formatError(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="actor-view-assign-form" role="group" aria-label="新分配角色">
      <div className="form-row">
        <label className="form-field">
          <span className="form-field-label">短剧</span>
          <select value={dramaPath} onChange={(e) => setDramaPath(e.target.value)} disabled={busy}>
            {dramas.map((d) => (
              <option key={d.path} value={d.path}>{d.name}</option>
            ))}
          </select>
        </label>
        <label className="form-field">
          <span className="form-field-label">角色</span>
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
      <label className="form-field">
        <span className="form-field-label">备注 (可选)</span>
        <textarea
          rows={2}
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          disabled={busy}
          maxLength={500}
        />
      </label>
      {alreadyAssignedHere ? (
        <p className="muted">⚠ 该角色已分配给本 actor — 重复提交会保留原 row（upsert）</p>
      ) : null}
      {error ? (
        <div role="alert" className="actor-view-delete-error">{error}</div>
      ) : null}
      <div className="form-actions">
        <button
          type="button"
          className="actor-view-assign-btn"
          onClick={() => void onSubmit()}
          disabled={busy || !currentDrama || !role}
        >
          {busy ? "分配中…" : "确认分配"}
        </button>
        <button type="button" className="actor-view-cancel-btn" onClick={onClose} disabled={busy}>
          取消
        </button>
      </div>
    </div>
  );
}

interface ActorPromptCardProps {
  prompt: ParsedActorPrompt;
  fileContent: string;
  filePath: string;
  mtimeHttp: string;
  onSaved?: () => void;
}

function ActorPromptCard({ prompt, fileContent, filePath, mtimeHttp, onSaved }: ActorPromptCardProps): JSX.Element {
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editBuffer, setEditBuffer] = useState<string>("");
  const [editSaving, setEditSaving] = useState<boolean>(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [copied, setCopied] = useState<boolean>(false);

  const onCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(prompt.body);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1500);
    } catch {
      setCopied(false);
    }
  }, [prompt.body]);

  const onEditStart = useCallback(() => {
    setEditBuffer(prompt.body);
    setEditError(null);
    setEditMode(true);
  }, [prompt.body]);

  const onEditCancel = useCallback(() => {
    setEditMode(false);
    setEditBuffer("");
    setEditError(null);
  }, []);

  const onEditSave = useCallback(async () => {
    if (editSaving) return;
    setEditSaving(true);
    setEditError(null);
    try {
      const newContent = replaceFencedCodeAt(fileContent, prompt.blockIndex, editBuffer);
      await putFile(filePath, newContent, { ifUnmodifiedSince: mtimeHttp });
      setEditMode(false);
      setEditBuffer("");
      if (onSaved) onSaved();
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setEditError("文件已被外部修改，请刷新后重试（你的编辑保留在 textarea 中）");
      } else {
        setEditError(formatError(err));
      }
    } finally {
      setEditSaving(false);
    }
  }, [editBuffer, editSaving, fileContent, filePath, mtimeHttp, onSaved, prompt.blockIndex]);

  return (
    <>
      <h3 className="actor-view-section-title">{prompt.heading}</h3>
      <div className={`actor-view-prompt-card${editMode ? " actor-view-prompt-card-editing" : ""}`}>
        <div className="actor-view-prompt-actions">
          {!editMode ? (
            <>
              <button
                type="button"
                className="actor-view-copy-btn"
                onClick={() => void onCopy()}
                aria-label="Copy prompt to clipboard"
                title="Copy"
              >
                {copied ? "✓ Copied" : "📋 Copy"}
              </button>
              <button
                type="button"
                className="actor-view-copy-btn"
                onClick={onEditStart}
                title="直接编辑此 prompt 内容（不影响文件其他部分）"
              >
                ✏ Edit
              </button>
            </>
          ) : (
            <>
              <button
                type="button"
                className="actor-view-copy-btn actor-view-prompt-save-btn"
                onClick={() => void onEditSave()}
                disabled={editSaving}
              >
                {editSaving ? "保存中…" : "✓ Save"}
              </button>
              <button
                type="button"
                className="actor-view-copy-btn"
                onClick={onEditCancel}
                disabled={editSaving}
              >
                ✕ Cancel
              </button>
            </>
          )}
        </div>
        {!editMode ? (
          <pre className="actor-view-prompt-text">{prompt.body}</pre>
        ) : (
          <textarea
            className="actor-view-prompt-textarea"
            value={editBuffer}
            onChange={(e) => setEditBuffer(e.target.value)}
            spellCheck={false}
            rows={Math.min(40, Math.max(10, editBuffer.split("\n").length + 1))}
            disabled={editSaving}
          />
        )}
        {editError ? (
          <div role="alert" className="actor-view-delete-error">{editError}</div>
        ) : null}
      </div>
    </>
  );
}

function formatError(err: unknown): string {
  if (err instanceof ApiError) {
    const kind = err.detail?.kind;
    if (kind === "actor_is_assigned") {
      const list = (err.detail?.assignments as ActorAssignment[] | undefined) ?? [];
      const summary = list.map((a) => `${a.drama}/${a.role}`).join(", ");
      return `actor 已分配到角色，无法删除：${summary}`;
    }
    return `请求失败: ${kind ?? err.status}`;
  }
  return err instanceof Error ? err.message : String(err);
}

function deriveActorId(path: string): string {
  const base = path.split("/").pop() ?? path;
  return base.replace(/\.md$/i, "");
}

function findFaceImage(mdPath: string, knownPaths: string[]): string | null {
  const lastSlash = mdPath.lastIndexOf("/");
  if (lastSlash < 0) return null;
  const folder = mdPath.slice(0, lastSlash + 1);
  const candidates = knownPaths.filter((p) => {
    if (!p.startsWith(folder)) return false;
    const tail = p.slice(folder.length);
    if (tail.includes("/")) return false;
    const lower = tail.toLowerCase();
    return IMG_EXTS.some((ext) => lower.endsWith(ext));
  });
  if (candidates.length === 0) return null;
  candidates.sort();
  return candidates[0];
}

function parseActorMd(content: string): ParsedActor {
  return { fields: parseFields(content), prompts: parsePrompts(content) };
}

function parsePrompts(content: string): ParsedActorPrompt[] {
  const blocks = findAllFencedCode(content);
  return blocks.map((b, i) => ({
    body: b.body.replace(/\n+$/, ""),
    blockIndex: i,
    heading: nearestHeadingBefore(content, b.start),
  }));
}

/** Walk backwards from `pos` and return the text of the nearest H1/H2/H3 above. */
function nearestHeadingBefore(content: string, pos: number): string {
  const before = content.slice(0, pos);
  const m = /^(#{1,3})\s+(.+)$/gm;
  let last: string = "生成 prompt";
  let r: RegExpExecArray | null;
  while ((r = m.exec(before)) !== null) {
    last = r[2].trim();
  }
  return last;
}

function parseFields(content: string): Array<{ key: string; value: string }> {
  const out: Array<{ key: string; value: string }> = [];
  const lines = content.split(/\r?\n/);
  let inTable = false;
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("|")) {
      if (inTable) break;
      continue;
    }
    const cells = trimmed.split("|").slice(1, -1).map((c) => c.trim());
    if (cells.length < 2) continue;
    if (cells[0] === "字段" || cells[0] === "field" || /^[-:\s]+$/.test(cells[0])) {
      inTable = true;
      continue;
    }
    inTable = true;
    if (cells[0]) out.push({ key: cells[0], value: cells[1] ?? "" });
  }
  return out;
}

