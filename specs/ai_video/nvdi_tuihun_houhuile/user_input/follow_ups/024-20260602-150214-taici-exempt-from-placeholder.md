---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 024 — 2026-06-02
刚才(follow-up 023)的规则对台词都不适用: 台词不要用 placeholder, 也继续使用「他们」等代词 when needed。

## 决策
`台词:` 字段是要显示给观众/被读出的字幕文字, placeholder 会被当字幕渲染出来 → 故台词整段豁免 023 的 placeholder 化, 用自然人名 + 口语代词/称呼。其他字段 (情节/走位/角色/动作/参考/Summary/Characters) 的 placeholder 化保持不变。

## 落地 (全 28 shot, 仅 `台词:` 行)
- placeholder → 自然人名: taijian_place_holder→太监 / chenguogong_place_holder→陈国公 / chenfan_place_holder→陈凡 (说话人标签 + 台词内容 + 口型注 全部)。
- 恢复原口语代词/称呼 (023 曾 token 化的): shot05 「朕与其之婚约」(其), shot10 「因为令郎」, shot12 「就不用老奴说了吧」, shot13 「老臣明白。老陈……」, shot19 「凡……儿？」, shot20 「父亲，请罪的折子」。
- 核查: 28 shot 台词行 placeholder = 0; 其他字段 placeholder 不动。

## 规则更新 (ai_video.md)
023 规则例外清单首条改为: `台词:` 整段不 placeholder 化 —— 自然人名 + 保留口语代词/称呼; token 化时跳过台词行。
