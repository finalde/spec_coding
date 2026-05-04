# Validation — manual_walkthrough（人工走查脚本）

> 项目：`wukong_juexing`（ai_video, sub_type=short）
> 工件：本文件 = 人工走查脚本；与 `validation/strategy.md` 同级、为其末级闸门
> 来源：`agent_refs/validation/general.md` 原则 4、6、8 + `agent_refs/validation/ai_video.md` 必备动作 #8 + `final_specs/spec.md` FR-29 / FR-30 / 验收 §Level 5

---

## 总览

**触发时机。** 本走查在以下两件事都完成之后**才**启动：

1. 阶段 6（execution）已落盘全部 12 个工件文件，且 Level 1–4 的所有自动化校验（文件存在 / schema / 内容规则 / 语义-电影性可静态检的部分）**全部通过**或剩余项已用户裁决放行。
2. 用户已**离线**完成以下三件外部事：
   - 用 `characters/ref_images/main_seedream.md` 在 Seedream 渲出主体立绘并保存为 `characters/ref_images/main_seedream.png`；
   - 用 `prompts/shotNN_kling.md`（每条都附上述立绘）在 Kling 渲出 5 段；
   - 用 `prompts/shotNN_seedance.md` 在 Seedance 渲出 5 段；
   - 每镜在 Kling/Seedance 两版里**择优**（"on-model 优先于美感"），落地一份 5 镜定稿；
   - 在外部剪辑器里把 5 段拼成一条 38 s ±4 s 的 9:16 成片。

**如何消费。** 父代理在所有自动化级别完成后写一条 `validation.requires_manual_walkthrough` 事件到 `events.jsonl`，事件 payload 指向本文件。用户照本文件**逐条**自查；任何"失败处置"被触发都不闭环、走对应的回退路径（见每条 §失败处置）。所有 ~13 条全部签出后，用户回到父代理报"manual walkthrough 通过"，父代理再写 `validation.pass`（manual_walkthrough）+ `pipeline.halted`（reason=`done`）收尾。

**心法。** 本级专门捕捉自动化够不到的东西：**像不像**这个角色、**像不像**这套美术、**钩不钩**得住人、**首尾**接不接得起来、以及上一阶段画的 Out-of-Scope 红线**有没有跟实际产出打架**。本级**不**复核任何能用字符串相等 / token 出现性 / 段数 / 哈希码做的检查（那些归 Level 1–4）。

---

## 前置条件

走查开始前，用户必须已完成：

| # | 前置项 | 检验方式 |
|---|---|---|
| P1 | `characters/ref_images/main_seedream.png` 存在（用户从 Seedream 落盘） | 文件存在；分辨率 ≥ 1024×1820 (9:16)；非空 |
| P2 | 5 个 Kling 渲染产物（mp4 或 mov）存在，命名 `renders/shot01_kling.mp4` … `shot05_kling.mp4` | 5 个文件，每个时长 ≈ 对应 FR-21 锁定时长（10s shot 渲染后已剪到目标时长） |
| P3 | 5 个 Seedance 渲染产物存在，命名 `renders/shot01_seedance.mp4` … `shot05_seedance.mp4` | 5 个文件，每个时长 = FR-21 锁定时长 |
| P4 | 用户已**择优**：`renders/final/shot0N.mp4`，N=1..5 | 5 个文件；每镜在 `renders/final_picks.md` 里写一行说明"采用 Kling/Seedance + 一句理由（on-model / 节奏 / 钢质感等）" |
| P5 | 5 段拼接成一条 9:16 成片：`renders/final/wukong_juexing_v1.mp4` | 1 个文件；总时长 38 s ±4 s；竖屏 9:16 |
| P6 | 阶段 6 自动化校验已收尾，`events.jsonl` 中存在 `validation.requires_manual_walkthrough` 事件 | grep `events.jsonl` 看到事件；本走查的承接对象 |

> `renders/` 不是 spec 产物目录，是用户工作区。可放在 `ai_videos/wukong_juexing/renders/`（已 gitignore），也可放任何用户偏好位置——本走查只要求**可同时打开比对**即可。

任何一项前置缺失：**停**走查、回到 `agent_team` 父代理报告缺哪一项；不要绕开继续。

---

## 走查脚本

逐条做。每条独立可重做。检查名后括号是它对标的 FR / agent_refs 原则。

### 1. 立绘 on-model 锁定（FR-11 / FR-14 / FR-32–FR-36）

