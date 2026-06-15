# Validation strategy — performance_library

Run: performance_library-20260613-014942
task_type: ai_video ｜ sub_type: N/A（共享资产库）

5 个 level-specialist worker 全部 `status: complete / confidence high`。本策略合成出 stage-6 运行期验证如何对每条 entry（= 一个 work unit）施加哪些 level、各 level 的 pass/fail 判定，并记录由 `validation_mechanism` level 反馈、已回写 spec FR-11/FR-13 的 6 个设计洞（D1–D6）。

## Levels chosen

| Level | 为什么需要 | 主要可机检 / 人工 |
|---|---|---|
| **acceptance_criteria** | 每条 FR 的 Gherkin 验收门（库的契约级 pass/fail） | 混合：结构可机检，1–5 表演分人工 |
| **bdd_scenarios** | 三个角色流（建库者/验证者/消费者）+ 生命周期行为（含 per-model 不对称、强忍子类型、强度阶梯、中文校准） | 混合 |
| **schema_structure_compliance** | 布局/编号/四维 frontmatter/status/语言/≤15s/双模型存在 等机械门（SV-1..SV-9） | 全可机检（grep/parse） |
| **content_substance** | 库的实质质量门：物理动作铁律/FACS 可追溯/内敛三层/强度阶梯/零耦合/强忍子类型（C-1..C-7） | 半机检 + 人工兜底 |
| **validation_mechanism** | 校验库自身的验证回路（检验视频+双模型+1–5 门）健全性——本库的核心价值所在 | 设计规范 + 可机检判据 |

未选用的 ai_video.md 剧目级 level（15s 镜头清单原子性 rule 2 仅以"检验视频≤15s"形式保留、角色一致性 rule 3 / 双 prompt+seam rule 4 / publish rule 6 / 台词大师 rule 9）——本任务无 episodes / 角色 bible / 台词 / publish，明确不适用（spec § Out of scope 已声明，对齐 validation general.md 原则 6：每个 carve-out 已显式确认意图）。

## Per-level summary

### Acceptance criteria（12 个 FR/NFR 区 A–L 的 Gherkin）
- 物理动作铁律（FR-5）含一个裸情绪名 FAIL 用例；内敛三层（FR-7）；FACS au_ref 可追溯且 AU 号不进 body（FR-6）。
- per-model 三轴门精确编码 `≥1 模型 表演达意≥4 ∧ 情绪可识别≥4 ∧ 过火≤2` + status 转移（FR-13）。
- 自动 vs 人工显式切分：emotion-noun 黑名单、`AU\d+`-in-body、drama 专名黑名单、95% 中文阈值、双 prompt/引用锁定串字节一致 → 可机检；1–5 表演分、内敛三层结构、webapp UI → `requires_manual_walkthrough`。

### BDD scenarios（4 Feature / 20 scenario，锚定 `perf_0003 压抑隐忍·强度3·内敛·眼神`）
- 三角色流 + 专门 edge-case Feature：Kling 败/Seedance 过仍 validated 且记 passing model（4.1）；强度5 起始帧 vs 强度3 纯文本（4.2）；强忍三子类型分立（4.3）；强度1→5 同 AU 核阶梯 + 后段招募张口 AU（4.4）；中文校准未验证（4.5）；3 轮上限 + 同因熔断（2.4/2.5）；字节稳定（3.2）。
- 每 scenario 带 `[AUTO]`/`[HUMAN]`/`[AUTO+HUMAN]` 标。

### Schema/structure compliance（SV-1..SV-9，全可机检）
- 布局/folder==stem/`_emotion.md`（FR-1）；零补四位全局唯一连续编号（FR-2，gap=warning）；四维 frontmatter 枚举（FR-4）；status 枚举（FR-13）；必填 body 段（FR-9）；≥95% 中文 + 专名白名单（rule 1）；检验视频 时长≤15s（rule 2）；双模型存在 + 锁定文本块字节一致控制变量子串（FR-11/NFR-2）；`git check-ignore` 覆盖 mp4/png（NFR-3）。
- 8 项 NOT 机检项（A–H）显式下放到 content_substance / 人工：FR-5 铁律（仅弱负向 grep）、FR-6/7/8、FR-10 样例正确性、FR-13 validated 真实性 vs 分数、NFR-1 解耦、NFR-2 跨 shot 字节稳定、FR-12 webapp（→ walkthrough）、OQ-1 过火 house-style。

### Content substance（C-1..C-7，半机检）
- Blocker：C-1 裸情绪名禁用（~40 词 body-only grep，frontmatter/标题合法）、C-2b 面/眼条不可分解为 FACS 命名动作、C-3 内敛缺三层任一、C-5 零耦合(无 drama 专名)、C-7 强忍子类型签名不符。
- Warning：C-2a AU 号进 body、C-4 强度阶梯跨条不一致（按 au_ref 聚类同 情绪×风格×载体）、C-6 house-style 浮夸预烘焙。
- 每个 FACS 依赖检查锚 dossier AU 底表（惊须无 AU4 / 真笑须 AU6 / 蔑须单侧；强忍子类型 忍泪 AU17+吞咽 vs 忍怒 AU23/24+咬肌 vs 强装镇定 维持线）。必要非充分边界贯穿：grep 只抓硬违规，1–5 分与"是否好导演"是人工。

