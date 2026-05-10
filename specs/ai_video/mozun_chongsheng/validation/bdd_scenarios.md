# BDD scenarios — mozun_chongsheng

Run: mozun_chongsheng-20260509-164205
Stage: 5 / BDD level
Mode: AUTONOMOUS

## Feature 1: 单集叙事节奏

```gherkin
Feature: 每集遵循"三钩"模型

  Background:
    Given 单集时长 ≤ 90 秒
    And 单集默认 10 镜，每镜 8-10 秒
    And 钩列表必须含 ≥ 2 个 H 模式（来自 H1..H10 钩库）

  Scenario: 黄金钩
    Given shot01 时长 8s
    When 检查 shot01_kling.md / _seedance.md "动作:" 字段
    Then 0-3s 必有画面冲击 / 悬念 / 钩子（H1 / H3 / H8 任意一种）
    And shot01 中 3-8s 后段须有上集召回（旁白 / 字幕） — 除 ep01 外

  Scenario: 第一反转钩
    Given shot04 或 shot05 时长 9s
    When 检查其 prompt
    Then 必落点至少一个 H 模式（H2 / H3 / H6 / H7 任意）

  Scenario: Cliffhanger
    Given shot09 或 shot10 时长 9s
    When 检查 episodes/epNN/episode.md 的"下集预告"字段
    Then 必给出 ≥ 一句话预告
    And shot10 prompt 必切动作 / 表情 / 一句话半截（H9）
```

## Feature 2: 六卷大事件分布

```gherkin
Feature: 60 集六卷大事件锁定（FR-38）

  Scenario: 卷边界
    Given arc_outline.md
    When 解析卷边界
    Then 卷一 = ep01-ep05; 卷二 = ep06-ep13; 卷三 = ep14-ep25
    And 卷四 = ep26-ep43; 卷五 = ep44-ep55; 卷六 = ep56-ep60

  Scenario: 关键大事件锚点
    Given arc_outline.md
    When 检查关键集
    Then ep01 描述含"镇压"或"sealed"或类同词
    And ep05 描述含"转生"或"乞丐"
    And ep13 描述含"血池"或"Midpoint"或"真相"
    And ep25 描述含"元婴"或"觉醒"
    And ep55 描述含"渡劫"或"前世"或"反转"
    And ep60 描述含"归位"或"终战"
```

## Feature 3: 多女主出场节奏

```gherkin
Feature: 三女主按既定 ep 区间登场

  Scenario: 主女主（苏璃月）
    Given 卷三起 (ep14-ep25)
    Then 主女主在 ep14-ep15 首次登场
    And 主女主出现的 shot prompt 必引用 nvzhu_suyiyue 锁定句子

  Scenario: 副女主 1（柳红袖）
    Given 卷二乞丐期 (ep06-ep10)
    Then 副 1 在 ep07-ep08 首次登场
    And 副 1 出现的 shot prompt 必引用 fuyi_liuhongxiu 锁定句子

  Scenario: 副女主 2（苓夭夭）
    Given 卷四药王谷 (ep26-ep30)
    Then 副 2 在 ep26-ep27 首次登场
    And 副 2 出现的 shot prompt 必引用 fuer_lingyaoyao 锁定句子
```

## Feature 4: 男主修为节奏

```gherkin
Feature: 男主修为按 FR-15 路径推进

  Scenario: 修为升级匹配 ep 区间
    Given arc_outline.md 每集"修为段"字段
    Then ep06-ep10: 练气
    And ep11-ep13: 筑基
    And ep14-ep20: 金丹
    And ep21-ep25: 元婴
    And ep26-ep30: 化神
    And ep31-ep36: 合体
    And ep37-ep43: 大乘
    And ep44-ep49: 渡劫
    And ep50-ep55: 真仙
    And ep59-ep60: 圣人 / 沧冥归位
```

## Feature 5: 视觉反差 (传统仙侠 × 黑金沉郁)

```gherkin
Feature: 每集 ≥ 1 镜两套美学同框

  Scenario: 同框反差
    Given 任意 episode 中至少一个 shot 同时引用 ≥ 1 位伪君子宗主 + 男主魔尊形态
    When 解析该 shot 的 Kling / Seedance prompt
    Then "光线/色调:" 字段必含双美学关键词:
      - 白衣仙气词（仙气、青绿、月白、雾岚 等）
      - 黑金沉郁词（黑袍、魔气、星河、沉金 等）

  Severity: warning (不至于 blocker，但每集都该有一镜)
  Severity escalation: 整集都没有同框镜 → blocker (违背项目核心反讽设定)
```

