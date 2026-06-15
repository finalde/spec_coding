# Validation refs — `task_type=ai_video`

Institutional memory loaded when the current task has `task_type=ai_video`. Layered on top of `general.md` in this same folder; per-task-type rules win when they conflict.

## Required validation moves

Numbered. Each is a level the parent MUST include in the stage-5 strategy unless the spec explicitly excludes it.

### 1. Language compliance

Every file written under `ai_videos/{name}/` MUST be Chinese in CONTENT. Filenames / folder names are English/pinyin per `agent_refs/project/ai_video.md` rule 1 — those are exempt.

Validator pseudo-rule:

- Read every `*.md` under `ai_videos/{name}/` recursively.
- Strip code fences, YAML frontmatter, raw URLs.
- Remaining text must be ≥95% Chinese-block characters (Han + fullwidth punctuation).
- English proper nouns inside Chinese sentences (`Kling`, `Seedance`, `Seedream`, `9:16`, character names if the project uses Romanized names) are allowed and not counted against the threshold.

Severity: failure = `blocker`.

### 2. 15-second shot atomicity

Every shot in any `shotlist.md` (or per-episode equivalent for novels) MUST declare `时长` ≤ 15 s with a one-line rationale. The validator parses the shot list and rejects any shot missing `时长` or with `时长` > 15 s. Splitting hint baked into the failure message: anything that needs a hard camera cut mid-generation is two shots.

Severity: any shot > 15 s, or any shot missing the field = `blocker`.

### 3. Character-visual-consistency

Every named character that appears in any shot prompt MUST resolve to:

- a Chinese descriptor block in `characters/<role>.md`, AND
- a Seedream ref-image prompt in `characters/ref_images/<role>_seedream.md`.

Every shot prompt that references the character MUST include the character's locked Chinese descriptor inline (so the prompt is self-contained when copy-pasted). Validator checks: the descriptor strings are byte-identical (modulo whitespace) across every shot in the same episode.

Severity:

- missing descriptor file = `blocker`.
- missing Seedream ref-image prompt = `blocker`.
- drift between two shots' descriptors of the same character within the same episode = `blocker`.

### 4. Dual-prompt presence + seam-frame still-image prompts

Every shot MUST ship with:

- `shots/shotNN_kling.md` — Kling text-to-video or image-to-video prompt.
- `shots/shotNN_seedance.md` — Seedance text-to-video prompt.
- `shots/shotNN_lastframe_seedream.md` — Seedream still-image prompt for the shot's final frame, per `agent_refs/project/ai_video.md` rule #11. Used as Kling's end-frame anchor and as the start-frame anchor of the next shot for clip-stitching consistency.

Additionally, the **first shot** of the video (or the first shot of each episode for novels) MUST ship with:

- `shots/shot01_startframe_seedream.md` — Seedream still-image prompt for the absolute opening frame. Used as Kling's start-frame anchor for shot 01.

Reason: Kling and Seedance produce noticeably different output; the workflow's job is to let the user A/B both per shot. Seam-frame stills are the load-bearing mechanism for stitching multiple ≤15 s clips into a longer video without visible drift across clip boundaries.

Severity: missing any required prompt file = `blocker`.

### 5. Aspect ratio + platform compliance

Every shot prompt MUST declare `比例` (default 9:16). Deviation requires an explicit per-project spec note. For shorts, the shot list MUST mark which shot is the hook (first ≤3 s) — and the hook shot's prompt MUST have a hook-conducive composition (subject in upper third, motion start within 0.5 s of frame zero).

Severity:

- missing `比例` field = `blocker`.
- shorts missing hook marker = `blocker`.
- novel hook composition issues — surface as `validation.requires_manual_walkthrough`, not auto-blocker (subjective).

### 6. Publish metadata presence

Every novel episode folder MUST contain `publish.md` with: hook-style title (≤30 Chinese chars), description (≤200 Chinese chars), 5–10 hashtags, cover-frame suggestion (which shot to thumbnail). Same applies to a short's top-level `publish.md`.

Severity: missing or partial = `blocker`.

### 7. Pinned items survive regeneration

Per `validation/general.md` principle 8 + `CLAUDE.md` § Pinned items survive regeneration. ai_video stages with promotion sidecars: interview, findings, final_specs, validation. Stage 6 (`ai_videos/{name}/`) does NOT support promotion in v1 — strategy MUST NOT generate this check for stage-6 regen.

### 8. Manual walkthrough before declaring an episode / short done

After all automated levels pass for a work unit (one episode for novels, the whole short for shorts), the parent emits `validation.requires_manual_walkthrough` with the prompt: *"Open `characters/ref_images/`, the shot list, and 2–3 shot prompts in random order — confirm character description matches across shots and the shot list reads as a coherent scene."* User confirmation closes the work unit.

### 9. 短剧故事 + 台词大师 (storyteller-dialogue master review)

Every newly-emitted or regenerated shot / episode / shotlist item is reviewed by a "短剧故事 + 台词大师" specialist BEFORE the work unit is marked done. The master enforces the dialogue + shot-design criteria documented in `agent_refs/project/ai_video.md` §12.4-D ("短剧故事 + 台词大师 review criteria"). At stage 5 this is one of the parallel level-specialist workers; at stage 6 the master runs against every shot md as it's written (per work unit) and at the closing pass of every episode / shot list.

