---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/shots/
  - ai_videos/wushen_juexing/episodes/ep02/shots/
  - ai_videos/wushen_juexing/scenes/
  - .claude/agent_refs/project/ai_video.md
  - validation/structure_schema.md
severity: medium
---

# Follow-up draft 023 — 2026-06-14

用户发现：新生成的 shot prompt 的 `参考:` 里没有场景了——每个 shot 都应该有场景。另：如果镜头是人物近景，背景可以模糊处理。

## 根因
FU020 重生成时，回忆镜（S10–13）与末镜（凌虚子·王府外）被当成「无背景板」生成，`参考:` 只列了人物、省掉了场景——违反 rule 12.4 / 参考行格式「每个场景都要列入参考」。

## 抽象后的指令（common-level）
1. **每个 shot 必须有场景**（含回忆/一次性/室外镜）：无复用主场景的镜也要建轻量·单角度 scene 资产并在 `参考:` + `场景:` 双引用。任何 shot 的 `参考:` 缺场景 = blocker。
2. **人物近景/特写 → 背景浅景深虚化柔焦、主体清晰**；中景/全景需交代环境的镜不虚化。

## 落地
- 新建 4 个场景资产：s2_回忆书房 / s3_回忆内室 / s4_回忆庭院（夜袭夜+凉薄日两态）/ s5_王府外高地（含步骤一背景图 seed prompt、高清+精准机位、回忆镜暖黄泛旧）。
- 回忆镜 S10–13 + 末镜 ep02/S07：`参考:` 补场景 token、`场景:` 改为 `{scene} · 一句话锁定`、Reference uploads 补场景背景图。
- 18 个特写/近景镜的 `镜头:` 行追加「人物近景/特写时背景浅景深虚化柔焦、主体清晰」。
- project ref ai_video.md：加两条 dated amendment（每镜必有场景含回忆 / 近景背景虚化）。
- validation structure_schema：加 S-SHOT-SCENE-REF（blocker）+ S-SHOT-CLOSEUP-BLUR（warning）。
