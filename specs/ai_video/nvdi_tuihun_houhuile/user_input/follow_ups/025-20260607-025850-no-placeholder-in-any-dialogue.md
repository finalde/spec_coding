---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 025 — 2026-06-07
确保所有 prompt 的台词里不要有 place_holder; place_holder 应只出现在台词以外的部分。

## 决策 / 范围扩展
024 只清了 `台词:` 字段。但「对白」也会**被引用在 `情节:` / `动作:` 的引号内**（同一句台词），那些引号内也残留了 placeholder (FU023 token 化时连引号内对白一起换了)。本轮把判定明确为: **引号内(对白) = 自然人名/代词; 引号外(叙述/描述) = placeholder**。

## 落地 (全 28 shot)
- 还原 `情节:` / `动作:` **引号内对白** 的 placeholder → 自然 (匹配台词字段): shot03 "三公子陈凡", shot05 "今解除朕与其之婚约"(情节+动作), shot07 "陈凡，接旨吧", shot09 "陈凡接旨", shot10 "哼。陈国公，因为令郎…", shot12 "就不用老奴说了吧", shot13 "老臣明白。老陈……", shot19 "凡……儿？", shot20 "父亲，"。
- 引号外的叙述/描述 placeholder **保留不动** (角色/走位/参考/情节叙述/动作叙述/Summary/Characters)。

## 核查
- 对白引号内 (“…”/《…》/「…」/"…") place_holder = 0 (全 28 shot)。
- 台词字段 place_holder = 0。
- 非台词描述层 placeholder 保留 (共 621 处)。

## 规则 (ai_video.md)
024 例外首条扩展: 一切「对白」(含嵌在情节/动作引号内的) 不 placeholder 化; 引号内=自然, 引号外=placeholder。
