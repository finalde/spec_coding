# 验收准则 — wukong_juexing

Run: wukong_juexing-20260503-201831
Stage: 5 (validation strategy) — level: acceptance_criteria
来源 spec: `specs/ai_video/wukong_juexing/final_specs/spec.md` (FR-1 ~ FR-42 + NFR-1 ~ NFR-8)

## 总览

本文档以 Gherkin (Given / When / Then) 形态固化 `wukong_juexing`(YouTube Shorts 短片,sub_type=short) stage-6 输出物的验收契约。每个场景对应一个明确的可判定通过/失败检查;场景按 stage-6 6 个 work unit (U1 角色 / U2 风格 / U3 叙事 / U4 提示词 / U5 发布 / U6 README) 与 5 个 Primary flow 步骤(读 README → 生成立绘 → 渲染分镜 → 拼接 → 发布)交叉覆盖。每个场景在标题行用 `[automated]` 或 `[manual_walkthrough_only]` 标注其在 stage-6 的执行模式;`[automated]` 由 stage-6 流式校验器在文件落盘时直接断言,`[manual_walkthrough_only]` 由 parent 在所有自动化级别通过后发出 `validation.requires_manual_walkthrough` 事件,由用户在 Seedream / Kling / Seedance 渲染完成后人工确认。

严重度遵循 `agent_refs/validation/{general,ai_video}.md`:语言违规、缺锁定描述符块、`时长` > 15s、缺 `比例:`、缺 hook 标记、缺 `publish.md`、descriptor 漂移 = `blocker`;palette/词表越界、hashtag 越界、README 同步缺失 = `blocker`;连续性 token 缺失但渲染前不可见 = `warning`(并升级为 manual walkthrough)。

## 自动化验收场景

### U1 — 角色 (character bible + Seedream 立绘提示词)

#### AC-U1-01 [automated] — 角色 bible 与立绘提示词文件存在
来源 FR: FR-2, FR-3
```gherkin
Given stage-6 U1 已完成
When 校验器列出 `ai_videos/wukong_juexing/characters/` 目录
Then `characters/main.md` 存在,`characters/ref_images/main_seedream.md` 存在
And 两个文件的字节大小均 > 0
```

