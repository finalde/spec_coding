from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class StageModule:
    id: str
    label: str
    relative_path: str
    description: str


@dataclass(frozen=True)
class StageDef:
    id: str
    label: str
    folder: str
    modules: tuple[StageModule, ...]
    invocation: str


STAGE_DEFS: tuple[StageDef, ...] = (
    StageDef(
        id="intake",
        label="1. Intake",
        folder="user_input",
        invocation="Re-revise the prompt: read raw_prompt.md plus every follow_ups/*.md in numeric order and rewrite revised_prompt.md to the canonical form.",
        modules=(
            StageModule(
                id="revised_prompt",
                label="revised_prompt.md",
                relative_path="user_input/revised_prompt.md",
                description="Canonical revised prompt = raw + every follow-up.",
            ),
        ),
    ),
    StageDef(
        id="interview",
        label="2. Interview",
        folder="interview",
        invocation="Run the interview stage: invoke agent_team__interview_manager with the current revised_prompt.md and rewrite interview/qa.md.",
        modules=(
            StageModule(
                id="qa",
                label="qa.md",
                relative_path="interview/qa.md",
                description="Multi-round Q&A consolidated by the interview manager.",
            ),
        ),
    ),
    StageDef(
        id="research",
        label="3. Research",
        folder="findings",
        invocation="Run the research stage: invoke agent_team__research_manager with revised_prompt.md + qa.md and rewrite findings/dossier.md (and per-angle files).",
        modules=(
            StageModule(
                id="dossier",
                label="dossier.md",
                relative_path="findings/dossier.md",
                description="Consolidated research dossier.",
            ),
            StageModule(
                id="angles",
                label="angle-*.md",
                relative_path="findings/",
                description="Per-angle research notes.",
            ),
        ),
    ),
    StageDef(
        id="spec",
        label="4. Spec compilation",
        folder="final_specs",
        invocation="Compile the spec: read revised_prompt.md + qa.md + dossier.md and rewrite final_specs/spec.md.",
        modules=(
            StageModule(
                id="spec",
                label="spec.md",
                relative_path="final_specs/spec.md",
                description="Canonical spec for the project.",
            ),
        ),
    ),
    StageDef(
        id="validation_strategy",
        label="5. Validation strategy",
        folder="validation",
        invocation="Run validation strategy: invoke agent_team__validation_manager (strategy mode) with spec.md and rewrite validation/strategy.md plus the per-level files.",
        modules=(
            StageModule(
                id="strategy",
                label="strategy.md",
                relative_path="validation/strategy.md",
                description="Top-level validation strategy.",
            ),
            StageModule(
                id="acceptance_criteria",
                label="acceptance_criteria.md",
                relative_path="validation/acceptance_criteria.md",
                description="High-level acceptance criteria.",
            ),
            StageModule(
                id="bdd_scenarios",
                label="bdd_scenarios.md",
                relative_path="validation/bdd_scenarios.md",
                description="BDD scenarios.",
            ),
        ),
    ),
    StageDef(
        id="execution",
        label="6. Execution + streaming validation",
        folder="",
        invocation="Run execution: implement work units against the spec and have agent_team__validation_manager (runtime mode) validate each unit. Outputs land under projects/{name}/ or ai_videos/{name}/.",
        modules=(
            StageModule(
                id="execution_outputs",
                label="generated outputs",
                relative_path="",
                description="Code/tests/README under projects/{name}/ or ai_videos/{name}/.",
            ),
        ),
    ),
)


@dataclass(frozen=True)
class StagesPayload:
    project_type: str
    project_name: str
    stages: tuple[StageDef, ...] = field(default_factory=lambda: STAGE_DEFS)


def list_stages(project_type: str, project_name: str) -> dict[str, object]:
    return {
        "project_type": project_type,
        "project_name": project_name,
        "stages": [
            {
                "id": s.id,
                "label": s.label,
                "folder": s.folder,
                "invocation": s.invocation,
                "modules": [
                    {
                        "id": m.id,
                        "label": m.label,
                        "relative_path": m.relative_path,
                        "description": m.description,
                    }
                    for m in s.modules
                ],
            }
            for s in STAGE_DEFS
        ],
    }


