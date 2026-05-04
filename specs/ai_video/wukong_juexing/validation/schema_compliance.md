# 验证策略 — Level 03: schema_compliance（结构合规层）

Run: `wukong_juexing-20260503-201831`
Stage: 5 (validation strategy)
Level: **schema_compliance** — 文件存在、字段在场、语言合规、双 prompt 在场、画幅+时长枚举、标签数。
Sub_type: `short`（单片 5 镜头平铺）。

输入文件：
- `C:\workspace\spec_coding\specs\ai_video\wukong_juexing\final_specs\spec.md`
- `C:\workspace\spec_coding\.claude\agent_refs\validation\general.md`
- `C:\workspace\spec_coding\.claude\agent_refs\validation\ai_video.md`

预读契约（pre_reading_consulted）记录于本 run 的 `events.jsonl` stage-5 首事件。

---

## 总览

本层的工作面是「机械可判定」的结构合规检查 —— 每一项都能用 `grep`、Python 行级解析或 `os.path.exists` 在数秒内回答 pass / fail。语义层（locked-descriptor 字节相等的全局一致性、首钩+缩略图契约、回环契约、调色板/词表 token 锁）属于 Level 04 (content_lock)；本层只负责**字段在场**与**值落在枚举**。

工作单元映射（见 spec §「Stage-6 work-unit decomposition」）：

| 工作单元 | 本层关心的产物 | 触发的检查组 |
|---|---|---|
| U1 — character bible | `characters/main.md`、`characters/ref_images/main_seedream.md` | §2、§3 |
| U2 — style guide | `style_guide.md` | §4 |
| U3 — narrative | `script.md`、`shotlist.md` | §5 |
| U4 — prompts | `prompts/shot{01..05}_{kling,seedance}.md`（共 10 个文件） | §6、§7 |
| U5 — publish | `publish.md` | §8 |
| U6 — readme | `README.md` | §1 |
| 全局 | 上述全部 `*.md` | §9（语言合规扫描） |

每一项检查严格遵循以下结构：

- **名称 (id)**：在 `events.jsonl` 中以 `audit_event=<id>` 写入。
- **目标文件**：绝对 glob，工作目录无关。
- **通过条件**：可直接转为 Python 表达式 / 正则 / 字符计数。
- **失败严重度**：参考 `agent_refs/validation/general.md` 标准表 + `ai_video.md` 升级表。
- **审计事件 tag**：在 stage-6 由 streaming validator 写入 `events.jsonl`。

严重度速查（合并 general + ai_video）：

| 触发情形 | 严重度 | 是否 halt |
|---|---|---|
| 必备文件缺失（FR-1..FR-8） | `blocker` | 是（3 轮修订上限） |
| 双 prompt 之一缺失 | `blocker` | 是 |
| 画幅 / 时长字段缺失或值越界 | `blocker` | 是 |
| 镜头 > 15 s 或 missing 时长 | `blocker` | 是 |
| 中文内容 < 95% 阈值 | `blocker` | 是 |
| 必备字段（角色/场景/动作/镜头/光线-色调/比例/时长）缺失 | `blocker` | 是 |
| Seedance 文件出现 `negative_prompt:` 或 `[参考图:]` | `blocker` | 是（违反工具能力契约） |
| Kling 文件缺失 `negative_prompt:` 或 `[参考图:]` | `blocker` | 是 |
| publish.md hashtag 数 < 3 或 > 5 / 缺失 `#Shorts` | `blocker` | 是 |
| 标题 > 30 中文字 / 简介越界 [150, 250] | `blocker` | 是 |
| Kling `时长:` 不在 {`5s`, `10s`} 枚举 | `blocker` | 是 |
| Seedance `时长:` 与 FR-21 配额不一致 | `blocker` | 是 |
| 章节缺失（README 4 节 / publish 6 节 / Seedream 10 节） | `blocker` | 是 |
| shotlist 行数 ≠ 5 或缺列 | `blocker` | 是 |
| 任何枚举落在「灰区」（与 spec 完全一致但与某 FR 文字描述微差） | `warning` | 否 |

---

## 检查项

### §1 README.md

绝对路径：`C:\workspace\spec_coding\ai_videos\wukong_juexing\README.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-README-01` | 文件存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.readme.missing` |
| `SCH-README-02` | 4 个二级标题在场 | 文件中按出现顺序匹配 4 个 H2：`## 项目概要`、`## 使用说明`、`## 角色清单`、`## 风格关键词`（精确文字、允许首尾空格） | `blocker` | `validation.issue.raised:schema.readme.section_missing` |
| `SCH-README-03` | 项目概要为单段 | 在 `## 项目概要` 与下一个 `## ` 之间，非空段落数 == 1 | `warning` | `validation.issue.raised:schema.readme.summary_shape` |
| `SCH-README-04` | 使用说明含编号步骤 | 在 `## 使用说明` 块中至少匹配 5 行形如 `^\d+[\.、]` 的有序步骤（对应 spec primary-flow 1..5） | `blocker` | `validation.issue.raised:schema.readme.steps_missing` |
| `SCH-README-05` | 角色清单 ≥ 1 项 bullet | 在 `## 角色清单` 块中至少 1 行 `^- ` | `blocker` | `validation.issue.raised:schema.readme.role_list_empty` |
| `SCH-README-06` | 风格关键词 5–10 项 | 在 `## 风格关键词` 块中以 `、` / `,` / `换行` 拆分后非空 token 数 ∈ [5, 10] | `blocker` | `validation.issue.raised:schema.readme.style_kw_count` |
| `SCH-README-07` | 中文内容率 ≥ 95% | 通过 §9 公共语言扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |

