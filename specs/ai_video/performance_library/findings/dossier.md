# Findings dossier — performance_library

Run: performance_library-20260613-014942

四个 research angle 全部 `status: complete`（2 个 high / 2 个 medium confidence）。本 dossier 合成出 stage-4 spec 可直接继承的：① 经实证验证的四维 schema 基础 ② 首批 10 情绪 seed 清单与优先序 ③ entry schema 形态 ④ 验证机制设计 ⑤ 物理动作权威词汇底表。

## Angles researched

1. **acting-method-taxonomy**（confidence high）— 斯坦尼/Laban/Chekhov/Hagen/Meisner/FACS 如何把"情绪"拆成可导演的物理动作，哪些分类轴可借入四维 schema。
2. **facs-microexpression**（confidence high）— FACS 面部动作编码(AU) → 各情绪规范 AU 组合 → 中文可见画面；强度 A–E 标度；压抑/泄漏机制。
3. **cdrama-performance-tropes**（confidence medium）— 国内短剧高频情绪（按功能主轴而非基本情绪）+ 每情绪可识别表演套路 + 配套镜头惯例。
4. **ai-video-acting-controllability**（confidence medium）— Kling/Seedance 2025 对表演/情绪/微表情描述词的真实服从性；起始帧 vs 纯文本；过火来源；双模型差异。

## Cross-cutting insights

- **【最强结论】"写物理动作、不写情绪标签"被两个完全独立的 angle 各自独立推导出同一条铁律。** 表演学（Stanislavski 物理动作法："情绪无法被指挥，动作可以"）与 AI 模型实测（Segmind：裸情绪名"feels emotional"被忽略/欠渲染，列举肌肉动作"eyebrows draw together slightly, eyes lower gradually"得 4.7/5）从舞台教学和工程测试两端汇聚到完全相同的规则。这是整个库最 load-bearing 的设计约束，必须是 stage-4 的硬规则。*(acting-method-taxonomy + ai-video-acting-controllability)*
- **四维 schema 没有一个轴是凭空发明的，全部有真实 pedagogy 背书。** 强度 1–5 ≈ FACS 的 per-AU A–E 强度标度（A 痕迹→E 极致）；风格(内敛/外放) ≈ Laban Effort 的 Flow bound↔free + Weight/Time 组合，且 ≈ Chekhov MFFR 的 Molding(内敛压抑)↔Radiating(外放爆发)；载体(面部/眼神/肢体/呼吸) ≈ FACS AU 分区 + 复合=Chekhov Psychological Gesture；情绪只是 index key。*(acting-method-taxonomy + facs-microexpression)*
- **"过火"是模型相关的（model-correlated），不只是 prompt 写法问题——这恰好为双模型验证门提供了硬理由。** 实测：Kling 倾向 aggressive/theatrical 过投射（过火风险高），Seedance 倾向 restrained/cinematic（欠演风险高，subtle beat 可能不达意）；且 AI 模型在强度区间的"中段"最可控、两端（micro 被丢、extreme 变僵）都失败。短剧行业也并存"土味浮夸"与"精品微表情"两派。⇒ 过火必须**按模型分别打分**，不能合并；"≥1 模型达标即通过"成立，但须记录哪个模型过、各自分数。*(ai-video-acting-controllability + cdrama-performance-tropes)*
- **高强度 entry 应配"表情已到位的起始帧"，这与现有 shot schema 的起始帧/结束帧块天然咬合。** 实测：纯文本最难的恰是强度天花板（rage/嚎啕/shock 变僵）；短剧实战里强度 5（崩溃嚎啕/扶墙滑坐）又是高频承重 beat。起始帧已含峰值表情 ⇒ 模型只需做"动作插值"（更可靠）而非"从文字合成峰值表情"。ai_video.md rule 12.4 的 `## 起始帧` 块正好是承载点。*(ai-video-acting-controllability + cdrama-performance-tropes + 既有 ai_video.md schema)*
- **表演与镜头强耦合，entry 不能只写表演、要带配套镜头。** 短剧证据：特写吃微表情（人物占画 70%+）、升格慢镜吃高光情绪帧、冷调=压抑/暖调=新生与表演同步切换、"事件→反应→反转→再反应"要求承受方 reaction shot。⇒ entry schema 应含一个选填 `配套镜头:` 块（景别/运镜/色调）。*(cdrama-performance-tropes + ai-video-acting-controllability)*
- **情绪轴应按"功能"选、用"基本情绪 AU 核"写。** 行业按 爽感/痛感/欲望/惊悚 四功能主轴组织情绪（非教科书六基本情绪平铺）；但 FACS/表演学给的精确物理词汇是按六基本情绪的 AU 核。二者不冲突而是分工：seed 清单按功能主轴选 10 种复合情绪，每条 entry 的 body 用对应基本情绪的 AU 核 + 修饰层写出（如"压抑隐忍"= 悲/怒 AU 核 + 抑制肌 AU23/24/17 + bound flow）。*(cdrama-performance-tropes + facs-microexpression + acting-method-taxonomy)*

