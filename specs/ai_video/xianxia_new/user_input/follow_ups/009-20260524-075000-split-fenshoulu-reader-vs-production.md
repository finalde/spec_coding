---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md   # rule 2 v2 → v3 (split novel layout)
  - specs/ai_video/xianxia_new/final_specs/spec.md   # FR-1 through FR-14 path updates
  - my_novel/feng_shou_lu/   # restructure to reader-only
  - ai_videos/feng_shou_lu/  # restructure to production-canonical
severity: high
---

# Follow-up draft 009 — 2026-05-24 07:50:00 UTC

Summary: 拆分 `feng_shou_lu` 物理 folder layout 为两侧:

- **`my_novel/feng_shou_lu/`** = **纯小说 reader format** (matching downloaded_novels schema). 内容仅 `_meta.json` + `README.md` + `chapters/{NNNN}-{title}.md`. 用户当作 起点 / 番茄 / 晋江 上的小说章节去读, 无 YAML envelope, 无 production metadata, 无 shot 引用.
- **`ai_videos/feng_shou_lu/`** = **AI 短剧 production canonical**. 含 world.md / style_guide.md / arc_outline.md / characters/ / scenes/ / episodes/{epNN/script,shotlist,publish}.md + prompts/ / copyright_clearance.md / README.md (production-side index). 这里是 production team / 渲染流水线 / webapp 的工作区.

## 用户原话

> 現在有兩個fenshoulu folder一個在my novels 下面， 一個在ai videos 下面，請把my_novels 下面的變成純粹的小説模樣，格式跟downloaded_novels一樣，只是用來讀的，ai videos 下面那個才是我們用做短劇的

## 用户意图抽象

「现在 my_novel/feng_shou_lu/ 已经堆了世界观 / 风格指南 / 角色档 / 场景档 / 剧本 / 分镜 / shot prompts / 发布信息 / 版权清查 — 这些都不是「读小说」需要的. 我作为一个普通读者打开这个文件夹, 只希望看到 _meta.json + README + chapters/. 让这个文件夹长得跟 downloaded_novels/xianxia/fanren_xiuxian_zhuan/ 一模一样 — 就是别人小说的格式. AI 短剧的所有 production 资产都放到 ai_videos/feng_shou_lu/ 那边去, 那边才是工作区.」

## 改动 1: agent_refs/project/ai_video.md rule 2 v3 (split layout)

`task_type=ai_video, sub_type=novel` 的 layout 拆分为两侧:

**reader-side `my_novel/{name}/`** (matches downloaded_novels schema per follow-up 111):

```
my_novel/{name}/
├── _meta.json     # novel metadata (slug, title, author, chapters[])
├── README.md      # 小说扉页 (Chinese title + 一段概要 + 章节列表 link)
└── chapters/
    ├── 0001-第一集 {title}.md   # 单章 prose, H1 + 章节正文, 无 YAML envelope
    ├── 0002-第二集 {title}.md
    └── ...
```

**production-side `ai_videos/{name}/`** (full drama production, supersedes the earlier my_novel/{name}/ layout):

```
ai_videos/{name}/
├── README.md                 # 短剧项目 index (中文 + 项目概要 + 使用说明)
├── world.md                  # 世界观 (修炼境界 / 三方势力 / 地理 / 寄生 lore)
├── style_guide.md            # 镜头 + 调色 + 字幕 + 负向
├── arc_outline.md            # 60-ep one-liner 大纲
├── characters/
│   └── c{NN}_{pinyin}/{中文名}.md   # 角色 bible (rule 12.5 v5)
├── scenes/
│   └── s{N}_{name}.md              # 场景 bible + 嵌入 Seedream 立绘 (rule 12.3 v2)
├── episodes/
│   └── epNN/
│       ├── script.md         # screenplay form (derived from chapter)
│       ├── shotlist.md       # 镜头清单
│       ├── prompts/shotNN.md # 每镜 prompt
│       └── publish.md        # 发布信息
└── copyright_clearance.md    # 版权清查 SIGN-OFF
```

**Authoring source-of-truth contract (post-follow-up 009)**:

- chapter.md 物理位置: **`my_novel/{name}/chapters/{NNNN}-{title}.md`** (reader-side).
- script.md / shotlist.md / prompts/shotNN.md 物理位置: **`ai_videos/{name}/episodes/epNN/`** (production-side).
- production-side script 仍 derived from reader-side chapter (跨文件夹 cross-reference: `chapter excerpt` section in shot prompts 引用 `../../my_novel/{name}/chapters/{NNNN}-{title}.md`).
- chapter.md → script.md → shotlist.md → prompts/shotNN.md 的 chapter-first authoring order (follow-up 006) 保留不变, 只是物理上拆到两个 folder.

## 改动 2: 物理 mv 操作 (xianxia_new feng_shou_lu)

非冲突 mv (chapter-excerpt worker 仍在 shot prompts 上 edit, 暂不动 shot prompts + chapter.md, 其他全 mv):

