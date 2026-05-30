---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - .claude/agent_refs/validation/ai_video.md
  - ai_videos/feng_shou_lu/episodes/ep01/dialogue.md
  - ai_videos/feng_shou_lu/episodes/ep01/shots/
  - ai_videos/feng_shou_lu/README.md
  - ai_videos/feng_shou_lu/episodes/ep01/shotlist.md
  - ai_videos/feng_shou_lu/episodes/ep01/publish.md
severity: high
---

# Follow-up draft 011 — 2026-05-24

每 episode 必须包含三类核心文件，且 shots 目录从 `prompts/` 重命名为 `shots/`。本 follow-up 同时落地（a）共同层 rule 升级 + （b）feng_shou_lu ep01 物理补齐。

## 抽象指令

`agent_refs/project/ai_video.md` rule 2 (sub_type=novel) + rule 3 (sub_type=short) 的 per-episode 文件清单未明确锁定「纯对白文件」这一独立 artifact，且 shot prompts 文件夹命名 `prompts/` 在团队语义里偏 ai-prompt 技术词，对配音 / 操作 / 后期 / 字幕团队不直观。本 follow-up 重写两条 rule：

1. **新增 rule 12.6-B：每 episode 必须 ship `dialogue.md`** —— 纯对白文件，derived from chapter.md（同 script.md / shotlist.md 的 derive 模式），格式 `{角色名}: "{台词}" ({语气情感注释; 5-15 字})` 逐行铺陈。三类填充契约：(a) 音量 + (b) 情感 + (c) 物理特征 (声线 / 共鸣点 / 停顿位 / 唇齿动作)，1-3 类按需组合。文件位置 `ai_videos/{name}/episodes/epNN/dialogue.md` (novel) / `ai_videos/{name}/dialogue.md` (short)。系统弹窗用 `[系统]` 占位，未具名旁白用 `[旁白]`，内心 OS 用 `{角色名} (内心)`。文末 `## 本集角色发声清单` 表格列每角色台词条数 + 总字数供配音 / TTS 工时估算。Stage-6 validation：缺失 = blocker，行格式 >20% 不符 = blocker，注释少于三件套至少 1 类 = warning。

2. **`prompts/` → `shots/` rename**（rule 2 + rule 3 sub_type 双向）—— 全局重命名，含 agent_refs/project/ai_video.md + agent_refs/validation/ai_video.md 的所有 `prompts/` 路径引用（共 14 处）+ 三个 active 项目（feng_shou_lu / mozun_chongsheng / nvdi_tuihun_houhuile）下所有 `ai_videos/{name}/episodes/epNN/prompts/` folder 物理 mv 到 `shots/`，以及内部 README / shotlist / publish 中 14 处 cross-doc 路径引用同步 patch。Naming rationale: "shots" 更直观——它是"镜头"文件夹，shotNN.md 在其内；"prompts" 太技术化 (Kling / Seedream prompt 容易跟 character prompt / scene prompt 混淆)。

3. **feng_shou_lu ep01 物理补齐** —— 本轮即从 `my_novel/feng_shou_lu/chapters/0001-第一集 落雁渊.md` 抽取台词生成 `ai_videos/feng_shou_lu/episodes/ep01/dialogue.md` (27 条台词 / 11 个发声单位 / 5 段时间线对齐 chapter §1-§5)；同步 mv `prompts/` → `shots/` 并 patch shotlist.md + publish.md + README.md 的 3 处 cross-doc 路径引用。

## 不动的契约

- chapter.md 仍是 episode 的 canonical source-of-truth (rule 12.6 v2 / follow-up 006)。dialogue.md 是 derived。
- script.md / shotlist.md / shots/shotNN.md 的 derive 模式不变, 仅多加一道 dialogue.md derive。
- shotNN.md 文件本身的 schema (chapter excerpt + shot context + 视频 prompt 三段) 不变 (rule 12.6 v2)。
- 8-字段锁定描述符 / 一句话锁定 / character bible / scene bible 全部 byte-identical 不变。
- 现有 mozun_chongsheng ep01-ep05 + nvdi_tuihun_houhuile ep01 也按本 follow-up 同步 mv 到 shots/, 保持全局 rule 一致 (无 divergence note 需要)。

## 触发原因

用户原话："每一個episode要包含以下幾種文件，一個是小説原文，完整的小説，有所有詳細信息，還有一個是純對白，類似於人物A:.... 人物B:..... 對加上點語氣情感注釋。還有一組文件是shots，有一個shots folder，下面是shotNN.md,幾根現在的shot差不多，每個episode 下面都要follow這樣的structure， 把他加到spec driven規則裏面去". 用户通过多选锁定: shots/ rename + dialogue derived from chapter + ep01 本轮生成。
