---
worker_id: level-specialist-07-internal_consistency
stage: 5
role: level-specialist
level: internal_consistency
status: complete
blockers: []
confidence: high
---

# Validation level — internal_consistency

## 1. Scope + boundary vs the other 6 levels

This level checks **project-specific narrative invariants** that no other validator catches. The 6 sibling levels at stage 5 (`ai_video_compliance`, `character_visual_consistency`, `copyright_clearance`, `storyteller_dialogue_master`, `hook_retention`, `genre_fidelity`) each cover a different concern surface; this one fills the seventh gap.

| Level | What it catches | Why it can NOT catch the internal-consistency invariants |
|---|---|---|
| `ai_video_compliance` | Schema lint — every shot has `时长/景别/运镜/光线/比例/负向/9:16` etc. per `ai_video.md` rule 12.4 | Cannot read **narrative meaning** of a beat (e.g., "did the level-up burn a tick?" is not a schema field) |
| `character_visual_consistency` | byte-identical re-paste of 一句话锁定 + 面部 across every shot referencing a character | Cannot see whether the character's **future-reveal etymology** is planted at ep01 — only whether their face is locked |
| `copyright_clearance` | Auto-grep of BLACKLIST + mozun cross-grep + naming collision check | Cannot read **in-fiction cadence alignment** — the names pass grep even when the cadence is broken |
| `storyteller_dialogue_master` | Per-line dialogue craft (subtext, voice, register, on-frame字幕 cadence per shot) | Operates inside a single shot's dialogue field; cannot see cross-episode invariants like the parasitic-cost ledger |
| `hook_retention` | First-3s hook present, cliffhanger present, paid-conversion node tagged | Tags the *existence* of the cadence beat; does NOT verify the beat's narrative content matches dossier R-6 |
| `genre_fidelity` | 8-stage ladder present, 三方 trifecta present, 修炼→突破 cadence | Treats the genre primitives as a checklist; cannot see whether the parasitic-cost is paired with the level-up |

**This level's exclusive job:** narrative-level contract checks that span ≥ 2 files (script ↔ arc_outline ↔ character bibles ↔ world.md ↔ style_guide ↔ publish ↔ README). Boundary: anything single-file falls to one of the 6 above; anything cross-file with narrative semantics falls here.

The 7 validators below are designed so they fire when the corresponding stage-6 work unit emits `exec.unit.completed` — see § 5 for the runtime hook ordering.

---

## 2. Validators V-IC-1 through V-IC-7

### V-IC-1 — Parasitic-cost ledger

**Trigger work_unit_kinds:** `episodes/ep01/script.md`, `episodes/ep01/shotlist.md`, `episodes/ep01/shots/shotNN.md`, `arc_outline.md`, `characters/裴知秋.md` (carries cumulative ledger), `world.md` § 寄生系统 lore.

**Check (executable):**

1. **ep01 ledger check.** In `episodes/ep01/script.md`, find every shot / beat whose narrative content includes a level-up event (the FR-8 0:30–1:15 beat: `焚寿罗盘浮现 + 系统弹窗「代价已计算 · 寿元 -1 / 修为 +1」`). For each level-up event:
   - **REQUIRED tokens** in the same beat (script body OR shot prompt 系统弹窗 字幕 block):
     - `寿元 -N` (N ≥ 1) OR `寿命 -N年` per visual_style §3.3.3 拍 1 token
     - OR `记忆 -1段` per dossier R-6 / FR-2 § 寄生系统 lore (memory cost variant)
   - **REQUIRED visual motif** per FR-10.4 / visual_style §3.3.3: the 5s 三拍 motif (`系统弹窗 1.5s` → `寄生 aura 2s` → `寿命流失 1.5s`).
   - Missing tick-burn token on a level-up beat → **blocker**.
   - Missing motif on a level-up beat → handled by V-IC-5 (the two validators must both pass).

2. **arc_outline.md cumulative ledger check.** Parse `arc_outline.md` 60 lines; for each line whose synopsis contains a level-up token (`升 1 阶` / `突破` / `修为 +1` / `境界跃迁` / explicit `寿元 -N` etc.), verify the line ALSO carries a cost token (tick burn or memory erase). Confirmed mandatory level-up beats per dossier R-6 / spec FR-4:
   - **ep01** — 1st level-up · 寿元 -1
   - **ep08** — 归砚镜 first activation (memory shard recovery — INVERSE event, no tick burn; flagged separately, not a ledger debit)
   - **ep10** — paid node 1 · 寿元 -? / 记忆 -1段 (失去关于母亲长相的记忆 — explicit per dossier R-6)
   - **ep17** — 前世名揭晓 (NOT a level-up; story beat; no ledger row)
   - **ep20** — 《偿岁真言》mirror 揭示 (NOT a level-up; lore reveal)
   - **ep28** — 容漪 reveal (NOT a level-up; relational reveal)
   - **ep30** — paid node 2 · 寄生系统起源部分揭示 (story beat, likely includes 1 level-up + cost)
   - **ep35** — 长烟幡 transfer (功法 transfer; carries its own cost — long-yan-fan 每展开一段 -1年 寿元 per character_anonymization §3.4)
   - **ep49** — 归砚镜 拼回完整记忆 (recovery, not debit)
   - **ep50** — paid node 3 · 主角=系统source 真相 (story beat)
   - **ep60** — 季终 · 言息 击败 · 容漪 记忆被吃光 (terminal cost; cumulative ledger must zero out / 焚寿罗盘 exhausted)

