"""
Canonical six-stage definition (FR-10).

Single source of truth for stage IDs, labels, folders, invocations, and modules.
Returned by GET /api/stages and consumed by the regen-prompt assembler.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Module:
    id: str
    label: str
    relative_path: str
    description: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "relative_path": self.relative_path,
            "description": self.description,
        }


@dataclass(frozen=True)
class Stage:
    id: str
    label: str
    folder: str
    invocation: str
    modules: tuple[Module, ...]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "label": self.label,
            "folder": self.folder,
            "invocation": self.invocation,
            "modules": [m.to_dict() for m in self.modules],
        }


STAGES: tuple[Stage, ...] = (
    Stage(
        id="intake",
        label="intake",
        folder="user_input",
        invocation="Claude rewrites raw_prompt + every follow_ups/*.md → revised_prompt.md (no agent).",
        modules=(
            Module("revised_prompt", "revised_prompt.md", "user_input/revised_prompt.md", "Auto-regenerated from raw + follow-ups."),
        ),
    ),
    Stage(
        id="interview",
        label="interview",
        folder="interview",
        invocation="Claude reads playbooks/interview.md + agent_refs/interview/*.md, identifies probe categories, asks via AskUserQuestion (max 3 rounds), produces qa.md.",
        modules=(
            Module("qa", "qa.md", "interview/qa.md", "Round-by-round Q/A produced by the interview team."),
        ),
    ),
    Stage(
        id="research",
        label="research",
        folder="findings",
        invocation="Claude reads playbooks/research.md + agent_refs/research/*.md, spawns one researcher per business angle in parallel, synthesizes dossier.md.",
        modules=(
            Module("angles", "angle-*.md", "findings/angle-*.md", "Per-angle researcher outputs."),
            Module("dossier", "dossier.md", "findings/dossier.md", "Synthesized cross-angle dossier."),
        ),
    ),
    Stage(
        id="spec",
        label="spec compilation",
        folder="final_specs",
        invocation="Claude reads revised_prompt.md + qa.md + dossier.md and writes final_specs/spec.md directly (no agent).",
        modules=(
            Module("spec", "spec.md", "final_specs/spec.md", "Compiled specification."),
        ),
    ),
    Stage(
        id="validation",
        label="validation strategy",
        folder="validation",
        invocation="Claude reads playbooks/validation.md + agent_refs/validation/*.md, decides applicable levels, spawns level-specialist workers in parallel, consolidates strategy.md.",
        modules=(
            Module("strategy", "strategy.md", "validation/strategy.md", "Top-level multi-level plan."),
            Module("acceptance_criteria", "acceptance_criteria.md", "validation/acceptance_criteria.md", "Gherkin scenarios per AC-NN."),
            Module("bdd_scenarios", "bdd_scenarios.md", "validation/bdd_scenarios.md", "Feature-level behaviors."),
            Module("unit_tests", "unit_tests.md", "validation/unit_tests.md", "Backend + frontend unit cases."),
            Module("system_tests", "system_tests.md", "validation/system_tests.md", "Multi-component scenarios."),
            Module("security", "security.md", "validation/security.md", "Security probes."),
            Module("performance", "performance.md", "validation/performance.md", "Latency / size budgets."),
            Module("accessibility", "accessibility.md", "validation/accessibility.md", "WCAG-anchored a11y checks."),
        ),
    ),
    Stage(
        id="execution",
        label="execution + streaming validation",
        folder="projects",
        invocation="Claude implements work units against final_specs/spec.md and runs the validation/* checks per work unit (3 revision rounds max).",
        modules=(
            Module("project", "projects/{name}/", "projects/{name}/", "Generated project tree (backend + frontend if applicable)."),
        ),
    ),
)


def stages_to_jsonable() -> list[dict]:
    return [s.to_dict() for s in STAGES]


def stage_by_id(stage_id: str) -> Stage | None:
    for s in STAGES:
        if s.id == stage_id:
            return s
    return None
