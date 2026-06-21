# Changelog — wushen_juexing

## EP3 shot7 多声轨混乱修复（视频静音 + 全 mux）— 2026-06-21
Source: 用户「shot7 的语言生成出来彻底混乱了，而且系统没有用上传的 MP4 里的声音」
- **根因**：shot7 同镜有 系统×2（SYS-gold-01）+ 主角 OS（PR-hero-01）三条台词，靠 Seedance 单声轨从 `台词:` 文本 TTS → 多音色混在一起"彻底混乱"，且生不出上传的系统 MP4 锁定音色。
- **修复**：本镜全部不对口型（系统=UI、主角=内心独白），改为**视频静音 + 全后期 mux**：`台词: 无`、负面词加人声抑制组、三条台词正文留在 `## 台词配音 prompt`（系统两句 SYS-gold-01、主角句 PR-hero-01），后期 `tools/mux_av.py` 分轨合。系统对话框内字属 diegetic 画面元素、照常视觉渲染。shot07.md + all_shot_prompts.md + Shot context + 台词配音 头注 同步。
- **skill/ref 进化**：`ai_video.md` 新增「多声轨/系统音色镜→视频静音+全 mux」规则（明确 rule 704 单声轨 TTS 的边界）；`格式契约` 新增 **K22b** 机械校验（多 voice_id 或系统锁定音色镜须静音 mux；单声轨在画口型对话镜不适用）。
- **玉佩去上画（用户确认：全程不上画·保留剧情线）**：EP3 玉佩**全集不上画、画面从不出现玉佩本体**，剧情线靠体感+OS 保留。
  - shot6 由「掏出玉佩细看·上画特写」改为「隔衣按胸·收手垂眼·感知第二宝之疑·不掏出」（去 `玉佩=>` ref + 删玉佩外观描述符 + 镜头改面部特写 + 小说原文改隔衣感知版 + 负面词改"画面出现玉佩/掏出玉佩/玉佩外露"）。为避免与 shot5 按胸视觉重复，shot6 设计为「手自胸口收回→垂眼内省」的疑窦 beat（惊→疑分层）。
  - shot7 回退我上一轮加的"收玉佩入衣襟"beat（既然 shot6 不再掏出，无物可收）。
  - shot5 维持不上画（原就藏衣内骤热）；改掉"取出留 shot6"等指向掏出的旁注。shot2/shotlist/汇编头部玉佩轴统一为"全集不上画、无玉佩 ref、视觉揭示推迟到后续某集"。
  - 第二宝 hook 现靠 shot5 骤热 + shot6 隔衣感知生疑 的体感与内心独白种下。

## EP3 出片前 审查总编排 整集收尾（shot01–shot10）— 2026-06-21
Source: 用户「好的」（同意整集跑审查总编排收尾）
- 按 格式契约→台词→白话→站位朝向→运镜→动作→时长节奏→光线→特效→剧情连贯→全剧序列→立意安全 逐层过 EP3 全 10 镜。
- **唯一 blocker（自查出·已修）**：shot9 的 `台词:` 槽被加了无人声旁注（上一轮 K22 误导）→ 违反 K21（台词槽 prose 会被烧成字幕，正是 shot9 当初的 bug）。已改回干净 `台词: 无`，无人声诉求全移到 `负面词:`（shot09.md + all_shot_prompts.md 同步）。
- **连带修规则**：K22 + ai_video.md rule 705 早先「`台词: 无` 后加注」与 K21 自相矛盾 → 改为「人声抑制只进 `负面词:`、`台词:` 仍只写 无」。
- 其余维度全 pass：暖金流光轴/玉佩轴单调一致、藏锋无外放、独角戏朝向(盘坐朝南·神像朝北)贯穿、景别有节奏、台词白话配速 ≤5 字/秒、零 hex/字幕铁律/锁定串 byte-identical 齐全、shot8→9→10 姿态承接(看手掌→起身→推门)。
- 审计：`.audit/adhoc_agents/2026-06-21/wushen_juexing-20260621-070706/events.jsonl`。

## EP3 shot9 去玉佩 + 静默镜无人声负面词（成片误念"裴知秋"）— 2026-06-21
Source: 用户「shot9 就不需要出现玉佩了，还有命名没有台词、生成的视频主句却念了"裴知秋"三个字」
- **shot9 去玉佩**：整镜移除玉佩（参考去 `玉佩=>`、删玉佩描述符/取出/收回 beat、删 jade 负面词、镜头收尾改"握拳+望门外"、小说原文去看玉佩句）。shot9 改为纯"收功起身·握拳·望庙门外深夜"的变强实感静默镜，承接 shot10 叠化天亮推门。**理由附带**：看玉佩"第二宝 hook"已在 shot6 种下，shot9 再看属重复 beat（N6/全剧序列），去掉同时消重。shot07.md + all_shot_prompts.md + shotlist.md 玉佩轴同步：本集玉佩**仅 shot6 上画一次**（shot6 掏出→shot7 收回衣内→shot8/9/10 藏衣内不上画）。
- **静默镜误念角色名修复**：shot9 本是 `台词: 无`，成片却念出"裴知秋"——生成器从 `角色:`/`情节:` 抓角色名 TTS 成画外音，`台词: 无` 单独挡不住。已给 shot9 `负面词:` 加人声抑制组（人声/配音/旁白/念白/念出角色名或台词文字/任何生成人声音轨/no voiceover/no speech/no narration）+ `台词: 无` 后加注。**只对静默镜加**——有台词镜禁加（rule 704：Seedance 从 `台词:` 文本生成配音，加了会压哑台词）。EP3 仅 shot9 是静默镜，无需扫其余镜。
- **skill/ref 进化**：`格式契约` 新增 **K22**（静默镜必带无人声负面词，且明确只对静默镜加）；`ai_video.md` rule 705 追加同条（带 EP3 shot9 实测来源 + 与 rule 704 的边界）。

## EP3 shot7 系统 ref 补漏 + 玉佩跨镜状态连贯（shot6→7→8→9）— 2026-06-21
Source: 用户「shot7 是不是应该由系统在参考里面，还有请确保和上一个 shot 的状态连贯性，好像上个 shot 手里是拿着玉佩的？各个人物物品的连贯性是你 always 应该检查的，每次更改都要」
- **系统 ref 补漏（K20）**：shot7 系统对话框上画，`参考:` 漏 `系统=>`。已补 `系统=>` 至 shot07.md + all_shot_prompts.md 的 `参考:`，并把系统 UI 行改成 byte-identical 锁定描述符（`c2_系统` field 9：鎏金极简冷调半透明对话框 仅主角可见 冷白等线体 【】选项）。
- **系统 UI 配色对齐锁定卡**：shot7 多处把系统框写成「半透青蓝/冷蓝 UI」，与 `c2_系统` field 3「半透明墨黑底」冲突。已全部改为「半透明墨黑底」（shot07.md 小说原文/情节/动作/光线、all_shot_prompts.md 同名行、shotlist.md 运镜锚）。
- **玉佩跨镜状态轴修复（N6）**：shot6 末玉佩仍在手中细看，shot7 直接归拢丹田/破境、玉佩凭空消失（无收回 beat）。已给 shot7 开场加「先将掌中古玉顺红绳收回衣襟·藏入衣内贴胸（承 shot6）」beat（情节/走位/动作三处 + 聚合）。下游连带：shot9 原直接「摊掌看玉佩」缺取出 beat（shot7/8 已收衣内），补「探手入衣襟取出玉佩摊掌」beat。轴：shot6 掏出上画 → shot7 收回衣内 → shot8 衣内不上画 → shot9 取出上画·镜尾收回。
- shotlist.md「玉佩 prop」锚加 S7（收功前先收回衣襟·不上画）；「系统 UI」锚补 S7 带 `系统=>` ref。
- **skill 进化**：`格式契约` K20 从「道具 ref↔可见」扩成「**可锁定 on-画 元素（道具＋非实体 UI/法宝等）**ref↔可见双向一致」，明确系统 UI 也是 ref-bearing、上画镜必带 `系统=>`+锁定描述符（带本次教训来源）。
- 连贯性已查：shot8 无玉佩字样（衣内·一致）；shot6↔7↔8↔9 玉佩态单调顺承、每次状态改变都有动作 beat。


## EP2 shot11 收玉佩动作太假修复（玉佩一碰胸口就进去）— 2026-06-20
Source: 用户「2-11 收起玉佩时候的动作明显太假，玉佩一碰胸口就进去了」
- **根因**：动作只写「顺着衣领塞回衣襟内贴胸」太笼统，模型渲成玉佩一触胸口即没入（穿胸/瞬移感）。
- **修复**：把收玉佩改成分步物理动作并配时间轴（1–4.5s）：指尖拈起玉佩连红绳 → 另一手撩开交领右衽领口开口 → 手连玉佩探进领口、手背带衣襟撑开、玉佩滑入内层贴胸 → 抽手 → 抚平领襟合拢复位 → 隔衣按实两下确认。`掀襟→入襟→整襟→按实` 一整套，三处（情节/走位/动作）同步。
- 负面词加：玉佩一碰胸口就消失 / 玉佩穿胸 / 玉佩穿透衣服没入 / 不撩衣襟直接进胸 / 玉佩瞬移进衣襟 / 收玉佩动作过快穿帮（保 K15 基线项）。
- 连贯性：承接 shot10 结尾「手扣玉佩按胸」一致；本镜为 EP2 末镜、玉佩最终仍收进衣襟、对 EP3 开场无影响。字数 1548 < 2000。
## 加了出场卡的 shot prompt 控字数 ≤2000（牺牲负面 section） — 2026-06-20
Source: 用户「请确保有了人物卡的新 prompt 也在2000字以内，不行可以牺牲一点负面 section 的内容」
- 量了三个首登 shot（K10：视频 prompt body 不计 `情节:` 块）：shot01=1231、shot02=1734 均 OK；**shot03=2148 超 148**（裴昭+沈婉两张卡、出场卡字段最长）。
- shot03 修剪（保 K15 基线负面项）：① 负面词去掉 11 个冗余字幕同义词（字幕/中文字幕/对白字幕/对白文字/台词文字/字幕条/弹幕/caption/text overlay/subtitles 等），保留 `画面文字 / 台词字幕` 即覆盖；② 渲染样式的超长「全程绝对无字幕…」前缀缩成「不自烧台词字幕（台词后期叠）；出场卡见上为角标可显示」——顺带解掉「绝对无文字」与「出场卡要显示」的内部冲突；③ 出场卡字段去冗余措辞。→ **shot03=1977 OK**。
- EP1 全 12 shot 复量：全部 < 2000。

## EP3 台词自然化+饱满化（S10 去突兀 + S1/S2/S3 放开写顺）— 2026-06-20
Source: 用户反馈（① S10「先去镇上那场考核」突兀——"那场考核"观众不知何来，改"听人说…"自然引入；② 整体表达仍有不自然处、文字偏少，正常可接受约 2x 字数）
- **S10**：「天亮了。先去镇上那场考核，找个宗门落脚，安心练功。」→「天总算亮了，雨也停了。对了——听人说镇上有家宗门要开考核、招新人。我去试试，落个脚，安心练功。」（用"听人说"把考核作为听来的信息自然引入、不再凭空假设；情节字段同步改为"听人说…")
- **S1**：「走了大半夜，雨越下越大。前面这座破庙，先躲一躲。」→「走了大半夜，这雨不光没停，反倒越下越大。前头正好有座破庙，先进去躲躲、避一避吧。」（更饱满口语）
- **S2**：「这副病躯底子太差，光赶路撑不久。趁四下没人，把这具武神躯，好好运转一遍。」→「这副身子底子太差，光赶路撑不了几天。趁四下没人，把这具武神躯运转一遍，探探深浅。」
- **S3**：「闭上眼，把心神沉进丹田……那股力，顺着我的意念，缓缓转了起来。」→「闭上眼，把心神慢慢沉进丹田……奇了，那股力竟真顺着我的意念，一点一点缓缓转了起来。」（加"奇了…竟真"的真实临场感）
- 节奏复核：S1=4.25 / S2=4.5 / S3=3.6 / S10=4.75 字/秒，均 ≤5（借时长头寸把原本偏空的台词写满写顺）。
- S4–S8 judged 已自然且 grounded（S4「这就是…武神躯」、S5/S6 玉佩疑、S7 入境、S8 修行速度），本轮保留未动。
- 同步：shot.md(台词 ·+配音) / dialogue.md / script.md / all_shot_prompts.md(台词+配音+S10情节)。
No conflicts: 武神躯/那股力指代体系、特效、场景、玉佩零光钩、情节链 均未受影响。

## EP3 shot8 台词改写 + 台词大师全集 review — 2026-06-20
Source: 用户反馈（① shot8 别再一个劲提武神躯、改说「照这个速度修行会比以前快很多」类；② 改完让台词大师 review 整 EP3、查台词+情节连贯，不连贯直接改或加 shot）
- **S8 改写**：「这就是武神躯……运转得又快又顺，一点没卡。换作从前这副废丹田，想都不敢想。」→「运转得又快又顺，一点没卡。照这个速度练下去，往后修行会比从前快太多了。」（去武神躯复读、爽点转为修行速度）
- **台词大师 review（D1–D9 + 全集情节链）**：发现上一轮「暖流→武神躯」后 S2/S3/S4/S5 连续四镜复读「武神躯」（犯 D8 口头禅）。修正：武神躯只在 S2(定意)+S4(体感实证payoff)点名；S3「武神躯给的这股力」→「那股力」、S5「跟武神躯的力应和」→「跟我体内那股力应和」。全集再无「暖流」、武神躯不复读、指代清楚。
- **情节链裁定**：S1避雨→S2定意→S3-S4运功→S5玉佩共鸣→S6掏玉佩疑→S7破境入武人一级→S8感叹→S9收功→S10出庙，顺、动机可信、爽点落地、相邻镜无重复无跳跃，玉佩 prop 状态(S5衣内→S6掏出→S9收回)承接一致——无须加 shot。
- 同步：shot.md(台词 ·+配音) / dialogue.md / script.md / all_shot_prompts.md(台词+配音)。
No conflicts: 特效/场景/玉佩零光钩/系统 UI 未受影响；台词节奏字数÷时长≤5 维持。

## EP3 破庙场景重构+细化 / 运功台词去「暖流」/ 武神躯特效释放口 — 2026-06-20
Source: 用户连续反馈（① 荒废神庙描述再细致些、画面要好；② bg1/bg2 应是两个 folder、要 follow 其他 scene 的「主 prompt 出全景→图生图出各 bg」结构与流程；③ shot2~6「暖流」一词突兀、改提「武神躯」；④ 武神躯运功特效再多一点点）

**① 破庙场景结构对齐 + 描述细化**（之前未 follow 既有 scene 规范，本次修正）
- `2_世界观人设/scenes/破庙/破庙.md` 重写为与集市长街/暮色荒道 **逐节 1:1** 的场景总档：场景定位 → 8 字段锁定描述符表(恰 8 行) → 关键变化态 → 步骤一 Seedream 立绘**全局建场底图**(handle `破庙`·细化到泥塑剥落/褪色壁画/体积光柱/薄雾雨幕/前中后景深/4K 材质) → 背景图系统 index 表。删除原先多出的「8b 行」与「出场登记」段。
- 新建两个**独立 plate folder**（image→image sidecar）：`破庙/bg1_庙内_神像前/bg1_庙内_神像前.md`、`破庙/bg2_庙门/bg2_庙门.md`，各「上传步骤一全局底图作 reference + 本机位 prompt → 图生图」，首行＝plate handle。流程＝主 prompt 出全景 → 据此图生图出 bg1/bg2，与其它 scene 一致。（.png 由用户跑 prompt 生成。）
- ep03 全 10 镜 `场景:` 行刷为细化后 byte-identical 锁定串（S1–S8 bg1 夜雨态 / S9 bg1 雨歇态 / S10 bg2 庙门态），修掉原先 shot01 完整、其余简写的不一致；all_shot_prompts.md 同步。

**② 运功台词去「暖流」改提「武神躯」**（shot2/3/4/5 + S8 同词）
- S2「把体内那股暖流好好运转运转」→「把这具武神躯好好运转一遍」；S3「丹田里那股暖流…」→「武神躯给的这股力…」；S4「暖流走一圈」→「这股力走一圈」；S5「跟体内的暖流应和」→「跟武神躯的力应和」；S8「暖流走得又快又顺」→「运转得又快又顺」。
- 五处同步：shot.md(台词 ·行+台词配音) / dialogue.md / script.md / all_shot_prompts.md(台词+配音)。(情节/visual 描述按需保留「气血/力」表述。)

**③ 武神躯运功特效——藏锋释放口（EP3 divergence·用户授权）**
- 经多选确认：路线＝**体内气血暖金内透为主 + 仅 S7 破境一记克制外放**；色彩＝**气血暖色(暖金/赤金/暖橙)**、与冷青庙堂冷暖对冲、表气血淬体、非字面血、非金光滥放。调用 `ai_videos__特效设计` 按 X1–X8 落地。
- 落地（shot.md 动作/光线·色调/负面词 + all_shot_prompts 同步）：S3/S4 皮下沿经脉淡暖金赤金内透(贴肤·略可见·不外溢) + 物理副产(浮尘/碎发无风轻扬)；S5 胸口皮下随玉佩共鸣淡暖金明灭(玉佩本体仍只热不亮零光透温·保留第二宝钩)；S7 破境一刹丹田一点暖金光华 + 一记短促暖金赤金气劲升腾(衣袂鼓/发扬/浮尘碎瓦轻掀/积水涟漪·蓄-发-收一记不滥)，随后系统框浮现「已入武人一级」；S8/S9 承接「气劲已收尽/暖流平复归丹田、回归藏锋内敛」。
- **divergence 说明**：EP3 是藏锋弧内**首个受控释放期**（运功觉醒破境），对原「EP3 全程无外放」契约开运功段释放口；边界守住——仍无瞳光、无满屏金光、不过曝、气劲短促即收、玉佩零光，符合 ai_video.md 特效设计 X6「释放期按等级·克制升级」。shotlist.md / all_shot_prompts.md 藏锋贯穿注已改写。
- 平台合规(X7)：暖金内透/克制气劲为电影级真实质感，非过曝闪烁/血腥，过审无虞。

No conflicts: 玉佩第二宝钩(零光透温)未破；系统 UI motif 未改；shot06(已是「这股力量」)与 shot10 未受影响；台词节奏(字数÷时长≤5)维持。

## 修：导入的人物卡被 rename pass 改名、烧录找不到 — 2026-06-20
Source: 用户「点人物卡 button，卡照片不在指定地方；导入地点和卡不匹配；重下了卡到 downloads、帮我 fix 并重新导入」
- **根因**：导入把卡放到 `characters/c1_裴知秋/intro_card.png` 后，**MediaRenamer 的 rename pass 把角色文件夹里所有图统一改成 `{文件夹名}{N}.png`**——`intro_card.png` 被改成 `c1_裴知秋2.png`，烧录按 `intro_card.png` 找不到。
- **修复**：MediaRenamer 加 `_RESERVED_STEMS={"intro_card"}`——`intro_card.*` 是固定 canonical 名、rename pass **跳过不改**（也不参与立绘编号）。
- **重新导入**：删掉被错误改名的 `c1_裴知秋2.png`，用修好的导入器把 downloads 里新下载的 `kling_…_裴知秋名牌卡_….png` 导入 → 落 `c1_裴知秋/intro_card.png`（kind=intro_card），rename pass 已不动它；立绘归位 `c1_裴知秋.png`。烧录 `_find_card_in_drama(裴知秋)` 已能找到。
- 新增 3 回归测试（intro_card 抗改名 / 道具路由 / 场景立绘留根不进 plate）；downloads-import 14 + intro-card 6 全过。

## 人物卡出片改走 model 渲染 + 烧录修黑底/裁切 — 2026-06-20
Source: 用户「卡是黑底黑框、一开始就在正中央；要透明、右上角、人物出现1秒后渐进淡入停留再淡出」+「我现在通过上传照片让 Seedance/Kling 生成、不再点 button，改 shot prompt 提醒模型怎么做」
- **烧录修复（fallback 路径）**：用户卡是黑底/宽幅 → overlay 出黑块。intro_card writer 加 **cropdetect 自动裁到名牌 bbox + colorkey 抠黑底→透明**；真机渲染验证：用户真卡（裴知秋烫金竖名+白纹螺框）已正确透明叠右上角、黑底消失。6 测试过。
- **改走 model 渲染（主路径·用户选择）**：首登镜 `## 视频 prompt` 块加 **`出场卡:` 字段**，指示 Seedance/Kling 把上传的人物卡参考图当叠加角标——「{角色}出现约1秒后、顶角(右上/左上)渐进淡入、半透明、停留~3s、再渐进淡出、不挡主体、不打断正剧、卡内文字即参考图原样不另生成」。shot01/02/03 已加。
- **契约**：`出场卡:` 为 rule 12.4「画面不烧台词字幕」的**例外**（deliberate 叠加角标 + 来自上传参考，同系统 UI 框；非台词字幕）。rule 11d 记两种出片方式(model 渲染主 / 后期烧录备)，style_guide §7 同步。
- 注：视频模型对「定时精准叠图」未必可靠；后期 overlay 烧录仍是 deterministic 备选（已修好）。

## 人物卡入角色文件夹 + 道具库 + 导入修复 + 首登镜引入卡作参考 — 2026-06-20
Source: 用户「intro card 放 character 下面（不用额外 folder）；帮我导入 download 里的主角 intro card / 新 scene 图 / 玉佩，导入不太 work 帮 fix；所有人物首次出场 shot 都要引入人物卡、放进参考、我会上传照片」
- **人物卡入角色文件夹**：弃 `2_世界观人设/intro_cards/`，卡图改放各角色 `characters/cN_{中文名}/intro_card.md`(出图 prompt)+`intro_card.png`(成品)。intro_card writer `_find_card_in_drama` 改为按 `卡图=角色名` 在 `characters/*{角色}*/intro_card.{ext}` 解析。intro_cards.md `卡图`列、shot01/02/03 `首登字卡:` 路径同步。
- **道具库**：`2_世界观人设/props/{道具名}/{名}.md+png`（与 characters/scenes 同层）。
- **导入（DownloadsImporter）修 3 处**：① 人物卡——角色匹配 + 文件名含「名牌/出场卡/intro card」marker → 落 `intro_card.{ext}`（只覆盖 intro_card.*、不动立绘）；出图 prompt 开头加「{角色} · 出场名牌卡」做路由 token。② 道具——`props/{名}/` 作候选 → 落 `props/{名}/{名}.{ext}`。③ **场景立绘误入 plate 子目录的 bug**——「破庙·场景立绘」文件名含「小神庙内部」，其中「庙内」误中 plate `bg1_庙内_神像前` 的方位 token、被塞进 plate 并清掉真 plate 图；加 `_SCENE_ROOT_MARKER`(场景立绘/全局/建场/底图…)→ 命中则留场景根、不进 plate。
- **本次实导入 3 图**：主角卡 → `characters/c1_裴知秋/intro_card.png`；破庙立绘 → `scenes/破庙/破庙_场景立绘.png`；玉佩 → `props/玉佩/玉佩.png`（与既有 玉佩.md 配对）。裴霆/裴昭/沈婉 卡待用户出图。
- **首登镜引入人物卡作参考**：shot01/02/03 的 `参考:` 末尾加 `{角色}出场卡=>` token、Reference uploads 列出 `characters/cN_X/intro_card.png`（用户生成 shot 时一并上传）。rule 11d 增标准条。
- 约定同步：rule 11d（卡入角色文件夹/道具库/导入路由/首登镜引入参考）、style_guide §7、stage6 playbook、UI 提示。intro-card 6 测试 + downloads-import 11 测试全过。