3. **Cumulative ledger coherence.** The cumulative 寿元 burned across the 60-ep cadence should resolve to the reference table in § 3 (24 ticks = 焚寿罗盘 exhausted as designed per character_anonymization §3.4 / dossier R-6).
   - Mismatch between arc_outline.md's implicit total and the § 3 reference total → **warning** (stage 4 may have refined the per-episode tick count; the user reviews).
   - Total > 24 → **blocker** (overdraws the 24-格刻度盘 — breaks the in-fiction 神器 contract).
   - Total < 12 → **warning** (under-utilizes the cost mechanic; the 60-ep series should burn at least half the dial to land the dramatic stakes).

**Severity:** `blocker` for missing tick-burn on a level-up beat, ledger overdraw beyond 24. `warning` for cumulative mismatch within bounds. Reason: V-IC-1 is the load-bearing differentiator per dossier CCI-2 — no parasitic cost = no project.

**Recovery:** If V-IC-1 fires `blocker`, work unit is paused; user prompted to confirm the level-up was intentional cost-free (which would itself be a story decision worth surfacing) or to insert the missing ledger token.

---

### V-IC-2 — Reveal cadence integrity

**Trigger work_unit_kinds:** `arc_outline.md`, `world.md` (the FR-2 § 寄生系统 lore section that pre-declares the full 5-stage reveal), `episodes/ep01/script.md` (must plant ep08/10/17/28 seeds).

**Check (executable):**

1. **Beat presence.** `arc_outline.md` MUST contain all 11 cadence beats from spec FR-4 / dossier R-6 (see § 4 reference table). For each of the 11 episodes (ep01, ep08, ep10, ep17, ep20, ep28, ep30, ep35, ep49, ep50, ep60):
   - The corresponding `### epNN` line MUST exist.
   - The line's synopsis MUST mention the cadence beat's key revelation token (per § 4 reference table, column 「key revelation token」). Tokens are matched as substrings or close paraphrase that preserves the key noun + verb.
   - Missing beat or misplaced beat (e.g., ep10 reveal lands at ep11) → **blocker**.

2. **Episode placement integrity.** No cadence beat may land at a different episode than the table assigns. The episodes are load-bearing because they align with paid-conversion nodes (CCI-5 — ep10/30/50/60 are 70/25/5%/season-end paid nodes); drift = paid-node revelation mismatch = monetization break.

3. **Cross-doc ratification.** `world.md` § 寄生系统 in-fiction lore (FR-2 §5) MUST pre-declare the 5-stage reveal targets (ep17 / ep30 / ep49 / ep50 / ep60) so the script writer in stage 6 can plant seeds correctly. If `world.md` § 5 is missing the 5-stage statement → **blocker** (stage 6 will write blind).

**Severity:** `blocker` on missing or misplaced cadence beat; `blocker` on world.md missing the 5-stage lore statement.

**Recovery:** Stage 4 spec already carries the 11-beat table verbatim (FR-4 table). Any stage-6 drift is a stage-6 error to correct, not a stage-4 redesign.

---

### V-IC-3 — Character etymology coherence

**Trigger work_unit_kinds:** `characters/{name}.md` (every of 9 bibles), `episodes/ep01/script.md`, `episodes/ep01/shots/shot01.md`–`shot07.md`, `arc_outline.md`.

**Check (executable):**

1. **「词源」line present.** Per FR-5.2, every character bible's last line is a single 「词源」row. For each of the 9 bibles, grep for `^\s*词源[:：]` or section heading `## 词源` — must match the etymology in `findings/angle-character_anonymization.md` §3 verbatim (or surgical paraphrase preserving the core glyph attribution + future-reveal hook). Missing 「词源」 row → **blocker** (V-IC-3 cannot run on a bible without it).

2. **裴知秋 / 裴长砚 reveal plant (ep01 → ep17).** ep17 cadence beat is "前世名「裴长砚」揭晓"; ep01 final-15s scene per FR-8 is "自取新名「裴知秋」(水边题字)". The ep01 self-naming MUST be visually structured so the ep17 reveal is retroactively legible:
   - `episodes/ep01/script.md` 1:15–1:45 beat must include the self-naming action with the explicit framing "自取新名" or "重新命名" (not "我叫" — that would imply original name, breaking ep17).
   - At least one ep01 shot prompt must include the gesture of WRITING the new name (per FR-8 "水边题字") so the act of self-renaming is on-frame.
   - `characters/裴知秋.md` AND `characters/裴长砚.md` both exist as separate files (per FR-5) with explicit cross-reference noting 裴长砚 is the archived 前世 alias.
   - Etymology incoherence between the two files (e.g., 裴长砚 bible's 词源 fails to mention it's the 前世 name) → **warning**.