### Validation mechanism（库自身验证回路规范，stage-6 照此跑）
- §1 控制变量 11 类钉死矩阵 + canonical `_testrig.md`（已回写 FR-11）。
- §2 评分 schema（per-model × 三轴 + 模式 + 版本/日期）+ 压抑隐忍·强度3 填例 + 强制 `消费提示` 行。
- §3 通过规则压测：OR-across-models 正确但须记 passing_models；过火必 per-model 逐行判；卡线条目 2× 渲染取差（D5）；强度1 改 mode 不放宽阈值（D6）。
- §4 迭代回路：失败轴→修正动作映射、3 轮封顶、同轴同因两轮熔断、per-entry blocked 不阻塞全库、stage-6 事件流。
- §5 文本 vs 起始帧 A/B 最小可用规范（库成自身数据集，pilot 强度1与5 各一条双模式×双模型种子点）。
- §6 中文 prompt 校准前置（stage-6 第一个 work_unit，已回写 OQ-5 决议 + acceptance）。
- §7 复验节奏：大版本跳变强制复验高强度 passing_model entry；追加行不删旧行；validated 是版本绑定非永久。

## Cross-cutting concerns

- **本库无安全面、无并发、无外部输入**：标准 severity 表里 security/path-traversal/性能/a11y 行不适用；本库最高 severity 是 `blocker`（无 `critical`），因 grep 层无 security surface（schema worker 已确认）。
- **可机检 vs 人工的边界是本库验证的主轴**：结构（frontmatter 枚举、三层块在场、AU 可追溯、字节一致、status 转移、迭代计数、引用契约）= 脚本可派生；表演质量（情绪可读性、过火、起始帧保真、中文落地、阶梯自然度）= 必须人工看检验视频。后者正是 FR-13 人工验证门存在的理由——不能假装机检能替代渲染打分。
- **状态从文件派生（NFR-4 / CLAUDE.md 确定性）**：`passing_models` 由渲染表 ✓ 行 grep 派生，`validated ⟺ passing_models 非空`；无外部存储。
- **控制变量是验证有效性的命脉**：D1（光照）/D3（prompt 骨架）若不钉，"唯一变量=表演"名存实亡，所有分数失去可比性——故已升级回 FR-11 为硬常量。

## How runtime validation will use this（stage 6）

每条 entry 是一个 work unit（`work_unit_kind = performance_entry`），按以下顺序施加 level：

1. **撰写后、渲染前（纯静态门，全可机检）**：`schema_structure_compliance`（SV-1..9）+ `content_substance` 的可机检子集（C-1 铁律 grep / C-2a AU-in-body / C-5 零耦合 / C-3 内敛三层在场性 / C-7 强忍签名）。任一 blocker 未过 → 不进入渲染，先修。
2. **渲染后、打分时（人工 + 派生）**：`validation_mechanism` §2 schema 回填双模型三轴分；`acceptance_criteria` 的表演分相关门 + `content_substance` 的"是否好导演"人工兜底；派生 `passing_models`。
3. **判定**：`passing_models` 非空 ⇒ `validation.pass`；否则 `validation.issue.raised`（失败轴）→ §4 修正回路（3 轮封顶 / 同因两轮熔断 / blocked 不阻塞全库）。
4. **work_unit 顺序**：`_testrig.md` → `_calibration.md`（中文校准，stage-6 第一个 entry-render work_unit）→ 压抑隐忍各 entry。校准若触发中文警报则升级、可能回 stage-4。
5. **事件**：每 work unit emit `validation.started`（带 `pre_reading_consulted`）/ `validation.issue.raised` / `validation.pass` / `validation.requires_manual_walkthrough`（1–5 分人工门、webapp 浏览确认）/ `exec.revision.applied` / 封顶时 `pipeline.halted`（该条 blocked 语义，整库继续）。

## Promotion-preservation check

`specs/ai_video/performance_library/` 各 spec-pipeline 阶段（interview/findings/final_specs/validation）的 `promoted.md` 目前均不存在（无 pin）。一旦存在，每个 pin 必须逐字出现在该阶段重生成产物中（`parse_promoted_text` 解析、modulo whitespace 断言）；缺失 pin = `critical`、错位 = `blocker`。Stage 6（`ai_videos/_performances/` 库代码/内容）v1 不支持 promotion——本策略不为 stage-6 regen 生成此检查（对齐 validation general.md 原则 8 / ai_video.md rule 7）。

## 回写 spec 的设计洞（D1–D6，已落 FR-11/FR-13）

| # | 洞 | 严重 | 已处理 |
|---|---|---|---|
| D1 | FR-11 未钉光照（冷暖调本身演情绪） | 高 | ✅ FR-11 ⑥ 均匀中性白光 ~5200K |
| D2 | FR-11 未钉画幅 + 景别/机位具体值 | 中 | ✅ FR-11 ③④⑦ |
| D3 | FR-11 未钉 prompt 固定骨架 | 高 | ✅ FR-11 ⑧ + byte-diff 判据 |
| D4 | FR-13 未解 Seedance 过/Kling 消费盲区 | 高 | ✅ FR-13 强制 passing_models + 消费提示 + reference 渲染器提示 |
| D5 | 单次渲染方差 | 中 | ✅ FR-11 卡线 2× 渲染取差 |
| D6 | 强度1 微表情系统性卡达意 | 中 | ✅ FR-13 强度1 默认 mode=起始帧 |
