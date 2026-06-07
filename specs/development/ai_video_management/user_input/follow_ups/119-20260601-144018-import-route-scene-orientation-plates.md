---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py
severity: low
---

# Follow-up draft 119 — 2026-06-01
导入+重命名 (DownloadsImporter) 要支持把场景背景图归位到「朝向 plate 子 folder」，而不仅是 scene 根。

## 背景
ai_video 场景背景采 folder-per-朝向：`scenes/{scene}/bg{N}_{方位}_{描述}/`，每朝向一张 PNG。出图工具 (jimeng/即梦) 的下载文件名取 prompt `主体:` 行正文，含朝向「方位词」(朝北/朝南/朝东/朝西/高位俯瞰/案前)，但**不**含完整 plate_id。旧导入只把文件匹配到 scene 根，6 张朝向图全挤在 scene 根 + 被 rename 折叠，无法归位。

## What landed (stage-6 净增量)
`libs/infrastructure/writers/downloads__writer.py`:
- `_plate_orientation_token(folder_name)` — 取 `bg\d+_` 之后第一段 (= 方位) 作路由 token；非 `bg{N}_` folder 返回 None。
- `_match_scene_plate(filename, scene_folder)` — 文件已匹配到 scene 后，遍历该 scene 的 plate 子 folder，按**方位段**子串匹配，命中则把目标下沉到该 plate folder。
- `import_drama` 在 `chosen.kind == "scene"` 时调用上面，命中后 kind 记 `scene_plate`。
- 只匹配方位段、不匹配描述段 (描述词如 厅门/东侧 会作相机走位词散落别朝向文件名→串档；方位段两两互斥)。
- 含 scene 名但无方位词的文件 (walk-through `.mp4`) 仍留 scene 根。
- 既有 `rename_drama` 步骤自动把归位后的文件按父 folder 名改成 `{plate_id}.png` — 无需改动。

纯增量：不改 character / shot / 既有 scene-根 路由语义；仅在 scene 下存在 `bg\d+_*` 子 folder 时触发。

## 验证
实跑 `import_drama("ai_videos/nvdi_tuihun_houhuile")`：6 张 jimeng 背景 PNG 全部归位 bg1–bg6 + 自动重命名，moved 全为 `scene_plate`，0 unmatched / 0 error。
