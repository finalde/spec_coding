# Project refs — `task_type=ai_video`

Cross-cutting rules about the outputs of every ai_video-task project (`ai_videos/{name}/`). Loaded when the current task has `task_type=ai_video`. Per `CLAUDE.md` § Stage playbooks and reference docs: this file overrides `project/general.md`; the per-project spec under `specs/ai_video/{name}/` overrides this file for that one project (with a divergence note).

## Rules

### 1. Path language

- `task_name` is **pinyin or English**, never Chinese. Example: `chongsheng_zhi_zongcai_furen`, not `重生之总裁夫人`. Reason: task_id 构造（`task_id = "{task_name}-{YYYYMMDD-HHmmss}"`）必须 ASCII 稳定；`.audit/adhoc_agents/{date}/{task_id}/` 路径在 Windows + git 下需保持简洁。The Chinese title lives in `ai_videos/{name}/README.md`.
- Folder names inside `ai_videos/{name}/` 默认为 **English or pinyin** (`characters/`, `episodes/ep01/`, `shots/`, `ref_images/`)。这些是结构化目录，命名稳定性 > 可读性。
- File names inside `ai_videos/{name}/` 默认为 **English or pinyin**（`shotlist.md`, `shot01_kling.md`, `episode.md`），但 **角色 / 场景 / 道具等"内容性"文件可 opt-in 中文命名**（`沧冥-魔尊本相.md` / `紫霄宫-禁地暗室.md`），便于在 ai_video_management webapp 中一眼识别"哪个文件对应哪个人物 / 场景"。Opt-in 须在 `specs/ai_video/{name}/final_specs/spec.md` 显式记录 divergence note。
- 结构性文件（`shotlist.md` / `episode.md` / `shot{NN}_{kling,seedance,lastframe_seedream}.md` / `publish.md` / `arc_outline.md` / `world.md` / `style_guide.md` / `README.md`）保持 English/pinyin —— 这些是骨架，跨项目模板复用率高。
- File **contents** are **Chinese**. The project's "everything Chinese in `ai_videos/`" rule applies to file content, not paths.

*(Per follow-up `mozun_chongsheng/002` 与 `ai_video_management/004`：现代 Windows + git 已能稳定处理 UTF-8 路径；ai_video_management webapp `is_inside` / `safe_resolve` / 前端 Sidebar 已支持 UTF-8 中文路径段；放宽限制以提升内容文件可识别性。)*

### 1b. No hex color codes / hex-bound color annotations in outputs

- **任何 `ai_videos/{name}/` 输出文件都不得含十六进制色码** (`#` + 6 hex digits, e.g. `#a87838`)，无论是否包裹反引号。色码对目标 AI 视频/图像模型 (Kling / Seedance / Seedream / ...) 不可解析，只是噪声。
- **色码 + 与之绑定的颜色名共同删除**：形如 `色名 #hex`（`月夜紫黑 #2a0a3a`）或 `(#hex 色名)`（`(#a87838 冷金挑光)`）的「颜色提示」整体去掉颜色部分——保留它所修饰的物件名 (`青灰长袍 #7a8a8a` → `长袍`；`骨白碎冰刃 #e8d8c0` → `碎冰刃`)；纯色/情绪短语 (`月夜紫黑 #2a0a3a + 残血暗 #5a1a14`) 整段移除。颜色仅以自然中文描述存在于行文里，不再设专门「配色 hex」字段或 `色名 #hex` 标注。
- **本规则覆盖各模板里残留的 hex 字段标签**：rule 12.8 锁定描述符 `瞳色（hex）`/`服装 / 主色（hex）`/`配色 hex（主/辅/点缀/高光）`、rule 12.3 场景档 `配色 hex（主/辅/点缀）`、rule 12.4 视频 prompt `色调对齐主/辅/点缀 hex` —— 一律不带 hex，直接用中文色彩描述；style_guide 调色表里的色码列清空（保留命名/用途列）。
- 色温 (`5500K`/`4500K`)、尺寸、机位等非色码信息**保留**——它们不是颜色提示。

*(Per follow-up：用户要求去掉所有 prompt 里的颜色提示（如 `(#a87838 冷金挑光)`）。既有三项目 `feng_shou_lu` / `mozun_chongsheng` / `nvdi_tuihun_houhuile` 已全量清理 (696 处 / 126 文件 → 0 hex)。)*

### 2. Output layout — `sub_type=novel` (v3, post follow-up xianxia_new/009 — split reader vs production)

**Reader-side `my_novel/{name}/`** (matches downloaded_novels schema per follow-up 111; pure novel format users read like 起点/番茄/晋江):

```
my_novel/{name}/
├── _meta.json     # novel metadata (slug, title, category, author, source, chapters[])
├── README.md      # 小说扉页 (Chinese title + 概要 + 章节列表 link + 题材标签)
└── chapters/
    ├── {NNNN}-第N集 {title}.md   # 单章 prose (H1 chapter title + 章节正文); 无 YAML envelope, 无 production metadata
    └── ...
```

**Production-side `ai_videos/{name}/`** (full drama production工作区):

```
ai_videos/{name}/
├── README.md                    # 短剧项目 index (中文 + 项目概要 + 使用说明 + 渲染产物布局 + 角色清单)
├── world.md                     # 世界观: 修炼境界 / 三方势力 / 地理 / lore (本剧 specific)
├── style_guide.md               # 风格指南: 镜头词典 / 调色 / 字幕 / 负向 / motif
├── arc_outline.md               # 全集 one-liner 大纲 + ledger
├── copyright_clearance.md       # 版权清查 SIGN-OFF
├── characters/
│   └── c{N}_{中文名}/c{N}_{中文名}.md   # 角色 bible per rule 12.8 v2 + 12.9 (folder + filename byte-identical, both Chinese, N 不补零 not zero-padded)
├── scenes/                      # opt-in: 当 ≥2 shots 复用同一地点 (template: rule #12.3 v2 + folder-per-asset per 12.8 v2 + 12.9)
│   ├── s{N}_{中文名}/s{N}_{中文名}.md   # 场景档 + 嵌入 Seedream 立绘段 + 场景 reference 视频 prompt 段 (single-file pattern; folder also holds 渲染 mp4 + ref.png, gitignored)
│   └── ...
├── arc_outline.md               # 剧集大纲, 一行/集
└── episodes/
    └── epNN/
        ├── script.md           # screenplay form (scene heading + 动作 + 对白 + 内心 OS, derived from reader-side chapter)
        ├── dialogue.md         # 纯对白 derived from chapter (rule 12.6-B; format: `角色名: "台词" (语气情感注释)` 每行)
        ├── shotlist.md         # 镜头清单, 每镜≤15s
        ├── shots/              # per rule 2 v3 (post follow-up xianxia_new/011): renamed from `prompts/` for naming clarity
        │   └── shotNN/         # ⚠ folder-per-shot per rule #12.9 (NOT a flat shotNN.md). Folder holds prompt .md + subtitles.md + renders/ media.
        │       └── shotNN.md   # per rule #5 v3 (3-section: chapter excerpt + shot context + 视频 prompt)
        └── publish.md          # 发布信息: 标题/简介/标签/封面建议
```

**Authoring order (canonical → derived, post-follow-up xianxia_new/006 + 009 split + 011 dialogue.md + shots/ rename)**:

