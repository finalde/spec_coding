# CLAUDE.md — spec_coding monorepo

Hosts a **spec-driven workflow** and the platform that drives it. Every non-trivial task moves through six stages with artifacts persisted as plain files so any stage can be inspected, edited, or resumed.

## State surfaces (explicit determinism)

All workflow / `agent_team` state lives in one of these surfaces. No hidden caches, no other locations:

1. **`CLAUDE.md`** — rules and conventions (this file).
2. **`.claude/settings.json`** + **`settings.local.json`** — harness config, hooks, permissions, env.
3. **`specs/{task_type}/{task_name}/`** — per-task pipeline artifacts.
4. **`.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/`** — runtime spawn logs (`spawns/{worker_id}/{prompt.md, output.md}`), `events.jsonl`, per-round answer JSONs.
5. **Stage playbooks + refs** under `.claude/skills/agent_team/` and `.claude/agent_refs/` — see § Stage playbooks and reference docs.

Rules:

- **Pipeline status is derived from the filesystem, not from memory.** "Stage N done" iff Stage N's expected artifacts under `specs/{type}/{name}/` exist. Resume logic reads the tree.
- **New mechanisms must land in one of the surfaces above.** No sidecars, session-scoped stores, or side-channel caches.
- **Round-trip artifacts** between parent ↔ workers / user (e.g., `round1_answers.json`, aggregated worker outputs) live under `.audit/`, NOT in `specs/` (which is reserved for canonical user-facing output).

## Auto-memory is disabled

Do NOT use the auto-memory system. Do NOT read or write `.claude/memory/` or `~/.claude/projects/<slug>/memory/`. If session-start instructions mention `MEMORY.md`, treat its absence as canonical: there are no memories.

If you'd save a memory entry, persist to a state surface instead:
- Cross-conversation rules → `CLAUDE.md`.
- Per-project intent → `specs/{type}/{name}/`.
- Per-run audit → `.audit/adhoc_agents/{date}/{task_id}/`.
- Harness config → `.claude/settings*.json`.

The urge to save memory is a signal that one of the surfaces is missing the information. Put it there instead.

## Repo layout

```
spec_coding/
├── CLAUDE.md
├── pyproject.toml                         # canonical Python deps; `uv sync` reads this
├── requirements.txt                       # mirror for pip fallback
├── README.md
├── .claude/
│   ├── agent_refs/                        # institutional memory (see § Stage playbooks and reference docs)
│   │   ├── interview/{general.md, <task_type>.md}
│   │   ├── research/{general.md, <task_type>.md}
│   │   ├── validation/{general.md, <task_type>.md}
│   │   └── project/{general.md, <task_type>.md}
│   ├── skills/agent_team/
│   │   ├── SKILL.md                       # pipeline orchestrator (parent-direct)
│   │   └── playbooks/{interview,research,validation}.md
│   └── settings.local.json
├── specs/
│   └── {task_type}/{task_name}/
│       ├── user_input/{raw_prompt.md, revised_prompt.md, follow_ups/NNN-{date}-{slug}.md}
│       ├── interview/{qa.md, promoted.md}
│       ├── findings/{angle-*.md, dossier.md, promoted.md}
│       ├── final_specs/{spec.md, promoted.md}
│       ├── validation/{strategy.md, acceptance_criteria.md, ..., promoted.md}
│       └── changelog.md                   # append-only follow-up log
├── projects/{name}/                       # task_type=development outputs
├── ai_videos/{name}/                      # task_type=ai_video outputs
└── .audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/   # gitignored; events.jsonl + spawns/
```

## task_type enum

Required at task start. Pick one; ask the user if unclear; never invent.

- `development` — software outputs land in `projects/{name}/`.
- `ai_video` — video planning + render outputs land in `ai_videos/{name}/`.

## The six-stage workflow

The skill `agent_team` is the single entry point and walks all six stages. Users invoke it as `/agent_team` or by asking for a spec-driven task.

