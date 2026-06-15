---
worker_id: level-specialist-03-schema_structure_compliance
stage: 5
role: level-specialist
level: schema_structure_compliance
status: complete
blockers: []
confidence: high
---

# Validation level — schema_structure_compliance（机检层）

适用对象：`ai_videos/_performances/` 下的全部 entry 与库结构。本层只负责**可自动化的 grep/parse 级**校验：布局、命名、frontmatter schema、status 枚举、必备 body 段、语言比例、检验视频时长原子性、双模型 prompt 存在性与受控变量字节一致性、gitignore 覆盖。

严重度策略沿用 `agent_refs/validation/general.md` § Standard severity policy 与 `agent_refs/validation/ai_video.md` § Severity escalations：
- 验收准则失败 / 硬项目规则违背 = `blocker`（标准 3 轮修正封顶）。
- 安全 / sandbox 逃逸 = `critical`（立即 halt）——本层无安全面，故无 `critical`。
- 观测型 / 推荐型缺口 = `warning`（记录，不 halt）。

通用约定：所有正则在 entry 文件 `perf_NNNN.md` 全文上跑（除非另注）；frontmatter 指 `---` … `---` 之间的首块 YAML；语言/字节检查在剥离 code fence + frontmatter 后跑。

---

## SV-1 三级布局与 folder==stem（FR-1）

**parse**：glob `ai_videos/_performances/*/*/` 取每个 entry 目录；对每个目录读其内 `*.md`。

**pass 条件（全部满足）**：
1. 路径深度恰为三级：`_performances/{emotion}/perf_NNNN/`，无更深或更浅嵌套（emotion 目录直接挂 perf 目录，perf 目录直接挂文件）。
2. perf 目录内**恰好一个** `perf_NNNN.md`，且文件 stem == 父目录名（`basename(dir) == basename(file, ".md")`）。
3. 每个 `{emotion}` 目录下存在 `_emotion.md`。
4. emotion slug 为英文/拼音（正则 `^[a-z0-9_]+$`，不含中日韩字符）。

**grep 实现**：
```bash
# 目录名与文件 stem 一致
for d in ai_videos/_performances/*/perf_*; do
  stem=$(basename "$d")
  test -f "$d/$stem.md" || echo "MISMATCH $d"
done
# 每个 emotion 目录有 _emotion.md
for e in ai_videos/_performances/*/; do
  test -f "$e/_emotion.md" || echo "NO_EMOTION_MD $e"
done
# emotion slug 不含 CJK
ls -d ai_videos/_performances/*/ | grep -P '[\x{4e00}-\x{9fff}]'
```

**failure message**：
- folder!=stem → `FR-1 布局违背：entry 目录 {dir} 内缺少与目录同名的 {stem}.md（folder name 必须 == file stem）。`
- 缺 `_emotion.md` → `FR-1/FR-2 违背：情绪目录 {emotion} 缺 _emotion.md（情绪定义 + entry 清单）。`
- 嵌套层级错 / CJK slug → `FR-1/FR-3 违背：{path} 层级或命名不符三级英文/拼音布局。`

**severity**：`blocker`（验收准则「三级布局正确」直接失败）。

---

## SV-2 全局连续零补四位编号（FR-2）

**parse**：glob 全库 `perf_*` 目录名，抽取 `NNNN`。

**pass 条件**：
1. 每个编号匹配 `^perf_[0-9]{4}$`（零补正好 4 位；`perf_12` / `perf_00001` 失败）。
2. 全局唯一：跨**所有** emotion 目录，同一 `NNNN` 不得出现两次（编号不随情绪重置）。
3. 连续：排序后从最小到最大无空洞（`perf_0001, perf_0002, … perf_000K` 无缺号）。起点不强制为 0001，但建议；缺号视为漏写或误删。

**grep 实现**：
```bash
# 抽全部编号
nums=$(ls -d ai_videos/_performances/*/perf_*/ | sed -E 's#.*/perf_([0-9]{4})/#\1#')
# 格式（非 4 位）
ls -d ai_videos/_performances/*/perf_*/ | grep -vP '/perf_[0-9]{4}/$'
# 重复检测（全局唯一）
echo "$nums" | sort | uniq -d        # 任何输出 = 重号
# 连续性：去重后计数应 == (max-min+1)
echo "$nums" | sort -u | awk 'NR==1{min=$1} {max=$1; c++} END{
  exp=max-min+1; if(c!=exp) print "GAP: have "c" expect "exp" ("min".."max")"}'
```

