---
worker_id: level-specialist-01-acceptance_criteria
stage: 5
role: level-specialist
level: acceptance_criteria
status: complete
blockers: []
confidence: high
---

# Acceptance criteria — 《焚寿录》ep01 (slug `feng_shou_lu`)

## 1. Scope

This file is the Gherkin gate-check layer of the stage-5 validation strategy for run `xianxia_new-20260524-101931` (MVP scope: ep01 only, per `interview/qa.md` Q11 override and follow-up 001). It produces one or more `Given / When / Then` scenarios for every FR-1 through FR-14 in `final_specs/spec.md`, a measurable `Rule:` assertion for every NFR-1 through NFR-13, and a master scenario for each AC-1 through AC-7. Severity uses the table in `agent_refs/validation/general.md` § Standard severity policy, escalated per `agent_refs/validation/ai_video.md` § Severity escalations.

What this file does **not** cover (handed off to sibling level-specialists in the same stage-5 fan-out):

- Subjective hook landing / 通俗易懂 dialogue / character voice fidelity → `storyteller_dialogue_master` per ai_video.md rule 9.
- Per-axis copyright grep against BLACKLIST + `ai_videos/mozun_chongsheng/` → `copyright_clearance` level.
- Genre-fidelity ladder / trifecta / cadence checks → `genre_fidelity` level.
- Internal-consistency / 寿元 ledger arithmetic across episodes → `internal_consistency` level.
- Short-drama feasibility cast-size / prop-density audits (named characters per shot, prop per scene) → `short_drama_feasibility` level (NFR-7, NFR-8 are surfaced here as `Rule:` assertions but the auditing column they verify against lives in that level).

Stage 6 reads this file mechanically per work unit: each scenario maps to one or more grep / lint / count / file-existence checks. A scenario's `Then` clauses are the literal pass / fail predicates.

## 2. Scenarios

### FR-1 — README

**Scenario: AC-FR1-A — README primary file exists and opens with the locked H1**
Given the stage-6 run has emitted the FR-1 deliverable
When `my_novel/feng_shou_lu/README.md` is read
Then the file exists and is non-empty
And the first line equals `# 《焚寿录》— AI 视频项目`
And the body contains the four mandatory sections: `项目概要`, `使用说明`, `角色清单`, `风格关键词`
And `角色清单` lists exactly 9 character entries each linking to a path under `characters/`
**Severity:** blocker
**Source:** FR-1

**Scenario: AC-FR1-B — mirror README under ai_videos/ matches the canonical one**
Given `my_novel/feng_shou_lu/README.md` exists
When `ai_videos/feng_shou_lu/README.md` is read
Then the file exists and is non-empty
And the H1 matches the canonical README byte-for-byte
And the four mandatory sections are present
**Severity:** blocker
**Source:** FR-1, FR-13

### FR-2 — world.md