| # | Stage | Output | Coordination |
|---|---|---|---|
| 1 | Intake | `user_input/{raw,revised}_prompt.md` | parent-direct, no workers |
| 2 | Interview | `interview/qa.md` | parent-direct, optional category workers |
| 3 | Research | `findings/{angle-*.md, dossier.md}` | parent-direct + parallel angle workers |
| 4 | Spec compilation | `final_specs/spec.md` | parent-direct, no workers |
| 5 | Validation strategy | `validation/{strategy.md, ...}` | parent-direct + parallel level-specialist workers |
| 6 | Execution + streaming validation | `projects/{name}/` or `ai_videos/{name}/` | parent-direct + parallel validators per work unit |

The procedural detail for each coordinated stage lives in `.claude/skills/agent_team/playbooks/{interview,research,validation}.md`. The parent-direct coordination model — and why there is no manager-subagent layer — is documented once in § Tool scoping and team coordination.

## Skill + playbook naming

- Repo-owned skills use `<prefix>__<name>` (double underscore). The orchestrator skill `agent_team` is the exception (top-level workflow, no prefix).
- Stage playbooks live under `.claude/skills/agent_team/playbooks/`. They are NOT subagent definitions — they are runbooks the parent reads inline.
- `.claude/agents/` is reserved for future permanent subagents (currently empty; every spec-driven stage is parent-direct).
- Workers spawned at runtime are general-purpose subagents driven by playbook prompts, captured under `.audit/adhoc_agents/{date}/{task_id}/spawns/`.
- YAML frontmatter `description` field has a hard ceiling of **500 characters**.

## Stage playbooks and reference docs

Two folders sit alongside the workflow, with intentionally separate lifecycles:

- **Playbooks** at `.claude/skills/agent_team/playbooks/{interview,research,validation}.md` — the procedural runbook for each coordinated stage. The contract for *what the parent does*.
- **Refs** at `.claude/agent_refs/` — accumulated institutional memory. *What the parent has learned*. Two scopes:
  - **Stage-scoped:** `agent_refs/{interview,research,validation}/{general.md, <task_type>.md}` — what's been learned at each stage.
  - **Project-scoped:** `agent_refs/project/{general.md, <task_type>.md}` — cross-cutting rules about the *outputs* (e.g., light-theme app chrome for development webapps). NOT for project-specific facts (those go under `specs/`) and NOT for harness contracts (those stay in `CLAUDE.md`).

**Pre-reading contract.** Before each coordinated stage (2, 3, 5) and before each stage-6 work-unit `validation.started`, the parent MUST read:
1. The stage playbook.
2. `agent_refs/{stage}/general.md`.
3. `agent_refs/{stage}/<task_type>.md`, if present.
4. `agent_refs/project/general.md`.
5. `agent_refs/project/<task_type>.md`, if present.

The parent records the absolute paths it actually read in a single `pre_reading_consulted` array on the run's first `events.jsonl` event for that stage (or on each `validation.started` event in stage 6). A missing or empty array is a **critical failure** — institutional memory wasn't loaded.

**Precedence when rules conflict:** per-task-type ref > matching `general.md` in same folder; project-scoped ref > stage-scoped ref > playbook default. A project-specific spec under `specs/{type}/{name}/` may override project-scoped refs for that one project, with a note explaining the divergence.

**Update protocol.** Surgical only — one new principle / severity row / required move at a time, with a one-line citation of the source run / follow-up. Wholesale rewrites are anti-patterns; the goal is to grow institutional memory.

**Why three folders, not one:** different lifecycles. Playbooks change rarely; stage refs accumulate per stage; project refs accumulate per task-type. Folding them together would either balloon the playbook past readability or conflate stage-time-of-use with output-time-of-use.

The spec_driven webapp's `EXPOSED_TREE` recursive globs (`.claude/skills/agent_team/playbooks/*.md`, `.claude/agent_refs/**/*.md`) auto-pick up new subfolders.

## Project rules (under `projects/`)

- One folder per project; no cross-project imports. `backend/` + `frontend/` subfolders when both are needed.
- Python: own `requirements.txt` (direct deps only); mirrored into root `pyproject.toml`; root `requirements.txt` is the pip fallback.
- Backend entry: `main.py` (~15 lines: parse args, hand off to `libs/`). All app logic in `libs/<module>.py`. Domain concepts as classes; `@dataclass(frozen=True)` for immutable containers; avoid free-standing module functions except pure utilities.
- Strong typing on every parameter, return, and attribute. Use `str | None`, not `Optional[str]`.
- Frontend: standard React; `node_modules/` in `.gitignore`.
- README required and updated alongside any feature change.
- **Cross-cutting project-output rules** (themes, visual defaults, structural conventions) live in `.claude/agent_refs/project/` per § Stage playbooks and reference docs — NOT in this section.