**failure message**：
- 格式错 → `FR-2 违背：{name} 编号非零补四位（须 ^perf_[0-9]{4}$）。`
- 重号 → `FR-2 违背：编号 {NNNN} 在多个情绪目录重复出现，破坏全局唯一性。`
- 缺号 → `FR-2 警示：编号区间 {min}..{max} 存在空洞（缺 {missing}）；编号应全局连续不随情绪重置。`

**severity**：格式错 / 重号 = `blocker`（破坏全局唯一 reference 句柄）；缺号 = `warning`（不破坏唯一性，但提示漏写/误删，记录不 halt）。

---

## SV-3 四维 frontmatter schema（FR-4）

**parse**：解析每个 `perf_NNNN.md` 首块 YAML frontmatter。

**必填键 + 取值域**：
| 键 | 约束 |
|---|---|
| `emotion` | 非空 slug，须与所在情绪目录名一致（交叉校验）。 |
| `intensity` | 整数，`1 ≤ n ≤ 5`（拒绝 `"3"` 字符串型亦可宽容解析为 int；拒绝 0 / 6 / 浮点）。 |
| `style` | ∈ {`内敛压抑`, `外放爆发`}。 |
| `carrier` | ∈ {`面部`, `眼神`, `肢体`, `呼吸`, `复合`}。 |

**选填键（出现则校验，不出现不报错）**：
- `lma_tag`（自由文本，Weight/Time/Flow 标签）。
- `mffr` ∈ {`Molding`,`Flowing`,`Flying`,`Radiating`}（出现时校验枚举）。
- `stance` ∈ {`反派`, `主角`}（出现时校验枚举）。
- `au_ref`（自由文本/列表，AU 编号可追溯）。

**pass 条件**：四必填键齐全，全部落在取值域内；`emotion` == 父情绪目录 slug；出现的选填枚举键合法。

**grep / parse 实现**：
```bash
# 用 yq/python 解析 frontmatter；伪规则：
#   require keys {emotion,intensity,style,carrier}
#   assert intensity is int in 1..5
#   assert style in {内敛压抑,外放爆发}
#   assert carrier in {面部,眼神,肢体,呼吸,复合}
# 快速 grep 兜底（缺键侦测）：
for f in ai_videos/_performances/*/perf_*/perf_*.md; do
  for k in emotion intensity style carrier; do
    grep -qP "^$k:" "$f" || echo "MISSING $k :: $f"
  done
done
```

**failure message**：
- 缺键 → `FR-4 违背：{file} frontmatter 缺必填四维键 {key}。`
- 越界 → `FR-4 违背：{file} {key}={value} 不在取值域（intensity∈1..5 / style∈内敛压抑|外放爆发 / carrier∈面部|眼神|肢体|呼吸|复合）。`
- emotion 与目录不符 → `FR-4 违背：{file} frontmatter emotion={e} 与所在目录 {dir} 不一致。`
- 选填枚举非法 → `FR-4 违背：{file} 选填键 {key}={value} 不在枚举（mffr / stance）。`

**severity**：`blocker`（验收准则「四维 frontmatter 完整」失败）。

---

## SV-4 status 枚举（FR-13 / NFR-4）

**parse**：frontmatter `status` 字段。

**pass 条件**：`status` 存在且 ∈ {`draft`, `pending_review`, `validated`, `needs_revision`}。

**grep 实现**：
```bash
grep -hP '^status:' ai_videos/_performances/*/perf_*/perf_*.md \
  | grep -vP '^status:\s*(draft|pending_review|validated|needs_revision)\s*$'
# 任何输出行 = 非法或缺失（缺失另由逐文件 grep -q 兜底）
```

**failure message**：`FR-13/NFR-4 违背：{file} status={value} 不在枚举 {draft|pending_review|validated|needs_revision}（验证状态须可 grep 派生）。`

