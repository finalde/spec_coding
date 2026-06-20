# AI 短剧全链路生产流程 — 设计蓝图 v1.0（已定稿·待 build）

> 状态：**定稿（32 题访谈已完成）**，据此批量建 skill / playbook / 模板。
> 定位：未来所有 AI 短剧的生产基石；`task_type=ai_video` 走本流程，取代 agent_team（仅视频侧）。
> 所有流程/知识文件统一 `ai_videos__` 前缀 + **中文后缀**（中文已实测可注册）。
> 本期范围：**阶段 1–6（产出标准化 AI 分镜 Prompt 即止）**；阶段 7 批量渲染+剪辑暂不做。

---

## 1. 全局贯穿原则
**生产铁律**：3 秒钩子 / 15 秒小反转 / 单集结尾强悬念；文字四层分离（剧情/台词/镜头/渲染不混写）；人物锁死（面部+服化+声口）；台词三类区分（口头对白/内心独白/系统UI）；运镜先情绪后机位。
**三大机制（贯穿每阶段，见 §6）**：① 每步 QC 关卡（强制过关才进下一步）；② 每次 update 默认复核（跑受影响范围 review + 记 changelog）；③ 反馈→进化（每条实战反馈 surgical 更新对应 skill/playbook/ref + 记教训）。
**交互默认**：**interactive**——每阶段先用多选题问用户、用答案细化再生成（用户可随时说"这段自动"跳过提问）。

---

## 2. 命名规范（全中文后缀）
| 现 skill | 新名 |
|---|---|
| 审查总编排 | `ai_videos__审查总编排` |
| 台词大师 | `ai_videos__台词大师` |
| 站位朝向 | `ai_videos__站位朝向` |
| 运镜 | `ai_videos__运镜` |
| 动作表演 | `ai_videos__动作表演` |
| 光线色调 | `ai_videos__光线色调` |
| 时长节奏 | `ai_videos__时长节奏` |
| 剧情连贯 | `ai_videos__剧情连贯` |
| 全剧序列 | `ai_videos__全剧序列` |
| 格式契约 | `ai_videos__格式契约` |
| （新建总编排） | `ai_videos__全流程编排` |

改名 = 重命名文件夹 + 改 frontmatter `name:` + 全局替换 `.claude/**/*.md` 里的 `ai_video__*` 引用（`ai_video.md` 无 `__`，不误伤）。旧 `one_piece_research`/`prompt_generator`/`ai-short-drama` 退役（新流程不引用；其有用工艺拆进对应 playbook）。

---

## 3. 项目文件夹结构（阶段编号目录，一眼看出属于哪步）
```
ai_videos/{name}/
├── 1_立项/concept.md
├── 2_世界观人设/{world.md, characters/{角色}/…, scenes/{场景}/…, props/{物件}/…, casting.md, style_guide.md}
├── 3_大纲/arc_outline.md
├── 4_剧本/episodes/epNN/{script.md, dialogue.md}
├── 5_6_分镜与prompt/episodes/epNN/{shotlist.md, shots/shotNN/shotNN.md, all_shot_prompts.md, shots/shotNN/subtitles.md}
└── README.md（中文，全剧门面）
```
- 阶段 5、6 产物**合一在 shotNN.md**（先写运镜设计字段、再校五层 prompt 契约）。
- 新项目默认用此结构；`wushen_juexing` 现有产物保留、可选迁移（不强制、不重跑）。

---

