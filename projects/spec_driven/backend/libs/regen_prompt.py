from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from libs.file_reader import FileReadError


REGEN_WARN_BYTES: int = 50 * 1024
REGEN_HARD_CEILING_BYTES: int = 1024 * 1024


AUTONOMOUS_IMPERATIVE: str = (
    "Do not call AskUserQuestion. For anything unclear, use your best judgment, "
    "record the choice inline in the artifact, and keep going. Produce every "
    "requested artifact below in this single turn before stopping."
)


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
        label="Intake",
        folder="user_input",
        invocation=(
            "Stage 1 (Intake): Claude reads raw_prompt.md and writes a cleaned "
            "revised_prompt.md. No agent."
        ),
        modules=(
            StageModule(
                id="raw_prompt",
                label="raw_prompt.md",
                relative_path="user_input/raw_prompt.md",
                description="User's verbatim original prompt.",
            ),
            StageModule(
                id="revised_prompt",
                label="revised_prompt.md",
                relative_path="user_input/revised_prompt.md",
                description="Cleaned, expanded prompt; raw + every follow-up.",
            ),
        ),
    ),
    StageDef(
        id="interview",
        label="Interview",
        folder="interview",
        invocation=(
            "Stage 2 (Interview): spawn agent_team__interview_manager. The manager "
            "defines an interviewer team; the parent runs the team and forwards "
            "AskUserQuestion calls; consolidated output is interview/qa.md."
        ),
        modules=(
            StageModule(
                id="qa",
                label="qa.md",
                relative_path="interview/qa.md",
                description="Multi-round multi-choice interview transcript.",
            ),
        ),
    ),
    StageDef(
        id="research",
        label="Research",
        folder="findings",
        invocation=(
            "Stage 3 (Research): spawn agent_team__research_manager. The manager "
            "defines research angles; the parent runs them in parallel; manager "
            "synthesizes findings/dossier.md."
        ),
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
                description="Per-angle research notes (one file per angle).",
            ),
        ),
    ),
    StageDef(
        id="spec_compilation",
        label="Spec compilation",
        folder="final_specs",
        invocation=(
            "Stage 4 (Spec compilation): Claude reads revised_prompt + qa + dossier "
            "and writes final_specs/spec.md directly. No agent."
        ),
        modules=(
            StageModule(
                id="spec",
                label="spec.md",
                relative_path="final_specs/spec.md",
                description="Canonical compiled specification.",
            ),
        ),
    ),
    StageDef(
        id="validation_strategy",
        label="Validation strategy",
        folder="validation",
        invocation=(
            "Stage 5 (Validation strategy): spawn agent_team__validation_manager "
            "in strategy mode. The manager defines validation levels; the parent "
            "runs the team; manager synthesizes validation/strategy.md plus per-level files."
        ),
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
                description="Gherkin acceptance scenarios.",
            ),
            StageModule(
                id="bdd_scenarios",
                label="bdd_scenarios.md",
                relative_path="validation/bdd_scenarios.md",
                description="BDD scenario set.",
            ),
            StageModule(
                id="system_tests",
                label="system_tests.md",
                relative_path="validation/system_tests.md",
                description="System-level test descriptions.",
            ),
            StageModule(
                id="unit_tests",
                label="unit_tests.md",
                relative_path="validation/unit_tests.md",
                description="Unit-level test descriptions.",
            ),
            StageModule(
                id="security",
                label="security.md",
                relative_path="validation/security.md",
                description="Security probes and threat model.",
            ),
        ),
    ),
    StageDef(
        id="execution",
        label="Execution",
        folder="(projects)",
        invocation=(
            "Stage 6 (Execution + streaming validation): Claude implements work "
            "units against the spec. For each unit, agent_team__validation_manager "
            "(runtime mode) validates against the strategy. Issues loop back as "
            "revisions, capped at 3 rounds per unit."
        ),
        modules=(
            StageModule(
                id="implementation",
                label="implementation",
                relative_path="(projects/{name}/...)",
                description="Code, tests, README under projects/{name}/.",
            ),
        ),
    ),
)


@dataclass(frozen=True)
class RegenPromptResult:
    prompt: str
    warning: str | None
    selected_stages_count: int
    follow_ups_count: int
    autonomous: bool


def list_stages(project_type: str, project_name: str) -> dict[str, object]:
    stages: list[dict[str, object]] = []
    for stage in STAGE_DEFS:
        stages.append({
            "id": stage.id,
            "label": stage.label,
            "folder": stage.folder,
            "invocation": stage.invocation,
            "modules": [
                {
                    "id": m.id,
                    "label": m.label,
                    "relative_path": m.relative_path,
                    "description": m.description,
                }
                for m in stage.modules
            ],
        })
    return {
        "project_type": project_type,
        "project_name": project_name,
        "stages": stages,
    }


def _project_dir(project_type: str, project_name: str, repo_root: Path) -> Path:
    return repo_root / "specs" / project_type / project_name


def _read_or_empty(path: Path) -> str:
    try:
        if path.exists() and path.is_file():
            return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    return ""


def _list_followups(project_dir: Path) -> list[Path]:
    fu_dir = project_dir / "user_input" / "follow_ups"
    if not fu_dir.is_dir():
        return []
    try:
        files = [p for p in fu_dir.iterdir() if p.is_file() and p.suffix.lower() == ".md"]
    except OSError:
        return []
    return sorted(files, key=lambda p: p.name)


