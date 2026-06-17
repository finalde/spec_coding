---
name: ai_videos__审查总编排
description: AI 短剧全维度审查总编排——按【单镜 → 整集 → 全剧】三层顺序，依次调用各专项审查 skill(机械契约/台词/站位朝向/运镜/动作表演/光线色调/剧情连贯/全剧序列)，逐个落地 surgical 修改并汇总审计。当用户说"全面审一下这集/这部剧""出片前过一遍""把所有检查跑一遍""review 一下整体"，或改完剧本/重剪某集要做收尾把关时触发。它是把分散的单项审查串成标准工序的入口——每个 ep / 每个 shot 出片前都应跑它；缺失的专项 skill 自动跳过并记录。
---

# 审查总编排（review suite）

把 AI 短剧（`ai_videos/{name}/`）的各项审查**串成一道标准工序**，按作用范围分三层、按依赖定顺序逐个调用专项 skill，每步**当场 surgical 落地修改**，最后汇总审计。目标：让"每个 ep、每个 shot 出片前过完整套审查"成为默认动作，而不是临时想起来跑哪个。

本 skill 是 CLAUDE.md「改动剧本/台词后默认连贯性 check」+「全剧序列 review」+ `ai_video.md` rule 12.4-D + `agent_refs/validation/ai_video.md` move #9 的**编排执行版**。各专项审查的准则不在这里重复，本 skill 只负责**顺序、范围、聚合、审计**。

## 何时用
- 用户说"全面审一下 / 出片前过一遍 / 把检查都跑一遍 / review 整体"。
- 写完/重剪某集后的收尾；stage-6 每个 work-unit 出片前。

## 输入
- 范围：某 shot、某集（`episodes/epNN/`）、或整个 drama（默认按用户指定；未指定且改了某集 → 该集）。
- task_id（`{task_name}-{YYYYMMDD-HHmmss}`）用于审计目录。

## 调用顺序（机械先行 → 单镜审美 → 整集 → 全剧）

按依赖排序：先把格式/契约修干净（否则审美审查在坏结构上跑无意义），再单镜审美，再跨镜整集，最后跨集全剧。**每个 shot 走完单镜层再进下一镜；整集层在全镜单镜层完成后跑；全剧层最后跑。**

**命名约定**：审美审查 = `ai_video__{维度}_master`（8 个）；机械确定性校验 = `ai_videos__格式契约`；编排 = `ai_videos__审查总编排`。

| 序 | 层 | 调用 skill | 职责 | 状态 |
|---|---|---|---|---|
| 0 | 横切 | `ai_videos__格式契约` | 字段/字幕/锁定/hex/字数/比例时长 机械校验 | ✅ |
| 1 | 单镜 | `ai_videos__台词大师` | 台词（说人话/白话/因果/信息量/声口/情绪/节奏） | ✅ |
| 2 | 单镜 | `ai_videos__站位朝向` | 站位/朝向/眼神/走位（A 别背对 B 说话、内心独白视线、防角色重复） | ✅ |
| 3 | 单镜 | `ai_videos__运镜` | 景别/角度/镜头/运镜/180°轴线/视线匹配/9:16/相邻镜不重复 | ✅ |
| 4 | 单镜 | `ai_videos__动作表演` | 动作具体配时间轴/落钩不干站/配角反应/微表情/四层密度 | ✅ |
| 5 | 单镜 | `ai_videos__时长节奏` | 时长合理性裁决：台词念得完/动作演得开/不赶不拖（台词+动作 settled 后做时长仲裁） | ✅ |
| 6 | 单镜 | `ai_videos__光线色调` | 光线色调随情绪/场景一致/色彩锁定/回忆滤镜/眼不发光 | ✅ |
| 7 | 整集 | `ai_videos__剧情连贯` | 情节链/动机/爽点落地/系统互动 + 相邻镜衔接 + 跨镜重复 + 本集专名时序 | ✅ |
| 8 | 全剧 | `ai_videos__全剧序列` | 跨集查重宣告/签名台词/开场结尾 + 爽点递进 + 跨集专名 + 锁定/voice_id 叙事一致 | ✅ |

**缺失 skill 的处置（无声 fallback 禁止）**：某专项 skill 尚未建成时，**不静默跳过**——在最终报告里显式记 `跳过：{skill}（未建成），该维度未审`。绝不假装某维度已审。（当前全 9 项已建成。）

## 工作流
1. **定范围 + 建审计**：确定 shot/ep/drama；在 `.audit/adhoc_agents/{date}/{task_id}/events.jsonl` 写本轮起始事件，记 `pre_reading_consulted`（读过的 playbook/ref，含 sha256）。
2. **逐层调用**：按上表 0→7 调用各 skill；每个 shot 先走单镜层（0–5）全部，再进下一镜；全镜完成后跑整集层（6），最后全剧层（7）。
3. **每步落地**：各专项 skill 自身 surgical 改并三处同步（shot `台词:`/`走位:`/`镜头:` 等 + `dialogue.md` + `script.md`）。本编排负责**承接其 patch 列表**、确认已落地。
4. **冲突仲裁**：若两个 skill 对同一字段给出矛盾 patch（如 camera 要"偏头反打" vs blocking 要"正脸不背对"），**以 blocking/朝向硬约束优先**（防"对空气/背对说话"是底线），并记仲裁。
5. **聚合审计**：每个 shot/ep 一条 `validation.started`（levels=跑过的维度列表）；每个不合格项一条 `validation.issue.raised`（level=维度、severity、patch）；全清则 `validation.pass`，否则按 CLAUDE.md 迭代上限（默认 3 轮）处理，超限 `pipeline.halted`。
6. **复验**：shot 数 / 锁定串 / 零 hex / 比例 不被审美层破坏；blocker 清零；输出每 shot/ep 的维度通过矩阵。

## 硬约束
- **顺序不可乱**：机械契约（0）必须先跑——在缺字段/带字幕的坏结构上跑审美审查浪费且易误判。
- **不重复准则**：各维度判定标准只存在于对应专项 skill / ref，本编排引用不复制；准则漂移在专项 skill 改，不在这里改。
- **审计是唯一状态面**：审查结论写 `.audit` 的 events.jsonl，**不**往 shot 文件里塞"review 状态"字段（CLAUDE.md：状态从文件系统派生、审计进 .audit）。
- 迭代上限、circuit-break、`pipeline.halted` 遵 CLAUDE.md § Iteration bounds。

## 接入点（让它成为"每个 ep/shot 的一部分"）
- **stage-6 validation level #9**：由"短剧故事+台词大师"扩为调用本 suite，每个 shot/ep 出片前必过。
- **CLAUDE.md 连贯性 amendment**：改剧本/台词后的默认自检 = 跑本 suite（而非只跑台词）。
- **12.4-D**：D/S 准则拆进各专项 skill 后，12.4-D 退化为指向本 suite 与各 skill 的索引。

## 输出
- 维度通过矩阵（每 shot/ep × 各维度 = pass / patched / 跳过）+ 全部已落地 patch 汇总 + blocker/warning 计数 + 一句话总结论 + 审计事件落点。
