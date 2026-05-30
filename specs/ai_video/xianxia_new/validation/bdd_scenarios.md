---
worker_id: level-specialist-02-bdd_scenarios
stage: 5
role: level-specialist
level: bdd_scenarios
status: complete
blockers: []
confidence: high
---

# BDD scenarios — xianxia_new (《焚寿录》 ep01 MVP)

## Scope

Feature-level behaviors for the eight stages of the spec § Primary production flow, grouped so that each `Feature` block describes how a complete production unit behaves end-to-end (contract, not implementation). Each Feature pairs at least one happy-path `Scenario` with at least one alternate / failure `Scenario` per `validation/general.md` principle 1. The acceptance-criteria deliverable (sibling file `acceptance_criteria.md`) carries the mechanical FR-by-FR Gherkin; this file is the **rollup gate** — every Feature names which FR-level criteria roll up to it and which `work_unit_kind` triggers it at stage-6 runtime per the validation playbook stage-6 input contract. Background blocks fix the state shared by all scenarios in a feature so individual scenarios stay tight. Examples tables enumerate parametric variants where a single Scenario covers a family of inputs (character names, beat slots, paid-conversion nodes, etc.).

## Features

### Feature F1 — Project bootstrap (slug rename, top-level files, README mirror)

```gherkin
Feature: Project bootstrap completes the slug rename and lays down top-level scaffolding
  work_unit_kind: project_bootstrap
  Rolls up: FR-1 (README in my_novel/), FR-13 (README mirror in ai_videos/), spec Open Question #1 (title pick)

  Background:
    Given stage 4 has produced specs/ai_video/xianxia_new/final_specs/spec.md
    And spec Open Question #1 lists "feng_shou_lu" as the proposed final slug
    And the user has approved the slug pick at the stage-4 review gate
    And the working folder still lives at specs/ai_video/xianxia_new/

  Scenario: Happy path — full bootstrap with approved slug
    When stage 6 starts the project_bootstrap work unit
    Then specs/ai_video/xianxia_new/ is renamed to specs/ai_video/feng_shou_lu/
    And the folder my_novel/feng_shou_lu/ is created
    And the folder ai_videos/feng_shou_lu/ is created
    And my_novel/feng_shou_lu/README.md exists with H1 "# 《焚寿录》— AI 视频项目"
    And the README contains the four required sections 项目概要 / 使用说明 / 角色清单 / 风格关键词
    And ai_videos/feng_shou_lu/README.md mirrors the same four sections
    And both README files contain only Chinese in the body (English allowed only for proper nouns Kling / Seedance / Seedream and the slug token)
    And the audit log emits exec.unit.started + exec.unit.completed for project_bootstrap

  Scenario: Failure — user defers the slug pick at the review gate
    Given the user has chosen "defer" instead of approving "feng_shou_lu"
    When stage 6 attempts to start the project_bootstrap work unit
    Then the work unit halts with pipeline.halted reason "slug_unresolved"
    And no rename of specs/ai_video/xianxia_new/ occurs
    And no my_novel/ or ai_videos/ folder is created
    And the user is prompted to resolve Open Question #1 before proceeding

  Scenario: Failure — README mirror is missing or off-spec
    Given my_novel/feng_shou_lu/README.md is correctly authored
    But ai_videos/feng_shou_lu/README.md is missing the 角色清单 section
    When the bootstrap validator runs
    Then a validation.issue.raised event fires with severity "blocker"
    And the issue cites FR-13 mirror requirement
    And the work unit does not transition to completed
```

### Feature F2 — Character bible production

