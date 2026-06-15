---
worker_id: level-specialist-02-bdd_scenarios
stage: 5
role: level-specialist
level: bdd_scenarios
status: complete
blockers: []
confidence: high
---

# BDD scenarios — performance_library 表演演技库

Run: performance_library-20260613-014942

这些是 **feature 级行为规范**（Feature / Scenario / Given-When-Then），描述演技库在三个 actor flow 与若干边界条件下**必须表现出的行为**。与 `acceptance_criteria.md`（逐 FR 的 pass/fail 验收点）互补：本文件描述「跨生命周期的行为」，验收准则描述「单条产物的合规判定」。

**自动化 vs 人工判断标注约定**：每个 Scenario 末尾标 `[AUTO]`（可由 grep/脚本/frontmatter 派生判定，validator 无需主观）或 `[HUMAN]`（须人眼看检验视频 / 凭表演经验打分，机器无法替代）。混合的标 `[AUTO+HUMAN]`。

示例 entry 全程沿用一条具体条目：**`perf_0003 · 压抑隐忍·强度3·内敛·眼神`**（pilot 情绪「压抑隐忍」的中段、内敛、以眼神为主要载体）。

---

## Feature 1: 库建设者撰写一条 entry（四维 → 物理动作 body → 检验视频 prompt 流水线）

  作为库建设者（Claude，stage 6），
  我要把一个表演意图（情绪×强度×风格×载体）落成一条经物理动作铁律约束的 entry，
  以便它可被检验、可被任意短剧逐字引用。

  Background:
    Given 库根 `ai_videos/_performances/` 存在且布局为 `{emotion}/perf_NNNN/perf_NNNN.md`
    And 全局编号 `perf_NNNN` 连续、零补四位、不随情绪重置
    And dossier「物理动作底表」（AU→中文可见动作）与「情绪→规范 AU 组合」可用

### Scenario 1.1: 四维 frontmatter 完整且合法地开一条新 entry
    Given 我要撰写「压抑隐忍·强度3·内敛·眼神」
    When 我创建 `_performances/yayi_yinren/perf_0003/perf_0003.md`
    Then frontmatter 必须含四维全部必填字段且取自合法枚举
    And `status` 初值为 `draft`

    Examples: 四维字段合法取值
      | 字段       | 本条取值       | 合法枚举/范围                                  |
      | emotion    | 压抑隐忍       | 10 情绪 seed 之一                              |
      | intensity  | 3              | 整数 1–5（锚 FACS A–E）                        |
      | style      | 内敛压抑       | 内敛压抑 \| 外放爆发                            |
      | carrier    | 眼神           | 面部 \| 眼神 \| 肢体 \| 呼吸 \| 复合           |
      | status     | draft          | draft \| pending_review \| validated \| needs_revision |
    `[AUTO]`

### Scenario 1.2: 锁定文本块写成可观察物理动作，严禁裸情绪名（FR-5 铁律）
    Given 我在写 `## 锁定文本块`
    When body 描述表演
    Then body 只含可观察物理动作 + 主动动词（取自 AU 底表的中文画面）
    And body 中不出现任何裸情绪名作为表演描述

    Examples: 物理动作铁律正反例
      | 判定 | 文本                                                         |
      | 正例 | 视线下垂半秒后强行抬起、下睑微紧、喉头一动咽下、双唇收紧压平 |
      | 反例 | 表现压抑、眼神很悲伤、忍住情绪                                |
    And validator 可用 grep 扫裸情绪名词表（悲伤/愤怒/压抑/隐忍/委屈…作动词宾语）命中即 fail
    `[AUTO]`  *(裸情绪名黑名单可 grep；但「这段动作是否真表达了该情绪」属 1.x 之外的 HUMAN 判定，见 Feature 2)*

