# Changelog — xianxia_new (working slug)

Append-only log of follow-ups landed against this spec-driven project.

## Follow-up 001 — 2026-05-24 11:41:09
Source: user_input/follow_ups/001-20260524-114109-mvp-ep01-only-iterative.md
Summary: MVP scope cut to ep01 only. Stage 4 detail batch shrinks from 5 (ai_video.md default) to 1; ep02–60 stay at one-liner outline depth. Iterative cadence: ship ep01 → review → learn → next-ep regen as a follow-up run.

Auto-updated:
- user_input/revised_prompt.md — "Composed from" header now lists follow_ups/001; "Desired outcome" section rewritten with MVP scope (11 numbered deliverables ending at ep01 + Deferred + Iterative cadence note).
- interview/qa.md — Q11 (detail batch size) carries an explicit override note: 5 → 1, with the rationale (iterative learning per episode).
- findings/dossier.md — Open question #4 (detail-batch trade-off) resolves to batch = 1; note added that R-2/R-3/R-4 stay at full depth because ep01's 0:03–0:30 betrayal montage references every named character + faction.

No conflicts found in: angle-baseline_extraction.md (corpus-generic conclusions unaffected), angle-trend_research.md (paid-conversion theory unchanged; ep10 node simply lands in a later run), angle-visual_style.md (style guide is project-wide; ep01-only ships the SAME style guide), angle-character_anonymization.md (full naming table is preserved; ep01 references all 9 characters visually).

## Follow-up 002 — 2026-05-24 13:24:54
Source: user_input/follow_ups/002-20260524-132454-ruanyao-rename.md
Summary: 11th character bible 阮瑶 (rename from working draft 楚瑶 to clear CCI-1 collision vs 《楚乔传》 + align with water-radical naming family 容/池/流/阮). 阮瑶 is the ep40 reveal core (容漪 杀阮瑶 — "第二操作员" reveal).

Auto-updated:
- final_specs/spec.md — FR-5 header count 10 → 11 (10 active + 1 archive); new row for 阮瑶.md added to character table.
- findings/angle-character_anonymization.md — §3 parent-amended block for 阮瑶 (etymology + visual palette + signature ability + sites of appearance).
- (NB: Tier 2 character_bible workers later spawn 11 not 10; Tier 5 copyright_clearance grep adds 阮瑶 positive + 楚瑶 negative tokens.)

## Follow-up 003 — 2026-05-24 06:56:52 UTC
Source: user_input/follow_ups/003-20260524-065652-scenes-single-file-no-seam-frame.md
Summary: Two pipeline simplifications. (1) `scenes/ref_images/` 全废止 — 每场景 1 个 `scenes/{name}.md` 文件含嵌入式 Seedream 立绘 (`---` 分隔). (2) shot prompts 中 startframe / lastframe Seedream 静帧 嵌入块 全废止 — rule 5 v2 收缩为「二段式」(Shot context + 视频 prompt), rule 11 archive, rule 12.4 v2 字段矩阵 seam 列移除. 跨 shot 视觉连续性依靠描述层 byte-identical + 共享 turntable mp4 + 共享 scene PNG.

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 5 (三段式 → 二段式), rule 11 (整段 archive), rule 12.3 (v2 单文件 scene pattern), rule 12.4 v2 (seam 字段列移除).
- final_specs/spec.md — FR-7 (scene 单文件), FR-10 (shotNN.md 二段式, seam-frame 块 abolished).
- my_novel/feng_shou_lu/scenes/s1_无寿崖.md + s2_落雁渊.md — 追加 Seedream 立绘 section (`---` 分隔).
- my_novel/feng_shou_lu/scenes/ref_images/ — DELETED (整子目录 + 2 文件).
- my_novel/feng_shou_lu/episodes/ep01/prompts/shot{01..07}.md — 删除 `## Seam-frame still prompts` section + 其下所有 startframe + lastframe Seedream fenced blocks. shot01 删除 startframe + lastframe 双块, shot02-07 删除 lastframe 块.
- my_novel/feng_shou_lu/README.md — 「使用说明」items 6+8 (characters/ref_images/ + scenes/ref_images/) 删除并简化; item 11 删除「+ 嵌入式 seam-frame Seedream prompt」字样; 「工作流」diagram 简化删除两条 Seedream PNG 渲染步骤.

