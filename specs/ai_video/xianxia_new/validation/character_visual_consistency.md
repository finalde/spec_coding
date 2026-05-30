---
worker_id: level-specialist-04-character_visual_consistency
stage: 5
role: level-specialist
level: character_visual_consistency
status: complete
blockers: []
confidence: high
---

# Validation level — character_visual_consistency

## 1. Scope + role-of-this-level

**Scope.** Byte-identical 一句话锁定 + face-differentiator strings across every prompt that references the same character — within a single episode AND between the three artifact layers that name a character:

1. **Character bible** — `my_novel/feng_shou_lu/characters/{name}.md` (per spec FR-5, ai_video.md rule 12.1).
2. **Seedream立绘 prompt** — `my_novel/feng_shou_lu/characters/ref_images/{name}_seedream.md` (per FR-6, rule 12.2).
3. **Shot prompts** — `my_novel/feng_shou_lu/episodes/ep01/shots/shotNN.md` (per FR-10, rule 12.4 v4).

**Role of this level vs `ai_video_compliance` (sibling level).** Hard separation:

| Aspect | character_visual_consistency (this level) | ai_video_compliance |
|---|---|---|
| Granularity | CROSS-FILE — every check requires reading ≥ 2 files and byte-diffing extracted substrings. | SINGLE-FILE — each check reads one file and validates schema/field presence. |
| Failure mode caught | Character identity drift across shots (the load-bearing failure for image-first pipelines). | Missing fields, wrong aspect ratio, prompt-body length exceeding NFR-1, broken schema. |
| Authority | Owns the byte-identical contract per ai_video.md rule 4 + 12.4 + NFR-2. | Owns the schema contract per ai_video.md rule 12.1 / 12.2 / 12.3 / 12.4 v4. |
| Overlap | This level assumes ai_video_compliance has already confirmed the field EXISTS. It then checks if the field's value matches across files. | If a `一句话锁定` row is missing entirely, ai_video_compliance flags it as a schema blocker; this level does NOT redundantly re-flag it. |

If both levels would flag the same defect, the schema-side blocker (ai_video_compliance) is raised first; this level's cross-file check only runs once the field is present. This avoids double-counting blockers in the audit log.

## 2. Validators V-CV-1 through V-CV-8

Each validator has a fixed `validator_id` so stage-6 streaming validation can emit `validation.issue.raised` events with stable identifiers (per CLAUDE.md § Event stream).

### V-CV-1 — Character bible existence

- **validator_id:** `V-CV-1`
- **Trigger:** Stage 6 work-unit kinds `episode_full` and any `shot_prompt`. Also runs at `character_bible` work-unit completion (sanity loop — same file written, then re-read).
- **Check (executable):**
  1. Read every `episodes/ep01/shots/shot*.md`. Parse the `角色:` line for character names (each name = a substring matching the FR-5 cast list `[裴知秋, 裴长砚, 闻砚清, 容漪, 卫长烛, 应砚之, 戚归砚, 池洇, 阮惘, 言息]`).
  2. For each name encountered, assert `characters/{name}.md` exists and is non-empty (≥ 200 bytes — empty stub would pass naive existence check but fail real consumption).
  3. Cross-check the 9-character roster against FR-5 cast list: any FR-5 entry without a bible file = blocker even if no shot references it (deferred regression — they ship at episode_full).
- **Severity:** `blocker` (missing bible) — per validation/ai_video.md severity table "Missing Seedream ref-image prompt for a named character" extended to bible files in the same row's spirit.
- **Notes:** 裴长砚 is the past-life archived name; its bible file is the archived dossier (per spec FR-5). The validator accepts the bible file even if its body header reads `# 裴长砚 · 前世名（archived）` rather than `# 裴长砚 · {epithet}`.

### V-CV-2 — Seedream立绘 prompt existence

