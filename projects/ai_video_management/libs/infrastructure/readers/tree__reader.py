from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from libs.common.exposed_tree import ExposedTree, TREE_VISIBLE_EXTENSIONS
from libs.common.sub_type_lookup import lookup as sub_type_lookup
from libs.domain.value_objects.novel__valueobject import CANONICAL_NOVELS, categories as novel_categories

_IMAGE_EXTENSIONS: frozenset[str] = frozenset({".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"})
_VIDEO_EXTENSIONS: frozenset[str] = frozenset({".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v"})
_AUDIO_EXTENSIONS: frozenset[str] = frozenset({".mp3", ".wav", ".m4a", ".aac", ".ogg", ".flac"})
_ACTOR_FOLDER_RE = re.compile(r"^actor_\d{4,}$")


class TreeReader:
    """Walks the EXPOSED_TREE root and emits the recursive TreeNode shape.

    Single section: "AI Videos".
    """

    def __init__(self, exposed: ExposedTree) -> None:
        self._exposed = exposed
        self._root = exposed.root

    def build(self) -> dict[str, Any]:
        return {
            "type": "section",
            "name": "root",
            "path": "",
            "children": [self._ai_videos_section(), self._novels_section()],
        }

    def _ai_videos_section(self) -> dict[str, Any]:
        ai_videos_root = self._root / "ai_videos"
        children: list[dict[str, Any]] = []
        deleted_child: dict[str, Any] | None = None
        if ai_videos_root.is_dir():
            for project_dir in sorted(p for p in ai_videos_root.iterdir() if p.is_dir()):
                if project_dir.name in self._exposed.excluded_dirs():
                    continue
                project_node = self._walk_project(project_dir)
                if project_node is None:
                    continue
                if project_dir.name == "_deleted":
                    deleted_child = project_node
                else:
                    children.append(project_node)
        if deleted_child is not None:
            children.append(deleted_child)
        return {
            "type": "section",
            "name": "AI Videos",
            "path": "",
            "children": children,
        }

    def _novels_section(self) -> dict[str, Any]:
        novels_root = self._root / "novels"
        children: list[dict[str, Any]] = []
        if novels_root.is_dir():
            category_zh = dict(novel_categories())
            slug_to_title: dict[str, str] = {s.slug: s.title_zh for s in CANONICAL_NOVELS}
            slug_order: dict[str, int] = {s.slug: i for i, s in enumerate(CANONICAL_NOVELS)}
            cat_order: dict[str, int] = {c: i for i, (c, _) in enumerate(novel_categories())}
            for cat_dir in sorted(
                (p for p in novels_root.iterdir() if p.is_dir() and not p.is_symlink()),
                key=lambda p: cat_order.get(p.name, 9999),
            ):
                if cat_dir.name in self._exposed.excluded_dirs():
                    continue
                novel_nodes: list[dict[str, Any]] = []
                for novel_dir in sorted(
                    (p for p in cat_dir.iterdir() if p.is_dir() and not p.is_symlink()),
                    key=lambda p: slug_order.get(p.name, 9999),
                ):
                    if novel_dir.name in self._exposed.excluded_dirs():
                        continue
                    if not self._novel_is_complete(novel_dir):
                        continue
                    sub = self._walk_filtered(novel_dir, self._is_allowed_leaf)
                    novel_nodes.append(
                        {
                            "type": "directory",
                            "name": novel_dir.name,
                            "display_name": slug_to_title.get(novel_dir.name, novel_dir.name),
                            "path": self._rel(novel_dir),
                            "children": sub,
                        }
                    )
                if not novel_nodes:
                    continue
                children.append(
                    {
                        "type": "directory",
                        "name": cat_dir.name,
                        "display_name": category_zh.get(cat_dir.name, cat_dir.name),
                        "path": self._rel(cat_dir),
                        "children": novel_nodes,
                    }
                )
            for entry in sorted(
                (p for p in novels_root.iterdir() if p.is_file() and not p.is_symlink()),
                key=lambda p: p.name.lower(),
            ):
                if self._is_allowed_leaf(entry):
                    children.append(self._leaf_for(entry))
        return {
            "type": "section",
            "name": "Novels",
            "path": "",
            "children": children,
        }

    def _novel_is_complete(self, novel_dir: Path) -> bool:
        """Per follow-up 104: the Novels section only surfaces novels whose
        `_meta.json.complete == True`. In-progress downloads stay on disk
        (resume checkpoint preserved) but are filtered out of the sidebar.
        """
        meta_path = novel_dir / "_meta.json"
        if not meta_path.is_file():
            return False
        try:
            data = json.loads(meta_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return False
        return bool(data.get("complete", False))

    def _walk_project(self, project_dir: Path) -> dict[str, Any] | None:
        sub = self._walk_filtered(project_dir, self._is_allowed_leaf)
        meta = sub_type_lookup(self._root, project_dir.name)
        project_meta_payload: dict[str, Any] | None = None
        if meta.sub_type is not None or meta.shot_count is not None or meta.episode_count is not None:
            project_meta_payload = {
                "sub_type": meta.sub_type,
                "shot_count": meta.shot_count,
                "episode_count": meta.episode_count,
            }
        node: dict[str, Any] = {
            "type": "directory",
            "name": project_dir.name,
            "path": self._rel(project_dir),
            "children": sub,
            "project_meta": project_meta_payload,
        }
        zh_title = self._project_zh_title(project_dir)
        if zh_title:
            node["display_name"] = zh_title
        return node

    def _project_zh_title(self, project_dir: Path) -> str | None:
        """Per CLAUDE.md AI video rules: the Chinese title lives in
        `ai_videos/{name}/README.md`. Extract it from the first H1 line —
        canonical shape `# 《<title>》— AI 视频项目`.
        """
        readme = project_dir / "README.md"
        if not readme.is_file():
            return None
        try:
            with readme.open(encoding="utf-8") as fh:
                for line in fh:
                    stripped = line.strip()
                    if stripped.startswith("# "):
                        m = re.search(r"《([^》]+)》", stripped)
                        if m:
                            return m.group(1)
                        return stripped[2:].strip() or None
        except OSError:
            return None
        return None

    def _walk_filtered(self, directory: Path, leaf_predicate: Any) -> list[dict[str, Any]]:
        children: list[dict[str, Any]] = []
        excluded = self._exposed.excluded_dirs()
        try:
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except OSError:
            return children
        for entry in entries:
            if entry.is_symlink():
                continue
            if entry.name in excluded:
                continue
            if entry.is_dir():
                collapsed = self._collapsed_actor_leaf(entry)
                if collapsed is not None:
                    children.append(collapsed)
                    continue
                sub = self._walk_filtered(entry, leaf_predicate)
                if sub:
                    children.append(
                        {
                            "type": "directory",
                            "name": entry.name,
                            "path": self._rel(entry),
                            "children": sub,
                        }
                    )
            elif entry.is_file():
                if leaf_predicate(entry):
                    children.append(self._leaf_for(entry))
        return children

    def _is_allowed_leaf(self, p: Path) -> bool:
        return p.suffix.lower() in TREE_VISIBLE_EXTENSIONS

    def _collapsed_actor_leaf(self, entry: Path) -> dict[str, Any] | None:
        if not _ACTOR_FOLDER_RE.match(entry.name):
            return None
        try:
            rel_parts = entry.resolve().relative_to(self._root).parts
        except (OSError, ValueError):
            return None
        if len(rel_parts) != 3 or rel_parts[0] != "ai_videos" or rel_parts[1] != "_actors":
            return None
        sidecar = entry / f"{entry.name}.md"
        if not sidecar.is_file():
            return None
        return {
            "type": "actor",
            "name": entry.name,
            "path": self._rel(sidecar),
            "face_path": self._first_face_image(entry),
            "children": [],
        }

    def _first_face_image(self, folder: Path) -> str | None:
        try:
            entries = sorted(folder.iterdir(), key=lambda p: p.name.lower())
        except OSError:
            return None
        for p in entries:
            if p.is_symlink() or not p.is_file():
                continue
            if p.suffix.lower() in _IMAGE_EXTENSIONS:
                return self._rel(p)
        return None

    def _leaf_for(self, f: Path) -> dict[str, Any]:
        ext = f.suffix.lower()
        if ext in _VIDEO_EXTENSIONS:
            node_type = "video"
        elif ext in _IMAGE_EXTENSIONS:
            node_type = "image"
        elif ext in _AUDIO_EXTENSIONS:
            node_type = "audio"
        else:
            node_type = "file"
        return {"type": node_type, "name": f.name, "path": self._rel(f)}

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._root).as_posix()
        except ValueError:
            return p.as_posix()
