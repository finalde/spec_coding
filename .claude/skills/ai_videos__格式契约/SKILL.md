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
| K10 | **字数上限（全局 2000 硬顶）** | 任一生成 prompt 的 ```text body > 2000 字（shot 视频 prompt 不计 `情节:` 块；场景背景图 / 场景 walk-through 视频 / 角色 turntable prompt 全计）——**无 cover-frame / 长 shot / 12.4-E 例外** | 去重合并冗余罗列、砍堆砌，trim 到 ≤ 2000 字（ai_video.md 2026-06-18 全局 2000 硬顶；密度靠不重复而非堆字） | blocker |
| K11 | **比例 / 时长范围** | 比例非 9:16（无项目级 divergence note）；时长 < 3s 或 > 15s | 比例改 9:16 或补 divergence note；时长拉回 3–15s（>15s 拆镜 + 连续性 token） | warning |
| K12 | **路径英文 / 内容中文** | `ai_videos/{name}/` 路径含中文（task_name 应 pinyin/英文）；或文件正文出现非中文 prompt 主体 | 路径改 pinyin（中文标题进 README.md）；正文改中文 | warning |
| K13 | **眼睛不发光** | `光线` / `动作` 写"瞳泛金 / 瞳孔发光 / 瞳心泛金"等发光特效 | 删发光，能量入体改"眉心一缕微光内敛"，眼变化靠表演；`光线` 末尾补"眼里不加发光特效/有色光斑" | warning |
| K14 | **worker 输出 envelope** | `.audit/.../spawns/{id}/output.md` 或 canonical 产物缺 YAML envelope（worker_id/stage/role/status） | 补 envelope（CLAUDE.md § Tool scoping 契约） | blocker |
| K15 | **负面词块必填** | shot prompt 缺 `负向` 段，或负向段缺基线项（人脸变形/五官漂移/多余发光特效/画面文字/畸形肢体/夸张金光/现代服饰） | re-paste `style_guide.md § 负向锁定` 基线（ai_video.md 2026-06-17 负面词块 contract） | blocker |
| K16 | **turntable 统一声样台词** | 实体角色 `characters/{名}/{名}.md` 的 7s turntable 仍残留"一/二/三"中文计数（`朗声"一"` / `中文计数` / `数字计数台词` 表）；或所念声样台词与全剧锁定句不**逐字相同**、不**跨角色 byte-identical** | 替换为锁定统一句 `你好，今天天气还不错，外面很安静。`（0–3s 念完、动作不变），跨所有实体角色 byte-identical（ai_video.md 2026-06-18 turntable 声样契约） | blocker |
| K17 | **Seedance 审核敏感词（武器特写 / 真实军事地标）** | 生成 prompt 含 刀 / 剑 / 长枪 / 刃口 / 錾纹 / 寒光 等武器特写，或 长城 / 烽燧 / 关隘 等真实军事地标，或真人演员名 / 真实品牌 / 受版权 IP 名（视频审核易判 `generation failed` 拒绝，2026-06-18 实测） | 武器改 甲胄 / 仪仗 / 玄铁器物、删特写 dwell；地标改 山川城垣 / 关山 或泛化「北疆山河图」；真人/品牌/IP 名删（ai_video.md 2026-06-18 审核敏感词替换表） | warning |
| K18 | **跨景别造型一致** | 同一角色在相邻镜变景别（远/中/近/特写）时，造型字段（服装 / 发型 / 妆容 / 道具）出现变化——AI 漫剧第一痛点：远近景服装不统一、纹理突变（红果实测） | 造型字段按 bible 锁定描述符跨景别 byte-identical 对齐，相邻变景别镜零变化（ai_video.md §14.4） | blocker |
| K19 | **无字幕铁律落点齐全（2026-06-20 教训：EP1 shot8 / EP2 shot6 多角色口型对白镜渲染烧了字幕）** | shot 缺以下任一：① `渲染样式` 含「全程无字幕、不烧任何字幕/台词文字」directive；② `负面词` 含 `字幕 / 台词字幕 / 对白字幕 / subtitles / 画面文字`（K15 基线只有"画面文字"、不够，须含"字幕/subtitles"）。**多角色口型对白镜**(≥2 句 `正常台词·口型对`)字幕烧录风险显著更高，却只用基线档 | 补齐两处落点。**口型对白镜按高风险档加强**：`渲染样式` 前置「【全程绝对无字幕·画面不烧任何字幕/台词文字/对白文字/caption】」+ `负面词` 扩到 `中文字幕 / 对白文字 / 台词文字 / 字幕条 / 弹幕 / caption / text overlay`。⚠ 注：prompt 已合规仍出字幕多为**渲染抽卡变异**（同 EP1 shot8）→ 提示用户重 roll，非 prompt 缺陷 | warning |
| K20 | **道具 ref/描述符 ↔ 上画可见 双向一致（2026-06-21 教训：EP3 shot5 玉佩本应藏衣内不外露，却带了 `玉佩=>` ref + 完整外观描述符 → 生成器把玉佩画了出来、没掏的动作就凭空贴上来）** | 该镜道具**实际不上画**（情节/走位写明 藏衣内 / 不外露 / 不掏出 / 看不见），却仍在 `参考:` 带该道具 `xxx=>` ref，或在 `情节:`/`角色:` 写了该道具完整外观锁定描述符——给了生成器"把它画出来"的强信号，与"藏起来"自相矛盾 | **双向校验**：① 道具**上画可见**镜 → 必带 `xxx=>` ref + 锁定描述符（原 rule）；② 道具**本镜不上画**镜 → **禁带该道具 ref、禁写完整外观描述符**，`情节:` 只可点名提及（"衣内玉佩骤热·不外露"）。该藏却带 ref/描述符 = blocker，当场删 ref + 删描述符。配合 `动作表演` A9（道具状态须动作驱动）与 `ai_video.md` 道具可见性铁律 | blocker |
| K21 | **台词字段只放台词正文 / 静默镜 `台词: 无`（2026-06-21 教训：EP3 shot9 把"（本镜无台词·默剧静默拍；环境音…）"写进了 `台词:` 字段 → 被生成器当字幕烧进画面）** | `## 视频 prompt` 码块的 `台词:` 字段里出现**非台词 prose**：舞台提示 / 环境音说明 / 旁注（如"（本镜无台词…）""环境音：…""默剧静默拍"）——凡坐在 `台词:` 槽里的文字都可能被渲染成字幕 | `台词:` 只允许"角色〔类型〕：实际台词"逐条，或静默镜写 `台词: 无`。环境音 / 舞台提示 / 旁注一律移出码块（挪到码块外的 `## 台词配音 prompt` 注释或 Shot context）。静默镜同时省略 `## 台词配音 prompt` 内的生成块、仅留码块外环境音注释 | blocker |

