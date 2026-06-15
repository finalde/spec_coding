---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/episodes/ep01/
  - ai_videos/wushen_juexing/episodes/ep02/
  - ai_videos/wushen_juexing/arc_outline.md
  - final_specs/spec.md
  - validation/
  - .claude/agent_refs/project/ai_video.md
severity: high
---

# Follow-up draft 022 — 2026-06-14

重新编排每集时长：**每集控制在 1 分半左右（~90s）；超出的内容顺延到下一集**（对白不删、不压缩）。

## 背景
follow-up 020 为加密对白把 EP1 膨胀到 136s/22 镜，与「1 分半/集」冲突。用户的解法不是删对白，而是**按 ~90s 切分、溢出顺延**。

## 抽象后的指令（common-level + project）
1. 每集 ~90s（[85,100]s / 14–18 镜）。
2. 对白密度全保留（follow-up 020 的对峙不删）。
3. 单集内容超出 ~90s → 超出的镜顺延下一集（拆在就近场景/节拍边界，重编号）。
4. 溢出段所在集可暂短（<90s/<14 镜），标「溢出段·待补」，待该集自有剧情补足。

## 落地
- EP1（136s/22 镜）按 90s 切分：EP1 = S01–S15（15 镜/90s，收在「武神觉醒系统于至暗绑定」钩子）；溢出 S16–S22 → EP2 shot01–07（46s，二选一/走出/武神躯觉醒/凌虚子末镜）。
- EP2 新建：shots 文件夹（移入并重编号 02集NN镜 / ep02 / work_unit_id）+ script/dialogue/shotlist/publish。
- arc_outline / spec FR-7(+FR-7b)/FR-9/NFR-4 / validation bounds 回到 ~90s + 溢出豁免；project ref ai_video.md 加「overflow cascades, never trim dialogue」通则。
