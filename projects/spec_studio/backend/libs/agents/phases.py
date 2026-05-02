from __future__ import annotations

from ..models import Phase, Task


def build_phase_prompt(phase: Phase, task: Task) -> str:
    """Build the phase-specific prompt the SKILL would use.

    Each prompt instructs Claude to invoke a specific agent_team__* agent
    against this task's persisted artifacts. Prompts deliberately reference
    files on disk rather than pasting content — agents read inputs themselves.
    """
    task_id = task.id
    builders = {
        Phase.INTERVIEW: _interview_prompt,
        Phase.SPEC: _spec_prompt,
        Phase.RESEARCH: _research_prompt,
        Phase.PLAN: _plan_prompt,
        Phase.EXECUTE: _execute_prompt,
        Phase.FINAL_VALIDATE: _final_validate_prompt,
    }
    if phase not in builders:
        raise ValueError(f"phase {phase} is not directly invokable as an agent run")
    return builders[phase](task_id, task)


def _interview_prompt(task_id: str, task: Task) -> str:
    return (
        f"Use the agent_team__interview_manager agent to run a multi-turn interview "
        f"for task '{task_id}'.\n\n"
        f"Initial user prompt:\n> {task.initial_prompt}\n\n"
        f"Read CLAUDE.md and specs/interviews/{task_id}/initial_prompt.md for context. "
        f"Persist consolidated Q&A to specs/interviews/{task_id}/qa.md using the format "
        f"defined in .claude/agents/agent_team__interview_manager.md. "
        f"This is round 1 — present the question batch and stop. The platform will "
        f"surface answers and re-invoke this phase for any follow-up rounds."
    )


def _spec_prompt(task_id: str, task: Task) -> str:
    return (
        f"Use the agent_team__spec_compiler agent for task '{task_id}'.\n\n"
        f"Inputs: specs/interviews/{task_id}/qa.md, CLAUDE.md.\n"
        f"Output: specs/specs/{task_id}/spec.md.\n\n"
        f"Honor the fixed section order from .claude/agents/agent_team__spec_compiler.md "
        f"and surface anything ambiguous under ## Open Questions instead of inventing facts."
    )


def _research_prompt(task_id: str, task: Task) -> str:
    return (
        f"Use the agent_team__research_manager agent for task '{task_id}'.\n\n"
        f"Read specs/specs/{task_id}/spec.md, choose 3–8 angles dynamically, spawn one "
        f"adhoc researcher per angle in parallel, and consolidate to "
        f"specs/findings/{task_id}/dossier.md.\n\n"
        f"Capture every adhoc spawn under .audit/adhoc_agents/{{date}}/{task_id}/spawns/. "
        f"You do NOT research yourself — manager-only role."
    )


def _plan_prompt(task_id: str, task: Task) -> str:
    return (
        f"Use the agent_team__execution_plan_compiler agent for task '{task_id}'.\n\n"
        f"Inputs: specs/specs/{task_id}/spec.md, specs/findings/{task_id}/dossier.md, "
        f"and specs/specs/{task_id}/adjustments.md if present.\n"
        f"Output: specs/execution_plans/{task_id}/plan.yaml.\n\n"
        f"Follow the YAML schema in .claude/agents/agent_team__execution_plan_compiler.md. "
        f"Carry unresolved Open Questions verbatim from spec.md into plan.yaml — do not invent answers."
    )


def _execute_prompt(task_id: str, task: Task) -> str:
    output_root = f"{task.root_folder.value}/{task.name}"
    return (
        f"Run agent_team__execution_manager and agent_team__validation_manager IN PARALLEL "
        f"for task '{task_id}'.\n\n"
        f"Plan: specs/execution_plans/{task_id}/plan.yaml.\n"
        f"Output root: {output_root}/.\n"
        f"Event stream: .audit/adhoc_agents/{{date}}/{task_id}/events.jsonl (append + tail).\n\n"
        f"Both managers spawn adhoc workers per work unit and coordinate exclusively through "
        f"the event stream. Honor revision_policy from the plan and circuit-break per the rules "
        f"in CLAUDE.md."
    )


def _final_validate_prompt(task_id: str, task: Task) -> str:
    return (
        f"Run a final holistic validation pass via agent_team__validation_manager for task "
        f"'{task_id}'. Spawn validators for requirements_compliance, cross_unit_integration, "
        f"documentation, and audit_trail. Emit validation.final.pass on the event stream when "
        f"clean, otherwise validation.issue.raised events with severity tags."
    )