- **操作步骤：**
  1. 同屏并排打开 `characters/main.md`（locked descriptor v1 块）和 `characters/ref_images/main_seedream.png`。
  2. 逐条对照锁定描述符里的**6 个硬锚点**：
     - 凤翅紫金冠（双侧凤翅、冠体 `#6B4226` 紫金底 + `#C9A96E` 鎏金高光）；
     - 锁子黄金甲（甲片层叠、同上金属双锚色）；
     - 金箍棒（长 ≈ 2 米、反射环境暖光、**无**自身外发光辉）；
     - 棕褐毛色（`#5C4A3A` 山岩灰褐 base + `#8A6A3A` 逆光金边），**非**金毛；
     - 面部：猴相+人格化、五官稳定无畸变、非二次元大眼；
     - 体魄：站姿/重心/比例 = 黑神话级"沉重写实"。
- **通过标准：** 6 锚点**全部**在立绘上可肉眼识别；金属底色无飘到 `#F2A65A` 暖橘金（那是环境光，不是金属本色）。
- **失败处置：**
  - 若 ≥1 锚点不符 → 回到 `characters/ref_images/main_seedream.md`，迭代该 prompt 第 2 / 3 / 4 节（面貌/发型+头冠/服装），**不**改 `characters/main.md` 的锁定描述符 bytes（FR-11 immutable）；重渲立绘；本条重测。
  - 若锁定描述符自身出错（用户认定 6 锚点描述本身有歧义）→ 升级，触发**阶段 4 重生** spec 之 §Locked descriptor specifics 段；后续阶段链式重生。

### 2. 跨 5 镜角色一致性（FR-11/12/13、ai_video.md 严重度表第 3 行 = blocker）

- **操作步骤：**
  1. 把 `renders/final/shot01.mp4` … `shot05.mp4` 5 段**首帧**截图（任一截帧工具）成 5 张静帧；
  2. 5 张静帧 + 立绘 PNG 共 6 张并排平铺。
- **通过标准：** 任意拿 2 张并比，**同一个孙悟空**可被一个未读过 spec 的旁人指认（脸型/毛色/头冠造型/盔甲层次/棒身比例的累计辨识度 ≥ 5/6 锚点）。
- **失败处置：**
  - 1 镜偏离 → 重渲那一镜（Kling 与 Seedance 都重；优先 Kling 因为是 i2v + 立绘锚定）。
  - ≥ 2 镜偏离 → 检查那些镜的 prompt `角色:` 字段是否字节等同 `characters/main.md`（自动化 Level 3 应已捕到；如未捕，是 Level 3 漏检，记 `validation.issue.raised` 升级补 Level 3）。

### 3. 美术风格寄存器（FR-18 / FR-19、agent_refs/project/ai_video.md "黑神话美术风"锚）

- **操作步骤：**
  1. 把成片 `wukong_juexing_v1.mp4` 在播放器里以**正常速度**完整看一遍；
  2. 看完后做**寄存器 5 选 1 自检**：成片整体**最像**下面哪一种？
     - (a) 黑神话·悟空美术风（沉重写实、影石质感、暖灰金/黄昏紫主调）✓ 唯一允许
     - (b) 86 版西游记现实主义戏剧妆 ✗
     - (c) 京剧脸谱 / 戏曲 ✗
     - (d) 二次元 / cel-shading / Q 版 ✗
     - (e) 低多边形 / 体素 ✗
- **通过标准：** 用户答 (a)；并能指出**至少 2 处**具体证据（如"shot 03 棒身金属反光是黑神话级 PBR 不是动画反光"、"shot 02 山岳轮廓压重心、空气透视分明"）。
- **失败处置：**
  - 整体偏 (b)/(c)/(d)/(e) → 检查 `prompts/shotNN_*.md` 是否丢了"黑神话·悟空美术风"锚或丢了 `negative_prompt:` 禁用 token；如 prompt 无误，是渲染端不可控漂移 → 调高 Kling `cfg_scale:` / 在 Seedance `约束:` 里加强反义；本条重渲。
  - 单镜偏 → 仅重那镜。

### 4. 调色板"黑神话味"目检（FR-15 / FR-16 / FR-17 / NFR-3）

- **操作步骤：**
  1. 在 `style_guide.md` 的 7 行调色板表（暮色青 / 紫金底 / 鎏金高光 / 暖橘金 / 山岩灰褐 / 逆光金边 / 文人浅墨 等）里挑 **3 个核心 hex**：`#6B4226`、`#C9A96E`、`#F2A65A`；
  2. 对成片每一镜暂停一帧，用取色器（系统/Photoshop/任意）在金属/光束/远山三点取色。