## 人物卡库挪到本剧 + 中文命名 — 2026-06-20
Source: 用户「文件请用中文；既然具体到某一部剧，应放在武神觉醒/2_世界观人设 下面」
- **弃全局库 `ai_videos/_intro_cards/`**，改为**每剧专属** `ai_videos/{name}/2_世界观人设/intro_cards/`（与 characters/scenes 同层）。
- **中文命名**（与角色档 `cN_{中文名}` 一致）：每角色一对 `{中文名}.md`（出图 prompt）+ `{中文名}.png`（成品）。EP1 建 `裴知秋/裴霆/裴昭/沈婉` 4 个 prompt + 库 README；删旧 pinyin 文件与全局库。
- **writer 解析改为按本剧**：`卡图` 列存原始引用；writer 从 shot 路径定位 drama root，裸中文名 → 在本剧 `intro_cards/` 下 glob `{名}.{png/webp/jpg}`；路径引用相对 drama root 或全 sandbox 路径。value object 不再硬编码库路径。
- intro_cards.md `卡图`列改裸中文名（裴知秋…）；shot01/02/03 `首登字卡:` 行卡图路径改 `2_世界观人设/intro_cards/{中文名}.png`。
- 约定同步：rule 11d（每剧库+中文命名）、style_guide §7、stage6 playbook §5、UI title + 缺图提示。6 测试更新全过（含中文路径真机合成）；tsc 干净。
No conflicts: 与 11c 字幕独立；renders/ 不覆盖契约不变。注：本类美术资产沿用角色档中文命名（与 ai_video.md rule 1 的 pinyin 路径惯例并存，characters/scenes 早已如此）

## 人物卡改「图片合成」（弃程序化画图）— 2026-06-20
Source: 用户「程序生成的效果总是不够好；在 props 下单开人物卡、我让 Kling 生成模板卡图、上传作为 reference、你生成 shot 时直接插进去」
- **架构调头**：放弃 ASS 程序化画框/烫金字/纹螺（迭代多版仍不够好），改为 **整张卡 PNG 图片合成**。
- **全局库 `ai_videos/_intro_cards/`**（像 _actors/_bgm/_voices）：每角色一张 Kling 做好的完整卡 PNG（透明底·含框+烫金名+身份）。建 `_intro_cards/README.md` 说明。
- **intro_card 聚合重写**：value object 改解析图片行式（`角色|首登shot|出现点|卡图|位置|时长|宽度占比`，卡图=库内裸名或完整路径）；writer 改 ffmpeg **overlay 合成**——卡图按宽度占比缩放、fade 淡入淡出、叠到镜头顶角（左/右）、多卡链式；探测视频宽+时长、`-loop 1 -t {dur}` 限定图片输入防挂死；输出 `shot{NN}.mp4`（renders/ 原片不动、二次烧录覆盖）。新增错误 `intro_card_image_missing`（404）。
- **EP1**：intro_cards.md 改图片格式，引用 `peizhiqiu/peiting/peizhao/shenwan.png`（**待用户用 Kling 生成放库**）；shot01/02/03 `首登字卡:` 行改「顶角叠人物卡图」。
- 约定同步：ai_video.md rule 11d（图片库+行式+overlay 烧录+美术建议）、style_guide §7、stage6 playbook §5、UI 按钮 title + 卡图缺失提示。
- 测试重写为图片合成（解析/缺图报错/合成时长不变/双卡）共 6 个全过；tsc 干净。
- **卡图 prompt 文件**：`_intro_cards/` 改扁平同名配对——`{id}.md`（出图 prompt，喂即梦/Seedream/Kling）+ `{id}.png`（你出的图）。建 EP1 4 个 prompt（peizhiqiu/peiting/peizhao/shenwan，竖排古风名牌·烫金名+白纹螺框+身份·透明底）+ 更新库 README。
- **shot prompt 改（融入卡图）**：shot01/02/03 ① `镜头:` 加「顶角留负空间（主体不顶到该角）」纯构图指令，让后期叠的卡图不挡主体；② `首登字卡:` 行写明「最终 shotNN.mp4 = render + 该卡图合成」并指向 `_intro_cards/*.png`。rule 11d 增「shot 侧构图留白」标准条。卡是后期 overlay、非视频模型渲染。
No conflicts: 与 11c 字幕烧录独立；renders/ 原片不覆盖契约不变；镜头改为构图留白 clause、不动剧情/台词/站位

## 字幕烧录全流程默认关闭（流程级规则）— 2026-06-20
Source: 用户反馈「shot4/shot5 不要字幕」→「加到流程里，所有的 shot prompt 都不要烧字幕」
- **common-level 规则**：字幕烧录全流程默认关闭。pipeline 不再生成 per-shot `subtitles.md`，默认不烧任何字幕；字幕由用户后期自行添加。webapp 烧字幕功能代码保留，仅手动 opt-in，不属默认产物、不参与格式契约校验、缺失不报错。
- 落点：`CLAUDE.md`（AI video rules bullet）、`agent_refs/project/ai_video.md` rule 11c + 布局描述、`ai_videos__全流程编排` stage6_prompt playbook §6 + BLUEPRINT.md。
- 本项目清理：删除 wushen_juexing 现存全部 21 个 `subtitles.md`（ep01 ×11、ep02 ×10）。各 shot.md prompt 本就「全程无字幕」，无需改动。整集合成默认走「原片」`ep{NN}.mp4`（无字幕版）。

## EP1 shot05 内心独白台词润色（去突兀 + 白话）— 2026-06-20
Source: 用户口头反馈（① shot05「够了——这命，我不认」太突兀，换表达；② 再把「这条任人踩踏的命」改白话）
- 旧：`够了——这命，我不认。丹田废了又怎样？离开裴家，外面天大地大，我照样能闯出条活路。`
- 新：`丹田废了，又能怎样？这条命被人踩来踩去，我偏不认。离开裴家，外面天大地大，我照样能闯出条活路。`
- 理由：旧开头「够了——」像喊口号且缺前因；改为从眼前处境(丹田废了)反问引出、再咬实「我偏不认」，贴小说原文"废了丹田又如何？这条任人踩踏的命，他偏不认"，并把书面词「任人踩踏」换成口语「被人踩来踩去」（白话大师·去书面词）。
- 五处同步：shot05.md（台词/语速注/台词配音·台词）、shots/shot05/subtitles.md（7 句双语时间轴按新断句重排，≈4.4 字/秒 ≤9s）、4_剧本 script.md(S5)、4_剧本 dialogue.md(五)、all_shot_prompts.md（顺带把此处残留旧尾句「闯出一片天地」统一为「闯出条活路」）。
- 审查（审查总编排·受影响范围）：格式契约 pass（无字幕信息/零 hex/voice_id=PR-hero-01 一致/4.4 字秒）；台词大师·白话大师 pass；相邻连贯 pass——新开头「丹田废了」承 shot04「丹田碎」、决意「离家闯活路」预呼应 shot06 系统选项②，衔接较旧版更顺。其余单镜维度(站位/运镜/动作/光线)未被本次台词改动触及。
No conflicts: 站位/运镜/动作/光线/时长 字段未改；shot04/shot06 未改。


## 人物出场定格字卡（全剧默认 · 后期叠层）— 2026-06-20
Source: user_input/follow_ups/015-20260620-072629-renwu-dingge-zika.md（用户「重要人物登场屏幕顿一下出美工字体文字简介；加进流程、全剧默认、只对重要角色、ep2 强盗老人不发」）
- ai_video.md 新增 **rule 11d 人物出场定格字卡**：重要角色首登＝定格亮相(~0.6–1s)+后期美工名牌字卡(主名+一句身份)；后期烧入、prompt 不写字卡文字(守 12.4/K4/K19)；门槛只对主角/核心反派/关键长线配角(龙套·路人·系统不发)；同角色全剧仅首登一次；每集 intro_cards.md + shot `## Shot context` 标 `首登字卡:`；格式契约校验
- style_guide.md 新增 **§7**：本剧全剧默认开启 + 美工调性(瘦金/书法冷白描金·lower-third 避字幕区·~1.5–2.5s 淡入淡出) + 重要角色发卡名单
- EP1 落地：新建 `episodes/ep01/intro_cards.md`（裴知秋/裴霆/裴昭/沈婉 4 卡·**文案初稿待用户审**）；shot01/02/03 `## Shot context` 加 `首登字卡:` 行（字卡文字未入 prompt ```text``` 块）
待审: 4 张卡的副身份文案（用户审定）
No conflicts: 与 11c 字幕烧录(独立后期路径)、12.4 prompt 不含画面文字契约 一致；系统 UI motif 不受影响

### 追加 2026-06-20：webapp「一键烧人物卡」+ 标准流程化
- ai_video_management webapp 新增 **`POST /api/burn-intro-cards`** + shot render 卡片「🪧 人物卡」按钮：按本集 intro_cards.md 在定格点 freeze-frame（"屏幕顿一下"）+ ASS 名牌字卡（主名描金大号/副身份冷白小号·lower-third 避字幕区·淡入淡出）→ 生成 **`shot{NN}.mp4`** 落 shot 根目录（**`renders/` 原片不覆盖**、输出名稳定二次烧录覆盖、先渲 tmp 再 move）。可多卡/镜（shot03 双卡）、含 audio 静默对齐。DDD 全分层(domain valueobject/error + infra writer + app dto/mapper/command + route + container + UI)，6 测试全过(含真 ffmpeg freeze 验证输出变长 + renders 原片未动)。同时硬化 subtitle/intro-card 的 shot 根定位(解析最近 shotNN 祖先)，保证烧录永不写进 renders/。
- **标准流程化**：stage6_prompt playbook §5 加「人物定格字卡」标准步骤 + §6 输出物，后续每集自动遵循（重要角色首登才出卡，龙套/路人/系统不出；同角色全剧仅首登一次）。EP2 无重要新角色首登（地痞/老人不算）→ 无 intro_cards.md，符合门槛。

### 追加 2026-06-20（设计调整·按用户反馈）：人物卡改「不停顿·顶角描金框」+ 出现时机/可读时长
- **不再 freeze**：取消"屏幕顿一下"，改为**视频流畅播放 + 顶角浮现框字卡**（淡入淡出叠在动态画面上）。burn 由 freeze+concat 大幅简化为**单遍 ass overlay + `-c:a copy`**（时长不变、音频原样）。
- **顶角 + 描金边框裱起**：位置 **右上/左上**（默认对齐角色画面侧）。intro_cards.md 列改 `位置(右上/左上)`。
- **配色修正（用户反馈「背景黄、黄字看不出」）**：BorderStyle=3 会用 OutlineColour 当框底色→整框变金、金字被吃掉。改为 **BorderStyle=1 文字（透明背景）+ 单独 \p1 矢量绘制边框**（框内透明）；框尺寸按字数估算 hug 文本。

### 追加 2026-06-20（再调·按用户反馈）：古风竖排 + 金黄立体名 + 白花纹框
- **字体立体**：主名 **金黄色 + 深铜描边 + 深铜投影**（\3c+\4c\shad）做 3D 立体感。
- **金黄而非橙黄**：name 色改饱和金黄。
- **边框白色 + 花纹（非直线）**：白色 **双线框 + 四角云钉（菱形）**，矢量 \p 绘制；框内透明。
- **文字竖排（从上而下）**：主名在右列、副身份在左列（古风右起），每字 \N 堆叠；**副身份精简为 4–7 字**（竖排过长会拉很高）——EP1 4 卡副身份改短（裴知秋「镇北王府废少」/裴霆「镇北王」/裴昭「镇北王幼子」/沈婉「镇北王妃」）。
- **真机验证**：在纹理视频上渲染确认（金黄立体竖排名 + 白花纹框 + 透明背景 + 顶角左右）。注：纯色平底测试源会出 h264 重影伪影，真实画面无此问题。
- value object `cards_to_ass` 重写为每卡 4 事件（白框 + 角钉 + 金名 + 白副）；5 测试更新全过；tsc 干净。intro_cards.md / rule 11d / style_guide §7 同步「竖排·金黄立体·白花纹框·副身份要短」。

### 追加 2026-06-20（再调·按用户反馈）：烫金效果 + 卷云纹螺花纹边框
- **烫金（非普通黄）**：主名改**金属金箔感**——金面 + 深铜描边 + 深铜投影浮雕 + **浅香槟高光（blur 半透）做金箔光泽**（双层：emboss base + sheen highlight）。
- **边框花纹纹螺（非直线）**：四角云钉（菱形）→ **四角卷云纹螺角花**——双线框 + 每角一个 bezier 绘制的螺旋卷草（同一基形按 x/y 镜像到四角，线描 traced）。
- value object 每卡事件 4→8（白框 + 4 角纹螺 + 金名 base + 金名 sheen + 白副）；真机渲染验证（烫金竖排名 + 四角纹螺白框 + 透明）。5 测试更新全过、tsc 干净。rule 11d / style_guide §7 / intro_cards.md 同步「烫金 + 卷云纹螺角花」。
- **出现时机 = 角色一出场即出卡**；**显示时长 ≥3.5s**；新增原则：重要角色首登镜首句台词/焦点窗口须 ≥ 卡时长，太短则加长（11d + style_guide §7 + 格式契约 warning）。
- **EP1 落地**：intro_cards.md 改 4 卡（出现点=入场、位置右上[裴知秋/裴霆/裴昭]·左上[沈婉]、时长 3.5–3.8s）；**shot03 沈婉首登 beat 加长**——焦点窗口 2s→5s(8.5–13.5)、台词加长「…这个家，护不住你了」(3-way 同步 shot03/dialogue/script，沈婉配音 4→5s)、shot03 12→15s；EP1 总时长 ~129→~132s（divergence note 同步更新）。shot01/02/03 `首登字卡:` 行改 overlay 措辞。
- 代码：intro_card valueobject 重写（cards_to_ass 框式顶角 ASS：每卡 2 事件=矢量描金框 + 金名白副文本）+ writer burn 改 overlay；5 测试全过（断言时长不变 + 透明框 \p1 + 金名白副 + 顶角左右 pos）。tsc 干净。

## 流程级契约变更 — 2026-06-18 选角供脸（user-cast face）
Source: 用户指令「我会人工选择角色，因为我有角色库，所以每个 character 面部的描述可以直接选角，但是发型、妆容、服饰其他所有细节都还是需要的」+ 澄清「之后每个 shot 都会上传人物图片，Seedance/Kling 仍靠文字匹配多人物，应保留简要描述帮助匹配正确」。
范围：流程级（改全流程契约，所有 ai_video 项目适用）。

共识机制（脸由选角图承载，文字不重建五官，只留「角色识别标签」做多人 shot 绑定消歧）落地于：
- `.claude/agent_refs/project/ai_video.md` — 新增「2026-06-18 amendment 选角供脸」+ 更新 12.8 锁定描述符表（删面貌、瞳色降级为铁律、新增妆容、一句话锁定→角色识别标签）。
- `.claude/skills/ai_videos__全流程编排/playbooks/ai_videos__stage2_世界观人设.md` — 访谈步/产物规格/卡片模板/turntable 全改选角供脸 + 妆容字段 + 发型贴合身份。
- `.claude/skills/ai_videos__全流程编排/playbooks/ai_videos__stage6_prompt.md` — shot 面部辨识特征 → 角色识别标签 + 参考图绑定。
- 审查 skill：`ai_videos__格式契约`（K3/K8/K8b）、`ai_videos__站位朝向`（C6）同步。

## Follow-up 001 — 2026-06-18 06:59:27
Source: user_input/follow_ups/001-20260618-065927-zhujue-heiseyizhuang-juese-zhigan.md
Summary: 各角色服饰按角色质感与地位重做，主角改黑色系武装质感、王爷服饰显尊严、各角色颜色彼此区别。

Auto-updated:
- 2_世界观人设/characters/c1_裴知秋/c1_裴知秋.md — 服装 月白旧布直裰 → 玄黑旧布劲装（武装质感、保留洗旧磨痕维持庶子对比）；配色主→玄黑；负向改对比项。
- 2_世界观人设/characters/c3_裴霆/c3_裴霆.md — 服装升级为玄青蟒纹王袍罩鎏金深银轻甲玄狐裘领玄金王爵肩章悬王印（显王爵尊严）；配色点缀→玄金/高光→鎏金。
- 2_世界观人设/characters/c4_裴昭/c4_裴昭.md — 朱红织金锦袍强化锦缎织金质感、对比对象改为主角玄黑旧布劲装。
- 2_世界观人设/characters/c5_沈婉/c5_沈婉.md — 藕荷云锦绣花宫装强化质感（柔软垂坠）；色调温柔与各角色区别。
- 5_6_分镜与prompt/episodes/ep01/shots/shot01–12 + all_shot_prompts.md — 凡主角衣着 月白旧布直裰→玄黑旧布劲装（沈婉月白披帛、shot04 月白冷光=月色 保留不动）。

## Follow-up 002 — 2026-06-18 06:59:27
Source: user_input/follow_ups/002-20260618-065927-faxing-fuhe-juese.md
Summary: 发型须贴合角色身份/职业（习武者与文人不同）。

Auto-updated:
- 各角色卡发型确认贴合身份（裴霆/裴昭 习武高束利落；裴知秋 半束略散显病弱文弱；沈婉 妇人发髻）——本项现状已满足，无需逐字改。
- 通用原则同步进 stage2 playbook 服化步（发型随身份/职业有可辨差异）。

## 选角供脸项目回填 — 2026-06-18
据上述流程级契约回填 wushen_juexing 现有产物：
- 角色卡 c1–c5：删文字五官（面貌行/标志特征点解剖清单）；瞳色降级为「绝不发光」铁律；新增「妆容」字段（c3 左眉骨旧战疤转伤妆、c5 右眉心花钿转妆饰）；一句话锁定 → 角色识别标签（byte-identical 新串）。
- c3 裴霆 / c4 裴昭 / c5 沈婉：补齐此前缺失的「turntable 角色 reference 块（吃选角脸）」——此前只有主角 c1 有该块（用户最初提问的根因）。c2 系统为非实体，沿用 UI 浮现块、无 turntable。
- ep01 12 个 shot + all_shot_prompts.md：角色行换新识别标签、删五官（含 Shot context Characters 摘要与动作字段内的五官名词）、每个角色行下新增「角色识别 / 参考图」绑定行（多人同框写死参考图↔画面位置↔标签防串脸）。

