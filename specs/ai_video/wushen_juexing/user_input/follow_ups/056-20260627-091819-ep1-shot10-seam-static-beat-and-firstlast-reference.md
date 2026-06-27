# Follow-up draft 056 — 2026-06-27

承 055：① 按方案把 ep1 shot10 末帧由"走路中途"改成"面南立定收势"(seam 落静定 beat)、shot11 自立定起步；② 新建首尾帧 prompt 写法 reference 文件并纳入流程。

---
target_stage: 6
target_artifacts:
  - 5_6_分镜与prompt/episodes/ep01/shots/shot10/shot10.md
  - 5_6_分镜与prompt/episodes/ep01/shots/shot11/shot11.md
  - .claude/agent_refs/project/ai_video_shouweizhen.md
severity: medium
---

## 指令
1) shot10 重设计：末帧「已朝南门前行两三步(走路中途)」→「转身完成、面朝南门立定收势站定(未迈步·蓄势将起步·末段锁机位+留环境微动)」；shot11 首帧对齐到立定、动作首拍「自立定起步、不重演转身」。根治"接缝落走路中途致跳帧"。需重生 shot10（末帧变了）→ 再截首帧给 shot11。
2) 新建 `.claude/agent_refs/project/ai_video_shouweizhen.md`（首尾帧 reference，沿用 ai_video_jingbie.md 体例）：承接 vs 硬切、三种帧模式×结构化指令、九条铁律、出片端抹平、落点清单、ep1 shot10→11 正反例、归口。
3) 纳入流程：ai_video.md 承接 amendment 头 + 运镜 M8 + stage5/stage6 + 格式契约 K26 五处加引用（同 jingbie）。

## 约束 / 验证
- shotNN 视频 prompt ≤2000：shot10=1693、shot11=1848 ✓。
- all_shot_prompts.md(ep01) 同步重汇编、清残留。
- 连贯：shot10 起幅 / shot11 末帧未动，仅 shot10→11 seam 改一致。
