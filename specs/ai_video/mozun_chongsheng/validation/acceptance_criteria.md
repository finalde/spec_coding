# Acceptance criteria — mozun_chongsheng

Run: mozun_chongsheng-20260509-164205
Stage: 5 (validation strategy / acceptance level)
Mode: AUTONOMOUS

## Conventions

Gherkin-style `Given / When / Then`，每条 AC 对应一个或多个 spec FR / NFR。验证粒度：

- **静态合规**: 检查 stage 6 输出的 .md 文件结构、字段、内容（无需渲染）
- **手动走查**: 视觉一致性、叙事连贯性（user-confirmed）

## AC-1 · 语言合规

```gherkin
Feature: ai_videos/mozun_chongsheng/ 下所有 .md 文件内容必须为中文

Scenario: 抽查任意 .md 文件
  Given 一份 ai_videos/mozun_chongsheng/**/*.md 文件
  When 剥离 code fence、YAML frontmatter、URL 后
  Then 剩余文本中 ≥95% 字符必须是 Han 块或全角标点
  And 英文 proper nouns（Kling、Seedance、Seedream、9:16、shot01 之类）不计入门槛
  And 角色名（沧冥、叶无尘、苏璃月、柳红袖、苓夭夭、白月清、赵焚天、方鼎元、韩夺心、司空玄）必须为中文姓名

  Severity: blocker
  覆盖 FR: NFR-8 / per agent_refs/validation/ai_video.md 规则 1
```

## AC-2 · 15-秒镜头原子性

```gherkin
Feature: 每个 shotlist.md 中的镜头时长必须 ≤ 15 秒

Scenario: 抽查任意 episodes/epNN/shotlist.md
  Given 一份 shotlist.md
  When 解析其 GFM 表格
  Then 每行必含 `时长` 字段
  And `时长` 数值必须 ≤ 15 秒
  And 单集所有镜头时长之和 ≤ 95 秒（默认 90 秒，弹性 ±5 秒）
  And 默认每镜 8-10 秒（FR-23 软约束）

  Severity: blocker (任何 shot > 15s 或缺失字段)
  覆盖 FR: FR-23 / NFR-3 / per agent_refs/validation/ai_video.md 规则 2
```

## AC-3 · 角色一致性 (byte-identical 锁定描述符)

```gherkin
Feature: 同一角色的"一句话锁定"在所有 shot prompt 中 byte-identical

Scenario: 抽查任意角色在同一集内的所有引用
  Given 角色 X 在 characters/{X}.md 的"一句话锁定"字段值 = S
  And 角色 X 在 episodes/epNN/prompts/ 下被引用 N 次
  When 解析每个引用 shot prompt 中"角色:"行
  Then 每行的字符串值必须 (modulo whitespace) 等于 S
  And 同一集内不允许出现两个不同的 X 描述符

  Severity: blocker (同集内 drift) / blocker (缺失锁定句子)
  覆盖 FR: FR-5 / NFR-2 / per agent_refs/validation/ai_video.md 规则 3
```

## AC-4 · 双管线 + seam-frame 完整性

```gherkin
Feature: 每镜必含 Kling + Seedance + lastframe Seedream prompt; 每集首镜必含 startframe Seedream

Scenario: 抽查任意 episodes/epNN/prompts/
  Given 该集 shotlist.md 列出 M 个镜头 (默认 M=10)
  When 检查 prompts/ 目录
  Then 必存在 M 份 shot{NN}_kling.md
  And 必存在 M 份 shot{NN}_seedance.md
  And 必存在 M 份 shot{NN}_lastframe_seedream.md
  And 必存在 1 份 shot01_startframe_seedream.md

  Severity: blocker (任何缺失)
  覆盖 FR: FR-9 / FR-10 / FR-11 / FR-12 / NFR-4 / per agent_refs/validation/ai_video.md 规则 4
```

## AC-5 · 比例 + 规避词字段

```gherkin
Feature: 每镜 prompt 含必备字段

Scenario: 抽查任意 shot prompt
  Given 一个 prompts/shot{NN}_kling.md 或 _seedance.md
  When 解析其字段
  Then 必含 `比例: 9:16` 行
  And 若是 Seedance prompt: 必含以"避免:"开头的规避词列表段
  And 若是 Kling prompt: 必含 `[参考图: ...]` 注释行（指向 ref_images / lastframe）
  And 必含 `时长: <= 10s` 或具体秒数

  Severity: blocker (任何字段缺失)
  覆盖 FR: FR-24 / FR-25 / NFR-5 / NFR-6 / per agent_refs/validation/ai_video.md 规则 5
```

## AC-6 · Publish 元数据完整

