## Follow-up 001 — 2026-05-24

Source: user_input/follow_ups/001-20260524-actor-photo-directive-and-prompts-to-shots-rename.md
Summary: Add 演员参考照片解读契约 (actor photo = face/build anchor only, 装扮 strictly per prompt) as new common-level rule 12.5-A + apply to c1/c3/c4 turntable prompts. Patch raw_prompt.md to reflect user's `prompts/` → `shots/` rename in both ai_videos READMEs.

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — new sub-rule `#### 12.5-A 演员参考照片解读契约` inserted before rule 12.6. Establishes byte-identical contract paragraph that must appear in every character turntable prompt's `主体:` 行下方.
- `ai_videos/nvdi_tuihun_houhuile/characters/c1_陈凡/c1_陈凡.md` — turntable prompt `主体:` 行下追加契约段 + 装扮锚 line (黑发束白玉冠 / 玉白世家锦袍 / 装废态病弱妆 vs 演员日常素颜).
- `ai_videos/nvdi_tuihun_houhuile/characters/c3_陈国公/c3_陈国公.md` — turntable prompt 契约段 + 装扮锚 (紫金冠 / 长须银白及胸 强制加须 / 一品国公朝服).
- `ai_videos/nvdi_tuihun_houhuile/characters/c4_太监/c4_太监.md` — turntable prompt 契约段 + 装扮锚 (玄色冠 / 强制无须无胡 / 内监紫袍).
- `specs/ai_video/nvdi_tuihun_houhuile/user_input/raw_prompt.md` — layout diagram `prompts/` → `shots/` to match user's README edit; folder-per-asset path corrected to `shots/shotNN/shotNN.md` per rule 12.9.

No conflicts found in: world.md, style_guide.md, arc_outline.md, scenes/s1_陈国公府正厅 (scene reference 不涉及演员照片解读 per 12.5-A 应用范围 ❌ 部分), episodes/ep01/script.md + shotlist.md (无演员照片 / 文件夹路径直接引用).