No conflicts found in: world.md, style_guide.md, scenes/*, arc_outline.md, 4_剧本/*（未涉及服饰/面貌锁定）。

## Follow-up 003 — 2026-06-18 07:30:33
Source: user_input/follow_ups/003-20260618-073033-xianxia-shenmei-fushi-jianhua.md
Summary: 服饰/发型/头饰整体改仙侠审美、去华丽夸张（修正 follow-up 001 把王爷/弟弟做得过于华丽）。

Auto-updated:
- c1_裴知秋：服装措辞去"武装质感/甲纹理"改清简布质（仙侠寒素）；负向加"不要甲胄/军装感"。**识别标签不变**（避免重扫全 shot）。
- c3_裴霆：玄青蟒纹王袍罩鎏金深银轻甲玄狐裘领玄金肩章 → 玄青暗纹广袖长袍外罩深氅 + 玄玉冠 + 玄铁素带 + 暗银鞘长刀；配色去玄金/鎏金；识别标签 → 「玄青暗纹广袖长袍外罩深氅 … 玄玉冠 … 沉峻王者」。
- c4_裴昭：朱红织金锦袍描金缠枝玉腰带+描金束发冠+描金折扇 → 朱红交领广袖锦衫+白玉佩素带+白玉冠+素骨折扇；识别标签 → 「朱红交领广袖锦衫白玉束发冠 握折扇 骄纵贵气少年」。
- c5_沈婉：藕荷云锦绣花宫装+珠钗 → 藕荷交领襦裙素雅暗花+素银步摇玉簪；识别标签 → 「藕荷交领襦裙月白披帛 … 温婉柔妇」。
- shot02/03/04/08/10 + all_shot_prompts.md：裴霆/裴昭/沈婉 角色行换新仙侠标签，参考图绑定行/Characters 摘要/造型散文里的 蟒纹/鎏金甲/玄狐裘领/织金/描金/绣花宫装 等华丽词同步改仙侠（裴知秋玄黑不变、沈婉月白披帛保留）。

Supersedes: follow-up 001 中「裴霆显王爷尊严=蟒纹王袍鎏金甲玄狐裘领」「裴昭织金描金」的华丽方向（改判定为过华丽、不合仙侠审美）。其余 001（主角黑色系、各角色区别色）保留。

## Follow-up 004 — 2026-06-18 07:45:00
Source: user_input/follow_ups/004-20260618-074500-scene-xianxia-gufeng-denglong.md
Summary: 场景走仙侠古风唯美、不那么写实；王府内部古风细腻、室内通透柔光、很多暖黄古雅宫灯。

Auto-updated:
- 2_世界观人设/scenes/zhenbei_wangfu_zhengting/（主场景档 + walk-through + 6 bg plate）：建筑补古风细腻(雕梁斗栱/镂空木格/藻井/帷幔)、满布暖黄古雅宫灯、默认光源改暖黄宫灯群通透柔光、配色/氛围去冷硬、一句话锁定改「…暖黄古雅宫灯林立 室内通透柔光」；保留尚武身份。
- shot 场景/光线 propagation：11 个正厅 shot 的 `场景:` 换新锁定串、`光线:` 基调由冷金日光改暖黄宫灯柔光(保留各镜情绪调制 + 藏锋无外放/眼不发光 + 系统UI微光)；shot04 旧院夜回忆月色保留。（与 005 合并为同一次 shot pass）

## Follow-up 005 — 2026-06-18 07:45:00
Source: user_input/follow_ups/005-20260618-074500-quban-fashi-qufen-se.md
Summary: 去裴霆脸上的疤；发簪重设计/隐藏；服饰花样+颜色区分度（主角黑→父亲不用黑）。

Auto-updated:
- c3_裴霆：删左眉骨旧战疤（妆容/turntable/识别标签全清）；主袍 玄青→**苍青**(云水暗纹，明确非黑、与主角区分)；发饰 玄玉冠→墨玉小簪(不戴繁冠)；识别标签换新。
- c4_裴昭：发饰 白玉冠→白玉小簪；衣料 折枝暗纹；识别标签换新。
- c5_沈婉：发饰 步摇+玉簪→仅一支素净羊脂玉簪；衣料 折枝花卉暗纹；识别标签换新。
- c1_裴知秋：素木簪半束保留（已是最素净 humble 款；识别标签不变，避免重扫全 shot）。
- 全员配色区分：知秋 玄黑(素无纹)/裴霆 苍青(云水纹)/裴昭 朱红(折枝纹)/沈婉 藕荷(花卉纹)。
- shot02/03/04/08/10 propagation：裴霆/裴昭/沈婉 角色行换新标签（苍青/无疤/新发饰）。（与 004 合并为同一次 shot pass）

## Follow-up 006 — 2026-06-18 07:55:00
Source: user_input/follow_ups/006-20260618-075500-zhujue-yudian-anwen-mawei.md
Summary: 主角衣料加细微雨点暗纹质地（别太朴素）；去发簪、长发改高束马尾。

Auto-updated:
- c1_裴知秋：服装 玄黑旧布劲装 → 玄黑雨点暗纹劲装（细密暗纹质地、保留洗旧磨痕）；发型 素木簪半束 → 高束马尾(素发带束、无簪)；识别标签换新；turntable 全块同步；负向加「不要发簪/不要披发不束」。
- ep01 全 12 shot + all_shot_prompts.md：裴知秋 角色行换新串、衣料雨点暗纹、头发高束马尾（含背影镜 shot11/12 束发与下摆；shot04 年少裴知秋同步衣料+马尾）；裴霆/裴昭/沈婉/系统/场景/光线不动。

## Follow-up 007 — 2026-06-18 08:05:00
Source: user_input/follow_ups/007-20260618-080500-tangsong-fengge-quhuadian.md
Summary: 沈婉去花钿；全员服饰唐宋形制；场景/建筑唐宋 + 室内字画/摆设/灯笼细节到位 + 仙侠气质。

Auto-updated:
- c5_沈婉：删右眉心花钿（妆容→温婉淡妆、眉心无红点，全文零残留）。
- 服饰唐宋形制（保留各自色/暗纹/发饰）：知秋 玄黑雨点暗纹**交领布袍**(唐宋寒士) / 裴霆 苍青云水暗纹**圆领襕袍**外罩大氅(唐制武将) / 裴昭 朱红折枝暗纹**交领广袖锦袍**(唐宋贵公子) / 沈婉 藕荷折枝暗纹**高腰襦裙**月白帔帛(唐制贵妇)。各卡 + turntable 同步，识别标签换新。
- scene zhenbei_wangfu_zhengting（主档+walk-through+6 plate）：建筑改唐宋木构斗拱/举折屋顶/直棂窗/梁架彩画；室内补字画(山水/书法挂轴)+摆设(古琴/铜香炉/博古架青瓷/盆景/屏风/帷幔)+唐宋宫灯样式(纱罩/莲花/羊角灯)细节；仙侠唯美不过度写实。**一句话锁定 #8 保持不变**→下游 shot 场景行无需改。
- ep01 全 12 shot + all_shot_prompts.md：四角色 角色行换唐宋新标签（形制 劲装→交领布袍 / 广袖长袍→圆领襕袍 / 广袖锦衫→交领广袖锦袍 / 襦裙→高腰襦裙、披帛→帔帛）；场景/光线/颜色/发饰不动。

Note: 项目无 raw_prompt.md/revised_prompt.md（未走 spec 流程初始化），follow-up + changelog 即审计轨迹；revised_prompt 重生 N/A。

## Follow-up 008 — 2026-06-18 08:20:00
Source: user_input/follow_ups/008-20260618-082000-wangfu-quhupi-tiliang-muse.md
Summary: 王府正厅去虎皮 + 整体色调提亮（暖木浅色明亮通透）。

Auto-updated:
- scene zhenbei_wangfu_zhengting（主档+walk-through+6 plate）：去虎皮（虎皮太师椅主位→楠木雕花高座素锦垫无兽皮；西墙虎皮/纛旗→山水书法挂轴+素色纛旗）；梁柱家具斗栱 朱漆/玄铁→暖木原木浅木、玄铁仅小面积点缀、青灰方砖→浅色方砖、室内明亮通透提亮；保留尚武身份+唐宋木构+字画摆设+唐宋宫灯+仙侠气质。
- 一句话锁定更新：`镇北王府正厅 — 石阶高台楠木高座主位 东墙兵器架 暖木雕梁斗栱浅色方砖 暖黄古雅宫灯林立 室内明亮通透`。
- ep01 11 个正厅 shot + all_shot_prompts.md：场景行换新串、光线提亮（暖木反光提亮、保留各镜情绪+藏锋/UI条款）、走位/小说原文"虎皮主位"→"楠木高座主位"；shot04 旧院夜回忆不动。全项目"虎皮"清零。

## Follow-up 009 — 2026-06-18 08:20:00
Source: user_input/follow_ups/009-20260618-082000-shenwan-huanzhuang-quhuadian.md
Summary: 沈婉服饰颜色+款式都换（去藕荷襦裙）；妆容"花钿"字样清掉（眉心素净）。

Auto-updated:
- c5_沈婉 + shot03：服饰 藕荷高腰襦裙月白帔帛 → **丁香淡紫对襟褙子 + 月白长裙**（宋制贵妇褙子、去帔帛、保留折枝花卉暗纹）；配色主→丁香淡紫；妆容去"花钿"字改"眉心素净无妆饰红点"；识别标签 → `沈婉 — 丁香淡紫折枝暗纹对襟褙子月白长裙 乌发挽髻素净玉簪 温婉柔妇`（c5#10 + turntable + shot03 三处一致）。
- 配色区分更新：知秋 玄黑 / 裴霆 苍青 / 裴昭 朱红 / 沈婉 **丁香淡紫**。

花钿确认：全项目无正面"花钿"提及（仅 follow-up/changelog 记录），沈婉眉心素净无红点。

## Follow-up 010 — 2026-06-18 08:30:00
Source: user_input/follow_ups/010-20260618-083000-shenwan-wangfu-furen-qidu.md
Summary: 沈婉穿着太小家碧玉、不像王府夫人 → 改出端庄雍容王府夫人气度（命妇大袖礼衣 + 霞帔，不堆金）。

Auto-updated:
- c5_沈婉 + shot03：对襟褙子+月白长裙 → **丁香淡紫折枝暗纹大袖衫(唐宋命妇大袖礼衣) + 月白长裙 + 霞帔(缀玉坠雅纹·诰命夫人品级)**；发 挽髻素净玉簪 → 乌发高绾贵妇髻+羊脂玉钗+珠花(端庄不繁)；配色点缀加霞帔雅纹+微暖金线；识别标签 → `沈婉 — 丁香淡紫折枝暗纹大袖衫月白长裙缀霞帔 乌发高绾贵妇髻玉钗 雍容王府夫人`（c5#10+turntable+shot03 三处一致）。
- 气度靠命妇形制规格+霞帔+好料，不堆金繁绣（守唐宋仙侠雅致）；颜色仍丁香淡紫；怯懦性格走表演不靠寒酸穿着。
- all_shot_prompts.md 重建同步。
- Supersedes follow-up 009 的"对襟褙子"款（改判定为太小家碧玉），009 的丁香淡紫配色与去花钿保留。

## Follow-up 011 — 2026-06-18 09:00:00
Source: user_input/follow_ups/011-20260618-090000-zhujue-shengxian-tai-chen-tai-an.md
Summary: 主角 PR-hero-01 配音「太沉太暗」→ 提亮音色、去压低，保留清冷隐忍少年基底，语速不变。

Auto-updated:
- 2_世界观人设/characters/c1_裴知秋/c1_裴知秋.md — 配音参考声线「清冷偏低、少年音偏沉」→「清冷清亮、少年音清润不压低」
- 5_6_分镜与prompt/episodes/ep01/all_shot_prompts.md — 9 处 PR-hero-01 音色锁定描述符同步为「清冷清亮少年音、不压低偏明净、偏慢留白多」
- 5_6_分镜与prompt/episodes/ep01/shots/{shot01,03,04,05,07,08,09,11,12}.md — 各 1 处 PR-hero-01 音色锁定描述符同步（byte-identical 内容）

No conflicts found in: casting.md(主角 voice_id 仍未指派, 不受影响), dialogue.md(无音色字段), 其它角色音色(PT-patriarch-01/PZ-brat-01/PW-consort-01/SYS-gold-01 未改), 语速/节奏/时长(未动)。

## 流程级契约变更应用 — 2026-06-18 23:19（turntable 声样 + 全局 2000 顶 + Seedance 审核安全化）
Source: 用户指令三条（均 common-level，规则本体已落 `ai_video.md` + `ai_videos__格式契约`，此处记其对 wushen 产物的应用）：①「turntable 念统一声样台词、所有角色同一句、喂 Seedance 前 3 秒声样」；②「给所有 prompt 设字数上限 2000」；③「场景生成失败、内容审核被拒」。

Auto-updated（wushen 产物）：
- **统一声样台词回填**：c1/c3/c4/c5 turntable 的「一二三计数」→ 统一句 `你好，今天天气还不错，外面很安静。`（姿态/音频/表 三处，跨角色 byte-identical；转身时点/造型/voice_id 不动）。c2_系统无 turntable，跳过。
- **全局 2000 字裁剪**：6 个 bg 朝向块裁到 1000–1202 字；主场景 walk-through 两块 2976/4517 → 1789/1998 字；4 个 turntable 块 → 1194–1329 字。12 个 ep01 shot 视频块实测本就 ≤2000（942–1539，未改）。
- **Seedance 审核安全化（主场景 walk-through 被拒修复）**：两块内武器特写/显式兵器/真实军事地标替换——`长枪/重剑/玄铁刀/兵器架` → `甲胄仪仗陈设架/玄铁器物`；视角 #5「玄铁刀錾纹刃口/重剑寒光长焦特写」→「玄铁立柱+甲胄仪仗陈设长焦」；`长城/烽燧/关隘` → `山川城垣`。

全局武器/地标传导清除（用户确认「现在就全部传导清掉」后执行）：
- **byte-identical 锁定串**「东墙兵器架」→「东墙甲胄仪仗」全局同步 13 处（scene 主档 #8 + bg3/5/6 + 9 个 shot 的 `场景:` 行 + all_shot_prompts.md），逐字一致。
- **bg3_朝东_东侧列柱**（武器为视觉核心）整块改：`甲胄仪仗陈设架成列(陈甲胄/仪仗器物)`、`錾纹刃口`→`器物纹饰`、`寒光`→`金属反光`，朝向/构图/光线逻辑不变。
- 替换表全 wushen 应用：`长枪/重剑/玄铁刀`→`甲胄/仪仗器物`、`玄铁兵器`→`玄铁器物`、`兵器`→`器物`、`兵戈`→`甲胄仪仗`、`长城/烽燧/关隘`→`城垣/烽台/关山`。
- 复验：全 wushen **零武器/地标残留**，所有场景/shot 视频块（扣情节行）**≤2000**，无替换叠词。

Seedance 字数次要风险（待观察）：实测 ~1500 字符比全局 2000 顶更低；walk-through 现 1789/1998 仍超 1500，本次失败是审核非字数，若改报 `InvalidNode` 需再压到 ~1400。

No conflicts found in: 剧情/台词/走位/朝向/timed beats（未动）, 锁定描述符识别标签 byte-identical（未动）, 色彩锁定零 hex（未动）。

## Follow-up 012 — 2026-06-18 09:30:00
Source: user_input/follow_ups/012-20260618-093000-scene-chouzhen-mp4-bukescheng-tu.md
Summary: scene 方位背景图导出按钮加回 + 截帧秒数对齐 scene prompt（表驱动）+ 修正「mp4 不能生成图片」流程误解 + bg6 虚化背景生成说明。

Auto-updated:
- 2_世界观人设/scenes/zhenbei_wangfu_zhengting/zhenbei_wangfu_zhengting.md — 生成流程改「video-first → 抽帧（主）+ image→image 精修」，删「image prompt + 上传 mp4 出图」；index 两条注释同改；bg6 从 13.5s 长焦段抽帧。
- （webapp，projects/ai_video_management）Reader 主工具栏加「🧭 截取方向背景图」按钮；ScenePlateExtractor 截帧秒数表驱动（读 scene md index 表，罗盘 map 兜底）+ bg6 纳入；+3 单测。
- （institutional memory）.claude/agent_refs/project/ai_video.md 场景生成流程铁律：mp4→图片 不支持，静帧靠抽帧 / image→image。

No conflicts found in: 步骤二 walk-through 时间轴（与 index 表截帧时点本就一致：北1.5/西4.5/俯瞰7.5/南10.5/东13.5）, 锁定描述符, 各 bg plate md, 其它 scenes（暂仅一个）。

## Follow-up 013 — 2026-06-19
Source: user_input/follow_ups/013-20260619-000000-scene-walkthrough-dwell-duiqi-chouzhen.md
Summary: scene walk-through 悬停窗口未覆盖固定截帧时点（北1.5/中景10.5/东13.5 落在运动段）→ 重排 dwell 居中对齐 1.5/4.5/7.5/10.5/13.5s。

Auto-updated:
- 2_世界观人设/scenes/zhenbei_wangfu_zhengting/zhenbei_wangfu_zhengting.md — 步骤二 `>` 注 + `动作:` 块 + index 表「视频秒段」列三处同步：dwell 改为 #1 0-2s / #2 4-5s / #3 7-8s / #4 10-11s / #5 13-15s（首尾 2s、中间 1s，4 段过渡）；5 个截帧点全部落入静止 dwell；prompt body 1970 字 ≤2000。

No conflicts found in: 截帧时点（仍 1.5/4.5/7.5/10.5/13.5，导出端表驱动一致）, 镜头/节奏行（仍「5 dwell + 4 段过渡」属实）, 方向序（北→西→俯瞰→中景→东 未动）, 锁定描述符/空间骨架。

待确认：是否把「dwell 必须覆盖固定截帧时点」回填 ai_video.md rule 12.10 作通用规则。

## Follow-up 014 — 2026-06-19
Source: user_input/follow_ups/014-20260619-010000-scene-liucheng-image-first-tushengtu.md
Summary: 场景方向背景图流程 video-first抽帧 → image-first 图生图（全局底图作 reference + 各方向 prompt → image→image）；抽帧降为兜底；walk-through 视频用途改为 shot reference。

Auto-updated:
- 2_世界观人设/scenes/zhenbei_wangfu_zhengting/zhenbei_wangfu_zhengting.md — 生成流程改 image-first（4 步）；步骤一 用法注升为「全局参考底图」；index 两条注释改「图生图为主、抽帧兜底」。
- .claude/agent_refs/project/ai_video.md — 场景生成流程规则改 image-first → 各方向 image→image（主），抽帧兜底，walk-through=shot reference；保留 mp4→图片不支持铁律。

No conflicts found in: 截帧时点表（保留作兜底，仍 1.5/4.5/7.5/10.5/13.5 且 dwell 已对齐）, 步骤二 walk-through prompt（仍生成、用途转 shot reference）, 锁定描述符/空间骨架, 命名/导入约定。

代码无改动：🧭 截取方向背景图 按钮 + ScenePlateExtractor（表驱动截帧）全部保留作兜底路径。

## Follow-up 014b — 2026-06-19（承 014：逐方向 plate prompt 改造）
Source: 同 014（用户确认逐方向 prompt 过一遍）
Summary: 6 个 bg plate md 全部改为 image→image 范式——参考行/流程注/小节标题从「上传 mp4 取视角」改为「上传步骤一全局底图作 reference + 本方向 prompt 图生图」，并对每个非朝北方向加 ⚠ 强转向锚（勿沿用底图朝北机位 + 本方向主体须为何）。

Auto-updated:
- scenes/zhenbei_wangfu_zhengting/{bg1..bg6}/{plate}.md — 各 3 处（`>` 流程注、`## 背景图 prompt` 标题、```text``` 内 `参考:` 行）；bg2朝南标「⚠180°反打」、bg3/bg4 标「⚠90°转」、bg5 标「⚠抬成俯瞰」、bg6 标「大光圈虚化」、bg1 标「底图即朝北可沿用」。各 prompt body 1077–1273 字 ≤2000。

No conflicts found in: 各 plate 的 主体/视角/光线/质感/构图 段（朝向几何本就写全、未动）, 导入归位「方位段」约定, 截帧时点表（兜底用，未动）。

## Follow-up 015 — 2026-06-19
Source: 用户报「downloads 场景立绘导入失败」
Summary: 场景立绘（步骤一全局底图）导入落 not_matched——下载文件名含「场景立绘」但无 pinyin scene handle，匹配不到 scene folder。修：① 立绘 prompt ```text``` 首行加 `zhenbei_wangfu_zhengting` handle（与步骤二一致）；② 已下载文件就位到 scene 根。

Auto-updated:
- scenes/zhenbei_wangfu_zhengting/zhenbei_wangfu_zhengting.md — 步骤一 ```text``` 首行加 pinyin handle；用法注加「导入路由」说明（首行=handle，缺则落 not_matched）。
- scenes/zhenbei_wangfu_zhengting/zhenbei_wangfu_zhengting.png — 既有下载文件从 not_matched/ 就位到 scene 根作全局建场底图（canonical 名）。
- .claude/agent_refs/project/ai_video.md — rule 12.3 v3 模板 step 6：立绘=image-first 全局底图，```text``` 首行须为 pinyin scene handle（无方位词），否则导入漏归位。

No conflicts found in: 步骤二 walk-through（首行本就是 handle、路由正常）, 各 bg plate（方位段路由、未受影响）, 导入器代码（无改动——本是数据/约定缺失，非代码 bug）。

## Follow-up 016 — 2026-06-19
Source: 用户「确保朝南/朝北/朝东等方向图下载导入也 work」
Summary: 实测各方向 plate 图导入也失败（同根因）——plate prompt 首行只有 `bg{N}_方位_描述`，无 pinyin scene token，importer 匹配不到 scene（中文标题/纯方位同样落 not_matched）。修：6 个 plate prompt ```text``` 首行各加路由 handle `zhenbei_wangfu_zhengting_{方位}`；用 importer 真逻辑仿真验证 6 方向全部正确归位。

Auto-updated:
- scenes/zhenbei_wangfu_zhengting/{bg1..bg6}/{plate}.md — ```text``` 首行加 `zhenbei_wangfu_zhengting_{方位}`（朝北/朝南/朝东/朝西/高位俯瞰/座前）；`>` 导入注从旧「方位段 from 主体行」改为「首行 handle = scene+方位」并标 not_matched 风险。各 body 1104–1300 字 ≤2000。
- .claude/agent_refs/project/ai_video.md — 命名/导入约定 + 「路由键」两条改：路由键 = `{scene}_{方位}` pinyin handle（既放首行、jimeng 时放主体行开头）；importer 需 filename 同时含 pinyin scene token + 方位 token，中文标题/纯方位会落 not_matched。

验证：用 DownloadsImporter 真 `_classify`+`_match_scene_plate` 仿真 kling 文件名 `..._zhenbei_wangfu_zhengting_{方位}_...png` → 朝北→bg1 朝南→bg2 朝东→bg3 朝西→bg4 高位俯瞰→bg5 座前→bg6 全 OK。

No conflicts found in: importer 代码（无改动——根因是 prompt 缺 pinyin handle）, 截帧时点/dwell（未动）, 立绘 first-line handle（015 已修、同源约定）。

## Follow-up 017 — 2026-06-19
Source: 用户「场景图 16:9 就挺好、只作 reference、shot 由 kling 转 9:16；已有的直接覆盖」
Summary: 确认场景立绘/plate 画幅非 load-bearing——16:9 可用（纯 reference，shot 按 9:16 出自动重取景）；导入对已有同方位图直接覆盖。

Auto-updated:
- .claude/agent_refs/project/ai_video.md — image-first 生成流程 bullet 末尾加「画幅非 load-bearing」+「导入覆盖语义」两句；以后不把场景参考图 16:9 当错误报。

已导入（上一步）：7 张就位（立绘 scene 根 + bg1..bg6 各 folder），Downloads 清空。其中 bg1 为旧 1920×1080、其余 2720×1536（16:9），均按「直接覆盖」语义放置。

No conflicts found in: plate prompt 内 `画幅: 9:16` 字段（保留为理想值、不强制；16:9 输出可接受）, 导入器代码（无改动）, shot 出片 9:16（不受 reference 比例影响）。

## 流程级契约变更应用 — 2026-06-19（`参考:` 行去 place_holder）
Source: 用户指令「每个 shot 的 `参考:` 行没必要放 placeholder 字样了，如 `裴知秋：place_holder, bg6_..._place_holder` → `裴知秋, bg6_...`」（common-level 格式约定，规则本体落 `ai_video.md` + stage6 playbook）。

Auto-updated:
- 规则：`ai_video.md` 新增 2026-06-19 amendment + 改 rule 12.4 参考行 canonical 模板（`{人物}, {场景bg代号}`、去 place_holder）；`ai_videos__全流程编排/playbooks/ai_videos__stage6_prompt.md` 五层模板 `参考:` 行同步。
- 产物：ep01 全 12 shot + all_shot_prompts.md 的 `参考:` 行去 `：place_holder` / `_place_holder`（如 `参考: \`裴昭, 裴知秋, 沈婉, bg3_朝东_东侧列柱\``）；各 shot `## Shot context` 的 `Reference uploads` 行同理去 ` place_holder`；scene 主档背景图系统说明里 `{plate_id}_place_holder` → `{plate_id}`。共清 89 处，全 wushen 零 place_holder 残留。

No conflicts found in: 角色行/识别标签/绑定行（未动）, 情节/台词/动作/走位（未动）, 出场列入规则（人物+场景仍全列、仅去占位字样）。

## Follow-up 018 — 2026-06-19（修正 016：导入改 importer 方位路由，比长 handle 更稳）
Source: 用户「朝北重下了，请导入并确保导入功能 work」
Summary: 实测 kling 把下载名截到 prompt 首行前 ~10 字——016 给 plate 首行加的长 handle `zhenbei_wangfu_zhengting_朝北` 反而把方位挤出截断窗、会误落 scene 根。改对策：① revert 6 plate 首行回 plate_id（方位在前、抗截断）；② 改 importer：未匹配到 scene 名时按方位 token 跨 scene 找唯一 plate 归位（`_match_plate_any_scene`，歧义→not_matched 不串档）。bg1 朝北已导入（覆盖旧 1920×1080 → 新 2720×1536）。

Auto-updated:
- libs/infrastructure/writers/downloads__writer.py — 加 `_match_plate_any_scene` 方位兜底路由 + 接入 import_drama（仅在 `_classify` 未命中时触发，加性改动）。
- tests/test_downloads_import_shots.py — +3 回归测试（真 kling 截断名 6 方位全归位 / 立绘 handle 落 scene 根 / 多 scene 同方位歧义→not_matched）。19 全过。
- scenes/zhenbei_wangfu_zhengting/{bg1..bg6}/{plate}.md — 首行 revert 回 plate_id；`>` 导入注改回方位路由。
- .claude/agent_refs/project/ai_video.md — 命名/导入约定 + 截断说明两条改写：plate 首行=plate_id（方位在前抗截断）、importer 按方位跨 scene 唯一匹配；立绘/walkthrough 靠首行 `{scene}` handle 留 scene 根。

验证：DownloadsImporter.import_drama 对真 kling 截断名（`bg1_朝北_高座主` 等 6 个 + `zhenbei_wangf` 立绘）端到端仿真——6 方位各归 bg folder、立绘归 scene 根、全 unmatched 空。

No conflicts found in: 立绘首行 handle（015，仍需要、未动）, 截帧时点/dwell（未动）, 16:9 画幅约定（017，未动）。

## 流程级契约变更应用 — 2026-06-19（`参考:` 句柄加填写分隔符 `=>`）
Source: 用户指令「`参考:` 行加个分隔符、我自己填 `=>` 之后的部分；不用冒号怕跟 `参考:` 混淆误导 Kling，问有无好分隔符」→ 选定 `=>`（避开 `:`/`：` 混淆 + 避开单箭头 `→` 被读成运动方向）。

Auto-updated:
- 规则：`ai_video.md` rule 12.4 参考行模板 + 2026-06-19 amendment 改为每句柄跟 `=>`；`ai_videos__全流程编排/playbooks/ai_videos__stage6_prompt.md` 五层模板 `参考:` 行同步。
- 产物：ep01 全 12 shot + all_shot_prompts.md 的 `参考:` 行每句柄后加 `=>`（如 `参考: \`裴昭=>, 裴知秋=>, 沈婉=>, bg3_朝东_东侧列柱=>\``），共 24 行。`## Shot context` 的 `Reference uploads` 行保持纯清单（不加 `=>`，非填模型 ref 处）。

No conflicts found in: 角色行/识别标签/绑定行/情节/台词/走位（未动）。

## Follow-up 019 — 2026-06-19
Source: 用户「shot1 "脑子里全是这身子的事" 太突兀、不像正常人说的」
Summary: 台词大师 D1 + 自然口语进阶（禁"这/那+事"指代含糊黑话）——主角 S1 OS 把含糊的"脑子里全是这身子的事"改成具体自然的"这身子的记忆，全涌进脑子"（贴 c1 声口：沉静克制、慢语速留白多；逗号加气口；对齐 script "前身记忆如潮灌入"）。

Auto-updated:
- 5_6_分镜与prompt/episodes/ep01/shots/shot01/shot01.md — 台词配音块 + 视频prompt台词字段（2 处）
- 4_剧本/episodes/ep01/dialogue.md — 裴知秋 S1 OS 行
- 4_剧本/episodes/ep01/script.md — S1 台词列
四处同步一致；含义不变（穿越+前身记忆+今天除族），S1→S2 连贯保持（S1 OS 预告除族 → S2 裴霆宣判，呼应不破）。

待定（未动，超出本次请求）：S1 OS 约 55 字 / 10s ≈ 5.5 字/秒，OS 理想 ≈3 字/秒——偏密；如要更从容可交 时长节奏 仲裁（加时长或拆镜），本次只按用户所指 surgical 改措辞、不动结构。

## Follow-up 020 — 2026-06-19
Source: 用户「shot3 主角跪着背对父亲讲话很突兀，为什么没提前发现？」+「找到原因后检查每个 shot 每个 prompt 防再发生」
Summary: 站位朝向（C 系列）漏检——主角受责跪姿在 shot03 被整身转向旁人(裴昭)、背/侧对北面高台上的父亲。根因：站位朝向 skill 无「下位/跪者身体锚定权威、只转头应旁人」+「跨镜朝向连贯」规则。已修 shot03、补规则、全 ep01 扫一遍。

根因（为何没发现）:
- ai_videos__站位朝向 原 C1–C6 只查「说话人朝向写死/对谁说=视线/相对位/OS朝向/防重复/参考图绑定」，**没有**「受责跪者身体必须锚定权威方、只转头应对旁人」这一条；也**没有**强制「跨镜同人朝向/站位连贯（对相邻镜+scene 站位锚）」。shot03 把主角整身转向裴昭满足了 C1/C2（朝向写死了、视线落点也有），却让他背对了北面的父亲——规则盲区，故过审未拦。

Auto-updated:
- .claude/skills/ai_videos__站位朝向/SKILL.md — 新增 C7（跪/受责/下位者身体锚定权威、只转头应旁人、绝不整身背对）+ C8（跨镜朝向/站位连贯、对齐 scene 站位锚）；工作流加「必带核对 C7/C8」。
- shots/shot03/shot03.md — 走位/角色识别/情节/动作/台词 五处改：裴知秋身体始终朝北跪向高台父亲、仅转头朝东应对裴昭、绝不背对；沈婉归位西侧（对齐 scene 站位锚 母妃居西）；台词加面向 tag。
- shots/shot05/shot05.md — 走位 立→半跪（承 shot02/03 受责跪姿、起身在 S8）+ 标注面部特写仅见脸（南向为主观、非空间背对）。

全 ep01 站位朝向扫查（12 镜）结论:
- shot02/shot08：主角正确面朝北面父亲（受责跪 / 起身平视），✓。
- shot03：本次修复（身体朝北、转头应裴昭）。
- shot05：立→半跪 posture 连贯修复。
- shot01/06/07/09：bg6 座前虚化「面部特写」，主观 OS/系统镜、背景全虚化不显父亲空间，偏南/向镜为主观取景、无可见背对破绽，四镜彼此一致，✓。
- shot04：回忆镜（年少护弟挡掌），正面迎黑影、背护裴昭＝正确护人站位，✓。
- shot10/11/12：决然离场，背对高座朝南门走＝剧情本意（离家不回头），✓。

No conflicts found in: 各镜台词措辞（未动，归台词大师）, 景别运镜（未动，归运镜）, 剧情链（未动）, 锁定描述符/色彩。

## webapp 修复 — 2026-06-19（导入路由 shot→character 误判 + 字幕/合成功能澄清）
Source: 用户报「shot1 视频下到 Downloads，应导入 shot1 folder 却进了 character folder；且每 shot 字幕文件/烧字幕按钮、ep 合成按钮等改 workflow 后『没了』，请加回」。

根因：`projects/ai_video_management/libs/common/drama_layout.py` 的 `episodes_dir()` 只认 `episodes/` 与 `4_剧本/episodes/`，**不认新布局的 `5_6_分镜与prompt/episodes/`**（shots 实际所在）→ `DownloadsImporter._collect_candidates` 收 0 个 shot 候选 → shot 视频 fall through 到文件名打分、命中名内「裴知秋」→ 误入 character folder。其余「丢失」感同根：shot folder 一直无 render 视频 → 字幕按钮（挂 shot 视频 tile）不显示、ep 合成（需 renders）抛 `NoShotVideosError`。

Fixed（projects/ai_video_management 代码）:
- `libs/common/drama_layout.py` — 加 `SHOTS_STAGE="5_6_分镜与prompt"`；`episodes_dir()` 候选加 `5_6_分镜与prompt/episodes`（优先于 script-only `4_剧本/episodes`）；同时修复同样依赖它的 bgm-cue 扫描与 sub_type 计数。
- `tests/test_drama_layout.py` — 加回归 `test_shots_stage_episodes_wins_over_script_stage`（5/5 通过）。
- `apps/ui/src/components/SiblingMedia.tsx` — 烧字幕按钮 tooltip 由错误的 `*_subtitled_zh.mp4` 改为实际产物名 `shot{NN}_zh.mp4`（zh/en/zhen）。

调查结论（两 Explore agent）：字幕（`subtitles.md` 中/英/中英双语 + 💬 烧录按钮，输出 `shot{NN}_{zh|en|zhen}.mp4`）、ep 合成（episode-md 阅读栏 `🎬合成(原片)/中文/EN/中英`→`/api/concat-episode`）、BGM/角色视频/媒体管理 **均完整存在且已接线，无代码丢失**，仅被导入 bug 挡住。唯一从未落地的是 CLAUDE.md/ai_video.md 提及的 `tools/mux_av.py`（视频+台词MP3+BGM 三轨混音），待用户确认是否新建。

wushen 产物:
- 导入 shot1 视频 → `5_6_分镜与prompt/episodes/ep01/shots/shot01/renders/`（保留原始下载名）。
- 删误路由旧副本 `2_世界观人设/characters/c1_裴知秋/c1_裴知秋1.mp4`。

## Follow-up 021 — 2026-06-19（字幕 + 台词人称/自然度）
Source: 用户三条——① shot8 自带字幕，确保所有 shot 不带字幕；② shot9「潜伏待显，旁人看不出」突兀、「这股劲……进骨头里了」别扭；③ shot2 父亲当面对主角说话却用「他」(除他族籍)，最基本的人称都错。

A. 字幕（全 12 shot）:
- 实测 Seedance/Kling 对有台词的镜会自动把对白烧成字幕，prompt 不写字幕样式也照烧（对白越密越烧，shot8=4 句最明显）；旧负面词「画面文字」挡不住。
- 修：全 12 shot `渲染样式` 收尾「全程无字幕、画面不烧任何字幕/台词文字」；`负面词` 加「字幕 / 台词字幕 / 对白字幕 / subtitles」(系统 UI 文字镜 shot6/9 不禁画面文字、只禁台词字幕)。
- 规则回填 ai_video.md §12.4 amendment（2026-06-19）：负面词必须显式禁字幕。

B. shot2 人称（D7 新规则）:
- 裴霆当面俯视主角宣判却用第三人称「一个废人…除他族籍」，与 S8 他自己说的「随你」(第二人称) 还不一致。改为当面第二人称：「你丹田碎了、连口气都引不动，留在府里只会丢镇北王府的脸。」+「今日起，除你族籍，送你出府。」四处+subtitles 同步。
- 为何没 capture：台词大师 D1–D6 无「当面对话人称(你/他)正确」检查。已补 **D7**（当事人=受话人→用你；不在场/说给第三方→才用他），并复核全 ep01：仅 S2 错，S10「有他哭的」(对离场背影说给众人)正确、各 OS 三人称正确。

C. shot9 台词（系统+OS 自然度）:
- 系统「【武神躯】已注入——潜伏待显，旁人看不出」→「…已注入，暂时潜伏、外人看不出来」(去半文四字格「潜伏待显」)。
- OS「这股劲……进骨头里了。先压着，没必要这会儿就让他们看见」→「这股劲……沉进骨子里了。先压着，这会儿还不能让人看出来」。四处同步。
- 为何没 capture：台词大师 朗读/自然 检查只盯角色对白、漏审 OS/系统/旁白行。已在 skill 把「朗读测试 + D1–D7」明确**适用所有发声单元(对白+OS+系统+旁白)**、系统/旁白禁半文四字格言。

Auto-updated:
- shots/shot0[1-9..12]/*.md ×12 — 字幕负面词强化；shot02/shot09 台词四处同步 + subtitles.md。
- 4_剧本/episodes/ep01/{dialogue.md, script.md} — S2/S9 台词同步。
- .claude/skills/ai_videos__台词大师/SKILL.md — 新增 D7 人称关系 + 朗读测试/D1–D7 适用所有发声单元 + 工作流/description 更新。
- .claude/agent_refs/project/ai_video.md §12.4 — 负面词显式禁字幕 amendment。

No conflicts found in: 站位朝向(未动)、运镜、剧情链、锁定描述符；各 shot 视频 prompt body 仍 ≤2000。

## Follow-up 022 — 2026-06-19（ep01 全 12 镜台词总检 · 升级清单一次过）
Source: 用户「一次性全检查一遍」（用升级后 D1–D7 + 朗读自然 + 人称 + 节奏 完整清单）。
范围：ep01 全 12 镜每个发声单元（对白 + 内心独白 + 系统 + 旁白），逐行过。

结论：**无新增硬错**。本 session 已修的 S2(人称你/他)、S9(系统半文+OS别扭) 与先前 S1(自然度)、S3(站位) 之外，其余各行 D1–D7 + 朗读 + 人称 + 节奏(字数÷时长≤5) 全部通过。
- 节奏复核：S1 55字/11s=5.0(临界 OK)；S2 4.8；S3 3.6；S4 4.7；S5 3.7；S6 4.5；S7 4.3；S8 3.7；S9 4.4；S10 2.9；S11 3.75；S12 1.5——全 ≤5。
- 人称复核：当面对话仅 S2 曾错(已修)；S10「有他哭的」(对离场背影说给众人)、各 OS 三人称(S4他=幼弟/S7他=旧主) 均正确。

两处「可接受但偏」项（未改、留待你定）:
1. shot06 系统选项「②硬刚离府」——「硬刚」是网络流行词；放系统(游戏机制冷声)+红果短剧语感里属可接受、且够punchy，故保留。要更古雅可改「②离府自闯」。
2. shot11 OS「我的路自己走，我的命自己做主」——轻微对仗；决意起点 beat 里这种排比可接受，故保留。要去对仗可改「往后的路，我自己走、自己扛」。

No changes applied this pass (确认性总检)；如需动上两处再说。

## Follow-up 023 — 2026-06-19（shot2 台词白话+朝向 / 全集白话再过一遍）
Source: 用户——① shot2「除你族籍/送你出府」仍书面、要白话；主角跪向没面朝父亲正北。② 大部分 shot 对话+旁白仍不够白话，仔细再过一遍。

A. shot2:
- 台词白话：line1「裴家世代以武立身，守的是北疆万里、挡的是关外妖患…」→「裴家几代人都靠真本事守北疆、挡妖物。你丹田一碎、连气都提不上，留在府里只会给裴家丢脸。」；line2「今日起，除你族籍，送你出府」→「从今天起，你就不是裴家的人了，离府吧。」
- 朝向（站位朝向 C7）：走位/镜头/角色识别写死——裴知秋身体与跪向正面朝北、正对仰向高台父亲、四分之三侧背朝镜头、绝不正脸朝南/朝镜头；相机自南偏侧越其侧背向北仰拍。

B. 全 12 镜白话再过一遍（对白+OS），改书面/对仗/成语为大白话:
- S1：把我除族→把我赶出裴家。
- S5：闯出一片天地/天大地大→外面天大地大，闯出条活路。
- S7：苟…落得什么下场→窝囊一辈子…落了个什么下场。
- S8：这族籍…我自己退→这个姓…我自己不要了。
- S11：我的命自己做主/亲眼去看看→我的命我自己说了算/去看个明白。
- 其余（S3/S4/S6系统/S9/S10/S12）复核已够白话或属机械系统音、保留。
- 四处同步（shot 台词+配音 / dialogue.md / script.md / subtitles.md），各 body ≤2000。

待办：shot8 字幕仍在（负面词没挡住，见下条单独处理）。

## EP2 启动 — 2026-06-19（stage4 剧本）
Source: 用户「EP1 差不多了，开始做 EP2」+ 交互定调（地痞欺弱·主角看不过出手 / 主角刚得武神躯修为浅·收拾地痞够用遇高手不够 / 本集不点太虚剑宗·只给战力印象 / 玉佩零光 / 双景）。

产出：4_剧本/episodes/ep02/{script.md, dialogue.md}——12 镜 ~100s「离家上路·初入江湖·玉佩异动」。
- 承 EP1 末（已离府独行，不重演离家）；起=暮色荒道独行+系统含糊初引(不点宗门)；承=进集市初见江湖；转=地痞欺压叫卖老者→主角出手→几下放倒但挨一记+打完微喘(战力锚:能打混混·遇高手不够)；钩=玉佩透微温零光起疑(身世)+暗处目光掠过(暗线)+江湖不太平(危机)。
- 战力锚：S7 能打+险+S8 OS 自评三处合力，给真实战力印象、不无敌；藏锋全程无外放。
- QC：台词大师 D1–D7 自审通过（白话、人称正确无当面用他、节奏 ≤5/s、声口分明、无字幕信息）；全剧序列边界：去 EP2 结尾「暮山如压」避免与 EP1 S12「压城」重复。

待办（stage5/6 前）：建新卡——场景 暮色荒道/集市长街（场景档+全局底图+各方向 plate）、角色 地痞头目+喽啰/叫卖老者（锁定描述符+voice_id+ref，配角轻量）。然后 stage5/6 分镜+prompt（站位朝向 C1–C8 + 无字幕铁律 + 格式契约）。

## EP2 剧本 迭代 — 2026-06-19（台词多轮打磨）
Source: 用户连续反馈（同 stage4 内）。
- 整体对白更丰富/更白话 + 市井烟火（加摊贩吆喝、口语小词、地痞痞气）。
- 称呼修正：地痞非官 → 老者改称「几位大爷」（删「官爷」）。
- S4 去突兀说教句「武者的天下比裴家大」→ 主角自己想到「宗门是练武去处」、铺垫找宗门。
- 系统去掉「前头有机缘，自己去寻」（系统更克制、不当任务发布机、不剧透机缘）；S4 随之改为主角自行连接宗门。
- S8 点出**丹田暗复**：武神躯让丹田悄悄复原（故能打地痞）、旁人仍当他废人——与战力锚合一（修为刚起步·收拾混混够·遇高手不够）；S8 时长 10→12s 容这句 OS。
- QC：台词大师 D1–D7 复核——全白话、人称正确、节奏 ≤5/s（S8 4.3、S6 4.8 等）、声口分明；藏锋无外放、零字幕信息。script+dialogue 同步。

## 新增 skill：白话大师 + EP2 白话再过 — 2026-06-19
Source: 用户「有没有白话文大师技能加到 claude，重过一遍 EP2 剧情和对话」。
- 新建 `.claude/skills/ai_videos__白话大师/SKILL.md`——白话口语化专项（B1 朗读测试 / B2 去文言半文四字格 / B3 去对仗格言排比 / B4 书面→白话替换词典 / B5 去翻译腔 / B6 小词短句口头语 / B7 称呼声口地道）；台词大师 D1/D1b/自然口语进阶的"专项加强版"，台词仍书面时单独再过。只动说话方式、不动剧情/人称/朝向/setting 专名。
- 接入流程：`全流程编排` stage4 QC = 台词大师 + 白话大师；`审查总编排` 单镜层加序 1b（紧跟台词大师）。
- EP2 用白话大师重过：5 处书面残留换口语——根基扎稳→底子打牢 / 去处→地方 / 一位→一个 / 旁人→别人 / 罢了→算了。EP2 全台词过朗读测试。

## 新增 skill：武打设计 + 特效设计 — 2026-06-19
Source: 用户「EP2 开始有打戏、武打动作特效是仙侠卖点，有 skill 吗？没有就建」+「不光武打还要特效，分开还是合并？」
- 新建 `ai_videos__武打设计`（W1–W7）：招式具体配时间轴/攻防回合/受击打击感/战力分级/节奏镜头配合/**藏锋无外放特效边界（不靠金光、靠身手+劲力+风压尘土+对手反应）**/平台合规。动作表演的打戏专项加强版。
- 新建 `ai_videos__特效设计`（X1–X7）：超自然视觉层（威能/法术/灵气/玉佩/暖流/系统UI/异象）的有无·形态·**力量外放边界（藏锋期全禁外放光效）**·释放时机·氛围真实·平台合规。与光线色调协作（发光禁令由光线色调落地、本 skill 定该不该有/边界）。**分开建**（单一职责：武打=动作、特效=超自然视觉、光线色调=光色执行）。
- 接入：`审查总编排` 单镜层加 4b 武打设计(仅打斗)、6b 特效设计(涉超自然)；`全流程编排` stage5 QC 条件性加二者。