覆盖：FR-1, FR-9, FR-42, NFR-7, NFR-8。

---

### §2 characters/main.md（角色锁定描述符）

绝对路径：`C:\workspace\spec_coding\ai_videos\wukong_juexing\characters\main.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-CHAR-01` | 文件存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.character.missing` |
| `SCH-CHAR-02` | 锁定描述符块起止哨位在场 | 同时匹配（按出现顺序，且开始在结束之前）：开始哨位 `【孙悟空 · 觉醒态 · 锁定描述符 v1】` 与结束哨位 `禁用 卡通线条、cel-shading、二次元大眼、低多边形。` | `blocker` | `validation.issue.raised:schema.character.sentinel_missing` |
| `SCH-CHAR-03` | 块内含「标志性动作」段标 | 在两个哨位之间出现子串 `标志性动作` | `blocker` | `validation.issue.raised:schema.character.signature_section_missing` |
| `SCH-CHAR-04` | 块内字数 ≥ 200 中文字 | 在两哨位之间剔除哨位文本后，中文字符（`一-鿿`）数量 ≥ 200 | `warning` | `validation.issue.raised:schema.character.body_too_short` |
| `SCH-CHAR-05` | 中文内容率 ≥ 95% | 通过 §9 公共语言扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |

注：本层只检查「哨位在场」与「块内字数门槛」。**11 文件锁定描述符字节相等**属于 Level 04 (content_lock)。本层不重复跑该检查，但暴露提取函数 `extract_locked_block(text)` 给 Level 04 复用 —— 见 §10 示例脚本。

覆盖：FR-2, FR-9, FR-11（在场部分；字节相等由 Level 04 校验）。

---

### §3 characters/ref_images/main_seedream.md（Seedream 立绘 prompt）

绝对路径：`C:\workspace\spec_coding\ai_videos\wukong_juexing\characters\ref_images\main_seedream.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-SEED-01` | 文件存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.seedream.missing` |
| `SCH-SEED-02` | 10 段在场 | 按 FR-14 / dossier §4 顺序，10 个 H2/H3 子串均出现：`主体定义`、`面貌细节`、`发型`、`服装`、`身材`、`道具`、`画面控制`、`风格`、`比例`、`负向提示` | `blocker` | `validation.issue.raised:schema.seedream.section_missing` |
| `SCH-SEED-03` | 主体字数 ∈ [250, 400] 中文字 | 剔除 H1/H2/H3 标题行、code fences、URL、英文 token 后，统计 `一-鿿` 字符数 | `blocker` | `validation.issue.raised:schema.seedream.body_length` |
| `SCH-SEED-04` | 比例段含 `9:16` 与「竖构图」 | 在「比例」节内同时匹配 `9:16` 与子串 `竖构图` | `blocker` | `validation.issue.raised:schema.seedream.ratio_missing` |
| `SCH-SEED-05` | 负向提示段非空 | 「负向提示」节中至少一行非空 token（≥ 4 中文字 或 ≥ 1 英文单词） | `blocker` | `validation.issue.raised:schema.seedream.negative_empty` |
| `SCH-SEED-06` | 中文内容率 ≥ 95% | 通过 §9 公共语言扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |

覆盖：FR-3, FR-9, FR-14, NFR-5。

---

### §4 style_guide.md

绝对路径：`C:\workspace\spec_coding\ai_videos\wukong_juexing\style_guide.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-STYLE-01` | 文件存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.style.missing` |
| `SCH-STYLE-02` | 调色板表 ≥ 7 行 | 解析 markdown 表格：定位含表头单元格 `名称` / `hex` / `用途`（任意大小写、容许中英混排）的表，剔除表头/分隔行后数据行数 ≥ 7 | `blocker` | `validation.issue.raised:schema.style.palette_rows` |
| `SCH-STYLE-03` | 每行调色板含 hex 色码 | 表内每行至少匹配一个 `#[0-9A-Fa-f]{6}` | `blocker` | `validation.issue.raised:schema.style.palette_hex_missing` |
| `SCH-STYLE-04` | 6 个光照状态 token 在场 | 在文件全文（剔除 code fences）中匹配 6 个锁定 token：`金光-bursting`、`金光-fading`、`体积光丁达尔束`、`暮光-冷尾`、`月辉-银蓝`、`雷弧-硬白`（具体 6 词以 `findings/angle-visual-style.md §3.3` 为准；本检查依字符串完全匹配） | `blocker` | `validation.issue.raised:schema.style.lighting_tokens_missing` |
| `SCH-STYLE-05` | 5 个动作 pattern token 在场 | 在文件全文中匹配 5 个锁定 token：`定身`、`扫棒`、`腾跃`、`回望`、`持棒压顶`（以 §3.5 为准；字符串完全匹配） | `blocker` | `validation.issue.raised:schema.style.motion_tokens_missing` |
| `SCH-STYLE-06` | 3 条转场规则在场 | 全文匹配 3 个 token：`hard cut`、`match cut`、`overlap cut`（以 §3.6 为准） | `blocker` | `validation.issue.raised:schema.style.transition_rules_missing` |
| `SCH-STYLE-07` | 含画幅声明 `9:16` | 全文存在 `9:16` 且位于含「画幅」二字行 | `blocker` | `validation.issue.raised:schema.style.ratio_row_missing` |
| `SCH-STYLE-08` | 中文内容率 ≥ 95% | 通过 §9 公共语言扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |

注：§4 严格做「token 在场」检查；token 字面量在 stage-6 启动前应由 Level 04 与本 level 共用一份 `vocab.json`（参见 §10 末尾的「下游消费契约」）。如执行时 `vocab.json` 缺失，stage-6 退化为按 spec.md FR-15 与本表枚举的字面量进行字符串匹配。

覆盖：FR-4, FR-9, FR-15, NFR-3, NFR-5。

---

### §5 script.md + shotlist.md

绝对路径：
- `C:\workspace\spec_coding\ai_videos\wukong_juexing\script.md`
- `C:\workspace\spec_coding\ai_videos\wukong_juexing\shotlist.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-SCRIPT-01` | script.md 存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.script.missing` |
| `SCH-SCRIPT-02` | script.md 含 5 个分镜段标 | 全文匹配（不区分大小写）`Shot\s*0?[1-5]` 或 `镜头\s*0?[1-5]` 共 5 处不同编号 | `blocker` | `validation.issue.raised:schema.script.shot_breaks_missing` |
| `SCH-SHOT-01` | shotlist.md 存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.shotlist.missing` |
| `SCH-SHOT-02` | shotlist.md 主表头含 6 列 | 第一张 markdown 表的表头按顺序包含子串：`shot`、`时长`、`景别`、`动作摘要`、`连续性 tokens`、`是否hook`（容许其它列存在；列名容许中英混排但必含上述 6 个子串） | `blocker` | `validation.issue.raised:schema.shotlist.header_columns_missing` |
| `SCH-SHOT-03` | shotlist.md 数据行 == 5 | 剔除表头/分隔行，数据行数严格 == 5 | `blocker` | `validation.issue.raised:schema.shotlist.row_count` |
| `SCH-SHOT-04` | 每行 shot 列匹配 `shot0[1-5]` | 5 行第 1 列正则 `^shot0[1-5]$`，且 5 个编号互异 | `blocker` | `validation.issue.raised:schema.shotlist.shot_id_invalid` |
| `SCH-SHOT-05` | 每行 时长 ≤ 15s 且非空 | 第 2 列 = `^(\d+)s?$` 数值 ∈ [1, 15]（允许尾随 `s`） | `blocker` | `validation.issue.raised:schema.shotlist.duration_invalid` |
| `SCH-SHOT-06` | 时长总和 ∈ [34, 42] | 5 行时长之和 ∈ [38−4, 38+4] | `blocker` | `validation.issue.raised:schema.shotlist.total_duration_window` |
| `SCH-SHOT-07` | 时长枚举与 FR-21 一致 | 按 shot id 排序后 [5, 8, 8, 10, 7] | `blocker` | `validation.issue.raised:schema.shotlist.duration_allocation` |
| `SCH-SHOT-08` | 恰好 1 行标记 hook | 第 6 列出现 `是` / `Y` / `✓` 共且仅 1 行（按 ai_video.md required move #5 — shorts 必须标 hook 镜头） | `blocker` | `validation.issue.raised:schema.shotlist.hook_marker_missing` |
| `SCH-SHOT-09` | hook 行 == shot01 | 该唯一 hook 行的 shot 列 == `shot01`（spec FR-28: 首钩在 t≈2s burst-peak） | `blocker` | `validation.issue.raised:schema.shotlist.hook_not_first` |
| `SCH-SHOT-10` | 每行连续性 tokens 非空 | 第 5 列内容剔除空白后长度 ≥ 1 | `warning` | `validation.issue.raised:schema.shotlist.continuity_empty` |
| `SCH-SHOT-11` | 中文内容率 ≥ 95% | 两文件均通过 §9 公共语言扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |

覆盖：FR-5, FR-6, FR-9, FR-20, FR-21, FR-22, ai_video.md 必备移动 #2 + #5。

---

### §6 prompts/shot{01..05}_kling.md（5 个 Kling 镜头 prompt）

目标 glob：`C:\workspace\spec_coding\ai_videos\wukong_juexing\prompts\shot0[1-5]_kling.md`

