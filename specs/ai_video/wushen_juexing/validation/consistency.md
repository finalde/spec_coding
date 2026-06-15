---
worker_id: level-specialist-04-consistency
stage: 5
role: level-specialist
level: consistency
status: complete
blockers: []
confidence: high
---

# 校验级别 — 角色视觉一致性（character-visual-consistency）

适用范围：stage-6 输出 `ai_videos/wushen_juexing/`，本轮仅 EP1（`episodes/ep01/`）。
依据：spec §命名/视觉锁定（命名表、视觉锁定、FR-4/FR-5、NFR-3）、`agent_refs/validation/ai_video.md` move #3、dossier `findings/angle-visual-style.md` §3 四角色锁定描述符。

四个受管角色（点名于任一 shot prompt 时受全部规则约束）：
**裴知秋(C1) / 裴昭(C2) / 裴霆(C3) / 凌虚子(C4)**。

项目结构契约（rule 12.8/12.9）：bible 落 `characters/cN_中文名/cN_中文名.md`（folder + filename 同名中文，N 不补零）。Seedream 立绘 prompt 可**内嵌**于 bible，或落单独 ref_images 文件——本级别只要求立绘 prompt **存在**（内嵌或独立皆可），不锁定具体文件名。

---

## 规则表（每条含 严重度 + 具体可执行检查）

### C-1 角色 bible 存在性
**规则**：EP1 任一 shot prompt 中点名的角色，必须解析到一份 bible：`characters/cN_中文名/cN_中文名.md`（folder 名 == filename 名 == 中文角色名，N 不补零）。
**检查**：
1. 抽取所有 shot prompt（`episodes/ep01/shots/shot*.md`）`人物/角色 Characters` 字段中出现的角色名集合 `S_shot`。
2. 对每个 `name ∈ S_shot`，断言 `characters/cN_{name}/cN_{name}.md` 存在且非空（C1=裴知秋, C2=裴昭, C3=裴霆, C4=凌虚子）。
3. 命中失败列出缺失角色名 + 期望路径。
**严重度**：缺 bible 文件 = **blocker**（move #3：missing descriptor file = blocker）。

### C-2 未声明角色 = blocker
**规则**：任一 shot prompt 点名 `characters/` 下未声明的角色，即视为漂移隐患。
**检查**：`S_shot − {裴知秋, 裴昭, 裴霆, 凌虚子}` 必须为空集；任何多出的具名人物（非群演/无名 NPC）触发失败。提示：无名角色应以"侍卫甲/族老/围观弟子"等通用称谓出场，不计为具名角色。
**严重度**：shot 引用 `characters/` 未声明角色 = **blocker**（severity 表："Shot prompt references a character not declared in `characters/`"）。

### C-3 Seedream 立绘 prompt 存在性
**规则**：每个受管角色须有一份 Seedream ref-image 立绘 prompt（竖屏/4K，含主体/面部/服装/姿态/背景/光源/风格段），用于锁定跨镜一致性（FR-5）。立绘可内嵌于该角色 bible 或落独立 ref_images 文件。
**检查**：对每个 `name ∈ S_shot`，断言其立绘 prompt 存在——满足以下任一即通过：
   (a) `characters/cN_{name}/cN_{name}.md` 内含可识别的 Seedream 立绘段（标题/标签含「立绘 / Seedream / ref-image」且含 主体/面部/服装/姿态/背景/光源/风格 多段结构）；或
   (b) 同目录存在独立立绘文件（任意文件名）含上述立绘段。
两者皆无 = 失败。
**严重度**：缺 Seedream 立绘 prompt = **blocker**（move #3 + severity 表："Missing Seedream ref-image prompt for a named character"）。

### C-4 一句话锁定 跨引用 byte-identical（EP1 内）
**规则**：每个受管角色的 **一句话锁定（≤30字）** 字符串，在其 bible 与每个点名该角色的 shot prompt 的 `人物/角色` 引用块中**逐字一致（modulo whitespace）**（NFR-3、FR-4、move #3）。
**检查**：
1. 从每个 bible 抽取该角色「一句话锁定」`L_bible(name)`（dossier §3 锁定句逐字继承；当前 dossier 值——注意 C1 名已由「裴玄」改定为「裴知秋」，bible 须用最终定名的锁定句）：
   - 裴知秋：`玄黑描金长衫、墨发高马尾、眸由颓转锋的清瘦少年。`
   - 裴昭：`朱红织金锦袍、金冠折扇、眉尾上挑的骄纵少主。`
   - 裴霆：`玄青蟒纹王袍、霜白鬓玉冠、鹰目不怒自威的家主。`
   - 凌虚子：`月白广袖道袍、素鞘长剑、足踏薄雾的清冷剑仙。`
2. 对每个 shot prompt 中点名 `name` 的引用块抽取重贴的锁定句 `L_shotK(name)`。
3. 规整化（去首尾及内部多余空白、统一全角标点）后断言：对同一 EP1 内所有 K，`normalize(L_shotK(name)) == normalize(L_bible(name))`，两两相等。
4. 失败时列出首个分歧 shot、bible 值与 shot 值的 diff。
**严重度**：同一 EP1 内同角色两镜锁定句漂移（或与 bible 不一致）= **blocker**（move #3：drift between two shots' descriptors = blocker；severity 表同列）。
**辅助检查**：锁定句长度 ≤30 字（超长 = **warning**，提示 bible 收紧）。