## EP2 stage5/6 完成 — 2026-06-19
- 建卡：c6_地痞头目、c7_叫卖老者（配角轻量·锁定识别标签+voice_id）；场景 mose_huangdao(暮色荒道)、jishi_changjie(集市长街)（image-first：锁定描述符+一句话锁定+步骤一全局底图+plate index）。
- 分镜：shotlist.md（11 镜/104s）+ shots/shot01–11/shotNN.md（全套五层 prompt + 台词配音）。
- 规则落地：站位朝向 C1–C8（受责/对话朝向写死、护人不背对、视线落点）· 无字幕铁律（全 11 镜 渲染样式「全程无字幕」+负面词禁字幕/subtitles）· 锁定描述符 byte-identical · 9:16 · 3–15s · ≤2000字（1027–1544）· 藏锋无外放（无金光瞳光威能）。
- S7 打戏（武打设计 W1–W7 落地）：侧闪/扣腕借力摔/卸力/沉肘 具体招式配时间轴 + 攻防回合 + 受击反馈(摔翻扬尘/闷哼) + 战力锚(几下放倒地痞·挨头目一记横拳·打完压息) + 藏锋无外放(风压鼓衣/脚下扬尘/掀退=物理冲击、零金光) + 合规(无喷血断肢/凶器刃口特写)。
- S2/S9/S8 特效设计落地：系统鎏金UI(微光不照人)、玉佩零光透温、暖流贴身内透不成光斑。
- 待办（用户渲染前）：各场景 plate folder + 图生图 prompt 文件；按需出图/出片。

## 场景文件夹全面中文化 — 2026-06-19（用户「全做」）
Source: 用户「PNG/prompt keyword 还是拼音，所有地方一起改成中文，确保导入 work」。
- 场景文件夹/主.md/全局底图PNG/walk-through MP4 + 所有引用（场景卡步骤一 handle、各 plate 参考、EP2 全 shot 的参考/场景行、shotlist、world.md）从拼音改中文。
- 重命名：jishi_changjie→集市长街 ✅、mose_huangdao→暮色荒道 ✅（文件夹+文件全改）；zhenbei_wangfu_zhengting→镇北王府正厅 **内部文件已改名(.md/.png/.mp4)，但文件夹改名被占用句柄阻塞(WinError5)——待用户关掉占用后补一条 rename**。
- 内容替换 23 文件 71 处；清理"中文 中文"重复 + "pinyin handle"措辞 14 处。
- 导入验证：中文文件夹下 `集市长街_...png`→scene根、`集市长街_街角_摊位_...png`→bg2 plate，路由正常；27 测试全过。
- 约定更新：CLAUDE.md ai_videos 路径规则——drama 文件夹+结构性文件仍 pinyin；角色/场景/plate 子文件夹**可中文**（左 nav 原生中文 + 导入 routing key 全中文）。
- 待办：用户关掉 zhenbei 场景文件夹的占用句柄（资源管理器窗口/视频播放器/webapp 标签）后，补 `镇北王府正厅` 文件夹改名。

## EP2 实拍反馈批修 — 2026-06-20
Source: 用户连发 EP2 shot2/6/7/8/9 实拍问题（"不指名 shot 即 EP2"约定）

Auto-updated（产物）:
- ep02/shot02（系统句）— "宿主已离裴家…找个能练身子的地方落脚"→"宿主已离开裴家。眼下要紧的，是找个地方落脚，把功夫练起来"；同步 dialogue.md/script.md/shot02.md（4 处）
- ep02/shot06 — 镜内三人站位钉死"全程相对位置不变·反打不换位"+护人改"横臂虚拦不搂抱"（修主角"抱"老人→恶霸挤中间→老人移位）
- ep02/shot07 — 2 喽啰各给差异化外形（瘦高甲/矮壮乙）+ 点名区分 + 负面词禁同脸复制人；"脚下一沉/跺脚"改"挨棍趔趄踉跄强撑站稳"（动作可读）
- ep02/shot08 — 老者钉死"没逃、留场道谢"+负面词禁"老者逃跑/混在逃跑人群"（修老者被卷进落荒人群）
- ep02/shot09 + shot11 — 玉佩加"褪色旧红绳系挂颈间、垂入衣襟内贴胸"（修像凭空贴皮）；同步 c1_裴知秋 bible 标志道具

Auto-updated（skill 进化）:
- 白话大师 +B2b（单字文言动词带宾语→双音节：离裴家→离开裴家）+B5 拆"能V的N"别扭定语 + 词典/反例补行
- 站位朝向 +C9（镜内多 beat/反打站位连贯）+C10（在场/离场锚定：该留的不许跟着逃）
- 动作表演 +A8（动作可读·禁孤立功能性简写如跺脚）
- 武打设计 +W8（群战杂兵无 ref 也差异化、禁同脸）
- 特效设计 +X8（超自然道具世俗承载合理：玉佩须绳系挂、非贴皮）

No conflicts found in: world.md / arc_outline.md / 其他 ep / 其他 shot

