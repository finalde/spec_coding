---
worker_id: level-specialist-01-acceptance_criteria
stage: 5
role: level-specialist
level: acceptance_criteria
status: complete
blockers: []
confidence: high
---

# 验收准则 — performance_library（`_performances/` 表演演技库）

Run: performance_library-20260613-014942 ｜ level: acceptance_criteria

本文件以 Gherkin（Given/When/Then）写出 stage-6 产出的验收场景，一条对应一个主流程 / 关键 FR。每条标注 **自动可测**（grep/parse 可判定）还是 **人工判定**（1–5 演技分等固有主观项）。严重度对齐 `agent_refs/validation/general.md` 标准策略：验收准则失败 = `blocker`；语言 / 15s 原子性 = `ai_video.md` 升级表里的 `blocker`；演技分等主观项 → `validation.requires_manual_walkthrough`。

约定：`{root}` = `ai_videos/_performances/`；`entry` = 一条 `{root}/{emotion}/perf_NNNN/perf_NNNN.md`。

---

## A. 库结构与全局编号（FR-1, FR-2）

### Scenario A1 — 库根三级布局成立
```gherkin
Given stage 6 已运行
When 检查 ai_videos/ 下的顶层目录
Then 存在 _performances/ 目录，与 _actors/ / _voices/ 同级（下划线前缀共享资产库）
And 其下每个 {emotion}/ 目录含一个 _emotion.md
And 每条 entry 位于 _performances/{emotion}/perf_NNNN/perf_NNNN.md（folder-per-entry，与 _actors/actor_NNNN/ 同构）
```
自动可测：glob `{root}/*/perf_*/perf_*.md` 校验三级深度；每个 `{emotion}/` 须含 `_emotion.md`。

### Scenario A2 — perf 编号全局连续、零补四位、不随情绪重置
```gherkin
Given 库内存在多条 entry，可能跨多个 emotion 目录
When 收集所有 perf_NNNN 文件夹名并按目录树排序
Then 每个编号匹配正则 ^perf_\d{4}$（恰好四位、零补）
And 编号全局唯一（无重复）
And 同一编号在 frontmatter 标题与文件夹名一致（folder perf_0007 ↔ # perf_0007）
And 编号不随 emotion 目录重置（即换情绪目录后不从 0001 重新计数）
```
自动可测：grep 文件夹名 + 解析；唯一性 = `sort | uniq -d` 为空；folder↔标题一致性 parse。

### Scenario A3 — `_emotion.md` 含情绪定义、功能主轴、entry 清单
```gherkin
Given 一个 emotion 目录 {root}/yayi_yinren/
When 打开其 _emotion.md
Then 含中文情绪名（如「压抑隐忍」）、功能主轴标注（如 痛感）
And 含该情绪下所有 perf_NNNN 的清单
And 清单与该目录下实际存在的 perf_NNNN 文件夹一一对应（无悬挂、无遗漏）
```
自动可测：清单 perf 编号 ⊆ 实际文件夹集合且反向相等。情绪定义文字质量 = 人工。

### Scenario A4 — 渲染产物 gitignored，git 只追 markdown（FR-1, NFR-3）
```gherkin
Given entry 文件夹可含 perf_NNNN__kling.mp4 / __seedance.mp4 / __startframe.png
When 检查 .gitignore 与 git ls-files
Then *.mp4 / 起始帧 *.png 等渲染产物被 .gitignore 覆盖、不被 git 追踪
And git 追踪的仅为 *.md（entry + _emotion.md + README）
```
自动可测：`git check-ignore` mp4/png 路径；`git ls-files {root}` 仅返回 `.md`。

---

## B. 四维 frontmatter 完整性 + status 枚举（FR-4, FR-13）

### Scenario B1 — 四维必填字段齐备且取值合法
```gherkin
Given 任意一条 entry
When 解析其 YAML frontmatter
Then 必含 emotion（10 情绪 seed 之一）
And 必含 intensity（整数 1–5）
And 必含 style ∈ {内敛压抑, 外放爆发}
And 必含 carrier ∈ {面部, 眼神, 肢体, 呼吸, 复合}
And 选填字段若出现则合法：lma_tag / mffr ∈ {Molding,Flowing,Flying,Radiating} / stance ∈ {反派,主角}
```
自动可测：parse frontmatter + 枚举校验。emotion 须在 README 声明的 seed 集合内。

### Scenario B2 — status 枚举合法
```gherkin
Given 任意一条 entry
When 读取 frontmatter status 字段
Then status ∈ {draft, pending_review, validated, needs_revision}
And 不存在缺失 status 的 entry（NFR-4：状态从文件派生）
```
自动可测：grep `^status:` 全覆盖 + 枚举校验。