#### AC-U1-02 [automated] — 锁定描述符块字节级嵌入 `characters/main.md`
来源 FR: FR-11, FR-32, FR-34, FR-36, NFR-2
```gherkin
Given `characters/main.md` 已落盘
When 校验器在文件中搜索 "【孙悟空 · 觉醒态 · 锁定描述符 v1】" 起始,至 "禁用 卡通线条、cel-shading、二次元大眼、低多边形。" 结束的文本块
Then 该块作为连续子串完整出现(允许其上下有 framing 文本)
And 块内包含字面字符串 "金箍棒" 与 "2 米"
And 块内包含字面字符串 "棕褐" 与 hex `#5C4A3A`
And 块内包含字面字符串 "凤翅紫金冠" 与 hex `#6B4226` 及 `#C9A96E`
And 块尾出现"禁用 卡通线条、cel-shading、二次元大眼、低多边形。"
```

#### AC-U1-03 [automated] — Seedream 立绘提示词遵守 10 段结构 + 字数
来源 FR: FR-14, NFR-5
```gherkin
Given `characters/ref_images/main_seedream.md` 已落盘
When 校验器解析其 markdown header 序列
Then 文件依序包含 10 个段落标题: 主体定义 / 面貌细节 / 发型+头冠 / 服装 / 身材+姿态 / 道具 / 画面控制 / 风格-质感 / 比例+输出 / 负向提示
And 文件中出现字面字符串 "9:16" 与 "竖构图"
And 全文(剔除 header)中文字数(Han 统计)落在 [250, 400] 闭区间内
```

### U2 — 风格 (style guide)

#### AC-U2-01 [automated] — `style_guide.md` 存在并包含锁定调色盘
来源 FR: FR-4, FR-15, FR-35
```gherkin
Given `ai_videos/wukong_juexing/style_guide.md` 已落盘
When 校验器读取该文件
Then 文件存在且非空
And 文件中字面包含全部 7 个 palette 命名行(山岩灰褐 `#5C4A3A`、暖金高光 `#C9A96E`、紫金底 `#6B4226`、暖橘金 `#F2A65A`、金鳞光晕 `#8A6A3A`、暗夜冷蓝 配套色、神性白光 配套色)对应的 7 个 hex 码
And 文件中字面出现 6 个光线状态 token、5 个运动模式 token、3 条转场规则
And 文件中字面包含 "戏剧化星空 + 银河淡带" 用作 FR-35 的星空密度锚点
And 文件 `画幅` 行字面包含 "9:16"
```

#### AC-U2-02 [automated] — palette hex 集合即权威白名单
来源 FR: FR-17, NFR-3
```gherkin
Given `style_guide.md` 已落盘
When 校验器抽取该文件 palette table 中所有 hex(正则 `#[0-9A-Fa-f]{6}`),作为 ALLOWED_HEXES
And 校验器扫描全部 10 个 `prompts/shotNN_*.md` 文件并抽取所有 hex
Then 任一在 prompt 文件中出现的 hex 都属于 ALLOWED_HEXES
And 出现未授权 hex 时报告对应文件路径与 hex 字符串(便于定位违规)
```

### U3 — 叙事 (script + shotlist)

#### AC-U3-01 [automated] — `shotlist.md` 恰列出 5 个分镜且字段完整
来源 FR: FR-5, FR-6, FR-20
```gherkin
Given `script.md` 与 `shotlist.md` 均存在
When 校验器解析 `shotlist.md` 中的分镜表格(markdown table)
Then 表格恰有 5 行数据行(不计 header)
And 每一行的列集合 ⊇ {`shotNN`, `时长`, `景别`, `动作摘要`, `连续性 tokens`, `是否 hook 镜头`}
And 第 01 行 `shotNN` 字面 = "shot01" 且 `是否 hook 镜头` 字段非空且为肯定值(如 "是" / "✓" / "hook")
```

#### AC-U3-02 [automated] — 分镜时长锁定 + 总和 = 38s + 单镜 ≤ 10s
来源 FR: FR-21, FR-22, ai_video.md 验证移动 #2
```gherkin
Given `shotlist.md` 已落盘
When 校验器逐行解析 `时长` 字段(剥离 "s" 后转 int)
Then shot01 = 5,shot02 = 8,shot03 = 8,shot04 = 10,shot05 = 7
And sum(时长) == 38
And max(时长) <= 10
And 任意分镜的 `时长` <= 15(harness 上限)
```

#### AC-U3-03 [automated] — Shot03 金箍棒微弱内发光例外被显式标记
来源 FR: FR-33
```gherkin
Given `shotlist.md` 已落盘
When 校验器读取 shot03 行的 `连续性 tokens` 字段
Then 该字段中字面包含 "金箍棒钎柄微弱内发光" 或等价 token "棒身钎柄内发光"
And 该字段中字面包含 hex `#F2A65A`
And shot01/02/04/05 行的 `连续性 tokens` 中均不包含上述内发光 token
```

#### AC-U3-04 [automated] — 转场规则 hard cut + match cut 已锁定
来源 FR: FR-31
```gherkin
Given `shotlist.md` 与 `script.md` 已落盘
When 校验器在 `shotlist.md` 转场列(或 `script.md` 转场段落)中查找 shot01→shot02 与 shot04→shot05 的转场标记
Then shot01→shot02 转场字面 = "hard cut"
And shot04→shot05 转场字面 = "match cut"
And 文档中 NOT 出现 "0.3" / "0.5" 秒级 "白闪" / "white flash" 转场表述(已显式 out-of-scope)
```

### U4 — 提示词 (10 个 shot prompt 文件)

#### AC-U4-01 [automated] — 全部 10 个 shot prompt 文件落盘且字段集合完整
来源 FR: FR-7, FR-26, ai_video.md 验证移动 #4
```gherkin
Given stage-6 U4 已完成
When 校验器枚举 `prompts/` 目录
Then `prompts/shot{01,02,03,04,05}_kling.md` 与 `prompts/shot{01,02,03,04,05}_seedance.md` 共 10 个文件存在
And 每个 Kling 文件均包含字段标题: `角色:`, `场景:`, `动作:`, `镜头:`, `光线/色调:`, `比例:`, `时长:`, `negative_prompt:`, 且首行为 `[参考图: characters/ref_images/main_seedream.md 生成的孙悟空立绘]`
And 每个 Seedance 文件均包含字段标题: `角色:`, `场景:`, `动作:`, `镜头:`, `光线/色调:`, `比例:`, `时长:`, `风格:`, `画质:`, `约束:`, `seed:`, 且 NOT 包含 `negative_prompt:`,且 NOT 包含 `[参考图:` 行
```

#### AC-U4-02 [automated] — 锁定描述符在 11 个文件间字节相等(load-bearing)
来源 FR: FR-11, FR-12, FR-13, NFR-2,ai_video.md 验证移动 #3
```gherkin
Given `characters/main.md` 与 10 个 `prompts/shotNN_{kling,seedance}.md` 均已落盘
When 校验器从每个文件中抽取 "【孙悟空 · 觉醒态 · 锁定描述符 v1】" 起 至 "禁用 卡通线条、cel-shading、二次元大眼、低多边形。" 止 的描述符块
Then 11 个文件抽取出的 11 份描述符块字节级完全相等(SHA-256 一致)
And 抽取失败(块缺失或边界不全)的文件数 = 0
```

#### AC-U4-03 [automated] — `比例:` 三重一致 = 9:16
来源 FR: FR-27, NFR-5,ai_video.md 验证移动 #5
```gherkin
Given 10 个 shot prompt 文件均已落盘
When 校验器逐文件读取 `比例:` 行
Then 每个 prompt 文件的 `比例:` 字段值字面 = "9:16"
And `style_guide.md` `画幅` 行包含 "9:16"
And `characters/ref_images/main_seedream.md` "比例+输出" 段落字面包含 "9:16" 与 "竖构图"
```

#### AC-U4-04 [automated] — Kling 时长 enum + 渲染说明退化注释
来源 FR: FR-27, NFR-6
```gherkin
Given 5 个 `prompts/shotNN_kling.md` 文件已落盘
When 校验器逐文件读取 `时长:` 字段
Then shot01_kling.md `时长:` = "5s"
And shot04_kling.md `时长:` = "10s"
And shot02_kling.md, shot03_kling.md, shot05_kling.md 的 `时长:` 字段 ∈ {"5s", "10s"}(shot02/03 锁定 8s、shot05 锁定 7s,Kling 无对应 enum,文件值必为 "5s" 或 "10s")
And 凡 `时长:` 与 shotlist 锁定值不一致的 Kling 文件,文件中字面包含 `# 渲染说明:` 块,且块内包含 "trim" 或 "压缩" 字样的退化方案
```

#### AC-U4-05 [automated] — Seedance 时长落在锁定整数
来源 FR: FR-27, NFR-6
```gherkin
Given 5 个 `prompts/shotNN_seedance.md` 文件已落盘
When 校验器逐文件读取 `时长:` 字段
Then shot01_seedance.md = "5s",shot02_seedance.md = "8s",shot03_seedance.md = "8s",shot04_seedance.md = "10s",shot05_seedance.md = "7s"
And 每个值均为 [2, 12] 区间内整数 + "s"
```

#### AC-U4-06 [automated] — 双 prompt 不对称: negative_prompt 仅 Kling、约束尾仅 Seedance
来源 FR: FR-23, FR-24, FR-19
```gherkin
Given 10 个 shot prompt 文件已落盘
When 校验器扫描每个 Kling 文件的 `negative_prompt:` 行
Then 每个 Kling 文件 `negative_prompt:` 行字面包含全部以下 token: "卡通", "Q版", "cel-shading", "二次元", "戏曲妆", "京剧脸谱", "低多边形", "86版西游记", "多余手指", "五官畸变", "文字水印", "字幕", "logo", "模糊", "鬼影", "闪烁", "现代服饰", "现代建筑", "多人出现"
And 每个 Seedance 文件 NOT 包含 "negative_prompt:" 字符串
And 每个 Seedance 文件 `约束:` 字段字面包含正向反面表达: "五官稳定不畸变", "同一角色全程一致", "单人画面无多余人物", "无文字水印", "无字幕", "无现代元素", "无模糊鬼影闪烁"
And 每个 prompt 文件正文(`角色:` 与 `场景:`/`动作:`/`镜头:` 区域)NOT 出现禁用 register token 的肯定形式("卡通"等)
```

#### AC-U4-07 [automated] — 视觉 register 锚句出现在每个 prompt
来源 FR: FR-18
```gherkin
Given 10 个 shot prompt 文件已落盘
When 校验器读取每个文件的 `场景:` 行与 `风格:` 行(Seedance)/或合并的 `场景:` 行(Kling)
Then 每个文件至少有一行字面包含 "黑神话·悟空美术风"(中点 · 字符为 U+00B7)
```

#### AC-U4-08 [automated] — `光线/色调:` 词表锁定
来源 FR: FR-16, NFR-3
```gherkin
Given `style_guide.md` 已落盘并定义了 6 光线 token + 7 palette 命名行
When 校验器抽取 6 光线 token 与 palette 命名集合作为 LIGHTING_VOCAB
And 校验器逐文件读取每个 shot prompt 的 `光线/色调:` 行
Then 该行 tokenize 后,每个非技术 token(剔除 hex / "9:16" / 数字+s)均属于 LIGHTING_VOCAB
And 该行 NOT 出现自由形态词如 "warm tones"、"暖色调"(裸用未锚定 hex 时)、"cold light"
```

#### AC-U4-09 [automated] — Seedance 动作字段按秒分段
来源 FR: FR-25
```gherkin
Given 5 个 `prompts/shotNN_seedance.md` 文件已落盘
When 校验器解析每个文件 `动作:` 字段下的内容
Then `动作:` 内容至少含 2 段以 `N–M 秒:` 或 `N-M 秒:` 形态开头的子段(如 "0–2 秒: ..." / "2–5 秒: ...")
And 子段时间区间总和 ∈ [shot 实际时长 - 1, shot 实际时长](允许 1 秒边界余量)
And 区间不重叠且单调递增
```

#### AC-U4-10 [automated] — Hook 缩略图契约 + Shot01 t≈2s burst-peak
来源 FR: FR-28, FR-29,ai_video.md 验证移动 #5
```gherkin
Given `prompts/shot01_kling.md` 与 `prompts/shot01_seedance.md` 已落盘
When 校验器读取两文件顶部
Then 两文件均以 `# 缩略图契约` 块起始,块内字面包含 "9:16 Shorts 缩略图"、"裂石 + 金光迸发"、"上 2/3"、"单焦点"
And shot01_kling.md `动作:` 散文中字面出现 "t≈2s" 或 "约 2 秒" 与 "burst-peak"/"迸发峰值" 同句出现
And shot01_seedance.md `动作:` 中 "0–2 秒:" 段尾字面包含 "迸发峰值" 或 "burst-peak"
```

#### AC-U4-11 [automated] — 回环契约 + Shot05 终帧匹配 Shot01 起帧
来源 FR: FR-30, FR-31
```gherkin
Given `prompts/shot05_kling.md` 与 `prompts/shot05_seedance.md` 已落盘
When 校验器读取两文件顶部
Then 两文件均以 `# 回环契约` 块起始,块内字面引用 "shot01 frame 0",并字面声明同机位/同焦距/同构图
And 块内字面区分起止光线状态: shot01 = "金光-bursting / 体积光丁达尔束",shot05 = "金光-fading / 余烬冷尾"
And 块内 NOT 声明任何镜头/焦距/构图差异(光线状态除外)
```

### U5 — 发布 (publish.md)

#### AC-U5-01 [automated] — `publish.md` 6 段骨架完备
来源 FR: FR-8, FR-37,ai_video.md 验证移动 #6
```gherkin
Given `ai_videos/wukong_juexing/publish.md` 已落盘
When 校验器解析其 markdown header 序列
Then 文件依序包含 6 个段落: 标题 / 简介 / Hashtag 规则 / 封面建议 / 发布时段建议 / 跨平台复用
And 6 个段落均非空(每段至少 1 行非空白内容)
```

#### AC-U5-02 [automated] — 标题、简介、hashtag 量级
来源 FR: FR-38, FR-39, FR-40
```gherkin
Given `publish.md` 已落盘
When 校验器读取 "标题" 段、"简介" 段、"Hashtag 规则" 段
Then 标题段首条非空行 Han 字数 <= 30,且该行 NOT 包含 "#" 字符
And 简介段正文 Han 字数 ∈ [150, 250]
And 简介段首句作为 hook,以 "。" / "!" / "?" 之一结尾(单行场景概述)
And Hashtag 规则段或简介段中明示的 hashtag 数量 ∈ [3, 5],且必含 `#Shorts`
And 整个文件中 hashtag 出现总次数(标题 + 简介合计)<= 15
```

#### AC-U5-03 [automated] — 发布时段双锚定
来源 FR: FR-41
```gherkin
Given `publish.md` 已落盘
When 校验器读取 "发布时段建议" 段
Then 段中字面包含 "周四" 与 "周五" 与 "19:00" 与 "21:00" 与 "北京时间"(主推时段)
And 段中字面包含 "周四" 与 "11:00" 与 "12:00" 标识北美华人受众次推时段
```

#### AC-U5-04 [automated] — 封面建议指向 Shot01 t≈2s
来源 FR: FR-29, FR-37
```gherkin
Given `publish.md` 已落盘
When 校验器读取 "封面建议" 段
Then 段中字面包含 "shot01" 或 "Shot 01" 或 "第一镜"
And 段中字面包含 "t≈2s" 或 "2 秒" 或 "迸发峰值"
And 段中 NOT 推荐独立 Seedream 封面(out-of-scope per spec)
```

### U6 — README

#### AC-U6-01 [automated] — `README.md` 4 段结构 + 中文 + 关键词同步
来源 FR: FR-1, FR-42, NFR-7
```gherkin
Given `ai_videos/wukong_juexing/README.md` 已落盘
When 校验器解析其 markdown header 序列
Then 文件依序包含 4 个段落: 项目概要 / 使用说明 / 角色清单 / 风格关键词
And 项目概要段为 1 个段落(<= 5 行)
And 使用说明段为有序列表(`1.` `2.` `3.` `4.` `5.`),5 步与 spec Primary flow 一一对应:读 README / 生成立绘 / 渲染分镜 / 拼接 / 发布
And 角色清单段恰含 1 条孙悟空 bullet
And 风格关键词段含 5–10 个关键词,且每个关键词均出现在 `style_guide.md` 中(子串匹配)
```

### 跨工作单元 — 语言、路径、晋升保留

#### AC-X-01 [automated] — 中文内容率 >= 95%
来源 FR: FR-9, NFR-4, NFR-8,ai_video.md 验证移动 #1
```gherkin
Given `ai_videos/wukong_juexing/` 下全部 `*.md` 已落盘
When 校验器递归读取所有 md 文件
And 剥离 ``` 代码围栏块、YAML frontmatter、裸 URL、hex 码、`9:16`、`Ns`/`Nm` 时长、参数 key (`negative_prompt:`, `cfg_scale:`, `seed:`, `camera_fixed`)、模型/工具名 (`Kling`, `Seedance`, `Seedream`)
Then 剩余正文字符中 Han + 全角标点占比 >= 95%
And 任何 ASCII 英文连续单词长度 >= 3 的子串(剔除上述白名单)出现次数 == 0(防止英文叙事漏网)
```