## EP2 shot11 玉佩凭空跳出+像钱币 — 2026-06-20
Source: 用户反馈 shot11 手按胸前玉佩凭空弹出、且玉佩像钱币
Auto-updated:
- ep02/shot11 — 改"按回玉佩"为"隔衣襟按胸口、玉佩全程藏衣内不外露、不显示玉佩本体"（小说原文/情节/走位/动作/负面词）
- ep02/shot09 — 展示玉佩处补写形态"不规则断裂半块古玉、断口粗糙、非圆铜钱"+负面词禁"像铜钱/钱币/硬币"
- c1_裴知秋 bible 标志道具 — 玉佩形态(非钱币)+平时藏衣内不外露+不凭空冒出
- 特效设计 X8 扩写 — 超自然道具的承载/出没/形态三点（藏衣内别凭空弹出、半块古玉非圆钱币）
No conflicts found in: 其他 shot / world.md

## EP2 shot6 渲染烧字幕 — 2026-06-20
Source: 用户反馈 shot6 出字幕、其他 shot 正常
Note: shot6 原"无字幕"落点与好镜一字不差→prompt 非区别项，最可能是多角色口型对白镜渲染抽卡烧字幕（同 EP1 shot8）
Auto-updated:
- ep02/shot06 — 渲染样式前置「全程绝对无字幕」directive + 负面词扩到 中文字幕/对白文字/字幕条/弹幕/caption/text overlay（高风险档兜底）
- 格式契约 +K19（无字幕铁律落点齐全校验 + 多角色口型对白镜高风险加强档 + 已合规仍出字幕=渲染抽卡→重roll 提示）
建议: shot6 重 roll 一次即可清掉
No conflicts found in: 其他 shot

## EP2 shot8 对白接独白太快 — 2026-06-20
Source: 用户反馈 shot8 主角答"没事"后立刻接内心独白、太快、中间要空0.5~1秒
Auto-updated:
- ep02/shot08 — 插入 7.5-8.5s 静默留白 beat、时长 12s→13s；动作/节奏/台词/配音块/Duration 标"应'没事'后静默约1秒再起独白"；同步 script.md S8(12→13s+静默标注)
- 时长节奏 +PA8（镜内换气口：对白结束→紧接内心独白/情绪大转折前 默认留 0.5~1秒静默 beat、不抢话）
No conflicts found in: 其他 shot / dialogue.md

## EP2 shot9 玉佩缺取出动作 + 修正全链路连贯 — 2026-06-20
Source: 用户反馈 shot9 玉佩发烫该有从衣内掏出的动作、怎么突然就在衣外
Auto-updated:
- ep02/shot09 — 补可见取出 beat：探手入衣襟→捏红绳→从衣内掏出→提到眼前细看（情节/走位/动作6-9s/负面词）
- ep02/shot11 — 修正连贯：上一版"玉佩全程藏衣内"与 shot10(玉佩在手中看)矛盾；改为承接 shot10、把手里玉佩塞回衣襟内的可见动作（小说原文/情节/走位/动作/负面词）
- 玉佩全链路连贯：shot9 掏出 → shot10 手中端详 → shot11 塞回，每次进出衣内皆有动作、不瞬移
- 特效设计 X8 ② 加强：道具露出/收回必须写可见取出/塞回动作 beat（探手入衣襟→捏绳→掏出→提眼前），"只写撩衣襟看"不够
No conflicts found in: shot10（玉佩在手中、与新链路一致）

## EP3 阶段4 剧本完成 — 2026-06-20
Source: 用户「继续武神觉醒 → 开 EP3 剧本」+ 三问决策（测灵根晶石 / 不屑隐藏半露 / 邋遢老剑客形象的凌虚子暗中观察）
新建（产物）:
- 4_剧本/episodes/ep03/script.md — 12 镜 / 112s，起承转钩：抵落魄太虚剑宗→测灵根晶石入门测验受轻慢→不屑藏死、灵石透一缕异光半露即收（藏锋·法器反应非体放）→邋遢老剑客(凌虚子真身)一眼识异破格留人→大比在即垫底即除名生死局→藏锋待发收钩
- 4_剧本/episodes/ep03/dialogue.md — 同步三类台词 + 声口提示
QC（阶段4 关卡·blocker 清零）:
- 台词大师 D1–D7：全白话无古语、有因果、声口分明、人称正确 ✅
- 节奏（字数÷时长≤5）：S4/S9/S10/S11 原超标→ trim 台词 + 延时（S4 8→10/S9 10→11/S10 9→12/S11 9→10），全镜达标 ✅
- 全剧序列+连贯（跨 EP1/EP2 通读）：开场不重启、口头禅带变奏非平复用、爽点递进未泄底、系统线承接无矛盾、集内站位单调推进无二次离场 ✅
承接 EP2 末：数日跋涉抵宗门，不重演出镇；玉佩/暗处目光长线本集不接。
待建卡（stage5/6 前）：场景 太虚剑宗山门/演武场；角色 测验执事/轻视弟子/凌虚子(邋遢老剑客形象)。
No conflicts found in: world.md / arc_outline.md / EP1 / EP2

## EP2 全集语速校准 + metrics 工具 — 2026-06-20
Source: 用户反馈 shot8 老者"小恩公"吞字、台词太快；并建议每集生成 fact&metrics(语速/字数)
根因: 时长节奏 PA1 阈值一刀切≤5，老者(慢嗓)4.86压线过、实则该按~3.4；且 skill 是"被调用才跑"、未对 shot8 实算
Auto-updated（工具/机制）:
- 新增 tools/ep_metrics.py：扫某集所有 shot、按音色算字/秒(OS/慢嗓3.5、普通5)、标⚠超速、出 episodes/{ep}/metrics.md(派生缓存·勿手改)
- 时长节奏 PA1/PA2 改：按"每句各自角色语速"算、慢嗓/老者/OS 按~3-3.5、别卡阈值上限作者化(留余量、配音块写"逐字念全莫吞末字")
- 时长节奏 工作流加"集级先跑 ep_metrics.py 锁定超速句"
- 生成 ep02/metrics.md：首轮报 10 句超速
Auto-updated（ep02 产物·全部加时长修，⚠清零）:
- shot01 9→11s、shot02 10→13s、shot04 8→9s、shot05 10→14s、shot06 9→12s、shot08 14→15s；shot03 路人甲时长目标3.5→5s(镜长不变)
- 各 shot 时长目标/动作时间窗/Duration 同步；script.md S1/2/4/5/6/8 时长 + 头注约102s→约120s
- 复跑 metrics：over_speed_lines=0，全集120s/平均2.75字每秒
No conflicts found in: dialogue.md（台词未改，仅时长）/ 其他 shot

## EP2 shot11 玉佩突然在手上 — 2026-06-20
Source: 用户反馈 shot11 玉佩突然在手上、之前在胸前、突兀
根因: shot10 只开头"看玉佩"、随后整镜回头警觉、玉佩/手位置丢失；shot11 开场玉佩摊在手→跳变
Auto-updated:
- ep02/shot10 — 一凛时"握玉佩的手收拢按到胸口、全程攥在手按胸前"，让玉佩状态延续到镜尾(走位/动作)
- ep02/shot11 — 改为承接 shot10 末"手仍扣玉佩按在胸口"→顺势塞回衣襟，去掉"玉佩摊在手上"的跳变(小说原文/情节/走位/动作)
- 玉佩链路连续：shot9掏出→shot10攥手按胸→shot11塞回
- 特效设计 X8 加 ④跨镜状态承接：手持道具上一镜结尾状态须在下一镜开头延续、交界两镜都写"承接上一镜:道具在哪什么姿势"
No conflicts found in: shot9（掏出在手、与新链路一致）

## 全局：去除所有人物口头禅 + 台词大师 D8 — 2026-06-20
Source: 用户「把所有人物口头禅都去掉」（起因：EP3 上一版把主角 bible「锋，藏着」当口头禅复用、读着像念稿喊口号）
Auto-updated（产物·7 角色 bible 去口头禅段）:
- c1 裴知秋 / c2 系统 / c3 裴霆 / c4 裴昭 / c5 沈婉 — 删「## 标志台词或口头禅」整段；c1「说话风格模板」示例句去签名句、改中性示意
- c6 地痞头目 — 删「## 标志台词（口头禅）」段；c7 叫卖老者 — 删「## 标志台词」段（声口仍由 voice_id 配音参考定义）
Auto-updated（skill 进化）:
- 台词大师 +D8（禁角色口头禅/签名重复句：同义每次换不同大白话、辨识靠声口+造型不靠重复台词；bible 不再设标志台词字段）+ 描述/工作流 D1–D7→D1–D8
约定：角色辨识不靠口头禅；后续所有集台词都不安排反复签名金句。

## EP3 阶段4 剧本重写（try again·新剧情）— 2026-06-20
Source: 用户大改方向——镇上宗门招收考核(灵石测资)、众宗门含落魄剑宗到场、主角一家+裴昭也来、裴昭上等资质被顶宗争抢、主角资质显惊艳又显残缺(须武神躯暗补否则有殒命风险·众人不知)、叹息转回弟弟 + 三问决策（结尾落魄剑宗老剑客收下 / 家人冷认出有言语交锋）
Regen（阶段4·delete-then-rewrite）:
- 4_剧本/episodes/ep03/script.md 整集重写：12 镜/113s。起承转钩＝抵镇循考核→撞见家人/裴昭被顶宗抢→裴昭冷认出言语交锋→主角上灵石爆光比裴昭更盛(法器发光非体放)→光中显残缺、顶宗惊变缩手→叹息转回裴昭、主角无人问津(武神躯暗补众人不知)→落魄剑宗邋遢老剑客(凌虚子真身)破格收下→家人冷散→入太虚剑宗藏锋收钩
- 4_剧本/episodes/ep03/dialogue.md 同步重写
关键反转链：废人→资质绝顶(打脸全场一瞬)→却残缺必死(被弃)→武神躯暗补(藏锋·真底牌不露、世人当必死残废)。复用家人卡 c3/c4/c5。
QC（阶段4·blocker 清零）:
- 台词大师 D1–D8：全白话无古语(改「虚位以待→位子给您留着」)、有因果(S8 残→反噬→没命)、声口分明、人称正确(S5/S11 当面"你"·对父说主角"他/废物"第三方)、**无口头禅/签名重复句**(裴昭讥讽每次新写) ✅
- 节奏(字数÷时长≤5)：12 镜重算全达标(最高 ≈4.3) ✅
- 全剧序列+连贯(跨 EP1/EP2)：开场承接不重启、资质惊艳一闪但武神躯真底牌不泄(藏锋 intact)、系统线无矛盾、改「被赶出府→离了府」对齐 EP1 主动离家 canon、集内站位单调推进家人仅一次离场 ✅
承接 EP2 末：数日后抵镇循考核；玉佩/暗处目光长线本集不接。
待建卡(stage5/6 前)：场景 镇演武场(考核场·旗台+灵石)；角色 凌虚子(邋遢老剑客)/顶宗执事(群)/围观武者(群)；复用 c3 裴霆/c4 裴昭/c5 沈婉。
No conflicts found in: world.md / arc_outline.md / EP1 / EP2

## 宏大重构：考核弧扩展 + 六幕蓝图 + 两季规模 + 多条 canon — 2026-06-20
Source: 用户连发多条 macro 方向（考核多集化/群英+皇室公主/人妖战火背景/双宝合一主线/两季80集/裴霆武王/武神传说/武徒改名）
world.md（§四 canon + §1 力量体系）新增/更新:
- §1.5 新立【资质五档+测资灵石特效+内外门弟子分档+残缺资质机关+境界梯揭示规则】
- §四 新增：大梁皇朝(萧姓)、靖安公主萧若云(爱民统兵杀妖·边疆并肩主线钩)、各宗翘楚(云骁/百里寒/江晚/女天骄)、太虚师姐(待建卡)、双宝合一主线(武神躯+第二宝=最强·败妖王·终局锚)
- §四 更新：玉佩(与武神躯伴生·疑第二宝线索)；凌虚子(=EP2暗处观察者·与第二宝相关)
- 裴霆→武王境(望裴昭登武皇超越自己)；武神→世人当传说不信真有人能至
- 规模：两季×各~80集，先做第一季；境界首阶 武徒→武童(world/arc/ep03 共3文件统一替换)
arc_outline.md 重构: 新增两季划分 + 六幕蓝图(每幕概要+重大转折) + 长线伏笔(双宝/凌虚子观察者/玉佩伴生/妖族细作区分) + 考核弧拆5集细纲(EP3铺垫/EP4群英/EP5皇室公主人妖战火/EP6裴昭直招轮到主角/EP7主角反转残缺收徒,EP4-7留松)
EP3 script/dialogue 重写为考核世界观铺垫集(99s/11镜)；S1 按用户改"我也去测一测挑个宗门落脚"
⚠ 待办(下一步)：EP3 钩尾 S10–S11 现以"轮到主角上灵石"收尾，但主角测资反转已挪到弧末(EP6–7)，需 surgical 改 EP3 钩尾为前向钩(群英/皇室将登场·主角人群冷眼)，不在 EP3 让主角上场
QC：EP3 台词 D1–D8(含 D8 无口头禅)+节奏≤5 已过
No conflicts: EP1/EP2 已拍(EP2 暗处目光归属凌虚子=不露脸,无需改 EP2)

## 双宝伏笔·亲身体悟 beat — 2026-06-20
Source: 用户「主角需找个地方使用下武神躯，过程中跟玉佩互动埋伏笔，少一样机缘=最后成就武神所需」
- world.md §四 双宝合一行 补「亲身体悟（埋法）」：主角私下试用武神躯→玉佩异动互动→自察武神躯尚缺一样机缘(=第二宝/成就武神所需)，亲身埋钩非旁人告知
- arc_outline 长线伏笔 双宝行 + 第三幕概要 落该 beat（第三幕入宗修炼初期·可酌情提前到考核弧清净夜）
No conflicts: 与既有双宝主线/玉佩伴生/凌虚子暗线一致

## EP1 全维度 enhance（review_suite 过审）— 2026-06-20
Source: 用户「重新 enhance 一下 EP1 的 shot」→ ai_videos__审查总编排 全维度过 EP1 12 镜（task_id wushen_juexing-20260620-045637）
落地（surgical，4 并行 reviewer + 中央同步）:
- shot01: OS 台词白话精简(58→50字)、时长 11→13s；三处同步（shot01.md + dialogue.md §一 + script.md S1）
- shot02/03/08/10/11/12: K19 多角色口型对白镜升「高风险无字幕档」（渲染样式前置全程绝对无字幕 + 负面词扩 字幕条/弹幕/caption/text overlay）
- shot04: 回忆 OS 9→12s 解语速 + 挡掌打击感(顿帧/受创强撑、藏锋黑影无光、无喷血合规)
- shot06: 系统锁定串补 byte-identical(K8/X5) + 系统句间 0.4s 气口
- shot07/09: 时长/换气口校准；shot09 **姿态 break 修复**（半跪坐→承接已起身·全程站姿；整集姿态链单调:半跪1,3,5,6,7→起身8→站立9-12）
- shot09: 武神躯暗授藏锋无外放(暖流内透不成光斑/玉佩红绳系挂藏衣内/金芒一敛收净)；眼不发光铁律严守
- 多镜: PA8 对白→内心独白换气口；锁定描述符四角色 byte-identical、4 voice_id 对齐、零 hex、跨景别造型零漂移
跨层: 整集连贯(P1-P6)+全剧序列(EP1↔EP2 边界无重启/无签名台词复用)+立意安全(成长向·无低俗血腥) 全过
**已裁决（用户 2026-06-20）**: EP1 集级总时长 **129s 略超 90-120s 完播率窗**(PA7/14.3)——各镜语速修正累计所致。用户选 **B：保留台词全文、接受 129s + divergence note**（不精简）。落地：script.md 头注改 ~129s + 写 divergence note；script.md 镜表时长列同步至最终 shot（S1→13/S2→14/S4→12/S7→9/S11→10）。EP1 专属偏离，全剧默认仍 ≤120s。
审计: .audit/adhoc_agents/2026-06-20/wushen_juexing-20260620-045637/（events.jsonl + 4 spawn output.md）
No conflicts in: 锁定 bible / style_guide / world.md / arc_outline（均只读未改）

## 破庙场景 + 境界分级 canon + 第一季80集分弧架构 — 2026-06-20
Source: 用户「加破庙用武神躯场景(玉佩呼应+提示入武人一级,前身丹田碎前为武人第x级) + 看每幕怎么填满80集第一季,需更多剧情转折」
world.md §1.1 境界分级 canon:
- 每境分九级(一级最低/九级巅峰),跨大境界破"境关";升级由系统冷冽提示=成长爽点刻度
- 前身丹田碎前曾达武人三级、碎后跌回废人;主角破庙首运武神躯后正式入武人一级(从最底重修,武神躯之路直指武神无瓶颈)
arc_outline 更新:
- 双宝"亲身体悟 beat"前置到 EP3 破庙: 首运武神躯→玉佩呼应→系统提示入武人一级→暖流滞涩自察"缺一样机缘方成武神"(双宝伏笔亲身埋,不点破)
- 新增【第一季 episode 架构(填~80集·分弧)】: 幕一(EP1-2)/破庙(EP3)/考核弧(EP4-9·6集)/幕三太虚扎根(~EP10-40·30集·5子弧:入宗冷遇/藏锋潜修凌虚子点拨/内门选拔受辱/宗门大比生死局/振兴起步身份揭角)/幕四宗门历练崭露(~EP41-78·38集·5子弧:历练外派初遇天骄/妖族细作初触妖威/秘境夺机缘发现第二宝线索/玉佩揭角半露锋芒/战火逼近季末转折)≈77+机动≈80;每弧自带"被看轻→藏锋逆转→震动旁人"小爽点
- 细纲: 插 EP3 破庙(待写);考核铺垫 EP3→EP4(待 rename 文件夹+钩尾retune前向钩);旧松散EP4-7 renumber EP5-9 指向架构
⚠ 待办: ① rename ep03 文件夹→ep04 + 改其 S10-S11 钩尾为前向钩 ② 写 EP3 破庙剧本
No conflicts: EP1/EP2 已拍(破庙承 EP2 末玉佩/暗处目光,顺);与双宝/玉佩伴生/藏锋一致

## 解决两待办：EP3 破庙新写 + ep03→ep04 rename+retune — 2026-06-20
Source: 用户「先把这两个代办解决掉」
① rename + retune:
- git mv ep03→ep04（考核铺垫剧本）
- EP4 re-scope：去掉"裴昭上品测资+顶宗直招内门"(挪EP8)、"轮到主角上灵石"(挪EP9)；改钩尾为【前向钩】(各宗压轴天骄/皇室公主将至·选苗子赴边疆杀妖 + 太虚冷台凌虚子暗瞥主角)；主角本集不上场；承接改 EP3 破庙；标题/承接/留后全同步。98s/11镜
② EP3 破庙新写（短集 86s/10镜·内省独角戏）:
- 夜宿破庙首运武神躯→病躯渐稳→玉佩骤热与暖流共鸣(接EP2玉佩线·升级)→系统「已入武人一级」(成长刻度爽点)→冲下一关口滞涩"缺一块"→自察武神躯缺一机缘(双宝伏笔·亲身埋不点破)→天明决意奔考核兼寻所缺
- 藏锋：全程无金光瞳光、暖流/玉佩发烫靠OS+微表演不发光；系统一句鎏金UI
QC（D1–D8 + 节奏≤5 + 连贯/全剧序列）：均过——EP2出镇→EP3破庙→EP4抵镇链顺、玉佩共鸣升级非重复、系统线一致、爽点递进武神躯底牌仍藏、EP4凌虚子一瞥接canon
arc_outline 细纲：EP3破庙✅、EP4✅(rename+retune完成) 标记更新
待建卡(stage5/6前)：场景 破庙(单角度轻量)、镇演武场；角色 测资执事/凌虚子(一瞥)/群像；复用 c1/c2/c3/c4/c5

## EP3 破庙台词三处 fix + 台词大师 D9/D1b 进化 — 2026-06-20
Source: 用户逐句 review EP3 破庙——①"系统让我练身子"出戏(身子俗) ②"从头来过·这一次不一样"突兀(依赖观众没见过的前身级别) ③"还差一样东西·那才是真正的关键"+"找找我缺的那样东西"突兀(刚开练的主角像全知、连缺什么都不知道却说要找)
台词 fix(script+dialogue 同步):
- S2 "这身子底子太差…系统让我练身子" → "这副病躯底子太差…趁四下没人，把体内那股暖流，好好运转运转"(去"身子/练身子"出戏词)
- S7 "武人一级…从头来过。可这一次，不一样了" → "武人一级…一个废了丹田的人，也能重新踏上武道。这一步，才刚开始"(只用观众已知"废丹田"、不依赖前身级别、给爽点预期)
- S9 "还差一样东西。差的那样，才是真正的关键" → "总觉得还差点什么，又说不上来"(降全知结论为felt不安·主角自己也不知道差什么)
- S10 "找找我缺的那样东西" → "这力量里的古怪，往后再慢慢弄明白"(他不知道缺什么,不能说去找)
- 双宝伏笔锚/钩尾注解同步软化(felt不安·authorial才是第二宝·忌写满)
台词大师进化(反馈→进化):
- D1b 扩"白话≠出戏俗词"(仙侠慎用 练身子/身子骨→调养根基/这副病躯/运功)
- +D9 信息边界·伏笔别写满(角色别说超出当下认知的结论/别拿观众没见过的前情作比较/伏笔留authorial、台词只埋felt不安);描述+工作流 D1–D8→D1–D9
QC:节奏 S2/S7/S9/S10 重算≤4.5 全过;连贯不变
⚠ 提示:EP2(已定稿)主角 OS 也有"练身子……这身子太虚"同款出戏词(老者"身子骨"属乡野声口可留);是否回改 EP2 待用户定

## canon 修正：第二宝=武皇→武神的钥匙·武皇前不受影响 — 2026-06-20
Source: 用户「'像是缺了一块打不通'不对——玉佩背后的线索(第二宝)是主角从武皇突破武神的关键，之前都不会受影响」
canon 锁死(world.md):
- §四 双宝行重写：武神躯能带主角一路通畅修到武皇(武皇前不受第二宝有无影响)；唯武皇→武神是死关、须第二宝呼应合一方破=武神沦为"传说"的根因；埋法修正——武皇前绝不演修炼受阻/缺一块(演了即违canon)，第二宝只靠玉佩共鸣神秘感埋，"须双宝成武神"留季末/临武皇挑明
- §1.1 武神行：加"武皇→武神死关·须第二宝机缘方破→传说根因"
EP3 破庙剧本修正(去"受阻"逻辑硬伤):
- S8 "再往下冲…像缺了一块打不通"(受阻·错) → "这暖流走得又快又顺，一点没卡，我这废了丹田的底子竟顺成这样"(顺得反常·武神躯逆天爽点)
- S9 "总觉得还差点什么说不上来"(缺机缘felt·错) → "这力量这玉佩都来得蹊跷，可浑身前所未有地轻快有力——管它什么来头"(来历疑+focus变强)
- S10 "这力量里的古怪往后弄明白" → "找个落脚的地方，也找条往上走的路"(纯前向目标)
- header/双宝伏笔锚/钩尾注解同步：第二宝伏笔只靠玉佩共鸣、不演受阻、不让主角自察缺口/全知
arc_outline 同步：长线伏笔双宝行、第三幕概要(删旧"试用武神躯体悟缺机缘")、EP3细纲核心④、架构EP3 bullet 全改"顺得反常+玉佩共鸣·不演受阻"
QC:EP3 节奏 S8/S9/S10 ≤3.6 全过;连贯爽点正向、玉佩仍埋第二宝hook、无受阻矛盾

