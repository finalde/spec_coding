"""
tree_walker — produce the EXPOSED_TREE JSON consumed by GET /api/tree.

Output shape (FR-1):
    {name, path, type, children[]}

Where `type` ∈ {"section", "type", "project", "stage", "file"}.

Every non-leaf node carries a `children` array. The frontend Sidebar descends
node["children"] uniformly — there is NO `task_type.projects` or `project.stages`
drift (regression-2026-05-02-clean).

Paths are forward-slash normalized (NFR-13).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypedDict

from .exposed_tree import CANONICAL_STAGES, PROJECT_LEVEL_FILES, ExposedTree


class TreeNode(TypedDict):
    name: str
    path: str
    type: str
    children: list["TreeNode"]


@dataclass(frozen=True)
class TreeWalker:
    exposed: ExposedTree

    def walk(self) -> list[TreeNode]:
        return [self._claude_section(), self._projects_section()]

    def _rel(self, p: Path) -> str:
        try:
            return p.resolve().relative_to(self.exposed.root.resolve()).as_posix()
        except ValueError:
            return p.as_posix().replace("\\", "/")

    def _file_node(self, p: Path) -> TreeNode:
        return {"name": p.name, "path": self._rel(p), "type": "file", "children": []}

    def _claude_section(self) -> TreeNode:
        children: list[TreeNode] = []
        claude_md = self.exposed.claude_md()
        if claude_md.is_file():
            children.append(self._file_node(claude_md))

        agents = self.exposed.claude_agents()
        if agents:
            children.append(
                {
                    "name": ".claude/agents",
                    "path": ".claude/agents",
                    "type": "section",
                    "children": [self._file_node(a) for a in agents],
                }
            )

        skill_files = self.exposed.claude_skill_files()
        if skill_files:
            children.append(
                {
                    "name": ".claude/skills",
                    "path": ".claude/skills",
                    "type": "section",
                    "children": sorted(
                        [self._file_node(s) for s in skill_files],
                        key=lambda n: n["path"].lower(),
                    ),
                }
            )

        refs = self.exposed.claude_agent_refs()
        if refs:
            children.append(
                {
                    "name": ".claude/agent_refs",
                    "path": ".claude/agent_refs",
                    "type": "section",
                    "children": sorted(
                        [self._file_node(r) for r in refs],
                        key=lambda n: n["path"].lower(),
                    ),
                }
            )

        return {
            "name": "Claude Settings & Shared Context",
            "path": "_claude",
            "type": "section",
            "children": children,
        }

    def _projects_section(self) -> TreeNode:
        type_groups: dict[str, list[TreeNode]] = {}
        for project_dir in self.exposed.project_dirs():
            type_name = project_dir.parent.name
            project_children: list[TreeNode] = []

            for top_file in self.exposed.project_top_level_files(project_dir):
                project_children.append(self._file_node(top_file))

            for stage_dir in self.exposed.project_stage_dirs(project_dir):
                stage_files: list[TreeNode] = []
                for entry in sorted(stage_dir.iterdir(), key=lambda x: x.name.lower()):
                    if entry.is_file():
                        stage_files.append(self._file_node(entry))
                    elif entry.is_dir():
                        sub_files = [
                            self._file_node(f)
                            for f in sorted(entry.iterdir(), key=lambda x: x.name.lower())
                            if f.is_file()
                        ]
                        if sub_files:
                            stage_files.append(
                                {
                                    "name": entry.name,
                                    "path": self._rel(entry),
                                    "type": "stage",
                                    "children": sub_files,
                                }
                            )
                project_children.append(
                    {
                        "name": stage_dir.name,
                        "path": self._rel(stage_dir),
                        "type": "stage",
                        "children": stage_files,
                    }
                )

            type_groups.setdefault(type_name, []).append(
                {
                    "name": project_dir.name,
                    "path": self._rel(project_dir),
                    "type": "project",
                    "children": project_children,
                }
            )

        type_nodes: list[TreeNode] = []
        for type_name in sorted(type_groups.keys(), key=str.lower):
            type_nodes.append(
                {
                    "name": type_name,
                    "path": f"specs/{type_name}",
                    "type": "type",
                    "children": type_groups[type_name],
                }
            )

        return {
            "name": "Projects",
            "path": "_projects",
            "type": "section",
            "children": type_nodes,
        }


def to_jsonable(node: TreeNode) -> dict[str, Any]:
    return {
        "name": node["name"],
        "path": node["path"],
        "type": node["type"],
        "children": [to_jsonable(c) for c in node["children"]],
    }
