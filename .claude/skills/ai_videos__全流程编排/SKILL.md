---
name: ai_videos__全流程编排
description: AI 短剧全链路生产流程总编排（脑洞→立项→世界观人设→分集大纲→文学剧本→分镜运镜→标准化分镜Prompt）。当用户要做/开始/继续一部 AI 短剧、微短剧、竖屏剧、古风/仙侠/复仇短剧，或说"立项/写世界观/写人设/写大纲/写剧本/做分镜/出 prompt/做短剧"时触发。它按六阶段走、每阶段先用多选题问你再生成、每阶段强制过 QC 关卡(对应审查 skill)才进下一步、每次改动默认复核、并随你反馈不断进化。本期产出到标准化 AI 分镜 Prompt 即止(渲染剪辑暂不做)。task_type=ai_video 走本流程，取代 agent_team。
---

# AI 短剧全流程编排（ai_videos__全流程编排）

把一部 AI 短剧从脑洞走到**标准化 AI 分镜 Prompt**，分**六阶段**，每阶段先问你、再生成、再过 QC 关卡。是 `task_type=ai_video` 的唯一入口，取代 agent_team（仅视频侧）。完整设计见同目录 `BLUEPRINT.md`；各阶段细则见 `playbooks/ai_videos__stageN_*.md`；输出规则见 `agent_refs/project/ai_video.md`。

## 何时用
- 用户要做/开始/继续一部短剧；说"立项/世界观/人设/大纲/剧本/分镜/出 prompt/做短剧"。
- 恢复某个半成品短剧（从文件系统判断进度续跑）。

## 六阶段（本期 1–6，出 prompt 即止；阶段 7 渲染剪辑暂不做）
| # | 阶段 | playbook | 产物落点 | QC 关卡（审查 skill） |
|---|---|---|---|---|
| 1 | 核心创意立项 | `ai_videos__stage1_立项` | `ai_videos/{name}/1_立项/concept.md` | 人工确认 |
| 2 | 世界观+锁定人设 | `ai_videos__stage2_世界观人设` | `2_世界观人设/{world.md, characters/, scenes/, casting.md, style_guide.md}` | `ai_videos__格式契约` |
| 3 | 分集大纲 | `ai_videos__stage3_大纲` | `3_大纲/arc_outline.md` | `ai_videos__剧情连贯` + `ai_videos__全剧序列` |
| 4 | 文学剧本(台词) | `ai_videos__stage4_剧本` | `4_剧本/episodes/epNN/{script.md, dialogue.md}` | `ai_videos__台词大师` |
| 5 | 分镜运镜设计 | `ai_videos__stage5_分镜` | `5_6_分镜与prompt/episodes/epNN/{shotlist.md, shots/shotNN/shotNN.md}` | `ai_videos__站位朝向`+`ai_videos__运镜`+`ai_videos__动作表演`+`ai_videos__光线色调`+`ai_videos__时长节奏` |
| 6 | 标准化分镜 Prompt | `ai_videos__stage6_prompt` | 各 `shotNN.md` 五层 prompt + `台词配音` + `all_shot_prompts.md` | `ai_videos__格式契约` + 出片前全 `ai_videos__审查总编排` |

> 阶段 5、6 产物**合一在 shotNN.md**（先写运镜设计、再校五层 prompt 契约）。

## 每阶段执行循环（interactive 默认）
1. **读**：该阶段 playbook + 上游产物 + `agent_refs/project/ai_video.md` + 相关审查 skill 准则。
2. **问**：用 `AskUserQuestion`（多选题）问该阶段 playbook 的「内建提问清单」（重要阶段多问、多角度）；用户可说"这段自动"跳过提问。
3. **做**：用答案 + 锁定的全局默认（见 BLUEPRINT §4）生成该阶段产物，落固定阶段目录。
4. **审**：跑该阶段 QC 关卡（对应审查 skill）；**blocker 清零才进下一步**（严格度=严）。不过则回修。
5. **续**：进下一阶段；状态从文件系统派生（阶段目录里产物在=该阶段 done），支持断点续。

## 三大机制（贯穿，务必执行）
1. **每步 QC 关卡**：每阶段末强制过审，blocker 清零方可进下一步。
2. **每次 update 复核**：任何对已有产物的改动/重生，默认跑受影响范围的 `ai_videos__审查总编排` + 在 `specs/ai_video/{name}/changelog.md` 记一条（沿用 ai_video.md 2026-06-17 amendment，扩到"每次 update"）。
3. **反馈→进化**：用户每条实战反馈 → surgical 更新对应 playbook / 审查 skill / `agent_refs` + 记一条"教训"（带来源镜号/反馈引用）。落点=审查 skill 准则表 + agent_refs。**流程越用越强**。

## 锁定的全局默认（节选，全表见 BLUEPRINT §4）
古风仙侠复仇为首要赛道 · 单集 90–120s · 篇幅自适应 · 9:16 多平台(红果/抖音/海外) · **藏锋·无外放** · 人设面部+服化+声口全锁 · 起承转钩四段 · 强口语白话/OS仅关键 · 鎏金极简系统 UI · 三声线解耦后期 mux · 情绪→运镜映射 · 单镜 3–15s 按 beat · Seedance+Kling · 影视写实仙侠 · **负面词块必填** · prompt 零字幕后期加 · 锁定描述符+voice_id+Seedream ref图+turntable · 多角色同框同角色只具名一次。

## 项目文件夹结构（阶段编号目录，一眼看出属于哪步）
```
ai_videos/{name}/
├── 1_立项/concept.md
├── 2_世界观人设/{world.md, characters/, scenes/, casting.md, style_guide.md}
├── 3_大纲/arc_outline.md
├── 4_剧本/episodes/epNN/{script.md, dialogue.md}
└── 5_6_分镜与prompt/episodes/epNN/{shotlist.md, shots/shotNN/shotNN.md, all_shot_prompts.md}
```
新项目默认用此结构；已有项目（如 wushen_juexing）保留原结构、可选迁移、不强制。

## 硬约束
- 本期范围阶段 1–6；阶段 7（渲染+剪辑）暂不做。
- 审计写 `.audit/adhoc_agents/{date}/{task_id}/`（沿用 CLAUDE.md 契约）。
- 不静默跳过 QC；缺失 skill 显式记录。