## 玉佩独立 prop 卡 + ref 图系统 + EP3 三句 fix — 2026-06-20
Source: 用户①EP2 两镜玉佩样子不一致,重要信物应单独设计 prompt+ref 图,每 shot reference ②EP3 破庙 S8/S9/S10 三句突兀/出戏
玉佩 ref 系统(新机制):
- ai_video.md +rule 4b【重要复用道具 image-first ref 图 pipeline】:跨≥2镜复用的信物/法器/标志道具立独立 prop 卡(props/{道具名}/)+Seedream ref 图 prompt,每 shot 参考行加 {道具名}=> handle+byte-identical 复用锁定描述符(与角色 ref 同机制);升级后角色 bible 标志道具行指向 prop 卡
- 新建 2_世界观人设/props/玉佩/玉佩.md:锁定描述符(不规则断裂半块古玉/断口粗糙/温润泛淡青/古朴隐纹/旧红绳系挂/非圆铜钱)+藏锋负向锁定(零光透温不发光)+Seedream ref 图 prompt(纯道具白灰底特写,首行 handle 玉佩)+用法+出场登记(EP2 shot9/10/11、EP3 S5-6/S9)
- EP2 shot09/10/11 参考行追加 玉佩=> handle;c1 bible 标志道具行加 prop 卡指针
- 待办(用户侧):用 prop 卡 prompt 生成 玉佩.png → 重渲 EP2 玉佩三镜(附 ref)统一样子
EP3 破庙台词 fix(script+dialogue 同步):
- S8 "怪了…竟顺成这样?"(困惑·错,系统早告知武神躯) → "这就是武神躯…换作从前这副废丹田想都不敢想"(感叹武神躯之能)
- S9 "这力量、这玉佩都来得蹊跷"(错,武神躯系统给的不蹊跷) → "武神躯是系统给的,这玉佩的来历却到现在都摸不透"(疑只落玉佩)
- S10 "也找条往上走的路"(对仗金句+比喻出戏) → "找个宗门落脚,安心练功"(具体大白话)
台词大师 D1 加严(反馈→进化):+【禁对仗金句/文艺比喻】具体反例("找条往上走的路"=排比+比喻=编剧漂亮话非真人念头;OS 尤要 raw 具体不抽象)
QC:S8/S9/S10 节奏≤4 全过;连贯一致(武神躯系统给/玉佩谜/不演受阻)

## EP2 玉佩三镜统一描述符 + props/ 类目登记 + EP3 S9 静默 — 2026-06-20
Source: 用户①要重渲 EP2 玉佩视频、把三镜内联描述统一成 prop 卡锁定符 ②问玉佩 md 该不该在 2_世界观人设 跟人物/场景并列做"重要物件"栏目 ③S9 重复强调玉佩来历摸不透、多余
EP2 玉佩三镜统一(为重渲):
- shot09/10/11 玉佩视觉描述符全部统一为 prop 卡锁定核心串(不规则断裂半块古玉·断口粗糙·温润半透泛淡青·古朴隐纹断口处戛然而止·褪色发白旧红绳系挂·绝非圆铜钱/硬币/圆玉牌);玉佩负面词补齐(灵光/完整玉牌玉璧等);shot10 原无玉佩描述符/负面词→补全
props/ 类目正式登记(用户提议·已有):
- 玉佩卡确认在 2_世界观人设/props/玉佩/玉佩.md=与 characters/scenes 并列的"重要物件"栏目(英文类目+中文物件子folder)
- 登记进结构文档:CLAUDE.md stage2 行 + 全流程编排 SKILL.md(表+结构块) + BLUEPRINT.md 均加 props/
EP3 破庙 S9 改静默:
- 去掉 "武神躯是系统给的,这玉佩来历摸不透…变强要紧"(玉佩来历 S5-6 已埋·重复多余)→S9 改无台词静默拍(收功变强实感+看玉佩一眼视觉钩);S10 画面去重复的"拢回玉佩"(并入S9);三类清点/钩尾同步
QC:EP3 连贯顺、OS 密度降(去冗余)、玉佩钩改视觉化;EP2 三镜描述符一致待重渲

## 玉佩形制改为"完整玉的一半+拼合接口"(非摔碎) — 2026-06-20
Source: 用户「玉佩不要破碎，而是一个完整玉佩的一半形状，有一个接口」
设计改：从"不规则断裂/断口粗糙的摔碎残片"→"一整块古玉本就做成两半相合的形制·本体是规整的一半·相合侧带平整拼合接口(子母榫槽+对位小孔、可与另一半严丝合缝扣成整块)·古朴隐纹延伸至接口·非摔碎残片"。更贴双宝/合一主题(半玉寻另一半)。
统一落点：props/玉佩/玉佩.md(锁定符+Seedream prompt+负向全改)、c1 bible(标志道具+turntable道具两处)、EP2 shot09/10/11 玉佩描述符全改("半块古玉"→"半枚古玉")
核查：concept/ep01/world 的"断裂/破碎"均为丹田碎(保留)、无玉佩破碎表述
待办(用户侧)：用更新后 prop prompt 生成 玉佩.png(带接口的一半玉)再重渲 EP2 玉佩三镜

## 玉佩仙侠化设计(造型+花纹+细节) — 2026-06-20
Source: 用户「玉佩的形状和花纹要比较仙侠一点不要中规中矩、要有更多细节」
设计升级(保留:一半带接口/不破碎/不发光藏锋):
- 造型: 半弯卷云/残月状(非规整几何半块)、边缘随云纹起伏
- 花纹: 正面浅浮雕蟠曲螭龙(无角小龙·龙鳞/龙爪/龙须)缠绕翻卷流云纹 + 古朴星点 + 摩挲浅淡古篆符箓；龙身纹样在接口处中断、与另一半续成整条龙整句符(强化双宝合一)
- 接口: 顺纹起伏的契合边带子母榫卯+对位小孔(似龙睛/星位)
- 玉质: 温润半透泛淡青、玉内蕴似云气流动/水线游走的天然冰纹(天然非发光)、岁月包浆
- 藏锋: 仙气靠雕工+玉质、不靠光；负向加 玉内发光/素面光板/中规中矩
落点: props/玉佩/玉佩.md(锁定描述符+Seedream prompt 主体/细节/负向 全面重写为螭龙云纹版)、c1 bible(标志道具+turntable道具)、EP2 shot09/10/11(描述符升级+负面词加 素面光板/玉内发光；shot10 补全玉佩负面词)
待办(用户侧): 用新 prop prompt 生成 玉佩.png(螭龙云纹半枚仙玉)再重渲 EP2 三镜

## EP3 破庙 stage 5/6 分镜+prompt 生成 — 2026-06-20
Source: 用户「生成 ep3 的 shot 还有细节」
新建场景卡: 2_世界观人设/scenes/破庙/破庙.md(单角度轻量·2 plate:bg1_庙内_神像前 夜雨 / bg2_庙门 天明·含 Seedream 底图 prompt+场景锁定+负向)
EP3 stage5/6 产物(5_6_分镜与prompt/episodes/ep03/):
- shotlist.md(10 镜/86s·先情绪后机位)
- shots/shot01-10/shotNN.md(各:小说原文+Shot context+五层视频prompt+台词配音)；独角戏裴知秋(PR-hero-01)+系统(SYS-gold-01·S7)+玉佩prop(S5/6/9)
- all_shot_prompts.md(全镜汇编只读快照)
镜序: S1入庙(孤寂)→S2坐定运功(沉静)→S3引暖流(凝神特写)→S4病躯渐稳(体感)→S5玉佩共鸣(异动惊)→S6掏玉佩细看(疑·第二宝hook)→S7系统入武人一级(系统流爽点)→S8顺得反常感叹(爽点)→S9收功看玉佩(静默无台词钩)→S10天明推门奔考核(冷暖对冲·启考核弧)
藏锋落地: 全程无金光瞳光、暖流靠气色微转、玉佩零光透温不发光、系统框diegetic UI非字幕、眼不发光
QC(stage5/6 五道+格式契约+连贯): blocker 清零——站位朝向(朝向固定·OS视线写死)/运镜(情绪先行·景别节奏·轴线一致)/动作(beats铺满·无干站)/光线(冷调一致·S10冷暖对冲·零hex)/时长节奏(OS字数÷时长≤4.5)/格式契约(五层齐·无字幕·锁定串byte-identical·voice_id·9:16/8-10s)
待办(用户侧): 生成场景底图 破庙_bg1/bg2.png + 玉佩.png(螭龙云纹) → image-to-video 出 10 镜

## 家族称谓+身份统一：同母嫡亲一家(大公子/二公子/镇北王夫人) — 2026-06-20
Source: 用户「人物卡细节不准确——主角是王府大公子、父亲镇北王、母亲镇北王夫人、弟弟王府二公子」+ 确认「同母嫡亲一家」
canon 改：主角裴知秋＝镇北王与镇北王夫人沈婉的嫡长子(大公子)、裴昭＝同母嫡次子(二公子)；废弃"庶出/庶长子/母妃/幼子"。亲爹亲娘都偏爱有天赋的二公子、冷落废了丹田的亲长子(连亲生父母都嫌弃·至暗底色更狠)
统一替换(全项目·语义改非盲替)：庶长子/庶出长子→嫡长子；庶子→废人长子/大公子；幼子→二公子；母妃/王妃→镇北王夫人(角色层)/母亲(台词层)；同父异母(或嫡出)→同母嫡出
落点：c1(定位+表层+服装注+关键场景)、c3、c4(标题+关系句+turntable+intro_card副身份"镇北王府二公子")、c5(标题+定位+全卡)、world(§2.1家族结构+§四新增家族结构锁定行+§1.1/1.3)、style_guide、arc(裴家线)、concept、镇北王府正厅场景档、EP1(script/dialogue/shot03/all_shot_prompts 母妃沈婉→镇北王夫人沈婉、别怪母妃→别怪母亲)、EP4(script/dialogue 父亲母亲、天才二公子)
⚠ EP1 已渲染连带(待用户决定是否重做)：
- shot03 沈婉口型台词"别怪母妃…"→"别怪母亲…"(配音层改、已渲音频stale·若要一致须重配该句)
- 裴昭出场字卡若已烧"镇北王幼子"→应重烧"镇北王府二公子"(intro_card.md 已更新)
- EP1 其余台词未提称谓(裴昭/裴霆称呼无"庶/母妃")、画面无影响
核对：grep 全项目 庶/母妃/幼子/同父异母 = 0 残留

## 人物卡(intro card)修复：description + 导入路由 + button 路径 — 2026-06-20
Source: 用户 5 条人物卡反馈
#1 description(副身份)修正：c1 镇北王府废少→大公子、c5 镇北王妃→镇北王夫人(c3 镇北王/c4 镇北王府二公子 已对)
#3+#4 导入撞名 + button 找不到图(同一根因·零代码内容修)：
- 根因：intro_card.md 首行"裴昭 · 出场名牌卡"里 名牌 marker 在第8-9字、即梦截断文件名后 marker 不触发→downloads__writer line181 不识别为 intro_card→当普通角色图、被 renamer 规范化成跟主角 ref 图撞名；burn(intro_card__writer _find_card_in_drama)又必须找 characters/cN_角色/intro_card.png→找不到报 IntroCardImageMissingError
- 修：4 张 intro_card.md 首行路由 token 改 `{角色}名牌卡`——角色名(c4 _classify 按子串匹配)+名牌 marker 双双在最前、抗截断→导入必归位 characters/cN_角色/intro_card.png(自己的名、不撞 ref);button 即能找到
- 用户侧：用更新后 prompt 重出/重导人物卡图即可
#2 待定(Seedance 渲中文字不准·需用户拍板)：现 intro_card.md 让 Seedance 把中文字烧进图→AI 渲中文不可靠出错别字、与"字卡后期烧入"契约矛盾。正解＝Seedance 只出空名牌框(零字)、webapp burn 用 PIL/真字体后期烧 主名+副身份(从 intro_cards.md 读)→100%准。属 webapp feature 改动(改 IntroCard valueobject+parse+burner+bundle 中文字体, 且烫金书法→需 PIL 描金渲染)，待用户确认是否实施

## EP3 实战反馈批次（看片逐镜）+ 三类生成 bug skill 进化 — 2026-06-21
Source: 用户看 EP3 渲染片逐镜反馈（S3 措辞、shot5 玉佩凭空现、shot7 入境单薄、shot9 注释烧字幕、shot10 时间跳变、玉佩自动挂脖）

EP3 产物修改（四面同步：shotNN.md / script.md / dialogue.md / all_shot_prompts.md）：
- S3 台词去"奇了"（突兀）：「…沉进丹田……那股力竟真顺着我的意念…」；语速备注同步去"奇了轻起"
- shot5 玉佩凭空出现修正：删 `玉佩=>` ref + 删完整外观描述符；玉佩本镜藏衣内不外露不掏出（取出动作连贯交给 shot6），画面看不见玉佩本体、只靠胸口体感+皮下暖流表现
- shot7 入境刻画加厚 + 系统破例恭喜：主角破境表演加厚（病气褪去/眼底回光/脊背挺直/眼眶一热）；系统改为冷 readout「丹田重塑，经脉贯通。已入武人一级。」+ **破例一句恭喜**「废了丹田，也能重上武道。恭喜，宿主。」（配音拆三块：系统冷 readout / 系统破例恭喜 / 主角 OS 精简）
- shot9 字幕泄漏修正：`台词:` 字段「（本镜无台词…环境音…）」prose 被烧成字幕 → 改 `台词: 无`，环境音注释移到码块外
- shot10 时间跳变修正（门一关一开天就亮太假）：改为已是次日清晨的 establishing 起手 + S9→S10 叠化时间流逝转场，天亮发生在时间省略里、非推门触发；S9 镜尾压回深夜暗色（不提前透晨光）

人设进化：
- c2 系统人设开"重大节点破例口子"（characters/c2_系统）：冰冷零情绪仍是日常基线，唯破境/觉醒/入境等重大成长节点破例多给刻度 readout + 一句克制恭喜/撑腰（同 voice_id 不换音色、点到为止不滥用、不变话痨）；EP1/EP2 冷调仍有效

skill/ref 进化（三类生成 bug → surgical 补丁）：
- Pattern A 道具状态须动作驱动（shot5 玉佩凭空现 / 玉佩自动挂脖无挂的动作）：
  · agent_refs/project/ai_video.md rule 4b 新增「道具可见性/连续性铁律」(ref/描述符↔上画可见双向绑定 + 状态改变须动作驱动)
  · ai_videos__动作表演 新增 A9（道具状态改变须 motivating 动作 beat，禁凭空出现/自动佩戴）
  · ai_videos__格式契约 新增 K20（道具 ref/描述符↔上画可见 双向一致，该藏却带 ref/描述符=blocker）
- Pattern B 非台词文本禁进生成块（shot9 注释烧字幕）：
  · ai_videos__格式契约 新增 K21（台词字段只放台词正文或"无"，舞台提示/环境音移出码块）
  · ai_video.md「不烧字幕」rule 段补静默镜 `台词:无` + 非台词文本移出码块
- Pattern C 大时间跨度禁瞬切（shot10 关门开门天就亮）：
  · ai_videos__剧情连贯 新增 N5（大时间跨度禁绑单一连续动作瞬切，须叠化/时间流逝 establishing/空镜过渡，后镜开场即新时段）

Auto-updated:
- ai_videos/wushen_juexing/4_剧本/episodes/ep03/{script.md,dialogue.md}
- ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep03/shots/{shot03,shot05,shot07,shot09,shot10}/shotNN.md
- ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep03/all_shot_prompts.md
- ai_videos/wushen_juexing/2_世界观人设/characters/c2_系统/c2_系统.md
- .claude/agent_refs/project/ai_video.md（rule 4b 道具铁律 + 不烧字幕段静默镜）
- .claude/skills/ai_videos__动作表演/SKILL.md（A9）
- .claude/skills/ai_videos__格式契约/SKILL.md（K20/K21）
- .claude/skills/ai_videos__剧情连贯/SKILL.md（N5）

待用户侧：上述改动的 shot 需用新 prompt 重出片（shot5/7/9/10 + S3 配音）；shot7 系统两行配音须分别生成。

## Follow-up 016 — 2026-06-21 00:00:00
Source: user_input/follow_ups/016-20260621-000000-jingjieti-keduan-wushen-wuhuang.md
Summary: EP4 境界梯科普刻意不提武神（常人不知）+ 渲染武皇遥不可及 + 裴霆 S7 自陈卡武王境、望裴昭登武皇。

Auto-updated:
- 2_世界观人设/world.md — §1.1 阶七加「公开科普只点到武皇、不提武神」夹注；§1.5④ 改为「点到武皇为止·武神不揭·裴霆武王/武皇期望坐实」
- 4_剧本/episodes/ep04/script.md — S2 科普去武神、武皇渲成几百年一出；S7 加裴霆台词（9s→12s）；总时长 98s→101s；铺垫锚/三类台词清点/header 同步
- 4_剧本/episodes/ep04/dialogue.md — S2 改写；S7 加裴霆台词（12s）；声口提示裴霆条更新
- 3_大纲/arc_outline.md — 弧二概要 + EP4 细纲科普口径改为「武人→武皇·武神不揭」

No conflicts found in: characters/（c3/c4/c5 不含境界科普）, EP1–EP3 产物（无考核科普）, style_guide.md

## Follow-up 017 — 2026-06-21 00:01:00
Source: user_input/follow_ups/017-20260621-000100-zizhi-qidang-feixiapin.md
Summary: 资质体系 5 档→7 档（废/下/中/上/玄/王/帝）；主角=帝品(残缺)、裴昭=上品、云骁=王品。

Auto-updated:
- 2_世界观人设/world.md — §1.5① 表扩为七档（新增玄/王/帝行·废品替无/废）；§1.5② 核心档改「王品/帝品」；§1.5③ 残缺资质改「读数直冲帝品」；§1.5 标题 EP3→考核弧EP4；§四 canon 云骁极品→王品
- 4_剧本/episodes/ep04/script.md — S3 执事台词点出全七品；S5「没资质」→「废品」；header/铺垫锚/留后 极品→帝品、五档→七档
- 4_剧本/episodes/ep04/dialogue.md — S3/S5 同步；S5 小标题改
- 3_大纲/arc_outline.md — 资质五档→七档；主角极品/绝顶→帝品（弧2.1/EP9×2）；云骁极品→王品；EP4 细纲档名口径同步

待用户侧/留意：裴昭=上品、云骁=王品 为本次映射决策（旧「极品」已非档名，须重定），如需调整请告知；EP8/EP9 细化时复用此映射。

No conflicts found in: characters/（c1/c4 不含资质档名）, EP1–EP3 产物, style_guide.md

## EP3 玉佩跨镜状态轴不一致 + 跨镜道具/服装一致性归属 — 2026-06-21
Source: 用户「shot2 玉佩在胸口、shot3 又在衣服里，不 consistent；shot2 不用展示玉佩；跨镜物品/衣服 consistency 归哪个 skill、如何避免」

EP3 修正：
- shot2 删 `玉佩=>` ref（玉佩全程藏衣内、只在 shot6 掏出；shot2 带 ref 导致玉佩被画在胸口外，与 shot3 藏衣内打架）。情节/动作只按位置点名提玉佩、无外观描述符（符合 K20）。同步 shot02.md + all_shot_prompts.md
- 全 ep3 扫 玉佩 ref：仅 shot6(掏出)/shot9(摊掌看) 真上画保留 ref，其余镜不带（shot2 本轮修、shot5 上轮已修）
- all_shot_prompts.md 头部新增「玉佩可见性时间轴」作单一事实源（shot1-10 逐镜 藏/露 状态 + 状态改变动作点）

跨镜一致性归属（回答用户）：
- 衣服外观一致 → 格式契约（角色锁定描述符 byte-identical K8 + K18 跨景别造型一致）
- 衣服状态一致(披风/束发/血污，靠动作改) → 剧情连贯(整集) + 全剧序列(跨集)
- 道具外观一致 → prop 卡+ref图+锁定描述符(ai_video.md 4b)，机械校验 格式契约
- 道具可见状态一致：单镜 ref↔可见=格式契约 K20、状态改变须动作=动作表演 A9；**跨镜状态轴=剧情连贯 N6(本轮新增)**

skill 进化：
- ai_videos__剧情连贯 新增 N6（跨镜道具/服装状态轴一致：整集把每个道具/服装态排成时间轴通查相邻镜，状态改变须动作驱动；建议多变集在 all_shot_prompts/shotlist 记可见性时间轴作单一事实源）

Auto-updated:
- ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep03/shots/shot02/shot02.md
- ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep03/all_shot_prompts.md（shot02 + 头部玉佩时间轴）
- .claude/skills/ai_videos__剧情连贯/SKILL.md（N6）

待用户侧：shot2 用新 prompt 重出片（去玉佩 ref 后玉佩不再画在胸口外）。

## Follow-up 018 — 2026-06-21 00:02:00
Source: 用户反馈（EP4 S3 执事台词不白话、拗口）
Summary: EP4 S3 测资执事台词由一句塞满改写为三句白话（按石/七品名/分档），S3 9s→13s，总时长 101s→105s。

Auto-updated:
- 4_剧本/episodes/ep04/script.md — S3 台词三句化 + 时长 9s→13s；时长合计 101s→105s
- 4_剧本/episodes/ep04/dialogue.md — S3 同步（13s）

教训（可选进化·待用户确认）：规则/科普类长台词一句塞满多条信息易拗口，拆成「做什么/有哪些/怎么分」短句更白话——可固化进 ai_videos__白话大师 / 台词大师。

## Follow-up 019 — 2026-06-21 00:03:00
Source: user_input/follow_ups/019-20260621-000300-ep4-zongmen-paiwei-xiaozong-mingming.md
Summary: EP4 一批细化——执事台词三句白话化 + 玄品档说详细 + 菜鸡少年点明所入宗门(青松派/铁剑门) + 新增「宗门排位」围观 shot；台词大师固化 D10。EP4 11镜/98s→12镜/117s。

Auto-updated:
- 4_剧本/episodes/ep04/script.md — S3(原)执事台词三句白话化+玄品详化；S4/S5 点明青松派/铁剑门；新增 S3 宗门排位围观 shot，原 S3–S11 后移 S4–S12；时长合计→117s、header→117s/12镜；三类台词清点/世界观铺垫锚/钩尾 shot 号全部后移
- 4_剧本/episodes/ep04/dialogue.md — 同步：新增 S3、菜鸡少年/执事点明小宗、全段 renumber、声口提示裴霆 S7/S8→S8/S9
- 2_世界观人设/world.md — §2.2 顶宗加剑道/御法分工 + 新增万象门(一流)/青松派/铁剑门(中小) + 宗门实力排位 bullet；§四 canon 加「宗门实力排位」行
- 3_大纲/arc_outline.md — EP4 细纲 98s/11镜→117s/12镜；钩尾 S10–S11→S11–S12
- .claude/skills/ai_videos__台词大师/SKILL.md — 新增 D10「长串规则/科普台词拆短句」+ frontmatter/工作流 D1–D9→D1–D10 + 范本表加 EP4 拆句例（common-level 进化）

