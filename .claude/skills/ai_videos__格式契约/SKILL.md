---
name: ai_videos__格式契约
description: AI 短剧 prompt 契约/格式机械校验器——不靠审美、纯规则地检查并【直接修正】每个 shot / 每集是否符合 ai_video.md 的硬契约。当用户说"校验一下格式/字段""检查 shot 模板对不对""看看有没有漏字段/带字幕/超字数/hex 没清/锁定串不一致",或在出片前要过一遍确定性规范时触发。它逐项过：文件结构、视频 prompt 字段齐全、台词字段纯净(无字幕信息)、台词配音块与 voice_id、锁定描述符 byte-identical、零 hex、字数上限、比例/时长范围、中文内容/英文路径。能确定修的当场修，含糊的报出来。
---

# 契约校验器（contract checker）

对 `ai_videos/{name}/` 的 shot / 集做**确定性**契约校验——不评判好不好看，只判断**符不符合 `agent_refs/project/ai_video.md` 的硬规则**。能无歧义修正的当场 surgical 改（删字幕行、改错 label、删废止块、补缺字段壳），有歧义的列成 flag 交人。

本 skill 是 `agent_refs/validation/ai_video.md` 与 `ai_video.md` rule 12.4 系列的**机械执行版**——审美类问题归 `ai_videos__审查总编排` 串起来的审查 skill，本 skill 只管"格式对不对"。

## 何时用
- 出片前过一遍格式规范；用户说"校验格式/字段/模板""有没有带字幕/超字数/hex 没清/锁定串不一致"。
- `ai_videos__审查总编排` 的**第一道工序**（机械校验先于审美审查）。

## 输入
- 范围：某 shot、某集（`episodes/epNN/`）、或整个 drama。
- 必读（判定锁定一致性用）：相关 `characters/{中文名}/{中文名}.md`（锁定描述符 + voice_id）、`scenes/{name}.md`、被校验的 `shots/shotNN.md` / `dialogue.md` / `script.md` / `shotlist.md`。

## 校验项（逐 shot / 逐文件过；列严重度 blocker / warning）

