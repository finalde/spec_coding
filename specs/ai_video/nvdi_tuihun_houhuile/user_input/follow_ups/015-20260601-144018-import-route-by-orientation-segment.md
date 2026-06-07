---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/
  - projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 015 — 2026-06-01
当前导入没把 6 张朝向图放进指定的朝向 folder。要求查下载文件的命名规则，确保「导入+重命名」能把它们归位到对应朝向 folder。

## 实测命名规则 (jimeng / 即梦)
下载文件名 = `jimeng-{date}-{4位id}-{prompt 主体行前段}.png`，例:
`jimeng-2026-06-01-3688-陈国公府正厅 朝北视角，相机自南厅门方向平视向北，35mm…png`。
→ 工具**不**用 prompt 首行 (014 设想的 plate_id key) 做文件名，而用 `主体:` 行正文。故 014 的「首行写 key→归位」机制**失效**，本条修正之。

## 抽象结论 (institutional)
- 归位路由键 = 朝向 folder 名 `bg{N}_{方位}_{描述}` 的**方位段**（朝北/朝南/朝东/朝西/高位俯瞰/案前），它必出现在 `主体:` 行开头 → 必入下载文件名。
- 导入器只匹配**方位段**，不匹配描述段：描述词 (厅门/东侧/西墙…) 会作为相机走位词散落在别朝向文件名里 (如「朝北…自南厅门方向」含「厅门」)，匹配描述段会串档；方位段两两互斥。
- 场景 walk-through `.mp4` (含 scene 名、无方位词) 留 scene 根。

## 落地
1. `DownloadsImporter` 新增 scene→plate 路由：匹配到 scene 后，按方位段把文件下沉到 `bg{N}_…/` 子 folder (`_match_scene_plate` / `_plate_orientation_token`)。move 后既有 rename 步骤自动改名为 `{plate_id}.png`。
2. `bg6_案前虚化背景` → 重命名 `bg6_案前_虚化背景` (补方位段下划线，使方位段 = `案前` 可匹配 `案前跪礼区` 文件名)。
3. 实跑导入：6 张 PNG 全部归位 bg1–bg6 并重命名，0 unmatched / 0 error；清掉 scene 根一张旧的误路由重复图 (hash 与 bg1 一致)。
4. scene 主档 + 各 plate md + ai_video.md「命名/导入约定」全部从「首行 key」改述为「方位段路由」。
