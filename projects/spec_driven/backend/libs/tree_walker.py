from __future__ import annotations

from pathlib import Path

from libs.exposed_tree import ALLOWED_EXTENSIONS


_STAGES: tuple[str, ...] = (
    "user_input",
    "interview",
    "findings",
    "final_specs",
    "validation",
)

_VALIDATION_PRIORITY: tuple[str, ...] = (
    "strategy.md",
    "acceptance_criteria.md",
    "bdd_scenarios.md",
)


def build_tree(repo_root: Path) -> dict[str, object]:
    return {
        "settings": _build_settings(repo_root),
        "projects": _build_projects(repo_root),
    }


def _build_settings(repo_root: Path) -> dict[str, object]:
    return {
        "claude_md": _build_claude_md(repo_root),
        "agents": _build_agents(repo_root),
        "skills": _build_skills(repo_root),
        "agent_refs": _build_agent_refs(repo_root),
    }


def _build_claude_md(repo_root: Path) -> list[dict[str, object]]:
    target = repo_root / "CLAUDE.md"
    if _safe_exists(target) and not _safe_is_symlink(target) and target.is_file():
        return [_leaf("CLAUDE.md", "CLAUDE.md")]
    return []


def _build_agents(repo_root: Path) -> list[dict[str, object]]:
    agents_dir = repo_root / ".claude" / "agents"
    if not agents_dir.is_dir():
        return []
    entries: list[dict[str, object]] = []
    try:
        children = list(agents_dir.iterdir())
    except OSError:
        return []
    for child in sorted(children, key=lambda p: p.name.lower()):
        if _safe_is_symlink(child):
            continue
        if not child.is_file():
            continue
        if child.suffix != ".md":
            continue
        rel = f".claude/agents/{child.name}"
        entries.append(_leaf(child.name, rel))
    return entries


def _build_agent_refs(repo_root: Path) -> list[dict[str, object]]:
    refs_dir = repo_root / ".claude" / "agent_refs"
    if not refs_dir.is_dir():
        return []
    out: list[dict[str, object]] = []
    try:
        manager_dirs = list(refs_dir.iterdir())
    except OSError:
        return []
    for manager_dir in sorted(manager_dirs, key=lambda p: p.name.lower()):
        if _safe_is_symlink(manager_dir) or not manager_dir.is_dir():
            continue
        try:
            files = list(manager_dir.iterdir())
        except OSError:
            continue
        leaves: list[dict[str, object]] = []
        for f in sorted(files, key=lambda p: p.name.lower()):
            if _safe_is_symlink(f) or not f.is_file():
                continue
            if f.suffix.lower() != ".md":
                continue
            rel = f".claude/agent_refs/{manager_dir.name}/{f.name}"
            leaves.append(_leaf(f.name, rel))
        out.append({
            "kind": "folder",
            "name": manager_dir.name,
            "path": f".claude/agent_refs/{manager_dir.name}",
            "children": leaves,
        })
    return out


def _build_skills(repo_root: Path) -> list[dict[str, object]]:
    skills_dir = repo_root / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    entries: list[dict[str, object]] = []
    try:
        folders = list(skills_dir.iterdir())
    except OSError:
        return []
    for folder in sorted(folders, key=lambda p: p.name.lower()):
        if _safe_is_symlink(folder):
            continue
        if not folder.is_dir():
            continue
        skill_md = folder / "SKILL.md"
        if _safe_exists(skill_md) and not _safe_is_symlink(skill_md) and skill_md.is_file():
            rel = f".claude/skills/{folder.name}/SKILL.md"
            entries.append(_leaf(folder.name, rel))
    return entries


