from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libs.exposed_tree import ExposedTree
from libs.safe_resolve import SafeResolver
from libs.stages import Stages

SOFT_LIMIT_BYTES: int = 50 * 1024
HARD_LIMIT_BYTES: int = 1_048_576

_AUTONOMOUS_IMPERATIVE: str = """\
This run is **AUTONOMOUS**. The following imperative is in force for the duration of this turn:

- Do NOT call `AskUserQuestion`. Not for clarification, not for "should I do A or B," not for confirmation. The user is not at the keyboard.
- For anything ambiguous, use best judgment AND record the choice inline in the produced artifact (e.g., `*(judgment call — chose X because Y)*`) so the user has a self-explaining trail.
- Produce every requested artifact in the same turn before stopping. Do not pause for confirmation between stages. Iteration bounds (3 revision rounds per unit, 30-minute wall clock) still apply — when a bound trips, halt cleanly with a `pipeline.halted` event and a summary of what was done and why you stopped.
- Every other rule still applies (state surfaces, agent-spawning contract, follow-up procedure for new instructions arriving mid-run). Autonomous mode lifts only the question-asking restriction.
"""

_READ_ZERO_CONTRACT: str = """\
A regeneration deletes prior outputs first and rewrites from scratch — the regenerated stage's prior outputs MUST be treated as deleted before the new generation runs. Surgical preservation of prior text is **forbidden** during regen — it makes the output a function of (input ∧ all previous runs) and defeats the workflow.

The regenerated stage reads ONLY:
1. The current stage's *input* artifacts (canonical outputs of prior stages).
2. `CLAUDE.md` and shared `.claude/` context (skill, playbooks, refs).
3. The user-input layer (`raw_prompt.md` + every `user_input/follow_ups/*.md`).
4. The current stage's `<stage>/promoted.md` sidecar, if present.

Per-stage delete-then-regenerate contract:

| Stage | Delete first | Preserve | Inputs |
|---|---|---|---|
| 1 — Intake | (none — `revised_prompt.md` rewritten in place from raw + follow-ups) | n/a | `user_input/raw_prompt.md`, `user_input/follow_ups/*.md` |
| 2 — Interview | `interview/qa.md` | `interview/promoted.md` | `user_input/revised_prompt.md`, `interview/promoted.md`, `CLAUDE.md`, `.claude/skills/agent_team/{SKILL.md, playbooks/interview.md}`, `.claude/agent_refs/{interview,project}/*.md` |
| 3 — Research | `findings/*` except `promoted.md` | `findings/promoted.md` | `revised_prompt.md`, `interview/qa.md`, `findings/promoted.md`, `CLAUDE.md`, `.claude/skills/agent_team/{SKILL.md, playbooks/research.md}`, `.claude/agent_refs/{research,project}/*.md` |
| 4 — Spec | `final_specs/spec.md` | `final_specs/promoted.md` | `revised_prompt.md`, `interview/qa.md`, `findings/dossier.md` (+ angles if useful), `final_specs/promoted.md` |
| 5 — Validation | every file under `validation/` except `promoted.md` | `validation/promoted.md` | `final_specs/spec.md`, `validation/promoted.md`, `CLAUDE.md`, `.claude/skills/agent_team/{SKILL.md, playbooks/validation.md}`, `.claude/agent_refs/{validation,project}/*.md` |
| 6 — Execution | the entire `projects/{name}/` or `ai_videos/{name}/` folder | (no v1 promoted.md in stage 6) | `final_specs/spec.md`, every file under `validation/`, `CLAUDE.md`, `.claude/agent_refs/project/*.md` |

Operational notes:

- Delete is real `rm -rf`-equivalent, not logical "treat as missing." Stale bytes are how surgical-edit regen creeps back in. `<stage>/promoted.md` stays in Preserve, never Delete.
- Multi-stage regen is sequential. Delete each stage's outputs the moment that stage runs (after inputs are confirmed), not all up-front; otherwise stage N+1 is missing its inputs.
- Selective module regen. If the prompt selects only some stage modules (e.g., only `validation/security.md` + `performance.md`), delete only those files. Default copy-paste prompts select all.
- `changelog.md` and `.audit/` are NEVER regen outputs. They are the audit log; they get appended to with a record of what was deleted/regenerated.

Audit-event protocol for any regen: emit `regen.delete.planned` (one line per file before delete), `regen.delete.completed` (with count), `regen.write.completed` (path + size after write) into `events.jsonl`.

Pinned items survive regeneration: `<stage>/promoted.md` is an INPUT, not an output. Every pin appears verbatim in the regenerated artifact at the natural insertion point. Orphaned pins (insertion point gone) go to a `## Pinned items (orphaned)` section at the end of the originally-pinned source file. NEVER silently dropped.
"""


