---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
severity: medium
---

# Follow-up draft 008 — 2026-06-14

场景生成分步走（video-first），且场景 video 每一秒的朝向必须与截帧方向一一对应。

## 抽象后的指令

场景生成流水线分三步：
1. **背景图 seed prompt**：生成一张基底背景图（即现在的 Seedream 立绘风格，保留）。
2. **场景 video prompt**：另给一条视频 prompt，用户把第①步的背景图**上传作 reference**，生成一段**环视各角度**的场景视频。
3. **一键截各方向场景图**：用户下载视频后，用 webapp 已有功能一键从视频里截出**各个方向**的场景图（DownloadsImporter 按 `bg{N}_{方位}` 方位段路由到对应 plate folder）。

**核心要求**：场景 video 的**每一秒朝向**必须与**截帧方向 / plate 方位**严格一一对应——即视频 prompt 要带**逐秒方位时间轴**（朝北/朝东/朝南/朝西/高位俯瞰…），且与背景图系统 index 表里「方位 ↔ 秒段 ↔ 截帧时点 ↔ plate folder」完全吻合，这样用户在某一秒截帧 = 已知方位的 plate。

## 落地

- scene 档 s1_裴王府正厅 重构为三段：① 步骤一·背景图 seed prompt（保留现有立绘）② 步骤二·场景 walk-through video prompt（15s，逐秒方位时间轴，上传背景图作 reference）③ 背景图系统 index（方位↔秒段↔截帧时点↔plate folder）。
- 建 folder-per-朝向 plate（`scenes/s1_裴王府正厅/bg{N}_{方位}_{描述}/{同名}.md`），每 plate 的 image prompt `主体:` 行以「{scene} {方位}视角」开头（nvdi 015：方位段须进 主体行，供下载文件名路由）。
- 唯美仙侠写实 + 反卡通铁律（follow-up 007）延续；零 hex；不点名 IP。
