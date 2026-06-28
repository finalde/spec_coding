# Follow-up draft 073 — 2026-06-28
台词书面/不白话反复出现——加「生成时白话 self-check」默认规则 + EP6 若干句微改

---
target_stage: 4
target_artifacts:
  - CLAUDE.md
  - 4_剧本/episodes/ep06/{script,dialogue}.md
severity: medium
---

## 问题
台词书面/公文腔/绕口反复出现（"众家新苗按序上前、按手灵石定档，不得喧哗"／"今儿这一石下去"／"半分没丢"／"是你的，跑不了"），用户已提醒多次，问如何根本避免。

## 根因
白话标准只由下游 `台词大师`/`白话大师` review 把关（生成之后），生成时没强制自检，所以书面句先被写出来、只能等审查才抓。

## 根本修复（common-level·CLAUDE.md §General coding rules）
新增默认自检（与「prompt 长度自检」「连贯性自检」同级）：**AI-video 台词白话 self-check（default, no reminder needed）**——生成或修改任何台词（script/dialogue 对白·旁白·OS、shot 台词），完成前必须**逐句朗读、确认是真人口语大白话**，无公文/唱礼/文言/书面/对仗/翻译腔；书面句不得在生成时出现、不留给下游 review；当场口语化。宗师/皇室可带少量声口 register 词、但不堆砌文言。

## EP6 微改（用户逐句）
- S4 裴昭 OS 去"今儿这一石下去/我裴昭等的就是这一下/困在武王境大半辈子"换白话。
- S5 裴昭去"半分没丢"；裴霆删"是你的，跑不了"。
