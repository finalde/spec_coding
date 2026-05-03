"""
regen_prompt — POST /api/regen-prompt assembler (FR-10, FR-11, FR-12).

Output prompt structure:

    # EXECUTION MODE: AUTONOMOUS|INTERACTIVE
    [Do not call AskUserQuestion ... single turn before stopping.]   # AUTONOMOUS only

    ## Project — {project_type}/{project_name}

    ## Revised prompt
    <inline revised_prompt.md or raw_prompt.md>

    ## Follow-ups
    - 001-...md
    - 002-...md

    ## Stage: {stage.label} ({stage.id})
    Invocation: {stage.invocation}
    Modules:
    - {module.label}: {module.relative_path}
    ### Pinned items (MUST survive regeneration)        # if <stage>/promoted.md non-empty
    <verbatim contents of promoted.md>
    [...next stage...]

    ### Constraints
    [State surfaces, parent-direct contract, audit events, read-zero contract, ...]

Size policy (FR-12):
- bytes <= 50 KB        -> warning: null
- 50 KB < bytes <= 1 MB -> warning: human-readable
- bytes > 1 MB          -> 413 with {detail: {kind: "too_large", bytes: <count>}}
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .stages import STAGES, stage_by_id

AUTONOMOUS_IMPERATIVE = (
    "Do not call AskUserQuestion. For anything unclear, use your best judgment, "
    "record the choice inline in the artifact, and keep going. "
    "Produce every requested artifact below in this single turn before stopping."
)
WARN_THRESHOLD = 50 * 1024
HARD_LIMIT = 1024 * 1024
READ_ZERO_SENTENCE = "regeneration deletes prior outputs first; new generation reads only the inputs."


class RegenInputError(Exception):
    pass


class TooLargePromptError(Exception):
    def __init__(self, bytes_count: int) -> None:
        super().__init__(f"prompt too large: {bytes_count} bytes")
        self.bytes_count = bytes_count


@dataclass(frozen=True)
class RegenResult:
    prompt: str
    warning: str | None
    selected_stages_count: int
    follow_ups_count: int
    autonomous: bool
    bytes: int

    def to_dict(self) -> dict:
        return {
            "prompt": self.prompt,
            "warning": self.warning,
            "selected_stages_count": self.selected_stages_count,
            "follow_ups_count": self.follow_ups_count,
            "autonomous": self.autonomous,
            "bytes": self.bytes,
        }


_FOLLOW_UP_RE = re.compile(r"^(\d+)-")


def _list_follow_ups(project_dir: Path) -> list[Path]:
    fu_dir = project_dir / "user_input" / "follow_ups"
    if not fu_dir.is_dir():
        return []
    keyed: list[tuple[int, str, Path]] = []
    for p in fu_dir.iterdir():
        if not p.is_file() or p.suffix.lower() != ".md":
            continue
        m = _FOLLOW_UP_RE.match(p.name)
        if not m:
            continue
        keyed.append((int(m.group(1)), p.name, p))
    keyed.sort(key=lambda t: (t[0], t[1]))
    return [t[2] for t in keyed]


def _read_intent_block(project_dir: Path) -> tuple[str, str]:
    revised = project_dir / "user_input" / "revised_prompt.md"
    raw = project_dir / "user_input" / "raw_prompt.md"
    if revised.is_file() and revised.stat().st_size > 0:
        return ("revised_prompt.md", revised.read_text(encoding="utf-8"))
    if raw.is_file():
        return ("raw_prompt.md", raw.read_text(encoding="utf-8"))
    raise RegenInputError("project has neither revised_prompt.md nor raw_prompt.md")


@dataclass(frozen=True)
class RegenPromptAssembler:
    repo_root: Path

    def assemble(
        self,
        project_type: str,
        project_name: str,
        stage_ids: list[str],
        modules: dict[str, list[str]],
        autonomous: bool,
    ) -> RegenResult:
        if not stage_ids:
            raise RegenInputError("at least one stage required")
        for sid in stage_ids:
            if stage_by_id(sid) is None:
                raise RegenInputError(f"unknown stage id: {sid!r}")

        project_dir = self.repo_root / "specs" / project_type / project_name
        if not project_dir.is_dir():
            raise RegenInputError(f"project not found: {project_type}/{project_name}")

        intent_label, intent_body = _read_intent_block(project_dir)
        follow_ups = _list_follow_ups(project_dir)

        out: list[str] = []
        out.append("# EXECUTION MODE: AUTONOMOUS\n" if autonomous else "# EXECUTION MODE: INTERACTIVE\n")
        out.append("\n")
        if autonomous:
            out.append(AUTONOMOUS_IMPERATIVE)
            out.append("\n\n")

        out.append(f"## Project — {project_type}/{project_name}\n\n")

        out.append(f"## Revised prompt — `{intent_label}`\n\n")
        out.append(intent_body.rstrip())
        out.append("\n\n")

        out.append(f"## Follow-ups ({len(follow_ups)})\n\n")
        if follow_ups:
            for fu in follow_ups:
                out.append(f"- `user_input/follow_ups/{fu.name}`\n")
            out.append("\n")
            for fu in follow_ups:
                out.append(f"### `{fu.name}`\n\n")
                out.append(fu.read_text(encoding="utf-8").rstrip())
                out.append("\n\n")
        else:
            out.append("_No follow-ups recorded._\n\n")

        for sid in stage_ids:
            stage = stage_by_id(sid)
            assert stage is not None
            out.append(f"## Stage: {stage.label} (`{stage.id}`)\n\n")
            out.append(f"_Invocation_: {stage.invocation}\n\n")

            selected_module_ids = modules.get(sid, [])
            picked = [m for m in stage.modules if not selected_module_ids or m.id in selected_module_ids]
            if not picked:
                picked = list(stage.modules)
            out.append("Modules selected:\n")
            for m in picked:
                out.append(f"- **{m.label}** (`{m.relative_path}`) — {m.description}\n")
            out.append("\n")

            promoted_path = project_dir / stage.folder / "promoted.md"
            if promoted_path.is_file():
                promoted_text = promoted_path.read_text(encoding="utf-8").strip()
                if promoted_text:
                    out.append("### Pinned items (MUST survive regeneration)\n\n")
                    out.append(promoted_text)
                    out.append("\n\n")

        out.append(self._constraints_section(autonomous))

        prompt = "".join(out)
        encoded = prompt.encode("utf-8")
        size = len(encoded)
        if size > HARD_LIMIT:
            raise TooLargePromptError(size)

        warning: str | None = None
        if size > WARN_THRESHOLD:
            warning = f"prompt is {size / 1024:.1f} KB; review before pasting"

        return RegenResult(
            prompt=prompt,
            warning=warning,
            selected_stages_count=len(stage_ids),
            follow_ups_count=len(follow_ups),
            autonomous=autonomous,
            bytes=size,
        )

    @staticmethod
    def _constraints_section(autonomous: bool) -> str:
        lines = [
            "### Constraints\n",
            "\n",
            "- **State surfaces (CLAUDE.md).** Pipeline state lives in exactly four places: `CLAUDE.md`, "
            "`.claude/settings.json` / `settings.local.json`, `specs/{type}/{name}/`, and "
            "`.audit/adhoc_agents/{date}/{task_id}/`. No hidden state outside these.\n",
            "- **Canonical paths.** Per-task pipeline artifacts live under `specs/{task_type}/{task_name}/`. "
            "Generated outputs land in `projects/{name}/` (development) or `ai_videos/{name}/` (ai_video).\n",
            "- **Parent-direct manager-spawn contract.** The parent (Claude) reads each stage's playbook + "
            "agent_refs inline and spawns workers itself via the `Agent` tool. There is no manager-subagent "
            "layer; subagents cannot themselves spawn further subagents.\n",
            f"- **Read-zero contract.** {READ_ZERO_SENTENCE} Surgical edits to or preservation of prior "
            "outputs is forbidden during regeneration.\n",
            "- **Audit-event protocol.** Before deletion, list each file to be deleted and emit one "
            "`regen.delete.planned` event per line into the run's `events.jsonl`. After deletion, emit "
            "`regen.delete.completed` with the count. After each new file is written, emit "
            "`regen.write.completed` with the path and size.\n",
            "- **AskUserQuestion in autonomous mode is forbidden** (already enforced at the top of this "
            "prompt for AUTONOMOUS runs; restated here so it survives any sectional reading).\n",
            "- **Pinned items survive regeneration.** Any `<stage>/promoted.md` listed above MUST appear "
            "verbatim in the regenerated artifact. Missing pin = critical.\n",
        ]
        return "".join(lines)
