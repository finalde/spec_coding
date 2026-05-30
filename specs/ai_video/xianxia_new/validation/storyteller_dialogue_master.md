---
worker_id: level-specialist-06-storyteller_dialogue_master
stage: 5
role: level-specialist
level: storyteller_dialogue_master
status: complete
blockers: []
confidence: high
---

# Storyteller-Dialogue Master — qualitative review spec (xianxia_new / ep01)

This level operationalizes `agent_refs/project/ai_video.md` §12.4-D + `agent_refs/validation/ai_video.md` move 9 for the《焚寿录》 ep01 work unit. It is the ONLY stage-5 level that grades **content quality** (not contract conformance) — every other level (language compliance, 15s atomicity, character-visual-consistency, dual-prompt presence, aspect ratio, publish-metadata, copyright clearance, internal consistency, hook/retention) checks structure or ledger. The master reads the `台词 / 字幕:` block + the surrounding shot design (镜头 / 动作 / 整体) and emits **patches**, not prose.

---

## 1. Scope + boundaries

**This level reviews:**

- Every `my_novel/feng_shou_lu/episodes/ep01/shots/shotNN.md` `台词 / 字幕:` block + `动作:` timed beats + `镜头:` + the shot's stated hook (per shotlist `cover_frame` / hook marker).
- `my_novel/feng_shou_lu/episodes/ep01/script.md` dialogue lines (the upstream source the shot prompts derive from).
- `my_novel/feng_shou_lu/episodes/ep01/shotlist.md` — for hook / cliffhanger flags that gate S1 检查.

**Boundaries (NOT this level):**

| Concern | Owned by |
|---|---|
| Character descriptor byte-identity across shots | `internal_consistency` level (NFR-2) |
| 时长 ≤ 15s + 动作 beats sum to 时长 | `acceptance_criteria` level (NFR-5) |
| 9:16 / 比例 / 字幕规范 / 负向 re-paste | `acceptance_criteria` level (NFR-3, FR-10.5/6) |
| Word count caps (≤ 2000/2500) | `acceptance_criteria` level (NFR-1) |
| BLACKLIST + mozun cross-grep | `copyright_clearance` level (NFR-4) |
| 寄生 motif present ≥ 1 time in ep01 | `internal_consistency` level (NFR-9) |
| 焚寿罗盘 ledger across episodes | `internal_consistency` level |

The master assumes the conformance levels have already greened — if they haven't, master findings may be diluted. The parent runs master AFTER acceptance + internal-consistency on each iteration.

---

## 2. The 8 review axes