**severity**：`blocker`（NFR-4 状态从文件派生是确定性契约；非法 status 使统计失真）。

> 注：`status: validated` 的**判定正确性**（是否真的满足「至少一个模型 表演达意≥4 且 情绪可识别≥4 且 过火≤2」）不在本机检层 —— 见 § 不可机检项 D，须由 content-substance 层解析 `## 实测与验证` 三轴分数交叉核验。本层只验枚举合法性。

---

## SV-5 必备 body 段（FR-9）

**parse**：扫 entry 正文标题行。

**pass 条件（必备段全部存在）**：
1. 标题 H1：`^# perf_[0-9]{4} ·`（FR-9 ①，格式 `# perf_NNNN · {情绪}·强度{N}·{风格}·{载体}`）。
2. `## 锁定文本块`（FR-9 ③，被 reference 的核心产物）。
3. `## 检验视频`（FR-9 ⑥，含双模型 prompt —— 详 SV-7/SV-8）。
4. `## 实测与验证`（FR-9 ⑦，回填三轴分数 —— 内容正确性归 content 层）。

**选填段（不报缺失）**：`## 配套镜头`（FR-9 ④）、`## 起始帧表情`（FR-9 ⑤；高强度 entry 强烈建议但非硬性 —— 「intensity≥4 缺起始帧」可作 `warning` 提示，见下）。

**grep 实现**：
```bash
for f in ai_videos/_performances/*/perf_*/perf_*.md; do
  grep -qP '^# perf_[0-9]{4} ·'  "$f" || echo "NO_TITLE $f"
  grep -qxF '## 锁定文本块'        "$f" || echo "NO_LOCK $f"
  grep -qxF '## 检验视频'          "$f" || echo "NO_TESTVIDEO $f"
  grep -qxF '## 实测与验证'        "$f" || echo "NO_VALIDATION $f"
done
```

**failure message**：`FR-9 违背：{file} 缺必备 body 段 {section}（必备：标题 / 锁定文本块 / 检验视频 / 实测与验证）。`

**severity**：缺任一必备段 = `blocker`（验收准则「body 标准块」失败）。可选增强：`intensity≥4 且 缺 ## 起始帧表情` = `warning`（FR-9 ⑤「强烈建议」，记录不 halt）。

---

## SV-6 语言合规 ≥95% 中文（ai_video validation ref rule 1 / FR-3）

**parse**：每个 entry `perf_NNNN.md` 与每个 `_emotion.md` 与库 `README.md`，递归全库 `*.md`。

**pre-strip（不计入分母）**：剥离 ``` code fence 块、YAML frontmatter、裸 URL。

**白名单专有名词（出现在中文句中不计为「非中文」）**：`Kling`、`Seedance`、`Seedream`、`9:16`、AU 编码（`AU\d{1,2}[a-z]?`，如 AU12 / AU25）、actor 句柄（`actor_\d{4}`）、perf 句柄（`perf_\d{4}`）、FACS A–E 强度字母、`mp4`/`png` 扩展名。

**pass 条件**：剥离与白名单扣除后，剩余正文的中文块字符（Han + 全角标点）占比 ≥ 95%。

**parse 实现（伪）**：
```
text = strip_code_fences(strip_frontmatter(file))
text = remove(text, URL_REGEX)
text = remove(text, WHITELIST_REGEX)   # Kling|Seedance|Seedream|9:16|AU\d+|actor_\d{4}|perf_\d{4}|[A-E]强度|mp4|png
han = count(text, [一-鿿，。！？；：、「」（）…—])
total = count(text, non-whitespace)
assert han / total >= 0.95
```

**failure message**：`ai_video rule1/FR-3 违背：{file} 中文占比 {pct}% < 95%（剥离 code/frontmatter/URL/白名单后）。检出英文段：{snippet}。`

**severity**：`blocker`（硬项目规则，与 ai_video.md 严重度表「English content in ai_videos/*.md」一致）。

---

## SV-7 检验视频 ≤15s 时长原子性（ai_video validation ref rule 2 / FR-11）

**parse**：`## 检验视频` 段内 Kling 与 Seedance 两个 prompt 各自的 `时长` 声明。