```gherkin
Feature: Character bibles + Seedream立绘 prompts ship as a coherent 9-bible / 10-prompt bundle
  work_unit_kind: character_bible
  Rolls up: FR-5 (9 bibles + sub-requirements FR-5.1 through FR-5.4), FR-6 (10 Seedream立绘 prompts), NFR-2 (byte-identical descriptor reuse), ai_video.md rule 12.1 / 12.2

  Background:
    Given world.md and style_guide.md have been written (F3 done)
    And the dossier's character_anonymization §3 names are pinned (裴知秋, 裴长砚, 闻砚清, 容漪, 卫长烛, 应砚之, 戚归砚, 池洇, 阮惘, 言息)
    And the 6-faction palette + 双形态契约 are locked in style_guide.md

  Scenario: Happy path — all 9 bibles + 10 Seedream prompts pass schema and uniqueness
    When stage 6 produces character_bible work units for all 9 named characters
    Then each my_novel/feng_shou_lu/characters/<name>.md follows ai_video.md rule 12.1 schema
    And each bible carries the 10-field 锁定描述符表 + 性格 + 动机 + 弧光 + 标志台词 + 关键场景 + 标志能力 + 配音参考 + 负向
    And each bible ends with a single 「词源」line citing the dossier etymology (FR-5.2)
    And 裴知秋.md carries TWO sets of 10-field 锁定描述符 labeled "state A: 重生弱体" and "state B: 寄生觉醒" (FR-5.1)
    And both 裴知秋 states share the byte-identical "左眼下方 0.3cm 灰青胎记" face differentiator
    And exactly 10 Seedream prompts exist under characters/ref_images/ (8 single + 2 for the 双形态主角)
    And each Seedream prompt declares 比例 9:16 + 4K
    And each Seedream prompt's 负向 re-pastes style_guide.md § 负向锁定 verbatim
    And the audit log emits validation.pass for character_bible after all 9 work units complete

  Scenario Outline: Happy path examples — every named character resolves to a bible + ref-image
    When stage 6 writes the bible for <name>
    Then characters/<name>.md exists with a non-empty 锁定描述符表
    And characters/ref_images/<name>_seedream.md exists with the 9:16 / 4K declaration
    And the bible's 词源 line cites dossier character_anonymization §3.<section>

    Examples:
      | name     | section | role                              |
      | 裴知秋   | 3.1     | 主角 本世 (双形态)                |
      | 裴长砚   | 3.1     | 主角 前世 (archived 档案)         |
      | 闻砚清   | 3.1     | 师父                              |
      | 容漪     | 3.1     | 主女主 (ep01 cameo only)          |
      | 卫长烛   | 3.2     | 正派背叛者 #1                     |
      | 应砚之   | 3.2     | 正派背叛者 #2                     |
      | 戚归砚   | 3.2     | 散修背叛者 #3                     |
      | 池洇     | 3.2     | 散修背叛者 #4                     |
      | 阮惘     | 3.2     | 魔门背叛者 #5                     |
      | 言息     | 3.2     | 魔门 BOSS 背叛者 #6               |

  Scenario: Failure — descriptor drift between two state-A and state-B references
    Given 裴知秋.md state-A descriptor cites the 胎记 at "左眼下方 0.3cm"
    But 裴知秋.md state-B descriptor cites the 胎记 at "左眼下方 0.4cm"
    When the character_bible validator runs
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-2 + FR-5.1 shared face-differentiator requirement
    And no character_bible work unit transitions to validation.pass until the drift is reconciled

  Scenario: Failure — Seedream prompt count off by one
    Given 9 character bibles exist
    But only 9 Seedream立绘 prompts exist (主角 has only 1 prompt instead of the required 2)
    When the validator counts files under characters/ref_images/
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-6 (≥ 10 Seedream prompts) + FR-5.1 (双形态主角)
```

### Feature F3 — World + style guide production

