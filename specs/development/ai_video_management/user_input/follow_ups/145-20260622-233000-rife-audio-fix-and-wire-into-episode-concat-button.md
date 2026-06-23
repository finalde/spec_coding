# Follow-up draft 145 — 2026-06-22
安装/配置 RIFE 后实测 EP1 承接缝补帧效果获认可；给 `tools/seam_concat.py` 加回音轨 + 逐缝承接/硬切控制；把 RIFE 补帧接进 webapp「合成本集视频」button。

---
target_stage: 6
target_artifacts:
  - tools/seam_concat.py
  - projects/ai_video_management/libs/infrastructure/writers/episode__writer.py
  - projects/ai_video_management/apps/ui/src/components/Reader.tsx
severity: medium
---

## 背景
144 落地 seam_concat 工具（trim+dedup，RIFE 未本地实测）。本回合：
1. 本机装好 RIFE（`rife-ncnn-vulkan` 20221029），GPU 自检通过（NVIDIA RTX 5000 Ada；运动中点帧落在中间＝真补帧非叠化）。安装位置 `C:\tools\rife\rife-ncnn-vulkan-20221029-windows\rife-ncnn-vulkan.exe`。
2. EP1 实测：只在 2 条**承接缝**（shot10→11、shot11→12）补帧、其余 9 条硬切保持原样 → 用户认可效果（「效果不错」）。
3. 用户反馈两点：① 成片**没声音**了；② 把 RIFE 补帧**接进 webapp 的 button 点击**。

## 改动
### A. seam_concat 加回音轨
- `_render_body` 保留对应时间窗的音频（`atrim` 对齐视频 trim；源无音轨→`anullsrc` 静音补齐），统一 44100/stereo/aac。
- RIFE 桥段（合成帧本无声）加同长静音轨——桥落在 <0.2s 的走位/驻足 beat，静音即静、非掉音。
- 末段 concat 改 `v=1:a=1`（双流），每段 a/v layout 一致才能 concat。
- 顺手修：`main()` 开头把 stdout/stderr 重配 utf-8，避免中文路径在 cp1252 终端 print 崩溃。

### B. seam_concat 逐缝承接/硬切控制（关键正确性）
- 新增 `--seams`：长度＝片段数-1 的 `b`(承接 bridge＝trim+RIFE)/`c`(硬切＝纯 butt-join，不 trim 不补帧) 串。省略＝全 bridge（旧行为）。
- 原因：工具原先对**每条缝**一视同仁 trim+补帧，会把**故意的硬切**也补糊。EP1 只有 2 条承接缝，其余是设计好的切镜，绝不能动。
- `seam_concat()` 现返回实际补帧的 bridge 数（供 webapp 上报）。

### C. RIFE 接进 webapp「合成本集视频」button
- 链路：Reader.tsx 复选框「🪄 RIFE 补帧」(localStorage 持久化、默认开) → `concatEpisode(path, lang, rife)` → `POST /api/concat-episode {rife}` → `EpisodeCommand.concat(..., rife)` → `EpisodeConcatBuilder.build(rel, lang, rife)`。
- builder 已有 `_is_continuity_shot`（读 shotNN.md `衔接:` 行判承接/硬切），据此自动生成 `--seams`；rife=True 且存在承接缝时，**复用 `tools/seam_concat.py`（按 sandbox root 路径 import，单一事实源、不复制逻辑）**做拼接，否则走原忠实硬拼接（行为不变）。
- RIFE exe 路径来自 env `RIFE_NCNN_VULKAN_EXE`，否则默认安装路径。**rife=True 但 exe 不存在 → 明确报错（`rife_exe_not_found`），绝不静默退回 butt-join**（符合 CLAUDE.md「无静默 fallback」）。
- 结果新增 `rife_used` / `rife_bridges`，UI toast 显示「RIFE 补帧 N 处承接缝」。

## 决策记录（写给未来）
- **承接/硬切判定的唯一来源** = shotNN.md 的 `衔接:` 行（builder `_is_continuity_shot` 已实现；seam_concat 侧用 `--seams` 显式接收）。webapp 自动算、CLI 手动传。
- **webapp 不复制补帧逻辑**：按路径 import `tools/seam_concat.py`，避免与用户后续调参漂移。
- 默认开 RIFE：用户要的就是它；无 GPU/exe 的机器会明确报错提示装/设路径，而非偷偷降级。

## 验证
- seam_concat 重建 EP1（`--seams cccccccccbb`）：12 镜、2 RIFE 桥、131.7s、含 aac 44100 stereo 音轨。
- builder 直驱（button 代码路径）`build(ep01, lang=zh, rife=True)`：rife_used=True、rife_bridges=2、12 镜 0 跳过、写 ep01_zh.mp4。
- 既有 `tests/test_episode_concat.py` 21 项全过（rife 默认 False，旧行为不变）。
- 前端 `tsc --noEmit` 0 错；`npm run build` 成功，bundle 写入 apps/backend/static。
