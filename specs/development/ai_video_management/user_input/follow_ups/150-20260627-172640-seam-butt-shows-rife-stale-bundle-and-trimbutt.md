# Follow-up draft 150 — 2026-06-27

拼接：选了硬切/硬拼，出来的还是有 rife 效果。

---
target_stage: 6
target_artifacts:
  - projects/ai_video_management/apps/ui/vite.config.ts
  - projects/ai_video_management/apps/ui/vite.config.js
severity: high
---

## 根因（构建/服务路径错配 → 服务的是陈旧 bundle）
`app_factory.py` 服务 `apps/api/static/`（实为空·只有 .gitkeep），但 `vite.config.{ts,js}` 的 outDir 还指向 `apps/backend/static/`（backend→api 重构遗留）。于是每次 `npm run build` 都落到 app **不服务**的目录 → prod 模式拿到陈旧 bundle。用户此前已把 SeamPlanModal/api.ts/episode__writer 升级成**三态拼接**（硬拼 butt / 裁切平接 trim / RIFE），逻辑都对，但这些前端改动从未进入被服务的 bundle → 跑的是升级前的旧 UI，所以「硬拼仍出 rife」。Makefile `clean` 与 README 均指 `apps/api/static`，确认 vite.config 是 stale。

## 落地
- `vite.config.{ts,js}` outDir `apps/backend/static` → `apps/api/static`（app_factory 服务目录），`npm run build` 重建到该目录（index.html + assets 已落位）。
- 三态拼接（butt/trim/rife）后端 + 前端为用户并行实现、已完整正确，本 follow-up 不改其逻辑，只修构建落点让其生效。
- 遗留：`apps/backend/static/` 旧产物已不再使用（可后续清理，不影响服务）。