```gherkin
Feature: world.md and style_guide.md establish the canonical universe and visual contract
  work_unit_kind: world_and_style
  Rolls up: FR-2 (world.md 5 sections), FR-3 (style_guide.md 6 mandatory subsections), NFR-9 (寄生升级 motif), ai_video.md rule 12.4 v4 dependency

  Background:
    Given the dossier R-2, R-3, and visual_style §3 are pinned
    And the cultivation ladder terminal stage is locked to 大乘 (spec Open Question #2)
    And mozun_chongsheng palette is locked to 黑/金/紫霄/朱砂 (for orthogonality)

  Scenario: Happy path — world.md carries all 5 sections in lock order
    When stage 6 writes my_novel/feng_shou_lu/world.md
    Then section 1 declares the 8-stage ladder 练气-筑基-金丹-元婴-化神-炼虚-合体-大乘 verbatim
    And section 2 documents the parasitic-system divergence (lifespan + memory cost per level-up)
    And section 3 lists all three faction blocks (正派联盟 / 散修盟 / 魔门) with founding myth + head figure + politics + visual
    And section 4 declares 澹江洲 / 落雁渊 / 栖梧崖 (and the 旧名「无寿崖」 reveal note)
    And section 5 captures the FULL parasitic-system in-fiction truth across the ep17 / ep30 / ep49 / ep50 / ep60 reveal stages
    And the file body is entirely Chinese (folder names + proper nouns excepted)

  Scenario: Happy path — style_guide.md ships all 6 mandatory subsections
    When stage 6 writes my_novel/feng_shou_lu/style_guide.md
    Then the file contains the 镜头语言关键词字典 (13 景别 + 9 运动)
    And the file contains the 12-state 光影词典 (mozun's 10 + 寄生 aura #4a1a5a + 寿命流失 #a82c2c)
    And the file contains the 6-faction 调色板 with 主/辅/点缀 hex + ≥ 3 web visual citations each
    And the file contains the 字幕规范 mapping to the 三选一 contract (内嵌硬 / 后期软 / 默剧)
    And the file contains the 转场词典 9 类 including the project-unique 寿命计数器过
    And the file contains the 负向锁定 block with ≥ 24 mozun baseline + 12 project-specific items
    And the 寄生升级 motif 五拍 signature is documented for stage-6 shot prompts to re-paste

  Scenario: Failure — terminal stage cadence collision
    Given world.md section 1 declares the ladder ending in 渡劫 instead of 大乘
    When the world_and_style validator runs
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites spec Open Question #2 lock + dossier CCI-1 cadence-echo avoidance vs wode_moni_changsheng_lu

  Scenario: Failure — style_guide.md missing a mandatory subsection
    Given style_guide.md is missing the 字幕规范 subsection
    When the validator audits style_guide.md against FR-3 + ai_video.md rule 12.4 v4
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-3 sub-requirement list (6/6 required)
    And the work unit cannot proceed to F5 / F6 (which depend on the 字幕规范 三选一 contract)
```

### Feature F4 — Arc outline production (60 episodes one-liner)

```gherkin
Feature: arc_outline.md captures all 60 episodes with the locked cadence beats at their assigned slots
  work_unit_kind: arc_outline
  Rolls up: FR-4 (60 lines + cadence-beat table), AC-6 (arc_outline completeness), dossier R-6 reveal cadence

  Background:
    Given world.md and the 9 character bibles are in place
    And the dossier R-6 cadence beat table is pinned (ep01 / ep08 / ep10 / ep17 / ep20 / ep28 / ep30 / ep35 / ep49 / ep50 / ep60)
    And the paid-conversion nodes are locked at ep10 (70%), ep30 (25%), ep50 (5%), ep60 (season-end)

  Scenario: Happy path — 60 lines with cadence beats at correct slots
    When stage 6 writes my_novel/feng_shou_lu/arc_outline.md
    Then exactly 60 lines numbered ep01 through ep60 exist
    And each line follows the pattern "### epNN — {title} — {hook} — {one-line synopsis}"
    And each one-line synopsis is ≤ 40 字 Chinese
    And the 10 cadence-beat episodes carry their assigned beats verbatim from FR-4 table

  Scenario Outline: Happy path examples — cadence beat lands at the assigned episode
    When the validator reads arc_outline.md line for ep<N>
    Then the line contains the substring "<expected_beat_token>"

    Examples:
      | N  | expected_beat_token                                     |
      | 01 | 死亡开局                                                |
      | 01 | 系统觉醒                                                |
      | 01 | 裴知秋                                                  |
      | 08 | 归砚镜                                                  |
      | 10 | 付费节点 1                                              |
      | 10 | 卫长烛                                                  |
      | 17 | 裴长砚                                                  |
      | 20 | 偿岁真言                                                |
      | 28 | 容漪                                                    |
      | 30 | 付费节点 2                                              |
      | 35 | 长烟幡                                                  |
      | 49 | 归砚镜拼回                                              |
      | 50 | 付费节点 3                                              |
      | 60 | 季终                                                    |

  Scenario: Failure — cadence beat missing or mis-placed
    Given arc_outline.md has 60 lines
    But ep10's line does NOT contain "付费节点 1"
    When the arc_outline validator runs
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-4 cadence-beat table row for ep10
    And the issue recommends inserting the missing token before the work unit re-validates

  Scenario: Failure — line count off
    Given arc_outline.md has only 58 numbered ep lines
    When the validator counts numbered headers
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-4 + AC-6
```

