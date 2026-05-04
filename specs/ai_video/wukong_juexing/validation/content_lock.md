# Validation level — content_lock

Run: `wukong_juexing-20260503-201831`
Stage: 5 (validation strategy)
Level: 04 — content_lock (image-first 字符锁 / 风格锁 / 双工具非对称 / 回环 / 缩略图契约)
任务类型: ai_video, sub_type=short
负责文件: `validation/content_lock.md`

输入档:
- `final_specs/spec.md` (FR-11..FR-19, FR-23..FR-25, FR-28..FR-36, NFR-2, NFR-3)
- `findings/angle-character-design-and-ref.md` §3
- `findings/angle-visual-style.md` §3
- `.claude/agent_refs/validation/general.md`
- `.claude/agent_refs/validation/ai_video.md` (移动 #3)

---

## 总览

本级是 **image-first 字符锁定流水线** 的承重层。Stage 6 输出共 12 个文件中,本级覆盖 11 个 prompt 文件 (1 character bible + 5 Kling + 5 Seedance) + style_guide.md + shotlist.md + 2 个特别合同文件 (shot01 缩略图、shot05 回环) 的语义内容规则。

本级与隔壁三级的边界:
- 与 **schema_compliance** 互补:本级假设字段已存在 (schema 通过),只校验字段值的语义。如 schema 已确认 `光线/色调:` 字段存在,本级校验其取值是否落在 6-token 词汇表内。
- 与 **acceptance_criteria** 互补:本级是机械可解析的字符串规则;acceptance 关注端到端可见行为。
- 与 **manual_walkthrough** 互补:本级所有规则都是 grep / regex 即可裁定的硬规则,失败=`blocker`。视觉一致性 (在 Seedream 立绘出图后) 才进入 manual。

**整体严重度策略:** 本级所有失败均为 `blocker`(参见 `.claude/agent_refs/validation/ai_video.md` 严重度表 — 字符描述符漂移、未声明比例、缺少 hook 标记、跨 prompt 字符不一致都列为 blocker)。任何本级失败都会触发标准 3 轮修订上限,逾此则 `pipeline.halted`。

**执行口径:** Stage 6 流式校验器在每个 work-unit 完成时(尤其 U1 character bible 与 U4 prompts)运行本级所有 check,失败发 `validation.issue.raised` 事件。

---

## 检查项

### A. 锁定描述符契约 (FR-11, FR-12, FR-13, NFR-2, ai_video.md #3)

#### CHK-CL-A01 — 锁定描述符块可提取

- **目标文件:** `characters/main.md`, `prompts/shot{01..05}_kling.md` (5), `prompts/shot{01..05}_seedance.md` (5)。共 **11 个文件**。
- **通过条件:** 每个文件必须含一个由以下两个 sentinel 包夹的连续文本块:
  - 起始: `【孙悟空 · 觉醒态 · 锁定描述符 v1】`
  - 终止: `禁用 卡通线条、cel-shading、二次元大眼、低多边形。`
  - 提取正则 (Python, `re.DOTALL`): `r"【孙悟空 · 觉醒态 · 锁定描述符 v1】.*?禁用 卡通线条、cel-shading、二次元大眼、低多边形。"`
- **失败模式:** 任一文件缺起始 sentinel、缺终止 sentinel、或起始/终止间没有匹配文本。
- **严重度:** `blocker`(缺角色 bible → 整套 image-first lock 失效)。
- **审计事件:** `validation.issue.raised` with `level=content_lock`, `check=descriptor_extractable`, `path=<failing_file>`。

#### CHK-CL-A02 — 描述符跨 11 文件字节一致 (modulo 空白)

- **目标文件:** 同 A01 的 11 个文件。
- **通过条件:** 把每个文件中 A01 提取出的块以下述规则归一化后两两 byte-identical:
  - `re.sub(r"\s+", " ", block).strip()` (任意空白合并为单个空格,首尾 trim)
  - 不做大小写归一化 (中文无大小写)。
  - 不做标点归一化 (`,` vs `,` 视为不同 — 描述符已用全角中文标点)。
- **比对策略:** 取 `characters/main.md` 中的块为基准 (canonical),其余 10 个 prompt 文件与之逐一相等。
- **失败模式:** 任一文件归一化后与 canonical 不等。诊断输出 unified diff 行号。
- **严重度:** `blocker`(`ai_video.md` 严重度表第 3 行: "Two shots in same episode use different descriptors for the same character" = blocker;此处场景为 short 整片,等价)。
- **审计事件:** `validation.issue.raised` with `check=descriptor_byte_equal`, `path=<failing_file>`, `diff=<line_diff>`。

#### CHK-CL-A03 — 描述符块下挂在 `角色:` 字段下

- **目标文件:** 10 个 prompt 文件 (Kling + Seedance)。`characters/main.md` 不受此规则约束 (FR-11 允许其上方加项目语境段)。
- **通过条件:** 在每个 prompt 文件中,描述符块的起始 sentinel 上方 (回溯最多 3 行非空行) 必须出现以 `角色:` 或 `角色：` 开头的字段标签。
- **失败模式:** 描述符块出现在 `场景:` / `动作:` / 文件其他位置。
- **严重度:** `blocker`(FR-12, FR-13 明确字段绑定)。
- **审计事件:** `check=descriptor_under_role_field`。

---

### B. 调色盘锁 (FR-15, FR-17, NFR-3)

#### CHK-CL-B01 — 锁定调色盘 allowlist

锁定调色盘 (从 `findings/angle-visual-style.md` §3.1 提取,共 7 行 8 个 hex):

```
ALLOWED_HEXES = {
    "#F2A65A",  # 暖橘金 (落日金辉) — 环境/逆光/勾边
    "#9B2D20",  # 血暮赤
    "#2E5C6E",  # 深岩青 (冷阴影)
    "#3A2A55",  # 紫罗兰夜霞
    "#E8E6D9",  # 星辰白
    "#5C4A3A",  # 山岩灰褐 — 毛色基底
    "#8A6A3A",  # 毛色逆光金 (visual-style §3 + spec FR-34)
    "#6B4226",  # 装饰金 (紫金底)
    "#C9A96E",  # 装饰金 (鎏金高光)
    "#1A2A30",  # 深岩青压暗到极限 (visual-style §3.4)
}
```

注: visual-style §3.1 列了 7 行,但行内多处给双 hex (`装饰金 #6B4226 与 #C9A96E 双层`),实际命中 hex 共 9 个;§3.4 补充 `#1A2A30` 作为黑位下限,共 10 个 hex 进 allowlist。`style_guide.md` 必须含全部 10 个;若 stage-6 的 `style_guide.md` 漏掉任一,B02 会捕获。

#### CHK-CL-B02 — `style_guide.md` 含完整 allowlist

- **目标文件:** `style_guide.md`。
- **通过条件:** allowlist 中的 10 个 hex 在 `style_guide.md` 中均出现至少 1 次 (大小写不敏感,`#f2a65a` 等价 `#F2A65A`)。
- **失败模式:** allowlist 中任一 hex 缺席。
- **严重度:** `blocker`(NFR-3: 所有 palette 引用必须可追溯到 style_guide.md)。
- **审计事件:** `check=palette_present_in_style_guide`, `missing=<hex_list>`。

#### CHK-CL-B03 — 全工程 hex ⊆ allowlist

- **目标文件:** `style_guide.md`, `script.md`, `shotlist.md`, `characters/main.md`, `characters/ref_images/main_seedream.md`, 10 个 prompt 文件。共 **15 个文件**。
- **通过条件:** 用正则 `r"#[0-9A-Fa-f]{6}\b"` 提取每个文件全部 hex,归一化大写后必须 ⊆ allowlist。
- **失败模式:** 出现 allowlist 之外的 hex (如 `#FFD700`、`#000000`、`#C9A14A` — 注意 `#C9A14A` 是 character-design 角度文档 Q4 的笔误近似值,正确应为 `#C9A96E`)。
- **严重度:** `blocker`(FR-17)。
- **审计事件:** `check=hex_in_allowlist`, `path=<file>`, `unknown_hex=<hex>`。

---

### C. 词汇锁:光线 / 运镜 / 转场 (FR-15, FR-16, NFR-3)

#### CHK-CL-C01 — 6-token 光线词汇

锁定光线 token (visual-style §3.3,逐字使用):

```
LIGHTING_TOKENS = [
    "暮色魔幻时刻顶光",
    "星空环境光",
    "金色边缘逆光",
    "点状装饰光",
    "体积光丁达尔束",
    "冷蓝补光",
]
```

- **目标文件:** 10 个 prompt 文件。
- **通过条件:** 每个文件的 `光线/色调:` 字段(取该字段冒号至下一字段标签或文件末)中,至少含 1 个上述 token (子串匹配)。
- **失败模式:** 字段值是自由发挥 (`"warm tones"`、`"暖色调"`、`"金色光线"` 但无 `金色边缘逆光` token);或字段值缺失。
- **严重度:** `blocker`(FR-16)。
- **审计事件:** `check=lighting_token_present`, `path=<file>`。

#### CHK-CL-C02 — 5-pattern 运镜词汇

锁定运镜 pattern (visual-style §3.5,逐字使用):

```
MOTION_PATTERNS = [
    "极缓推近",  # dolly-in 中文锚点
    "慢速广角揭示",  # reveal pan 中文锚点
    "轨道环绕",  # arc
    "手持轻微浮动",  # handheld micro-sway
    "垂直升降",  # crane-up
]
```

- **目标文件:** 10 个 prompt 文件。
- **通过条件:** 每个文件的 `镜头:` 字段值中至少含 1 个上述 token。
- **失败模式:** 自由发挥的运镜 (`"快速横移"`、`"360 度旋转"` 等明确禁用项 — 见 visual-style §3.5 禁用清单)。
- **严重度:** `blocker`(NFR-3)。
- **审计事件:** `check=motion_pattern_present`, `path=<file>`。

#### CHK-CL-C03 — 3-rule 转场词汇

锁定转场 (visual-style §3.6,且经 spec FR-31 收紧 — 0.3-0.5s 白闪过渡因 AI 不可控被剔除):

```
TRANSITION_TOKENS = [
    "hard cut",        # 硬切 (默认)
    "match cut",       # 匹配剪辑
    "硬切",
    "匹配剪辑",
]
# 注意: visual-style §3.6 原列入 "金光闪白过渡" 但 FR-31 已剔除;此处不收。
```

- **目标文件:** `shotlist.md` 的 `连续性 tokens` 列。
- **通过条件:** 每行的连续性 token 字段中至少含 1 个上述 token (子串)。Shot 04→05 行必须含 `match cut` 或 `匹配剪辑`(FR-31)。Shot 01→02 行必须含 `hard cut` 或 `硬切`(FR-31 显式锁定)。
- **失败模式:** 出现 `dissolve` / `推拉` / `白闪过渡` / `cross fade` (visual-style §3.6 禁用列表),或 FR-31 锁定的两个转场未按指定值出现。
- **严重度:** `blocker`(NFR-3 + FR-31)。
- **审计事件:** `check=transition_token_present`, `shot_pair=<from-to>`。

#### CHK-CL-C04 — 禁用运镜负检测

- **目标文件:** 10 个 prompt 文件 + `shotlist.md`。
- **通过条件:** 不含以下 token (visual-style §3.5 禁用): `whip-pan` / `360° 旋转` / `360 度旋转` / `鱼眼` / `第一人称 POV` / `POV` (英文独立词)。
- **失败模式:** 任一禁用 token 出现在文件正文。
- **严重度:** `blocker`。
- **审计事件:** `check=motion_negative_list`, `path=<file>`, `forbidden=<token>`。

---

### D. 负向词汇锁 (FR-19)

#### CHK-CL-D01 — 禁用 register token 不出现在正文

锁定禁用 register token (FR-19):

```
FORBIDDEN_REGISTER = [
    "卡通", "Q版", "Q 版", "cel-shading", "cel shading",
    "二次元", "戏曲妆", "京剧脸谱", "低多边形", "86版西游记", "86 版西游记",
]
```

- **目标文件:** 10 个 prompt 文件 + `style_guide.md` + `script.md` + `shotlist.md` + `characters/main.md` + `characters/ref_images/main_seedream.md`。共 **15 个文件**。
- **允许例外的字段:**
  - Kling prompt 文件中 `negative_prompt:` 字段值内 (FR-23)。
  - Seedance prompt 文件中 `约束:` 字段值内,以 "无 / 不 / 禁用" 等否定词为前缀的复合短语 (FR-23 — Seedance 用 positive contraries 表达否定)。
  - `style_guide.md` 与 `characters/main.md` / `main_seedream.md` 中的 "禁用" 或 "avoid" 子句内 (visual-style §3.3 禁用列表、character-design §3 末段、§4 第 10 段负向提示)。
- **检测策略:** 提取每个文件的字段映射;对 prompt 文件,取 `negative_prompt:` / `约束:` 字段值组成 allow-region;对 character/style 文件,取以 "禁用" / "avoid" / "**禁用**" 为开头到下一段落空行的子串组成 allow-region。其余正文若出现 FORBIDDEN_REGISTER 任一 token = 失败。
- **失败模式:** `卡通` 出现在 Kling 文件 `场景:` 字段;`二次元` 出现在 Seedance `动作:` 字段。
- **严重度:** `blocker`(FR-19 硬禁用)。
- **审计事件:** `check=forbidden_register_in_body`, `path=<file>`, `forbidden=<token>`, `field=<field_name>`。

#### CHK-CL-D02 — Kling `negative_prompt:` 必含禁用 register tokens 全集

- **目标文件:** `prompts/shot{01..05}_kling.md` (5 个)。
- **通过条件:** 每个文件的 `negative_prompt:` 字段值必须含 FR-23 列出的全部 10 个 register token (允许变形: `Q 版`/`Q版` 任一即算命中) + 标准 artifact guards (`多余手指, 五官畸变, 文字水印, 字幕, logo, 模糊, 鬼影, 闪烁, 现代服饰, 现代建筑, 多人出现`)。
- **失败模式:** `negative_prompt:` 字段缺失;或字段存在但漏一个或多个 token。
- **严重度:** `blocker`(FR-23)。
- **审计事件:** `check=kling_negative_prompt_complete`, `path=<file>`, `missing=<token_list>`。

#### CHK-CL-D03 — Seedance `约束:` 必含 positive contraries

- **目标文件:** `prompts/shot{01..05}_seedance.md` (5 个)。
- **通过条件:** 每个文件的 `约束:` 字段值必须含 FR-23 列出的 8 项 positive contraries 全集 (`五官稳定不畸变, 同一角色全程一致, 单人画面无多余人物, 无文字水印, 无字幕, 无现代元素, 无模糊鬼影闪烁`),允许语序与并列符差异 (中文逗号 / 顿号 / 空格)。
- **失败模式:** `约束:` 字段缺失;或漏关键 contrary。
- **严重度:** `blocker`(FR-23)。
- **审计事件:** `check=seedance_constraint_complete`, `path=<file>`, `missing=<contrary_list>`。

---

### E. 双工具非对称契约 (FR-23, FR-24, FR-26)

#### CHK-CL-E01 — Kling 文件不含 `约束:` 字段;Seedance 文件不含 `negative_prompt:`

- **目标文件:** 10 个 prompt 文件。
- **通过条件:**
  - Kling 文件 (5 个): 全文不含独立行 `negative_prompt:` 与 `约束:` 同时出现 — Kling 必须有 `negative_prompt:`,且 `约束:` 字段不应作为独立顶层字段出现 (避免和 Seedance 文件结构混淆)。
  - Seedance 文件 (5 个): 全文不含独立行 `negative_prompt:`(FR-23 明确禁止);必须含 `约束:`(D03 已校验)。
- **检测正则:**
  - Kling: `re.search(r"^negative_prompt:", text, re.MULTILINE)` 必须命中;`re.search(r"^约束[：:]", text, re.MULTILINE)` 不命中。
  - Seedance: `re.search(r"^negative_prompt:", text, re.MULTILINE)` 不命中;`re.search(r"^约束[：:]", text, re.MULTILINE)` 必须命中。
- **失败模式:** 用户在 Seedance 文件复制粘贴了 Kling 模板 (常见错误)。
- **严重度:** `blocker`(FR-23 双向硬规则)。
- **审计事件:** `check=tool_field_asymmetry`, `path=<file>`, `tool=<kling|seedance>`, `violation=<missing|extra>`。

#### CHK-CL-E02 — `[参考图: ...]` 行非对称 (FR-24)

- **目标文件:** 10 个 prompt 文件。
- **通过条件:**
  - Kling 文件首行 (跳过 YAML frontmatter / `# 缩略图契约` / `# 回环契约` 注解块后第一行非空行) 必须匹配正则: `r"^\[参考图:\s*characters/ref_images/main_seedream\.md.*?\]"`。
  - Seedance 文件全文不得含 `[参考图:` 子串。
- **失败模式:** Kling 漏写参考图行,或路径写错;Seedance 文件复制粘贴了参考图行 (Seedance t2v 不接图)。
- **严重度:** `blocker`(FR-24 + ai_video.md #4 双工具)。
- **审计事件:** `check=ref_image_line_asymmetry`, `path=<file>`, `tool=<kling|seedance>`。

#### CHK-CL-E03 — Seedance `动作:` 字段含 per-second timeline (FR-25)

- **目标文件:** `prompts/shot{01..05}_seedance.md` (5 个)。
- **通过条件:** `动作:` 字段值须含至少 2 个 per-second segment header,匹配正则 `r"\d+[–\-~]\d+\s*秒[:：]"`(全角冒号或半角)。Shot 01 必须含 `0[–\-~]2\s*秒[:：]` (FR-28 burst-peak segment)。
- **失败模式:** Kling 风格的散文 `动作:` 复制粘贴到 Seedance 文件。
- **严重度:** `blocker`(FR-25)。
- **审计事件:** `check=seedance_timeline_segments`, `path=<file>`, `segments_found=<count>`。

---

### F. Q1–Q5 specifics (FR-32..FR-36)

#### CHK-CL-F01 — 金箍棒长度 `2 米` 锚点 (FR-32, Q1)

- **目标文件:** `characters/main.md` (锁定描述符已含 `本片默认全长约 2 米`,A02 byte-equality 已隐式覆盖) + 10 个 prompt 文件。
- **通过条件:** A02 通过即视为隐式通过 (描述符已含)。额外硬规则: 10 个 prompt 文件中,任何 `动作:` / `场景:` / `镜头:` 字段不得含与 2 米冲突的长度 token,如 `1 米` / `5 米` / `10 米` (允许 `镜身延长` 等定性表达,但具体米数受限)。
- **检测正则负向:** `r"\b(1|3|4|5|6|7|8|9|10|15|20)\s*米"` — 命中且非否定上下文则失败。
- **失败模式:** 某 shot 单方面把金箍棒画成 5 米长,违反描述符锚点。
- **严重度:** `blocker`(FR-32 + ai_video.md #3 描述符漂移)。
- **审计事件:** `check=ruyi_bang_length_anchor`, `path=<file>`。

#### CHK-CL-F02 — 金箍棒发光默认 = 反射环境暖光 (FR-33, Q2)

- **目标文件:** 10 个 prompt 文件。
- **通过条件:**
  - shot01/02/04/05 (各 Kling+Seedance 共 8 个文件): 不得含 `内发光` / `自身发光` / `自体发光` token,允许 `反射环境暖光` / `反射金光` / `鎏金高光`。
  - shot03 Kling+Seedance (2 个文件): 允许 `内发光` token,但同行或紧邻段落必须含约束子串 `≤5%` 或 `≤ 5%` 或 `不超过 5%` 或 `5% 以内` (FR-33 表面积上限)。
- **检测正则:** `r"内发光|自身外发光|自体发光"` 命中后再校验 `r"≤\s*5\s*%|不超过\s*5|5\s*%\s*以内"` 在同段落内。
- **失败模式:** shot01 prompt 把金箍棒画成自带金光 (违反 Black Myth 厚重写实档位);shot03 写了内发光但漏 5% 约束。
- **严重度:** `blocker`(FR-33)。
- **审计事件:** `check=ruyi_bang_emission_default`, `path=<file>`, `shot=<NN>`。

#### CHK-CL-F03 — 悟空毛色锚点 (FR-34, Q3)

- **目标文件:** 10 个 prompt 文件 + `characters/main.md` + `characters/ref_images/main_seedream.md` + `style_guide.md`。
- **通过条件:**
  - 描述符 byte-equality (A02) 隐式锚定毛色为 `#5C4A3A` + `#8A6A3A` 逆光 (描述符 § 面貌 + § 标志性动作之间的毛色描述)。
  - 全 13 文件不得含 token: `金色毛发` / `金毛` / `全身金毛` / `黄金毛`(stylized golden full-fur 显式禁用)。允许 `金辉勾边` / `金边逆光` / `毛发逆光金辉` (这些是逆光勾边,非毛色本身)。
  - `逆光金辉` / `金鬃` 等若有命中,需验同段落含 `逆光` / `rim` / `rim light` / `勾边` 限定词。
- **检测正则负向:** `r"金色毛发|金毛|全身金毛|黄金毛"`。
- **失败模式:** 某 prompt 把 Wukong 写成《大圣归来》风格的全身金毛。
- **严重度:** `blocker`(FR-34)。
- **审计事件:** `check=fur_color_anchor`, `path=<file>`。

#### CHK-CL-F04 — 星空密度锚点 (FR-35, Q4)

- **目标文件:** `prompts/shot{02,04,05}_kling.md` + `prompts/shot{02,04,05}_seedance.md` (6 个文件) + `style_guide.md`。
- **通过条件:** 每个文件 `场景:` 字段(或 `光线/色调:` 字段)中含至少一组锚点 token: `戏剧化星空` 与 `银河淡带` 任意一者出现即可,但两者 union 在 6 个文件至少累计出现 6 次 (即每文件平均 1 次)。
- **失败模式:** 出现 `密集星空` / `真实星空` / `数千颗星`(违反 visual-style §6 Q4 决议 — AI 控制力弱,选戏剧化)。
- **检测正则:** 必须命中 `r"戏剧化星空|银河淡带"`;不应命中 `r"密集星空|真实星空|photorealistic.*star"` (大小写不敏感)。
- **严重度:** `blocker`(FR-35)。
- **审计事件:** `check=starry_sky_density`, `path=<file>`。

#### CHK-CL-F05 — 金属/光场 hex 上下文区分 (FR-36, 跨切)

- **目标文件:** 10 个 prompt 文件。
- **通过条件:** 区分 hex 出现的语义上下文:
  - `#6B4226` 与 `#C9A96E`: 出现时上下文必须为金属表面 (头冠 / 甲胄 / 金箍棒 metal surfaces)。允许 token: `紫金冠`/`锁子黄金甲`/`金箍棒`/`鎏金`/`錾刻`/`护肩甲`/`箍环` 等金属语境词在同段。
  - `#F2A65A`: 出现时上下文必须为环境/光场 (rim light / 逆光 / 金光 / 体积光 / 余晖)。允许 token: `逆光`/`勾边`/`体积光`/`金光`/`暮光`/`晚霞`/`rim`/`勾出轮廓`。
  - 反例: `金箍棒主体 #F2A65A` (把 `#F2A65A` 当金属本色) — 违反 FR-36;`头冠环境光 #6B4226` (把装饰金当光场) — 违反 FR-36。
- **检测策略:** 取每个 hex 出现位置左右各 30 字符窗口,逐个 hex 校验该窗口含本组 hex 应有的上下文 token (任一即可) AND 不含错位上下文 token。
- **失败模式:** 复制粘贴时 hex 与上下文错配。
- **严重度:** `blocker`(FR-36 跨切语义)。
- **审计事件:** `check=hex_context_match`, `path=<file>`, `hex=<#xxx>`, `expected_context=<metal|light>`。

---

### G. Hook + 缩略图契约 (FR-28, FR-29)

#### CHK-CL-G01 — Shot 01 双文件含 `# 缩略图契约` 注解块

- **目标文件:** `prompts/shot01_kling.md`, `prompts/shot01_seedance.md`。
- **通过条件:** 文件顶部 (前 5 行非空行内) 必须出现以 `# 缩略图契约` 开头的二级或一级 markdown 标题/注解块,块体含至少以下 3 句 (子串匹配,允许同义短语):
  - `单一视觉焦点` / `单焦点构图`
  - `主体置于上 2/3` / `居中上 1/3` / `上三分之二`
  - `调色盘合规` / `调色盘锁定` / `palette-compliant`
- **失败模式:** 注解块缺失,或块体不含必须的内容声明。
- **严重度:** `blocker`(FR-29)。
- **审计事件:** `check=thumbnail_contract_block`, `path=<file>`。

#### CHK-CL-G02 — Shot 01 burst-peak 在 t≈2s 声明

- **目标文件:** `prompts/shot01_kling.md`, `prompts/shot01_seedance.md`。
- **通过条件:**
  - Kling shot01: `动作:` 字段值含子串 `t≈2s` 或 `t ≈ 2s` 或 `t=2s` 或 `第 2 秒` 或 `2 秒处` 或 `2 秒时`,且与 `爆发` / `峰值` / `burst-peak` / `破壳峰值` / `金光峰值` 任一同句出现。
  - Seedance shot01: `动作:` 字段值含 segment `0[–\-~]2\s*秒[:：]`,且该 segment 末句含 `峰值` / `burst-peak` / `爆发顶点` / `破壳爆发顶点`。
- **失败模式:** 漏 t=2s 锚点 → Shorts 自动取首帧时 thumbnail 不会落在最强张力帧。
- **严重度:** `blocker`(FR-28)。
- **审计事件:** `check=burst_peak_t2s`, `path=<file>`, `tool=<kling|seedance>`。

#### CHK-CL-G03 — `shotlist.md` 标记 Shot 01 为 hook 镜头

- **目标文件:** `shotlist.md`。
- **通过条件:** Shot 01 行 `是否 hook 镜头` 列值为 `是` / `Y` / `yes` / `✓` / `true` 之一 (子串匹配,大小写不敏感)。其余 Shot 02-05 该列必须为 `否` / `N` / `no` / `false`。
- **失败模式:** 漏标或全部标 `是`。
- **严重度:** `blocker`(ai_video.md #5: 短片必须标 hook)。
- **审计事件:** `check=hook_shot_marked`, `shot=<NN>`。

---

### H. 回环契约 (FR-30, FR-31)

#### CHK-CL-H01 — Shot 05 双文件含 `# 回环契约` 注解块

- **目标文件:** `prompts/shot05_kling.md`, `prompts/shot05_seedance.md`。
- **通过条件:** 文件顶部 (前 5 行非空行内) 必须出现以 `# 回环契约` 开头的注解块,块体含全部以下 4 项声明 (子串匹配):
  - `构图字节级等同 Shot 01 frame 0` / `构图与 Shot 01 frame 0 字节一致` / `composition byte-identical to Shot 01 frame 0`
  - `相机角度同源` / `same camera angle` / `相机焦段同 Shot 01`
  - `主体框选同源` / `subject framing 同 Shot 01`
  - `仅光照状态差异` / `lighting state delta only` / `余烬冷尾` (后者是具体差异描述,作为锚点)。
- **失败模式:** 注解块缺失或仅含部分声明。
- **严重度:** `blocker`(FR-30)。
- **审计事件:** `check=loopback_contract_block`, `path=<file>`。

#### CHK-CL-H02 — Shot 05 光照状态相对 Shot 01 的明确差异声明

- **目标文件:** `prompts/shot05_kling.md`, `prompts/shot05_seedance.md`。
- **通过条件:** 文件 `光线/色调:` 字段必须含 token `金光-fading` 或 `金光淡出` 或 `余烬冷尾` (FR-30 锚点)。Shot 01 文件 `光线/色调:` 必须含 `金光-bursting` 或 `金光峰值` 或 `体积光丁达尔束` (匹配 visual-style §3.3 + FR-30 起点)。
- **失败模式:** 两 shot 光照 token 一致 → 回环成了静态重复,失去叙事弧度。
- **严重度:** `blocker`(FR-30 lighting delta requirement)。
- **审计事件:** `check=loopback_lighting_delta`, `shot=<01|05>`, `path=<file>`。

#### CHK-CL-H03 — Shot 04→05 transition = match cut

- **目标文件:** `shotlist.md`。
- **通过条件:** Shot 04→05 行 `连续性 tokens` 列含 `match cut` 或 `匹配剪辑`(FR-31)。Shot 01→02 行含 `hard cut` 或 `硬切`。
- 已并入 C03 检验,此处仅作 cross-link。

---

### I. 美术风锚点 (FR-18)

#### CHK-CL-I01 — `黑神话·悟空美术风` 出现在每个 prompt 文件

- **目标文件:** 10 个 prompt 文件。
- **通过条件:** 每个文件 `场景:` 或 `风格:` 字段值含子串 `黑神话·悟空美术风` 或同义锚点 `Black Myth: Wukong 美术风` / `黑神话:悟空美术风` (允许冒号宽窄变体);精确匹配上述任一字符串即算命中。
- **失败模式:** 风格描述沦为自由发挥 (`"中国神话风"`、`"古风"` 但无 IP 锚点)。
- **严重度:** `blocker`(FR-18)。
- **审计事件:** `check=visual_register_anchor`, `path=<file>`。

---

## 示例 Python 校验脚本片段

以下为 **CHK-CL-A01 + A02** 的可运行参考实现,stage-6 流式校验器可直接挪用。

```python
"""validators/content_lock_descriptor.py — locked-descriptor byte-equality check."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DESCRIPTOR_START = "【孙悟空 · 觉醒态 · 锁定描述符 v1】"
DESCRIPTOR_END = "禁用 卡通线条、cel-shading、二次元大眼、低多边形。"

# 跨行非贪婪匹配
DESCRIPTOR_RE = re.compile(
    re.escape(DESCRIPTOR_START) + r".*?" + re.escape(DESCRIPTOR_END),
    re.DOTALL,
)

WHITESPACE_RE = re.compile(r"\s+")


@dataclass(frozen=True)
class DescriptorCheckResult:
    path: str
    extracted: bool
    normalized: str | None
    matches_canonical: bool | None  # None when extraction failed


class DescriptorChecker:
    def __init__(self, project_root: Path) -> None:
        self.project_root: Path = project_root
        self.canonical_path: Path = project_root / "characters" / "main.md"
        self.target_paths: list[Path] = self._build_target_paths()

    def _build_target_paths(self) -> list[Path]:
        paths: list[Path] = [self.canonical_path]
        for tool in ("kling", "seedance"):
            for n in range(1, 6):
                paths.append(
                    self.project_root / "prompts" / f"shot{n:02d}_{tool}.md"
                )
        return paths

    @staticmethod
    def _normalize(block: str) -> str:
        return WHITESPACE_RE.sub(" ", block).strip()

    def _extract(self, path: Path) -> str | None:
        if not path.is_file():
            return None
        text: str = path.read_text(encoding="utf-8")
        match: re.Match[str] | None = DESCRIPTOR_RE.search(text)
        if match is None:
            return None
        return self._normalize(match.group(0))

    def check(self) -> list[DescriptorCheckResult]:
        canonical_block: str | None = self._extract(self.canonical_path)
        results: list[DescriptorCheckResult] = []
        for path in self.target_paths:
            extracted_block: str | None = self._extract(path)
            if extracted_block is None:
                results.append(
                    DescriptorCheckResult(
                        path=str(path),
                        extracted=False,
                        normalized=None,
                        matches_canonical=None,
                    )
                )
                continue
            matches: bool | None
            if canonical_block is None:
                matches = None
            else:
                matches = extracted_block == canonical_block
            results.append(
                DescriptorCheckResult(
                    path=str(path),
                    extracted=True,
                    normalized=extracted_block,
                    matches_canonical=matches,
                )
            )
        return results


def emit_audit(results: list[DescriptorCheckResult], events_path: Path) -> int:
    failures: int = 0
    with events_path.open("a", encoding="utf-8") as fh:
        for r in results:
            if not r.extracted:
                fh.write(
                    json.dumps(
                        {
                            "type": "validation.issue.raised",
                            "level": "content_lock",
                            "check": "descriptor_extractable",
                            "path": r.path,
                            "severity": "blocker",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                failures += 1
                continue
            if r.matches_canonical is False:
                fh.write(
                    json.dumps(
                        {
                            "type": "validation.issue.raised",
                            "level": "content_lock",
                            "check": "descriptor_byte_equal",
                            "path": r.path,
                            "severity": "blocker",
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                failures += 1
    return failures


if __name__ == "__main__":
    project_root: Path = Path(sys.argv[1])
    events_path: Path = Path(sys.argv[2])
    checker: DescriptorChecker = DescriptorChecker(project_root)
    results: list[DescriptorCheckResult] = checker.check()
    failures: int = emit_audit(results, events_path)
    sys.exit(1 if failures else 0)
```

调用约定 (stage-6 编排器):

```bash
uv run python validators/content_lock_descriptor.py \
    ai_videos/wukong_juexing \
    .audit/adhoc_agents/2026-05-03/wukong_juexing-20260503-201831/events.jsonl
```

退出码 0 = 通过;1 = 至少一项 `blocker` issue。

---

## 覆盖 FR 矩阵

| FR / NFR | 覆盖检查项 | 严重度 |
|---|---|---|
| FR-11 | A01, A02 | blocker |
| FR-12 | A01, A02, A03 | blocker |
| FR-13 | A01, A02, A03 | blocker |
| FR-14 | (out — 由 schema_compliance 级处理 10 段结构 + 字数) | — |
| FR-15 | B02, C01, C02, C03 | blocker |
| FR-16 | C01 | blocker |
| FR-17 | B03 | blocker |
| FR-18 | I01 | blocker |
| FR-19 | D01, D02, D03 | blocker |
| FR-23 | D02, D03, E01 | blocker |
| FR-24 | E02 | blocker |
| FR-25 | E03 | blocker |
| FR-26 | (out — schema_compliance 字段存在性) | — |
| FR-27 | (out — schema_compliance 比例 + 时长枚举) | — |
| FR-28 | G02 | blocker |
| FR-29 | G01 | blocker |
| FR-30 | H01, H02 | blocker |
| FR-31 | C03, H03 | blocker |
| FR-32 | F01 (+ A02 隐式) | blocker |
| FR-33 | F02 | blocker |
| FR-34 | F03 (+ A02 隐式) | blocker |
| FR-35 | F04 | blocker |
| FR-36 | F05 | blocker |
| NFR-2 | A01, A02, A03 (整级承重) | blocker |
| NFR-3 | B02, B03, C01, C02, C03, C04 | blocker |
| (ai_video.md #3) | A01, A02, A03, F03 | blocker |
| (ai_video.md #5 hook) | G03 | blocker |
| (visual-style 禁用运镜) | C04 | blocker |

未覆盖项及其归口:

- FR-1..FR-10 (文件存在性 + 语言 + 路径语言) — 归 schema_compliance 级。
- FR-14 (Seedream 10 段结构 + 字数) — 归 schema_compliance。
- FR-20..FR-22 (shot 数 + 时长枚举) — 归 schema_compliance。
- FR-26, FR-27 (字段存在性 + 比例) — 归 schema_compliance。
- FR-37..FR-42 (publish + README) — 归 schema_compliance + acceptance_criteria。
- NFR-1, NFR-4..NFR-8 — 归 schema_compliance / acceptance_criteria。
- 视觉端到端一致性 (Seedream 立绘出图后 5 个镜头观感) — 归 manual_walkthrough,本级不裁。

---

## 与隔壁级的接口契约

- **acceptance_criteria 级:** 本级 `blocker` 失败时,acceptance 级 BDD 场景中"可复制粘贴的 prompt 文件"测试自动 fail (依赖)。本级通过是 acceptance 级前置条件。
- **schema_compliance 级:** 本级假设 schema 通过 (字段存在 + 比例 = 9:16 + 时长枚举合规)。schema 失败时,本级跳过并发 `validation.skipped` (中性事件) — 按 `general.md` 原则 3,跳过非失败但需明确标记。
- **manual_walkthrough 级:** 本级 + acceptance 全过后,manual 级才发起。本级是 manual 的硬前置 — 字符描述符未对齐时,人眼复检无意义。

---

## 备注:潜在歧义与决议

- **A02 的归一化策略选择空白合并而非完全等同**: 严格 byte-identical 对换行/缩进过敏,而 ai_video.md #3 已明确"modulo whitespace"。本级跟随 ai_video.md。
- **F05 hex 上下文窗口为 30 字符**: 经验值,既能捕获同句修饰语,又不会因跨段误匹配。stage 6 实测时若误报率高,可调至 50;若漏报高,可改为同段 (paragraph-bounded)。
- **C04 motion 禁用列表使用 token 粒度而非 phrase**: `whip-pan` 作为单 token 在中文语料中较稳定;`快速横移` 在中文语料中常出现合法用法 (如非快速 whip),改用具体 visual-style §3.5 禁用清单原文。
- **G02 的 burst-peak 容忍多种声明形式**: spec FR-28 明确 "the burst-peak frame lands at t≈2s", 但 stage 6 prompt 编写者可能写成不同表述。本级正则覆盖了 6 种常见形式。
