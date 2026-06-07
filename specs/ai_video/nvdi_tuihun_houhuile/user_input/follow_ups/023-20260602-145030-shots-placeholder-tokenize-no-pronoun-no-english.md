---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/
  - .claude/agent_refs/project/ai_video.md
severity: high
---

# Follow-up draft 023 — 2026-06-02
把 prompt 里所有人物出现处全换成 `{人物拼音}_place_holder`; 禁止「他/他们」之类代词, 全换成具体人物 placeholder; prompt 里除 placeholder 外不出现其他英文单词。

## 决策 (interactive 澄清)
- 深度 = **全部彻底, 台词也换** (情节/走位/角色/动作/Summary/Characters/参考 + 台词内人名全 token 化)。
- 范围 = **ep01 全部 28 个 shot**。

## 落地
- 人物 → placeholder: 太监→`taijian_place_holder`, 陈国公→`chenguogong_place_holder`, 陈凡→`chenfan_place_holder` (保护地名 `陈国公府` 不动)。`参考:` 人物条目收拢 `{名}：place_holder`→`{拼音}_place_holder`。
- 代词/称谓 → placeholder: 他/他们/其/二人/老臣(指代)/老国公/老人/为人父者/纨绔(指代)/三公子(叙事指代)/这位/老奴/父亲/令郎/儿子 → 对应人物 placeholder (逐 shot 按语境定指, 避开 他人/其他/国公府)。
- 英文 → 中文: cinematic→电影感, photorealism→照片级写实, 4K HDR→超高清高动态范围, OS/V.O.→画外音/旁白, fast-cut→快切, reverse-POV→反打视角, reveal/motif→反转/母题, face-differentiator→面部辨识特征, mm/cm/s→毫米/厘米/秒, anime/cartoon/illustration/manga/painterly stylization/over-airbrushed/bokeh/HDR/PNG 等全译。
- **保留 (判断)**: 形容/比喻称谓 (老臣沉稳/老练阴柔=气质描述)、成语 (判若两人)、指物 (二物/二者)、台词内正式称呼「{府}三公子」与圣旨措辞 (用户「台词也换」仅指人名 token, 称呼/措辞保留, 同用户给的预览)、朕/女帝 (画外权威·无参考图, 不 token)、场景 plate 代码 (bg1_…)、地名陈国公府、Shot context/frontmatter/标题等模板脚手架 (不粘贴进模型)。

## 抽象规则 (common → ai_video.md)
shot 生成块可选「人物全 placeholder 化 + 零英文」: 所有人物指代→{拼音}_place_holder, 英文全译中文; 形容用称谓/成语/物指/plate代码/地名/模板脚手架为例外; token 化须保护地名、避开他人/其他。