### Feature F5 — Scene production (2 scenes + 2 立绘)

```gherkin
Feature: scenes/ ships exactly two locked-down ep01 scenes with paired Seedream立绘 prompts
  work_unit_kind: scene_pack
  Rolls up: FR-7 (2 scenes + 2 立绘 prompts), ai_video.md rule 12.3

  Background:
    Given style_guide.md is in place (F3 done) for negative-prompt re-paste
    And the spec § Out of scope rule 3 limits this run's scenes/ to exactly two files

  Scenario: Happy path — both scene files + both Seedream prompts pass schema
    When stage 6 writes scenes/s1_无寿崖.md and scenes/s2_落雁渊.md
    Then each file contains the 8-field 锁定描述符表 per ai_video.md rule 12.3
    And s1_无寿崖.md declares 关键变化态 covering 雷劫态 + 静默态
    And s2_落雁渊.md declares 关键变化态 covering 黎明态 + 夜态
    And both files contain the 出现镜头表 (forward-filled once shotlist exists)
    And both files end with a 负向 block re-pasting style_guide.md § 负向锁定
    And scenes/ref_images/s1_无寿崖_seedream.md exists with 比例 9:16 + 4K
    And scenes/ref_images/s2_落雁渊_seedream.md exists with 比例 9:16 + 4K

  Scenario: Failure — a third scene file leaks in (scope creep)
    Given the spec § Out of scope rule 3 limits scenes/ to two files
    When stage 6 writes scenes/s3_朝堂.md (a montage flash backdrop that should be inline)
    Then validation.issue.raised fires with severity "warning"
    And the issue cites ai_video.md rule 12.3 (declare scene only on ≥ 2-shot reuse) + spec § Out of scope rule 3
    And the validator recommends inlining the 朝堂 backdrop in its single shot prompt instead

  Scenario: Failure — scene declared but unreferenced in shotlist
    Given scenes/s1_无寿崖.md exists with an empty 出现镜头表
    When stage 6 episode_full work unit has completed shotlist.md
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-7 forward-fill requirement
    And the issue notes that an undeclared 出现镜头 list breaks the cross-shot consistency contract
```

### Feature F6 — Episode 1 production (script + shotlist + per-shot prompts + publish)

