---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - CLAUDE.md
  - episodes/ep01/shots/shot*.md
severity: high
---

# Follow-up draft 020 — 2026-06-14

武帝觉醒(wushen_juexing) 的 shot prompt 和别的剧（nvdi_tuihun_houhuile）差太多——之前告诉过的一些要求没 update 进 skill / CLAUDE setting / refs，导致新剧生成时丢了整层格式。

## 抽象后的指令

- nvdi 通过 follow-up 009/010/034 发展出的「导演级 + TTS-解耦」shot 模板此前只在 nvdi 项目级（034 明确"不改通用契约"），从未升级进通用 ref → 新剧 wushen 生成时缺失。**现正式升级为所有 ai_video 剧通用标准**。
- 三项决定（用户确认）：
  1. **台词配音(TTS)层 → 升级为通用标准**：每个有台词的 shot 加 `## 台词配音 prompt` 块（角色 / 音色锁定 voice_id / 情绪 / 语速 / 类型 / 台词 / 时长目标）+ `tools/mux_av.py` 音画解耦；推翻旧「v1 不生成 TTS / visuals-only」。
  2. **取消 起始帧/结束帧** 两个静帧 block（2026-05-27 强制规则作废）。
  3. **现在就重生成 wushen ep01 全部 16 镜** 到统一标准。

## 落地

1. **通用规则**：`.claude/agent_refs/project/ai_video.md` 新增 2026-06-14 amendment（canonical shot 模板 + 台词配音 TTS 层 + 面部辨识特征）；rule 12.1 配音参考段撤销「v1 不生成 TTS」改为 voice_id 锁定源；2026-05-27 起始帧/结束帧 amendment 标 ABOLISHED。`CLAUDE.md` AI-video 节同步收窄 visuals-only、记录 canonical shot 模板 + 配音层 + 帧块作废。
2. **wushen ep01 全 16 镜 regen**（stage-6 delete-then-write，4 个并行 worker）：补齐 参考头/角色锁定+面部辨识特征/情节/场景/走位(世界坐标)/比例 9:16 + 台词配音块（voice_id 锁定 PZQ-lead-01/PZ-brat-01/PT-patriarch-01/SW-consort-01/LXZ-immortal-01）；删 起始帧/结束帧/负向/场景视角锚；默剧镜(05/06/10/13/14)标 SFX 无台词。
3. 审计：`.audit/adhoc_agents/2026-06-14/wushen_juexing-20260614-191047/`（events.jsonl + 4 spawns）。

校验：16/16 shot YAML 信封/参考/角色+面部辨识/走位/情节/比例=1；起始帧/结束帧/负向/场景视角锚 残留=0。
