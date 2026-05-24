# Follow-up draft 030 — 2026-05-21
小说文本 @-ref header 用「中文剧名」而非 task_name pinyin，且 char/scene id 去掉 `cN_` / `sN_` 前缀，只保留纯中文名。

## 背景
follow-up 029 已经引入 `## 小说文本 / Novel prose` 段及其 `@-ref header`，但首版格式遗留两个不便人读的细节：

1. 用了项目路径用的 pinyin slug（`mozun_chongsheng`）做小说名，而项目本身是 `魔尊归来`。读散文时挂着英文 slug 显得割裂，也与"读小说"的目标体验冲突。
2. char/scene id 带着列表用的 `cN_` / `sN_` 序号前缀（如 `c1_沧冥`、`s3_铸器堂`），这层前缀只在 `## Reference placeholders` 段内做局部去重和绑图用，写进散文 header 里是冗余。

## 规则
小说文本段首行 @-ref header 改为下列格式：

`{人物1}請參考:@{小说中文名}_{人物中文名}，... {场景}請參考:@{小说中文名}_{场景中文名}`

具体到本项目：

- **小说中文名 = `魔尊归来`**，取自 `ai_videos/mozun_chongsheng/README.md` 的 H1 中文剧名；**不是** task_name pinyin slug。
- **人物 / 场景中文名** = `## Reference placeholders` 段 placeholder 的中文名部分，去掉 `cN_` / `sN_` 前缀。例：`{ref_c1_沧冥}` → header 中写 `沧冥`；`{ref_s7_山道平台}` → `山道平台`。
- 人物在前 / 场景在后，「，」分隔。
- header 后空一行，再写散文正文。

例：`沧冥請參考:@魔尊归来_沧冥，长阶顶請參考:@魔尊归来_长阶顶`

## 影响面
- 已写入的 ep01 / ep02 共 20 个 shot 的 @-ref header 改为新格式（上一轮已完成）。
- 待补的 ep03 / ep04 / ep05 共 30 个 shot 在新增 `## 小说文本 / Novel prose` 段时直接采用新格式。
- `agent_refs/project/ai_video.md` 中"小说文本 / Novel prose"模板段的 @-ref 说明改为新格式（上一轮已完成）。
- follow-up 029 文档内的示例 @-ref 同步改新格式（上一轮已完成）。