```gherkin
Feature: ep01 ships a coherent script + shotlist + per-shot prompts + publish bundle
  work_unit_kind: episode_full
  Rolls up: FR-8 (script), FR-9 (shotlist), FR-10 (per-shot prompts FR-10.1 through FR-10.8), FR-11 (publish.md), NFR-1 / NFR-3 / NFR-5 / NFR-6 / NFR-7 / NFR-9 / NFR-10, AC-1 through AC-4

  Background:
    Given F1–F5 work units have all reached validation.pass
    And the 9 character bibles + 2 scene files + style_guide.md are in place
    And the dossier R-4 ep01 beat structure is pinned (0:00–0:03 / 0:03–0:30 / 0:30–1:15 / 1:15–1:45 / 1:45–2:00)

  Scenario: Happy path — script + shotlist + 7 shot prompts + publish all schema-clean
    When stage 6 writes episodes/ep01/script.md
    Then the script carries 集名 + 摘要 + 角色出场 + 场景列表 + 剧本正文
    And the script's beats reproduce the R-4 5-beat structure
    And the total runtime is ≤ 8 minutes
    When stage 6 writes episodes/ep01/shotlist.md
    Then exactly 7 shots are listed (target per FR-9; 6–10 acceptable)
    And each shot row carries shot_id + 时长 + 景别 + 运动 + 主要角色 + 主要 prop + 主要场景 + hook summary + seam-frame contract
    And every shot's 时长 is between 3 and 15 seconds inclusive
    And exactly one shot carries cover_frame: true (the cliffhanger shot)
    When stage 6 writes episodes/ep01/shots/shot01.md through shot07.md
    Then each shot prompt body (fenced text only) is ≤ 2500 字 hard / target ≤ 2000 字 soft
    And each shot declares 比例 9:16
    And each shot's 动作 timed beats sum exactly to the shot's 时长
    And each shot's 角色 line re-pastes the locked Chinese descriptor byte-identical from characters/<name>.md
    And each shot's 渲染样式 re-pastes ≤ 9 core keywords from style_guide.md § 正向关键词
    And each shot's 负向 re-pastes ≤ 24 core items from style_guide.md § 负向锁定
    And the 寄生升级 motif 五拍 signature appears in at least one shot (NFR-9)
    And shot01.md carries the startframe Seedream still per ai_video.md rule 12.4 v2/v7
    And every shot ships a lastframe Seedream still
    When stage 6 writes episodes/ep01/publish.md
    Then 标题 ≤ 30 字 + 简介 ≤ 200 字 + 5–10 hashtags + 封面建议 referencing the cover_frame shot
    And 平台备注 covers Douyin / 红果 / YouTube Shorts (YT Shorts marked "EN subtitle pass deferred")

  Scenario Outline: Happy path examples — each beat-slot has the right narrative content
    When the validator parses script.md beat at <time_slot>
    Then the beat contains the substring "<required_token>"

    Examples:
      | time_slot   | required_token                                          |
      | 0:00–0:03   | 雷劫                                                    |
      | 0:00–0:03   | 剑刺穿                                                  |
      | 0:03–0:30   | 倒叙                                                    |
      | 0:30–1:15   | 焚寿罗盘                                                |
      | 0:30–1:15   | 寿元 -1                                                 |
      | 1:15–1:45   | 裴知秋                                                  |
      | 1:15–1:45   | 闻砚清 剪影                                             |
      | 1:45–2:00   | cliffhanger                                             |

  Scenario: Failure — shot 时长 exceeds 15 s
    Given episodes/ep01/shotlist.md row for shot03 declares 时长: 18 s
    When the episode_full validator runs
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites ai_video.md rule 6 + validation/ai_video.md move #2 (15-second shot atomicity)
    And the issue's hint suggests splitting shot03 into two shots with a seam-frame token

  Scenario: Failure — runtime exceeds the hard ceiling
    Given the sum of all 时长 fields in shotlist.md is 11:30 (over the 8-minute hard ceiling per NFR-6)
    When the validator sums durations
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-6 + qa.md Q4

  Scenario: Failure — character descriptor drift between two shot prompts
    Given shot02.md inlines 裴知秋 state-A descriptor as one variant
    But shot05.md inlines 裴知秋 state-A descriptor with even minor wording drift
    When the validator byte-compares descriptors across all shot prompts referencing the same character/state
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-2 + validation/ai_video.md move #3 (character-visual-consistency)

  Scenario: Failure — cover_frame missing or unflagged
    Given the cliffhanger shot exists in shotlist.md
    But no shot row carries cover_frame: true
    When the validator scans for the cover frame
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-10.8 + NFR-10

  Scenario: Failure — 寄生升级 motif absent from ep01
    Given no shot prompt in episodes/ep01/shots/ contains the 五拍 寄生升级 motif tokens
    When the validator greps for the motif signature
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-9 (load-bearing differentiator per dossier CCI-2)

  Scenario: Failure — publish.md missing the cover_frame link
    Given episodes/ep01/publish.md carries 标题 + 简介 + 标签 + 平台备注
    But 封面建议 is absent or references a shot that does not carry cover_frame: true
    When the publish validator runs
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites FR-11 + ai_video.md rule 8

  Scenario: Manual walkthrough — narrative beats land
    Given all automated levels for the ep01 work unit have passed
    When the parent emits validation.requires_manual_walkthrough
    Then the user is prompted to read episodes/ep01/script.md end-to-end (AC-3)
    And the user is prompted to skim at least one shot prompt — recommended shot01.md (AC-4)
    And the work unit only transitions to completed once the user has acknowledged
```