## Per-angle highlights

### acting-method-taxonomy
- Stanislavski 物理动作法 = 全库第一铁律：entry body 是可观察动作/主动动词，情绪只做索引。
- Laban Effort 四因子（Weight/Time/Space/Flow）是 强度+风格 的引擎：内敛压抑=bound flow+sustained+held weight（Wring/Press）；外放爆发=free flow+sudden+strong weight（Punch/Slash）。建议每条带内部 LMA tag（可不出现在最终 prompt 串）作为"这条到底算压抑还是爆发"的机检清单。
- Chekhov MFFR 给 复合载体 一个现成二级标签（Molding↔内敛 / Radiating↔外放）；Psychological Gesture 概念验证"复合"= 一个融合 面部+眼神+肢体+呼吸 的单一动作 icon。
- Hagen/Meisner 是"生成情绪的过程方法"，对图像模型无输出串等价物——从 entry 内容里剔除，只在 README 里作为"每条 entry 应叠 ≥2 载体"的理由（Conditioning Forces）。

### facs-microexpression
- 交付了 17 个 load-bearing AU 的"AU→中文可见动作"底表 + 7 情绪的"规范 AU 组合→中文画面"表（见下方"物理动作底表"）。
- 强度 1→5 的权威授权规则：**多为同一 AU 集在 A→E 升强度，外加后段招募张口 AU（AU25/26/27）**——不是换一组肌肉。强度1=单区/痕迹，强度5=全集/极致/张口。
- 风格=内敛 ≠ "外放的弱化版"，而是三层叠加：泄漏的真情绪 AU（低强度/单区）+ 可见抑制肌 AU（AU23/24/17/14、吞咽、控制下颌）+ 上下脸冲突（眼/眉泄漏而嘴强行平复）。**眼睛先泄漏**（下脸比上脸更易随意控制）⇒ 眼神是内敛情绪的最高信号载体。
- 两个高价值判别器要写进 entry：AU6 在否=真笑/假笑；AU4 在否=恐惧/惊讶。蔑视是唯一规范的**单侧不对称**表情。
- 强忍应分子类型：强忍泪水/强压怒火/强装镇定，抑制肌签名不同，各成独立 entry。

### cdrama-performance-tropes
- 提议 10 情绪首批清单 + 每条可直接进 prompt 的物理 beat + 配套镜头（见下方"首批 seed 清单"）。
- 四维映射极贴实战：强度=哭戏"递进式表演"（含泪不落2→红眼眶颤抖3→扶墙滑坐4→嚎啕5）；风格=行业现成"隐忍式 vs 炸裂式"二分；实战多为"复合"载体。
- 镜头-表演耦合惯例：特写/中近景主导、升格+逆光+90°运镜、冷暖调即情绪载体、反应镜头结构、定格+音效留白。
- ⚠ 诚实 gap：狠戾/愤怒/委屈/不屑 四条物理 beat 标 [综合]（基于摘要+通用表演常识，一手长文被 403/登录墙挡），落库前建议拉片复核；confidence=medium。

