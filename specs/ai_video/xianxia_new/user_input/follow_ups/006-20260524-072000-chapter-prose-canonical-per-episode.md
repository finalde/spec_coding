---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md   # rule 2 (novel layout) — add episodes/epNN/chapter.md
  - specs/ai_video/xianxia_new/final_specs/spec.md   # NEW FR for chapter.md + reorder FR-8/FR-9/FR-10 as derived
  - my_novel/feng_shou_lu/episodes/ep01/chapter.md   # NEW
severity: high
---

# Follow-up draft 006 — 2026-05-24 07:20:00 UTC

Summary: 在每个 episode 下面新增 `chapter.md` 作为**用户可读的小说篇章** (novel prose), 是 episode 的 **canonical source-of-truth**. Authoring order 改为: **chapter.md → script.md → shotlist.md → prompts/shotNN.md**. script.md 退化为 "screenplay form derived from chapter" (给剪辑 / 渲染 / 字幕 操作使用), shotlist + prompts 进一步从 script 推导. Chapter 质量底线: **比 downloaded_novels/xianxia/ 14 本基线 (凡人修仙传 / 我的模拟长生路 / 等) 更细致精彩** — 句法 / 描写密度 / 内心 OS 微观 / 感官细节 / 仙侠 mood / 角色声口 / cliffhanger 钩 全面 superior.

## 用户原话

> 在每個episode下面，我要的是小説篇章，可以給用戶讀的那種，要先有篇章，才有shots，篇章的精彩程度要比我下載的那些還要細緻精彩

## 用户意图抽象

「我现在拿到的 episodes/ep01/ 里只有剧本 (script.md, 戏剧体 — 场景头 + 动作 + 对白) + 分镜表 + shot prompts. 我要的是 **小说文体** 的 chapter — 中文网络小说的标准章节形态, 用户可以坐下来读, 像读起点 / 番茄上的仙侠章节那样. 而且我们的 chapter 应该比下载的那些参考小说写得更好 — 更细致的场景刻画, 更微观的内心活动, 更扣人心弦的钩子, 更具仙侠美学的 mood. chapter 是源头, shots 是从 chapter 推导出来的, 不是相反.」

## 改动 1: agent_refs/project/ai_video.md rule 2 novel layout

`episodes/epNN/` 子目录新增 `chapter.md` 作为 **canonical** 文件 (置于其他文件之前):

```
episodes/
└── epNN/
    ├── chapter.md          # NEW: 小说体 chapter (canonical, 用户可读, 5000-8000+ 字 中文)
    ├── script.md           # screenplay form, derived FROM chapter.md (给渲染 / 字幕 / 操作使用)
    ├── shotlist.md         # derived from script.md
    ├── prompts/
    │   └── shotNN.md       # 每镜 prompt, derived from shotlist + script
    └── publish.md
```

Authoring order (canonical → derived):

1. **chapter.md** — 写小说篇章 (5000-8000+ 字, 中文小说体)
2. **script.md** — 把 chapter 改写为 screenplay (scene heading + 动作 + 对白 + 内心 OS), 保持 byte-identical 角色 一句话锁定 + 场景 一句话锁定 + 标志台词
3. **shotlist.md** — 从 script 切分为 ≤ 15s 的 shot, 决定 cliffhanger / cover_frame
4. **prompts/shotNN.md** — 每镜的 14-字段 prompt schema (per rule 12.4 v2)

## 改动 2: spec.md 新增 FR-7.5 (chapter.md) + reorder

新增 FR-7.5 `episodes/ep01/chapter.md` — episode chapter (novel prose):

- 全中文小说体 (≥ 5000 字, 上限不严格, 8000-12000 字 范围常见).
- 第三人称跟随主角 (主角视角 + 偶尔切换到旁观全知).
- 含分段 (`## §1 标题` / `## §2 标题` ...) 反映 plot beats; 每个 §N 段对应 script.md 的 一组 shot.
- 描写密度 ≥ 下载基线 14 本平均水平 — 感官细节 / 内心 OS / 环境 mood / 对白 subtext / 动作微观 全面 expand.
- Cliffhanger 钩 在 §N 末段必埋, 与 script.md cliffhanger shot 对齐.