3. **容漪 ep01 cameo plant (ep01 → ep28).** ep28 cadence beat is "容漪 = 忘川教 planted memory backup". ep01 must include 容漪 in the 0:03–0:30 montage or as a 旁观者 in one shot per FR-5 (容漪 row: "主女主 — ep01 cameo only ... 作为旁观者出现于某 montage 帧, ≤1 shot"):
   - At least one ep01 shot prompt includes 容漪 in `角色:` line.
   - The shot's 动作 OR 镜头 framing positions her as observing-from-distance (not interacting) — so the ep28 reveal that she's been planted retroactively makes sense.
   - 容漪's 词源 line in `characters/容漪.md` MUST mention the ep28 reveal target (per character_anonymization §3.1).
   - Missing ep01 cameo entirely → **warning** (stage 6 may have deferred for tighter ep01 pacing; ep05 full debut still covers it but loses the retro-plant payoff).

4. **闻砚清 ep01 cliffhanger plant (ep01 → ep17).** ep17 beat = 师父真相 (per FR-2 §5 — 焚寿罗盘 relic from 师父 闻砚清). ep01 final-15s per FR-8 = 师父剪影 + 正脸闪一帧. Must verify:
   - `episodes/ep01/script.md` 1:45–2:00 beat includes 师父剪影 (silhouette) + the 1-frame 正脸 reveal.
   - `episodes/ep01/shots/shot07.md` (or whichever is the cliffhanger shot per FR-9) carries the silhouette + flash-frame contract in its 动作 timing.
   - `characters/闻砚清.md` 词源 line MUST mention his ep01 cliffhanger appearance + ep17 真相 reveal.
   - Missing flash-frame in cliffhanger shot → **blocker** (the ep17 reveal needs ep01 visual prefunding).

5. **6 betrayers visible in ep01 0:03–0:30 montage.** Per character_anonymization §3.2 + spec FR-8: the 5 betrayers + 言息 (6 total: 卫长烛 / 应砚之 / 戚归砚 / 池洇 / 阮惘 / 言息) must each be visibly identifiable in the ep01 倒叙 quick-cut montage (each pair ≤ 2.5s, face + defining gesture). Validator checks:
   - `episodes/ep01/script.md` 0:03–0:30 beat lists all 6 names in 角色出场.
   - For each name, the script body OR the corresponding shot prompt(s) include the character's `一句话锁定` byte-identical re-paste (per FR-10.1).
   - For each name, the script lists the defining gesture (e.g., 卫长烛 递剑 → 剑回主角心口; 应砚之 联名上奏 → 改成弹劾; etc. per character_anonymization §3.2 + dossier R-4).
   - Missing any of the 6 from ep01 montage → **blocker** (each is referenced by name in ep08/10/17/20/28/35/49/50/60 outline beats — their ep01 visual plant is required for the over-arc payoffs to land).

6. **5 signature 神器/功法 plant.** Per character_anonymization §3.4: 《残忆经》/ 焚寿罗盘 / 《偿岁真言》/ 归砚镜 / 长烟幡 each carry a 5-stage reveal arc. ep01 plants them as follows:
   - **焚寿罗盘** — ep01 visible in 0:30–1:30 beat (FR-8) → MUST appear in `world.md` § 5 + at least one ep01 shot prompt's `道具:` line.
   - **《残忆经》** — main protagonist 功法; ep01 may not visually show the book itself, but at least mentioned by name in `world.md` § 5 / `characters/裴知秋.md`.
   - **归砚镜** — 师父遗物; ep17 reveal that 闻砚清 is the source; ep01 plant via 师父剪影 (V-IC-3.4). MAY or MAY NOT be visible at ep01 — `characters/闻砚清.md` 词源 must state when it surfaces (ep08 first activation per dossier R-6).
   - **《偿岁真言》** — 魔门 mirror; ep20 reveal; no ep01 plant required, but `world.md` § 5 must pre-declare existence.
   - **长烟幡** — ep35 transfer; no ep01 plant required, but `world.md` § 5 + `characters/容漪.md` etymology must pre-declare.
   - Missing any of the 5 from `world.md` § 5 → **blocker**.

**Severity:** `blocker` on missing 词源 row, missing 6-betrayer ep01 plants, missing cliffhanger flash-frame, missing 5-神器/功法 from world.md §5. `warning` on softer etymology / cameo gaps (stage 4 may have refined; user reviews).

---

### V-IC-4 — Faction-system coherence

**Trigger work_unit_kinds:** `world.md`, `characters/{name}.md` (each betrayer + each protagonist + 师父 + 主女主), `copyright_clearance.md` (PROPOSED naming table sanity).

**Check (executable):**

1. **Declared factions.** `world.md` § 三方势力格局 (FR-2 §3) MUST declare:
   - **正派联盟** — 赤霞门 · 九寰阁 · 澹台宗
   - **散修盟** — 流烛盟
   - **魔门** — 忘川教
   - Missing any declaration → **blocker**.
   - Adding a 4th 正派 (栖梧阁 per character_anonymization §4.2 — stage-4 may have added) is acceptable, recorded as divergence.

