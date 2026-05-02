from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from libs.exposed_tree import ALLOWED_EXTENSIONS, STAGE_SUBFOLDERS, ExposedTree

NodeKind = Literal["file", "folder", "missing-folder"]


VALIDATION_PRIORITY: tuple[str, ...] = (
    "strategy.md",
    "acceptance_criteria.md",
    "bdd_scenarios.md",
)


@dataclass(frozen=True)
class TreeNode:
    name: str
    kind: NodeKind
    path: str
    children: tuple["TreeNode", ...] = field(default_factory=tuple)
    present: bool = True


def _sort_files_in_stage(stage: str, files: list[Path]) -> list[Path]:
    if stage != "validation":
        return sorted(files, key=lambda p: (p.name.lower(), p.name))
    priority_index: dict[str, int] = {n: i for i, n in enumerate(VALIDATION_PRIORITY)}
    return sorted(
        files,
        key=lambda p: (
            priority_index.get(p.name, len(priority_index)),
            p.name.lower(),
            p.name,
        ),
    )


def _stage_node(stage: str, project_dir: Path, repo_root: Path) -> TreeNode:
    stage_dir = project_dir / stage
    if not stage_dir.is_dir() or stage_dir.is_symlink():
        return TreeNode(
            name=stage,
            kind="missing-folder",
            path=str((stage_dir).relative_to(repo_root)).replace("\\", "/"),
            present=False,
        )
    file_entries: list[Path] = []
    for entry in stage_dir.iterdir():
        if not entry.is_file() or entry.is_symlink():
            continue
        if entry.suffix.lower() not in ALLOWED_EXTENSIONS:
            continue
        file_entries.append(entry)
    sorted_files = _sort_files_in_stage(stage, file_entries)
    children = tuple(
        TreeNode(
            name=p.name,
            kind="file",
            path=str(p.relative_to(repo_root)).replace("\\", "/"),
        )
        for p in sorted_files
    )
    return TreeNode(
        name=stage,
        kind="folder",
        path=str(stage_dir.relative_to(repo_root)).replace("\\", "/"),
        children=children,
        present=True,
    )


def _project_node(project_dir: Path, repo_root: Path) -> TreeNode:
    children = tuple(_stage_node(s, project_dir, repo_root) for s in STAGE_SUBFOLDERS)
    return TreeNode(
        name=project_dir.name,
        kind="folder",
        path=str(project_dir.relative_to(repo_root)).replace("\\", "/"),
        children=children,
    )


def _projects_section(repo_root: Path) -> list[TreeNode]:
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return []
    type_nodes: list[TreeNode] = []
    for type_dir in sorted(
        (p for p in specs_dir.iterdir() if p.is_dir() and not p.is_symlink()),
        key=lambda p: (p.name.lower(), p.name),
    ):
        project_nodes: list[TreeNode] = []
        for project_dir in sorted(
            (p for p in type_dir.iterdir() if p.is_dir() and not p.is_symlink()),
            key=lambda p: (p.name.lower(), p.name),
        ):
            project_nodes.append(_project_node(project_dir, repo_root))
        type_nodes.append(
            TreeNode(
                name=type_dir.name,
                kind="folder",
                path=str(type_dir.relative_to(repo_root)).replace("\\", "/"),
                children=tuple(project_nodes),
            )
        )
    return type_nodes


def _settings_section(tree: ExposedTree) -> dict[str, list[TreeNode]]:
    repo_root = tree.repo_root
    claude_md_path = tree.claude_md()
    claude_md_node: list[TreeNode] = []
    if claude_md_path.exists() and claude_md_path.is_file():
        claude_md_node = [
            TreeNode(
                name="CLAUDE.md",
                kind="file",
                path=str(claude_md_path.relative_to(repo_root)).replace("\\", "/"),
            )
        ]
    agents = [
        TreeNode(
            name=p.name,
            kind="file",
            path=str(p.relative_to(repo_root)).replace("\\", "/"),
        )
        for p in tree.agent_files()
    ]
    skills = [
        TreeNode(
            name=p.parent.name,
            kind="file",
            path=str(p.relative_to(repo_root)).replace("\\", "/"),
        )
        for p in tree.skill_files()
    ]
    return {"claude_md": claude_md_node, "agents": agents, "skills": skills}


def _node_to_dict(node: TreeNode) -> dict[str, object]:
    out: dict[str, object] = {"name": node.name, "kind": node.kind, "path": node.path, "present": node.present}
    if node.children:
        out["children"] = [_node_to_dict(c) for c in node.children]
    return out


def build_tree(repo_root: Path) -> dict[str, object]:
    tree = ExposedTree(repo_root=repo_root)
    settings = _settings_section(tree)
    projects = _projects_section(repo_root)
    return {
        "settings": {
            "claude_md": [_node_to_dict(n) for n in settings["claude_md"]],
            "agents": [_node_to_dict(n) for n in settings["agents"]],
            "skills": [_node_to_dict(n) for n in settings["skills"]],
        },
        "projects": [_node_to_dict(n) for n in projects],
    }