## 4. 锁定的全局默认（访谈定稿）
| 维度 | 默认 |
|---|---|
| 首要赛道 | 古风玄幻 / 仙侠复仇（重生·逆袭·打脸·藏锋）；pipeline 自适应其它赛道 |
| 单集时长 | 90–120s |
| 篇幅 | 自适应（立项定总集数，长/中/短篇皆可） |
| 目标平台 | 红果/番茄 + 抖音/快手 + 海外 YouTube/TikTok；统一 9:16 母版，中英双语 subtitles |
| 世界观特效 | **藏锋·无外放**（无金光/瞳光/外放威能，力量靠体内暖流+表演） |
| 人设锁定 | 面部辨识特征 + 服饰配色发型 + 说话风格模板 **全必锁**；标志小动作（加分） |
| 单集结构 | 固定 **起-承-转-钩尾** 四段 |
| 钩尾类型库 | 危机/杀机 · 情感/身世 · 实力/藏锋将显 · 信息/秘密（每集结尾择一预埋） |
| 台词 | 强口语（脱口而出·短句·语气词）；白话禁古语；OS 仅关键节点 |
| 系统 UI | 鎏金对话框·极简冷冷·仅主角可见·【】选项按钮 |
| 配音 | 三声线解耦（对白对口型 / OS·系统不对口型）·后期 mux（voice_id 全剧锁定） |
| 运镜 | 情绪→运镜映射表（先定情绪目的再出机位）；影视化动态运镜默认优先 |
| 单镜时长 | 3–15s·按 beat 给（由 `ai_videos__时长节奏` 裁决） |
| 生成模型 | 即梦 Seedance + 可灵 Kling（model-agnostic schema，文件名区分 variant） |
| 渲染风格 | 影视级真人写实仙侠（全剧统一渲染样式串） |
| 负面词 | **全剧固定负面词块·必填**：人脸变形/五官漂移/多余发光/画面文字/畸形肢体/夸张金光/现代服饰 |
| 字幕 | prompt 零字幕·后期自加 |
| 一致性 | 锁定描述符 byte-identical + voice_id 锁（契约级）+ Seedream ref 图 + turntable；场景 bg 代号+场景档；ref 图在阶段二生成；多角色同框同角色只具名一次 |
| 质量门 | 每阶段强制过关（blocker 清零）才进下一步；严格度=严 |

---

## 5. 六阶段详规（每阶段：内建提问清单 → 输入 → 输出物 → QC 关卡 → 避坑）
> 「内建提问清单」即 playbook 里 interactive 模式默认问用户的题（源自本次 32 题访谈）；括号内为已锁默认值（推荐项）。

### 阶段 1 · 核心创意立项 → `1_立项/concept.md`
- 提问：赛道题材(古风玄幻/仙侠复仇) · 单集时长(90–120s) · 总集数/篇幅 · 目标平台(红果+抖音+海外) · 核心爽点主线(1 句) · 核心人物对立(主角+反派+关键配角+暗线) · 每集硬钩规则。
- 输出：立项策划单 concept.md。
- QC：人工确认（主角诉求+敌人动机+长线伏笔齐全）。避坑：杜绝模糊脑洞，必须有长线伏笔（玉佩/黑影式暗线）。

### 阶段 2 · 世界观 + 锁定人设 → `2_世界观人设/`
- 提问：时代/地域(古风) · 力量体系+特效尺度(藏锋无外放) · 势力划分 · 角色清单 · 每角色面部锁定特征/服化色发/说话风格模板/标志小动作 · voice_id 选定。
- 输出：world.md（bg 代号/力量规则/势力）+ characters/{角色}/{角色}.md 人物卡（含 Seedream ref 图 prompt + turntable）+ scenes/{场景}/ 场景档 + casting.md（voice_id）+ style_guide.md。
- QC：`ai_videos__格式契约`（锁定串 byte-identical / voice_id / 零 hex / 场景 bg 档齐全）。避坑：人脸/服装漂移靠人物卡复制锁死；藏锋规则写进力量体系防 AI 乱加特效。

### 阶段 3 · 分集大纲 → `3_大纲/arc_outline.md`
- 提问：总集数切割 · 每集「上集承接+本集核心+下集伏笔」 · 起承转钩四段的镜数/时长预算 · 每集钩尾类型(危机/情感/实力/信息)。
- 输出：arc_outline.md。
- QC：`ai_videos__剧情连贯` + `ai_videos__全剧序列`（跨集承接/钩/爽点单调递进/无重复宣告）。避坑：强制标镜号区间防镜与镜衔接断层。

