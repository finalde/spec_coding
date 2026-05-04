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

### 4. Dual-prompt presence

Every shot MUST ship with BOTH:

- `prompts/shotNN_kling.md` — Kling text-to-video or image-to-video prompt.
- `prompts/shotNN_seedance.md` — Seedance text-to-video prompt.

Reason: Kling and Seedance produce noticeably different output; the workflow's job is to let the user A/B both per shot.

Severity: missing one of the two = `blocker`.

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

## Update protocol

Surgical: one new move / severity row per lesson. Cite the run id where the lesson surfaced.
