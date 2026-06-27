# Follow-up draft 148 — 2026-06-27

一键把所有带字幕的 ep 导出到 production folder（中文/英文分子文件夹）；并新增剧 level 主页（点 left nav 的剧 → 右侧 main page 放剧级按钮与展示）。

---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/components/Reader.tsx
  - projects/ai_video_management/apps/api/routes/
severity: medium
---

## 指令
1. **一键导出 production**：把一部剧所有**带字幕的 ep 成片**拷到 `ai_videos/{drama}/production/`——中文（`ep{NN}_zh.mp4`）进 `中文/` 子文件夹、英文（`ep{NN}_en.mp4`）进 `英文/` 子文件夹（中英 `ep{NN}_zhen.mp4` 若存在进 `中英/`）；子文件夹内文件去语言后缀命名 `ep{NN}.mp4`（lang 由文件夹表示）。覆盖、不删旧文件、报每语言计数。
2. **剧 level 主页（dashboard）**：left nav 的剧级 toolbar 按钮已放不下；点击一部剧（其 README 页作锚）右侧呈现一个 main page，承载剧级按钮（导出 production + 全剧烧字幕等）与剧级展示/功能，后续剧级功能都往这放。

## 落地
- 后端：`production__{writer,command,dto,mapper,route}` + container wiring + routes/__init__ 注册。`POST /api/export-production {path}` → 解析 drama root（复用 subtitle_batch `_drama_root`/`_episode_dirs` 两种 layout）→ 找各 ep 的 `ep{NN}_{zh|en|zhen}.mp4` → `shutil.copy2` 到 `production/{中文|英文|中英}/ep{NN}.mp4`。
- 前端：`exportProduction` in api.ts + 新 `DramaDashboard` 组件（在 isDramaReadme 页渲染为 main page：剧级动作区[导出 production + 全剧烧字幕 zh/en/both（从 toolbar 迁入）] + README 内容）；toolbar 去拥挤。
- 测试：`test_production_export.py`（两 layout、按语言路由、去后缀命名、skip 无字幕 ep）。