- **通过标准：** 3 个核心 hex 在成片中**有迹可循**（取色 ΔE ≤ 12 即算命中），且没有大面积出现表外不在调色板上的高饱和色（霓虹蓝 / 亮粉等）。
- **失败处置：**
  - 大面积表外色 → 检查那镜的 `光线/色调:` 是否仅用 vocab token；若 prompt 合规仍漂 → 渲染端 cfg_scale ↑ + seed 换；重渲。

### 5. 钩子可视性 — 前 2 秒（FR-28 / FR-29、ai_video.md 必备动作 #5 hook 锚）

- **操作步骤：**
  1. `wukong_juexing_v1.mp4` 从 t=0 开始**只**播 0–2 s 然后停；
  2. 自问：如果这是抖一下指头就划走的 Shorts feed，**这 2 秒**会不会让我**停**下手指？
  3. 在 t≈2.0 s 暂停一帧，观察：是否爆发峰值（裂石+金光迸射）就在此刻发生？
- **通过标准：** (a) 0–0.5 s 内已经有显著动作起手（不是黑屏 / 慢入）；(b) t≈2.0 s ±0.3 s 命中爆发峰值；(c) 旁人首看会"咦"一下。
- **失败处置：**
  - 爆发不在 t≈2 s → 重渲 shot01（Kling 与 Seedance 都重；强化 prompt `动作:` 段的 "0–2 秒：金光在 t≈2 秒达到峰值" 措辞）。
  - 0–0.5 s 静止过头 → shot01 prompt `动作:` 加一句 "frame 0 即起势，无静态停留"。
  - 仍不抓人但峰值时点正确 → 是创意问题不是合规问题，做**用户判定**：可接受 v1 / 触发阶段 4 局部重生（仅改 shot01 立意）。

### 6. 缩略图独立可读性（FR-29 缩略图契约）

- **操作步骤：**
  1. 从 `renders/final/shot01.mp4` 的 t=2.0 s 抽一帧导出为 `renders/thumbnail_candidate.png`；
  2. 把这张静帧**单独**放到一个白底背景里看（模拟 YouTube Shorts 信息流缩略图大小，约 320×180 直至 9:16 等比缩略）；
  3. 自问 4 件事：
     - 单一焦点？（裂石 + 金光迸射在视觉中心上 2/3 处）
     - 调色板合规？（暖灰金 / 紫金底 / 暖橘金 是否清晰可辨）
     - 识别度？（一眼能看出是 "孙悟空 + 觉醒"，哪怕没看过视频）
     - 不靠文字？（v1 没有文字叠层，纯视觉是否成立）
- **通过标准：** 4 项全 yes。
- **失败处置：**
  - 焦点散 / 多焦点 → 重渲 shot01 用更强的 `镜头:` 中心构图（push-in 或 dolly + 焦点向裂石收紧）。
  - 缩略图认不出是悟空 → 矛盾：成片 on-model 但缩略图认不出，通常是**头部不在画面**问题；shot01 prompt `镜头:` 段加 "保留头冠或上半身入框" 约束；重渲 shot01。

### 7. 闭环（loop-back）首尾呼应（FR-30 / FR-31）

- **操作步骤：**
  1. 抽两帧并排：`shot01.mp4` 的 frame 0 + `shot05.mp4` 的最后一帧；
  2. 然后看成片末尾，让播放器循环一次，观察 t=38s 跳回 t=0s 的接缝。
- **通过标准：**
  - 两帧构图（机位、焦距、主体框定、棒/角色相对位置）肉眼判定**可叠合**（差异仅在光强：开 = 金光 burst-peak；末 = 余烬冷尾衰减）；
  - 成片循环一次，接缝处**没有**跳切违和感（不是"硬切回开头"，而是"光衰落 → 光重生"）。
- **失败处置：**
  - 构图不叠合 → 重渲 shot05（强化 prompt `# 回环契约` 块的存在和 frame-by-frame 措辞；可让 Kling 用 shot01 frame 0 做 image-ref 的 reverse-match）。
  - 光衰落不到位 → 重渲 shot05 的 `光线/色调:`，强化"金光 fading / 余烬冷尾"vocab。
  - 接缝感强 → 在外部剪辑器试 0.3–0.5 s 交叉淡化（注意 spec 的 v1 已声明这种过渡 AI 端不做；剪辑端做是允许的）。

### 8. 镜间过渡 + 节奏（FR-31、shotlist.md 连续性 tokens）

- **操作步骤：**
  1. 看成片，专注**镜间衔接**：01→02 应为 hard cut；04→05 应为 match cut（构图/动作向上一镜末态对齐）；02↔03、03↔04 走默认。
