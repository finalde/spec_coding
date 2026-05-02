# CLAUDE.md — spec_coding monorepo

This repo hosts a **spec-driven workflow** and the platform that drives it. Every non-trivial task moves through six stages, with artifacts persisted as plain files so any stage can be inspected, edited, or resumed.

## Auto-memory lives in this repo, not at user level

**At session start:** read `.claude/memory/MEMORY.md` (the index) and any linked entries that look relevant.

**When saving new memories:** write them to `.claude/memory/`, not to `~/.claude/projects/<slug>/memory/`. Update `.claude/memory/MEMORY.md` to index them. The whole thing is git-tracked.

The user-level `~/.claude/projects/<slug>/memory/` path is **not** the source of truth here — leave it alone.

## Repo layout

```
spec_coding/
├── CLAUDE.md                              # this file
├── pyproject.toml                         # canonical Python deps; `uv sync` reads this
├── requirements.txt                       # mirror for pip fallback
├── README.md
├── .claude/
│   ├── agents/
│   │   ├── agent_team__interview_manager.md
│   │   ├── agent_team__research_manager.md
│   │   └── agent_team__validation_manager.md
│   ├── memory/                            # project-scoped auto-memory
│   ├── skills/
│   │   └── agent_team/SKILL.md            # pipeline orchestrator
│   └── settings.local.json
├── specs/                                 # persistence for the spec-driven workflow
│   └── {task_type}/{task_name}/
│       ├── user_input/{raw_prompt.md, revised_prompt.md}
│       ├── interview/qa.md
│       ├── findings/{angle-*.md, dossier.md}
│       ├── final_specs/spec.md
│       └── validation/{strategy.md, acceptance_criteria.md, bdd_scenarios.md, ...}
├── projects/                              # task_type=development outputs
│   └── {name}/{README.md, backend/, frontend/}   # or single-folder Python projects
├── ai_videos/                             # task_type=ai_video outputs
│   └── {name}/...
└── .audit/                                # gitignored — runtime logs from manager agents
    └── adhoc_agents/{YYYY-MM-DD}/{task_id}/
        ├── events.jsonl                   # append-only event stream
        └── spawns/{agent_id}/{prompt.md, output.md}
```

## task_type enum

Required when starting a new task. Pick one:

- `development` — software / tooling outputs land in `projects/{name}/`.
- `ai_video` — AI video planning + render artifacts land in `ai_videos/{name}/`.

If the task type is unclear, **ask the user**. Do not invent new task types.

## The six-stage workflow

1. **Intake** — `specs/{type}/{name}/user_input/`. User submits a raw prompt; Claude revises it (cleans grammar, expands abbreviations, surfaces implicit constraints — never invents requirements). No agent.
2. **Interview** — `specs/{type}/{name}/interview/qa.md`. `agent_team__interview_manager` analyzes the use case, dynamically builds an interviewer team (one sub-agent per probe category), asks the user **multi-choice questions** via `AskUserQuestion`, and iterates until the team agrees the requirement is crystal clear.
3. **Research** — `specs/{type}/{name}/findings/`. `agent_team__research_manager` identifies business/use-case research angles, dynamically builds a research team, runs them in parallel, and consolidates a `dossier.md`.
4. **Spec compilation** — `specs/{type}/{name}/final_specs/spec.md`. Claude takes revised_prompt + qa.md + dossier.md and writes the spec directly. No agent.
5. **Validation strategy** — `specs/{type}/{name}/validation/`. `agent_team__validation_manager` (strategy mode) builds a validation team that produces a multi-level plan: high-level acceptance criteria, BDD scenarios, system tests, unit tests, plus any non-functional checks the spec requires.
6. **Execution + streaming validation** — outputs land under `projects/{name}/` or `ai_videos/{name}/`. Claude implements work units against the spec; for each unit, `agent_team__validation_manager` (runtime mode) validates the output against the strategy. Issues loop back as revisions, capped at 3 rounds per unit.

The skill `agent_team` is the single entry point and walks through all six stages. Users invoke it as `/agent_team` (or by asking for a spec-driven task).

## Agent + skill naming

- All repo-owned skills and agents use the `<prefix>__<name>` pattern with a **double underscore**.
- The pipeline orchestrator skill is `agent_team` (no prefix — it's the top-level workflow).
- Permanent agents live under `.claude/agents/` and follow `agent_team__<role>`. Only three exist:
  - `agent_team__interview_manager`
  - `agent_team__research_manager`
  - `agent_team__validation_manager`
- The dynamic sub-agents that managers spawn at runtime are NOT permanent agent files — they are general-purpose agents driven by manager-authored prompts, captured under `.audit/adhoc_agents/{date}/{task_id}/spawns/`.
- YAML frontmatter `description` field has a hard ceiling of **500 characters**.

## Project rules (under `projects/`)

- One folder per project. No cross-project imports.
- Backend + frontend live as `backend/` and `frontend/` subfolders inside the project when both are needed.
- Python: own `requirements.txt` listing direct dependencies only; mirror those into root `pyproject.toml` (canonical for `uv sync`); root `requirements.txt` is the pip fallback.
- Backend entry point: `main.py` (preferred). Keep it thin (~15 lines): parse args, hand off to `libs/`.
- All Python application logic lives in `libs/<module>.py`. Model domain concepts as classes; use `@dataclass(frozen=True)` for immutable data containers; avoid free-standing module-level functions except for pure utilities.
- Strong typing on every parameter, return value, and class attribute. Use `str | None` syntax (Python 3.10+), not `Optional[str]`.
- Frontend: standard React layout. Add `node_modules/` to `.gitignore` when introducing the first frontend.
- README.md required and updated alongside any feature change.

## Event stream

`.audit/adhoc_agents/{date}/{task_id}/events.jsonl` is append-only JSONL. The validation_manager (runtime mode) writes to it. Lines parse independently, atomic line-sized appends are safe, and the file doubles as the audit trail. Event types: `exec.unit.started`, `exec.unit.completed`, `validation.started`, `validation.issue.raised`, `validation.pass`, `exec.revision.applied`, `pipeline.halted`.

## Iteration bounds

- Default 3 revision rounds per work unit before halting.
- Cap interview iterations at 3 rounds total.
- Circuit-break + emit `pipeline.halted` if the same issue repeats across two iterations or wall-clock exceeds 30 minutes on a single unit.
- After halt, escalate to the user. Never silently retry past the bound.

## Task ID convention

When the skill kicks off a pipeline run, build `task_id = "{task_name}-{YYYYMMDD-HHmmss}"`. Use this for `.audit/adhoc_agents/{date}/{task_id}/` paths.

## General coding rules

- Default to writing no comments. Only add one when the *why* is non-obvious.
- Don't add features, abstractions, or backwards-compatibility shims that the task did not ask for.
- Don't add error handling for cases that cannot happen. Validate at system boundaries (user input, external APIs); trust internal calls.
- Prefer editing existing files over creating new ones. Never create `*.md` documentation files unless explicitly requested.
- Strong typing and OOP rules above apply to all Python under `projects/` and `tools/`.