每一项检查针对 5 个文件分别执行；任意一文件失败即记 1 个 `validation.issue.raised`。

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-KLING-01` | 5 个文件全部存在 | `glob` 命中数 == 5，且 shot 编号集合 == {01,02,03,04,05} | `blocker` | `validation.issue.raised:schema.kling.missing` |
| `SCH-KLING-02` | 必备字段在场 | 每文件均匹配以下 7 个行级字段 + 2 个特殊行：`角色:`、`场景:`、`动作:`、`镜头:`、`光线/色调:`、`比例:`、`时长:`、`negative_prompt:`、`[参考图: characters/ref_images/main_seedream.md` | `blocker` | `validation.issue.raised:schema.kling.field_missing` |
| `SCH-KLING-03` | 比例值锁定 | `比例:` 行的右值（去空白）== `9:16` | `blocker` | `validation.issue.raised:schema.kling.ratio_invalid` |
| `SCH-KLING-04` | 时长枚举锁定 | `时长:` 行的右值（去空白）∈ {`5s`, `10s`}（Kling 2.1 Pro 硬枚举 — NFR-1, NFR-6, FR-27） | `blocker` | `validation.issue.raised:schema.kling.duration_enum_invalid` |
| `SCH-KLING-05` | 7s/8s 镜头含 `# 渲染说明:` 注释 | 对 shot02 / shot03 / shot05（FR-21 时长 8s/8s/7s 不在 Kling 枚举），文件须含一行以 `# 渲染说明:` 开头的注释，内容含子串 `trim` 或子串 `motion-compressed` 或子串 `渲染至10s` | `blocker` | `validation.issue.raised:schema.kling.render_note_missing` |
| `SCH-KLING-06` | negative_prompt 含禁用 token | `negative_prompt:` 行至少包含子串 `卡通` 与 `cel-shading` 与 `多余手指` 与 `文字水印`（FR-19 + FR-23 的最低门槛；完整 token 列表由 Level 04 校验） | `blocker` | `validation.issue.raised:schema.kling.negative_tokens_insufficient` |
| `SCH-KLING-07` | 角色字段含锁定描述符开始哨位 | 在 `角色:` 行起、至下一字段（任意以 `场景:` 开头的行）止的范围内，含子串 `【孙悟空 · 觉醒态 · 锁定描述符 v1】` | `blocker` | `validation.issue.raised:schema.kling.locked_descriptor_sentinel_missing` |
| `SCH-KLING-08` | 参考图行格式锁定 | 完整匹配 `\[参考图:\s*characters/ref_images/main_seedream\.md` | `blocker` | `validation.issue.raised:schema.kling.refimg_path_invalid` |
| `SCH-KLING-09` | 中文内容率 ≥ 95% | 全部 5 文件均通过 §9 扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |
| `SCH-KLING-10` | 缩略图契约块（仅 shot01） | shot01_kling.md 文件首部含 `# 缩略图契约` 块（H1 或 H2，文件首 30 行内） | `blocker` | `validation.issue.raised:schema.kling.thumbnail_block_missing` |
| `SCH-KLING-11` | 回环契约块（仅 shot05） | shot05_kling.md 文件首部含 `# 回环契约` 块 | `blocker` | `validation.issue.raised:schema.kling.loopback_block_missing` |

注：FR-12（11 文件字节相等）由 Level 04 验证；本层只断言「角色字段中含开始哨位」以快速定位结构错位。

覆盖：FR-7（Kling 半侧）, FR-9, FR-12（在场部分）, FR-23（Kling 半侧）, FR-24（Kling 半侧）, FR-26（Kling 字段集）, FR-27, FR-28, FR-29, FR-30, FR-31, NFR-1, NFR-4, NFR-5, NFR-6。

---

### §7 prompts/shot{01..05}_seedance.md（5 个 Seedance 镜头 prompt）

目标 glob：`C:\workspace\spec_coding\ai_videos\wukong_juexing\prompts\shot0[1-5]_seedance.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-SEED-PROMPT-01` | 5 个文件全部存在 | glob 命中数 == 5，shot 编号集合 == {01..05} | `blocker` | `validation.issue.raised:schema.seedance.missing` |
| `SCH-SEED-PROMPT-02` | 必备字段在场 | 每文件均匹配 11 个行级字段：`角色:`、`场景:`、`动作:`、`镜头:`、`光线/色调:`、`比例:`、`时长:`、`风格:`、`画质:`、`约束:`、`seed:` | `blocker` | `validation.issue.raised:schema.seedance.field_missing` |
| `SCH-SEED-PROMPT-03` | 禁止字段不在场 | 文件全文不出现 `negative_prompt:` 子串（FR-23 — Seedance 没有 negative_prompt 槽位） | `blocker` | `validation.issue.raised:schema.seedance.negative_prompt_forbidden` |
| `SCH-SEED-PROMPT-04` | 禁止参考图行 | 文件全文不出现 `[参考图:` 子串（FR-24 — Seedance t2v 无 image-ref 槽位） | `blocker` | `validation.issue.raised:schema.seedance.refimg_forbidden` |
| `SCH-SEED-PROMPT-05` | 比例值锁定 | `比例:` 行的右值（去空白）== `9:16` | `blocker` | `validation.issue.raised:schema.seedance.ratio_invalid` |
| `SCH-SEED-PROMPT-06` | 时长与 FR-21 配额一致 | 按 shotNN ↦ 时长映射：shot01=`5s`、shot02=`8s`、shot03=`8s`、shot04=`10s`、shot05=`7s`；右值（去空白）须严格匹配 | `blocker` | `validation.issue.raised:schema.seedance.duration_mismatch` |
| `SCH-SEED-PROMPT-07` | 时长 ≤ 12s | 数值部分 ∈ [2, 12]（Seedance 1.0 Pro 接受整数 2..12，NFR-1） | `blocker` | `validation.issue.raised:schema.seedance.duration_out_of_range` |
| `SCH-SEED-PROMPT-08` | 动作字段含时间线分段 | `动作:` 行起至下一字段止的内容中，匹配至少 1 处正则 `\d+\s*[–\-~至]\s*\d+\s*秒` | `blocker` | `validation.issue.raised:schema.seedance.timeline_segment_missing` |
| `SCH-SEED-PROMPT-09` | 时间线段落覆盖整段时长 | 提取所有 `a–b 秒` 段，按 b 排序后最后一段的 b 值 == `时长:` 数值（spec FR-25 + FR-21） | `warning` | `validation.issue.raised:schema.seedance.timeline_coverage_gap` |
| `SCH-SEED-PROMPT-10` | 角色字段含锁定描述符开始哨位 | 在 `角色:` 行起、至下一字段止的范围内，含子串 `【孙悟空 · 觉醒态 · 锁定描述符 v1】` | `blocker` | `validation.issue.raised:schema.seedance.locked_descriptor_sentinel_missing` |
| `SCH-SEED-PROMPT-11` | seed 字段为整数 | `seed:` 行的右值正则 `^\d+$` | `blocker` | `validation.issue.raised:schema.seedance.seed_invalid` |
| `SCH-SEED-PROMPT-12` | 约束字段含禁用 token 的正向反义 | `约束:` 行内出现至少 4 个 token：`五官稳定不畸变`、`同一角色全程一致`、`无文字水印`、`无现代元素`（FR-23 最低门槛；完整 token 列表由 Level 04 校验） | `blocker` | `validation.issue.raised:schema.seedance.constraint_tokens_insufficient` |
| `SCH-SEED-PROMPT-13` | 中文内容率 ≥ 95% | 全部 5 文件均通过 §9 扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |
| `SCH-SEED-PROMPT-14` | 缩略图契约块（仅 shot01） | shot01_seedance.md 文件首部含 `# 缩略图契约` 块 | `blocker` | `validation.issue.raised:schema.seedance.thumbnail_block_missing` |
| `SCH-SEED-PROMPT-15` | 回环契约块（仅 shot05） | shot05_seedance.md 文件首部含 `# 回环契约` 块 | `blocker` | `validation.issue.raised:schema.seedance.loopback_block_missing` |

覆盖：FR-7（Seedance 半侧）, FR-9, FR-13（在场部分）, FR-23（Seedance 半侧）, FR-24（Seedance 半侧）, FR-25, FR-26（Seedance 字段集）, FR-27, FR-28, FR-29, FR-30, FR-31, NFR-1, NFR-4, NFR-5, NFR-6。

---

### §8 publish.md

绝对路径：`C:\workspace\spec_coding\ai_videos\wukong_juexing\publish.md`

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-PUB-01` | 文件存在 | `os.path.isfile(...)` | `blocker` | `validation.issue.raised:schema.publish.missing` |
| `SCH-PUB-02` | 6 个章节在场 | 按出现顺序匹配 6 个 H2 子串：`标题`、`简介`、`Hashtag 规则`、`封面建议`、`发布时段建议`、`跨平台复用` | `blocker` | `validation.issue.raised:schema.publish.section_missing` |
| `SCH-PUB-03` | 标题 ≤ 30 中文字 | 在 `## 标题` 节内提取首条非空非引用的内容行；中文字符（`一-鿿`）数 ≤ 30 | `blocker` | `validation.issue.raised:schema.publish.title_too_long` |
| `SCH-PUB-04` | 标题不含 hashtag 字符 | 标题行不出现 `#` 字符 | `blocker` | `validation.issue.raised:schema.publish.title_has_hashtag` |
| `SCH-PUB-05` | 简介中文字数 ∈ [150, 250] | 在 `## 简介` 节内剔除 hashtag (`#\S+`)、code fences、URL 后，统计中文字符数 | `blocker` | `validation.issue.raised:schema.publish.description_length` |
| `SCH-PUB-06` | hashtag 总数 ∈ [3, 5] | 在 `## 简介` + `## Hashtag 规则` 联合块中匹配所有 `#[一-鿿A-Za-z0-9_]+`，去重后计数 | `blocker` | `validation.issue.raised:schema.publish.hashtag_count` |
| `SCH-PUB-07` | `#Shorts` 强制在场 | 上一项匹配集合中含 `#Shorts`（区分大小写） | `blocker` | `validation.issue.raised:schema.publish.shorts_tag_missing` |
| `SCH-PUB-08` | 标题+简介 hashtag 总数 ≤ 15 | 全文（题+简介）中 `#\S+` 总出现次数（不去重） ≤ 15 | `blocker` | `validation.issue.raised:schema.publish.hashtag_total_cap` |
| `SCH-PUB-09` | 发布时段含必备时段串 | 在 `## 发布时段建议` 节中同时匹配子串 `周四`、`周五`、`19:00`、`21:00`、`北京时间`（FR-41 主时段） | `blocker` | `validation.issue.raised:schema.publish.publish_window_missing` |
| `SCH-PUB-10` | 北美次时段在场 | 在同节中匹配子串 `周四 11:00` 或 `11:00–12:00`（FR-41 次时段） | `warning` | `validation.issue.raised:schema.publish.na_window_missing` |
| `SCH-PUB-11` | 简介首句即钩子句 | 简介首句（首句号 `。`/`!`/`！` 之前）中文字数 ∈ [10, 60] | `warning` | `validation.issue.raised:schema.publish.hook_sentence_shape` |
| `SCH-PUB-12` | 中文内容率 ≥ 95% | 通过 §9 扫描 | `blocker` | `validation.issue.raised:schema.lang.threshold` |

覆盖：FR-8, FR-9, FR-37, FR-38, FR-39, FR-40, FR-41, ai_video.md 必备移动 #6。

---

## §9 语言合规扫描（公共 suite）

依据：`agent_refs/validation/ai_video.md` 必备移动 #1 + `spec.md` FR-9 + NFR-4 + NFR-8。

| id | 名称 | 通过条件 | 严重度 | audit-event tag |
|---|---|---|---|---|
| `SCH-LANG-01` | 路径全英 / 拼音 | 递归遍历 `C:\workspace\spec_coding\ai_videos\wukong_juexing\` 下所有文件与目录，每段路径名仅匹配 `[A-Za-z0-9._\-]+` | `blocker` | `validation.issue.raised:schema.lang.path_not_ascii` |
| `SCH-LANG-02` | 中文内容率 ≥ 95% | 见下方 token 化与计数规则 | `blocker` | `validation.issue.raised:schema.lang.threshold` |
| `SCH-LANG-03` | 无禁用 register 英文 token | 全文（剔除 code fences）不出现 `cartoon style`、`cel shaded`、`anime`、`chibi`（FR-19 register 锁的英文同义词；中文同义词由 Level 04 校验） | `warning` | `validation.issue.raised:schema.lang.forbidden_english_register` |

`SCH-LANG-02` token 化与计数规则（**stage-6 streaming validator 必须按此实现**，与 ai_video.md 必备移动 #1 文字保持一致）：

1. 读入 `*.md` 全文，UTF-8。
2. 移除 code fences（` ``` ... ``` `，多行；`~~~ ... ~~~`）。
3. 移除 YAML frontmatter（首行 `---` 至次个 `---` 之间）。
4. 移除 raw URL：正则 `https?://\S+`。
5. 移除技术 token 白名单（按出现位置整段抠掉）：
   - hex 色码 `#[0-9A-Fa-f]{6}`
   - 画幅 `9:16`
   - 时长 `\b\d+s\b`
   - 参数键名 `\b(negative_prompt|cfg_scale|seed|camera_fixed|input_image_urls|image_url|prompt)\b\s*[:：]`
   - 工具 / 模型名 `\b(Kling|Seedance|Seedream|YouTube|Shorts)\b`
6. 在剩余文本中：
   - `cjk_chars` = `一-鿿` + 全宽标点 `[　-〿＀-￯]` 命中数。
   - `non_space_total` = 剔除 `\s+` 后字符总数。
   - 通过条件：`cjk_chars / max(non_space_total, 1) >= 0.95`。
7. 缺省例外：纯空文件（`non_space_total == 0`）自动 pass，不计入分母。

`SCH-LANG-02` 是其它每个 §1..§8 中「中文内容率」检查的唯一来源 —— 不在每文件单独实现，统一在本 suite 跑一次并将结果路由到对应 audit-event。

覆盖：FR-9, FR-10, NFR-4, NFR-8。

---

## §10 示例 Python 校验脚本（locked-descriptor 11 文件字节相等的提取部分）

下方代码是 stage-6 validator 的「即贴即用」骨架，**仅实现 Level 04 (content_lock) 即将依赖的提取函数 + Level 03 角色字段哨位在场检查**。完整字节相等比对由 Level 04 文件给出。本 §10 只解决最容易出错的一步：从 11 个不同结构的文件中切出同一块文本。

```python
# locked_descriptor.py — 共用提取器（stage-6 由 Level 03 + Level 04 共同导入）
import re
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(r"C:\workspace\spec_coding\ai_videos\wukong_juexing")

START_SENTINEL = "【孙悟空 · 觉醒态 · 锁定描述符 v1】"
END_SENTINEL = "禁用 卡通线条、cel-shading、二次元大眼、低多边形。"

# 11 个文件 = 1 character bible + 5 Kling + 5 Seedance
LOCKED_DESCRIPTOR_FILES = [
    PROJECT_ROOT / "characters" / "main.md",
    *[PROJECT_ROOT / "prompts" / f"shot0{i}_kling.md" for i in range(1, 6)],
    *[PROJECT_ROOT / "prompts" / f"shot0{i}_seedance.md" for i in range(1, 6)],
]

def extract_locked_block(text: str) -> Optional[str]:
    """切出 START_SENTINEL ... END_SENTINEL（含两端哨位）的最短匹配。
    若任一哨位缺失或顺序反转，返回 None。
    """
    start = text.find(START_SENTINEL)
    if start == -1:
        return None
    end = text.find(END_SENTINEL, start + len(START_SENTINEL))
    if end == -1:
        return None
    return text[start : end + len(END_SENTINEL)]

def extract_role_field_block(text: str) -> Optional[str]:
    """从 prompt 文件中切出 `角色:` 行起到下一字段的内容
    (下一字段 = 任意以 `场景:` / `动作:` / `镜头:` / `光线/色调:` 开头的行)。
    """
    role_match = re.search(r"^\s*角色\s*[:：]", text, re.MULTILINE)
    if not role_match:
        return None
    after = text[role_match.start():]
    next_field = re.search(
        r"^\s*(场景|动作|镜头|光线/色调|比例|时长|风格|画质|约束|seed|negative_prompt)\s*[:：]",
        after[role_match.end() - role_match.start():],
        re.MULTILINE,
    )
    if not next_field:
        return after
    return after[: next_field.start() + role_match.end() - role_match.start()]

# === Level 03 (schema_compliance) — SCH-CHAR-02 / SCH-KLING-07 / SCH-SEED-PROMPT-10 ===
def check_sentinel_presence() -> list[dict]:
    issues = []
    for path in LOCKED_DESCRIPTOR_FILES:
        if not path.is_file():
            issues.append({
                "audit_event": "validation.issue.raised:schema.locked.file_missing",
                "severity": "blocker",
                "path": str(path),
            })
            continue
        text = path.read_text(encoding="utf-8")
        if path.name == "main.md":
            block = extract_locked_block(text)
            if block is None:
                issues.append({
                    "audit_event": "validation.issue.raised:schema.character.sentinel_missing",
                    "severity": "blocker",
                    "path": str(path),
                })
        else:
            role_text = extract_role_field_block(text)
            if role_text is None or START_SENTINEL not in role_text:
                tag = (
                    "schema.kling.locked_descriptor_sentinel_missing"
                    if "kling" in path.name
                    else "schema.seedance.locked_descriptor_sentinel_missing"
                )
                issues.append({
                    "audit_event": f"validation.issue.raised:{tag}",
                    "severity": "blocker",
                    "path": str(path),
                })
    return issues

# === Level 04 (content_lock) 即将复用 extract_locked_block 做 11 文件字节相等比对，
#     具体实现见 validation/content_lock.md。本文件停止在「在场」断言处。===

if __name__ == "__main__":
    import json, sys
    issues = check_sentinel_presence()
    if issues:
        for i in issues:
            print(json.dumps(i, ensure_ascii=False))
        sys.exit(1)
    print("OK: locked-descriptor sentinel present in all 11 files.")
```

下游消费契约：

- `extract_locked_block(text)` 与 `extract_role_field_block(text)` 是 Level 03 + Level 04 的共享 API。Level 04 的 `content_lock.md` 引用本文件作为依赖；如本文件改 API，Level 04 检查必须同步更新（一致性接口契约）。
- 哨位字符串 `START_SENTINEL` / `END_SENTINEL` 须与 `findings/angle-character-design-and-ref.md §3` + spec FR-11 完全一致；任何字面量改动 = stage-5 的 schema_compliance + content_lock 双层均需要更新。
- 共享 `vocab.json`（§4 中提及）若由 stage-6 提供，则放在 `ai_videos/wukong_juexing/.derived/vocab.json` —— 但 v1 不强制；缺失时本层退化为字面量匹配。

---

## §11 覆盖 FR 矩阵

| FR / NFR | spec 文字摘要 | 本层覆盖检查（id） | 是否完全覆盖 | 备注 |
|---|---|---|---|---|
| FR-1 | README 在场 | SCH-README-01 | 完全 | — |
| FR-2 | characters/main.md 在场 | SCH-CHAR-01 | 完全 | — |
| FR-3 | characters/ref_images/main_seedream.md 在场 | SCH-SEED-01 | 完全 | — |
| FR-4 | style_guide.md 在场 | SCH-STYLE-01 | 完全 | — |
| FR-5 | script.md 在场 | SCH-SCRIPT-01 | 完全 | — |
| FR-6 | shotlist.md 在场 | SCH-SHOT-01 | 完全 | — |
| FR-7 | 10 个 prompt 文件在场 | SCH-KLING-01 + SCH-SEED-PROMPT-01 | 完全 | — |
| FR-8 | publish.md 在场 | SCH-PUB-01 | 完全 | — |
| FR-9 | 全文中文内容（含技术 token 白名单） | SCH-LANG-02 + 各组的 `中文内容率` 子项 | 完全 | — |
| FR-10 | 路径全英/拼音 | SCH-LANG-01 | 完全 | — |
| FR-11 | 锁定描述符 v1 哨位 | SCH-CHAR-02 + SCH-CHAR-03 | 部分 | 字节相等由 Level 04 |
| FR-12 | Kling 文件角色字段含锁定描述符 | SCH-KLING-07 | 部分 | 字节相等由 Level 04 |
| FR-13 | Seedance 文件角色字段含锁定描述符 | SCH-SEED-PROMPT-10 | 部分 | 字节相等由 Level 04 |
| FR-14 | Seedream 10 段 + 250–400 中文字 | SCH-SEED-02 + SCH-SEED-03 | 完全 | — |
| FR-15 | style_guide.md token 在场 | SCH-STYLE-02..06 | 完全 | — |
| FR-16 | 光线/色调 行 token 锁 | — | 不覆盖 | Level 04 (content_lock) 负责 |
| FR-17 | 任何 hex 必属调色板 | — | 不覆盖 | Level 04 |
| FR-18 | 「黑神话·悟空美术风」锚定短语 | — | 不覆盖 | Level 04 |
| FR-19 | 禁用 register token | SCH-KLING-06 + SCH-SEED-PROMPT-12（最低门槛） + SCH-LANG-03 | 部分 | 完整 token 列表 + 中文同义词由 Level 04 |
| FR-20 | shotlist 5 行 + 6 列 | SCH-SHOT-02..04 | 完全 | — |
| FR-21 | 时长配额 [5,8,8,10,7] | SCH-SHOT-07 + SCH-SEED-PROMPT-06 | 完全 | — |
| FR-22 | 每镜 ≤ 10s（实际） | SCH-SHOT-05 + SCH-SEED-PROMPT-07 | 完全 | shotlist 上限 15s（必备移动 #2）/ Seedance 文件上限 12s |
| FR-23 | negative_prompt 不对称 | SCH-KLING-02 + SCH-KLING-06 + SCH-SEED-PROMPT-03 + SCH-SEED-PROMPT-12 | 部分 | 完整 token 集 Level 04 |
| FR-24 | Kling 含参考图行 / Seedance 不含 | SCH-KLING-08 + SCH-SEED-PROMPT-04 | 完全 | — |
| FR-25 | Seedance 时间线分段 | SCH-SEED-PROMPT-08 + SCH-SEED-PROMPT-09 | 完全 | — |
| FR-26 | 字段集（Kling 8 / Seedance 11） | SCH-KLING-02 + SCH-SEED-PROMPT-02 | 完全 | — |
| FR-27 | 比例 9:16；Kling 时长枚举；Seedance 与 FR-21 一致 | SCH-KLING-03 + SCH-KLING-04 + SCH-SEED-PROMPT-05 + SCH-SEED-PROMPT-06 | 完全 | — |
| FR-28 | t≈2s burst-peak | — | 不覆盖 | Level 04（语义） |
| FR-29 | 缩略图契约块 | SCH-KLING-10 + SCH-SEED-PROMPT-14 | 部分（仅块在场；构图属 Level 04 / 05） | — |
| FR-30 | 回环契约块 | SCH-KLING-11 + SCH-SEED-PROMPT-15 | 部分（仅块在场） | — |
| FR-31 | 转场规则 | — | 不覆盖 | Level 04 |
| FR-32..36 | 武器/毛色/星空/金属 | — | 不覆盖 | Level 04 |
| FR-37 | publish.md 6 章节 | SCH-PUB-02 | 完全 | — |
| FR-38 | hashtag 3–5 总数 + #Shorts + ≤ 15 上限 | SCH-PUB-06 + SCH-PUB-07 + SCH-PUB-08 | 完全 | — |
| FR-39 | 标题 ≤ 30 中文字 + 无 hashtag | SCH-PUB-03 + SCH-PUB-04 | 完全 | — |
| FR-40 | 简介 150–250 中文字 + 首句钩子 | SCH-PUB-05 + SCH-PUB-11 | 完全 | — |
| FR-41 | 发布时段双窗口 | SCH-PUB-09 + SCH-PUB-10 | 完全 | — |
| FR-42 | README 4 章节 + 风格关键词 5–10 | SCH-README-02..06 | 完全 | — |
| NFR-1 | Kling 2.1 Pro / Seedance 1.0 Pro 枚举 | SCH-KLING-04 + SCH-KLING-05 + SCH-SEED-PROMPT-07 | 完全 | — |
| NFR-2 | 11 文件字节相等 | — | 不覆盖 | Level 04 主战场 |
| NFR-3 | 词表锁 | — | 不覆盖 | Level 04 |
| NFR-4 | 中文 prompt body | SCH-LANG-02 应用于 prompt 文件 | 完全 | — |
| NFR-5 | 三处 9:16 冗余 | SCH-SEED-04 + SCH-STYLE-07 + SCH-KLING-03 + SCH-SEED-PROMPT-05 | 完全 | — |
| NFR-6 | Kling 时长枚举 + 渲染说明注释 | SCH-KLING-04 + SCH-KLING-05 | 完全 | — |
| NFR-7 | README ↔ style_guide 同步 | — | 不覆盖 | follow-up changelog；超出 schema 层 |
| NFR-8 | 中文优先级 | SCH-LANG-02（自动满足） | 完全 | — |

「不覆盖 / 部分」的项已在「备注」列指明下游 level；本层与 Level 04 (content_lock) 接口边界清晰，互不重复。

---

## §12 审计事件汇总

stage-6 streaming validator 在执行本层每一项检查前后须分别写：

- 进入工作单元时：`validation.started` —— `payload.level = "schema_compliance"`、`payload.work_unit = "U{N}"`、`payload.checks = [<id 列表>]`、`payload.pre_reading_consulted = [...]`。
- 每项检查通过：`validation.pass` —— `payload.check_id = <id>`。
- 每项检查失败：`validation.issue.raised` —— `payload.check_id = <id>`、`payload.audit_event = <表中 audit-event tag>`、`payload.severity = <表中严重度>`、`payload.path = <文件绝对路径>`、`payload.evidence = <≤200 字定位文本>`。
- 本层全部通过：`validation.pass` —— `payload.level = "schema_compliance"`、`payload.summary = <id 计数与时长>`。

`validation.requires_manual_walkthrough` 在本层不会被触发 —— 所有检查都是机械可判定。手动走查归属 Level 05。

迭代上限：`general.md` § Iteration bounds 标准（每工作单元 3 轮修订；同一 issue 跨 2 轮重复或单元墙钟 > 30 分钟即 `pipeline.halted`）。本层不另设上限。
