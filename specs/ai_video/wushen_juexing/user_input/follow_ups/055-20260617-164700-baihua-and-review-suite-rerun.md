---
target_stage: 6
target_artifacts:
  - episodes/ep01/
  - episodes/ep02/
  - casting.md
severity: medium
---

# Follow-up draft 055 — 2026-06-17

台词、小说原文与 prompt 正文一律白话文、禁古语；并用新建的全维度审查 skill 体系（review_suite）把 EP1 + EP2 全量重跑、修复存量问题。

## 指令

1. **白话铁律（项目落地）**：本剧所有 shot `台词:`、`dialogue.md`/`script.md` 台词、shot「小说原文」段与 prompt 正文里的对白/旁白，一律现代白话口语，禁文言/古语/对仗格言腔。仙侠题材也不例外——身份/年代差异只靠用词分寸、语气、称谓体现。**系统播报亦白话**（保留系统流术语：宿主/检测到/激活/武神躯/【选项】，去书面公文腔）。
2. **全维度重跑 EP1 + EP2**：用 review_suite（台词/站位朝向/运镜/动作表演/时长节奏/光线色调/整集连贯/全剧序列/机械契约 九维）逐镜逐集审查并 surgical 修复。
3. **跨集 voice_id 锁定**：同角色全剧复用同一 voice_id；权威源回填 `casting.md`。

## 已落地修复（输出已被本次直接 surgical patch）

- **白话化**：`何曾`→`哪`（EP1 shot12/裴昭，5 文件 7 处）；EP1 系统 shot04「心志触发…」/shot13「之路…即可领取」白话；EP2 系统 shot02「断绝达成/已注入体内」、shot08「初成/根基未稳」白话；EP1 shot02「除其族籍」→「把他逐出族谱」；EP2 shot01 裴昭「他日你若…放狂言」、shot03 主角「以武神之身回来」白话。
- **剧情/连贯**：EP1 起身·气场反转 beat 在 shot06→07→14 重演 → 改为只反转一次、后续承接；EP1 shot04 系统首话对齐 canonical。
- **时长节奏**：EP2 shot03 离场宣言 9s→10s + 补 1s 离场收尾 beat（缓解语速边界）。
- **跨集一致性**：系统 voice_id 统一 `SYS-gold-01`、裴昭统一 `PZ-brat-01`；`casting.md` 回填全部锁定 voice_id（含系统、凌虚子）杜绝复发。

## 备注（common-level，已落公共面、非本项目专属）

白话铁律已写入 `.claude/agent_refs/project/ai_video.md`（2026-06-16 amendment）；九维审查 skill + `review_suite` 编排 + 「任何 ep/shot 改动默认跑 suite」已写入各 SKILL.md、ai_video.md（2026-06-17 amendment）、CLAUDE.md。故本剧后续 regen 会自动套用，无需在 revised_prompt 重述规则细节。