待用户拍板（未决）：① 裴昭=上品、云骁=王品 映射；② S10 主角 OS 两版打架（script「找个能安身的地方就够了」 vs dialogue「轮到我，还早」）择一对齐。

No conflicts found in: characters/, EP1–EP3 产物, style_guide.md, 5_6 分镜(ep04 暂无 shotNN)

## EP3 跨镜特效态轴(暖金流光重起) + shot2 彻底清除玉佩 — 2026-06-21
Source: 用户「shot3 经脉暖金流光已流转、shot4 又从无到有重跑一遍 ramp，需 consistency，且同理 apply 之后所有 shot」+「shot2 手里怎么还有玉佩，这个 shot 不要出现玉佩」

EP3 修正：
- shot4：开场即承接 shot3 已流转的皮下暖金流光、继续走四肢百骸，不再 0-3s 无流光→3-6s 重起 ramp（动作 + 光线 改"承 shot3 延续·稳定不熄不重起"）
- shot6：补"皮下暖金流光仍极淡未熄(承 shot3-5·尚未收功)"——杜绝 shot5 有→shot6 无→shot7 气劲 的闪烁；收功熄灭只发生在 shot7
- shot2：上轮只删了玉佩 ref，但情节/动作/光线仍点名"古玉/玉佩位置"会 cue 模型 → 本轮彻底清除全部玉佩字样，按胸口改为纯 EP2 余悸手势(手中与画面均无玉佩)，负面词加"画面出现玉佩/手持玉佩/玉佩入画/胸前挂玉佩"
- all_shot_prompts.md 头部新增「武神躯暖金流光时间轴」单一事实源(shot1/2 无→shot3 起 ramp→shot4-6 承接延续/极淡→shot7 收功熄灭→shot8-10 无；只 shot3 可演从无到有)；玉佩时间轴 shot2 改为"完全不出现"

skill 进化：
- ai_videos__剧情连贯 N6 从「道具/服装状态轴」扩为「跨镜状态轴——道具/服装/特效能量态/伤势」：新增 (iii) 特效/能量态(运功流光/灵气/破境气劲/法宝光/觉醒异象)——后镜禁把前镜已建立的效果从零重演 ramp、该延续不得凭空消失；明确"效果只 ramp 一次(首次出现镜)，后续镜承接已建立态、按轴单调变化(铺展/增强/减弱/收束)"；(iv) 伤势态。引 EP3 头部两条时间轴作范例

Auto-updated:
- ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep03/shots/{shot02,shot04,shot06}/shotNN.md
- ai_videos/wushen_juexing/5_6_分镜与prompt/episodes/ep03/all_shot_prompts.md（shot02/04/06 + 头部暖金流光时间轴 + 玉佩时间轴 shot2）
- .claude/skills/ai_videos__剧情连贯/SKILL.md（N6 扩展到特效/能量态/伤势）

待用户侧：shot2/4/6 用新 prompt 重出片（shot2 不再有玉佩；shot4/6 流光承接不重起）。

## Follow-up 020 — 2026-06-21 00:04:00
Source: 用户反馈（EP4 S2「了不起也就武王境」逻辑反了——武王本就是镇守一方的强者）
Summary: EP4 S2 围观乙台词由「贬低武王」改为「赞叹武王到场」，对齐 world §1.1 武王=镇守一方的实力坐标。

Auto-updated:
- 4_剧本/episodes/ep04/script.md — S2 乙台词改「武王就已是镇守一方的大人物，今天竟来了好几位！」；情绪列加「赞武王到场」
- 4_剧本/episodes/ep04/dialogue.md — S2 同步 + 注释更新

连贯：与 S8 镇北王(武王境)亲自到场互相呼应，强化考核分量；S2 仍 10s、总时长不变 117s。

教训（可选进化）：台词对设定内事物的评价/语气须与 world 实力坐标一致——别把设定里"很强"的境界/物件说成"也就/不过"，否则逻辑反。可固化进台词大师（D2 因果 / 设定一致性）。

## Follow-up 021 — 2026-06-21 00:05:00
Source: 用户连续反馈（台词大师 review EP4：S2武王逻辑/玄品拆句加圣子/裴霆困死改措辞/主角接话换句/裴霆人设不落井下石/删退人群镜/前置入城游览开场）
Summary: EP4 一轮台词大师 review + 结构重排：境界逻辑修正、资质高阶档拆出圣子镜、裴霆措辞+人设修正、删藏锋退人群镜、新增入城游览开场(含说书支线埋妖患)。EP4 12镜/116s → 16镜/152s（偏长·待拆）。

Auto-updated:
- 4_剧本/episodes/ep04/script.md — 整体重写：①前置入城开场 S1–S4（城门/主街市集/街角说书支线埋妖患/人群涌动跟去）；②测资由1镜拆为 S8基础分档+S9高阶圣子（玄品以上"天之骄子/进核心/资源名师任挑/兴许成一宗圣子"两句）；③删原退人群·藏锋镜；④裴霆"困死在武王境"→"卡在武王境大半辈子"；⑤裴昭交锋镜：主角"用不着你管"→两句"用不着你操心。你这点嘴皮子，改不了什么"、裴霆"别理这种人，丢份"→"昭儿，当这么多人，别丢了王府的脸。走"(不落井下石)；⑥S2武王"了不起也就武王"→"武王就已是镇守一方的大人物，今天竟来了好几位"(上一轮)；⑦S7宗门排位精简节奏；全表 renumber S1–S16、时长合计152s、header/铺垫锚/三类台词清点/承接钩尾/待建卡同步；附「拆集建议」。
- 4_剧本/episodes/ep04/dialogue.md — 整体重写同步：新增 S1–S4 + S5–S16 renumber + 各句注释 + 声口提示补说书先生/路人、裴霆人设钉。
- 2_世界观人设/characters/c3_裴霆/c3_裴霆.md — §性格加「人设边界(不落井下石·冷待源于无法习武而非厌恶)」+ 说话风格禁忌补「不当众讥讽废长子」。
- 2_世界观人设/world.md — §2.1 裴霆条加人设钉；§1.5② 核心/亲传补「宗门圣子」。
- 3_大纲/arc_outline.md — EP4 116s/12镜→152s/16镜·偏长待拆；钩尾 S11–S12→S15–S16 + 拆集预案。
- .claude/skills/ai_videos__台词大师/SKILL.md — （本轮调用台词大师 review；D10 已于 019 固化）。

待用户拍板：① **EP4 偏长(152s/16镜)是否拆集**（建议：S1–S12 留 EP4、S13–S16 并入 EP5 群英录开场）；② 裴昭=上品、云骁=王品 映射是否 OK。

No conflicts found in: c4/c5 卡, EP1–EP3 产物, style_guide.md, 5_6 分镜(ep04 暂无 shotNN)

## Follow-up 022 — 2026-06-21 00:06:00
Source: 用户拍板（EP4 拆两集；裴昭资质提到玄品）
Summary: EP4(152s/16镜) 拆为 EP4(S1–S13·入城+考核铺垫·结家人到场悬念钩·123s) + 新建 EP5(家人交锋3镜+群英录待细化)；裴昭资质 上品→玄品（云骁仍王品·主角帝品）。EP6–EP9 编号不变。

Auto-updated:
- 4_剧本/episodes/ep04/script.md — trim 到 S1–S13（删原 S14–S16 交锋/前向钩/收束）；header/合计(123s)/三类台词清点/铺垫锚/钩尾(改为家人到场悬念钩)/留后/待建卡 同步；裴昭 上品→玄品；删凌虚子(移 EP5)
- 4_剧本/episodes/ep04/dialogue.md — 同步 trim 到 S1–S13 + 声口提示去裴昭(移EP5)
- 4_剧本/episodes/ep05/script.md — 新建：S1–S3 定稿（家人交锋+前向钩+凌虚子一瞥+收束·由原EP4拆出）+ S4 群英录待细化；承 EP4 S13 钩
- 4_剧本/episodes/ep05/dialogue.md — 新建：S1–S3 台词 + 声口提示（裴昭刻薄归此、群英段待写）
- 3_大纲/arc_outline.md — 第二幕概要 裴昭上品→玄品；EP4 条改 123s/13镜·家人到场钩；新增 EP5(家人交锋+群英录) 条；EP6–EP9 编号不变说明；episode 架构列表同步
- 2_世界观人设/world.md — §四 新增「关键角色资质档」行（主角帝品残缺＞云骁王品＞裴昭玄品）

待用户：EP5 群英录段（云骁/百里寒/江晚/女天骄登场）待推进到该集再细化（敏捷）。

No conflicts found in: c3/c4/c5 卡, EP1–EP3 产物, style_guide.md, 5_6 分镜(ep04/ep05 暂无 shotNN)

## Follow-up 023 — 2026-06-21 11:55:00
Source: 用户「ep4 还行，帮我生成 shot 的 detail」（EP4 推进 stage4 → stage5/6）
Summary: EP4(S1–S13·123s) 进 stage5/6——新建 2 张场景卡 + 13 个 canonical shotNN.md（分镜运镜 + 五层标准化 prompt 合一）+ all_shot_prompts.md 汇编 + intro_cards.md。4 个并行 worker 分段铺镜（S1–4/S5–8/S9–11/S12–13），全部 byte-identical 锁定串。已过复验（格式契约/锁定串一致/运镜跨镜/光线跨镜/站位朝向/测资灵石非体放/眼不发光）。

Auto-updated / 新增:
- 2_世界观人设/scenes/镇主街/镇主街.md — 新建场景卡（白日入城主街·城门/主街市集/街角茶棚 3 plate·与 EP2 暮夜集市长街不复用）
- 2_世界观人设/scenes/镇演武场/镇演武场.md — 新建场景卡（白日露天考核大场·场口/全景旗台/测资灵石台/太虚冷台/人群骚动 5 plate·测资灵石发光非体放铁律）
- 5_6_分镜与prompt/episodes/ep04/shots/shot01..13/shotNN.md — 新建 13 镜 canonical（YAML envelope + 小说原文 + Shot context + 视频 prompt 五层 + 台词配音）
- 5_6_分镜与prompt/episodes/ep04/all_shot_prompts.md — 新建 13 镜汇编（跨镜状态轴：藏锋/玉佩不出/测资灵石非体放/场景轴/境界梯/裴霆人设钉）
- 5_6_分镜与prompt/episodes/ep04/intro_cards.md — 新建字卡登记（裴霆/裴昭/沈婉 EP1 已发卡·本集不重发；群像不发卡）

复验结论（validation.pass · .audit events.jsonl）:
- 机械：零 hex / 无字幕污染 / 14 字段齐全 / 渲染样式 13 镜 byte-identical / 负向基线齐
- 锁定串：裴知秋(S1-5/S12-13)·裴霆/裴昭/沈婉(仅S13) 标签 byte-identical；场景串分区正确(主街S1-4/演武场S5-13)
- voice_id：递归角色一致（测资执事 KS-examiner-01 ×4 跨 worker 一致、裴知秋 PR-hero-01 ×7、裴霆 PT-patriarch-01）；群像一次性龙套(S12/S13 围观)通用音色无 id·可接受
- 铁律：测资灵石光只在石面/石心、不溢人身、非体放 + 负面词「不要 灵石光染亮人身」；全员无金光瞳光；S13 四角色站位朝向写死(裴霆面朝裴昭·主角隔人海 OS·防雷同脸)
- 运镜：景别节奏有起伏(全景铺陈→科普大场摇移→测资中近→S11快切对比→S12横移热冷切→S13全景→中→推近特写收悬念)；S6/S7 talking-head 已改镜头游走；白日暖白通透全集一致

待后续（stage5/6 渲染前）:
- 各场景 per-plate 图生图 prompt（镇主街 3 plate / 镇演武场 5 plate）+ 全局底图出图
- 角色/场景 ref 图实际渲染（turntable + plate）
- EP4 publish.md（平台元数据）

No conflicts found in: EP1–EP3 产物, world.md, style_guide.md, c1/c3/c4/c5 卡, EP5 剧本

## Follow-up 024 — 2026-06-21 12:05:00
Source: user_input/follow_ups/024-20260621-120500-style-game-cg.md（小镇场景更丰富 + 画面转 3D 游戏 CG 唯美大片·景观享受；镇主街+镇演武场都要）
Summary: 全剧视觉风格由「影视级真人写实 photorealism」改为 **3D 游戏 CG 唯美大片**（黑神话悟空/原神既视感·虚幻引擎次世代实时渲染·全局光照体积光·史诗级场景纵深）。用户经多选题明确选 B（知悉影响 style_guide + EP1–4 全部 + 后续，EP1–3 需重渲）。

Auto-updated:
- 2_世界观人设/style_guide.md — §1 渲染样式串整串换新（删「影视级真人写实/photorealism/工笔肤色/三庭五眼」，加「电影级CG大片质感·AAA游戏级唯美渲染·黑神话悟空与原神既视感·虚幻引擎次世代实时渲染·全局光照体积光·史诗级场景纵深·高精度次世代角色建模·唯美东方面孔·写实材质细腻不卡通」，保 9:16/浅景深/逆光描边/东方古风/反卡通/不烧字幕）+ §1 加 2026-06-21 风格切换注记 + §2 删负向「不要 CG渲染感/不要 3D游戏场景」改为「不要 低质感塑料感/不要 廉价手游画质」
- 全局 byte-identical 刷新渲染样式串：26 文件（style_guide + EP3 10镜 + EP4 13镜 + ep01/ep03/ep04 三汇编中走锁的）
- 2_世界观人设/scenes/镇主街/镇主街.md — 游戏CG大片重写：8字段描述符大幅丰富（高耸城门楼飞檐斗拱/极纵深青石长街/鳞次栉比唐宋楼阁/远山如黛/晨霭炊烟/丁达尔体积光）+ seed prompt 史诗化（广角纵深/体积光柱/全局光照/黑神话原神既视感）+ plate index 注 CG大片锚；≤30字一句话锁定保持稳定
- 2_世界观人设/scenes/镇演武场/镇演武场.md — 游戏CG大片重写：8字段丰富（极开阔大校场/旗台如林巨幅旗幡/顶宗鎏金台阁雕梁画栋/青玉测资灵石巨台/群山环抱天高云阔/体积光柱/人海如潮）+ seed prompt 史诗化 + 测资灵石温润半透不暴闪铁律重申；一句话锁定稳定
- 5_6_分镜与prompt/episodes/ep04/shots/shot01,02,05,06.md — 4 个核心景观镜增强 场景/镜头/光线：史诗构图（大全景仰拍/渺小行者衬恢弘）+ 丁达尔/体积光柱 + 远山如黛（S1入城/S2主街游览/S5抵场/S6演武场全景）
- 5_6_分镜与prompt/episodes/ep04/all_shot_prompts.md — 重新汇编（头部加风格说明 + 反映新串与景观增强）

复验: 13镜渲染样式新串 byte-identical 一致 / 旧串残留0 / 4景观镜增强标记齐 / 一句话场景锁定稳定（shot 仍 byte-identical 命中）/ 测资灵石非体放与藏锋无发光未被破坏。

待办（用户已知悉）:
- **EP01/EP02 为前锁定期 legacy**（各镜 bespoke 渲染串、已出片 mp4），未走 byte-identical 锁、本轮未自动换 → 待单独 restyle（保留各镜场景专属 token、基底换游戏CG串）+ 重渲
- EP03 文本已换新串但旧 mp4 待重渲；EP04 各场景 per-plate 图生图 prompt 出图（按新 CG 大片锚）
- EP05 剧本无渲染串（stage4），推进到 stage5/6 时直接用新串

No conflicts found in: world.md, arc_outline, c1/c3/c4/c5 卡（角色锁定描述符未动·仅渲染层风格变）, EP4 台词/剧情/站位（未动）

## Follow-up 025 — 2026-06-21 12:30:00
Source: user_input/follow_ups/025-20260621-123000-seedance-compliance.md（Seedance 提示场景提示词不符合平台规则·research+改 prompt）
Summary: Research（web + 项目 institutional）确认 Seedance/即梦 拒审两类主因：① **生成块点名商业游戏IP/引擎商标**（黑神话悟空/原神/虚幻引擎——字节因 Disney/奥特曼侵权函收紧 IP 拦截，web 实证）；② **暴力叙述触发词**（杀/刺/死伤/无数/血战/踏破，社区+实测确认）。全部换描述性/中性等价词。

Auto-updated:
- 2_世界观人设/style_guide.md — §1 渲染样式串去 IP/商标：黑神话悟空与原神既视感→3A级国风游戏唯美渲染+开放世界电影级既视感；虚幻引擎次世代实时渲染→次世代游戏引擎级实时渲染画质（+§1 切换注记同步去 IP 名）
- 全局 byte-identical 刷 IP-free 渲染串：26 文件（style_guide + EP3 10镜 + EP4 13镜 + 汇编）
- 2_世界观人设/scenes/{镇主街,镇演武场}.md — seed prompt [主体]/[风格] 行去 IP 名（→3A级国风游戏CG大片既视感/次世代游戏引擎级实时渲染）
- 5_6_分镜与prompt/episodes/ep04/shots/shot03.md — 软化妖患叙述：小说原文/情节/台词「踏破→连破、血战死伤无数→节节败退」+ 配音块同步；3-way 同步 dialogue.md/script.md S3
- 5_6_分镜与prompt/episodes/ep04/shots/shot09,10,11,13.md — 良性复合词软化（死寂→沉寂、血色正常→气色正常、暴闪→过曝乱闪、写死→固定）防误伤
- 5_6_分镜与prompt/episodes/ep04/all_shot_prompts.md — 重新汇编（加平台合规说明 + 反映清洗）
- .claude/agent_refs/project/ai_video.md — 2026-06-18 Seedance 审核 amendment 扩 §2b（游戏IP/引擎商标禁入+替换）+ §2c（暴力叙述词替换表）；流程级·所有 ai_video 项目

复验: IP残留0（含汇编注记）/ EP4渲染面暴力触发词残留0 / 13镜渲染串IP-free byte-identical一致 / shot03台词3-way同步 / 测资灵石非体放与藏锋未破。
注: script.md 铺垫锚/钩尾里「皇室选苗赴边疆杀妖」属 planning 剧情概念词、不送模型、保留。

No conflicts found in: world.md, arc_outline, c1/c3/c4/c5 卡, EP4 剧情/站位/运镜（仅措辞合规层改）

### 025 附记 — Seedance 创作提示采纳裁决（2026-06-21）
Seedance 给的两条「创作提示」（非合规修复）裁决：
- **「加古风摊贩细节」→ 采纳**：镇主街 seed prompt [主体]/[细节] 增补古风摊贩群（糖画担/馄饨汤摊/果蔬山货/卖花担/捏面人/字画卦摊/杂耍卖艺/货郎/铁匠铺火星/药铺晾药），堆「主角行于壮丽市井」景观纵深前景细节。
- **「换黄昏暖调」→ 不采纳（保持白日晨光暖调）**：① 黄昏不解决合规（拒因＝IP名·已修）；② S4 人潮涌动→S5 抵演武场是连续同一时刻、时辰不能跳，改黄昏须连演武场 S5–S13 一起改、否则穿帮；③ 撞 EP2 集市长街暮夜暖调、对比变弱。现有「晨光金辉+丁达尔体积光柱」已是暖金大片感、零代价。用户拍板保持白日。

## Follow-up 026 — 2026-06-21 12:45:00
Source: 用户「要保留仙侠剧的唯美，不用 100% 写实」
Summary: 风格再调一档——游戏 CG 大片底子上**仙侠唯美优先、不追 100% 写实**。强化唯美仙侠意境/仙气氤氲，去渲染串里「写实材质」过度写实信号，但保留「不卡通不塑料」避免廉价手游感。

Auto-updated:
- 2_世界观人设/style_guide.md — §1 渲染样式串：加「唯美仙侠意境 · 仙气氤氲」，「淡仙气薄雾」→「淡仙气薄雾氤氲」，「写实材质细腻不卡通」→「质感细腻唯美不卡通不塑料」；§1 注记补「仙侠唯美优先·不追求 100% 写实」
- 全局 byte-identical 刷新渲染串：26 文件（style_guide + EP3 10镜 + EP4 13镜 + 汇编）
- 2_世界观人设/scenes/{镇主街,镇演武场}.md — [风格] 行去「真实材质细腻不卡通」→「材质细腻唯美不卡通不塑料」+ 加唯美仙侠意境仙气氤氲

复验: 13镜新唯美仙侠串 byte-identical 一致 / 写实材质信号残留0 / 汇编同步。
说明: 仍保留次世代游戏引擎级实时渲染/全局光照体积光/史诗纵深（景观大片感）+ 不卡通不塑料（防廉价）；只是天平往仙侠唯美意境侧加重，去掉硬写实词。

## Follow-up 027 — 2026-06-21 13:00:00
Source: 用户「为什么镇主街下面没有 bg1/bg2 folder，跟其他 scene 不一致，这不是第一次，流程哪里有 issue？」
Summary: 诊断＝**反复复发的流程 bug**：新建场景卡时把 v3 canonical scene template item 9 的 folder-per-plate 写成「待建（stage5/6 渲染前）」、从未补建；stage5/6 worker 交付清单不含 plate；无 QC 扫 plate 存在性。shot 却已 `参考: 镇主街_bg1_城门=>` 引用不存在的 plate。三处叠加致 scene 缺 bg 子文件夹。

