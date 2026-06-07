---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/shot01/shot01.md
  - episodes/ep01/shots/shot02/shot02.md
  - episodes/ep01/shots/shot03/shot03.md
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 009 — 2026-06-01
shot prompt 自包含 (禁跨 shot 引用)；每 shot 自带台词且跨 shot 连贯不重复；画外 OS 说话人声音须入参考。

## 抽象指令（针对 shot02 台词，泛化为通用规则）

用户审阅 shot02 台词发现三个问题：

1. **禁止跨 shot 引用**：shot02 台词写了「宣旨词承 shot01「奉天承运 女帝诏曰」、续于 shot03, 本镜不重复宣旨词」——把 shot01/shot03 的信息塞进当前镜，会误导 Kling。shot prompt 正文（镜头/动作/台词等）必须**只描述本镜、自包含**，严禁「承 shotNN」「续于 shotNN」「下一镜」等跨 shot 引用。

2. **每 shot 自带台词 + 跨 shot 连贯不重复**：每个 shot 都应有自己的 `台词`（台词可由不在镜头里的人说出，如 shot02 此刻是太监画外音）。连续对白跨多 shot 时拆成**不重叠的连续片段**，跨 shot 连贯且不重复。
   - 圣旨连续拆分：shot01「奉天承运，女帝诏曰：」→ shot02（太监 OS）「陈国公府三公子陈凡，」→ shot03「纨绔放荡，不学无术，得不配位。」→ shot05「今解除朕与其之婚约。钦此。」
   - (修正上一轮 follow-up 008 把 shot02 台词清空为「本镜无新增字幕」的做法——应给本镜自己的 OS 片段，而非留空。)

3. **画外 OS 说话人声音入参考**：本集台词由太监说出，shot02 中太监虽不入镜，`参考` 仍须提示其声音参考（「声音请参考 xxx」），供用户 attach 配音参考。格式 `{角色}(画外 OS·声音请参考)：place_holder`。

## 落地

- shot02：台词改为 `太监(画外 OS 宣旨, 不入画):"陈国公府三公子陈凡，"`（自包含、本镜自己的 OS 片段，去掉 shot01/shot03 引用）；`参考` 加 `太监(画外 OS·声音请参考)：place_holder`；保留闭口指令。
- shot03：台词去掉重复的「陈国公府三公子陈凡，」，改 `太监(续宣):"纨绔放荡, 不学无术, 得不配位。"`（与 shot02 连贯不重复）。
- shot01：`镜头` 去掉「shot02 才进」跨镜引用；Summary/Characters 同步去 shot02 引用。
- ai_video.md：新增三条通用规则（① 每 shot 自带台词 + 跨 shot 连贯不重复 ② prompt 正文禁跨 shot 引用 ③ 画外 OS 说话人声音入参考）。