## AI video rules (under `ai_videos/`)

Detailed output rules live in `.claude/agent_refs/project/ai_video.md` per § Stage playbooks and reference docs. This section captures only the harness contract that other parts of `CLAUDE.md` reference.

- One folder per project at `ai_videos/{task_name}/`. `task_name` is **pinyin or English**, never Chinese (e.g. `chongsheng_zhi_zongcai_furen`). The Chinese title lives in `ai_videos/{name}/README.md`.
- Folder and file names inside `ai_videos/{name}/` are English/pinyin. **All file content is Chinese.** The "everything Chinese in `ai_videos/`" rule applies to content, not paths.
- Two sub-types, distinguished at stage-2 interview: `novel` (multi-episode, layout under `episodes/epNN/`) and `short` (single-piece, flat layout). Sub-type is captured in `qa.md` metadata and reasserted in stage-4 spec.
- Every shot ≤ 15 s. Every shot ships with BOTH a Kling prompt AND a Seedance prompt. Default aspect ratio 9:16. Visuals only in v1 (no audio prompts emitted).
- Image-first character consistency: each named character gets a Seedream ref-image prompt + a locked Chinese descriptor; the descriptor is re-pasted byte-identically in every shot prompt that names the character.
- Per-episode (or per-short) `publish.md` with platform metadata is part of the stage-6 contract.
- README required and in Chinese, updated alongside any feature change.
- Cross-cutting output rules and the full layout spec live in `.claude/agent_refs/project/ai_video.md`. Per-project deviations live in `specs/ai_video/{name}/` with a divergence note.

## Event stream

`.audit/adhoc_agents/{date}/{task_id}/events.jsonl` is append-only JSONL. Lines parse independently; atomic line-sized appends are safe. Event types:

`exec.unit.started`, `exec.unit.completed`, `validation.started`, `validation.issue.raised`, `validation.pass`, `validation.requires_manual_walkthrough`, `exec.revision.applied`, `pipeline.halted`, `regen.delete.planned`, `regen.delete.completed`, `regen.write.completed`.

The parent writes during stage 6 runtime validation and at the start of each coordinated stage to record `pre_reading_consulted`.

## Follow-up prompt handling

Once a spec-driven project exists, follow-up chat may contain additional intent for it. Triage every new prompt before doing anything else.

1. **Triage.** Casual chat / general question with no spec-driven impact → answer normally, no persistence. Real instruction → classify which project. **If ambiguous (project X, Y, or none), ASK the user** — do not silently pick.
2. **Persist** at `specs/{type}/{name}/user_input/follow_ups/NNN-{YYYYMMDD-HHmmss}-{slug}.md` (NNN zero-padded, sequential). Contents: abstracted instruction (drop chitchat); prefix with `# Follow-up draft NNN — {YYYY-MM-DD}` + a one-line summary.
3. **Regenerate `revised_prompt.md`** = `raw_prompt.md` + every `follow_ups/*.md` in numerical order. No confirmation needed.
4. **Walk downstream artifacts** in order: `interview/qa.md` → `findings/dossier.md` + per-angle → `final_specs/spec.md` → `validation/strategy.md` + per-level → generated outputs under `projects/` or `ai_videos/`.
5. **Auto-update affected sections in place.** Smallest change that resolves the conflict / fills the gap. Surgical only; no whole-file regen. Inline markers (`<!-- auto-updated by follow-up NNN -->`) are NOT added by default — ask the user if a particular update is invasive enough to warrant one.
6. **Append `changelog.md`** at `specs/{type}/{name}/changelog.md`:
   ```markdown
   ## Follow-up NNN — {YYYY-MM-DD HH:mm:ss}
   Source: user_input/follow_ups/NNN-{slug}.md
   Summary: {one line}

   Auto-updated:
   - {path} — {one-line description}

   No conflicts found in: {list}
   ```
