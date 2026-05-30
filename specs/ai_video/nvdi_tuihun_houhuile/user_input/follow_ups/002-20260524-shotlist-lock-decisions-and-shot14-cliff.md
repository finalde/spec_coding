---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shotlist.md
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot14/shot14.md
  - specs/ai_video/nvdi_tuihun_houhuile/user_input/raw_prompt.md
severity: medium
---

# Follow-up draft 002 — 2026-05-24

User authorized parent-direct best-judgment on all 待确认 items from follow-up 001's shotlist + correct earlier `prompts/` → `shots/` claim.

## Locked decisions (6 items)

| # | Item | Resolution | Rationale |
|---|---|---|---|
| (a) | shot14 cliff 是否拍 | ✅ 拍 | reveal motif 完整释放 + ep02 入口锚, 8s 短而力, 与 shot06 reveal 1 帧闪对偶 |
| (b) | shot06 V.O. 字幕呈现 | 浅金 `#d8b070` 斜体 + "OS:" 前缀 | 沿用 style_guide.md default |
| (c) | shot01 朱红诏书展开 motif 渲染 | 实拍 太监 手持 | 与全片真人写实风格统一 |
| (d) | shot04 / shot11 reaction 是否微推 | 纯锁机位 | 微表情 carry beat, 推镜稀释力度 |
| (e) | shot02 父子跪听机位 | 侧背 + 略低仰角 5° | 体现"被宣旨"压抑感 |
| (f) | shot01 标题卡 0.5s 加不加 | 不加 | cold open 视觉力度更纯; 标题可在剪映后期加 |

## Generated artifact

- `episodes/ep01/shots/shot14/shot14.md` — cliff shot, 8s, 陈凡 reveal motif 完整释放 (装废姿瞬解 + 桃花眼锐光渐变 3-5s + V.O. "戏 ... 该开场了"). 包含 反向锐光 光位渐变 motif (顶左 30° 斜光 → 0° 正面冷光 4200K), 是 shot06 的 0.1s 1 帧闪 reveal 的 "对偶完整版"。

## Correction to follow-up 001's claim

follow-up 001 stated:

> The canonical rule in `agent_refs/project/ai_video.md` (rule #2 v3 layout diagram lines 45-51 + rule #12.9 layout lines 1174-1180) still says `prompts/` — this is a known drift that may want to be promoted to canonical in a future follow-up.

This was **incorrect**. Grep of `agent_refs/project/ai_video.md` shows the canonical rule was already migrated to `shots/` by follow-up `xianxia_new/011`. There is no drift to promote. `raw_prompt.md` reference patched to drop the inaccurate "project-scoped naming divergence" note.

## Final ep01 structure

```
ai_videos/nvdi_tuihun_houhuile/episodes/ep01/
├── script.md           # screenplay (single 接旨 scene)
├── shotlist.md         # 14 shots locked, 70s total
└── shots/
    ├── shot01/shot01.md  # cold open 朱红诏书 + 太监起手 (5s, hook)
    ├── shot02/shot02.md  # 父子跪听全景 (4s, cutaway)
    ├── shot03/shot03.md  # 太监续宣 (5s)
    ├── shot04/shot04.md  # 陈国公 侧脸 reaction (3s)
    ├── shot05/shot05.md  # 太监 收尾宣旨 钦此 (4s)
    ├── shot06/shot06.md  # 陈凡 V.O. + reveal 1 帧 (6s)
    ├── shot07/shot07.md  # 太监催 接旨 (4s)
    ├── shot08/shot08.md  # 陈凡 接诏 全景微推 (5s)
    ├── shot09/shot09.md  # 陈凡 谢主隆恩 (4s)
    ├── shot10/shot10.md  # 太监 警告起手 (5s, cover-frame)
    ├── shot11/shot11.md  # 陈国公 reaction (4s)
    ├── shot12/shot12.md  # 太监 续警告 + 阴笑 (5s)
    ├── shot13/shot13.md  # 陈国公 表态收束 (8s)
    └── shot14/shot14.md  # cliff: 陈凡 reveal motif 完整释放 (8s)
```

## Next步 (操作人执行)

1. 渲染 3 个角色 turntable mp4: c1_陈凡 / c3_陈国公 / c4_太监 各 7s (rule 12.5 v11)
2. 渲染 s1_陈国公府正厅 walk-through mp4 15s (rule 12.10 v3)
3. 按 shotlist 渲染顺序拍 shot01-14
4. 剪映 / CapCut 拼接 + 后期软字幕 + (可选) 0.5s 黑底烫金标题卡 → ep01_final.mp4