### Scenario B3 — 标题格式咬合四维
```gherkin
Given 任意一条 entry
When 读取首行 H1 标题
Then 匹配 # perf_NNNN · {情绪}·强度{N}·{风格}·{载体}
And 标题里的 强度N / 风格 / 载体 与 frontmatter 的 intensity / style / carrier 一致
```
自动可测：正则 + frontmatter 交叉比对。

---

## C. 物理动作铁律（FR-5）— 全库首要校验项

### Scenario C1 — 锁定文本块出现裸情绪名作表演描述 → FAIL
```gherkin
Given 一条 entry，其 ## 锁定文本块 内容为待测表演串
When validator 扫描锁定文本块正文（不含标题、不含 frontmatter emotion 索引键）
And 该正文把一个裸情绪名（如「悲伤」「愤怒」「表现悲伤」「显得很生气」）当作表演描述
Then 该 entry 判 FAIL（blocker）
And 失败信息引用违规词并提示改写为可观察物理动作 + 主动动词
```
自动可测（高价值）：维护裸情绪名黑名单（悲伤/愤怒/恐惧/惊讶/开心/厌恶/痛苦/绝望/喜悦…及「表现X」「显得X」「感到X」模板）；grep 锁定文本块正文命中即 FAIL。情绪名仅允许出现在 frontmatter `emotion` 键与 H1 标题。

### Scenario C2 — 合规锁定文本块（正例）PASS
```gherkin
Given 一条 entry，锁定文本块为「眉内角上提、嘴角下拉抿紧、屏息后喉头一动」
When validator 扫描
Then 通过：每个分句是可观察肌肉/肢体动作 + 主动动词，无裸情绪名
```
自动可测（黑名单未命中）+ 人工抽检「是否真为可观察动作」（动词性主观项）。

### Scenario C3 — 锁定文本块非空且可逐字嵌入 shot 字段
```gherkin
Given 任意一条 entry
When 读取 ## 锁定文本块
Then 块非空、为纯中文 physical-action 串、不含剧目专有名词（见 J 区 NFR-1）
And 该串可原样粘入 shot 的 动作: / 表情: 字段（无需改写的占位符/模板变量）
```
自动可测：非空 + 无 `{...}` 占位 + 黑名单（NFR-1）。

---

## D. 内敛 = 三层模型（FR-7）

### Scenario D1 — 内敛压抑 entry 含三层
```gherkin
Given 一条 style=内敛压抑 的 entry（如 压抑隐忍·强忍泪水）
When 检视其锁定文本块
Then 含 ① 泄漏的真情绪 AU（低强度/单区，如「眉内角微提、眼眶湿润」）
And 含 ② 可见抑制肌（如「双唇收紧相压 / 下巴上推抗住嘴角 / 吞咽 / 控制下颌」）
And 含 ③ 上下脸冲突（眼/眉泄漏而嘴强行平复）
And 眼神被作为最高信号载体优先泄漏
```
半自动：可 grep 抑制肌关键词（收紧/相压/抗住/吞咽/控制下颌）确认 ② 存在；三层的"真有上下脸冲突结构" = 人工判定。

### Scenario D2 — 内敛不是外放的弱化版
```gherkin
Given 同一情绪的 内敛 与 外放 entry
When 对比两条锁定文本块
Then 内敛条独有抑制肌层 + 上下脸冲突描述，而非仅把外放条的动作幅度调小
```
人工判定（结构性差异，非词频）。

### Scenario D3 — 强忍按子类型分立 entry
```gherkin
Given 压抑隐忍情绪下的强忍类 entry
When 枚举
Then 强忍泪水 / 强压怒火 / 强装镇定 各为独立 entry（抑制肌签名不同）
And 不存在把三种强忍混写进同一条的情况
```
自动可测：标题/frontmatter 子类标签可区分；签名差异 = 人工。

---

## E. FACS 可追溯（FR-6）

### Scenario E1 — 面部/眼神 entry 有 au_ref metadata
```gherkin
Given 一条 carrier ∈ {面部, 眼神} 的 entry
When 解析 frontmatter
Then 含 au_ref 字段，列出该表演对应的 AU 编号（如 au_ref: [AU1, AU4, AU15]）
And au_ref 的 AU 组合与 dossier 物理动作底表中该情绪的规范组合一致（可追溯）
```
自动可测：carrier∈{面部,眼神} → 必有 `au_ref`；AU 组合对照底表 = 半自动（底表为参考表）。

