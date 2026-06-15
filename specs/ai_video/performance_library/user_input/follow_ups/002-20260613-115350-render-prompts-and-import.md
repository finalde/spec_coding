# Follow-up draft 002 — 2026-06-13

给我一系列可以 copy-paste 的 prompt（发给 Seedance / Kling 生成测试视频）；下载视频后希望一键从 download folder 导入到对应的表情演技栏目下面。整个设计要 well structured。

---

## 抽象指令

为演技库提供端到端的「渲染 → 下载 → 一键归位」工作流：

1. **可 copy-paste 的 prompt 清单**：每种情绪一个 `_render_queue.md`，从上到下列出每条 entry 的 起始帧 / Kling / Seedance render prompt，整段可复制。
2. **下载视频一键导入**：下载的检验视频/起始帧能按 entry 自动归位到 `_performances/{emotion}/perf_NNNN/`，并重命名为规范名。
3. 整个设计 well-structured、可复现、与既有 shot 渲染导入机制同源。

## 设计（已实现）

- **导入 tag 约定**：每个 render prompt 块首行加紧凑 tag `演{NNNN}{克|即|始}`（演=演技库 / NNNN=perf号 / 克=Kling、即=即梦Seedance、始=起始帧Seedream）。落在 Kling 9 字符截断窗口内、每条唯一——解决「所有 prompt 以 actor_0001 开头会撞名」的路由问题（同 ai_video.md rule 12.4 shot tag 思路）。
- **渲染队列**：`tools/build_render_queue.py` 从各 perf 文件抽取 render 块生成 `{emotion}/_render_queue.md`（generated，勿手改）。
- **一键导入**：复用 `POST /api/import-from-downloads`，path=`ai_videos/_performances` 时 dispatch 到新的 `DownloadsImporter.import_performances()`，按文件名 `演{NNNN}` 路由到 perf 文件夹、按 克/即/始 重命名为 `perf_NNNN__{kling|seedance|startframe}.{mp4|png}`；未匹配进 `_performances/_not_matched/`；重导入覆盖。
- **前端按钮**：侧栏 `_performances` 根显示「📥 导入检验视频」按钮（复用 onRenameClick）。

## 影响

- 关联 FR-11（检验视频 prompt）/ FR-12（webapp 集成）/ FR-13（实测回填）。新增渲染-导入工作流，落 spec FR-15。
- 路径仍英文/拼音；tag 与文件名为内容层，符合既有约定。