FR-8 script.md 改为 derived: 「从 chapter.md 改写为 screenplay form, 保持 byte-identical 一句话锁定 + 标志台词 + plot beat 顺序」.

FR-9 shotlist.md 从 script.md derive.
FR-10 prompts/shotNN.md 从 shotlist.md + script.md + chapter.md derive.

## 改动 3: chapter quality contract (vs downloaded baseline)

「比下载基线更细致精彩」具体落地:

- **感官细节密度**: 每场景至少 ≥ 3 个非视觉感官细节 (听觉 / 嗅觉 / 触觉 / 味觉 / 痛觉). 基线 14 本平均 ~1-2 个 per scene.
- **内心 OS 占比**: 内心活动 / 自陈 / 回忆 / 推断 ≥ 30% 行长. 基线平均 15-20%.
- **环境 mood 描写**: 每场景开头 1 段 ≥ 50 字 environment-only setup (无角色动作). 基线常 跳过.
- **对白 subtext**: 关键对白 ≥ 3 句含「言外之意」(对白后 1 行括号外 narrator 注 OR 内心 OS 解构对方意图). 基线常 直白.
- **动作微观**: 关键动作切分为 ≥ 3 个 sub-beat (前 / 中 / 后), 每 beat 至少 1 个 micro-detail (e.g., 「指尖蘸水, 水波从指尖向外散开三圈」). 基线常用 1-beat 概括.
- **仙侠 mood**: 每千字至少 1 处 仙侠-specific 视觉 锚 (修真意象: 灵气 / 真元 / 雷劫 / 法宝 / 灵识 / 等). 基线 ✅ 满足, 本作要 superior 通过 更精确的 motif 锚.
- **Cliffhanger 钩力**: 末段 cliff 钩 (~150-300 字) 必含 3 重 (悬念问题 + 角色情绪反转 + 视觉冲击锚). 基线 ✅ 大量 但常 单层.

## 改动 4: 项目层落地 (ep01 chapter writer)

- 新建文件: `my_novel/feng_shou_lu/episodes/ep01/chapter.md`.
- 内容: ep01 完整 novel prose (~5000-8000 字), 按 5 plot beat 分段 (前世渡劫 / 倒叙 6 betrayers / 渊底苏醒+罗盘+motif / 自取新名 / 师父 cliffhanger).
- 复用 byte-identical 一句话锁定 + 标志台词 + 焚寿罗盘 描述 from bibles. 复用 NFR-9 motif 三拍 from style_guide §5.2 (chapter prose 形式重写, 但保持视觉 anchor 不漂移).

## 改动 5: ep02+ 后续 episodes 默认 chapter.md 先行

ep02 以后任何 stage-4 regen / stage-6 启动, **必须先写 chapter.md, 再 derive script / shotlist / prompts**. 这是流水线 authoring order 的 hard contract.

## Out of scope

- 不重写已 ship 的 ep01 script.md / shotlist.md / prompts/ — 那些是 derived artifacts, 与新的 chapter.md 一致 ✅ (因为 chapter 是 retrospectively 根据已 ship 的 plot 撰写的, 命名 / beat / cliff 一致). 但 chapter 比 script 多了 prose 层 (descriptive 段 + 内心 OS), script 不会 byte-identical 反向 derive.
- 不重写 arc_outline.md 60-ep one-liner — 用户最终需要 chapter 时再展开 (ep02 / ep03 / ... 按 follow-up 触发 stage-6 regen 时 write chapter).
- 不动 publish.md, copyright_clearance.md, world.md, style_guide.md, characters/, scenes/. 这些是 cross-episode shared assets.

## Acceptance

- `.claude/agent_refs/project/ai_video.md` rule 2 novel layout 已更新 (chapter.md 列在 epNN/ 子目录最前).
- `specs/ai_video/xianxia_new/final_specs/spec.md` 已新增 FR-7.5 + 重新表述 FR-8/FR-9/FR-10 为 chapter-derived.
- `my_novel/feng_shou_lu/episodes/ep01/chapter.md` 已 ship (≥ 5000 字, novel prose, 5 plot beat 全 cover, quality 满足 §3 contract).
- `specs/ai_video/xianxia_new/changelog.md` 已追加 follow-up 006 条目.
- `revised_prompt.md` regenerated (composed from 已含 005 + 006).
