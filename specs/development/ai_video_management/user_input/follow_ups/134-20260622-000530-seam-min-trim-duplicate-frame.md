# Follow-up draft 134 — 2026-06-22
首尾帧链接 + concat freeze-trim 后，承接接缝处仍有轻微卡顿（~1帧）；要在 concat 时把残留的"结构性重复帧"也去掉，画面 smooth、观众看不出。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: medium
---

## 根因（残留卡顿）
承接镜 B 的**首帧 = 上一镜 A 的末帧**（B 就是用 A 末帧生成的），所以 seam 处那一帧是**结构性重复帧**。原 freeze-trim 用 freezedetect（d=0.04s）检测头部静止段——但**1–2 帧的极短重复/近似帧低于其检测阈值时会漏检**，留下 ~1 帧 micro-stutter。

## 修法（concat 端，按钮即处理，无需改 prompt）
`EpisodeConcatBuilder`：承接镜（i>0）的 head_trim 改为 `max(detected_freeze, _SEAM_MIN_HEAD_TRIM_S=0.08s)`——freezedetect 没测到长 freeze 时，**也保底裁掉 ~0.08s（2–3 帧@30fps）**，确保结构性重复帧一定被去掉。硬切镜与首镜不裁。

## 用户问答
- 「前后各延长0.1秒」→ **方向反了**：延长=加 hold=更卡。要 **裁掉**重复帧（或 crossfade 重叠），不是 extend。
- 「点 button 能处理么/要改 prompt 么」→ **button（concat）端处理，零 prompt 改动**。帧级接缝与 prompt 文本无关。
- 若保底裁后仍有"速度突变"型 hitch（A 减速入帧 vs B 加速出帧）→ 下一步可加**承接 seam 短 crossfade（~0.12s）**（escalation，未做）。

## 实现 + 校验
- 新增常量 `_SEAM_MIN_HEAD_TRIM_S=0.08`；build() head_trim 取 max(detected, min)。
- 测试 +1（detector stub=0 → 承接镜 trimmed_s==min，硬切/首镜=0）；pytest 22 绿（episode 15 + boot smoke）。
