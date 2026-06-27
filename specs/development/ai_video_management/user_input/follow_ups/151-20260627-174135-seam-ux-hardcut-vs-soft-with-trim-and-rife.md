# Follow-up draft 151 — 2026-06-27

拼接 UI 改结构：先选 硬拼 / 不硬拼；不硬拼时 裁切 与 RIFE 可同时存在并各自调整。另：ep4 shot11→12 选硬拼出来不像硬拼（疑似 stale render）。

---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/src/components/SeamPlanModal.tsx
severity: medium
---

## 指令 1 — 拼接 UI 两级结构（SeamPlanModal）
原三互斥按钮（硬拼/裁切/RIFE）改为两级：① 主选 **硬拼 / 不硬拼**；② 选「不硬拼」时展开：**裁切秒**（始终可调，0=不裁）+ **RIFE 补帧**勾选框 + **密度**（勾 RIFE 时）。即裁切与 RIFE 在「不硬拼」下并存可调（裁切+不勾=只裁平接 method `trim`；裁切+勾=裁切+补帧 method `rife`；硬拼=method `butt`）。后端 butt/trim/rife 三态已就绪，纯前端重构 + 文案/CSS。

## 指令 2 — ep4 shot11→12 硬拼结果不对（诊断）
查证：ep4 `seam_plan.json` 中 `shot11->shot12 method=butt`（保存正确）；shot11=硬切独立首帧、shot12=承接 shot11 末帧，故该缝是**承接缝**。当前后端 butt→`{bridge:False}`=纯硬拼。结论：非代码 bug——用户看到的成片是**改成 butt 之前 / bundle 修复前的旧 render**（且此前 vite outDir 错配，前端改动从未被服务）。需重启后端 + 硬刷新 + **重新生成 ep4**。承接缝纯硬拼会保留首尾帧 ramp/重复帧（看着发软），想干净应用「不硬拼+裁切」。
