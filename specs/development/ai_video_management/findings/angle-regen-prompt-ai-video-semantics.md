# Angle — `regen-prompt-ai-video-semantics`

Researcher: 03
Run: `ai_video_management-20260505-002710`
Source inputs: `CLAUDE.md` (§ Regeneration semantics, § Pinned items, § AI video rules, § Iteration bounds, § Regeneration prompts & autonomous mode), `projects/spec_driven/backend/libs/{regen_prompt.py, stages.py, api.py}`, `.claude/agent_refs/project/ai_video.md`, `specs/development/ai_video_management/{user_input/revised_prompt.md, interview/qa.md}`, `specs/ai_video/wukong_juexing/`, `ai_videos/wukong_juexing/`.

## 1. What this angle covers

The exact wire body that `POST /api/regen-prompt` MUST emit so the user can paste it into Claude Code CLI and re-run any subset of stages 1–6 against an `ai_video` project. The webapp is the structural twin of `spec_driven` (which already implements this for `task_type=development`); this angle pins the **two delta surfaces** unique to `ai_video`:

1. **`sub_type`-aware stage 6 wording.** The stage-6 delete contract differs between novel (`ai_videos/{name}/episodes/`) and short (flat `ai_videos/{name}/`).
2. **`scope` axis on stage 6 of novels.** `scope=project | episode N | episodes M..N`, controlling exactly which subtree gets deleted before regeneration. Shorts are `scope=project` only.

Stages 1–5 of an ai_video project are textually identical (modulo project-type / project-name) to the spec_driven case: same delete-then-regenerate table, same pinned-item contract, same audit events. `regen_prompt.py` for the new webapp can reuse the spec_driven assembly path verbatim for stages 1–5 and only branch on stage 6.

## 2. HTTP API spec

### Request: `POST /api/regen-prompt`

Content-Type `application/json`. Body schema (extends the spec_driven `RegenPromptBody` with two ai_video-only optional fields; ignored when `project_type != "ai_video"`):

```json
{
  "project_type": "ai_video",            // string, required, enum {"ai_video", "development"}
  "project_name": "wukong_juexing",      // string, required, project folder under specs/{type}/
  "stages": ["execution"],               // string[], required, subset of {"intake","interview","research","spec","validation","execution"}
  "modules": {                           // object, optional. Keys are stage ids; values are module-id subsets.
    "validation": ["security", "performance"]
  },
  "autonomous": false,                   // bool, default false. Drives the EXECUTION MODE header.
  "scope": "episode",                    // string, optional, default "project". enum {"project","episode","episodes"}.
                                         //   Only honored when project_type == "ai_video" AND "execution" in stages.
                                         //   Rejected with 400 for development projects (or silently coerced to "project" — see open Q).
  "scope_episode": 3,                    // int, required iff scope == "episode". 1-based.
  "scope_episode_range": {"start": 5, "end": 8} // {start: int, end: int}, required iff scope == "episodes". Inclusive, start <= end.
}
```

Validation rules (server-side, 400 on violation):

- `scope == "episode"` requires `scope_episode` ≥ 1 AND the project's `sub_type == "novel"`.
- `scope == "episodes"` requires `scope_episode_range` with `1 ≤ start ≤ end` AND `sub_type == "novel"`.
- For `sub_type == "short"`, `scope` MUST be omitted or `"project"`.
- `sub_type` is detected via `specs/ai_video/{name}/interview/qa.md` parse (per qa.md → Regen-scope-UI Q2 answer A). If qa.md absent or sub_type unparseable, server returns `409 {"detail": {"kind": "subtype_unknown"}}`.

### Response 200

```json
{
  "prompt": "# EXECUTION MODE: INTERACTIVE\n\n...",   // string, the full paste-ready body
  "warning": null,                                     // null | {"kind": "approaching_ceiling", "bytes": 73421, "soft_limit": 51200}
  "selected_stages_count": 1,                          // int
  "follow_ups_count": 2,                               // int
  "autonomous": false,                                 // bool, echoed
  "bytes": 18342,                                      // int, len(prompt.encode('utf-8'))
  "scope": "episode",                                  // string, echoed (omitted for development)
  "scope_resolved": "ep03"                             // string, present iff scope in {episode, episodes}; e.g. "ep03" or "ep05..ep08"
}
```

### Error responses