class PromptTooLarge(Exception):
    pass


@dataclass(frozen=True)
class AssembledPrompt:
    prompt: str
    warning: dict[str, Any] | None
    selected_stages_count: int
    follow_ups_count: int
    autonomous: bool
    bytes_len: int

    def to_payload(self) -> dict[str, Any]:
        return {
            "prompt": self.prompt,
            "warning": self.warning,
            "selected_stages_count": self.selected_stages_count,
            "follow_ups_count": self.follow_ups_count,
            "autonomous": self.autonomous,
            "bytes": self.bytes_len,
        }


class RegenPromptBuilder:
    def __init__(self, exposed: ExposedTree, resolver: SafeResolver) -> None:
        self._exposed = exposed
        self._resolver = resolver
        self._root = exposed.root

    def build(
        self,
        project_type: str,
        project_name: str,
        stages: list[str],
        modules: dict[str, list[str]] | None,
        autonomous: bool,
    ) -> AssembledPrompt:
        modules = modules or {}
        parts: list[str] = []
        header = "# EXECUTION MODE: AUTONOMOUS" if autonomous else "# EXECUTION MODE: INTERACTIVE"
        parts.append(header)
        parts.append("")
        if autonomous:
            parts.append(_AUTONOMOUS_IMPERATIVE)

        parts.append(f"## Project")
        parts.append(f"")
        parts.append(f"- type: `{project_type}`")
        parts.append(f"- name: `{project_name}`")
        parts.append("")

        revised_block, used_raw_fallback = self._inline_user_intent(project_type, project_name)
        parts.append(revised_block)

        follow_ups_block, follow_ups_count = self._inline_follow_ups(project_type, project_name)
        parts.append(follow_ups_block)

        selected_stages: list[str] = []
        for stage_id in stages:
            stage = Stages.by_id(stage_id)
            if stage is None:
                continue
            selected_stages.append(stage_id)
            stage_section = self._render_stage_section(
                project_type, project_name, stage_id, modules.get(stage_id)
            )
            parts.append(stage_section)

        parts.append(self._constraints_section(selected_stages))

        prompt = "\n".join(parts).rstrip() + "\n"
        size = len(prompt.encode("utf-8"))

        if size >= HARD_LIMIT_BYTES:
            raise PromptTooLarge(size)

        warning: dict[str, Any] | None = None
        if size > SOFT_LIMIT_BYTES:
            warning = {
                "kind": "approaching_ceiling",
                "bytes": size,
                "soft_limit": SOFT_LIMIT_BYTES,
            }

        return AssembledPrompt(
            prompt=prompt,
            warning=warning,
            selected_stages_count=len(selected_stages),
            follow_ups_count=follow_ups_count,
            autonomous=autonomous,
            bytes_len=size,
        )

    def _inline_user_intent(self, project_type: str, project_name: str) -> tuple[str, bool]:
        revised_rel = f"specs/{project_type}/{project_name}/user_input/revised_prompt.md"
        raw_rel = f"specs/{project_type}/{project_name}/user_input/raw_prompt.md"
        revised_path = self._safe_path(revised_rel)
        raw_path = self._safe_path(raw_rel)
        if revised_path is not None and revised_path.is_file():
            body = revised_path.read_text(encoding="utf-8").rstrip()
            return (
                f"## Revised prompt\n\n_From `{revised_rel}` (raw + every follow-up in numeric order)._\n\n{body}\n",
                False,
            )
        if raw_path is not None and raw_path.is_file():
            body = raw_path.read_text(encoding="utf-8").rstrip()
            return (
                f"## Raw prompt (no revised yet)\n\n_From `{raw_rel}`._\n\n{body}\n",
                True,
            )
        return ("## Revised prompt\n\n_(no user_input files found)_\n", False)

    def _inline_follow_ups(self, project_type: str, project_name: str) -> tuple[str, int]:
        rel_dir = f"specs/{project_type}/{project_name}/user_input/follow_ups"
        dir_path = self._safe_path(rel_dir)
        if dir_path is None or not dir_path.is_dir():
            return ("## Follow-ups\n\n_(no follow-ups present)_\n", 0)
        files = sorted(
            (p for p in dir_path.iterdir() if p.is_file() and p.suffix == ".md"),
            key=self._follow_up_sort_key,
        )
        if not files:
            return ("## Follow-ups\n\n_(no follow-ups present)_\n", 0)
        chunks: list[str] = ["## Follow-ups", "", f"_{len(files)} follow-up(s) inlined in numeric order._", ""]
        for f in files:
            body = f.read_text(encoding="utf-8").rstrip()
            chunks.append(f"### Follow-up: `{f.name}`")
            chunks.append("")
            chunks.append(body)
            chunks.append("")
        return ("\n".join(chunks), len(files))

    @staticmethod
    def _follow_up_sort_key(p: Path) -> tuple[int, str]:
        name = p.name
        prefix = name.split("-", 1)[0]
        try:
            return (int(prefix), name)
        except ValueError:
            return (10**9, name)

    def _render_stage_section(
        self,
        project_type: str,
        project_name: str,
        stage_id: str,
        selected_modules: list[str] | None,
    ) -> str:
        stage = Stages.by_id(stage_id)
        if stage is None:
            return ""
        modules = list(stage.modules)
        if selected_modules is not None:
            sel = set(selected_modules)
            modules = [m for m in modules if m.id in sel]
        chunks: list[str] = [f"## Stage {stage.label}", ""]
        chunks.append(f"_Folder:_ `{stage.folder}`")
        chunks.append("")
        chunks.append(f"_Invocation:_ {stage.invocation}")
        chunks.append("")
        chunks.append("_Modules selected:_")
        chunks.append("")
        if modules:
            for m in modules:
                chunks.append(f"- `{m.relative_path}` — {m.label}: {m.description}")
        else:
            chunks.append("- (no modules selected)")
        chunks.append("")

        promoted_rel = f"specs/{project_type}/{project_name}/{stage.folder}/promoted.md"
        promoted_path = self._safe_path(promoted_rel)
        if promoted_path is not None and promoted_path.is_file():
            body = promoted_path.read_text(encoding="utf-8").strip()
            if body:
                chunks.append("### Pinned items (MUST survive regeneration)")
                chunks.append("")
                chunks.append(f"_From `{promoted_rel}` — INPUT, not output. Insert verbatim at natural points; orphans go to a trailing `## Pinned items (orphaned)` section in the originally-pinned source file._")
                chunks.append("")
                chunks.append(body)
                chunks.append("")
        return "\n".join(chunks)

    def _constraints_section(self, selected_stages: list[str]) -> str:
        chunks: list[str] = ["### Constraints", ""]
        chunks.append(_READ_ZERO_CONTRACT)
        chunks.append("")
        if selected_stages:
            chunks.append(f"_Selected stages this run:_ {', '.join(selected_stages)}.")
            chunks.append("")
        return "\n".join(chunks)

    def _safe_path(self, rel: str) -> Path | None:
        return self._resolver.resolve(rel)
