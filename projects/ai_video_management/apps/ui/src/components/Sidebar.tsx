import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteActor, deleteVoice, importFromDownloads } from "../api";
import { ApiError, type TreeNode } from "../types";
import { ActorPoolGenerator } from "./ActorPoolGenerator";
import { VoicePoolGenerator } from "./VoicePoolGenerator";
import { BgmPoolGenerator } from "./BgmPoolGenerator";

const ACTOR_ID_RE = /^actor_\d{4,}$/;
const VOICE_ID_RE = /^voice_\d{4,}$/;

export interface SidebarProps {
  tree: TreeNode | null;
  currentPath: string;
  onSelect: (path: string) => void;
  loadError?: string | null;
  onTreeReload?: () => void;
}

interface FlatNode { node: TreeNode; depth: number; parentPath: string | null; }

export function Sidebar({ tree, currentPath, onSelect, loadError, onTreeReload }: SidebarProps): JSX.Element {
  const navigate = useNavigate();
  const treeRef = useRef<HTMLDivElement>(null);
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [focusedPath, setFocusedPath] = useState<string | null>(null);
  const [renamingPath, setRenamingPath] = useState<string | null>(null);
  const [renameToast, setRenameToast] = useState<{ kind: "ok" | "err"; text: string } | null>(null);
  const [generatorOpen, setGeneratorOpen] = useState<boolean>(false);
  const [voiceGeneratorOpen, setVoiceGeneratorOpen] = useState<boolean>(false);
  const [bgmGeneratorOpen, setBgmGeneratorOpen] = useState<boolean>(false);
  const [deletingActorId, setDeletingActorId] = useState<string | null>(null);
  const [deletingVoiceId, setDeletingVoiceId] = useState<string | null>(null);

  const onRenameClick = useCallback(
    async (e: React.MouseEvent, dramaPath: string) => {
      e.stopPropagation();
      if (renamingPath) return;
      setRenamingPath(dramaPath);
      setRenameToast(null);
      try {
        const result = await importFromDownloads(dramaPath);
        const errorCount = result.errors.length + result.rename.errors.length;
        const summary =
          `已导入 ${result.moved.length} / 未分类 ${result.unmatched.length} ` +
          `/ 已重命名 ${result.rename.renamed.length} / 失败 ${errorCount}`;
        setRenameToast({ kind: errorCount > 0 ? "err" : "ok", text: summary });
        if (onTreeReload) onTreeReload();
      } catch (err) {
        const msg = err instanceof ApiError
          ? `导入失败: ${err.detail?.kind ?? err.status}`
          : `导入失败: ${err instanceof Error ? err.message : String(err)}`;
        setRenameToast({ kind: "err", text: msg });
      } finally {
        setRenamingPath(null);
      }
    },
    [onTreeReload, renamingPath],
  );

  const onActorDeleteClick = useCallback(
    async (e: React.MouseEvent, actorId: string) => {
      e.stopPropagation();
      if (deletingActorId) return;
      const ok = window.confirm(
        `Delete ${actorId}? Moves folder to _deleted/_actors/ and unassigns from all casting.md.`,
      );
      if (!ok) return;
      setDeletingActorId(actorId);
      setRenameToast(null);
      try {
        const result = await deleteActor(actorId);
        const refs = result.unassigned.length;
        const summary =
          refs > 0
            ? `已删除 ${actorId}（解除 ${refs} 个 casting 引用）`
            : `已删除 ${actorId}`;
        setRenameToast({ kind: "ok", text: summary });
        if (onTreeReload) onTreeReload();
      } catch (err) {
        const msg = err instanceof ApiError
          ? `删除失败: ${err.detail?.kind ?? err.status}`
          : `删除失败: ${err instanceof Error ? err.message : String(err)}`;
        setRenameToast({ kind: "err", text: msg });
      } finally {
        setDeletingActorId(null);
      }
    },
    [deletingActorId, onTreeReload],
  );

  const onVoiceDeleteClick = useCallback(
    async (e: React.MouseEvent, voiceId: string) => {
      e.stopPropagation();
      if (deletingVoiceId) return;
      const ok = window.confirm(
        `Delete ${voiceId}? Moves folder to _deleted/_voices/. Refuses if assigned.`,
      );
      if (!ok) return;
      setDeletingVoiceId(voiceId);
      setRenameToast(null);
      try {
        await deleteVoice(voiceId);
        setRenameToast({ kind: "ok", text: `已删除 ${voiceId}` });
        if (onTreeReload) onTreeReload();
      } catch (err) {
        const msg = err instanceof ApiError
          ? `删除失败: ${err.detail?.kind ?? err.status}`
          : `删除失败: ${err instanceof Error ? err.message : String(err)}`;
        setRenameToast({ kind: "err", text: msg });
      } finally {
        setDeletingVoiceId(null);
      }
    },
    [deletingVoiceId, onTreeReload],
  );

  useEffect(() => {
    if (!tree) return;
    const accum: Record<string, boolean> = {};
    const walk = (node: TreeNode): void => {
      if (node.type === "file" || node.type === "image" || node.type === "video" || node.type === "audio" || node.type === "actor" || node.type === "voice") return;
      if (node.path) accum[node.path] = false;
      for (const c of node.children ?? []) walk(c);
    };
    walk(tree);
    setExpanded((prev) => ({ ...accum, ...prev }));
  }, [tree]);

  useEffect(() => {
    if (!currentPath) return;
    const parts = currentPath.split("/").slice(0, -1);
    const accum: Record<string, boolean> = {};
    let acc = "";
    for (const p of parts) {
      acc = acc ? `${acc}/${p}` : p;
      accum[acc] = true;
    }
    setExpanded((prev) => ({ ...prev, ...accum }));
  }, [currentPath]);

  useEffect(() => {
    const handler = (event: KeyboardEvent): void => {
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && (event.key === "E" || event.key === "e")) {
        event.preventDefault();
        const root = treeRef.current;
        if (!root) return;
        const first = root.querySelector<HTMLElement>('[role="treeitem"]');
        if (first) {
          first.focus();
          const path = first.getAttribute("data-path");
          if (path) setFocusedPath(path);
        }
      }
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, []);

  const flat = useMemo<FlatNode[]>(() => {
    if (!tree) return [];
    const out: FlatNode[] = [];
    const walk = (node: TreeNode, depth: number, parentPath: string | null): void => {
      out.push({ node, depth, parentPath });
      const isOpen = depth === 0 ? true : expanded[node.path] === true;
      if (isOpen && node.children && node.children.length) {
        for (const child of node.children) walk(child, depth + 1, node.path);
      }
    };
    if (tree.type === "section" && (tree.path === "" || !tree.path)) {
      for (const top of tree.children ?? []) walk(top, 0, null);
    } else {
      walk(tree, 0, null);
    }
    return out;
  }, [tree, expanded]);

  const toggle = useCallback((path: string) => {
    setExpanded((prev) => ({ ...prev, [path]: !prev[path] }));
  }, []);

  const onCollapseAll = useCallback(() => {
    if (!tree) return;
    const accum: Record<string, boolean> = {};
    const walk = (node: TreeNode): void => {
      if (node.type === "file" || node.type === "image" || node.type === "video" || node.type === "audio" || node.type === "actor" || node.type === "voice") return;
      if (node.path) accum[node.path] = false;
      for (const c of node.children ?? []) walk(c);
    };
    walk(tree);
    setExpanded(accum);
  }, [tree]);

  const onItemKeyDown = (event: React.KeyboardEvent<HTMLDivElement>, item: FlatNode): void => {
    const items = flat;
    const index = items.findIndex((i) => i.node.path === item.node.path);
    const isLeaf = item.node.type === "file" || item.node.type === "image" || item.node.type === "video" || item.node.type === "audio" || (item.node.children ?? []).length === 0;
    const isOpen = expanded[item.node.path] === true;
    if (event.key === "ArrowDown") {
      event.preventDefault();
      const next = items[index + 1];
      if (next) focusByPath(treeRef.current, next.node.path, setFocusedPath);
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      const prev = items[index - 1];
      if (prev) focusByPath(treeRef.current, prev.node.path, setFocusedPath);
    } else if (event.key === "ArrowRight") {
      event.preventDefault();
      if (!isLeaf && !isOpen) toggle(item.node.path);
    } else if (event.key === "ArrowLeft") {
      event.preventDefault();
      if (!isLeaf && isOpen) toggle(item.node.path);
      else if (item.parentPath) focusByPath(treeRef.current, item.parentPath, setFocusedPath);
    } else if (event.key === "Enter" || event.key === " ") {
      event.preventDefault();
      if (item.node.type === "file" || item.node.type === "image" || item.node.type === "video" || item.node.type === "audio") onSelect(item.node.path);
      else toggle(item.node.path);
    }
  };

  if (loadError) {
    return (
      <nav className="sidebar" aria-label="File tree">
        <div role="alert" className="sidebar-error">Failed to load tree: {loadError}</div>
      </nav>
    );
  }
  if (!tree) {
    return (
      <nav className="sidebar" aria-label="File tree">
        <div className="sidebar-loading">Loading…</div>
      </nav>
    );
  }

  return (
    <nav className="sidebar" aria-label="File tree">
      <div className="sidebar-toolbar">
        <button
          type="button"
          className="sidebar-collapse-all"
          aria-label="折叠全部"
          title="折叠全部 · Collapse all folders"
          onClick={onCollapseAll}
        >
          ⊟
        </button>
      </div>
      {renameToast ? (
        <div
          role="status"
          aria-live="polite"
          className={`sidebar-toast sidebar-toast-${renameToast.kind}`}
        >
          {renameToast.text}
          <button
            type="button"
            className="sidebar-toast-dismiss"
            aria-label="关闭"
            onClick={() => setRenameToast(null)}
          >
            ×
          </button>
        </div>
      ) : null}
      <div ref={treeRef} role="tree" aria-label="File tree" className="tree">
        {flat.map((item) => {
          const isLeaf = item.node.type === "file" || item.node.type === "image" || item.node.type === "video" || item.node.type === "audio" || item.node.type === "actor" || item.node.type === "voice";
          const hasChildren = (item.node.children ?? []).length > 0;
          const isOpen = expanded[item.node.path] === true || item.depth === 0;
          const isActive = currentPath === item.node.path;
          const isFocused = focusedPath === item.node.path;
          const subType = item.node.project_meta?.sub_type;
          const dramaPathParts = item.node.path ? item.node.path.split("/") : [];
          const isAiVideoChild = item.node.type === "directory" && dramaPathParts.length === 2 && dramaPathParts[0] === "ai_videos";
          const isSystemFolder = isAiVideoChild && dramaPathParts[1].startsWith("_");
          const isDrama = isAiVideoChild && !isSystemFolder;
          const isActorsRoot = isAiVideoChild && dramaPathParts[1] === "_actors";
          const isVoicesRoot = isAiVideoChild && dramaPathParts[1] === "_voices";
          const isBgmRoot = isAiVideoChild && dramaPathParts[1] === "_bgm";
          const isPerformancesRoot = isAiVideoChild && dramaPathParts[1] === "_performances";
          const isDeletedRoot = isAiVideoChild && dramaPathParts[1] === "_deleted";
          const isActorEntry =
            item.node.type === "actor" &&
            dramaPathParts.length >= 3 &&
            dramaPathParts[0] === "ai_videos" &&
            dramaPathParts[1] === "_actors" &&
            ACTOR_ID_RE.test(dramaPathParts[2]) &&
            !dramaPathParts.includes("_deleted");
          const actorId = isActorEntry ? dramaPathParts[2] : null;
          const isVoiceEntry =
            item.node.type === "voice" &&
            dramaPathParts.length >= 3 &&
            dramaPathParts[0] === "ai_videos" &&
            dramaPathParts[1] === "_voices" &&
            VOICE_ID_RE.test(dramaPathParts[2]) &&
            !dramaPathParts.includes("_deleted");
          const voiceId = isVoiceEntry ? dramaPathParts[2] : null;
          const isDeletingThis = actorId !== null && deletingActorId === actorId;
          const isDeletingVoiceThis = voiceId !== null && deletingVoiceId === voiceId;
          const isRenamingThis = renamingPath === item.node.path;
          return (
            <div
              key={item.node.path || item.node.name}
              role="treeitem"
              tabIndex={isFocused || (focusedPath === null && item === flat[0]) ? 0 : -1}
              data-path={item.node.path}
              aria-level={item.depth + 1}
              aria-expanded={isLeaf ? undefined : isOpen}
              aria-selected={isActive}
              className={["tree-item", isLeaf ? "tree-leaf" : "tree-branch", isActive ? "tree-active" : ""].filter(Boolean).join(" ")}
              style={{ paddingLeft: `${8 + item.depth * 14}px` }}
              onFocus={() => setFocusedPath(item.node.path)}
              onKeyDown={(e) => onItemKeyDown(e, item)}
              onClick={(e) => {
                e.stopPropagation();
                if (isLeaf) { onSelect(item.node.path); return; }
                if (hasChildren) toggle(item.node.path);
              }}
            >
              {!isLeaf && hasChildren ? (
                <button type="button" className="tree-disclosure" aria-label={isOpen ? "Collapse" : "Expand"}
                  onClick={(e) => { e.stopPropagation(); toggle(item.node.path); }}>
                  {isOpen ? "▾" : "▸"}
                </button>
              ) : null}
              {item.node.type === "image" ? <span aria-hidden="true" className="tree-icon">🖼</span> : null}
              {item.node.type === "video" ? <span aria-hidden="true" className="tree-icon">🎬</span> : null}
              {item.node.type === "audio" ? <span aria-hidden="true" className="tree-icon">🎵</span> : null}
              {item.node.type === "actor" ? <span aria-hidden="true" className="tree-icon">🎭</span> : null}
              {item.node.type === "voice" ? <span aria-hidden="true" className="tree-icon">🎙</span> : null}
              {isActorsRoot ? <span aria-hidden="true" className="tree-icon">🎭</span> : null}
              {isVoicesRoot ? <span aria-hidden="true" className="tree-icon">🎙</span> : null}
              {isBgmRoot ? <span aria-hidden="true" className="tree-icon">🎵</span> : null}
              {isPerformancesRoot ? <span aria-hidden="true" className="tree-icon">🎬</span> : null}
              <span className="tree-label">{item.node.display_name || item.node.name}</span>
              {subType ? (
                <span className={`subtype-badge subtype-${subType}`}
                  aria-label={`项目类型: ${subType === "novel" ? "剧" : "短"}`}>
                  {subType === "novel" ? "剧" : "短"}
                </span>
              ) : null}
              {isDrama ? (
                <button
                  type="button"
                  className="drama-rename-btn"
                  aria-label={`从 Downloads 导入近 7 天的图片/视频到 ${item.node.name} 并按 parent folder 重命名`}
                  disabled={renamingPath !== null}
                  title="从 Downloads 按文件名分类导入近 7 天的图片/视频，并按 parent folder 重命名"
                  onClick={(e) => onRenameClick(e, item.node.path)}
                >
                  {isRenamingThis ? "导入并重命名中…" : "📥 导入 + 重命名"}
                </button>
              ) : null}
              {isPerformancesRoot ? (
                <button
                  type="button"
                  className="drama-rename-btn"
                  aria-label="从 Downloads 导入近 7 天的演技库检验视频，按 演{编号}{克|即|始} tag 归位到对应 perf 文件夹"
                  disabled={renamingPath !== null}
                  title="从 Downloads 按 演{编号}{克|即|始} tag 导入近 7 天的检验视频/起始帧，归位到 perf 文件夹并重命名为规范名"
                  onClick={(e) => onRenameClick(e, item.node.path)}
                >
                  {isRenamingThis ? "导入中…" : "📥 导入检验视频"}
                </button>
              ) : null}
              {isActorsRoot ? (
                <>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="生成新一批 AI 演员人脸"
                    title="调用 Kling text-to-image 生成一批新演员人脸，按属性 label 入库"
                    onClick={(e) => { e.stopPropagation(); setGeneratorOpen(true); }}
                  >
                    🎭 生成演员
                  </button>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="从 Downloads 导入近 7 天的外部出图，按 id{编号}{f|b} tag 归位到对应 actor 文件夹"
                    disabled={renamingPath !== null}
                    title="prompt-only 出图后用：从 Downloads 按 id{编号}{f|b} tag 导入近 7 天的人脸/全身图，转码为规范名归位到 actor 文件夹"
                    onClick={(e) => onRenameClick(e, item.node.path)}
                  >
                    {isRenamingThis ? "导入中…" : "📥 导入演员"}
                  </button>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="在网格视图中查看所有演员"
                    title="网格视图：一屏多图对比，分页浏览"
                    onClick={(e) => { e.stopPropagation(); navigate("/actors"); }}
                  >
                    🔲 网格
                  </button>
                </>
              ) : null}
              {isVoicesRoot ? (
                <>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="生成新一批配音 prompt"
                    title="本地合成 Chinese 配音 prompt，粘贴入外部 AI 配音模型"
                    onClick={(e) => { e.stopPropagation(); setVoiceGeneratorOpen(true); }}
                  >
                    🎙 生成配音
                  </button>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="在网格视图中查看所有配音"
                    title="网格视图：archetype 筛选 + 一键试听"
                    onClick={(e) => { e.stopPropagation(); navigate("/voices"); }}
                  >
                    🔲 网格
                  </button>
                </>
              ) : null}
              {isBgmRoot ? (
                <>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="生成新一批 BGM 背景音乐"
                    title="调用 Stable Audio 生成一批背景音乐（耗时较长），按情绪分类入库"
                    onClick={(e) => { e.stopPropagation(); setBgmGeneratorOpen(true); }}
                  >
                    🎵 生成 BGM
                  </button>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="从 Downloads 导入近 7 天的背景音乐，按 bgm_编号 tag 归位到对应轨道"
                    disabled={renamingPath !== null}
                    title="ElevenLabs 出乐后用：从 Downloads 按 bgm_编号 tag 导入近 7 天的音频，归位到对应 bgm 文件夹"
                    onClick={(e) => onRenameClick(e, item.node.path)}
                  >
                    {isRenamingThis ? "导入中…" : "📥 导入下载音乐"}
                  </button>
                  <button
                    type="button"
                    className="drama-rename-btn"
                    aria-label="在网格视图中查看所有 BGM"
                    title="网格视图：情绪分类筛选 + 一键试听"
                    onClick={(e) => { e.stopPropagation(); navigate("/bgm"); }}
                  >
                    🔲 网格
                  </button>
                </>
              ) : null}
              {isDeletedRoot ? (
                <button
                  type="button"
                  className="drama-rename-btn"
                  aria-label="打开回收站清理视图"
                  title="多选 + 永久删除 _deleted/ 下的 media 文件"
                  onClick={(e) => { e.stopPropagation(); navigate("/deleted"); }}
                >
                  🧹 永久清理
                </button>
              ) : null}
              {isActorEntry && actorId ? (
                <button
                  type="button"
                  className="actor-delete-btn"
                  aria-label={`软删除 ${actorId}`}
                  title="软删除 actor — 移到 _deleted/_actors/，并从所有 casting.md 取消分配"
                  disabled={deletingActorId !== null}
                  onClick={(e) => onActorDeleteClick(e, actorId)}
                >
                  {isDeletingThis ? "删除中…" : "🗑"}
                </button>
              ) : null}
              {isVoiceEntry && voiceId ? (
                <button
                  type="button"
                  className="actor-delete-btn"
                  aria-label={`软删除 ${voiceId}`}
                  title="软删除 voice — 移到 _deleted/_voices/（已分配的 voice 会拒绝删除）"
                  disabled={deletingVoiceId !== null}
                  onClick={(e) => onVoiceDeleteClick(e, voiceId)}
                >
                  {isDeletingVoiceThis ? "删除中…" : "🗑"}
                </button>
              ) : null}
            </div>
          );
        })}
      </div>
      <ActorPoolGenerator
        open={generatorOpen}
        onClose={() => setGeneratorOpen(false)}
        onGenerated={() => { if (onTreeReload) onTreeReload(); }}
      />
      <VoicePoolGenerator
        open={voiceGeneratorOpen}
        onClose={() => setVoiceGeneratorOpen(false)}
        onGenerated={() => { if (onTreeReload) onTreeReload(); }}
      />
      <BgmPoolGenerator
        open={bgmGeneratorOpen}
        onClose={() => setBgmGeneratorOpen(false)}
        onGenerated={() => { if (onTreeReload) onTreeReload(); }}
      />
    </nav>
  );
}

function focusByPath(root: HTMLDivElement | null, path: string, setFocused: (p: string) => void): void {
  if (!root) return;
  const el = root.querySelector<HTMLElement>(`[data-path="${cssEscape(path)}"]`);
  if (el) { el.focus(); setFocused(path); }
}

function cssEscape(value: string): string {
  if (typeof CSS !== "undefined" && typeof CSS.escape === "function") return CSS.escape(value);
  return value.replace(/["\\]/g, "\\$&");
}
