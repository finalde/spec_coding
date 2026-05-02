# CLAUDE.md — spec_coding monorepo

## Auto-memory lives in this repo, not at user level

**At session start:** read `.claude/memory/MEMORY.md` (the index) and any linked entries that look relevant. These are project-scoped lessons saved by past sessions — feedback, project context, references.

**When saving new memories:** write them to `.claude/memory/`, not to `~/.claude/projects/<slug>/memory/`. Update `.claude/memory/MEMORY.md` to index them. The whole thing is git-tracked so the user can see and review what you remember.

The user-level `~/.claude/projects/<slug>/memory/` path that the default harness uses is **not** the source of truth here — it's intentionally empty for this repo.

---

This repo hosts a **spec-coding workflow** and the platform that drives it. Every non-trivial task moves through two stages:

1. **Planning** — initial prompt → multi-turn interview → spec → research findings → optional adjustments → execution plan (YAML).
2. **Execution** — implement against the plan with parallel validation; revise on validation feedback; final validation pass.

The pipeline is implemented as a team of agents under `.claude/agents/` driven by a single skill at `.claude/skills/agent_team/SKILL.md`. Artifacts persist as plain files under `specs/`. Outputs land in `projects/{name}/` for code or `ai_videos/{name}/` for video work.

## Repo layout

```
spec_coding/
├── CLAUDE.md                 # this file
├── pyproject.toml            # canonical Python deps; `uv sync` reads this
├── requirements.txt          # mirror for the pip fallback path
├── .claude/
│   ├── agents/               # agent_team__* agent definitions
│   ├── memory/               # project-scoped auto-memory (git-tracked)
│   └── skills/agent_team/SKILL.md   # pipeline orchestrator (hand-edited)
├── specs/                    # persistence layer for the spec-coding workflow
│   ├── index.json            # task registry
│   ├── interviews/{task_id}/qa.md
│   ├── specs/{task_id}/{spec.md, adjustments.md}
│   ├── findings/{task_id}/{angle-*.md, dossier.md}
│   └── execution_plans/{task_id}/plan.yaml
├── projects/                 # code projects (root_folder = "projects")
│   └── <project>/{README.md, requirements.txt, main.py, libs/}
├── ai_videos/                # AI video projects (root_folder = "ai_videos")
│   └── <project>/...
└── .audit/                   # local-only, gitignored
    └── adhoc_agents/{YYYY-MM-DD}/{task_id}/
        ├── events.jsonl              # append-only event stream
        ├── spawns/{agent_id}/{prompt.md, tools.json, output.md}
        └── findings_report.md        # mandatory post-mortem
```

## root_folder enum

When creating a new task, the user MUST pick one:

- `projects` — software / tooling outputs land in `projects/{name}/`.
- `ai_videos` — AI video planning + render artifacts land in `ai_videos/{name}/`.

If the task type is unclear, **ask the user**. Do not invent new root folders.

## Agent + skill naming

- All repo-owned skills and agents use the `<prefix>__<name>` pattern with a **double underscore**.
- The spec-coding pipeline uses prefix `agent_team__`. Current roster:
  - `agent_team__interview_manager`
  - `agent_team__spec_compiler`
  - `agent_team__research_manager`
  - `agent_team__execution_plan_compiler`
  - `agent_team__execution_manager`
  - `agent_team__validation_manager`
- Adhoc subagents that managers spawn at runtime are NOT permanent agent files — they are dynamic prompts captured under `.audit/adhoc_agents/{date}/{task_id}/spawns/`.
- The SKILL.md and the six `agent_team__*.md` files are **hand-edited**. Subagents may paraphrase them when needed but must never rewrite them.
- YAML frontmatter `description` field has a hard ceiling of **500 characters**.

## Project rules (under `projects/`)

- One folder per project. No cross-project imports.
- Own `requirements.txt` listing direct dependencies only. Mirror those deps into the root `pyproject.toml` (canonical for `uv sync`) — root `requirements.txt` is kept for the pip fallback path.
- Entry point: `main.py` (preferred), `app.py`, or `run.sh`. Keep entry point thin (~15 lines): parse args, hand off to `libs/`.
- All application logic lives in `libs/<module>.py`. Model domain concepts as classes; use `@dataclass(frozen=True)` for immutable data containers; avoid free-standing module-level functions except for pure utilities.
- Strong typing on every parameter, return value, and class attribute. Use `str | None` syntax (Python 3.10+), not `Optional[str]`.
- README.md required and updated alongside any feature change.

## Execution plan as intermediate code

Specs are concise and human-readable; the execution plan is **explicit, comprehensive, machine-friendly YAML**. The compiler turns spec + findings + adjustments into a plan with numbered work units, explicit dependencies, tool allow-lists, and acceptance checks. The execution manager reads the YAML and spawns one adhoc executor per work unit. This intermediate layer is the determinism wedge — agents do not improvise from the spec; they execute the plan.

## Event stream

`.audit/adhoc_agents/{date}/{task_id}/events.jsonl` is append-only JSONL. Both `agent_team__execution_manager` and `agent_team__validation_manager` write to it; both tail it. Lines parse independently, atomic line-sized appends are safe, and the file doubles as the audit trail. Event types: `exec.unit.started`, `exec.unit.completed`, `exec.unit.failed`, `validation.started`, `validation.issue.raised`, `validation.pass`, `exec.revision.applied`, `manager.iteration.bumped`, `pipeline.halted`.

## Iteration bounds

- Default `max_iterations: 3` per work unit.
- Circuit-break + emit `pipeline.halted` if the same issue id repeats across two iterations, more than five issues stay open after iteration 2, or wall-clock exceeds 30 minutes on a single unit.
- After halt, escalate to the user. Never silently retry past the bound.

## Findings report — mandatory

After every pipeline run, the SKILL writes `.audit/adhoc_agents/{date}/{task_id}/findings_report.md`. Cover: pipeline summary table, agents spawned per phase, durations, surprises/blockers, recommendations. This is the post-mortem and is non-optional.

## General coding rules

- Default to writing no comments. Only add one when the *why* is non-obvious.
- Don't add features, abstractions, or backwards-compatibility shims that the task did not ask for.
- Don't add error handling for cases that cannot happen. Validate at system boundaries (user input, external APIs); trust internal calls.
- Prefer editing existing files over creating new ones. Never create `*.md` documentation files unless explicitly requested.
- Strong typing and OOP per the rules above apply to all Python under `projects/` and `tools/`.
