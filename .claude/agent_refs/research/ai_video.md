# Research refs — `task_type=ai_video`

Institutional memory loaded when the current task has `task_type=ai_video`. Layered on top of `general.md` in this same folder; per-task-type rules win when they conflict.

## Default angle catalog

The parent picks a relevant subset per `general.md` principle 1. This is a catalog, not a checklist. Each angle's worker writes to `findings/angle-<slug>.md` with citations per `general.md` principle 2.

### 1. story-structure

What narrative shape does the project want?

- **novel:** episode arc + season arc. For 短剧 specifically: per-episode hook → escalation → cliffhanger; season arc with inciting incident, midpoint reversal, payoff.
- **short:** hook (≤3 s) → escalation → payoff (punchline / reveal / loop).

**Citation bar:** at least two real comparable productions linked, with their structural pattern named.

### 2. character-design

What does each main character look / sound / move like? Resolves to a Chinese visual descriptor (面貌 / 发型 / 服装 / 身材 / 气质 / 标志性动作) per character. The descriptor must be specific enough that two artists reading it would draw the same character.

**Citation bar:** each character description references at least one real source image / still (URL); the descriptor is in Chinese, the URLs may be from any source.

### 3. visual-style

Cinematography, lighting, color palette, lens behavior, motion vocabulary. Drives the per-shot mood / motion fields.

**Citation bar:** at least three visual references with URLs; describe the palette in named or RGB terms (`暖橘黄主调 #F2A65A + 冷青阴影 #2E5C6E`), not in vibes.

### 4. platform-conventions

Per-platform best practices: Douyin hook timing, 快手 captioning conventions, YouTube Shorts retention curve, 视频号 thumbnail conventions, hashtag conventions per platform.

**Citation bar:** cite each platform's official creator docs OR a 2025+ creator-economy article with date.

### 5. 15s-shot-decomposition

How does scene-X get split into ≤15 s atomic clips that Kling / Seedance can each generate in one pass? Models the seam constraint: motion start/end states, character continuity tokens between shots, prop position carry-over.

**Citation bar:** cite Kling and Seedance documentation for length cap, supported motion descriptors, image-to-video parameter set.

### 6. kling-seedance-prompt-schema

What does a high-quality Chinese prompt look like for Kling vs Seedance today? Both share text-to-video; Kling supports image-to-video with character ref. Schema differences matter — fields, length, motion-vocabulary keywords, negative-prompt support.

**Citation bar:** cite each tool's prompt guide; include 1–2 worked examples in Chinese with annotated structure (角色 / 场景 / 动作 / 镜头 / 光线 / 比例 / 时长).

### 7. seedream-character-ref-prompt

What does a high-quality Seedream立绘 prompt look like? Output: full-body or 3/4 turnaround, neutral pose, clean background — usable as the reference frame for every Kling image-to-video shot featuring this character.

**Citation bar:** cite Seedream prompt guide + 1 worked example per common 短剧 character archetype the project is likely to want.

### 8. (novel only) episode-arc-pacing

Across the planned episode count, where do beats land? Inciting incident at ep N, midpoint reversal at ep M, payoff at ep K. Tied to the genre captured in stage 2.

### 9. (novel only) series-hook-strategy

What ends episode N to make the user start episode N+1? Cliffhanger / unresolved dialogue / reveal of a new threat. Match dominant 短剧 conventions; cite real successful series.

## `dossier.md` requirements

Beyond the synthesis required by `general.md` principle 3:

- **Concrete character descriptor for every named character.** Stage 4 inherits these verbatim; the spec stage MUST NOT regenerate descriptors from thin air.
- **Concrete style-guide table.** Palette (named + hex), lens characteristics, lighting state vocabulary, motion characteristics. Stage 4 inherits this as `style_guide.md`.
- **One worked sample shot decomposition** for one scene of the project — same scene split into N ≤15 s shots, each with a Kling prompt block, a Seedance prompt block, and the continuity tokens between shots. Stage 4 inherits this as the prompt template applied to every other scene.

## Update protocol

Surgical: new angle or new dossier requirement only when a real run surfaces a need. Cite source run id.