Auto-updated（实例修复）:
- 2_世界观人设/scenes/镇主街/{bg1_城门,bg2_主街市集,bg3_街角茶棚}/*.md — 补建 3 个 per-plate 图生图 prompt（image→image·首行路由 handle·纯背景无人物·新仙侠唯美CG串·IP-free·合规）
- 2_世界观人设/scenes/镇演武场/{bg1_场口,bg2_全景旗台,bg3_测资灵石台,bg4_太虚冷台,bg5_人群骚动}/*.md — 补建 5 个 per-plate prompt（测资灵石 plate 含温润半透不暴闪铁律）
- 2_世界观人设/scenes/{镇主街,镇演武场}.md — index 尾注「待建」→「已创建·PNG 待渲」

Auto-updated（流程根治·common-level）:
- .claude/skills/ai_videos__格式契约/SKILL.md — 加 **K23**：场景 plate folder 完整性（index 行 ↔ {plate}/{plate}.md ↔ shot 参考 handle 三方一致），缺即 blocker、当场补建
- .claude/agent_refs/project/ai_video.md — v3 scene template 加 **2026-06-21 amendment「folder-per-plate 当场建·禁待建」**：建卡同一步必须创建全部 plate .md、禁用「待建（stage5/6 渲染前）」推迟 prompt（PNG 可推迟、.md 不可）；挂 K23 gate

复验: EP4 全部 shot 的 8 个 plate handle ↔ plate 文件三方对齐 ✓；镇主街3/镇演武场5 plate 文件齐。
根因留档: 此 bug 复发是因 plate 创建既非 worker 显式交付项、又无 QC 把关、且卡模板用「待建」语言诱导推迟——K23 + amendment 同时堵住「漏建」与「待建话术」两个口子。

No conflicts found in: shot 内容, world.md, 其他 scene

## Follow-up 028 — 2026-06-21 13:20:00
Source: 用户「为什么街角茶棚导入失败？」
Summary: 诊断＝plate 命名违约定致 DownloadsImporter 路由失败。`bg3_街角茶棚` 漏切 `bg{N}_{方位}_{描述}` → 方位 token 变整坨"街角茶棚"⊃"街角"，撞 EP2 `集市长街/bg2_街角_摊位` 的方位"街角"→ importer 查到 2 候选无法消歧 → not_matched（downloads__writer.py `_match_plate_any_scene` 防误投返回 None）。其余 7 plate 同样违约定(单 blob 方位)、隐患同源。

Auto-updated（实例修复·重命名为合规三段式 + 方位互斥）:
- 2_世界观人设/scenes/镇主街/{bg1_城门→bg1_城门_入城, bg2_主街市集→bg2_主街_市集, bg3_街角茶棚→bg3_茶棚_说书}（folder+内层md+首行handle）
- 2_世界观人设/scenes/镇演武场/{bg1_场口→bg1_场口_入场, bg2_全景旗台→bg2_旗台_全景, bg3_测资灵石台→bg3_灵石台_测资, bg4_太虚冷台→bg4_冷台_太虚, bg5_人群骚动→bg5_人潮_让道}
- 同步 16 文件的 handle 引用：EP4 全 shot `参考:`/Shot context + 两场景卡 index/关键态 + all_shot_prompts
- 方位 token 选取避让全 drama 现有(街角/顺街/庙内/镇口/朝北…)：城门/主街/茶棚/场口/旗台/灵石台/冷台/人潮——模拟 importer 验证 8 个全唯一命中、撞车0

Auto-updated（流程根治·common-level）:
- .claude/skills/ai_videos__格式契约/SKILL.md — 加 **K23b**：plate 命名三段式 `bg{N}_{方位}_{描述}` + 方位 token 跨 drama 互斥（importer 路由约束），违即 blocker
- .claude/agent_refs/project/ai_video.md — 2026-06-21 folder-per-plate amendment 补 (d)：命名三段式 + 方位短且跨 drama 互斥 + 建卡前列已有方位避让

复验: 8 shot handle ↔ plate 三方对齐 ✓；8 方位 token 模拟 importer 全唯一命中、撞车0 ✓。茶棚现可正常导入。
根因链: K23(存在性) 堵了"漏建"，但没堵"命名错/方位撞车"——K23b 补上；两条 QC 合起来覆盖 plate 的"建没建 + 名对不对 + 能不能路由"。

No conflicts found in: shot 内容/剧情, 其他 scene, world.md

## Follow-up 029 — 2026-06-21 13:35:00
Source: 用户「又下载了5张图（镇演武场 plate）在 Downloads，确保都能正常导入」
Summary: 用真实 importer 逻辑模拟 5 个下载文件名（ElevenLabs gpt-image-2 渲的 bg1_场口/bg2_全景旗台/bg3_测资灵石台/bg4_太虚冷台/bg5_人群骚动）。发现 4/5 命中（新方位 token ⊂ 旧名仍路由）、**bg5 失败**——上一轮我把 bg5 方位「人群」→「人潮」，而下载文件名是旧「人群骚动」、不含「人潮」→ 0 命中 not_matched。

Auto-updated:
- 2_世界观人设/scenes/镇演武场/bg5_人潮_让道 → bg5_人群_让道（方位改回「人群」：既在已下载文件名内、又跨 drama 唯一）+ 同步 3 文件 handle（shots + 场景卡）
- .claude/agent_refs/project/ai_video.md — folder-per-plate amendment 补 (e)：改名兼容已渲图——新方位 token 应仍是旧名子串，否则已下载文件失配须重渲

复验: 5/5 模拟全部唯一命中（bg1→场口_入场 / bg2→旗台_全景 / bg3→灵石台_测资 / bg4→冷台_太虚 / bg5→人群_让道）；shot handle 三方对齐。

## Follow-up 030 — 2026-06-21 13:55:00
Source: 用户「整体风格不要太CG，要3A游戏的唯美细节、但还是真人剧」+「重新审视所有 scene/shot 确保」+「风格全部改为真人实拍、不要 CG 风格」
Summary: 风格最终定调＝**影视级真人实拍剧**（photorealism·真实皮肤毛孔与布料肌理·电影胶片质感），借 3A 游戏级唯美场景细节/光影/美术做画面质感参考、但**渲染风格真人实拍、不要 CG/游戏引擎渲染/3D建模感**。撤销 024 的「转 3D 游戏 CG 大片」。

Auto-updated:
- 2_世界观人设/style_guide.md — §1 渲染样式串改真人实拍（影视级真人实拍质感·photorealism·真实皮肤毛孔与布料肌理·电影胶片质感·3A游戏级唯美场景细节与美术·…去掉 CG大片/游戏引擎渲染/次世代建模）；§1 注记重写为 030 settled 定调（含历史 024→026→030）；§2 负向「反 CG/画质控制」组每镜必挂（不要 CG渲染感/游戏引擎画面感/3D建模感/游戏过场CG/卡通渲染…）
- 全局 byte-identical 刷真人实拍渲染串：26 文件（style_guide + EP3 10镜 + EP4 13镜 + 汇编）
- 2_世界观人设/scenes/{镇主街,镇演武场}.md + 全 11 plate（含 3 镇主街 + 8 镇演武场）— [风格]/seed/[主体]/header 去 CG 措辞（3D游戏CG/电影级CG/游戏引擎渲染/CG大片既视感 → 真人实拍·3A唯美场景细节）；seed 负向补 anti-CG
- 5_6_分镜与prompt/episodes/ep04/shots/shot01–13 — 渲染样式真人实拍化；场景行 3D游戏CG→真人实拍·3A唯美细节（S1/S2/S5）；负向 13/13 补「不要 CG渲染感/游戏引擎画面感/3D建模感」
- all_shot_prompts.md — 重聚合 + 真人实拍风格说明头

复验: 全 drama 零 CG 正向措辞（EP01–04 全 shot + 所有 scene + 角色卡）；汇编 13 镜真人实拍串一致、CG 残留 0；EP01/EP02 本就「影视级真人写实」（前锁定期 bespoke·从未 CG）。**全剧现统一真人实拍。**
说明: 3A 游戏「唯美细节」保留为画面质感/美术参考（场景细节·光影·体积光·史诗纵深），非渲染风格；渲染风格＝真人实拍 photorealism。

No conflicts found in: 剧情/台词/站位/运镜（仅渲染风格层改）, world.md, arc_outline

## Follow-up 031 — 2026-06-21 14:20:00
Source: 用户「shot11/shot13 平台审核未过」+「镇演武场像西方格斗场·要仙侠气质·测资灵石着重描写·按手要特效·要不要单独 prop」
Summary: ① 修 shot11/shot13 Seedance 拒审；② 镇演武场重写为中式仙侠（去斗兽场感）；③ 测资灵石建独立 prop 卡 + 七档按手特效。

A. 平台审核修复（shot11/shot13 + 同隐患 shot02/05/06/07/12）:
- shot11 拒因＝「像死了一般」（死亡意象·小说原文+情节）→「如顽石般沉寂无波」
- shot13 拒因＝「挎刀带剑」（武器·围观武者群像·命中 K17）→「各色粗布劲装的江湖习武之人」
- 全 EP4 武器词扫平（shot02 满街挎刀带剑→满街都是练家子·保武为尊世风去刀剑名词、shot05 兵器碰撞声→习武吆喝声、shot06/07/12/13 围观武者去挎刀带剑、挎刀新手/带剑老手→新手/老手）；shot02 台词 3-way 同步 dialogue/script
- 10 文件扫平、武器/死亡词残留 0

B. 镇演武场仙侠化重写（病灶＝「夯土大校场+四周高墙环列」斗兽场感）:
- 2_世界观人设/scenes/镇演武场/镇演武场.md — 视觉目标/锁定#2#3/seed[主体][细节]/主色 全改中式仙侠：青石演武法坛（非夯土斗兽场）+ 四周飞檐宗门阁楼朱漆牌坊旗幡环抱（中式楼阁·非环形看台高墙）+ 场心青玉测灵碑为焦点 + 远景云雾仙峰飞檐楼阁 + 仙气氤氲；主色 夯土黄褐→青石灰

C. 测资灵石 prop（决策：建·rule 4b 重要复用法器）:
- 2_世界观人设/props/测资灵石/测资灵石.md — 新建：青玉测灵碑锁定描述符（顶圆微拱·莲台座·测灵符箓云雷纹·静置不发光）+ 七档按手特效表（废=死寂/下=明灭微光/中=碑心柔光/上=灵气环碑/玄=成束/王=漩涡震颤/帝=冲天光柱异象/帝残=缺一块裂一道·主角EP9）+ 藏锋铁律（碑光不染人身·非体放）+ Seedream ref 图 prompt + 用法/出场登记

待续（prop 接线）: bg3_灵石台_测资 plate 补测灵碑细节；EP4 S8–S11 shot 补 `测资灵石=>` ref + re-paste 描述符 + 按手特效（S10 下品/S11 废+中）；测资灵石 ref 图实渲。

No conflicts found in: 其他 scene, world.md（七档特效本就 canon·prop 卡据其落地）

### 031 补完 — 测资灵石 prop 接线（2026-06-21）
- EP4 S8–S11 shot 已接线：`参考:` 加 `测资灵石=>` + 情节 re-paste 青玉测灵碑描述符（顶圆微拱·莲台青石座·测灵符箓云雷纹·温润半透苍青·静置不发光）；按手特效 S10（下品·碑面明灭微光）/ S11（废品·碑面沉寂无光 / 中品·碑心稳定柔光）已落地、碑光不染人身。S8/S9＝执事讲规则·碑静置不发光。
- 验证：S8–S11 参考行均含 `测资灵石=>` ✓（K20 ref↔可见双向一致）。
待续（实渲层）：`测资灵石.png` ref 图实渲（用 prop 卡 Seedream prompt）；bg3 plate 可选补测灵碑前景细节。

## Follow-up 032 — 2026-06-21 14:50:00
Source: 用户「确定所有 shot 的 CG 风格都修复了吗？之前生成视频太假、一点不真人」
Summary: 诚实复审发现 030 的真人实拍化**不彻底**——渲染串与各 shot `光线/场景` 字段仍散落大量致假词（审计：体积光97×/全局光照76×/游戏63×/工笔61×/3A游戏60×/唯美56×/史诗级63× 等，共~255处/55文件）。这些「游戏/全局光照/体积光/工笔/唯美/CG」是把模型推向游戏CG/插画/磨皮假脸的元凶。032 全量清除、纯真人实拍化。

Auto-updated:
- 2_世界观人设/style_guide.md — §1 渲染串彻底重写为纯真人影视实拍词汇：`真人实拍电影质感 · 影视剧实景拍摄 · photorealism 照片级写实 · 真人演员出演 · 真实皮肤纹理与毛孔 · 真实布料织物质感 · 电影胶片颗粒 · 自然光影 · 35mm电影镜头 · 浅景深 · 古装仙侠剧 · 古风实景置景考究丰富 · 东方古风 · 精致真实的古风服饰纹样 · 真实东方面孔 · 自然淡雾薄霭 · 真实质感不卡通不塑料不假 · 画面不烧任何字幕文字`；§1 注记重写为 032 纯真人实拍定调；§2 负向加「不要 游戏感/渲染感/磨皮/假脸/失真塑料感」
- 全局致假词扫平：55+9 文件——渲染串整串换；字段内 体积光柱→丁达尔天光/天光、全局光照→自然光影、3A游戏级唯美场景细节→考究丰富的实景置景细节、工笔质感→真实质感、唯美仙侠意境仙气氤氲→古装仙侠剧实拍质感、逆光描边→自然逆光、史诗级→恢弘、唯美→真实；EP1 王府场景 古风工笔→古风真人实拍
- 范围：EP3+EP4 全 shot + 所有 scenes（含 EP1 王府正厅 plate/卡）+ style_guide + 汇编
- all_shot_prompts.md 重写（修一处聚合重复 651→331 行）+ 真人实拍说明头

复审: 致假词（3A游戏/全局光照/体积光/工笔/唯美/史诗级/仙气氤氲）正向字段**零残留**；13 镜真人实拍串 byte-identical 一致。
教训（institutional·待固化 ai_video.md）：真人剧风格 prompt **禁词清单**＝游戏/3A游戏/游戏引擎/全局光照/体积光/次世代/CG/工笔/插画/磨皮/唯美渲染——这些即便配 photorealism 也会把输出拽向假/CG。真人实拍靠：真人演员/实景拍摄/35mm/真实皮肤毛孔/胶片颗粒/自然光 + 负向 不要游戏感/渲染感/磨皮/假脸。

No conflicts found in: 剧情/台词/站位（仅渲染风格词汇层）, world.md

## Follow-up 026 — 2026-06-21 13:00:00
Source: user_input/follow_ups/026-20260621-130000-ep3-shot7-system-voice-female-and-congrats-front.md
Summary: EP3 shot7 系统音「恭喜宿主」移到最前(去逗号)、删「废了丹田也能重上武道」、readout 丰富成 2 句；全剧系统音锁定女声。

Auto-updated:
- 5_6_分镜与prompt/episodes/ep03/shots/shot07/shot07.md — 系统 UI 文本/情节/动作/两条系统配音块重排(恭喜宿主置最前)+女声+readout 改 2 句；Summary 同步
- 5_6_分镜与prompt/episodes/ep03/all_shot_prompts.md — 同步 ep03 shot7 聚合(系统UI/情节/动作/配音行)
- 2_世界观人设/characters/c2_系统/c2_系统.md — 声线由「无性别中性」改「冰冷清冽女声」(全剧锁定女声·对齐上传 MP4)
- 5_6_分镜与prompt/episodes/ep01/shots/shot06/shot06.md、shot09/shot09.md、ep02/shots/shot02/shot02.md — 系统音色/情绪描述符改女声
- 5_6_分镜与prompt/episodes/ep01/all_shot_prompts.md — 同步 3 处系统音色/情绪改女声
- 4_剧本/episodes/ep03/{script.md,dialogue.md} — S7 系统两句重排(恭喜宿主置前)+女声+readout 2 句
- 4_剧本/episodes/ep02/dialogue.md — 系统声口改女声

No conflicts found in: shot07 小说原文(原著节选·保留原措辞不动)，其余 EP，站位/朝向/运镜/光线。

## Follow-up 033 — 2026-06-21 15:05:00
Source: 用户「EP4 为什么没有 shotlist」
Summary: 诊断＝EP4 stage5/6 生成时漏建 `shotlist.md`（EP1/EP2/EP3 都有·标准每集交付件）。与漏 plate folder 同源——stage5/6 每集交付清单无强制校验。

Auto-updated:
- 5_6_分镜与prompt/episodes/ep04/shotlist.md — 新建：13 镜清单总表（镜｜内容(情绪目的)｜出场角色｜景别+运动｜时长｜标记）+ 头部集信息（场景/角色/voice_id/prop/真人实拍贯穿/合规）+ 运镜锚（情绪→机位/景别节奏/测资灵石prop特效/主角藏锋主线/字卡）；反映当前状态（真人实拍·青玉测灵碑prop·中式仙侠演武场·武器词已去）
- .claude/skills/ai_videos__格式契约/SKILL.md — 加 K24：每集 stage5/6 交付件完整性（shotlist.md / all_shot_prompts.md / shots/ / intro_cards.md 对照同 drama 其它集自检·漏件 blocker）

复验: EP4 交付件现与 EP1–3 对齐（shotlist + all_shot_prompts + intro_cards + shots×13）。
根因链: 漏 plate folder(K23)→漏命名约定(K23b)→漏每集交付件(K24)，三条 QC 合起来覆盖 stage5/6 产物完整性。

No conflicts found in: shot 内容, 其它集

## Follow-up — 2026-06-21 EP3 shot07 prompt 简化 + 系统女声确认
Source: 用户口头指令（重写 shot7·系统声女声·简化 prompt·≤2000字）

Auto-updated:
- 5_6_分镜与prompt/episodes/ep03/shots/shot07/shot07.md — 视频 prompt 大幅精简（1199 字，去空白 1149，≤2000）；系统两句台词配音显式标注「女声·SYS-gold-01」；剧情/走位/动作时间轴/台词/时长(9s)全等，仅压缩冗余措辞；保留 load-bearing 契约（S7=收功熄灭点·暖金流光轴、diegetic 系统框非字幕、多声轨静音后期 mux、藏锋无瞳光）
- 5_6_分镜与prompt/episodes/ep03/all_shot_prompts.md — 同步 shot07 段为精简版 + 女声标注

复验（连贯·暖金流光轴 N6）: shot6(极淡未熄)→shot7(收功一记即收→归无)→shot8(承已收尽)，唯一熄灭点仍在 S7，轴不破；玉佩本集不上画，S7 不涉，无影响。

No conflicts found in: shot07 剧情内容, 其它镜, 其它集

## Follow-up 034 — 2026-06-21 16:00:00 — EP4 全面重构（放慢+丰富+真人实拍）
Source: 用户连续密集实测反馈（shot1→2/3→4 硬切·shot2台词↔画面不一致·shot6短发不像古人·shot9观众同脸·shot10台词归属错·shot11废品要有反应+中品谁要交涉·shot12太虚给老剑仙特写当结尾·shot13话太快拆镜·整体语速太快·"编剧/情节大师要改改"·整体review放慢丰富）
Summary: EP4 从 13 镜重构为 **15 镜 / 171s**（放慢节奏·正常语速≤3.5字/秒·超15s拆镜·丰富情节）。**结构改**：结尾从「家人到场悬念钩」改为「太虚冷台+老剑仙凌虚子特写·暗线hook」；**家人到场整段移 EP5 开场**。

Auto-updated（spec 重构）:
- 4_剧本/episodes/ep04/script.md — 重写为 15 镜表（入城4 + 科普3 + 测资段8放慢有反应 + 太虚老剑仙收尾）；原 S8 长台词拆 S8+S9；菜鸡测试拆 S11少年怔/S12招走/S13废品不甘/S14中品谁要交涉；S15 太虚+老剑仙凌虚子
- 4_剧本/episodes/ep04/dialogue.md — 同步 15 镜台词（废品汉子"再让我试一次"+中品"谁要→铁剑门要→道谢"等新交涉台词）
- 2_世界观人设/characters/c8_凌虚子/c8_凌虚子.md — 新建角色卡（老剑仙·扫地剑仙·拄秃竹扫帚·邋遢·暗线=EP2暗处目光·藏锋无剑气外放·S15特写首登发字卡·voice LX-swordsage-01）
- 5_6_分镜与prompt/episodes/ep04/shots/shot01..15 — **4 worker 并行重铺**（S1-4/S5-9/S10-13/S14-15）：真人实拍·中式仙侠·古装群像多样·过渡接点·台词↔画面一致·测灵碑特效·受测者反应·台词归属写死·正常语速（进行中）
- 5_6_分镜与prompt/episodes/ep05/_staging_from_ep04/ — 旧 shot13(家人到场)暂存待移 EP5

Auto-updated（流程·"大师改改"）:
- .claude/agent_refs/project/ai_video.md — 加「2026-06-21 真人古装仙侠剧出片铁律」7条（真人实拍零致假词/中式非西方/群像古装发型+面孔多样/相邻镜过渡铺垫禁硬切/台词↔画面一致/功能角色有反应别走过场/正常语速超15s拆镜）·编剧·情节·分镜大师 + 生成默认遵守

待续: ① 4 worker 完成后复验 15 镜 + 重生 shotlist.md/all_shot_prompts.md/intro_cards.md（含凌虚子字卡）；② EP5 开场并入家人到场段（接现有交锋）；③ 把 7 条铁律分发到 剧情连贯/运镜/时长节奏/动作表演 各 skill 的检查项。

No conflicts found in: world.md（七档/凌虚子 canon 本就有）, EP1-3

## Follow-up 035 — 2026-06-21 16:40:00 — 多镜复用角色漏建卡（测资执事等）
Source: 用户「测资执事出现很多回为什么不建character·流程哪出问题」+「是不是还有其他人物漏了」
Summary: 诊断＝**角色没套用"≥2镜复用就立档"门槛**（场景有此门槛、角色漏）。多镜功能配角被默认"群像内联·不锁定"→无角色卡无 ref 图→跨镜面孔漂。漏建：测资执事(6镜)、菜鸡少年(2镜)、围观武者甲/乙(2镜)。1镜龙套(说书先生/路人/废品汉子/中品青年/招人执事)豁免。

Auto-updated:
- 2_世界观人设/characters/{c9_测资执事,c10_菜鸡少年,c11_围观武者甲,c12_围观武者乙}/ — 新建 4 张轻量角色卡（8字段锁定描述符 + voice_id + 真人实拍 Seedream ref 立绘 prompt·古装束发非现代短发）
- 5_6_分镜与prompt/episodes/ep04/shots/shot06-14（9镜）— `参考:` 行接线 cN ref handle（c9 测资执事→S8-14·c10 菜鸡少年→S11/12·c11/c12 围观甲乙→S6/7），ref 图锁面孔防漂
- all_shot_prompts.md 重聚合（角色 ref 入汇编）

Auto-updated（流程根治）:
- .claude/agent_refs/project/ai_video.md — 加「角色≥2镜复用就立档」amendment（对称场景门槛·任一角色含episode-local配角出现≥2镜必建卡+ref·1镜龙套豁免·角色卡≠出场字卡）
- .claude/skills/ai_videos__格式契约/SKILL.md — 加 K25：角色≥2镜必有卡+ref+参考handle+byte-identical标签·缺即blocker

复验: 测资执事/菜鸡少年/围观甲乙 4 卡建齐；9 镜参考行已带 cN ref。
角色卡累计 c1–c12（c6/c7 EP2群像·c9-12 EP4群像·同一立档门槛）。

No conflicts found in: shot 内容/剧情, world.md

## Follow-up 036 — 2026-06-21 17:20:00 — prompt 字数 K10 自检 + 固化
Source: 用户「确保每个 prompt <2000 字」+「这点每次新建/改 prompt 你应自己 check 不要每次提醒」
Summary: 扫全 drama 271 个生成块查 K10(≤2000字)——EP4 worker 重铺的 shot14(2481→压)/shot15(2858→压)超标(老剑仙/中品交涉写太丰富)。压缩冗余字段至 ≤2000，并把「生成后默认自检字数」固化成铁律。

Auto-updated:
- 5_6_分镜与prompt/episodes/ep04/shots/shot14,shot15 — 压缩超长字段(去重复藏锋句、精简走位/动作/光线/镜头、负向去重~45→32项、测灵碑描述符精简)至 ≤2000 字；信息无损(blocking/藏锋/特效全保留)
- all_shot_prompts.md 重聚合
- .claude/agent_refs/project/ai_video.md — 真人古装剧铁律加第8条「生成/改 prompt 后默认自跑格式契约 K10 字数自检·fan-out worker 产出 parent 必补检·不待用户提醒」

复验: EP4 全 15 镜视频prompt + 角色/prop/场景 ref 块全 ≤2000 字。
待办: EP5 暂存 old_shot13(2323·porting时trim)、EP1 shot03(2129·legacy)——非本次范围、各自处理时修。

No conflicts found in: EP4 剧情/锁定串
