# Spec — 《焚寿录》 (working title; see Open Question #1)

**task_type:** ai_video · **sub_type:** novel · **genre:** xianxia
**Working spec-folder slug:** `xianxia_new` → **proposed final slug:** `feng_shou_lu` (matches the working-title pick; switches on user approval per Open Question #1)
**Run:** `xianxia_new-20260524-101931`
**MVP scope:** ep01 only (per follow-up 001 — iterative cadence)
**Composed from:** `user_input/revised_prompt.md` + `interview/qa.md` + `findings/dossier.md` + follow-up 001

---

## Goal

Author an original xianxia (仙侠) short-drama series 《焚寿录》, MVP-shipped one episode at a time. The novel uses the 14 baseline downloaded xianxia novels as a corpus from which structural common elements are extracted and re-mixed without字面 carryover, while every distinctive entity is renamed via the dossier's web-verified naming table. The central conceit is a parasitic system that costs the protagonist lifespan and memory per cultivation level-up — the first cross-corpus differentiator (no 2025–2026 hit ships this mechanic) — paired with a 重生复仇 protagonist who chooses what to spend the dwindling lifespan on. Final output is a multi-episode Chinese-language vertical 9:16 short-drama (60 episodes planned; **only ep01 produced in this run**, with the remaining 59 captured at one-line outline depth in `arc_outline.md` so cross-episode foreshadowing is correctly planted from ep01 forward).

## Out of scope (MVP / this run)

1. **ep02–60 detailed deliverables.** No script, shotlist, shot prompts, or scene files for ep02–60 in this run. The next iteration (after ep01 user review) will land ep02 via a stage-4 regen.
2. **Characters debuting after ep01.** 灵兽乌泽 (ep05 debut per dossier R-6) and any ep02+ named character that does NOT appear in ep01's 0:03–0:30 betrayal montage do not get a `characters/{name}.md` file in this run. Their existence is recorded in `arc_outline.md` only.
3. **Scenes that only appear after ep01.** `scenes/` directory contains exactly two files this run: `s1_无寿崖.md` and `s2_落雁渊.md`.
4. **English / overseas subtitle pass.** YouTube Shorts was selected as a platform (qa.md Q13) but the EN-subtitle pass is a post-v1 follow-up. ep01 ships Chinese-only.
5. **Actual video rendering.** This task produces *prompt files* and *plan files* — no Kling/Seedance/Seedream API calls. The human operator drives the AI tools downstream of this spec.
6. **Audio synthesis (TTS / 配乐) only.** v1 visual-only applies to AUDIO synthesis — no TTS prompts, no music selection. Dialogue text itself remains a FIRST-CLASS shot field per ai_video.md rule 12.4 三选一 contract (内嵌硬字幕 / 后期软字幕 / 默剧); dialogue ships as on-frame subtitle text, not silenced. The carve-out is audio-only.
7. **mozun_chongsheng cross-pollination.** This is a separate project — no shared characters, no shared scenes, no shared Seedream ref-images. Stage-5 copyright clearance has a grep gate against `ai_videos/mozun_chongsheng/` outputs.
8. **Top-level directory restructure.** Already landed under `specs/development/ai_video_management/` follow-up 113 — out of scope here.

## User roles & primary production flow

### Roles

- **Author / director (Claude).** Produces every text artifact under `my_novel/{slug}/` + `ai_videos/{slug}/` per this spec. Strong-typed deliverable list; each file's structure conforms to a rule in `.claude/agent_refs/project/ai_video.md`.
- **Human operator (the user).** Reviews each stage gate. After stage 6 ships ep01 deliverables, drives Seedream → Kling/Seedance → 剪映 to render the actual video. The operator is also the iteration trigger for ep02+.
- **AI rendering services.** Seedream (character立绘 + scene立绘 + 静帧 seam frames), Kling 2.1+ Pro (image-to-video with chars-reel reference), Seedance 1.0+ Pro (text-to-video, longer clips). Each service has a model-agnostic prompt schema per ai_video.md rule 12.4 v2/v4.
- **Viewer.** Douyin / 红果 / YouTube Shorts audience — male-skewing xianxia 短剧 fans, 1–2 min/episode appetite, paid-conversion driven by cliffhanger cadence.

### Primary production flow (MVP — ep01 only)

```
stage 4 (this stage)
└─ writes final_specs/spec.md  ← you are here

stage 5
└─ writes validation/strategy.md + per-level files
   covering: copyright clearance · genre fidelity · short-drama feasibility ·
             hook/retention · internal consistency

stage 6 (the actual production work)
├─ writes my_novel/feng_shou_lu/
│   ├─ README.md
│   ├─ world.md
│   ├─ style_guide.md
│   ├─ arc_outline.md                              ← 60 episodes at one-liner depth
│   ├─ characters/{name}.md                        ← 9 character bibles (ep01 cast)
│   ├─ characters/ref_images/{name}_seedream.md    ← 9 Seedream立绘 prompts
│   ├─ scenes/s1_无寿崖.md, s2_落雁渊.md
│   ├─ scenes/ref_images/{scene}_seedream.md       ← 2 scene立绘 prompts
│   ├─ episodes/ep01/script.md
│   ├─ episodes/ep01/shotlist.md
│   ├─ episodes/ep01/shots/shotNN.md             ← per-shot self-contained prompts
│   ├─ episodes/ep01/publish.md
│   └─ copyright_clearance.md
├─ each work unit gets a streaming validation pass from stage 5's strategy
└─ after ep01 ships → user review → iterate → ep02 in next run

operator workflow (out of this spec; documented for context)
├─ render character turntables (Seedream → Kling turntable.mp4)
├─ render scenes (Seedream PNG)
├─ render seam frames (Seedream PNG)
├─ render shots (Kling image-to-video + Seedance text-to-video)
└─ 剪辑 + 字幕叠加 + 发布
```

## Functional requirements

All FR paths assume the final slug `feng_shou_lu` per Open Question #1; if the title pick changes, every `feng_shou_lu` in this section is replaced consistently and ONLY here (no other artifact carries the slug verbatim — the spec is the source of truth).

### FR-1 — README

- `my_novel/feng_shou_lu/README.md` first line = `# 《焚寿录》— AI 视频项目`.
- Chinese-only content; contains: 项目概要 (one paragraph) · 使用说明 (this file → that file → which tool consumes which) · 角色清单 (9 entries linking to characters/) · 风格关键词 (one-line lift from style_guide.md).
- Same conventions for `ai_videos/feng_shou_lu/README.md` (the rendering-side mirror).

### FR-2 — world.md

- `my_novel/feng_shou_lu/world.md`. Chinese-only.
- Sections (in this order):
  1. **修炼境界体系** — verbatim from dossier R-2 / baseline_extraction §2.1: 8-stage ladder 练气-筑基-金丹-元婴-化神-炼虚-合体-大乘 (resolved per dossier Open Question #3 to `大乘` terminal — avoids cadence echo with `wode_moni_changsheng_lu`'s `渡劫`).
  2. **修炼物理规则** — qi has substance, can be cultivated, costs time and resources; **the parasitic-system divergence** — for the protagonist alone, level-ups additionally consume biological lifespan (寿元) and episodic memory (记忆) per the `焚寿罗盘` ledger. The system is invisible to others — they see a prodigy who burns out.
  3. **三方势力格局** — verbatim from baseline_extraction §2.2 + dossier character_anonymization §3.3: 正派联盟 (赤霞门 / 九寰阁 / 澹台宗) · 散修盟 (流烛盟) · 魔门 (忘川教). Each faction gets a one-paragraph block: founding myth, current head figure, internal politics, signature visual.
  4. **地理与时代背景** — 澹江洲 (the protagonist's home region) · 落雁渊 (ep01 awakening site) · 栖梧崖 / 旧名「无寿崖」 (the past-life death site; ep17 reveal that 栖梧 was a deliberate rename to hide 无寿). Other locations stay inline per ai_video.md rule 12.3 (declared only on ≥2-shot reuse).
  5. **寄生系统的 in-fiction lore** — what is 焚寿罗盘 in-universe? Where did it come from? (Answer revealed in stages: ep17 = it's a relic from 师父 闻砚清 · ep30 = the relic is a fragment of 忘川教's 偿岁真言 contract · ep49/50 = the protagonist himself created the original contract to trap 忘川教 → it backfired into self-binding · ep60 = the final cost.). `world.md` captures the FULL truth so stage-6 ep01 prompts can plant correct seeds even though viewers only get fragments.

### FR-3 — style_guide.md

- `my_novel/feng_shou_lu/style_guide.md`. Chinese-only. Verbatim lift from `findings/angle-visual_style.md` §3 (all 7 subsections), replacing the working slug.
- MUST include the 6 mandatory subsections per ai_video.md rule 12.4 v4 dependency:
  - 镜头语言关键词字典 (景别 13 类 + 运动 9 类 — fixed dictionary; shot prompts re-paste, do not invent)
  - 光影词典 12 状态 (mozun's 10 + new `寄生 aura` + `寿命流失`)
  - 调色板 6 派系 (each with 主/辅/点缀 hex + ≥3 web visual citations)
  - 字幕规范 (per ai_video.md 12.4 三选一 — see FR-5.6)
  - 转场词典 9 类 (mozun's 8 + new `寿命计数器过` for the parasitic motif)
  - 负向锁定 (≥ 24-item base from mozun baseline + 12 project-specific = the negative-prompt block re-pasted into every shot)

### FR-4 — arc_outline.md (60 episodes at one-liner depth)

- `my_novel/feng_shou_lu/arc_outline.md`. Chinese-only.
- 60 numbered lines (`### ep01 — {title} — {hook} — {one-line synopsis}`).
- The 10 reveal-cadence beats from dossier R-6 MUST appear at the assigned episodes:

| Ep | Cadence beat |
|---|---|
| ep01 | 死亡开局 + 重生 + 系统觉醒 + 自取新名「裴知秋」+ 师父剪影 cliffhanger |
| ep08 | 归砚镜首次激活，ep01 背叛画面 unfiltered 回放 |
| ep10 | **付费节点 1** · 卫长烛 face-slap + 第一次「不可承受寿命代价」(失去关于母亲长相的记忆) + 神秘人 cliffhanger |
| ep17 | 前世名「裴长砚」揭晓；前世/本世 timeline 缝合 |
| ep20 | 《偿岁真言》 vs 《残忆经》镜像揭示 |
| ep28 | 容漪 = 忘川教 planted memory backup |
| ep30 | **付费节点 2** · 寄生系统起源部分揭示 (主角前世 = 系统设计者) |
| ep35 | 长烟幡 transfer (容漪 → 裴知秋) |
| ep49 | 归砚镜拼回完整记忆 — 主角发现 system 设计是为困住忘川教，反噬自己 |
| ep50 | **付费节点 3** · 主角 = 系统 source 真相揭晓 |
| ep60 | 季终 · 言息击败 · 容漪记忆被吃光 · 续季钩 ({偿岁真言}残片寄居容漪) |

- Remaining 49 lines: hook + synopsis per dossier reveal-cadence shape (复仇靶标 distribution across 60 ep). Each line is ≤ 40 字 Chinese.

### FR-5 — Character bibles (10 files: 9 active + 1 archive)

Per ai_video.md rule 12.1 schema (10-field 锁定描述符表 + 性格/动机/弧光/标志台词/关键场景/标志能力/配音参考/负向) + rule 12.5 v4 folder pattern (per follow-up 004): each character ships as `characters/{中文名}/{中文名}.md` (folder + 主 bible 文件).

Video reference (turntable) prompt 已嵌入主 bible 文件作为 `---` 分隔的第二段 (per rule 12.5 v4 主文件 schema; supersedes rule 12.2 sibling Seedream 立绘 PNG pattern which was abolished per follow-up 003).

| File | Role | Source of truth |
|---|---|---|
| `characters/c01_pei_zhi_qiu/裴知秋.md` | 男主 (本世). State A 重生弱体 + state B 寄生觉醒 — 双形态档 (per dossier visual_style §3.3 双形态契约). | dossier character_anonymization §3.1 etymology + visual_style §3.3 palette |
| `characters/c02_pei_chang_yan/裴长砚.md` | 男主前世名义档案 — 引用在 ep01 倒叙 + ep17 揭晓; 用「档案 archived」语义标记 | character_anonymization §3.1 |
| `characters/c03_wen_yan_qing/闻砚清.md` | 师父 — ep01 final-15s cliffhanger 出场 (剪影); ep17 真相揭晓 | character_anonymization §3.1 |
| `characters/c04_rong_yi/容漪.md` | 主女主 — ep01 cameo only (作为旁观者出现于某 montage 帧, ≤1 shot); 完整出场始于 ep05 | character_anonymization §3.1 |
| `characters/c06_wei_chang_zhu/卫长烛.md` | 正派背叛者 #1 (赤霞门掌门) | character_anonymization §3.2 |
| `characters/c07_ying_yan_zhi/应砚之.md` | 正派背叛者 #2 (朝堂太师之嫡子) | character_anonymization §3.2 |
| `characters/c08_qi_gui_yan/戚归砚.md` | 散修背叛者 #3 (流烛盟元老暗投魔门) | character_anonymization §3.2 |
| `characters/c09_chi_yin/池洇.md` | 散修背叛者 #4 (流烛盟杀手) | character_anonymization §3.2 |
| `characters/c10_ruan_wang/阮惘.md` | 魔门背叛者 #5 (忘川教三长老) | character_anonymization §3.2 |
| `characters/c11_yan_xi/言息.md` | 魔门背叛者 #6 / 最终 BOSS (忘川教教主) | character_anonymization §3.2 |

Per follow-up 004 (rule 12.5 v4): each character lives in its own `characters/{中文名}/` folder; the主 bible file is `{中文名}/{中文名}.md`. 文件夹允许 sibling 文件按角色复杂度按需添加 (state-A/B turntable / 单独 Seedream 立绘 / 配音参考详档 / etc.) — stage-6 validator 不强制要求 sibling 文件存在.

FR-5 sub-requirements:

- **FR-5.1** — 主角 双形态档案. `characters/c01_pei_zhi_qiu/裴知秋.md` carries TWO sets of 10-field 锁定描述符 — clearly labeled `## 锁定描述符 — state A: 重生弱体` and `## 锁定描述符 — state B: 寄生觉醒`. The 一句话锁定 line differs per state but contains a shared 面部 differentiator (the「左眼下方 0.3cm 灰青胎记」) byte-identical across both — so AI recognizes them as the same person. Both states get a turntable prompt embedded in the same file (post-003 single-file pattern), or optionally split into sibling files `characters/裴知秋/state_a_turntable.md` + `characters/裴知秋/state_b_turntable.md` per rule 12.5 v4 folder flexibility — current落地 keeps both turntables in主 bible 文件以 review 方便.
- **FR-5.2** — 词源行 mandatory. Each character bible ends with a single「词源」行 documenting the in-fiction etymology from dossier character_anonymization §3 — this is the seed for future-episode reveals; stage-5 internal-consistency validator greps for it.
- **FR-5.3** — 配音参考 stays planning-only per ai_video.md rule 12.1 — no TTS prompts generated in v1.
- **FR-5.4** — 负向 block re-pastes from style_guide.md § 负向锁定 + adds character-specific items where appropriate (e.g., 卫长烛's 负向 includes「不要戴墨镜 / 不要现代修剪眉」).

### FR-6 — Character video reference prompts (embedded in主 bible files per rule 12.5 v4)

Per ai_video.md rule 12.5 v11 video turntable prompt schema (post follow-up 003: 角色 turntable PNG via Seedream 立绘 已 abolished, 替代为 7s 单 take 视频 reference). Each turntable prompt lives嵌入 in `characters/{中文名}/{中文名}.md` 作为 `---` 分隔的第二段 (or optionally as sibling file `characters/{中文名}/{state}_turntable.md` per follow-up 004 v4 folder flexibility).

- 主角 双 state → 2 turntable prompts (state A + state B) 嵌入 `characters/c01_pei_zhi_qiu/裴知秋.md` 主 bible 文件.
- 裴长砚 前世形态 → 1 turntable prompt 嵌入 `characters/c02_pei_chang_yan/裴长砚.md`.
- 其余 9 角色 → 1 turntable prompt 嵌入各自主 bible 文件.
- Total: 12 turntable prompts. 12 不再以独立 Seedream PNG 立绘 文件存在 (rule 12.2 sibling Seedream 路径 abolished per follow-up 003 + rule 12.5 v3 → v4 folder pattern).

For each: 主体定义 + 主体/构图 + 面部 + 服装 + 姿态 + 背景 (low-suppression, doesn't compete with subject) + 光源 + 风格 (re-paste from style_guide.md § 正向关键词 ≥ 3) + 负向 (re-paste + character-specific).

### FR-7 — Scene files (2 files, single-file pattern per follow-up 003)

Per ai_video.md rule 12.3 v2 (post follow-up xianxia_new/003). Two scenes get full lock-down (≥ 2 shots reuse each within ep01); each ships as **one self-contained file** with bible + Seedream立绘 prompt merged (`---` separator):

- `scenes/s1_无寿崖.md` — past-life 渡劫处. Bible + 立绘 同文件. Visual: white-梧桐 forest + cliff + 落叶 + 雷劫.
- `scenes/s2_落雁渊.md` — present-life 系统觉醒地. Bible + 立绘 同文件. Visual: 深陷山渊 + 渊底白色 / 灰色鸟骨 + 苇草.

Each scene file: ① bible 段 (8-field 锁定描述符表 + 关键变化态: 雷劫态 vs 静默态 for s1; 黎明态 vs 夜态 for s2 + 出现镜头表 + 负向) + `---` 分隔符 + ② Seedream 立绘 prompt 段 (per rule 12.3 v2 single-file schema).

`scenes/ref_images/` 子目录已废止 per follow-up 003.

Other ep01 backdrops (朝堂 / 议事厅 / 沙场 during the 0:03–0:30 montage flashes) stay inline in shot prompts per ai_video.md rule 12.3 — they don't appear in ≥2 shots.

### FR-7.5 — episodes/ep01/chapter.md (NEW per follow-up 006, canonical source-of-truth)

- `my_novel/feng_shou_lu/episodes/ep01/chapter.md`. Chinese novel-prose chapter (用户可读), ≥ 5000 字.
- 第三人称跟随主角视角 (主角 OS occasional; 前世 裴长砚 OS only in §1 cold open).
- 5 段 (`## §N 标题`) reflecting the 5 plot beats (§1 渡劫之夜 / §2 死前那一闪的六张脸 / §3 落雁渊渊底的童子 / §4 水面上的「知秋」二字 / §5 渊口那道剪影).
- 质量 contract (per follow-up 006 §3): 感官细节 ≥ 3 非视觉 / 段; 内心 OS ≥ 30% 行长; 环境 mood ≥ 50 字 / 段; byte-identical 一句话锁定 + 标志台词 + 焚寿罗盘描述 + NFR-9 motif 9-keyword; 对白 subtext / 动作微观 ≥ 3 sub-beat; 仙侠 mood 锚 ≥ 6 处; §5 cliff ≥ 3 重钩.
- **比 downloaded_novels/xianxia/ baseline 更 detail-dense / OS-rich / cliff-strong** — 描写密度 ~50% 高于 凡人修仙传 ch01.
- chapter.md 是 episode 的 **canonical source-of-truth**; FR-8 script / FR-9 shotlist / FR-10 prompts 全部从 chapter derive.

### FR-8 — episodes/ep01/script.md (derived from chapter.md per follow-up 006)

- Full screenplay in Chinese, **derived from chapter.md** — same plot beat / 角色出场 / 标志台词 / cliffhanger, but rewritten in screenplay form.
- Sections: 集名 · 摘要 · 角色出场 · 场景列表 · 剧本正文 (with scene headings, action, dialogue, internal monologue).
- ≤ 8 minutes runtime target (per qa.md Q4 1–2 min × ~6–10 shots; ep01 hooks tighter at the lower end for paid conversion). Hard ceiling: 8 min.
- Beat structure (per dossier R-4):
  - **0:00–0:03** — 前世渡劫 — 雷劫劈下 + 剑刺穿. Cut to black.
  - **0:03–0:30** — 倒叙 quick-cut montage of 5 reasons-to-trust → 5 reasons-to-die for each of 6 betrayers (each pair ≤ 2.5s).
  - **0:30–1:15** — 主角苏醒于 落雁渊 渊底 7 岁练气体 + 焚寿罗盘 浮现 + 系统弹窗「代价已计算 · 寿元 -1 / 修为 +1」+ 寄生升级 motif 五拍 (per visual_style §3.3.3).
  - **1:15–1:45** — 自取新名「裴知秋」(水边题字) + 师父闻砚清 剪影出现.
  - **1:45–2:00** — Cliffhanger: 师父剪影 turn → 正脸闪一帧 (倒叙中已死的师父) → 闪黑 → 「第二集 即将揭晓」字幕.

### FR-9 — episodes/ep01/shotlist.md

- Per ai_video.md rule 6 (3–15s per shot, beat-driven; no padding to 15s).
- 6–10 shots total (within `1-2 min episode = ~6–10 shots` qa.md Q4 lock).
- Each row: shot_id · 时长 · 景别 · 运动 · 主要角色 · 主要 prop · 主要场景 · 一句 hook summary · seam-frame contract (前/后帧来源).
- Cliffhanger shot is explicitly flagged + marked `cover_frame: true` (the thumbnail-of-choice for short-platform feed).
- Shot count target: **7** shots (one per the 5 beat groups in FR-8, plus 1 extra for the 倒叙 dense pack, plus 1 for the cliffhanger turn — adjust during stage 6 if natural).

### FR-10 — episodes/ep01/shots/shotNN.md (one per shot)

Per ai_video.md rule 12.4 v2 (post follow-up 003) + rule 5 v2 (2-section schema). Each file: ① Shot context (Summary / Characters / Scene / Duration / Reference uploads checklist) + ② 视频 prompt fenced ```text``` block per the 12-field schema (post-003 seam-frame columns 主体定义 + 姿态 frozen instant removed).

Seam-frame Seedream embedded blocks (startframe + lastframe) **abolished per follow-up 003**. Cross-shot continuity now relies on description-layer byte-identical (角色一句话锁定 + 场景一句话锁定 + 光线/色调 + 渲染样式 + 负向 verbatim) + shared turntable mp4 + scene立绘 PNG reference uploads.

- **FR-10.1** — `角色:` line follows rule 12.4 v4 — one-sentence-lock + 50–80 字 face-differentiator per character, NOT inline-expanded.
- **FR-10.2** — `场景:` references the scene file by token if it's a declared scene; inline otherwise.
- **FR-10.3** — `动作:` is timed-beat with beats summing exactly to `时长:`.
- **FR-10.4** — `台词 / 字幕:` is one of the 三选一 per rule 12.4 — **default for this project: 内嵌硬字幕 for 系统弹窗 / 集头标题 / 黄金钩台词; 后期软字幕 for everything else** (per visual_style §3.7).
- **FR-10.5** — `渲染样式:` re-pastes from style_guide.md § 正向关键词 (≤ 9 core keywords per rule 12.4 v4).
- **FR-10.6** — `负向:` re-pastes from style_guide.md § 负向锁定 (≤ 24 core items per rule 12.4 v4).
- **FR-10.7** — Each shot prompt body (fenced text only) ≤ 2000 字 soft / ≤ 2500 hard per rule 12.4 v4 / NFR-1.
- **FR-10.8** — Cliffhanger shot (FR-9) Shot context includes an explicit `cover_frame: true` line.

### FR-11 — episodes/ep01/publish.md

Per ai_video.md rule 8. Chinese-only. Sections:

- **标题** (≤ 30 字) — hook-first title that doesn't spoil the cliffhanger.
- **简介** (≤ 200 字) — set the parasitic-cost hook + tease the cliffhanger.
- **标签** — 5–10 hashtags (e.g., #仙侠短剧 #重生 #系统流 #红果短剧 #反派打脸).
- **封面建议** — which shot's lastframe.png is the thumbnail (= the cliffhanger shot per FR-9).
- **平台备注** — Douyin / 红果 specific notes (post hashtag + post-time recommendation if research surfaced one); YouTube Shorts marked "EN subtitle pass deferred" per qa.md Q13.

### FR-12 — copyright_clearance.md

Per the dossier's stage-5 hand-off design. Single file at `my_novel/feng_shou_lu/copyright_clearance.md` containing:

- **BLACKLIST table** (lifted from baseline_extraction §2.5) — every distinctive baseline entity + source novel/chapter — auto-grep gate for stage 5.
- **Mozun_chongsheng cross-grep table** — every named entity / location / artifact from `ai_videos/mozun_chongsheng/` — auto-grep gate.
- **PROPOSED naming table** (lifted from character_anonymization §3) — every name + etymology + WebSearch collision check result.
- **DELTA report** — for each baseline novel + mozun_chongsheng, our delta justification (≤ 1 字面 carryover; differs on cost-mechanic / palette / faction-naming etc.).
- **SIGN-OFF section** — populated by stage 5 with the grep-pass timestamp.

### FR-13 — Mirror README under ai_videos/feng_shou_lu/

Per ai_video.md rule 9. `ai_videos/feng_shou_lu/README.md` — same H1 + 项目概要 + 使用说明 + 角色清单 + 风格关键词. This is the operator-facing README that links to the rendering-side prompt files.

Note: under MVP scope, the bulk of files live at `my_novel/feng_shou_lu/`. The `ai_videos/feng_shou_lu/` directory carries the README + any rendered output once the operator drives the pipeline; stage 6 does NOT pre-populate the entire ai_video layout (per qa.md MVP scope, only ep01-shipping files are created).

### FR-14 — Audit events for stage 6 work-unit progress

Stage 6 emits to `.audit/adhoc_agents/2026-05-24/xianxia_new-20260524-101931/events.jsonl`:

- `exec.unit.started` / `exec.unit.completed` for the single ep01 work unit (further sub-units if stage-6 decomposition adds them).
- `validation.started` / `validation.issue.raised` / `validation.pass` per ai_video.md / stage-5 strategy.
- `validation.requires_manual_walkthrough` once automated levels pass (per CLAUDE.md stage 6 contract for content tasks).

## Non-functional requirements

| # | NFR | Rationale | Verification (stage 5 / 6) |
|---|---|---|---|
| NFR-1 | Each shot prompt body ≤ 2000 字 soft / ≤ 2500 字 hard | ai_video.md rule 12.4 v4 NFR-17 — past these limits Seedance + Kling silently truncate, leading to drift | Stage 5 lints every shot prompt; hard limit = blocker |
| NFR-2 | Every character bible 角色 line + Seedream立绘 byte-identical across all references | ai_video.md rule 4 + 12.4 — drift = character identity drift across episodes | Stage 5 byte-compares; mismatch = blocker |
| NFR-3 | 9:16 aspect ratio in every shot + Seedream prompt | ai_video.md rule 7 + qa.md Q (implicit) | Stage 5 greps `比例: 9:16`; missing = blocker |
| NFR-4 | Every named entity passes the BLACKLIST + mozun cross-grep gate | dossier CCI-1 + copyright safety user requirement | Stage 5 auto-grep against BLACKLIST + `ai_videos/mozun_chongsheng/`; hit = blocker |
| NFR-5 | Every shot's 动作 timed beats sum exactly to 时长 | ai_video.md rule 12.4 v4 动作-timing 契约 | Stage 5 numerical check; mismatch = blocker |
| NFR-6 | ep01 runs ≤ 8 minutes total wall-clock | qa.md Q4 + paid-conversion theory (ep01 is hook, not closure) | Stage 5 sums shot 时长; >8min = warning, >10min = blocker |
| NFR-7 | ≤ 5 named characters per shot | ai_video.md rule for short-drama feasibility | Stage 5 counts named characters per shot prompt; >5 = warning |
| NFR-8 | ≤ 6 prop per scene | revised_prompt + short-drama feasibility | Stage 5 audits scene files + shot prompts; >6 = warning |
| NFR-9 | 寄生升级 motif present in ep01 ≥ 1 time | parasitic system is the load-bearing differentiator (dossier CCI-2) — ep01 establishes it | Stage 5 greps for the motif 5-beat signature; absent = blocker |
| NFR-10 | Cliffhanger shot exists + flagged `cover_frame: true` | qa.md Q10 + short-drama feasibility | Stage 5 audits shotlist + shot prompts; missing = blocker |
| NFR-11 | Every Chinese file content is Chinese (folder names + structural file names stay pinyin / English) | ai_video.md rule 1 | Stage 5 audits file body language; mixed = warning, English content body = blocker |
| NFR-12 | All cross-document references resolve (e.g., `[闻砚清]` link → `characters/闻砚清.md` exists) | basic deliverable hygiene | Stage 5 link-checker; broken = blocker |
| NFR-13 | Stage 6 produces validation.requires_manual_walkthrough before declaring done | CLAUDE.md stage 6 contract for content tasks | Stage 6 audit-event check; absent = blocker |

## Acceptance criteria summary

ep01 is "done" iff:

- **AC-1** — Every FR-1 through FR-14 deliverable exists at its specified path with non-empty content.
- **AC-2** — All NFR-1 through NFR-13 checks pass (warnings allowed; blockers must be resolved).
- **AC-3** — User has read `my_novel/feng_shou_lu/episodes/ep01/script.md` end-to-end and confirmed the narrative beats land.
- **AC-4** — User has skimmed at least one shot prompt (`shots/shot01.md` recommended — the 死亡开局) and confirmed the 14-field schema is filled per ai_video.md rule 12.4.
- **AC-5** — `copyright_clearance.md` `SIGN-OFF section` carries a stage-5 grep-pass timestamp + zero unresolved blacklist hits.
- **AC-6** — `arc_outline.md` has all 60 lines including the cadence beats per FR-4 table.
- **AC-7** — `validation.requires_manual_walkthrough` event has been emitted and the user has acknowledged.

Stage-5 validation strategy operationalizes AC-2; stage-6 streaming validation runs the strategy per work unit and gates progress.

## Open questions (surface to user at stage 4 review gate)

1. **Final title pick.** Proposed: **《焚寿录》** / slug `feng_shou_lu`. Alternatives from dossier R-1:《残忆长砚》(`can_yi_chang_yan`) ·《知秋不返》(`zhi_qiu_bu_fan`). The folder rename `mv specs/ai_video/xianxia_new/ specs/ai_video/{final_slug}/` happens at stage-4 approval; subsequently `my_novel/{final_slug}/` + `ai_videos/{final_slug}/` are created at stage-6 start.
2. **Cultivation ladder terminal stage.** Spec picks `大乘` (resolves dossier Open #3). Confirm or override to `渡劫`.
3. **Empty baseline folders** (`cong_jianshu_xiuxing`, `gou_zai_xiuxianjie`, `zhutian_daozu`) — dossier Open #2. Spec does NOT block stage 5 on the补抓; user can fire that download as a follow-up to `specs/development/ai_video_management/` at any time before stage-5 copyright_clearance runs. Confirm: don't block here.
4. **主角 双形态立绘 — one file or two.** FR-5.1 lets stage 6 pick. The user may have a preference (one file is denser; two files is easier to test each state independently). No default needed if no preference.
5. **Cliffhanger shot strategy.** FR-9 shot count target = 7; the cliffhanger is the 7th shot. Alternative: 6-shot ep01 with the cliffhanger merged into shot 6's last 4 seconds. Trade-off: tighter pace vs cleaner seam frame. Stage 6 decides; user can preempt.
6. **Mozun_chongsheng grep gate scope** — NFR-4. Should it grep ALL `ai_videos/mozun_chongsheng/` files (including its drafts/) or just the canonical 角色 / 场景 / world files? Spec defaults to ALL non-draft files; user can narrow.

## Pre-reading consulted (stage 4 — informational, not contracted)

Stage 4 is parent-direct without workers; the pre-reading contract (CLAUDE.md § Stage playbooks and reference docs) applies to stages 2/3/5 and stage 6 work-unit validation.started events. This stage still read for spec compilation:

- `specs/ai_video/xianxia_new/user_input/revised_prompt.md` (post follow-up 001)
- `specs/ai_video/xianxia_new/user_input/follow_ups/001-20260524-114109-mvp-ep01-only-iterative.md`
- `specs/ai_video/xianxia_new/interview/qa.md` (post Q11 override)
- `specs/ai_video/xianxia_new/findings/dossier.md` (post resolution of Open #4)
- `specs/ai_video/xianxia_new/findings/angle-baseline_extraction.md`
- `specs/ai_video/xianxia_new/findings/angle-trend_research.md`
- `specs/ai_video/xianxia_new/findings/angle-visual_style.md`
- `specs/ai_video/xianxia_new/findings/angle-character_anonymization.md`
- `.claude/agent_refs/project/ai_video.md` (rule 1 path · rule 2 novel layout · rule 4 image-first pipeline · rule 6 duration · rule 7 ratio · rule 8 publish · rule 9 README · rules 12.1–12.4-B prompt templates)
- `.claude/agent_refs/project/general.md`