- **通过标准：** 04→05 用户能感到一个"动作或构图被接住"的 match-cut 时刻（不是另一个硬切）；其他过渡不违和。
- **失败处置：**
  - 04→05 不像 match cut → 检查 shot04 末态描述与 shot05 首态描述是否在 `连续性 tokens` 里对齐；不对齐则改 shotlist + 两镜 prompt 的 `镜头:` / `动作:` 末态/首态；重渲 shot04 末段或 shot05 首段。

### 9. 整段电影感（subjective、agent_refs/general.md 原则 4）

- **操作步骤：** 完整看 1 遍成片，闭眼回想，自问："这 38 秒是**一个连贯的觉醒瞬间**，还是**5 张漂亮图的幻灯片**？"
- **通过标准：** 答"一个连贯的觉醒瞬间"，并能用一句话讲出弧线（hook 裂石 → 远眺山河 → 棒起气劲 → 高潮释放 → 余烬归位）。
- **失败处置：**
  - 答"幻灯片" → 通常是镜与镜之间情绪不递进。检查 shot 03（climax）的强度是否真的高于 shot 02、shot 04 是否真的有"释放"质感。可能要重 shot 03 或 shot 04；或回阶段 4 局部重生 narrative arc。

### 10. 第三方旁观验证（可选但强烈推荐）

- **操作步骤：** 把 `wukong_juexing_v1.mp4` 发给一个**没读过**这个 spec 的人，问 3 个问题：
  1. 看完一句话讲它讲了什么？
  2. 这是哪个 IP / 美术风？
  3. 有没有让你记住的瞬间？
- **通过标准：**
  - Q1 答案出现"觉醒 / 变身 / 顿悟 / 起势"任一关键词；
  - Q2 答出"黑神话悟空"或"中国神话写实风"或"西游记电影感"；
  - Q3 能具体指一个时刻（通常应该是 t≈2 s 的爆发或 shot 03 的高潮）。
- **失败处置：**
  - Q1 完全 miss → 视频叙事失败，回阶段 4 改 narrative arc。
  - Q2 答成"动漫"或"游戏 CG" → 美术寄存器漂；回 §3 / §4 复检。
  - Q3 都没记住 → hook 太弱或 climax 太弱；回 §5 / §9 复检。

### 11. 最终镜次表（hook / climax / loop）签出

- **操作步骤：** 在脑里（或纸上）逐项填：
  - hook 镜（shot01）首 2 s 在哪一帧爆发？_____ s
  - climax（shot03）峰值在哪一秒？_____ s
  - loop-back（shot05 末帧）和 shot01 frame 0 是否构图叠合？是 / 否
- **通过标准：** 三栏与 spec 锁定值（FR-28: t≈2s；FR-21: shot03 在 13–21s 区间内；FR-30: loop-back 叠合）一致。
- **失败处置：** 不一致条 → 对应那镜重渲。

### 12. 每镜单独"过得去"自检

- **操作步骤：** 把 5 段单独循环看，每段问 1 句："这一段如果只发它一个 5–10 s 短片，能不能发？"
- **通过标准：** 5 段都答"能"。
- **失败处置：** 某段答"不能" → 该段重渲（如果是 on-model 问题，强化 `角色:` 字段；如果是节奏，调 Seedance 的 `0–N 秒:` 时间段；如果是构图，调 Kling 的 `镜头:`）。

### 13. Render-side 异常清扫

- **操作步骤：** 5 段成品逐段查肉眼级渲染瑕疵：
  - 多余手指 / 多生肢 / 五官畸变？
  - 文字水印 / 字幕 / logo 残影？
  - 闪烁 / 鬼影 / 动作畸变？
  - 现代元素穿帮（手表、塑料、霓虹灯等）？
  - 多人出现（v1 应该全程**单人**，孙悟空一个角色）？
- **通过标准：** 5 段全部干净。
- **失败处置：**
  - 出现禁项 → 检查 Kling 的 `negative_prompt:` 是否完整列出 + Seedance 的 `约束:` 是否涵盖；漏的项加上再渲那镜。
  - prompt 完整但渲染端仍漏过 → 换 seed 重渲；或上 Kling 3.0 / Seedance 2.0（NFR-1 允许付费档使用）。

---

## 碎片碎补（Spec carve-out 复核）

`general.md` 原则 6 的硬性要求：阶段 5 必须把每条 Out-of-Scope 浮出水面、向用户确认其有意 / 不与实际产物冲突。逐条做：

