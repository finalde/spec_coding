---
target_stage: 6
target_artifacts:
  - apps/ui/src/components/PerfScorePanel.tsx
  - apps/api/routes/perf_check__route.py
severity: low
---

# Follow-up draft 123 — 2026-06-13

表演评分面板新增「让 Claude 检查已下载 MP4 并打分」按钮：一点即定位该 perf 条目已下载的成片，未发现或发现多个时报错，恰好一个时组装 copy-paste prompt 让 Claude 抽帧检查并打分。

- 按钮落在 perf-score 面板（`PerfScorePanel`，仅 `_performances/<情绪>/perf_NNNN/perf_NNNN.md` 条目可见），紧邻既有的「保存我的评分」。
- 后端新增只读 `perf_check` 端点 `POST /api/perf-check-prompt`（body `{path}`，path = 该 `perf_NNNN.md` 相对路径）。读侧 Query → Reader，遵循与 `shot_regen` 完全一致的结构（query 跳过 domain 层的读侧豁免）。
- MP4 定位：只扫描该条目 `renders/` 文件夹的直接 `.mp4` 子文件（大小写不敏感，不递归 `archive/`）——与 episode-concat / downloads「每镜最新 renders mp4」约定一致。
  - 0 个 → `{ok:false, kind:"no_mp4", message}`（未发现，提示先放进 `renders/` 或用「从下载导入」）。
  - >1 个 → `{ok:false, kind:"multiple_mp4", candidates, message}`（列出文件名，要求只保留要评的那个）。
  - 恰好 1 个 → `{ok:true, kind:"ok", prompt, mp4, candidates}`，prompt 指示 Claude Code CLI：读条目拿目标情绪+锁定块+达标线 → ffmpeg 抽帧 + Read 看图 → 三轴 1–5 盲评 → `curl POST /api/perf-score`（`who=Claude`，后端默认 `127.0.0.1:8766`）写回并重算合议。
- 接线：container（`perf_check_reader` Singleton + `perf_check_query` Factory）+ `routes/__init__.py`。路径非法走既有 `InvalidDramaPathError` → 400 映射（`PerfCheckPathError` 继承之，与 `ShotRegenPathError` 同模式）。
- 前端：`api.ts` `perfCheckPrompt()` + `PerfScorePanel` 按钮/handler/状态 + 只读 prompt 文本框 + 📋 复制。沿用浅色主题真实变量（`--bg`/`--text`/`--border`），不再硬编码深色。
