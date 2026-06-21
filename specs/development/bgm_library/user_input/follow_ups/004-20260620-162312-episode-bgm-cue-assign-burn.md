# Follow-up draft 004 — 2026-06-20
Episode 级 BGM 编排：按剧情稀疏 cue 时间线 + 像 casting 一样把库内 bgm 分配进占位 + 一键烧录进带字幕的整集视频。

---
target_stage: 6
target_artifacts:
  - final_specs/spec.md
severity: high
---

## 指令（抽象后）

在 `ai_video_management` webapp 上，为 BGM 库补一层 **episode 级编排 + 烧录**，对接 v1 留作后续的「多 cue 整条 bgm.md 自动编排」：

1. **每个 episode 一个 BGM 编排**：按剧情生成一条**稀疏** cue 时间线（不是每秒都有 BGM，只在强烈激情/武打/悲伤等特定剧情段才铺），落 `episodes/epNN/bgm/bgm.md`（独立 `bgm/` 文件夹 + md）。每条 cue = 时间窗(整集秒数) + 期望情绪(category) + vol/duck/fade + 剧情注释。cue 编排由 AI-video pipeline 人工读剧本产出（不在 webapp 自动生成）。
2. **像 assign actor 一样 assign BGM**：用户在 webapp 的 episode BGM 面板里，给每个 cue 占位（`-`）从库里按情绪选一条 `bgm_NNNN` 填入（webapp 改写 bgm.md 的该行 slot）。
3. **一键烧录按钮**：把已分配的 cue 按时间窗烧进**带字幕的整集视频** `ep{NN}_zh.mp4`（不是原视频/不是 renders），输出 `ep{NN}_zh_bgm.mp4`；**二次烧录直接覆盖**。源 `ep{NN}_zh.mp4` 保留不动作为干净重烧源。`renders/` 原始视频绝不覆盖。
4. duck=on 的 cue 在台词处自动让路（用整集自身台词音轨做 sidechain）；未分配的 cue 烧录时跳过并在结果里报。

## 决策（已与用户确认）

- BGM 级别 = **episode**（一条跨整集的稀疏时间线），非 shot 级。
- 输出文件名 = **`ep{NN}_zh_bgm.mp4`**；源 `ep{NN}_zh.mp4` 保留；重烧覆盖 `_zh_bgm`。
- cue 编排来源 = **AI 人工读剧本写**（pipeline 侧），webapp 只做 assign + 烧录。
- episode bgm 落点 = `episodes/epNN/bgm/bgm.md`（folder + md）。
