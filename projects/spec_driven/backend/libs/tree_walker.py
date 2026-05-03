from __future__ import annotations

from pathlib import Path
from typing import Any

from libs.exposed_tree import ALLOWED_EXTENSIONS, ExposedTree


class TreeWalker:
    def __init__(self, exposed: ExposedTree) -> None:
        self._exposed = exposed
        self._root = exposed.root

    def build(self) -> dict[str, Any]:
        return {
            "type": "section",
            "name": "root",
            "path": "",
            "children": [
                self._claude_section(),
                self._projects_section(),
            ],
        }

    def _claude_section(self) -> dict[str, Any]:
        children: list[dict[str, Any]] = []

        for f in self._exposed.claude_root_files():
            children.append(self._leaf_for(f))

        dotclaude_node = self._build_dotclaude_node()
        if dotclaude_node is not None:
            children.append(dotclaude_node)

        return {
            "type": "section",
            "name": "Claude Settings & Shared Context",
            "path": "",
            "children": children,
        }

    def _build_dotclaude_node(self) -> dict[str, Any] | None:
        dotclaude = self._root / ".claude"
        if not dotclaude.is_dir():
            return None
        sub_children: list[dict[str, Any]] = []

        skills_dir = dotclaude / "skills"
        if skills_dir.is_dir():
            skills_children = self._walk_filtered(
                skills_dir,
                lambda p: p.name == "SKILL.md"
                or (p.parent.name == "playbooks" and p.suffix == ".md"),
            )
            if skills_children:
                sub_children.append(
                    {
                        "type": "directory",
                        "name": "skills",
                        "path": self._rel(skills_dir),
                        "children": skills_children,
                    }
                )

        refs_dir = dotclaude / "agent_refs"
        if refs_dir.is_dir():
            refs_children = self._walk_filtered(refs_dir, lambda p: p.suffix == ".md")
            if refs_children:
                sub_children.append(
                    {
                        "type": "directory",
                        "name": "agent_refs",
                        "path": self._rel(refs_dir),
                        "children": refs_children,
                    }
                )

        return {
            "type": "directory",
            "name": ".claude",
            "path": self._rel(dotclaude),
            "children": sub_children,
        }

    def _projects_section(self) -> dict[str, Any]:
        # FR-15: "Specs" subtree is `{type}/{name}/` mirrored from `specs/`.
        # Elide the literal `specs/` wrapper so task_type is the direct child.
        specs_dir = self._root / "specs"
        children: list[dict[str, Any]] = (
            self._walk_filtered(specs_dir, self._is_allowed_leaf)
            if specs_dir.is_dir()
            else []
        )
        return {
            "type": "section",
            "name": "Specs",
            "path": "",
            "children": children,
        }

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
        return p.suffix.lower() in ALLOWED_EXTENSIONS

    def _leaf_for(self, f: Path) -> dict[str, Any]:
        return {"type": "file", "name": f.name, "path": self._rel(f)}

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self._root).as_posix()
        except ValueError:
            return p.as_posix()