def _build_projects(repo_root: Path) -> list[dict[str, object]]:
    specs_dir = repo_root / "specs"
    if not specs_dir.is_dir():
        return []
    out: list[dict[str, object]] = []
    try:
        type_dirs = [p for p in specs_dir.iterdir() if p.is_dir() and not _safe_is_symlink(p)]
    except OSError:
        return []
    for type_dir in sorted(type_dirs, key=lambda p: p.name.lower()):
        try:
            name_dirs = [p for p in type_dir.iterdir() if p.is_dir() and not _safe_is_symlink(p)]
        except OSError:
            continue
        names_payload: list[dict[str, object]] = []
        for name_dir in sorted(name_dirs, key=lambda p: p.name.lower()):
            project_rel = f"specs/{type_dir.name}/{name_dir.name}"
            stages_payload = _build_stages(name_dir, project_rel)
            names_payload.append({
                "kind": "project",
                "name": name_dir.name,
                "path": project_rel,
                "children": stages_payload,
            })
        out.append({
            "kind": "task_type",
            "name": type_dir.name,
            "path": f"specs/{type_dir.name}",
            "children": names_payload,
        })
    return out


def _build_stages(project_dir: Path, project_rel: str) -> list[dict[str, object]]:
    stages: list[dict[str, object]] = []
    for stage in _STAGES:
        stage_dir = project_dir / stage
        rel = f"{project_rel}/{stage}"
        if not stage_dir.exists():
            stages.append({
                "kind": "missing-folder",
                "name": stage,
                "path": rel,
                "present": False,
                "files": [],
                "children": [],
            })
            continue
        if _safe_is_symlink(stage_dir):
            stages.append({
                "kind": "missing-folder",
                "name": stage,
                "path": rel,
                "present": False,
                "files": [],
                "children": [],
            })
            continue
        children = _walk_stage(stage_dir, rel, stage)
        files_flat = _collect_filenames(children)
        stages.append({
            "kind": "folder",
            "name": stage,
            "path": rel,
            "present": True,
            "files": files_flat,
            "children": children,
        })
    return stages


def _collect_filenames(children: list[dict[str, object]]) -> list[str]:
    out: list[str] = []
    for c in children:
        if c.get("kind") == "file":
            name = c.get("name")
            if isinstance(name, str):
                out.append(name)
        elif c.get("kind") == "folder":
            grand = c.get("children")
            if isinstance(grand, list):
                out.extend(_collect_filenames([g for g in grand if isinstance(g, dict)]))
    return out


def _walk_stage(directory: Path, rel: str, stage: str) -> list[dict[str, object]]:
    try:
        entries = list(directory.iterdir())
    except OSError:
        return []
    files: list[Path] = []
    folders: list[Path] = []
    for e in entries:
        if _safe_is_symlink(e):
            continue
        if e.is_file() and e.suffix.lower() in ALLOWED_EXTENSIONS:
            files.append(e)
        elif e.is_dir():
            folders.append(e)

    if stage == "validation":
        files_sorted = _sort_validation(files)
    else:
        files_sorted = _alpha_sort(files)
    folders_sorted = _alpha_sort(folders)

    out: list[dict[str, object]] = []
    for f in files_sorted:
        out.append(_leaf(f.name, f"{rel}/{f.name}"))
    for d in folders_sorted:
        sub_rel = f"{rel}/{d.name}"
        children = _walk_stage(d, sub_rel, stage="")
        out.append({
            "kind": "folder",
            "name": d.name,
            "path": sub_rel,
            "children": children,
        })
    return out


def _alpha_sort(paths: list[Path]) -> list[Path]:
    return sorted(paths, key=lambda p: (p.name.lower(), p.name))


def _sort_validation(paths: list[Path]) -> list[Path]:
    by_name: dict[str, Path] = {p.name: p for p in paths}
    head: list[Path] = []
    used: set[str] = set()
    for priority in _VALIDATION_PRIORITY:
        if priority in by_name:
            head.append(by_name[priority])
            used.add(priority)
    rest = [p for p in paths if p.name not in used]
    return head + _alpha_sort(rest)


def _leaf(name: str, rel: str) -> dict[str, object]:
    return {"kind": "file", "name": name, "path": rel}


def _safe_exists(p: Path) -> bool:
    try:
        return p.exists()
    except OSError:
        return False


def _safe_is_symlink(p: Path) -> bool:
    try:
        return p.is_symlink()
    except OSError:
        return False
