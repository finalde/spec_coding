# Follow-up draft 006 — 2026-06-13

打分不要按 Kling/Seedance 分模型，对 prompt 统一打分就好。

---

## 抽象指令

评分去掉模型维度：既然每条 entry 只有一个通用 prompt（model-agnostic），就对**这条 prompt 统一打分**——你 + Claude 各评一次三轴，不再每模型一行。

## 实现（已落地）

- schema：`## 实测与验证` 表去掉「模型」列，只剩 你 / Claude 两行 × 三轴 + 笔记（tools/migrate_validation_block.py 重跑，38 条）。
- 引擎 perf_score__writer.py：去模型维度，按评分者 keyed；合议=双方均达标 accept / 都评未达标 revise / 一方未评 pending。
- 端点 / 命令 / 前端面板 / perf_rate CLI / api.ts：全部去 model 参数。
- 前端面板去掉模型下拉。

## 影响

- 改 FR-16（去模型维度，对 prompt 统一打分）+ _testrig.md 评分段。
- 测试更新（6 个全过）；前端 tsc 通过。不改四维 schema / 物理动作铁律。
