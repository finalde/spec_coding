---
worker_id: level-specialist-03-ai_video_compliance
stage: 5
role: level-specialist
level: ai_video_compliance
status: complete
blockers: []
confidence: high
---

# Level — `ai_video_compliance`

The project-rules gate. Validates that every stage-6 ep01 output conforms to the mandatory schema / layout / language / aspect-ratio / publish-metadata / pin-preservation contracts in `.claude/agent_refs/project/ai_video.md` (rules #1, #2, #5, #6, #7, #8, #9, #11, #12.1–12.7) and `.claude/agent_refs/validation/ai_video.md` (moves 1, 2, 5, 6, 7).

## Scope + the rule-4-vs-rule-5 reconciliation

**Rule-4-vs-rule-5 reconciliation (load-bearing).** `.claude/agent_refs/project/ai_video.md` was authored across several follow-ups; two passes left contradictory layout hints:

- **Legacy rule #4 (high-level semantic)** + **rule #2 layout block** + **`validation/ai_video.md` move 4** all describe the per-shot deliverable as **three separate files**: `shots/shotNN_kling.md` + `shots/shotNN_seedance.md` + `shots/shotNN_lastframe_seedream.md` (+ `shot01_startframe_seedream.md` on the episode's first shot).
- **Rule #5 (rev follow-up 007) + rule #12.6 + rule #12.4 v2** **supersede** the older split: every shot ships as **one** self-contained `shotNN.md` with three internal sections — ① Shot context + ② `## 视频 prompt` ```text``` fenced block carrying the rule #12.4 v2 14-field schema + ③ embedded `## Seam-frame still prompts` code blocks (lastframe every shot; startframe only on the episode's shot 01).
- **Current contract = rule #5.** Rule #4 is legacy and explicitly says (rule #5 final line) "supersedes rule #5 file-set requirement; supersedes rule #11 seam-frame independent file structure." `validation/ai_video.md` move 4 ("Dual-prompt presence + seam-frame still-image prompts") therefore requires **adaptation**: the validator no longer looks for three files per shot; it looks for ONE `shotNN.md` whose body satisfies the three internal sections above.
- **Folder-per-asset variant (rule #12.8 v2 + rule #12.9, per follow-up 014).** A shot may equivalently live at `episodes/ep{NN}/shots/shot{NN}/shot{NN}.md` (folder of same name with gitignored media siblings). The validator MUST accept either `episodes/ep01/shots/shotNN.md` OR `episodes/ep01/shots/shotNN/shotNN.md`.
- **The spec for `feng_shou_lu` (FR-9, FR-10) is explicit:** it uses the flat `episodes/ep01/shots/shotNN.md` pattern. Validator default = flat; folder variant is a documented alternative if stage 6 switches.

**Spec path note.** `final_specs/spec.md` puts the canonical text artifacts under `my_novel/feng_shou_lu/` and only mirrors a README at `ai_videos/feng_shou_lu/README.md` (FR-13). Validator paths therefore root at `my_novel/feng_shou_lu/` for FR-1 through FR-12, plus `ai_videos/feng_shou_lu/README.md` for FR-13. `validation/ai_video.md` Move 1's "every `*.md` under `ai_videos/{name}/`" language is **broadened** to also cover `my_novel/feng_shou_lu/` for this project — that's where the body content lives.

**Language compliance gate cross-check.** ai_video.md rule #1 explicitly says **file content** must be Chinese, but folder + structural file names (`README.md`, `world.md`, `shotlist.md`, `episodes/ep01/`, `shots/`, etc.) stay English / pinyin. The spec's `characters/裴知秋.md` filename is the opt-in Chinese-filename allowance (rule #1 paragraph 2) — explicitly recorded as a divergence in the spec; this is **valid** and must NOT be flagged.

---

## Validators

### V-1 Language compliance

- **Source rules:** ai_video.md rule #1; validation/ai_video.md move 1; spec NFR-11.
- **Trigger:** stage 6 — runs at the close of every work unit that writes or rewrites any `*.md` under `my_novel/feng_shou_lu/` or `ai_videos/feng_shou_lu/`. Final pass once all ep01 deliverables exist.
- **Check (executable):**
  1. Enumerate every `*.md` under `my_novel/feng_shou_lu/**` and `ai_videos/feng_shou_lu/**`.
  2. Per file: read content, strip ```...``` fenced blocks (any language tag), strip YAML frontmatter (`---` … `---` at top), strip raw URLs (`https?://\S+`), strip Markdown link syntax (`[text](url)` → keep `text`), strip hex color tokens (`#[0-9A-Fa-f]{3,8}`), strip ASCII punctuation runs.
  3. Tokenize the remainder. Count:
     - `chinese` = chars in Unicode block CJK Unified (`一-鿿`) + CJK Ext-A (`㐀-䶿`) + CJK fullwidth punctuation (`　-〿`, `＀-￯`).
     - `latin` = ASCII letters NOT in the allow-list `{Kling, Seedance, Seedream, Sora, Veo, Runway, Midjourney, Imagen, Flux, 9:16, 16:9, 1:1, ep01, ep02, ..., shot01, shot02, ..., text, png, mp4, K, HDR, fps, hex, lux, K, ASCII, UTF-8}` and NOT matching `c\d+_` / `s\d+_` placeholder prefixes.
  4. Pass if `chinese / (chinese + latin) ≥ 0.95`.
  5. Allow exception: any file in `my_novel/feng_shou_lu/copyright_clearance.md`'s BLACKLIST table that quotes baseline-novel terms verbatim — those rows are stripped before the ratio is computed (regex: lines starting with `| ` inside a `## BLACKLIST` section).
- **Severity:** any file < 95% Chinese-block → `blocker`. Filename in Chinese with no English/pinyin alternative + no divergence note in spec → `warning` (the spec's named `characters/裴知秋.md` etc. are pre-approved by FR-5 + rule #1 opt-in; structural files `world.md` / `style_guide.md` / etc. must stay English/pinyin → English filename on those = pass, Chinese filename on those = `blocker`).
- **Expected outcome:** `pass` if all files clear the 95% threshold AND every structural filename matches the FR-1 to FR-13 path list.

### V-2 15-second shot atomicity + beat-sum

- **Source rules:** ai_video.md rule #6, rule #12.4 v4 动作 timing 契约; validation/ai_video.md move 2; spec NFR-5.
- **Trigger:** stage 6 — runs immediately after `episodes/ep01/shotlist.md` is written, and again after each `episodes/ep01/shots/shotNN.md` is written.
- **Check (executable):**
  1. Parse `episodes/ep01/shotlist.md`. For each shot row, extract `shot_id` + `时长` (regex: `时长[:：]\s*(\d+)\s*[s秒]`).
     - 3 ≤ 时长 ≤ 15 → pass.
     - 时长 missing → `blocker` (no rationale).
     - 时长 < 3 or > 15 → `blocker` UNLESS the Shot context Summary in `shots/shotNN.md` carries a divergence note per rule #6 final paragraph.
  2. For each `shots/shotNN.md`:
     a. Locate the `## 视频 prompt` `text` fenced block.
     b. Extract `时长:` line — must match `时长[:：]\s*(\d+)\s*[s秒]`.
     c. Extract `动作:` block — collect every beat timecode `(\d+)[-–](\d+)\s*[s秒]` (or `0–{时长}s` single beat).
     d. Beats MUST be contiguous (beat[i].end == beat[i+1].start) and MUST cover [0, 时长].
     e. Sum of (beat.end − beat.start) MUST exactly equal `时长`.
  3. Cross-check: shotlist.md `时长` for shot NN == `shots/shotNN.md` `时长:` for same NN (exact integer match).
- **Severity:**
  - Shot > 15 s = `blocker`.
  - Beat sum ≠ 时长 OR beats non-contiguous OR don't cover [0, 时长] = `blocker`.
  - shotlist `时长` ≠ prompts `时长` for same shot = `blocker`.
  - Shot < 3 s without divergence note = `blocker`; with note = `warning` (per rule #6 final paragraph).
- **Expected outcome:** `pass` if every shot in 6–10 shot range obeys all three rules.

### V-3 File layout per rule #2 (novel sub_type)

- **Source rules:** ai_video.md rule #2 (novel layout) + spec FR-1 through FR-13.
- **Trigger:** stage 6 — runs after the parent declares all work units complete; ALSO as a pre-flight check before any work unit that depends on a prior artifact (e.g., before shot prompts are written, `characters/` + `scenes/` must exist).
- **Check (executable):** assert each of the following paths exists with non-empty content:
  ```
  my_novel/feng_shou_lu/README.md
  my_novel/feng_shou_lu/world.md
  my_novel/feng_shou_lu/style_guide.md
  my_novel/feng_shou_lu/arc_outline.md
  my_novel/feng_shou_lu/characters/裴知秋.md
  my_novel/feng_shou_lu/characters/裴长砚.md
  my_novel/feng_shou_lu/characters/闻砚清.md
  my_novel/feng_shou_lu/characters/容漪.md
  my_novel/feng_shou_lu/characters/卫长烛.md
  my_novel/feng_shou_lu/characters/应砚之.md
  my_novel/feng_shou_lu/characters/戚归砚.md
  my_novel/feng_shou_lu/characters/池洇.md
  my_novel/feng_shou_lu/characters/阮惘.md
  my_novel/feng_shou_lu/characters/言息.md
  my_novel/feng_shou_lu/characters/ref_images/  ⟶ ≥ 9 *_seedream.md (10 if 裴知秋 two-file variant per FR-5.1)
  my_novel/feng_shou_lu/scenes/s1_无寿崖.md
  my_novel/feng_shou_lu/scenes/s2_落雁渊.md
  my_novel/feng_shou_lu/scenes/ref_images/s1_无寿崖_seedream.md
  my_novel/feng_shou_lu/scenes/ref_images/s2_落雁渊_seedream.md
  my_novel/feng_shou_lu/episodes/ep01/script.md
  my_novel/feng_shou_lu/episodes/ep01/shotlist.md
  my_novel/feng_shou_lu/episodes/ep01/shots/  ⟶ shotNN.md ×  count_in [6, 10]
  my_novel/feng_shou_lu/episodes/ep01/publish.md
  my_novel/feng_shou_lu/copyright_clearance.md
  ai_videos/feng_shou_lu/README.md
  ```
- **Additional checks:**
  - `episodes/ep01/shots/` shot count is in `[6, 10]` (FR-9). < 6 or > 10 = `blocker`.
  - shot files match either `shotNN.md` (flat) or `shotNN/shotNN.md` (folder-per-asset, rule #12.8 v2). Mixed patterns across shots in same episode = `warning` (stylistic inconsistency).
  - Folder names match the rule #1 enumeration (English / pinyin for structural; opt-in Chinese for content files per spec FR-5). `characters/<role>.md` Chinese filename is pre-approved per spec; any non-listed Chinese filename without spec divergence note = `blocker`.
  - 裴知秋 Seedream files: either ONE file `裴知秋_seedream.md` containing both states OR TWO files `裴知秋_state_a_seedream.md` + `裴知秋_state_b_seedream.md` (FR-5.1). Neither pattern present = `blocker`.
- **Severity:** any missing required path = `blocker`. Folder name in Chinese for a structural file = `blocker` (rule #1).
- **Expected outcome:** `pass` if all required paths exist + non-empty + shot count in range.

### V-4 Single self-contained shotNN.md schema (rules #5 + #12.4 v2/v4 + #12.6)

- **Source rules:** ai_video.md rule #5 (single self-contained shot file), rule #12.4 v2 (14-field 视频 schema), rule #12.4 v4 (字数上限 + 角色 line trim + 渲染样式 ≤9 / 负向 ≤24), rule #12.6 (三段 Shot context), rule #11 (seam-frame contract for embedded code blocks).
- **Trigger:** stage 6 — runs immediately after each `shots/shotNN.md` is written.
- **Check (executable):** for each `episodes/ep01/shots/shotNN.md`:
  1. **Section 1 — Shot context** must contain all 5 sub-items per rule #12.6:
     - `**Summary**:` (2–3 sentences)
     - `**出场角色 / Characters in this shot**:` table
     - `**场景 / Scene**:` referencing `scenes/sN_*.md` if declared, inline otherwise
     - `**时长 / Duration**:` line `X seconds — hard 上限 15s` + timed-beats summary
     - `**Reference uploads — pre-flight checklist**:` checkbox list
     - Missing any sub-item = `blocker`.
  2. **Section 2 — `## 视频 prompt` `text` fenced block** must contain every required field for the video-shot column of the rule #12.4 v2 mandatory-matrix:
     - Required: `角色:`, `场景:`, `镜头:`, `动作:`, `台词 / 字幕:`, `光线 / 色调:`, `节奏:`, `渲染样式:`, `比例:`, `时长:`, `负向:`.
     - Conditional: `[参考图]` / `input_image_urls` — present iff target model supports image-to-video.
     - Any required field missing = `blocker`.
  3. **Field-level sub-checks:**
     - `角色:` line = byte-identical 一句话锁定 + ~50–80 字 face-differentiator per character (rule #12.4-A v3, rule #12.4 v4). If shot has ≥ 4 named characters, only the first 3 carry full 一句话锁定; rest may be 1-line collective reference (rule #12.4-A). Violation = `blocker`.
     - `场景:` line must match `scenes/sN_*.md` 「一句话锁定」 byte-identically when scene is declared, OR be inline if scene is not declared.
     - `镜头:` line uses 景别 + 运动 vocabulary from `style_guide.md § 镜头语言关键词字典` — vocab not in dictionary = `warning` (style drift, may not be intentional novelty).
     - `动作:` timed beats — already covered by V-2.
     - `台词 / 字幕:` follows one of the 三选一 formats (rule #12.4 v3 / v4 / 12.6 v2): 内嵌硬字幕 / 后期软字幕 / 无台词. Format violations = `blocker`. Per FR-10.4 the project default is 内嵌硬字幕 for 系统弹窗 / 集头标题 / 黄金钩台词 and 后期软字幕 for everything else — drift from the default flagged as `warning` (author judgment).
     - `渲染样式:` re-pastes from `style_guide.md § 正向关键词`; ≤ 9 core keywords per rule #12.4 v4. > 9 = `warning`. Must include ≥ 4 photorealism 强化 keywords per rule #12.7-B+ — missing = `warning`.
     - `负向:` re-pastes from `style_guide.md § 负向锁定`; ≤ 24 core items per rule #12.4 v4. > 24 = `warning`. Must include all 14 项扩展 photorealism 负向 (rule #12.7-B+) and all 11 项 AI-同质化 负向 (rule #12.7-C) — missing any of these required core items = `blocker`.
     - `比例:` line MUST be `比例: 9:16` — see V-5.
     - `时长:` integer 3–15 — see V-2.
  4. **Section 3 — `## Seam-frame still prompts`** must contain:
     - One `text` code block for **lastframe** Seedream prompt (EVERY shot).
     - One `text` code block for **startframe** Seedream prompt — present iff shot is the FIRST shot of ep01 (i.e., shot01.md) per rule #11; absent on shot02–shotNN; presence-elsewhere = `warning`.
     - Each seam-frame block must contain rule #12.4 v2 静帧 seam column required fields: `主体定义:`, `角色:` (byte-identical 一句话锁定), `场景:`, `镜头:` (景别 only, no 运动), `姿态（frozen instant）:`, `光线 / 色调:`, `渲染样式:`, `比例:`, `负向:`.
     - Missing lastframe code block on any shot = `blocker`.
     - Missing startframe code block on shot01.md = `blocker`.
     - Any required field missing inside a seam block = `blocker`.
     - Lastframe 主体定义 + 姿态 MUST match the video shot's final 动作 beat frozen state (rule #12.4 v4 动作 timing 契约 → 最后一拍 frozen 状态). Drift = `warning` (subjective, surface to manual walkthrough).
  5. **Byte-cap (rule #12.4 v4 / NFR-1 / spec FR-10.7):**
     - Count characters inside the `## 视频 prompt` `text` fenced block contents only (exclude the ``` fence lines, exclude Shot context section, exclude seam-frame blocks). Each Chinese char + each ASCII char = 1.
     - body ≤ 2000 字 → `pass` (soft).
     - 2000 < body ≤ 2500 字 → `warning` (soft-cap exceeded).
     - body > 2500 字 → `blocker` UNLESS Shot context Summary carries one of the rule #12.4-E exception notes (multi-character cover-frame OR ≥ 8 s density-only). With note → `pass`.
- **Severity:** see per-rule severity above.
- **Expected outcome:** `pass` if every shot prompt satisfies the three-section schema, every required field present, byte-cap honored, seam-frame contract honored.

### V-5 Aspect ratio + cliffhanger / cover-frame marker

- **Source rules:** ai_video.md rule #7 (aspect ratio), spec NFR-3, NFR-10, FR-9, FR-10.8; validation/ai_video.md move 5.
- **Trigger:** stage 6 — runs after `shotlist.md` is written, and after each `shots/shotNN.md` is written.
- **Check (executable):**
  1. Every `## 视频 prompt` `text` block must contain a `比例:` line.
     - `比例: 9:16` → pass.
     - `比例:` present but ≠ `9:16` → `pass` ONLY if spec.md carries an override divergence note (per rule #7); else `blocker`.
     - `比例:` missing → `blocker`.
  2. Every seam-frame code block in `## Seam-frame still prompts` section must also carry `比例:`. Missing = `blocker`.
  3. Every character立绘 prompt at `characters/ref_images/*_seedream.md` and every scene立绘 prompt at `scenes/ref_images/*_seedream.md` MUST contain `9:16` or `画幅: 9:16` token. Missing = `blocker`.
  4. **Cliffhanger / cover-frame marker:** `shotlist.md` MUST contain exactly one row with `cover_frame: true` (FR-9 + FR-10.8). The same shot's `shots/shotNN.md` Shot context Summary MUST contain the `cover_frame: true` line.
     - Multiple rows with `cover_frame: true` → `blocker` (rule says exactly one cliffhanger / thumbnail-of-choice).
     - Zero rows → `blocker`.
     - Marker on shotlist but missing on prompt md → `blocker`.
  5. **Hook composition (subjective — surface to manual walkthrough).** Per validation/ai_video.md move 5 novel carve-out: hook composition (subject in upper third, motion start within 0.5 s of frame zero) is NOT auto-blocker for novels. Emit `validation.requires_manual_walkthrough` with prompt: *"Open shots/shotNN.md (cliffhanger shot) and confirm the 镜头 + 动作 first 0.5 s composes a thumbnail-grade cover frame."*
- **Severity:** `比例:` missing or wrong = `blocker`. cover_frame marker missing / duplicated / mismatched = `blocker`. Hook composition = `validation.requires_manual_walkthrough`.
- **Expected outcome:** `pass` if all `比例: 9:16` present, exactly one cover_frame shot marked consistently across shotlist + prompt md, manual walkthrough emitted.

### V-6 Publish metadata presence (`episodes/ep01/publish.md`)

- **Source rules:** ai_video.md rule #8; validation/ai_video.md move 6; spec FR-11.
- **Trigger:** stage 6 — runs after `episodes/ep01/publish.md` is written.
- **Check (executable):** parse `episodes/ep01/publish.md` as Markdown and assert:
  1. **标题** section — non-empty + Chinese char count ≤ 30. Empty = `blocker`; > 30 字 = `blocker`.
  2. **简介** section — non-empty + Chinese char count ≤ 200. Empty = `blocker`; > 200 字 = `blocker`.
  3. **标签** section — count `#`-prefixed hashtags. Count must be in `[5, 10]`. Outside range = `blocker`.
  4. **封面建议** section — non-empty + MUST reference a `shotNN_lastframe.png` (or `shots/shotNN/shot{NN}_lastframe.png` folder variant) where shotNN is the cover_frame shot identified in V-5 (FR-9 cliffhanger). Missing reference / wrong shot = `blocker`.
  5. **平台备注** section — non-empty + MUST mention `Douyin` (or `抖音`) AND `红果` (FR-11). May additionally mention `YouTube Shorts` with the explicit text `EN subtitle pass deferred` per spec FR-11 + qa.md Q13. Missing either Douyin or 红果 = `blocker`. YouTube Shorts mentioned without the EN-deferred note = `warning`.
- **Severity:** any of the five fields missing / empty / over-budget = `blocker`.
- **Expected outcome:** `pass` if all five sections present, lengths in budget, cross-refs resolve.

### V-7 Pinned items survive regeneration

- **Source rules:** validation/general.md principle 8; validation/ai_video.md move 7; CLAUDE.md § Pinned items survive regeneration.
- **Trigger:** stage 5 strategy emits this check for stages 2 / 3 / 4 / 5 ONLY. Stage 6 is OUT of scope per v1 (no project-code promotion). Within stage 6 this validator is **not generated** for stage-6 work units — but the check IS specified here so that any future stage-2/3/4/5 regen run for `xianxia_new` (e.g., a stage-4 spec re-emit) honors it.
- **Status as of this stage 5:** `specs/ai_video/xianxia_new/interview/promoted.md`, `findings/promoted.md`, `final_specs/promoted.md`, `validation/promoted.md` are all currently empty / nonexistent. Validator MUST still be specified for future runs.
- **Check (executable):** for each stage `S ∈ {interview, findings, final_specs, validation}`:
  1. If `specs/ai_video/xianxia_new/<S>/promoted.md` does not exist OR is empty → check returns `pass (no pins)`.
  2. Otherwise, parse the file via `libs/promotions.py::parse_promoted_text` (per CLAUDE.md / general.md principle 8). For each pinned item:
     a. Locate the canonical artifact for that stage (`interview/qa.md` / `findings/dossier.md` / `final_specs/spec.md` / `validation/strategy.md`).
     b. Assert the pinned text appears in the canonical artifact byte-identically modulo whitespace.
     c. If the original insertion point (line / heading anchor) no longer exists, the pin MUST appear under the canonical artifact's `## Pinned items (orphaned)` section.
- **Severity:**
  - Missing pin (pinned text not anywhere in artifact) = `critical` (halts work unit — silent loss of user-pinned content is the highest-priority regression per general.md principle 8).
  - Out-of-place pin (under "(orphaned)" without justification note) = `blocker`.
  - Empty `promoted.md` → `pass (no pins)`.
- **Expected outcome:** `pass (no pins)` for this stage-5 run; check remains specified for future regenerations.

---

## Validator priority order

Per work_unit_kind. Stage 6 emits one work unit per artifact group; validators run in this order so that contract failures surface before content-content failures:

| Priority | Validator | Kind | Notes |
|---|---|---|---|
| 1 | V-3 (layout / file existence) | `pre_flight` per work unit | Cheapest, runs first. If a prerequisite path is missing, downstream validators have nothing to check. |
| 2 | V-1 (language compliance) | `per_file` (after each *.md write) | Catches accidental English content body before going deeper. Runs on every file as it's written. |
| 3 | V-2 (15 s + beat sum) | `per_shot` (for shotlist + each shotNN.md) | Numerical, cheap; runs after V-1 on shot-related files. |
| 4 | V-5 (aspect ratio + cover_frame) | `per_shot` + `per_prompt_file` (立绘 too) | Cheap regex; runs after V-2 on shot files; runs standalone on立绘 files. |
| 5 | V-4 (shotNN.md schema) | `per_shot` (after each shotNN.md write) | Deepest schema check; depends on V-2 (动作 timed beats) + V-5 (比例) being clean first. |
| 6 | V-6 (publish.md) | `per_episode` (one-shot at episode close) | Runs once after `publish.md` exists; depends on V-4 (so it can resolve the cover_frame shot reference). |
| 7 | V-7 (pinned-items preservation) | `per_stage_regen` | Stage-5 here emits as `pass (no pins)` for the current run; check is dormant unless a future regen of stages 2/3/4/5 populates `promoted.md`. NOT generated for stage-6 work units. |

**Cross-cutting rule:** V-1 + V-2 + V-5 are gating cheap checks; V-4 is the deep schema; V-3 + V-6 + V-7 are once-per-set checks. The parent SHOULD NOT proceed to V-4 on a shot file that fails V-2 (动作 timed beats malformed → V-4 cannot meaningfully validate the body).

**work_unit_kind taxonomy** (recommended for stage 6 to consume):

- `pre_flight` — V-3 file-layout assertion before any other validator runs against a work unit's outputs.
- `per_file` — V-1 language check, runs on each `*.md` write.
- `per_shot` — V-2, V-4, V-5 cluster, runs on each shotNN.md (and on shotlist.md for V-2 / V-5 portions).
- `per_prompt_file` — V-5 ratio check on `characters/ref_images/*_seedream.md` + `scenes/ref_images/*_seedream.md`.
- `per_episode` — V-6 publish.md check, runs after the episode's last work unit closes.
- `per_stage_regen` — V-7 pin-preservation, dormant when promoted.md is empty.

---

## Stage-6 audit-event template

Per the event types defined in CLAUDE.md § Event stream + validation/general.md principle 5 ("the audit log is part of the validation artifact"). Every validator MUST emit at least one started event and either a pass or one-or-more issue events. Halt events (`pipeline.halted`) are emitted only on `critical` severity (V-7 missing-pin path) or on the third consecutive revision-round failure for any `blocker`.

Each event is one JSONL line appended to `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl`.

### V-1 Language compliance

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-1", "scope": "<file_path>", "pre_reading_consulted": ["<abs_path>", ...]}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-1", "scope": "<file_path>", "metrics": {"chinese_ratio": 0.978, "file_count_passed": 1}}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-1", "scope": "<file_path>", "severity": "blocker", "rule": "ai_video.md#1", "detail": "chinese_ratio=0.62 below 0.95 threshold; offending tokens=[...]"}
```

### V-2 15-second + beat-sum

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-2", "scope": "episodes/ep01/shots/shot03.md"}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-2", "scope": "episodes/ep01/shots/shot03.md", "metrics": {"shot_id": "shot03", "时长": 11, "beat_sum": 11}}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-2", "scope": "episodes/ep01/shots/shot03.md", "severity": "blocker", "rule": "ai_video.md#6 + #12.4 v4 动作 timing 契约", "detail": "shot03 时长=11s, beat_sum=8s (beats: 0-3, 3-6, 6-8); gap [8s, 11s]"}
```

### V-3 File layout

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-3", "scope": "my_novel/feng_shou_lu/**"}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-3", "scope": "my_novel/feng_shou_lu/**", "metrics": {"required_paths_present": 23, "shot_count": 7}}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-3", "severity": "blocker", "rule": "ai_video.md#2 + spec FR-7", "detail": "missing scenes/ref_images/s2_落雁渊_seedream.md"}
```

### V-4 shotNN.md schema

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-4", "scope": "episodes/ep01/shots/shot01.md"}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-4", "scope": "episodes/ep01/shots/shot01.md", "metrics": {"shot_context_subitems_present": 5, "video_prompt_fields_present": 11, "seam_lastframe_present": true, "seam_startframe_present": true, "video_prompt_body_chars": 1834}}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-4", "scope": "episodes/ep01/shots/shot05.md", "severity": "blocker", "rule": "ai_video.md#12.4 v2 mandatory matrix", "detail": "shot05 视频 prompt block missing required field '负向:'"}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-4", "scope": "episodes/ep01/shots/shot07.md", "severity": "warning", "rule": "ai_video.md#12.4 v4 字数上限 soft", "detail": "shot07 video prompt body = 2187 字 (soft cap 2000)"}
```

### V-5 Aspect ratio + cover_frame

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-5", "scope": "episodes/ep01/"}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-5", "scope": "episodes/ep01/", "metrics": {"shots_checked": 7, "cover_frame_shot": "shot07"}}
{"ts": "<ISO8601>", "event": "validation.requires_manual_walkthrough", "work_unit": "<wuk>", "validator": "V-5", "scope": "episodes/ep01/shots/shot07.md", "prompt": "Open shots/shot07.md (cliffhanger) and confirm 镜头 + 动作 first 0.5 s composes a thumbnail-grade cover frame."}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-5", "scope": "characters/ref_images/容漪_seedream.md", "severity": "blocker", "rule": "ai_video.md#7 + spec NFR-3", "detail": "Seedream立绘 prompt missing '9:16' / '画幅: 9:16' token"}
```

### V-6 publish.md

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-6", "scope": "episodes/ep01/publish.md"}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-6", "scope": "episodes/ep01/publish.md", "metrics": {"标题_字数": 22, "简介_字数": 178, "标签数": 7, "封面建议_shot": "shot07"}}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-6", "scope": "episodes/ep01/publish.md", "severity": "blocker", "rule": "ai_video.md#8 + spec FR-11", "detail": "标签 count=4, required 5-10"}
```

### V-7 Pinned items

```jsonl
{"ts": "<ISO8601>", "event": "validation.started", "work_unit": "<wuk>", "level": "ai_video_compliance", "validator": "V-7", "scope": "specs/ai_video/xianxia_new/<stage>/promoted.md"}
{"ts": "<ISO8601>", "event": "validation.pass", "work_unit": "<wuk>", "validator": "V-7", "scope": "specs/ai_video/xianxia_new/<stage>/promoted.md", "metrics": {"pin_count": 0, "note": "no pins to preserve"}}
{"ts": "<ISO8601>", "event": "validation.issue.raised", "work_unit": "<wuk>", "validator": "V-7", "scope": "specs/ai_video/xianxia_new/findings/promoted.md", "severity": "critical", "rule": "general.md principle 8", "detail": "pin id=p3 text='{...}' not present in findings/dossier.md (silent loss)"}
{"ts": "<ISO8601>", "event": "pipeline.halted", "work_unit": "<wuk>", "reason": "critical V-7 missing-pin", "validator": "V-7"}
```

---

## Pre-reading consulted

- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/final_specs/spec.md`
- `C:/workspace/spec_coding/.claude/agent_refs/project/ai_video.md` (rules #1, #2, #5, #6, #7, #8, #9, #11, #12.1, #12.2, #12.3, #12.4 v2/v4, #12.4-A, #12.4-B, #12.4-D, #12.4-E, #12.5, #12.6, #12.7, #12.8, #12.9)
- `C:/workspace/spec_coding/.claude/agent_refs/validation/ai_video.md` (moves 1, 2, 4, 5, 6, 7 + severity escalations table)
- `C:/workspace/spec_coding/.claude/agent_refs/validation/general.md` (principle 5 audit-log + principle 8 pin preservation + standard severity policy)

## Executive summary

- **7 validators (V-1 through V-7); 6 of the 7 emit `blocker` severity on primary failure (V-7 escalates to `critical` on missing pin), so the gate is strict — only V-5 hook-composition + V-4 byte-cap-soft + a small set of stylistic vocab checks downgrade to `warning` / `validation.requires_manual_walkthrough`.**
- **Most likely failure mode for ep01:** V-4 schema drift on `shotNN.md` — specifically the `动作:` timed-beat sum ≠ `时长:` (rule #12.4 v4 动作 timing 契约) combined with the `负向:` line under-populating the required 14 项扩展 photorealism + 11 项 AI-同质化 items per rule #12.7-B+/C. Stage 6 will need to re-paste from style_guide.md verbatim, not paraphrase.
- **Recommended `work_unit_kind` taxonomy for stage 6:** `pre_flight` (V-3) → `per_file` (V-1) → `per_shot` (V-2, V-4, V-5 cluster on shotNN.md) → `per_prompt_file` (V-5 ratio check on `_seedream.md` files) → `per_episode` (V-6) → `per_stage_regen` (V-7, dormant this run). The parent stops on V-2 failure for a shot before running V-4 on that same shot.