**pass 条件**：
1. 两版 prompt 各自显式声明 `时长`（缺字段即失败）。
2. 声明值 ≤ 15s（FR-11 建议统一 5s；本层只卡 ≤15 上限，统一性归 content 层）。

**grep 实现**：
```bash
# 抽 时长 行，拒绝缺失或 >15
grep -nP '时长[:：]\s*\d+' ai_videos/_performances/*/perf_*/perf_*.md \
 | awk -F'时长[:：]' '{gsub(/[^0-9].*/,"",$2); if($2>15) print "OVER15 "$0}'
# 缺失：逐文件断言 检验视频 段内出现至少两条 时长（Kling+Seedance）
```

**failure message**：
- 缺 → `ai_video rule2/FR-11 违背：{file} 检验视频 prompt 未声明 时长（须显式标 ≤15s）。`
- 超 → `ai_video rule2/FR-11 违背：{file} 检验视频 时长 {n}s > 15s；超 15s 须拆两段加连续性 token。`

**severity**：缺字段或 >15s = `blocker`（与 ai_video.md「Shot > 15s」严重度行一致）。

---

## SV-8 双模型 prompt 存在 + 受控变量字节一致（FR-11 / NFR-2）

**parse**：`## 检验视频` 段，定位 Kling 版与 Seedance 版两个 code fence（或两个标注子块）。同时定位本 entry `## 锁定文本块` 的内容串 S。

**pass 条件**：
1. `## 检验视频` 段内**同时**存在 Kling 版与 Seedance 版 prompt（两块都在）。
2. **受控变量字节一致**：锁定文本块串 S 作为子串，在 Kling 版与 Seedance 版 prompt body 中**逐字节相同**地出现（这是 FR-11 唯一变量 = 表演描述；两版差异仅模型适配语，表演描述 substring 必须 byte-identical）。
3. 串 S 同时与本 entry `## 锁定文本块` 正文 byte-identical（NFR-2 锁定串字节稳定 —— entry 内一致性；跨 shot 引用一致性归 content/引用层）。

**parse 实现（伪）**：
```
lock = extract_section(file, "## 锁定文本块").strip()
tv   = extract_section(file, "## 检验视频")
kling, seed = extract_two_prompt_blocks(tv)   # 缺一即 fail
assert (lock in kling) and (lock in seed)      # 锁定串原样嵌入两版
# 受控变量一致：两版中锁定串区段对位 byte 比对
assert substring_of(kling, lock) == substring_of(seed, lock) == lock
```

**failure message**：
- 缺一版 → `FR-11 违背：{file} 检验视频缺 {Kling|Seedance} 版 prompt（双模型控制变量须双版齐全）。`
- 字节漂移 → `FR-11/NFR-2 违背：{file} 锁定文本块在 Kling 与 Seedance 版之间字节不一致（受控变量必须 byte-identical）；diff: {a} vs {b}。`
- 嵌入缺失 → `FR-11 违背：{file} 锁定文本块未原样嵌入检验视频 prompt（唯一变量须为该锁定串）。`

**severity**：`blocker`（受控变量被破坏 → 检验视频不再隔离单一变量，验证结论失效；对齐 ai_video.md「同一角色两 shot 描述符漂移 = blocker」的字节一致精神）。

---

## SV-9 渲染产物 gitignore 覆盖（NFR-3）

**parse**：仓库 `.gitignore`（根级，或覆盖 `ai_videos/` 的就近 `.gitignore`）。

**pass 条件**：存在规则使 `ai_videos/_performances/` 下的 `*.mp4` 与 `*.png` 被忽略。可接受形态：
- 通配 `ai_videos/_performances/**/*.mp4` + `… /*.png`，或
- 更宽的全局 `*.mp4` / `*.png`，或 `ai_videos/**/*.mp4` 等覆盖该路径的规则。

**验证实现**：
```bash
# 用 git check-ignore 做权威判定（胜过文本 grep）
git check-ignore -q ai_videos/_performances/yayi_yinren/perf_0001/perf_0001__kling.mp4 \
  && echo "MP4_IGNORED_OK" || echo "MP4_NOT_IGNORED"
git check-ignore -q ai_videos/_performances/yayi_yinren/perf_0001/perf_0001__startframe.png \
  && echo "PNG_IGNORED_OK" || echo "PNG_NOT_IGNORED"
```