#### AC-X-02 [automated] — 路径全英文/拼音
来源 FR: FR-10
```gherkin
Given `ai_videos/wukong_juexing/` 已落盘
When 校验器递归列出所有路径(目录 + 文件)
Then 任意路径分段(`/` 切分后的 segment)中 Han 字符数 == 0
And 任意路径分段仅由 [a-zA-Z0-9_.-] 字符组成
```

#### AC-X-03 [automated] — 晋升项 verbatim 落入再生成产物
来源 general.md 原则 8,ai_video.md 验证移动 #7
```gherkin
Given `<stage>/promoted.md` 在 stage-6 输入侧存在(可能为空文件)
And 校验器使用 `libs/promotions.py` 的 `parse_promoted_text` 解析每条 pin
When stage-6 流式校验器在每个 work unit 落盘后比对其 promoted-source 文件
Then 每条 pin 的字符串内容(剔除前后空白)在再生成产物中以 verbatim 子串出现
And 找不到 pin 插入点时,其落入对应源文件末尾的 `## Pinned items (orphaned)` 段且附 1 行说明
And v1 stage-6 (`ai_videos/wukong_juexing/`) 不生成 promoted 检查(per ai_video.md 验证移动 #7)
```

## 手动验收场景

#### AC-M-01 [manual_walkthrough_only] — 立绘 on-model 抽检
来源 FR: FR-11, FR-14, FR-32, FR-34, FR-36
```gherkin
Given 用户已在 Seedream 中粘贴 `characters/ref_images/main_seedream.md` 并保存为 `ref_images/main_seedream.png`
When 用户随机抽取 1 张立绘图与 `characters/main.md` 的锁定描述符块对照
Then 视觉特征命中: 凤翅紫金冠、锁子黄金甲、2 米金箍棒(无自身外发光)、棕褐毛色、黑神话美术质感、9:16 竖构图
And NOT 出现: 卡通/Q版/京剧脸谱/低多边形/86版西游记面孔
And parent 仅在用户回答"on-model"后关闭该 work unit
```

#### AC-M-02 [manual_walkthrough_only] — 角色一致性盲读校验
来源 FR: FR-12, FR-13, NFR-2,ai_video.md 验证移动 #8
```gherkin
Given 5 镜 Kling + 5 镜 Seedance 视频片段已生成
When parent 发出 `validation.requires_manual_walkthrough`,提示用户:"以乱序打开 2–3 个 shot 提示词文件与对应渲染样片,确认描述符与画面同人"
Then 用户对每对(prompt, 样片)给出 "同一角色" / "可接受同源差异" / "明显漂移" 三档判断
And 任意一对判定为 "明显漂移" 即触发重渲并回到 prompts work unit
```

#### AC-M-03 [manual_walkthrough_only] — Hook 缩略图抽检 (上 2/3 / 单焦点 / 可识别)
来源 FR: FR-28, FR-29
```gherkin
Given Shot01 已渲染完成
When 用户截取 t≈2s 帧并以 9:16 缩略图尺寸预览(模拟 YouTube Shorts feed)
Then 视觉确认: 主体(裂石 + 金光迸发)位于上 2/3 区域;单一视觉焦点;palette 命中 `#C9A96E` / `#F2A65A`;无文字/水印/字幕
And NOT 出现现代元素或多人画面
And 用户在 1 秒视线内能识别"破石孙悟空觉醒"主题(retention abuse-test)
```

#### AC-M-04 [manual_walkthrough_only] — 回环视觉闭合
来源 FR: FR-30, FR-31
```gherkin
Given Shot01 与 Shot05 均已渲染完成并被用户挑出最佳版本
When 用户并排对比 Shot01 frame 0 与 Shot05 final frame
Then 视觉确认: 同机位、同焦距、同主体框景、同道具位置
And 唯一可见差异为光线状态: Shot01 = 金光迸发峰值;Shot05 = 余烬冷尾衰退
And Shot04 末帧 → Shot05 首帧采用 match cut(主体/构图无错位跳变)
```

#### AC-M-05 [manual_walkthrough_only] — 38s ±4s 拼接长度
来源 FR: FR-21, Primary flow 步骤 4
```gherkin
Given 用户已在外部剪辑器中拼接 5 镜
When 用户读取最终时间线总时长
Then 总时长 ∈ [34s, 42s]
And 任意单镜在剪辑后 <= 10s(Kling 退化裁剪后仍达约束)
```

#### AC-M-06 [manual_walkthrough_only] — README → Primary flow 可走通
来源 FR: FR-42, Primary flow 全 5 步
```gherkin
Given 用户首次拿到 `ai_videos/wukong_juexing/` 包,只读 `README.md`
When 用户按 README "使用说明" 5 步顺序操作: 读 README → 用 Seedream 生成立绘 → 把立绘附给每个 Kling shot 提示词并跑 Seedance 文本提示词 → 拼接 → 用 publish.md 发到 YouTube Shorts
Then 用户无需翻阅 spec 即可独立完成所有 5 步
And 任一步出现 "下一步要打开哪个文件不清楚" 即视为 README 失败,回到 U6 work unit 修订
```

## 覆盖矩阵

| Scenario ID | Mode | Covered FRs / NFRs |
|---|---|---|
| AC-U1-01 | automated | FR-2, FR-3 |
| AC-U1-02 | automated | FR-11, FR-32, FR-34, FR-36, NFR-2 |
| AC-U1-03 | automated | FR-14, NFR-5 |
| AC-U2-01 | automated | FR-4, FR-15, FR-35 |
| AC-U2-02 | automated | FR-17, NFR-3 |
| AC-U3-01 | automated | FR-5, FR-6, FR-20 |
| AC-U3-02 | automated | FR-21, FR-22 |
| AC-U3-03 | automated | FR-33 |
| AC-U3-04 | automated | FR-31 |
| AC-U4-01 | automated | FR-7, FR-26 |
| AC-U4-02 | automated | FR-11, FR-12, FR-13, NFR-2 |
| AC-U4-03 | automated | FR-27, NFR-5 |
| AC-U4-04 | automated | FR-27, NFR-6 |
| AC-U4-05 | automated | FR-27, NFR-6 |
| AC-U4-06 | automated | FR-19, FR-23, FR-24 |
| AC-U4-07 | automated | FR-18 |
| AC-U4-08 | automated | FR-16, NFR-3 |
| AC-U4-09 | automated | FR-25 |
| AC-U4-10 | automated | FR-28, FR-29 |
| AC-U4-11 | automated | FR-30, FR-31 |
| AC-U5-01 | automated | FR-8, FR-37 |
| AC-U5-02 | automated | FR-38, FR-39, FR-40 |
| AC-U5-03 | automated | FR-41 |
| AC-U5-04 | automated | FR-29, FR-37 |
| AC-U6-01 | automated | FR-1, FR-42, NFR-7 |
| AC-X-01 | automated | FR-9, NFR-4, NFR-8 |
| AC-X-02 | automated | FR-10 |
| AC-X-03 | automated | (cross-cut: pin preservation per general.md §8) |
| AC-M-01 | manual | FR-11, FR-14, FR-32, FR-34, FR-36 |
| AC-M-02 | manual | FR-12, FR-13, NFR-2 |
| AC-M-03 | manual | FR-28, FR-29 |
| AC-M-04 | manual | FR-30, FR-31 |
| AC-M-05 | manual | FR-21 |
| AC-M-06 | manual | FR-42 (Primary flow 1–5) |

### FR 反向覆盖检查

下列 FR 至少由一个场景覆盖(自动化或手动): FR-1 ~ FR-42 全部 + NFR-2 / NFR-3 / NFR-4 / NFR-5 / NFR-6 / NFR-7 / NFR-8。

NFR-1(Kling 2.1 Pro / Seedance 1.0 Pro 版本锚定)由 spec 元数据声明、不在 stage-6 文件输出中显式断言,故不单独建场景;若用户在 stage-6 启用更高版本,影响范围限于"是否兼容",由用户验证而非自动化校验器把关。