### Scenario E2 — AU 编号不出现在 prompt body
```gherkin
Given 同一条面部/眼神 entry
When 扫描 ## 锁定文本块 / ## 检验视频 等会进入 prompt 的正文
Then 不出现任何 "AU\d+" 字样（模型读中文画面，不读 AU12）
And AU 编号只存在于 frontmatter au_ref
```
自动可测（高价值）：grep 正则 `AU\s*\d+` 命中 prompt body 即 FAIL；仅允许在 frontmatter。

---

## F. 控制变量检验视频 prompt（FR-11）

### Scenario F1 — 每条 entry 含双模型控制变量 prompt
```gherkin
Given 任意一条 entry
When 读取 ## 检验视频
Then 含 Kling 版与 Seedance 版两个生成 prompt
And 固定测试演员（指定 _actors/actor_NNNN，全库统一少数中性演员之一）
And 固定中性场景、固定景别+机位、固定时长（统一，如 5s）
And 唯一变量是本 entry 的锁定文本块（该串字节一致地出现在两版里）
```
自动可测：检验视频块含 Kling+Seedance 两段；actor 引用匹配 `_actors/actor_\d{4}`；锁定文本块串在 Kling 版与 Seedance 版中 byte-identical（diff 仅模型适配措辞，表演描述部分一致）。"演员/场景/机位/时长固定到全库统一" = 半自动（跨 entry 比对统一锚点）。

### Scenario F2 — 双版差异仅为模型适配
```gherkin
Given 一条 entry 的 Kling 版与 Seedance 版 prompt
When 对齐两版的表演描述字段
Then 表演描述（锁定文本块嵌入部分）字节一致
And 仅模型适配性措辞（如各模型的语法/字段习惯）不同
```
半自动：抽取表演描述子串比对一致；模型适配差异合理性 = 人工。

### Scenario F3 — 检验视频时长 ≤ 15s 原子性（ai_video validation ref rule 2）
```gherkin
Given 一条 entry 的检验视频 prompt
When 读取其时长字段
Then 时长 ≤ 15s（库统一建议 5s）且字段存在
And 不存在缺失时长或 > 15s 的检验视频
```
自动可测：parse 时长；缺失或 >15s = `blocker`（对齐 ai_video.md rule 2）。

---

## G. 验证门（FR-13）

### Scenario G1 — per-model 三轴分数齐备
```gherkin
Given 一条 status=validated 或 pending_review 的 entry
When 读取 ## 实测与验证
Then 记录了 Kling 与 Seedance 各自的三轴分数：表演达意(1–5) / 情绪可识别(1–5) / 是否过火(1–5)
And 过火按模型分别记（不合并成单一值）
And 记录了使用模式 ∈ {纯文本, 起始帧}
And 记录了验证所用模型版本/日期（NFR-5）
```
自动可测：parse 实测块的 per-model 三轴字段齐全 + 数值范围 1–5。

### Scenario G2 — 通过判定规则正确执行
```gherkin
Given 一条 entry 的 per-model 三轴分数
When 应用通过规则：至少一个模型满足 表演达意≥4 且 情绪可识别≥4 且 是否过火≤2
Then 若满足 → status 允许置 validated 且记录"哪个模型通过"
And 若不满足 → status 必须为 needs_revision（不得标 validated）
```
自动可测（规则判定）：解析分数 + status，交叉验证一致性。**分数本身是人工打分**（1–5 演技评分固有主观）→ 渲染+打分环节 `validation.requires_manual_walkthrough`。

### Scenario G3 — status 转换与迭代上限
```gherkin
Given 一条未达标 entry
When 触发修正迭代
Then status 经 draft → pending_review →（达标 validated / 不达标 needs_revision）
And 单条 entry 修正 ≤ 3 轮（CLAUDE.md 迭代上限）；超限 → pipeline.halted 上报
```
自动可测：status 枚举 + 迭代轮次受 3 轮封顶（审计 events.jsonl 计数）。

### Scenario G4 — pilot 验证回填 ≥3 条 validated
```gherkin
Given pilot 情绪「压抑隐忍」
When 统计该情绪下 status=validated 的 entry
Then ≥ 3 条，且每条 ## 实测与验证 已回填真实 per-model 分数 + 笔记（非占位）
```
自动可测：grep `status: validated` 计数；分数非占位 = 半自动（数值存在）+ 人工（分数真实性）。

---

## H. 引用契约样例（FR-10）

### Scenario H1 — 至少一个完整 entry→shot 引用样例
```gherkin
Given spec 要求至少 1 个完整引用样例
When 查找库内/spec 内的引用样例文件
Then 存在一个样例 shot 代码块
And 其顶部含 reference-handle 头一行：表演请参考: _performances/perf_NNNN（对齐 <char>请参考: 约定）
And 该 perf_NNNN 是一条 validated entry
And 该 entry 的 ## 锁定文本块 内容逐字嵌入样例 shot 的 动作: / 表情: 字段
```
自动可测：样例含 `表演请参考: _performances/perf_\d{4}` 头；被引 entry status=validated；锁定文本块串在样例 shot 字段中 byte-identical 出现。

