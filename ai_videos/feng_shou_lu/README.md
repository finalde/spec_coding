# 《焚寿录》— AI 短剧 production 工作区 (feng_shou_lu)

## 项目概要

《焚寿录》是一部男频硬核仙侠 AI 短剧 (60 集 × 1-2 分钟, 9:16 竖屏). 本目录是 **AI 短剧制作工作区** — 所有 剧本 / 分镜 / shot prompts / 角色档 / 场景档 / 风格指南 / 世界观 / 60 集大纲 / 发布信息 / 版权清查 等 production 资产都在这里.

小说原稿 (用户可读的章节文件) 位于平级目录 `my_novel/feng_shou_lu/`. chapter 是 production 的源头 (canonical source-of-truth), script / shotlist / shot prompts 全部从 chapter derive (chapter-first authoring order per follow-up 006).

## 目录布局 (post follow-up 009 split)

```
ai_videos/feng_shou_lu/                # YOU ARE HERE — production canonical
├── README.md                          # 本文件
├── world.md                           # 世界观 (修炼境界 / 三方势力 / 地理 / 寄生 lore)
├── style_guide.md                     # 风格指南 (镜头词典 / 调色 / 字幕 / 负向)
├── arc_outline.md                     # 60 集 one-liner 大纲 + 24-tick 寿元 ledger
├── copyright_clearance.md             # 版权清查 SIGN-OFF
├── characters/
│   └── c{N}_{中文名}/{中文名}.md      # 11 个角色 bible (rule 12.5 v5 hybrid folder)
├── scenes/
│   ├── s1_无寿崖.md                    # 场景档 + 嵌入式 Seedream 立绘段 (rule 12.3 v2)
│   └── s2_落雁渊.md
└── episodes/
    └── ep01/
        ├── script.md                  # screenplay form (derived from chapter)
        ├── shotlist.md                # 7 shots 镜头清单
        ├── shots/
        │   └── shotNN.md              # 每镜 prompt (3-section: chapter excerpt + shot context + 视频 prompt) per rule 5 v3
        └── publish.md                 # 发布信息 (标题 / 简介 / hashtag / 封面)

my_novel/feng_shou_lu/                # 平级 — reader-side novel format (downloaded_novels-compatible schema)
├── _meta.json                         # 章节 metadata
├── README.md                          # 小说扉页 + 章节列表
└── chapters/
    └── 0001-第一集 落雁渊.md          # 章节 prose (用户可读, ~10,943 字)
```

## 渲染产物布局 (操作人填充)

```
ai_videos/feng_shou_lu/
├── characters/
│   └── c{N}_{中文名}/
│       └── turntable.mp4              # 从主 bible 中的 turntable prompt 渲染的 7s 单 take
├── scenes/
│   ├── s1_无寿崖.png                  # 从 scenes/s1_无寿崖/s1_无寿崖.md 中嵌入式 Seedream 立绘段渲染 (静默态, 默认; 用于 ep17 / ep49 / ep60)
│   ├── s1_无寿崖_渡劫态.png            # 渡劫态变体 PNG (ep01/shot01 cold open + ep08 倒叙 unfiltered)
│   ├── s1_无寿崖.mp4                  # 15s walk-through 场景 reference 视频 (rule 12.10); 喂 Kling/Seedance image-to-video 时作 scene reference 上传
│   ├── s2_落雁渊.png                  # Seedream 立绘 PNG (黎明态 + 焚寿罗盘 cold light; 用于 ep01 / ep02)
│   └── s2_落雁渊.mp4                  # 15s walk-through 场景 reference 视频 (rule 12.10)
└── episodes/
    └── ep01/
        ├── shots/
        │   ├── shot01_kling.mp4       # Kling 渲染产物
        │   ├── shot01_seedance.mp4    # Seedance 渲染产物
        │   └── ...
        ├── ep01_final.mp4             # 剪映 / CapCut 拼接 + 字幕成片
        └── ep01_cover.png             # 发布封面 (= shot07.lastframe 静帧定格)
```

## 使用说明 (人 → AI 模型)