def build_regen_prompt(
    project_type: str,
    project_name: str,
    stage_ids: list[str],
    module_ids: dict[str, list[str]],
    autonomous: bool,
    repo_root: Path,
) -> str:
    project_dir = _project_dir(project_type, project_name, repo_root)

    revised_path = project_dir / "user_input" / "revised_prompt.md"
    raw_path = project_dir / "user_input" / "raw_prompt.md"
    intent_text = _read_or_empty(revised_path)
    intent_label = "user_input/revised_prompt.md"
    if not intent_text:
        intent_text = _read_or_empty(raw_path)
        intent_label = "user_input/raw_prompt.md"

    followups = _list_followups(project_dir)

    parts: list[str] = []
    if autonomous:
        parts.append("# EXECUTION MODE: AUTONOMOUS")
        parts.append("")
        parts.append(AUTONOMOUS_IMPERATIVE)
    else:
        parts.append("# EXECUTION MODE: INTERACTIVE")
    parts.append("")
    parts.append(f"## Project: {project_type}/{project_name}")
    parts.append(f"Project root: `specs/{project_type}/{project_name}/`")
    parts.append("")

    parts.append("### Current intent")
    parts.append(f"Inlined from `{intent_label}`:")
    parts.append("")
    parts.append("```markdown")
    parts.append(intent_text if intent_text else "(no intent file present)")
    parts.append("```")
    parts.append("")
    parts.append("Follow-ups in numerical order:")
    if followups:
        for f in followups:
            parts.append(
                f"- `specs/{project_type}/{project_name}/user_input/follow_ups/{f.name}`"
            )
    else:
        parts.append("- (none)")
    parts.append("")

    parts.append("### Stages to regenerate")
    selected_defs = [s for s in STAGE_DEFS if s.id in stage_ids]
    if not selected_defs:
        parts.append("- (no stages selected)")
    for stage in selected_defs:
        parts.append(f"#### {stage.label} (`{stage.id}`)")
        parts.append(stage.invocation)
        parts.append("")
        chosen_module_ids = module_ids.get(stage.id) or [m.id for m in stage.modules]
        parts.append("Modules in scope:")
        for module in stage.modules:
            if module.id in chosen_module_ids:
                target = (
                    f"specs/{project_type}/{project_name}/{module.relative_path}"
                    if not module.relative_path.startswith("(")
                    else module.relative_path
                )
                parts.append(f"- **{module.label}** — `{target}` — {module.description}")
        parts.append("")

    parts.append("### Constraints")
    parts.append(
        "- Honor every rule in `CLAUDE.md`: state surfaces (CLAUDE.md, .claude/settings*, "
        "specs/{type}/{name}/, .audit/...), agent naming (`agent_team__<role>`), "
        "iteration bounds (3 revisions / 30 minutes per unit)."
    )
    parts.append(
        "- Persist artifacts at canonical paths under "
        f"`specs/{project_type}/{project_name}/...`. No sidecar caches, no hidden state."
    )
    parts.append(
        "- For stages 2 (interview), 3 (research), and 5 (validation strategy), spawn "
        "the named manager agent per CLAUDE.md (`agent_team__interview_manager`, "
        "`agent_team__research_manager`, `agent_team__validation_manager`)."
    )
    parts.append(
        "- **Read-zero contract**: regeneration deletes prior outputs first; new "
        "generation reads only the inputs. Do not read prior `final_specs/spec.md`, "
        "prior `validation/*`, or any prior generated artifact in the stages being "
        "regenerated. Each stage starts from a clean slate so stale assumptions cannot "
        "leak forward."
    )
    parts.append(
        "- Emit `regen.delete.planned`, `regen.delete.completed`, and "
        "`regen.write.completed` events to the run's `events.jsonl` under "
        ".audit/adhoc_agents/{date}/{task_id}/."
    )
    if autonomous:
        parts.append(
            "- Autonomous mode: do NOT call `AskUserQuestion`. Do not stop to ask. "
            "Use best judgment for ambiguous choices and record the decision inline "
            "in the produced artifact."
        )
    else:
        parts.append(
            "- Interactive mode: `AskUserQuestion` is permitted only when intent "
            "cannot be inferred from the existing artifacts."
        )
    parts.append("")

    return "\n".join(parts)


def build_regen_prompt_result(
    project_type: str,
    project_name: str,
    stage_ids: list[str],
    module_ids: dict[str, list[str]],
    autonomous: bool,
    repo_root: Path,
) -> RegenPromptResult:
    prompt = build_regen_prompt(
        project_type, project_name, stage_ids, module_ids, autonomous, repo_root
    )
    encoded_size = len(prompt.encode("utf-8"))
    if encoded_size > REGEN_HARD_CEILING_BYTES:
        raise FileReadError(413, "too_large", kind="too_large")

    project_dir = _project_dir(project_type, project_name, repo_root)
    follow_ups_count = len(_list_followups(project_dir))
    selected_stages_count = len([s for s in STAGE_DEFS if s.id in stage_ids])

    warning: str | None = None
    if encoded_size > REGEN_WARN_BYTES:
        kb = encoded_size / 1024
        warning = (
            f"prompt is {kb:.1f} KB (> 50 KB threshold) — verify your selection "
            "before pasting"
        )

    return RegenPromptResult(
        prompt=prompt,
        warning=warning,
        selected_stages_count=selected_stages_count,
        follow_ups_count=follow_ups_count,
        autonomous=autonomous,
    )
