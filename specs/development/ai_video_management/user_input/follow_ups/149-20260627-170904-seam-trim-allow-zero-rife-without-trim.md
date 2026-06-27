# Follow-up draft 149 — 2026-06-27

拼接功能（SeamPlanModal）裁切秒应允许从 0 开始（现在 min=0.04），即可以「只选 RIFE 但不裁切」（trim=0）。

---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/components/SeamPlanModal.tsx
  - tools/seam_concat.py
severity: low
---

## 指令
RIFE 接缝的「裁切秒」输入框 `min=0.04` 强制至少裁 0.04s，用户无法选「RIFE + 不裁切」。允许 trim 从 0 开始。

## 根因 / 落地
- 前端：`SeamPlanModal.tsx` 裁切 input `min={0.04}` → `min={0}`（step 0.02、max 0.4 不变）；TRIM_HELP 补一句「0=不裁切，仅在接缝处补帧平滑」。
- 后端：plan 路径已不 floor trim（seam_concat `trims[j]=float(e["trim"])`），但 `_rife_bridge` 在 trim≈0 时桥段音频复用的 atrim 切片为空 → acrossfade 失败 → 静默回退 butt-join（违背「选 RIFE」）。加守卫：trim < eps 时不复用两侧环境声、改用 anullsrc 静音桥（0.04s），保证 trim=0 仍出 RIFE 桥而非回退。