## Feature 6: 系统弹窗一致性

```gherkin
Feature: 系统弹窗在所有相关 shot 中视觉一致

  Scenario: 系统 UI 视觉规范
    Given style_guide.md 含"系统 UI 视觉规范"段
    Then 该段必锁定:
      - 配色 (金色文字 #a8842c + 黑底半透明面板 #0a0a0a + 银白边框 #f5f5f0)
      - 字体（建议中文宋体 / 楷体）
      - 动画（弹入 0.3s + 停留 1.5s + 淡出 0.3s）
      - 文案模板（"叮——任务发布: ..."）

  Scenario: 任意 shot 含系统弹窗
    Given 一个 shot 含 H2 钩模式
    When 解析其 prompt
    Then "动作:" 或"光线/色调:" 字段必引用上述规范关键词
```

## Feature 7: Seam-frame 工作流

```gherkin
Feature: Seam-frame 静帧 prompt 与视频 prompt token 同步

  Scenario: 末帧与下镜首帧一致
    Given shot{N}_lastframe_seedream.md 与 shot{N+1}_kling.md（视频 prompt）
    When 解析其"场景:" / "光线/色调:" 字段
    Then 末帧 prompt 描述的视觉状态 ≈ 下镜首帧的初始状态
    And 角色锁定句子（如出现）byte-identical
```

## Feature 8: 抖音 / YouTube Shorts 发布合规

```gherkin
Feature: publish.md 元数据符合平台规范

  Scenario: 抖音标题
    Given publish.md 中 "抖音标题:" 字段
    Then 字数 ≤ 25 中文字
    And 必含 "《魔尊归来》第NN集" 前缀
    And 后段须有 ≥ 一个钩子词（重生 / 反杀 / 当年 / 我倒要 / 你以为 等）

  Scenario: YouTube Shorts 双语标题
    Given publish.md 中 "YouTube Shorts 标题:" 字段
    Then 字数 ≤ 90 字符
    And 必含中文剧名 + 英文 "Demon Lord Returns"
    And 必含 "#shorts #cdrama #xianxia" 至少这 3 个 hashtag

  Scenario: 抖音 hashtag 3 层
    Given publish.md 中 "抖音 hashtag:" 列表
    Then 数量 ∈ [5, 10]
    And 必含 P0 层 (#短剧 #仙侠 #魔尊归来)
    And 必含 P1 / P2 / P3 任意层
```

## Feature 9: ep01 开场契约

```gherkin
Feature: ep01 不需要 30s 教学集，且符合"重生流"惯例

  Scenario: ep01 开场
    Given episodes/ep01/episode.md
    Then 描述应当直接进入"魔尊被镇压"场景
    And 不出现"初次见面 / 自我介绍"类描述
    And ep02-ep04 通过倒叙交代因果 (FR-38)

  Scenario: ep01 shot01 黄金 3 秒
    Given episodes/ep01/prompts/shot01_kling.md
    When 解析其 "动作:" 字段
    Then 0-3s 必有 H1 模式（极端虐 / 镇压瞬间）
```

## Feature 10: 二季钩开关

```gherkin
Feature: ep60 final shot 双版本

  Scenario: 单季 ending 版本
    Given episodes/ep60/prompts/shot10_finale_kling.md
    Then 必描述"屠尽伪君子 / 三女主 / 全剧终"

  Scenario: 二季钩 ending 版本
    Given episodes/ep60/prompts/shot10_hook_kling.md
    Then 必描述"主女主立于雪中腹微凸光芒一闪 / 远方一道魔气未灭"

  Scenario: 用户二选一
    Given 渲染前
    Then 用户根据首发期留存数据选择渲染哪个版本
    And shotlist.md 应注明这两份是 OR 关系
```

## Feature 11: 单集编号一致性

```gherkin
Feature: 文件名 + 内容编号一致

  Scenario: ep 编号补零
    Given 任意 episodes/epNN/ 目录
    Then 目录名 NN 必为 2 位数字（ep01..ep60，不允许 ep1 / ep001）
    And 内部文件 episode.md / shotlist.md / publish.md 中"集号"字段必与目录名一致

  Scenario: shot 编号补零
    Given 任意 prompts/shot{NN}_*.md 文件
    Then NN 必为 2 位数字（shot01..shot10）
```