| # | Out-of-Scope 条目 | 复核问题 | 实际产出有冲突吗？ | 用户裁决 |
|---|---|---|---|---|
| OS-1 | 多角色场景 | 5 镜里有没有任何蛛丝马迹的第二角色（影子 / 远处人形 / 模糊轮廓）？ | □ 无 / □ 有 → 重渲该镜 | □ 确认 v1 单角色 |
| OS-2 | 多集 / 连载结构 | publish.md / README 有没有暗示"下集"或"第 N 部"？ | □ 无 / □ 有 → 改文案 | □ 确认 v1 单短片 |
| OS-3 | 音轨 / 音乐 / 音效 prompt | 渲染端有没有自动加上音轨？（Seedance/Kling 默认通常静音，但需肉眼/耳确认） | □ 静音 / □ 有声 → 剪辑端去音 | □ 确认 v1 静音 |
| OS-4 | 文字叠层 / 对白 / lip-sync | 5 段里有没有**意外**生成的文字（标题 / 字幕 / 角色嘴型说话）？ | □ 无 / □ 有 → 重渲（negative_prompt 列入"文字水印 字幕"） | □ 确认 v1 纯视觉 |
| OS-5 | 跨平台变体（抖音 / 视频号 / Reels） | publish.md 是否还是只有 YouTube Shorts 主版（跨平台仅作 appendix）？ | □ 是 / □ 否 → 删多余 | □ 确认 v1 仅 YouTube Shorts |
| OS-6 | 阶段 6 实拍渲染（pipeline 不渲） | 用户确实是**自己**在外部跑了 Seedream / Kling / Seedance 的吧？（不是父代理偷渲） | □ 是 / □ 否 → 调查异常 | □ 确认外部渲染 |
| OS-7 | 英文 publish 变体 | publish.md 是否纯中文？（除允许的英文技术 token）| □ 是 / □ 否 → 改回中文 | □ 确认 v1 仅中文 |
| OS-8 | 独立封面 Seedream prompt | shot01 t≈2s burst-peak 这一帧是否真的承担了缩略图角色？（与 §6 联动） | □ 是 / □ 否 → 复制 §6 失败处置 | □ 确认 v1 不另出封面 prompt |
| OS-9 | `#BlackMythWukong` tag 沿用 | publish.md 的 hashtag 列表里**没有** `#黑神话悟空` 或 `#BlackMythWukong`？ | □ 无 / □ 有 → 删 | □ 确认避让 IP |
| OS-10 | AI 不可控的精确帧过渡（白闪等） | 成片有没有用到 0.3–0.5s 白闪？（v1 spec 已声明 AI 端不做；外部剪辑可加但需用户自决） | □ 无 / □ 有（剪辑端添加，用户已决） / □ 有但是 AI 误生成 → 重渲 | □ 确认与 spec 一致 |

> 任意条出现"实际产出与 carve-out 冲突" → 这是 `general.md` 原则 6 定义的 **contract drift**（critical），不是 scoping 误会；写 `validation.issue.raised` 事件，severity=`critical`，halt manual_walkthrough，回溯到对应阶段（多数是 4 或 6）做局部修正后重走相关条目。

---

## 签出条件

manual_walkthrough 通过的硬条件，**全部**满足才能签出：

1. **走查脚本 §1–§13** 全部"通过"，或个别项失败已按§失败处置闭环并复测通过；
2. **Spec carve-out 复核** 10 条全部勾选"确认"，**无** contract-drift 升级；
3. 用户在脑里能**一句话**复述视频弧线（hook 裂石 → 山河远望 → 棒起气劲 → 觉醒高潮 → 金光归位），并对成片整体满意度 ≥ 7/10（主观但用户自评）；
4. 用户在 `agent_team` 父代理的对话里回报字面：**"manual walkthrough 通过 — wukong_juexing v1 可发布"**。

签出后父代理写两条事件到 `events.jsonl`：

```json
{"ts":"<now>","type":"validation.pass","level":"manual_walkthrough","unit":"wukong_juexing","note":"user-confirmed; all 13 walkthrough items + 10 carve-out items resolved"}
{"ts":"<now>","type":"pipeline.halted","reason":"done","unit":"wukong_juexing","note":"v1 ready for user-side YouTube Shorts publish"}
```

随后用户可按 `publish.md` 的 §发布时段建议（周四/周五 19:00–21:00 北京时间）发布。

---

> 任何走查项**不确定**怎么判 → 不要自己拿主意，**回 `agent_team` 父代理**报"manual_walkthrough 第 N 条不确定 + 看到了什么 + 期望什么"，由父代理在循环内裁决。原则 4 的本意：人工走查不是**人工糊弄**，而是**人工把关**。
