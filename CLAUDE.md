# CLAUDE.md — spec_coding monorepo

This repo hosts a **spec-driven workflow** and the platform that drives it. Every non-trivial task moves through six stages, with artifacts persisted as plain files so any stage can be inspected, edited, or resumed.

## State surfaces (explicit determinism)

Everything in the spec_driven workflow / `agent_team` pipeline must live in one of these four surfaces. No hidden state, no opaque caches, no other locations are allowed to influence pipeline behavior:

1. **`CLAUDE.md`** — rules and conventions.
2. **`.claude/settings.json`** and **`.claude/settings.local.json`** — harness configuration, hooks, permissions, environment.
3. **`specs/{task_type}/{task_name}/`** — per-task pipeline artifacts (raw + revised prompt, qa.md, findings, spec.md, validation/*).
4. **`.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/`** — runtime spawn logs (`spawns/{agent_id}/{prompt.md, output.md}`), `events.jsonl`, and any per-round answer JSONs that record the round-trip between parent and a manager agent.

Rules that follow:

- **Pipeline status is derived from the filesystem, not from memory.** "Stage N is paused / complete" is true iff Stage N's expected artifacts under `specs/{type}/{name}/` are missing / present. Resume logic must read the tree, never trust a memory entry.
- **Before adding any new mechanism** (a sidecar JSON, a session-scoped store, a lookup file, a side-channel cache), check it lands in one of the four surfaces above. If not, don't add it.
- **Round-trip artifacts** between parent and a manager agent (e.g., `round1_answers.json` produced by the parent after collecting `AskUserQuestion` responses) live under `.audit/adhoc_agents/{date}/{task_id}/`, NOT inside `specs/` (which is reserved for the canonical, user-facing pipeline output).

## Auto-memory is disabled in this repo

**Do NOT use the auto-memory system.** Specifically:

- Do NOT read from or write to `.claude/memory/` (the directory does not exist and should not be recreated).
- Do NOT read from or write to `~/.claude/projects/<slug>/memory/` either — that user-level path is also off-limits for this project.
- If the harness's session-start instructions mention reading `MEMORY.md`, treat the absence of the file as the canonical state: there are no memories.
- If you would otherwise save a memory entry, instead persist the information to one of the four allowed state surfaces above (most often: `CLAUDE.md` for cross-cutting rules, or `specs/{type}/{name}/` for project-specific facts).

**Why:** The user wants pipeline behavior to be 100% explicit, deterministic, and regeneratable from the four state surfaces above. Auto-memory was previously holding a mix of (a) rules already documented in `CLAUDE.md` and (b) pipeline-status snapshots that drift from the filesystem. Both classes of entry are anti-features here — duplicated rules drift, and pipeline-status memory bypasses the "derive status from `specs/` tree" rule. Removing memory entirely makes the four state surfaces the only place state can hide.

**How to apply:**
- Cross-conversation rules / conventions → add to `CLAUDE.md`.
- Per-project intent / facts → add to `specs/{type}/{name}/` (revised_prompt, follow-ups, README, or wherever fits).
- Per-run audit / event data → `.audit/adhoc_agents/{date}/{task_id}/`.
- Harness config / hooks / permissions → `.claude/settings.json` or `.claude/settings.local.json`.
- If you ever feel the urge to save a memory entry, that's a signal that one of the four surfaces is missing the information; put it there instead.

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
│       ├── user_input/
│       │   ├── raw_prompt.md
│       │   ├── revised_prompt.md          # auto-regenerated = raw + every follow-up
│       │   └── follow_ups/NNN-{date}-{slug}.md
│       ├── interview/qa.md
│       ├── findings/{angle-*.md, dossier.md}
│       ├── final_specs/spec.md
│       ├── validation/{strategy.md, acceptance_criteria.md, bdd_scenarios.md, ...}
│       └── changelog.md                   # append-only log of follow-up auto-updates
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

## Follow-up prompt handling

Once a spec-driven project exists, follow-up chat from the user often contains additional intent for that project. Most chat is casual; some is real instruction. Triage every new prompt before doing anything else.

### 1. Triage

- If the prompt is casual chat or a general question with no spec-driven impact, answer normally — no persistence.
- If the prompt is real instruction that could change a known spec-driven project's intent, classify which project it impacts.
- **If ambiguous** (could be project X, Y, or none), **ask the user** which project (or "none") before persisting anything. Do NOT silently pick the most-likely candidate.

### 2. Persist as a follow-up draft

When the prompt impacts project P:
- Path: `specs/{type}/{name}/user_input/follow_ups/NNN-{YYYYMMDD-HHmmss}-{slug}.md` where NNN is the zero-padded sequence (`001`, `002`, …) of follow-ups for that project.
- Contents: abstracted instruction (drop chitchat, keep the spec-relevant content). Prefix with `# Follow-up draft NNN — {YYYY-MM-DD}` and a one-line summary.

### 3. Immediately regenerate `revised_prompt.md`

Always-current revision = `raw_prompt.md` + every `follow_ups/*.md` in numerical order. This is cheap, deterministic, and runs **without confirmation**.

### 4. Scan downstream artifacts for conflicts and gaps

After the revised prompt regenerates, walk every downstream artifact looking for sections that contradict the new requirement OR are missing coverage the new requirement asks for. Order:

1. `interview/qa.md`
2. `findings/dossier.md` and per-angle files
3. `final_specs/spec.md`
4. `validation/strategy.md` and per-level files
5. Generated outputs under `projects/{name}/` (code, tests, README, Makefile) or `ai_videos/{name}/`.

### 5. Auto-update affected sections in place

For each conflict or gap:
- Make the smallest change that resolves the conflict or fills the gap. Surgical edits only — don't regenerate the whole file. Don't ask first.
- **Inline markers** in the edited artifact (e.g., `<!-- auto-updated by follow-up 003 -->`) are **NOT** added by default. If a particular update is invasive enough that you think a local marker is warranted, **ask the user** before adding one.

### 6. Leave a mark in `changelog.md`

Path: `specs/{type}/{name}/changelog.md` — single append-only log per project. Format per follow-up:

```markdown
## Follow-up NNN — {YYYY-MM-DD HH:mm:ss}
Source: user_input/follow_ups/NNN-{slug}.md
Summary: {one line}

Auto-updated:
- {artifact path} — {one-line description of the section edited}
- ...

No conflicts found in: {list of scanned artifacts that needed no change}
```

### 7. Never auto-trigger a full stage regeneration

- Do NOT re-invoke `agent_team__interview_manager`, `agent_team__research_manager`, or `agent_team__validation_manager` from a follow-up.
- Full regen is a user-triggered action only. The `changelog.md` entries are the user's signal that downstream artifacts were touched; if they want a fresh regen, they say so.

## Regeneration prompts & autonomous mode

The `spec_driven` webapp emits **copy-paste regeneration prompts** that the user pastes into Claude Code CLI to re-run one or more stages of a project. Every such prompt opens with one of two execution-mode headers. Claude MUST honor them when it sees them at the top of a turn's input.

### Header contract

- **`# EXECUTION MODE: AUTONOMOUS`** at the top of a pasted prompt means:
  - **Do NOT call `AskUserQuestion`.** Not for clarification, not for "should I do A or B," not for confirmation. The user is not at the keyboard.
  - **For anything ambiguous, use best judgment**, *and record the choice inline in the artifact you produce* (e.g., a one-line "judgment call: chose X because Y" note in the relevant section). The user wants a self-explaining trail of decisions when they come back.
  - **Produce every requested artifact in the same turn before stopping.** Do not pause for confirmation between stages. Iteration bounds (3 revision rounds per unit, 30-minute wall clock) still apply — when a bound trips, halt cleanly with a `pipeline.halted` event and a summary of what was done and why you stopped, but do not interrupt for clarification before the bound is hit.
  - **Still honor every other rule in this file** — state surfaces, agent-spawning contract, follow-up procedure for any *new* user instructions that arrive during the run, etc. Autonomous mode lifts the question-asking restriction; it does not lift any safety, sandbox, or auditability rule.

- **`# EXECUTION MODE: INTERACTIVE`** at the top of a pasted prompt means: default behavior. `AskUserQuestion` may be used when a decision is genuinely ambiguous and the user's intent cannot be inferred from the existing artifacts.

- **No header at all** = treat as INTERACTIVE.

### What the webapp generates

The webapp's `POST /api/regen-prompt` (FR-14c) builds the prompt body. It always inlines the project's current `revised_prompt.md` (or `raw_prompt.md` if there is no revised yet) plus a list of every `user_input/follow_ups/*.md`. So a pasted regen prompt is a self-contained re-statement of intent — a fresh Claude session can act on it without browsing other files first (though it may, of course).

### Default

- The webapp's autonomous-mode toggle defaults to **off** (interactive). Accidental autonomous runs should not be the path of least resistance.
- The toggle's value is persisted in browser `localStorage` under `spec_driven.autonomous_mode.v1`. There is no server-side persistence — autonomous mode is a per-prompt flag, not a global setting.

## Tool scoping and team coordination

Some tools in this harness are **deferred** — their schemas are not loaded at session start and calling them directly fails with `InputValidationError`. They appear by name in the session-start system reminder. To call one, first run `ToolSearch(query="select:<name>", max_results=1)` to load its schema.

**Empirically established scoping (load-bearing for the manager agents):**

- **`AskUserQuestion`** is **parent-only**. Subagents return "no matching deferred tools found" when they ToolSearch for it. The `agent_team__interview_manager` handles this by emitting a JSON question pool back to the parent; the parent forwards questions via `AskUserQuestion` and re-invokes the manager with answers attached as input.
- **`WebSearch` / `WebFetch`** load successfully **at first-level subagent scope** (verified 2026-05-02 inside the four research-angle workers). They also load at parent scope.
- **The `Agent` (subagent-spawn) tool is parent-only.** Subagents do NOT have access to `Agent`; they cannot spawn further nested subagents. This is the most load-bearing finding for the manager pattern: a manager subagent CANNOT actually spawn its own "team" — only the parent can.

**Coordination model that follows from the above** (this is the canonical contract; the three permanent manager agents under `.claude/agents/` all follow it):

1. **The parent is the spawner.** When a stage's manager describes "spawn a team," what actually happens is: the manager-subagent is invoked to *define* the team (angles, categories, validation levels), the parent receives that definition, and the parent calls `Agent` to spawn the workers — possibly in parallel — passing each worker its prompt template plus context paths.
2. **Workers write their own outputs and audit files.** Each worker writes its artifact to the canonical `specs/{type}/{name}/` location AND its spawn audit (`prompt.md` + `output.md`) under `.audit/adhoc_agents/{date}/{task_id}/spawns/{worker_id}/`. No fabricated spawn folders.
3. **The manager does synthesis.** After workers finish, the parent re-invokes the manager (or, if synthesis is mechanical enough, performs it directly) with the worker outputs attached or referenced by path. The manager produces the consolidated artifact (`qa.md`, `dossier.md`, `strategy.md`) and returns its absolute path.
4. **Parent-direct execution** is allowed when the synthesis step is small or when the manager-subagent layer would just shuffle JSON without adding judgment. The manager file documents which steps the parent can elide.

**Universal rules for deferred tools and team coordination:**

- No silent fallbacks. If a tool fails to load, the agent stops and returns a structured failure (`{status, missing, partial_results_if_any}`) — never paraphrases from training data, never invents citations, never dumps multi-choice questions as inline plaintext, never fabricates "subagent" outputs that the manager actually authored itself.
- Plaintext-fallback for `AskUserQuestion` is explicitly forbidden — the multi-choice UX is a hard contract.
- If a manager refers to "spawning a team" in its own prose, that's shorthand — the actual spawn is parent-driven per the model above. Manager files SHOULD make this explicit at the top.
- If a new agent discovers a deferred-tool or scoping finding not listed here, update this section and patch the agent contract before proceeding.

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