- **validator_id:** `V-CV-2`
- **Trigger:** Same as V-CV-1.
- **Check (executable):**
  1. For every name passing V-CV-1, assert `characters/ref_images/{name}_seedream.md` exists.
  2. **裴知秋 dual-state carve-out (FR-5.1):** the validator accepts EITHER `characters/ref_images/裴知秋_seedream.md` containing two `## Prompt — state A` + `## Prompt — state B` sections, OR the pair `characters/ref_images/裴知秋_state_a_seedream.md` + `..._state_b_seedream.md`. Missing either state = blocker.
  3. Each `_seedream.md` file body matches ai_video.md rule 12.2 four-section minimum: `主体 / 构图` + `面部` + `服装` + `负向` (the validator does not enforce ALL rule 12.2 sections — that's ai_video_compliance's job; this level only confirms the FILE exists and is non-empty for byte-comparison purposes).
- **Severity:** `blocker` (per validation/ai_video.md severity table row "Missing Seedream ref-image prompt for a named character").

### V-CV-3 — 锁定描述符 schema conformance

- **validator_id:** `V-CV-3`
- **Trigger:** Same as V-CV-1.
- **Check (executable):**
  1. For each `characters/{name}.md`, parse the `## 锁定描述符` table (per ai_video.md rule 12.1 — 10 rows).
  2. Assert all 10 rows present with non-empty values.
  3. Assert row #10 `一句话锁定` value is ≤ 30 Chinese characters (count Chinese chars; ASCII / punctuation excluded). This is the byte-identical anchor used in every shot.
  4. **裴知秋 dual-state carve-out (FR-5.1):** two tables labeled `## 锁定描述符 — state A: 重生弱体` + `## 锁定描述符 — state B: 寄生觉醒` BOTH must satisfy 1–3 above.
  5. Assert each bible has a `词源` row (per FR-5.2) — single line documenting in-fiction etymology from `findings/angle-character_anonymization.md` §3. Missing 词源 = blocker (not a warning — it's the seed for future-episode reveals).
- **Severity:** `blocker` for any missing field, empty value, missing 词源 row, or 一句话锁定 > 30 字.

### V-CV-4 — Byte-identical 一句话锁定 across shot prompts

**This is the load-bearing gate (per validation/ai_video.md move 3 + NFR-2).**

- **validator_id:** `V-CV-4`
- **Trigger:** Stage 6 work-unit kind `shot_prompt` (per-shot, runs after every shot prompt write) AND `episode_full` (closing pass across all 7 shots of ep01).
- **Check (executable):**
  1. For each shot prompt under `episodes/ep01/shots/shot*.md`, parse the `角色:` line of the fenced ```text``` block (per rule 12.4 v4). The line has the form `角色: {name1} — {一句话锁定_1} + {face-differentiator_1} · {name2} — {一句话锁定_2} + {face-differentiator_2} ...` (per rule 12.4-A).
  2. For each named character, extract the substring between `{name} — ` and the next ` · ` separator (or end-of-line). Apply normalization (§ 3).
  3. Across every shot of ep01 that references the same character, the extracted 一句话锁定 substring MUST be byte-identical (post-normalization).
  4. The face-differentiator portion (50–80 字 after the 一句话锁定 — for non-protagonist characters this is the locked 标志特征点 string from bible row #11; for 裴知秋 it is the shared state A/B differentiator string per V-CV-6) MUST also be byte-identical across shots for the SAME state of the same character.
- **Severity:** `blocker` on ANY drift between two shots within ep01. The error message MUST cite both shot files + both extracted substrings to make the diff manually patchable.

### V-CV-5 — Byte-identical 锁定 between bible, ref-image, and shots

- **validator_id:** `V-CV-5`
- **Trigger:** Stage 6 work-unit kinds `character_bible` (sanity loop after bible write), `seedream_prompt` (after each立绘 prompt write), and `episode_full` (closing pass).
- **Check (executable):**
  1. For each character, extract THREE candidate 一句话锁定 strings:
     - **A (bible):** `characters/{name}.md` § 锁定描述符 row #10 value.
     - **B (ref-image):** `characters/ref_images/{name}_seedream.md` Prompt header — the first sentence following `# Seedream 立绘 prompt — {name} ·` + `{epithet}\n参考: ...\n画幅: ...\n\n## Prompt\n\n{name} · {epithet}。{此处一句话锁定}` per rule 12.2 template.
     - **C (shots):** the set of unique 一句话锁定 substrings extracted in V-CV-4 across all shots of ep01 that reference this character.
  2. Assert `A == B`. Drift = blocker.
  3. Assert every element of `C ⊆ {A}` — i.e., the shot-extracted strings must equal `A` exactly (the bible is the source of truth). For 裴知秋 the set `{A}` has TWO elements (state A locked string + state B locked string).
- **Severity:** `blocker` on any pairwise drift; the error message MUST cite all three sources + their extracted substrings.

### V-CV-6 — 双形态契约 enforcement for 裴知秋

- **validator_id:** `V-CV-6`
- **Trigger:** Same as V-CV-5 + always runs as part of `episode_full`.
- **Check (executable):**
  1. Parse `characters/裴知秋.md` for BOTH `## 锁定描述符 — state A: 重生弱体` and `## 锁定描述符 — state B: 寄生觉醒`. Missing either = blocker.
  2. Extract the shared face-differentiator from bible row #11 of BOTH tables. Assert the **substring** `左眼下方 0.3cm 灰青胎记` appears byte-identically inside both state A's row #11 and state B's row #11 value (per visual_style §3.3.2 / dossier R-3). State A may caveat it as "半隐" / state B as "在寄生紫调下显现为冷紫色斑" — the validator accepts these state-specific framing words IF the canonical `左眼下方 0.3cm 灰青胎记` token is byte-present in both.
  3. For each shot prompt that references 裴知秋, parse the Shot context `state:` field (or, if the shot prompt does not declare a state field, infer state from which 一句话锁定 the shot uses):
     - State A 一句话锁定 string is the one paired with the state A bible row #10.
     - State B 一句话锁定 string is the one paired with the state B bible row #10.
  4. Assert no mismatch — i.e., a shot prompt that declares `state: A` (or uses no `state:` field but uses the state A anchor) MUST use the state A 一句话锁定; symmetric for state B. The face-differentiator substring `左眼下方 0.3cm 灰青胎记` MUST appear in the shot's 角色 line for 裴知秋 regardless of state (it is the shared mark identifying both as the same person).
- **Severity:** `blocker` on state mismatch, missing state-A/B label in bible, or missing shared face-differentiator substring.
- **Note:** ep01 narratively only shows state A (per FR-8 — the 寄生觉醒 motif is the first system event but the dossier R-4 0:30–1:15 beat shows the system弹窗 + 五拍 motif, which transitions into state B by 1:45). The validator therefore expects both state A and state B 一句话锁定 strings to appear in ep01 shot prompts; the cliffhanger shot (per FR-9 / FR-10.8) is the bridge — its 角色 line declares `state: A → B` or, simpler, the shot's 动作 timed beats hand off between the two anchors mid-shot. Stage 6 picks the implementation, but the bible + bookend pair must be consistent.

### V-CV-7 — Multi-character shot rule (≥ 4 named characters)

- **validator_id:** `V-CV-7`
- **Trigger:** Stage 6 work-unit kind `shot_prompt`.
- **Check (executable):**
  1. Count named characters in each shot's `角色:` line.
  2. If count ≥ 4 (per ai_video.md rule 12.4-A v4 "Multi-character shot"):
     - The line MUST list the first 3 main subjects' 一句话锁定 + face-differentiator in full.
     - The remaining characters MUST be summarized as `其余 N 名 ... (参考各 character refs)` or equivalent boilerplate.
  3. If the shot's `角色:` line expands all ≥ 4 character locked strings inline (e.g., the 倒叙 0:03–0:30 montage shot listing all 6 betrayers' anchors), flag as `warning` — the prompt body is still functionally renderable but exceeds NFR-1 prompt-budget pressure (per ai_video.md rule 12.4 v4 字数上限契约).
- **Severity:** `warning` (not blocker — over-budget but functional). The warning message proposes the rewrite: keep the first 3, collapse the rest. Stage 6 may accept the warning if the cover-frame justification is annotated in Shot context Summary per rule 12.4 v4 hard-limit exception clause.
- **Specifically for ep01:** the 倒叙 montage shot (shot02 per FR-8 / FR-9 — the 0:03–0:30 reasons-to-trust → reasons-to-die quick-cut) is the most likely V-CV-7 trigger. The shot has 6 betrayers + the protagonist + the师父 cameo = 7+ named characters in 27 seconds of split-frame. The validator expects this shot to ship with the `其余 N 名` collapse OR an explicit Shot context Summary note `本 shot 为 cover-frame / 全员同框，prompt 长度上限放宽` per rule 12.4 v4.

### V-CV-8 — Cross-project (mozun_chongsheng) face-differentiator non-collision

- **validator_id:** `V-CV-8`
- **Trigger:** Stage 6 work-unit kind `character_bible` (each bible write) AND `episode_full` (closing pass).
- **Check (executable):**
  1. For each `characters/{name}.md` in xianxia_new, extract bible row #11 `标志特征点` (face-differentiator). For 裴知秋: extract the shared `左眼下方 0.3cm 灰青胎记`.
  2. Read `ai_videos/mozun_chongsheng/characters/c*/c*_{name_part}.md`. Extract row #11 face-differentiator for each of the 10 mozun characters.
  3. Pairwise compare. A "collision" is defined as: same body part + same side (左/右) + same artifact-type token (痣 / 疤 / 胎记 / 耳钉 / 银环 / 玉佩 / 雀斑 / 暗纹 / 红痕).
  4. If exact collision → `blocker`.
  5. If near-collision (same body part + side, different artifact-type) → `warning` + ask user to disambiguate (e.g., move 裴知秋's mark to right cheek or change to a different artifact type).
- **Severity:** `blocker` on exact collision; `warning` on near-collision.
- **Known mozun_chongsheng face-differentiator inventory (pre-loaded from `ai_videos/mozun_chongsheng/characters/c*/c*.md` at this strategy compile time):**

  | mozun char | mark | location | side | type | color |
  |---|---|---|---|---|---|
  | c1_沧冥 | 朱砂痣 | 眼下 | 右 | 痣 | 朱红 |
  | c2_叶无尘 | 小银环 | 眉骨 | 左 | piercing | 银 |
  | c3_苏璃月 | 珍珠耳坠 | 耳 | 左 | jewelry | 雪白珍珠 |
  | c4_柳红袖 | 红点小痣 | 唇角 | 右 | 痣 | 朱红 |
  | c5_苓夭夭 | 淡褐雀斑 | 鼻尖 | (中) | 雀斑 | 淡褐 |
  | c6_白月清 | 淡红痕 | 眉心 | (中) | 痕 | 淡红 |
  | c7_赵焚天 | 古旧暗红疤 | 颊 | 左 | 疤 | 暗红 |
  | c8_方鼎元 | 黑长痣 | 下颌 | 左 | 痣 | 黑 |
  | c9_韩夺心 | 斜疤 | 眼角 | 右 | 疤 | 浅 |
  | c10_司空玄 | 十字暗纹 | 颈侧 | 左 | 刺青 | 暗 |

  **裴知秋's proposed mark per visual_style §3.3.2 / dossier R-3:** `左眼下方 0.3cm 灰青胎记`. Cross-checked against the table above:
  - 沧冥 holds 右眼下方 朱砂痣 — different side (左 vs 右), different type (胎记 vs 痣), different color (灰青 vs 朱红). **No collision.**
  - No other mozun character occupies 眼下 / 眼周 region on either side.
  - **Conclusion at strategy time:** V-CV-8 PASSES at this strategy compile time (灰青胎记 vs 朱砂痣, opposite eye side, different artifact-type token, different color family). The validator must still re-run at stage-6 work-unit time in case 裴知秋's mark string is paraphrased during bible authoring (e.g., a stage-6 author writing `左眼下泪痣` would re-trigger this check and could surface a near-collision with 沧冥 via the shared `痣` token).
- **Note on the 9 other xianxia_new characters:** the dossier does not pre-commit face-differentiators for 闻砚清 / 容漪 / 卫长烛 / 应砚之 / 戚归砚 / 池洇 / 阮惘 / 言息. Stage 6 must invent these per ai_video.md rule 12.1 row #11 — the validator runs V-CV-8 at each bible write and ALSO performs intra-project pairwise comparison (the 10 xianxia_new characters must not collide with EACH OTHER either, in addition to not colliding with the 10 mozun characters). Total comparison matrix at episode_full closure: 10 × (10 + 10 - 1) = 190 pairwise checks; tractable.

## 3. Drift-detection algorithm

Pseudocode for the byte-identical compare used by V-CV-4 / V-CV-5 / V-CV-6.

```python
def normalize_locked_string(raw: str) -> str:
    """
    Normalize an extracted 一句话锁定 / face-differentiator substring for byte-comparison.
    Goal: tolerate whitespace + line-wrap noise; reject any character-level edit.
    """
    import unicodedata
    s = unicodedata.normalize("NFC", raw)        # 1. NFC: canonical equivalence (e.g., 漢 vs 漢)
    s = s.replace(" ", " ").replace("　", " ")  # 2. fold non-breaking + fullwidth spaces to ASCII space
    s = " ".join(s.split())                       # 3. collapse runs of whitespace to single space
    s = s.strip()                                 # 4. strip leading / trailing whitespace
    return s


def extract_locked_string_from_bible(bible_md_text: str) -> str:
    """
    Extract row #10 一句话锁定 value from a character bible markdown table.
    For 裴知秋: returns a dict {"state_a": ..., "state_b": ...}.
    """
    # Strategy: locate "## 锁定描述符" heading, then find the row whose first cell contains "一句话锁定",
    # then take the value cell (last `|`-separated column on that row), strip leading/trailing `**` etc.
    ...

def extract_locked_string_from_seedream(seedream_md_text: str) -> str:
    """
    Extract the first-sentence locked string from a Seedream prompt body.
    Per rule 12.2 template: '## Prompt\n\n{name} · {epithet}。{一句话锁定}'.
    Returns the substring after the first '。' on the Prompt opening line, up to the next '。' or newline.
    """
    ...

def extract_locked_string_from_shot(shot_md_text: str, char_name: str) -> str | None:
    """
    Extract the 一句话锁定 portion of a 角色: line for a given character.
    Per rule 12.4-A: line format = '角色: {name1} — {locked_1} + {face_diff_1} · {name2} — {locked_2} + {face_diff_2} ...'
    Returns None if char_name absent from the line.
    """
    ...

def drift_check(extracted_strings: dict[str, str]) -> list[Issue]:
    """
    Given a dict {source_path: extracted_locked_string}, return blockers for any pairwise drift.
    """
    issues = []
    normalized = {k: normalize_locked_string(v) for k, v in extracted_strings.items()}
    canonical = None
    for path, norm in normalized.items():
        if canonical is None:
            canonical = norm
            continue
        if norm != canonical:
            issues.append(Issue(
                validator_id="V-CV-4 or V-CV-5",  # caller specifies
                severity="blocker",
                message=f"locked-string drift between sources",
                details={"canonical_source": list(normalized.keys())[0],
                         "drifted_source": path,
                         "canonical": canonical,
                         "drifted": norm},
            ))
    return issues
```

**Normalization rules (the contract):**

1. **Unicode NFC** — canonical equivalence handles edge cases where a CJK glyph is represented as a composed code point in the bible but as a decomposed sequence in a shot prompt (e.g., variation selectors injected by an IME). Per spec, all xianxia_new content is hand-authored in Chinese, but a stage-6 worker might paste from a different IME — NFC fixes the false-positive.
2. **Whitespace folding** — fullwidth space `　`, non-breaking space ` `, and consecutive ASCII spaces all collapse to a single ASCII space; this tolerates line-wrap differences and IME-inserted spacing without losing semantic content.
3. **Leading / trailing strip** — guards against table-cell padding inserted by markdown formatters.
4. **What is NOT normalized (intentional):** punctuation (`，。、` vs `,.,`), digit width (半角 `0.3` vs 全角 `０.３`), CJK quotation marks (`「」` vs `""`), and any reordering of substrings. These ARE drift — if a shot rewords `左眼下方 0.3cm 灰青胎记` to `左眼下方0.3公分灰青胎记`, the algorithm correctly flags a drift blocker.
5. **Locale-independent** — all extraction + comparison runs on UTF-8 byte streams; no `locale.strcoll`.

**Comparison ordering for V-CV-5:** the **bible row #10** is the canonical source. The Seedream prompt and every shot prompt are compared AGAINST the bible's normalized string. Drift in the bible itself is impossible by definition; drift in Seedream or any shot points the blocker at the non-bible file (so stage 6 patches the dependent file, not the source-of-truth).

## 4. Runtime mode trigger — work_unit_kind mapping

Stage 6 streaming validation (per CLAUDE.md § Event stream + stage-6 contract) runs this level on the following work-unit kinds:

| work_unit_kind | Validators triggered | Cadence |
|---|---|---|
| `character_bible` (one per character — 9 work units total) | V-CV-3, V-CV-6 (only when character == 裴知秋), V-CV-8 | runs IMMEDIATELY after each bible write — fast feedback so naming drift is caught at author time, not at episode_full closure |
| `seedream_prompt` (one per character × state — 10 work units: 8 single-state + 2 for 裴知秋) | V-CV-2 (existence), V-CV-5 (bible ↔ seedream byte-identical pair) | runs immediately after each立绘 prompt write |
| `shot_prompt` (one per shot — 7 work units for ep01) | V-CV-1 (existence of bible for every name in shot), V-CV-2 (existence of seedream for every name), V-CV-4 (cross-shot byte-identical — RE-RUNS on every new shot, scanning all prior shots in ep01), V-CV-5 (shot ↔ bible byte-identical), V-CV-6 (when 裴知秋 referenced), V-CV-7 (multi-character expansion rule) | runs immediately after each shot prompt write; V-CV-4 incrementally compares the new shot against all prior ep01 shots — this is the most frequent trigger |
| `episode_full` (ep01 closing pass — single work unit) | ALL validators V-CV-1 through V-CV-8 | runs once at end-of-episode; catches deferred regressions where a character was referenced before its bible was written |

**Idempotency contract.** Validators are pure functions of the on-disk artifact set; re-running them produces identical results unless files changed. Stage 6 may safely re-run the full level after any single file regen.

**Halt + bound.** Per CLAUDE.md § Iteration bounds: 3 revision rounds per work unit. If V-CV-4 keeps blocking on the same byte-diff across 3 consecutive rounds, the parent emits `pipeline.halted` + escalates to the user (per CLAUDE.md § Iteration bounds — drift fixes are bible-side patches, not shot-side rewrites; if a worker keeps hand-typing the shot's 角色 line rather than copy-pasting from the bible row #10, the human escalation message MUST suggest "stop re-typing; copy the bible's row #10 value byte-for-byte").

**Cross-level dependency.** This level depends on `ai_video_compliance` having confirmed schema presence first (per § 1). If `ai_video_compliance` is blocked on a missing schema field, this level emits `validation.skipped` with the upstream blocker id, NOT a redundant blocker.

## 5. Acceptance summary for this level

A work unit clears this level when:

- All triggered validators (per the work_unit_kind mapping above) return zero `blocker` issues.
- Outstanding `warning` issues are documented in the work unit's `validation.issue.raised` event with proposed rewrites, AND a human acknowledgement is recorded (per CLAUDE.md stage-6 contract for content tasks — V-CV-7 multi-character warnings on the 倒叙 montage shot are the expected case here).
- The closing `episode_full` pass emits one final `validation.pass` event referencing all 8 validators in its `validators_run` array.