**failure message**：`NFR-3 违背：渲染产物未被 gitignore 覆盖（{*.mp4|*.png} 在 _performances 路径下未被忽略）；git 应只追踪 markdown。`

**severity**：`blocker`（NFR-3 是硬约束；未忽略会把 per-machine 大体积可重生产物提交进库，污染版本树）。

---

## 不可机检项（须 defer 到 content-substance 层或人工）

本层显式声明以下 FR/NFR **不能**靠 grep/parse 判真伪，必须交给 content-substance level-specialist 或人工 walkthrough。机检层只能验「形」，不能验「质」：

- **A — FR-5 物理动作铁律（无裸情绪名作表演描述）**。可做**弱机检负样本**：在 `## 锁定文本块` 内 grep 裸情绪名（如 `表现悲伤`/`显得愤怒` 等 `表现|显得|流露出 + 情绪词` 模式）作 `warning` 提示，但「是否写成可观察物理动作 + 主动动词」是语义判断 → defer content 层（content 层应将其作 blocker 级首要校验项）。
- **B — FR-6/FR-7/FR-8 物理词汇取自 FACS 底表 / 内敛三层模型 / 强度阶梯**。能 grep 出「面部/眼神条是否带 `au_ref`」「内敛条是否含三层关键词」等**存在性近似**，但底表回溯正确性、三层是否真泄漏/抑制/冲突、强度阶梯是否共享情绪核 → 语义，defer content 层。
- **C — FR-10 引用契约样例正确性**。能 grep `表演请参考: _performances/perf_NNNN` 头是否存在、锁定串是否逐字嵌入 shot，但「样例选的是不是 validated entry」「嵌入是否语义贴合 shot」→ content 层 + 人工。
- **D — FR-13 验证通过判定正确性**。SV-4 只验 `status` 枚举合法；但「`status: validated` 是否真满足 至少一模型 表演达意≥4 ∧ 情绪可识别≥4 ∧ 过火≤2」需解析 `## 实测与验证` 三轴分数并交叉核验 status —— 这是 content 层的结构化解析校验（可半自动），非纯 grep。
- **E — NFR-1 跨剧目零耦合（body 无剧目专有名词/角色名）**。需一份剧目专名黑名单才能 grep；名单不全则漏检 → defer content 层 + 人工（含「是否 generic」的语义判断）。
- **F — NFR-2 跨 shot 引用字节稳定**。SV-8 只验 entry 内（锁定块 vs 检验视频）一致；跨**所有引用该 entry 的 shot** 的 byte-identical 需扫全 `ai_videos/` 各剧目 shot prompt，属引用层/content 层的全库交叉校验。
- **G — FR-12 webapp 集成（sidebar 可见 + 可浏览）**。运行时行为，非文件 schema → `validation.requires_manual_walkthrough`（人工在 webapp 确认 `_performances/` 挂载且 entry markdown 可浏览）。
- **H — OQ-1 过火 house style（精品微表情派判过火）**。审美判断 → content 层 + 人工。

---

## 汇总：本层 validator → severity

| ID | 校验 | FR/NFR | severity |
|---|---|---|---|
| SV-1 | 三级布局 / folder==stem / `_emotion.md` | FR-1,FR-2,FR-3 | blocker |
| SV-2 | 编号零补四位 / 全局唯一 | FR-2 | blocker；缺号 warning |
| SV-3 | 四维 frontmatter 必填 + 枚举 | FR-4 | blocker |
| SV-4 | status 枚举合法 | FR-13,NFR-4 | blocker |
| SV-5 | 必备 body 段存在 | FR-9 | blocker；高强度缺起始帧 warning |
| SV-6 | 中文占比 ≥95% | rule1,FR-3 | blocker |
| SV-7 | 检验视频 时长 ≤15s | rule2,FR-11 | blocker |
| SV-8 | 双模型双版 + 锁定串字节一致 | FR-11,NFR-2 | blocker |
| SV-9 | 渲染产物 gitignore 覆盖 | NFR-3 | blocker |