### Feature F7 — Copyright clearance

```gherkin
Feature: copyright_clearance.md proves zero字面 carryover from baseline corpus and zero collision with mozun_chongsheng
  work_unit_kind: copyright_clearance
  Rolls up: FR-12 (BLACKLIST + cross-grep + naming + DELTA + SIGN-OFF), NFR-4 (auto-grep gate), AC-5 (grep-pass timestamp), dossier CCI-1

  Background:
    Given the dossier baseline_extraction §2.5 BLACKLIST table is pinned
    And ai_videos/mozun_chongsheng/ outputs are present on disk
    And every named entity in this project has been web-checked per dossier character_anonymization §3
    And the 3 empty baseline novel folders (cong_jianshu_xiuxing / gou_zai_xiuxianjie / zhutian_daozu) are acknowledged in spec Open Question #3

  Scenario: Happy path — all four tables present and grep gate clean
    When stage 6 writes my_novel/feng_shou_lu/copyright_clearance.md
    Then the file contains a BLACKLIST table sourced from baseline_extraction §2.5
    And the file contains a Mozun_chongsheng cross-grep table covering all named entities from that sibling project
    And the file contains a PROPOSED naming table with etymology + WebSearch collision result per name
    And the file contains a DELTA report per baseline novel + mozun_chongsheng with ≤ 1 字面 carryover justification
    When the auto-grep validator runs the BLACKLIST + mozun cross-grep against all stage-6 outputs under my_novel/feng_shou_lu/ and ai_videos/feng_shou_lu/
    Then zero blacklist hits are found
    And the SIGN-OFF section is populated with the grep-pass timestamp
    And the audit log emits validation.pass for copyright_clearance

  Scenario: Failure — blacklist hit
    Given baseline_extraction §2.5 blacklists 天玄镜 (from wode_moni_changsheng_lu)
    But episodes/ep01/shots/shot04.md contains the literal string "天玄镜"
    When the auto-grep validator runs
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-4 + dossier CCI-1 forbidden-zone for wode_moni 字面 carryover
    And the work unit cannot transition to completed until the offending token is renamed
    And the SIGN-OFF section is NOT timestamped

  Scenario: Failure — mozun cross-grep collision
    Given mozun_chongsheng has a character named 苍冥
    But our 阮惘 bible accidentally references the surname 苍 in a 词源 line
    When the cross-grep validator scans for mozun-character-name occurrences
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-4 + dossier CCI-4 palette/character orthogonality contract
```

### Feature F8 — Stage-6 work-unit validation orchestration (audit events)