### ai-video-acting-controllability
- 裸情绪名被忽略；命名肌肉动作+视线锚点+强度副词("slightly/subtly/gradually")才 land。可控带在强度中段；两端失败（micro 丢、extreme 僵）。
- 起始帧"锁定构图/光照/风格，比纯文本更精确"——但无公开的"同表情 文本 vs 起始帧"对照 A/B；我们的控制变量渲染正是这个缺失实验。
- Kling vs Seedance 反向失败（Curious Refuge 5 测 Seedance 4 胜，更克制/电影感；Kling 更 aggressive/theatrical + 偶发口型漂移）⇒ 双模型门保留、按模型记分、不塌缩成单一 pass/fail。
- ⚠ 全部实测为英文 prompt；中文表演指令是否同样表现**未经公开验证**，需早期校准渲染。

## 物理动作底表（stage-4 直接继承，author entries off this）

**AU → 中文可见动作**（17 个 load-bearing，prompt 用中文画面、AU 号仅作 metadata 不进 prompt body）：
AU1 眉内角上提(忧)／AU2 眉外梢上挑／AU4 皱眉下压(川字纹)／AU5 上睑提瞪眼／AU6 颧肌堆起眼眯弯(真笑标记)／AU7 下睑收紧眼神凌厉／AU9 皱鼻／AU10 上唇抬露上齿／AU12 嘴角斜上拉(微笑)／AU14 嘴角内收(蔑视/勉强)／AU15 嘴角下拉(倒八字)／AU17 下巴上推噘嘴／AU20 嘴角水平拉扯(恐惧)／AU23 双唇收紧变薄／AU24 双唇用力相压(强忍)／AU25/26/27 唇分/下颌松落/大张口／AU43 闭眼。

**情绪 → 规范 AU 组合 → 中文画面**（established EMFACS/Ekman coding）：
- 喜：AU6+AU12（开口大笑加 AU25/26）→ 嘴角上扬+眼周堆起眯弯；缺 AU6=假笑。
- 悲：AU1+AU4+AU15(+AU17) → 眉内角上提+眉间皱+嘴角下拉(+噘嘴)；微表情常只露 AU1+AU4，眼神先垮。
- 惊：AU1+AU2+AU5+AU26 → 全眉抬+瞪眼+张口；**无 AU4**（与恐惧分水岭）。
- 惧：AU1+AU2+AU4+AU5+AU7+AU20+AU26 → 眉抬又皱+瞪眼下睑紧+嘴角横扯+张口；含 AU4。
- 怒：AU4+AU5+AU7+AU23 → 压眉瞪眼+下睑紧+双唇抿压；微表情常只露 AU4+AU7。
- 厌：AU9+AU15+AU16（或 AU10）→ 皱鼻+上唇抬+嘴角下拉露下齿。
- 蔑：AU12+AU14 **单侧** → 单边嘴角内收上提(不对称冷笑)。

## 首批 seed 清单（10 情绪，按题材承重力优先序）

① 压抑隐忍（痛感）② 爽感反转/扬眉吐气（爽感）③ 崩溃失控（痛感）④ 狠戾/阴鸷（痛→爽）⑤ 震惊错愕（惊悚）⑥ 柔情/深情（欲望）⑦ 委屈/装可怜（欲望/痛感）⑧ 不屑/嘲讽（爽感）⑨ 羞辱难堪（爽感反向）⑩ 外放愤怒（痛/爽）。前 5 覆盖 爽感+痛感+惊悚 三主轴，是打脸/复仇/重生 的承重墙，应先把四维槽位铺满做范例。每情绪含物理 beat + 配套镜头底稿（见 angle-cdrama-performance-tropes §2b）。

## Recommendations for the spec