Validator pseudo-rule per shot:

1. Parse the `台词 / 字幕:` section. For each line: check 通俗易懂性 (modern colloquial Chinese, no untriggered 古文 / 文言文 / 玄学 aphorisms), 信息量 (advances plot or reveals stake / character), 节奏 (≤ 15 字 punchy unless ceremonial), 角色声口 (line voice matches the character's personality and station per `characters/<role>.md`). Lines failing on any axis → flag with proposed alternate.
2. Check shot's hook landing — 黄金钩 / 反转 / cliffhanger shots must have their named hook visibly landed in 镜头 + 动作 + 台词 within the declared seconds.
3. Check 情节链 — the shot's beat must be a non-removable step in the episode's plot chain (per `episode.md` arc). Decorative shots whose removal wouldn't break the chain are flagged.
4. Check character-station fidelity — speaker tone in `(语气..., 朝/望谁): "..."` matches the character's 锁定描述符 from §12.4-C and §12.4-D combined.

Severity:

- One dialogue line fails 通俗易懂性 → `warning` with proposed rewrite.
- A shot's hook is named but not landed → `blocker`.
- A character's voice contradicts their `characters/<role>.md` 角色定位 → `blocker`.
- Two shots within the same episode reuse near-identical dialogue templates (e.g., 两个角色 都说 "今日便是你的劫数") → `warning` with differentiation hint.
- 沿用 anachronistic character references (a name from a later arc appears in an earlier shot) → `blocker`.

The master's output is a per-shot inline patch list, NOT free-form prose review: each failure cites the shot, the failing line, the criterion, and the proposed rewrite. The parent applies the patches surgically and re-runs the level until 0 blockers + ≤ 2 warnings remain.

### 10. Folder-per-shot structural integrity (per follow-up wushen_juexing/021 — 2026-06-14)

Every shot MUST be a same-named folder `episodes/epNN/shots/shotNN/` containing `shotNN.md` (+ optional `subtitles.md` + `renders/` media), per `agent_refs/project/ai_video.md` rule #12.9. A **flat `episodes/epNN/shots/shotNN.md`** (prompt file sitting directly under `shots/` with no enclosing `shotNN/` folder) is non-conformant — it breaks the webapp display contract, the render-import routing into `shots/shotNN/renders/`, and 台词 burn-in (`subtitles.md` lives beside the prompt). This must be uniform across ALL dramas in the repo (the inconsistency that surfaced this rule: `nvdi_tuihun_houhuile` used folders, `wushen_juexing` used flat files).

Validator pseudo-rule:
- `find episodes/epNN/shots -maxdepth 1 -name 'shot*.md'` MUST return 0 (no flat shot md directly under `shots/`).
- For each `shotNN/` folder, `shotNN/shotNN.md` MUST exist (folder + filename byte-identical).
- `shotlist.md` (episode-level) correctly stays flat under `episodes/epNN/` — it is NOT a shot.

Severity: any flat `shots/shotNN.md`, or a `shotNN/` folder whose inner md name ≠ folder name = `blocker`.

## Severity escalations specific to ai_video

| Issue class | Severity | Reason |
|---|---|---|
| English content in `ai_videos/{name}/*.md` (excluding code fences / URLs / proper nouns) | `blocker` | Hard project rule. |
| Shot > 15 s | `blocker` | Tool generation limit; can't render in one pass. |
| Two shots in same episode use different descriptors for the same character | `blocker` | Visible character drift; the entire image-first strategy exists to prevent this. |
| Missing Seedream ref-image prompt for a named character | `blocker` | Image-first pipeline is broken without it. |
| Missing `publish.md` for an episode / short | `blocker` | Workflow promise breached; user expected copy-paste-ready outputs. |
| Aspect ratio omitted on a shot prompt | `blocker` | Tool default may not be 9:16; rendered video ends up wrong format. |
| Hook shot missing or unmarked on a short | `blocker` | First 3 s is the retention battle. |
| Shot prompt references a character not declared in `characters/` | `blocker` | Character drift waiting to happen. |
| Continuity token between adjacent shots missing when state should carry over | `warning` | Often invisible until rendered; flag for manual walkthrough. |
| Missing `shotNN_lastframe_seedream.md` for any shot | `blocker` | Without the seam-frame still, Kling has no `input_image_urls` end-frame anchor and the next shot has no start-frame anchor — visible drift across clip boundaries when stitched. Per `agent_refs/project/ai_video.md` rule #11. |
| Missing `shot01_startframe_seedream.md` on the first shot of a video / episode | `blocker` | Without the absolute opening frame, Kling shot 01 image-to-video has no start-frame anchor — character / scene / lighting drift in the very first 15 seconds. Per rule #11. |
| Flat `shots/shotNN.md` instead of folder-per-shot `shots/shotNN/shotNN.md` | `blocker` | Breaks webapp display + render-import (`renders/`) + 台词 burn-in (`subtitles.md`) contracts. Per rule #12.9 / validation move #10. |

## Update protocol

Surgical: one new move / severity row per lesson. Cite the run id where the lesson surfaced.
