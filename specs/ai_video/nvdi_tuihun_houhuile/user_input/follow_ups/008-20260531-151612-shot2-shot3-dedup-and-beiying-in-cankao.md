---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/shot02/shot02.md
  - episodes/ep01/shots/shot03/shot03.md
  - .claude/agent_refs/project/ai_video.md
  - episodes/ep01/shots/*/shot*.md
severity: medium
---

# Follow-up draft 008 — 2026-05-31
shot2/shot3 台词重复 (都含"陈国公府三公子陈凡") 去重；shot2 去掉太监背影；通用规则：所有 shot 即使背影/远景角色也须列入参考 (以便 attach 参考图)。

## 抽象指令

1. **台词去重**：shot02 与 shot03 台词都含「陈国公府三公子陈凡」。整道圣旨连续：shot01「奉天承运，女帝诏曰：」→ shot03「陈国公府三公子陈凡，纨绔放荡，不学无术，得不配位。」。shot02 是父子听旨切镜，不应重复宣旨词。修法：shot02 台词改为纯听旨切镜（不重复宣旨词，承 shot01、续于 shot03），shot03 保留完整句（对齐 chapter P3）。

2. **shot02 去太监背影**：生成视频中 shot02 又出现太监背影。按 follow-up 003，shot02 为 reverse POV、太监不入画。`负向` 加「不要 太监入画 / 不要 太监背影 / 不要 第三人入画」。

3. **背影/远景也入参考（通用规则）**：对所有 shot，只要角色在该镜画面内（哪怕仅背影 / 远景 / 侧影），就须列入 `参考` 占位（`{名}：place_holder`），以便用户 attach 背影 / 远景 参考图。turntable 是否必需不变（背影/远景可无须），但「turntable 无须」≠「参考可省」。仅纯 OS / 画外（完全不入画）才不列。写入 ai_video.md（参考行格式 + 出场角色派生规则注）。
