# Validation strategy — mozun_chongsheng

Run: mozun_chongsheng-20260509-164205
Stage: 5
Mode: AUTONOMOUS
Coordination: parent-direct (workers consolidated)

## Levels chosen

| Level | File | Why |
|---|---|---|
| Acceptance criteria | `acceptance_criteria.md` | 10 个 AC 锁定 spec 的对外契约（Gherkin） |
| BDD scenarios | `bdd_scenarios.md` | 11 个 Feature 验证 stage 6 输出的叙事 / 视觉 / 节奏行为 |
| AI-video specific | `ai_video_specific.md` | 8 个强制 level（per agent_refs/validation/ai_video.md），是本 task_type 的合规地基 |

**未启用** levels: unit_tests / system_tests / performance / security / accessibility — 本项目仅产出文本 prompt 文件，无运行时 / 网络 / 用户输入路径，安全 / 性能 / 可访问性维度不适用。

## Per-level summary

### Acceptance criteria（10 个 AC，Gherkin）

- **AC-1 语言合规**：所有 .md 中文 ≥95%（blocker）
- **AC-2 镜头原子性**：每镜 ≤15s（blocker）
- **AC-3 角色一致性**：同集内 byte-identical 描述符（blocker）
- **AC-4 双管线完整**：每镜含 Kling+Seedance+lastframe；每集首镜含 startframe（blocker）
- **AC-5 比例+规避词**：每镜含 9:16；Seedance 含"避免:"段（blocker）
- **AC-6 Publish 完整**：抖音 + YouTube Shorts 双套元数据（blocker）
- **AC-7 10 份立绘齐备**：9 角色 + 男主双形态（blocker）
- **AC-8 角色声明前置**：shot prompt 引用必须在 characters/ 已声明（blocker）
- **AC-9 arc_outline 完整**：60 集 + 6 卷（blocker）
- **AC-10 手动走查**：自动 level 全 pass 后人工签字（manual）

### BDD scenarios（11 个 Feature）

涵盖：单集三钩节奏 / 六卷大事件 / 多女主出场节奏 / 男主修为路径 / 视觉反差 / 系统弹窗一致性 / Seam-frame 同步 / 平台合规 / ep01 开场契约 / ep60 二季钩 / 编号补零。

### AI-video specific（8 个 level）

per agent_refs/validation/ai_video.md：语言 / 15s 原子 / 角色一致 / 双管线+seam-frame / 比例+规避词 / Publish / Pinned items（v1 跳过）/ 手动走查。

## Cross-cutting concerns

### 验证粒度

| 粒度 | 触发 | 由谁执行 |
|---|---|---|
| 项目级 | stage 6 完成时 | parent runtime 验证（一次） |
| 单集（episode）work-unit | 每集 ep01-ep05 写完后 | parent 直接 / 或 spawn validator |
| 单文件 | 写文件时 | 写入端自检（可选） |

### 状态隔离 / 重置

本项目无运行时状态——所有 validation 都是静态文件检查。无 flaky 风险。

### Seedance 无 negative_prompt 字段（CC-5）

强制每镜 Seedance prompt 含"避免:"前缀的规避词列表。在 stage 6 写入时执行，stage 5 acceptance + ai_video L5 双重保障。

## How runtime validation will use this

stage 6 的每个 work unit（默认 = 一集 episode）按以下流程跑 validation：

```
work_unit_kind = "episode"
levels_to_run = [
    AC-1 (语言),
    AC-2 (15s),
    AC-3 (角色一致),
    AC-4 (双管线),
    AC-5 (比例+规避词),
    AC-6 (Publish),
    AC-8 (角色声明),
    BDD Feature 1 (三钩),
    BDD Feature 5 (视觉反差) — warning if 0 同框镜
]

if 单元 = "project_scaffold":
    levels_to_run += [AC-7 (10 份立绘), AC-9 (arc_outline)]

if 单元 = "ep60":
    levels_to_run += [BDD Feature 10 (二季钩双版本)]

# 全 pass 后
emit("validation.requires_manual_walkthrough") → AC-10
```

每 level 独立运行，issues 列表汇总。任何 blocker → halt 该 work unit；warning → log 并继续。

### 修订循环（per CLAUDE.md § Iteration bounds）

- 默认每 work unit 最多 3 轮修订
- 同一 issue_id 在两轮内未消解 → emit `pipeline.halted`
- wall clock 单 unit > 30 min → 同上

## Promotion-preservation check

当前 v1 无 `<stage>/promoted.md` 锁定项 → skip。

如果未来用户在 stage 2-5 任一阶段执行 pin 操作产生 promoted.md，则 stage 5 strategy 必须为该 stage 添加额外 level：
"每个 pin 在该 stage 重生成的 artifact 中 byte-identical 出现"。

## Severity escalations specific to mozun_chongsheng

继承 agent_refs/validation/ai_video.md 标准严重度表，加 1 个项目专属：

| Issue class | Severity | Reason |
|---|---|---|
| 整集 0 个"白衣 vs 黑袍"同框镜 | blocker | 违背项目核心反讽设定（FR-21）；本剧的视觉张力立不住 |
| 男主修为段与 ep 区间不匹配（FR-15） | blocker | 修为节奏是六卷情绪曲线锚点 |
| ep60 缺少二季钩 + 单季双版本 | blocker | FR-39 / Feature 10 要求两版本共存 |
| Kling prompt 中"动作:"字段复述 ref-image 中已有内容 | warning | CC-2 给出的最佳实践，但不至于阻断 |

## Stage 6 work unit decomposition

stage 6 应当划分为以下 work units（按 R-3 推荐）：

1. **U1 · project_scaffold** — README / world / style_guide / arc_outline + 10 份角色 .md + 10 份 ref_images Seedream
2. **U2 · ep01** — 卷一镇压开场，单集
3. **U3 · ep02-ep04** — 卷一倒叙因果（合并三集，因为节奏紧密相关）
4. **U4 · ep05** — 卷一收尾 + 转生 cliffhanger
5. **U5 · 验证 + 手动走查** — 全自动 level + manual walkthrough 入口

总计 ~5 work units（细节批次 ep01-ep05 + 项目级 + 验证）。

## Audit event protocol（stage 6 强制）

每 work unit 必发 4 个事件：

```json
{"event": "exec.unit.started", "work_unit_id": "...", "ts": "..."}
{"event": "exec.unit.completed", "work_unit_id": "...", "ts": "..."}
{"event": "validation.started", "work_unit_id": "...", "levels": [...], "ts": "..."}
{"event": "validation.pass" | "validation.issue.raised" | "validation.requires_manual_walkthrough", ...}
```

任何 issue 必发 `validation.issue.raised`；修订必发 `exec.revision.applied`。

---

> Stage 5 完成。`validation/strategy.md` + `acceptance_criteria.md` + `bdd_scenarios.md` + `ai_video_specific.md` 共 4 文件已落盘。
> 下一步：stage 6 — execution + streaming validation。