- `400` — bad scope / sub_type combination, malformed range.
- `409 {"detail": {"kind": "subtype_unknown"}}` — qa.md missing or sub_type token absent.
- `413 {"detail": {"kind": "too_large"}}` — assembled body ≥ HARD_LIMIT_BYTES (1 MiB; same constant as spec_driven).

Soft warning at SOFT_LIMIT_BYTES (50 KiB), same constants as spec_driven.

## 3. Stage 1–5 prompt template

Identical structure for `project_type=ai_video` and `project_type=development`. `{placeholders}` are filled by `regen_prompt.py`.

```markdown
# EXECUTION MODE: {INTERACTIVE_OR_AUTONOMOUS}

{IF_AUTONOMOUS_INSERT_IMPERATIVE_BLOCK}

## Project

- type: `{project_type}`
- name: `{project_name}`
{IF_AI_VIDEO_INSERT: - sub_type: `{novel_or_short}`}

## Revised prompt

_From `specs/{project_type}/{project_name}/user_input/revised_prompt.md` (raw + every follow-up in numeric order)._

{REVISED_PROMPT_BODY}

## Follow-ups

_{N} follow-up(s) inlined in numeric order._

### Follow-up: `{NNN-YYYYMMDD-HHmmss-slug}.md`

{FOLLOW_UP_BODY}

{REPEAT_PER_FOLLOW_UP}

## Stage {STAGE_LABEL}

_Folder:_ `{STAGE_FOLDER}`

_Invocation:_ {STAGE_INVOCATION}

_Modules selected:_

- `{module_relative_path}` — {module_label}: {module_description}
{REPEAT_PER_SELECTED_MODULE}

### Pinned items (MUST survive regeneration)

_From `specs/{project_type}/{project_name}/{STAGE_FOLDER}/promoted.md` — INPUT, not output. Insert verbatim at natural points; orphans go to a trailing `## Pinned items (orphaned)` section in the originally-pinned source file._

{PROMOTED_MD_BODY}

{REPEAT_STAGE_BLOCK_PER_SELECTED_STAGE}

### Constraints

{READ_ZERO_CONTRACT_VERBATIM}

_Selected stages this run:_ {comma_joined_stage_ids}.
```

`{READ_ZERO_CONTRACT_VERBATIM}` is the `_READ_ZERO_CONTRACT` block from `projects/spec_driven/backend/libs/regen_prompt.py` (the per-stage table + operational notes + audit-event protocol + pinned-items paragraph). It MUST be byte-identical to `CLAUDE.md` § Regeneration semantics → "The regenerated stage reads ONLY:" through the pinned-items paragraph. The `### Pinned items` block is omitted when `promoted.md` is missing or empty (rstrip).

## 4. Stage 6 — `sub_type=short` template

Stage 6 ALWAYS has `scope=project` for shorts. Inserted in place of the generic stage-6 block:

