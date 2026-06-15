# Spec — performance_library（表演演技库 `_performances/`）

Run: performance_library-20260613-014942
task_type: ai_video ｜ sub_type: N/A（共享资产库，非剧目）

## Goal

在 `ai_videos/` 下建立一个与 `_actors/` / `_voices/` 同级的下划线前缀**共享表演演技库** `ai_videos/_performances/`。库的内容是把人类表演方法提炼成一批 **generic、跨剧目复用、经检验视频实证验证**的表演 prompt 条目（entry），按 **情绪 × 强度 × 风格 × 载体** 四维归类。每条 entry 的核心产出物是一段写成「可观察物理动作」的中文锁定文本块，可逐字嵌入任意短剧 shot prompt 的 `动作:` / `表情:` 字段。库稳定后，任何短剧镜头想要某种演技效果时直接 reference 对应 entry，取代当前每个 shot 现场即兴撰写表演描述的做法。

## Out of scope（v1 明确不做）

- **不是剧目**：不产出 `episodes/`、`script.md`、`shotlist.md`、`publish.md`，不进入 novel/short 流程。库内检验视频只是验证素材，不是成片。
- **不做音频/TTS**：表演 = 视觉表演（面部/眼神/肢体/呼吸的可见动作）。声线归 `_voices/`，本库不下发任何音频 prompt。
- **不在本期实现 webapp 结构化编辑器 / ✨LLM 推荐**：本期 webapp 集成仅限「sidebar 挂载 + 可浏览只读」（FR-12），结构化编辑器与逐栏推荐留作独立 follow-up。
- **不替换既有三部剧的现有 shot prompt**：引用机制（FR-10）只定义并产出"如何 reference"的契约与样例，不回溯改写 `feng_shou_lu` / `mozun_chongsheng` / `nvdi_tuihun_houhuile` 的已有 shot。
- **复合情绪（PNAS 21-blend）不强求入 v1**：`载体=复合` 是单一情绪内多通道联动的旗舰条；跨情绪 blend（如又惊又怕）的 21 类 AU recipe 不在 v1 必做范围。
- **不做自动渲染**：库产出检验视频的**生成 prompt**；实际 Kling/Seedance 渲染与打分由用户在工具侧人工完成（与 `_actors` 试镜照同模式）。

## User roles & primary flows

- **库建设者（Claude，本任务 stage 6）**：按四维 schema 批量撰写 entry（physical-action body + 检验视频生成 prompt + 起始帧 prompt），落盘到 `_performances/{emotion}/perf_NNNN/`。
- **库验证者（用户）**：拿 entry 的检验视频生成 prompt，在 Kling 与 Seedance 各渲一版控制变量视频，按三轴 1–5 打分，把分数/实测笔记回填进 entry，标记验证状态；不通过的 entry 触发修正迭代。
- **库消费者（未来任何短剧的 shot 作者）**：在 shot prompt 顶部写 reference-handle 头引用某 entry，并把该 entry 的锁定文本块嵌入 `动作:`/`表情:` 字段。

**主流程（每条 entry 的生命周期）**：撰写(physical-action body) → 生成检验视频 prompt（控制变量）→ 用户双模型渲染 + 1–5 打分 → 回填实测笔记 + per-model 分数 + 使用模式 → status: `draft → pending_review → validated`（或 `needs_revision` 回到撰写）。

## Functional requirements（编号，逐条可测）

### 库结构与命名

- **FR-1 顶层布局**。库根为 `ai_videos/_performances/`。三级布局 `_performances/{emotion}/perf_NNNN/perf_NNNN.md`，与 `_actors/actor_NNNN/` 同构：每条 entry 一个文件夹，文件夹内除 `perf_NNNN.md` 外存放检验视频 mp4（`perf_NNNN__kling.mp4` / `perf_NNNN__seedance.mp4`）与可选起始帧 `perf_NNNN__startframe.png`（这些是 per-machine、gitignored 的渲染产物）。
- **FR-2 情绪目录**。`{emotion}` 为英文/拼音 slug（如 `yayi_yinren` 压抑隐忍 / `shuanggan_fanzhuan` 爽感反转），中文情绪名记录在该情绪目录下的 `_emotion.md`（情绪定义 + 功能主轴 + 该情绪 entry 清单）。`perf_NNNN` 全局连续编号、零补四位、不随情绪重置（与 actor 编号同风格，便于全局唯一 reference）。
- **FR-3 路径/内容语言**。路径英文/拼音，文件内容中文（继承 ai_video.md rule 1 / rule 13）。entry body、检验视频 prompt、实测笔记全部中文。