1. **硬规则：每条 entry 的 body 写可观察物理动作+主动动词，严禁裸情绪名。** 情绪是 index key，body 是"颤唇+下垂湿润目光+屏息"而非"悲伤"。（两 angle 互证，最高杠杆。）
2. **四维 schema 定稿并锚定权威标度**：强度 1–5 = FACS A–E（schema doc 写明 A–E gloss 供作者一致校准）；风格 内敛/外放 = LMA Flow bound/free（每条带内部 LMA tag 作机检）；载体 面部/眼神/肢体/呼吸/复合（复合=Chekhov PG，带 MFFR 标签）。
3. **entry schema 增两个块**：选填 `配套镜头:`（景别/运镜/色调，因表演-镜头强耦合）；`起始帧表情:`（高强度 entry 强烈建议配峰值表情起始帧，咬合 ai_video.md rule 12.4 `## 起始帧` 块）。
4. **风格=内敛 按三层模型独立成块**（泄漏 AU 低强度/单区 + 可见抑制肌 AU23/24/17/14 + 上下脸冲突），不是外放的弱化版。强忍再分子类型：强忍泪水/强压怒火/强装镇定。眼神是内敛的最高信号载体。
5. **验证机制**：双模型(Kling+Seedance)各渲一版控制变量检验视频（固定 actor[取自 `_actors/`]/场景/机位/时长，唯一变量=表演描述）；用户按 表演达意/情绪可识别/是否过火 三轴 1–5 打分；**过火按模型分别打分**；记录哪个模型过、各自分数、以及使用模式（纯文本 vs 起始帧）——库本身成为 text-vs-startframe 与 per-model 服从性的 A/B 数据集。
6. **库布局**：`ai_videos/_performances/{emotion}/perf_NNNN/perf_NNNN.md`（与 `_actors/actor_NNNN` 同构，文件夹装检验视频 mp4 + 起始帧 png）。
7. **引用机制**：shot 代码块顶部 reference-handle 头（对齐 `<char>请参考:` 约定）+ entry 锁定文本块逐字嵌入 `动作:`/`表情:` 字段。
8. **首批范围建议**：先把 ① 压抑隐忍 一种情绪的四维槽位（强度1–5 × 内敛/外放 × 主要载体）做满 + 双模型验证跑通，作为模板范例（pilot），再批量扩展其余 9 情绪——对齐 stage-2 "先打样" 的风险最小化倾向。复合(PNAS 21-blend) v1 暂不强求。

## Open questions surviving research

- **"过火"house style 未定**：库默认走"精品微表情"派还是用风格维度同时容纳两派、由强度上限区分？直接影响"是否过火"的评分锚点。*(cdrama + controllability)*
- **5 级 vs 3 级强度**：FACS 支持 5 级，但短剧 beat 可能实际只用 micro/normal/outburst 3 级；20–40 条/情绪 是否会向两端聚集？*(acting-method + cdrama)*
- **复合(载体=复合)v1 是否入库**：PNAS Du et al. 2014 的 21 类 compound AU recipe 未全量拉取；若 v1 含复合需补 fetch。*(facs)*
- **反派 vs 主角 同情绪差异**：狠戾/愤怒在反派(更油外放) vs 黑化主角(更冷压)beat 不同，是否在情绪下再加"立场"子标签？*(cdrama)*
- **中文 prompt 表演服从性未验证**：所有公开实测为英文；需早期中文校准渲染确认"嘴角微微下垂，眉头轻蹙"类中文肌肉描述是否同样 land。*(controllability)*
- **眼神载体需 FACS 之外的 oculesics 源**：FACS 不编码视线方向/眨眼率/泪膜/瞳孔，而这些是眼神演技核心；眼神 entry 的完整词汇需补一个注视行为学来源。*(facs)*
- **[综合]beat 一手复核**：狠戾/愤怒/委屈/不屑 四条物理 beat 落库前建议拉片或一手长文复核。*(cdrama)*
