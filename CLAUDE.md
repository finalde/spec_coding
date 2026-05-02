# CLAUDE.md — spec_coding monorepo

This repo hosts a **spec-driven workflow** and the platform that drives it. Every non-trivial task moves through six stages, with artifacts persisted as plain files so any stage can be inspected, edited, or resumed.

## State surfaces (explicit determinism)

Everything in the spec_driven workflow / `agent_team` pipeline must live in one of these four surfaces. No hidden state, no opaque caches, no other locations are allowed to influence pipeline behavior:

1. **`CLAUDE.md`** — rules and conventions.
2. **`.claude/settings.json`** and **`.claude/settings.local.json`** — harness configuration, hooks, permissions, environment.
3. **`specs/{task_type}/{task_name}/`** — per-task pipeline artifacts (raw + revised prompt, qa.md, findings, spec.md, validation/*).
4. **`.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/`** — runtime spawn logs (`spawns/{worker_id}/{prompt.md, output.md}`), `events.jsonl`, and any per-round answer JSONs that record the round-trip between the parent and the user (e.g., interview answers between rounds).

Rules that follow:

- **Pipeline status is derived from the filesystem, not from memory.** "Stage N is paused / complete" is true iff Stage N's expected artifacts under `specs/{type}/{name}/` are missing / present. Resume logic must read the tree, never trust a memory entry.
- **Before adding any new mechanism** (a sidecar JSON, a session-scoped store, a lookup file, a side-channel cache), check it lands in one of the four surfaces above. If not, don't add it.
- **Round-trip artifacts** between the parent and workers / the user (e.g., `round1_answers.json` produced by the parent after collecting `AskUserQuestion` responses, or aggregated per-worker outputs) live under `.audit/adhoc_agents/{date}/{task_id}/`, NOT inside `specs/` (which is reserved for the canonical, user-facing pipeline output).

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
│   ├── agent_refs/                        # accumulated institutional memory per stage
│   │   ├── interview/{general.md, <task_type>.md}
│   │   ├── research/{general.md, <task_type>.md}
│   │   └── validation/{general.md, <task_type>.md}
│   ├── skills/
│   │   └── agent_team/
│   │       ├── SKILL.md                   # pipeline orchestrator (parent-direct)
│   │       └── playbooks/{interview.md, research.md, validation.md}
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
└── .audit/                                # gitignored — runtime logs from worker spawns
    └── adhoc_agents/{YYYY-MM-DD}/{task_id}/
        ├── events.jsonl                   # append-only event stream
        └── spawns/{worker_id}/{prompt.md, output.md}
```

## task_type enum

Required when starting a new task. Pick one:

- `development` — software / tooling outputs land in `projects/{name}/`.
- `ai_video` — AI video planning + render artifacts land in `ai_videos/{name}/`.

If the task type is unclear, **ask the user**. Do not invent new task types.

## The six-stage workflow

There is no separate "manager" subagent layer. The parent (Claude in the `agent_team` skill) IS the manager at every stage — it reads the relevant playbook + agent_refs, decides team composition, spawns workers in parallel via the `Agent` tool, and synthesizes the outputs itself. The manager-subagent indirection that previously sat between the parent and the workers has been removed for parallelism, lower latency, and lower communication cost.

1. **Intake** — `specs/{type}/{name}/user_input/`. The user submits a raw prompt; Claude revises it (cleans grammar, expands abbreviations, surfaces implicit constraints — never invents requirements). No workers.
2. **Interview** — `specs/{type}/{name}/interview/qa.md`. Per `.claude/skills/agent_team/playbooks/interview.md`, Claude identifies probe categories, generates a multi-choice question pool (directly, or via parallel category workers when categories diverge), asks the user via `AskUserQuestion`, and iterates up to 3 rounds.
3. **Research** — `specs/{type}/{name}/findings/`. Per `.claude/skills/agent_team/playbooks/research.md`, Claude identifies 3–6 business/use-case research angles, spawns one researcher worker per angle in parallel via `Agent`, and synthesizes `dossier.md`.
4. **Spec compilation** — `specs/{type}/{name}/final_specs/spec.md`. Claude takes revised_prompt + qa.md + dossier.md and writes the spec directly. No workers.
5. **Validation strategy** — `specs/{type}/{name}/validation/`. Per `.claude/skills/agent_team/playbooks/validation.md` (strategy mode), Claude decides which validation levels apply, spawns one level-specialist worker per level in parallel via `Agent`, and consolidates `strategy.md`.
6. **Execution + streaming validation** — outputs land under `projects/{name}/` or `ai_videos/{name}/`. Claude implements work units against the spec; for each unit, per `.claude/skills/agent_team/playbooks/validation.md` (runtime mode), Claude spawns validators in parallel via `Agent` against the strategy. Issues loop back as revisions, capped at 3 rounds per unit.

The skill `agent_team` is the single entry point and walks through all six stages. Users invoke it as `/agent_team` (or by asking for a spec-driven task).

## Skill + playbook naming

- All repo-owned skills use the `<prefix>__<name>` pattern with a **double underscore**.
- The pipeline orchestrator skill is `agent_team` (no prefix — it's the top-level workflow).
- Stage playbooks live under `.claude/skills/agent_team/playbooks/{interview,research,validation}.md`. They are NOT subagent definitions — they are procedural runbooks the parent reads inline at the start of each stage.
- The `.claude/agents/` folder is reserved for any future permanent subagent definitions; it is currently empty because every spec-driven stage is parent-direct.
- The workers the parent spawns at runtime (per-category interviewer workers, per-angle researcher workers, per-level validation workers, per-work-unit validators) are general-purpose subagents driven by playbook-defined prompts, captured under `.audit/adhoc_agents/{date}/{task_id}/spawns/`.
- YAML frontmatter `description` field has a hard ceiling of **500 characters**.

## Stage playbooks and reference docs

A fifth state surface, layered on top of the four declared at the top of this file:

5. **Stage playbooks and refs** — per-stage procedural runbooks plus per-stage accumulated institutional memory. Two folders, intentionally separate:
   - `.claude/skills/agent_team/playbooks/{interview,research,validation}.md` — the procedural runbook for each coordinated stage. The parent reads its stage's playbook before acting on that stage. These are the contract for what the parent does.
   - `.claude/agent_refs/{interview,research,validation}/{general.md, <task_type>.md}` — accumulated institutional memory the parent must consult before deciding team composition. `general.md` holds task-type-agnostic principles; `<task_type>.md` (e.g., `development.md`, `ai_video.md`) holds lessons learned from past runs of that task type. These are what the parent has learned, not what it does.

Rules:

- For each coordinated stage (2, 3, 5, 6), the parent MUST read both files BEFORE acting: the playbook for the stage AND `general.md` for the stage's folder under `agent_refs/`. When `<task_type>.md` exists for the current task's type under the same folder, that is also required reading.
- The parent records the absolute paths it actually read in a `pre_reading_consulted` array on the run's first `events.jsonl` event for that stage (or per-work-unit `validation.started` event in stage 6). A missing or empty array is a critical failure — it means institutional memory wasn't loaded.
- Per-task-type rules **override** the playbook's defaults when they conflict. The playbook is the contract; the refs are what has been *learned*. Different lifecycles.
- Updates to ref files are surgical (one new principle, one new severity row, one new "required validation move"). They cite the run id where the lesson surfaced. Wholesale rewrites are anti-patterns — the goal is to grow institutional memory, not to refactor it.
- The `EXPOSED_TREE` of the spec_driven webapp includes both `.claude/skills/agent_team/playbooks/*.md` and `.claude/agent_refs/**/*.md`, so users can view and edit them alongside `CLAUDE.md` via the same UX.
- Why two folders, not one: playbooks are **what the parent does**; refs are **what the parent has learned**. As lessons accumulate, embedding everything in the playbook would balloon it past readability.

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

`.audit/adhoc_agents/{date}/{task_id}/events.jsonl` is append-only JSONL. The parent writes to it during stage 6 runtime validation (and at the start of each coordinated stage to record `pre_reading_consulted`). Lines parse independently, atomic line-sized appends are safe, and the file doubles as the audit trail. Event types: `exec.unit.started`, `exec.unit.completed`, `validation.started`, `validation.issue.raised`, `validation.pass`, `validation.requires_manual_walkthrough`, `exec.revision.applied`, `pipeline.halted`, `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`.

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

- Do NOT re-run stage 2, 3, or 5 in their full coordinated form (with worker spawns and team synthesis) from a follow-up. Surgical patches per the steps above are fine; full regeneration is not.
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

### Regeneration semantics: read-zero from prior outputs

When a regeneration prompt asks Claude to re-run one or more stages, the regenerated stage's prior outputs MUST be treated as deleted. The regenerated stage depends ONLY on:

1. The current stage's *input* artifacts (the canonical outputs of the prior stages, used as inputs).
2. `CLAUDE.md` and shared `.claude/` context (skill definition, stage playbooks, agent_refs).
3. The user-input layer (`raw_prompt.md` + every `user_input/follow_ups/*.md`).
4. **The current stage's `<stage>/promoted.md` sidecar**, when present (see "Pinned items survive regeneration" below).

**Surgical edits to / preservation of prior outputs is forbidden during regeneration.** The prior file is not "the starting point you tweak" — it is "the thing you delete and rewrite from scratch." A regeneration that preserves prior text drifts away from the inputs and becomes a function of (input ∧ all previous runs), which defeats the point of the workflow.

Per-stage delete-then-regenerate contract:

| Stage being regenerated | Files to delete first | Files to preserve (NEVER delete) | Inputs the new generation reads |
|-------------------------|------------------------|----------------------------------|---------------------------------|
| 1 — Intake | (none — `revised_prompt.md` is rewritten in place from raw + follow-ups; this stage has no other prior outputs) | (n/a) | `user_input/raw_prompt.md`, every `user_input/follow_ups/*.md` |
| 2 — Interview | `interview/qa.md` | `interview/promoted.md` | `user_input/revised_prompt.md`, `interview/promoted.md`, `CLAUDE.md`, `.claude/skills/agent_team/SKILL.md`, `.claude/skills/agent_team/playbooks/interview.md`, `.claude/agent_refs/interview/*.md` |
| 3 — Research | every file under `findings/` (`dossier.md` + every `angle-*.md`) **except `findings/promoted.md`** | `findings/promoted.md` | `user_input/revised_prompt.md`, `interview/qa.md`, `findings/promoted.md`, `CLAUDE.md`, `.claude/skills/agent_team/SKILL.md`, `.claude/skills/agent_team/playbooks/research.md`, `.claude/agent_refs/research/*.md` |
| 4 — Spec compilation | `final_specs/spec.md` | `final_specs/promoted.md` | `user_input/revised_prompt.md`, `interview/qa.md`, `findings/dossier.md` (+ `findings/angle-*.md` if useful), `final_specs/promoted.md` |
| 5 — Validation strategy | every file under `validation/` (`strategy.md`, `acceptance_criteria.md`, `bdd_scenarios.md`, `unit_tests.md`, `system_tests.md`, `security.md`, `performance.md`, `accessibility.md`, etc.) **except `validation/promoted.md`** | `validation/promoted.md` | `final_specs/spec.md`, `validation/promoted.md`, `CLAUDE.md`, `.claude/skills/agent_team/SKILL.md`, `.claude/skills/agent_team/playbooks/validation.md`, `.claude/agent_refs/validation/*.md` |
| 6 — Execution + streaming validation | the entire output project folder (`projects/{name}/` for `task_type=development`, or `ai_videos/{name}/` for `task_type=ai_video`) | (no promoted.md in stage 6 — out of scope for v1) | `final_specs/spec.md`, every file under `validation/`, `CLAUDE.md` |

### Pinned items survive regeneration

Each spec-pipeline stage (interview, findings, final_specs, validation) supports a `promoted.md` sidecar in its stage folder. When the user pins (📌) an atomic item — a Q/A pair, a recommendation bullet, an FR-NN / NFR-NN / AC-NN / SYS-NN block — that pin is appended to `<stage>/promoted.md`. Pins are written by the spec_driven webapp's `POST /api/promote` endpoint and removed by `DELETE /api/promote`.

Contract on regeneration:

1. **`<stage>/promoted.md` is an INPUT, not an output.** It is NOT deleted by the read-zero contract. The Files-to-preserve column above is load-bearing.
2. **Every pin in `<stage>/promoted.md` MUST appear verbatim in the regenerated artifact.** The regen agent reads the pinned content and inserts it at the natural location for its source-file/id metadata. Newly-generated content for a pinned slot is dropped (promoted always wins).
3. **If a pin's natural insertion point no longer exists** (e.g., the pinned `AC-7` no longer appears among the regenerated ACs), the agent appends the pin verbatim to a `## Pinned items (orphaned)` section at the end of the originally-pinned source file. The pin is NEVER silently dropped.
4. **Editing a pin updates `promoted.md` only.** The generated artifact is not touched until the next regeneration. The user accepts that the two versions can drift between regens; the drift is resolved by running stage N regen.
5. **`<stage>/promoted.md` is itself viewable and editable** through the spec_driven webapp via the same path-sandbox as any other artifact. It is NOT a regen target — there is no `POST /api/regen-prompt` mode that rebuilds it.
6. **Stage 6 (project code under `projects/{name}/`) does NOT support promotion in v1.** Out of scope. A `projects/{name}/promoted.md` would have a different granularity story (per file? per function?) and is deferred.

Operational notes:

- **Delete is a real `rm -rf`-equivalent action**, not a logical "treat as missing." After delete, the file MUST not exist on disk; regeneration writes the new file fresh. Stale bytes are how surgical-edit regen creeps back in. Note: `<stage>/promoted.md` is in the Preserve column, not the Delete column — it must NOT be removed.
- **Multi-stage regeneration is sequential.** When the regen prompt selects multiple stages, delete each stage's outputs at the moment that stage runs (after its inputs are confirmed present), not all up-front. Otherwise stage N+1 will be missing its inputs while stage N is being regenerated.
- **Selective module regeneration.** If the regen prompt selects only some of a stage's modules (e.g., regenerate only `validation/security.md` and `validation/performance.md`), delete only those module files, not every file in the stage folder. The default in copy-paste prompts is "all modules selected" → delete the entire stage folder.
- **`changelog.md` and `.audit/` are NOT regeneration outputs** — they are the audit log. They are never deleted as part of a regeneration; they are appended to with a new entry that records what got deleted and what got regenerated.
- **Project README and Makefile under `projects/{name}/`** are part of stage 6 outputs and ARE deleted along with the rest of the project folder. The new generation rebuilds them from the spec.
- **The `agent_team` skill, its stage playbooks (`.claude/skills/agent_team/playbooks/*.md`), and the agent_refs (`.claude/agent_refs/*/*.md`)** are NOT regeneration outputs — they are part of the harness/shared context. Never deleted by a project-scoped regeneration.

Why: surgical edits accumulate path-dependent decisions that diverge from the inputs. The user wants regeneration runs to be a pure function of inputs, so the regen output is a faithful test of "what would these inputs produce today." If the inputs are insufficient to reproduce a load-bearing prior decision, that's a signal the inputs need a follow-up — not a signal to copy the decision forward silently.

How to apply:
- Before any regeneration, list the files that will be deleted and emit a `regen.delete.planned` event (one line per file) into the run's `events.jsonl`.
- After deletion, emit `regen.delete.completed` with the count.
- After the new generation writes the file, emit `regen.write.completed` with the new file's path and size.
- The webapp's regen-prompt assembly (`projects/spec_driven/backend/libs/regen_prompt.py`) must include this contract verbatim in the constraints section of every assembled prompt.

## Tool scoping and team coordination

Some tools in this harness are **deferred** — their schemas are not loaded at session start and calling them directly fails with `InputValidationError`. They appear by name in the session-start system reminder. To call one, first run `ToolSearch(query="select:<name>", max_results=1)` to load its schema.

**Empirically established scoping (load-bearing for the parent-direct workflow):**

- **`AskUserQuestion`** is **parent-only**. Subagents return "no matching deferred tools found" when they ToolSearch for it. This is precisely why stage 2 (interview) is parent-direct — only the parent can ask the user questions, so there is no value in sandwiching a manager subagent between the parent and the `AskUserQuestion` call.
- **`WebSearch` / `WebFetch`** load successfully **at first-level subagent scope** (verified 2026-05-02 inside research-angle workers). They also load at parent scope, which lets the parent run an angle directly when a worker's deferred-tool load fails.
- **The `Agent` (subagent-spawn) tool is parent-only.** Subagents do NOT have access to `Agent`; they cannot spawn further nested subagents. This is the load-bearing finding that drives the parent-direct model: only the parent can fan out workers in parallel, so the parent must own that responsibility for every coordinated stage.

**Coordination model (parent-direct):**

1. **The parent is the manager.** For each coordinated stage (2, 3, 5, 6), the parent reads the stage's playbook and agent_refs inline, decides team composition (categories / angles / validation levels), and spawns workers itself. There is no manager-subagent layer in between.
2. **The parent spawns workers in parallel.** All workers for a stage are spawned in a single message with multiple `Agent` tool calls. This is the canonical way to maximize parallelism on this harness.
3. **Workers write their own outputs and audit files.** Each worker writes its artifact to the canonical `specs/{type}/{name}/` location AND its spawn audit (`prompt.md` + `output.md`) under `.audit/adhoc_agents/{date}/{task_id}/spawns/{worker_id}/`. No fabricated spawn folders.
4. **The parent does synthesis directly.** After workers finish, the parent reads the worker outputs and produces the consolidated artifact (`qa.md`, `dossier.md`, `strategy.md`) itself.

**Universal rules for deferred tools and team coordination:**

- No silent fallbacks. If a tool fails to load, the parent (or the worker) stops and returns a structured failure (`{status, missing, partial_results_if_any}`) — never paraphrases from training data, never invents citations, never dumps multi-choice questions as inline plaintext, never fabricates worker outputs.
- Plaintext-fallback for `AskUserQuestion` is explicitly forbidden — the multi-choice UX is a hard contract.
- The parent records `pre_reading_consulted` (absolute paths of playbook + agent_refs files it loaded) in the run's `events.jsonl` at the start of each coordinated stage. A missing array is a critical failure.
- If a new finding about deferred-tool scoping or worker coordination surfaces, update this section before proceeding.

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