### 四维分类 schema（每条 entry 的 frontmatter 必填）

- **FR-4 四维字段**。每条 entry 以 YAML frontmatter 标注四维：
  - `emotion`：10 情绪 seed 之一（见 FR-9）。
  - `intensity`：整数 1–5，锚定 **FACS A–E 强度标度**（1=痕迹/微表情，3=清晰宏表情，5=极致/失控张口）。schema doc 必须写明 A–E gloss。
  - `style`：`内敛压抑` | `外放爆发`，锚定 **Laban Effort Flow**（内敛=bound flow+sustained+held weight；外放=free flow+sudden+strong weight）。
  - `carrier`：`面部` | `眼神` | `肢体` | `呼吸` | `复合` 之一。
  - 选填 `lma_tag`（Weight/Time/Flow 内部机检标签，不进 prompt body）、`mffr`（Molding/Flowing/Flying/Radiating，复合条用）、`stance`（`反派` | `主角` 立场子标签，仅当同情绪需区分时）。
- **FR-5 物理动作铁律（HARD RULE）**。entry 的 body（锁定文本块）必须写成**可观察物理动作 + 主动动词**，**严禁出现裸情绪名作为表演描述**（情绪名只允许出现在 frontmatter `emotion` 索引键与标题）。正例："眉内角上提、嘴角下拉抿紧、屏息后喉头一动"；反例："表现悲伤"。此规则由表演学（Stanislavski 物理动作法）与 AI 模型实测（裸情绪名被忽略）双重背书，是 stage-5/6 validator 的首要校验项。
- **FR-6 物理词汇取自权威底表**。`载体=面部/眼神` 的 body 从 dossier「物理动作底表」（FACS AU→中文可见动作 + 各情绪规范 AU 组合）撰写；AU 编号仅作 frontmatter metadata（`au_ref:`）保留可追溯，**不进 prompt body**（模型读中文画面，不读 "AU12"）。
- **FR-7 内敛=三层模型**。`style=内敛压抑` 的 entry 不是外放的弱化版，body 必须含三层：① 泄漏的真情绪 AU（低强度/单区）② 可见抑制肌（双唇收紧相压/下巴上推抗住嘴角/吞咽/控制下颌）③ 上下脸冲突（眼/眉泄漏而嘴强行平复）。眼神是内敛情绪的最高信号载体（眼睛先泄漏）。强忍按子类型分立 entry：强忍泪水 / 强压怒火 / 强装镇定。
- **FR-8 强度阶梯规则**。强度 1→5 主要是**同一 AU 集在升强度 + 后段招募张口 AU（AU25/26/27）+ 肢体招募**，而非换一组肌肉。同一 (情绪×风格×载体) 的不同强度 entry 应共享情绪核、按此阶梯递增。

### 内容范围

- **FR-9 entry body 标准块**。每条 `perf_NNNN.md` 至少含：① 标题 `# perf_NNNN · {情绪}·强度{N}·{风格}·{载体}` ② 四维 frontmatter（FR-4）③ `## 锁定文本块`（可逐字嵌入 shot 字段的中文 physical-action 串；这是被 reference 的核心产物）④ 选填 `## 配套镜头`（景别/运镜/色调建议——表演与镜头强耦合）⑤ 选填 `## 起始帧表情`（高强度 entry 强烈建议：峰值表情静帧的 Seedream 生成 prompt，咬合 ai_video.md rule 12.4 `## 起始帧` 块）⑥ `## 检验视频`（FR-11）⑦ `## 实测与验证`（FR-13）。
- **FR-10 引用契约（v2，follow-up 007 — 融入而非照抄）**。shot **引用**表演库、按剧情**融入**，不照抄整段：
  1. **标注**：shot.md 的 `## Shot context` 加一行 `表演库参考: perf_NNNN (情绪·强度·风格·载体) — 用于 <角色> <剧情 beat>`（可多条，对应多个角色/beat）。shot 代码块顶部可选带 reference-handle 头 `表演参考: perf_NNNN`。
  2. **融入（非照抄）**：把被引 entry `## 锁定文本块` 的**物理动作要点**改写进该 shot 的 `动作:` / `表情:` 字段——保留"写物理动作不写情绪名"的内核与关键肌肉动作，但**按本 shot 的角色、机位、时长、剧情语境重新措辞**（替换通用主体为本剧角色、贴合本镜时长拆 beat、并入本镜既有走位/台词）。**不要**把 entry 的检验视频 prompt 整段粘进 shot。
  3. shot 标注了用哪些 perf 作 reference，使「更新表演库后可重生成本 shot prompt」可机检（见 FR-17 重生成按钮）。
  - 规则在库稳定后回写 `.claude/agent_refs/project/ai_video.md`（新增"引用表演库"规则）。样例见 `_performances/_reference_usage.md`。