def _read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _list_followups(project_dir: Path) -> list[Path]:
    follow_dir = project_dir / "user_input" / "follow_ups"
    if not follow_dir.is_dir():
        return []
    return sorted(p for p in follow_dir.iterdir() if p.is_file() and p.suffix.lower() == ".md")


def build_regen_prompt(
    project_type: str,
    project_name: str,
    stage_ids: list[str],
    module_ids: dict[str, list[str]] | None,
    autonomous: bool,
    repo_root: Path,
) -> str:
    project_dir = repo_root / "specs" / project_type / project_name
    selected_stages = [s for s in STAGE_DEFS if s.id in stage_ids] if stage_ids else list(STAGE_DEFS)
    if not selected_stages:
        selected_stages = list(STAGE_DEFS)

    lines: list[str] = []
    if autonomous:
        lines.append("# EXECUTION MODE: AUTONOMOUS")
        lines.append("")
        lines.append(
            "Do not call AskUserQuestion. For anything unclear, use your best judgment, "
            "record the choice inline in the artifact, and keep going. Produce every requested "
            "artifact below in this single turn before stopping."
        )
        lines.append("")
    else:
        lines.append("# EXECUTION MODE: INTERACTIVE")
        lines.append("")
        lines.append("You may use AskUserQuestion when a decision is genuinely ambiguous.")
        lines.append("")

    lines.append(f"## Project: {project_type}/{project_name}")
    lines.append("")
    lines.append(f"Project root: `specs/{project_type}/{project_name}/`")
    lines.append("")

    raw = _read_text(project_dir / "user_input" / "raw_prompt.md")
    revised = _read_text(project_dir / "user_input" / "revised_prompt.md")
    follow_ups = _list_followups(project_dir)

    lines.append("### Current intent")
    lines.append("")
    if revised is not None:
        lines.append("**revised_prompt.md** (current):")
        lines.append("")
        lines.append("```markdown")
        lines.append(revised.rstrip("\n"))
        lines.append("```")
        lines.append("")
    elif raw is not None:
        lines.append("**raw_prompt.md** (no revised yet):")
        lines.append("")
        lines.append("```markdown")
        lines.append(raw.rstrip("\n"))
        lines.append("```")
        lines.append("")
    else:
        lines.append("_No raw_prompt.md or revised_prompt.md found yet — gather intent from the user before regenerating._")
        lines.append("")

    if follow_ups:
        lines.append(f"**Follow-ups ({len(follow_ups)})**:")
        lines.append("")
        for fp in follow_ups:
            rel = fp.relative_to(repo_root).as_posix()
            lines.append(f"- `{rel}`")
        lines.append("")

    lines.append("### Stages to regenerate")
    lines.append("")
    for stage in selected_stages:
        lines.append(f"#### {stage.label}")
        lines.append("")
        lines.append(stage.invocation)
        lines.append("")
        chosen_modules = module_ids.get(stage.id) if module_ids else None
        modules_for_stage = (
            [m for m in stage.modules if m.id in chosen_modules]
            if chosen_modules
            else list(stage.modules)
        )
        if not modules_for_stage:
            modules_for_stage = list(stage.modules)
        lines.append("Artifacts in scope:")
        for m in modules_for_stage:
            target = (
                f"specs/{project_type}/{project_name}/{m.relative_path}"
                if m.relative_path
                else f"projects/{project_name}/ (or ai_videos/{project_name}/)"
            )
            lines.append(f"- **{m.label}** → `{target}` — {m.description}")
        lines.append("")

    lines.append("### Constraints")
    lines.append("")
    lines.append("- Honor every rule in `CLAUDE.md` (state surfaces, agent naming, iteration bounds).")
    lines.append("- Persist artifacts at the canonical paths above. Do not invent new locations.")
    lines.append(
        "- For stages 2/3/5, spawn the named manager agent per the contract in CLAUDE.md "
        "(parent is the spawner; managers cannot self-spawn nested subagents)."
    )
    if autonomous:
        lines.append("- Do not stop to ask. Do not emit AskUserQuestion. Run the full pipeline above to completion.")
    lines.append("")
    lines.append("Begin.")
    lines.append("")
    return "\n".join(lines)