## 工作流（校验 → 能定就改）
1. 读范围内全部目标文件 + 相关 characters/scenes bible（取锁定串 + voice_id）。
2. 逐 shot / 逐文件过 K1–K21，列出不合格项（cite 文件:行 / 准则 / 严重度）。
3. **无歧义的当场 surgical 修**（删字幕行、改 label、删废止块、补字段壳、覆盖锁定串、删 hex / 发光）。**有歧义的只 flag**（如字数超且该不该豁免、时长该不该拆镜），交人或交审美 skill。
4. **锁定一致性以 bible 为准**：shot 与 bible 冲突时改 shot，不改 bible（除非用户改的是 bible）。
5. 改后复验：blocker 清零；warning 列清单 + 处置建议。

## 硬约束
- 本 skill **不动剧情 / 台词措辞 / 运镜创意 / 站位审美**——那是审美类 review skill 的职责。只修"格式 / 字段 / 契约"。
- blocker 未清零 = 该 shot 不可出片（stage-6 validation 失败）。
- 审计写进 `.audit/adhoc_agents/{date}/{task_id}/events.jsonl` 的 `validation.issue.raised`（level=contract、severity=blocker/warning、payload=patch）。

## 输出
- 一份 inline patch 清单（文件 / 原行 / 准则 / 严重度 / 改写后）+ 已落地的机械改动 + blocker/warning 计数与复验结论。