7. **Never auto-trigger a full stage regeneration.** Surgical patches only. Full regen is user-triggered (the `changelog.md` entries are the user's signal that downstream artifacts were touched).

## Regeneration prompts & autonomous mode

The `spec_driven` webapp emits **copy-paste regeneration prompts** the user pastes into Claude Code CLI to re-run one or more stages. Every such prompt opens with one of two execution-mode headers — Claude MUST honor them at the top of a turn's input.

**Header contract:**

- **`# EXECUTION MODE: AUTONOMOUS`** —
  - Do NOT call `AskUserQuestion`. Not for clarification, not for "A or B," not for confirmation. The user is not at the keyboard.
  - For ambiguity, use best judgment AND record it inline in the produced artifact (e.g., `*(judgment call — chose X because Y)*`) so the user has a self-explaining trail.
  - Produce every requested artifact in the same turn before stopping; do not pause for confirmation between stages. Iteration bounds (§ below) still apply — when a bound trips, halt cleanly with a `pipeline.halted` event + summary.
  - Every other rule still applies (state surfaces, agent-spawning contract, follow-up procedure for new instructions arriving mid-run). Autonomous lifts only the question-asking restriction.
- **`# EXECUTION MODE: INTERACTIVE`** — default. `AskUserQuestion` available when intent is genuinely ambiguous and not inferrable from existing artifacts.
- **No header** = INTERACTIVE.

**What the webapp generates.** `POST /api/regen-prompt` (FR-14c) inlines the project's current `revised_prompt.md` (or `raw_prompt.md` if no revised yet) plus every `user_input/follow_ups/*.md`. A pasted regen prompt is therefore self-contained.

**Defaults.** The webapp's autonomous-mode toggle defaults to **off** (interactive); accidental autonomous runs should not be the path of least resistance. The toggle persists in browser `localStorage` under `spec_driven.autonomous_mode.v1` (no server-side persistence — autonomous is per-prompt, not global).

### Regeneration semantics: read-zero from prior outputs

A regeneration deletes the regenerated stage's prior outputs and rewrites from scratch. Surgical preservation of prior text is **forbidden** during regen — it makes the output a function of (input ∧ all previous runs) and defeats the workflow.

The regenerated stage reads ONLY:
1. The current stage's *input* artifacts (canonical outputs of prior stages).
2. `CLAUDE.md` and shared `.claude/` context (skill, playbooks, refs).
3. The user-input layer (`raw_prompt.md` + every `user_input/follow_ups/*.md`).
4. The current stage's `<stage>/promoted.md` sidecar, if present (see § Pinned items).

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
- **Multi-stage regen is sequential.** Delete each stage's outputs the moment that stage runs (after inputs are confirmed), not all up-front; otherwise stage N+1 is missing its inputs.
- **Selective module regen.** If the prompt selects only some stage modules (e.g., only `validation/security.md` + `performance.md`), delete only those files. Default copy-paste prompts select all.
- **`changelog.md` and `.audit/` are NEVER regen outputs.** They are the audit log; they get appended to with a record of what was deleted/regenerated.
- **Project README and Makefile** under `projects/{name}/` are stage-6 outputs and ARE deleted with the rest of the folder.
- **AI-video novels accept a per-episode regen scope.** When `task_type=ai_video, sub_type=novel`, a regen prompt may declare `scope=episode N` (or `scope=episodes M..N`); the parent then deletes only `ai_videos/{name}/episodes/ep{NN}/` for the named range, preserving `characters/`, `world.md`, `style_guide.md`, `arc_outline.md`, and other episodes' folders. Default remains `scope=project` (whole-folder delete per the table). Shorts have only the project-level scope.
- **The `agent_team` skill, playbooks, and agent_refs** are NOT regen outputs — they are harness context. Never deleted by a project-scoped regen.

Audit-event contract for any regen: emit `regen.delete.planned` (one line per file before delete), `regen.delete.completed` (with count), `regen.write.completed` (path + size after write) into `events.jsonl`. The webapp's `regen_prompt.py` includes this contract verbatim in every assembled prompt's `### Constraints` section.

### Pinned items survive regeneration

Each spec-pipeline stage (interview, findings, final_specs, validation) supports a `<stage>/promoted.md` sidecar. The user pins atomic items via the spec_driven webapp (`POST /api/promote`); they're written to `promoted.md` and deleted via `DELETE /api/promote`.

1. **`<stage>/promoted.md` is an INPUT, not an output.** Preserved across regen (Files-to-preserve column above).
2. **Every pin appears verbatim in the regenerated artifact** at the natural insertion point for its source-file/id metadata. Newly-generated content for a pinned slot is dropped — promoted always wins.
3. **Orphaned pins** (insertion point gone) go to a `## Pinned items (orphaned)` section at the end of the originally-pinned source file. NEVER silently dropped.
4. **Editing a pin updates `promoted.md` only.** The generated artifact is touched at the next regen. Drift between editions is acceptable; users resolve it by running stage N regen.
5. **`<stage>/promoted.md` is itself viewable / editable** through the webapp via the same path-sandbox. It is NOT a regen target.
6. **Stage 6 (project code) has no v1 promotion** — different granularity story, deferred.

## Tool scoping and team coordination

Some tools are **deferred** — schemas not loaded at session start; calling them directly fails with `InputValidationError`. They appear by name in the session-start system reminder. Load with `ToolSearch(query="select:<name>", max_results=1)` first.

**Empirically established scoping** (load-bearing for the parent-direct workflow):

- **`AskUserQuestion`** is **parent-only**. Subagents return "no matching deferred tools found" on ToolSearch. This is precisely why stage 2 is parent-direct — only the parent can prompt the user.
- **`WebSearch` / `WebFetch`** load at first-level subagent scope (verified 2026-05-02 in research workers) AND at parent scope. The parent can run an angle directly when a worker's deferred-tool load fails (recovery path).
- **The `Agent` (subagent-spawn) tool is parent-only.** Subagents cannot spawn nested subagents. This drives the parent-direct model: only the parent fans out workers in parallel.

**Coordination model (parent-direct):**

1. **The parent IS the manager** at every coordinated stage (2, 3, 5, 6). It reads playbook + refs, decides team composition, spawns workers, synthesizes outputs. There is no manager-subagent layer in between.
2. **Workers spawn in parallel** — single message, multiple `Agent` tool calls. Canonical way to maximize parallelism on this harness.
3. **Workers write their own outputs and audit files.** Each worker writes its artifact to the canonical `specs/{type}/{name}/` location AND its spawn audit (`prompt.md` + `output.md`) under `.audit/adhoc_agents/{date}/{task_id}/spawns/{worker_id}/`. No fabricated spawn folders.
4. **The parent does synthesis directly** after workers finish — `qa.md`, `dossier.md`, `strategy.md` are parent-written.

**Universal rules:**

- **No silent fallbacks.** If a tool fails to load, halt with a structured failure (`{status, missing, partial_results_if_any}`). Never paraphrase from training data, never invent citations, never dump multi-choice questions inline as plaintext, never fabricate worker outputs.
- **Plaintext-fallback for `AskUserQuestion` is forbidden** — the multi-choice UX is a hard contract.
- **The parent records `pre_reading_consulted`** on the run's first event for each coordinated stage. Missing array = critical failure.
- **New scoping findings update this section** before proceeding.

## Iteration bounds

- Default 3 revision rounds per work unit before halting.
- Cap interview iterations at 3 rounds total.
- Circuit-break + emit `pipeline.halted` if the same issue repeats across two iterations OR wall-clock exceeds 30 minutes on a single unit.
- After halt, escalate to the user. Never silently retry past the bound.

## Task ID convention

`task_id = "{task_name}-{YYYYMMDD-HHmmss}"`, built once at run start. Use for `.audit/adhoc_agents/{date}/{task_id}/`.

For `task_type=ai_video`, `task_name` is pinyin or English even when the project's natural identifier is a Chinese title (per `agent_refs/project/ai_video.md` rule 1). The Chinese title is captured in `ai_videos/{name}/README.md`, not in the path.

## General coding rules

- Default to writing no comments. Only when the *why* is non-obvious.
- Don't add features, abstractions, or backwards-compat shims the task didn't ask for.
- Don't add error handling for cases that cannot happen. Validate at system boundaries (user input, external APIs); trust internal calls.
- Prefer editing existing files over creating new ones. Never create `*.md` documentation files unless explicitly requested.
- Strong typing + OOP rules above apply to all Python under `projects/` and `tools/`.