| # | 检查 | 不合格信号 | 修法 | 严重度 |
|---|---|---|---|---|
| K1 | **文件结构** | shotNN.md 缺 YAML envelope，或缺 `## Shot context` / `## 视频 prompt` / `## 台词配音 prompt`（有台词镜）段 | 补缺失段壳，按 canonical 顺序 | blocker |
| K2 | **废止块残留** | 出现 `## 起始帧` / `## 结束帧` 静帧块（rule 12.4-H 已废止） | 删整块 | blocker |
| K3 | **视频 prompt 字段齐全** | `## 视频 prompt` 代码块缺任一字段：参考 / 角色 / 角色识别·参考图 / 情节 / 场景 / 镜头 / 走位 / 动作 / 台词 / 光线 / 节奏 / 渲染样式 / 比例 / 时长 | 补缺字段（壳可空待审美 skill 填，但字段名必须在）；脸不写五官文字（2026-06-18 选角供脸） | blocker |
| K4 | **台词字段纯净** | `台词:` 字段内含任何字幕信息（字幕 / 字体 / 字号 / 位置 / 颜色 / 内嵌硬字幕 / 后期软字幕 / 软字幕 / 硬字幕 / 字幕窗 / 鎏金字幕样式…）；或仍用旧 label `台词 / 字幕:` | 删字幕字样、label 改回 `台词:`（字幕由用户后期自加，rule 12.4 v2） | blocker |
| K5 | **台词二标注** | 在画对白未标 `正常台词` / `内心独白`；内心独白未标"嘴唇不动 / 不对口型" | 补类型标注 + 口型指令（rule 12.4-F / 685 行口型契约） | blocker |
| K6 | **台词正文不可剥离** | 有台词镜的 `台词:` 字段被清空（成片会变哑，shot05 教训） | 恢复台词正文；全员无口型镜用"画外配音 voice-over + 禁 lip-sync"而非删文 | blocker |
| K7 | **台词配音块 + voice_id** | 有台词镜缺 `## 台词配音 prompt`；或 voice_id 与该角色 bible 不一致 / 跨集变了（音色一致性铁律） | 补块；voice_id 对齐角色 bible，全剧同角色复用同一 id | blocker |
| K8 | **角色识别标签 byte-identical** | shot `角色:` 行的"角色识别标签"与 `characters/{名}.md` 第 8 行识别标签不逐字相同（跨镜跨集漂移）；**或残留文字五官 / face-differentiator 痣疤五官锚**（2026-06-18 选角供脸：脸由选角图承载，prompt 不写五官） | 用 bible 识别标签覆盖 byte-identical；删任何文字五官描述 | blocker |
| K8b | **选角供脸契约** | 多人物同框 shot 缺「参考图↔画面位置↔识别标签」绑定行（易串脸）；或角色 bible 缺 `妆容` 字段；或 bible 仍含「面貌（眉/眼/鼻/唇/轮廓）」五官行 / face-differentiator 解剖锚 | 多人 shot 补绑定行（rule 12.4-B）；bible 补妆容字段、删五官行 | blocker |
| K9 | **零 hex** | 任何 prompt / 锁定 / 场景档 / style_guide 出现颜色 hex 码（#RRGGBB） | 删 hex，改自然中文色名（rule 12.8 / 12.3 / 12.4） | warning |
| K10 | **字数上限（全局 2000 硬顶）** | 任一生成 prompt 的 ```text body > 2000 字（**含 `情节:`、所有字段一并计**——`情节:` 豁免 2026-06-22 已废；shot 视频 prompt / 场景背景图 / 场景 walk-through 视频 / 角色 turntable prompt 一律全计）——**无 cover-frame / 长 shot / 12.4-E / soft-hard 例外** | 去重合并冗余罗列、砍堆砌，trim 到 ≤ 2000 字（ai_video.md 2026-06-18 全局 2000 硬顶；密度靠不重复而非堆字） | blocker |
| K11 | **比例 / 时长范围** | 比例非 9:16（无项目级 divergence note）；时长 < 3s 或 > 15s | 比例改 9:16 或补 divergence note；时长拉回 3–15s（>15s 拆镜 + 连续性 token） | warning |
| K12 | **路径英文 / 内容中文** | `ai_videos/{name}/` 路径含中文（task_name 应 pinyin/英文）；或文件正文出现非中文 prompt 主体 | 路径改 pinyin（中文标题进 README.md）；正文改中文 | warning |
| K13 | **眼睛不发光** | `光线` / `动作` 写"瞳泛金 / 瞳孔发光 / 瞳心泛金"等发光特效 | 删发光，能量入体改"眉心一缕微光内敛"，眼变化靠表演；`光线` 末尾补"眼里不加发光特效/有色光斑" | warning |
| K14 | **worker 输出 envelope** | `.audit/.../spawns/{id}/output.md` 或 canonical 产物缺 YAML envelope（worker_id/stage/role/status） | 补 envelope（CLAUDE.md § Tool scoping 契约） | blocker |
| K15 | **负面词块必填** | shot prompt 缺 `负向` 段，或负向段缺基线项（人脸变形/五官漂移/多余发光特效/画面文字/畸形肢体/夸张金光/现代服饰） | re-paste `style_guide.md § 负向锁定` 基线（ai_video.md 2026-06-17 负面词块 contract） | blocker |
| K16 | **turntable 统一声样台词** | 实体角色 `characters/{名}/{名}.md` 的 7s turntable 仍残留"一/二/三"中文计数（`朗声"一"` / `中文计数` / `数字计数台词` 表）；或所念声样台词与全剧锁定句不**逐字相同**、不**跨角色 byte-identical** | 替换为锁定统一句 `你好，今天天气还不错，外面很安静。`（**0–2s 念完**、动作不变·turntable 已压到 4s/2026-06-27），跨所有实体角色 byte-identical（ai_video.md 2026-06-18 turntable 声样契约 + 2026-06-27 4s 压缩） | blocker |
| K16b | **建立视频块覆盖（统一建立模式·2026-06-27）** | 任一**命名人形角色卡** `characters/{名}/{名}.md` 缺建立视频块（`# turntable 角色 reference prompt — {N}s 建立视频`〔时长无关·现行 4s〕 + ```text + 统一声样台词表 + turntable 说明）——不分主配、不分出场方式（正脸/全景/背影/远景/剪影一律要）。**仅非人形实体（系统/UI）豁免**（无 turntable·用 UI 浮现块）。**时长须为 4s**（`时长: 4s`、5-phase `0-1/1-1.5/1.5-2.5/2.5-3/3-4`、抽帧 front 0.5/side 2.0/back 3.5；2026-06-27 压缩，残留 7s 即不合格） | 当场补建/改为 4s 建立视频块（mirror 既有角色块结构）：有选角脸的吃选角脸、仅有自身立绘的吃 `cN_名字.png`；念统一声样台词(0–2s)、4s 5-phase locked-framing、≤2000 字、块内无真人演员名（ai_video.md 2026-06-27 amendment） | blocker |
| K17 | **Seedance 审核敏感词（武器特写 / 真实军事地标）** | 生成 prompt 含 刀 / 剑 / 长枪 / 刃口 / 錾纹 / 寒光 等武器特写，或 长城 / 烽燧 / 关隘 等真实军事地标，或真人演员名 / 真实品牌 / 受版权 IP 名（视频审核易判 `generation failed` 拒绝，2026-06-18 实测） | 武器改 甲胄 / 仪仗 / 玄铁器物、删特写 dwell；地标改 山川城垣 / 关山 或泛化「北疆山河图」；真人/品牌/IP 名删（ai_video.md 2026-06-18 审核敏感词替换表） | warning |
| K18 | **跨景别造型一致** | 同一角色在相邻镜变景别（远/中/近/特写）时，造型字段（服装 / 发型 / 妆容 / 道具）出现变化——AI 漫剧第一痛点：远近景服装不统一、纹理突变（红果实测） | 造型字段按 bible 锁定描述符跨景别 byte-identical 对齐，相邻变景别镜零变化（ai_video.md §14.4） | blocker |
| K19 | **无字幕铁律落点齐全（2026-06-20 教训：EP1 shot8 / EP2 shot6 多角色口型对白镜渲染烧了字幕）** | shot 缺以下任一：① `渲染样式` 含「全程无字幕、不烧任何字幕/台词文字」directive；② `负面词` 含 `字幕 / 台词字幕 / 对白字幕 / subtitles / 画面文字`（K15 基线只有"画面文字"、不够，须含"字幕/subtitles"）。**多角色口型对白镜**(≥2 句 `正常台词·口型对`)字幕烧录风险显著更高，却只用基线档 | 补齐两处落点。**口型对白镜按高风险档加强**：`渲染样式` 前置「【全程绝对无字幕·画面不烧任何字幕/台词文字/对白文字/caption】」+ `负面词` 扩到 `中文字幕 / 对白文字 / 台词文字 / 字幕条 / 弹幕 / caption / text overlay`。⚠ 注：prompt 已合规仍出字幕多为**渲染抽卡变异**（同 EP1 shot8）→ 提示用户重 roll，非 prompt 缺陷 | warning |
| K20 | **可锁定 on-画 元素（道具 + 非实体 UI/法宝等）ref/描述符 ↔ 上画可见 双向一致（2026-06-21 教训：① EP3 shot5 玉佩本应藏衣内不外露，却带了 `玉佩=>` ref + 完整外观描述符 → 生成器把玉佩画了出来、没掏的动作就凭空贴上来；② EP3 shot7 系统对话框明明上画，`参考:` 却漏了 `系统=>` ref——系统 UI 也是有锁定卡 `c2_系统` 的 ref-bearing 元素，不是只有道具才进 `参考:`）** | 凡有**锁定卡/锁定描述符**的 on-画 元素——**道具（玉佩/法器/信物）＋非实体可视资产（系统 UI、法宝、觉醒异象图腾等）**——出现 ref↔可见两侧打架：(a) 该镜**实际上画可见**却漏带 `xxx=>` ref 或漏 re-paste 锁定描述符；或 (b) 该镜道具/UI**实际不上画**（情节/走位写明 藏衣内 / 不外露 / 不掏出 / 该镜无 UI），却仍带 ref 或写完整锁定描述符 | **双向校验**（对每个有锁定卡的元素，含系统 UI）：① **上画可见**镜 → 必带 `xxx=>` ref（系统镜带 `系统=>`）+ byte-identical 锁定描述符；② **本镜不上画**镜 → **禁带 ref、禁写完整描述符**，`情节:` 只可点名提及（"衣内玉佩骤热·不外露"）。漏带或该藏却带 = blocker，当场补/删 ref + 描述符。配合 `动作表演` A9（状态须动作驱动）与 `ai_video.md` 道具可见性铁律 | blocker |
| K21 | **台词字段只放台词正文 / 静默镜 `台词: 无`（2026-06-21 教训：EP3 shot9 把"（本镜无台词·默剧静默拍；环境音…）"写进了 `台词:` 字段 → 被生成器当字幕烧进画面）** | `## 视频 prompt` 码块的 `台词:` 字段里出现**非台词 prose**：舞台提示 / 环境音说明 / 旁注（如"（本镜无台词…）""环境音：…""默剧静默拍"）——凡坐在 `台词:` 槽里的文字都可能被渲染成字幕 | `台词:` 只允许"角色〔类型〕：实际台词"逐条，或静默镜写 `台词: 无`。环境音 / 舞台提示 / 旁注一律移出码块（挪到码块外的 `## 台词配音 prompt` 注释或 Shot context）。静默镜同时省略 `## 台词配音 prompt` 内的生成块、仅留码块外环境音注释 | blocker |
| K22 | **静默镜（`台词: 无`）必须带"无人声"负面词（2026-06-21 教训：EP3 shot9 已写 `台词: 无`，成片却仍念出"裴知秋"——生成器从 `角色:`/`情节:` 里抓角色名 TTS 出来；`台词: 无` 单独挡不住）** | 某 shot `台词: 无`（静默/默剧镜），但 `负面词:` 里**缺**人声/配音抑制词——模型会把 `角色:`/`情节:` 中的角色名或文字读成画外音 | 静默镜 `负面词:` 必须含一组人声抑制词：`人声 / 配音 / 旁白 / 念白 / 念出角色名或台词文字 / 任何生成人声音轨 / no voiceover / no speech / no narration`。**人声抑制只写进 `负面词:`**——⚠ **禁止把这组话写进 `台词:` 槽**（`台词: 无` 必须保持干净、否则违反 K21 被当字幕烧进画面）；`台词:` 仍只写 `无`，无人声诉求全靠 `负面词:` 承载。**且只对静默镜加**——**有台词镜禁加人声负面词**（rule 704：Seedance 正是从 `台词:` 文本生成台词配音，加了会把台词音也压哑） | blocker |
| K22b | **系统镜：台词保留 + 明确标女声（2026-06-21 用户定调修正：系统照常念台词、且要女声——直接在 `台词:` 里把系统标成女声让 Seedance 生成女声即可；不静音、不强制 mux、不写"否则男声"啰嗦。原"系统镜须静音+全mux"方案作废、仅作多声轨实测仍乱时备选）** | 系统镜 `台词:` 写成"无"、或系统句**没标女声**（缺 `女声·SYS-gold-01·女性系统提示音`）→ Seedance 默认 TTS 男声；或仍残留"视频静音/不生成人声/后期mux/否则男声"旧啰嗦 + 人声抑制负向（会把系统声也压没） | 系统镜 `台词:` **保留台词正文**，系统句标 `〔女声·SYS-gold-01·女性系统提示音·不对口型〕`、主角句标 `〔OS·男声·不对口型〕`，让 Seedance 按标注生成（系统女声/主角男声）；**删"静音/不生成人声/否则男声/mux"啰嗦 + 人声抑制负向**。⚠ 仅多声轨实测音色仍乱才 fallback mux（备选·非默认） | blocker |
| K23 | **场景 plate folder 完整性 — index 行 ↔ `{plate}/{plate}.md` ↔ shot `参考:` handle 三方一致（2026-06-21 教训：EP4 新建 `镇主街`/`镇演武场` 只写了父卡 + index 表、per-plate folder 全标"待建"没建，shot 却已 `参考: 镇主街_bg1_城门=>` 引用不存在的 plate；此类"scene 缺 bg 子文件夹"反复出现）** | 任一 ① `scenes/{名}/{名}.md` 的「背景图系统 index」表里某 plate 行**缺**对应 `scenes/{名}/{plate}/{plate}.md` 文件；或 ② 某 shot `参考:` 行的 `{场景}_{plate}=>` handle 在场景里**找不到**对应 plate folder/.md；或 ③ 场景卡把 per-plate 写成「待建/stage5/6 渲染前」却已被 shot 引用（v3 canonical scene template item 9：folder-per-plate 是**建卡当场必做项**、非"待建"，ai_video.md） | **当场补建**缺失的 `scenes/{名}/{plate}/{plate}.md`（image→image 图生图 prompt：首行=`{plate}` 路由 handle + `参考:` 全局底图 + 主体/视角/光线/风格/负向/比例，纯背景无人物，复用本场景锁定描述符与全剧渲染串）；把场景卡 index 尾注的"待建"改为"已创建·PNG 待渲"。PNG 底图 gitignored、可留待实际出图 | blocker |
| K23b | **plate 命名约定 + 方位 token 跨 drama 互斥（2026-06-21 教训：EP4 plate 命名 `bg3_街角茶棚`（漏切 `bg{N}_方位_描述`）→ 方位 token 变整坨"街角茶棚"⊃"街角"，与 EP2 `集市长街/bg2_街角_摊位` 的方位 token"街角"撞车 → DownloadsImporter 查到 2 候选无法消歧 → 导入失败 not_matched）** | plate folder 名 ① 不是 `bg{N}_{方位}_{描述}` 三段式（缺第二个 `_`、方位段是长描述 blob）；或 ② 其**方位 token**（`bg{N}_` 后第一段）与本 drama 任一其它 plate 的方位 token 互为子串 / 相等（importer 用 `方位 token in 下载文件名` 匹配，下载名取自 plate 首行 handle；非互斥→多命中→拒投或误投，downloads__writer.py `_match_plate_any_scene`） | 重命名为 `bg{N}_{方位}_{描述}`，**方位段取短、与全 drama 现有方位 token 互斥**（建卡前先列全 drama 已有方位 token 避让：如 街角/顺街/庙内/镇口/朝北…）；同步改 plate folder + 内层 `{plate}.md` 首行 handle + 场景卡 index + 所有 shot `参考:` 的 `{场景}_{plate}=>` handle（byte-identical 三方一致）；自检：每个 plate 方位 token 在「全 drama plate 名集合」里只唯一命中自身 | blocker |
| K24 | **每集 stage5/6 交付件完整性（2026-06-21 教训：EP4 生成 stage5/6 时建了 shots/ + all_shot_prompts.md + intro_cards.md，却漏了 `shotlist.md`——EP1/EP2/EP3 都有；此类"某集少一个标准交付件"与漏 plate folder 同源·反复出现）** | `5_6_分镜与prompt/episodes/epNN/` 缺以下任一标准交付件：① `shotlist.md`（镜头清单总表）；② `all_shot_prompts.md`（全镜 prompt 汇编）；③ `shots/shotNN/shotNN.md`（逐镜·数量对齐 shotlist）；④ 含重要角色首登/复用的集缺 `intro_cards.md`。**对照同 drama 其它集的交付件集合自检**（其它集有、本集无 = 漏件） | **当场补建**缺失件：`shotlist.md` 照同 drama 既有集格式（头部集信息 + `镜｜内容(情绪目的)｜出场角色｜景别+运动｜时长｜标记` 表 + 运镜锚），从本集 `4_剧本/script.md` + 各 `shotNN.md` 派生；`all_shot_prompts.md`（派生只读快照）**跑 `python tools/build_all_shot_prompts.py <epNN_dir>` 从各 shotNN.md 聚合生成、禁手改/手抄**；`intro_cards.md` 列本集字卡 | blocker |
| K25 | **角色 ≥2 镜复用必有卡+ref（2026-06-21 教训：EP4 `测资执事` 出现 6 镜·`菜鸡少年`/`围观武者甲乙` 各 2 镜，却被当"群像内联·不锁定"没建角色卡没 ref 图 → 跨镜面孔漂；场景有"≥2 镜立档"门槛、角色漏套用）** | 某角色名（台词配音块 `角色:` 行 / 视频 prompt `角色:`·`群像:` 行的命名角色）在**≥2 个 shot** 出现，却 ① 无 `characters/cN_{名}/cN_{名}.md` 角色卡；或 ② 出现它的 shot `参考:` 行漏 `cN_{名}=>` ref handle；或 ③ shot `角色:` 识别标签与卡第8行不 byte-identical。**对照"哪些角色名出现≥2镜"自检**（纯 1 镜一次性龙套豁免） | **当场补建**轻量角色卡（参 c7/c9–c12：8 字段锁定描述符 + voice_id + Seedream ref 立绘 prompt·首行路由 handle `cN_{名}`）；出现它的每个 shot `参考:` 行补 `cN_{名}=>` + `角色:` re-paste byte-identical 识别标签。角色卡≠出场字卡（字卡仍只重要角色发）| blocker |
| K26 | **跨镜首帧承接落点三方一致 + 结构化首末帧字段 + body 无跨镜 meta（ai_video.md 2026-06-21 (H)/(H2)；写法见 `agent_refs/project/ai_video_shouweizhen.md`）** | shot ① `## Shot context` 缺 `衔接:` 行（每镜必写 `承接 shot{NN} 末帧（首帧＝上一镜末帧）` 或 `硬切（独立首帧）` 其一；每集首镜须为硬切）；或 ② `衔接:`=承接，却缺落点任一——`参考:` 行最前的 `本镜首帧=>` handle（缩短形）/ `Reference uploads` 的「上一镜末帧…」行 / `参考:` 行**下方**的结构化首末帧指令（`首末帧:` 或 `首帧:`，见 ai_video.md (H)）；或 ③ `衔接:`=硬切，却残留 `本镜首帧=>` handle / 末帧 upload 行 / 首末帧字段（硬切镜禁挂）；或 ④ 某镜是**交接源**（下一镜 `衔接: 承接 本镜`）却缺 `尾帧锁定:` 行 / `参考:` 行末尾 `本镜末帧=>` handle / `参考:` 下方的 `末帧:`(或`首末帧:`)指令；或 ⑤ **视频 prompt body 残留跨镜/工作流 meta**（`承 S\d`/`接 S\d`/`接 shotN`/`顺承接 shotN`/`同场景跨镜一致`/`同场景接 shotN 光线一致`/`供下镜承接`/`承 SN 同一人`/`diegetic…`/`(上一镜末帧)`·`(重生时上传)` 括注/`【写死·防对空气…】`/`【全程绝对无字幕…】`/日期·follow-up 编号——模型只生成单镜读不懂、占字数、字幕类提醒还反噬，ai_video.md (H)） | 补 `衔接:` 行（承接/硬切判定归 `运镜` M8、本 skill 只校字段在场 + 落点齐全/互斥）；承接镜补齐缩短 handle + upload 行 + 首末帧指令；硬切镜删残留；交接源镜补 `尾帧锁定:` 行 + `本镜末帧=>` handle + 末帧指令；⑤ 删净 body 内跨镜/工作流 meta（连贯由 byte-coherent 落点 + 相邻镜 check 兜底） | blocker |
| K27 | **Seedance 2.0 全能参考 @标签 + 首尾帧角色分配（`参考分配:` 字段）齐全（ai_video.md 2026-06-22 amendment·research-backed）** | shot `参考:` **≥2 项**（多参考·几乎每镜·universalize 2026-06-23），却 ① 缺 `参考分配:` 行（`参考:` 行下方紧跟、把每项映射 @图N→角色/场景）；或（有首/尾帧承接的镜额外）② `参考分配:` 缺 `@图X为首帧` / `@图Y为尾帧` 句（首尾帧未派角色）；或 ③ `@图N` 句柄编号与 `参考:` 上传清单顺序不一致 / 非 byte-identical（`@图1` 写成「第一张图」「图一」等）；或 ④ `参考分配:` 里改造了主体外观（应只描述首→尾之间的运动·点名 carrier 不变锚点）；或 ⑤ 全能参考素材超槽位（>9 图 / >3 视频 / 视频总>15s / >3 音频 / 混合>12 文件） | 补 / 修 `参考分配:` 行：把 `参考:` 每项映射成 `@图N`/`@视频N`/`@音频N`（按清单顺序、byte-identical），写全 `@图X为首帧(承接上一镜末帧)`+`@图Y为尾帧(本镜末帧)`+`@图Z锁定角色{名}`+`@图W作为场景{bg}参考`(+`参考@视频N运镜`/`@音频N背景音`)，并加「保持角色服装/场景/光线一致、只生成首帧到尾帧之间的运动」；删主体改造措辞；超槽位提示拆镜/减参考。⚠ 仅对有首/尾帧承接的镜要求（纯硬切独立镜可只 `@图1为首帧` 或不写） | blocker |