### 渲染-导入工作流（follow-up 002）

- **FR-15 渲染队列 + 一键导入**。提供端到端「复制 prompt → 渲染 → 下载 → 一键归位」流：
  - **导入 tag（v2，generic）**：render 块首行紧凑 tag——检验视频 `演{NNNN}`、起始帧 `演{NNNN}始`（演=演技库标记 / NNNN=perf号；不含模型标记，因一条 entry 一个通用 prompt）。落在 Kling 9 字符截断窗口内且每条唯一（约定见 `_testrig.md`）。
  - **渲染队列**：`{emotion}/_render_queue.md`（`tools/build_render_queue.py` 生成，勿手改）按 entry 顺序列出每块可复制 prompt + 工作流说明。
  - **一键导入**：`POST /api/import-from-downloads` path=`ai_videos/_performances` → `DownloadsImporter.import_performances()`，按下载文件名 `演{NNNN}` 路由到 `{emotion}/perf_NNNN/`：检验视频进 `perf_NNNN/renders/`（保留原名，多模型渲染共存）、`演{NNNN}始` 静帧重命名为 `perf_NNNN__startframe.{ext}`；未匹配 → `_performances/_not_matched/`。侧栏 `_performances` 根有「📥 导入检验视频」按钮。

### 双评分者评分闭环（follow-up 004）

- **FR-16 你 + Claude 评分 + 合议（对 prompt 统一打分，follow-up 006 去模型维度）**。评分针对**这条唯一通用 prompt**，不分渲染模型。每条 entry 的 `## 实测与验证` 是双评分者表（**你** / **Claude**，各一行 × 三轴 1–5：表演达意 / 情绪可识别 / 是否过火）。单轴达标=达意≥4 ∧ 可识别≥4 ∧ 过火≤2。**合议**：双方均达标 ⇒ `accept`(validated)；双方都评过但未同时达标 ⇒ `revise`(needs_revision)；一方未评 ⇒ `pending`。
  - **你评分**：webapp 每个 perf 页面顶部「表演评分」面板（三轴按钮 + 笔记 + 保存）→ `POST /api/perf-score`（`PerfScorer.update_scores_text` 重算合议）。
  - **Claude 评分**（能力边界：读图不读 mp4）：`tools/extract_perf_frames.py`（cv2 抽帧到 `renders/_frames/`）→ Claude 看帧 → `tools/perf_rate.py`（复用同一引擎写 Claude 行）。连续动作流畅度标注为静帧推断。
  - revise 时按失败轴改 prompt（达意↓=词汇具体化/拆 beat；可识别↓=补判别器 AU/补内敛第三层；过火↑=降副词/改起始帧）。

- **FR-17 shot「按表演库重生成」按钮（follow-up 007）**。webapp shot 页面（路径匹配 `/shots/*/shot*.md`）若 shot.md 含 `表演库参考:` 标注，显示「🎭 按表演库重生成」按钮 → `POST /api/regen-shot-prompt {path}`（`ShotRegenPromptReader`）：解析标注的 perf IDs、读各 entry **最新** `## 锁定文本块`、连同本 shot 的 `## Shot context` 组装一份 copy-paste 重生成 prompt（指令=按剧情融入而非照抄、只改表演字段），返回供用户粘进 Claude Code 重新融入。更新表演库后即可一键重生成引用它的 shot。

### 检验视频与验证机制