```bash
# Move production assets from my_novel/ → ai_videos/
mv my_novel/feng_shou_lu/world.md         ai_videos/feng_shou_lu/world.md
mv my_novel/feng_shou_lu/style_guide.md   ai_videos/feng_shou_lu/style_guide.md
mv my_novel/feng_shou_lu/arc_outline.md   ai_videos/feng_shou_lu/arc_outline.md
mv my_novel/feng_shou_lu/copyright_clearance.md  ai_videos/feng_shou_lu/copyright_clearance.md
mv my_novel/feng_shou_lu/scenes/*         ai_videos/feng_shou_lu/scenes/    # 2 文件
mv my_novel/feng_shou_lu/episodes/ep01/script.md     ai_videos/feng_shou_lu/episodes/ep01/script.md
mv my_novel/feng_shou_lu/episodes/ep01/shotlist.md   ai_videos/feng_shou_lu/episodes/ep01/shotlist.md
mv my_novel/feng_shou_lu/episodes/ep01/publish.md    ai_videos/feng_shou_lu/episodes/ep01/publish.md

# Characters/ — drop the my_novel/ side (canonical is now ai_videos/, no dual ownership)
rm -rf my_novel/feng_shou_lu/characters

# scenes/ folder empty after files moved
rmdir my_novel/feng_shou_lu/scenes
```

Deferred mv (worker still touching, wait for completion):

```bash
# chapter.md → my_novel chapters/ (strip YAML envelope + rename)
mv my_novel/feng_shou_lu/episodes/ep01/chapter.md  my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md
# (followed by sed to strip YAML envelope)

# shot prompts (post-chapter-excerpt-worker)
mv my_novel/feng_shou_lu/episodes/ep01/prompts/* ai_videos/feng_shou_lu/episodes/ep01/prompts/

# Then patch chapter excerpt path references in shot prompts:
# from "my_novel/feng_shou_lu/episodes/ep01/chapter.md" → "my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md"

rmdir my_novel/feng_shou_lu/episodes/ep01/prompts
rmdir my_novel/feng_shou_lu/episodes/ep01
rmdir my_novel/feng_shou_lu/episodes
```

## 改动 3: 新增文件

- `my_novel/feng_shou_lu/_meta.json` (per follow-up 111 schema): slug / title / author / source / chapters[]
- `my_novel/feng_shou_lu/README.md` (rewrite as reader-facing): 中文标题 + 一段概要 + 章节列表
- `my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md` (from ep01/chapter.md, strip YAML envelope)
- `ai_videos/feng_shou_lu/README.md` (rewrite as production-index)

## 改动 4: spec.md FR path migration

所有 FR 中的 `my_novel/feng_shou_lu/...` path 引用全部迁移:

- FR-1 README: `my_novel/feng_shou_lu/README.md` 拆为两个 README — reader (`my_novel/`) + production (`ai_videos/`)
- FR-2 world.md → `ai_videos/feng_shou_lu/world.md`
- FR-3 style_guide.md → `ai_videos/feng_shou_lu/style_guide.md`
- FR-4 arc_outline.md → `ai_videos/feng_shou_lu/arc_outline.md`
- FR-5 character bibles → `ai_videos/feng_shou_lu/characters/c{NN}_{pinyin}/{中文名}.md`
- FR-7 scenes → `ai_videos/feng_shou_lu/scenes/`
- FR-7.5 chapter.md → **moved to `my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md`** (reader-side, post-007 v2)
- FR-8 script.md → `ai_videos/feng_shou_lu/episodes/ep01/script.md`
- FR-9 shotlist.md → `ai_videos/feng_shou_lu/episodes/ep01/shotlist.md`
- FR-10 shot prompts → `ai_videos/feng_shou_lu/episodes/ep01/prompts/shotNN.md`
- FR-11 publish.md → `ai_videos/feng_shou_lu/episodes/ep01/publish.md`
- FR-12 copyright_clearance.md → `ai_videos/feng_shou_lu/copyright_clearance.md`
- FR-13 ai_videos README → `ai_videos/feng_shou_lu/README.md` (now project-wide canonical index)

## 改动 5: ep02+ contract

后续 episodes 默认遵循 split layout: chapter 写入 `my_novel/{name}/chapters/{NNNN}-XXX.md`, production assets 写入 `ai_videos/{name}/episodes/epNN/`. chapter-first authoring order 跨 folder 应用.

## Out of scope

- 不改 webapp 代码 (mv-only restructure, paths 改了但 web tree reader 仍按 ai_videos/ 扫 production-side).
- 不改 downloaded_novels/ 既有 layout.
- 不动 mozun_chongsheng (它没有 my_novel/ 端, 不受影响).

## Acceptance

- `my_novel/feng_shou_lu/` = `{_meta.json, README.md, chapters/0001-第一集 落雁渊.md}` 三件套 (matches downloaded_novels schema).
- `ai_videos/feng_shou_lu/` 含全部 production 资产 (world/style_guide/arc_outline/characters/scenes/episodes/copyright_clearance).
- agent_refs rule 2 已修订 (split layout).
- spec.md FR-1 through FR-14 paths 已更新.
- changelog.md / revised_prompt.md 已 update.
- chapter excerpt 在 shot prompts 中的 path 引用更新为 my_novel/feng_shou_lu/chapters/0001-XXX.md (post chapter-excerpt-worker).