```
1. 读 ../../my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md    ← canonical chapter prose
        ↓
2. 读 episodes/ep01/script.md       ← screenplay derived from chapter
        ↓
3. 角色 turntable: 复制 characters/c{N}_{中文名}/{中文名}.md 中 `---` 后的 turntable prompt
   → 粘贴到 Seedance/Kling/Sora/Veo 渲染 7s mp4
        ↓
4a. 场景立绘 (静默/黎明态): 复制 scenes/s{N}_{name}.md 中第一段 `---` 后的 Seedream 立绘 prompt
   → 粘贴到 Seedream 渲染 PNG (s1_无寿崖.png 静默态 / s2_落雁渊.png 黎明态)
        ↓
4b. 场景立绘 渡劫态变体 (仅 s1): 复制 s1_无寿崖.md 中 `# Seedream 立绘 prompt — s1_无寿崖 渡劫态变体` 段
   → 粘贴到 Seedream 渲染 PNG (s1_无寿崖_渡劫态.png; ep01/shot01 + ep08 用)
        ↓
4c. 场景 reference 视频 (15s walk-through): 复制 scenes/s{N}_{name}.md 中 `# 场景 reference video prompt` 段
   → 粘贴到 Kling 2.1 Pro 或 Seedance 1.0 Pro (duration=15s, aspect_ratio=9:16, no_audio=true)
   → 渲染 mp4 (s1_无寿崖.mp4 / s2_落雁渊.mp4); 该 mp4 作为下游所有 shot 的 scene video reference 上传
        ↓
5. shot 视频: 复制 episodes/ep01/shots/shotNN.md 中 `## 视频 prompt` 下的 fenced text 段
   → 粘贴到 Kling 2.1 Pro 或 Seedance 1.0 Pro
   → 上传 Reference uploads checklist 中列的 turntable mp4 + 场景 mp4 (优先, 取代纯 PNG) + 场景 PNG (备选)
   → 渲染 7 个 ≤ 15s 视频片段
        ↓
6. 剪映 / CapCut 拼接 + 后期软字幕 → ep01_final.mp4
        ↓
7. publish.md → 标题 / 简介 / hashtag / 封面 copy 到抖音 / 红果 / YouTube Shorts
```

## 角色清单 (ep01 出场, c-prefix folder)

| folder | 中文名 | 派系 | ep01 出场方式 |
|---|---|---|---|
| c1_裴知秋 | 裴知秋 | 男主 · 双形态 | 全集 (state A 重生弱体 ep01 主) |
| c2_裴长砚 | 裴长砚 | 男主前世 (archived) | 0:00–0:03 渡劫死亡 cold open |
| c3_闻砚清 | 闻砚清 | 师父 | 1:35–2:00 剪影 + 1 帧正脸 cliffhanger |
| c4_容漪 | 容漪 | 主女主 | 0:18–0:30 远处 visual cameo |
| c5_阮瑶 | 阮瑶 | 童年邻家姐姐 | (ep01 未直接出场, ep02 江岸初登场) |
| c6_卫长烛 | 卫长烛 | 正派 · 赤霞门 | 0:03–0:08 倒叙第一位 (递剑 → 反手刺穿) |
| c7_应砚之 | 应砚之 | 朝堂 · 太师之子 | 0:08–0:13 倒叙第二位 |
| c8_戚归砚 | 戚归砚 | 散修 + 魔门 dual | 0:13–0:18 倒叙第三位 (内衬深紫翻领伏笔) |
| c9_池洇 | 池洇 | 散修盟 杀手长老 | 0:18–0:21 倒叙第四位 |
| c10_阮惘 | 阮惘 | 魔门 三长老 | 0:21–0:25 倒叙第五位 |
| c11_言息 | 言息 | 魔门教主 / BOSS | 0:25–0:30 倒叙第六位 (黑卷裴长砚名字红光屑) |

## 风格关键词

水墨灰青 · 月白 · 寄生紫 `#4a1a5a` · 寿元红 `#a82c2c` · 9:16 · cinematic · 4K HDR · DSLR 85mm · ARRI · photorealism · 真人写实 · 亚洲俊男靓女 · 寿命计数器过 (本剧专属转场) · 5s 寄生升级 motif (系统提示 1.5s → 寄生 aura 2s 顿挫 → 寿命流失 1.5s)

---

*生成自 spec-driven 流水线 `xianxia_new-20260524-101931`. 文本性 spec / 研究 / 验证 详见 `specs/ai_video/xianxia_new/`. 小说原稿 (用户可读的章节文件) 在平级 `my_novel/feng_shou_lu/`. Post follow-ups 003 (scenes single-file + seam-frame abolished) + 004 (characters folder pattern) + 005 (mirror characters) + 006 (chapter.md canonical) + 007 (chapter excerpts in shots) + 008 (c-prefix hybrid folder) + 009 (split reader vs production).*