Deferred:
- c2_女帝 — placeholder bible, no turntable prompt yet; will inherit 12.5-A 契约 when ep02+ 实出场时填档.
- ~~`prompts/` → `shots/` 是否提升为 canonical rule — 留待下个 follow-up~~ **Corrected in follow-up 002**: canonical rule already says `shots/` (migrated by xianxia_new/011 earlier than follow-up 001's grep). 无 drift, 无需 promote.

---

## Follow-up 002 — 2026-05-24

Source: user_input/follow_ups/002-20260524-shotlist-lock-decisions-and-shot14-cliff.md
Summary: User authorized parent-direct best-judgment on shotlist 待确认 items. Locked 6 decisions, generated shot14 cliff, corrected follow-up 001's wrong `prompts/` → `shots/` divergence claim.

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shotlist.md` — header re-locked from 13→14 shots / 68→70s total; "待 user 确认" section replaced with "已锁定决定" 6-row table; shot14 row demoted from "cliff 候选" to "cliff" with reveal motif 光位渐变 detail; renderorder note updated.
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot14/shot14.md` — created. 8s 特写锁机位 + 反向锐光 (顶左 30° → 0° 正面冷光 4200K), 3-5s 桃花眼瞳孔渐变 暗琥珀→冷金, V.O. "戏 ... 该开场了" ep02 入口锚。负向严防 reveal 锐光骤现 / 装废+reveal 同时出现 / 唇角勾起过大。
- `specs/ai_video/nvdi_tuihun_houhuile/user_input/raw_prompt.md` — `shots/` 注释 corrected: 从 "project-scoped naming divergence" → "canonical per xianxia_new/011" (follow-up 001 的判断有误, 实际无 drift).

No conflicts found in: shot01-13 prompts (无需 patch — 决定已 byte-aligned 进各 shot prompt 的 reaction shot 锁机位 / shot02 侧背仰角 / shot01 实拍诏书 等 detail).

Final ep01 状态: 14 shots locked, 70s total, 渲染 ready. 操作人下步: 渲染 3 角色 turntable + s1 scene walk-through, 按 shotlist 顺序拍 shot01-14, 后期剪映拼接出 ep01_final.mp4.

---

## Follow-up 003 — 2026-05-30 02:22:17

Source: user_input/follow_ups/003-20260530-shot02-face-eunuch-respectful-receive-edict.md
Summary: shot02 改为父子统一面朝太监恭敬接旨 (reverse POV, 父子正面入画), 太监不入画 (仍 OS)。取代 follow-up 002 锁定决定 (e) 的"侧背"构图。

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot02/shot02.md` — 全文 patch: 标题改"父子面朝接旨全景 (reverse POV)"; Summary / Characters / reference 备注 / 起始帧 / 结束帧 / 视频 prompt 的 镜头 + 动作 + 光线 全部由"侧背 (从太监身后 30°)"改为"reverse POV 父子正面面朝太监恭敬接旨, 双手前举 + 垂首, 太监不入画"; 负向加"不要 父子侧背入画 / 不要 太监入画"。小说原文段 陈凡 posture 由"不弓背不叩首慵懒"改为"垂首敛眉恭谨接旨 + 眸底藏锋"(与装废伪装自洽)。
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shotlist.md` — shot02 行景别由"全景 锁机位 (背向 / 侧背)"改为"reverse POV, 父子正面, 太监不入画"; 已锁定决定 (e) 标记被 follow-up 003 取代 (侧背 → reverse POV 正面)。

No conflicts found in: script.md (无 shot02 posture / 机位描述), dialogue.md (仅台词), c1_陈凡 bible (装废仍为总体 canon — 本 shot 公开恭谨属伪装表层, 不改 bible), shot01 + shot03-14 (shot01 太监正面朝镜头 / shot02 reverse POV 朝父子 构成 shot/reverse-shot 对偶, 几何自洽)。

---

## Follow-up 004 — 2026-05-31 22:01:23

Source: user_input/follow_ups/004-20260531-220123-shot01-no-unroll-eunuch-staging.md
Summary: shot01（3 分钟 fast-cut 重生成版）调度修正 —— 太监不做展卷动作、持已展开诏书直接宣读；居厅中长案前居中站位、面向画面外阶下跪礼的陈国公父子方向（**父子本镜不入画，下一镜 shot02 才进**，shot01 仅太监一人入画）；机位正面锁定，背景正厅中轴对称端正。

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/shot01/shot01.md` — 小说原文 + 情节 改为"持早已展开的诏书、无展卷之举、面向跪礼父子"；标题去"展开 motif"；Characters / Reference uploads / 参考 占位行 保持仅 **太监 + 场景**（父子不入画，shot02 进）；镜头由"特写 + 推 (从诏书推向太监)"改为"中近景 + 锁机位 (太监居正中、正面朝画面外父子方向, 父子不入画, 背景中轴对称端正, 无推无拉无展卷)"；动作去除"诏书缓缓展开"拍, 改为全程手持已展开诏书 + 平视画面外父子方向起手宣旨；场景行加"中轴对称端正"。
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shotlist.md` — shot01 行景别 特写→中近景 / 运动 推→锁机位 / 主角色 仍仅太监 (标注"父子不入画, shot02 进") / 内容 改"太监居厅中持展开诏书、面向画面外父子方向起手宣旨 (无展卷动作, 中轴对称端正)"；开场钩描述同步。
- `ai_videos/nvdi_tuihun_houhuile/episodes/ep01/script.md` — Hook 行 + SCENE 1 调度行去"展开"动作措辞, 改为"持早已展开诏书、居厅中、面向跪礼父子, 镜头正面对称、身后正厅中轴端正"。

No conflicts found in: dialogue.md (仅台词), c4_太监 bible (锁定描述符不变), 其余 shot (shot01 调度独立, 不影响 shot02+)。
时长不变 (shot01 仍 5s, ep01 仍 188s)。

---

## Follow-up 005 — 2026-05-31 14:40:30

Source: user_input/follow_ups/005-20260531-144030-chuchang-roster-completeness-and-qingjie-highlight.md
Summary: 出场角色完整性全集扫一遍 —— 每 shot 的 参考/角色/Characters 按出场角色派生规则列全画面内角色 (用户点名 shot02 漏列陈国公); shot 顶部小说段出场角色名加粗高亮 (显示层, 代码块内 情节 保持纯文本)。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — rule 5 v3 ① 段追加「出场角色名高亮约定 (per follow-up nvdi 005)」: Chapter excerpt / 小说原文 段内出场角色名以 markdown 粗体标注, 显示层 (去 ** 后 byte-identical), 代码块内 情节 不加粗。
- `episodes/ep01/shots/shot02/shot02.md` — 补 陈国公 入 参考/角色/Characters (`陈凡 / 陈国公`); 镜头行 stale「收纳…案前太监」→「收纳父子正面跪礼区 (reverse POV 自太监位置朝父子拍, 太监不入画)」(对齐 follow-up 003)。
- `episodes/ep01/shots/shot08/shot08.md` — 补 陈国公 (全景接旨跪礼区, `陈凡 / 陈国公`)。
- `episodes/ep01/shots/shot14/shot14.md` — 补 陈凡 + 陈国公 (全景太监退场父子留, 三人同框 `太监 / 陈凡 / 陈国公`)。
- `episodes/ep01/shots/shot19/shot19.md` — 补 陈国公 (全景去而复返撞见, `陈凡 / 陈国公`)。
- `episodes/ep01/shots/shot01–shot28` (全 28 镜) — 顶部小说段出场角色名加粗 (字面出现处); 单角色镜 roster 经验证已完整, 保持 byte-identical。

已知局限: 部分镜小说正文以代词/别称指代角色 (「他」「国公」「父子二人」「老国公」), 无字面角色 token, 故 shot04/14/18/19(陈凡侧)/21/24 加粗为零或不全; 各镜 `Characters:` 行为权威完整 roster。

No conflicts found in: script.md / shotlist.md (主要角色列保持聚焦单角色语义, 非出场全集, 不改), dialogue.md, 角色 bibles (锁定描述符 byte-identical 引用未改)。

---

## Follow-up 006 — 2026-05-31 14:40:30

Source: user_input/follow_ups/006-20260531-144030-chapter-first-full-novel-prose.md
Summary: 项目从「无源小说」升级为 chapter-first —— 写 ≥5000 字 ep01 完整小说正文为 canonical 源; 每 shot 顶部由 `## 小说原文`(短片段) 改为 `## Chapter excerpt` + 该镜对应段落 200-400 字 verbatim 引用; 代码块内 情节 同步。

Auto-updated:
- `my_novel/nvdi_tuihun_houhuile/chapters/0001-第1集 接旨退婚.md` — 新建, ≥5000 字中文小说正文 (28 段对应 28 镜, 连续成章, 覆盖接旨退婚 + 锋芒初露全弧)。
- `my_novel/nvdi_tuihun_houhuile/README.md` — 新建小说扉页 (Chinese title + 概要 + 章节列表 link + 题材标签)。
- `.claude/agent_refs/project/ai_video.md` — rule 5 v3: nvdi_tuihun_houhuile 从「No reader-side novel」示例移出, 加入「Reader-side novel exists」(标注 post-follow-up 006 migrated)。
- `episodes/ep01/shots/shot01–shot28` (全 28 镜) — 顶部 `## 小说原文` 段 → `## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)` + verbatim blockquote; 代码块内 `情节:` 同步为该段纯文本 verbatim。
- `specs/.../user_input/revised_prompt.md` — 新建 (raw + follow-ups 001-006 合成)。

chapter 为源, script.md / shotlist.md / dialogue.md 维持既有 derived 产物 (剧情 beat 一致, 本次未重生成, 与新 chapter 无冲突)。

No conflicts found in: world.md, style_guide.md, arc_outline.md, scenes/, 角色 bibles。

---

## Follow-up 007 — 2026-05-31 15:16:12

Source: user_input/follow_ups/007-20260531-151612-silent-shots-closed-mouth-kling.md
Summary: 非说话镜给 Kling 显式闭口指令 (shot04 默剧生成时角色乱动嘴/鸟语)。用户选「全部非说话镜」13 镜。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — rule 5 v3 台词三选一契约下新增「在画人物口型契约 (per follow-up nvdi 007)」: 默剧/静默/仅环境音/V.O.内心独白/听旨等在画不出声镜, `台词` 须显式 `· 在画人物口型: 全程闭口/嘴唇不动/无说话口型`, `负向` 须含 不要说话/不要嘴部开合/不要说话口型/不要lip sync/不要自动配音; 根因 Kling 默认加口型。
- `episodes/ep01/shots/shot02,04,06,08,11,14,15,16,17,18,24,27,28` (13 镜) — `台词 / 字幕:` 行 append 在画人物口型闭口子句 (V.O.镜注明 OS 画外配音非现场出声; shot02 听旨方注明太监 OS 不入画); `负向:` 行 append 8 项 mute 反向词。V.O.镜 OS 字幕原文全部保留。

No conflicts found in: 说话镜 (shot01,03,05,07,09,10,12,13,19,20,21,22,23,25,26 — 说话人嘴部应动, 未加闭口), script.md/shotlist.md/dialogue.md, 角色 bibles。

---

## Follow-up 008 — 2026-05-31 15:16:12

Source: user_input/follow_ups/008-20260531-151612-shot2-shot3-dedup-and-beiying-in-cankao.md
Summary: shot2/shot3 台词重复去重; shot2 去太监背影; 通用规则——所有 shot 即使背影/远景角色也须入 `参考` (以便 attach 参考图)。

Auto-updated:
- `episodes/ep01/shots/shot02/shot02.md` — 台词去重: `(太监 OS 续):"陈国公府三公子陈凡……"` → `(太监 OS 续宣旨, 父子垂首静听; 宣旨词承 shot01、续于 shot03, 本镜不重复宣旨词)`; `负向` append 「不要 太监入画 / 不要 太监背影 / 不要 第三人入画」(去 reverse-POV 误生成的太监背影)。shot03 保留完整宣旨句 (对齐 chapter P3)。
- `.claude/agent_refs/project/ai_video.md` — 参考行格式 新增 bullet「背影/远景/剪影出场也必须列入 `参考` (per follow-up nvdi 008)」+ 出场角色派生规则表后加注: 「turntable 无须」≠「参考可省」, 仅纯 OS/画外不列。
- 全 28 镜 roster 重扫 (2 worker, 保守判据) — **0 处需补**: 被 flag 的 shot03/05/07/08/10/12/13/15 中, 其他角色均为「注视对象 / 画外 OS / 已离场背影」(shot 档 `动作` 已标画外, 如 shot20「与画外父亲对视」), 严格本镜取景下不在画, 正确未列。

Open question — RESOLVED (用户选「只 shot08 补太监」): `episodes/ep01/shots/shot08/shot08.md` — 补太监(递诏手臂/背影入画, 不露正脸): Summary + `参考`(加 太监：place_holder) + `- Characters`(加 太监（背影/递诏手臂, 不露正脸）) + `角色`(append 太监 byte-identical 一句话锁定 + 「本镜仅递诏手臂/背影入画，不露正脸」后缀) + `动作`(0-2s 太监背影/手臂前递诏书) + `负向`(加 不要 太监正脸入画)。其余「宣旨/反应」镜维持现状 (对侧为画外/注视对象, 不补)。

---

## Follow-up 009 — 2026-06-01 12:01:14

Source: user_input/follow_ups/009-20260601-120114-shot-self-contained-own-dialogue-os-voice-ref.md
Summary: shot prompt 自包含 (禁跨 shot 引用); 每 shot 自带台词、连续对白拆成不重叠连续片段; 画外 OS 说话人声音入参考。(针对 shot02 台词, 泛化为通用规则。)

Auto-updated:
- `episodes/ep01/shots/shot02/shot02.md` — 台词由「(太监 OS 续宣旨…承 shot01…续于 shot03…本镜无新增字幕)」改为本镜自己的 OS 片段 `太监(画外 OS 宣旨, 不入画):"陈国公府三公子陈凡，"`(去跨 shot 引用 + 给本镜台词); `参考` 加 `太监(画外 OS·声音请参考)：place_holder`(OS 说话人声音参考); 闭口指令保留。
- `episodes/ep01/shots/shot03/shot03.md` — 台词去掉重复的「陈国公府三公子陈凡，」→ `太监(续宣):"纨绔放荡, 不学无术, 得不配位。"`(与 shot02 连贯、不重复)。
- `episodes/ep01/shots/shot01/shot01.md` — `镜头` 去「shot02 才进」跨镜引用 → 「父子不入画, 仅以太监朝向与视线暗示其在画外」; Summary/Characters 同步去 shot02 引用。
- `.claude/agent_refs/project/ai_video.md` — 三条通用规则: (参考行格式)「画外 OS 说话人声音参考」bullet (per follow-up nvdi 009); (台词契约) 「每 shot 自带台词 + 跨 shot 连贯」+「prompt 正文禁跨 shot 引用」段。

圣旨连续拆分 (跨 shot 连贯不重复): shot01「奉天承运，女帝诏曰：」→ shot02「陈国公府三公子陈凡，」→ shot03「纨绔放荡，不学无术，得不配位。」→ shot05「今解除朕与其之婚约。钦此。」

No conflicts found in: chapter 0001 (台词去重/拆分仅在 shot 台词字段, 小说正文 verbatim 不动), shot05 (已含「今解除…钦此」, 连贯无重复), 其余 shot, script.md/shotlist.md, 角色 bibles。
修正记录: 本 follow-up 修正 follow-up 008 把 shot02 台词清空 (「本镜无新增字幕」) 的做法 —— 应给本镜自己的 OS 片段。

---

## Follow-up 010 — 2026-06-01 12:38:43

Source: user_input/follow_ups/010-20260601-123843-zouwei-blocking-field-every-prompt.md
Summary: 每个 prompt 须描述人物站位/朝向/相对位置 (如太监面向父子) + 各人物相对场景的朝向位置。新增 `走位:` 字段 (全 28 镜) + 通用契约 + scene 站位锚。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — (字段矩阵) 新增 field 4b `走位:` (置于 `镜头:` 后、`动作:` 前); (镜头取词契约后) 新增「走位/站位契约 (per follow-up nvdi 010)」: 每镜描述每个在画人物 位置+朝向+相对位置, 单人镜亦须, 世界坐标系 (东南西北+面向对象) 不用画面左右; (markdown 渲染契约) field-label highlight 列表加入 `走位:`。
- `ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — 新增「站位/走位锚 (调度几何)」段: 方位锚 (北=长案/太师椅/水墨/高窗; 南=朱漆厅门; 西墙高窗) + 默认接旨态站位 (太监厅中长案前面南; 父子并跪跪礼区面北, 陈国公居东陈凡居西) + 锋芒态站位 (陈凡起身移长案前; 陈国公 shot19 南门跨入面北、与陈凡南北相对; shot27-28 陈凡独处)。
- `episodes/ep01/shots/shot01–shot28` (全 28 镜) — prompt body 插入 `走位:` 字段 (镜头后、动作前), 从 scene 站位锚派生本镜在画人物的位置+朝向+相对关系 (世界坐标系)。INSERT-ONLY, 其余字段未动。

约定 (本次判断, 已在交付中说明供用户复核): 走位用世界坐标 (东南西北); 父子并跪 陈国公居东、陈凡居西。

No conflicts found in: chapter 0001, script.md (script 已有【调度】块, 与 scene 站位锚一致), shotlist.md, 角色 bibles。各镜 `走位:` 与既有 `镜头:` 的方位描述一致 (如 shot01 镜头「太监居正中面向画外父子」↔ 走位「面向南」; shot02 reverse POV ↔ 走位「太监正北画外」)。
注: scene 档「## 出现镜头 (ep01)」段为旧 6-7 镜列表 (stale, 与现 28 镜不符), 未在本次修改范围 —— 已记录, 待后续校正。

---

## Follow-up 011 — 2026-06-01 12:38:43

Source: user_input/follow_ups/011-20260601-123843-scene-background-plate-system.md
Summary: 仅标 scene 名不足以保证背景一致; 每 scene 成体系生成多面相/方位背景图 (存 scene 下), 每镜指明用哪张。用户选: 全套 6 张; 引用位置=改参考行场景占位。

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — 新增「背景图系统」段: 6 张 plate (bg1_朝北_长案主位 / bg2_朝南_厅门 / bg3_朝东_东侧墙 / bg4_朝西_西窗 / bg5_高位俯瞰 / bg6_案前虚化背景), 各含独立 text-to-image prompt + 用途表; PNG 存 `scenes/s1_陈国公府正厅/{plate_id}.png`。
- `.claude/agent_refs/project/ai_video.md` — 参考行格式新增「场景背景图系统 (per follow-up nvdi 011)」: 每 scene 成体系多面相背景图存 scene folder, shot 参考占位须指明具体 `{场景名}·背景图 {plate_id}：place_holder`, 依相机朝向选 plate。
- `episodes/ep01/shots/shot01–shot28` (全 28 镜) — `参考:` 场景占位 `陈国公府正厅：place_holder` → `陈国公府正厅·背景图 {plate_id}：place_holder`。bg1朝北: 01,03,05,07,08,10,12,17,18,20,21,23,24,26,27,28 (16镜, 拍太监正脸/陈凡在案=相机自南向北); bg2朝南: 02,04,06,09,11,13,14,15,16,19,22,25 (12镜, 拍父子正脸/陈国公在门=相机自北向南)。

No conflicts found in: chapter 0001, script.md, shotlist.md, 角色 bibles。约定: ep01 全沿南北轴, 仅用 bg1/bg2; bg3-6 系统补全/备用。

---

## Follow-up 012 — 2026-06-01 12:38:43

Source: user_input/follow_ups/012-20260601-123843-reveal-eye-gaze-not-light.md
Summary: reveal 眼神「锐光/冷金锐光」让 Kling 把眼睛渲染成字面发光 (超能力感); 改为眼神/神态语言 + 负向。表达很重要。

Auto-updated:
- `.claude/agent_refs/project/ai_video.md` — 新增「眼神 reveal / 锐光表达契约 (per follow-up nvdi 012)」: reveal 眼神 motif 用神态语言 (瞳孔微缩/目光如刃/凌厉/冷冽) + 加注「纯神态非发光」, 负向含 不要眼睛发光/瞳孔发光/眼内光效/超能力发光特效; 根因 Kling 把「光」字面渲染成眼睛射光。
- `episodes/ep01/shots/shot06,15,16,20,21,23,26,28` (reveal 8 镜) — `动作:` 「锐光一闪/冷金锐光/冷金锋芒/锐定」→ 眼神/神态语言 (眼神一锐即敛、目光如刃/凌厉/冷冽沉定, 加注非发光); `负向:` 追加 不要 眼睛发光/眼睛放光/瞳孔发光/眼内光效/眼睛冒光/超能力发光特效。
- `episodes/ep01/shots/shot06,15,20,26,28` — `光线 / 色调:` 「桃花眼冷金锐光高光」等给眼睛打光指令 → 「眼神冷冽锐利/目光如刃 (纯神态, 非眼睛发光)」。

No conflicts found in: 情节 (小说正文 verbatim 文学化「锐光」保留, 由动作/光线/负向 主导渲染), chapter 0001, 其余镜。

---

## Follow-up 013 — 2026-06-01 13:56:53

Source: user_input/follow_ups/013-20260601-135653-scene-orientation-folders-video-first-import.md
Summary: 场景背景图改 folder-per-朝向 (每朝向一 folder + 该朝向 prompt 的 md); video-first 流程; 命名支持导入功能把 mp4/png 归位对应 folder。

Auto-updated:
- `ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/{plate_id}/{plate_id}.md` × 6 (新建) — bg1_朝北_长案主位 / bg2_朝南_厅门 / bg3_朝东_东侧墙 / bg4_朝西_西窗 / bg5_高位俯瞰 / bg6_案前虚化背景, 各含该朝向 image-from-video prompt + 流程 + 输出命名说明。先前内联在 scene 主档的 6 段 prompt 移入各 folder。
- `ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — 「背景图系统」段改为: 生成流程 (video-first: 主档 walk-through video → s1_陈国公府正厅.mp4 存 scene 根 → 上传 → 各朝向 md 出图) + 各朝向 folder 索引表 + 命名/导入约定 (prompt/folder/输出文件同名; mp4→scene 根, {plate_id}.png→同名子 folder); 删去内联 6 prompt; 段首 PNG 路径改为 `{plate_id}/{plate_id}.png`。
- `.claude/agent_refs/project/ai_video.md` — 「场景背景图系统」规则更新 (per follow-up nvdi 011+013): folder-per-朝向结构 + video-first 流程 + 命名/导入约定。

No conflicts found in: shot `参考:` 行 (已是 `陈国公府正厅·背景图 {plate_id}：place_holder`, plate_id=folder 名, 无需改), chapter, shotlist, 角色 bibles。
注: scene 主档旧 single 场景立绘 text-to-image prompt (lines ~47-73) 与旧 walk-through video prompt 仍在 —— walk-through 即 video-first 流程的源 mp4 prompt (保留); 旧 single 立绘被 folder-per-朝向 系统取代 (低优先, 暂留, 后续可清)。

---

## Follow-up 014 — 2026-06-01 14:13:34

Source: user_input/follow_ups/014-20260601-141334-bg-prompt-key-first-and-photoreal-texture.md
Summary: 背景图/视频 prompt 首行加 key (供下载文件含 key → 导入+重命名归位 folder); 强调影视级写实质感 (反卡通) + 增加细节/质感/美感 (如精良古装剧置景)。

Auto-updated:
- `scenes/s1_陈国公府正厅/{bg1..bg6}/{plate_id}.md` × 6 (重写) — ```text``` 块首行加 key `{plate_id}`; 新增 `质感/细节:` 行 (木纹包浆/石材纹理/漆面微裂/黄铜氧化/宣纸烫金/斜光浮尘/丁达尔光束) + `风格:` 行 (影视级真人实拍写实+cinematic+4K HDR+超写实 photorealism+电影级布光色彩分级+古装剧置景美感, 类比琅琊榜/长安十二时辰/知否); 主体加丰富材质细节; `负向` 强化 (不要 卡通/动画感/3D游戏场景/CG渲染感/塑料质感/扁平光/廉价置景/过曝失真); 顶部说明补 key-首行→导入归位。
- `scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — walk-through 视频 prompt ```text``` 首行加 key `s1_陈国公府正厅`; 末尾加 `风格:`(影视级写实质感+古装剧置景)+`负向:`(反卡通) 行; 「命名/导入约定」补「prompt 首行写 key」条。
- `.claude/agent_refs/project/ai_video.md` — 场景背景图系统规则补 (per follow-up nvdi 014): prompt 首行写 key (供下载文件名含 key→导入重命名归位) + 写实质感要求 (anti-cartoon, 强调真实材质/古装剧置景美感, 负向强禁 卡通/动画/游戏/CG/塑料)。

No conflicts found in: shot 文件 (shot `渲染样式:` 已含 photorealism; 本次仅改 scene 背景 prompt), chapter, shotlist, 角色 bibles。

No conflicts found in: chapter 0001 (台词去重仅在 shot 台词字段, 不涉及小说正文), script.md/shotlist.md, 角色 bibles。

---

## Follow-up 015 — 2026-06-01 14:40:18

Source: user_input/follow_ups/015-20260601-144018-import-route-by-orientation-segment.md
Summary: 修正 014——实测 jimeng 下载文件名取 prompt `主体:` 行正文 (非首行 key), 故「首行 key→归位」失效。改为按朝向 folder 的「方位段」路由, 并实跑把用户已下载的 6 张朝向图归位到对应 bg folder。

根因: jimeng/即梦下载命名 = `jimeng-{date}-{id}-{主体行前段}.png`, 不含我们设想的首行 plate_id key。文件名里唯一可靠区分朝向的是**方位词** (朝北/朝南/朝东/朝西/高位俯瞰/案前)。

Auto-updated:
- `projects/ai_video_management/libs/infrastructure/writers/downloads__writer.py` (代码) — 新增 scene→plate 路由: `_plate_orientation_token` (取 `bg\d+_` 后第一段 = 方位) + `_match_scene_plate` (scene 命中后按方位段子串匹配下沉到 bg 子 folder)；`import_drama` 在 chosen.kind=="scene" 时调用，kind 记为 `scene_plate`；模块 docstring 补述。**只匹配方位段、不匹配描述段** (描述词如 厅门/东侧 会散落别朝向文件名→串档)。
- `scenes/s1_陈国公府正厅/bg6_案前虚化背景/` → 重命名 `bg6_案前_虚化背景/` (+ 内 .md 同名)，补方位段下划线使方位段=`案前` 可匹配 `案前跪礼区…` 文件名；md 首行 key、heading、prose 同步。
- `scenes/s1_陈国公府正厅/{bg1..bg6}/{plate_id}.md` × 6 — 顶部 prose 从「首行 key→归位」改述为「方位段→归位」(提取 `bg{N}_` 后第一段匹配)。
- `scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — index 表 + folder 表 bg6 改名；「命名/导入约定」段整段重写为方位段路由机制 (含 jimeng 实测命名规则 + 「只匹配方位段不匹配描述段」告警 + walk-through mp4 留 scene 根)。
- `.claude/agent_refs/project/ai_video.md` — 场景背景图系统「命名/导入约定」+ 原 014「首行写 key」两条 bullet 改述为方位段路由 (per nvdi 015 supersedes 014)。

实跑结果 (真实 `DownloadsImporter.import_drama`):
- 6 张 jimeng PNG 从 Downloads 全部归位 → bg1–bg6 对应 folder, 自动重命名为 `{plate_id}.png`, moved 全为 `scene_plate`, 0 unmatched / 0 error。
- 清理: scene 根一张旧的误路由 `s1_陈国公府正厅.png` (SHA256 与 bg1 一致 = 之前导入未进朝向 folder 的重复图) 已删除；scene 根现仅留 .md + 2 个 walk-through .mp4。

No conflicts found in: shot 文件 (shot `参考:` 场景占位用 `背景图 {plate_id}`, bg6 旧名未被 shot 引用, 仅 scene 主档+bg6 自身引用 → 已改), chapter, shotlist, 角色 bibles, validation/*。

---

## Follow-up 016 — 2026-06-01 15:07:42
Source: user_input/follow_ups/016-20260601-150742-scene-prompts-gorgeous-gufeng-onmyoji.md
Summary: 场景 prompt 层改「绚丽唯美古风」(参考郭敬明《阴阳师/晴雅集》)，重新生成 scene 所有 prompt。Interactive 澄清定: 风格=电影级唯美打底真实 (放宽反CG)，范围=仅 scene 所有 prompt (shot 不动)。修正 follow-up 014 的「必须真人实拍写实 + 强禁 CG」。

Auto-updated:
- `scenes/s1_陈国公府正厅/{bg1..bg6}/{plate_id}.md` × 6 — `主体/光线/质感/风格/构图/负向` 全部重写: 真实材质打底 + 叠加绚丽唯美元素 (鎏金描金/金箔流光/云雾氤氲/飞花落瓣/纱幔轻扬/烛火宫灯/琉璃/丁达尔光束/暖金 bokeh/浮尘流光/缠枝祥云回纹雕饰) + 宝石色调; `风格:` 统一为「影视级唯美古风…类比郭敬明《阴阳师/晴雅集》」; `负向:` 去「不要 CG 渲染感/3D 游戏场景/illustration」改「不要 廉价游戏CG感」, 保留反卡通/反塑料/反扁平/反廉价。**各 plate `主体:` 行方位词原位保留 (朝北/朝南/朝东/朝西/高位俯瞰/案前)，不破 follow-up 015 的方位段导入路由。**
- `scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — (a) walk-through 视频 prompt 的 `场景/时辰/配色/空间/光线色调/风格/负向` 注入同套唯美 DNA (新增纱幔/琉璃宫灯/飞花/云雾/描金/暖金倒影, 几何相机路径+dwell锁机位+≤15s+纯视觉 约束不变, ambient 飞花袅烟不构成抖动); (b) 旧 single 场景立绘 text-to-image prompt 的 `[主体]/[细节]/[风格]/[负向]` 同步改唯美古风 + 新增「唯美元素」清单行。
- `.claude/agent_refs/project/ai_video.md` — 「写实质感要求(014)」改为「质感/美术方向(014+016)」: 真实质感打底+反卡通/塑料/廉价为通则; 美术方向 per-project (默认=真人实拍写实+强禁CG / 唯美古风 opt-in=电影级唯美打底真实+放宽反CG); nvdi 选唯美古风, 项目内全场景统一并记 divergence。

No conflicts found in: final_specs/spec.md + validation/* (无写实/photorealism/反CG 硬断言, 美术方向未被 spec 锁定 → 无冲突可改); shot 文件 (本次范围仅 scene, 29 shot 渲染样式按澄清保持不动); chapter/shotlist/角色 bibles; 导入路由 (folder 名与方位段未变, 6 张已归位 PNG 不受影响, 下次重生成图沿用唯美 prompt)。
注: shot 背景将 reference 这套唯美场景图/视频 → 跨镜视觉自然偏唯美; 若后续要 shot 渲染样式也显式跟唯美, 另开 follow-up (本次用户明确限 scene)。

---

## Follow-up 017 — 2026-06-01 16:08:15
Source: user_input/follow_ups/017-20260601-160815-scene-tang-song-opulent-decor-walls-floor.md
Summary: 场景 prompt 再加雍容华贵陈设细节 (室内装饰/雕刻/图案/陈设书画), 明确墙上花纹 + 地面(砖vs毯), 朝代定位**中国古代唐宋时期** (非明清)。同一轮含用户追加的「墙花纹 + 地砖还是地毯 + 唐宋风格」要求。

判断 (interactive, 未再追问): 朝代取「唐风为体、宋韵为饰」综合 (雍容华贵偏唐之富丽 + 唯美书画合宋之雅致); 与 016《阴阳师/晴雅集》参考不冲突 (阴阳师/平安美学即唐风衍生) → 阴阳师留作唯美光氛参考, 唐宋作朝代/陈设/纹样参考。

Auto-updated:
- `scenes/s1_陈国公府正厅/{bg1..bg6}/{plate_id}.md` × 6 — 各加 `陈设书画/雕饰纹样 (唐宋风格)` 整行 (按朝向分配可见墙面/区域): 障壁画/团窠织锦壁衣/墙裙联珠卷草 (墙花纹) + 紫檀架格陈唐三彩宋青瓷/鎏金狻猊博山炉/玉璧经卷 + 落地山水屏风 + 壸门牙板卷草透雕 + 斗八藻井沥粉贴金宝相莲 + 梁枋碾玉装五彩遍装彩画 + 雄大斗拱朱白叠晕 + 地面 (灰青莲花团窠纹磨光方砖墁地 + 跪礼区织锦地毯, 砖毯并存); `风格:` 尾加「朝代定位唐宋古风 (唐之雍容富丽+宋之雅致; 宝相花/团窠/联珠/卷草唐草/碾玉装彩画) + 类比唐宋宫廷绘画/障壁画屏风《捣练图》《韩熙载夜宴图》」。bg1/bg5 `主体:` 内「一品太师椅/太师椅」→「宋式高背官帽椅 (壸门券口/铺锦褥) / 月牙凳绣墩」。
- `scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — (a) walk-through 视频 `空间` 段加 `陈设 (唐宋风格)` 整句 (障壁画/壁衣/墙裙纹 + 架格唐三彩宋瓷 + 屏风 + 藻井碾玉装彩画 + 方砖墁地+跪礼区地毯), `风格:` 加唐宋朝代定位; (b) 旧 single 立绘 `[细节]` 加 `陈设书画/雕饰(唐宋)` + `墙上花纹` + `地面(砖?毯?)` 三条 bullet, `[风格]` 加唐宋朝代定位; (c) 全文件 `太师椅`→`宋式高背官帽椅` (replace_all, 覆盖 空间/5 个 dwell/立绘构图)。
- `.claude/agent_refs/project/ai_video.md` — 唯美方向补「场景陈设完整性 + 朝代定位」要求 (墙纹/地面砖vs毯/书画陈设须显式描述; 选定朝代后须避免他朝代家具彩画穿越)。

清除的明清穿越元素: 太师椅→宋式高背官帽椅; 博古架/多宝格→紫檀架格; 景泰蓝/掐丝珐琅→唐三彩/宋青瓷(汝窑天青/影青); 和玺/旋子彩画→宋碾玉装/五彩遍装+唐沥粉贴金宝相; 抱柱楹联/中堂→障壁画/屏风。

验证: 6/6 plate `主体:` 行方位词仍在开头段 (不破 015 路由); 全 scene 已无 `太师椅` 残留; shot 文件未硬编明清家具 (经背景图 reference 自动继承唐宋唯美)。

No conflicts found in: final_specs/spec.md + validation/* (未锁朝代/家具); shot 文件 (仅 scene 范围; shot 经 `参考: 背景图 {plate_id}` 继承, 无硬编冲突); chapter/shotlist/角色 bibles; 导入路由 (folder 名/方位段未变)。

---

## Follow-up 018 — 2026-06-01 16:39:25
Source: user_input/follow_ups/018-20260601-163925-remove-edict-add-architecture-game-refs.md
Summary: (1) 桌上不放「奉天承运」圣旨 → 从场景生成 prompt 全移诏书; (2) 屋内细节不够 → 补建筑营造层 + 唐宋游戏画质参考锚 (web search 确认 剑网3唐/逆水寒宋·营造法式)。

判断: 移诏书双理由 —— ①「奉天承运」明初朱元璋始创、明清专属 (与唐宋穿越); ② 诏书是接旨态 shot 剧情道具 (太监展开), 不应烤入跨 shot/跨集复用的纯背景 plate。web search (WebSearch×2) 确认参考锚: 唐风→《剑网3》家园厅堂, 宋构→《逆水寒》汴京·《营造法式》。

Auto-updated:
- `scenes/s1_陈国公府正厅/{bg1..bg6}/{plate_id}.md` × 6 — ① bg1/bg5 `主体`+`质感` 移诏书, 案上换唐宋文房 (经卷书帖/鎏金狻猊香炉/汝窑天青瓷/青玉镇纸), 案前改织锦地毯; ② 每 plate 新增 `建筑木作/门窗顶棚 (唐宋·营造法式)` 整行 (月梁/阑额普拍枋/柱头补间铺作斗栱/叉手托脚 + 斗八藻井/平棋平暗 + 毬文格子门/破子棂窗 + 须弥座台基/勾栏望柱 + 覆莲柱础 + 朱白碾玉装彩画, 按朝向分配); ③ `风格:` 尾挂游戏参考锚 (《剑网3》唐 / 《逆水寒》宋·营造法式)。bg6 虚化层加斗栱藻井虚影 + 参考锚。
- `scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — walk-through 视频: `场景/配色/空间` 移诏书+加营造法式木作 (藻井/铺作/格子门/台基); dwell **#4 案前中景 / #5 长焦特写** 由「朱红诏书/奉天承运」改为**案上唐宋器物** (鎏金狻猊博山炉出香 / 汝窑天青瓷笔洗冰裂釉 / 青玉镇纸), dwell #1/#3 诏书→织锦地毯+藻井, `光线/节奏` motif 改案上香炉陈设, `风格` 加营造法式+游戏锚, `用法` note motif 改案上陈设 (几何相机路径/时长/焦距全程不变)。立绘: `[主体/时辰/构图/背景/道具/主色]` 去诏书+改唐宋营造+加 `建筑木作` bullet, `[风格]` 加营造法式+游戏锚, `[负向]` 加明清穿越禁用 (太师椅/博古架/景泰蓝/和玺彩画/抱柱楹联/奉天承运圣旨)。scene metadata: 标志道具 (标注诏书为 shot 道具不入背景) / 配色 / 一句话锁定 / bg5 索引行 去诏书+改唐宋方砖斗栱。
- `.claude/agent_refs/project/ai_video.md` — 唯美方向补「建筑木作 + 朝代措辞 + 参考锚」: ①屋内细节补营造层(非只陈设); ②朝代穿越检查含道具措辞(禁「奉天承运」); ③per-shot 剧情道具不烤入静态背景; ④细节密度可挂游戏级唐宋参考锚。

验证: 6/6 plate 方位词仍在主体行开头 (不破 015 路由); 全场景生成 prompt 已无「奉天承运」(仅立绘负向作禁用句保留); 诏书仅留 plot/state metadata (站位接旨态/空厅态/出现镜头) 供 shot 用。

DRIFT 标记 (需用户知悉): 「一句话锁定」LOOK 串去掉「朱红诏书」并改唐宋方砖斗栱; 既有 29 个 shot 的 `场景:` 行仍是旧 byte-copy (含「朱红诏书 / 灰青地砖」) —— 按本轮"shot 不动"约束未改, 待用户触发 shot 重生成时自动同步。

No conflicts found in: final_specs/spec.md + validation/* (未锁道具/朝代); chapter/shotlist/角色 bibles; 导入路由 (folder 名/方位段未变)。

---

## Follow-up 019 — 2026-06-02 12:01:16
Source: user_input/follow_ups/019-20260602-120116-scene-prompts-photoreal-kill-cartoon-stars.md
Summary: 上传 video 没问题但加 prompt 后 bg 图像动画片 (色彩/不真实光线/星星)。把 8 个 scene prompt 的渲染风格全部拉回照片级真实, 唐宋雍容华贵的陈设/建筑/书画内容保留不动。

根因诊断: 016-018 为「唯美」做的三件事联合导致卡通化 —— ①放宽反CG (删「不要CG渲染感/3D游戏场景」改「唯美CG氛围」); ②挂游戏参考锚 (剑网3/逆水寒) + 郭敬明《阴阳师》(CG/奇幻); ③堆光效粒子 (暖金 bokeh/浮尘流光/飞花/金箔流光/光尘漂浮 = 用户看到的「星星」) + 宝石色调/暖金满屏 (色彩失真)。即便参考 video 写实, prompt 的 风格+负向 主导了输出。

Auto-updated (6 plate + 视频 + 立绘, 共 8 prompt):
- `风格:` 全改 —— 「影视级真人实拍写实 · 超写实 photorealism · 照片级真实质感 · 真实自然光与真实电影色彩分级 (自然不过饱和、不偏色) · 真实材质 (…均为实物质感非自发光) · 唐宋营造法式真实木构 · 雍容华贵但写实克制」; 参考锚换**真人实拍/实景搭建** (《妖猫传》唐风实景 / 《长安十二时辰》/《清平乐》/《梦华录》实景古装剧 / 故宫·山西唐宋古建实拍 / 专业建筑摄影), **删除游戏锚 (剑网3/逆水寒) 与《阴阳师》**, 结尾「追求纪实摄影般的真实, 绝非游戏/CG/动画/插画渲染」。
- `负向:` 全改强化 —— + 不要 动画片 / 动画感 / CG 渲染感 / 游戏画面 / 3D 游戏场景 / 渲染感 / 星星 / 星光 / 闪光粒子 / 漂浮光点光斑 / 梦幻光效 / 过度光晕 / 镜头光晕泛滥 / 过曝 / 过饱和 / 偏色 (直击用户报的 动画片/星星/色彩 问题)。
- `光线:` 去粒子 —— 删 丁达尔光束过度 / 暖金 bokeh / 浮尘流光 / 飞花微瓣 / 暖金镜面倒影; 改 真实自然窗光 + 真实窗格光斑 + 自然柔和反光 (非镜面发光) + 极淡自然浮尘 (写实非闪光/星点); 宫灯烛火仅微弱暖光点缀。
- `主体/质感:` 去 薄雾氤氲/暖金光尘/飞花/bokeh 尾巴, 改 自然采光通透 + 照片级材质质感; 立绘「唯美元素」bullet 改「真实氛围」bullet (严禁星点/飞花/漂浮光斑/金箔流光/暖金 bokeh/梦幻光晕); 主色去 宝石色调/暖金 改 自然真实色彩不过饱和。视频 `场景/配色/空间/光线色调/dwell#5` 同步去粒子; 几何相机路径/dwell/≤15s **不变**。
- `.claude/agent_refs/project/ai_video.md` — 唯美方向补「⚠️重要失败模式」(放宽反CG+游戏锚/阴阳师+粒子光效 三者联合致卡通化/星点/过饱和, 即便参考 video 写实) + 「无比真实/照片级写实配方」(真人实拍参考锚 + 强反CG/动画/星光负向 + 真实自然窗光去粒子; 雍容华贵内容保留, 只换渲染层); 标注 nvdi 现采「照片级写实 + 唐宋雍容华贵内容」。

验证: 6/6 plate 方位词仍在主体行开头 (不破 015 路由); 全 scene 生成 prompt 已无 阴阳师/剑网3/逆水寒/绚丽唯美古风/暖金 bokeh/飞花/浮尘流光/宝石色调 等卡通诱因 (仅作负向禁用句保留); 6/6 plate 风格含「真人实拍写实/照片级真实」锚。

No conflicts found in: final_specs/spec.md + validation/* (未锁渲染风格); chapter/shotlist/角色 bibles; 导入路由 (folder 名/方位段未变); 唐宋陈设/建筑/书画内容层 (本轮只改渲染风格, 内容保留)。

---

## Follow-up 020 — 2026-06-02 12:25:11
Source: user_input/follow_ups/020-20260602-122511-jimeng-seedance-platform-rule-compliance.md
Summary: scene bg prompt 放进 Seedance/即梦 报「prompt 不符合平台规则」。research (WebSearch×2) 确认是内容审核拦截 (显性/隐性 IP + 画面文字 + 帝王政治词), 清理 8 个生成块。

Research 结论: 即梦/Seedance 硬性过滤 ①IP/版权 (影视剧名/画作名/景点名/游戏名/真人名 ——「显性+隐性 IP 双重规避」, 提及常见 IP 直接失败); ②文字相关 (引号待渲染文字 + 文字加冒号 敏感); ③敏感政治元素; ④真人素材参考已暂停 (人脸人声敏感个人信息)。

Auto-updated (8 prompt 生成块; 仅清触发词, 写实/唐宋/陈设内容全保留):
- **删所有 IP 名** (6 plate + 视频 + 立绘 `风格:`): 参考锚由点名《妖猫传》《长安十二时辰》《清平乐》《梦华录》《捣练图》《韩熙载夜宴图》故宫·山西 改为不点名通用「质感对标真实电影实景搭建的古装厅堂、真实唐宋古建筑实景照片与专业建筑/室内摄影」。
- **去画面文字**: bg2 主体/陈设、视频 空间/dwell#1 的「勤政」匾 → 鎏金匾额 (素面无字); 立绘 `负向` 去「奉天承运圣旨」改「明清穿越元素 + 不要在画面渲染任何文字」。
- **去帝王政治词** (生成块): 接旨跪礼区/接旨态 → 厅前礼仪空地 / 礼仪空地 / 纯空间背景; 无诏书道具 → 案面陈设简洁; 庄重朝堂氛围 → 庄重古典厅堂氛围; 北墙远山水墨水画 → 水墨立轴。
- `.claude/agent_refs/project/ai_video.md` — 新增「平台内容审核合规 (即梦/Seedance/Dreamina)」规则: 禁 IP 名/画面引号文字/敏感政治词, 真人一致性靠文字+自有参考图; 生成块「只描述画面、不点名、不含待渲染文字、不涉政治」。

保留 (不喂平台, 属剧情设定): scene **metadata** 的 诏书/接旨态/勤政/朝堂 站位与状态记载 (lines 5/12/14/22-33/46/81-86) —— 这些是 plot 文档, 不进 ```text``` 生成块, 故未改。

验证: 6/6 plate 方位词仍在主体行开头 (不破 015 路由); awk 抽取全部 ```text``` 生成块 (6 plate + 视频 + 立绘) grep 触发词 = 0 (无 IP 名 / 无 勤政奉天承运圣旨诏书接旨朝堂)。

No conflicts found in: final_specs/spec.md + validation/*; chapter/shotlist/角色 bibles; 导入路由 (folder 名/方位段未变); 渲染风格层 (019 的照片级写实保留)。
提示: 若仍报规则, 可further ① 把 `负向:` 段移到平台独立的"反向提示词"输入框; ② 缩短单条 prompt; ③ 即梦3.0 对 `标签:` 冒号格式敏感, 可改逗号顺写。

---

## Follow-up 021 — 2026-06-02 13:57:02
Source: user_input/follow_ups/021-20260602-135702-shots-inframe-chars-in-ref-and-explicit-names.md
Summary: (1) 镜头内入画人物 (含背影/前景下方) 须列入 `参考` (例 shot03 漏列); (2) 关系称谓「父子/父亲」→ 具体名「陈国公/陈凡」(每镜对 AI 独立)。全 ep01 28 shot 扫查修正。

Auto-updated:
- `episodes/ep01/shots/shot{01,02,03,05,07,10,12,14}/*.md` — 「父子 / 陈国公父子」→「陈国公和陈凡」, 凡 AI-fed 字段 (情节/走位/动作/Summary/Characters); 脚本跳过 `>` Chapter excerpt 引用块 (保留小说原文)。
- `shot20/shot21` 走位「父亲」→「陈国公」。
- **入画补参考**: `shot{03,05,07,10,12}` 参考补 `陈国公：place_holder, 陈凡：place_holder` (太监中景, 二人在镜头前景下方背影/未露正脸), Characters 补「/ 陈国公 / 陈凡 (前景背影、未露正脸)」, 走位由「南侧画外」改「南侧跪礼区、面向北 (镜头前景下方, 背影/未露正脸)」; `shot20` 参考补 `陈国公` + Characters 补 + 走位标陈国公「门内前景背影/侧面、未露正脸」。
- **不入画显式化**: `shot23` (陈国公在画外) / `shot25` (陈凡在画外) 走位补「(画外)」标注, 使其单人物参考有据。
- `.claude/agent_refs/project/ai_video.md` — 新增「AI-fed 字段用具体角色名、禁关系称谓 (per nvdi 021)」规则: 每镜对模型独立无跨镜记忆, 关系/相对称谓 (父子/父亲/儿子/二人) 在生成字段须改具体名; 走位关系称谓是 blocker; 例外为台词口语称呼与小说引用块。

核查: 全 28 shot —— AI-fed 字段「父子」残留 = 0 (仅 `>` 引用块保留); 走位「父亲/儿子」残留 = 0; 每个走位提到但不在参考的人物均显式标 画外/不入画/离去 (shot01/02/04/06/09/11/13/15/21/22/23/25/26); 每个入画人物 (含背影/前景/远景/半身) 均在参考。

No conflicts found in: 场景背景图系统 (参考用 `背景图 {plate_id}`, 未动) / 角色 bibles / chapter (小说原文未改, 仅 shot 内 AI-fed 字段) / 导入与 scene prompt (本轮仅 shot 文本字段)。
范围说明: 本轮限 nvdi ep01 shots; 规则已入 ai_video.md 通用层, feng_shou_lu / mozun_chongsheng 等项目若有同类关系称谓, 待各自触发时按新规则修 (本轮未扫其他项目)。

---

## Follow-up 022 — 2026-06-02 14:03:48
Source: user_input/follow_ups/022-20260602-140348-shots-suppress-crowd-hallucination.md
Summary: shot5 生成视频被 Kling 加了一众大臣 (本不应入镜)。根因为帝王圣旨措辞致「接旨=满堂群臣」语义致幻; 全 28 shot 加定员 + 负向禁群众。

根因诊断: 非 prompt 写错, 是语义联想 —— `情节`/`台词`「今解除朕与其之婚约。钦此」(`朕`+`钦此`=帝王圣旨) + `走位`「跪礼区」+ 太监宣旨 → 模型训练数据里「太监宣旨/接旨」≈ 一堂跪伏群臣, 遂把空厅填满群众; `情节` 虽写「空旷正厅」但无显式定员、`负向` 无禁群众 → 按惯例补人。属 ep01 接旨戏通病。

Auto-updated (全 ep01 28 shot):
- 每个 `走位:` 末尾加正向定员: 「厅内系国公府私宅正厅 (非朝堂金殿), 仅本镜入画人物, 别无他人 —— 无群臣 / 无侍从 / 无围观人群, 不得凭空增添群众。」(点明私宅非朝堂 + 定员, 反制 court-crowd 联想)。
- 每个 `负向:` 加 `不要 群臣 / 大臣 / 百官 / 群众 / 围观人群 / 跪伏群臣 / 侍从随从 / 多余人物 / 凭空增添人物`。
- 帝王措辞 (`朕`/`钦此`) 为剧情台词必需, **不删**; 靠定员 + 负向反制其人群联想。
- `.claude/agent_refs/project/ai_video.md` — 新增「隐含人群的场景须定员 + 负向禁群众 (per nvdi 022)」规则: 宣旨/接旨/朝会/升堂/婚宴/法事/战阵 等隐含一堂人的场景, 视频/图像模型会凭空补群众; 须 走位正向定员 (仅本镜人物/别无他人 + 点明场所非朝堂) + 负向禁群众。

核查: 28/28 shot 走位含「别无他人」定员句; 28/28 负向含「不要 群臣」。

No conflicts found in: 角色 bibles / chapter (台词帝王措辞未删, 仅加约束) / 场景背景图与 scene prompt (本轮仅 shot 文本) / 上轮 021 的参考与具体名修正 (本轮为追加, 未回退)。
范围: 本轮限 nvdi ep01; 规则入 ai_video.md 通用层, 其他项目同类「隐含人群」场景待触发时按新规修。

---

## Follow-up 023 — 2026-06-02 14:50:30
Source: user_input/follow_ups/023-20260602-145030-shots-placeholder-tokenize-no-pronoun-no-english.md
Summary: 全 28 shot 的 ```text``` 生成块 —— 所有人物 (名/代词/称谓/台词内人名) → `{拼音}_place_holder`, 禁代词全换具体 placeholder, 除 placeholder 外无英文单词。Interactive 澄清: 深度=全部彻底(台词也换), 范围=ep01 全 28 shot。

Auto-updated (28 shot 的 ```text``` 块 + Shot context Summary/Characters):
- **人物 token 化**: 太监→`taijian_place_holder` / 陈国公→`chenguogong_place_holder` / 陈凡→`chenfan_place_holder` (脚本先挡地名 `陈国公府` 再换 `陈国公`, 避开 他人/其他/国公府); `参考:` 人物条目由 `{名}：place_holder` 收拢为 `{拼音}_place_holder`, 场景背景条目保留 `…bg{N}_…：place_holder`。
- **代词/称谓 → placeholder** (逐 shot 按语境定指): 他/他们/其(其正北方/其侧脸/其周身…)/二人/老臣(指代)/老国公/老人/为人父者/纨绔(叙事指代)/三公子(叙事指代)/这位/老奴/父亲/令郎/儿子 → 对应人物 placeholder。
- **英文 → 中文** (生成块内): cinematic→电影感, photorealism→照片级写实感, 4K HDR→超高清高动态范围, OS/V.O.→画外音/旁白, fast-cut→快切, reverse-POV→反打视角, reveal/motif→反转/母题, face-differentiator→面部辨识特征, mm/cm/s→毫米/厘米/秒, anime/cartoon/illustration/manga/painterly stylization/over-airbrushed/bokeh/HDR/PNG/reaction/beat/cliff 等全译。
- `.claude/agent_refs/project/ai_video.md` — 新增「人物 placeholder 化 + 生成块无英文 (per nvdi 023, 可选·按项目)」规则 + 例外清单 + 地名保护提醒。

保留 (判断, 非指代): 形容/比喻称谓 (老臣沉稳/老练阴柔/废柴公子-simile)、成语 (判若两人)、指物 (二物/二者)、台词内正式称呼「陈国公府三公子」与圣旨措辞 (朕/钦此/奉天承运 —— 用户「台词也换」按其预览仅指人名 token, 称呼措辞保留)、画外权威 (朕/女帝, 无参考图不 token)、场景 plate 代码 (bg1_…)、地名 (陈国公府)、Shot context/frontmatter/标题/Reference uploads 等模板脚手架 (不粘贴进模型, 非 prompt 本体)。

核查: 全 28 shot text 块 —— 裸代词/关系称谓 = 0 (descriptor/idiom/物指/安全词除外); 英文单词 = 0 (placeholder + bg plate 代码除外)。shot05 抽样: 参考=taijian/chenguogong/chenfan_place_holder + 背景; 情节/走位/台词/动作 全 token 化; 渲染样式=电影感·超高清高动态范围·照片级写实感; 时长=6秒; 负向全中文。

No conflicts found in: 角色 bibles (人物画像未改) / chapter (小说原文 `>` 引用块保留, 仅 shot 生成字段 token 化) / 场景与 scene prompt (未动) / 上轮 021/022 的参考补全/定员 (本轮在其上叠加 token 化, 定员句与负向禁群众保留)。
注 (范围): 本轮 token 化/去英文限 ```text``` 生成块 (粘贴进模型的本体)。Shot context 字段标签 (Summary/Characters/Scene/Duration/Reference uploads)、frontmatter、标题、`Reference uploads` 行 (s1_…mp4 / 15s walk-through / PNG) 等**模板脚手架英文未改** (不粘贴进模型); 如需一并清理可另开 follow-up。

---

## Follow-up 024 — 2026-06-02 15:02:14
Source: user_input/follow_ups/024-20260602-150214-taici-exempt-from-placeholder.md
Summary: 修正 023 —— `台词:` 字段不适用 placeholder 化 (台词是显示给观众/被读出的字幕, placeholder 会被当字幕渲染出来), 改回自然人名 + 口语代词/称呼。其他字段 placeholder 化保持不变。

Auto-updated (全 28 shot, 仅 `台词:` 行):
- placeholder → 自然人名: `taijian_place_holder`→太监 / `chenguogong_place_holder`→陈国公 / `chenfan_place_holder`→陈凡 (说话人标签 + 台词内容 + 在画人物口型注 全部还原)。
- 恢复 023 曾 token 化的口语代词/称呼: shot05 `今解除朕与其之婚约`(其) / shot10 `因为令郎` / shot12 `就不用老奴说了吧` / shot13 `老臣明白。老陈……` / shot19 `凡……儿？` / shot20 `父亲，请罪的折子`。
- `.claude/agent_refs/project/ai_video.md` — 023 规则例外清单首条改为「`台词:` 整段不 placeholder 化: 自然人名 + 保留口语代词/称呼; token 化时跳过台词行」。

核查: 28/28 shot 台词行 place_holder = 0; 其他字段 (情节/走位/角色/动作/参考/Summary/Characters) placeholder 不变 (抽 shot05: 角色/情节/走位 共 10 token 仍在)。台词成品自然: 太监(宣):"今解除朕与其之婚约。钦此。" / 陈国公:"凡……儿？你这是……" / 陈凡:"父亲，请罪的折子，不必递了。" 等。

No conflicts found in: 023 的其他字段 token 化 (本轮仅动台词行); 角色 bibles / chapter / 场景 prompt。

---

## Follow-up 025 — 2026-06-07 02:58:50
Source: user_input/follow_ups/025-20260607-025850-no-placeholder-in-any-dialogue.md
Summary: 确保所有 prompt 的台词里无 place_holder, placeholder 只在台词以外。024 只清了 `台词:` 字段; 本轮把同一句对白**嵌在 `情节:`/`动作:` 引号内**的残留 placeholder 也还原。判定: 引号内(对白)=自然人名/代词, 引号外(叙述/描述)=placeholder。

Auto-updated (全 28 shot, 仅引号内对白):
- 还原 `情节:`/`动作:` 引号内对白 placeholder → 自然 (匹配台词字段, 仅引号内, 保留引号外叙述 placeholder): shot03 `“…三公子陈凡，纨绔放荡…”` / shot05 `“今解除朕与其之婚约。钦此。”`(情节+动作) / shot07 `“陈凡，接旨吧”` / shot09 `“陈凡接旨”` / shot10 `“哼。陈国公，因为令郎，女帝很不开心”` / shot12 `“…就不用老奴说了吧”` / shot13 `“老臣明白。老陈……一定亲自进京请罪”` / shot19 `“凡……儿？你这是……”` / shot20 `“父亲，”`。
- `.claude/agent_refs/project/ai_video.md` — 024 例外首条扩展为「一切『对白』(含嵌在 情节/动作 引号内的) 不 placeholder 化; 引号内=自然人名/代词, 引号外=placeholder」。

核查 (全 28 shot): 对白引号内 (“…”/《…》/「…」/"…") place_holder = **0** (Python 提取引号 span 验证); `台词:` 字段 place_holder = **0**; 非台词描述层 placeholder 保留 (共 **621** 处)。

No conflicts found in: 角色 bibles / chapter (`>` 引用块未动) / 场景 prompt; 描述层 token 化 (本轮仅动引号内对白, 引号外 placeholder 不变)。

---

## Follow-up 026 — 2026-06-07 03:26:14
Source: user_input/follow_ups/026-20260607-032614-remove-all-negative-prompt-fields.md
Summary: 把 nvdi 所有 prompt 的 `负向` 字段去掉。

Auto-updated (nvdi 全部 prompt):
- `episodes/ep01/shots/shot{01..28}/*.md` — 移除各 ```text``` 块的 `负向:` 行 (28 个)。
- `scenes/s1_陈国公府正厅/bg{1..6}/*.md` — 移除 6 个朝向背景 plate 的 `负向:` 行。
- `scenes/s1_陈国公府正厅/s1_陈国公府正厅.md` — 移除 walk-through 视频 prompt 的 `负向:` 行 + 场景立绘 prompt 的 `[负向]` 段 (header+内容) + `## 负向` 文档段 (re-paste 参考, 孤立后一并删)。
- `.claude/agent_refs/project/ai_video.md` — 新增「`负向` 字段可按项目从生成块移除 (per nvdi 026)」: 反向约束可挪到平台「反向提示词」输入框; ref 各处「负向应含 X」规则仍定义抑制内容, 仅承载位置变。

核查: nvdi 全树 grep `负向`/`[负向]`/`## 负向` = 0; Python 验证所有 ```text``` 块闭合正常 (末行为 时长/构图/[参数] 等, 非空非残缺); shot05 末行=「时长: 6秒」, bg1 末行=「构图: …」。

范围说明: 本轮仅 nvdi。feng_shou_lu (46 文件含负向) / mozun_chongsheng (166 文件含负向) **未动** —— 待用户确认「所有」是否含其他两项目。

No conflicts found in: 主体/角色/走位/情节/动作/台词/光线/风格/构图 等其他字段 (仅删负向行); 角色 bibles / chapter / 导入路由。

---

## Follow-up 027 — 2026-06-07 05:16:04
Source: user_input/follow_ups/027-20260607-051604-monologue-mouth-still-express-via-face.md
Summary: 内心独白时角色嘴不动, 但要通过表情反应出内心所想。

Auto-updated:
- `episodes/ep01/shots/shot{06,15,17,27,28}/*.md` (5 个内心独白 shot) — `台词` 行的 `在画人物口型:` 注追加「**但内心所想须靠面部表情 / 眼神 / 神态演出来** —— 嘴不动, 内心情绪全凭表情反应 (眼神由倦转锐 / 微表情 / 唇线收紧或微扬 / 瞳孔变化 / 神色冷峻), 不靠开口、不对口型」。
- `.claude/agent_refs/project/ai_video.md` — 在画人物口型契约 (nvdi 007) 追加「内心独白镜『闭口但表情演内心』(nvdi 027)」: 嘴唇不动 ≠ 面无表情; 内心情绪须靠表情/眼神/神态外显, 口型注追加「靠表情演、不靠开口」, 动作给神态 beat。

核查: 5/5 内心独白 shot 含新增句; 其余 shot (出声对白镜/默剧镜) 未动。这 5 镜的 `动作:` 本就含神态变化 beat (如 shot06 眼神骤然一锐即敛 / shot28 冷峻锐光凝至极致), 与新口型注一致。

No conflicts found in: 出声对白 shot (口型正常动, 不适用) / 默剧 reaction shot (已是纯表情演出) / 026 删负向 (本轮只动口型注, 不涉负向)。

---

## Follow-up 028 — 2026-06-07 06:22:36
Source: user_input/follow_ups/028-20260607-062236-strip-subtitle-meta-and-name-inframe-chars.md
Summary: (A) 台词里「后期软字幕/思源宋体斜体」等字幕排版信息扰乱 Kling, 移除, 只留跟视频有关的; (B) prompt 写明本镜入镜人物 (正面/背影) 防 Kling 加多余人。

Auto-updated (全 28 shot):
- **A 台词去排版**: `台词` 行正则删除字幕排版/后期信息 (`— 后期软字幕, 思源宋体, 画面下 1/6 居中, 白色描边黑` / `| 三选一字幕契约取「后期软字幕」: 视频不烧字, 字幕窗 约X秒-Y秒, 思源宋体(斜体), 前缀 "画外音:", 白色描边黑` / `默剧处理无字幕`)。**保留**对白内容 (说话人 + 台词/独白) + `· 在画人物口型:` 口型指令 (跟视频有关)。25 shot 改动。
- **B 走位点名入镜人物**: 定员句由「仅本镜入画人物, 别无他人 —— 无群臣/侍从/围观, 不得凭空增添群众」改为**点名 + 正背面**「本镜入镜人物仅 {A}(正面)、{B}与{C}(前景下方背影、未露正脸); 别无他人, 不得增添任何其他人物 (无群臣/侍从/围观人群/路人)」, 每 shot 按其入镜人物 (源自 Characters 字段) 定制 (28 种 list)。28/28。
- `.claude/agent_refs/project/ai_video.md` — 台词/字幕契约补「`台词` 字段只留对白+口型、不含字幕排版 (per nvdi 028, 根因: 排版非画面内容会扰乱 Kling)」; 隐含人群定员规则 (022) ①「正向定员」强化为「正向定员且点名 + 正背面状态」。

核查: 台词排版词 (后期软字幕/思源宋体/三选一字幕契约/白色描边黑/字幕窗) 残留 = 0; 入镜人物 clause 28/28; CRLF = 0 (写文件用 newline="\n", 保持 LF, edit 按钮不回退)。台词口型注 (含 027 表情演内心) 完整保留。

No conflicts found in: 口型契约/027 表情演内心 (口型注保留, 仅删排版); 026 删负向 (定员句在走位非负向); 023/024/025 placeholder (台词仍自然人名, 走位入镜人物用 placeholder 符合描述层约定); LF 行尾 (FU122)。

---

## Follow-up 029 — 2026-06-07 06:53:03
Source: user_input/follow_ups/029-20260607-065303-backtick-sections-and-scene-token.md
Summary: (1) 每个 structured 字段值用反引号包裹 (帮 Kling 分段); (2) 参考场景背景改单 token (和人物参考一样), 参考+场景用同一 token。

Auto-updated (全 28 shot ```text``` 块):
- **反引号包裹**: 每个 `{label}: {value}` → `` {label}: `{value}` `` (参考/角色/情节/场景/镜头/走位/动作/台词 / 字幕/光线 / 色调/节奏/渲染样式/比例/时长)。28/28。
- **场景 token 化**: `陈国公府正厅·背景图 {plate}：place_holder` → `{plate}_place_holder` (单 token, 如 `bg2_朝南_厅门_place_holder`); `场景:` 字段场景名 `陈国公府正厅` → 同一 `{plate}_place_holder`。token 用 shot 的背景 plate 做名 (保留朝向)。OS 声音参考占位不动。28/28, 无 verbose `陈国公府正厅·背景图` 残留。
- `.claude/agent_refs/project/ai_video.md` — 加「场景背景参考=单 token (nvdi 029)」+「每个 structured 字段值反引号包裹 (nvdi 029)」两条。

核查: 反引号 28/28 (Python 验证); 场景 token 28/28; LF 保持 (newline="\n")。

## Follow-up 030 — 2026-06-07 06:53:03
Source: user_input/follow_ups/030-20260607-065303-dynamic-camera-in-jingtou.md
Summary: 所有 shot 的 `镜头` 加动态运镜 (如缓慢推近特写) 增强关键瞬间 (如「眼神骤然一锐即敛」) 的视觉冲击。

Auto-updated (全 28 shot `镜头` 字段):
- 多数 shot 由「锁机位/完全静止机位」改为按情绪 beat 的运镜: **关键眼神/反转瞬间→缓慢推近至面部/桃花眼特写** (shot06 眼神骤然一锐即敛/反转揭示一、shot15 冷金锐光凝定/转折点、shot20 转身正脸冷峻、shot28 锐光凝至极致/集尾钩); **reaction→缓推捕捉微表情** (04/11/22/25); **太监阴笑/威胁→压迫式推近** (10/12); **宣旨/建场→随语势缓推** (01/02/03/05/07); **已有运镜保留增强** (08/13/14/16/18/21/24/27)。保留景别+9:16, 运镜缓/控速/稳/不抖。
- `.claude/agent_refs/project/ai_video.md` — 加「`镜头:` 用动态运镜增强关键瞬间 (nvdi 030)」: 关键情绪/反转/眼神瞬间用缓慢推近至面部/眼睛特写, 运镜缓控速稳。

核查: 28/28 含运镜; 0 残留「完全静止机位」; 反引号包裹与场景 token (029) 不变; LF 保持。

No conflicts found in: 029 反引号/场景 token (本轮只改镜头值内容, 仍在反引号内); 走位定员/口型注/台词 (未动); LF (FU122)。

---

## Follow-up 031 — 2026-06-07 07:07:10
Source: user_input/follow_ups/031-20260607-070710-distinguish-background-backs.md
Summary: shot07 两道背影 (应陈国公+陈凡) 都被 Kling 渲染成陈凡。根因: 角色行只描述太监、两道背影无外貌、台词聚焦陈凡。修: 给背影补外貌 + 显式区分双背影。

根因: shot03/05/07/10/12 (太监中景+父子双背影) 的 `角色:` 只描述太监, 陈国公/陈凡两道前景背影无任何外貌; 背影靠衣色/发型区分, 无文字线索 Kling 不能分辨, 加台词/情节聚焦陈凡 → 两道背影都成陈凡。上传参考为正脸, 对背影帮助有限, 文字区分是关键。

Auto-updated:
- `shot{03,05,07,10,12}/*.md` — `角色:` 行补两道背影的**背影可见外貌**: chenguogong (深紫一品国公朝服/玉带/紫金冠/银白长须/年长沉稳) + chenfan (玉白世家锦袍/黑色长发披肩/半束白玉冠/年轻挺拔); `走位:` 入镜人物句改为逐一点明每道背影衣色/发型 + 加「两道背影衣色与发型迥异、须各按其参考分别渲染, 严禁两道背影雷同或都渲染成 chenfan」。
- `shot20/shot20.md` — `角色:` 补陈国公 (前景背影/侧面) 背影外貌 (此前 角色 仅陈凡)。
- shot08 不动 (角色已含陈国公描述, 且陈凡正面、混淆风险低)。
- `.claude/agent_refs/project/ai_video.md` — 背影 rule (008) 补 nvdi 031: 背影/非焦点人物 `角色:` 仍须给「背影可见」外貌 (衣色/发型/冠/体态), ≥2 背影须逐一点名+区分特征+「严禁雷同/都渲染成同一人」(根因: 缺背影外貌+台词聚焦致模型把所有背影渲染成焦点人物)。

核查: 5/5 角色补陈国公背影; 5 入镜人物含反雷同句; shot20 补陈国公; CRLF=0 (LF 保持); 反引号包裹(029)/场景token 不变。

No conflicts found in: 029 反引号 (角色值仍在反引号内, 在闭合 ` 前追加); 台词/口型/镜头/走位定员 (定员句增强未删); 角色 bibles (外貌取自既有 bible, 一致)。

---

## Follow-up 032 — 2026-06-08 11:37:11
Source: user_input/follow_ups/032-20260608-113711-shot07-element-at-mention-trial.md
Summary: 试验 Kling 3.0 Omni 的 Element + `@元素名` 硬绑定方案(根治 shot07 双背影都成陈凡)。仅 shot07 改, 作 A/B 验证, 有效后再决定全量迁移。

Research 结论: Kling 3.0 Omni 有 Element 库 + `@元素名`(硬绑定, 强于自由文本 placeholder 软提示)+ 多视角元素(正/左¾/右¾/**背面**)。元素含背面图 → 解决"背影没脸、正脸参考用不上"的根因。FU031 的文字区分是软补救; @element + 背面图是硬解。

Auto-updated:
- `shot07/shot07.md` — prompt 内 token 改 @ 形式: @taijian / @chenguogong / @chenfan / @bg1 (`{拼音}_place_holder` → `@拼音`, 场景 → @bg1); Reference uploads 行改注「库内预建元素、每个 4 视角含背面过肩」。台词及对白内自然名(陈凡/太监)不动。

未改 (待验证后再定):
- 其余 27 shot 的 `_place_holder` token 不动 (shot07 有意偏离作 A/B; 非约定变更)。
- `.claude/agent_refs/project/ai_video.md` 不改 (「元素优先 + 4视角含背面 + @硬绑定」规则待 shot07 验证有效后再入)。

前提: 用户账号须 Kling 3.0 Omni (支持 @); 旧版无 @名。

核查: shot07 残留 _place_holder=0; @ 元素到位; 台词自然名完好; CRLF=0 (LF); 反引号包裹不变。

No conflicts found in: 台词不 token 化 (FU024/025, @ 只进叙述/走位/角色); 反引号 (FU029); 镜头运镜 (FU030); FU031 背影文字区分 (保留, 与 @ 互补——元素失效时仍有文字兜底)。

---

## Follow-up 033 — 2026-06-08 11:47:29
Source: user_input/follow_ups/033-20260608-114729-revert-shot07-to-placeholder.md
Summary: 撤销 FU032 的 shot07 @element 试验, 改回 `_place_holder`; 28 shot 重新统一。并修正 FU032 的错误诊断。

修正诊断: FU032 误判根因为「用户用旧的多图参考/软绑定」。用户澄清本就在 Kling 3.0 Omni 用 placeholder=@element 硬绑定且大部分 work。正确根因: @element 绑身份、身份靠脸落实; shot07 同时抽掉脸(双背影)+ 分区模糊(两人贴一起同姿势)+ 注意力失衡(@chenfan 被强调) → 绑定无判别信号可依据。最可能具体原因: 元素用正脸图建、缺互不相同的背面图 (吻合"大部分 work、只背影镜翻车")。问题不在 token 格式 (placeholder vs @), 真正修复在给元素补互不相同的背面图 + 拉开双背影 + 均衡注意力; FU031 文字区分是有效兜底。

Auto-updated:
- `shot07/shot07.md` — `@拼音` 全部还原为 `{拼音}_place_holder` (@taijian/@chenguogong/@chenfan/@bg1 → *_place_holder); Reference uploads 行还原原文。残留 @=0, token 计数与 FU032 改动前一致, 台词自然名完好, LF 保持, 反引号包裹不变。
- `032-*.md` — 顶部加一行「已被 FU033 撤销并修正诊断」指针, 原文保留作审计轨迹。

未改: 其余 27 shot (本就未动); `.claude/agent_refs/project/ai_video.md` (FU032 本就没改; token 格式不入规范)。

结论(沉淀方向, 待验证): 规范要写的不是 placeholder vs @, 而是「无脸出场(背影/远景)的人物, 其 Kling 元素必须含背面视角图; 同框多个无脸主体的元素背面须互不相同」+ 配 FU031 文字区分。用户用含背面图的元素验证有效后再入 ai_video.md。

核查: shot07 残留 @=0; *_place_holder 还原 (taijian11/chenguogong7/chenfan10/bg1 2); CRLF=0; 与 27 shot 约定重新一致。

---

## Follow-up 034 — 2026-06-09 20:30:16
Source: user_input/follow_ups/034-20260609-203016-dialogue-tts-section-and-av-mux-tool.md
Summary: 高端 AI 情感 TTS 配音路线, 第一步——28 个 shotNN.md 各加独立「台词配音 prompt」section。仅项目级, 不改通用工作流契约。

Auto-updated:
- episodes/ep01/shots/shot01..28/shotNN.md — 末尾追加 `## 台词配音 prompt` 段 (有台词镜=可复制 ```text``` 配音块: 角色/锁定音色id/情绪/语速/类型/纯台词/时长目标; 默剧镜=「无台词」+SFX 注记)。全 28 镜, LF 保持 (CRLF=0), 既有内容未改, 幂等 (marker 去重)。
- user_input/revised_prompt.md — 顶部加 ### 034 条目。

待用户推进 (本轮未做, 按「一步一步来」暂停):
- 第二步 (用户侧): 用台词配音 prompt 逐镜生成台词 MP3 + 自备 BGM MP3。
- 第三步 (待批准后做): 新增 tools/mux_av.py 合成 video MP4 + 台词 MP3 + BGM MP3。

tradeoff (记录): 新 section 不在 rule 12.4 通用模板内 → 若经 webapp/stage-6 regen 重生成 shot 会丢失。项目级决定, 暂不升级通用 schema。

No conflicts found in: 视频 prompt 块 (解耦, 未动); 台词/字幕 既有行 (保留, 新段从其派生); 其余 spec 工件。

## Follow-up 035 — 2026-06-14 21:00:00
Source: user_input/follow_ups/035-20260614-210000-no-subtitle-detail-in-shot-prompt.md
Summary: shot prompt 台词字段去字幕化（common-level 规则，详见 ai_video.md §12.4 v2 + CLAUDE.md）。nvdi 本就无字幕排版，仅做 label 改名 + 去「/ 字幕」。

Auto-updated:
- ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/* (28 文件) — 台词字段 label `台词 / 字幕:`→`台词:`；内心独白 OS 行「为画外配音 / 字幕」→「为画外配音」
（common-level 规则文件 .claude/agent_refs/project/ai_video.md §12.4 v2 + CLAUDE.md 已由 wushen follow-up 022 同批更新）

校验：nvdi shot model-fed 字段零字幕 token；台词原文 + 在画人物口型契约 verbatim 未改。nvdi 既有 `画外音/朗声 + 口型` 标注表达正常/内心独白之分，未强改二元标签（gold-standard 保持）。
No conflicts found in: 角色档/world/arc/style_guide。