- **FR-11 通用检验视频 prompt（v2，follow-up 003 — generic）**。每条 entry 的 `## 检验视频` 含**一个通用、model-agnostic 的** prompt（不再分 Kling/Seedance；二者本就字节相同）。库级常量见 `_performances/_testrig.md`：① **演员=用户上传的任意 actor 参考照**（image-to-video）——考察演技，actor 可替换；prompt 不固定演员，同一情绪内比较 entry 时建议用同一张参考照使「唯一变量=表演描述」成立 ② **场景=简洁表演室**（无宏大布景/道具）③ 景别=近景 ④ 机位=正面平视、镜头静止 ⑤ **时长=按 beat 分配（4–15s，非固定，follow-up 005）**：强度1=4s / 2–3=5s / 4=7s / 5=9s，显式多拍渐进条按拍数 ~2.5s/拍（8–15s，时间窗等比放大）；15s 是上限非目标（短 beat 配长时长会诱发模型填充）。由 `tools/set_perf_durations.py` 分配。 ⑥ **灯光=按当前情绪氛围**（取自 `{emotion}/_emotion.md` 的「灯光氛围（检验视频）」行；取舍：灯光承载情绪氛围而非全局中性，同情绪内统一灯光+演员以保表演为唯一比较变量）⑦ 画幅=9:16 ⑧ prompt 骨架固定：除 `[演员…]` 行、灯光、`{{锁定文本块}}` 外逐字节相同。高强度/微表情条另配 `## 起始帧表情`（基于上传 actor + 峰值表情的 Seedream 静帧，作 image-to-video 起始帧）。
  > 早期 v1 的「固定 actor_0001 + 中性灰墙 + 中性白光 + Kling/Seedance 双 prompt」设计已被本 generic 设计取代（用户反馈：库要 generic、演员自上传、表演室够用、灯光按情绪）。
- **FR-12 webapp 最小集成**。`_performances/` 挂入 ai_video_management webapp 的 sidebar 并可只读浏览；本期**不**做结构化编辑器、不做 ✨推荐、不做 promote。集成范围以"能在 webapp 里浏览 entry markdown + 检验视频"为限。generic TreeReader walker 自动遍历（零代码即可浏览）。**nav label 显示中文**（follow-up 001）：库根经 README H1 `《表演演技库》` 由 `_project_zh_title` 解析；各情绪目录由 `tree__reader._sidecar_zh_label()` 从 `{emotion}/_emotion.md` H1 取中文名（剥除 `（拼音）`）设为 `display_name`。路径仍英文/拼音，仅显示层中文。
- **FR-13 验证门与实测回填（每条可测）**。一条 entry 的 `## 实测与验证` 含三个派生字段（`validation_status` / `validation_round` / `passing_models`）+ 一张**渲染记录表**（每行 = 一次 模型×模式 实测）：列为 `模型 | 版本/日期 | 模式(纯文本|起始帧) | 表演达意 | 情绪可识别 | 是否过火 | 通过 | 实测笔记`，三轴各 1–5，**过火按模型逐行分别判**（过火 1=自然克制、5=严重过火，越低越好；锚点按精品微表情派偏严）。**单模型通过**：该行 `表演达意≥4 且 情绪可识别≥4 且 过火≤2` ⇒ ✓。`passing_models` = 所有 ✓ 行的模型集合（grep 派生）。**验证通过判定**：`passing_models` 非空（≥1 模型达标）⇒ `validated`。`status` ∈ `draft | pending_review | validated | needs_revision | blocked`。
  > **D4（消费盲区）**：`passing_models` 是强制字段，且 `## 实测与验证` 必含一行 `消费提示:` 显式写明"在哪个渲染器上 land / 在哪个上需起始帧或降档引用"——因 Kling/Seedance 反向失败，一条"只 Seedance 过"的 entry 被消费者用 Kling 渲染会拿到未通过的表演。FR-10 的 reference-handle 头联动带渲染器提示（如 `表演请参考: _performances/perf_NNNN (seedance-validated)`）。
  > **迭代**：未达标 → `needs_revision`，按失败轴诊断改写 body（达意↓=词汇具体化/拆 beat/加视线锚点；可识别↓=补判别器 AU/补内敛第三层/升强度档；过火↑=降强度副词/高强度改 mode=起始帧）→ 重测。单条封顶 3 轮（CLAUDE.md 迭代上限）；同一失败轴连续两轮同因复现即熔断、置 `blocked`、不阻塞其余 entry。
  > **D6**：`intensity=1`（微表情）易系统性卡达意，允许其 mode 默认=起始帧（峰值静帧兜底），不放宽阈值。

## Non-functional requirements