### Scenario 1.3: 内敛条必须含三层模型（FR-7）
    Given `style=内敛压抑`
    When 我写 body
    Then body 必须可识别地含三层，缺任一层即不合规
      | 层               | 本条（眼神）落点                          |
      | ① 泄漏的真情绪 AU | 下睑微紧 + 目光短暂下垂（悲/怒核低强度单区） |
      | ② 可见抑制肌     | 喉头吞咽 + 双唇收紧压平（AU24/23/17 类）   |
      | ③ 上下脸冲突     | 眼/眉先泄漏而嘴强行平复                    |
    And 眼神被作为内敛情绪的最高信号载体优先描写（眼睛先泄漏）
    `[AUTO+HUMAN]`  *(三层是否存在可结构化检查 [AUTO]；「眼先于嘴泄漏」的微妙是否真做到属 [HUMAN]）*

### Scenario 1.4: 面部/眼神条物理词汇可回溯到 FACS 底表（FR-6）
    Given `carrier ∈ {面部, 眼神}`
    When body 引用一个肌肉动作
    Then 该动作的中文画面来自 dossier AU 底表
    And frontmatter `au_ref:` 记录对应 AU 编号（如 AU7/AU24/AU17）
    But AU 编号绝不进 body（模型读中文画面，不读「AU24」）
    `[AUTO]`

### Scenario 1.5: 生成完全控制变量的双模型检验视频 prompt（FR-11）
    Given entry 的锁定文本块已定稿
    When 我写 `## 检验视频`
    Then prompt 固定测试演员（指定 `_actors/actor_NNNN`，全库统一中性演员）
    And 固定中性场景 + 固定景别机位 + 固定时长（如 5s）
    And 唯一变量是本 entry 的锁定文本块
    And 同时给出 Kling 版与 Seedance 版，两版表演描述字节一致（差异仅模型适配壳）
    `[AUTO]`

### Scenario 1.6: 起始帧块按强度条件出现（FR-9 / FR-1.x 高强度规则）
    Given 一条 entry
    When 强度为 5（峰值/失控张口，纯文本最易变僵）
    Then entry 必须含 `## 起始帧表情`（峰值表情静帧的 Seedream 生成 prompt，咬合 ai_video.md rule 12.4）
    But When 强度为 1–3（中段，纯文本可控带）
    Then `## 起始帧表情` 为选填，可纯文本
    `[AUTO+HUMAN]`  *(块存在性 [AUTO]；起始帧表情是否真"到位"须看渲染 [HUMAN]，见 Scenario 4.2)*

---

## Feature 2: 库验证者跑双模型控制变量测试并回填打分（检验视频 → 1–5 → 状态流转）

  作为库验证者（用户），
  我要在 Kling 与 Seedance 各渲一版控制变量视频、按三轴 1–5 打分、回填，
  以便把一条 entry 从 draft 推进到 validated，或退回 needs_revision 迭代。

  Background:
    Given 一条 `status=draft` 的 entry，其检验视频 prompt 已生成
    And 三轴评分为「表演达意 / 情绪可识别 / 是否过火」各 1–5
    And 过火轴 1=自然、5=严重过火（越低越好），库为「精品微表情」派、锚点偏严（OQ-1 已决议）
    And 验证通过判定：≥1 个模型满足「表演达意≥4 且 情绪可识别≥4 且 是否过火≤2」

### Scenario 2.1: 双模型分别渲染并按模型分别记分（过火不可合并）
    Given perf_0003 的 Kling 版与 Seedance 版检验视频均已渲出
    When 我打分
    Then 我在 `## 实测与验证` 为每个模型分别记三轴分（共 6 个分）
    And 「是否过火」按模型分别记，绝不塌缩成单一数
    And 记录使用模式（纯文本 \| 起始帧）

    Examples: 双模型 per-model 评分回填
      | 模型     | 表演达意 | 情绪可识别 | 是否过火 | 使用模式 |
      | Kling    | 4        | 4          | 3        | 纯文本   |
      | Seedance | 4        | 4          | 2        | 纯文本   |
    `[AUTO+HUMAN]`  *(分数是否齐全/格式合法 [AUTO]；打分本身是 [HUMAN])*

### Scenario 2.2: 至少一个模型达标 → status 转 validated
    Given 上表分数（Seedance: 达意4/可识别4/过火2）
    When 我应用通过判定
    Then Seedance 满足 ≥4/≥4/≤2，判定通过
    And `status` 由 `pending_review` 转 `validated`
    And 实测笔记记录「哪个模型通过」= Seedance
    And 锁定文本块自此 byte-frozen（NFR-2）
    `[AUTO]`  *(给定回填分数后，状态转移是纯函数，可脚本派生)*

### Scenario 2.3: 两模型都不达标 → status 转 needs_revision 并迭代
    Given Kling: 达意3/可识别4/过火4，Seedance: 达意3/可识别3/过火2
    When 我应用通过判定
    Then 无任一模型满足 ≥4/≥4/≤2
    And `status` 转 `needs_revision`
    And 实测笔记记录失败原因（如 Kling 过火4=过投射；Seedance 达意3=欠演不达意）
    And 触发回到 Feature 1 重撰 body
    `[AUTO+HUMAN]`

### Scenario 2.4: 修正迭代 3 轮封顶后 halt（CLAUDE.md 迭代上限）
    Given 一条 entry 已 needs_revision 并重撰
    When 修正轮次累计达到 3 轮仍未达标
    Then 不得第 4 轮静默重试
    And 发 `pipeline.halted` 事件并升级给用户
    And entry 停在 `needs_revision`，记录已用 3 轮与各轮分数轨迹

    Examples: 迭代轮次边界
      | 轮次 | 结果           | 动作                        |
      | 1    | needs_revision | 重撰 body，再验             |
      | 2    | needs_revision | 重撰 body，再验             |
      | 3    | needs_revision | 封顶：halt + 升级，停止迭代 |
    `[AUTO]`  *(轮次计数与 halt 是 [AUTO]；每轮怎么改 body 是 [HUMAN])*

### Scenario 2.5: 同一 issue 跨两轮重复 → 提前 circuit-break
    Given 第 1 轮与第 2 轮的失败 issue 相同（如两轮都「Kling 过火4」）
    When 我检测到同一 issue 跨两次迭代重复
    Then 即便未到 3 轮也提前 `pipeline.halted`（CLAUDE.md circuit-break）
    `[AUTO]`

---

## Feature 3: 库消费者把 validated entry 引用进真实 shot prompt（FR-10 / NFR-2）

  作为某未来短剧的 shot 作者，
  我要用两段式引用把一条 validated entry 接入我的 shot，
  以便取代现场即兴撰写表演描述，并保证锁定串字节稳定。

  Background:
    Given perf_0003 `status=validated`，其锁定文本块已 frozen

### Scenario 3.1: reference-handle 头 + 锁定文本块逐字嵌入
    Given 我在写一个 shot 代码块
    When 我引用 perf_0003
    Then shot 顶部加一行 reference-handle 头 `表演请参考: _performances/perf_0003`（对齐 `<char>请参考:` 约定）
    And perf_0003 的锁定文本块内容逐字嵌入该 shot 的 `动作:` / `表情:` 字段
    `[AUTO]`

### Scenario 3.2: 锁定串跨所有引用 byte-identical（NFR-2）
    Given perf_0003 被 N 个不同 shot 引用
    When 我对比每个 shot 嵌入的锁定串与 entry 源串
    Then 全部 byte-identical（含标点/空格/换行）
    And 任何引用方对锁定串的就地改写都是违规

    Examples: 字节稳定判定
      | 引用方            | 嵌入串与源串 diff | 判定 |
      | shotA            | 0 字节差           | pass |
      | shotB（改了标点）| ≥1 字节差          | fail |
    `[AUTO]`

### Scenario 3.3: 引用条必须是 validated（不可引 draft/needs_revision）
    Given perf_0007 `status=draft`
    When 某 shot 试图引用 perf_0007
    Then 该引用违规（只允许引用 validated 条）
    `[AUTO]`

### Scenario 3.4: 锁定串修订须升 entry 或显式记 divergence（NFR-2）
    Given perf_0003 已 validated 且被引用
    When 锁定串需要修改
    Then 不得就地静默改 frozen 串
    And 须升一条新 entry（新 perf_NNNN）或在 entry 内显式记 divergence note
    `[AUTO+HUMAN]`

### Scenario 3.5: 引用条零剧目耦合（NFR-1）
    Given 我把 perf_0003 嵌入一个具体剧目的 shot
    When 我检查锁定串内容
    Then 锁定串不含任何剧目专有名词/角色名/场景名（它是 generic 资产）
    `[AUTO]`

---

## Feature 4: 行为边界条件（per-model 不对称、强度阶梯、强忍子类、中文校准）

### Scenario 4.1: Kling 失败但 Seedance 通过 → 仍 validated，记录通过模型（per-model 不对称）
    Given perf_0003，Kling 偏 aggressive/theatrical（易过火），Seedance 偏 restrained/cinematic（易欠演）
    When Kling 过火=4（过投射，不达标）而 Seedance 达意4/可识别4/过火2（达标）
    Then entry 仍判 `validated`（≥1 模型达标即通过）
    And 实测笔记显式记「通过模型=Seedance；Kling 过火，该条偏内敛微表演，Kling 不宜用纯文本」
    But When 反向：Seedance 欠演不达意（达意3）而 Kling 达标
    Then 同理 validated，记录通过模型=Kling
    `[AUTO+HUMAN]`  *(per-model 非对称是真实模型偏置；哪个模型"过火/欠演"须人眼判 [HUMAN])*

### Scenario 4.2: 强度5 须配峰值表情起始帧 vs 强度3 纯文本即可（FR-9 / dossier）
    Given 同一 (压抑隐忍×内敛×眼神) 系列
    When 撰写强度5（崩溃边缘/失控张口，纯文本易变僵）
    Then 强烈建议配 `## 起始帧表情`（峰值表情已到位，模型只做动作插值更可靠）
    And 验证回填的「使用模式」记为 `起始帧`
    But When 撰写强度3（中段可控带）
    Then 纯文本即可，使用模式记 `纯文本`

    Examples: 起始帧需求随强度
      | 强度 | 纯文本可控性 | 起始帧建议 | 典型使用模式 |
      | 3    | 高（可控带） | 选填       | 纯文本       |
      | 5    | 低（易变僵） | 强烈建议   | 起始帧       |
    `[AUTO+HUMAN]`

### Scenario 4.3: 强忍三子类各成独立 entry（FR-7）
    Given 「强忍」在压抑隐忍下
    When 我建模强忍
    Then 强忍泪水 / 强压怒火 / 强装镇定 是三条独立 entry（各自 perf_NNNN）
    And 三者抑制肌签名不同，不可合并为一条
      | 子类     | 泄漏核        | 抑制肌签名                       |
      | 强忍泪水 | AU1+AU15 悲核 | 喉头吞咽 + 眨眼挤回泪膜 + 仰头   |
      | 强压怒火 | AU4+AU7 怒核  | 双唇用力相压(AU24) + 下颌咬紧    |
      | 强装镇定 | 混合泄漏      | 上下脸冲突最强 + 刻意放松肩颈    |
    `[AUTO]`  *(子类拆分可结构化检查；签名是否在视频里区分得开属 [HUMAN])*

### Scenario 4.4: 强度阶梯=同 AU 核升强 + 后段招募张口 AU，非换肌肉（FR-8）
    Given 同一 (压抑隐忍×内敛×眼神) 的强度 1→5 系列
    When 我对比相邻强度的 body
    Then 各级共享同一情绪 AU 核（不换一组肌肉）
    And 升强主要靠该 AU 集 A→E 升强 + 后段（强度4–5）招募张口 AU（AU25/26/27）+ 肢体招募
    And 强度1=单区/痕迹（微表情），强度5=全集/极致/张口

    Examples: 同核升强阶梯（压抑隐忍·内敛·眼神）
      | 强度 | AU 核（共享） | 新增招募            | 中文画面增量              |
      | 1    | 悲/怒核痕迹   | —                   | 目光极轻一垂、几不可察    |
      | 3    | 同核清晰      | 抑制肌(AU24/17)     | 下睑紧、喉头一动、唇压平  |
      | 5    | 同核极致      | 张口 AU25/26 + 肢体 | 唇分气音、肩颤、扶物撑住  |
    `[AUTO+HUMAN]`  *(「是否换了肌肉集」可对 au_ref 集合做包含检查 [AUTO]；阶梯感是否自然属 [HUMAN])*

### Scenario 4.5: 中文 prompt 校准——行为未验证（OQ-5）
    Given 全部公开实测为英文 prompt，中文肌肉描述（「嘴角微微下垂，眉头轻蹙」）是否同样 land 未经验证
    When pilot 阶段开篇
    Then 应先跑一条中文 vs 英文表演描述的控制变量校准渲染（低成本去风险）
    And 在校准结论回填前，所有中文条的服从性结论标记为「未经中文校准确认」
    And 校准结果（中文是否等效 land、哪些中文词被忽略）记入库 README / 实测笔记
    `[HUMAN]`  *(须看校准渲染对照，纯人工判断)*

### Scenario 4.6: 模型大版本漂移 → 高强度条需复验（NFR-5）
    Given 一条已 validated 的强度5 entry，记录了验证所用 Kling/Seedance 版本与日期
    When Kling 或 Seedance 发布大版本更新
    Then 该高强度条的服从性结论视为失效
    And 库 README 指示「模型大版本更新后高强度 entry 需复验」
    And 复验前不得据旧结论扩量产
    `[AUTO+HUMAN]`  *(版本/日期是否记录 [AUTO]；是否需复验的触发判断 [HUMAN])*

---

## 行为覆盖矩阵（Feature × FR/NFR 回溯）

| Feature/Scenario | 覆盖的 FR/NFR/OQ              | 自动化属性 |
| F1.1–1.6         | FR-1/2/4/5/6/7/9/11          | 多为 AUTO  |
| F2.1–2.5         | FR-13 + 迭代上限             | AUTO+HUMAN |
| F3.1–3.5         | FR-10 / NFR-1 / NFR-2        | 多为 AUTO  |
| F4.1             | per-model 不对称（FR-13）    | AUTO+HUMAN |
| F4.2             | FR-9 起始帧                  | AUTO+HUMAN |
| F4.3             | FR-7 强忍子类                | AUTO       |
| F4.4             | FR-8 强度阶梯                | AUTO+HUMAN |
| F4.5             | OQ-5 中文校准                | HUMAN      |
| F4.6             | NFR-5 复验节奏               | AUTO+HUMAN |

**自动化 vs 人工分界总结**：结构合规（四维字段、frontmatter 枚举、三层块存在、AU 可回溯、字节稳定、状态转移、迭代轮次、引用契约）全部 `[AUTO]` 可脚本/grep 派生；表演质量判断（情绪是否可识别、是否过火、起始帧是否到位、中文是否 land、阶梯是否自然、哪个模型偏过火/欠演）全部 `[HUMAN]`，须看检验视频并凭表演经验打分——这正是为何 FR-13 的验证门由用户人工完成而非自动渲染。