```gherkin
Feature: Stage 6 emits the required audit events for every work unit so the pipeline is replayable
  work_unit_kind: audit_orchestration (meta — applies to every other work_unit_kind)
  Rolls up: FR-14 (audit events), NFR-13 (manual walkthrough before done), AC-7 (user ack), CLAUDE.md § Event stream + § Tool scoping pre-reading contract, validation/general.md principle 5

  Background:
    Given the run task_id is xianxia_new-20260524-101931
    And the audit file lives at .audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl
    And the parent has pre-read the stage playbooks + agent_refs for stage 6 per CLAUDE.md pre-reading contract

  Scenario: Happy path — full event lifecycle for a single work unit
    When stage 6 starts the episode_full work unit for ep01
    Then events.jsonl appends exec.unit.started with work_unit_kind: episode_full
    And the same line carries the pre_reading_consulted array of absolute paths (non-empty per CLAUDE.md pre-reading contract)
    When the parent dispatches the level-specialist validators (acceptance_criteria + bdd_scenarios + character_consistency + copyright_grep + storyteller_dialogue_master)
    Then each validator emits validation.started with its level name
    And on pass, each validator emits validation.pass
    And on issue, each validator emits validation.issue.raised with severity + cited contract
    When all automated levels pass
    Then the parent emits validation.requires_manual_walkthrough with the manual-review prompt
    When the user acknowledges (AC-7)
    Then the parent emits exec.unit.completed
    And events.jsonl is append-only and parseable line-by-line as JSON

  Scenario: Happy path — pre-reading array populated on every coordinated stage start
    When stage 6 begins any work_unit_kind from the dispatch table
    Then the first event for that work unit's validation.started carries a pre_reading_consulted array of ≥ 4 absolute paths
    And the array contains the stage-6 playbook + agent_refs/validation/general.md + agent_refs/validation/ai_video.md + agent_refs/project/ai_video.md

  Scenario: Failure — manual walkthrough skipped
    Given all automated validators have emitted validation.pass for ep01
    But the parent emits exec.unit.completed without an intervening validation.requires_manual_walkthrough event
    When the audit-event validator scans events.jsonl
    Then validation.issue.raised fires with severity "blocker"
    And the issue cites NFR-13 + AC-7 + validation/ai_video.md move #8
    And the work unit's "completed" status is rolled back pending the manual walkthrough

  Scenario: Failure — empty pre_reading_consulted array
    Given the parent has emitted validation.started for the episode_full work unit
    But pre_reading_consulted on that event is an empty array
    When the audit validator scans the event line
    Then validation.issue.raised fires with severity "critical"
    And the issue cites CLAUDE.md § Stage playbooks and reference docs (missing pre-reading is a critical failure)
    And the pipeline halts with pipeline.halted

  Scenario: Failure — issue raised but no revision applied within iteration bound
    Given validation.issue.raised has fired three times for the same shot prompt in the episode_full work unit
    But no exec.revision.applied event has resolved the issue
    When the iteration-bound monitor checks the audit stream
    Then pipeline.halted fires per CLAUDE.md § Iteration bounds (3-round cap)
    And the user is escalated to with the summary of unresolved issues
```

## Rollup matrix

Maps each Feature to the FR-level (and NFR / AC) acceptance-criteria scenarios that contribute to it. Read this matrix as: "if every Feature passes, every FR is covered by at least one Feature".

| Feature | Contributing FR / NFR / AC                                                                                                  | Notes |
|---------|----------------------------------------------------------------------------------------------------------------------------|-------|
| F1 — Project bootstrap | FR-1, FR-13, spec Open Question #1                                                                                | Slug rename gate; both READMEs must mirror. |
| F2 — Character bible production | FR-5 (incl. FR-5.1 / FR-5.2 / FR-5.3 / FR-5.4), FR-6, NFR-2, NFR-11 (Chinese body)                            | 9 bibles + 10 Seedream prompts; 双形态主角 is the only character producing 2 立绘. |
| F3 — World + style guide | FR-2, FR-3, NFR-9, NFR-11, spec Open Question #2 (大乘 lock)                                                           | F3 is the gate for F5 / F6 because 字幕规范 三选一 + 负向锁定 + 寄生升级 motif feed every downstream prompt. |
| F4 — Arc outline | FR-4, AC-6, dossier R-6 cadence beats                                                                                       | Cadence beats are 10 of the 60 lines; remaining 49 lines are content-validated as ≤ 40 字 Chinese. |
| F5 — Scene production | FR-7 (2 scenes + 2 Seedream prompts), ai_video.md rule 12.3                                                            | Only 2 scenes this run; other backdrops stay inline per spec § Out of scope rule 3. |
| F6 — Episode 1 production | FR-8, FR-9, FR-10 (FR-10.1 through FR-10.8), FR-11, NFR-1, NFR-3, NFR-5, NFR-6, NFR-7, NFR-9, NFR-10, AC-1, AC-2, AC-3, AC-4 | The biggest feature — single work unit covers script + shotlist + 7 shot prompts + publish.md + manual walkthrough. |
| F7 — Copyright clearance | FR-12, NFR-4, AC-5, dossier CCI-1                                                                                       | Auto-grep gate runs at F7 close; blacklist hit cannot escape to AC-1 sign-off. |
| F8 — Audit orchestration | FR-14, NFR-13, AC-7, CLAUDE.md § Event stream                                                                          | Meta-feature; every other feature emits the prescribed audit events while running. |