- **NFR-1 跨剧目零耦合**。库不 import 任何具体剧目；entry 的 body 不得含剧目专有名词/角色名/场景名。它是 generic 资产。
- **NFR-2 锁定串字节稳定**。`## 锁定文本块` 一旦 validated，跨所有引用它的 shot prompt byte-identical（契约同 ai_video.md rule 4 角色锁定描述符）。修订须升 entry 或显式记 divergence。
- **NFR-3 渲染产物 gitignored**。检验视频 mp4、起始帧 png 是 per-machine 可重生缓存，进 `.gitignore`；git 只追踪 markdown（entry + 实测笔记）。
- **NFR-4 验证状态从文件派生**。entry 的 validated/draft 状态以 frontmatter `status` 为准、可被 grep 派生统计；不依赖任何外部存储（对齐 CLAUDE.md 状态面确定性）。
- **NFR-5 re-validation 节奏**。Kling/Seedance 版本漂移会使服从性结论失效；entry 实测笔记须记录验证所用模型版本/日期，库 README 写明"模型大版本更新后高强度 entry 需复验"。

## Acceptance criteria summary（完整准则在 stage 5）

- 库根 `ai_videos/_performances/` 存在，三级布局正确，编号全局唯一零补四位。
- 每条 entry 四维 frontmatter 完整、status 合法；body 满足物理动作铁律（无裸情绪名作表演描述，validator 可 grep）。
- 内敛条满足三层模型；面部/眼神条物理词汇可回溯到 FACS 底表。
- 每条 entry 含控制变量检验视频 prompt（Kling+Seedance 双版，仅表演描述为变量）。
- `_performances/_testrig.md`（固定测试台常量，FR-11）在任何 `perf_NNNN` 之前产出；`_performances/_calibration.md`（中文 vs 英文锁定文本块校准渲染结论，OQ-5）作为 stage-6 第一个 work_unit、先于任何 entry 产出，结论入 README。
- 至少一个情绪（建议 ① 压抑隐忍）的四维槽位（强度1–5 × 内敛/外放 × 主要载体）铺满，作为 pilot 范例，并跑通双模型验证回填 ≥3 条 validated。
- 至少 1 个完整"entry → 嵌入 shot prompt"引用样例。
- `_performances/` 在 webapp sidebar 可见且 entry markdown 可浏览。
- 库 README（中文）含：库定位、四维 schema 说明（含 FACS A–E gloss）、引用用法、验证流程、模型版本复验说明。

## Open questions（进入 stage 5/6 时一并决议；autonomous 下取建议默认并内联标注）

- **OQ-1 过火 house style** — ✅ **已决议（2026-06-13）：库默认"精品微表情"派**，过火评分锚点偏严（追求克制/电影感）。`style` 维度仍区分内敛/外放，但"外放爆发"指强度/通道铺张，不等于土味浮夸；validator 以精品派为基准判过火。
- **OQ-2 强度粒度**：5 级（FACS 支持，建议保留）还是短剧实际只用 3 级（micro/normal/outburst）？建议 schema 保留 5 级但 seed 内容可不必每级填满。
- **OQ-3 v1 情绪批量范围** — ✅ **已决议（2026-06-13）：pilot-first**。stage 6 先只做「压抑隐忍」一种情绪，把四维槽位（强度1–5 × 内敛/外放 × 主要载体）铺满做成样板范例 + 跑通双模型验证回填 ≥3 条 validated，验证 schema 后再批量扩其余 9 情绪（后续 stage-4/6 regen 批次）。
- **OQ-4 立场子标签**：狠戾/愤怒是否需 `stance: 反派|主角` 区分（反派更油外放、主角更冷压）？建议设为选填、仅在 beat 确有差异时用。
- **OQ-5 中文 prompt 校准** — ✅ **已决议（2026-06-13）：做**。stage 6 第一个 work_unit 即中文 vs 英文校准渲染（取压抑隐忍·强度3·内敛一条，语义等价中英两版锁定文本块，沿用固定测试台、唯一变量=语言，双模型各渲中/英）；结论写 `_performances/_calibration.md`。若中文系统性低于英文（达意/可识别差≥2）触发 spec 级警报、需调 body 撰写规则。
- **OQ-6 眼神 oculesics 源**：眼神 entry 需 FACS 之外的注视行为学词汇（视线方向/眨眼率/泪膜/瞳孔）；是否在 stage 6 补一个 mini research？建议 pilot 阶段按需补。
