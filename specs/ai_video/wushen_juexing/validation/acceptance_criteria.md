---
worker_id: level-specialist-01-acceptance
stage: 5
role: level-specialist
level: acceptance_criteria
status: complete
blockers: []
confidence: high
---

# Acceptance criteria —《武神觉醒》EP1 production CONTRACT (Gherkin)

验收对象 = 创作者/观众实际消费的 EP1 工件契约。每个 Scenario 对应一条 primary flow，criterion 尽量 greppable。
根目录约定：`ROOT = ai_videos/wushen_juexing/`，`EP1 = ai_videos/wushen_juexing/episodes/ep01/`。

---

## Flow A — 项目骨架文件齐备（FR-1/2/3/6，中文内容）

```gherkin
Feature: 项目骨架四件套齐备且中文

  Scenario: 骨架文件存在且非空
    Given 仓库 ROOT = ai_videos/wushen_juexing/
    When 检查骨架文件
    Then ROOT/README.md 存在且字节数 > 0
    And ROOT/world.md 存在且字节数 > 0
    And ROOT/style_guide.md 存在且字节数 > 0
    And ROOT/arc_outline.md 存在且字节数 > 0

  Scenario: README 含规定章节（中文）
    Given ROOT/README.md
    When 读取内容
    Then 含中文标题「武神觉醒」（grep "武神觉醒"）
    And 含使用说明并出现 "Seedream" 与 "Kling" 与 "Seedance" 三个流程关键词
    And 含角色清单（grep "裴知秋" 且 "裴昭" 且 "裴霆" 且 "凌虚子"）
    And 含风格关键词段（grep "9:16" 或 "竖屏"）
    And 正文以中文为主（非 ASCII 字符占比 > 50%）

  Scenario: world.md 落三轴 + 一句铁律 + 系统
    Given ROOT/world.md
    When 读取内容
    Then 资质轴 5 档齐全（grep "黄阶" "玄阶" "地阶" "天阶" "王体资质" 全部命中）
    And 境界轴 9 境齐全（grep "武徒" "武者" "武师" "武宗" "武王" "武皇" "武帝" "武圣" "武神" 全部命中）
    And 体质轴出现 "武神躯"
    And 含一句铁律 "资质决定上限的高度，体质改写上限本身"
    And 含系统设定 "武神觉醒系统"
    And 含裴王府势力/地理背景段（grep "裴王府"）

  Scenario: arc_outline.md 标 EP1 已详化、其余 skeleton
    Given ROOT/arc_outline.md
    When 读取内容
    Then 含 80 集 one-liner 大纲（出现 "80 集" 或 "EP80"/"第80集"）
    And EP1 行标注 "✅" 或 "已详化"
    And 其余集标注 "skeleton" 或 "骨架"
    And 含三幕拍点（出现 "中点" 或 "~40" 身世反转 且 "第7集"/"第 7 集" 钩 且 "79"/"80" payoff）
```

---

## Flow B — 4 角色 bible + 立绘 prompt 齐备且一句话锁定 byte-identical（FR-4/5, NFR-3）

```gherkin
Feature: 角色锚定与跨镜一致性

  Scenario: 4 角色目录与文件齐备（中文命名，N 不补零）
    Given ROOT/characters/
    When 列目录
    Then 存在 c1_裴知秋/、c2_裴昭/、c3_裴霆/、c4_凌虚子/ 四个目录
    And 每个目录含同名中文 bible 文件（如 c1_裴知秋/c1_裴知秋.md）且非空

  Scenario: 每个 bible 含锁定描述符全字段
    Given 任一角色 bible 文件
    When 读取内容
    Then 含字段：性别年龄体型、面貌、发型发色、服装主色（自然色名）、标志道具、标志动作、气质
    And 含 "一句话锁定" 标记且其值 ≤ 30 字
    And 含 性格动机、弧光、段位/能力 三段

  Scenario: 一句话锁定 byte-identical 跨所有引用 shot
    Given 角色 X 的 bible 中 "一句话锁定" 字符串 S_X
    And EP1 所有点名角色 X 的 shotNN.md
    When 在每个该 shot prompt 中提取重贴的锁定句
    Then 每处重贴串 == S_X（逐字节相等，无标点/空格差异）
    And 不存在任一 shot 漏贴 S_X（点名即重贴）

  Scenario: 4 份立绘 prompt 齐备
    Given ROOT/characters/ 下各角色目录
    When 检查 Seedream 立绘 prompt
    Then 每个角色含一份立绘 ref-image prompt（grep "Seedream" 或 "立绘"）
    And 每份含 主体/面部/服装/姿态/背景/光源/风格 段
    And 每份标注 竖屏 与 4K
```

---

## Flow C — EP1 剧本/对白/分镜/分镜prompt/publish 齐备（FR-7..FR-11）