### 阶段 4 · 单集文学剧本 → `4_剧本/episodes/epNN/{script.md, dialogue.md}`
- 提问：本集起承转钩拆段 · 台词口语化强度(强口语) · OS 用量(关键节点) · 系统 UI 风格(鎏金极简) · 三类台词标注。
- 输出：script.md（镜号|时长|场景|画面动作|台词三类标注）+ dialogue.md（纯台词）。
- QC：`ai_videos__台词大师`（说人话/白话/因果/信息量/声口/情绪/节奏）。避坑：严禁跳过剧本直接写 prompt；台词去书面长句/对仗/破折号堆砌。

### 阶段 5 · 分镜运镜设计（合入 shotNN.md）
- 提问：每场景连贯镜序 · 每镜情绪目的→机位映射 · 走位/相对朝向 · 单镜时长(3–15s 按 beat) · 光影色调。
- 输出：shotlist.md + 各 shots/shotNN/shotNN.md 的运镜设计字段（构图机位/动态运镜/走位动作分秒/光影）。
- QC：`ai_videos__站位朝向` + `ai_videos__运镜` + `ai_videos__动作表演` + `ai_videos__光线色调` + `ai_videos__时长节奏`。避坑：先情绪后机位、不堆砌运镜名词；A 不背对 B 说话；同角色只具名一次。

### 阶段 6 · 标准化 AI 分镜 Prompt（合入 shotNN.md）→ `all_shot_prompts.md`
- 提问：目标生成模型(Seedance+Kling) · 渲染风格(影视写实仙侠·全剧统一) · 负面词块确认 · 字幕策略(零字幕)。
- 输出：各 shotNN.md 五层结构（场景bg/锁定角色/剧情分镜动作/光影氛围/渲染参数+**负面词块**）+ 台词配音 prompt + 汇编 all_shot_prompts.md。
- QC：`ai_videos__格式契约`（五层/字段齐全·无字幕·负面词块在·锁定串·字数·比例时长）+ 出片前全 `ai_videos__审查总编排`。避坑：严限特效"无外放威能·人物不自发光"；台词画面剥离；剪影暗线只写轮廓。

---

## 6. 三大机制（活流程的核心）
1. **每步 QC 关卡**：每阶段末跑对应审查 skill，blocker 清零方可进下一步（严格度=严）。由 `ai_videos__全流程编排` 强制。
2. **每次 update 复核**：任何对任一阶段产物的改动/重生，默认跑受影响范围的 `ai_videos__审查总编排` + 在 `specs/ai_video/{name}/changelog.md` 记一条（沿用并扩展 ai_video.md 2026-06-17 amendment 到"每次 update"）。
3. **反馈→进化**：用户每条实战反馈 → surgical 更新对应 playbook / 审查 skill / agent_refs + 记一条"教训"（带来源镜号/反馈引用），落点 = 审查 skill 准则表 + agent_refs（沿用更新协议）。**流程越用越强**——这是本系统的自我进化回路。

---

## 7. 编排器 `ai_videos__全流程编排` 行为
- 识别项目状态（从 `ai_videos/{name}/` 阶段目录派生哪步已完成）→ 决定从哪阶段续。
- 每阶段：先按该阶段内建提问清单 interactive 问用户（多选题）→ 用答案生成产物 → 跑该阶段 QC 关卡 → 不过则回修 → 过关进下一步。
- 断点续：产物落固定阶段目录，状态从文件树派生。
- 范围本期 1–6（出 prompt 即止）。

---

## 8. 实现清单（build 阶段执行）
1. 改名 10 个审查 skill → `ai_videos__中文`，更新全部引用；退役 3 个旧 skill。
2. 新建 `ai_videos__全流程编排` SKILL.md（编排）+ 6 个阶段 playbook + 模板（concept/人物卡/大纲/剧本/五层prompt+负面词块）。
3. 项目结构改为阶段编号目录（新项目；wushen 可选迁移）。
4. 改 CLAUDE.md：task_type=ai_video 路由到本流程、skill 命名约定（ai_videos__中文）、六阶段表注明视频走 pipeline、三大机制。
5. 改 ai_video.md：补负面词块强契约、指向 pipeline。
6. 三大机制写进编排 + CLAUDE.md + 各审查 skill。

---
*v1.0 已 build 落地（2026-06-17）：改名 11 skill、建总编排 + 6 playbook、CLAUDE.md/ai_video.md 路由与负面词契约、格式契约 K15。*