**Scenario: AC-FR2-A — world.md contains all five mandatory sections in order**
Given the stage-6 run has emitted the FR-2 deliverable
When `my_novel/feng_shou_lu/world.md` is read
Then headings appear in this exact order: `修炼境界体系` → `修炼物理规则` → `三方势力格局` → `地理与时代背景` → `寄生系统的 in-fiction lore`
And `修炼境界体系` lists 8 stages in the locked sequence `练气-筑基-金丹-元婴-化神-炼虚-合体-大乘` (terminal stage `大乘`, NOT `渡劫`, per Open Question #2 default)
And `修炼物理规则` contains the parasitic divergence clause naming both `寿元` and `记忆` as costs
And `三方势力格局` names exactly the five organizations `赤霞门`, `九寰阁`, `澹台宗`, `流烛盟`, `忘川教`
And `地理与时代背景` names `澹江洲`, `落雁渊`, and `栖梧崖` with the `无寿崖` rename hint
And `寄生系统的 in-fiction lore` captures the full ep17 / ep30 / ep49 / ep50 / ep60 truth (not redacted for MVP)
**Severity:** blocker
**Source:** FR-2

### FR-3 — style_guide.md

**Scenario: AC-FR3-A — style_guide.md ships all six mandatory subsections**
Given the stage-6 run has emitted the FR-3 deliverable
When `my_novel/feng_shou_lu/style_guide.md` is read
Then the six mandatory subsections are all present: `镜头语言关键词字典` (13 景别 + 9 运动), `光影词典` (12 状态 including `寄生 aura` and `寿命流失`), `调色板` (6 派系 each with 主/辅/点缀 hex), `字幕规范`, `转场词典` (9 类 including `寿命计数器过`), `负向锁定` (≥ 36 items: 24 baseline + 12 project-specific)
And every color entry includes a `#RRGGBB` hex triplet
And every palette entry carries ≥ 3 web visual citations
**Severity:** blocker
**Source:** FR-3, NFR-1 (cascades into shot prompts)

### FR-4 — arc_outline.md

**Scenario: AC-FR4-A — arc_outline contains 60 numbered episode lines**
Given the stage-6 run has emitted the FR-4 deliverable
When `my_novel/feng_shou_lu/arc_outline.md` is read
Then exactly 60 H3 lines match the pattern `### ep(0[1-9]|[1-5][0-9]|60) — `
And every line is ≤ 40 Chinese characters in the synopsis portion
**Severity:** blocker
**Source:** FR-4, AC-6

**Scenario: AC-FR4-B — the 10 reveal-cadence beats land at the assigned episodes**
Given `arc_outline.md` parsed by episode number
When the cadence-beat lookup table from spec § FR-4 is applied
Then ep01 line mentions `死亡开局`, `重生`, `系统觉醒`, `裴知秋`, AND `师父` cliffhanger
And ep08 line mentions `归砚镜` first activation
And ep10 line is flagged as `付费节点 1` AND mentions `卫长烛` AND mentions `母亲长相` memory loss
And ep17 line reveals `裴长砚` past-life name
And ep20 line names both `偿岁真言` and `残忆经`
And ep28 line names `容漪` AND `忘川教 planted`
And ep30 line is flagged as `付费节点 2` AND mentions parasitic-system origin
And ep35 line names `长烟幡` transfer
And ep49 line names `归砚镜` full memory restoration
And ep50 line is flagged as `付费节点 3` AND reveals 主角 = 系统 source
And ep60 line names `言息` defeat AND `续季钩`
**Severity:** blocker
**Source:** FR-4, AC-6

### FR-5 — Character bibles

**Scenario: AC-FR5-A — all 9 character bible files exist**
Given the stage-6 run has emitted the FR-5 deliverable
When `my_novel/feng_shou_lu/characters/` is listed
Then exactly these 9 `.md` files exist: `裴知秋.md`, `裴长砚.md`, `闻砚清.md`, `容漪.md`, `卫长烛.md`, `应砚之.md`, `戚归砚.md`, `池洇.md`, `阮惘.md`, `言息.md`
And each file follows the ai_video.md rule 12.1 schema (10-field 锁定描述符 + 性格 + 动机 + 弧光 + 标志台词 + 关键场景 + 标志能力 + 配音参考 + 负向)
And every file ends with a single `词源` line per FR-5.2
**Severity:** blocker
**Source:** FR-5

*Note: spec FR-5 table actually lists 10 file rows (the 9th `言息` plus the protagonist's archived past-life identity `裴长砚`). The FR-5 header says "9 files" but the table enumerates 10. AC-FR5-A treats the table as authoritative — 10 files total (`裴知秋` + `裴长砚` + 8 others). This divergence is flagged for stage-4 sign-off; the count line in FR-5's header should be patched.*

**Scenario: AC-FR5-B — protagonist 双形态 contract is honored**
Given `characters/裴知秋.md` is parsed
When the 锁定描述符 sections are extracted
Then exactly two locked descriptor blocks are present, labeled `## 锁定描述符 — state A: 重生弱体` AND `## 锁定描述符 — state B: 寄生觉醒`
And both blocks contain the literal string `左眼下方 0.3cm 灰青胎记` byte-for-byte identical
And the `一句话锁定` line differs between A and B
**Severity:** blocker
**Source:** FR-5.1, NFR-2

**Scenario: AC-FR5-C — every character bible ends with a 词源 line**
Given every file under `characters/*.md`
When the last non-empty line is read
Then the line begins with `词源` (or `# 词源` for sub-heading style)
**Severity:** blocker
**Source:** FR-5.2

**Scenario: AC-FR5-D — 配音参考 stays planning-only with no TTS prompts**
Given any character bible
When `配音参考` section is scanned
Then no TTS-API field (e.g., `voice_id`, `tts_provider`, `eleven_voice`) appears anywhere in the file
**Severity:** warning
**Source:** FR-5.3 (v1 visuals-only carve-out per spec § Out of scope #6)

**Scenario: AC-FR5-E — 负向 block re-pastes from style_guide + adds character-specific items**
Given each character bible
When the `负向` section is read
Then it contains every item from `style_guide.md § 负向锁定` (byte-identical, modulo whitespace)
And `卫长烛.md` 负向 contains both `不要戴墨镜` and `不要现代修剪眉`
**Severity:** warning (style_guide baseline drift) / blocker (if absent entirely)
**Source:** FR-5.4

### FR-6 — Seedream立绘 prompts

**Scenario: AC-FR6-A — every named character has a Seedream ref-image prompt; protagonist has two**
Given the stage-6 run has emitted the FR-6 deliverable
When `my_novel/feng_shou_lu/characters/ref_images/` is listed
Then the count of Seedream prompts is exactly 10 (or 11 if 裴长砚 also gets a立绘 — stage 6 decides)
And `裴知秋_state_a_seedream.md` + `裴知秋_state_b_seedream.md` BOTH exist (or one `裴知秋_seedream.md` with two prompts — both patterns acceptable per FR-5.1)
And every prompt declares `比例: 9:16` AND `4K` resolution
And every prompt body contains the byte-identical 一句话锁定 line from the matching character bible
**Severity:** blocker
**Source:** FR-6, NFR-2, NFR-3, ai_video.md rule 12.2

**Scenario: AC-FR6-B — every Seedream prompt carries the 8-block content schema**
Given every file under `characters/ref_images/*.md`
When the body is parsed for the 8 mandatory blocks
Then all of these are present: `主体定义`, `主体/构图`, `面部`, `服装`, `姿态`, `背景`, `光源`, `风格`
And a `负向` block follows, lifted from `style_guide.md § 负向锁定` + character-specific items
**Severity:** blocker
**Source:** FR-6

### FR-7 — Scene files + Scene立绘

**Scenario: AC-FR7-A — both scene files exist with locked descriptors**
Given the stage-6 run has emitted the FR-7 deliverable
When `my_novel/feng_shou_lu/scenes/` is listed
Then both `s1_无寿崖.md` and `s2_落雁渊.md` exist
And both `ref_images/s1_无寿崖_seedream.md` and `ref_images/s2_落雁渊_seedream.md` exist
And each scene file contains the 8-field 锁定描述符 + `关键变化态` (≥ 2 states per scene) + `出现镜头表` (forward-filled once shotlist exists) + `负向`
And every scene Seedream prompt declares `比例: 9:16`
**Severity:** blocker
**Source:** FR-7, NFR-3, ai_video.md rule 12.3

**Scenario: AC-FR7-B — scenes used in ≥2 shots are declared; one-shot backdrops stay inline**
Given the shotlist enumerates every shot's `主要场景`
When scene reuse is counted per scene token
Then any backdrop appearing in ≥ 2 shots has a matching `scenes/{slug}.md` file
And any backdrop appearing in exactly 1 shot has its description inline in that shot's prompt (no `scenes/` file required)
**Severity:** warning (a one-shot backdrop with a declared scene file is wasteful, not broken) / blocker (a ≥2-shot backdrop without a scene file)
**Source:** FR-7, ai_video.md rule 12.3

### FR-8 — episodes/ep01/script.md

**Scenario: AC-FR8-A — ep01 script lands all five beat groups within 8-min ceiling**
Given the stage-6 run has emitted the FR-8 deliverable
When `episodes/ep01/script.md` is parsed
Then the five required beat-time-ranges are present: `0:00–0:03`, `0:03–0:30`, `0:30–1:15`, `1:15–1:45`, `1:45–2:00`
And the `0:00–0:03` beat names `渡劫` + `雷劫` + `剑刺穿`
And the `0:03–0:30` beat encodes 6 betrayer pairs (reasons-to-trust → reasons-to-die)
And the `0:30–1:15` beat names `落雁渊`, `7 岁练气体`, `焚寿罗盘`, and `寿元 -1 / 修为 +1`
And the `1:15–1:45` beat shows the protagonist self-naming `裴知秋` + `闻砚清` 剪影
And the `1:45–2:00` beat carries `第二集 即将揭晓` cliffhanger字幕
And the runtime total (sum of beat durations) is ≤ 8 minutes
And the script contains the five mandatory sections: 集名 / 摘要 / 角色出场 / 场景列表 / 剧本正文
**Severity:** blocker
**Source:** FR-8, NFR-6, NFR-9

### FR-9 — episodes/ep01/shotlist.md

**Scenario: AC-FR9-A — shotlist contains 6–10 shots with mandatory columns**
Given the stage-6 run has emitted the FR-9 deliverable
When `episodes/ep01/shotlist.md` is parsed
Then 6 ≤ shot count ≤ 10 (target 7 per FR-9)
And every row carries: `shot_id`, `时长`, `景别`, `运动`, `主要角色`, `主要 prop`, `主要场景`, `hook summary`, `seam-frame contract`
And every `时长` value satisfies 3 ≤ duration ≤ 15 seconds
And the sum of `时长` ≤ 480 seconds (8-min ceiling)
**Severity:** blocker
**Source:** FR-9, NFR-5, NFR-6, ai_video.md rule 6

**Scenario: AC-FR9-B — exactly one shot is flagged `cover_frame: true` and is the cliffhanger**
Given the parsed shotlist
When the `cover_frame` flag is counted
Then exactly one shot carries `cover_frame: true`
And that same shot is the final shot of the episode (the cliffhanger per FR-8 beat `1:45–2:00`)
**Severity:** blocker
**Source:** FR-9, FR-10.8, NFR-10

### FR-10 — shotNN.md prompt files

**Scenario: AC-FR10-A — every shot in the shotlist has a matching prompt file**
Given the shotlist enumerates N shots
When `episodes/ep01/shots/` is listed
Then exactly N files match `shot[0-9][0-9].md`
And every file pairs 1-to-1 with a shotlist row by `shot_id`
**Severity:** blocker
**Source:** FR-10, ai_video.md rule 12.4

**Scenario: AC-FR10-B — every shot prompt fills the 14-field schema and carries a fenced text block**
Given every `shots/shotNN.md` file
When the body is parsed
Then the fenced ```text``` block contains all 14 fields per ai_video.md rule 12.4 v4
And the `角色:` line carries a one-sentence-lock + 50–80 字 face-differentiator per named character (FR-10.1)
And the `场景:` references a `scenes/{slug}.md` file when the scene is declared, OR is inline-described otherwise (FR-10.2)
And the `动作:` line is timed-beat and the sum of beat durations equals the `时长:` value (FR-10.3, NFR-5)
And the `比例:` field equals `9:16` (NFR-3)
**Severity:** blocker
**Source:** FR-10, NFR-3, NFR-5

**Scenario: AC-FR10-C — 台词 / 字幕 honors the 三选一 contract**
Given every `shots/shotNN.md` file
When the `台词 / 字幕:` block is parsed
Then exactly one of three patterns is declared: `内嵌硬字幕`, `后期软字幕`, or `默剧`
And system 弹窗 / 集头标题 / 黄金钩 lines use `内嵌硬字幕` per FR-10.4
And dialogue lines use `后期软字幕` per FR-10.4
**Severity:** blocker
**Source:** FR-10.4, ai_video.md rule 12.4 三选一

**Scenario: AC-FR10-D — 渲染样式 + 负向 re-pasted from style_guide**
Given every `shots/shotNN.md` file
When the `渲染样式:` and `负向:` blocks are compared against `style_guide.md § 正向关键词` and `§ 负向锁定`
Then `渲染样式:` contains ≤ 9 core positive keywords lifted from the style_guide (FR-10.5)
And `负向:` contains ≤ 24 core negative items lifted from the style_guide (FR-10.6)
And both blocks are byte-identical (modulo whitespace) to the style_guide source
**Severity:** blocker (drift breaks visual consistency)
**Source:** FR-10.5, FR-10.6, NFR-2

**Scenario: AC-FR10-E — shot prompt body length stays within budget**
Given every `shots/shotNN.md` file
When the fenced text body word count is measured (字 count, Chinese characters)
Then ≤ 2500 字 (hard ceiling)
And ≤ 2000 字 triggers no warning; > 2000 字 + ≤ 2500 字 = warning; > 2500 字 = blocker
**Severity:** warning (2000–2500) / blocker (>2500)
**Source:** FR-10.7, NFR-1, ai_video.md rule 12.4 v4

**Scenario: AC-FR10-F — cliffhanger shot prompt carries `cover_frame: true` in shot context**
Given the cliffhanger shot identified in AC-FR9-B
When `shots/shotNN.md` for that shot is read
Then the shot-context block contains an explicit `cover_frame: true` line
**Severity:** blocker
**Source:** FR-10.8, NFR-10

**Scenario: AC-FR10-G — dual-prompt presence + seam-frame stills**
Given every shotlist row
When the prompts directory is checked per ai_video.md rule 4 + rule #11 + validation/ai_video.md rule 4
Then for every shot, a Kling-compatible prompt AND a Seedance-compatible prompt are present (whether as separate files `shotNN_kling.md` + `shotNN_seedance.md` or as labeled blocks inside a single `shotNN.md` — spec FR-10 chooses the consolidated pattern)
And `shots/shotNN_lastframe_seedream.md` (or equivalent embedded block per FR-10's "Seam-frame still prompts as embedded code blocks" clause) is present for every shot
And `shots/shot01_startframe_seedream.md` (or equivalent embedded block) is present for shot01 only
**Severity:** blocker
**Source:** FR-10, ai_video.md rule 4 + rule #11, validation/ai_video.md § Required validation moves #4

### FR-11 — publish.md

**Scenario: AC-FR11-A — publish.md ships the five mandatory sections within length budgets**
Given the stage-6 run has emitted the FR-11 deliverable
When `episodes/ep01/publish.md` is read
Then all five sections are present: `标题`, `简介`, `标签`, `封面建议`, `平台备注`
And `标题` ≤ 30 Chinese characters AND does not spoil the 师父 cliffhanger
And `简介` ≤ 200 Chinese characters AND names the parasitic-cost hook
And `标签` lists 5 ≤ N ≤ 10 hashtags
And `封面建议` references the shot id that carries `cover_frame: true`
And `平台备注` mentions Douyin / 红果 specifics AND marks YouTube Shorts "EN subtitle pass deferred"
**Severity:** blocker
**Source:** FR-11, ai_video.md rule 8, validation/ai_video.md § Required validation moves #6

### FR-12 — copyright_clearance.md

**Scenario: AC-FR12-A — copyright_clearance carries five required sections + sign-off**
Given the stage-6 run has emitted the FR-12 deliverable
When `my_novel/feng_shou_lu/copyright_clearance.md` is read
Then these sections exist: `BLACKLIST table`, `Mozun_chongsheng cross-grep table`, `PROPOSED naming table`, `DELTA report`, `SIGN-OFF section`
And the BLACKLIST table contains every distinctive baseline entity from `findings/angle-baseline_extraction.md §2.5`
And the cross-grep table covers every named entity / location / artifact under `ai_videos/mozun_chongsheng/`
And the PROPOSED naming table lifts the character_anonymization §3 names with WebSearch collision-check column
And the DELTA report has one row per baseline novel + one row for mozun_chongsheng with ≤ 1 字面 carryover justification
And the SIGN-OFF section carries a stage-5 grep-pass timestamp + 0 unresolved blacklist hits
**Severity:** blocker
**Source:** FR-12, AC-5, NFR-4

### FR-13 — Mirror README (already covered by AC-FR1-B)

See AC-FR1-B.

### FR-14 — Audit events

**Scenario: AC-FR14-A — stage 6 emits the required exec + validation events**
Given `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl` after stage-6 completes
When the event log is parsed line-by-line
Then exactly one `exec.unit.started` event exists for the ep01 work unit
And exactly one `exec.unit.completed` event exists for the same work unit
And every validation level emits a `validation.started` + (`validation.pass` OR `validation.issue.raised`) pair
And a single `validation.requires_manual_walkthrough` event is present after all automated levels pass
**Severity:** blocker
**Source:** FR-14, NFR-13, AC-7, validation/general.md principle 5

## 3. NFR rules (measurable assertions)

**Rule: NFR-1 — Shot prompt body length budget**
For every `episodes/ep01/shots/shotNN.md`: fenced text body Chinese-character count ≤ 2500 (hard) / ≤ 2000 (soft). > 2500 = `blocker`; 2000 < count ≤ 2500 = `warning`.
**Severity:** warning / blocker
**Source:** NFR-1

**Rule: NFR-2 — Character descriptor byte-identical across all references**
For every named character in any shot's `角色:` line and in `characters/<name>.md` and in `characters/ref_images/<name>_seedream.md`: the 一句话锁定 + 50–80 字 face-differentiator strings must be byte-identical (modulo whitespace).
**Severity:** blocker
**Source:** NFR-2, validation/ai_video.md § Required validation moves #3

**Rule: NFR-3 — 9:16 aspect ratio declared everywhere**
For every shot prompt and every Seedream ref-image prompt: `比例:` field equals `9:16`. Missing or any other value = `blocker`.
**Severity:** blocker
**Source:** NFR-3, validation/ai_video.md § Required validation moves #5

**Rule: NFR-4 — BLACKLIST + mozun cross-grep gate passes**
grep every named entity (characters, locations, organizations, artifacts) across all stage-6 outputs against (a) the BLACKLIST table in `copyright_clearance.md` and (b) every non-draft `*.md` under `ai_videos/mozun_chongsheng/`. Any hit = `blocker`.
**Severity:** blocker
**Source:** NFR-4

**Rule: NFR-5 — 动作 timed-beat arithmetic**
For every shot prompt: parse the `动作:` line for timed beats (e.g., `0–2s: …`, `2–5s: …`). The sum of beat durations MUST equal the `时长:` field exactly. Mismatch = `blocker`.
**Severity:** blocker
**Source:** NFR-5

**Rule: NFR-6 — ep01 runtime ≤ 8 minutes**
Sum every shot's `时长` in the shotlist. Result ≤ 8 min (480 s) = pass. 8 < result ≤ 10 min = `warning`. > 10 min = `blocker`.
**Severity:** warning / blocker
**Source:** NFR-6

**Rule: NFR-7 — ≤ 5 named characters per shot**
For every shot prompt: parse `角色:` for the count of named characters. > 5 = `warning`.
**Severity:** warning
**Source:** NFR-7

**Rule: NFR-8 — ≤ 6 prop per scene**
For every scene file + every shot prompt's prop list: count distinct prop tokens. > 6 = `warning`.
**Severity:** warning
**Source:** NFR-8

**Rule: NFR-9 — 寄生升级 motif lands in ep01 ≥ 1 time**
grep across ep01 prompts + script for the motif 5-beat signature (e.g., 罗盘浮现 → 红字弹窗 → 寿元 -1 → 修为 +1 → 三拍 顿挫). Zero hits = `blocker`.
**Severity:** blocker
**Source:** NFR-9

**Rule: NFR-10 — Cliffhanger shot exists and is `cover_frame: true`**
See AC-FR9-B. `Rule:` form: shotlist has exactly one row with `cover_frame: true`, and it is the last shot. Missing = `blocker`.
**Severity:** blocker
**Source:** NFR-10

**Rule: NFR-11 — Chinese-content compliance**
For every `*.md` under `my_novel/feng_shou_lu/` and `ai_videos/feng_shou_lu/`: strip code fences, YAML frontmatter, URLs; remaining text ≥ 95% Chinese-block characters (Han + fullwidth punctuation). English content body (non-proper-noun) = `blocker`; mixed (above the 95% bar but with non-proper-noun English fragments) = `warning`.
**Severity:** blocker (English content) / warning (mixed above 95%)
**Source:** NFR-11, validation/ai_video.md § Required validation moves #1

**Rule: NFR-12 — Cross-document references resolve**
For every `[name]` or relative-path link in `*.md` files under `my_novel/feng_shou_lu/`: the referenced file MUST exist. Broken = `blocker`.
**Severity:** blocker
**Source:** NFR-12

**Rule: NFR-13 — validation.requires_manual_walkthrough emitted before done**
See AC-FR14-A. The audit log must contain exactly one `validation.requires_manual_walkthrough` event before `exec.unit.completed`. Missing = `blocker`.
**Severity:** blocker
**Source:** NFR-13, validation/ai_video.md § Required validation moves #8

## 4. Master scenarios per AC (AC-1 through AC-7)

**Scenario: AC-1 — every FR-1 through FR-14 deliverable exists at its specified path with non-empty content**
Given stage 6 declares the ep01 work unit complete
When the deliverable file tree is enumerated against FR-1 through FR-14's file-list
Then every named file exists
And every file is non-empty (≥ 1 byte after whitespace strip)
And all FR-1 through FR-14 sub-scenarios above (AC-FR1-A through AC-FR14-A) pass
**Severity:** blocker
**Source:** AC-1

**Scenario: AC-2 — all NFR-1 through NFR-13 checks pass (warnings allowed; blockers must be resolved)**
Given the NFR `Rule:` set above has run
When results are aggregated per NFR
Then zero NFRs return `blocker`
And any NFRs returning `warning` are logged with rationale
**Severity:** blocker
**Source:** AC-2

**Scenario: AC-3 — user has read script.md end-to-end and confirmed beats land**
Given automated NFR levels have passed
When the parent emits `validation.requires_manual_walkthrough` with the prompt "open script.md and confirm the five beats land"
Then the user responds with explicit confirmation
And the user's response is appended to the audit log as `validation.requires_manual_walkthrough` resolution
**Severity:** blocker
**Source:** AC-3, NFR-13

**Scenario: AC-4 — user has skimmed shot01 prompt and confirmed 14-field schema**
Given AC-3 confirmed
When the parent prompts "open shots/shot01.md and confirm the 14-field schema is filled per ai_video.md rule 12.4"
Then the user responds with explicit confirmation
**Severity:** blocker
**Source:** AC-4

**Scenario: AC-5 — copyright_clearance SIGN-OFF carries timestamp + zero blacklist hits**
Given stage 5's copyright_clearance level has run
When `copyright_clearance.md § SIGN-OFF` is read
Then a stage-5 grep-pass timestamp (ISO-8601) is present
And the unresolved-hits counter equals 0
**Severity:** blocker
**Source:** AC-5, NFR-4

**Scenario: AC-6 — arc_outline.md has all 60 lines including cadence beats**
See AC-FR4-A + AC-FR4-B.
**Severity:** blocker
**Source:** AC-6

**Scenario: AC-7 — validation.requires_manual_walkthrough emitted and acknowledged**
See AC-FR14-A.
**Severity:** blocker
**Source:** AC-7, NFR-13

## 5. Carve-out review (per validation/general.md principle 6)

Each item in spec § Out of scope reviewed for contract drift. Per principle 6, every carve-out must be either confirmed as intentional with no consumer disowned, or flagged as drift with severity.

1. **ep02–60 detailed deliverables.** Intentional carve-out; matches `interview/qa.md` Q11 override (follow-up 001 — MVP = ep01 only) and `arc_outline.md` captures ep02–60 at one-liner depth so cross-episode foreshadowing is correctly planted from ep01 forward (FR-4 contract). No consumer disowned; the 60-ep design intent stays at design depth. **No contract drift.**

2. **Characters debuting after ep01.** Intentional carve-out, consistent with FR-5's 9-character (or 10 — see AC-FR5-A divergence note) ep01 cast. `arc_outline.md` records `乌泽` and any ep02+ named character's existence; their `characters/<name>.md` files arrive in the next iteration. No FR depends on a post-ep01 character bible. **No contract drift.**

3. **Scenes that only appear after ep01.** Intentional carve-out; FR-7 explicitly locks `scenes/` to exactly two files (`s1_无寿崖.md`, `s2_落雁渊.md`). Other ep01 backdrops appearing in single shots stay inline per ai_video.md rule 12.3. AC-FR7-B enforces. **No contract drift.**

4. **English / overseas subtitle pass.** Intentional carve-out; FR-11's `平台备注` marks YouTube Shorts "EN subtitle pass deferred". The `publish.md` reader (= operator) is explicitly told the EN pass is post-v1. **No contract drift.**

5. **Actual video rendering.** Intentional carve-out; spec § User roles & primary production flow names "AI rendering services" as a downstream consumer with the human operator as the driver. No FR depends on rendered video being produced in this run. **No contract drift.**

6. **Audio synthesis (TTS / 配乐).** **Potential contract drift — flagged for stage-4 sign-off.** Spec § Out of scope #6 says "v1 visual-only", and FR-5.3 says "配音参考 stays planning-only — no TTS prompts generated in v1". HOWEVER: FR-10.4 makes `台词 / 字幕` a **first-class field** in every shot prompt, rendered as on-frame subtitles per ai_video.md rule 12.4 三选一 contract. The carve-out is narrower than its surface wording suggests — visuals-only applies to **audio synthesis**, NOT to dialogue text. AC-FR10-C enforces dialogue presence. Spec § Out of scope #6 already captures this narrowing explicitly ("Dialogue ships as on-frame subtitle text…, not as audio prompts"), so the contract is consistent — but the carve-out wording reads ambiguously on first scan. **Recommendation:** sharpen § Out of scope #6 wording at stage-4 sign-off to make the "dialogue YES / audio NO" line unambiguous. **Severity if left ambiguous:** warning (cosmetic clarity); the contract itself is internally consistent.

7. **mozun_chongsheng cross-pollination.** Intentional carve-out; NFR-4 enforces the grep gate AGAINST mozun_chongsheng outputs, which is the inverse of "share with". The grep-gate consumer is stage-5 `copyright_clearance` level. **No contract drift.**

8. **Top-level directory restructure.** Intentional carve-out; landed under `specs/development/ai_video_management/` follow-up 113. No FR in this spec depends on it. **No contract drift.**

**Carve-out review verdict:** 7 of 8 carve-outs are clean intentional scoping. Item 6 has cosmetic wording risk (the "v1 visual-only" phrase reads as banning dialogue text until you read the narrowing parenthetical); recommend a 1-line edit at stage-4 sign-off but no functional contract drift. Severity for the cosmetic item if not patched: `warning`. **No `critical` contract-drift alarms triggered.**

## 6. Severity / source summary table

| Scenario / Rule | Severity | Source |
|---|---|---|
| AC-FR1-A | blocker | FR-1 |
| AC-FR1-B | blocker | FR-1, FR-13 |
| AC-FR2-A | blocker | FR-2 |
| AC-FR3-A | blocker | FR-3, NFR-1 |
| AC-FR4-A | blocker | FR-4, AC-6 |
| AC-FR4-B | blocker | FR-4, AC-6 |
| AC-FR5-A | blocker | FR-5 |
| AC-FR5-B | blocker | FR-5.1, NFR-2 |
| AC-FR5-C | blocker | FR-5.2 |
| AC-FR5-D | warning | FR-5.3 |
| AC-FR5-E | warning / blocker | FR-5.4 |
| AC-FR6-A | blocker | FR-6, NFR-2, NFR-3 |
| AC-FR6-B | blocker | FR-6 |
| AC-FR7-A | blocker | FR-7, NFR-3 |
| AC-FR7-B | warning / blocker | FR-7 |
| AC-FR8-A | blocker | FR-8, NFR-6, NFR-9 |
| AC-FR9-A | blocker | FR-9, NFR-5, NFR-6 |
| AC-FR9-B | blocker | FR-9, NFR-10 |
| AC-FR10-A | blocker | FR-10 |
| AC-FR10-B | blocker | FR-10, NFR-3, NFR-5 |
| AC-FR10-C | blocker | FR-10.4 |
| AC-FR10-D | blocker | FR-10.5, FR-10.6, NFR-2 |
| AC-FR10-E | warning / blocker | FR-10.7, NFR-1 |
| AC-FR10-F | blocker | FR-10.8, NFR-10 |
| AC-FR10-G | blocker | FR-10, validation/ai_video.md #4 |
| AC-FR11-A | blocker | FR-11 |
| AC-FR12-A | blocker | FR-12, AC-5, NFR-4 |
| AC-FR14-A | blocker | FR-14, NFR-13, AC-7 |
| NFR-1 Rule | warning / blocker | NFR-1 |
| NFR-2 Rule | blocker | NFR-2 |
| NFR-3 Rule | blocker | NFR-3 |
| NFR-4 Rule | blocker | NFR-4 |
| NFR-5 Rule | blocker | NFR-5 |
| NFR-6 Rule | warning / blocker | NFR-6 |
| NFR-7 Rule | warning | NFR-7 |
| NFR-8 Rule | warning | NFR-8 |
| NFR-9 Rule | blocker | NFR-9 |
| NFR-10 Rule | blocker | NFR-10 |
| NFR-11 Rule | blocker / warning | NFR-11 |
| NFR-12 Rule | blocker | NFR-12 |
| NFR-13 Rule | blocker | NFR-13 |
| AC-1 master | blocker | AC-1 |
| AC-2 master | blocker | AC-2 |
| AC-3 master | blocker | AC-3 |
| AC-4 master | blocker | AC-4 |
| AC-5 master | blocker | AC-5 |
| AC-6 master | blocker | AC-6 |
| AC-7 master | blocker | AC-7 |

**Totals:**

- **Critical:** 0 (no security / sandbox class for an ai_video text-deliverable run; carve-out review surfaced no contract-drift `critical`).
- **Blocker:** 39 (most scenarios; severe deliverable / consistency gates).
- **Warning:** 8 (NFR-7, NFR-8, some NFR-1 / NFR-6 / NFR-11 / AC-FR5-D / AC-FR5-E / AC-FR7-B / AC-FR10-E variants).
- **Scenarios total:** 47 (28 Gherkin scenarios + 13 NFR `Rule:` assertions + 6 AC master scenarios that reference back into the FR / NFR set, counted as 47 distinct gate checks).

Stage 6's per-work-unit validator runs every blocker scenario to a halt-on-fail outcome and every warning scenario to a log-only outcome; AC-3 and AC-4 require user response via `validation.requires_manual_walkthrough` before `exec.unit.completed` can be emitted.