```gherkin
Feature: EP1 全套出片素材齐备

  Scenario: EP1 顶层文件齐备且非空
    Given EP1 = ai_videos/wushen_juexing/episodes/ep01/
    When 检查文件
    Then EP1/script.md 存在且非空
    And EP1/dialogue.md 存在且非空
    And EP1/shotlist.md 存在且非空
    And EP1/publish.md 存在且非空
    And EP1/shots/ 目录存在且含 N 个 shotNN.md（N == shotlist 镜数）

  Scenario: script.md 为 screenplay 形式且落 15 节拍
    Given EP1/script.md
    When 读取内容
    Then 含场景标题 + 动作 + 对白 + 内心 OS 四要素
    And 含首爽点（第 1 分钟系统绑定/起身反转）与末段王体+武神躯觉醒大爽点
    And 末段含宗门暗线 cliffhanger（grep "凌虚子" 或 "宗门"/"剑修"）

  Scenario: dialogue.md 为纯对白逐行格式
    Given EP1/dialogue.md
    When 读取每一对白行
    Then 行格式形如 角色名: "台词" (语气情感注释)
    And 出场角色名只在 4 个 canonical 名中（裴知秋/裴昭/裴霆/凌虚子）或系统旁白显式归属

  Scenario: 每个 shot 文件结构完整（三 code block + 必填）
    Given EP1/shots/ 下任一 shotNN.md
    When 读取内容
    Then 含 小说原文段（200–400 字中文，出场角色名加粗）
    And 含 Shot context（Summary/Characters/Scene/Duration/Reference）
    And 含 起始帧 + 结束帧 + 视频 三个 code block
    And 每块首行为紧凑中文标签，形如 "01集NN镜始"/"01集NN镜末"/"01集NN镜视"
    And 不含废止字段（grep "负向"/"场景视角锚"/"body 角色" 命中 = 0）
    And OS/画外音台词显式归属说话人 + 含在画人物口型闭口指令
```

---

## Flow D — EP1 前 10 秒铁律（FR-7, S01 即冲突，无世界观旁白前置）

```gherkin
Feature: 红果前 10 秒铁律

  Scenario: S01 即冲突，禁世界观旁白前置
    Given EP1/script.md 与 EP1/shotlist.md 与 EP1/shots/shot01.md
    When 检查开篇 0–10s
    Then S01（shot01）即呈现当众废丹/除族冲突（grep "废丹"/"除名"/"除族"/"丹田碎"）
    And 0–3s 段无世界观设定旁白先于冲突（首镜不出现资质轴/境界轴讲解性旁白）
    And ~6s 段含退婚/羞辱节拍
    And ~10s 段含系统觉醒前兆（grep "系统"/"武神残魂"/"觉醒前兆"）

  Scenario: 计时锚点对齐
    Given EP1/script.md beat 计时
    Then 首爽点 ≈ 第 1 分钟（grep "30s"/"~30"/"第1分钟" 系统绑定锚）
    And 资质觉醒大爽点 ≈ ~120s
    And 末镜为宗门暗线 cliffhanger
```

---

## Flow E — EP1 总时长 ∈ [85,100]s、约 14–18 镜、每镜 ≤15s（FR-9, NFR-4, 规则 6 · follow-up 020 dialogue-rich 重定）

```gherkin
Feature: EP1 时长与镜数契约

  Scenario: shotlist 镜数在区间
    Given EP1/shotlist.md
    When 统计镜数 N
    Then 28 ≤ N ≤ 32
    And EP1/shots/ 下 shotNN.md 数量 == N

  Scenario: 每镜时长合法
    Given EP1/shotlist.md 每镜时长字段
    When 逐镜读取
    Then 每镜时长 ∈ [3,15] 秒
    And 每个 shotNN.md 的 Duration 与 shotlist 同镜时长一致

  Scenario: 总时长落区间且有显式合计行
    Given EP1/shotlist.md
    When 读取 "时长合计" 行
    Then 存在 "时长合计" 行
    And 合计值 == 各镜时长之和
    And 180 ≤ 合计值 ≤ 195
```

---

## Flow F — 零 hex 色码（FR-3, NFR-2, 规则 1b）

```gherkin
Feature: ai_videos 输出零十六进制色码

  Scenario: 全目录无 hex 色码
    Given ROOT = ai_videos/wushen_juexing/ 下所有 .md 文件
    When 执行 grep -rE "#[0-9a-fA-F]{6}\b" ROOT
    Then 命中行数 == 0
    And 颜色仅以自然中文色名出现（如 玄黑/朱红/玄青/月白/暖金/霜白）
```

---

## Flow G — publish.md 含 IAA 标注与全部规定字段（FR-11）

```gherkin
Feature: publish.md 元数据契约

  Scenario: publish.md 含全部规定字段
    Given EP1/publish.md
    When 读取内容
    Then 含标题且标题 ≤ 30 中文字
    And 含口语化钩子副标题
    And 含简介且 ≤ 200 字
    And 含 5–10 个 hashtags
    And 含封面建议并指明具体镜号（grep "封面" + "镜"/"shot"）
    And 含变现标注 "变现模式: IAA 免费+广告"（grep "IAA"）且不出现 "付费充值"/"付费墙"
    And 含题材标签（男频 且 古风玄幻 且 系统流 且 逆袭 且 武神 全部命中）
    And 含 "80 集" 与 "9:16"
    And 含预留 4–5 字推广关键词
    And 含前 72 小时高热运营提示（grep "72 小时"/"前72小时"/"高热"）
```

---

## 通过门槛（汇总）

- Flow A–G 所有 Scenario 全部 Then 命中 → EP1 production CONTRACT 验收 PASS。
- 任一 Scenario 失败：Flow D/E/F/G 失败为 **blocker**（铁律/时长/合规/平台元数据硬契约）；Flow A/B/C 缺件为 **blocker**，字段不全为 **warning**（可单镜补）。
- 一句话锁定 byte-identical（Flow B 第 3 Scenario）失败为 **blocker**——跨镜一致性是出片地基。
