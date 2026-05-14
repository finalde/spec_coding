from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Module:
    id: str
    label: str
    relative_path: str
    description: str

    def to_payload(self) -> dict[str, Any]:
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

    def to_payload(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "label": self.label,
            "folder": self.folder,
            "invocation": self.invocation,
            "modules": [m.to_payload() for m in self.modules],
        }


CANONICAL_STAGES: tuple[Stage, ...] = (
    Stage(
        id="intake",
        label="1 — Intake",
        folder="user_input",
        invocation="Re-run intake: rebuild user_input/revised_prompt.md = raw + every follow_up in numerical order.",
        modules=(
            Module(
                id="revised_prompt",
                label="revised_prompt.md",
                relative_path="user_input/revised_prompt.md",
                description="Auto-regenerated as raw + every follow-up in numeric order.",
            ),
        ),
    ),
    Stage(
        id="interview",
        label="2 — Interview",
        folder="interview",
        invocation="Re-run interview stage: ask multi-choice questions via AskUserQuestion (interactive) or use best judgment (autonomous), produce interview/qa.md.",
        modules=(
            Module(
                id="qa",
                label="qa.md",
                relative_path="interview/qa.md",
                description="Round → category → Q/A pairs.",
            ),
        ),
    ),
    Stage(
        id="research",
        label="3 — Research",
        folder="findings",
        invocation="Re-run research stage: spawn researcher workers per angle, synthesize findings/dossier.md.",
        modules=(
            Module(
                id="dossier",
                label="dossier.md",
                relative_path="findings/dossier.md",
                description="Synthesis of every researcher angle.",
            ),
            Module(
                id="angles",
                label="angle-*.md",
                relative_path="findings/",
                description="Per-angle research files.",
            ),
        ),
    ),
    Stage(
        id="spec",
        label="4 — Spec compilation",
        folder="final_specs",
        invocation="Re-run spec compilation: parent-direct write of final_specs/spec.md from revised_prompt + qa + dossier.",
        modules=(
            Module(
                id="spec",
                label="spec.md",
                relative_path="final_specs/spec.md",
                description="Functional + non-functional requirements + acceptance summary.",
            ),
        ),
    ),
    Stage(
        id="validation",
        label="5 — Validation strategy",
        folder="validation",
        invocation="Re-run validation strategy: spawn level-specialist workers per level, consolidate validation/strategy.md and per-level files.",
        modules=(
            Module(
                id="strategy",
                label="strategy.md",
                relative_path="validation/strategy.md",
                description="Top-level rollup of every validation level.",
            ),
            Module(
                id="acceptance_criteria",
                label="acceptance_criteria.md",
                relative_path="validation/acceptance_criteria.md",
                description="AC-NN list mapping spec FRs/NFRs to checks.",
            ),
            Module(
                id="bdd_scenarios",
                label="bdd_scenarios.md",
                relative_path="validation/bdd_scenarios.md",
                description="Given/When/Then scenarios per primary flow.",
            ),
            Module(
                id="unit_tests",
                label="unit_tests.md",
                relative_path="validation/unit_tests.md",
                description="Per-lib unit-test contracts.",
            ),
            Module(
                id="system_tests",
                label="system_tests.md",
                relative_path="validation/system_tests.md",
                description="End-to-end / boot-smoke tests.",
            ),
            Module(
                id="security",
                label="security.md",
                relative_path="validation/security.md",
                description="SEC-NN probe set.",
            ),
            Module(
                id="performance",
                label="performance.md",
                relative_path="validation/performance.md",
                description="NFR-1..3 budgets and load tests.",
            ),
            Module(
                id="accessibility",
                label="accessibility.md",
                relative_path="validation/accessibility.md",
                description="WCAG focus / contrast / motion checks.",
            ),
        ),
    ),
    Stage(
        id="execution",
        label="6 — Execution + streaming validation",
        folder="(projects)",
        invocation="Re-run execution: implement work units against the spec, run per-unit validators in parallel.",
        modules=(
            Module(
                id="project",
                label="projects/{name}/",
                relative_path="projects/",
                description="Code + tests + README + Makefile under projects/{name}/.",
            ),
        ),
    ),
)


class Stages:
    @staticmethod
    def list() -> list[Stage]:
        return list(CANONICAL_STAGES)

    @staticmethod
    def by_id(stage_id: str) -> Stage | None:
        for s in CANONICAL_STAGES:
            if s.id == stage_id:
                return s
        return None

    @staticmethod
    def to_payload() -> list[dict[str, Any]]:
        return [s.to_payload() for s in CANONICAL_STAGES]