### Scenario H2 — 锁定串字节稳定（NFR-2）
```gherkin
Given 一条 validated entry 被多处 shot 引用
When 对比各引用处嵌入的锁定文本块串
Then 跨所有引用 byte-identical（modulo whitespace）
And 任何修订都升 entry 或显式记 divergence note，不静默改字节
```
自动可测：跨引用 diff（v1 引用样例数有限，至少校验样例与源 entry 一致）。

---

## I. webapp 最小集成（FR-12）

### Scenario I1 — `_performances/` 在 sidebar 可见且可浏览
```gherkin
Given ai_video_management webapp 已加载 _performances/ 集成改动
When 用户打开 webapp sidebar
Then _performances/ 作为新顶层资产目录出现（EXPOSED_TREE / extractDramaAssets 识别）
And 可下钻到 {emotion}/perf_NNNN/perf_NNNN.md 并只读浏览 entry markdown
And 可浏览检验视频（若 mp4 存在）
And 不出现结构化编辑器 / ✨推荐 / promote 入口（v1 明确不做）
```
自动可测部分：EXPOSED_TREE/extractDramaAssets 含 `_performances` 的代码改动（grep webapp 源）。**sidebar 实际可见 + 可浏览 = 人工 walkthrough**（UI 行为）→ `validation.requires_manual_walkthrough`。

---

## J. 跨剧目零耦合（NFR-1）

### Scenario J1 — entry body 不含剧目专有名词
```gherkin
Given 任意一条 entry 的全部正文（锁定文本块 + 配套镜头 + 检验视频 + 实测笔记）
When 扫描专有名词黑名单
Then 不出现三部既有剧的角色名/场景名/剧名（feng_shou_lu / mozun_chongsheng / nvdi_tuihun_houhuile 及其中文角色名）
And 不出现任何具体剧目语境的 generic-违例词
```
自动可测（高价值）：维护剧目专有名词黑名单，grep entry 全文命中即 FAIL（NFR-1 = generic 资产硬约束）。

---

## K. 语言合规（ai_video validation ref rule 1）

### Scenario K1 — entry / README 内容中文，路径英文/拼音
```gherkin
Given _performances/ 下所有 *.md
When 剥离 code fence / YAML frontmatter / 裸 URL 后统计正文
Then 剩余正文 ≥95% 为中文块字符（汉字 + 全角标点）
And 路径/文件夹名为英文/拼音（_performances, yayi_yinren, perf_0007 等）—— 此为豁免项
And 允许的英文专有名词：Kling / Seedance / Seedream / AU<n>仅限frontmatter / actor_NNNN / 9:16 等不计入阈值
```
自动可测：对齐 ai_video.md rule 1 验证伪规则；<95% 中文 = `blocker`。

---

## L. 库 README 完整性（Acceptance summary 末条）

### Scenario L1 — README（中文）含所有必述要点
```gherkin
Given 库根 README
When 检视内容
Then 含 库定位、四维 schema 说明（含 FACS A–E gloss）、引用用法、验证流程、模型版本复验说明（NFR-5）
And 全文中文
```
自动可测：分节存在性（A–E gloss / 引用 / 验证 / 复验关键词 grep）+ 语言阈值。说明质量 = 人工。

---

## 自动 vs 人工 速查

| 检查 | 性质 |
|---|---|
| 三级布局 / 编号正则唯一 / gitignore（A） | 自动 |
| 四维枚举 + status 枚举 + 标题咬合（B） | 自动 |
| 裸情绪名黑名单（C1）/ AU 不进 body（E2）/ 剧目专名（J1）/ 语言阈值（K1） | 自动（高价值 grep） |
| 锁定文本块"真为可观察动作"（C2）/ 内敛三层结构（D1·D2）/ 强忍签名差异（D3） | 人工 |
| au_ref 存在性 | 自动；AU 组合贴底表 | 半自动 |
| 双版表演描述字节一致（F1·F2）/ 时长≤15s（F3） | 自动 |
| 三轴分数齐备 + 通过规则判定 + status 一致性（G1·G2·G3） | 自动（规则） |
| 1–5 演技评分本身（渲染+打分） | 人工 → requires_manual_walkthrough |
| 引用样例字节一致（H1·H2） | 自动 |
| webapp EXPOSED_TREE 改动 | 自动；sidebar 实际可见可浏览 | 人工 walkthrough |
| README 分节存在 | 自动；文字质量 | 人工 |