No conflicts found in: validation/strategy.md (seam-frame validators 现 obsolete 但保留 archive 形式不删), CC-3 montage 描述 (seam-frame *剧情节拍说明* 保留, 不指向 PNG).

## Follow-up 004 — 2026-05-24 06:56:52 UTC
Source: user_input/follow_ups/004-20260524-065652-characters-folder-pattern.md
Summary: characters/ 改为 folder-per-character pattern (rule 12.5 v3 → v4). 每角色 1 个 `characters/{中文名}/` 文件夹 + 主 bible 文件 `characters/{中文名}/{中文名}.md` (含 rule #12.1 bible + 默认 turntable). 文件夹内允许 sibling 文件 (state-A/B turntable / 单独 Seedream 立绘 / 配音参考详档 / 等) 按角色按需添加. v3 single-file pattern superseded.

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 12.5 v3 → v4 (folder pattern + v3 → v4 演进 rationale).
- my_novel/feng_shou_lu/characters/{中文名}.md × 11 → my_novel/feng_shou_lu/characters/{中文名}/{中文名}.md × 11 (11 folder + 11 主 bible 文件; mv 完成).
- my_novel/feng_shou_lu/episodes/ep01/prompts/shot{01..07}.md — 角色 reference 路径全部更新 (`characters/{name}.md` → `characters/{name}/{name}.md`).
- my_novel/feng_shou_lu/README.md — 「使用说明」item 5 (`characters/{name}.md` → `characters/{中文名}/{中文名}.md`).
- final_specs/spec.md — FR-5 character file 路径表 11 行全部更新 (folder pattern); FR-6 turntable embedded note.

No conflicts found in: shot prompts 内容 (path 更新, body 不动); script.md (角色 reference 仅在角色出场段以 row #10 一句话锁定形式出现, 不直接 path-reference); 11 个 character bible 文件本身 (folder mv 后内容 byte-identical).

## Follow-up 005 — 2026-05-24 07:18:00 UTC
Source: user_input/follow_ups/005-20260524-071800-mirror-characters-to-ai-videos.md
Summary: Mirror 11 character folders 从 `my_novel/feng_shou_lu/characters/` → `ai_videos/feng_shou_lu/characters/`. 修复 ai_video_management webapp casting feature 无法扫到 fenshoulu 角色 (casting writer 只扫 `ai_videos/{drama}/`, 不扫 `my_novel/`).

Auto-updated:
- ai_videos/feng_shou_lu/characters/{中文名}/{中文名}.md × 11 — NEW mirrored copies (byte-identical with my_novel/ side).

Single source of truth: `my_novel/feng_shou_lu/characters/` 仍为 canonical (spec FR-5); ai_videos/ 端为 mirrored copy 供 webapp consumption. 未来 my_novel/ 端 character bible 修订须 re-mirror.

## Follow-up 006 — 2026-05-24 07:20:00 UTC
Source: user_input/follow_ups/006-20260524-072000-chapter-prose-canonical-per-episode.md
Summary: 在每个 episode 下新增 `chapter.md` 作为**用户可读小说篇章** (canonical source-of-truth). Authoring order 改为 chapter → script → shotlist → prompts. 质量 contract: 比 downloaded_novels/xianxia/ 14 本基线小说 更细致精彩 (~50% 描写密度提升 + 30% 内心 OS 占比 + ≥ 3 重 cliffhanger 钩 + byte-identical 角色 / 台词 / motif anchors).

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 2 novel layout 新增 episodes/epNN/chapter.md 列为子目录最前 canonical 文件 + authoring order note (chapter → script → shotlist → prompts).
- specs/ai_video/xianxia_new/final_specs/spec.md — 新增 FR-7.5 (chapter.md 强制 ≥ 5000 字 + quality contract), FR-8 改述为 "derived from chapter.md".
- user_input/revised_prompt.md — Composed from 含 003-006; Desired outcome list 新增 7a (chapter.md canonical) + 7b (script.md derived).
- my_novel/feng_shou_lu/episodes/ep01/chapter.md — NEW (worker spawning, ~5000-8000 字 novel prose).

ep02+ contract: 任何后续 episode 必须 chapter-first 写, derive 顺序固定. ep01 retrospective chapter 不重写 script / shotlist / prompts (plot 已对齐, chapter 只在 prose 层 expand).

## Follow-up 007 — 2026-05-24 07:40:00 UTC
Source: user_input/follow_ups/007-20260524-074000-chapter-excerpt-in-shots.md
Summary: 每个 shotNN.md 在 YAML envelope 后, H1 前 插入 `## Chapter excerpt` section (200-400 字 verbatim 块引用 from chapter.md 对应 §N 段). AI 模型 + 人类 review 同时看到 novel prose mood + shot schema. shot 视频 prompt body 继续聚焦 动作 + 角色互动 micro-detail; chapter prose 提供 surrounding context.

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 5 v2 → v3 (3-section schema: chapter excerpt + shot context + 视频 prompt).
- my_novel/feng_shou_lu/episodes/ep01/prompts/shot{01..07}.md — 插入 `## Chapter excerpt` section, 200-400 字 per shot (shot01 §1 / shot02 §2 上半 / shot03 §2 下半+容漪 cameo / shot04 §3 苏醒 / shot05 §3 motif / shot06 §4 / shot07 §5 cliff).
- specs/ai_video/xianxia_new/final_specs/spec.md — FR-10 update (3-section schema).

## Follow-up 008 — 2026-05-24 07:40:00 UTC
Source: user_input/follow_ups/008-20260524-074000-c-prefix-folder-rename-fix-assign.md
Summary: Fix webapp casting assign-actor bug. 11 character folders 重命名为 `c{NN}_{pinyin_slug}/` (webapp-compatible per `_CHARACTER_DIR_RE = ^c\d+(_.*)?$` + `dramas.ts:22`). bible 文件内部保留 Chinese `{中文名}.md`. rule 12.5 v4 → v5 hybrid (c-prefix folder + Chinese filename). casting UI dropdown 现可弹出 11 个 c-prefix 选项, 用户可 assign actor.

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 12.5 v4 → v5 (hybrid c-prefix folder + Chinese filename + v4 → v5 演进 rationale).
- my_novel/feng_shou_lu/characters/{中文名}/ × 11 → my_novel/feng_shou_lu/characters/c{NN}_{pinyin}/ × 11 (mv 完成, internal {中文名}.md 文件不动).
- ai_videos/feng_shou_lu/characters/ × 11 sync mirror 同步 rename.
- my_novel/feng_shou_lu/episodes/ep01/prompts/shot{01..07}.md — 路径引用 `characters/{中文名}/{中文名}.md` → `characters/c{NN}_{pinyin}/{中文名}.md` (sed 完成, 仅 shot01 有显式路径; 其他 shots 用 chars-reel 引用 不含 path).
- my_novel/feng_shou_lu/README.md — item 5 path 列表更新.
- specs/ai_video/xianxia_new/final_specs/spec.md — FR-5 11-row file path 表更新.

No conflicts found in: chapter.md (内容 byte-identical, 不动); script.md / shotlist.md (角色名 row #10 一句话锁定 + 标志台词 仍 byte-identical, 路径未引用); webapp Python / TypeScript 代码 (未修改, 选择重命名 folder 而非 patch regex 以避免破坏 mozun_chongsheng).

## Follow-up 009 — 2026-05-24 07:50:00 UTC
Source: user_input/follow_ups/009-20260524-075000-split-fenshoulu-reader-vs-production.md
Summary: 物理拆分 fenshoulu folder layout. `my_novel/feng_shou_lu/` 变成纯小说 reader format (matches downloaded_novels schema: `_meta.json` + `README.md` + `chapters/{NNNN}-{title}.md`). 所有 production 资产 (world / style_guide / arc_outline / characters / scenes / episodes script-shotlist-publish-prompts / copyright_clearance) 移到 `ai_videos/feng_shou_lu/`. chapter.md 内容 转化为 reader-format chapter file (`chapters/0001-第一集 落雁渊.md`, YAML envelope 已 strip). Chapter excerpt path 引用在 7 shot prompts 中同步 patch 为新 chapter 路径.

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 2 v2 → v3 (split layout: reader my_novel/ + production ai_videos/).
- specs/ai_video/xianxia_new/final_specs/spec.md — FR-1 through FR-14 path 全部从 `my_novel/feng_shou_lu/...` 迁移到 `ai_videos/feng_shou_lu/...` (chapter.md 单独迁移到 `my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md`).
- 物理 mv: 
  - `my_novel/feng_shou_lu/{world,style_guide,arc_outline,copyright_clearance}.md` → `ai_videos/feng_shou_lu/`
  - `my_novel/feng_shou_lu/scenes/*` → `ai_videos/feng_shou_lu/scenes/`
  - `my_novel/feng_shou_lu/episodes/ep01/{script,shotlist,publish}.md` → `ai_videos/feng_shou_lu/episodes/ep01/`
  - `my_novel/feng_shou_lu/episodes/ep01/prompts/shot{01..07}.md` → `ai_videos/feng_shou_lu/episodes/ep01/prompts/` (post chapter-excerpt-worker)
  - `my_novel/feng_shou_lu/episodes/ep01/chapter.md` → `my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md` (YAML envelope stripped)
  - `rm -rf my_novel/feng_shou_lu/characters/` (canonical 已 mirror 在 ai_videos/, 不再双份)
  - 清理空 my_novel/feng_shou_lu/episodes/ 子目录
- 新增文件: my_novel/feng_shou_lu/_meta.json (downloaded_novels schema, 1 chapter) + my_novel/feng_shou_lu/README.md (reader-facing, 重写) + ai_videos/feng_shou_lu/README.md (production-side index, 重写).
- 7 shot prompts 中 chapter excerpt path 引用 sed-patched: `my_novel/feng_shou_lu/episodes/ep01/chapter.md` → `my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md`.

ep02+ contract: 任何后续 episode chapter 写入 `my_novel/{name}/chapters/{NNNN}-XXX.md` (reader-side); 所有 production assets 仍写入 `ai_videos/{name}/episodes/epNN/` (production-side). chapter-first authoring order 跨 folder 应用.

No conflicts found in: chapter prose body (byte-identical, 仅 YAML envelope strip + 文件名改为 `0001-第一集 落雁渊.md`); 7 shot prompts body (chapter excerpt section + Shot context + 视频 prompt 全 preserve, 仅 cross-doc path 引用 sed-patched); 11 character bibles (canonical 现在 ai_videos/, 内容 byte-identical 与 mv 前一致).


## Follow-up 010 — 2026-05-24 16:09:10
Source: user_input/follow_ups/010-20260524-160910-scene-prompts-novel-prose-and-walkthrough.md
Summary: 场景 prompts 升 novel-prose-grade 细节密度 + 补齐缺失的 15s walk-through 场景视频 reference (per project ref rule 12.4-E + rule 12.10). 范围: s1_无寿崖 + s2_落雁渊 两个立档场景, 每文件 (a) 增厚 Seedream 立绘 image prompt 的 [细节] 段为感官散文 (材质纹理 + 风/雾/尘/光物理行为 + 各表面对主光源的真实反应); (b) 新增 rule 12.10 的 15s walk-through 场景视频 reference prompt (body 1950-2000 字, s1=1979 / s2=1998, 内含 6 字段 + 5 个 canonical dwell + 4 段平滑过渡 + 焦距渐变 24mm→28mm→28mm→35mm→85mm + 重要视角 frontload<6s). s1 额外加渡劫态变体立绘 image prompt (服务 ep01/shot01 cold open + ep08 倒叙 unfiltered byte-identical 复用).

Auto-updated:
- ai_videos/feng_shou_lu/scenes/s1_无寿崖.md — [细节] 段从结构化 5 行升级为感官散文 (前景落叶绒毛/中景青石苔痕剑身锈蚀/背景三层叠云海); 新增渡劫态变体 Seedream 立绘 image prompt (~1500 字); 新增 15s walk-through 场景 reference video prompt body (1979 字, 静默态).
- ai_videos/feng_shou_lu/scenes/s2_落雁渊.md — [细节] 段同等增厚 (鸟骨风化层 / 苇草叶背银白蜡质 / 渊壁水痕带 / 焚寿罗盘冷光晕半径渐变); 新增 15s walk-through 场景 reference video prompt body (1998 字, 黎明态 + 焚寿罗盘 cold light 叠加).
- ai_videos/feng_shou_lu/README.md — 渲染产物布局 scenes/ 段增加 s1_无寿崖_渡劫态.png + s1_无寿崖.mp4 + s2_落雁渊.mp4; 使用说明步骤 4 拆为 4a (Seedream 默认立绘) / 4b (渡劫态变体, 仅 s1) / 4c (15s walk-through 视频); 步骤 5 加场景 mp4 作下游 shot 优先 reference 上传.

No conflicts found in: 8-字段锁定描述符 (跨段 byte-identical 保留) / 一句话锁定 #8 (≤30 字硬上限不动) / [主体]/[参数]/负向 段 (byte-identical 保留) / shot prompts 内  单行 token (保留 rule 12.3 v2 byte-identical 复用契约) / character bibles / world.md / style_guide.md / arc_outline.md / chapter.md / script.md / shotlist.md / 7 个 shot prompts.


## Follow-up 011 — 2026-05-24 17:18:30
Source: user_input/follow_ups/011-20260524-171830-per-episode-files-and-shots-rename.md
Summary: Per-episode 文件清单升级 (rule 2 + rule 3 sub_type 双向) + 文件夹 rename  →  全局生效. 三件套: (a) 新增 rule 12.6-B 强制  (derived from chapter, 纯对白格式 ; 系统弹窗  内心  占位; 文末发声清单表); (b)  →  全局重命名 (agent_refs 14 处路径引用 + 3 active 项目 7 个 epNN folders 物理 mv + 3 active 项目 README/shotlist/publish 14 处 cross-doc 路径引用 patch); (c) feng_shou_lu ep01 本轮即生成 dialogue.md (27 条台词 / 11 个发声单位 / 5 段时间线对齐 chapter §1-§5).

Auto-updated:
- .claude/agent_refs/project/ai_video.md — rule 2 (sub_type=novel) authoring order 增 dialogue.md derived step 3 + shots/ rename (4 处文档树 path); rule 3 (sub_type=short) 同样升级; rule 1 file-naming convention 中 prompts/ → shots/; rule 12.6-B 全新章节插入 (~80 行 schema + 例 + validation + rationale); rule 12.8 v2 path pattern (Shot folder) prompts → shots; layout 文档树 (2 处).
- .claude/agent_refs/validation/ai_video.md — rule #5 v3 文件清单 4 处  → .
- ai_videos/feng_shou_lu/episodes/ep01/ — 物理 mv prompts/ → shots/ (7 files); 新增 dialogue.md (27 条台词 5 段时间线); shotlist.md + publish.md 各 1 处 cross-doc path patch.
- ai_videos/feng_shou_lu/README.md — 目录布局 + 渲染产物 + 使用说明 三段 prompts → shots 共 2 处. 
- ai_videos/mozun_chongsheng/episodes/ep01-ep05/ — 物理 mv prompts/ → shots/ (5 episodes × 10 files = 50 files); README.md 7 处 cross-doc path patch.
- ai_videos/nvdi_tuihun_houhuile/episodes/ep01/ — 物理 mv prompts/ → shots/; README.md 3 处 cross-doc path patch.

No conflicts found in: chapter.md (canonical source-of-truth 不动) / 8-字段锁定描述符 / 一句话锁定 #8 / character bibles / scene bibles / shotNN.md schema (chapter excerpt + shot context + 视频 prompt 三段全 preserve) / world.md / style_guide.md / arc_outline.md / copyright_clearance.md / publish.md (除 shots/ path patch 外内容不动) / specs/ai_video/xianxia_new/ 下游 interview/findings/final_specs/validation 全部 artifacts (本 follow-up 只增不改 rule + 物理重命名, derive 模式与既有契约一致 — script.md/shotlist.md 已沿用 derive 路径, dialogue.md 只是补一道并列 derive). 现有 mozun_chongsheng + nvdi_tuihun_houhuile 因仍未生成 dialogue.md, 下次任一项目 stage-6 regen 时 dialogue.md 会按 rule 12.6-B 自动生成 — 无需追溯补齐 (本轮仅生成 feng_shou_lu/ep01 作为 demonstration).
