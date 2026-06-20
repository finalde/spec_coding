# Changelog — wushen_juexing

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