2. **Betrayer faction assignment.** Per character_anonymization §3.2 + spec FR-5 character table, the 6 betrayers MUST be assigned as:

   | 角色 | Faction in `characters/{name}.md` | Faction declared in `world.md` |
   |---|---|---|
   | 卫长烛 | 正派 / 赤霞门 (掌门) | 赤霞门 |
   | 应砚之 | 朝堂太师之嫡子 | **NOT a sect** — `world.md` does not declare 朝堂 as a faction. Flag for cross-check (see #4 below). |
   | 戚归砚 | 散修 / 流烛盟 元老 (暗投忘川教) | 流烛盟 + 忘川教 (dual-affiliation must be explicit) |
   | 池洇 | 散修 / 流烛盟 杀手长老 | 流烛盟 |
   | 阮惘 | 魔门 / 忘川教 三长老 | 忘川教 |
   | 言息 | 魔门 / 忘川教 教主 (final boss) | 忘川教 |

   - Validator compares each bible's faction field against `world.md` declarations.
   - Mismatch (e.g., a bible assigns a betrayer to a faction the `world.md` doesn't declare) → **blocker**.
   - 戚归砚's dual-affiliation MUST be explicit in both his bible AND `world.md` (under 流烛盟's 内部政治 OR 忘川教's 暗投 paragraph) → missing dual-affiliation declaration → **warning**.

3. **3-faction distribution coverage (CCI-5).** Per dossier CCI-5 + spec R-6: the betrayers MUST span all 3 factions (正派 + 散修 + 魔门). Validator counts:
   - 正派 betrayers — expected ≥ 1 (卫长烛).
   - 散修 betrayers — expected ≥ 1 (池洇 OR 戚归砚).
   - 魔门 betrayers — expected ≥ 1 (阮惘 OR 言息).
   - Missing a faction's representative → **blocker** (the revenge-arc design requires all 3 fronts).

4. **应砚之 — 朝堂 carve-out.** 应砚之 is assigned to 朝堂 (the imperial court), which `world.md` does NOT declare as a sect. Stage 4 spec leaves this as an out-of-sect betrayer — that's intentional per character_anonymization §3.2 (his betrayal is political, not sectarian). Validator checks:
   - `world.md` § 三方势力格局 OR § 地理与时代背景 MUST mention 朝堂 / 太师府 as a non-sect political entity (parallel to the 3 factions, not a member of one).
   - Missing 朝堂 mention → **warning** (应砚之's role is unanchored without it; stage 6 can still ship but the cross-doc semantic is weaker).

5. **Sect visual signature uniqueness (cross-check with style_guide.md §3.3.1).** Each faction's 主/辅/点缀 palette MUST be distinct enough for viewers to read at a glance:
   - 正派 — 银白 + 浅青 + 浅金 (`#f5f5f0 / #a8c8c0 / #e8d098`)
   - 散修 — 土褐 + 草绿 + 麻白 (`#8c6a4a / #7a8a5a / #d8c8a8`)
   - 魔门 — 漆黑 + 深紫 + 骨白 (`#0a0a0a / #2a0a3a / #e8d8c0`)
   - Validator confirms `style_guide.md` declares these 3 distinct palettes + cross-checks `characters/{name}.md` 服饰 hex matches the faction palette (e.g., 卫长烛 — 赤霞门 palette family; 阮惘 — 忘川教 palette family).
   - Mismatch (e.g., 卫长烛's 服饰 in 紫黑骨白) → **blocker** (visual ↔ narrative faction misalignment misleads the viewer).

**Severity:** `blocker` on missing faction declaration, missing dual-affiliation for 戚归砚 IF arc_outline.md references his betrayal arc explicitly, missing 3-faction distribution, faction ↔ palette mismatch. `warning` on softer cross-doc gaps.

---

### V-IC-5 — 寄生升级 motif visual signature

**Trigger work_unit_kinds:** `episodes/ep01/script.md`, `episodes/ep01/shotlist.md`, `episodes/ep01/shots/shotNN.md`, `arc_outline.md` (for future-episode motif obligations), `style_guide.md` § 3.3.3 (the spec source for the motif).

**Check (executable):**

1. **Motif structural presence.** For every level-up event in ep01 (per V-IC-1 enumeration: exactly 1 level-up at 0:30–1:30 per FR-8), the corresponding shot prompt MUST embed the 5s 三拍 motif per visual_style §3.3.3:
   - 拍 1 (0–1.5s) — `系统弹窗 + 寿命红计数器跳动`: REQUIRED tokens `系统弹窗` or `叮——任务完成 / 修为 +1 阶` or `寿命 -N年`.
   - 拍 2 (1.5–3.5s) — `寄生 aura 顿挫`: REQUIRED tokens `寄生 aura` or `黑紫细丝` or `寄生紫 #4a1a5a` or `双瞳由暗褐→寄生紫一闪`.
   - 拍 3 (3.5–5s) — `寿命流失`: REQUIRED tokens (≥ 1 of) `嘴角血` / `鬓边骤白` / `青脉浮` / `代价已扣除`.
   - Missing any 拍 → **blocker** (V-IC-5 is the operational expression of CCI-2 — the differentiator must be visually executed, not just narratively named).

2. **`节奏: 顿挫` field.** Per style_guide.md §3.3.3 + §3.1.3, the motif's `节奏:` line in the shot prompt MUST equal `顿挫` (one of the 4 declared 速度 词典 entries). Mismatch (`标准` / `慢镜` / `快剪`) → **blocker** (the 5s 三拍 stops working without the prescribed pacing).

3. **Motif visual reference to style_guide.** The shot prompt's `光线 / 色调:` line MUST reference one of: `寄生 aura`, `寿命流失`, or both (declared in style_guide.md §3.2 12-state lighting). Re-pasted byte-identical from the style guide.
   - Missing the lighting state reference → **warning** (the motif may still work if 拍 1/2/3 tokens fire, but Seedance/Kling may render the wrong palette without the lighting state pin).

4. **NFR-9 satisfaction.** Per spec NFR-9 (motif ≥ 1 in ep01), at least one ep01 shot prompt MUST satisfy #1, #2, #3 together. Failure → **blocker** (NFR-9 mapped to blocker per spec § Non-functional requirements).

5. **Future-episode motif obligations.** Per arc_outline.md cadence beats — every ep that contains a level-up event (per V-IC-1 enumeration: ep10, ep30, ep35 + others per the § 3 reference table) MUST be flagged in arc_outline.md's synopsis with a 「motif」or「寄生升级」token so stage 6 (when that episode is written) knows to embed the motif. Missing flag → **warning** (does not block this run because ep02-60 are out-of-scope MVP, but the flag is forward-funding).

**Severity:** `blocker` on missing 拍 / wrong 节奏 / NFR-9 unsatisfied. `warning` on missing lighting state reference / missing future-ep motif flag.

---

### V-IC-6 — Cross-document slug + title consistency

**Trigger work_unit_kinds:** `README.md` (both `my_novel/{slug}/README.md` AND `ai_videos/{slug}/README.md`), every file with a slug-aware path, `episodes/ep01/publish.md`, `copyright_clearance.md` SIGN-OFF section, the folder name itself.

**Check (executable):**

1. **Slug consistency.** Final slug per spec Open Question #1 = `feng_shou_lu` (or whatever the user picks at stage-4 approval). Validator:
   - Folder name = `my_novel/{slug}/` AND `ai_videos/{slug}/` — drift between the two = **blocker**.
   - All cross-document references to the slug (e.g., shot prompts naming the project, copyright_clearance.md PROPOSED naming table) use the same slug — drift = **blocker**.
   - The spec at `specs/ai_video/{slug or working slug}/final_specs/spec.md` records the slug it expects; cross-check against actual file paths.

2. **Title consistency.** Title `《焚寿录》` (or final pick) MUST appear:
   - As `README.md` H1: `# 《焚寿录》— AI 视频项目` (per FR-1).
   - In `ai_videos/{slug}/README.md` H1 (same).
   - In `episodes/ep01/publish.md` 标题 field (one of the title shapes — verbatim title, "焚寿录 · 第一集 · {hook}", or shape declared in publish.md per FR-11).
   - Drift between any of the 3 locations → **blocker**.

3. **slug ↔ title etymology.** The slug `feng_shou_lu` pinyin must be the romanization of the title `《焚寿录》` exactly (per ai_video.md rule 1: 「task_name is pinyin or English, never Chinese」). Mismatch (e.g., title 《焚寿录》 with slug `xianxia_new` after stage-4 approval) → **blocker** (= stage-4 didn't actually rename the folder).

4. **Working slug `xianxia_new` cleanup.** After stage-4 approval, no file body should still reference `xianxia_new` as the canonical slug except:
   - Audit logs under `.audit/` (historical, immutable).
   - The spec's reference to its working slug history (one informational line is fine).
   - Validator flags any other `xianxia_new` reference → **warning** (could be a leftover stage-3 string; user reviews).

**Severity:** `blocker` on slug/title drift across canonical files; `warning` on `xianxia_new` leftovers.

---

### V-IC-7 — 60-ep over-arc ↔ ep01 plant consistency

**Trigger work_unit_kinds:** `arc_outline.md`, `episodes/ep01/script.md`, every `characters/{name}.md`, `world.md`.

**Check (executable):**

1. **Forward-plant verification.** For every ep02–60 outline line in `arc_outline.md` that references a person / thing / location, verify:
   - **Person:** the named character has a `characters/{name}.md` file OR is explicitly marked in arc_outline.md as 「post-ep01 debut」 (per spec § Out of scope #2 — 灵兽乌泽 ep05 debut etc.).
   - **Thing:** the artifact (神器 / 功法) is declared in `world.md` § 5 寄生系统 lore OR `characters/{name}.md`.
   - **Location:** the place is declared in `world.md` § 地理与时代背景 (落雁渊 / 栖梧崖 / 澹江洲) OR allowed as an inline-only backdrop per ai_video.md rule 12.3.
   - A future outline beat referencing an entity that's NOT in any spec FR / character file / scene file → **blocker** (dangling reference).

2. **Backward-plant verification.** For every named character in ep01's 0:03–0:30 montage (per V-IC-3.5) AND in the 1:45 cliffhanger (闻砚清 per V-IC-3.4), verify:
   - The character is referenced by name in at least one ep02–60 outline beat in `arc_outline.md` (otherwise they're an ep01-only character with no payoff — flag as **warning**).
   - The character bible's 词源 line names a future-episode reveal target (per FR-5.2 + character_anonymization §3).

3. **Visual specificity for over-arc payoffs.** Per the prompt rubric — "if ep10 outline says 卫长烛 face-slap, ep01 must have planted 卫长烛's face in the 倒叙 montage with sufficient visual specificity that a viewer can recognize him at ep10". Validator checks:
   - For each of the 5 betrayers + 言息: `episodes/ep01/script.md` 0:03–0:30 montage OR the corresponding shot prompt must include the character's `一句话锁定` (per FR-10.1) byte-identical re-paste from `characters/{name}.md`.
   - Each betrayer's `面部` field (one of the 10 锁定描述符 per ai_video.md rule 12.1) MUST be visible in at least 1 ep01 shot (verifiable via the shot prompt's 角色 line + 镜头 景别 — close shots required for face-readable plant).
   - Missing face-readable plant on any betrayer referenced in arc_outline.md ep02–60 → **blocker** (the over-arc face-slap / face-reveal payoff fails without it).

4. **Planted entity that never appears in ep01 yet is referenced in ep02–10 outline.** Per the prompt rubric: this is a **warning** (stage 4 might intentionally defer the visual plant — e.g., 灵兽乌泽 doesn't need ep01 plant if ep05 is his debut).

5. **Cross-doc consistency on parasitic-system source.** `world.md` § 5 declares the 5-stage reveal (ep17 = relic from 闻砚清 → ep30 = fragment of 偿岁真言 contract → ep49/50 = protagonist created it → ep60 = final cost). Validator:
   - Every ep17 / ep30 / ep49 / ep50 / ep60 outline line MUST reference the SAME 5-stage reveal sequence (no contradictions like "ep17 reveal: 闻砚清 is alive" — the actual ep17 reveal is the 前世名 + 师父 relic origin).
   - Drift → **blocker**.

**Severity:** `blocker` on dangling references, missing face-readable plant on a referenced betrayer, world.md ↔ arc_outline.md 5-stage reveal drift. `warning` on backward-plant gaps, intentionally-deferred plants.

---

## 3. Parasitic ledger reference table

The cumulative tick-burn schedule across the 60-ep cadence. Each row = one level-up event. **24 rows total** (matching the 24-格刻度盘 declared in character_anonymization §3.4 / world.md FR-2 §5). This table is the canonical reference V-IC-1 checks against; stage 6 may refine specific tick counts (e.g., split 寿元 -2 into 寿元 -1 + 记忆 -1段) but the cumulative total at ep60 MUST equal 24 ticks (with memory-erase counted as fractional ticks per the table's convention).

| # | Episode | Level-up trigger | Stage gained | Tick cost (寿元 -N) | Memory cost (记忆 -1段) | Cumulative ticks burned | Notes |
|---|---|---|---|---|---|---|---|
| 1 | ep01 | 系统觉醒 — 7岁练气体 born from 落雁渊 awakening | 0 → 练气 1 阶 | -1年 | — | 1 / 24 | FR-8 0:30–1:15; visual_style §3.3.3 motif required |
| 2 | ep03 | 练气 1→2 | 练气 2 阶 | -1年 | — | 2 / 24 | arc_outline placeholder; stage-6 ep03 work refines |
| 3 | ep05 | 练气 2→3 + 灵兽乌泽 contract | 练气 3 阶 | -1年 | — | 3 / 24 | 乌泽 ep05 debut; he absorbs subsequent partial ticks on主角's behalf |
| 4 | ep07 | 练气 3→4 | 练气 4 阶 | -1年 | — | 4 / 24 | — |
| 5 | ep08 | 归砚镜 first activation (NOT a level-up) | — | — | — | 4 / 24 | INVERSE event — surfaces a previously-lost memory; ledger UNCHANGED |
| 6 | ep10 | **paid node 1** — 练气 4→5 + 卫长烛 face-slap setup | 练气 5 阶 | -2年 | 母亲长相 (记忆 -1段) | 6 / 24 (+ 1 mem) | dossier R-6: "不可承受寿命代价 + 失去关于母亲长相的记忆"; first dual-cost |
| 7 | ep13 | 练气 5→6 | 练气 6 阶 | -1年 | — | 7 / 24 (+ 1 mem) | — |
| 8 | ep15 | 筑基突破 (练气 → 筑基 1) | 筑基 1 阶 | -1年 | — | 8 / 24 (+ 1 mem) | Major境界 breakthrough; tick cost normalizes back to 1 because 焚寿罗盘 自适应 |
| 9 | ep17 | **前世名揭晓** (NOT a level-up) | — | — | — | 8 / 24 (+ 1 mem) | Story beat; ledger UNCHANGED |
| 10 | ep18 | 筑基 1→2 (post-reveal first 升阶) | 筑基 2 阶 | -2年 | — | 10 / 24 (+ 1 mem) | Cost spikes — 前世名揭晓后罗盘"识破"主角真身, raises rate |
| 11 | ep20 | 偿岁真言 mirror 揭示 (NOT a level-up) | — | — | — | 10 / 24 (+ 1 mem) | Lore reveal; ledger UNCHANGED |
| 12 | ep22 | 筑基 2→3 | 筑基 3 阶 | -1年 | — | 11 / 24 (+ 1 mem) | — |
| 13 | ep25 | 筑基 3→4 | 筑基 4 阶 | -1年 | 师父早期教诲 (记忆 -1段) | 12 / 24 (+ 2 mem) | Foreshadows ep28 reveal |
| 14 | ep28 | 容漪 = 忘川教 planted (NOT a level-up) | — | — | — | 12 / 24 (+ 2 mem) | Relational reveal; ledger UNCHANGED |
| 15 | ep30 | **paid node 2** — 金丹突破 + 寄生系统起源部分揭示 | 金丹 1 阶 | -3年 | — | 15 / 24 (+ 2 mem) | First triple-cost; tied to paid conversion node |
| 16 | ep33 | 金丹 1→2 | 金丹 2 阶 | -1年 | — | 16 / 24 (+ 2 mem) | — |
| 17 | ep35 | 长烟幡 transfer + 容漪 共苦盟约 | 金丹 3 阶 | -1年 (主角) -1年 (容漪 via 长烟幡) | — | 17 / 24 (+ 2 mem) | First shared cost; long-yan-fan adds 容漪 to the ledger (informal — main ledger only tracks主角) |
| 18 | ep38 | 金丹 3→4 | 金丹 4 阶 | -1年 | 与容漪 first 相遇 (记忆 -1段) | 18 / 24 (+ 3 mem) | Foreshadows ep49 reveal |
| 19 | ep41 | 元婴突破 | 元婴 1 阶 | -2年 | — | 20 / 24 (+ 3 mem) | Major境界 breakthrough |
| 20 | ep45 | 元婴 1→2 | 元婴 2 阶 | -1年 | — | 21 / 24 (+ 3 mem) | — |
| 21 | ep49 | 归砚镜 拼回完整记忆 (NOT a level-up, but memory RESTORE event) | — | — | +3段 restored (offsets ep10/25/38 losses) | 21 / 24 (mem reset to 0) | INVERSE event; restores memory but ticks stay burned |
| 22 | ep50 | **paid node 3** — 化神突破 + 主角=系统source 揭晓 | 化神 1 阶 | -2年 | — | 23 / 24 | Penultimate breakthrough |
| 23 | ep55 | 化神 1→2 (post-reveal cost penalty) | 化神 2 阶 | -1年 (penalty + 0.5 unspecified) | — | 24 / 24 — DIAL EXHAUSTED | 24th tick burns; 焚寿罗盘 displays 0 remaining |
| 24 | ep60 | **季终 · 言息 击败 · 容漪 记忆被吃光** | 化神 → 炼虚 attempt; rolled back | -∞ (final cost) | 容漪 与主角 共同记忆 全段 | 24 / 24 — DIAL CRACKS, "续季钩" carries over | Penultimate cost lands ON 容漪 (per dossier R-6: 容漪 与主角 共同记忆 → 陌生人); season hook = 偿岁真言 残片寄居 容漪 |

**Cumulative ledger total at ep60 = 24 ticks burned (dial fully exhausted) + 4 memory segments lost (3 restored at ep49 leaves net 1 + ep60 final 容漪 段 = 2 outstanding).** Stage 4 may refine specific per-episode tick counts (e.g., re-balance ep10 vs ep30); the cumulative MUST equal 24 at ep60 for the 神器 contract to land.

Notes for stage-6 lookup:
- "Level-up" rows (1, 2, 3, 4, 6, 7, 8, 10, 12, 13, 15, 16, 17, 18, 19, 20, 22, 23) = 18 rows = 18 actual 升阶 events.
- "Story / reveal / inverse" rows (5, 9, 11, 14, 21, 24) = 6 rows — ledger UNCHANGED on 4 of these (5, 9, 11, 14), RESTORE on 1 (21), TERMINAL on 1 (24).
- 24 ticks = 18 level-ups × 1 base + extra ticks at breakthroughs (ep10 +1, ep15 +0, ep18 +1, ep30 +2, ep41 +1, ep50 +1, ep55 +0.5, ep60 ∞) ≈ 24 budgeted ticks.
- Memory ledger (separate from tick ledger but tracked in same `characters/裴知秋.md` 累计 ledger field): 4 lost + 3 restored at ep49 + 容漪 final at ep60 = net deeply diminished but specific items recoverable in season 2.

---

## 4. Reveal cadence reference table (dossier R-6 / spec FR-4)

11-beat cadence for stage-6 lookup. V-IC-2 checks `arc_outline.md` against this table verbatim (close paraphrase preserving the key revelation token allowed).

| # | Episode | Paid node | Key revelation token | Source artifact (where stage-6 plants) |
|---|---|---|---|---|
| 1 | ep01 | — | 死亡开局 + 重生 + 系统觉醒 + 自取新名「裴知秋」+ 师父剪影 cliffhanger | `episodes/ep01/script.md` + cliffhanger shot prompt |
| 2 | ep08 | — | 归砚镜 首次激活 — ep01 背叛画面 unfiltered 回放 (确认非偏执) | `arc_outline.md` ep08 line; 归砚镜 declared in `world.md` §5 |
| 3 | ep10 | **付费节点 1 (70%)** | 卫长烛 face-slap + 第一次「不可承受寿命代价」(失去关于母亲长相的记忆) + 神秘人 cliffhanger | `arc_outline.md` ep10 line; betrayer face plant at ep01 (V-IC-3.5 + V-IC-7.3) |
| 4 | ep17 | — | 前世名「裴长砚」揭晓 — 前世/本世 timeline 缝合 + 师父 闻砚清 真相起点 | `arc_outline.md` ep17 line; `characters/裴长砚.md` + `characters/闻砚清.md` |
| 5 | ep20 | — | 《偿岁真言》 vs 《残忆经》 镜像揭示 — 魔门功法 = 主角功法的源头 | `arc_outline.md` ep20 line; `world.md` §5 pre-declared |
| 6 | ep28 | — | 容漪 = 忘川教 planted memory backup — 信任反转 | `arc_outline.md` ep28 line; `characters/容漪.md` ep01 cameo plant (V-IC-3.3) |
| 7 | ep30 | **付费节点 2 (25%)** | 寄生系统起源部分揭示 — 主角前世 = 系统设计者 (但为何目的尚未明) | `arc_outline.md` ep30 line; `world.md` §5 pre-declared 5-stage |
| 8 | ep35 | — | 长烟幡 transfer (容漪 → 裴知秋) — 共苦盟约 | `arc_outline.md` ep35 line; `characters/容漪.md` + `characters/裴知秋.md` |
| 9 | ep49 | — | 归砚镜 拼回完整记忆 — 主角发现 system 设计是为困住忘川教，反噬自己 | `arc_outline.md` ep49 line |
| 10 | ep50 | **付费节点 3 (5%)** | 主角 = 系统 source 真相揭晓 | `arc_outline.md` ep50 line |
| 11 | ep60 | **季终** | 言息 击败 · 容漪 记忆被吃光 · 续季钩 (《偿岁真言》残片寄居 容漪) | `arc_outline.md` ep60 line + 续季钩 declaration |

---

## 5. Runtime hook (stage 6 ordering)

When stage 6 produces `episodes/ep01/script.md` OR `arc_outline.md` OR any `characters/{name}.md` OR `world.md`, the validator dispatch order is:

1. **`internal_consistency` (this level) runs FIRST** — before `character_visual_consistency`. Reason: internal_consistency catches narrative breaks (missing 词源, missing cadence beat, missing parasitic ledger entry) that would otherwise propagate as descriptor drift downstream. If the cadence is broken at ep10 but `character_visual_consistency` runs first, it byte-checks every shot's character descriptor and passes — meanwhile the ep10 face-slap callback is mute because the ep01 plant is missing. By running IC first, we fail-fast on narrative contracts before checking visual fidelity to those (now-known-broken) contracts.

2. **`ai_video_compliance`** — schema-level lint runs second.

3. **`character_visual_consistency`** — byte-identical descriptor re-paste runs third.

4. **`copyright_clearance`** — BLACKLIST + mozun cross-grep runs fourth.

5. **`storyteller_dialogue_master`** — per-line dialogue craft runs fifth.

6. **`hook_retention`** + **`genre_fidelity`** — runs in parallel sixth (they don't share contracts).

7. **`validation.requires_manual_walkthrough`** event emitted last per `agent_refs/validation/general.md` principle 4.

The audit ordering for each work unit:

```
exec.unit.started (work_unit = episodes/ep01/script.md)
  → validation.started (level = internal_consistency, validators = V-IC-1..V-IC-7)
    → validation.issue.raised (if any blocker fires) → exec.revision.applied (max 3 rounds per general.md) → re-run IC
    → validation.pass (level = internal_consistency)
  → validation.started (level = ai_video_compliance) ...
  ...
  → validation.requires_manual_walkthrough
exec.unit.completed
```

---

## 6. Worker self-report

- **Validators total:** 7 (V-IC-1 through V-IC-7).
- **Blocker-severity validators:** 6 (V-IC-1, V-IC-2, V-IC-3, V-IC-4, V-IC-5, V-IC-7). V-IC-6 carries blockers on slug/title drift; warnings on `xianxia_new` leftovers — counted as blocker-severity overall because the primary slug/title check is a blocker.
- **Warning-severity validators:** 0 are warning-only; all 7 carry at least one blocker condition. The breakdown of blocker vs warning conditions is in each validator's Severity line.
- **Highest-leverage validator:** **V-IC-1 (parasitic-cost ledger)** — per dossier CCI-2, the parasitic system is the project's load-bearing differentiator. If V-IC-1 fails, the project's central conceit is mute on screen; every other validator passing would still leave the project indistinguishable from generic 重生 短剧.
- **Under-spec'd dependencies surfaced for stage-4 follow-up:**
  - **应砚之 朝堂 affiliation** (V-IC-4.4) — `world.md` § 三方势力格局 doesn't currently declare 朝堂 / 太师府 as a non-sect political entity. Stage-4 should add a one-paragraph 朝堂 declaration to `world.md` so V-IC-4.4 doesn't fire on a real semantic gap.
  - **戚归砚 dual-affiliation declaration** (V-IC-4.2) — needs to be explicitly written into both `world.md` (under 流烛盟 or 忘川教 paragraph) AND `characters/戚归砚.md`. Stage-4 should pre-script this.
  - **Cumulative ledger arithmetic** (V-IC-1 § 3 reference table) — the 24-tick total is plausible but the per-episode tick counts in § 3 are stage-5 reference-table estimates. Stage 6 may refine; the cumulative MUST end at 24 ticks at ep60 for the 神器 contract to land, and that constraint should be re-stated in `characters/裴知秋.md` 累计 ledger field as a hard target.

## 7. Pre-reading consulted

- `specs/ai_video/xianxia_new/final_specs/spec.md`
- `specs/ai_video/xianxia_new/findings/dossier.md`
- `specs/ai_video/xianxia_new/findings/angle-character_anonymization.md`
- `specs/ai_video/xianxia_new/findings/angle-visual_style.md`
- `.claude/agent_refs/validation/general.md`
- `.claude/skills/agent_team/playbooks/validation.md` (parent-direct; this worker reads playbook via parent's pre-reading)
- `.claude/agent_refs/project/ai_video.md` (rule 1, 12.1, 12.2, 12.3, 12.4)
