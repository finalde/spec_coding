---
target_stage: 6
target_artifacts:
  - .claude/skills/ai_video__dialogue_master/
  - ai_videos/wushen_juexing/episodes/ep01/
severity: high
---

# Follow-up draft 019 — 2026-06-14

EP1 纯文本对白太浅、不像正常人说话、缺因果；建「情节对白大师」skill 审查+直接改；补主角↔系统互动。

## 抽象后的指令
1. 建 **情节对白大师 skill**（`.claude/skills/ai_video__dialogue_master/`）：站普通观众立场审每个 shot/集的情节+对白，发现浅/假/缺因果/有漏洞/系统缺互动就**当场改**。
2. 用它把 EP1 对白改深：给因果、说人话（如"裴家不养废物"→讲清"你丹田碎了修不了武、裴家以武立命、容不下废人占嫡位"）。
3. **补主角↔系统互动**：系统不能只单方面弹面板，主角要与系统有来回（发现/质疑/调侃/抉择）。

## 落地
- skill 已建（D1–D6 台词准则 + P1–P6 情节准则 + 系统互动 P4 + review→直接改 workflow）。
- EP1：S02/S03/S04/S07/S16 等浅台词改深加因果；S08/S12/S15 润；S09 扩成主角↔系统来回对话（系统绑定→主角质疑→系统给二选一→主角冷笑选②），时长 7→9s；dialogue.md/script.md 同步。
- 台词层 surgical：shot 数仍 16、锁定串/零hex 不变；总时长 94→96s（仍 ∈[85,100]）。