1. **reader-side**: `my_novel/{name}/chapters/{NNNN}-XXX.md` — novel prose chapter (canonical source-of-truth, ≥ 5000 字 中文, 用户可读).
2. **production-side script**: `ai_videos/{name}/episodes/epNN/script.md` — screenplay derived from chapter.
3. **dialogue**: `ai_videos/{name}/episodes/epNN/dialogue.md` — 纯对白 derived from chapter (per rule 12.6-B). 配音/TTS/字幕团队的轻量入口, 比 script.md 更简洁(只保留说话角色+台词+语气情感注释)。
4. **shotlist**: `ai_videos/{name}/episodes/epNN/shotlist.md` — derived from script.
5. **shot prompts**: `ai_videos/{name}/episodes/epNN/shots/shotNN/shotNN.md` — derived from shotlist + script + chapter excerpt. **⚠ folder-per-shot (rule #12.9): each shot is a same-named folder `shots/shotNN/` containing `shotNN.md` (+ `subtitles.md` + `renders/` media), NEVER a flat `shots/shotNN.md`.** The webapp display + render-import (`renders/` routing) + 台词 burn-in (`subtitles.md`) contracts all depend on this folder. A flat `shotNN.md` is a stage-6 structural blocker.

Chapter excerpt section (rule 5 v3, follow-up 007) 在每个 shotNN.md 的最顶部 quote 200-400 字 chapter prose, 跨 folder cross-reference: `../../my_novel/{name}/chapters/{NNNN}-XXX.md`.

ep02+ contract: chapter-first 必须先写 reader-side chapter, 再 derive production-side script / dialogue / shotlist / shot prompts.
```

At stage 4 the `episodes/` tree contains detailed files only for the first `detail_batch_size` episodes (default 5). Remaining episodes appear in `arc_outline.md` as one-line synopses; full detail is generated by a stage-4 regen targeted at the next batch.

### 3. Output layout — `sub_type=short`

```
ai_videos/{name}/
├── README.md
├── characters/
│   ├── main.md                  # template: rule #12.1
│   └── ref_images/
│       └── main_seedream.md     # template: rule #12.2
├── scenes/                      # opt-in: 当 ≥2 shots 复用同一地点 (template: rule #12.3)
│   ├── {scene_name}.md
│   └── ref_images/
│       └── {scene_name}_seedream.md
├── style_guide.md               # 短片不需要 world.md, 风格信息融入此文件
├── script.md
├── dialogue.md                  # 纯对白 derived from script (rule 12.6-B; format: `角色名: "台词" (语气情感注释)` 每行)
├── shotlist.md                  # 标记 hook 镜头
├── shots/                       # per rule 3 v3 (post follow-up xianxia_new/011): renamed from `prompts/` for naming clarity
│   ├── shot01_startframe_seedream.md  # only shot 01 (template: rule #12.4)
│   ├── shotNN_kling.md                # template: rule #12.4
│   ├── shotNN_seedance.md             # template: rule #12.4
│   └── shotNN_lastframe_seedream.md   # every shot (template: rule #12.4)
└── publish.md
```

### 4. Image-first character pipeline

Every named character MUST get a Seedream ref-image prompt under `characters/ref_images/<role>_seedream.md`. The user generates the立绘 once via Seedream; that image is then attached as the reference frame in every Kling image-to-video shot featuring that character.

Reason: pure-text character description drifts visibly across hundreds of generations. Image-to-video on Kling locks the face / outfit / build origin.

Concrete shot-prompt template (Kling, image-to-video):

```
[参考图: characters/ref_images/<role>_seedream.md 生成的立绘]
角色: {主角名} — {锁定的中文描述, byte-identical 跨所有镜头}
场景: {场景描述, 引用 world.md / style_guide.md}
动作: {镜头内动作, 0–15s 内 timed beats}
镜头: {景别 + 运动}
光线/色调: {匹配 style_guide.md}
比例: 9:16
时长: 15s
```

Seedance prompt is text-to-video (it doesn't take character refs in the same way). Same template minus the `[参考图]` line, with the locked Chinese descriptor as the primary character anchor.

*(Field-level strict 模板见 rule #12.4；本节保留为高阶语义说明。)*

### 4b. Image-first key-prop pipeline (重要复用道具 ref 图 · 2026-06-20 follow-up)

A **recurring key prop** — 贯穿多镜/多集的信物 / 法器 / 标志道具（如 `武神觉醒` 的半块古玉佩＝长线伏笔 + 第二宝线索）— 靠每镜文字复述必然渲染漂移（EP2 两镜玉佩样子就不一致）。这类道具 MUST 像具名角色一样，立 **自己的 asset 卡 + Seedream ref 图 prompt**，每个出现它的 shot 都 reference 这一张图。

- **Prop 卡落点**：`2_世界观人设/props/{道具名}/{道具名}.md`（与 `characters/`、`scenes/` 平行；道具名可中文 opt-in，per rule 1）。卡内含：① **锁定描述符**（byte-identical 复制到每个出现它的 shot 的道具描述行）；② 专属 **Seedream text→image ref prompt**（纯道具白灰底特写、便于抠像）；③ 用法说明 + 藏锋/负向锁定。
- **生成一次 ref 图**（`{道具名}.png` 同 folder），之后**每个出现该道具的 shot**：在 `参考:` 行追加 `{道具名}=>` handle、并 byte-identical re-paste 锁定描述符（与角色 ref 同机制）。
- **适用判定**：**跨 ≥2 镜复用、且外观须一致的关键道具**才立卡（一次性道具不必）。普通随身物仍可留在角色 bible 的「标志道具」字段；当它升级为长线伏笔 / 多镜特写对象时，提升为独立 prop 卡（角色 bible 的标志道具行改为指向该 prop 卡）。
- **藏锋/特效铁律照旧**落该道具的每个 shot（如玉佩零光透温、不发光）。

### 5. Single-self-contained-file-per-shot requirement (rev follow-up 007 → v3 per xianxia_new/007)

Every shot ships with **one** `shotNN.md` self-contained file. **v3 schema (3 sections, post-follow-up xianxia_new/007 2026-05-24)**:

① **Per-shot novel prose** (NEW per follow-up 007; scope widened 2026-05-30) — a 200-400 字 中文 passage of the corresponding novel prose at the **very top** of `shotNN.md`, kept in 小说形态 (flowing narrative — 叙述 + 内心 OS + 感官 + 必要对白), placed before the `# epNN / shotNN` H1 and separated from it by a `---` rule. Two cases:
>   - **Reader-side novel exists** (`my_novel/{name}/chapters/…`): heading `## Chapter excerpt (from chapter.md §N {section})`, a **verbatim** blockquote of the most directly-corresponding chapter prose (e.g. `feng_shou_lu`, `nvdi_tuihun_houhuile` post-follow-up 006 — migrated from novel-less to chapter-first).
>   - **No reader-side novel** (script-first / novel-less dramas, e.g. `mozun_chongsheng`): heading `## 小说原文`, a passage **authored from that shot's own script + Shot-context** (Summary / 动作 / 台词 / Scene / Characters), written so consecutive shots read as one continuous chapter. Pure prose — no `>` blockquote, no reference-handle (`…请参考:@…`) lines, no field labels.
>
>   Either way the prose lives **outside** the ```text``` fenced blocks (it is NOT a prompt; the structured editor and stage-6 prompt validators ignore it) and gives the model + human reviewer the surrounding mood / 内心 OS / 感官 anchor. **出场角色名高亮约定 (per follow-up nvdi 005):** 在 `## Chapter excerpt` / `## 小说原文` 段内，本 shot 出场的角色名以 markdown **粗体** 标注（如 **陈凡** / **陈国公**），便于与 Shot context `Characters:` 行交叉核对出场角色完整性。粗体仅为显示层 — 去除 `**` 标记后与 chapter 正文 / 原 prose **byte-identical**；代码块内 `情节:` 字段保持纯文本（不加粗，避免污染复制到模型的 prompt）。Exactly **one** such section per shot — do not duplicate it with a second prose heading (`## 小说文本 / Novel prose` and the like were consolidated into `## 小说原文` per follow-up 2026-05-30).

② **Shot context** (rule 5 v2 retained) — Summary / Characters / Scene / Duration / Reference uploads checklist.

③ **视频 prompt** (rule 5 v2 retained) — model-agnostic 12-field schema per rule #12.4 v2 (post-003), ` ```text ` fenced ready-to-copy-paste.

The earlier ④ Seam-frame still prompts section (startframe / lastframe Seedream embedded code blocks) remains **abolished** per follow-up xianxia_new/003.

Cross-shot visual continuity continues to rely on **description-layer continuity** + chapter excerpt cross-reference (which keeps prose context human-readable across the episode).

*(Evolution: pre-006 → 006 single → 007 single+seam → **v2 (003) seam abolished** → **v3 (007) chapter excerpt added at top**.)*

### 6. Per-shot duration — flexible 3–15 s by plot beat (≤ 15 s ceiling)

Every shot's `时长:` is chosen **per-shot** to match what the dramatic beat actually needs, anywhere in **3–15 seconds**. 15 s is the **ceiling, not the target** — padding a 5 s reaction to 15 s of slow camera drift dilutes the beat and tells the model to invent uninstructed filler (where it typically drifts in motion / framing / lighting). Conversely, hook / cliff / monologue / cover-frame shots that genuinely carry information toward 15 s should use it.

Author-side duration heuristic (non-binding — adjust per script):

| Plot-beat type | Typical duration |
|---|---|
| Quick reaction / cut-in / micro-glance | 3–5 s |
| Single action beat / one line of dialogue | 5–8 s |
| Two-beat exchange / short dialogue + reaction | 8–11 s |
| Multi-character standoff / monologue / hook landing / cover-frame | 11–15 s |

The shot's `动作:` timed beats and `台词 / 字幕:` time windows MUST sum to exactly the `时长:` value. No divergence note required for any duration in 3–15 s; durations outside the range (< 3 s twitch cuts, or > 15 s) DO require an explicit divergence note in the Shot context Summary.

**Kling 2.1 Pro cap (10 s) note:** when a shot's `时长:` > 10 s is rendered via Kling, the user splits the render into back-to-back Kling calls (each ≤ 10 s) and uses the shot's own `shot{NN}_lastframe.png` mid-seam as input to the second call. The shot prompt itself is always written for whatever duration the beat needs — the Kling split is a user-side rendering step, not a schema concern. Seedance accepts ≤ 15 s directly in a single call.

**Per-episode total duration — 180–195 s (3:00–3:15).** Each episode (novel) / short MUST assemble to a total runtime of **180–195 秒**. The episode total is the binding target; per-shot durations are still chosen per beat (above), but the author writes **enough beats** that the `时长` column of `shotlist.md` sums into `[180, 195]`. `shotlist.md` carries an explicit `时长合计` line proving the sum is in range (stage-6 validator greps it).

**Fast-cut default + 15 s hard cap.** Default episode pacing is **fast-cut: 名义 5–8 s/shot, ~25–35 shots/episode** (国内短剧 cut rhythm). **No shot exceeds 15 s** — 15 s is a hard rendering cap (Kling/Seedance), not just a dramatic ceiling. Because every shot is now ≤ 15 s, the legacy ">15 s beat split with seam frame" carve-out is retired: a beat that would run long is authored as multiple consecutive ≤15 s shots, not one over-length shot. The 3–15 s per-beat heuristic table still governs individual shot sizing within the fast-cut budget.

*(rev — follow-up "flexible per-shot duration" — 2026-05-21: reversed the earlier "15 s is the target, fill the full budget" stance because user empirical review found forced-15 s shots dilute fast beats and let the model invent uninstructed filler. The earlier policy originated from a "Seedance single-generation budget" optimization that turned out to favor model uptime over dramatic pacing. New policy: duration follows the beat, with 15 s as ceiling only.)*

*(rev — follow-up "每集 3 分钟 + fast-cut + 15s 硬上限": added per-episode total 180–195 s, fast-cut 5–8 s default (~25–35 shots/ep), and a hard 15 s/shot cap (Kling/Seedance render limit). Per-shot beat sizing unchanged; episode now assembled to total. All 7 existing episodes regenerated under this rule.)*

**Overflow cascades to the next episode — never trim dialogue or cram (per follow-up wushen_juexing/022 — 2026-06-14).** When a drama declares a per-episode duration target (whether the 180–195 s default above or a per-project divergence such as wushen_juexing's ~90 s), and an episode's content (especially dialogue-dense 对峙 scenes) exceeds that target, the author **splits at the nearest scene/beat boundary near the target and pushes the surplus shots into the next episode** — re-numbering the moved shots (folder `shotNN/`, compact tag `{NN}集{NN}镜…`, H1, frontmatter `work_unit_id`) to the new episode. Do **NOT** compress shots, delete dialogue, or pad to hit the bound. The overflow episode may temporarily run short (fewer than the min shot count / under the min seconds) — mark its `shotlist.md` with `溢出段·待补` and exempt it from the S-DUR bounds until that episode's own beats fill it back to target. Rationale: dialogue density and episode length are independent levers; cap length by cascading, not by gutting the script.

### 7. Aspect ratio

9:16 default for both sub-types. 16:9 / 1:1 only on explicit per-project spec override (with a divergence note).

### 8. Publish metadata

Every episode (novel) and every short ships with `publish.md` containing: hook title (≤30 Chinese chars), description (≤200 Chinese chars), 5–10 hashtags, cover-frame suggestion (which shot to thumbnail). Same Chinese-content rule applies.

### 9. README required, in Chinese

Every `ai_videos/{name}/README.md` ships with: 项目概要, 使用说明 (how to take these files into Seedream + Kling + Seedance), 角色清单, 风格关键词. Updated alongside any feature change per `CLAUDE.md`'s general project rule.

### 9b. 引用表演演技库（`ai_videos/_performances/`）— 标注 + 按剧情融入

短剧 shot 需要某种演技效果时，**引用**共享表演演技库（`_performances/{emotion}/perf_NNNN/`）的条目，按本镜剧情**融入**，**不照抄**整段（契约 = performance_library FR-10 v2）：

1. **标注**：shot.md 的 `## Shot context` 加一行（可多条）
   `表演库参考: perf_NNNN (情绪·强度·风格·载体) — 用于 <角色> <剧情 beat>`。
   shot 代码块顶部可选 reference-handle 头 `表演参考: perf_NNNN`。
2. **融入（非照抄）**：把被引 entry `## 锁定文本块` 的**物理动作要点**改写进 shot 的 `动作:` / `表情:` 字段——保留"写物理动作不写情绪名"的内核与关键肌肉动作（泪膜成形不落 / 眨眼抑制 / 上下脸冲突 等），但按本 shot 的**角色 / 机位 / 时长 / 剧情语境重新措辞**（替换通用主体为本剧角色、按本镜时长拆 timed beats、并入本镜走位与台词）。严禁把 entry 的检验视频 prompt 整段粘进 shot。
3. **可重生成**：`表演库参考:` 标注让"更新表演库后一键重生成本 shot prompt"可机检——webapp shot 页面的「🎭 按表演库重生成」按钮据此组装重生成 prompt（`POST /api/regen-shot-prompt`），重读被引 entry 的最新锁定块、重新融入本 shot。

样例见 `ai_videos/_performances/_reference_usage.md`。表演库条目永远 generic（无剧目专名）；剧目专名只出现在 shot 里、不回灌库。

*(Originated from follow-up performance_library/007 — 引用表演库按剧情融入而非照抄 + shot 标注被引 entry。)*

### 10. Stage-6 regeneration scope

Per the per-prompt regen scope flag (`scope=episode | scope=project`):

- `scope=episode N` (novels only): delete only `ai_videos/{name}/episodes/ep{NN}/`. Character bibles, world, style guide, other episodes preserved.
- `scope=episodes M..N`: delete only the named range; everything else preserved.
- `scope=project` (default): delete the entire `ai_videos/{name}/` folder per `CLAUDE.md` regen-semantics table.

Shorts have only `scope=project`.

### 11. Seam-frame still-image pipeline — **ABOLISHED per follow-up xianxia_new/003 (2026-05-24)**

> **Status: ARCHIVED.** This rule is no longer load-bearing. Stage-6 validators no longer grep for seam-frame blocks; new shot prompts written under rule 5 v2 ship with only 2 sections (Shot context + 视频 prompt). Cross-shot visual continuity is handled by description-layer continuity (byte-identical 角色/场景 一句话锁定 + 光线/色调 + 渲染样式 + 负向 verbatim) plus shared turntable mp4 + scene立绘 PNG reference uploads. The text below is retained for historical context only.

AI-video generators (Kling 2.1 Pro, Seedance 1.0 Pro) cap individual clips at ~10–15 s. To stitch clips into a longer video without visible drift, **the last frame of clip N must visually match the first frame of clip N+1** — same character pose, lighting state, prop position, environment. Generating those seam frames as still images first via Seedream, then passing them to Kling as `input_image_urls = [start_frame, end_frame]` (Kling 2.1 Pro accepts up to 4 reference frames), pins both ends of every clip deterministically and eliminates seam drift.

**Per-shot prompt files (mandatory):**

- `shots/shotNN_lastframe_seedream.md` — Seedream still-image prompt for the final frame of shot NN. **Every shot**.
- `shots/shot01_startframe_seedream.md` — Seedream still-image prompt for the absolute opening frame. **Only the first shot of the video** (shorts) **or the first shot of each episode** (novels).

**Frame-prompt body structure** (analogous to `characters/ref_images/<role>_seedream.md` but scene-level, not character-level):

1. 主体定义 — full scene at that frozen instant: character + environment + prop positions + lighting state.
2. 角色 — re-paste the locked character descriptor block byte-identically (same contract as video shot prompts).
3. 场景 / 镜头 / 光线/色调 — re-use the SAME tokens as the corresponding video shot prompt's `场景:` and `光线/色调:` lines, so the still is visually consistent with the video's middle.
4. 姿态 — a frozen instant: exact pose / camera angle / lighting state at the seam moment.
5. 比例 — 9:16 (or project override).
6. 负向 — same禁用 list as video prompts.

**Workflow:**

1. Render each `_seedream.md` frame prompt via Seedream; save the PNG next to the prompt:
   - `shots/shot01_startframe.png` (only shot 01 of video / each episode)
   - `shots/shot{NN}_lastframe.png` (every shot)
2. For each Kling shot, set `input_image_urls = [start_frame_path, end_frame_path]`:
   - shot 01: `[shot01_startframe.png, shot01_lastframe.png]`
   - shot N (N ≥ 2): `[shot{N-1}_lastframe.png, shot{N}_lastframe.png]`
3. Seedance is text-to-video (no image input). Seam frames are not Seedance API parameters, but their described content MUST match across adjacent shots — re-use the same `场景:` / `光线/色调:` tokens and the locked character descriptor so Seedance text-only outputs read consistently next to neighboring Kling outputs.
4. Stitch the resulting clips with any video editor (ffmpeg `concat`, CapCut, DaVinci, Premiere). With seam frames pinned, the stitch points should be invisible.

**Loop-back contracts:** when a shot's last frame must equal another shot's start frame (e.g., visual loops where Shot N's tail = Shot 01's head), both prompts still ship; the user generates ONE PNG and re-uses it for both seams. Each prompt body should describe the frame near-identically and explicitly note the loop relationship in a header comment block (e.g., `# 回环契约: 本帧与 shot01_startframe.md 字节级相同`).

*(Originated from follow-up "use last-frame-as-input-image for clip stitching" — 2026-05-06. **ABOLISHED follow-up xianxia_new/003 — 2026-05-24.**)*

*(Field-level strict 模板见 rule #12.4 v2 (post-003)；seam-frame 列已删除。)*

### 11c. 台词烧录 — 每 shot `subtitles.md` 时间轴 + webapp 一键烧字幕

渲染完成后把台词（含内心独白 OS）按时间烧进 shot mp4 的 render-side 后期步骤。**与 prompt 层解耦**：shot 视频 prompt 里的 `台词 / 字幕:` 字段（rule 12.4 三选一契约）不变，本规则只新增一个「渲染产物 → 带字幕渲染产物」的后处理。

- **每 shot 一个 `shots/shot{NN}/subtitles.md`**（与 `shot{NN}.md` 同级，是 `renders/` 的父目录），所有 take 共用。文件名 English/pinyin（结构性文件），内容 Chinese + English。
- **双语格式（follow-up wushen_juexing/048 — 2026-06-16）**：fenced ```text 块内，每行 `起-止(秒) 中文 || English`。`||` 左为中文、右为英文；省略 `||` 即中文单语（向后兼容旧的纯中文文件）。`#` / 空行 / ``` fence 行忽略。内心独白(OS)写法相同——**不单独区分字幕样式**（统一底部居中硬字幕，仅时间窗不同）。解析正则 `^\s*(\d+(?:\.\d+)?)\s*[-–~至]\s*(\d+(?:\.\d+)?)\s*[:：]?\s*(\S.*?)\s*$`（`|` 已不作时间-文本分隔符、专留作双语分隔），随后文本按 `||` 切中/英；`end<=start` 或两侧皆空的行跳过。
  ```text
  0-3      老天爷，竟真让我重活一回。 || Heavens — I really have lived again.
  3-5.5    （内心）这一世我绝不再忍。 || This life, I will never yield again.
  5.5-8    你们，都等着。            || Just you all wait.
  ```
- **ai_video_management webapp（烧字幕）**：每个 render mp4 卡片（`shots/shot{NN}/` 下视频）有「📝 生成台词」(`POST /api/scaffold-subtitles`，从 `shot{NN}.md` 的 `## 台词配音` 块 `台词:` + `时长:` 均分生成**双语模板** `中文 || `（英文留空待填），已存在非空则拒绝) 与**三个语言烧录按钮**「💬中文 / 💬EN / 💬中英」(`POST /api/burn-subtitles` body `{path, lang}`，`lang ∈ zh|en|both`)。烧录把 `subtitles.md` 按所选语言渲成 ASS、ffmpeg `subtitles` 滤镜 + libx264 烧进视频。**输出命名（follow-up wushen_juexing/049）**：不再用原 take stem，而是每 shot 每语言一个**稳定 master**——`shots/shot{NN}/shot{NN}_{zh|en|zhen}.mp4`，放在 **shot 文件夹根目录**（不在 `renders/`），与原始 take 区分；同 shot 可导入多个原始 mp4，烧任一个 take 都覆盖同名 master。**原 render 保留**。所选语言无可烧文本（如选 EN 但英文列空）→ `empty_subtitles`；`lang` 非法 → `invalid_subtitle_lang`。
- **按语言合成整集（follow-up wushen_juexing/049）**：episode 的 `shotlist.md` 工具栏「🎬 合成本集视频」**改为 4 个按钮**「原片 / 中文 / EN / 中英」(`POST /api/concat-episode` body `{path, lang}`，`lang ∈ original|zh|en|both`)。`original` 仍取每 shot `renders/` 最新 take → `ep{NN}.mp4`；`zh|en|both` 取每 shot 的 `shot{NN}_{zh|en|zhen}.mp4` master → `ep{NN}_{zh|en|zhen}.mp4`。缺该语言 master 的 shot 跳过（reason `no_{suffix}_subtitle_mp4`）。故一集最多 4 个版本：`ep{NN}.mp4` / `ep{NN}_zh.mp4` / `ep{NN}_en.mp4` / `ep{NN}_zhen.mp4`。
- **内心独白(OS) 也进字幕**：`subtitles.md` 收录该 shot **所有发声单元**（含 内心独白 / 系统提示音 / 画外音），与台词配音块一一对应；scaffold 从 `## 台词配音` 全部 `台词:` 行取词，绝不漏掉内心独白。
- **样式 + 自动换行（follow-up wushen_juexing/050）**：9:16 1080×1920 画布、底部居中、白字黑描边；中文 微软雅黑 64、英文 Arial 46；**左右安全边距各 120px（可用宽 840px）、底边距 170px**。**一行排不下自动换行成多行**——`WrapStyle: 0` + 渲染层按每行上限（中文 ≤13 字 / 英文 ≤32 字）把长台词**均分折行**（手机竖屏长台词必折行、绝不溢出边缘）。`both` 模式把中文行 + 英文行合成**一个底部锚定块**（中文在上、英文在下、整体向上堆叠），多行折行也不会与彼此重叠。libass 按实际分辨率缩放。无 UI 调节控件。
- ffmpeg 由 `imageio-ffmpeg` wheel 提供（无需系统安装）。后端实现镜像 frame-extract 特性（`subtitle__writer.py` / `subtitle__command.py` / `subtitle__route.py`），DDD 分层一致。

*(Originated from follow-up "每个 shot 一个台词时间轴文件 + UI 一键把台词按时间烧进 shot mp4" — 2026-06-14.)*

### 11d. 人物出场定格字卡（character intro card / nameplate）— 后期叠层 · 重要角色首次登场

重要角色**首次登场**时：画面**定格亮相（freeze-frame，~0.6–1s 顿一拍）** + 后期叠一张**非剧情（non-diegetic）美工名牌字卡**（角色名 + 一句身份）。这是与 11c 字幕烧录同类的**后期叠层**，**与 prompt 层解耦**——shot 视频 prompt 的 ```text``` 块**绝不写字卡文字**（守 rule 12.4「prompt 不含画面文字」/ K4 / K19 契约；字卡与台词字幕一样由作者后期加）。AI 渲不出可靠中文美工字，故一律后期。

- **生效门槛（只对重要角色）**：仅【主角 / 核心反派 / 关键长线配角】——即在 `concept.md`「核心人物对立」或长线伏笔里有戏份、跨集复用的角色。**单集功能性龙套 / 路人不发卡**（如 ep2 地痞头目·喽啰、叫卖老者、路人甲乙），即便建了简档。**系统 / 金手指不发卡**（它有自己的在画 UI 对话框 motif）。
- **一次性**：同角色**全剧仅在首次登场那一集那一镜发一次**，之后不再发。
- **每集一个 `episodes/epNN/intro_cards.md`**（English/pinyin 路径、中文内容，与 `shotlist.md` 同级）。行式、可 grep，每个重要角色一行：`角色 | 首登 shot | 定格时间点(秒) | 主名 | 副身份 | 字体/样式 | 位置 | 显示时长(秒)`。后期据此在该镜叠卡。无重要角色首登的集可省此文件。
- **shot 侧（不进 prompt 块）**：角色首登镜在 `## Shot context` 加一行 `首登字卡: 角色X 首次登场 → post 定格亮相 + 名牌字卡（见 intro_cards.md）`，并确保该镜有一个**该角色入画稳定、亮相清晰（面朝镜头或清晰侧亮相）的帧**可供后期定格。字卡文字**不写进** `## 视频 prompt` 的 ```text``` 块。
- **美工 / 排版默认（可被 style_guide 项目级覆盖）**：主名大号 + 副身份小号；古风仙侠题材用书法 / 瘦金 / 宋体变体美工字，描金或冷白细描边、配色对齐该剧 style_guide 调色；位置走**下三分之一（lower-third）或角色侧留白**，**避开底部台词字幕安全区**（底部留给 11c 字幕）；入场淡入 + 轻微位移、显示 ~1.5–2.5s 后淡出，定格期间在屏。
- **审查**：`ai_videos__格式契约` 校验——重要角色首登镜有 `首登字卡:` Shot-context 行 + 该集 `intro_cards.md` 有其行；且字卡文字**未混入** shot ```text``` 块（混入=blocker，等同画面文字违规）。龙套被误发卡 / 同角色二次发卡 = warning。
- **产物落点（webapp「🪧 人物卡」烧录）**：输入取 `renders/` 下的原始 take（**不覆盖原片**）；输出落 **shot 文件夹根目录、命名 `shot{NN}.mp4`**（不进 `renders/`），即该镜的成片视频。输出名稳定，**二次烧录覆盖同名 `shot{NN}.mp4`**（除 `renders/` 原片外其余生成物均可覆盖）。shot 根定位解析到最近的 `shotNN` 祖先目录，嵌套 `renders/**` 的 take 也只往 shot 根写；先渲 tmp 再 move，避免读写同文件。与 11c 字幕烧录（输出 `shot{NN}_{zh|en|zhen}.mp4`）落点同规、互不覆盖。

*(Originated from follow-up "重要人物首次登场：定格 + 美工字卡介绍（裴知秋·镇北王府…）；加进流程、全剧默认、只对重要角色、龙套不发" — 2026-06-20；产物落点 per follow-up "renders 下是原片不可覆盖；生成物放外面、直接叫 shot{NN}.mp4、二次烧录可覆盖" — 2026-06-20.)*

### 12. Prompt 模板（导演 + prompt master 视角）

四类 prompt-emitting 文件的强制 schema。Claude 同时以 **导演**（timing / framing / blocking）与 **prompt master**（locked vocabulary, byte-stable descriptors）的身份生成。模板字段顺序固定；缺字段 = stage-6 validation 失败。

> **⚠ 2026-05-25 amendment — 负向 field ABOLISHED across ALL prompt templates.** Per follow-up "所有的提示词，都不需要加负向": the `负向:` line is no longer part of any character / shot / scene prompt schema. Existing prompts have been stripped via `tools/strip_negative_prompts.py` (106 files across 3 dramas). Future prompts MUST NOT include a 负向 line. Below references to `负向` in 12.1 / 12.3 / 12.4 / 12.4-B / 12.4-E / 12.6 / etc. are retained only as historical context — treat them as struck-through. `style_guide.md § 负向锁定` may stay on disk as documentation but is no longer re-pasted into prompts. Stage-6 validators MUST reject any new prompt code block containing a `负向:` line.

> **⚠ 2026-05-25 amendment — `· 念法 (...)` sub-bullets SIMPLIFIED to 3-bullet format.** Per follow-up "尽量要简短，比如此处，直接表达两点，第一不要直接copy，第二此刻场景是太监宣读圣旨，kling应该知道这个场景应该如何变化，第三要把高音量..."): voice direction in shot prompts no longer carries per-字 micro-direction (e.g. `"奉天"二字起势重音 + 略拖音`) — AI video models derive voice modulation from scene context + key voice traits, not per-character timing. The canonical replacement format under any 台词 / 字幕 dialogue line is:
> ```
>   · 念法:
>     - 不要照抄 reference sample 的语气, 按本行重渲染
>     - 场景: <one-line scene/beat description, mirror the shot H1 title>
>     - 关键声音: <character archetype + key voice traits + any non-default constraint>
> ```
> Existing shot prompts migrated via `tools/simplify_voice_direction.py` (13 files / 17 lines, currently nvdi only — mozun_chongsheng + feng_shou_lu have no 念法 lines yet). Future shot prompts MUST follow this format; stage-6 validators MUST reject `· 念法 (...)` lines containing per-字 timing direction or `严禁 X / 严禁 Y` ban-lists (the no-copy and key-voice bullets carry all the model-actionable signal).

> **⚠ 2026-05-30 amendment — 画外音/OS 台词必须显式归属说话人 + 锁定在画人物口型 (避免说话人误判).** Per follow-up "shot2 台词是太监说的, kling 误解成陈国公说的": when a shot's 台词 is spoken by a character who is NOT in frame (画外音 / OS / voice-over / reverse-POV reaction cutaway), video models (observed: **Kling** in `nvdi_tuihun_houhuile` shot02) lip-sync the line onto the most prominent ON-SCREEN face, mis-attributing the speaker. Every off-screen 台词 line MUST therefore carry BOTH:
> 1. an explicit speaker label `【画外音 / OS · 说话人=<角色>(不在画面内)】` (NOT a bare `<角色> OS:`) so the line is not bound to a visible face;
> 2. a `· 在画人物口型:` sub-bullet naming **every** on-screen character and stating they 全程闭口 / 嘴唇不动 / 无说话口型 (听旨方·反应方, 非说话人), 严禁把该台词对到任何在画人物嘴上。
>
> Reinforce in the `动作:` beats (在画人物「全程闭口、无说话口型」) and, in shots that still carry a `负向:` line (起始帧/结束帧 frames), add `不要 给<在画人物>配口型`. **内心独白 / V.O. is the same contract** — the speaker's own mouth must not move (`V.O. 内心 OS 无嘴动`); `shot06` / `shot14` are the reference good-pattern. On-screen (on-camera) dialogue instead names the visible speaker in the 台词 label as normal. Stage-6 validators SHOULD flag any OS / 画外 / V.O. 台词 line whose shot has ≥1 on-screen character but no `在画人物口型` (or equivalent `无嘴动`) directive. Existing nvdi shots fixed: shot02 (full), shot04 + shot11 (OS 余音 over on-screen 陈国公).

> **⚠ 2026-05-30 amendment — shot 块首行 ID 改用紧凑中文标签 `{NN}集{NN}镜{视|始|末}` (适配 Kling 9-字符文件名截断 + 导入匹配).** Per follow-up "kling 用前 9 个字符作为 video/picture 名字": Kling names a downloaded render after the **first 9 characters** of the pasted prompt. The old ASCII first line `epNN_shotNN_{视频|起始帧|结束帧}` truncates to `ep01_shot` at 9 chars — losing the shot number AND block type, so every render in an episode collided on `ep01_shot…` and the import matcher could not route them. **Each shot block's first line is now a compact Chinese tag** `{NN}集{NN}镜{视|始|末}` (集 = episode, 镜 = shot; 视 = 视频 / 始 = 起始帧 / 末 = 结束帧). Example ep01·shot02: 视频 `01集02镜视`, 起始帧 `01集02镜始`, 结束帧 `01集02镜末` — 7 chars, fully inside the 9-char window, and distinct per block (so a shot's two frame PNGs never collide). The import matcher (`downloads__writer.py::_collect_candidates`) adds the `{NN}集{NN}镜` core as a shot-folder token (alongside the retained `epNN_shotNN` / `shotNN` ASCII tokens, so older downloads still match) and routes the file into `shots/shot{NN}/renders/`. Future shot prompts MUST start each fenced block with this Chinese tag. Migrated 213 first-lines across all 3 dramas via a one-time sweep.

> **⚠ 2026-05-27 amendment — `场景视角锚:` and `角色 (一句话锁定...):` body fields ABOLISHED in shot prompts.** Per follow-up "把 shot prompt里所有 场景视角锚 都去掉" + "把角色这一段也去掉": both fields duplicate information already carried by the reference-line header at the top of every shot code block (added 2026-05-24 per rule 12.4-F — `<char>请参考: <drama>_<char>` lines and `<scene>:<drama>_<scene>` line). Body-level repetition is废话 and bloats the prompt.
> - `场景视角锚:` (a paragraph describing which scene-mp4 dwell to anchor to + per-dwell ban list) — REMOVED. The reference-line header already names the scene handle; the model derives the anchor from the rendered scene mp4 + the `镜头:` framing description.
> - `角色 (N 一句话锁定, byte-identical 复制自 character bibles 第 10 行):` block + its indented child rows — REMOVED. The reference-line header already names every character (visible AND voice-only OS, per rule 12.4-F contract #4); the per-character 一句话锁定 in the body just re-prints the same character handle.
> - Single-line `角色: <one-line descriptor>` lines that immediately followed the shot-title line — also REMOVED for the same reason.
> 
> Existing shot prompts migrated via `tools/strip_redundant_fields.py` (20 files / 47 lines across nvdi_tuihun_houhuile + feng_shou_lu; mozun_chongsheng shots are still on the pre-2026-05-24 `{ref_*}` placeholder format and were untouched — they get the new reference header + redundant-field strip together when the user requests the mozun migration). Future shot prompts MUST NOT include either field; stage-6 validators MUST reject a `场景视角锚:` or body-level `角色:` line inside a shot code block.

> **⚠ 2026-05-31 amendment — stage-6 生成 shot 视频 prompt 默认输出「基础骨架版 (basic skeleton)」，描述性维度交由 webapp 逐栏目细化。** Per follow-up (ai_video_management 117) "自动生成的prompt显示一个very basic version + UI 上逐栏目细化": shot **视频 prompt** 在 stage-6 自动生成时不再一次写满每个维度的导演级细节，而是先落一个可直接复制、但刻意精简的骨架，留给用户在 ai_video_management webapp 里逐维度用 ✨ 推荐 (LLM-backed) 细化。契约：
> - **骨架仍含 rule #12.4 的全部必填字段**（顺序不变，缺字段照旧 = validation 失败）—— skeleton ≠ 删字段，而是「字段在、内容精简」。
> - **生成时必须实质填写**（substantive-at-generation）：`场景:` / `镜头:`（景别 + 运动 一行）/ `动作:`（至少 `0–{时长}s …` 一拍，写清主体在该镜做什么）/ `台词 / 字幕:`（三选一 + 台词原文）/ `比例:` / `时长:`。这些是该镜的剧情骨干，缺了无法判断镜头。
> - **允许留精简 stub**（refine-later）：`镜头:` 的逐拍运动细节、`动作:` 的多拍 timed-beat 展开、`运镜:`、`光线 / 色调:` 的光位/层次细描、`节奏:`、`渲染样式:` 的完整关键词组合 —— 生成时给一行概括即可，由用户在 webapp 逐栏目 ✨ 推荐里补足。
> - **字数**：骨架天然远低于全局 2000 字硬顶（2026-06-18）；不得为「凑骨架」而堆砌。
> - **Stage-6 validators 据此放宽**：只校验「必填字段在场 + substantive 字段非空 + 无被废止字段(负向/场景视角锚/body 角色)」，**不得**因描述性维度只有一行 stub 而判 warning/blocker（即不要求生成时就有逐拍 beat / 完整光线层次）。多拍 `动作:` 之和 = 时长 的校验仅在该字段已被展开成多拍时适用；单拍 `0–{时长}s …` 骨架合法。
> - **适用范围**：仅 shot **视频 prompt** body。起始帧/结束帧静帧、角色档、场景档、actor/voice 不受影响，照旧生成完整内容。
> - regen 语义不变（rule #10 / CLAUDE.md regen 表）：重生成 shot 时仍 delete-then-write 整个 shot，写出的就是新的骨架版。

> **⚠ 2026-05-31 amendment — shot 视频 prompt body 内的重复「shot 标题行」`ep{NN} / shot{NN} · {summary} [— {时长}]` ABOLISHED.** Per follow-up "在 shot prompt 里，类似这句话是完全多余的：`ep01 / shot06 · 陈凡 内心独白 + reveal motif checkpoint #1 — 6s`，把这类的语句全删掉": 部分 drama（feng_shou_lu / nvdi_tuihun_houhuile）在 `视频 prompt` 的 ```text 块里、紧跟 reference 头之后，重复写了一行自由文本式的镜头标题（`ep{NN} / shot{NN} · 概述 — 时长`）。这一行**完全多余**——它重复了文件的 `# ep{NN} / shot{NN} · …` H1 标题，也重复了块内 `场景:` / `时长:` 字段携带的信息，视频模型从中得不到任何 actionable 信号，只是占字数。**未来 shot 视频 prompt 的 ```text body MUST NOT 含这一行**；body 的合法首行仍是紧凑中文标签 `{NN}集{NN}镜{视|始|末}`（2026-05-30 amendment），其后直接是 reference 头与各字段。文件级 `# ep{NN} / shot{NN} · …` H1 标题（带 `# ` 前缀、在 code block 之外）是文件可导航标题，**保留不动**。Stage-6 validators MUST reject 任何出现在 shot 视频 prompt code block 内、形如 `ep{NN} / shot{NN} ·` 的行。Existing prompts migrated via `tools/strip_redundant_shot_title.py`（21 行 / 21 文件，feng_shou_lu 7 + nvdi_tuihun_houhuile 14；mozun_chongsheng 从未使用此行，0 命中）。

> **⚠ 2026-05-27 amendment — shot prompts now carry THREE code blocks: 起始帧 + 结束帧 + video prompt. — ABOLISHED per follow-up 2026-06-14 (canonical shot template unification).**
>
> **Status: ARCHIVED.** Per follow-up "武帝觉醒 shot prompt 和 nvdi 差太多 + 统一标准 → 取消起始/结束帧": the `## 起始帧` / `## 结束帧` static-frame blocks are **no longer part of the shot template** and validators MUST NOT require (or reject for missing) them. The canonical shot now carries exactly: ① the 小说原文 / Chapter excerpt prose, ② `## Shot context`, ③ `## 视频 prompt` (single copy-paste block), and ④ `## 台词配音 prompt` for speaking shots (rule 12.4-H below). Reason: the gold-standard drama (nvdi) never adopted the two frame blocks; cross-shot anchoring is carried by description-layer continuity (byte-identical 角色/场景 locks + 走位 world-coords) + the scene-mp4 / turntable reference uploads, same as the seam-frame pipeline (rule 11) it superseded. The historical text below is retained for context only; stage-6 generation MUST NOT emit 起始帧/结束帧 blocks and existing shots may have them stripped on regen.
>
> *(Historical:)* every `shotNN.md` had, in source order: 1. `## 起始帧` (t=0 静帧: `角色姿态 / 位置/构图 / 表情 / 道具`); 2. `## 结束帧` (末帧静态落点, same 4 fields); 3. `## 视频 prompt`. Migrated in via `tools/add_shot_start_end_blocks.py` (71 files).

> **⚠ 2026-05-27 amendment — Webapp ✏ Edit now renders a structured form instead of a raw textarea.** Same follow-up: when the user clicks ✏ Edit on any prompt code block under `ai_videos/`, the webapp (`apps/ui/src/components/PromptStructuredEditor.tsx`) parses the body's `label: value` lines and renders each as:
> - **dropdown** for enum-typed fields (`时长` / `比例` / `节奏`)
> - **textarea** for long-value fields (`动作` / `台词` / `字幕` / `光线/色调` / `渲染样式` / `镜头` / `运镜` / `角色姿态` / `位置/构图` / `场景`)
> - **input box** for everything else (1-line free text)
>
> Freeform prefix lines (reference-handle headers like `<char>请参考: <drama>_<char>`, blank separators) are preserved in a read-only "引用/表头" details panel; they survive round-trips byte-identical. A "📝 原文" mode toggle drops back to plain textarea when the body is too unstructured for the form. Save flow: structured editor serializes back to `label: value` lines → `replaceFirstFencedCode` / `replaceFencedCodeAt` → `PUT /api/file` with `If-Unmodified-Since` (unchanged from prior edit-mode contract). Field-widget dispatch lives in `apps/ui/src/lib/promptSchema.ts::fieldWidget()` — to add a new dropdown enum, extend `_DROPDOWN_OPTIONS` there; to mark a label as long-text, add it to `_TEXTAREA_LABELS`.

> **⚠ 2026-05-30 amendment — shot prompt blocks gain a fixed canonical schema + 人物 multi-select + 场景 picker (`ai_video_management` webapp).** Per follow-up "edit individual prompt … only 3 prompts … 人物 multiple selection, 场景, etc.": the structured editor for the three shot blocks (起始帧 / 结束帧 / 视频) no longer renders only the `label: value` lines that happen to exist in the file — it merges in a **fixed canonical field set** per block so the constrained fields always appear:
> - 起始帧 / 结束帧: `角色姿态` / `位置/构图` / `表情` / `道具`.
> - 视频: `人物` / `场景` / `镜头` / `动作` / `台词 / 字幕` / `光线 / 色调` / `节奏` / `渲染样式` / `比例` / `时长`.
> Missing canonical fields are appended empty (whitespace-insensitive label match avoids duplicates); extra non-canonical lines and the freeform reference/表头 prefix are preserved. Two widgets are added: **`人物` → multi-select** (checkbox group, options = the drama's `characters/cN_中文名/` folders, prefix stripped; value stored as a single `人物: a、b、c` line) and **`场景` → single-select picker** (options = the drama's `scenes/sN_中文名/` folders; the 自定义… escape hatch preserves a per-shot variant suffix like `无寿崖 渡劫态 …`). Options are drama-scoped, derived from the file tree by `apps/ui/src/lib/dramas.ts::extractDramaAssets()`.
>
> **This re-introduces a `人物:` line into the 视频 prompt body**, narrowing the 2026-05-27 "`角色:` body field ABOLISHED" amendment above: characters are again first-class *inside the copy-paste code block* (the user pastes 人物 to the model), in addition to the reference-handle header. The editor writes `人物:` on the first structured save; no bulk migration of existing shots is performed. Implementation: `promptSchema.ts` (`BlockKind`, `_CANONICAL`, `blockKindFromHeading`, `mergeWithCanonical`, `splitMulti`/`joinMulti`, `multiselect`/`select` widgets), `PromptStructuredEditor.tsx` (`blockKind`/`characterOptions`/`sceneOptions` props + `MultiSelectInput`/`SelectInput`), `renderer.tsx` (per-block kind via nearest preceding `## ` heading), `Reader.tsx` (supplies options). Stage-6 validators MUST NOT reject a `人物:` line inside a shot 视频 code block.

> **⚠ 2026-06-14 amendment — 统一 canonical shot 模板 + 台词配音(TTS)层升级为通用标准 + 面部辨识特征.** Per follow-up "武帝觉醒 shot prompt 和 nvdi 差太多 + 我之前的要求没 update 进 refs": nvdi 通过 follow-up 009/010/034 发展出的「导演级 + TTS-解耦」shot 模板此前**只在 nvdi 项目级**（034 明确「不改通用契约」），从未升级进本 ref —— 导致新剧 (wushen_juexing) 生成时丢了整层。现正式升级为**所有 ai_video 剧通用标准**：
>
> **(A) Canonical `shotNN.md` 结构（顺序固定，缺段 = stage-6 失败）：**
> 1. **YAML envelope**（`worker_id / stage / role / work_unit_id / status / blockers / confidence`）—— 每个 shot 文件顶部。
> 2. **`## 小说原文`**（novel-less 剧）或 **`## Chapter excerpt (from chapters/…)`**（reader-side 小说存在时，verbatim blockquote）—— 出场角色名 markdown 粗体（rule 5 ① + follow-up nvdi 005）。
> 3. **`# epNN / shotNN · {summary}`** H1。
> 4. **`## Shot context`** —— `Summary / Characters / Scene / Duration / Reference uploads` 五项。
> 5. **`## 视频 prompt — 复制下方代码块到视频生成模型`** —— 单个 ```text 块，字段顺序: 紧凑中文标签 `{NN}集{NN}镜视` / `参考:` (reference-handle 头, rule 12.4-F) / `角色:` (锁定描述符 + **`面部辨识特征:`** 子句) / `情节:` (该镜对应小说原文, 与第 2 段同源) / `场景:` (场景 handle + 一句话锁定) / `镜头:` / `走位:` (rule 走位契约, 世界坐标系) / `动作:` (timed beats) / `台词:` (正常台词 / 内心独白 二标注 + 口型, 无字幕信息, rule 12.4 v2) / `光线 / 色调:` / `节奏:` / `渲染样式:` / `比例: 9:16` / `时长:`。**不含** `起始帧`/`结束帧`/`负向`/`场景视角锚`/body 重复 `角色:` 行。
> 6. **`## 台词配音 prompt`**（见 (C)）—— 仅有台词的 shot；默剧/静默镜省略。
>
> **(B) `面部辨识特征:`** —— 角色锁定行末尾追加一句**可机检的辨识锚**（如「左脸颊一颗淡褐痣 0.3 厘米」/「眉骨一道旧疤」），byte-identical 复制自角色 bible；用于跨镜同一演员脸的核对。无显著特征的角色可省略该子句。
>
> **(C) 台词配音(TTS)层 —— 升级为通用，推翻旧「v1 不生成 TTS / visuals-only」契约。** 每个有台词的 shot 末尾加独立 `## 台词配音 prompt` 段（一个可复制 ```text 块），字段: `角色 / 音色(锁定·全剧复用 voice_id) / 情绪 / 语速 / 类型(在画对白·画外音对白·内心独白OS·默剧) / 台词(纯文本) / 时长目标`。规则:
>   - **音色一致性铁律**：同一角色全剧/跨集复用**同一 `voice_id`**（如 `TJ-eunuch-01`），不同镜只改情绪/语速、**不换音色**（= 视觉一致性圣经的音频版）。voice_id 锁定在角色 bible / casting.md。
>   - **台词文本**：从该镜 `台词 / 字幕:` 行 + 角色 bible 声线派生；**阿拉伯数字改口语中文**（5→五）。
>   - **音画解耦**：视频**不烧自动字幕、不依赖视频自带 TTS**；台词 MP3 单独生成，后期用 **`tools/mux_av.py`** 把 video MP4 + 台词 MP3 +（可选）BGM 合成成片（视频流 copy 不重编码；BGM 可 sidechain duck 让位人声）。注意这与 rule 11c 的「render-side 字幕烧录」是**两条独立路径**（11c=硬字幕；本层=配音音轨），同剧可二选一或并用。
>   - **默剧/静默镜**：`## 台词配音 prompt` 省略，或标「无台词」并注明属 SFX 的环境音。
>
> **(D) Regen 持久性**：因本层现已进通用 schema，stage-6 regen 重生成 shot 时 **MUST 保留/重生成** 这两层（配音 block + 面部辨识特征），不再像 034-时代那样因「不在模板内」而丢失。
>
> CLAUDE.md「Dialogue… visuals-only applies to audio synthesis (no TTS)」一句同步收窄（见 CLAUDE.md AI-video 节）。rule 12.1 角色档 `## 配音参考` 段不再标「v1 不生成 TTS」—— 它现在就是 voice_id + 声线锁定的权威源，喂给本层。

> **⚠ 2026-06-16 amendment — 改动剧本/台词后默认自动做连贯性 check（衔接相邻镜 + 跨集边界）.** Per follow-up "请确保 ep2 的台词剧情和 ep1 的结尾是连贯的…而且应该是每次改动剧本台词你都应该默认自动 check 的，应该写进 claude 流程里": 任何对 `script.md` / `dialogue.md` / shot `台词:` / 镜头剧情（小说原文/情节/动作/走位）的改动，**完成前必须默认自检叙事连贯性**，不需用户提醒：
> 1. **相邻镜衔接**：本镜与**前一镜、后一镜**的动作 / 站位 / 朝向 / 情绪 / 台词承接是否顺，有无重复或跳脱（如同一「撑身气场反转」beat 在相邻镜重复、走位方向自相矛盾）。**说话人朝向必须对着所说对象**——尤其对**正在离去 / 背对**的对象说话时，写"说话人整个人转身、正面朝其离去方向、目光锁其背影"，**禁"过肩 / 侧身 / 半侧 / 偏头奚落"**，且机位不得让说话人正面朝镜头而对象在其身后（否则渲染成"背对着远去的人说话 / 对空气说"，2026-06-17 shot01 教训；可执行细则见 ai_videos__台词大师 skill C2）。
> 2. **跨集边界**：若改动落在**本集首镜**，对照**上一集结尾**（script 结尾 + 末镜）；若落在**本集末镜**，对照**下一集开场**——确保情绪 / 姿态 / 剧情状态承接，不突兀、不重启、不重复已发生的转折。前集已发生的关键动作（如气场反转、立誓、觉醒）本集**不重演**，只承接其「已发生」状态。
> 3. **台词语体一致**：同角色跨镜/跨集语体对齐，**一律白话文、禁用古语**（见下方 2026-06-16「台词与小说原文一律用白话文」amendment；旧「白话/古文风格统一」选项作废）。
> 4. **契约一致**：藏锋 / 色彩锁定 / 一句话锁定 byte-identical / 时长等既定契约不被本次改动破坏。
> 发现不连贯就**当场surgical修**（改相邻镜或本镜，最小改动）。CLAUDE.md「General coding rules」加一条指向本规则的通用约束。
>
> **§ 全剧序列 review（2026-06-16 增补，per follow-up 050「你需要有个流程把所有 EP 的台词和剧情统一起来 review」）.** 上面 1–4 是**局部**自检（相邻镜 + 单条边界），它能抓「同一动作重演」却**抓不到「整段开场在重复上一集已经收尾的戏」**——典型坑：EP1 末已让主角撂下决裂宣告（"我也不稀罕"+ 升镜黑屏，观感已离场），EP2 S01 又来一段更长的决裂宣告 → 跨集**重复宣告**、开场像重启（"你不是已经走了么"）。局部 pairwise 永远发现不了，必须**通读整条序列**。触发时机：**定稿/重生某集、改动任一集的开场或结尾、或用户要求 review 剧情**时，除局部自检外**额外**做一次全剧序列 review：
> 1. **抽取序列**：把**每一集的开场 beat + 结尾 beat**（script 首尾段 + 首镜/末镜 台词与剧情）和**全部角色标志台词**，按集号顺序排成一条线通读（短剧则按场景顺序）。
> 2. **跨集查重 / 重启**：相邻两集的「开场是否在重复上一集已收尾的 beat / 已说过的宣告」「同一名场面台词或同义宣告是否在两集各来一遍」「开场是否像把上一集结局又演一遍」。前集已**收尾**的戏（决裂、立誓、觉醒、离场），本集只能**承接其后果**，不能重演或再宣告一遍。
> 3. **全剧一致性**：标志台词有无被多镜/多集复用稀释（同一句只该有一个"名场面"出处）；爽点 / 实力 / 藏锋契约跨集是否单调递进、无倒退或提前泄底；身份/伏笔钩子跨集呼应不矛盾。
> 4. **修法**：发现重复/重启就**保留更早（已出片或更靠前）的那一处**、把后一处改成**承接式**（默剧承接 / 推进式新 beat），surgical 改后集，不动已定稿的前集（除非用户许可重渲染）。本条是局部自检的**超集**——多集叙事在宣布"连贯"前必须跑一遍。
> 5. **review 的是「剧情+台词+走位/空间逻辑」整体，不是单条台词（per follow-up 050 二次反馈「你不能只改台词、变得不说话就完了」）.** 把一句重复台词**静音/改默剧并不算修好**——如果背后的**情节与走位**仍不合理（典型：上一集已让主角"宣告+离场感"，本集却把他留在原地连演数镜、又"转身走出"两次 → "他不是已经走了么/怎么还在大厅"），必须**顺着往后改剧情**：重排该 beat 与**其后所有相关镜**的空间状态，让人物的位置/朝向/进出在镜与镜之间**单调连续、动作只发生一次**（如"立定不退"在前、"转身走出"只此一次在后，中间镜一律保持"未移步"）。逐镜拉一条"人物此刻在哪、面朝何方、有没有移动"的空间轨迹核对，发现跳变就改后续镜的走位与剧情，而不是只动台词。

> **⚠ 2026-06-16 amendment — 台词与小说原文一律用白话文，禁用古语/文言.** Per follow-up「现在很多对话显得不自然…要用白话文不要使用古语」: 所有 shot `台词:`、`dialogue.md`、`script.md` 的台词，以及 shot 的「小说原文」段与 prompt 正文里的人物对白/旁白，**一律使用现代白话文（口语化普通话）**，**禁用文言/古语**——不得出现文言虚词与句式（吾 / 汝 / 尔 / 乃 / 之乎者也 / 矣 / 焉 / 哉 / 岂 / 何不 / 未尝 / 不亦…乎 / 安能 / 莫非…耶 等）、半文半白的拗口腔、纯古风格言警句。即便是仙侠 / 武侠 / 古装题材，角色身份与年代差异只通过**用词分寸、语气、称谓**体现，底层语体仍是白话。本条**收紧并覆盖**：① 上文第 3 点「台词语体一致」里允许古文的选项作废——只允许白话；② 12.4-D 的 D1（通俗易懂）/ D4（角色声口）按本条从严执行——D4 的"register 差异"指白话范围内的用词差异，不再以"某角色说文言"实现。成语 / 俗语仅在口语里自然会用时保留，不堆砌古词凑古风。Stage-6 validators 与台词大师 MUST flag 任何残留文言行并改写为白话。
>
> **⚠ 2026-06-17 amendment — 任何 ep/shot 改动 + 出片前，默认跑 `ai_videos__审查总编排` 全维度审查.** Per follow-up「确保之后所有 ep shot 的改动都默认调动这些 skill 来 review 保证质量」: AI 短剧审查已拆成 9 个单一职责 skill（台词 `台词大师` / 站位朝向 `站位朝向` / 运镜 `运镜` / 动作表演 `动作表演` / 时长节奏 `时长节奏` / 光线色调 `光线色调` / 整集连贯 `剧情连贯` / 全剧序列 `全剧序列` / 机械契约 `格式契约`），由 **`ai_videos__审查总编排`** 按「单镜→整集→全剧」编排。**默认工序（不需用户提醒）**：
> 1. **改动后必跑**：任何对 `script.md` / `dialogue.md` / shot `shotNN.md`（台词/情节/动作/走位/镜头/光线任一字段）/ `shotlist.md` 的改动，完成前**默认跑 `审查总编排`** 覆盖受影响范围（改某镜→至少该镜单镜层 + 该集整集层；改开场/结尾→加全剧层）。这取代旧「只跑台词大师 / 只做相邻镜连贯 check」——连贯性 check 现在是 suite 的整集层(continuity)+全剧层(arc)子集。
> 2. **出片前必跑**：stage-6 每个 work-unit 出片前跑整套 suite，blocker 清零方可出片。
> 3. **范围最小化**：suite 按改动落点选层，不是每次全剧全跑——单镜改只跑该镜单镜层 + 所在集整集层；只有动到集边界/定稿整集才触发全剧层。
> 4. CLAUDE.md「General coding rules」的 narrative-edit coherence check 通用约束同步指向本 suite（不再只指连贯性单项）。
> Stage-6 validation level #9 由「短剧故事+台词大师」扩为调用 `审查总编排`。
>
> **⚠ 2026-06-18 amendment — 选角供脸（user-cast face）：脸由角色库选角承载，卡片与 prompt 不再写解剖式五官，只留「角色识别标签」+ 造型全字段.** Per follow-up「我会人工选择角色，因为我有角色库，所以每个 character 面部的描述可以直接选角，但是发型、妆容、服饰其他所有细节都还是需要的」+ 反馈澄清「之后每个 shot 都会上传人物图片，Seedance/Kling 仍靠文字匹配多人物，应保留简要描述帮助匹配正确」: 项目已有 `casting.md`（role → `actor_id`）+ 每角色 `_cast.md` 嵌入 `_actors/actor_XXXX/*.jpg` 选角脸图——**该脸图 = 该角色长相的权威源**。由此对全流程作如下统一收窄：
> 1. **脸＝选角图，文字不再重建五官。** 角色 bible 与所有 prompt **停止用文字描脸**：rule 12.8 锁定描述符字段 **#2「面貌（眉/眼/鼻/唇/轮廓）」删除**；**#3「瞳色」降级**——只保留铁律约束（如「绝不发光 / 绝不挑金光」），不再描具体颜色（图里有）；rule 12.7「5–7 项 micro-detail 五官清单」与解剖式 face-differentiator（痣/疤/三庭五眼/鼻翼唇峰）**一律删除**。这些长相信息由选角图承载，文字重建是冗余。
> 2. **新增「妆容」字段 + 造型字段全保留并仍要写全。** 锁定描述符**新增一行 `妆容`**（素颜/淡妆/伤妆/泪妆/血污/病气妆 等，随剧情态可标变化态）。**保留并仍由文字锁定**：发型/发色、妆容、服饰、标志道具、性别/年龄观感/体型、标志动作、气质、配色、voice_id。**脸以外的一切照旧**。
> 3. **一句话锁定升格为「角色识别标签」（职责从描脸→多人消歧）。** rule 12.8 字段「一句话锁定（≤30字，byte-identical 复制到所有 shot `角色:` 行）」**保留**，但内容**只写画面可辨的造型项**（体型气质 + 发型 + 服饰 + 标志道具），**不写五官解剖**。它的新职责：在**多人物 shot** 里把「上传的哪张参考图 = 画面里哪个人」绑定消歧（见 §4）。
> 4. **shot prompt 的 `面部辨识特征:` 子句（rule 12.4-B）撤销「解剖辨识锚」，改为「角色识别 / 参考图绑定」。** 原「末尾追加可机检的痣/疤辨识锚、byte-identical 复制自 bible」**作废**。改为：`角色:` 行 = byte-identical 复制角色识别标签（§3）；**单人 shot** 只需此标签；**多人物同框 shot** 在 `参考:` / `走位:` 里逐个写死「参考图 ↔ 画面位置 ↔ 识别标签」绑定（如「画面左·裴知秋＝参考图A·清瘦病气少年月白直裰；画面右·裴昭＝参考图B·锦衣骄纵少年」）。**Why（必须保留文字的原因）**：Seedance/Kling 用上传参考图还原长相，但模型不知道画面里哪个人对应你传的哪张脸——多主体 shot 纯靠图片极易串脸/换头/融人，必须靠文字告诉它「有几个人、各自在哪、谁穿什么、谁是谁」。文字职责＝绑定与消歧，**不是**重建五官。
> 5. **turntable（rule 12.5）保留，改吃选角脸。** 每个有人形的命名角色**仍生成 7s turntable 参考视频**，但**输入 = 该角色 `_cast.md` 选角演员脸图 + 本卡的发型/妆容/服饰/道具文字**；turntable prompt 正文**不再写五官**，改写「以上传的参考脸为准，应用如下造型」。渲出的 turntable.mp4 锁定「完整造型」，仍作后续每个 shot 的角色 reference。（非实体角色如「系统」仍用 UI 浮现块例外，无 turntable。）旧 line 107「Seedream 立绘 ref-image prompt」与 line 643「`角色:` line = 一句话锁定 + face-differentiator」同步按本条收窄：立绘/turntable 改吃选角脸，face-differentiator 解剖锚删除。
> 6. **审查 skill 同步。** `ai_videos__格式契约`：**不再**校验五官 byte-identical、**不再**要求 face-differentiator 解剖锚；改校验 ① 角色识别标签 byte-identical ② `妆容` 字段在场 ③ 发型/服饰/道具等造型字段齐全 ④ 多人 shot 含参考图绑定行。`ai_videos__站位朝向`：多人物 shot 校验「参考图↔位置↔标签」绑定写死。`ai_videos__全剧序列`：跨集一致性查的是识别标签 + voice_id（不再查五官描述符）。
> 7. **范围＝流程级**：本条改全流程契约，所有 ai_video 项目（含 wushen_juexing 回填）按此执行。新项目默认走选角供脸。
>
> **⚠ 2026-06-18 amendment — 演技库匹配推荐 + 多选 + 按选择重生（扩展 rule 9b，非新机制）.** Per follow-up「在 shot 里参考演技库里匹配的演技：库里有 structure 信息（情绪大类 / 强度 / carrier / 4s 时长），匹配当下情节就借用过来——借用不是 100% copy，而是合理改成符合当下 shot 后再用；shot 页面显示借用了哪些演技，给我多选项让我挑，挑好后给一个 regenerate 按钮，按新选择重生本 shot 及可能被影响的其它 shot/episode；按钮不直接触发，而是给我一份带全 context 的 prompt，我自己 copy 到 claude session 跑」。**本条扩展既有 §9b（引用表演演技库·标注+融入不照抄，FR-10 v2）+ 既有 `POST /api/regen-shot-prompt`（FR-14c）**，只补三件之前没有的事：自动匹配推荐、用户多选、按选择重生。**沿用 §9b 既有约定**——`表演库参考: perf_NNNN (情绪·强度·风格·载体) — 用于 <角色> <beat>` 标注行 + 「融入不照抄」铁律 + regen 按钮；**不另立 `## 借用演技` 段、不加 `borrowed_performances` YAML 字段**（借用项就记在 §9b 的 `表演库参考:` 标注行）。
> 1. **structure（matcher 用的可机检字段）**：`_performances/{情绪}/perf_NNNN/perf_NNNN.md` 的 YAML `emotion(情绪大类) / intensity(强度) / style / carrier(载体) / au_ref / lma_tag` + `检验视频`时长。锁定文本块＝权威借用源（§9b 已定）。
> 2. **匹配（情绪+强度+时长 → top-N，§9b 之上的新能力）**：对每个带显著情绪的 beat，按 ① 情绪大类对齐 beat 情绪 ② 强度匹配 beat 烈度 ③ 时长贴合（`检验视频`时长 vs beat 时长窗）+ 可选 carrier↔景别（眼神↔特写）自动筛 **top-N 候选**。§9b 原本只规定「标注+融入」，没规定怎么挑——本条补上。
> 3. **借用＝适配非照抄**：同 §9b——把锁定文本块 surgical 改写贴合本 shot（角色名/走位/上下文与该 shot `情节:`/`走位:` 一致），保留 carrier+intensity+AU/LMA 内核；记录沿用 §9b 的 `表演库参考:` 标注行（不新增段/字段）。
> 4. **webapp 增量（本条真正的新功能——现有 FR-14c 只能就「已标注」的 ref 重生，缺“推荐+选择”这一环）**：ai_video_management 的 shot 页 ① 展示该 shot 已标注的借用演技（perf_id + 情绪 + 库 mp4 预览）；② 按 §2 列 **top-N 候选供多选**（照 `CastingView` 选角多选模式）；③ 用户选定后**写回该 shot 的 `表演库参考:` 标注行**（持久化，照 `casting__writer` 原子写 + `If-Unmodified-Since` 冲突检测）；④ 「regenerate」按钮**不直接触发生成**——按当前选择组装带全 context 的 copy-paste regen prompt（扩展 `POST /api/regen-shot-prompt`：除扫已有标注外，支持显式 `selected_perf_ids`），用户自己粘进 Claude session 跑。
> 5. **重生范围 = 本 shot + 受影响邻接**（同 2026-06-16/06-17 连贯性契约）：仅表演变化不影响剧情链 → 只重生本 shot；动到开场/结尾情绪走向 → regen prompt 须把相邻 shot/episode 纳入 context。
> 6. **审查同步**：`ai_videos__动作表演` 校验适配版保留原 perf 的 carrier/intensity 内核且未照抄打架；`ai_videos__时长节奏` 校验库时长与 beat 时长窗匹配。范围＝流程级（所有 ai_video 项目）。
>
> **⚠ 2026-06-19 amendment — `参考:` 行去 `place_holder`，句柄后跟填写分隔符 `=>`.** Per follow-up「`参考:` 行没必要放 placeholder 字样」+「加个分隔符、我自己填 `=>` 之后的部分；不用冒号怕跟 `参考:` 混淆误导 Kling」: `参考:` 行列出本 shot 要 attach 的引用句柄——角色名 + 场景 bg 代号，逗号分隔，**每个句柄后跟 `=>`**（用户在 `=>` 后填该模型实际 reference）。例：`参考: \`裴知秋=>, bg6_座前_虚化背景=>\``（旧 `参考: \`裴知秋：place_holder, bg6_座前_虚化背景_place_holder\`` 作废）。分隔符选 `=>`：不用 `:`/`：`（避免与行首 `参考:` 标签混淆误导 Kling/Seedance），不用单箭头 `→`（视频模型易读成运动方向）。
> 1. **列入规则不变**：本 shot 画面内每个人物（含背影 / 远景 / 剪影）+ 每个场景 plate 都列；纯 OS / 画外音有台词者列声音参考注 `{角色}(画外 OS·声音请参考)`（同样不带 place_holder）。
> 2. **收窄全文残留**：rule 12.4 参考行格式 + nvdi 008 / 009 / 029 等条款里的 `{名}：place_holder` / `{plate}_place_holder` 写法一律去 place_holder 字面（句柄照列）；`## Shot context` 的 `Reference uploads` 行同理。本条只动 `参考:` 行的占位字样，**不改** nvdi-023 可选的「prompt body 人物 placeholder 化」独立机制。
> 3. 范围＝流程级（所有 ai_video 项目）；wushen_juexing 现有 12 shot + 聚合档 + 场景档已回填。
>
> **⚠ 2026-06-18 amendment — Seedance/即梦 内容审核：武器特写 + 真实军事地标触发拒绝（敏感词替换）.** Per follow-up「场景生成失败、内容审核被拒」实测（wushen_juexing 主场景 walk-through 视频被 Seedance 拒，2026-06-18）：视频审核对**武器特写 / 刀剑刃口 / 显式兵器**与**真实军事地标**触发拒绝率高（视频比静图严）。规则：
> 1. **禁武器特写 dwell**：prompt 不写「刀 / 剑 / 长枪 / 刃口 / 錾纹 / 寒光 的长焦特写」；兵戈只能作远景 / 虚化背景陈列、且换中性词，不给镜头怼上去。
> 2. **敏感词替换表**：刀 / 剑 / 长枪 / 兵器架 → 甲胄 / 仪仗 / 陈设架 / 玄铁器物；錾纹刃口 / 重剑寒光 → 玄铁器物金属质感；长城 / 烽燧 / 关隘（真实地标）→ 山川城垣 / 烽台 / 关山 或泛化「北疆山河图」。真人演员名 / 真实品牌 / 受版权 IP 名同理禁入生成块（Kling 对真人名直接拒）。
> 3. **三类 fail 先区分再改**：`InvalidNode / ret=1046`=字数超（全局 2000 顶之外，**Seedance/即梦 实测 ~1500 字符更低**，长 prompt 仍可能挂）；`generation failed: final generation failed`=内容审核（本条）；无 url 无报错=并发限流。改前先认 fail 类型，别把限流 / 字数当审核改。
> 4. **审查同步**：`ai_videos__格式契约` 加 K17 扫武器特写 / 显式兵器 / 真实军事地标候选词并提示替换。范围＝流程级（所有 ai_video 项目）。
>
> **⚠ 2026-06-18 amendment — 全局 prompt 字数硬顶 2000 字（所有 prompt 类型，废止 soft/hard 2500 + 12.4-E 密度例外）.** Per follow-up「请确保场景的 prompt 少于 2000 字」+「给所有的 prompt 设置字数上限 2000」: **每个生成 prompt 的 fenced ```text 内文一律 ≤ 2000 字**（中文/ASCII 各按 1 计；shot 的 `情节:` 小说正文块仍不计入——它是叙事上下文非视觉指令）。**适用所有 prompt 类型**：shot 视频 prompt、场景背景图 prompt、场景 walk-through 视频 prompt、角色 turntable prompt。
> 1. **废止旧上限体系**：旧「soft 2000 / hard 2500」二档 + §12.4-E density 例外（≥8s 单双角色 3500-7000 字、cover-frame 6000-9500 字）+「12.4-E 详细密度优先于字数」裁决 + 超 cap 的 head-loaded truncation-mitigation 例外注释全部**作废**。现在只有一条：**≤ 2000 字 = hard，超 = blocker，无任何例外注释可放宽**。
> 2. **12.4-E 密度照旧但必须在 2000 字内落地**：4-layer-per-beat / 声线物理特征 / 2-4 句光线 等密度要求**不取消**，但作者用**经济语言 + 去重**把它压进 2000 字（删跨字段重复罗列、合并同义元素清单、砍堆砌形容词）——密度靠"信息不重复"实现，不靠堆字。
> 3. **范围＝流程级 + 现在回填**：所有 ai_video 项目；wushen_juexing 现有全部超标 prompt（6 场景朝向块 / 2 场景 walk-through 块 / 4 turntable 块 / ep01 全部 shot 块）本次裁到 ≤ 2000。
> 4. **审查同步**：`ai_videos__格式契约` K10 改为 hard 2000、覆盖所有 prompt 类型、severity=blocker、删 12.4-E 例外豁免。
>
> **⚠ 2026-06-18 amendment — 角色 turntable「统一声样台词」契约（替代 一二三 计数 · 喂 Seedance/Kling 前 3 秒声音采样 · 动作零改动）.** Per follow-up「角色 prompt 里保持动作不变、让角色台词多说一点（现有 turntable 只念一二三）；之后加 trim 截视频前 3 秒做声音采样——念什么由我决定但**要统一**、每个角色念的都一样，方便 Seedance 抓前 3 秒声线细节」。**纯 prompt 约定**（trim 由用户后期/工具做，不写代码）。规则：
> 1. **scope = 角色 reference / turntable（rule 12.5），不是 shot.** 受影响的是每个实体角色卡里的 7s turntable prompt（`characters/{中文名}/{中文名}.md`）。叙事 shot 的 `台词:` **不受本条影响**、保持各自剧情台词。（一个更早的同日草稿曾误写成「每个 shot 前 3 秒前置台词」——以本版 turntable 级为准，覆盖之。）
> 2. **统一声样台词（跨角色 byte-identical）**：所有实体角色的 turntable 念**同一句**固定台词，由本契约锁定为：**`你好，今天天气还不错，外面很安静。`**（中性、白话、四声齐备、不分年代；**非剧情台词、绝不出现在成片**，仅作声线采样）。各角色用**自己的 voice_id / 声线 / 语速**演绎这同一句——统一的是**文本**，音色仍按角色锁定。
> 3. **替代旧"一二三"计数**：turntable 原 0-2s 念"一""二" / 3-4s 念"三"的中文计数（含「3 句数字计数台词」表、"voice baseline byte-identical 跨角色"约定）**全部替换**为本统一台词；台词在 **0–3s（trim 窗口）内念完**，0–2s 正面为主、口型清晰，3s 后静默。
> 4. **动作零改动铁律**：只换"念的内容"，**turntable 的转身相位 / 姿态 / 构图 / 5-phase 时点 / 抽帧点 / 时长 / 光线 / 渲染样式一律不变**。
> 5. **trim 用途**：trim 截 turntable mp4 前 3 秒 = 该角色喂 Seedance/Kling 的**声音采样源**（与视觉 reference = turntable.mp4 整段解耦）。
> 6. **审查同步**：`ai_videos__格式契约` 校验每个实体角色 turntable 含本统一台词且**跨角色 byte-identical**、不残留"一二三"计数（K-新增）。范围＝流程级（所有 ai_video 项目，含 wushen_juexing 回填——本次已做）。
>
> **⚠ 2026-06-14 amendment — shot prompt `台词:` 字段废止字幕三选一，改「正常台词 / 内心独白」二标注.** Per follow-up "在 shot prompt 里，不要提及有关字幕的任何细节，我到时候会自己加字幕，你只需要把台词放上去，标明是正常台词还是内心独白，内心独白嘴是不能动的": shot 视频 prompt 的 dialogue 字段 **label 由 `台词 / 字幕:` 改为 `台词:`**，且**字段内严禁任何字幕信息**（「内嵌硬字幕 / 后期软字幕 / 软字幕 / 硬字幕 / 字幕样式 / 鎏金字幕 / 字体调性（方正粗黑 白底黑边…） / 字幕窗时间 / 不上字幕 / 登场字幕位」全删）。字幕由用户后期自加。字段只保留：① 说话人 + 台词原文；② 类型二标注 `正常台词`（口型随台词开合）或 `内心独白`（**嘴唇不动、不对口型**，靠表情 / 眼神演内心，per nvdi 027）；③ 在画人物口型指令。完整契约见 §12.4「台词契约（v2）」。Stage-6 validators MUST reject 任何 shot 视频 prompt 里仍含字幕字样 / 字体调性 / `台词 / 字幕:` 旧 label 的行。rule 11c 的 render-side 字幕烧录（`subtitles.md` + webapp 一键烧字幕）是**用户后期自加字幕的工具**，与本条不冲突 —— 它读 `台词:` 文本但不要求 prompt 里写字幕样式。
> **⚠ 2026-06-19 amendment — 负面词必须显式禁字幕（光「不写字幕样式」挡不住模型自动烧字幕）.** Per follow-up "shot8 自己带上字幕了，确保所有 shot 都不带字幕"：实测 Seedance/Kling 对**有台词(对白)的镜会自动把台词烧成字幕**，即便 prompt 不含任何字幕样式也照烧（对白越密越爱烧，shot8=4 句对白最明显）。光靠「不提字幕」+ 负面词「画面文字」不够。**铁律：每个 shot 视频 prompt 的 `渲染样式:` 收尾写「全程无字幕、画面不烧任何字幕/台词文字」，`负面词:` 显式含「字幕 / 台词字幕 / 对白字幕 / subtitles」**（系统 UI 文字镜如鎏金对话框例外、不禁「画面文字」、只禁台词字幕）。Stage-6 validator 应检查每个有台词的 shot 是否带这两道显式禁字幕。

**跨模板不变量：**

- 角色 / 场景的「一句话锁定」字符串在所有引用它的 prompt 中 byte-identical（contract 同 rule #4），且与目标 AI 模型无关。
- 比例默认 9:16；项目级 spec 覆盖时记 divergence note。
- 景别 / 运动 / 光影 / 负向词典统一来自 `style_guide.md`；模板只 re-paste，shot 级别**不新造词**。
- **负面词块基线（2026-06-17，必填 contract）**：`style_guide.md § 负向锁定` 的全剧基线**至少含** `人脸变形 / 五官漂移 / 多余发光特效 / 画面文字 / 畸形肢体 / 夸张金光 / 现代服饰`（可按项目/角色/场景追加，不得删基线）。每个 shot 的 `负向` 段 re-paste 此基线；`ai_videos__格式契约` 校验每镜 prompt 负向段在场且含基线项（K15）。该块是 AI 短剧 pipeline 阶段 6 的硬产物（见 `ai_videos__全流程编排`）。
- 「台词」字段（`台词:`）只写 说话人 + 台词原文 + 类型（正常台词 / 内心独白）+ 口型指令；**prompt 内不含任何字幕信息**（字幕用户后期自加），台词音轨由 12.4-H 配音(TTS)层单独生成（详见 12.4「台词契约（v2）」）。
- 「动作」必须以 timed beats 写成（如 `0–3s ... / 3–6s ... / 6–8s ...`），且最后一拍 frozen 状态 = 该 shot 的 `lastframe` 静帧 seam-frame 的「主体定义 / 姿态」描述。
- **模板 model-agnostic**：rule #12.4 schema 不区分目标 AI 模型（Kling / Seedance / Sora / Veo / Seedream / Midjourney / ...）。文件命名 `shotNN_{model}.md` 仅用于区分输出目标，不影响字段定义。

#### 12.1 角色档 — `characters/{role}.md`

````markdown
# {role-name} · {epithet}

## 角色定位
1–2 段：剧中位置 / 出场范围 / 与主角关系 / 段位档位（如适用）。

## 锁定描述符（10 字段，跨集 byte-identical）
| # | 字段 | 值 |
|---|---|---|
| 1 | 性别 / 年龄观感 / 体型 |  |
| 2 | ~~面貌（眉/眼/鼻/唇/轮廓）~~ **删除（2026-06-18 选角供脸）** — 脸由 `_cast.md` 选角图承载，不写文字五官 |  |
| 3 | 瞳色 — **仅记铁律约束**（如「绝不发光」），不描具体色（2026-06-18） |  |
| 4 | 发型 / 发色 |  |
| 4b | **妆容**（新增 2026-06-18：素颜/淡妆/伤妆/泪妆/血污/病气妆…，可标随剧情变化态） |  |
| 5 | 服装（自然色名，无 hex） |  |
| 6 | 标志道具 |  |
| 7 | 标志动作 |  |
| 8 | 气质 |  |
| 9 | 配色（主/辅/点缀/高光，自然色名无 hex） |  |
| 10 | **角色识别标签**（≤30 字，byte-identical 复制到所有 shot `角色:` 行；**只写画面可辨造型**：体型气质+发型+服饰+道具，**不写五官**；职责＝多人 shot 绑定消歧，2026-06-18） |  |

## 性格 / 动机
要点列表：核心动机 / 表层人设 / 反差点 / 关键弱点。

## 标志台词或口头禅
1–3 条 byte-stable 短句。shot 中通过「内嵌字幕 / 后期字幕」复用；可空（默剧角色填「无」）。

## 弧光
1 段：起点 → 关键拐点 → 终点。

## 关键场景
- ep##/shotNN — 一句描述
- ...

## 标志能力或动作
表格（段位 | 能力名 | 视觉关键词）。修真 / 能力题材填段位列；现代题材改填「关键场景动作」列。

## 配音参考（voice_id 锁定 · 喂台词配音层）
`voice_id`（全剧/跨集复用的锁定音色 id，如 `TJ-eunuch-01`）/ 声线 / 语速 / 口音 / 参考演员或角色。**这是 rule 12.4-H 台词配音(TTS)层的权威源**：每个有台词的 shot 的 `## 台词配音 prompt` 块从此处取 voice_id + 声线，同一角色不同镜只改情绪/语速、不换 voice_id。（2026-06-14：撤销旧「v1 不生成 TTS / 本期不下发」—— TTS 配音层已升级为通用标准。）

## 负向
re-paste `style_guide.md § 负向锁定`，可附 1–2 条角色专属（如「不要看起来超过三十岁」）。
````

#### 12.2 角色立绘 — `characters/ref_images/{role}_seedream.md`

````markdown
# Seedream 立绘 prompt — {role-name} · {epithet}

参考: characters/{role}.md
画幅: 9:16 竖屏 / 4K 原生分辨率

## Prompt

{role-name} · {epithet}。{一句话锁定 byte-identical}

### 主体 / 构图
{半身 | 全身}立绘，{正面 | 三七 | 侧面}，三庭五眼 {东方 | 混血 | 西方} 面孔，{年龄观感}。

### 面部
{面貌字段展开：眉/眼/鼻/唇/轮廓}。

### 服装
{服装字段展开 + 主辅点缀 hex}。

### 姿态
{标志动作 + 一个手势细节，frozen 化为静帧描述}。

### 背景
1–2 句概念性背景，对应 `world.md`，主体不被抢戏。色调对齐主/辅/点缀 hex。

### 光源
{方向 + 色温 + 强度}；如有自身散发光晕（魔气 / 仙气 / 系统提示）单独一行。

### 风格
re-paste `style_guide.md § 正向关键词` ≥ 3 个 + 类比真人剧 / 演员参考。

## 负向
re-paste `style_guide.md § 负向锁定` + 角色专属补充。
````

#### 12.3 场景档 + 场景立绘（v2 per follow-up xianxia_new/003）— `scenes/{scene}.md` 单文件

> **⚠ v3 canonical scene template — video-first 多方位背景板系统（per follow-up wushen_juexing/024 — 2026-06-14）。所有场景（现有 + 未来）必须用同一套结构，逐节对齐。** The v2 single-立绘 schema below is SUPERSEDED — kept for archive. The canonical reference实体 is `scenes/s1_裴王府正厅/`. Every `scenes/s{N}_{名}/s{N}_{名}.md` MUST have, in this exact order:
> 1. `# {场景名}`
> 2. `## 场景定位`
> 3. `## 锁定描述符（跨集 byte-identical，自然色名无 hex）` — 8-row table (field 8 = 一句话锁定 ≤30字)
> 4. `## 关键变化态`
> 5. `## 出现镜头`
> 6. `---` → `# 步骤一 · 背景图 seed prompt（Seedream 立绘）— {场景名}` (生成流程 `>` note + `参考:` + `画幅:` + `## Prompt` + ```text``` block; 高清4K + 精准机位)。**这张立绘是 image-first 流程的全局建场底图**（各方向 bg 的图生图 reference，per follow-up 014），落 scene 根 folder。**```text``` 块首行 = pinyin scene handle `{scene}`（无方位词），与步骤二同**——出图工具据首行命名下载文件，webapp 导入按文件名含 `{scene}` 归位到 scene 根；**首行若为 `【场景立绘…】` 等无 handle 文本，导入会漏归位落 `not_matched/`（per follow-up wushen_juexing — 2026-06-19）**。
> 7. `---` → `# 步骤二 · 场景 walk-through video prompt — {场景名}（15s 环视，逐秒方位）` (逐秒方位时间轴 `>` note 5段 + `参考:` + `画幅:` + `## Prompt` + ```text``` block, 时长 15s)
> 8. `---` → `# 背景图系统 index（方位 ↔ 视频秒段 ↔ 截帧时点 ↔ plate folder）` (5-row table + 两条 `>` note)
> 9. **folder-per-plate**: each index row → `scenes/s{N}_{名}/{plate}/{plate}.md` (per-direction static-frame Seedream prompt; PNG rendered into same folder, gitignored). 截帧时点固定 1.5/4.5/7.5/10.5/13.5s.
>
> 适用范围**无例外**：回忆 / 室内单间 / 室外 vista 一律用此结构（室外 vista 的「方位」可改为「角度/framing」，但表结构与节次不变）。**理由**：场景档若各长各样，shot 的场景 reference 就无统一来源、背景跨镜漂移、webapp 截帧路由失配。**任一场景缺 步骤一/步骤二/背景图系统 index 任一节，或 plate 文件夹名≠内层 md 名 = stage-6 blocker。** 单角度场景仍出 5 个 plate（多余朝向留作机动），保证格式一致。

**v2 schema (2026-05-24, SUPERSEDED by v3 above)**: 每场景 1 个且仅 1 个 `scenes/{scene}.md` 文件. Seedream 立绘 prompt 作为 `---` 分隔的第二段嵌入同一文件 (mirror rule 12.5 v3 character 单文件 pattern). `scenes/ref_images/{scene}_seedream.md` 子目录路径 **abolished**.

当 ≥ 2 shots 复用同一地点时，把该地点 lock down 为单一文件，shot prompts 的 `场景:` 行 byte-identical 引用「一句话锁定」。仅出现一次的地点不立档，直接在 shot 级别 inline 描述。

`scenes/{scene}.md`:

````markdown
# {scene-name}

## 场景定位
1 段：剧中功能 / 出场集数 / 与剧情关联。

## 锁定描述符（8 字段，跨集 byte-identical）
| # | 字段 | 值 |
|---|---|---|
| 1 | 类型 / 时代 / 室内外 |  |
| 2 | 空间结构（尺度 / 入口 / 关键区） |  |
| 3 | 主要建筑或自然元素 |  |
| 4 | 标志道具或装饰 |  |
| 5 | 默认光源 / 时辰 |  |
| 6 | 配色 hex（主/辅/点缀） |  |
| 7 | 氛围关键词（≤5 词） |  |
| 8 | **一句话锁定**（≤30 字，byte-identical 复制到所有 shot prompts 的 `场景:` 行） |  |

## 关键变化态
不同时辰 / 天气 / 事件下的变体（白天 / 夜雨 / 战后焦土）。每变体一行 + 必要 hex 调整。

## 出现镜头
- ep##/shotNN — 哪个变体
- ...

## 负向
re-paste `style_guide.md § 负向锁定` + 场景专属（如「不要现代建筑 / 不要西式柱廊」）。
````

**单文件 schema (v2)**: 上述 `scenes/{scene}.md` 文件在 8-字段锁定描述符 + 关键变化态 + 出现镜头 + 负向 section 之后, 紧接 `---` 分隔符, 然后 `# Seedream 立绘 prompt — {scene-name}` H1, 包含 参考 / 画幅 / 默认光影态 + Prompt 段 ([主体]/[细节]/[风格]/[参数]) + 负向 段. 即「场景档 + 场景立绘 同文件双段」.

立绘 [细节] 段与 12.2 角色立绘同构，但替换面部 / 服装 / 姿态 三段为：

- **视角**：推荐拍摄角度 + 焦距感（广角全景 / 标头中景 / 长焦特写片段）。
- **时辰**：默认变体的具体光源描述（晨雾 / 正午 / 黄昏 / 夜雨 / 雷夜）。
- **构图**：9:16 竖屏空间分配（前景 / 中景 / 背景的纵向铺陈）。

#### 12.4 镜头 prompt 模板（model-agnostic 二件套：视频 shot + 静帧 seam-frame）

模板按 prompt **用途**（视频 vs 静帧）分列，**不**按目标 AI 模型（Kling / Seedance / Sora / Veo / Seedream / Midjourney / ...）分列。同一 shot 可同时存在多个 model variant 文件（`shotNN_kling.md` / `shotNN_seedance.md` / `shotNN_sora.md` / ...），它们共享同一 schema；模型能力差异只通过 12.4-A「角色字段展开规则」与「`[参考图]` 行是否出现」两点自动适配。

文件命名约定（rev follow-up 006，不再按 model 分 variant）：

- 视频 shot prompt：`shotNN.md`（单一文件；model-agnostic schema；reference 上传方式由文件 metadata 表达）
- 静帧 seam-frame prompt：`shotNN_{start|last}frame_seedream.md`（seam-frame 仍按 model suffix 命名 — 它们是给 image-only 模型的输入，与视频 shot prompt 用途不同）

视频 shot prompt 文件结构（rule #12.4 v2, post-follow-up xianxia_new/003 — 2026-05-24，seam-frame section 已 abolished, ref_images 路径 已废止 → characters/{中文名}/{中文名}.md folder pattern v4 + scenes/{name}.md single-file 立绘合并）：

````markdown
# ep{NN} / shot{NN} · {1-line shot summary from shotlist.md}

## Shot context

- Summary: ...
- Characters: ...
- Scene: ...
- Duration: Xs
- Reference uploads checklist:
  | 角色 | turntable reference | 备注 |
  |---|---|---|
  | {character name} | `characters/{中文名}/{中文名}.md` → 渲染 7s turntable mp4 (rule #12.5 v11) | {正脸/全景 — turntable 必需 \| 光影/远景 — 无须} |
  | 场景 | `scenes/{location}.md` (含立绘 section, rule #12.3 v2) → 渲染 Seedream 立绘 PNG | 单 PNG, cross-shot 复用 |

---

## 视频 prompt — 复制下方代码块到视频生成模型

> **用法**：复制下方代码块整段，粘贴到任何视频生成模型（Seedance / Kling / Sora / Veo / Runway Gen-3 等）。按"Reference uploads checklist"上传该 shot 的 turntable mp4 + 场景 PNG. **seam-frame PNG 链路已 abolished (rule #11 abolished, rule #5 v2)**: 跨 shot 视觉连续性由描述层 byte-identical (角色一句话锁定 / 场景一句话锁定 / 光线色调 / 渲染样式 / 负向) + 共享 reference mp4 + 共享场景 PNG 承担, 不再依赖 input_image_urls seam frame PNG.

```text
{rule #12.4 v1 prompt body — 14-field schema}
```
````

**出场角色 checklist 派生规则**（per follow-up 006）：

| 角色出场方式 | turntable 是否必需 | 备注示例 |
|---|---|---|
| 正脸 / 主体角色 / 中近景 / 特写 | ✅ 必需 | 「主体角色，正脸可见」 |
| 全景配角 / 跟随主角 | ✅ 推荐 | 「配角，全景出场」 |
| 光影剪影 / 背影 / 远景 / 不具名 | ❌ 无须 | 「仅光影剪影出现」 |
| 物件 / 法宝（角色专属道具） | ❌ 无须 | 「仅道具出现，无人形」 |

> **注（follow-up nvdi 008）**：上表「turntable 是否必需」与「是否列入 `参考`」是两件独立的事。背影 / 远景 / 剪影出场 turntable 可 ❌ 无须，但**仍须列入 `参考` 占位**（用户要 attach 背影 / 远景 ref 图）。只有纯 OS / 画外（完全不入画）才既不列 `参考` 也无 turntable。

静帧 seam-frame prompt 文件头（**ABOLISHED per follow-up xianxia_new/003 — 2026-05-24**）:

~~`# ep{NN} / shot{NN} · seedream {start|last}frame`~~ — 不再生成。

**字段顺序与必填矩阵 (v2 post-003, 视频 shot 单列)** — 缺一即 stage-6 validation 失败:

| # | 字段 | 视频 shot |
|---|---|:---:|
| 0  | `参考:` (reference 占位行) | ✅ — 见下「参考行格式」 |
| 1  | `[参考图]` (`input_image_urls`) | conditional — 仅当目标模型支持 image-to-video 且参考图已生成 |
| 2  | `角色:` | ✅（按 12.4-A 展开） |
| 2b | `情节:` (该 shot 对应的小说正文，verbatim 取自 shot 文件顶部 `## 小说原文` / `## Chapter excerpt` 段；置于 `参考`/`角色` 之后、`场景` 之前) | ✅ |
| 3  | `场景:` (场景档一句话锁定 或 inline) | ✅ |
| 4  | `镜头:` (景别 + 运动) | ✅ |
| 4b | `走位:` (在画人物站位 + 朝向 + 相对位置, per follow-up nvdi 010) | ✅ |
| 5  | `动作:` (timed beats) | ✅ |
| 6  | `台词:` (正常台词 / 内心独白 二标注 + 口型，见下；**无字幕信息**) | ✅ |
| 7  | `光线 / 色调:` | ✅ |
| 8  | `节奏:` (visual-only) | ✅ |
| 9  | `渲染样式:` (re-paste `style_guide.md § 正向关键词`) | ✅ |
| 10 | `比例:` | ✅ |
| 11 | `时长:` (= 15s default per rule #6) | ✅ |
| 12 | `负向:` (re-paste `style_guide.md § 负向锁定`) | ✅ |

(字段 6 主体定义 + 字段 7 姿态 frozen instant 仅 seam-frame 使用, 一并 abolished 随 rule #11 / rule #5 v2.)

**参考行格式（field 0，prompt body 首行）**：`参考:` 行把**本 shot 出场的每个人物 + 每个场景**列成占位清单，供用户逐个替换为实际 reference（角色 turntable mp4 / 场景 ref）：

```
参考: {人物1}=>, {人物2}=>, {场景bg代号}=>
```

- 人物名 + 场景名(bg 代号)取自本 shot 的 `角色:` 行 / Shot context `Characters` + `Scene`；人物在前、场景在后，逗号分隔，**不加 `place_holder` 占位字样**（2026-06-19 收窄）。
- **每个句柄后跟填写分隔符 `=>`**（如 `裴知秋=>`），用户生成时在 `=>` 后填该模型的实际 reference 标记。用 `=>` 不用冒号 `:`/`：`——避免与行首 `参考:` 标签混淆、误导 Kling/Seedance；也不用单箭头 `→`（视频模型易读成运动方向）。
- 多人物 shot 列出全部出场人物；多场景同理。
- **背影 / 远景 / 剪影出场也必须列入 `参考`（per follow-up nvdi 008）**：只要人物在该镜画面内（哪怕仅背影 / 远景 / 侧影），就要在 `参考` 列出 `{名}`（不带 place_holder），以便用户 attach 背影 / 远景 reference 图。turntable 是否必需仍按「出场角色 checklist 派生规则」表（背影 / 远景可 ❌ 无须），但「turntable 无须」**≠**「`参考` 可省」。仅当人物完全不在画面内（纯 OS / 画外音）才不列入 `参考`（视觉占位）——但若其有台词，仍须给声音占位，见下条。
- **背影 / 非焦点人物必须在 `角色:` 给「背影可见」外貌，多个背影必须区分（per follow-up nvdi 031）**：只列入 `参考` 还不够——背影 / 远景 / 侧影 出场的人物，`角色:` 行**仍要给其外貌描述**，重点是**从背面也能看见的特征**（衣色 / 发型 / 发色 / 冠帽 / 体态年龄），脸部细节（痣 / 疤 / 瞳色）可略。**根因（nvdi shot07 实测）**：若 `角色:` 只描述了焦点人物、没给背影人物外貌，且台词 / 情节又在强调某个人，视频模型（Kling）**没有文字线索区分背影**，会把所有背影都渲染成那个被强调的人（观测：两道背影都成了 chenfan）。**当画面有 ≥2 个背影 / 相似人物**时，除各自外貌外，还须在 `走位:` / 入镜人物句**逐一点明每道背影是谁 + 其区分特征（衣色 / 发型）**，并显式写「两道背影衣色发型迥异、各按其参考分别渲染、严禁雷同或都渲染成同一人」。上传的参考图多为正脸，对「背影」帮助有限，**文字区分是关键**。
- **AI-fed 字段用具体角色名、禁关系称谓（per follow-up nvdi 021）**：每个 shot 对生成模型是**独立 context**，模型无跨镜记忆，无法解析「父子 / 父亲 / 儿子 / 二人」等关系/相对称谓指向谁。故凡进入生成的字段（`参考:` / `走位:` / `角色:` / `情节:` / `动作:` 等 ```text``` 块内字段，及 Shot context 的 `Characters`）一律用**具体角色名**（如 `陈国公`、`陈凡`），不用关系称谓。**例外**：`台词:` 内角色口语中的称呼（如儿子唤「父亲」、太监称「令郎」）是自然对白，保留；`## Chapter excerpt` 引用块（`>` 小说原文，不喂模型）保留原文。尤其 `走位:`（决定谁在画面内/何处）出现关系称谓是 blocker —— 模型会无法定位人物。配合上一/下一条：`走位:` 既要用具体名，也要把每个**入画**人物（含背影/前景/远景）列入 `参考:`，每个**不入画**者显式标 `画外/不入画/离去`。
- **人物 placeholder 化 + 生成块无英文（per follow-up nvdi 023，可选·按项目）**：当项目要求 shot prompt 完全自包含、零歧义时，可把 ```text``` 生成块内**所有人物指代**（人名 + 代词「他/他们/其/二人」+ 称谓「老臣/纨绔/父亲/令郎/老奴」+ 台词内人名）统一换成 **`{人物拼音}_place_holder`** 单一 token（如 `taijian_place_holder` / `chenguogong_place_holder` / `chenfan_place_holder`），`参考:` 行的人物条目亦收拢为该 token（`{名}：place_holder` → `{拼音}_place_holder`）。配套：生成块内**除 placeholder 外不留英文单词**——`cinematic`→电影感、`photorealism`→照片级写实、`4K HDR`→超高清高动态范围、`OS/V.O.`→画外音/旁白、`fast-cut`→快切、`mm/cm/s`→毫米/厘米/秒、`reveal/motif`→反转/母题 等全译中文。**例外（保留）**：① **一切「对白」不 placeholder 化（per follow-up nvdi 024 + 025）**——凡是会**被读出 / 显示成字幕**的对白文字（placeholder 会被当字幕渲染出来），一律用**自然人名**（太监 / 陈凡 / 陈国公）+ **保留口语代词与称呼**（他 / 其 / 父亲 / 令郎 / 老奴 / 老臣 / 凡儿 等，按需）。范围**不止 `台词:` 字段**——还包括**嵌在 `情节:` / `动作:` 等字段里、引号内（“…” / 《…》 / 「…」 / "…"）的对白**（同一句台词在叙述里被引用时也算对白）。判定：**引号内（对白）= 自然人名/代词；引号外（叙述/描述）= placeholder**。说话人标签 + 口型注亦用自然人名。②形容/比喻用法的称谓（`老臣沉稳` / `老练阴柔` 是气质描述，非指代）③成语（`判若两人`）④指物的「二物/二者」⑤场景背景 plate 代码（`bg1_朝北_长案主位`，是引用标识非英文词）⑥地名 `陈国公府`（含「陈国公」但是府邸名，不 token 化）⑦Shot context / frontmatter / 标题 等**模板脚手架**（不粘贴进模型，非「prompt」本体）。注意把人名 token 化时须**保护地名**（先挡 `陈国公府` 再换 `陈国公`）并避开 `他人/其他/国公府`；token 化时**跳过 `台词:` 行**。
- **隐含人群的场景须定员 + 负向禁群众（per follow-up nvdi 022）**：宣旨 / 接旨 / 朝会 / 升堂 / 早朝 / 婚宴 / 法事 / 战阵 等**语义上隐含一堂人**的场景，视频 / 图像模型 (Kling / 即梦等) 会按训练数据惯例**凭空补一堆群众 / 群臣 / 围观**（例：太监「今解除朕…钦此」宣旨 + 跪礼区 → Kling 把空厅填满跪伏百官）。即便 `情节` 写了「空旷正厅」也压不住。须双管齐下：① `走位:` **正向定员且点名（per follow-up nvdi 028 强化）**——不要只写泛泛的「仅本镜入画人物」，要**明确写出本镜入镜的每个人物 + 其正面/背影状态**，如「本镜入镜人物仅 {A}(正面)、{B}与{C}(前景下方背影、未露正脸); 别无他人, 不得增添任何其他人物 (无群臣/侍从/围观人群/路人)」，并点出场所性质（如「国公府私宅正厅, 非朝堂金殿」）。点名 + 正背面状态让模型清楚「只有这几个、长这样」，比泛泛定员更能挡掉凭空增添的人。② `负向:` 加 `不要 群臣 / 大臣 / 百官 / 群众 / 围观人群 / 跪伏群臣 / 侍从随从 / 多余人物 / 凭空增添人物`（若项目已移除 `负向` 字段 per nvdi 026，则此条挪到平台反向输入框）。台词里的帝王措辞 (`朕` / `钦此`) 是剧情必需不删，靠点名定员反制其人群联想。
- **画外 OS 说话人的声音参考（per follow-up nvdi 009）**：当某句台词由**不入镜**的角色说出（画外 / OS / V.O.），该角色虽不在画、无视觉 turntable，`参考` 行仍须给出其**声音**参考占位，格式 `{角色}(画外 OS·声音请参考)：place_holder`，供用户 attach 配音参考（与视觉 reference 占位区分）。
- **场景背景参考 = 单 token（per follow-up nvdi 029）**：`参考:` 里的场景背景条目要**和人物参考一样**用单个 `{xxx}_place_holder` token，**不写** verbose 的 `{场景名}·背景图 {plate}：place_holder`。token 用该 shot 的背景 plate 做名（`{plate}_place_holder`，如 `bg2_朝南_厅门_place_holder`，保留朝向信息让用户知道 attach 哪张朝向图）；且 shot 内**所有该场地的引用**（`参考:` + `场景:` 字段的场景名）都用同一个 token。
- **每个 structured 字段值用反引号包裹（per follow-up nvdi 029）**：shot prompt ```text``` 块里每个 `{label}: {value}` 字段的**值用反引号 `` ` `` 抱起来**——`` 镜头: `中近景 + 缓慢推近…` `` ——帮视频模型（Kling）清晰分辨各结构段的边界。所有字段（参考/角色/情节/场景/镜头/走位/动作/台词/光线/节奏/渲染样式/比例/时长）一致处理。
- **`镜头:` 用动态运镜增强关键瞬间（per follow-up nvdi 030）**：`镜头:` 不必一律「锁机位 / 完全静止机位」——**关键情绪 / 反转 / 眼神瞬间**（如「眼神骤然一锐即敛」、冷金锐光凝定、reaction 微表情、阴笑威胁）用**缓慢推近（slow push-in）至面部 / 眼睛特写**来放大视觉冲击；其余镜按情绪 beat 配合适运镜（推 / 拉 / 升降 / 跟）。运镜要**缓、控速、稳、不抖**（避免破坏 Kling 稳定性）；保留景别（中景/中近景/特写）+ 9:16 等信息。
- **每个 shot 必须有场景——含回忆 / 一次性 / 室外镜（per follow-up wushen_juexing/023 — 2026-06-14）**：`参考:` 行「每个场景」的要求**无例外**。回忆镜、闪回、室外、过场等**不复用主场景**的镜，**不得只列人物、省掉场景**——必须为其**建一个（轻量·单角度即可）scene 资产** `scenes/s{N}_{名}/s{N}_{名}.md`（含「步骤一 · 背景图 seed prompt」，声明高清 4K + 精准机位 + 该镜色调，回忆镜统一暖黄泛旧做旧颗粒），并在该 shot 的 `参考:`（`{scene}_bg`）与 `场景:`（`{scene} · 一句话锁定`）双双引用。根因：回忆镜被当成「无背景板」生成时 `参考:` 只剩人物，背景全靠模型即兴、跨镜漂移。**任何 shot 的 `参考:` 缺场景条目 = blocker。** 单角度回忆场景无须 rule 12 的多朝向 plate 系统，一张 bg 背景板足矣。
- **人物近景 / 特写 → 背景浅景深虚化（per follow-up wushen_juexing/023 — 2026-06-14）**：当 `镜头:` 景别为 **特写 / 大特写 / 中近景** 等人物近景时，`镜头:` 行须显式注明 **「人物近景/特写时背景浅景深虚化柔焦、主体清晰」**——把背景柔焦虚化、突出人物，既加强电影质感、也降低背景穿帮 / 漂移风险。中景 / 全景等需要交代环境的镜不虚化（背景须清晰可辨）。该注与 `渲染样式:` 的「浅景深特写」一致、是其在近景镜的显式落地。
- **「系统流」金手指 = 在画对话框（per follow-up wushen_juexing/025 — 2026-06-14）**：系统流 / 金手指类剧的「系统」一切交互（绑定 / 提示 / 选择 / 发奖）应表现为**直接出现在画面中的悬浮 UI 对话框 / 面板**（网文系统流游戏既视感）——半透明描边圆角框、框内字（系统流多用鎏金描边）、选项分行可带【】按钮高亮，主角与观众都看得见框内字；系统文字是**在画对话框内嵌字 + 提示音**（非纯画外音 / 后期软字幕）。**发奖要「送大礼」仪式感**：弹「恭喜宿主获得：X」贺词框 + 礼花光效 + 光门 / 礼匣自框炸开把奖励加身——而非平淡兑现。`情节:`/`走位:`/`台词:`/`光线:` 各字段都要点明对话框的位置与框内字，让视频模型把它当画面元素渲染。
- **shot 视频不烧任何字幕 / 文字（per follow-up wushen_juexing/033 — 2026-06-15）**：shot `视频 prompt` **不得指示模型在画面里烧入台词字幕 / 硬字幕 / 文字**——`台词:` 字段**只保留**说话人 + 台词原文 + 语气 + `口型归X` / OS 画外注（供模型对口型与后期配音），**删去**「内嵌硬字幕 / 硬字幕 / 白底黑边 / 字幕」等任何「把台词显示在画面上」的措辞；并在 `渲染样式:` 末尾加 `· 画面不烧任何字幕文字（台词后期另加）`。字幕由作者后期叠加。**例外（保留，属画面元素而非字幕）**：系统流的「系统对话框 / UI 面板内嵌字」（rule 12.4 系统流条）、剧情中本就存在的牌匾 / 信件 / 告示等 diegetic 文字。转场「下一集」等卡字也后期叠加（prompt 只留黑屏转场、不写字）。
- **`台词:` 字段必须保留台词正文 + 全员无口型镜防「读台词乱套」用强标画外配音而非删文（per follow-up wushen_juexing/037 修订 → 039 — 2026-06-15）**：⚠ 037 一度规定「全员无口型镜不写台词正文」，**实测错误已废**——视频模型（Seedance）正是从 `台词:` 文本生成台词配音的，删掉正文导致成片**完全没有台词声音**（shot05 剥离后变哑）。故**任何镜的 `台词:` 都必须写出台词正文**。先前 Seedance「读系统台词乱套」的真因是**画外音被硬 lip-sync 到某张在画脸上**（系统提示音安到主角脸做口型），而非「文本存在」。**正解**：保留台词正文，但对每句**画外 / OS / 系统**台词在 tag 里强标 `画外配音 voice-over` + `内心独白 OS` + `嘴唇不动不对口型`，系统句再加 `无任何在画人物对此口型/嘴动`；系统流对话框在画 UI 字（选项【】按钮等）照写。这样模型照常出台词音、又不会把画外音 lip-sync 到脸上致乱。**混排镜**：在画对白句标 `口型对X`，画外 / OS 句标 voice-over + 不对口型。
- **shot 时长须容得下台词（防语速飙）+ 上限 15 秒（per follow-up wushen_juexing/040 — 2026-06-15）**：一镜**总台词字数 ÷ 时长(秒) 应 ≤ 5**（目标 ≈ 4 字/秒；情绪 / 独白镜约 3 字/秒；多说话人镜各句字数相加），否则配音被迫加速、像抢词（实测 shot09）。超标三选一：① 加时长（**硬上限 15 秒**，不得突破）；② 精简台词（砍废字留因果，rule D3/D6）；③ 拆镜（一镜拆两镜各给够时长 + 连续性 token）。改后 shot `时长:` / 各句 `时长目标`(之和 ≤ shot 时长) / 台词字数 三者自洽。
- **`台词:` 字段排版标准（per follow-up wushen_juexing/034 — 2026-06-15）**：多说话人 / 系统 + OS 混排的 `台词:` 若挤成一行、且台词用 `"…"` 包裹又内嵌 `『』「」` 等引号，会让视频模型（Kling）分不清「哪段是台词、哪段是注释、谁说的」而渲染混乱。**标准结构**——`台词:` 行先写一句说明 `（画面不显示文字、仅供口型与配音参考；逐条↓）`，随后**每个发声单元各占一行**，格式 `· {说话人}〔{类型·口型注}〕：{台词正文}`：类型用 在画对白 / 内心独白 / 系统提示音(对话框UI字·不对口型) / 旁白；正文**纯文本、不加任何引号**（`"" 『』 「」` 全免，杜绝嵌套）；系统名等专名直接写（不加 `『』`）。一行一句、tag 与正文以 `：` 分隔，模型一眼可辨。系统二选一等含内部 `；：` 的台词照写正文即可（不再被外层分隔符歧义）。
- **场景背景图系统（per follow-up nvdi 011 + 013）**：仅标注 scene 名不足以保证背景一致。每个 scene 须**成体系生成多张不同面相 / 方位的背景图**（朝向 北/南/东/西 + 俯瞰 + 案前虚化 等）。**folder-per-朝向 结构**（rule 12.9 folder-per-asset 同源）：每个朝向一个子 folder `scenes/{scene}/{plate_id}/`，folder 内放该朝向的 prompt md `{plate_id}.md`，生成的 PNG 存回该 folder `{plate_id}/{plate_id}.png`。scene 主档「背景图系统」段只放 流程 + 索引表 + 命名约定（不再内联各朝向 prompt）。
  - **生成流程 image-first → 各方向 image→image（per follow-up wushen_juexing — 2026-06-19，取代 06-18 的「mp4 抽帧为主」）**：① 先用 scene 主档「步骤一 · 背景图 seed prompt（Seedream 立绘）」(text→image) 出**一张全局建场参考底图**（覆盖空间结构 + 材质 + 配色 + 光源）。② **各方向静帧主路径 = 图生图（image→image）**：逐方向用该方向 `{plate_id}.md` 的 image prompt + **上传全局底图作 reference** 出图——参考图锁材质/配色/光源/风格一致，prompt 驱动该方向机位/构图/主体（prompt 须写全该方向几何，单靠底图不足以转向）。③ scene 主档「步骤二 · walk-through video prompt」(15s) 仍生成 `{scene}.mp4` 存 scene 根 folder，但**用途 = 后续 shot 的视频 reference**，**不再是方向背景图来源**。④ **抽帧（webapp「🧭 截取方向背景图」按「背景图系统 index」表截帧时点）= 兜底**：某方向图生图转不过去（朝南 reverse / 俯瞰）或想快速打底时，从 walk-through 抽一张含正确机位的帧**作图生图 reference**再精修。**⚠ 平台能力铁律：AI 平台不支持「上传 mp4 → 生成图片」**——上传视频只能出视频、上传图片只能出图片；取静态图只能 ①图生图 或 ②从视频抽帧，**不能「文字 + 上传 mp4 → 出图」**。**为何 image-first 取代抽帧为主**：15s walk-through 每方向 dwell <1s、分辨率/锐度/压缩受限，抽出的方向图质量偏低且机位不稳；逐方向图生图质量更高、且共用同一全局底图作 reference 使跨方向材质/配色/光源更一致。`bg{N}_座前_虚化背景` 等浅景深层图生图时加「背景浅景深虚化」，或从长焦 detail dwell 抽帧打底再精修。**画幅非 load-bearing（per follow-up wushen — 2026-06-19）**：场景立绘 / 各方向 plate 是**纯 reference**（image→image 的材质/配色/光源锚 + shot 的视频 reference），其画幅不必 9:16——**16:9 横版完全可用**（视野更全、给模型空间信息更多），shot 视频由 kling/seedance 按生成参数 9:16 出、自动重新取景，reference 比例不传导到 shot。故不要把场景参考图的 16:9 当成错误来报；唯一需 9:16 的是把图当**最终背景直接合成**的情形（本流程 plate 只作参考、不直接合成）。导入覆盖语义：plate folder 只存一张 canonical 图，重导同方位**直接覆盖**旧图。
  - **命名 / 导入约定（per follow-up nvdi 015；2026-06-19 wushen 重写——importer 改 方位 路由）**：朝向 folder 命名 **必须** `bg{N}_{方位}_{描述}`，**方位段**（`朝北`/`朝南`/`朝东`/`朝西`/`高位俯瞰`/`案前`/`座前` 等）是 plate 归位键，且 plate prompt ```text``` **首行 = plate_id（`bg{N}_{方位}_{描述}`）**——方位在前 8 字内，**抗出图工具文件名截断**（实测 kling 把下载名截到 prompt 前 ~10 字、方位幸存、长 pinyin handle 会被截掉，故**不要**在首行前缀 scene handle，会把方位挤出截断窗）。`DownloadsImporter` 路由：① 先 `_classify` 按 filename 含 scene/character/shot name token 匹配；② **未匹配到 scene 名时，按 filename 含的方位 token 在全 drama 各 scene 的 plate folder 里找唯一匹配**（`_match_plate_any_scene`，跨 scene 同方位歧义则按 filename 是否含 scene token 消歧，仍歧义→`not_matched`，绝不静默串档），归位重命名 `{plate_id}.png`、覆盖旧图。**全局立绘 `.png` / walk-through `.mp4`** 无方位 → 靠 ```text``` **首行 = pinyin `{scene}` handle**（如 `zhenbei_wangfu_zhengting`，截断后 `zhenbei` 仍是 scene token）匹配 scene、留 scene 根。**只匹配方位段、不匹配描述段**——描述词（`厅门`/`东侧`…）会散落在别朝向文件名里串档。
  - shot 的 `参考:` 行场景占位必须指明**具体哪一张**：`{场景名}·背景图 {plate_id}：place_holder`（而非泛泛的 `{场景名}：place_holder`）。用哪张依本 shot 相机朝向（相机看向哪面 → 用对应方位的 plate），由 scene「站位 / 走位锚」推导。
  - **文件名截断与方位路由（2026-06-19 wushen 实测——supersedes nvdi 015「方位段进主体行」对 pinyin folder 的部分）**：① 出图工具（kling）把下载文件名截到 prompt **首行前 ~10 字**（遇 `:` 等特殊字符更早断），所以归位键必须**短、且方位在最前**——plate 用 `bg{N}_{方位}_…`（方位在 ~5 字处幸存），**不要**前缀长 pinyin handle（会把方位挤出窗口、误判成 scene-root）。② importer 不再要求 filename 同时含 pinyin scene token——`_match_plate_any_scene` **只按方位 token 跨 scene 找唯一 plate**（单 scene 必中；多 scene 同方位才需 scene token 消歧）。这把「只有方位、没有 scene 名」的真实下载名（`bg1_朝北_高座主…`）也救回。回归测试见 `tests/test_downloads_import_shots.py::test_scene_plate_routes_by_orientation_when_no_scene_token`。
  - **质感 / 美术方向（per follow-up nvdi 014 + 016）**：场景背景图 / 视频 prompt 须强调**真实材质质感（木纹包浆 / 石材纹理 / 漆面微裂 / 金属氧化 / 织物 / 斜光浮尘）+ 制作精良置景美感 + 空间纵深**，且 `负向` 始终强禁 `卡通 / 动画感 / anime / cartoon / 国漫 / 塑料质感 / 扁平光 / 廉价置景`（防卡通化、扁平、廉价）。在此真实质感打底之上，**美术方向是 per-project 选择**，scene prompt 的 `风格:` / `负向:` 行跟随项目美术方向：
    - **默认 = 影视级真人实拍写实**：加 `超写实 photorealism`，`负向` 额外强禁 `CG 渲染感 / 3D 游戏场景`。
    - **唯美古风（opt-in）= 电影级唯美打底真实**：真实材质打底 + 叠加唯美元素（鎏金描金 / 云雾 / 飞花 / 纱幔 / 烛火宫灯 / 琉璃 / 丁达尔光束 / 暖金 bokeh）+ 宝石色调。⚠️ **重要失败模式（per follow-up nvdi 019）**：此方向若**同时**①放宽反 CG ②挂游戏参考锚（剑网3 / 逆水寒）或《阴阳师》等 CG/奇幻片 ③堆光效粒子（暖金 bokeh / 浮尘流光 / 飞花 / 金箔流光 / 光尘），生成图会**卡通化 / 动画片 / 出现星点闪光 / 色彩过饱和**——即便上传的参考 video 是写实的，prompt 的 `风格:`+`负向:` 仍主导输出。故唯美方向**高风险**；只在用户明确要奇幻梦幻感时用，且须收住粒子量。
    - **「无比真实 / 照片级写实」配方（per follow-up nvdi 019，默认推荐）**：要真实就必须反向操作——① `风格:` 用「影视级真人实拍写实 · 超写实 photorealism · 照片级真实 · 真实自然光 · 自然不过饱和不偏色」；② 参考锚用**真人实拍 / 实景搭建**（《妖猫传》唐风实景 / 《长安十二时辰》/《清平乐》/《梦华录》/ 故宫·山西古建实拍 / 专业建筑摄影），**严禁游戏锚与 CG/奇幻片锚**；③ `负向:` 强写 `不要 动画片 / 动画感 / CG 渲染感 / 游戏画面 / 3D 游戏场景 / 渲染感 / 星星 / 星光 / 闪光粒子 / 漂浮光点光斑 / 梦幻光效 / 过度光晕 / 过曝 / 过饱和 / 偏色`；④ 光线写**真实自然窗光 + 极淡自然浮尘（写实非闪光）+ 自然柔和反光（非镜面发光）**，去掉一切粒子光效。雍容华贵的陈设/建筑/书画**内容照旧保留**，只换渲染风格层即可两全。项目选定后在 `specs/{type}/{name}/` 记 divergence 并全场景统一（nvdi 现采此「照片级写实 + 唐宋雍容华贵内容」方向）。
    - **场景陈设完整性 + 朝代定位（per follow-up nvdi 017）**：雍容华贵 / 唯美向场景，prompt 须显式描述**室内陈设细节**而非只给空间骨架——至少覆盖 ① **墙上花纹**（障壁画 / 织锦壁衣 / 墙裙纹样，非默认素壁）② **地面**（明确方砖墁地 vs 地毯 vs 二者并存，给纹样）③ **陈设书画**（书画立轴 / 屏风 / 架格陈设器物）④ **雕刻 / 图案 / 彩画 / 顶部藻井**。并须**明确朝代定位**（如唐宋 / 明清），prompt 内家具 / 彩画 / 器物 / 纹样**不得跨朝代穿越**（例：定唐宋则禁 太师椅 / 博古架多宝格 / 景泰蓝掐丝珐琅 / 和玺旋子彩画 / 抱柱楹联——这些是明清元素；改用 宋式高背官帽椅·壸门券口 / 紫檀架格 / 唐三彩·宋青瓷 / 碾玉装·五彩遍装彩画 / 障壁画屏风）。朝代定位写入 scene prompt `风格:` 行并在 `specs/{type}/{name}/` 记录。
    - **`负向` 字段可按项目从生成块移除（per follow-up nvdi 026）**：prompt ```text``` 块里的 `负向:` / `[负向]` 字段**不是必须**——项目可选择整体移除（反向约束改放平台独立的「反向提示词」输入框，或干脆不用）。本 ref 里各处「`负向` 应含 X」（反卡通 / 反群众 / 反星点 / 平台合规等）规则**仍定义"要抑制什么"**，只是承载位置可从生成块挪到平台的反向输入。nvdi 现已移除全部 prompt（28 shot + 6 朝向 plate + walk-through 视频 + 立绘 + scene 主档 `## 负向` 段）的 `负向` 字段。
    - **平台内容审核合规（per follow-up nvdi 020 — 即梦/Seedance/Dreamina 等）**：喂给国内 AI 出图/视频平台的 prompt（plate / walk-through / 立绘 的 ```text``` 块）会过内容审核，违规报「prompt 不符合平台规则」直接生成失败。必须规避：① **显性 + 隐性 IP**：prompt 内**禁止出现任何 影视剧名 / 画作名 / 景点名 / 游戏名 / 真人(导演/演员/作者)名**（如《妖猫传》《长安十二时辰》《清平乐》《梦华录》《捣练图》《韩熙载夜宴图》故宫 / 剑网3 / 逆水寒 / 阴阳师 / 郭敬明）——参考锚改为**不点名的通用描述**（「质感对标真实电影实景搭建的古装厅堂 / 真实唐宋古建筑实景照片 / 专业建筑摄影」）。② **画面文字**：prompt 内**不写引号待渲染文字**（如匾额「勤政」、圣旨「奉天承运」）——改「素面无字匾额」，并在 `负向` 写「不要在画面渲染任何文字」（平台对文字+冒号、引号文字敏感）。③ **敏感政治/帝王词**：弱化 圣旨 / 诏书 / 奉天承运 / 朝堂 / 接旨 / 女帝 / 退婚 等（生成块改 古典厅堂 / 礼仪空地 / 案面陈设简洁；剧情设定保留在 `specs/` 与 scene **metadata**，不进 ```text``` 生成块）。④ 平台**真人素材参考能力**可能被暂停，人脸/人声属敏感个人信息——角色一致性靠**纯文字描述 + 自有参考图**，勿在 prompt 提真人。**生成块力求"只描述画面、不点名、不含待渲染文字、不涉政治"。**
    - **建筑木作 + 朝代措辞 + 参考锚（per follow-up nvdi 018）**：① 「屋内细节不够」时补**建筑营造层**（非只陈设）——梁架 (月梁/阑额普拍枋/铺作斗栱/叉手托脚) + 顶棚 (斗八藻井/平棋/平暗) + 门窗 (唐宋直棂窗/破子棂窗/毬文格子门，非明清雕花窗) + 台基 (须弥座/勾栏望柱) + 柱础 (覆莲)；唐宋可标「营造法式」。② 朝代穿越检查须含**道具措辞 / 文字**：定唐宋则禁「奉天承运」圣旨开头 (明初朱元璋始创，明清专属)。③ **per-shot 剧情道具不烤入静态背景**：场景背景 plate / walk-through 是跨 shot / 跨集复用的「纯背景」，接旨诏书一类**随 shot 变化的剧情道具**应由 shot (太监展开) 提供，不写进 scene 静态背景 prompt；scene 的「一句话锁定」LOOK 串亦不含 transient 道具。④ 细节密度不足时，prompt `风格:` 行可挂**游戏级唐宋场景参考锚**（《剑网3》唐风家园厅堂 / 《逆水寒》宋构汴京·《营造法式》体系）以拉高精雕密度。

*(Per follow-up：用户要求 `参考:` 行把本 shot 全部人物与场景列成 `{名}：place_holder` 清单。三项目既有 203 shot 已全量改写。)*

**12.4-A 角色字段展开规则**（v3 per follow-up 013 — supersedes earlier "无参考图必须 inline 展开" hardcode）：

**Shot prompt 角色 line（rule #12.4 v4）**：
- `角色:` line = byte-identical 一句话锁定 + face-differentiator only (~50-80 字/char)。
- **不在 shot prompt 内 inline 展开** body / 发型 / 服装 / 道具 / 5-7 项 micro-details — 这些信息已经 carry 在:
  1. character ref turntable prompt（同角色文件第二段，上传 turntable.mp4 后 AI 模型从视频 inherit）
  2. character bible 锁定描述符 #1-#11 段（user 可手动喂模型作为 system prompt 的一部分，但不强制）
- 这样 shot prompt 字数从 ~250 字/char trim 到 ~80 字/char，缓解 6-char shot 角色 line 1500 字 → 480 字。

**Character ref turntable prompt 角色 line**（rule #12.5 v3 内部 — 与 rule #12.4 解耦）：
- 仍含 完整 inline expansion + 5-7 项 micro-details（per rule #12.7 v2）—— turntable mp4 渲染时 AI 据此构建角色形象，formal anchor。

**Multi-character shot (≥ 4 角色)** 进一步限制：shot prompt `角色:` line 仅含**前 3 个主体角色**的 locked 一句话 + face-differentiator；其余角色用 1 句话概括（如「其余 5 宗主背景出场（参考各 c{N} character refs）」）。

**Prompt 字数上限契约（rule #12.4 v4 / NFR-17）**：

- **Hard limit: 每个生成 prompt body（fenced ```text 内文）≤ 2000 字**（中文字符 + ASCII 一律按 1 计）。**适用所有 prompt 类型**——shot 视频 prompt / 场景背景图 prompt / 场景 walk-through 视频 prompt / 角色 turntable prompt 一律 ≤ 2000 字，**无 soft/hard 之分、无 cover-frame / 长 shot / 12.4-E 密度例外**（2026-06-18 amendment「全局 2000 字硬顶」收窄，覆盖旧 soft 2000 / hard 2500 + 12.4-E 例外）。超 2000 = blocker。
- 字数计 fenced ```text 内文（不含 ``` 标记 + 不含 Shot context / Reference placeholders 段 + 不含 Seam-frame still prompts 段）。
- **`情节:` 字段（field 2b）不计入 字数上限**：它是给模型的叙事上下文（小说正文 verbatim），非视觉指令；视觉指令字数预算（soft 2000 / hard 2500）只统计除 `情节:` 块之外的 prompt body 文字。

*(Per follow-up：用户要求把每个 shot 对应的小说正文也放进视频 prompt，置于 参考/角色 之后、场景 之前，字段名 `情节:`。三项目既有 shot 已全量回填。)*

**渲染样式 / 负向 字数 trim 政策（rule #12.4 v4）**：

- 渲染样式 line ≤ 9 核心 keywords（推荐组合：影视级真人写实 + cinematic + 4K HDR + 真实毛孔细节 + 真人皮肤真实质感 + 亚洲俊男靓女 + 三庭五眼东方面孔 + 仙侠真人剧主演级颜值 + photorealism 强化 1 项）。
- 负向 line ≤ 24 核心 items（去重 anime/cartoon/manga 变体；保留 14 项 stylization 核心 + 5 项 AI-同质化 + 5 项 photorealism + 项目专属如 不要现代服饰 / 不要文字水印 / 不要多余手指 / 不要镜头穿模）。

规则与目标模型解耦：参考图存在与否、模型类型差异、photorealism 关键词总数等都不影响 字数上限契约。

**Markdown-style 视觉渲染契约（rule #12.4 v4 + rule #12.6 v3 amend per follow-up 013）：**

- Webapp 渲染 ```text fenced code blocks 时，对 prompt body 内 field labels (`角色:` / `场景:` / `镜头:` / `走位:` / `动作:` / `台词 / 字幕:` / `节奏:` / `光线 / 色调:` / `渲染样式:` / `比例:` / `时长:` / `负向:`) 应用 CSS field-label highlight (推荐 暖橙色粗体)。
- Implementation: ReactMarkdown `pre` component override (`CopyableCode`) parse children → split by line → 行首匹配 field label 时 wrap label 在 `<span className="field-label">` 内；rest of line 原样。
- innerText / clipboard 行为保持纯文本（user click copy 复制纯文本，无 HTML markup 损失）。
- 视觉效果：prompt body 看起来像结构化 markdown 文档（field-value layout），而非 plain monospace 块。

**镜头取词契约**：景别 / 运动必须出自 `style_guide.md § 镜头语言关键词字典`（每个项目须维护至少景别 + 运动两张表）；`镜头:` 行格式 = `{景别} + {运动}（一句运动节奏描述）`。静帧 seam 行格式 = `{景别}` 单独。

**走位 / 站位契约（per follow-up nvdi 010）**：每个 shot prompt 必须含 `走位:` 字段（置于 `镜头:` 之后、`动作:` 之前），描述本镜**每个在画人物**的 ① 在场景中的位置（锚定 scene 方位 / 区域，如「长案前」「跪礼区」「厅门内」）② 朝向（面向谁 / 面向哪个方位，如「面向南侧的父子」）③ 与其他在画人物的相对位置（如「太监在父子正北、下首南北相对」）。**单人镜也必须写**该人物相对场景的位置与朝向（如「陈国公跪于跪礼区东侧、面向北朝太监，侧脸向西窗光」）。方位锚与默认站位由 scene 档「站位 / 走位锚」段提供，shot 级 `走位:` 从其派生、byte-stable 复用；用**世界坐标系（东/南/西/北 + 面向对象）**描述，**不用随相机翻转的「画面左/右」**（相机角度由 `镜头:` 负责）。画外 OS 说话人若有明确方位（如太监 OS 在画外北侧）也可注明，帮助模型摆正在画人物的视线朝向。

**眼神 reveal / 锐光表达契约（per follow-up nvdi 012）**：人物「眼神转锐 / 冷光 / 锋芒 / reveal」类 motif 必须用**眼神 / 神态**语言表达——瞳孔微缩、眼睑收紧、目光如刃 / 冷冽 / 凌厉、眼神一凛、神色转厉、眉峰收紧 + gaze 方向——**严禁写成「眼睛发光 / 放光 / 锐光 / 眼内光效 / 冷金锐光」等会被生成模型当作字面发光 / 超能力光效渲染的措辞**（`情节:` 小说正文里的文学化「锐光」可保留, 但 `动作:` 视觉指令必须用神态语言并加注「纯眼神 / 神态, 非发光」）。`负向:` 必须含 `不要 眼睛发光 / 不要 瞳孔发光 / 不要 眼内光效 / 不要 超能力发光特效`。根因: Kling 等模型把「光」字面渲染成眼睛射光, 人物看起来像有超能力 — 表达措辞直接决定成片。

**动作 timing 契约**：

- beats 时长之和 = `时长:` 字段。例：8s shot ⇒ 必须落成 `0–3s ... / 3–6s ... / 6–8s ...`。
- 最后一拍 frozen 状态 = 该 shot 的 `shotNN_lastframe_seedream.md` 中 `主体定义` + `姿态（frozen instant）` 描述。两文件同时改、同时保（regen 时一起删一起写）。
- 中间拍可省略（一拍到底），但必须显式写「`0–{时长}s ...`」，避免 stage-6 validator 误判 missing。

**台词契约（v2 — 2026-06-14，废止字幕三选一）**：字段 label 为 `台词:`（不再叫「台词 / 字幕:」）。**shot prompt 内严禁出现任何字幕信息**——字体 / 字号 / 位置 / 颜色 / 描边 / 字幕窗时间 / 「内嵌硬字幕」「后期软字幕」「软字幕」「硬字幕」「字幕样式」「鎏金字幕」「不上字幕 / 不烧字」「登场字幕位」等一律不写。**字幕由用户在后期自行添加**，prompt 不碰。`台词:` 字段只携带三样东西：

1. **说话人 + 台词原文**（引号内）。
2. **类型二选一标注**：
   - `正常台词` —— 在画 / 在镜说话，**口型随台词开合**。
   - `内心独白` —— OS / 画外心声，**嘴唇不动、不对口型**（在画人物全程闭口，仅靠表情 / 眼神 / 神态把内心演出来，per nvdi 027）。
3. **口型指令**（rule 12.4 在画人物口型契约，保留）：正常台词 → `口型对{说话人}`；内心独白 / 画外 OS / 听者方 → `{在画人物}全程闭口、嘴唇不动、不对口型`，且画外 OS 须注「台词系 {说话人} 画外，严禁对到在画人物嘴上」。

行格式：
- `台词: {说话人}（正常台词·{语气}）"{台词原文}"；口型对{说话人}。`
- `台词: {说话人}（内心独白·{语气}）"{台词原文}"；嘴唇不动、不对口型，{在画人物}全程闭口、仅靠表情 / 眼神演绎内心。`
- 默剧 / 无台词镜：`台词: 无台词 / 默剧（在画人物唇闭不动）`，不写任何字幕。

（旧 v1「内嵌硬字幕 / 后期软字幕 / 默剧」三选一契约已 **ABOLISHED**；stage-6 validators MUST reject 任何 shot 视频 prompt 里出现字幕字样 / 字体调性 / `台词 / 字幕:` 旧 label 的行。台词文本仍由 `script.md` / `dialogue.md` 决定，shot prompt 透传。）

**`台词` 字段只留跟视频有关的信息、不含字幕排版（per follow-up nvdi 028，v2 强化）**：喂给视频生成器（Kling / Seedance）的 `台词:` 字段**只保留**①对白内容（说话人 + 台词原文 / 内心独白）②`· 在画人物口型:` 口型指令（跟画面里嘴动不动有关，保留）。**必须移除**字幕排版 / 后期制作信息——字体（思源宋体 / 思源宋体斜体）、字号、位置（画面下 1/6 居中）、颜色（白色描边黑）、字幕窗时间（约 6 秒-9 秒）、前缀（「画外音:」）、「三选一字幕契约取后期软字幕」/「视频不烧字」/「不烧字」/「默剧处理无字幕」等。**根因**：这些是后期剪辑的字幕排版，不是画面内容，混在 prompt 里会**扰乱 Kling 生成视频**；prompt 须「只跟视频有关、简洁清晰」。字幕排版按需记在文件末尾 `### 后期字幕（不入 prompt）` 块。

**在画人物口型契约（per follow-up nvdi 007 — 防 Kling 自动加口型 / 乱口型 / 鸟语）**：凡在画人物在该镜中**不出声**的情形——默剧 / 静默 reaction / 仅环境音（脚步、衣袂、叩案、烛火等）/ V.O. 内心独白（画外配音，角色在画但不现场说话）/ 听者方（台词系他人 OS）——`台词 / 字幕:` 行必须显式追加子句 `· 在画人物口型: {在画角色}全程闭口、嘴唇不动、无说话口型`；V.O. 须注明「内心独白 OS 为画外配音 / 字幕、非现场出声，严禁把 OS 台词对到该角色嘴上」；听者方须注明「台词系 {说话人} OS（不入画），严禁对到听者嘴上」。同时 `负向:` 行必须含 `不要 说话 / 不要 嘴部开合 / 不要 说话口型 / 不要 lip sync / 不要 自动配音`。**根因**：Kling / Seedance 等模型默认给在画人脸自动叠加说话口型，弱表述（如「(静默, 无台词)」）不足以抑制，必须 `台词` 显式闭口指令 + `负向` 反向词双重锁定。（与 rule 5 v3 行 247-248 的 OS `在画人物口型:` 子项同源，此处扩展到全部「在画不出声」镜并强制 `负向` 反向词。）**内心独白镜「闭口但表情演内心」（per follow-up nvdi 027）**：嘴唇不动 **≠** 面无表情/呆滞——V.O. 内心独白镜里，角色须用**面部表情 / 眼神 / 神态**（眼神由倦转锐、微表情、唇线收紧或微扬、瞳孔变化、神色冷峻等）把内心独白的所想所感**演绎出来**，嘴不动但内心情绪外显。故 `在画人物口型:` 注除「全程闭口、嘴唇不动、无说话口型」外，须追加「**但内心所想靠表情 / 眼神 / 神态演出来，不靠开口、不对口型**」，并在 `动作:` 节奏里给出对应的神态变化 beat。

**每 shot 自带台词 + 跨 shot 连贯（per follow-up nvdi 009）**：① 每个 shot 携带**自己的** `台词`（哪怕该句由画外 OS 角色说出）；当一段连续对白 / 旁白跨多个 shot 时，须拆成**不重叠的连续片段**，每 shot 只放本镜对应的那一段，跨 shot 读下来连贯且**不重复**（反例：相邻两镜都塞整句同一台词 → 字幕/配音重复）。② **shot prompt 正文严禁跨 shot 引用**——不得在 prompt body（`镜头` / `动作` / `台词` 等任何字段）写「承 shotNN」「续于 shotNN」「本镜不重复…见 shotNN」「下一镜」之类；生成时每个 shot 独立喂入模型，跨 shot 引用纯属噪声且会误导生成。每个 shot prompt 必须**自包含、只描述本镜**。

字幕样式默认遵循 `style_guide.md § 字幕规范`；该项目无字幕规范段时，stage-2 interview 须补齐。

**节奏取词**：四档枚举 — `慢`（含慢镜 50%）/ `中`（标准 100%）/ `快`（含快剪短切）/ `顿挫`（停顿 + 爆点）。仅描述视觉节奏，**不混入音乐节拍**（v1 visual-only）。

**Cross-reference**：rule #4（角色 image-to-video 高阶模板）与 rule #11（seam-frame 还原模板）保留作为语义说明；本节 12.4 是字段级强契约。如二者矛盾，**以 12.4 为准**。Rule #5 dual-prompt 政策（每 shot 至少 `_kling.md` + `_seedance.md` 双 variant 输出）仍生效，但二者共享 12.4 的同一 schema —— variant 之间的差异仅来自「参考图是否出现」与 12.4-A 展开规则，schema 字段与字段顺序完全一致。

*(Originated from follow-up "导演 + prompt master 模板化" — 2026-05-10；rev — follow-up "model-agnostic templates" — 2026-05-10：把 Kling/Seedance 三件套抽象为视频/静帧二件套；新增 12.4-A 角色字段展开规则；shot prompt 文件命名统一为 `shotNN_{model}.md`。)*

#### 12.4-B Consolidated chars-reel reference + budget-shifted schema (per follow-up "concat + reorganize shot prompts")

When the user clicks "🎬 生成角色合辑" in the webapp, `ShotConcatBuilder` builds a per-shot **chars reel** — every involved character's first 2-second clip concatenated (with audio normalised) into `<shot_folder>/shotNN_chars.mp4` — AND patches the shot md's `## 视频 prompt` ```text``` block to follow the new schema:

| Field | New rule |
|---|---|
| `参考:` (new, top of block) | `参考: 请参考视频 {ref_chars_reel}，1~2s 为 {char1}, 3~4s 为 {char2}, ... ` — one line, byte-identical re-write on every concat, derived from `used` characters in table order. The `{ref_chars_reel}` token is what the user replaces with the actual `shotNN_chars.mp4` upload in Seedance. |
| `角色:` (was: long block per character) | **Deleted entirely.** Visual identity comes from the chars reel; descriptions are redundant. The 参考 line above already names every character with timing. |
| `场景: {ref_sN_xxx}` | **Token-only.** Any prose after the placeholder is stripped. The actual scene image / video is uploaded to Seedance separately. |
| `镜头:` (景别) | List EACH camera framing change with its time window. Format: `0–3s 全景仰拍 / 3–6s 推近中景沧冥 / 6–9s 切环绕中景白月清桃花玉佩 / 9–12s 拉远全景五人围拢 / 12–15s 推至沧冥脸部特写赤瞳`. Default is **at least 3 camera cuts per 15s shot** — single-take static is the failure mode. |
| `运镜:` | The mechanics of each transition: `平移`, `推`, `拉`, `环绕`, `升降`, `跟随`, `切换`, `Match cut`, `Whip pan`. Each entry tied to a 镜头 segment time. Example: `0–3s 升降镜自下缓升 / 3–6s 推镜由全景至中景 / 6–9s 环绕镜顺时针 90° / 9–12s 拉远 / 12–15s 推近特写`. |
| `动作:` (timed beats — every character every beat) | Timed beats covering all 15s. For EVERY beat, describe what EACH character on screen is doing — not just the speaker. Standing or sitting still is forbidden unless explicitly called out as a dramatic stillness. **Plus explicit gaze / body-orientation**: every character must have a named referent at every beat — `沧冥 正脸朝方鼎元`, `白月清 侧身 45° 望沧冥右肩`, `韩夺心 余光斜睨白月清`. Default failure mode of Seedance is "speakers staring into empty space while everyone else faces forward like a school photo" — fix it by naming the target of each character's gaze and the angle of their body to the addressee. Example: `9–12s: 方鼎元拂尘下垂半寸右手微颤，身体正对沧冥目光直锁沧冥眉心；韩夺心剑出鞘三分寒光乍现，侧身 30° 朝沧冥剑尖指向沧冥心口；赵焚天双拳暗握指节作响，正面立沧冥右后方目光从下颌扫向沧冥赤瞳；白月清桃花玉佩静止悬于半空气流凝滞，斜立沧冥左前方含笑斜睨沧冥；司空玄面具下嘴角微挑，半侧身白瓷面具缝隙锁定沧冥；沧冥赤瞳骤亮金赤双瞳浮现，左手负后纹丝不动，赤瞳缓扫五人面孔最后定于方鼎元`. |
| `台词 / 字幕:` | **MUST include per-line timing + speaker tone + speaker gaze + non-speaker reactions with gaze.** Format: `- 0–3s 方鼎元 (语气凌厉带怒，正脸朝沧冥，目光直锁沧冥眉心): "魔尊沧冥，今日便是你的劫数。" — 后期软字幕 方正粗黑 白底黑边 / 反应: 沧冥赤瞳冷睨方鼎元嘴角毫无动作；白月清侧首望沧冥玉佩轻颤；赵焚天双拳暗握目光自方鼎元转向沧冥；韩夺心余光从沧冥扫至方鼎元右手按剑；司空玄面具下半张脸朝沧冥不动`. Every dialogue line carries (a) `[start–end s]` time, (b) `{speaker} (语气..., 朝/望/视谁)`, (c) the line itself, (d) subtitle style, (e) `反应:` per non-speaker INCLUDING each one's gaze target. Seedance default failure modes this fixes: (i) wrong-speaker attribution, (ii) "everyone stands still" idle non-speakers, (iii) **"speaker stares into empty space" — A 念台词时眼睛根本不看 B**. Every speaker's gaze target MUST be named. Visual-only contract from §12.4 still applies (lines render as subtitles, never as audio prompts). |
| `时长:` | **Variable 3–15 s, set per the plot beat** (per rule #6 — reversed from the earlier "always 15s" stance because forced-15s shots dilute fast beats and invite model-invented filler). Author picks the duration the dramatic beat actually needs: quick reaction / cut-in 3–5 s, single action beat 5–8 s, two-beat exchange 8–11 s, multi-character standoff / monologue / hook 11–15 s. `动作:` timed beats and `台词 / 字幕:` windows MUST sum to `时长:` exactly. Kling renders a > 10 s shot as back-to-back Kling calls bridged by `shotNN_lastframe.png` mid-seam — user-side rendering step, not a schema concern. ≤ 10 s shots render in a single Kling call (no split needed). |
| `比例:` / `分辨率:` / `清晰度:` | **Removed entirely.** Aspect ratio and resolution are Seedance UI knobs, not prompt content. |
| `渲染样式:` | Keep, but **strip resolution / quality tokens** (`4K HDR`, `8K`, `1080p`, `HDR`, …). Keep the artistic-style anchors (`cinematic`, `真实毛孔细节`, `三庭五眼东方面孔`, etc.). |
| `负向:` | Unchanged. Re-paste `style_guide.md § 负向锁定` verbatim. |

**Why per-character `{ref_cN_xxx}` tokens are stripped from the same code block:** the consolidated `{ref_chars_reel}` covers every character. Leaving the per-character refs in the body would have the user upload a separate reference per character AND the chars reel — redundant. Per-character refs remain in the "Reference placeholders" table above the code block (documentation), but not in the prompt body.

**Idempotency contract:** the patch is a pure function of `(shot_md_content, used_characters_ordered)`. Re-running concat on an already-patched md produces byte-identical output. The implementation lives in `libs/infrastructure/writers/character_video__writer.py::ShotConcatBuilder._patch_chars_ref_line`.

**Length cap: ≤ 2000 characters** for the entire ```text``` prompt body (measured as raw character count of the code block contents, fence lines excluded). Seedance's prompt window has a soft limit around this size; overflow truncates silently and tail fields (`时长` / `负向`) get dropped first. Authors should trim 动作 / 台词 reaction lines first when over budget — never drop the 参考 line, the 镜头 cut list, the 时长 line, or the 负向 list (Seedance loses character likeness without negatives).

**Scope:** transforms apply to existing shot mds when concat runs. Future shot generation should follow this schema directly (skip the `角色:` block, omit `比例:`, set `时长: 15s` per rule #6 / the updated `时长` row above).

*(Originated from follow-up "concat + reorganize shot prompts" — 2026-05-17.)*

#### 12.4-D 短剧故事 + 台词大师 review criteria

> **编排入口（2026-06-17）**：本节的 D/S 准则已按单一职责拆进各专项审查 skill，**全 9 项均已建成**：台词→`ai_videos__台词大师`(D1–D6)；站位朝向→`ai_videos__站位朝向`(C1–C5)；运镜→`ai_videos__运镜`(M1–M7)；动作表演→`ai_videos__动作表演`(A1–A6, 含 P7/S1)；时长节奏合理性→`ai_videos__时长节奏`(PA1–PA6, 台词念得完/动作演得开/不赶不拖)；光线色调→`ai_videos__光线色调`(L1–L5)；整集剧情连贯→`ai_videos__剧情连贯`(P1–P6+N1–N4, 含 S2/S3/S5)；全剧序列→`ai_videos__全剧序列`(R1–R7)；机械契约→`ai_videos__格式契约`(K1–K14)。由 **`ai_videos__审查总编排`** 按「单镜→整集→全剧」顺序统一调用。**每个 ep/shot 的任何改动 + 出片前，默认跑该 suite**（见下方 2026-06-17 amendment）。本节下表保留为各 skill 准则的总索引；权威定义在各 skill 的 SKILL.md。

This section is the contract the storyteller-dialogue master applies on every shot / episode item the workflow emits — referenced by `agent_refs/validation/ai_video.md` validation level #9. The master treats every shot prompt's `台词 / 字幕:` block + the shot's overall design as a unit and grades it against the criteria below. Failures are emitted as inline patches with proposed rewrites, NOT prose critique.

**Dialogue criteria (台词):**

| # | Criterion | Definition | Failure example | Fix pattern |
|---|---|---|---|---|
| D1 | 通俗易懂 | Modern colloquial Chinese any 抖音/快手 viewer parses in one hearing. Idioms allowed only when contextually triggered. Pure 古文 / 文言 / 玄学 aphorisms with no actionable subtext fail. | 玄机暗藏，因果自衡 — abstract, no stakes | Rewrite to direct stake: 今夜你死，三界归我 |
| D2 | 信息量 / 钩 | Every line advances plot, raises stake, reveals character, OR plants a cliff. "Decorative" lines that could be cut without breaking the chain fail. | 风萧萧兮 (atmospheric only) | Rewrite to advance: 三日内拿不到玉佩，全宗满门 |
| D3 | 节奏 | ≤ 15 字 for punchy beats; longer only for declaration / ceremony (e.g. 召唤令). Two-clause max within one bubble. | 25-字 单 bubble | Split into two beats or compress |
| D4 | 角色声口 | Speaker's word choice / register matches their 锁定描述符 in `characters/<role>.md`. 魔尊 doesn't say sect-leader cadence; 乞丐少年 doesn't speak 文言. | 沧冥 说 "弟子愿听师尊教诲" | Restore character register |
| D5 | 反转密度 | For 短剧 / 短 sub-type: at least one line per shot lands a turn / reveal / threat. Group-monologue scenes get ONE reveal across the whole scene, not zero. | Whole shot 没有信息变化 | Add a stake / reveal beat |
| D6 | 名场面成语短 | Memorable / branded lines (cliffhangers, hook payoffs) ≤ 7 字 ideal. | 我必让你魂飞魄散并令你万劫不复 | 让你魂飞魄散 (6 字) |

**Shot-design criteria (镜头 / 动作 / 整体):**

| # | Criterion | Definition | Failure example | Fix pattern |
|---|---|---|---|---|
| S1 | 钩落 (hook landing) | Every shot named on the episode arc as a hook (黄金钩 / 反转 / cliff) MUST visibly land that hook in 镜头 + 动作 + 台词 within its declared seconds. | shot marked "H1 黄金钩" but action is just standing still | Re-author shot to deliver the hook |
| S2 | 情节链 (non-removable beat) | Shot's beat is a step the episode's plot chain can't skip. Decorative shots fail. | 30s of 沧冥 standing | Tie shot to a specific plot turn |
| S3 | 角色一致 (anachronism guard) | A character name / fact only enters the dialogue after they've been established in-story. Forward references to later-arc characters fail. | ep01/shot04 dialogue says "璃月" (introduced ep14) | Replace with in-scope reference |
| S4 | 视觉信息密度 | Each shot delivers a visually-distinct beat (not a near-duplicate of a neighbour). Two adjacent shots whose only diff is "from a different angle" with no plot delta fail. | shot04 & shot05 both = 沧冥 standing different angle | Merge or differentiate |
| S5 | 名字反差 (line variety) | Within an episode, two characters MUST NOT deliver near-identical phrasing for different threats. (e.g., 方鼎元 and 沧冥 both saying "今日便是你的劫数" — pattern duplication weakens both.) | Two shots' threats both use "今日便是 XX" | Differentiate cadence / metaphor |

**Master's output format (per shot):**

```
shot{NN}:
  D-flags: [D1, D5]
  S-flags: [S3]
  patches:
    台词 / 字幕 line "{old}" — fails D1: rewrite to "{new}"
    动作 0-3s — fails S3 (forward-ref to 璃月): drop the name, swap to "弟子" or scene-level reference
```

The parent applies patches surgically inline (one Edit per patch), then re-emits the shot. No prose review section is added to the shot md itself — the master's audit lives in the run's `.audit/{date}/{task_id}/events.jsonl` as `validation.issue.raised` entries with the patches as event payload.

*(Originated from follow-up "短剧故事 + 台词大师 — review every shot" — 2026-05-17.)*

#### 12.4-E Novel-prose-grade detail density in video prompt body (per follow-up "flexible per-shot duration + 增厚 prompt 细节" — 2026-05-21)

The shot md's `## 视频 prompt` code block must read like a **director-novelist 的镜头脚本**, not a field-checklist. The schema fields stay the same (rule #12.4 v4 + 12.4-B), but the *content* inside `动作:` / `台词 / 字幕:` / `光线 / 色调:` carries the kind of micro-detail a Chinese 仙侠 / 短剧 novel would name — facial micro-expressions, breath / pulse / shoulder physical tells, sensory atmospheric beats (魔气溢出之触感 / 雷光逆吹鬓边 / 长袍下摆吃风的厚度 / 尘埃自阶面浮起的方向), tonal qualifiers on every dialogue line, and named reactions on every non-speaker. Kling / Seedance interpret the prompt literally — the more specific the spec, the less the model invents uninstructed filler.

**Per-beat 动作 enrichment contract (every timed beat MUST carry at minimum 3 layers):**

1. **Macro action** — what the character physically does (the existing 12.4-B requirement; e.g. `沧冥左手负后右手二指轻屈`).
2. **Facial / 微表情** — eye state + brow + lip + jaw + breath in 5–15 字 (e.g. `赤瞳冷凝唇线略压下颌微收呼吸放缓`). Default failure mode: 角色 just "stands there" with a blank face. Fix by naming the micro-expression at every beat for every on-screen character — including non-speakers.
3. **Body orientation + gaze target** — re-paste of the 12.4-B gaze rule, restated here because it's load-bearing: 每个 character 每个 beat 必须有 named referent (`朝沧冥` / `望阶下` / `视方鼎元拂尘`), 不允许 "面无表情望向画外" 的占位描述。
4. **(optional but recommended for shots ≥ 8 s)** Sensory / atmospheric anchor — 1 句感官细节 carrying the scene's 时辰 / 魔气 / 雷光 / 风 / 尘 / 光晕 (e.g. `黑发被雷光气流逆吹半寸 / 长袍下摆吃风沉甸不动 / 阶面尘埃自右脚向外放射半寸`). For shots ≥ 11 s this layer is **required** at minimum every other beat.

Beats that 仅含 (1) (macro action only) are a stage-6 validation **warning**; beats lacking both (2) and (3) are a **blocker**.

**Per-line 台词 enrichment contract (5 elements per line, none droppable):**

每一行 `- {[start–end s]} {speaker} ({语气描述, 朝/望/视谁的精确目标}): "{台词}" — {字幕样式} / 反应: {每个非说话角色的 物理动作 + 微表情 + gaze target}`

12.4-B 的 5 元素已强制。本节加 6th implicit element：**语气描述** 不止情绪标签 ("冷漠")，须 carry 声线物理特征 — 音量 / 语速 / 共鸣点 / 停顿位 (e.g. `冷漠如冰带俯视感，喉腔低共鸣，每字间停半拍` 而非仅 `冷漠`)。Reason: TTS-aware downstream models (v2+) 会从语气描述提取声线参数；纯情绪标签 underspecifies。

**`光线 / 色调:` 行 enrichment：**

不再是单行 hex 罗列，而是 **2–4 句话** 描述：
- 主光源方向 + 色温 (`金紫雷柱自顶 5500K key 自上方贯下，左肩 1500lux 高光`)
- 各表面材质对光的反应 (`黑袍吸光仅左肩高光成银紫一线，金紫雷光在赤瞳虹膜形成两点反射`)
- 时辰 / 大气感 (`冷月为光，长阶尘埃悬浮中带寒意，画面整体偏冷青调底层叠魔气暗紫`)
- hex 主/辅/点缀仍要写，但 inline 嵌入描述句末 (`沉黑 #0a0a0a 主调 + 暗血红 #5a1a1a 阵旗补 + 紫金 #a8842c 法宝光点缀`)

**与 `## 小说文本 / Novel prose` 段的关系：**

「小说文本」段（rule #12.6 v2，shot md 独立散文段）仍 required，是 **人类 review 用**的全 shot 文学性叙事。本节 12.4-E 讲的是 **prompt body 内**的密度提升 — 两者不重复：

- Novel prose = 散文，给人读，禁止 timed beats / hex / placeholder。
- Prompt body 12.4-E = 结构化 timed beats + 字段，给 AI 读，但每个 beat 内文用小说式微观语言铺陈。

二者同时 carry 相同的 ground-truth 但 register 不同。

**字数上限（2026-06-18 收窄为全局 2000 硬顶）：** 所有 shot prompt body ≤ 2000 字（hard、blocker、无 soft/hard 之分）。增厚不是无限制堆字 — 12.4-E 的密度必须用经济语言压进 2000 字：短 shot (3-6s) 600-1200 字，长 / 多角色 shot 也一律 ≤ 2000 字（靠去重、合并同义清单、砍堆砌实现密度，而非堆字）。Padding for padding's sake = 反模式。

> **⚠ SUPERSEDED（2026-06-18 全局 2000 硬顶）**：以下「12.4-E density 例外」整段（3500-7000 / 6000-9500 字常态、"密度优先于字数" 裁决、超 cap 的 head-loaded truncation-mitigation 与例外注释模板）**全部作废**。现在所有 prompt 一律 ≤ 2000 字 hard、无任何放宽；12.4-E 密度要求保留但须在 2000 字内经济落地。本段保留仅作历史，不再执行。

**12.4-E density 例外（已废止 — 见上方 SUPERSEDED；rule #12.4-E vs #12.4 v4 字数上限冲突的明文裁决）：**

任何 shot — 不论单角色 / 双角色 / 多角色 / cover-frame — 一旦应用 12.4-E 的 4-layer-per-beat 强制（macro + 微表情 + body/gaze + atmospheric）+ 每角色每行台词的 6-element 强制（5 base + 6th 声线物理特征）+ 2-4 句 `光线/色调` 描述，**结构性上**就会超过 2500 字 hard cap。经验值（mozun_chongsheng ep01-ep05 empirical, 2026-05-21）：

- 单角色 / 双角色 shot ≥ 8 s 应用全 12.4-E enrichment → 3500-7000 字 prompt body 是常态。
- 多角色 (3+) cover-frame / 全员同框 shot ≥ 11 s → 6000-9500 字 prompt body 是常态。
- 单角色 / 双角色 shot < 8 s 与 12.4-E "atmospheric layer required" 阈值脱钩，body 通常仍可在 1500-2400 字范围内（不必应用例外）。

当 12.4-E 详细密度与 #12.4 v4 字数上限冲突时，**12.4-E 详细密度优先** — 因为 (a) cover-frame / 美学顶点 / 抖音封面候选 shot 的画面质量是 episode 头部钩子的生死线，(b) 即便单角色情绪长 shot 也需 12.4-E 的小说化微观语言来 anchor 模型不漂，(c) "干站着空对镜头 / 非说话者面无表情" 的失败模式 (rule #12.4 v4 负向 line) 必须被 4-layer 强制压住，比单 prompt 不被 truncate 重要。

**应用契约：**
- Shot body > 2500 字 时，在 Shot context Summary 末尾加显式 exception 注释（**所有**触发例外的 shot 都须加，不区分 cover-frame 与 density-only）：
  - 多角色 cover-frame：`**注: 本 shot 为 cover-frame / 全员同框 (N 角色)，prompt 长度上限按 rule #12.4-E multi-character cover-frame 例外条款放宽，prompt body XXXX 字 高于 2500 字 hard cap。**`
  - 单角色 / 双角色 density-only：`**注: 本 shot ≥ 8s 应用 rule #12.4-E 全 4-layer enrichment + 2-4 句光线/色调，prompt body XXXX 字 高于 2500 字 hard cap，按 12.4-E density 例外条款放宽。**`
- Stage-6 validator 看到 Shot context 含上述任一注释格式 → **不**发 byte-cap blocker。看不到注释而 body > 2500 字 → 仍发 blocker。
- (rule #12.4 v4 原有的 cover-frame 例外条款保留作 fallback ground，本节是其 12.4-E 层面的 alignment 重申 + density-only 路径补全。)
- 超 cap 的 prompt body 推荐采用 **head-loaded 字段顺序** 做 truncation-risk mitigation（Seedance 在 ~2000 字后倾向 silent-truncate 尾部）：

```
参考: {chars-reel} / {seam-frame ref}            ← critical, chars-reel patcher 已锁定 head 位置
场景: {ref_sN_xxx}                                ← critical scene anchor
时长: Xs                                         ← MOVED from tail; 字段定时 anchor 必须 survive truncation
负向: ... (full ban list)                         ← MOVED from tail; 模型同质化 / 卡通漂移的防火墙必须 survive
镜头: + 运镜:                                     ← high-level framing schedule
渲染样式: ...                                     ← high-level style anchor (short, robust)
节奏: ...                                         ← short anchor
光线 / 色调: ...                                  ← 2-4 sentence atmosphere block
动作: ...                                         ← longest field, tolerates partial tail truncation
台词 / 字幕: ...                                  ← second-longest field, tolerates partial tail truncation
比例: 9:16                                       ← optional; multi-character body 通常已 strip 至 9:16 fixed UI knob per 12.4-B
```

`参考:` 行位置由 ShotConcatBuilder 锁定在头部不可移动（rule #12.4-B 既定）；其余字段顺序为推荐而非强制。Body 在 2000 字内的 shot 保留原 12.4-B 字段顺序（`参考 / 场景 / 镜头 / 运镜 / 动作 / 台词 / 光线 / 节奏 / 渲染样式 / 时长 / 负向`），仅 multi-character cover-frame / 超 cap shot 应用 head-loaded 顺序。

**字符密度 sanity check：** 即便豁免 hard cap，作者仍应避免"reaction line 镜像复述" — 例如 "白月清侧身朝沧冥 / 赵焚天侧身朝沧冥 / 方鼎元侧身朝沧冥 / 韩夺心侧身朝沧冥 / 司空玄侧身朝沧冥"。多角色反应应承载差异化信息（不同 gaze target / 不同微表情 / 不同物理姿态），不是同一句话换名字。重复模式 = 12.4-E 详细密度精神之违背，即使 byte-cap 豁免也应 trim。

*(Originated from follow-up "flexible per-shot duration + 增厚 prompt 细节" — 2026-05-21; amended same day with "字数上限 vs 12.4-E 详细密度 冲突裁决 + head-loaded 字段顺序" subsection after empirical run on mozun_chongsheng ep01-ep03 produced 14/30 shots > 2500 字, all genuine multi-character cover-frame 美学 anchors. Solves: ① 强制 15s 让短情节 beat 灌水, model fills with uninstructed drift; ② 12.4-B 的 timed-beats 字段过于 mechanical, "干站着说话" 的失败模式仍偶发 — 本节强制 facial micro-expression + 感官 atmospheric layer 提供 model literal-instruction; ③ user 反馈"prompt 应该像小说一样"已被 12.6 novel-prose 部分回应, 本节把同样的 narrative-density 要求落到 prompt body 内供 AI 直接消费；④ 多角色 cover-frame shot 的 12.4-E 详细密度结构性超 2500 字, 通过 cover-frame 例外条款 + head-loaded 字段顺序 mitigation 化解 — 内容质量 > 单 shot prompt 不被 truncate。)*

#### 12.4-F Character + scene reference header in shot code block (per follow-up 2026-05-24)

**Hard rule:** every `shotNN.md` 视频 prompt code block MUST open with one reference line per appearing character + one line for the scene, using the canonical handle `{drama_chinese_name}_{name}`. Strip the `cN_` / `sN_` prefix when emitting the line — the handle is the bare 中文 name.

**Format (literal — characters first, scene last, one blank line, then the rest of the prompt body):**

```text
{char1_zh}请参考：{drama_chinese_name}_{char1_zh}
{char2_zh}请参考：{drama_chinese_name}_{char2_zh}
...
{scene_zh}:{drama_chinese_name}_{scene_zh}

ep{NN} / shot{NN} · {1-line summary from shotlist.md}
...rest of prompt body per 12.4 / 12.4-B / 12.4-E schemas...
```

Four contracts:

1. **First content inside the code block** — the reference lines come BEFORE the title line, BEFORE any `角色:` / `场景:` descriptor, BEFORE everything else. Exactly one blank line separates the reference block from the rest of the body.
2. **Bare 中文 name** — drop the `cN_` and `sN_` prefixes; the handle is the pure Chinese identifier the user shares with their external AI model. Example: `女帝退婚后悔了_太监`, NOT `女帝退婚后悔了_c4_太监`.
3. **Replaces legacy `{ref_xxx}` placeholders** — the older syntax (`参考: 请参考视频 {ref_chars_reel}, ...` + `场景: {ref_s1_长阶顶}`) is **abolished**. The character/scene handle IS the reference — the user pastes the externally-rendered turntable mp4 / scene PNG / voice sample under that label in their AI model UI. Any pre-existing `{ref_*}` line in a code block MUST be stripped during migration.
4. **Voice-only / OS characters MUST be listed too** (per follow-up 2026-05-25 "虽然太监不出镜，但是应该标注太监在朗读圣旨"). When a character speaks but does not appear on camera (OS / V.O. / 画外), they MUST appear:
   - In the **Shot context `Characters:` line** — as `cN_<name> (画外 OS, 不入画 — <one-line role description>)`.
   - In the **code-block reference header** — as `<name>请参考 (画外 OS, 仅声线无入画)：<drama_zh>_<name>` (note the parenthetical sits BEFORE the colon, not in the value).
   - The `(画外 OS, 仅声线无入画)` parenthetical is the literal contract; do NOT abbreviate to just `(OS)` or paraphrase. AI video models attend to this label to bind the voice sample without compositing the character into the visual frame.
   - The auto-injector `tools/add_shot_reference_lines.py` detects `画外` / `OS` / `V.O.` markers in the Characters: line parenthetical and emits the suffix automatically — author flow is: edit Characters: line → re-run the script.

**Punctuation:** 角色 line uses full-width colon `：`, 场景 line uses half-width `:` — this is the literal contract, not a typo. Authoring tools (`tools/add_shot_reference_lines.py`) emit both shapes.

**Why per-character lines instead of one consolidated reel:** each character / scene has its own externally-rendered visual (turntable mp4 / scene立绘 PNG / voice sample). One reference line per asset lets the user paste each into the model independently and gives the model an explicit `{label} = {handle}` binding — easier for the model to attend to than a single packed reel description.

**Drama 中文名 source:** `ai_videos/{slug}/README.md` H1 line. Strip surrounding `《》` and any trailing `— ...` suffix before use (e.g. `# 《女帝退婚后悔了》— 古风短剧` → `女帝退婚后悔了`).

**Stage-6 validators must reject** any new shot file whose code block's first non-blank line is neither a `{char}请参考：...` line nor a `{scene}:...` line. Migration of legacy shot files is one-shot via `tools/add_shot_reference_lines.py <drama_slug>` (idempotent — re-running is a no-op when the header is already canonical).

*(Originated from follow-up "在每一个shot的prompt的前几行，请加入一下角色和场景有关的提示词" — 2026-05-24. First applied to `ai_videos/nvdi_tuihun_houhuile/` (14 shots) before rolling forward.)*

#### 12.5 角色 reference 单 prompt 文件（character video-reference template）

每个角色一份「视频 reference」文件，**同文件内一段 copy-paste-ready 文字生视频 reference prompt** + 一张 3 句数字计数台词（"1, 2, 3"）配音对照表。该文件 supersedes 旧的「立绘单 prompt」格式（rule #12.2 完全），把 character pipeline 从「PNG 单参考」升级为「360° turntable 视频 + 标准声线 reference 一站到位」。

> **合规优先（per wushen_juexing follow-up 014 — 2026-06-14）：turntable 生成块（```text``` 段）受 §563(nvdi 020) 平台审核合规约束，凌驾于 §12.7 的「演员锚点」要求。生成块内严禁出现任何真人演员/导演名（Kling 实测对 e.g. 罗云熙 / 王鹤棣 等真人名直接以「违反社区规范」拒绝生成），亦不写「演员照片 / 演员素颜 / 照抄演员参考照片 / 现成短假发」等真人素材引用（人脸属敏感个人信息）。演员类比锚点仅留在 planning 层（角色 bible 顶部 `配音参考` / `specs/`），不进生成块；生成块的真实感靠 §593 推荐的纯风格词（影视级真人写实 / 真人皮肤毛孔 / 亚洲俊男靓女 / 三庭五眼东方面孔 / photorealism）+ 文字外貌描述。§12.7 的「1-2 名 specific 演员类比」改读作「写在 planning 层」。**

**为什么单 prompt 即够：**

Seedance / Sora / Veo / Runway Gen-3 等支持 **video-as-reference** 的视频模型已成主流（2026 年），用户从文字 prompt 一步生成 turntable 视频后，**该视频本身**作为后续所有 shot prompt 的 video reference 上传即可——形象 + 声线 + 节奏一次锁定。PNG 立绘步骤被 collapsed；如需 PNG（喂 Kling image-to-video 等仍在用的 image-input 模型），从 turntable 视频抽帧即可，无需独立 image prompt。

**为什么 7s 5-phase single-take with simplified plain-Chinese prompt（rule #12.5 v11，per ai_video_management follow-up 099 — 2026-05-19）：**

v10.2 (098, 同日早些时候) 引入 3 static landings + 2 motion bridges 解决 v10 单条 4s 连续 orbit 模型 under-rotates 的问题。schedule 设计是对的, 但 prompt 把 motion 路径在 4 个字段重复描述: 镜头 line 用 "motion bridge / 锁定机位 / no dolly / no zoom" jargon 列举 5 阶段, 动作 5 个 beats 每个都重复 phase 描述, 节奏 line 又复述 "5-phase 单 take, 3 static landings + 2 motion bridges", 负向 14-item list 含 qualifier 段落 (`不要 motion 跨越目标角度 (1s motion bridge 必须精确终止在 90° (t=3s)...)` + `不要 静态段内继续微调机位 (3-4s 段 + 5-7s 段必须完全静止...)`)。User 实测 v10.2 渲染 (同日晚段): "the camera did not move as you intended in the charactor prompt, I think kling got confused, you need to tell it in a more simple way and only once in the prompt. currently the it shart to turn around to side view at only about 5s." — 模型在多字段冗余描述下不信任任何单个 spec, 倾向 average 而 under-commit to motion, 把 motion 全部 squeeze 到 ~5s 之后。

v11 fix: schedule 不变 (3 static landings + 2 transitions, 同 timestamps), 但 **prompt 中 motion ONLY 描述一次**, 放在 动作 timed beats 字段, 用 plain Chinese (不用 "motion bridge" / "static landing" / "locked-framing" jargon)。
- `镜头:` 收窄为仅 framing/lens specs (medium-full ~40mm, 头到脚, no dolly, no zoom), 不再列举 5 阶段
- `动作:` 仍 5 个 timed beats 但语言简化: "镜头围绕角色顺时针绕 90° 到角色左侧身" / "镜头停在左侧身角度不动" — 不用 "motion bridge" / "锁定机位 medium-full" 等技术 jargon
- `节奏:` 缩为一句: "单 take 7s, 角色站立不动只说话, 镜头按 动作 timed beats 旋转 + 停顿" — 不重复 motion 路径
- `负向:` 砍到 10 项简单 bans (`dolly / zoom / 距离变化 / framing 变化 / 角色转身 / 走动 / cut / transition / fade / 超过 7s`), 不带 qualifier 段落
- 锁定机位 jargon 全部移除 — model 可能把 "锁定" 当 "全程不要动" 理解, 导致 motion 段也不动。改用 "镜头停在 X 角度不动" 描述静态段, "镜头围绕角色绕到 Y" 描述运动段

**Hypothesis**: motion 描述 ONCE + plain Chinese 让模型 trust the spec, 不再 average 多字段 conflicting descriptions, motion 会按 timed beats 真正执行。**Risk**: 如 v11 简化后模型仍 under-commit to motion (e.g., motion 仍延迟到 ~4s+), 说明问题不是 prompt 冗余而是模型对短 clip 内 motion 的根本偏见。退路: v12 (shift schedule earlier, 牺牲 0-2s truncate-compat byte-identical 契约 — 0-1s static front + 1-3s motion + 3-4s static side + 4-5s motion + 5-7s static back; CANONICAL_VIEWS side 改 0.5/3.5/6.0) 或 v13 multi-clip (render 3 separate 2-3s clips at front/side/back + 文件系统层 concatenate, most bulletproof)。

**为什么 v10.2 的 verbose multi-field prompt 不再生效（archive）：**

v10.2 (098) schedule 正确 (3 static landings + 2 motion bridges + locked framing), 但 prompt rendering 太 verbose: motion 路径在 镜头 / 动作 / 节奏 / 负向 4 字段重复, 用 "motion bridge" / "static landing" / "locked-framing" / "single continuous take" 技术 jargon。模型在多 conflicting 描述下 under-commit to motion, 把 motion squeeze 到 clip 末段, user empirical 报告 motion 实际起于 ~5s (而非 spec 的 2s)。v11 收窄到 ONE description in 动作 字段 + plain Chinese。

**为什么 7s locked-framing 5-phase single-take with static landings（rule #12.5 v10.2，per ai_video_management follow-up 098 — 2026-05-19）：**

v10 (096) 设计假设视频模型能在 4 秒 (2-6s) 内匀速完成 180° orbit at 45°/s。Empirical 实测 (user first v10 render, 2026-05-19): 模型实际 orbit 速度约 **22°/s** (~半速), 且 motion 段似乎 4-5s 才真正启动 — 7s 视频末帧仍在 ~90° 侧身, 根本没到 180° 背面。`抽帧时间戳 (1.0, 4.0, 6.0)` 在 v10 source 上得到的 3 张 png: front OK; side picks 落在 (model 启动延迟 + 速度减半 的) 仍接近正面的位置; back 落在 model 才到 ~90° 的位置 — 抽出来的 "back" 其实是 side, "side" 其实是 almost front。

Root cause: 视频模型不精确遵循 timed-beat *速度* 指令。 「slow continuous orbit at 45°/s for 4s」 给模型太多 latitude — 它解读 「slow」 时按内部 pacing 估算, 通常 ease-in/ease-out 吃 budget + 短 clip 内倾向 under-rotate 以规避 motion-blur 风险。spec 上的 `(t-2)*45°/s = 角度` 数学是对的, 渲出来的视频不线性遵守。

v10.2 把 latitude 取消: **3 个 static landings (front / side / back) + 2 个 1s motion bridges**, 而不是单条 4s 连续 orbit。每个角度 pick 来自 static hold (镜头完全不动), 而非依赖模型估算 orbit 进度。模型可以 motion 段内任意 pacing — 在 1s motion bridge 内冲快、缓动、ease-in-out 都行 — 但 static landing 是硬契约: 镜头必须在 t=3s 完全停在 90°, 在 t=5s 完全停在 180°, 这两个 timestamps 是 angle 的硬绑定。

**关键设计原则 v10.2: 5-phase locked-framing single take, 锁定机位 framing throughout (no dolly, no zoom), 3 static landings + 2 motion bridges:**
1. **0-2s static front lock** (与 v10 byte-identical content + framing, truncate-compat preserved)
2. **2-3s motion bridge** 0° → 90° (1s, 任意 pacing 内, 终止在精确 90°)
3. **3-4s static side lock** (镜头完全不动 1s, side pick from this window)
4. **4-5s motion bridge** 90° → 180° (1s, 任意 pacing, 终止在精确 180°)
5. **5-7s static back lock + settle** (镜头完全不动 2s, back pick from this window)

每个 motion bridge 起末速度 = 0 (从 static 加速 + 减速回到 static), 因此 motion blur 阈值低, character detector 可锁定 — 跟 v6/v5 fast 720°/s whip-pan 在 validator 视角下范畴不同。Kling validator 拒 v6 时给的理由是 "cuts or transitions"; v10.2 仍是 single continuous take with continuous timecode (no scene change, same character, same studio), motion 起末的 0 velocity = no motion blur ≠ cut/transition。Hypothesis: 如 v10 过 validator, v10.2 也过 (motion 总时长更少 + 每个 motion 段更短)。

**抽帧时间戳 (anchored on landings, not speeds):**
- front t=1.0s (mid 0-2s static, unchanged from v10)
- side  t=3.5s (mid 3-4s static side, v10 的 4.0s → 3.5s)
- back  t=6.0s (mid 5-7s static back, unchanged from v10 — 但 v10 此 pick 落在 orbit 末段, v10.2 此 pick 落在 static 中段 1s 远离 motion-end)

side timestamp 4.0s → 3.5s 的原因: v10.2 把 side static 段定为 3-4s (1s window), mid pick at 3.5s。t=4.0s 在 v10.2 已经是 motion bridge 起点 (motion to back 开始), 不是 static 中段。

**Risk acknowledgment (v10.2 retreat paths):**
- v10.3: drop one motion bridge — 0-2s front + 2-3s motion 0°→90° + 3-7s static side (4s)。Loses back angle。
- v10.4: drop both motion bridges — 全 7s static front (= v8 + v10.2 negatives)。Loses side AND back, extract pipeline degrades to front-only。
- v11+ multi-clip path: 3 separate 2-3s clips concatenated。Most expensive, most bulletproof。

**为什么 v10 的 4s 连续 orbit 不再生效（archive）：**

v10 (096, 同日早些时候) 押注「7s 内 4s 连续 orbit at 45°/s 能让模型匀速完成 180°」。Implementation 后 user 立即渲染 10 个角色 v10 mp4 + click 🖼 抽 3 视图按钮 (follow-up 093) — 发现 side png 仍接近正面, back png 实际显示 side, 视频末帧未到 180°。Root cause: 模型 under-rotates 短 clip 内的连续 orbit 指令, 不能依靠 timed-beat 速度估算 cleanly。v10.2 直接 reverse v10 的 「single continuous orbit」 设计, 改用 「3 static landings + 2 motion bridges」, 把角度契约从 「时间 × 速度」 → 「明确 landing 角度 hold」。

**为什么 7s locked-framing single-take（rule #12.5 v10，per ai_video_management follow-up 096 — 2026-05-18）：**

v9 (092, 同日早些时候) 用 15s slow push-in + slow orbit + reverse-dolly 复合运镜方案, 单 take 内 framing 从 wide ~35mm 推到 medium close-up ~50mm 再拉回 wide。设计意图是同时取得 face close-up reference + multi-angle silhouette reference + casting-grade dialogue capture。但实测中 follow-up 093 的「抽取 3 视图 + 音频」管线（front / side / back png + full mp3）暴露了 v9 的结构性缺陷:

- v9 的 front pick (t=1.0s) 在 0-2s 静态 wide 段, 框 head-to-toe；
- v9 的 side pick (t=7.0s) 在 5-13s orbit 段的 25% (= 90°), 此时 framing 处于 reverse-dolly 中段 (medium close-up → wide 之间), 头部约占 1/3 frame, 下半身边缘 crop；
- v9 的 back pick (t=9.0s) 在 orbit 50% (= 180°), framing 已接近 wide 但仍在 reverse-dolly 末段, 仍非 byte-identical 与 front pick。

3 张 png 出来 framing 不一致 — 无法作为 coherent 3-view character sheet 喂给 image-to-video 模型；下游 shot prompt 引用「角色背面 silhouette」时拿到的是半身 crop 而非全身背面。

v10 押注「7s 内信息够用 + 锁定 framing 抽帧才一致」两条假设, 完全 reverse v9 的 mixed-framing 设计:
1. **锁定 framing throughout** — 相机距角色的距离全程不变 (no dolly, no zoom), 只旋转。3 个角度的 png 出来 head-size + feet-position 完全一致 — 抽出来直接是 3-view character sheet。
2. **drop dolly + drop face close-up** — 不再追求专属面部 close-up window；medium-full framing 下面部 ~1/5 frame ≈ 360-400px tall (9:16 1080p), 用户接受这个 trade-off (096 clarifying 问中明确选 locked framing)。
3. **180° orbit suffices** — 身体左右对称, 90° + 180° silhouette 已覆盖 unique 信息, 270° 是 redundant。orbit 从 v9 的 360° 砍到 180°, 时长从 15s 砍到 7s。
4. **保留 0-2s 静态 truncate-compat** — 跟 v8 / v9 一样, 0-2s 段静态正面 + 一/二, 下游 ai_video_management 2s 切片输出保持兼容 (framing 从 v9 的 wide 收紧到 medium-full, 内容 still: 静态 + 正面 + 全身 + 一+二)。
5. **保留 ≤ 45°/s slow orbit + 单方向** — Kling validator hypothesis 不变, 跟 v9 的速度上限 + 方向单一约束 byte-identical。v9 若能过 validator, v10 应同样过。

**关键设计原则 v10：单镜头连续运镜 single continuous take, 3 阶段 (静态正面 + 180° orbit + 静态背面), 全程匀速无方向反转 + 锁定 framing。** 0-2s 静态正面 medium-full (一/二, truncate-compat) → 2-6s 缓慢顺时针 180° orbit at 45°/s (no dolly, no zoom, 相机距角色距离全程锁定) → 6-7s 锁定背面 medium-full settle。每段过渡是 motion velocity 的 smooth handoff (orbit 起末各 ~0.2s velocity ramp), 不是 snap stop。

**Risk acknowledgment.** v10 仍是 hypothesis: 7s 内信息够用 + locked-framing 抽帧足够喂 downstream 模型。如经验数据显示 v10 也被 validator 拒, 退路有二: (a) 退到 v10.1 — drop orbit, 全 7s 静态正面 (≈ v8 + 2-7s per-character dialogue), 抽帧管线退化到只有 front 视图可靠；(b) 退到 v10.2 — orbit 内插 90° / 180° 处的短暂 (~0.3s) static hold, 违反 single-take 慢动 + 无中断 rule 但每段 motion 段 < 2s 可能仍过 validator。096 follow-up 文件记录这个 hypothesis 和退路。

**为什么 v9 的 15s mixed-framing single-take 不再生效（archive）：**

v9（archive，per follow-up 092 — 2026-05-18 晚段, supersedes v8）：当时（同日）user 拒绝 v8 静态退让, 092 重新启用 motion 但限速 + 限方向, 加 2-5s dolly-in 取 face close-up + 5-13s slow 360° orbit 取 multi-angle silhouette + 同段 reverse-dolly 隐藏在 orbit 弧线内回 wide + 13-15s 锁定收尾。Implementation 后 follow-up 093 在 v9 基础上加了「抽 3 视图 + 音频」管线 (front t=1.0s / side t=7.0s / back t=9.0s + full audio), 但用户使用中发现 side / back png 出来 framing 不一致 — dolly-in 段 + reverse-dolly 段让 frame 中头部大小变化, 抽出来的 3 张 png 无法作为 coherent character sheet。096 (v10) 直接 reverse v9 的 mixed-framing 设计: locked camera distance + drop dolly + 180° orbit + 7s 时长。

**为什么 v8 的 7s static-camera 不再生效（archive）：**

v8（archive，per follow-up 091 — 2026-05-18 早段, supersedes v6 v7）：当时（同日）Kling validator 拒收 v6 15s casting reel, error message 见下方诊断段。v8 完全弃 motion 走 7s 静态正面机位 + 0-2s 弃 360° silhouette pass。Implementation 后, 10 个 mozun_chongsheng 角色 md files 应用 v8 patch (091 mozun_chongsheng/024) 完成, 但用户 review 后认为 trade-off 过深 — 静态全身远景下 face 仅占 frame 1/6 (太小不能 read), 且彻底失去 侧身 + 背面 reference (后续 shot prompt 无法 reference 角色背面或侧脸 silhouette)。v9 (092) 重新启用 motion **但限速 + 限方向**, 维持 v8 的 0-2s 静态契约 byte-identical, 在 2-15s 段引入 slow push-in + slow 360° orbit。

**v7 + v8 → v9 演进逻辑：** v6 fast-motion → v8 zero-motion 是对 Kling validator 的 over-correction; v9 是 controlled-motion 的 第三种尝试 — slow motion + 单方向 + 连续。

**为什么 v6 的 15s casting reel 不再生效（archive）：**

v6（archive，per follow-up 088 — 2026-05-17）：当时 reference upload ceiling 实测放宽到 ≥ 15s, v6 把 turntable 升到 15s + 7-segment beats + 8-row dialogue table。维持 v5 的「0-2s 自包含 + 一/二」契约, 在 2-15s 段加 6 个 camera moves（推近 / 反向 90° / 拉远 3/4 / 横向 pan 360° / 拉近 medium / 特写）+ 4 句 character-specific 台词（取自 bible 三句 + 最 character-defining 一句作 13-15s 收尾）+ 表情 range silent capture。Implementation 后 Kling reference upload 验证全部失败 — Kling validator error: "the current video contains cuts or transitions, and no clear, complete character is detected, please upload a single shot clear character video"。诊断: v5/v6/v7 全部在 0-2s 段做**快速 360° 顺时针环绕** (~720°/s), validator 判 cut/transition + fast spin motion-blur 让 character detector miss; v6 在 2-15s 段加 6 个 camera moves 含方向反转, validator 同样判 transitions。v8 完全弃 motion (091 同日早段) 走静态; v9 (092 同日晚段) 改回 slow continuous motion (≤ 45°/s 单方向) 押注 validator 接受。

**为什么 v5 的 4s 不再生效（archive）：**

v5（archive）：当时（2026-05-17 之前）下游 Seedance / Sora / Veo / Runway Gen-3 等 reference 上传 ceiling ≥ 4s 可稳定接收。v5 把 turntable 时长从 v4 的 2.9s 升到 4s, 加 "一/二/三" + 1s 面部定格 + 「前 2s 自包含」契约。够 ship 起手定场 + 360° + 推近 + 1s 定格, 但不够 ship 一个 proper casting reference — 缺多角度 silhouette / 缺角色 voice timbre baseline / 缺 emotion range / 缺标志特征点 final lock。v6 在 2026-05 中旬 reference upload ceiling 放宽到 ≥ 15s 之后把 turntable 升到 15s, 维持 v5 的「0-2s self-sufficient + 一/二」truncate-compat 契约不动, 在 2-15s 段加 6 个 camera moves + 4 句 character-specific 台词 + 表情 range。v8 又把 turntable 压回 7s 因 Kling validator 拒 multi-camera; 同时放弃 v5/v6 的 0-2s 360° silhouette pass (truncate 现仅给 frontal voice baseline)。

**为什么前 2s 必须自包含（rule #12.5 v5 / v6 / v8 / v9 / v10 / v10.2 共同契约，与 ai_video_management 短角色合辑对齐）：**

`ai_video_management` 的 `ShotConcatBuilder._ffmpeg_concat` 在 concat 前会 trim 每个 per-character clip 到 **前 2 秒**（`_CONCAT_SEGMENT_S = 2.0`，见 `projects/ai_video_management/libs/infrastructure/writers/character_video__writer.py`）；webapp 上的「✂ 截到 2s → video.mp4」按钮同样取前 2s。turntable prompt 必须把核心身份信息 front-load 到 0-2s 窗口内, 2s 截取片段才有意义。v5/v6/v7 都尝试在 0-2s 段塞「正面定场 + 360° 环绕一圈 + 中文数字 一/二 发声」, 但 360° 被 Kling validator 判 cut/transition + spin blur 让 character-detector miss。v8 把 0-2s 段简化为「静态正面全身 + 一/二」, 牺牲 silhouette catalog 换取 Kling 接受 upload + 仍保留 voice baseline 跨角色 byte-identical 对齐。v9 (092) **维持 v8 的 0-2s 静态正面 + 一/二 byte-identical 不动**。v10 (096) **再次维持 0-2s 静态正面 + 一/二**, 仅把 framing 从 v8/v9 的 wide ~35mm 收紧到 medium-full ~40mm — 0-2s 段在 v10 仍是 (a) 静态 (b) 正面 (c) 全身 (d) 一+二 voice baseline, 下游 webapp 2s 切片输出仍可用 (内容 same, framing 微调)。v10 仅在 2-7s 段引入 slow orbit, 不动 0-2s 切片契约。

**为什么 v4 的 2.9s 不再生效（archive）：**

v4（archive）：当时（2026-05-10）下游视频模型 video reference 上传体积/时长硬上限 ≤ 2.9s 最稳；原 12s 长 turntable 超限会被截断/拒绝。v4 把 turntable 时长从 12s 压到 2.9s；台词从 5 句多情绪样片简化为 3 个 Arabic 数字 "1, 2, 3"，运镜极快。v5 在 v4 的极速框架基础上把上限放宽到 4s + 把 Arabic 数字换成中文「一, 二, 三」+ 加 1s 面部特写定格 + 加上「前 2s 自包含」契约（与短角色合辑 2s 切片对齐）。v6 在 v5 的 0-2s 锁定基础上把 ceiling 升到 15s 并把 2-15s 段开放给 per-character casting reel — 多角度 + 角色 bible 自身台词 + 表情 range。

**文件位置约定（rule #12.5 v5, per follow-up xianxia_new/008 — 2026-05-24；SUPERSEDED by rule #12.8 v2 + rule #12.9，see follow-up feng_shou_lu/001 — 2026-05-24）：**

> **SUPERSEDED — DO NOT use the c{NN}_{pinyin} hybrid for new projects.** Canonical pattern is `characters/c{N}_{中文名}/c{N}_{中文名}.md` per rule #12.8 v2 + #12.9 (folder + filename byte-identical, both Chinese, N 不补零). The v5 hybrid was motivated by an unfounded fear that the webapp regex `^c\d+(_.*)?$` rejected Chinese folder segments — empirically (mozun_chongsheng, ai_video_management import) it accepts them. Migrate any existing v5 project to the 12.8 v2 shape. The text below is retained for archive only.

每角色一个**文件夹** `characters/c{NN}_{pinyin_slug}/` (hybrid: webapp-compatible c-prefix folder name + Chinese bible 文件 inside). 文件夹内主 bible 文件命名为 `{中文名}.md` (Chinese, 含 rule #12.1 bible 全段 + 视频 reference prompt 段). 文件夹名匹配 webapp `_CHARACTER_DIR_RE = r"^c\d+(_.*)?$"` 正则 (`apps/ui/src/lib/dramas.ts:22` + `libs/infrastructure/writers/character_video__writer.py:63`) — 没有 c 前缀的 folder 不会被 webapp casting / shot-concat / actor-assign feature 识别. 文件夹结构允许根据角色复杂度新增 sibling 文件 (双形态角色的额外 turntable / state-A/B Seedream 立绘 / 配音参考详档 / etc.), 同一文件夹内 sibling 文件按角色实际需要补充, 无强制 schema.

`characters/ref_images/` 全局子目录仍废止 (rule #12.5 v3 abolition 保留有效) — 角色专属资产现归并到 `characters/c{NN}_{pinyin}/` 文件夹下.

**v4 → v5 演进 rationale**: v4 (follow-up 004) 用纯中文 folder 名以达成 user-facing readability. 实际使用时发现 ai_video_management webapp 的 casting / shot-concat / dramas-extraction feature 全部依赖 `^c\d+(_.*)?$` 正则筛选, 纯中文 folder 不被 enumerable → casting UI dropdown 空 → 无法 assign actor. v5 hybrid 兼顾两者: folder 名 c-prefix (webapp 兼容) + 文件名内部中文 (cross-doc + 人类 readable). 编号约定: 按 ep01 出场顺序 + 角色重要性 manually assign — 主角 + 前世 + 师父 + 主女主 + 童年姐姐 + 6 betrayers = c01-c11 (per project).

**v3 → v4 演进逻辑**: v3 把多文件 (bible + 立绘 + turntable) collapse 到 single-file 以避免文件夹臃肿; v4 把 single-file 重新 expand 到 folder 因为 (a) dual-state 角色 (主角双形态) / 复杂叛者 (戚归砚 cover/truth 双层) 在单文件内堆叠多个 turntable + 多个 Seedream 立绘 prompt → 单文件 ≥ 1000 行 难以 review; (b) 用户希望按需 split 不同 turntable / 不同 Seedream 立绘 / 不同配音参考片段到 sibling 文件 (例如 `裴知秋/state_a_turntable.md` + `裴知秋/state_b_turntable.md` + `裴知秋/state_a_seedream.md` 等). v4 提供 folder + 主 bible 文件 + 可选 sibling 文件的灵活契约.

新结构 (v5):

```
characters/
├── c01_{pinyin_slug}/   # webapp-compatible folder name
│   ├── {中文名}.md      # 主 bible (Chinese filename, 含 rule #12.1 bible 全段 + 默认 turntable prompt)
│   ├── state_a_turntable.md   # 可选 — dual-state 角色单独的 state A turntable
│   ├── state_b_turntable.md   # 可选
│   └── {anything}.md          # 可选
├── c02_{pinyin_slug}/
│   └── {中文名}.md
...
├── c11_{pinyin_slug}/
│   └── {中文名}.md
```

最小落地形态: 每角色至少 1 个 c{NN}_ folder + 1 个 `{中文名}.md` 主 bible 文件. Sibling 文件按角色复杂度按需添加, stage-6 validator 不强制要求 sibling 文件存在.

**Cross-reference 路径更新**: 所有引用 character bible 的 shot prompt / scene 描述 / 任何 sibling 文档, 路径从 `characters/{中文名}/{中文名}.md` (v4) 改为 `characters/c{NN}_{pinyin}/{中文名}.md` (v5). (历史使用 `-{身份}.md` 后缀作 disambiguation 的 mozun_chongsheng 项目已经是 c-prefix 兼容形态, 不追溯.)

文件结构：

````markdown
# {中文名} · {身份}

## 角色定位
（per rule #12.1）

## 锁定描述符（11 字段，跨集 byte-identical）
（per rule #12.1 + #12.7：含 6 子项 face-differentiator + 标志特征点 row #11）

## 性格 / 动机
## 标志台词或口头禅
## 弧光
## 关键场景
## 标志能力或动作
## 配音参考（planning-only，v1 不生成 TTS）
## 负向

---

# 视频 reference prompt — Seedance / Kling / Sora / Veo / Runway Gen-3（7s locked-framing 5-phase single-take + 0-2s 一/二 lock + static landings at 0°/90°/180°）

> **用法**：复制下方代码块整段，粘贴到支持 video reference 的 AI 视频模型...

```text
{turntable prompt body — 7s locked-framing 5-phase single-take schema per rule #12.5 v10.2}
```

### 3 句数字计数台词（中文 "1, 2, 3"，配音演员对照表）

| ... |
````

**文件 schema：**

````markdown
# {中文名} · {身份} — 视频 reference prompt

参考: characters/{中文名}-{身份}.md
画幅: 9:16 竖屏 / 4K 原生分辨率

> **文件说明**：本文件含一段可直接 copy-paste 的视频 reference prompt（**7s 单 take, 镜头 0-2s 拍正面 + 2-3s 顺时针绕到左侧身 + 3-4s 停侧身 + 4-5s 顺时针绕到背面 + 5-7s 停背面 — Kling reference 上传约束 v11 (rule #12.5 v11, simplified prompt — camera motion 仅在 动作 timed beats 一次描述, plain Chinese);前 2s 自包含（一/二）byte-identical truncate-compat;static lock 在 0°/90°/180° 三个角度 supply downstream extract-3-views 管线**） + 一张 5 行 timed-beats 配音对照表。文件名沿用 `-立绘.md` 作为 legacy alias（per rule #12.5 v2）。

---

## 文字生视频 reference prompt — Seedance / Kling / Sora / Veo / Runway Gen-3（7s 单 take, 镜头依次拍正面 → 左侧身 → 背面, plain Chinese v11）

> **用法**：复制下方代码块整段，粘贴到支持 video reference 的 AI 视频模型（Seedance / Sora / Veo 3 / Runway Gen-3 / Kling 等）。**该样片本身**作为后续真正 shot 视频的 video reference 输入，锁定形象 + 声线 + 节奏。**注意：≤ 7s（rule #12.5 v11 时长）**（前 2s 必须自包含 byte-identical 一/二 — 下游 ai_video_management 短角色合辑 / ✂ 截到 2s 按钮均取 0-2s 片段；**镜头 motion ONLY 在 动作 timed beats 一次描述**, 不在 镜头/节奏/负向 字段重复;**3 个抽帧角度 (front t=1.0s / side t=3.5s / back t=6.0s) 全部来自 static lock 帧, framing byte-identical, 供下游 extract-3-views pipeline 用作 character sheet**）。

```text
{中文名} · {身份} — 角色 reference 7s 单 take

角色: {一句话锁定 byte-identical} + {体型 / 发型 / 服装 / 道具 inline 展开 per rule 12.4-A 无参考图分支}

场景: 中性灰 #808080 摄影棚 cyc wall 无缝背景, 地面同灰, 无家具.

镜头: 单 take 7s, 9:16 竖屏, medium-full ~40mm framing 全程不变 (头部约画面高度 1/5, 头顶到脚趾完整入画, 双脚距画面底缘约 5% 安全余量, 相机距角色距离不变 no dolly no zoom).

动作 (7s timed beats):
  - 0-2s: 镜头正面拍角色 medium-full. 角色站定, 自然呼吸, 眼神看镜, 说"一", "二". **必须在 2.0s 前说完**.
  - 2-3s: 镜头围绕角色顺时针绕 90° 到角色左侧身. 角色保持站立不动只呼吸.
  - 3-4s: 镜头停在左侧身角度不动. 角色说"三, 我是 {本角色姓名}".
  - 4-5s: 镜头继续顺时针绕 90° 到角色背面. 角色保持站立不动只呼吸.
  - 5-7s: 镜头停在背面角度不动. 角色说**{本角色 bible "标志台词" 第 1 句}**, 然后说**{本角色 bible "标志台词" 第 2 句}**; 自然定格收尾.

台词 / 字幕: 内嵌唇形对齐音频 (中文). **前 2s 必须包含 "一" + "二" 的完整发音** (下游 2s 截取契约); 2-7s 台词从角色 bible `## 标志台词或口头禅` 段前两句逐字复制.
  1. "一" (0-1s)
  2. "二" (1-2s, **2s 前结束**)
  3. "三, 我是 {角色名}" (2-3s, 自我识别 + 镜头转向侧身)
  4. {标志台词 #1} (3-5s, 标准声线 baseline, over 左侧身 hold + 转到背面)
  5. {标志台词 #2} (5-7s, 情绪 peak + final lock, over 背面 settle)

光线 / 色调: 三点布光 — 5500K key + 4500K fill + 7000K rim; 灰背景中性; {角色专属光晕, 如魔气 / 仙气, 可选}.

节奏: 单 take 7s, 角色站立不动只说话, 镜头按 动作 timed beats 旋转 + 停顿.

渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实皮肤布料质感.

比例: 9:16

时长: 7s

负向: {项目级负向 from style_guide.md} / {角色专属负向 from bible} / 不要 dolly / 不要 zoom / 不要 距离变化 / 不要 framing 变化 / 不要 角色转身 / 不要 角色走动 / 不要 cut / 不要 transition / 不要 fade / 不要 超过 7s.
```

### 5-row timed-beats + dialogue 对照表

| # | 台词 | 用途 | 时段 | 情绪基调 |
| --- | --- | --- | --- | --- |
| 1 | 一 | 起声 / 声线 timbre 锚点 | 0-1s | 平稳 / 中音（byte-identical 跨角色） |
| 2 | 二 | 中段 / 节奏校准（**2s 前结束**） | 1-2s | 平稳 / 中音（byte-identical 跨角色） |
| 3 | 三, 我是 {角色名} | 自我识别 + 镜头转向侧身 | 2-3s | 平稳 / 中音 |
| 4 | {标志台词 #1} | 标准声线 baseline (over 左侧身 hold + 转到背面) | 3-5s | character-specific (per bible 配音参考) |
| 5 | {标志台词 #2} | 情绪 peak + final lock (over 背面 settle) | 5-7s | character-specific |

参考 `配音参考` 段（characters/{中文名}-{身份}.md）。**0-2s 段 byte-identical 跨角色**（一 + 二, 保 truncate 切片 voice baseline 可对齐）；**2-7s 段 per-character**, 台词逐字取自 `## 标志台词或口头禅` 段前两句。

**抽帧时间戳契约 (v11 rule, per ai_video_management follow-up 099):** 下游 `libs/domain/value_objects/character_video__valueobject.py` 的 `CANONICAL_VIEWS` 锁定在 (front t=1.0s, side t=3.5s, back t=6.0s) — 与 v10.2 相同 (schedule 不变, 只是 prompt rendering 简化)。3 个时间点全部 anchored on **static landings** (mid 0-2s static front / mid 3-4s static side / mid 5-7s static back)。如本 rule 再次 rev (v12+), 这 3 个 constants 必须同步更新。
````

**0-2s static + 2-3s motion + 3-4s side static + 4-5s motion + 5-7s back static 设计原则（rule #12.5 v10.2）：**

- **全程单镜头单 take with continuous timecode, 5 phases: 3 static landings + 2 motion bridges, 锁定 framing throughout (no dolly, no zoom)**。phase 边界 (t=2 / t=3 / t=4 / t=5) 是 motion velocity 0 ↔ non-zero 的过渡, 每个 motion bridge 起末速度 = 0 平滑加减速, 不是 snap-cut。镜头/动作字段含 motion 描述但 motion 总时长仅 2s (= 2 × 1s bridges)。Kling validator hypothesis v10.2: motion 起末 0 velocity = no motion blur ≠ cut/transition; bookended motion 段是 v6 whip-pan 的 categorically different case (v6 是 720°/s 极速连续 spin)。**Risk**: 如 v10.2 仍被 validator 拒, 退到 v10.3 (drop 一个 motion bridge — 0-2s front + 2-3s motion 0°→90° + 3-7s static side 4s, 失去 back angle, extract 退化到 front + side 可靠) 或 v10.4 (drop 双 motion bridges — 全 7s 静态正面 = v8 + v10.2 negatives, 失去 side + back, extract 退化到 front-only)。
- **0-2s 段对所有角色 byte-identical**："一" + "二"。无任何角色化变量。下游 ai_video_management 短角色合辑（`_CONCAT_SEGMENT_S = 2.0`）+ ✂ 截到 2s 按钮 切到的 2s 片段, 跨 10+ 角色全部含 "静态正面 medium-full + 一+二 发声", voice timbre baseline 可直接对齐。**0-2s 段内容在 v8 / v9 / v10 / v10.2 共同 byte-identical (一+二+正面静态), framing 从 v8/v9 的 wide ~35mm 收紧到 v10/v10.2 的 medium-full ~40mm — 内容契约不变 framing 微调。**
- **"一" + "二" 必须在 2.0s 前完成发声**（与 v5/v6/v8/v9/v10 同契约）。
- **锁定 framing 全程 throughout**: 5 phases framing byte-identical (头部 ~1/5 frame, 头顶到脚趾完整入画, 双脚 ~5% 底边安全余量) — 仅角度变化。这是 v10 核心契约 preserved by v10.2, 为下游「抽 3 视图 + 音频」管线 (follow-up 093) 提供 framing-consistent 抽帧。
- **3 个 static landings 提供 clean 抽帧 sources**: front (0-2s) / side (3-4s) / back (5-7s)。每个 static landing 期间镜头完全不动, 抽帧管线在 mid-window timestamps (1.0 / 3.5 / 6.0) 取帧, 不依赖模型估算 orbit 进度。这是 v10.2 vs v10 的根本性架构改变 — **角度契约从「时间 × 速度」改为「明确 landing 角度 hold」**。v10 假设模型能 follow timed-beat 速度指令 (45°/s for 4s = 180°), empirical 发现模型 under-rotates (~22°/s) 导致 side/back picks 落在错角度;v10.2 把 picks anchor 到 static lock 帧从根本上 sidestep 此 sync 问题。
- **2-7s 段 per-character**: 3 句台词从角色 bible `## 标志台词或口头禅` 段前两句取 (slot #3 = 三+自报姓名 自动生成 over motion 0°→90° / slot #4 = #1 over 静态侧身 hold + motion 90°→180° / slot #5 = #2 over 静态背面 settle 兼做 catch + 情绪 peak + final lock); 角色仍站定不动, 仅说话 + 自然呼吸 + 头部微动。
- 一旦确定，跨 follow-up 不变（0-2s 锁定不能动；5 阶段 timed beats template + 锁定 framing + 3 static landings 不能动；抽帧时间戳 (1.0/3.5/6.0) 与 static lock windows 锁定; 2-7s 段 dialogue 内容随 character bible 修订而修订, 但结构不变）。

**Turntable 视频 prompt 锁定字段（10+ 角色 byte-identical, only 2-7s 段台词 per-character）：**

`场景` / `镜头`（5-阶段 timed beats single-take template, 3 static + 2 motion bridges, locked-framing）/ `光线 / 色调` / `节奏`（锁定 framing 5-phase）/ `渲染样式` / `比例` / `时长（=7s）` / `台词 0-2s（=中文 "一, 二"）` / 视频专属负向 14 个字段在所有角色 turntable prompt 中 byte-identical。`角色:` 段 + `台词 2-7s` 段 per-character（后者从角色 bible `## 标志台词或口头禅` 段前两句取）。10+ 角色 turntable 输出仍可剪辑成「角色介绍合集」: 0-2s 段跨角色 voice baseline 对齐, 2-7s 段拼出每个角色 5 秒含 90°/180° silhouette + 标志台词 的 casting reel。

**模型路径与 PNG 抽帧：**

- **支持 video reference 的视频模型**（Seedance / Sora / Veo 3 / Runway Gen-3 / Kling 等）：直接 copy-paste 此 prompt 生成 turntable 视频；视频本身作为后续 shot prompt 的 reference 上传。
- **仅 image-to-video 的旧模型**（Kling 早期版本，需 PNG input）：从 turntable 视频抽一帧（推荐 0s 正面帧）作为 PNG，喂 Kling image-to-video。无需独立 image prompt 文件。
- **声线 lock**：v1 visual-only 模型输出静音视频，"1, 2, 3" 3 个数字作为唇形 reference；v2 audio-aware 模型输出含音频的 voice reference，整段视频作为 video-to-video reference 喂下游 shot prompt（声线 timbre + 咬字基线由 3 个数字的发音锚定，多情绪表演由 shot prompt 的 dialogue script 承担）。

**与 rule #12.2 的关系：**

rule #12.5 v2 **完全 supersedes rule #12.2**。rule #12.2（角色立绘 prompt 单文件 8 子段结构）不再生效——character pipeline 不再独立生成 image prompt 文件。如历史 ai_video 项目仍保留 rule #12.2 格式的立绘 prompt 文件，可保持原状作为 archive，但新生成的 character ref 文件按 rule #12.5 v2 schema。

*(Originated from follow-up "character dual-prompt copy-paste file" — 2026-05-10；rev — follow-up "drop image prompt, video-only" — 2026-05-10：Seedance 等已支持 video reference 上传，①号 image prompt 块去除；rule #12.2 完全 superseded；workflow simplified to 单 prompt → turntable 视频 → 后续 shot reference 一站到位。rev — follow-up "compress reference videos to 2.9s" — 2026-05-10：rule #12.5 v4：turntable 时长 12s → 2.9s（Seedance 等 reference 上传约束）；5 句多情绪台词 → 3 个数字 "1, 2, 3"；动作 beats 重排为 全身定场 + 360° 快环 + 面部推近 三段，最大化 2.9s 内信息密度。rev — ai_video_management follow-up 078 — 2026-05-17：rule #12.5 v5：turntable 时长 2.9s → 4s（下游 Seedance 等 reference 上限放宽，多 ~38% 时间做身份捕捉）；Arabic "1, 2, 3" → 中文 "一, 二, 三"；动作 beats 重排为 0-1s 定场 + 1-2s 360° + 2-3s 推近 + 3-4s 1s 特写定格 四段；新增「前 2s 自包含」契约 — "一" + "二" 必须在 2.0s 前完成发声 + 镜头回正到正面，对齐 `ai_video_management` 短角色合辑 trim 2s + ✂ 截到 2s 按钮的下游切片边界。rev — ai_video_management follow-up 088 — 2026-05-17：rule #12.5 v6：turntable 时长 4s → 15s（下游 Seedance / Sora / Veo / Runway / Kling reference upload ceiling 2026-05 中旬放宽到 ≥ 15s, 同 rule #12.10 v3 scene-walkthrough dim-comparable）；保留 v5 的 0-2s lock（"一" + "二" + 正面定场 + 360° 回正）byte-identical 跨角色作 truncate-compat 契约；新增 2-15s per-character casting reel — 6 个 camera moves（推近 / 反向 90° / 拉远 3/4 / 横向 pan 360° / 拉近 medium / 特写）+ 4 句台词从角色 bible `## 标志台词或口头禅` 段三句逐字 + 13-15s 最 character-defining 一句作 catch close, 全部加 表情 range silent capture 段（8-11s）。台词跨角色不再 byte-identical（仅 0-2s 段保 byte-identical）；2-15s 段给 Seedance 真实 per-character voice timbre + emotion + 标志特征点 final-lock close-up reference。rev — ai_video_management follow-up 090 (v7 7s casting reel) — 2026-05-18: SUPERSEDED before implementation by follow-up 091。spec only, never shipped。kept on file as audit trail。rev — ai_video_management follow-up 091 — 2026-05-18：rule #12.5 v8 (skip v7)：turntable 时长 15s → 7s + **全程静态单镜头 single take, 锁定机位, 零运动**。Kling validator 拒收 v5/v6/v7 因 fast 360° orbit + push-in/pull-out/pan 全被判 cut/transition + spin blur 让 character-detector miss subject。v8 完全弃 multi-camera ambition: 5 段 timed beats 全部「同机位同构图」, 角色仅自然呼吸 + 头部微动 + 说话。0-2s 段简化为静态 frontal 全身 + 一/二 (弃 v5/v6 的 360° silhouette pass, truncate output 仅给 frontal voice baseline)。2-7s 段 per-character: 三 + 自报姓名 / 标志台词 #1 baseline / 标志台词 #2 catch+peak+final-lock。8-row dialogue table → 5-row。video-specific negatives 加 no-camera-motion + no-cut + no-turn-in-place 三组 Kling-validator-aware ban; 弃 v6 的 6-camera-move 段 ban + 360° direction-reversal ban。rev — ai_video_management follow-up 092 — 2026-05-18 (晚段)：rule #12.5 v9 (supersedes v8)：turntable 时长 7s → 15s + **单 take 连续运镜 single continuous take, 慢速 + 单方向 + 无方向反转**。用户拒绝 v8 的 multi-angle + face close-up reference trade-off (v8 静态全身远景下面部占 1/6 frame 太小不能 read; 侧身/背面 silhouette 全失), 092 直接 reversal v8 走 slow-motion 路线。v9 hypothesis: Kling validator 的 cut/transition 判定核心因子是**速度**+ 方向反转, 不是 motion 本身。v5/v6 fast 360° (~720°/s, 半秒 whip) + v6 多 camera moves 含方向反转 触发 validator; v9 走 ≤ 45°/s slow orbit + 单 dolly-in + 同段 reverse-dolly 隐藏在 orbit 弧线 (不构成方向反转) + 13-15s 锁定收尾。5 阶段连续运镜: 0-2s 锁定 (v8 同) + 2-5s 缓慢 dolly-in 到 medium close-up (face clear) + 5-13s 缓慢顺时针 360° 环绕 + 同段缓慢 reverse-dolly 回 wide + 13-15s 锁定收尾。0-2s 段 v8 + v9 完全相同 byte-identical (下游 webapp 2s 切片输出不变)。dialogue table 5-row 不变, 但 slot 3 (2-5s)/4 (5-10s)/5 (10-15s) 时段重排匹配 v9 5 阶段。video-specific negatives 由 v8 的 no-camera-motion 全禁 → v9 的 slow-motion-only + no-reversal + no-stop-and-go 限定 (11 项)。Risk acknowledged: 如 v9 仍被 validator 拒, 退到 v9.1 (drop orbit, keep 5s push-in) 或 v8 (7s static)。rev — ai_video_management follow-up 096 — 2026-05-18：rule #12.5 v10 (supersedes v9)：turntable 时长 15s → 7s + **锁定 framing single continuous take, no dolly + no zoom, 仅旋转**。v9 (092) 的 dolly-in + reverse-dolly 设计在 follow-up 093 「抽 3 视图 + 音频」管线上线后暴露结构性问题: front pick (t=1.0s) 在 wide 段抽到 full-body, side pick (t=7.0s) 落在 reverse-dolly 中段抽到 head ~1/3 frame, back pick (t=9.0s) 落在 reverse-dolly 末段仍非 byte-identical framing — 3 张 png framing 不一致, 无法作为 coherent character sheet 喂下游模型。v10 完全 reverse v9: drop 2-5s dolly-in (失去专属 face MCU, 接受 medium-full ~40mm 下面部 ~1/5 frame ≈ 360-400px tall) + drop 5-13s reverse-dolly (相机距角色距离全程锁定) + 360° orbit 砍到 180° (身体左右对称, 270° 右侧身 redundant) + 时长 15s → 7s。3 阶段 timed beats: 0-2s 静态正面 medium-full (一+二, byte-identical 跨 v8/v9/v10) + 2-6s 缓慢顺时针 180° orbit at 45°/s (相机距角色距离锁定, no dolly, no zoom) + 6-7s 锁定背面 medium-full settle。0-2s 段内容跨 v8/v9/v10 byte-identical (下游 webapp 2s 切片输出 content 不变, framing 微调 wide → medium-full)。dialogue table 5-row 不变, slot 3 (2-3s)/4 (3-5s)/5 (5-7s) 时段重排匹配 v10 3 阶段。video-specific negatives 由 v9 的 11 项 → v10 的 13 项 (加 no-dolly / no-zoom + no-framing-change 两组新 ban, 删 v9 的 reverse-dolly-allowed 例外)。配套代码: `libs/domain/value_objects/character_video__valueobject.py` 的 `CANONICAL_VIEWS` 时间戳 (1.0, 7.0, 9.0) → (1.0, 4.0, 6.0) — front pick t=1.0s 不变 (仍 mid 0-2s 静态), side t=4.0s = (4.0-2.0)*45°/s = 90°, back t=6.0s = (6.0-2.0)*45°/s = 180°。Risk acknowledged: 如 v10 仍被 validator 拒, 退到 v10.1 (drop orbit, 全 7s 静态正面 = v8 + 2-7s per-character dialogue, 抽帧管线退化到只有 front 可靠) 或 v10.2 (orbit 内插 90°/180° 处短暂 ~0.3s static hold)。096 用户在 clarifying 中明确选 locked-framing trade-off (3 张 png 一致 > 专属 face MCU)。rev — ai_video_management follow-up 098 — 2026-05-19：rule #12.5 v10.2 (supersedes v10)：turntable schema 由 v10 的 「3 阶段 (static front + 4s 连续 orbit + static back)」 → v10.2 的 「5 阶段 (static front + 1s motion + static side + 1s motion + static back)」, 加入两个 mid-shot static landings at 90° + 180°。用户 empirical 实测 (2026-05-19, 首批 v10 渲染后): 模型 under-rotates v10 单条 4s 连续 orbit (~22°/s 实测速度, ~半速), 且 motion 段似乎 4-5s 才真正启动 — 7s 视频末帧仍在 ~90° 侧身, 根本没到 180° 背面;`抽帧时间戳 (1.0, 4.0, 6.0)` 在 v10 source 上 side picks 落在仍接近正面位置, back picks 落在 ~90° (实际显示 side)。Root cause: 视频模型不精确遵循 timed-beat 速度指令, 「slow continuous orbit at 45°/s for 4s」 给模型太多 latitude — 模型解读 "slow" 时按内部 pacing 估算 + 短 clip 内倾向 under-rotate 规避 motion-blur。v10.2 把 latitude 取消: 3 个 static landings (front 0-2s, side 3-4s, back 5-7s) + 2 个 1s motion bridges, 每个 motion bridge 必须精确终止在指定角度 (90° at t=3s, 180° at t=5s), static lock 段镜头完全不动。抽帧 picks 全部来自 static 帧, sidestep 模型 orbit pacing 不准的根本问题。配套代码: `libs/domain/value_objects/character_video__valueobject.py` 的 `CANONICAL_VIEWS` 时间戳 (1.0, 4.0, 6.0) → (1.0, 3.5, 6.0) — front t=1.0s 不变 (仍 mid 0-2s static), side t=4.0s → t=3.5s = mid 3-4s static side (v10 的 4.0s 在 v10.2 已是 motion bridge 起点), back t=6.0s 不变 (仍 mid 5-7s static back, 但 v10 此 pick 落在 orbit 末段, v10.2 此 pick 落在 static 中段 1s 远离 motion-end)。dialogue table 5-row 结构 + 时段不变 (slot 3 = 2-3s, slot 4 = 3-5s, slot 5 = 5-7s), 仅 用途 column micro-edit ("orbit 起" → "motion 0°→90°", "over orbit 0-90°" → "over 静态侧身 hold + motion 90°→180°", "over orbit 90°-180° + 锁定收尾" → "over 静态背面 settle")。video-specific negatives 由 v10 的 13 项 → v10.2 的 14 项 (drop `不要 mid-shot freeze (除 0-2s + 6-7s 外, 2-6s 段全程匀速运动)` v10 ban — v10.2 显式 INTRODUCES 90° + 180° 两个 mid-shot static landings — 此 ban 直接 conflict, 必须 drop; add `不要 motion 跨越目标角度` + `不要 静态段内继续微调机位` 两组 new bans 确保 1s motion bridges 精确停在 angle landings 且 static lock 段绝对静止); modify `不要 快速运镜` qualifier 由 「orbit 旋转速度 ≤ 45°/s」 → 「motion bridge 段速度 ≤ 90°/s 平均, 起末 0 速度平滑加减速」 (motion 段更短但峰值速度可略高, ramp-up/down 起末 0 velocity 是 anti-blur 契约);  modify `不要 任何 cut / transition` qualifier 加 「(static-to-motion-to-static 切换是 0 velocity 边界, 不是 cut)」 显式 disclaim, 防止 validator 误判 phase 边界; modify `不要 旋转过程中角色脸部 motion blur` qualifier 由 「慢速 orbit + 角色站定」 → 「motion bridge 起末 0 速度 + 角色站定」。Risk acknowledged: v10.2 是 hypothesis (bookended motion 段 ≠ v6 whip-pan, validator 应接受); 如 v10.2 仍被 validator 拒, 退到 v10.3 (drop 一个 motion bridge, 失去 back angle, extract 退化到 front + side 可靠) 或 v10.4 (drop 双 motion bridges, 全 7s 静态正面 = v8 风格 + v10.2 negatives, 失去 side + back, extract 退化到 front-only); v11+ multi-clip path (3 个 separate clips concatenated) reserved for if all single-clip variants fail。rev — ai_video_management follow-up 099 — 2026-05-19：rule #12.5 v11 (supersedes v10.2)：schedule 不变 (3 static landings + 2 transitions + locked framing), CANONICAL_VIEWS (1.0, 3.5, 6.0) 不变 (无 code change), **仅简化 prompt rendering**。Root cause for v10.2 → v11: user 实测 v10.2 渲染发现 motion 实际起于 ~5s (而非 spec 的 2s), 因为 prompt 把 motion 路径在 4 字段重复描述 (镜头 + 动作 + 节奏 + 负向 qualifier 段落), 用 "motion bridge" / "static landing" / "locked-framing" / "single continuous take" 技术 jargon, 模型在多 conflicting 描述下 average 而 under-commit to motion。User: "I think kling got confused, you need to tell it in a more simple way and only once in the prompt"。v11 收窄: 镜头 = 仅 framing/lens specs (no motion path), 动作 = ONLY 字段描述 motion 路径 + 时间, 节奏 = 一句话 (无路径重复), 负向 = 10 项简单 bans (无 qualifier 段落)。Plain Chinese: "镜头围绕角色顺时针绕 90° 到角色左侧身" / "镜头停在左侧身角度不动" — 不用 "motion bridge" / "锁定机位 medium-full" 等 jargon。锁定机位 jargon 全部移除 — model 可能把 "锁定" 当 "全程不要动" 理解。Risk acknowledged: 如 v11 简化后模型仍 under-commit, 说明问题不是 prompt 冗余而是模型对短 clip 内 motion 的根本偏见; 退路 v12 (shift schedule earlier, 0-1s static + motion + 3-4s static side + motion + 5-7s static back, 牺牲 0-2s truncate-compat 契约, CANONICAL_VIEWS side 0.5/3.5/6.0) 或 v13 multi-clip (3 separate clips concatenated)。)*

#### 12.5-A 角色造型覆盖照片契约（v2 per follow-up 2026-05-25 — 取代 v1 generic boilerplate）

**The v1 generic-paragraph approach is废话 — it told the model "use the prompt settings" without naming WHAT those settings are.** v2 replaces the generic paragraph with a **concrete `角色造型` line that names the actual 发型 / 服装 / 道具 / 气质 values inline**, pulled byte-identically from the character's 锁定描述符 #4 / #5 / #6 / #9.

**Why concrete over generic:** AI video models attend to specific tokens. Telling the model `"装扮按 prompt 设定"` adds zero information about the desired look — the model doesn't know what 发型 the character has unless you write it. Naming `"发型 = 黑发束白玉冠 鬓边散两缕碎发"` directly is the only signal that prevents the model from carrying the actor photo's current 假发 / 发型 into the output.

**Mandatory format (character 7s turntable prompt 的 `主体:` / `角色:` 行下方 必须 byte-identical re-paste):**

```text
角色造型 (覆盖演员照片日常素颜 + 现成短假发 — 模型禁止 carry T-shirt / 现代发型 / 演员素颜 入画):
- 发型 (**以本 prompt 为准, 严禁照抄演员参考照片的实际发型 / 假发 / 现代发型**): <锁定描述符 #4 「发型 / 发色」字段值, byte-identical 复述>
- 服装: <锁定描述符 #5 「服装 / 主色 (hex)」字段值, byte-identical 复述>
- 道具: <锁定描述符 #6 「标志道具」字段值, byte-identical 复述>
- 神情 / 气质: <锁定描述符 #9 「气质」字段值, byte-identical 复述>
```

**Why 发型 gets its own inline annotation (v3 — 2026-05-25 amendment):** the umbrella `覆盖演员照片...` preamble is easy for the model to skim past as boilerplate, and 发型 is empirically the field most prone to leak from the actor reference photo (演员日常照普遍戴现成短假发，模型默认 carry 这种 modern 短发型). Inlining the prohibition into the 发型 row itself — adjacent to the desired hairstyle descriptor — gives the model a second strong signal exactly where it needs it.

Four contracts:

1. **`覆盖演员照片` preamble = 1 line, ≤ 30 字** — the only "abstract" prose allowed; the rest is concrete values.
2. **Each `- 发型 / 服装 / 道具 / 神情` row pulls from the character's 锁定描述符 row** byte-identically. Do NOT paraphrase or condense — the values in 锁定描述符 are already the canonical short forms.
3. **All four rows are required** — if a character's 锁定描述符 #6「标志道具」is empty (rare), write `- 道具: 无标志道具` literally, not omit the row.
4. **No `演员参考照片解读契约` v1 paragraph** — the v1 150-字 generic boilerplate is **abolished**. Any character file still carrying v1 must be migrated. Replace the entire v1 line (boilerplate + any "本角色装扮锚:" addendum) with the v2 block.

**Punctuation:** the preamble's `(` `)` are half-width; the trailing `:` after the preamble is half-width; bullet rows use `- ` (hyphen + space) and a half-width `:` after the field name; values inside rows preserve whatever punctuation the 锁定描述符 used (full-width or half-width, both fine).

**应用范围 (v2 unchanged from v1):**

- ✅ **必须**：每个 character `c{N}_{中文名}/c{N}_{中文名}.md` 中 rule #12.5 v11 turntable prompt 的 `主体:` 行下方紧接 4 行 re-paste 该 block，作为 prompt body 第二段。
- ✅ **推荐**：shot prompt（rule #12.6 v2）若该 shot 直接上传演员照片作为额外 reference（非 turntable mp4 派生）时，shot prompt body 的 `角色:` 行下方也 re-paste。
- ❌ **不必要**：仅上传 turntable mp4 作为 character reference 的 shot prompt（turntable 已经把角色造型 lock 进 mp4 里，下游模型不会再看到演员原始照片）。
- ❌ **不必要**：scene reference prompt（rule #12.10）— 场景与演员照片无关。

**与 rule #12.5 v11 schema 的关系：**

12.5-A v2 不改 v11 的 5 阶段 timed beats / 3 static landings / dialogue 5-row 表 / 14 项 negatives。仅在 prompt body 的 `主体:` 行后追加 5 行强制 `角色造型` block。Body 字数预计增加 ~150–250 字（中文，因角色而异），须压在**全局 2000 字硬顶**内（2026-06-18；超 = blocker，靠去重而非堆字）。

**与 character bible `## 锁定描述符` 字段的关系：**

12.5-A v2 是 #4 / #5 / #6 / #9 的 authority 显式投射到模型可见的 prompt body 内 —「锁定描述符」是 source of truth，本 block 是 byte-identical 投影。若 character bible 的 #4 / #5 / #6 / #9 后续修改，本 block 必须同步重渲染（不可两处独立编辑）。

**Stage-6 validators 必须 reject:**

- 任何 character file 仍 carry v1 `演员参考照片解读契约: 上传的演员参考照片为素颜 + 戴现成假发 ...` boilerplate。
- 任何 character file 的 prompt body 缺失 `角色造型` block（无论该 character 是否原本有 v1 boilerplate）。**所有 character prompts 都必须有 `- 发型 ...` 这一栏**，跨剧无例外。
- 任何 character file 的 `角色造型` block 中 `- 发型 / - 服装 / - 道具 / - 神情` 行的值与该 character 的 锁定描述符 #4 / #5 / #6 / #9 不一致。
- 任何 character file 的 `- 发型` 行缺少 `(**以本 prompt 为准, 严禁照抄演员参考照片的实际发型 / 假发 / 现代发型**)` 内联注解 — v3 强制 inline 注解必须 byte-identical 出现在 row label 上。

*(v1 originated from follow-up "actor photo is bare face + temp wig, model should re-style per character" — 2026-05-24。v2 supersedes v1 per follow-up "这段提示词是废话，请写明你要的发型是什么" — 2026-05-25。v3 amendment same day per follow-up "每一个charactor prompt都应该加入发型这一栏目，而且标注不能完全照抄我给的reference" — extends the `角色造型` block requirement to ALL character prompts cross-drama (not just those that originally had the v1 boilerplate), and adds the inline `严禁照抄演员参考照片` annotation directly on the `- 发型` row label so the prohibition sits adjacent to the desired hairstyle descriptor — the field most prone to leak from the reference photo.)*

#### 12.6 单一 shotNN.md 文件 schema（v2，per follow-up 009）

每 shot 一份 `shotNN.md` 文件，含四段：① 人类 review 用的 Shot context；② **Reference placeholders**（NEW per follow-up 009）— 列出本 shot 涉及的所有角色 + 背景场景 placeholder，user paste 到 Seedance 等模型时手动替换；③ **小说文本 / Novel prose**（NEW per follow-up "novel-prose per shot"）— 把本 shot 写成一段散文 / 小说叙事，让 user 顺读全 ep 所有 shot 的 prose 段时**有"在读一本仙侠小说"的体验**（不是 prompt 摘要，是带着文学描写的叙述）；④ 视频 prompt 代码块（含 `{ref_xxx}` placeholder 内联引用 + 多角色 dialogue script 格式）。

**Seam-frame still prompts 段已废止**（per follow-up 009 — drop start/end frame embedded code blocks）。Seam-frame 工作流仍保留作为 rule #11 的可选高阶 stitching 文档，但默认不在 shot file 内 ship；user 自行用 Seedream 生成 seam frames（image-to-video 模型路径）。

supersedes rule #5（pre-007 双管线 / 三件套 file 模型）+ rule #11 在 shot file 内嵌的 seam-frame block 部分（rule #11 stitching workflow 仍可独立用）。

**完整文件 schema（v2，per follow-up 009）：**

`````markdown
# ep{NN} / shot{NN} · {1-line shot summary from shotlist.md 内容 column}

## Shot context — human review

**Summary**: {2-3 句 — 本 shot 的叙事 / 视觉 / 钩点。derive from shotlist + episode.md。}

**出场角色 / Characters in this shot**:

| 角色 | 在本 shot 的角色 / 出场方式 | character file | turntable 必需 |
|---|---|---|---|
| {char1} | {正脸主体 / 全景配角 / 光影剪影 / 物件...} | `characters/{role}.md` | ✅ / ❌ |

**场景 / Scene**: {location + 时辰 + 氛围 + 配色}; references `scenes/{name}.md` if applicable, otherwise inline.

**时长 / Duration**: {X seconds — hard 上限 15s}。Timed beats: {0-3s / 3-6s / 6-Xs 摘要}。

---

## Reference placeholders — 复制 prompt 前请准备好以下 reference 并替换占位符

| Placeholder | 替换为 | 来源 |
|---|---|---|
| `{ref_<char_name>}` | 该角色 turntable.mp4 / 角色 reference 视频 | `characters/{role}.md` 渲染所得 |
| `{ref_<scene_short>}` | 该场景 background reference 视频 / 图 | `scenes/{name}.md` 渲染所得（若立档）/ user 自备 |

每 shot 列出**所有出场角色 + 所有出现场景** 的 placeholder。

---

## 小说文本 / Novel prose

> 把本 shot 写成一段**带着仙侠小说文学性的散文叙述**。读者顺读全 ep 11 个 shot 的此段时，应有"在读一本小说"的连贯体验，而非翻 prompt 清单。内容**派生自** Shot context Summary + 视频 prompt body 的 `动作:` timed beats + `台词:` 字段 + `光线 / 色调:` + `场景:`，但用文学描写的笔法重写，可加入感官细节（魔气的腥涩、雷光的灼意、长袍下摆的沉甸）、心理留白、节奏短句。**禁止**直接复制 timed-beats 行（`0-2s: ...`）或 prompt placeholder（`{ref_xxx}`）。

{第一行必含 @ref header — 形如 `沧冥请参考:@<小说中文名>_<人物中文名>，白月清请参考:@<小说中文名>_<人物中文名>，长阶顶请参考:@<小说中文名>_<场景中文名>`。

- **<小说中文名>** = `README.md` H1 内的中文剧名（如 `魔尊归来`），**不是** task_name pinyin slug（task_name 是 `mozun_chongsheng`，仅供文件/路径用，不进 @-ref）。
- **<人物 / 场景中文名>** = `## Reference placeholders` 段 placeholder 的中文名部分，**去掉 `cN_` / `sN_` 前缀**。例：placeholder `{ref_c1_沧冥}` → @-ref 中写 `沧冥`；placeholder `{ref_s7_山道平台}` → @-ref 中写 `山道平台`。
- 每个 @-ref 之间用「，」分隔，**人物在前 / 场景在后**。
- @-ref header 后空一行，再写散文正文。

例：`沧冥请参考:@魔尊归来_沧冥，长阶顶请参考:@魔尊归来_长阶顶`}

{200-400 字一段散文（首选）；如本 shot 信息密度大可拆 2-3 段。台词以「」或""引号嵌入散文，不另设标签。}

---

## 视频 prompt — 复制下方代码块到视频生成模型

> **用法**：① 先按上方 Reference placeholders 表准备好 reference 文件并上传到模型。② 把下方代码块整段粘贴到 Seedance / Sora / Veo / Runway / Kling，**手动把 `{ref_xxx}` 占位符替换为模型识别的 reference 标记**（每模型语法略不同：Seedance 上传后用 `[reference]` 链接 / Kling 用 `input_image_urls` / 其他模型按其文档）。

```text
角色: {ref_<char1>} {char1 一句话锁定，含 face-differentiator}；{ref_<char2>} {char2 锁定}（若多角色）...
场景: {ref_<scene>} {scene 一句话锁定 或 inline 描述}
镜头: {景别 + 运动}
动作: {timed beats — 0-3s ... / 3-6s ... / 6-Xs ...}
台词 / 字幕（多角色 script 格式，per rule #12.4 v3）:
  - {ref_<char1>} {char1}: {内嵌硬字幕 | 后期软字幕 | 默剧} "{台词原文}" — {字体调性}
  - {ref_<char2>} {char2}: ...
  - 旁白 / 标题: ...（如有 narrator/titlecard 字幕）
光线 / 色调: ...
节奏: {慢 | 中 | 快 | 顿挫}
渲染样式: {影视级真人写实 + cinematic + 4K HDR + ... + 亚洲俊男靓女 + 东方传统五官 + ...}
比例: 9:16
时长: {≤15s}
负向: {项目级 14 项 stylization + 11 项 AI-同质化 + 视频专属负向 / 不要 镜头穿模 / etc.}
```
`````

**Placeholder 命名规范（v2 per follow-up 009）：**

- 角色 placeholder: `{ref_<中文名>}`（如 `{ref_沧冥}`）或 `{ref_<中文名>-<身份>}`（如 `{ref_叶无尘-乞丐}` — 若角色多形态需区分）
- 场景 placeholder: `{ref_<scene 简称>}`（如 `{ref_长阶顶}` / `{ref_紫霄宫}` — 取 scene 一句话锁定的关键词缩写）
- 半角花括号 `{}` 包裹（user copy-paste 后 find/replace 友好）。
- 占位符必须 **同时**出现在「Reference placeholders 段」表中 + 「视频 prompt」code block 内文中，user 替换时一对一对应。

**Shot context「出场角色」段已不含 turntable reference path** — reference path 信息**全部移到 Reference placeholders 段**避免重复。「出场角色」段保留 turntable 必需 ✅/❌ 列作为 review 提示。

**「Shot context」段必填子项 5 项**（缺一即 stage-6 validation 失败）：

1. `**Summary**:` — 2-3 句本 shot 概述。
2. `**出场角色 / Characters in this shot**:` 表 — 每行 = 1 角色 + 出场方式 + turntable reference path + 是否必需。Per follow-up 006 出场方式派生规则。
3. `**场景 / Scene**:` — location + 时辰 + 氛围 + 配色，引用 `scenes/{name}.md`（如已立档）。
4. `**时长 / Duration**:` — `X seconds — hard 上限 15s` + timed beats 摘要（与视频 prompt body 的 `动作:` timed beats 同步；hard 上限是 rule #6 的 15s）。
5. `**Reference uploads — pre-flight checklist**:` — checkbox 列表 turntable + (可选) seam-frame PNGs。

**「小说文本 / Novel prose」段必填规则**（per follow-up "novel-prose per shot"）：

- 每 shot 必含一段 `## 小说文本 / Novel prose`，位置在「Reference placeholders」之后、「视频 prompt」之前。缺失 = stage-6 validation `blocker`。
- 长度 200-400 字（散文一段；信息密度极大的 cover-frame shot 可放宽到 600 字 / 拆 2-3 段）。
- 内容必须**派生自同 shot 内**的 Summary + `动作:` timed beats + `台词:` + `光线 / 色调:` + `场景:`；可加感官 / 心理 / 节奏笔法，但不得引入 timed-beats 没有的新动作或新角色。
- **禁止**：① 直接复制 `0-2s: ...` timed beats 行；② 出现 `{ref_xxx}` placeholder；③ 出现 hex 色号（#xxxxxx）或 fps / 比例 / 镜头景别等技术语；④ 列表 / 表格 / 代码块（必须散文）。
- 台词以「」或 `""` 直接嵌入散文，不另加角色名 / 字体注解。
- 顺读全 ep（11 个 shot 的 prose 段拼接）应有**"读小说"的连贯阅读体验** — 句首避免重复 "本 shot..." / "镜头中..."，多用情节衔接词（"忽而" / "与此同时" / "话音未落" / etc.）。

**多角色 `台词 / 字幕` 扩展格式**（rule #12.4 v3 amend per follow-up 007）：

支持 multi-line 列每个角色的台词：

```
台词 / 字幕:
  - 沧冥: 内嵌硬字幕 "当年你们怎么对我，今日我便十倍奉还。" — 方正粗黑 白底黑边
  - 白月清: 后期软字幕 "你怎敢..." — 方正粗黑 白底黑边
  - 旁白 / 标题: 内嵌硬字幕 "——五合天封禁阵" — 方正粗黑 白底黑边
```

或保留单行短格式（仅 1 角色 / 默剧）：

```
台词 / 字幕: 内嵌硬字幕 "{台词}" — 方正粗黑 白底黑边
台词 / 字幕: 无台词 / 默剧
```

**15s 硬上限 + timed-beats 重排原则：**

- Rule #6（每 shot ≤ 15s）仍生效。Hard 上限不可超。
- 「Shot context」段的 `Duration` 行**显式列出 timed beats 摘要**（例: "8s — 0-3s 雷柱 / 3-6s 合围 / 6-8s 炸开"），帮用户一眼看到节奏分配；与视频 prompt body 的 `动作:` timed beats 字面同步。
- **多角色 dialogue 时段建议 ≤ 4s 一句**（中文 8-12 字平均 3-4s 念完）；如 dialogue 总时长 > 1/2 shot 时长，节奏标 `慢` 给唇形留时间。
- Action 与 dialogue 同时段时，timed beats 行用 `+` 连接：`0-3s: 沧冥赤瞳一闪 + 白月清「你怎敢...」`。

**人物台词强制原则（per follow-up 010）：**

- 每 shot 「台词 / 字幕」字段除「真正纯视觉镜头」（≤ 25% of all shots in any ep — 例如 lightning 合围 / 法宝群攻全景 / 闪剪 cliffhanger 等）外，**优先加入至少 1 句人物台词**（multi-line script 格式 if 多角色）。
- 台词内容**衍生自**:
  1. 角色 bible 的 `## 标志台词或口头禅`（首选；保持声线一致 + 角色 voice tonal 锁定）
  2. shotlist 内容 + episode.md 剧情节奏（次选；shot-specific dialogue / 旁白 / 标题字幕）
- 单角色 shot 的 dialogue 可保留单行 short format；多角色 shot 必用 multi-line script 格式（每角色一行 `- {ref_<char>} <char>: ...`）。
- 默剧 shot 仍可有「旁白 / 标题」字幕（title card / narrator subtitle），不算违反人物台词原则——但优先级低于实际人物 dialogue。

**Visual style 渲染契约（per follow-up 010）：**

- Webapp 渲染 markdown 时（如 `projects/ai_video_management/frontend/`），所有 ```text``` / ```yaml``` / 等 fenced code blocks **必含一键 copy button**（top-right corner，hover 显眼，点击 copy → 短暂 "已复制 ✓" feedback）。Implementation: ReactMarkdown 的 `pre` component override + `navigator.clipboard.writeText` + transient state for visual feedback.
- `{ref_xxx}` 占位符在 rendered markdown view 中**视觉 highlight**（pill / inline tag styling）—— 让用户在 review 时清楚识别哪些 token 要替换。Implementation: 代码外的 markdown 文本中（如 Reference placeholders 表）用 regex pre-pass 包 `<span class="ref-placeholder">{ref_xxx}</span>`；**代码块内**保持 raw `{ref_xxx}` 不修改 markup（保证 copy button 复制纯文本，不带 HTML markup）。
- 这两个 渲染契约是 webapp 实现层面的要求，不是 markdown 文件内容层面的要求；shotNN.md / character.md 文件内**不需要**显式包 placeholder pill markup 或 copy button；webapp 自动注入。

**Cross-reference**：

- Rule #12.4 v2 视频 prompt 14-字段 schema 仍生效，作为 `## 视频 prompt` 段 ```text ``` 代码块的内容标准。
- Rule #12.4 v2 静帧 seam 列字段（主体定义 / 姿态 frozen instant / etc.）仍生效，作为 `## Seam-frame still prompts` 段两个代码块的内容标准。
- Rule #11 seam-frame 工作流契约（loop-back / 抽帧 / Kling input_image_urls）仍生效；只是文件级别从独立 `_seedream.md` 折叠为内嵌代码块。
- Rule #12.5 v2 character ref 文件依然独立（character pipeline 与 shot pipeline 解耦）；rule #12.6 的合并仅作用于 shot 级别。

*(Originated from follow-up "single self-contained shot file" — 2026-05-10。Supersedes rule #5 file-set requirement; supersedes rule #11 seam-frame independent file structure; multi-character `台词` extension introduced.)*

#### 12.6-C [RETIRED 2026-05-30] Structured shot inputs (UI-editable) — removed per follow-up "drop structured shot_inputs block"

> **RETIRED 2026-05-30.** The `## Shot inputs (structured, UI-editable)` YAML block (the 6 顶层字段 `dialogue` / `camera` / `character_action` / `scene_atmosphere` / `start_frame_prompt` / `end_frame_prompt`) is **no longer authored in any `shotNN.md`**. Exposing a separate structured source-of-truth layer above the rendered prompt was reversed: maintaining two parallel representations (YAML + rendered code block) created drift with no v2 renderer ever shipping to reconcile them.
>
> **Current shot template** (per rule #12.6 single self-contained shot file): `## Shot context` → `## Reference placeholders` → `## 小说文本 / Novel prose` → `## 起始帧` → `## 结束帧` → `## 视频 prompt`. The rendered `## 视频 prompt` ```text``` code block is the **source-of-truth** for the shot; `## 起始帧` / `## 结束帧` carry the seam-frame still prompts (Seedream / Midjourney first/last frame for the Kling image-to-video workflow). There is no separate structured-inputs layer.
>
> **Migrated 起始帧 / 结束帧 字段集** (folded in from the retired YAML's `start_frame_prompt` / `end_frame_prompt`): `画面位置` / `角色姿态` / `构图` / `表情` / `场景元素` / `光线` / `渲染样式` / `负向`. `角色姿态` / `构图` / `表情` / `光线` 必填；`画面位置` / `场景元素` / `渲染样式` / `负向` 可省。
>
> **Migration done 2026-05-30**: every shot that carried the YAML block (the `nvdi_tuihun_houhuile` ep01 set) had its `start_frame_prompt` / `end_frame_prompt` detail folded into the `## 起始帧` / `## 结束帧` text blocks; the YAML section was deleted.
>
> The detail below is retained as historical record only.

#### 12.6-C Structured shot inputs (UI-editable, per follow-up "shot prompt template form" — 2026-05-27)

每个 `shotNN.md` 必须在 `## Shot context` 之后、`## 视频 prompt — 复制下方代码块到视频生成模型` 之前插入一个 **`## Shot inputs (structured, UI-editable)`** 区段，内含一个 ```yaml``` 代码块，**6 个顶层字段**：`dialogue` / `camera` / `character_action` / `scene_atmosphere` / `start_frame_prompt` / `end_frame_prompt`。这 6 类是导演视角下一个镜头的最小可编辑单元 — 用户可以直接在 webapp UI 上修改这些字段而无需碰下方的 rendered prompt 代码块。前 4 类描述视频本体, 后 2 类描述供 Seedream / Midjourney 生成的首末静帧 (Kling 2.1 image-to-video 工作流的 seam frame)。

**这 4 个字段是 source-of-truth**：渲染后的 `## 视频 prompt` 代码块 (`角色` / `场景` / `镜头` / `动作` / `台词` / `光线` / `节奏` / `渲染样式` / `比例` / `时长`) 在概念上是从 `shot_inputs` 派生的。**短期（v1）保持手动同步** — 修改 structured inputs 后必须同步更新下方 rendered prompt；**长期（v2）由 webapp 渲染器从 YAML 自动 emit 代码块**（FR-shot-render，待立项）。

**完整 YAML schema**：

````yaml
shot_inputs:

  # 1. 台词 + 语气 (UI-editable)
  # 每个 on-camera 台词 / 画外 OS / V.O. 都是一项
  # 若 shot 为默剧 / 静默 reaction, dialogue: []
  dialogue:
    - speaker: "<角色名 或 旁白 / 标题 / V.O. <角色名>>"
      timing: "<Xs-Ys>"
      text: "<台词原文，用「」嵌入>"
      tone: "<整句基底声色 — 音区 / 音量 / 语速 / 情绪关键词>"
      per_phrase_delivery:                              # 可选 — 多分句时给逐句念法
        - phrase: "<分句>"
          note: "<重音 / 拖音 / 末字 / 停顿处理>"
      delivery_note: "<反例约束 — '不要 copy reference sample 的平稳基调' 等>"
      subtitle_style: "<字幕字体 / 颜色 / 位置 / 前缀>"

  # 2. 镜头 (UI-editable)
  camera:
    motion: <fixed | dolly_in | dolly_out | pan | tilt | zoom_in | zoom_out | composite>
    focal_length: "<24mm | 35mm | 50mm | 85mm | 35mm→50mm 等>"
    framing: "<景别 — 全景 / 中景 / 中近景 / 特写 / 侧脸特写 / 等>"
    detail: "<机位 / 仰俯角 / 锁机位还是运动 / 推进幅度 / 单 take 还是切剪 等>"

  # 3. 角色动作 (UI-editable)
  # 每个 on-screen 角色一项, 用 beats 给 timed 动作
  character_action:
    - character: "<角色名>"
      beats:
        - t: "<Xs-Ys>"
          action: "<物理动作 — 不含语气和镜头, 仅人物自身的姿态 / 表情 / 道具操作>"

  # 4. 场景 + 背景氛围 (UI-editable)
  scene_atmosphere:
    location: "<场景名, 与 scenes/{name}.md 对齐>"
    state: "<接旨态 / 议事态 / 空厅态 / 等关键变化态>"
    scene_anchor:                                       # rule #12.10 scene mp4 dwell 取景锚
      dwell: "<#1 Hero / #2 Reverse / #3 Vert / #4 Mid / #5 Detail>"
      frames: ["<抽帧 PNG 文件名>", ...]                 # 0-N 张
      rationale: "<本 shot 用此 dwell 的剧情理由>"
    lighting: "<时辰 + 主光位置 + 色温 + 主光打在何处 + 反光质感>"
    palette:
      primary: "<#hex 主色 + 中文标签>"
      secondary: "<#hex>"
      accent: "<#hex>"
      highlight: "<#hex>"
    pace: "<节奏 — 慢 / 中 / 快 / 顿挫 + 节拍切分>"
    mood: "<本 shot 整体氛围关键词 ≤ 30 字>"

  # 5. Start frame prompt (UI-editable) — 静帧 prompt 给 Seedream / Midjourney 生成 shot 起始帧
  start_frame_prompt:
    beat_position: "t=0s — <剧情位置, e.g. 「定格起手, 角色 X 准备宣旨」>"
    subject_pose: "<瞬间姿态 — 一句话凝固描述 (此 shot 第一帧时, 主体在做什么的瞬间)>"
    framing: "<构图 — 9:16 + 景别 + 主体位置 + 焦距感>"
    expression: "<面部 + 眼神 + 嘴形 + 神情>"
    scene_elements: "<场景背景 — 哪些厅景元素入画 / 虚化程度 / 背景 bokeh>"
    lighting: "<光线方向 + 色温 + 高光位置 + 阴影分布>"
    style_keywords: "<影视级真人写实 + cinematic + 4K HDR + 真人皮肤毛孔细节 + 古装仙侠剧主演级颜值 + 等>"
    negative: "<负向, 可选 — 如「不要现代发型 / 不要塑料皮肤」>"

  # 6. End frame prompt (UI-editable) — 静帧 prompt 给 Seedream / Midjourney 生成 shot 结束帧
  end_frame_prompt:
    beat_position: "t=Xs (shot 末帧) — <剧情位置, e.g. 「念毕诏书末字落定」>"
    subject_pose: "<瞬间姿态 — 一句话凝固描述 (此 shot 最后一帧时, 主体在做什么的瞬间)>"
    framing: "<构图, 通常与 start frame 同 — 因 fixed camera, 但 dolly/pan/zoom shot 可不同>"
    expression: "<面部 + 神情, 与 start frame 应有明显差异 (反映此 shot 的情绪/动作弧)>"
    scene_elements: "<场景背景, 通常与 start frame 同>"
    lighting: "<光线, 通常与 start frame 同; 光位翻转/光位渐变 shot 例外>"
    style_keywords: "<同 start frame, 保持风格一致>"
    negative: "<负向, 通常与 start frame 同>"
````

**字段使用规则**：

- **dialogue** 是数组；每项是一条 dialogue beat。可空 (`dialogue: []`) 表示默剧 / 静默 reaction shot。`per_phrase_delivery` 字段可选，多分句台词建议填，单字台词可省。`delivery_note` 必填，写明"不要 copy reference sample 的平稳基调"或类似反例约束 — 否则 Kling 会按上传配音样本的语气走，覆盖剧情语气。
- **camera.motion** 必须从枚举值选 (`fixed` / `dolly_in` / `dolly_out` / `pan` / `tilt` / `zoom_in` / `zoom_out` / `composite`)，方便 UI 渲染下拉框。
- **character_action** 是数组；每个 on-screen 角色一项。`beats` 内不写台词语气 (那属于 dialogue) 也不写镜头运动 (那属于 camera) — **三类信息严格分离**，编辑一类时不污染另一类。
- **scene_atmosphere.scene_anchor** 直接 cite scene mp4 的 dwell + 抽帧 PNG (per rule #12.10)，告诉模型从场景 reference 哪个角度取景。`rationale` 字段写剧情理由 (与 dwell 选择的因果关系)。
- 所有 free-form 文本字段保留 byte-identical 中文 (per project rule "ai_videos 路径英文 / 内容中文")。

**为什么 6 个字段**：

- 前 4 类 (dialogue / camera / character_action / scene_atmosphere) 是导演 / 用户日常调改的视频本体 — "TA 说什么" / "镜头怎么动" / "TA 在做什么" / "场景什么氛围"。
- 后 2 类 (start_frame_prompt / end_frame_prompt) 是 Kling 2.1 / Sora image-to-video 工作流必需的 seam frame — user 把 start frame prompt 喂给 Seedream / Midjourney 渲染一张 PNG 作为起始帧, 把 end frame prompt 喂渲染末帧 PNG; 然后把这两张 PNG 上传到 Kling 作为 first_frame + last_frame, Kling 在两帧之间补全运动。**比直接 text-to-video 一致性更高** — seam frame 锁定了角色长相 + 镜头构图 + 光线, Kling 只需要补运动 + 表情过渡。
- 其他字段 (`渲染样式` / `比例` / `时长` / `负向`) 是全项目锁定常量, 不逐 shot 暴露给 UI。
- 字段越少 → UI 越简洁 → 用户编辑成本越低。`渲染样式` / `比例` / `负向` 在 webapp 上由项目级 settings 一次性配置, 不进入每 shot 的可编辑层。
- `时长` 由 `dialogue.timing` + `character_action.beats.t` 的最大值派生; 不单独暴露。

**start / end frame prompt 派生原则**：

- `start_frame_prompt` 应从 `character_action[].beats[0]` (第一个 beat) + `camera.framing` + `scene_atmosphere.lighting` 综合 derive — 描述"shot 第一帧的凝固瞬间"。
- `end_frame_prompt` 应从 `character_action[].beats[-1]` (最后一个 beat) + 同样的 camera/scene 综合 derive — 描述"shot 最后一帧的凝固瞬间"。
- 二者的差异承载了本 shot 的"动作 / 情绪 / 镜头" 变化 — 例如 shot01 起始帧是「定格起手」末帧是「念毕拂尘稳垂」; shot14 起始帧是装废态半垂眼帘末帧是 reveal 锐光全开。
- **fixed camera shot**: framing / scene_elements / lighting 在 start/end 帧通常 byte-identical, 仅 expression + subject_pose 不同。
- **dolly/pan/zoom shot**: framing 在 start/end 不同 (例如 shot05 `28mm → 32mm` 微推); 显式写明两帧的焦距差异。
- **光位翻转 shot** (e.g. shot14): lighting 在 start/end 显式不同 (start 顶左 30° → end 正面 0° 冷光)。

**字段与 rendered prompt 代码块的字段映射**：

| `shot_inputs` 字段 | 派生到 rendered prompt 的字段 |
|---|---|
| `dialogue` | `台词 / 字幕:` |
| `camera.motion` + `camera.focal_length` + `camera.framing` + `camera.detail` | `镜头:` |
| `character_action` | `动作:` |
| `scene_atmosphere.location` + `state` | `场景:` 行 + `场景视角锚:` 段头 |
| `scene_atmosphere.scene_anchor` | `场景视角锚:` 段（含 dwell / frames / rationale） |
| `scene_atmosphere.lighting` + `palette` | `光线 / 色调:` |
| `scene_atmosphere.pace` + `mood` | `节奏:` |
| `start_frame_prompt` | (新增 seam-frame section, 或独立 `## Start frame prompt` 代码块) |
| `end_frame_prompt` | (新增 seam-frame section, 或独立 `## End frame prompt` 代码块) |

**Stage-6 validation** *(RETIRED 2026-05-30 — superseded by the validation rules below)*:

- 上述所有 `## Shot inputs (structured)` / `shot_inputs` YAML 字段校验**全部移除**。缺失该段不再是 blocker。
- 反向校验：shot 中**仍残留** `## Shot inputs (structured, UI-editable)` 段 = `warning`（legacy residue — 应迁移移除：把 `start_frame_prompt` / `end_frame_prompt` 折叠进 `## 起始帧` / `## 结束帧`，再删 YAML 段）。
- `## 起始帧` / `## 结束帧` 缺 `角色姿态` / `构图` / `表情` / `光线` 任一 = `blocker`；`画面位置` / `场景元素` / `渲染样式` / `负向` 可省。
- `## 视频 prompt` 代码块为 shot 的 source-of-truth，按 rule #12.4 v2 14-字段 schema 校验（不变）。

*(Originated from follow-up "shot prompt template form" — 2026-05-27. User asks for the 4 categories — dialogue + camera + character action + scene/background atmosphere — to be UI-editable structured fields in every shot.md. Amended same day: 加入 start_frame_prompt + end_frame_prompt 两个字段, 共 6 个顶层字段, 支持 Kling 2.1 / Sora image-to-video seam-frame 工作流. v1 保持 rendered prompt 代码块并存; v2 由 webapp 渲染器从 YAML 自动 emit 代码块。 **RETIRED 2026-05-30 per follow-up "drop structured shot_inputs block"** — the parallel YAML layer was removed; `## 视频 prompt` is now the sole source-of-truth and `start_frame_prompt` / `end_frame_prompt` were folded into `## 起始帧` / `## 结束帧`. See the retirement banner at the top of this rule.)*

#### 12.6-D Catalog prefix — 每个 copy-paste prompt 代码块首行是 filename-seed 标识符 (per follow-up "prompt 首行加 shot 元数据" — 2026-05-30)

图片 / 视频生成器下载产物时**默认用 prompt 开头几个词命名文件**。为便于下载后归档, 每个供复制粘贴的 ```text``` prompt 代码块 (`## 起始帧` / `## 结束帧` / `## 视频 prompt`) 的**第一行必须是一个 filename-seed 标识符**, 其后空一行再接 prompt 正文 (含角色 / 场景 reference 行)。

**标识符格式** (下划线连成单 token, 避免被文件名按空格截断):

| 代码块 | 首行标识符 (sub_type=novel) | 首行标识符 (sub_type=short) |
|---|---|---|
| `## 起始帧` | `ep{NN}_shot{NN}_起始帧` | `shot{NN}_起始帧` |
| `## 结束帧` | `ep{NN}_shot{NN}_结束帧` | `shot{NN}_结束帧` |
| `## 视频 prompt` | `ep{NN}_shot{NN}_视频` | `shot{NN}_视频` |

- `ep{NN}` / `shot{NN}` 取自文件路径 (零填充两位), 与文件夹名一致。
- 帧型 token 用中文 (`起始帧` / `结束帧` / `视频`), 与 ai_videos 内容中文规则一致; `ep` / `shot` / 数字保持 alphanumeric。
- 标识符**独占首行 + 下空一行**, 不写进正文句中。视频块的 reference 行排在标识符行 + 空行之后。
- 若某 shot 缺 `## 起始帧` / `## 结束帧` (例如纯标题 / 纯转场), 仅给存在的代码块加前缀。

**Stage-6 validation**: `## 起始帧` / `## 结束帧` / `## 视频 prompt` 任一代码块首行不是对应的 `*_起始帧` / `*_结束帧` / `*_视频` 标识符 = `warning` (不阻断渲染, 但破坏下载归档命名)。

*(Originated from follow-up "prompt 首行加 shot 元数据" — 2026-05-30. 下载图 / 视频按 prompt 首词命名, 加 shot 标识便于归档分类。)*

#### 12.6-E 起始帧 / 结束帧 still-frame 写作契约 — 多角色相对位置 + 动作 + 表情, 无声音 (per follow-up "still-frame 描述要素" — 2026-05-30)

`## 起始帧` / `## 结束帧` 是喂给 Seedream / Midjourney 的**静帧图片** prompt。图片生成器只画"这一帧定格的画面", 不放声音。因此这两段必须把"一张静止画面"描述完整、可画, 且**不含任何声音 / 台词 / 语气信息**。

**必须描述清楚 (每个 on-screen 角色都写)**:

1. **相对位置 (相对其他人物 + 相对画面)** — `角色姿态` 字段写明每个入画角色站 / 跪 / 坐在画面何处, 以及**彼此的相对位置关系** (谁在左 / 谁在右 / 谁在前景 / 谁在后景 / 间隔多远 / 谁面朝谁)。单角色 shot 写主体在 frame 的位置即可; 多角色 shot **必须给出角色之间的空间布局**, 不能只描述一个角色。画外不入画的角色显式标注"不入画"。
2. **动作 (定格瞬间)** — 每个角色在 t=0 (起始帧) / t=末 (结束帧) 那一帧**凝固的物理动作 / 姿态 / 道具操作**, 一句话定格 (不是一段时间的运动)。
3. **表情** — 每个角色的面部表情 / 眼神 / 嘴形 / 神情, 写进 `表情` 字段 (多角色时逐个写)。

**禁止 (因为是静帧图片)**:

- 不写台词原文 / 配音语气 / 音区音量 / 念法 / TTS 提示 — 一切声音信息只属于 `## 视频 prompt` 的 `台词 / 字幕:` 字段。
- 不写时间区间运动 (`0-2s ...`) — 起始 / 结束帧是单一瞬间; timed 运动只属于 `## 视频 prompt` 的 `动作:`。

**Stage-6 validation**:

- 多角色 shot 的 `## 起始帧` / `## 结束帧` 只描述了 1 个角色、缺少角色间相对位置 = `warning`。
- `## 起始帧` / `## 结束帧` 出现台词原文 / 配音语气 / 音量音区等声音信息 = `warning` (应移到视频 prompt 台词字段)。
- `表情` 字段缺失 (多角色时缺其中某角色的表情) = `warning`。

*(Originated from follow-up "still-frame 描述要素" — 2026-05-30. 用户要求 start / end frame 描述清楚角色相对其他人物的位置 / 动作 / 表情; 因生成图片无需声音。)*

#### 12.6-B Per-episode 纯对白 `dialogue.md` derived from chapter（per follow-up xianxia_new/011 — 2026-05-24）

每 episode 必须 ship 一个 `dialogue.md` 文件，定位为 **配音 / TTS / 字幕 / 配音演员选角** 团队的轻量入口 —— 比 `script.md` 更精简（剥离 scene heading / 动作 / 镜头 / 内心 OS），比 chapter prose 更结构化（按"说话角色 → 台词 → 语气情感注释"逐行铺陈，无散文叙事）。

**Authoring contract**: `dialogue.md` 是 **derived**, 从 `my_novel/{name}/chapters/{NNNN}-XXX.md` 抽取所有发声的台词（人物对白 / 系统弹窗文字 / 内心 OS 中被引号包起来的自言自语都算）。作者只维护 chapter; stage-6 regen 删 `dialogue.md` 然后从 chapter 重新抽取。同 `script.md` / `shotlist.md` 的 derive 模式。

**File location（sub_type=novel）**: `ai_videos/{name}/episodes/epNN/dialogue.md`.

**File location（sub_type=short）**: `ai_videos/{name}/dialogue.md` (与 script.md / shotlist.md 平级)。

**Body schema（强制）**:

````markdown
# 第 NN 集 · 纯对白

> Derived from `../../my_novel/{name}/chapters/{NNNN}-XXX.md`. Stage-6 regen 时删除后从 chapter 重新抽取。手动修改请同步修改 chapter; 否则下次 regen 被覆盖。

## 时间线

按 chapter 中台词出现顺序逐行铺陈。每一行格式严格如下：

```
{角色名}: "{台词}" ({语气情感注释; 5-15 字})
```

字段约束:
- **角色名**: 中文, byte-identical 跨集与 character bible 锁定描述符 #1 一致。**系统弹窗**用 `[系统]` 占位; **未具名旁白**用 `[旁白]`; **内心 OS** 用 `{角色名} (内心)`。
- **台词**: 双引号包裹, 完整一句; 中文标点(`，` `。` `？` `！` `——`)按 chapter 原文保留。
- **语气情感注释**: 圆括号包裹, 5-15 字; 必填三件套 — (a) 音量(`低声` / `怒喝` / `气声` / `轻语` / `平稳`); (b) 情感(`冷漠` / `决意` / `不甘` / `颤栗` / `讥诮`); (c) 物理特征(`喉腔低共鸣` / `每字间停半拍` / `齿间漏血气` / `唇近不动`)。三类按需 1-3 个组合, 不少于 1 类不多于 3 类。

## 段落分组

按 chapter 章节内自然段或剧情转折分 `## 段 N — {段标题}` H2 二级标题, 让配音员定位上下文方便。

## 角色发声清单

文末 `## 本集角色发声清单` 段以表格列出本集发声角色 + 台词条数 + 总字数, 用于 TTS / 配音工时估算:

| 角色 | 台词条数 | 总字数 |
|---|---|---|
| {角色 A} | 8 | 156 |
| ... | ... | ... |
````

**例（自 ep01 chapter §1 渡劫之夜节选）**:

```
裴长砚: "师弟, 今日是你逼我的。" (低声; 决意; 喉腔低共鸣每字间停半拍)
裴长砚: "这一剑, 我饮便是了。" (气声; 不甘藏于平静; 齿间漏血气唇近不动)
```

**12.6-B 与 script.md 的边界**:
- `script.md` 是 screenplay form, 含 scene heading / 动作 / 镜头 / 对白 / 内心 OS, 给镜头团队读。
- `dialogue.md` 是 voice-only extract, 只含说话与语气, 给配音 / TTS / 字幕团队读。
- 二者**都从 chapter derive**, **不**互相 derive (避免双重 derive 错配 risk)。

**Stage-6 validation**:
- 缺失 `dialogue.md` = **blocker**。
- 行格式不符合 `{角色名}: "{台词}" ({注释})` 严格模板 = **warning** (per-行); 全文 >20% 行不符合 = **blocker**。
- 语气情感注释少于 5 字或缺三件套至少 1 类 = **warning** (per-行)。
- 角色名出现 character bible 锁定描述符 #1 未登记的姓名 = **blocker** (cross-doc consistency check, 同 shot prompt `角色:` 行的 byte-identical 契约)。

*(Originated from follow-up xianxia_new/011 — 2026-05-24, 用户原话: "每一个episode要包含以下几种文件，一个是小说原文，完整的小说，有所有详细信息，还有一个是纯对白，类似于人物A:.... 人物B:..... 对加上点语气情感注释。" Solves: ① 配音 / TTS 团队读 chapter prose 需自行抽取台词成本高; ② script.md 含技术性 scene heading / 动作 / 镜头 描述对配音员是噪音; ③ 配音工时估算需要每角色台词条数 + 字数; ④ 字幕组需要按时间线 顺序的台词序列。)*

#### 12.7 Cross-character facial differentiation + 亚洲俊男靓女审美锚点（per follow-up 008）

为防止 AI 生成多角色面孔同质化（"AI 通用脸"问题），character bible 锁定描述符 #2「面貌」从单字段扩展为 **6 子项 + 必填「标志特征点」unique-identifier**；项目级 style_guide.md 锁定**亚洲俊男靓女审美锚点**。

**12.7-A 锁定描述符 #2 面貌 6 子项（rule #12.1 amend；rule #12.7 v2 per follow-up 012 expand to 5-7 micro-details per character）：**

| 子项 | 内容 | 必填 |
|---|---|---|
| 脸型 | 国字脸 / 鹅蛋脸 / 瓜子脸 / 方圆脸 / 鸭蛋脸 / 长脸 / 心型脸 / 菱形脸（8 类） | ✅ |
| 眉形 | 剑眉 / 卧蚕眉 / 柳叶眉 / 一字眉 / 八字眉 / 远山眉（6 类）+ 粗细 + 走向（高挑 / 平直 / 微聚） | ✅ |
| 眼型 | 丹凤眼 / 桃花眼 / 杏仁眼 / 狐狸眼 / 三角眼 / 圆眼（6 类）+ 单/双眼皮 + 眼距（窄 / 中 / 宽）+ 眼尾（上挑 / 下垂 / 平） | ✅ |
| 鼻型 | 高挺直鼻 / 蒜头鼻 / 鹰钩鼻 / 朝天鼻 / 蓄水鼻 / 短鼻（6 类）+ 鼻翼宽窄 | ✅ |
| 唇型 + 牙齿 | 薄唇 / 厚唇 / M 唇 / 一字唇 / 樱桃唇（5 类）+ 唇色 + (可选) 牙齿特征（虎牙 / 整齐贝齿 / 含微豁齿） | ✅ |
| **标志特征点 + 5-7 项 distinctive 微细节**（rule #12.7 v2，per follow-up 012）| **唯一识别符**（每角色 1-2 项 byte-stable）+ **覆盖 5 大维度的 5-7 项 micro-details**：① 眼周细节（上眼睑 / 卧蚕 / 下眼袋 / 内眼角 / 眼尾纹）② 鼻形细节（鼻头圆尖 / 鼻翼厚度 / 鼻孔形 / 山根高度）③ 唇形细节（上唇厚度 / 下唇厚度 / 唇峰锐 / 唇角下垂或上扬）④ 下颌细节（下颌轮廓硬度 / 颧骨高度 / 下巴形 / 喉结）⑤ 皮肤细节（肤色冷暖 / 毛孔可见度 / 法令纹 / 颈纹 / 唯一标记） | ✅ |

锁定描述符 #10「一句话锁定」必含 **face-differentiator token**（即「标志特征点」字段的核心元素），让一句话锁定本身就 carry 唯一识别符，shot prompt 引用该锁定时自动获得辨识度。

**12.7-B Cross-character similarity 一致性规则：**

任两个 character bible 的「锁定描述符 #2」6 子项必须满足：
- 至少 **2 子项 + 标志特征点** 不同。
- 「标志特征点」绝不重复（每角色独占 1-2 个 byte-stable 唯一标记，跨角色互斥）。
- 即使同类型角色（两个剑修 / 两个仙女）也须有可视化区分点。

Stage-6 validator scan：跨 N 角色 bible 计算 6 子项 + 标志特征点 cross-character similarity 矩阵；任两人 ≥ 5 子项相同 OR 标志特征点重复 OR 缺失 = **blocker**。

**12.7-B+ 真人写实强化锚点（rule #12.7 v2，per follow-up 012）：**

style_guide.md § 渲染样式锁定 段必含 follow-up 012 的 8 项 photorealism 强化正向（每份 prompt 必含 ≥ 4 个）+ 14 项扩展 photorealism 负向（每份 prompt 必含全部）。这些关键词专门解决 "AI 生成偏卡通 / 动漫感" 问题，密集输入 photorealism 信号让模型拉向 真人摄影 / Netflix HDR drama 标准。每 character ref turntable + shot prompt 的 `渲染样式:` line 必 carry ≥ 4 项 photorealism 强化正向；`负向:` line 必 carry 全 14 项扩展负向。

**12.7-C 项目级亚洲俊男靓女审美锚点（style_guide.md amend）：**

每项目的 style_guide.md 须含 § 亚洲俊男靓女审美锚点 段，包含：

1. **男性角色锚点表**：按角色类型（冷峻威压 / 清亮少年 / 烈火宗主 / 道貌温润 / 剑修冷锋 / etc.）列代表演员（中日韩古装真人剧主演级，例：罗云熙澹台烬 / 成毅战神 / 王鹤棣东方青苍 / 朱一龙沈巍 / 张哲瀚温客行 / etc.），每角色至少绑定 1-2 名演员锚点。
2. **女性角色锚点表**：按角色类型（仙气清冷 / 妖娆烟火 / 清纯灵动 / 端庄秀丽 / etc.）列代表演员（白鹿黎苏苏 / 虞书欣小兰花 / 杨紫颜淡 / 章若楠 / 文淇 / 倪妮 / etc.）。
3. **通用正向关键词**（每份 prompt 必含 ≥ 2 个）：

```
亚洲俊男靓女 / 东方传统五官 / 三庭五眼东方面孔
中日韩古装剧主角脸 / 仙侠真人剧主演级颜值
真实电影选角 / 大陆古装一线演员 / 港台日韩明星脸
```

4. **通用负向关键词**（每份 prompt 必含全部）：

```
不要 AI 生成同质化脸 / 不要 AI 通用脸 / 不要 模板化俊男靓女 / 不要 千篇一律的丹凤眼锥子脸
不要 西方审美面孔 / 不要 欧美选角风 / 不要 浓眉大眼欧化
不要 同款脸 / 不要 跨角色面孔重复 / 不要 网红脸 / 不要 整容脸模板
```

**12.7-D 应用到下游 prompt：**

- **Character bible** (rule #12.1 amend per 12.7-A)：锁定描述符 #2 面貌 6 子项 + 「标志特征点」必填行；锁定描述符 #10 一句话锁定 含 face-differentiator token。
- **Character ref turntable prompt** (rule #12.5 v2 amend)：`角色:` 字段 inline 展开 carry 「标志特征点」+ 锚定的 1-2 名 specific 演员类比（不止 generic "live-action 真人剧"）；负向段补 11 项 AI-同质化负向。
- **Shot prompt** (rule #12.4 v2 amend)：`角色:` 字段 inline 展开同步 carry 「标志特征点」+ 演员锚点；负向段同步补 11 项 AI-同质化负向。

face-differentiator token 与一句话锁定一同 byte-stable 跨集 byte-identical 复制（rule #5 / NFR-2 一致性约束扩展到 face-differentiator）。

*(Originated from follow-up "facial differentiation + Asian aesthetic" — 2026-05-10。Solves AI-generated samey-faces problem; locks Asian (中日韩) handsome/beautiful aesthetic with specific actor anchors per role type.)*

#### 12.8 Character / Scene 命名约定 cN_/sN_（per follow-up 011）

为防止 character / scene 文件名混乱 + placeholder ↔ 文件 mismatch + reference dangling，强制命名约定：

**Filename + folder pattern (rule #12.8 v2 per follow-up 014)：**

- Character: `characters/c{N}_{中文名}/c{N}_{中文名}.md` (folder of same name; folder also holds user-rendered turntable.mp4 + ref.png + 等 media，gitignored per NFR-18)
- Scene: `scenes/s{N}_{shortname}/s{N}_{shortname}.md` (same folder schema)
- Shot: `episodes/ep{NN}/shots/shot{NN}/shot{NN}.md` (same folder schema; folder holds rendered shot video + thumbnail，gitignored)

**Placeholder pattern (unchanged)：**

- `{ref_c{N}_{中文名}}` (e.g., `{ref_c1_沧冥}`)
- `{ref_s{N}_{shortname}}` (e.g., `{ref_s1_长阶顶}`)

**Numbering rules：**

- N 从 1 起递增（不从 0；不补零）。
- 一旦分配后**不可重排** (renumber)。即使删除 character / scene，也保持原 N 不复用；新增只能 append（c11_, s7_, etc.）。
- 排序原则（仅 initial 分配时使用）：
  - Character: 主角 → 主女主 → 副女主 → 反派
  - Scene: cross-ep chronological 出现顺序（首次出现的 ep + shot 越早，N 越小）
- 未立档 location 也可预分配 sN_ placeholder（如 `{ref_s7_山道平台}`），后续立档时 N 已锁定，无需 renumber。

**Reference validation contract（stage-6 validator NFR-16）：**

- 每 shot.md 中所有 `{ref_c{N}_*}` placeholder 必须有对应 `characters/c{N}_*.md` 文件存在。
- 每 shot.md 中所有 `{ref_s{N}_*}` placeholder 必须有对应 `scenes/s{N}_*.md` 文件存在 OR 标注为「未立档 — inline 描述」（s{N}_ 前缀已分配 + placeholder 引用，但无文件）。
- Reference placeholders table 「来源」列 path + 出场角色 table 「character file」列 path 必须 byte-identical 匹配实际文件 path。
- Dangling placeholder（引用但无文件 + 未标注 "未立档"）= blocker。
- Cross-character / cross-scene N 唯一性（任两个 character N 不冲突；scene 同理）= blocker。

**与 rule #12.5 v3 / #12.6 v2 的互动：**

- Character file (rule #12.5 v3 自包含 schema：bible + turntable ref) → 直接 rename to `c{N}_{中文名}.md`。
- Scene file (rule #12.7 8-字段 bible + ref turntable / 立绘) → mirror character pipeline → merged into single `s{N}_{shortname}.md` per follow-up 011 + per the schema:

````markdown
# {scene-name}

{scene bible content per rule #12.7 — 场景定位 / 锁定描述符 / 关键变化态 / 出现镜头 / 负向}

---

# 场景 reference prompt — Seedream / Midjourney / Imagen / Flux（场景立绘）

> **用法**：复制下方代码块整段，粘贴到 text-to-image 模型 → 输出场景立绘 PNG。

```text
{flatten 场景立绘 prompt body — 主体/构图、视角、时辰、背景、光源、风格、负向 inline-labeled}
```
````

- Shot file (rule #12.6 v2 三段 schema): 出场角色 table 第 3 列 path + Reference placeholders table 第 3 列 path + 视频 prompt code block 内 `{ref_xxx}` placeholders **全部** byte-rename 到 cN_/sN_ 命名。

*(Originated from follow-up "naming convention + scenes merge" — 2026-05-10。Solves: ① reference dangling 风险；② character/scene 文件名 chaos；③ scenes/ref_images/ 子目录与 characters/ pipeline 不对齐 — mirror characters merge per follow-up 009。Per follow-up `feng_shou_lu/001` — 2026-05-24, this rule **supersedes** rule #12.5 v5 hybrid (`c{NN}_{pinyin}/{中文名}.md`); v5's webapp-regex concern was empirically unfounded — `^c\d+(_.*)?$` accepts Chinese folder segments. New projects MUST use the 12.8 v2 shape; existing v5-hybrid projects (e.g. feng_shou_lu) require migration.)*

#### 12.9 Folder-per-asset + Media gitignore + Webapp display 契约（per follow-up 014）

每个 character / scene / shot 是一个**同名文件夹**（containing 同名 .md prompt + user-rendered media assets）。Webapp 渲染时 inline 显示 image media + 内嵌播放 video media。

**Folder schema：**

```
characters/c{N}_{name}/
├── c{N}_{name}.md         # tracked in git (prompt content)
├── turntable.mp4          # gitignored (user-rendered character ref video)
├── ref.png                # gitignored (Seedream 立绘 PNG)
└── ... (其他 media, gitignored)

scenes/s{N}_{name}/
├── s{N}_{name}.md         # tracked
├── ref.png                # gitignored
└── ... (其他 media)

episodes/ep{NN}/shots/shot{NN}/
├── shot{NN}.md            # tracked
├── shot{NN}_kling.mp4     # gitignored (Kling 渲染输出)
├── shot{NN}_seedance.mp4  # gitignored (Seedance 渲染输出)
├── shot{NN}_thumbnail.png # gitignored (缩略图)
└── ... (其他 media)
```

**Media gitignore（NFR-18）：**

`.gitignore` 必含：

```
ai_videos/**/*.mp4
ai_videos/**/*.mov
ai_videos/**/*.webm
ai_videos/**/*.mkv
ai_videos/**/*.avi
ai_videos/**/*.png
ai_videos/**/*.jpg
ai_videos/**/*.jpeg
ai_videos/**/*.webp
ai_videos/**/*.gif
ai_videos/**/*.bmp
```

prompt .md 文件继续 tracked。

**Webapp display 契约：**

`projects/ai_video_management/frontend/`:
- 当 user 选中 character / scene / shot folder（vs 选中 .md 文件）时，display：
  1. 同名 .md 文件渲染（默认显示 c1_沧冥/c1_沧冥.md 等）
  2. 该 folder 内所有 image files (.png/.jpg/.jpeg/.webp/.gif/.bmp) → `<img>` inline display
  3. 该 folder 内所有 video files (.mp4/.mov/.webm/.mkv/.avi) → `<video controls>` HTML5 player
- Media files 按文件名字典序展示。
- Backend (`projects/ai_video_management/backend/`) 须能 serve raw media bytes for any path under `ai_videos/` (return correct MIME type)。

**Path 引用更新（applied to shot files in follow-up 014）：**

OLD path → NEW path（applied across 50 shot files 出场角色 table + Reference placeholders source column）：

| OLD | NEW |
|---|---|
| `characters/c1_沧冥.md` | `characters/c1_沧冥/c1_沧冥.md` |
| ... (10 chars) | ... |
| `scenes/s1_长阶顶.md` | `scenes/s1_长阶顶/s1_长阶顶.md` |
| ... (6 scenes) | ... |

*(Originated from follow-up "folder-per-asset + media gitignore + webapp display" — 2026-05-10. Solves: ① media files 与 prompt 关联存储 (same folder)；② git 仓库 size 不因 binary media 膨胀；③ webapp 直接预览 media，无需另开外部 player。)*

#### 12.10 场景 reference 视频 prompt（15s walk-through 建模样片，per follow-up 017 "scene reference 升 3.9s → 15s 单视频 walk-through"）

镜像 character turntable pipeline（rule #12.5 v4，仍保持 2.9s 不动），为每个立档场景增加 **场景 reference 视频 prompt** 段，与现有 Seedream 立绘 image prompt（rule #12.8 v2 schema）并存：image prompt 喂 image-only 模型 / 静帧 fallback；video prompt 喂 Kling / Seedance 等 video-as-reference 模型，用 **15s** walk-through 单视频，沿一条几何连续的相机路径（连续 dolly + 平滑 yaw + 垂直俯仰 + 推进 zoom 的复合移动，无剪辑 / 无跳切）依次悬停在 5 个 canonical 视角上，让模型抓到场景空间结构 + 多角度几何 + 主要建筑或自然元素 + 标志道具材质 + 配色 hex + 时辰光源。15s × 30fps = 450 帧，5 个 canonical 悬停帧 + 约 350 张免费"3/4 中间角度"参考帧（user 可后续按需 ffmpeg 抽帧）。

**为什么 15s walk-through（per follow-up 017 — 把 scene reference 从 v2 的 3.9s 五段升到 v3 的 15s 单视频 walk-through）：**

Kling / Seedance 等 video-as-reference 下游模型的 reference 上传上限实测已可放宽至 ≥ 15s（不再是 v2 假设的 3.9s）。v2 的 3.9s 五段把 5 个 canonical 视角硬塞在 3.9s 内 — 单视角 dwell <0.8s、运镜过急，导致 (a) 每个 canonical 帧带 motion blur，作为 reference 不够锐利；(b) 极快运镜下模型偶发"跟不上"，中段材质 / 几何漂移。v3 把时长放宽到 **15s 单视频**，沿一条**几何连续**的相机路径（不能有剪辑 / 跳切 / 剧烈反向）依次悬停在同样 5 个 canonical 视角，每个 dwell ≥ 0.8s 给出锐利静帧。**关键约束：重要 canonical 视角 frontload 在视频前段（t < 6s）** —— Kling / Seedance 在 t > 12s 后进入训练分布边缘，常见失败模式（材质漂、几何缓慢变形、长尾噪点）集中在视频后段；frontload 重要帧后，即便后段翻车，损失的是次要参考图（3/4 角度 / 长焦特写），不至于丢失 hero / reverse 这种 ground truth。15s 也带来副产物 "**中间帧 buffet**" —— 非 canonical 时间点的 ~350 帧是免费的 3/4 角度参考（介于 hero 与 reverse 之间的任意偏移角度），user 可按需抽帧，无需重新调 API。本视频仍是纯视觉 reference — **不要任何音频 / BGM / 音效 / 旁白 / 环境音**；prompt body 显式声明该约束。

**12.10-A 场景文件 schema 扩展（rule #12.8 v2 amend，15s v3 schema）：**

每场景文件 `scenes/s{N}_{shortname}/s{N}_{shortname}.md` 在原 schema（bible + Seedream 立绘 image prompt）后追加 **场景 reference 视频 prompt** 段：

````markdown
# {scene-name}

{scene bible content per rule #12.7 — 场景定位 / 锁定描述符 / 关键变化态 / 出现镜头 / 负向}

---

# 场景 reference image prompt — Seedream / Midjourney / Imagen / Flux（场景立绘静帧）

> **用法**：复制下方代码块整段，粘贴到 text-to-image 模型 → 输出场景立绘 PNG（image-only 模型 fallback / 静帧 reference）。

```text
{flatten 场景立绘 prompt body — 主体/构图、视角、时辰、背景、光源、风格、负向 inline-labeled}
```

---

# 场景 reference video prompt — Kling / Seedance / Sora / Veo / Runway Gen-3（15s walk-through 建模样片）

> **用法**：复制下方代码块整段，粘贴到支持 video reference 的 AI 视频模型（Kling / Seedance 优先）。**该样片本身**作为后续真正 shot 视频的 video reference 输入，锁定场景空间 + 材质 + 配色 + 时辰光源 + 多角度几何。**注意：≤ 15s 硬上限**（reference 上传约束 per rule #12.10 v3，对应 Kling / Seedance 当前 tier）。**视频纯视觉，无任何音频 / BGM / 音效 / 旁白。** 渲染完成后保留 source mp4 与 scene 文件同 folder — 15s × 30fps = 450 帧可作"中间帧 buffet"按需 ffmpeg 抽取 3/4 角度参考图。

```text
{scene video reference prompt body — 15s v3 schema per rule #12.10-B}
```
````

**12.10-B 场景视频 reference prompt body schema（v3 — 15s walk-through，5 canonical dwell 帧 + 中间帧 buffet；compact format，≤ 2000 字，多行短行避免 horizontal scroll）：**

Body 仅保留 6 个 prompt 字段（`场景` / `镜头` / `动作` / `光线/色调` / `节奏` / `负向`）。平台 / API 侧设定的 4 字段（`渲染样式` / `比例` / `音频` / `时长`）**禁止出现在 body 内** —— user 在 Kling / Seedance UI 或 API call 中直接设定（duration=15s, aspect_ratio=9:16, no audio）。每个字段值用自然句号断行成多行短行（推荐每行 ≤ 80 字符宽），webapp 渲染时不出 horizontal scroll。

```text
{scene-name} — 15s walk-through 场景 reference

场景: {一句话锁定 byte-identical from scenes/s{N}/锁定描述符 #8}
时辰: {光源 from 锁定描述符 #5}
配色: {hex 主/辅/点缀 from 锁定描述符 #6}

空间: {空间结构 from 锁定描述符 #2 + 主要建筑或自然元素 from #3 详述，~120-180 字铺陈尺度 / 入口 / 关键区 + 主要元素相对位置}

镜头: 一条 15 秒几何连续相机路径（连续 dolly + 平滑 yaw + 垂直俯仰 + 推进 zoom 复合移动），焦距随路径段渐变 24mm → 28mm → 28mm → 35mm → 85mm。
沿路径依次悬停 5 个 canonical 视角（每个 dwell ≥0.8s + 4 段平滑过渡），重要视角 frontload 在 t<6s 抵御 Kling/Seedance 在 t>12s 后的训练分布边缘漂移。
关键约束：路径 monotonic 平滑，无剪辑/跳切/淡入淡出/hard cut/180° 瞬间反向；速度可慢可中等，禁止剧烈加速；全程绝对无抖动；dwell 段为完全静止锁机位，给出锐利非 blur 静帧。

动作:
- 0.0-1.0s 悬停 #1 正面建场（24mm）: {Hero 详描 ~100-130 字 — front view 大全景 + 主要元素入画 + 主朝向 + 天际线/顶部}。t=0.5s
- 1.0-4.0s 缓慢 dolly back + 平滑 yaw 约 180° {机位轨迹 ~30 字} 至反向位
- 4.0-4.8s 悬停 #2 反向广角（28mm）: {Reverse 详描 ~100-130 字 — 覆盖正面建场拍不到的反向 180° 空间 + 反侧主要元素}。t=4.4s
- 4.8-7.5s 缓慢 {上升至高位 OR 下沉至低位} 机位，俯仰角 {渐变描述}
- 7.5-8.3s 悬停 #3 {高位俯瞰 OR 低位仰望}（28mm）: {Vert 详描 ~100-130 字 — 垂直方向最强视觉信号}。t=7.9s
- 8.3-11.0s 缓慢 dolly 回中景轨道位，横移扫过 {本场景主要元素序列 from #3 + 关键区位 from #2 ~80-120 字}
- 11.0-11.8s 悬停 #4 中景定格（35mm）: {Mid 详描 ~100-130 字 — key zone 锁定 + 与周边元素同框关系}。t=11.4s
- 11.8-14.2s 缓慢 zoom 推进至 85mm 长焦位置，焦点对准 {detail 目标}
- 14.2-15.0s 悬停 #5 长焦特写（85mm）: {Detail 详描 ~100-130 字 — 标志道具 from #4 + 材质纹理 + 高光细节}。t=14.6s

光线/色调: {详描 ~200-300 字 — 主光 / 辅光 / 反光 + 各表面材质对光的反应 + 各 hex 在不同表面上的表现 + 时辰特有大气感}。配色 hex 主/辅/点缀严格锁定，15s 全程不漂。

节奏: 中等，5 个 canonical dwell ≥0.8s 给锐利静帧 + 4 段 transition monotonic 平滑过渡，信息密度优先于速度。

负向: {场景专属负向 from scenes/s{N}/锁定描述符 #负向，4-8 项} /
不要 抖动 / 剪辑 / 跳切 / hard cut / 加速或瞬反 / 镜头朝向跳跃 /
不要 时辰漂 / 配色偏 hex / 角色入画 / 起手非正面 / {场景专属构图禁忌 1-3 项} /
不要 任何音频 / 超过或短于 15s。
```

**Body 长度严格区间：1950 ≤ chars ≤ 2000**（v3 compact-rich）。短于 1950 字代表场景描述不够，模型抓不到足够 feature；长于 2000 字风险 Kling/Seedance prompt 截断或注意力稀释。实测 9 个场景 body 落在 1955-1998 字范围（s9_识海 蒙太奇黑底变体走特殊变体 schema，body 同样填到 1950-2000 区间，通过加大用法说明与负向项数填充）。

**与早期 v3 compact（750-1320 字）的差异**：① 新增 `空间` 字段（120-180 字），从锁定描述符 #2/#3 拉信息铺陈空间结构 / 入口 / 关键区 + 主要元素相对位置；② 5 个 canonical dwell 描述从 ~40 字扩到 ~100-130 字，加入 focal length 标注 (24mm / 28mm / 35mm / 85mm) 与材质 / 纹理细节；③ 4 段 transition 加机位轨迹细节（俯仰角度 / 高度变化）；④ `光线/色调` 从 ~80 字扩到 ~200-300 字，加入主光 / 辅光 / 反光 + 各表面对光的反应 + 时辰大气感；⑤ `负向` 加入场景专属构图禁忌 1-3 项。**禁止用废话填充字数** — 每多一字必须承载 model-actionable feature 信号（材质、几何、光照、构图、负向边界）。

**12.10-C Scene reference 上传与下游 shot prompt 联动：**

- 立档场景（≥ 2 shots 复用）：user 渲染 `s{N}_{name}.mp4` 后，在 shot prompt 的 Reference placeholders 表第 2 列填该 mp4 path（与 character turntable 同列处理）。Shot prompt 的 `{ref_s{N}_{name}}` placeholder 仍内联引用，user paste 时上传该 mp4 给 Kling / Seedance 即获 scene reference。
- 未立档场景（仅 1 shot 出现，inline 描述）：不生成 scene reference 视频；shot prompt 的 `场景:` 行 inline 描述足够。
- Shot prompt 文件 schema（rule #12.6 v2）不变 —— scene reference 视频上传逻辑由 user 操作时识别，不引入新 prompt 字段。
- **中间帧 buffet 使用**：15s × 30fps = 450 帧。canonical 5 帧的抽帧时间点已在 12.10-B 给出；user 后续若 shot 需要某个 3/4 偏移角度作为额外参考，可在 source mp4（与 scene 文件同 folder）上手动 ffmpeg `-ss <time> -vframes 1 -q:v 1 frame.png` 抽取，无需重新调 API。

**Scene video reference prompt 锁定字段（多场景 byte-identical，仅 `场景` / `时辰` / `配色` / `光线/色调` 段与场景专属负向随场景变化）：**

`镜头` / `节奏` / 视频专属负向核心项 **3 类**在所有场景 video reference prompt 中 byte-identical（v3 compact：从 v3 long 的 8 字段 / v2 的 7 字段缩减为 3 类，因 `渲染样式` / `比例` / `音频` / `时长` 4 字段移出 body 由平台 / API 侧设定；时长锁值 15s 改在 API call 的 `duration` 参数；比例 9:16 改在 `aspect_ratio` 参数；音频禁止改在 `no_audio=true` 或负向兜底；渲染样式锁在 model 选择与 settings）。这样 6+ 场景的 reference 视频输出可剪辑成「场景巡礼合集」，同时 body 字符数从 v3 long 的 ~2900 降到 v3 compact 的 ~1300-1500 字符，对齐 follow-up 013 的 ≤2000 字 shot prompt 上限。

*(Originated from follow-up "compress reference videos to 2.9s" — 2026-05-10；amended by follow-up 010 "scene ref video 3.9s + all-angle + front-start" — 2026-05-11；further amended by follow-up 017 "scene ref video 15s walk-through + 5 canonical dwell + frontload important poses + 中间帧 buffet" — 2026-05-13. v3 把时长从 3.9s 放宽到 15s 单视频；动作从五段极速序列重写为一条几何连续路径 + 5 个 canonical dwell 帧（每个 ≥ 0.8s）；显式 frontload 重要视角于 t < 6s 抵御长尾漂移；引入"中间帧 buffet"概念用于 user 按需抽 3/4 角度参考。Solves: ① v2 的 3.9s 五段中单视角 dwell < 0.8s 致 motion blur，参考图锐利度不足；② 极快运镜下偶发模型跟不上，中段材质 / 几何漂移；③ Kling / Seedance reference 上传上限实测已可放宽至 ≥ 15s；④ 通过 frontload 重要视角 + 中间帧 buffet，单条 walk-through 视频信息密度反而高于五段极速序列。Character turntable rule #12.5 不一致地保留 2.9s — 单体 360° 在 2.9s 内已足够覆盖，turntable 不存在场景 ref 的"球面采样多视角"信息密度问题。本规则仅 update 场景 reference 视频；角色 turntable (rule #12.5 v4) 与 shot prompts (rule #12.6 v2) 未触及。)*

#### 13 共享 BGM 库 + cue 契约（per run bgm_library — 2026-06-16）

与演员库 / 配音库同构的**共享背景音乐库**。情绪库一次生成、跨剧 / 跨场景按全局唯一 id 复用 —— 「一个 bgm_NNNN 像一个 actor_NNNN」。

- **库落盘**：`ai_videos/_bgm/{category}/bgm_NNNN/{bgm_NNNN.md, bgm_NNNN.mp3}`。`{category}/` 是文件夹层也是元数据字段；`bgm_NNNN` id **全局唯一（跨 category）**，剧本按裸 id 引用。软删到 `ai_videos/_deleted/_bgm/{category}/`。
- **12 类固定情绪枚举**（folder 兼 filter）：`tension 紧张对峙 / combat 打斗 / climax_hype 高燃爽点 / faceslap 打脸爽感 / tragic 悲情 / warm 温情 / romance_pain 虐恋 / suspense 悬疑 / daily 日常 / flashback 回忆 / theme_open 片头主题 / system_cue 系统提示音`。`system_cue` 为本仓自定（提示音性质）。
- **`bgm_NNNN.md` 元数据表**字段：`category / mood / bpm / duration / loopable / intensity(1-5) / instruments / generator / model / seed / license / notes` + 一个 `## 生成 prompt (Stable Audio)` 代码块。
- **生成后端**：自托管 **Stable Audio**（开源权重，Stability AI Community License — 年收入 < 100 万美元商用安全）。webapp 通过 subprocess 调 `tools/stableaudio_gen.py`（独立 venv，torch 不入 webapp 进程）。seed 复现为 best-effort（不像演员库硬复现）。
- **剧本侧 cue / `bgm.md`**：novel 每集 `episodes/epNN/bgm.md`，short 项目根 `bgm.md`。行格式（pipe 分隔、行式、可 grep）：
  `起-止(秒) bgm_NNNN | vol= | duck=on/off | fade=in/out`。`vol=` 为 **0-1 线性增益**。assignments 反查（「哪些剧引用了某 bgm」）即扫这些 `bgm.md` 的 `bgm_NNNN` token。删除一个 bgm 前若任一剧 bgm.md 仍引用它则**拒删**（仿 actor）。
- **合成**：`tools/mux_av.py` v1 = 单 BGM 合成（视频 `-c:v copy` + 台词 MP3 + 一条 BGM，`[bgm][dialogue]` sidechaincompress duck + `amix=normalize=0`，台词不被减半；BGM 让位人声）。多 cue 整条 `bgm.md` 编排留后续。
- 与 render-side 字幕烧录（rule 11c）是**两条独立路径**，互不耦合。

*(Originated from run bgm_library — 2026-06-16. 后端从 MusicGen（CC-BY-NC 非商用）换成 Stable Audio 因商用安全要求。)*

#### 14 红果平台官方/实测经验吸收（per run hongguo_borrow — 2026-06-19）

借鉴红果《动画微短剧（漫剧）内容创作建议》(2026-04-07 新规)、红果短剧「编剧第一课」创作指南、与多部 AI 漫剧实测复盘。四条新规，按阶段落地：

- **14.1 AI 扬长避短的题材 / 桥段原则（stage1 立项 + stage3 大纲）。** 实测共识：AI 漫剧**强在玄幻打斗 / 视觉奇观 / 爽感大场面**，**弱在细腻情感戏 / 复杂人性 / 重量感动作**（AI 生成此类「生硬、空洞、僵硬」）。故：① 立项 / 大纲选题与名场面优先**编排 AI 强项画面**（奇观、打斗、变身、爽点反转）当钩子与封面候选；② 必要的情感戏 / 内心转折**不靠 AI 硬演细腻微表情**，改用**台词（内心独白）+ 分镜节奏 + 光线色调 + 配乐**承载情绪，表演只给「可被 AI 稳定渲染」的中等幅度动作；③ 大纲里给每集标注其「AI 强项 beat」位置，避免整集靠纯情感对话支撑。

- **14.2 整剧立意 + 内容安全 gate（stage1 立项 → 审查总编排）。** 红果 2026-04-07 新规两大方向：**①整剧立意导向**——整部作品价值观须**积极向上、有明确正向落点**（不能通篇炫恶 / 复仇泄愤无收束 / 三观崩坏）；**②内容安全治理**——**低俗擦边 / 血腥 / 不良价值观**触发风险评估→整改或下线（八亿播放的《菩提临世》即因立意 / 价值观被下架）。落地：立项 concept.md 必须写明**全剧正向立意一句话 + 主角价值落点**；`ai_videos__审查总编排` 在「整集 / 全剧」层增设**立意 & 安全过审**——逐集检查有无低俗擦边 / 血腥渲染 / 价值观倾斜，全剧检查正向落点是否兑现。此为**整剧 / 整集层**关卡，与 §nvdi020/wushen023 的**生成块级**平台合规（敏感词 / IP / 武器特写）互补、不重叠。

- **14.3 集级节奏 / 卡点 / 完播率公式（stage3 大纲 + stage4 剧本 + `ai_videos__时长节奏`）。** 红果分账 = **播放量 × 停留时长 × 完播率**，一切服务完播率。律：① **单集 90–120s** 内完成一次完整「情绪 + 情节」推进；② 集内节奏 **15s 一反转、30s 一推进、结尾 10s 留悬念 / 卡点**；③ **黄金前 3 秒设钩**（开场即抛核心悬念 / 冲突，禁冗长铺垫）；④ 前几集结构 = 开场设钩→冲突建立→反转→结尾卡点；⑤ 每集**结尾必须留钩**（cliffhanger）拉完播 / 追看。大纲 arc_outline.md 每集标注「前 3 秒钩 + 结尾卡点」；剧本按此排 beat；`ai_videos__时长节奏` 在集级增设「单集时长 90–120s + 反转 / 推进 / 卡点间隔」校验。

- **14.4 跨景别造型一致性（强化锁定描述符 → `ai_videos__格式契约` + `ai_videos__运镜`）。** AI 漫剧第一痛点是**同角色远景 / 近景服装造型不统一、纹理突变**。在已有 byte-identical 锁定描述符基础上加一句铁律：**同一角色在远景 / 中景 / 近景 / 特写下造型为同一套，不随景别漂移**——shot prompt 的 `角色:` 锁定描述符跨景别 byte-identical 已覆盖文字层，校验时额外确认相邻镜若同角色变景别，造型字段（服装 / 发型 / 妆容 / 道具）零变化。

*(Originated from run hongguo_borrow — 2026-06-19. Sources: 红果《动画微短剧（漫剧）内容创作建议》2026-04-07 新规、红果短剧「编剧第一课」、多部 AI 漫剧实测复盘。)*

## Update protocol

Surgical. Cite source run / follow-up. Wholesale rewrites are anti-patterns.