## 工作流（校验 → 能定就改）
1. 读范围内全部目标文件 + 相关 characters/scenes bible（取锁定串 + voice_id）。
2. 逐 shot / 逐文件过 K1–K27（含 K22b 多声轨 mux、K26 跨镜首帧承接落点、K27 全能参考 @标签+`参考分配:`），列出不合格项（cite 文件:行 / 准则 / 严重度）。
3. **无歧义的当场 surgical 修**（删字幕行、改 label、删废止块、补字段壳、覆盖锁定串、删 hex / 发光）。**有歧义的只 flag**（如字数超且该不该豁免、时长该不该拆镜），交人或交审美 skill。
4. **锁定一致性以 bible 为准**：shot 与 bible 冲突时改 shot，不改 bible（除非用户改的是 bible）。
5. 改后复验：blocker 清零；warning 列清单 + 处置建议。

## 硬约束
- 本 skill **不动剧情 / 台词措辞 / 运镜创意 / 站位审美**——那是审美类 review skill 的职责。只修"格式 / 字段 / 契约"。
- blocker 未清零 = 该 shot 不可出片（stage-6 validation 失败）。
- 审计写进 `.audit/adhoc_agents/{date}/{task_id}/events.jsonl` 的 `validation.issue.raised`（level=contract、severity=blocker/warning、payload=patch）。

## 输出
- 一份 inline patch 清单（文件 / 原行 / 准则 / 严重度 / 改写后）+ 已落地的机械改动 + blocker/warning 计数与复验结论。