```gherkin
Feature: 每集 publish.md 含抖音 + YouTube Shorts 双套完整元数据

Scenario: 抽查任意 episodes/epNN/publish.md
  Given 一份 publish.md
  When 解析其内容
  Then 必含 "## 抖音" 段，含:
    - 标题（≤ 25 中文字）
    - hashtag 列表（5-10 个，3 层 P0/P1/P2/P3 结构）
    - 封面建议（含 cover-frame shot id + 字幕带 y 坐标）
  And 必含 "## YouTube Shorts" 段，含:
    - 双语标题（≤ 90 字符，含中英对照）
    - hashtag 列表（6-8 个）
    - 字幕语言策略
  And 必含 "## 描述" 段（≤ 200 字）

  Severity: blocker (任何子段缺失)
  覆盖 FR: FR-13 / FR-31..36 / NFR-7 / per agent_refs/validation/ai_video.md 规则 6
```

## AC-7 · 10 份 Seedream 立绘齐备

```gherkin
Feature: 9 个角色 + 男主第二形态 = 10 份 Seedream 立绘 prompt

Scenario: 检查 characters/ref_images/ 目录
  Given 项目根 ai_videos/mozun_chongsheng/characters/ref_images/
  When 列出所有 *_seedream.md 文件
  Then 必存在 10 份, 文件名 (含但不限于；per follow-up 002 中文命名):
    - 沧冥-魔尊本相-立绘.md
    - 叶无尘-乞丐转生-立绘.md
    - 苏璃月-紫霄圣女-立绘.md
    - 柳红袖-红袖招老板娘-立绘.md
    - 苓夭夭-药王谷医师-立绘.md
    - 白月清-紫霄宫主-立绘.md
    - 赵焚天-玄炎宗主-立绘.md
    - 方鼎元-太清掌教-立绘.md
    - 韩夺心-万剑宗主-立绘.md
    - 司空玄-影神殿主-立绘.md
  And 每份必含 4 段（主体/细节/风格/参数）

  Severity: blocker (缺失任意一份)
  覆盖 FR: FR-6 / per agent_refs/validation/ai_video.md 规则 3
```

## AC-8 · 角色声明前置

```gherkin
Feature: 任何 shot prompt 引用的角色必须在 characters/ 中已声明

Scenario: 抽查 shot prompt 中"角色:"字段
  Given 一个 shot prompt 中"角色:"指向角色 X 的锁定句子
  When 检查 characters/{X}.md 是否存在
  Then 必须存在
  And 该 .md 中"一句话锁定"字段必须等于 prompt 中"角色:"的值（byte-identical）

  Severity: blocker (角色未声明 = 视觉漂移待发生)
  覆盖 FR: FR-5 / NFR-9 / per agent_refs/validation/ai_video.md 规则 3
```

## AC-9 · arc_outline.md 完整性

```gherkin
Feature: 60 集大纲文件结构完整

Scenario: 抽查 ai_videos/mozun_chongsheng/arc_outline.md
  Given 一份 arc_outline.md
  When 解析其结构
  Then 必含 60 行集级一句话简介，命名格式 ep01..ep60
  And 必含 6 个分卷标题（卷一·镇压 / 卷二·乞丐重生 / 卷三·觉醒 / 卷四·恢复 / 卷五·反击 / 卷六·终战）
  And 每行必含主线大事件 + 修为段 + 钩列表

  Severity: blocker (缺失任一卷或集)
  覆盖 FR: FR-4 / FR-38
```

## AC-10 · 手动走查（人工签字）

```gherkin
Feature: 自动 level 全部通过后, 用户必须做一次随机抽查走查

Scenario: 全自动 level 全 pass 后
  Given stage 6 所有 work units 自动 level 全 pass
  When pipeline emit `validation.requires_manual_walkthrough` 事件
  Then 用户应:
    - 打开 characters/ref_images/ 任意 2 份立绘 prompt 朗读，确认能想象出角色
    - 打开 episodes/ep01..ep05 任意一集的 shotlist + 2-3 个 shot prompt
    - 检查 (a) 角色描述跨 shot 一致；(b) 单集叙事连贯（钩 → 反转 → cliffhanger）
  And 用户在 chat 中签字"通过"或具体反馈

  Severity: 人工 (无自动)
  覆盖 FR: per agent_refs/validation/ai_video.md 规则 8
```

## 严重度策略

| AC | Severity | Halt? | 来源规则 |
|---|---|---|---|
| AC-1 | blocker | 标准 3 轮修订 | ai_video.md 规则 1 |
| AC-2 | blocker | 标准 | ai_video.md 规则 2 |
| AC-3 | blocker | 标准 | ai_video.md 规则 3 |
| AC-4 | blocker | 标准 | ai_video.md 规则 4 |
| AC-5 | blocker | 标准 | ai_video.md 规则 5 |
| AC-6 | blocker | 标准 | ai_video.md 规则 6 |
| AC-7 | blocker | 标准 | ai_video.md 规则 3 |
| AC-8 | blocker | 标准 | ai_video.md 规则 3 |
| AC-9 | blocker | 标准 | spec FR-4 |
| AC-10 | manual_walkthrough | n/a | ai_video.md 规则 8 |

无 critical 级（无安全 / 数据 / sandbox 类风险——本项目仅产出文本 prompt，无运行时代码 / 网络 / 写权限）。