Per `agent_refs/project/ai_video.md` §12.4-D (D1–D6 dialogue + S1–S5 shot-design = 11 sub-criteria; we consolidate into 8 axes per move 9's 4-per-shot + 4-cross-shot grouping).

### Per-shot axes (1–4 = D1, D2/D5, D3/D6, D4 collapsed)

#### Axis 1 — 通俗易懂性 (D1)

**Question template:** "Could a 抖音/红果 viewer with no xianxia background parse this line in one hearing?"

**Triggers a flag when:**
- Line is pure 古文 / 文言文 / 玄学 aphorism with no actionable subtext (e.g., `玄机暗藏，因果自衡` standalone).
- Idiom usage without contextual trigger (a 7-year-old 重生 cultivator reciting `天行有常，不为尧存` in a survival scene).
- Compound classical compound (4+ chained四字成语 in a row).

**Carve-out for《焚寿录》:** 裴知秋 IS a 重生 cultivator with前世 memories — ONE deliberate ceremonial classical line is permitted in: (a) 师父剪影 cliffhanger beat (1:45–2:00), (b) 自取新名「裴知秋」水边题字 beat (1:15–1:30 — the题字 itself can be classical 「秋意至，鸿雁不返」-style), (c) 系统弹窗 if framed as 罗盘自生文字 (not protagonist's voice). Anywhere else = warning.

**Severity:** failure → `warning` + proposed rewrite. Two+ failures in the same shot → `blocker` (signals the whole shot's voice register is wrong, not one slip).

**Proposed-rewrite format:**
```
shot{NN} line {idx} (speaker={name}): fails Axis-1 (通俗易懂)
  old: "{exact quoted line}"
  reason: {古文 / 玄学 / idiom-chain — one phrase}
  new:   "{rewrite preserving the same beat function in modern colloquial — ≤ 15 字}"
```

#### Axis 2 — 信息量 / 钩 (D2 + D5)

**Question template:** "If this line were deleted, would the plot chain break OR a stake go missing OR a character beat be lost?"

**Triggers a flag when:**
- Line is atmospheric only (`风萧萧兮` / `夜深了` / `这一切都是命` standalone).
- Line restates what the previous line or the visual already said (`你回来了` after a cut-in showing the speaker arriving).
- 短剧 reversal-density rule: a shot longer than 6s with **zero** information change in dialogue (no stake / no reveal / no threat / no plant). Group-monologue shots get ONE reveal across the whole scene minimum.

**Carve-out for ep01:** the 0:03–0:30 倒叙 montage's 6 betrayer pairs each plant a face that ep08/ep10/ep17/ep28 will pay off. **Visual planting counts as information** — a montage shot with NO dialogue but a clearly-recognizable betrayer face passes Axis-2 (it's planting, not decorating). Master MUST NOT flag the montage as "decorative" — this is explicitly carved out per the prompt + dossier R-4.

**Severity:** failure → `warning` + proposed rewrite (master suggests what stake / reveal / plant the line could carry). Two+ failures consecutive → `blocker` (the scene is empty-calorie).

**Proposed-rewrite format:**
```
shot{NN} line {idx} (speaker={name}): fails Axis-2 (信息量)
  old: "{line}"
  reason: {decorative / restatement / no stake — one phrase}
  new:   "{rewrite that advances the named beat — name the planted seed or stake}"
  seed_planted (if applicable): {ep08 卫长烛 face / ep10 寿命代价 / ep17 前世名 / ...}
```

#### Axis 3 — 节奏 + 名场面 (D3 + D6)

**Question template:** "Is this line ≤ 15 字 (or ≤ 7 字 for a hook payoff / cliffhanger / branded line)? If it's longer, is it explicitly ceremonial / declaration / 召唤令?"

**Triggers a flag when:**
- ≥ 16 字 in a single bubble (NOT a labeled ceremony / 系统弹窗 / 召唤令).
- ≥ 3 clauses chained in one bubble (`你听好，我今日给你一个机会，但若你不珍惜，那便莫怪我心狠手辣`).
- Hook payoff / cliffhanger line > 7 字 when ≤ 7 字 version exists (`我必让你魂飞魄散` instead of `让你魂飞魄散`).
- 系统弹窗 line over 12 字 (the pattern `代价已计算 · 寿元 -1 / 修为 +1` is the gold standard — ~14 字 total but structured as 3 atomic clauses, OK).

**Ceremonial carve-outs for ep01:**
- 1:45 师父剪影 cliffhanger reveal line (闻砚清 first identifiable utterance) — up to 25 字 if it's a 召唤令 / 揭示性 ceremonial declaration.
- 系统弹窗 — counted as ledger text, not dialogue (no character voice register applies).

**Severity:** ≥ 16 字 single bubble → `warning` + split-or-compress patch. Hook payoff > 7 字 with cleaner alt → `warning`. Three+ Axis-3 failures in one shot → `blocker` (节奏 is broken at shot level).

**Proposed-rewrite format:**
```
shot{NN} line {idx} (speaker={name}): fails Axis-3 (节奏)
  old: "{line}" ({字数}字)
  reason: {长 bubble / 多 clause / hook 过长 — one phrase}
  new:   "{≤ 15 字 rewrite OR split-into-two-beats with second beat shown}"
```

#### Axis 4 — 角色声口 (D4)

**Question template:** "Does this line's word choice / register / 称谓 / cadence match the speaker's 锁定描述符 in `characters/{name}.md` (station, age observation, personality, schtick)?"

**Triggers a flag when:**
- 7岁体重生 裴知秋 speaks pure 前世 cadence in body B (the parasitic-awakening state) without the in-fiction beat (he hasn't `unlocked` 前世记忆 in ep01 yet — only 师父 cliffhanger triggers the 前世 echo at the closing 15s).
- 言息 (final boss, 忘川教教主, 名 = "息" pun) speaks like a low-station betrayer (`你给我等着，我要让你死无葬身之地`) — should carry 高 station register: 简练 + 命定感 + 第三人称自指或不带主语的预言.
- 应砚之 (朝堂太师之子, 文气背叛者) speaks like 池洇 (杀手 长老) — 应 should carry 朝堂书面感 (`此乃国法所容，岂能容你抗辩`); 池 should carry 散修杀手低沉 (`一刀，不说第二句`).
- 卫长烛 (赤霞门掌门, 正派背叛者 #1) using 魔门 register or vice versa.
- 闻砚清 师父 (ep01 剪影 + 最后一帧正脸闪) — should carry 沉稳师者 register; should NOT use 弟子 self-referential cadence.
- 容漪 ep01 cameo — VISUAL ONLY per spec FR-5 / NFR-12; she has NO dialogue in ep01. If a shot prompt assigns her a line, that's a separate Axis-7 blocker (anachronism — character is visual-only-cameo).

**Severity:** voice mismatch contradicting bible 角色定位 → `blocker` (per move 9). Voice mismatch within 角色定位 but minor register slip (e.g., 卫长烛 using 散修 cadence on one line) → `warning` with proposed register fix.

**Proposed-rewrite format:**
```
shot{NN} line {idx} (speaker={name}): fails Axis-4 (角色声口)
  old: "{line}"
  reason: {register collision — name the wrong station / wrong age-register / wrong schtick}
  expected_register: {one-line description from characters/{name}.md 锁定描述符}
  new:   "{rewrite carrying the expected register, same plot function}"
```

### Cross-shot axes (5–8 = S1, S2, S3, S5 — S4 visual-density is mostly conformance, folded into axis 8)

#### Axis 5 — 钩落 / hook landing (S1)

**Question template:** "For every shot tagged hook / 反转 / cliffhanger in shotlist.md, is the named hook visibly landed in 镜头 + 动作 + 台词 within the declared seconds?"

**ep01-specific hooks that MUST land (from FR-8 + R-4):**
- **shot01 (0:00–0:03) — 死亡开局 hook:** 雷劫劈下 + 剑刺穿 + cut-to-black must ALL be in 镜头 / 动作; 台词 may be silent or 1 line ≤ 5 字. Hook lands iff visual sequence completes before the cut.
- **倒叙 montage shots (covering 0:03–0:30) — planting hooks:** each of the 6 betrayer pairs must show the trust-frame + reversal-frame within its allotted seconds. Master accepts these as planting (per Axis-2 carve-out) but checks that the RECOGNIZABLE FACE shows in BOTH the trust frame AND the reversal frame (i.e., not a generic silhouette in either) — otherwise the ep08/ep10 callback can't be funded.
- **shot covering 0:30–1:15 — 系统觉醒 hook:** 焚寿罗盘 浮现 + 系统弹窗「代价已计算 · 寿元 -1 / 修为 +1」 + 五拍 寄生升级 motif must all be visibly delivered.
- **shot covering 1:15–1:45 — 自取新名 hook:** 水边题字「裴知秋」 must be readable on frame (the 3 characters visibly written / 题字 / 浮现).
- **cliffhanger shot (1:45–2:00) — 师父剪影 hook + cover_frame:** 剪影 + turn + 正脸闪一帧 + 闪黑 + 「第二集 即将揭晓」字幕. All five sub-beats must land.

**Severity:** named hook NOT landed within declared seconds → `blocker`. Hook landed but visually weak (e.g., 焚寿罗盘 shown but 弹窗 text missing) → `warning` + which sub-beat is missing.

**Patch format:**
```
shot{NN} (hook={hook_name}): fails Axis-5 (钩落)
  declared_seconds: {start}–{end}s ({duration}s)
  missing_sub_beat: {sub-beat name, e.g., "弹窗台词「代价已计算」not present in 台词 / 字幕"}
  patch: add to {field} — "{exact content to insert}"
```

#### Axis 6 — 情节链 (S2)

**Question template:** "Is this shot's beat a non-removable step in ep01's plot chain (per FR-8 5-beat structure + R-4)? If removed, does the chain still link?"

**Triggers a flag when:**
- Shot adds no plot turn, no character reveal, no stake escalation, no plant for ep02+, no hook landing — purely atmospheric or filler.
- Two adjacent shots could be merged with no loss of information.

**ep01-specific carve-out (REPEATED for emphasis, from prompt §Scope):** the 0:03–0:30 倒叙 montage's betrayer pairs ARE non-removable — each plants a face that ep08/ep10/ep17/ep28/ep49/ep60 will pay off. Master MUST NOT flag any of these montage shots as decorative. If the shotlist puts 6 betrayer pairs into 1 dense shot (≤15s) vs 2 shots (each ~12-13s), both designs are acceptable per Axis-6 — Axis-6 cares about whether the planting happens, not how it's packed.

**Severity:** decorative shot → `blocker` (per move 9). Two adjacent shots mergeable → `warning` with merge suggestion.

**Patch format:**
```
shot{NN}: fails Axis-6 (情节链)
  beat_claimed: {what the shot says it does}
  beat_actually_delivered: {what the shot really delivers}
  removal_test: chain still links if removed → YES
  patch: either (a) cut shot and renumber, OR (b) re-author beat to {specific step in FR-8 5-beat structure}
```

#### Axis 7 — Character-station fidelity + anachronism guard (S3 + per-prompt-extras)

**Question template:** "Does every character named in this shot's dialogue exist in ep01's introduced cast (per FR-5 9-character list)? Is any forward-arc reference present?"

**ep01-specific anachronism rules (HARD):**
- 容漪 ep01 cameo is VISUAL ONLY (spec FR-5 row: "ep01 cameo only (作为旁观者出现于某 montage 帧, ≤1 shot); 完整出场始于 ep05"). Her NAME must NOT appear in any dialogue line — not even as 那女子 / 她 referent if context makes the reader IDENTIFY her. The visual planting alone is acceptable; spoken-name = `blocker`.
- 灵兽 乌泽 (ep05 debut per dossier R-6) — name must NOT appear in ep01 dialogue.
- ep02+ NEW betrayers (none in ep01 cast — but stage 6 may invent supporting characters; any name not in the FR-5 9-character bible = blocker).
- 神器 / 功法 names: only **焚寿罗盘** (the 24-tick dial — central in ep01) is fair game in ep01 dialogue. **《残忆经》** (主角功法, hidden by 师父 in ep01 — not yet learned) — name may appear ONLY in 师父剪影 cliffhanger line if framed as a forward-tease, NOT in 主角 自指 dialogue. **《偿岁真言》** (ep20 reveal) → blocker. **归砚镜** (ep08 reveal) → blocker. **长烟幡** (ep35 reveal) → blocker.
- Sect names: 赤霞门 / 九寰阁 / 澹台宗 / 流烛盟 / 忘川教 — all 5 may appear in 倒叙 montage visual context (banners, robes, 阵旗), but NAMED in 台词 only if the betrayer is being identified by sect affiliation in that very montage pair. 忘川教 NAMED in 主角 ep01 inner-monologue without ep17 反 sect-realization having happened yet = warning (主角 in body B has前世 echo but doesn't fully recall — the name 言息 / 忘川教 in 自指 voice without 师父 trigger is too on-the-nose).
- 地名: **澹江洲** (主角家乡 — fine to name in ep01) / **落雁渊** (觉醒地 — fine) / **栖梧崖** (旧名 无寿崖, ep17 reveal) — the旧名「无寿崖」 may appear in ep01 倒叙 雷劫场景 inline diegetic (碑刻 / 旁白 / 雷劫处 title card); but if NAMED in 主角 本世 dialogue before ep17 reveal → blocker.

**Station fidelity:** speaker tone in `(语气..., 朝/望谁): "..."` matches character bible. Covered by Axis-4 mechanically; Axis-7 adds the cross-shot consistency check (e.g., 闻砚清 师父 should NOT appear via spoken name in betrayer dialogue at 0:03–0:30 — he died first, betrayers don't have a moment to name him).

**Severity:** any anachronistic name → `blocker` (per move 9). Station-fidelity drift across two shots of the same character within ep01 → `warning`.

**Patch format:**
```
shot{NN} line {idx} (speaker={name}): fails Axis-7 (anachronism / station fidelity)
  flagged_token: "{name / sect / artifact / location}"
  reason: introduced in {ep|stage|spec_section}; ep01 cast bound to FR-5 9-character list + scene-locked artifacts
  patch: replace with {scene-level pronoun / station referent / drop the name} — example: "{rewrite}"
```

#### Axis 8 — 反转密度 + 反复模板 + 视觉差异化 (D5 cross-shot + S4 + S5)

**Question template:** "Within ep01, do any two shots reuse near-identical dialogue templates for different characters / threats? Do any two adjacent shots deliver visually duplicate beats with no plot delta?"

**Triggers a flag when:**
- Two characters (e.g., 卫长烛 + 应砚之 + 戚归砚 — any pair) deliver near-identical threat / promise / oath phrasing in the 倒叙 trust-frame OR reversal-frame. The 6 betrayers MUST sound distinct from each other so the audience encodes each face with each voice — pattern duplication weakens all 6 future-payoff hooks.
- Two adjacent shots are visually near-duplicate (`from a different angle` with no plot delta — e.g., shot04 + shot05 both = 主角 standing at 落雁渊 渊底, different angle, same beat).
- 系统弹窗 line repeated verbatim in two non-consecutive shots without ledger increment (the弹窗 is supposed to TICK the dial — same text appearing twice means the dial didn't move = ledger fail; defer to internal_consistency for ledger math, but master flags duplicate text as a warning).

**ep01 differentiation hint matrix (6 betrayer voice-distinct templates):**
- 卫长烛 (赤霞门掌门, 正派 → 背叛 #1): 高位 + 礼训式 + 用「门规」「正道」托词. Trust frame: `此剑为吾门之器，今日传于汝`. Reversal: `背宗叛祖，门规处置`.
- 应砚之 (朝堂太师之子, 正派 → 背叛 #2): 朝堂书面感 + 用「国法」「天下」托词. Trust frame: `共上此奏，必可清君侧`. Reversal: `罪在不赦，唯有诛之`.
- 戚归砚 (散修 → 暗投魔门, 背叛 #3): 江湖兄弟感 + 用「共生」「兄弟」托词. Trust frame: `生死共担，永不相弃`. Reversal: `各人造化，莫怪`.
- 池洇 (散修杀手, 背叛 #4): 杀手低沉 + 不带托词 + 短句. Trust frame: `这条命，记你的`. Reversal: `一刀，不欠了`.
- 阮惘 (忘川教三长老, 背叛 #5): 魔门 + 命数感 + 用「劫」「数」托词. Trust frame: `此劫渡你，他日相还`. Reversal: `劫到，归位`.
- 言息 (忘川教教主 / final boss, 背叛 #6): 神位 + 不带主语 + 预言感. Trust frame: `授业三月，足矣`. Reversal: `时辰到`.

If two betrayers' lines feel interchangeable (same托词, same清浊, same字数 range), master flags + suggests differentiation hint from the matrix above.

**Severity:** two shots' threats reuse near-identical templates → `warning` + differentiation patch. Two adjacent shots visually duplicate with no plot delta → `warning` + merge-or-differentiate suggestion. NEVER blocker on Axis 8 alone (per move 9 severity policy).

**Patch format:**
```
shot{NN1} line {idx1} ({name1}) vs shot{NN2} line {idx2} ({name2}): fails Axis-8 (反复模板)
  pattern: "{shared phrasing — e.g., '今日便是你的劫数'}"
  differentiation_hint:
    {name1}: {voice-distinct template from matrix} — "{new line}"
    {name2}: {voice-distinct template from matrix} — "{new line}"
```

---

## 3. Project-specific dialogue do's and don'ts

Drawn from `findings/angle-trend_research.md` §3.1 (saturated tropes via dialogue) + §3.2 (right-use trope-borrowing) + dossier CCI-2 (parasitic-cost is the load-bearing differentiator).

### 3.1 — DON'T patterns (auto-flag with patch)

| Pattern | Why blocked | Example "old" | Patch direction |
|---|---|---|---|
| 工业糖精白月光台词 | trend §3.1 saturated; pulls 短剧 into 言情 register | `我会等你 / 你心里只有她 / 你怎么忍心` | Cut entirely OR replace with stake-bearing line (`你要的是我的命，不是我的心`) |
| 师父工具人台词 | 闻砚清 ep01 剪影 must be functional + tease, not 说教 | `孩子，记住为师的话` / `好自为之` | Replace with concrete next-step or revelation tease (`砚清未死。秋至，归来。`) |
| 圣母「我重生了但我要原谅」 | 主角弧光是复仇 — 重生原谅是 anti-genre | `我重生只为放下 / 既已重来何必复仇` | Replace with cost-aware revenge line (`重生不是为放下。这一次，他们一个都不能活。`) |
| 主角 expository 解释 寄生 mechanic | trend §3.1 + dossier R-4: 寄生 is SHOW-don't-tell — viewer infers from罗盘 + 弹窗 + 五拍 motif | `每升一阶我都会失去一段记忆和一年寿命` | Drop entirely. 弹窗自带 ledger; 主角 reaction line should be visceral / single-word / silence (`...一格`) |
| 集尾 自我提示 cliffhanger | trend §3.2: cliffhanger should TEASE via 第二集字幕 + 视觉 reveal, NOT 主角 self-narration | `欲知后事如何，请看下集` (主角自言) | Drop. Use platform-convention 倒数字幕 `第二集 即将揭晓` per FR-8 / trend §3.2 |
| 长 monologue 解释格局 | trend §3.1: 短剧 audience flees 5s+ uncut monologue | 60-字 解释 三方势力 in one bubble | Split into ≤ 15 字 beats interleaved with 镜头 + 动作 OR cut entirely (the 视觉 + world.md ledger carries it; ep01 doesn't need a格局讲解) |

### 3.2 — DO patterns (positive reinforcement)

| Pattern | Where it MUST appear in ep01 | Source contract |
|---|---|---|
| 系统弹窗 ledger pattern | shot covering 0:30–1:15 awakening beat — `代价已计算 · 寿元 -1 / 修为 +1` (or equivalent三段 atomic structure) | trend §3.2 + dossier R-4 + style_guide § 字幕规范 (内嵌硬字幕 per FR-10.4) |
| 倒数字幕 cliffhanger | last frame of cliffhanger shot (1:45–2:00) — `第二集 即将揭晓` | trend §3.2 platform convention + FR-8 |
| 自取新名 题字 | 1:15–1:30 水边题字 — 「裴知秋」 3字 visible on frame; 主角 utterance ≤ 7 字 OR silent | dossier R-4 + FR-8 |
| 系统觉醒 reaction = minimal | After 弹窗 + 罗盘 浮现 — 主角 反应 ≤ 3 字 or silence (`...一格 / ...痛 / 静默`) | trend §3.1 parasitic-show-don't-tell + dossier CCI-2 |
| 师父剪影 cliffhanger 揭示 | 1:45 — 闻砚清 first identifiable line, declarative / 预言性, ≤ 15 字 | FR-8 + Axis-3 ceremonial carve-out |

### 3.3 — 寄生系统 dialogue carve-out (project-unique)

Because parasitic-cost is《焚寿录》的 load-bearing differentiator (CCI-2 zero-precedent), the 弹窗台词 pattern is BOTH (a) a positive contract (must appear) AND (b) a separate visual motif protected by NFR-9. The dialogue line `代价已计算 · 寿元 -N / 修为 +1`:

- IS first-class dialogue per CLAUDE.md § AI video rules ("dialogue is first-class shot field rendered as on-frame subtitles") — counted toward 台词 / 字幕 schema.
- IS NOT counted under Axis-4 (角色声口) — it has no character speaker; it's 罗盘自生 ledger text.
- IS counted under Axis-7 (anachronism) — the format `代价已计算 · 寿元 -N / 修为 +1` is the LOCKED template for ep01–ep60; deviation in ep01 (e.g., adding 中文数词 or 文言文 framing) → warning.
- **Master proposes a project-spec carve-out at the bottom of this doc** — NFR-9 already protects the visual motif's PRESENCE; we propose adding **NFR-9b** for the textual template's BYTE-IDENTITY across episodes (similar to NFR-2 for character descriptors).

---

## 4. Patch-list output format

Per `agent_refs/project/ai_video.md` §12.4-D + `agent_refs/validation/ai_video.md` move 9, the master emits a **per-shot patch list** — NOT free-form prose. Stage-6 validators read this directly and the parent applies patches inline with `Edit`.

### 4.1 — Per-shot JSON envelope (the canonical machine-readable form)

```json
{
  "shot_id": "shot{NN}",
  "shot_path": "my_novel/feng_shou_lu/episodes/ep01/shots/shot{NN}.md",
  "axes_evaluated": [1, 2, 3, 4, 5, 6, 7, 8],
  "D_flags": ["D1", "D5"],
  "S_flags": ["S3"],
  "verdict": "pass | warning | blocker",
  "patches": [
    {
      "axis": 1,
      "severity": "warning",
      "field": "台词 / 字幕",
      "line_idx": 3,
      "speaker": "卫长烛",
      "old": "玄机暗藏，因果自衡",
      "reason": "古文 aphorism without contextual trigger",
      "new": "今夜你死，三界归我",
      "rationale": "preserves the threat function, ≤ 8 字, modern colloquial"
    },
    {
      "axis": 7,
      "severity": "blocker",
      "field": "台词 / 字幕",
      "line_idx": 5,
      "speaker": "裴知秋",
      "old": "归砚镜终有一日会照出真相",
      "reason": "归砚镜 = ep08 reveal; anachronistic in ep01",
      "new": "总有一日，所有真相都会照出来",
      "rationale": "preserves the foreshadow function via 抽象指代 without naming the future artifact"
    },
    {
      "axis": 5,
      "severity": "blocker",
      "field": "动作",
      "beat_range": "0–3s",
      "old": "主角静立望向远处",
      "reason": "shot marked H1 死亡开局 hook but 雷劫 + 剑刺 not visibly delivered",
      "new": "0–1s 雷柱第三道贯顶劈下 / 1–2s 剑光自背后穿心而出 / 2–3s 主角踉跄 + 画面渐黑切",
      "rationale": "lands all three sub-beats of the 死亡开局 hook per FR-8 + R-4"
    }
  ]
}
```

### 4.2 — Per-shot markdown form (the human-readable mirror, also written to `.audit/.../events.jsonl` as `validation.issue.raised` payloads)

```
## shot{NN} — {shot_summary}
D-flags: [D1, D5]
S-flags: [S3]
verdict: blocker
patches:
  - Axis 1 (warning) · 台词 / 字幕 line 3 · 卫长烛
    fails: 古文 aphorism without contextual trigger
    old: "玄机暗藏，因果自衡"
    new: "今夜你死，三界归我"
  - Axis 7 (blocker) · 台词 / 字幕 line 5 · 裴知秋
    fails: 归砚镜 = ep08 reveal; anachronistic in ep01
    old: "归砚镜终有一日会照出真相"
    new: "总有一日，所有真相都会照出来"
  - Axis 5 (blocker) · 动作 0–3s
    fails: H1 死亡开局 hook not landed — 雷劫 + 剑刺 missing
    old: "主角静立望向远处"
    new: "0–1s 雷柱第三道贯顶劈下 / 1–2s 剑光自背后穿心而出 / 2–3s 主角踉跄 + 画面渐黑切"
```

### 4.3 — Cross-shot patch block (Axis 8 + ep01 6-betrayer differentiation)

When axes 6 / 7 / 8 fire across multiple shots, the master emits a separate cross-shot block AFTER all per-shot blocks:

```
## cross-shot — ep01
axis-8 / 反复模板:
  - shot02 line 4 (卫长烛 reversal) + shot02 line 8 (应砚之 reversal):
    pattern: both use "今日便是你的劫数 + N 字"
    patch:
      卫长烛: "背宗叛祖，门规处置" (礼训式)
      应砚之: "罪在不赦，唯有诛之" (朝堂书面感)
axis-7 / anachronism:
  - shot06 line 2: 容漪 named in spoken dialogue — ep01 cameo is visual only per spec FR-5
    patch: drop the name; replace with "那女子" only if she's NOT visually identifiable in same shot; otherwise drop the line entirely (visual is enough)
```

### 4.4 — Final iteration verdict

After all patches are applied + master re-runs:

```
## ep01 master verdict
shots evaluated: {N}
total patches applied this round: {M}
remaining blockers: {B}
remaining warnings: {W}
verdict: PASS (B=0 AND W ≤ 2) | RE-RUN (B>0 OR W>2) | HALT (B>0 AND same-issue across 2 rounds)
```

---

## 5. Iteration protocol

Per move 9 + CLAUDE.md § Iteration bounds:

1. **Round 1:** master runs against the freshly-written ep01 shot prompts (post-acceptance / post-internal-consistency green). Emits patch list. Parent applies patches surgically via `Edit` — one `Edit` per patch (line-level for 台词 / beat-level for 动作 / field-level for 镜头).
2. **Round 2:** master re-runs. If any blocker persists from round 1 with the SAME `axis + shot_id + line_idx` triplet → **halt** with `pipeline.halted` event. (CLAUDE.md circuit-breaker: same issue repeats across two iterations = halt.)
3. **Round 3 (final cap):** if rounds 1 + 2 cleared all blockers but residual warnings still > 2, run a focused warning-resolution pass. After round 3, `pipeline.halted` if warnings > 2 still — surface to user with the patch list.
4. **PASS condition:** 0 blockers AND ≤ 2 warnings remain. Emit `validation.pass` for the storyteller-dialogue level. ep01 work unit can proceed to `validation.requires_manual_walkthrough` (move 8).

**Halt-and-escalate decision tree:**

| Round | Blockers | Warnings | Same-issue-repeat | Action |
|---|---|---|---|---|
| 1 | 0 | ≤ 2 | n/a | PASS |
| 1 | 0 | > 2 | n/a | Round 2 (warnings only) |
| 1 | > 0 | any | n/a | Round 2 (with patches) |
| 2 | 0 | ≤ 2 | n/a | PASS |
| 2 | 0 | > 2 | n/a | Round 3 (warnings only) |
| 2 | > 0 | any | YES | HALT + `pipeline.halted` |
| 2 | > 0 | any | NO | Round 3 (with patches) |
| 3 | 0 | ≤ 2 | n/a | PASS |
| 3 | 0 | > 2 | n/a | HALT + escalate warnings to user |
| 3 | > 0 | any | n/a | HALT + escalate blockers to user |

Audit-event contract per round:

- Round start: `validation.started` with `level=storyteller_dialogue_master, round={1|2|3}, shots_in_scope=[shot01..shotNN]`.
- Each patch issued: `validation.issue.raised` with payload = the JSON envelope from §4.1.
- Round end pass: `validation.pass` with `level=storyteller_dialogue_master, round={N}, verdict=PASS`.
- Round end halt: `pipeline.halted` with `level=storyteller_dialogue_master, round={N}, reason={same-issue-repeat | excess-warnings | excess-blockers}, residual_issues=[...]`.

---

## 6. ep01-specific risk register (most-likely first-pass failures, ranked)

Ordered by probability of triggering a blocker on round 1, based on the FR-8 5-beat structure + 6-betrayer 倒叙 + R-4 dossier:

1. **Axis 7 anachronism — 容漪 named in dialogue.** Spec FR-5 puts 容漪 in ep01 as visual-only cameo, but stage 6 may default to naming her in 主角 inner-monologue (`那女子让我心生悸动` etc.). PROBABILITY: HIGH. PATCH READY.
2. **Axis 8 + Axis 4 — 6 betrayers' 倒叙 dialogue sounds interchangeable.** Stage 6 may collapse all 6 reversal-frame lines into the same `今日便是你的劫数` template because they share the same beat function. PROBABILITY: HIGH. PATCH READY (the 6-template matrix in §2 Axis 8).
3. **Axis 5 — 死亡开局 hook under-delivered.** Stage 6 may write `主角站立 + 雷劫劈下` without explicitly sequencing 雷劫 → 剑刺 → cut-to-black, leaving the hook visually ambiguous in the 3s window. PROBABILITY: MEDIUM-HIGH. PATCH READY (3-sub-beat sequence in §2 Axis 5).
4. **Axis 1 + Axis 4 — 闻砚清 师父剪影 line drifts into 师父工具人 register.** The default trap is `孩子，记住为师的话` even though it's a cliffhanger reveal that should TEASE next ep. PROBABILITY: MEDIUM. PATCH: replace with concrete tease (`砚清未死。秋至，归来。`).
5. **Axis 2 — 弹窗 expository over-explained.** Stage 6 may add 主角 inner-monologue explaining 寄生 mechanic for clarity, violating show-don't-tell. PROBABILITY: MEDIUM. PATCH: drop monologue; rely on弹窗 + 罗盘 visual + 反应 single-word.
6. **Axis 3 — 师父剪影 line too long.** The cliffhanger reveal line tempts authors to over-explain (`砚清未死，但他的剑已不在他手中，秋至时分必有相见`); should be ≤ 15 字 declarative. PROBABILITY: LOW-MEDIUM. PATCH: compress.
7. **Axis 7 — 旧名 无寿崖 vs 现名 栖梧崖 anachronism.** 倒叙 雷劫场景 should use 无寿崖 (前世 era); 本世 should use 栖梧崖. If 主角 本世 narration uses 栖梧崖 fine, but 旧名 in 本世 自指 dialogue before ep17 reveal = blocker. PROBABILITY: LOW-MEDIUM. PATCH: tag by era.
8. **Axis 7 — 神器 anachronism.** Stage 6 may seed `归砚镜` or `《残忆经》` ahead of their reveal episodes in 主角 inner-monologue or 师父 cliffhanger. PROBABILITY: LOW-MEDIUM (depending on stage-6 awareness of reveal cadence). PATCH: replace with scene-level pronoun or drop.

---

## 7. Integration with stage-6 (work_unit_kind = `shot_prompt`)

Stage 6 emits `exec.unit.started` for each shot prompt as a work unit (per FR-14). After the unit completes:

1. **acceptance_criteria validator** runs first (NFR-1 word count, NFR-3 比例, NFR-5 timing, NFR-11 language, NFR-12 link integrity).
2. **internal_consistency validator** runs second (NFR-2 character descriptor byte-identity, NFR-9 寄生 motif presence, ledger math).
3. **storyteller_dialogue_master** runs third (this level — assumes the above are green; runs the 8-axis review).
4. **Other levels** (copyright clearance, genre fidelity, short-drama feasibility, hook/retention) run in parallel with steps 1–3 since they're independent.

Master's per-shot output flows back to stage 6 as:

- `validation.issue.raised` events with the JSON envelope from §4.1 as payload.
- Parent applies patches via `Edit` (one Edit per patch — line-level for 台词, beat-level for 动作).
- After all patches applied, parent re-spawns the master worker for round 2 (and round 3 if needed).
- Master emits `validation.pass` for the storyteller_dialogue level on the shot. Once ALL ep01 shots have storyteller_dialogue PASS + all other levels PASS, parent emits `validation.requires_manual_walkthrough` per move 8.

**Master does NOT block on shot-1 individually if shot-2..shot-N are still in-flight.** Cross-shot axes (5, 7, 8) require the WHOLE ep01 shotlist to be present. Strategy: master runs per-shot for axes 1–4 + 6 immediately on each shot completion; cross-shot axes 5 / 7 / 8 run at the EPISODE-CLOSING pass once all 7 shots exist. This is the same pattern as move 9's "stage 6 the master runs against every shot md as it's written + at the closing pass of every episode".

---

## 8. Proposed spec carve-out for system弹窗 dialogue template (NFR-9b)

NFR-9 already protects the 寄生升级 motif's PRESENCE (≥ 1 occurrence in ep01). What's NOT yet protected: the 弹窗 dialogue template's **byte-identity across episodes**. The line `代价已计算 · 寿元 -N / 修为 +1` will recur in ep08 (失母亲长相记忆 — `寿元 -1 / 修为 +1 / 记忆 -1段`), ep10, ep17, ep30, etc. If ep01 writes `代价已计算 · 寿元 -1 / 修为 +1` and ep08 drifts to `代价计算完成 · 寿元 减 1 / 修为 加 1`, the audience loses the franchise-style ledger callback.

**Proposed addition to spec.md NFR table:**

| NFR-9b | 系统弹窗 dialogue template byte-identity across episodes | The 弹窗 is BOTH visual motif (NFR-9) AND franchise-style ledger callback (cross-episode reveal cadence per dossier R-6); drift defeats the callback | Stage 5 byte-compares the弹窗 template substring across all ep`NN`/script.md + shot prompts; drift = blocker; ep01 sets the canonical form. |

This is a separate consideration from NFR-9 (visual motif) and complements rather than overlaps. RECOMMENDATION: surface as an Open Question for user approval at stage-5 validation review gate — if accepted, becomes NFR-9b in spec.md and binds ep02+ stage-4 regen.

---

## Pre-reading consulted (this level)

- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/final_specs/spec.md`
- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/findings/dossier.md`
- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/findings/angle-trend_research.md` (§3.1 saturated tropes + §3.2 right-use trope-borrowing — applied to §3 do/don't tables)
- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/findings/angle-character_anonymization.md` (§3 station + 词源 — applied to Axis 4 register matrix + Axis 8 6-betrayer differentiation matrix)
- `C:/workspace/spec_coding/.claude/agent_refs/project/ai_video.md` §12.4-D (lines 478–516 — D1–D6 + S1–S5 criteria + per-shot output format)
- `C:/workspace/spec_coding/.claude/agent_refs/validation/ai_video.md` move 9 (lines 83–102 — validator pseudo-rule per shot, severity policy, master output format)
- `C:/workspace/spec_coding/.claude/agent_refs/project/general.md` (background reference)
- CLAUDE.md § Iteration bounds (3-round cap, same-issue circuit-breaker, pipeline.halted contract)
