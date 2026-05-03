"""
EXPOSED_TREE definition (FR-2).

The EXPOSED_TREE is the union of:
- CLAUDE.md
- every .claude/agents/*.md
- every .claude/skills/**/SKILL.md
- every .claude/skills/agent_team/playbooks/*.md
- every .claude/agent_refs/**/*.md
- every specs/{type}/{name}/<canonical-stage>/** (limited to canonical stages)

Plus an explicit allow-listed __scratch__ subfolder under each project for fixture
writes (system tests need a writable area inside the sandbox).

This module returns absolute Path objects; safe_resolve still applies on top.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

CANONICAL_STAGES = ("user_input", "interview", "findings", "final_specs", "validation")
PROJECT_LEVEL_FILES = ("changelog.md",)
SCRATCH_DIRNAME = "__scratch__"


@dataclass(frozen=True)
class ExposedTree:
    root: Path

    def claude_md(self) -> Path:
        return self.root / "CLAUDE.md"

    def claude_agents(self) -> list[Path]:
        agents = self.root / ".claude" / "agents"
        if not agents.is_dir():
            return []
        return sorted([p for p in agents.glob("*.md") if p.is_file()])

    def claude_skill_files(self) -> list[Path]:
        skills = self.root / ".claude" / "skills"
        if not skills.is_dir():
            return []
        out: list[Path] = []
        for p in skills.rglob("SKILL.md"):
            if p.is_file():
                out.append(p)
        for p in (skills / "agent_team" / "playbooks").glob("*.md") if (skills / "agent_team" / "playbooks").is_dir() else []:
            if p.is_file():
                out.append(p)
        return sorted(set(out))

    def claude_agent_refs(self) -> list[Path]:
        refs = self.root / ".claude" / "agent_refs"
        if not refs.is_dir():
            return []
        return sorted([p for p in refs.rglob("*.md") if p.is_file()])

    def project_dirs(self) -> list[Path]:
        specs = self.root / "specs"
        if not specs.is_dir():
            return []
        out: list[Path] = []
        for type_dir in sorted(specs.iterdir()):
            if not type_dir.is_dir():
                continue
            for name_dir in sorted(type_dir.iterdir()):
                if name_dir.is_dir():
                    out.append(name_dir)
        return out

    def project_stage_dirs(self, project_dir: Path) -> list[Path]:
        out = []
        for stage in CANONICAL_STAGES:
            d = project_dir / stage
            if d.is_dir():
                out.append(d)
        scratch = project_dir / SCRATCH_DIRNAME
        if scratch.is_dir():
            out.append(scratch)
        return out

    def project_top_level_files(self, project_dir: Path) -> list[Path]:
        out = []
        for name in PROJECT_LEVEL_FILES:
            p = project_dir / name
            if p.is_file():
                out.append(p)
        return out