**Coverage check:**

- FR-1 → F1.
- FR-2 → F3.
- FR-3 → F3.
- FR-4 → F4.
- FR-5 (incl. FR-5.1–FR-5.4) → F2.
- FR-6 → F2.
- FR-7 → F5.
- FR-8 → F6.
- FR-9 → F6.
- FR-10 (incl. FR-10.1–FR-10.8) → F6.
- FR-11 → F6.
- FR-12 → F7.
- FR-13 → F1.
- FR-14 → F8.

14 of 14 FRs covered (100%). Every FR has at least one Feature with both a happy-path Scenario and a failure Scenario.

NFR coverage:

- NFR-1 → F6.
- NFR-2 → F2, F6.
- NFR-3 → F6.
- NFR-4 → F7.
- NFR-5 → F6.
- NFR-6 → F6.
- NFR-7 → F6 (implicit in shot prompts).
- NFR-8 → F5, F6 (scene + shot scrubbed).
- NFR-9 → F3 (motif documented), F6 (motif used).
- NFR-10 → F6.
- NFR-11 → F1, F2, F3, F4, F5, F6 (Chinese-body rule applies to every file).
- NFR-12 → F2, F5, F6 (cross-document links checked when bibles / scenes / shots cross-reference).
- NFR-13 → F6, F8.

13 of 13 NFRs covered. AC-1 through AC-7 all mapped via F1–F8.

## Work-unit-kind dispatch

Maps each stage-6 `work_unit_kind` (per validation playbook stage 6 input contract) to the Feature(s) that gate it. The parent reads this dispatch table at runtime to decide which Features' Scenarios to run as the level-specialist validators against each work unit.

| work_unit_kind         | Gating features                                | Notes |
|------------------------|-----------------------------------------------|-------|
| project_bootstrap      | F1                                             | First work unit; produces folders + READMEs. Slug rename and dual-README mirror gated here. |
| character_bible        | F2 (per-character) + F8 (audit)               | One work unit per character (9 total); validator dispatches F2 Scenario Outline for the specific name. |
| world_and_style        | F3 + F8 (audit)                                | Single work unit producing world.md and style_guide.md together (they cross-reference). |
| arc_outline            | F4 + F8 (audit)                                | Single work unit; validator checks all 60 lines + cadence beats. |
| scene_pack             | F5 + F8 (audit)                                | Single work unit producing 2 scene files + 2 Seedream prompts. |
| episode_full           | F6 + F8 (audit) + F7 (copyright sub-gate)     | The biggest work unit. F7 runs as a sub-gate inside F6's close (any blacklist hit in any new file blocks the episode close). |
| copyright_clearance    | F7 + F8 (audit)                                | Runs as its own work unit AFTER episode_full to populate the SIGN-OFF timestamp. F7 also runs as a continuous sub-gate during episode_full so blocking issues surface early. |
| audit_orchestration    | F8 (meta-validator)                            | Not a "produces files" work unit — runs continuously as the parent's event-emission contract. F8 Scenarios fire whenever any other work_unit_kind starts, validates, or completes. |

Dispatch sequencing (intended order, derived from spec § Primary production flow):

1. `project_bootstrap` (F1)
2. `world_and_style` (F3) — required input for F2 + F5 + F6
3. `character_bible` × 9 (F2) — parallel-safe; F2 Scenario Outline runs once per name
4. `scene_pack` (F5)
5. `arc_outline` (F4) — parallel-safe with F2 / F5
6. `episode_full` (F6) — depends on F2 / F3 / F5 outputs; F7 sub-gate runs continuously
7. `copyright_clearance` (F7) — standalone close; SIGN-OFF timestamp written here
8. `audit_orchestration` (F8) — runs throughout; closes with the manual walkthrough acknowledgement (AC-7)

Each work unit's `validation.started` event carries the `pre_reading_consulted` array per F8 Scenario "pre-reading array populated on every coordinated stage start" — empty array = `critical` halt.