```markdown
## Stage 6 — Execution + streaming validation

_Folder:_ `ai_videos/{project_name}/`
_sub_type:_ `short`
_scope:_ `project`

_Invocation:_ Re-run execution: implement work units against `final_specs/spec.md`, run per-unit validators in parallel.

_Modules selected:_

- `ai_videos/{project_name}/` — short-form artifact tree: README, characters/, style_guide.md, script.md, shotlist.md, prompts/shotNN_{kling,seedance}.md, publish.md.

### Delete-then-regenerate (this stage)

Before any new generation:

1. Emit one `regen.delete.planned` JSONL event per file under `ai_videos/{project_name}/`.
2. Recursively delete `ai_videos/{project_name}/` (real `rm -rf`-equivalent — stale bytes are forbidden).
3. Emit a single `regen.delete.completed` event with the file count.
4. Generate fresh outputs per `final_specs/spec.md` + `validation/*.md`.
5. Emit one `regen.write.completed` event per written file (path + size).

`changelog.md` and `.audit/` are NEVER touched.
```

(The shared `### Constraints` block at the end of the prompt still ships the full read-zero table, so the operator sees the universal regen contract too.)

## 5. Stage 6 — `sub_type=novel` template

Three scope variants. The one selected by `body.scope` is emitted; the others are NOT (no "options" — the prompt is paste-ready for one decision).

### 5a. `scope=project`

```markdown
## Stage 6 — Execution + streaming validation

_Folder:_ `ai_videos/{project_name}/`
_sub_type:_ `novel`
_scope:_ `project`

_Invocation:_ Re-run execution: full-project rebuild. Implement against `final_specs/spec.md`, run per-unit validators in parallel.

_Modules selected:_

- `ai_videos/{project_name}/` — full novel tree: README, characters/, world.md, style_guide.md, arc_outline.md, episodes/epNN/{script.md, shotlist.md, prompts/, publish.md}.

### Delete-then-regenerate (this stage)

1. `regen.delete.planned` per file under `ai_videos/{project_name}/`.
2. Recursive delete of `ai_videos/{project_name}/`.
3. `regen.delete.completed` with count.
4. Generate fresh outputs.
5. `regen.write.completed` per written file.
```

### 5b. `scope=episode N`

```markdown
## Stage 6 — Execution + streaming validation

_Folder:_ `ai_videos/{project_name}/episodes/ep{NN_zero_padded}/`
_sub_type:_ `novel`
_scope:_ `episode {N}`

_Invocation:_ Re-run execution for episode {N} only. Character bibles, world.md, style_guide.md, arc_outline.md, AND every other episode under `episodes/` are PRESERVED (read as inputs, not deleted, not rewritten).

_Modules selected:_

- `ai_videos/{project_name}/episodes/ep{NN}/script.md`
- `ai_videos/{project_name}/episodes/ep{NN}/shotlist.md`
- `ai_videos/{project_name}/episodes/ep{NN}/prompts/shotMM_kling.md` (every shot)
- `ai_videos/{project_name}/episodes/ep{NN}/prompts/shotMM_seedance.md` (every shot)
- `ai_videos/{project_name}/episodes/ep{NN}/publish.md`

### Delete-then-regenerate (this stage)

1. `regen.delete.planned` per file under `ai_videos/{project_name}/episodes/ep{NN}/` ONLY.
2. Recursive delete of `ai_videos/{project_name}/episodes/ep{NN}/`. Do NOT touch siblings.
3. `regen.delete.completed` with count.
4. Generate fresh ep{NN} outputs, reading character bibles + world + style guide + arc_outline as inputs.
5. `regen.write.completed` per written file.

Forbidden in this scope: editing `characters/`, `world.md`, `style_guide.md`, `arc_outline.md`, `README.md`, or any other `episodes/epMM/` where `MM != NN`. If the regeneration surfaces a desired change to one of those, halt with `pipeline.halted` and surface the conflict — the user must promote the change to a `scope=project` regen or a follow-up.
```

### 5c. `scope=episodes M..N`

Same as 5b but with the loop expanded:

```markdown
## Stage 6 — Execution + streaming validation

_Folder:_ `ai_videos/{project_name}/episodes/ep{MM}..ep{NN}/`
_sub_type:_ `novel`
_scope:_ `episodes {M}..{N}` (inclusive)

_Invocation:_ Re-run execution for episodes {M} through {N} inclusive. All other episodes + project-level files preserved.

_Modules selected:_

{FOR_EACH_EP_IN_RANGE_INSERT_FILE_LIST_BLOCK_FROM_5b}

### Delete-then-regenerate (this stage)

1. `regen.delete.planned` per file under each `ai_videos/{project_name}/episodes/ep{KK}/` for KK in [M..N].
2. Recursive delete of each `episodes/ep{KK}/` directory in turn (sequential per CLAUDE.md "Multi-stage regen is sequential").
3. `regen.delete.completed` with total count.
4. Generate fresh outputs for each KK in [M..N], reading shared inputs as in 5b.
5. `regen.write.completed` per written file.
```

## 6. Audit-event contract

The runner that EXECUTES the pasted prompt MUST emit JSONL into `.audit/adhoc_agents/{YYYY-MM-DD}/{task_id}/events.jsonl`. Event shapes (one JSON object per line, atomic append):

```json
{"ts": "2026-05-05T00:31:14Z", "event": "regen.delete.planned", "stage": "execution", "scope": "episode", "scope_resolved": "ep03", "path": "ai_videos/wukong_juexing/episodes/ep03/script.md"}
{"ts": "...", "event": "regen.delete.completed", "stage": "execution", "scope": "...", "scope_resolved": "...", "count": 17}
{"ts": "...", "event": "regen.write.completed", "stage": "execution", "scope": "...", "scope_resolved": "...", "path": "ai_videos/wukong_juexing/episodes/ep03/shotlist.md", "bytes": 4218}
```

For stages 1–5 (or stage 6 `scope=project`), `scope_resolved` is `"project"` and the file paths cover the per-stage Delete column from CLAUDE.md's table. The webapp does NOT emit these events itself — it only inlines the contract into the prompt body via the `_READ_ZERO_CONTRACT` block (verbatim) so the executor knows what to write.

## 7. Implications for the spec (stage 4)

- **`regen_prompt.py` MUST live under `projects/ai_video_management/backend/libs/` and reuse the spec_driven `_READ_ZERO_CONTRACT` block byte-identically** — copy the constant, do not re-paraphrase. Drift between the two webapps' regen contracts would defeat the workflow.
- **`Stages` table** is identical to spec_driven's `CANONICAL_STAGES` for stages 1–5; stage 6 (`execution`) needs its `folder` field updated to a sub_type-aware string (or the folder field becomes a callable resolved at render time). Recommendation: add `Stage.folder_for(project_type, sub_type)` that returns `f"ai_videos/{name}/"` for ai_video and `f"projects/{name}/"` for development.
- **`SubTypeResolver`** new class under `backend/libs/sub_type.py`: parses `specs/ai_video/{name}/interview/qa.md`, looks for `| sub_type | {value} |` token in the settled-facts table (per qa.md A2 of Regen-scope-UI category). Returns `"novel" | "short" | None`. None → 409.
- **`RegenPromptBuilder.build` signature** gains 3 optional kwargs: `scope: str = "project"`, `scope_episode: int | None = None`, `scope_episode_range: tuple[int, int] | None = None`. Stages 1–5 ignore them; stage 6 dispatches to `_render_stage6_short`, `_render_stage6_novel_project`, `_render_stage6_novel_episode`, `_render_stage6_novel_episodes` based on `(sub_type, scope)`.
- **Frontend `RegenPromptDialog.tsx`** surfaces the scope toggle ONLY when (a) the project is ai_video and (b) sub_type is novel and (c) `execution` is in selected stages. Per qa.md Regen-scope-UI Q1 answer A. Range input is two number boxes (M, N) with `1 ≤ M ≤ N` validation per qa.md Q3 answer A.
- **Test surface** must cover: short × project, novel × project, novel × episode, novel × episodes, sub_type unknown → 409, scope on development project → 400, oversized prompt → 413, soft warning → 200 with warning.

## 8. Open questions surfaced

1. **Scope on a development project.** Should `body.scope = "episode"` on a development-typed project return 400 (strict) or be silently coerced to `"project"` (lenient)? Recommendation: 400. Lenient coercion hides bugs in the frontend.
2. **`scope=episodes M..N` upper bound.** The spec says "1 ≤ M ≤ N" but doesn't cap N. Should the server reject N > number-of-episodes-detected-in-arc_outline? Recommendation: NO — the regen prompt is what fills in episodes that don't exist yet (initial generation of detail beyond the first `detail_batch_size`). Capping breaks that workflow.
3. **`sub_type` cache invalidation.** If `qa.md` changes mid-session, when does the webapp re-read it? Recommendation: never cache — read on every regen-prompt request (negligible cost; correctness wins).
4. **Pinned-item promotion at stage 6 in a novel-episode regen.** v1 stage-6 has no promoted.md (per CLAUDE.md "Stage 6 (project code) has no v1 promotion"). Confirm this stays true for the ai_video case, OR if a per-episode pin sidecar is needed when the user wants to preserve a specific shot prompt across an episode regen. Recommendation: keep deferred to v2 — same carve-out as spec_driven.
5. **`scope=episode` on a project that hasn't generated `episodes/epNN/` yet.** Is it valid to regen ep03 when only ep01..ep02 exist? Recommendation: YES — the prompt explicitly drives the executor to CREATE ep03 from arc_outline. Server validation must NOT require the directory to pre-exist.
6. **Episode zero-padding.** `epNN` always 2-digit (`ep03`, not `ep3`)? Recommendation: YES — matches `agent_refs/project/ai_video.md` rule 2 layout (`epNN`). Reject `scope_episode > 99` for v1 (or extend to `ep001` if novels grow past 99 episodes — defer).