### C-5 四主色不撞（同框可辨识）
**规则**：四角色服装主色锁定互不撞色，便于同框辨识（spec 视觉锁定 / style_guide 主色表）：
   - 裴知秋 **玄黑描金** / 裴昭 **朱红织金** / 裴霆 **玄青蟒纹** / 凌虚子 **月白淡青**。
**检查**：
1. `style_guide.md` 角色主色锁定表必须列全四角色且四主色名互异（无两角色共用同一主色名）。
2. 每个角色 bible 的「服装主色」字段与 style_guide 表对应行**一致**（同一自然色名）。
3. 每个点名该角色的 shot prompt 服装描述使用其锁定主色（不得把裴昭画成玄黑、把裴知秋画成朱红等串色）。
**严重度**：style_guide 缺主色表 / 两角色主色撞名 / bible 与 style_guide 主色不一致 = **blocker**（同框辨识是 image-first 一致性策略的核心，等同角色漂移）。shot 内偶发串色描述 = **blocker**（drift）。

### C-6 觉醒态变体（暖金裂纹）不得当新角色/新描述符漂移
**规则**：裴知秋觉醒态（体表浮**暖金裂纹**、发梢挑暖金光、剑气/金光柱异象）若在任一 shot 出现，必须在其 bible 中记为**同一角色的状态变体**（如「常态 / 觉醒态」两栏），而非新建一个独立锁定描述符或新角色。觉醒态变体共享同一「一句话锁定」基底（C-4），仅追加状态化增量描述（暖金裂纹、暖金发梢、王体/武神躯异象），不得改写基底锁定句。
**检查**：
1. 若任一 shot 描述裴知秋觉醒态特征（暖金裂纹/王体异象/武神躯金光），断言 `c1_裴知秋` bible 含「觉醒态 / 状态变体」小节明确登记该变体属裴知秋。
2. 断言觉醒态 shot 仍重贴裴知秋同一基底锁定句（C-4），觉醒增量以附加描述出现，未替换或改写基底句。
3. 断言 `characters/` 下不存在为「觉醒裴知秋」单独新建的 bible 文件夹/角色条目。
4. style_guide「觉醒暖金+残血暗红裂纹」motif 与 bible 觉醒态描述一致（强度取 spec open question 定的「中档」）。
**严重度**：
   - 觉醒态在 shot 出现但 bible 未登记为状态变体 = **blocker**（被当成新描述符漂移）。
   - 为觉醒态另立新角色/新 bible = **blocker**。
   - 觉醒态 shot 改写了基底锁定句（而非附加增量）= **blocker**（C-4 drift）。

---

## 执行说明（validator 落地）
- 本级别在 stage-6 EP1 work_unit 的 `validation.started`（levels 含 `consistency`）时运行，针对 `episodes/ep01/shots/shot*.md` + `characters/c1..c4/*` + `style_guide.md`。
- 规整化（normalize）= 去首尾空白 + 折叠内部连续空白为单空格 + 不改动汉字与全角标点；whitespace-only 差异不算漂移。
- 受管角色集合恒为 {裴知秋, 裴昭, 裴霆, 凌虚子}；EP1 未点名的角色不触发其规则（但一旦点名即全规则约束）。
- 任一 blocker 命中 → `validation.issue.raised`（level=consistency, severity=blocker, 含 work_unit_id + 失败 shot/角色），work_unit 不得标 done；surgical 修补后重跑本级别至 0 blocker。
- 与 move #3 的偏移：dossier 假设 ref 图落 `characters/ref_images/<role>_seedream.md`；本项目按 rule 12.8/12.9 采用单文件/角色模式，故 C-3 只要求立绘 prompt **存在**（内嵌或独立），不锁定 `ref_images/` 路径——记此 divergence，其余 move #3 语义（缺 bible/缺立绘/EP1 内漂移 = blocker）完整保留。

## C-7 角色 prompt 统一标准（rule #12.5 v11，follow-up 018）— blocker

**规则**：所有角色档 `characters/cN_{名}/cN_{名}.md`（含未来新增）必须用同一套 prompt 标准：
- 恰好 **1 个**「# 视频 reference prompt — … (rule #12.5 v11)」段 + 紧随 1 个「### 3 句数字计数台词」表。
- video reference prompt 的 ```text 块字段齐全：主体 / 造型锁定 / 身高观感 / 服装 / 面部细节 / 姿态(0–7s 转身+中文计数 一二三) / 镜头 / 光线·色调 / 渲染样式 / 比例 / 时长 / 音频。
- **禁止**旧式「# Seedream 立绘」单段、临时「# 角色转盘 video prompt」等非标准段。
- canonical 范例：`c1_裴知秋`。

**检查（greppable）**：
```bash
for f in ai_videos/wushen_juexing/characters/c*/c*_*.md; do
  v=$(grep -c '视频 reference prompt' "$f"); c=$(grep -c '数字计数台词' "$f")
  old=$(grep -cE '# Seedream 立绘|# 角色转盘 video prompt' "$f")
  [ "$v" = 1 ] && [ "$c" = 1 ] && [ "$old" = 0 ] || echo "$f: 非标准(v11=$v 计数=$c 旧段=$old)"
done
```
**severity**：任一角色档缺 v11 段 / 缺计数台词 / 含旧式段 → `blocker`（FR-5）。每新增角色 stage-6 必过此检查。
