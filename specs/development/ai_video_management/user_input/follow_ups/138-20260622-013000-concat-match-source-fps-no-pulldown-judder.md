# Follow-up draft 138 — 2026-06-22
合成视频整体「还是不顺」。诊断：根因不在接缝——是**强制 30fps 上变换**。shot render 实测 ~24fps（VFR，24.04–24.09），合成时被硬转 30fps，每 5 帧多复制 1 帧（4:5 pulldown），全片约 30% 帧是复制帧 → 整片 judder，所以裁接缝怎么裁都不顺。修法：合成输出帧率**跟随源**（探测中位 fps、snap 到最近标准帧率），不再硬编码 30。用户：「还是不顺」。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: high
---

## 背景
前三轮（裁重复帧 133/134、xfade 135 撤回 136、两侧裁坡道 137）都只动接缝，但用户始终觉得不顺。实测 mpdecimate：30fps 输出里 ~30% 是复制帧；改 24fps 后降到 ~3%（剩下是真静止内容）。源 clip 全是 ~24fps，硬转 30 注入大量复制帧＝全片卡顿，与接缝无关。这才是"不顺"的主因。

## 指令
合成输出帧率改为**匹配源 cadence**：`_ffmpeg_concat` 探测各 clip 的 fps、取中位、snap 到最近标准帧率（24/25/30/50/60，容差 1.5；24 与 25 仅差 1 故取最近不取首个命中），探测全失败才回落 `_CONCAT_FALLBACK_FPS=30`。`fps={target}` 用该值。其余（720×1280/pad/setsar/butt-join/两侧裁坡道）不变。

## 实现
- 常量：`_CONCAT_TARGET_FPS=30` → `_CONCAT_FALLBACK_FPS=30` + `_STANDARD_FPS=(24,25,30,50,60)` + `_FPS_SNAP_TOL=1.5` + `_FPS_RE`。
- 新增 `_target_fps`（中位+snap+回落）/`_probe_fps`（`ffmpeg -i` 解析 "NN fps"）/`_snap_fps`（取最近标准、容差内才 snap）。
- `_ffmpeg_concat` 算 `target_fps=self._target_fps(...)`，filter 用 `fps={target_fps}`。

## 校验
- 真跑 EP1（wushen_juexing）：输出 23.89fps（≈24 原生）、12 镜 127.6s；复制帧 ~30%→~3%。
- 测试 +3：`_snap_fps` 边界（24.05/23.89→24, 29.97→30, 25.10→25, 47→47）、`_target_fps` 24fps 源→24（不上变 30）、不可探测回落 30。合成测试用 30fps testsrc→snap 30 仍绿。pytest 28 绿。零 prompt 改动。
- 注：感知是否真顺需用户肉眼确认。若仍有残留接缝感，则属 i2v 两段独立生成的运动轨迹不连续（裁帧/帧率均无法消，需生成侧处理）。
