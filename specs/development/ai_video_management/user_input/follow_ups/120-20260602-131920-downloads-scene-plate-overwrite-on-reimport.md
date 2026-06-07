---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py
  - projects/ai_video_management/tests/test_downloads_import_shots.py
severity: medium
---

# Follow-up draft 120 — 2026-06-02
导入功能 re-import 场景朝向图时不 work: 已有 `{plate_id}.png` 的 plate folder 再导入新图, 会变成 `{plate_id}1.png` + `{plate_id}2.png` 编号重复, 而非覆盖。要求 fix, existing 图直接覆盖。

## 根因
`import_drama` 两步流程 (move 保留原名 → `rename_drama` 批量按父 folder 名重命名)。plate folder 已有 `{plate_id}.png` (上次导入) 时, 新 jimeng 文件 move 进来 → folder 内 2 个 png → `MediaRenamer._plan_folder` 走「多文件」分支, 命名为 `{plate}1.png`/`{plate}2.png` (编号), 不覆盖; 且 Windows `rename` 到已存在目标会失败。结果: 累积重复 + 无干净 `{plate_id}.png`。

## What landed (stage-6)
`libs/infrastructure/writers/downloads__writer.py`:
- 新增 `_clear_folder_media(folder)` — 删 folder 顶层 media 文件 (子目录/非 media/symlink/.md 不动)。
- `import_drama`: 当 `kind == "scene_plate"` (plate folder 恒为单图), move 前先 `_clear_folder_media(dst_folder)` 清掉旧图 + 编号 junk → 覆盖语义; 之后只剩新文件 → rename 产出干净 `{plate_id}.png`。
- 通用覆盖: `dst` 同名已存在时由「报 target_exists 跳过」改为「unlink 后覆盖」。
- docstring 补述 scene-plate 覆盖行为。
- **不影响** character/scene-根/shot renders 的多文件共存语义 (clear 仅对 scene_plate)。.md 提示词文件不被删 (非 media)。

## 验证
- `tests/test_downloads_import_shots.py` 新增 2 用例: `test_scene_plate_routes_by_orientation_token` (补 follow-up 015 方位段路由的回归保护, 之前无测试) + `test_scene_plate_reimport_overwrites_and_clears_numbered` (覆盖 + 清编号 junk + .md 存活)。`pytest` 6 passed。
- 实跑 `import_drama("ai_videos/nvdi_tuihun_houhuile")`: 6 张 06-02 新图全归位 bg1-bg6, 清掉旧的 `{plate}1/{plate}2.png` junk, 每 folder 恰 1 张 `{plate_id}.png` = 新图, 0 error。
