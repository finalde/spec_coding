---
worker_id: researcher-01-baseline_extraction
stage: 3
role: researcher
angle: baseline_extraction
status: partial
blockers:
  - "cong_jianshu_xiuxing: 目录为空，无 README / _meta.json / chapters，无法提取（per constraints 显式记录）"
  - "gou_zai_xiuxianjie: 目录为空，无可读内容（显式记录）"
  - "zhutian_daozu: 目录为空，无可读内容（显式记录）"
confidence: high
---

## 1. What this angle covers

本 angle 对 `downloaded_novels/xianxia/` 下的 14 本基线仙侠小说做 cross-novel 元素抽取，把"共性 = 可放心复用的题材结构"与"个性 = 必须改名/重做/丢弃的命名实体"两类资产分开列出。stage 4 的 spec 编纂将以此为去版权化判断依据 — 任何元素若仅出现在 1 本基线中（"溯源 = 1"），按 revised_prompt 的 copyright-safety 硬约束必须重新设计；若 ≥ 3 本共有，则视为类型公共资产，本作可径直复用。

14 本中实际可读 11 本（fanren_xiuxian_zhuan / gou_zai_liangjie_xiuxian / gou_zai_yaowu_luanshi / guangyin_zhiwai / jie_jian / meiqian_xiu_shenme_xian / shan_he_ji / shei_rang_ta_xiuxian_de / wode_moni_changsheng_lu / xuanjian_xianzu / zhen_wen_changsheng）。3 本（cong_jianshu_xiuxing / gou_zai_xiuxianjie / zhutian_daozu）目录完全为空，无法贡献观察。下文所有 citation 仅在可读语料范围内。

读取策略：每本读首 5 章（开篇 hook + 主角设定 + 修炼体系初露），spot-check 第 50 章、第 100 章、以及结尾章（surface mid-arc 节拍 + 收束基调）。

## 2. Key findings

### 2.1 修炼境界体系（cultivation ladder）

qa.md Q9 已锁定 8 阶经典阶梯：**练气-筑基-金丹-元婴-化神-炼虚-合体-大乘**。在可读语料中：

| 基线小说 | 境界命名 | 与 8 阶经典对齐？ | 引用 |
|---|---|---|---|
| fanren_xiuxian_zhuan | 练气 / 筑基 / 金丹 / 元婴 / 化神 / 炼虚 / 合体 / 大乘（"四大派"语境多次出现） | 完全对齐 | 第 1–5 章引入；mid-arc 节奏来自 ladder（韩立 stuck on 炼气 → 突破筑基为标志性 beat） |
| gou_zai_yaowu_luanshi | 炼气 → 筑基（开篇即明示"司徒家有不止一位筑基大修，寿延 200 年"） | 对齐 | ch01：「不入阶妖虫——石龙子」「炼气三层」「筑基大修」（chapters/0001） |
| gou_zai_liangjie_xiuxian | 修仙者 / 碧海门弟子选拔（散修视角） | 默认对齐，未与 8 阶冲突 | ch01–03（chapters/0001-0003） |
| shei_rang_ta_xiuxian_de | **逐字命中 8 阶**：「练气、筑基、金丹、元婴、化神、炼虚、合体、渡劫」 | 仅最后一阶用"渡劫"代"大乘"，本质同 | ch01：孟景舟与陆阳对话原文（chapters/0001） |
| guangyin_zhiwai | 凝气、筑基、结丹、元婴（明示 4 阶；元婴以上"竹简上没有记录"） | 截断对齐（前 4 阶同义改写：练→凝、金→结） | ch02：「分为凝气、筑基、结丹、元婴」（chapters/0002） |
| xuanjian_xianzu | 链气、筑基、玉芽丹（链气三层突破）；隐含同 8 阶 | 对齐（用"链气"作为"炼气"的同音异写，前 100 章未越筑基） | ch99：「李通崖突破练气三层…练气化筑基」（chapters/0100） |
| zhen_wen_changsheng | 链气期 / 筑基 / 化神（提及）；嫡传/内门/外门分层 | 对齐 | ch01–03 + ch100：「严教习…链气九层」「化神」隐现（chapters/0001, 0100） |
| wode_moni_changsheng_lu | 筑基、结丹、元婴、化神、合体、渡劫；万仙盟语境 | 对齐 | ch100：「机关傀儡战力压低到链气期…身体强度能硬抗元婴期」（chapters/0100） |
| jie_jian | 「炼剑诀」「灵胎」「下等灵胎」；游戏化命名层（不是纯境界） | 半对齐，加了 game-system overlay | ch48：「灵盘」「灵胎品阶」（chapters/0050） |
| meiqian_xiu_shenme_xian | 「仙道十大境界」「链气 → 筑基」「道心等级 / 法力水平」 | 形式对齐 + 数值化（道心 10 级 + 法力 60 点突破筑基） | ch03：「练气境作为仙道第一境…道心跨越 10 级、法力超过 60 点」（chapters/0003） |
| shan_he_ji | 丹师、镇魔司、丹品分级（八品 → 七品）；明确境界未细列 | 体系不同（聚焦丹师 + 镇魔司而非通用 ladder） | ch01：「八品丹师」「丹药司正规认证」（chapters/0001） |

**结论：8 阶经典 ladder 是绝对共性，11 本中 9 本完全 or 半字面对齐。`shei_rang_ta_xiuxian_de` 的 7+渡劫拼写 = 同概念；`guangyin_zhiwai` 的"凝/结"是 4 阶同义改写而非另立体系。**Stage 4 可以放心直写 8 阶；命名"练气-筑基-金丹-元婴-化神-炼虚-合体-大乘"或"练气-筑基-金丹-元婴-化神-炼虚-合体-渡劫"均不构成抄袭（共有 ≥ 3 本基线）。

### 2.2 三方势力格局（正道宗门 / 散修 / 魔门 trifecta）

| 基线 | 正道宗门 | 散修空间 | 魔门 / 反派组织 | 三方齐全？ |
|---|---|---|---|---|
| fanren_xiuxian_zhuan | 七玄门（七绝堂 / 百锻堂 / 内门 / 外门） | 韩立后期跳出门派成散修主线 | 后期"魔道"出现 | 是（典型代表） |
| zhen_wen_changsheng | 通仙门（嫡传/内门/外门 + 猎妖堂） | 散修 + 猎妖师 | 后期"叛门追杀"暗示；前 100 章未点名魔门 | 中（正 + 散明示，魔暗示） |
| shei_rang_ta_xiuxian_de | 问道宗、悬空庙（五大仙门，明示其中两个） | 主角陆阳自述"碰运气"散修出身 | 未在 ch01–03 出现 | 中 |
| xuanjian_xianzu | 隐世李家（耕荒家族）+ 大黎山周边宗门（未具名） | 李家本身是散修家族 | 仙人内斗（"仙人打架"村中震动）暗示派系 | 中 |
| wode_moni_changsheng_lu | 万仙盟（mid-arc 出现，正派联盟） | 主角李凡靠模拟器 solo 出身、太师身份混淆 | 未在样本中明示魔门 | 中 |
| gou_zai_yaowu_luanshi | 青竹山坊市（南荒修仙界，越国）+ 司徒家族 | 灵农 = 边缘散修 | "劫修"出现（袭击棚户区，黑袍蒙脸） | 是（劫修 = 魔门变体） |
| gou_zai_liangjie_xiuxian | 碧海门（一界）+ 大凉世界凡人帝国（二界） | 主角方青劳工兼穿越者，散修 | 未明示魔门 | 半 |
| jie_jian | 道门（东洲四大宗门之一）；游戏化 | 主角"开号"散修玩家 | 镇魔司类机构 + 罪犯 NPC | 是（游戏化变体） |
| meiqian_xiu_shenme_xian | "十大宗门"（高中体育课语境出现） | 主角张羽现代设定下的"贫困学生" | "元阴链气之术" / 邪派妖修暗示 | 半 |
| shan_he_ji | 丹霞帮、镇魔司（官方） | 主角陆行舟独立丹师 | 凶杀案中的隐藏黑手 | 半（侦探向） |
| guangyin_zhiwai | 修士聚落 + 神灵气息异化体 | 主角许青废墟散修 | 异质化的"异兽" + "诡异"（夜晚出没） | 是（魔门变体 = 神灵异质） |

**结论：三方格局是仙侠类型 muscle memory。11 本中 5 本明示三方齐全、5 本至少有正 + 散。**Stage 4 的 world.md 应直写"正道宗门 / 散修自由人 / 魔门或类似变体"，命名风格 freedom 极高。**唯一需要小心的命名 fingerprint**：

- "七玄门"（fanren）+ "通仙门"（zhen_wen）+ "问道宗"（shei_rang）+ "碧海门"（gou_zai_liangjie）= 4 个名字都是 "2 字描述 + 门/宗"。要避免与任一具体名字相撞，但模式本身（"X门 / X宗"）是 ≥ 4 本共用，可放心复用模式。
- "魔门" 这个泛称在 11 本中只在 fanren_xiuxian_zhuan 后期 + qa.md 设计中出现；多数基线用"劫修"（gou_zai_yaowu）、"邪派"、"异质 / 诡异"（guangyin）、"叛门"（zhen_wen）等替换。**"魔门" 作为概念安全，但具体组织名必须独创。**

### 2.3 主角原型矩阵（mapped to qa.md Q5 = 重生复仇）

| 基线 | 主角名 | 原型 | 起点 | 是否"重生"？ | 三角对照价值 |
|---|---|---|---|---|---|
| fanren_xiuxian_zhuan | 韩立 | 凡人逆袭 / 苟道（grind 派祖宗） | 山村穷孩子 → 七玄门记名弟子 → 墨大夫毒手中翻盘 | 否（单世界单生） | 中（提供 grind 节奏 + 蛰伏心机） |
| wode_moni_changsheng_lu | 李凡 | **模拟器重活+科举权臣→修仙** | 太师府寿宴上，70 岁权臣，目睹仙人斗法，发现自己有"锚定 + 重新过一遍人生"的模拟器 | **是（强重生 + 模拟器金手指）** | **★ 最强三角候选** — 重生 + "再来一遍"机制 + 复仇属性（杀宣景帝、夺琅琊王府）已是 qa.md 设定的近邻形态。注意：本作的 hostile-system 是"消耗寿命/记忆"，而李凡的模拟器是"无成本重来" — 这是关键差异点，必须强化。 |
| gou_zai_yaowu_luanshi | 方夕 | 穿越者 + **双界穿梭**（青竹山坊市 + 大凉妖武世界）；金手指 = "我又穿了一次" | 灵农 + 大凉富家少爷双重身份 | 否（穿越 ≠ 重生，但有"二次穿越"机制） | 高（提供"金手指 = 可恶代价"的早期框架 + 多界叙事节奏） |
| gou_zai_liangjie_xiuxian | 方青 | 穿越者，珠子（神器）金手指可两界传送 | 古蜀流民 → 海岛碧海门候选 | 否（穿越） | 中（神器型金手指 + 苟道）|
| zhen_wen_changsheng | 墨画 | 穿越者，识海有"道碑"金手指（前世现代美工） | 通仙门外门弟子，靠帮人代画阵法挣灵石 | 否（穿越 + 识海器灵） | 中（金手指有形式 = 神识依附）|
| xuanjian_xianzu | 陆江仙 / 鉴子 | **穿越成器灵（圆形发光物）** + 转世为李项平 | 出租房猝死 → 鉴子转世 + 月华吸收 | 弱重生（更接近器灵转世） | 低（设定特殊） |
| meiqian_xiu_shenme_xian | 张羽 | 穿越者 / 贫困考学生 | 现代仙道高中（嵩阳）面试失败 → 重新拾起境界 | 否（纯穿越 + 现代设定）| 低（设定迥异） |
| shei_rang_ta_xiuxian_de | 陆阳 | 穿越者，作弊金手指（"今日宜出行，不宜作弊"反讽） | 问道宗考生 | 否 | 低 |
| jie_jian | 楚槐序 | 游戏穿越（陪玩职业） | 戴上游戏头盔进入《借剑》 | 否 | 低 |
| shan_he_ji | 陆行舟 | 八品丹师 + 瘸子 + 杀人案嫌疑人 | 神秘 — 自家祖业被霸占，反向收购 | 隐藏前生暗线 | 中（"瘸"伪装 + 双面身份给 deception 节拍参考） |
| guangyin_zhiwai | 许青 | 末世废墟少年（神灵气息污染世界） | 拾荒杀秃鹫为食 | 否（黑暗末世起手）| 低 |

**结论：11 本中只有 `wode_moni_changsheng_lu` 是真正的"重生"原型 — 而且它还带模拟器、复仇、权臣身份这三个我们要的元素全套。这本必须列为本任务的头号"避撞 + 借节拍"对照本。**

具体三角行动：
- ✅ 借鉴节拍：李凡"前世已成太师 → 这一世重头来过 → 不走原路、走更险路"是本作 hostile-system / 寄生代价的近邻情绪 — 我们的差异化必须在"代价"上 — 李凡是无成本重活；我们是每升一级吃掉寿命/记忆。
- ❌ 避撞元素：李凡的具体姓名"李凡"、太师身份、宣景帝 / 琅琊王 / 玄京城、"模拟器锚定 N 年"、"温县 / 江淮府"这些具名 — 全部禁用。
- ❌ 避撞元素：李凡的金手指叫"天玄镜"（chapters/0050 出现） — 本作的 system 必须叫别的名字。

第二个值得三角的是 `fanren_xiuxian_zhuan`（韩立的 grind 节拍、墨大夫"师父变敌人"反转、心机蛰伏） — 不是重生但其 betrayal-survival 节奏天然兼容 qa.md 的 hostile-system 设定。

### 2.4 开篇 hook 矩阵（first-5-chapter analysis）

| 基线 | ep01 hook 类型 | 强度 | 引用 |
|---|---|---|---|
| fanren_xiuxian_zhuan | 山村穷小孩 → 三叔带去入门考核（七玄门炼骨崖） | 低强度，慢热 | ch01–04 |
| wode_moni_changsheng_lu | **太师寿宴**目睹仙人斗法 + 老爷子第一视角认知崩塌 + 后被仙凡瘴卷入死亡 → 醒来回到锚定前 | **极高强度，反差感拉满** | ch01 |
| gou_zai_yaowu_luanshi | 灵农抓妖虫赔本 + 抱怨穿越（前世考公） + 揭示二穿（双界）金手指 | 中（"被逼急了"反英雄爽点） | ch01–02 |
| gou_zai_liangjie_xiuxian | 流民夜逃 + 老叔捐血祭祀（道生）+ 主角触发珠子瞬移到海上 | 中高（祭祀 + 神秘宝物 + 海上死里逃生） | ch01–02 |
| zhen_wen_changsheng | 10 岁外门弟子蹲石头后画阵法挣灵石 → 揭示识海道碑金手指 | 中（"小聪明 + 隐藏底牌" 反差） | ch01–02 |
| xuanjian_xianzu | 现代社畜猝死 → 转世成河里的"圆形发光物"（鉴子，器灵）→ 被李家收养 | 中高（器灵 POV 罕见）| ch01–02 |
| jie_jian | 戴上游戏头盔进入 NPC 收钱 50 两的雨夜场景 → 第一句台词就是讨价还价 | 高（雨夜 + 油纸伞 + 黑色幽默） | ch01 |
| meiqian_xiu_shenme_xian | 高中面试官淡定问"你绝育了吗？现在初中生都得绝育" | **极高（荒诞反差）** | ch01 |
| shei_rang_ta_xiuxian_de | 雨中赶路上仙门考核车 → 与 NPC 商讨作弊 | 中（轻快幽默调）| ch01 |
| shan_he_ji | 镇魔司审讯 — 男主瘸子被怀疑全宅命案凶手 → 反向洗清 | 高（侦探氛围 + 主角扮猪吃虎） | ch01 |
| guangyin_zhiwai | 末世废墟下少年捕食秃鹫 + 神灵血雨 + 紫水晶治愈伤口 | 高（克苏鲁仙侠氛围） | ch01–03 |

**结论 for stage 4 ep01 design**：本作 ep01 hook = "拾到神器 / 系统觉醒 + 重生复仇"（qa.md Q8）。我们的开局形态最接近 wode_moni_changsheng_lu 的"目睹反差 → 触发金手指" + meiqian_xiu_shenme_xian 的"日常场景里突然出现非常规元素"组合。**安全 hook 配方**：让主角在前世死亡瞬间（被背叛者击杀），系统在他临死时"接通"，给他一次重生机会但每升一级吃他寿命/记忆。**禁忌**：不能复刻太师寿宴 + 流星仙人斗法（wode_moni 同款），不能复刻末世异质血雨（guangyin 同款），不能复刻雨夜油纸伞讨价还价（jie_jian 同款）。

### 2.5 distinctive 命名实体 rename list（"溯源 = 1，必须重做"）

下表全部为单一基线独占的命名实体，本作必须独立创造、不得借用字面：

| 类别 | 具名实体 | 源基线 + 章节 | 类型化后是否可保留？ |
|---|---|---|---|
| 神器 / 金手指 | 天玄镜 | wode_moni_changsheng_lu, ch50 | 概念（商店类系统镜）→ ok，名字必须换 |
| 神器 / 金手指 | 道碑（识海内古碑） | zhen_wen_changsheng, ch01–02 | 概念（识海器灵）→ ok 但需重新设计样态 |
| 神器 / 金手指 | 鉴子（圆形发光物 / 器灵） | xuanjian_xianzu, ch01 | 概念太独特，建议整体规避 |
| 神器 / 金手指 | 紫水晶（神灵尸身吸取） | guangyin_zhiwai, ch02–03 | 类型可（治疗型宝物），具名禁用 |
| 神器 / 金手指 | 珠子（两界穿梭） | gou_zai_liangjie_xiuxian, ch01–02 | 双界穿梭机制本身在 gou_zai_yaowu 也出现，但 gou_zai_liangjie 的"珠子"具名禁用 |
| 神器 / 金手指 | 玄天胎息丹（丹王炼） | jie_jian, ch48 | 类型可（突破丹），具名禁用 |
| 宗门 | 七玄门（七绝堂、百锻堂） | fanren_xiuxian_zhuan, ch02–05 | 模式可（"X 玄门 / X 绝堂"），具名禁用 |
| 宗门 | 通仙门（嫡传/内门/外门 + 猎妖堂） | zhen_wen_changsheng, ch01–03 | 模式可，具名禁用 |
| 宗门 | 问道宗、悬空庙、丹霞帮 | shei_rang_ta_xiuxian_de + shan_he_ji | 同上 |
| 宗门 | 碧海门、玉芽丹（突破丹） | gou_zai_liangjie + xuanjian_xianzu | 具名禁用 |
| 宗门 | 万仙盟 | wode_moni_changsheng_lu, ch100 | 具名禁用 |
| 功法 | 太阴吐纳练气诀 / 月华纪要秘旨 | xuanjian_xianzu, ch01 | 具名禁用 |
| 功法 | 月阙剑弧、玄水剑诀 | xuanjian_xianzu, ch99 | 具名禁用 |
| 功法 | 炼剑诀 | jie_jian, ch48 | 具名禁用（虽朴素，仍禁） |
| 阵法 | 铁甲阵（六道阵纹） | zhen_wen_changsheng, ch100 | 类型可（防御阵），具名禁用 |
| 阵法 | 五行阵法基础阵纹 | zhen_wen_changsheng, ch01 | "五行" 是通用概念，可保留 |
| 妖物 | 石龙子（不入阶妖虫） | gou_zai_yaowu_luanshi, ch01 | 具名禁用 |
| 妖物 | 吴柞虫（吐丝织灵布） | xuanjian_xianzu, ch99 | 具名禁用 |
| 妖物 | 缠香丝（毒物） | fanren_xiuxian_zhuan, ch50 | 具名禁用 |
| 地名 | 玄京、温县、江淮府、琅琊王府、嘉元城、岚州、青牛镇、彩霞山、落日峰、仙霞山 | wode_moni + fanren | 具名禁用 |
| 地名 | 通仙城、墨山、大黎山、眉尺河、黎泾村 | zhen_wen + xuanjian | 具名禁用 |
| 地名 | 青竹山坊市、南荒修仙界、越国 | gou_zai_yaowu | 具名禁用 |
| 地名 | 碧玉岛、巴郡、三水坳、天府城、大凉世界、黑石城 | gou_zai_liangjie | 具名禁用 |
| 地名 | 镜州、镜州城、夏州、京师 | fanren + shan_he_ji | 具名禁用 |
| 地名 | 嵩阳高中（仙道高中） | meiqian_xiu_shenme_xian | 具名禁用 |
| 地名 | 玄黄界 / 东洲（游戏世界） | jie_jian | 具名禁用 |
| 人物 | 韩立、墨大夫、舞岩、岳堂主、王护法、张铁、张均（fanren）；李凡、宣景帝、琅琊王、孙二狗（wode_moni）；墨画、白子胜、白子曦、安少爷、严教习、俞长老、墨山（zhen_wen）；方夕、方青、阿福、查老汉、珠儿（gou_zai 双本）；陆行舟、盛元瑶、柳擎苍、柳烟儿、白驰、霍家（shan_he_ji）；陆阳、孟景舟、戴不凡、云芝（shei_rang）；楚槐序、韩霜降（jie_jian）；张羽、王海（meiqian）；陆江仙 / 李项平 / 李木田 / 李通崖 / 李玄宣 / 田芸（xuanjian）；许青（guangyin） | 各对应基线 | 全部具名禁用 — 主角名、姓氏组合都要避开 |

### 2.6 recurring location archetypes（可放心复用的场景类型）

下列场景类型在 ≥ 3 本基线中重复出现，stage 4 + stage 6 可直接拿去 storyboard，无版权风险（命名必须独创，结构通用）：

| 场景原型 | 出现于（基线计数） | 短剧拍摄友好度（per revised_prompt prop ≤ 6） |
|---|---|---|
| 山门入口 / 宗门石阶 | fanren / zhen_wen / shei_rang / wode_moni（4 本） | 高（石阶 + 牌坊 + 雾） |
| 山顶悬崖 / 渡劫场 | fanren / wode_moni / gou_zai_liangjie（3 本） | 高（悬崖 + 云海 + 雷劫） |
| 洞府（修炼密室） | fanren / wode_moni / xuanjian / zhen_wen / jie_jian（5 本） | 高（蒲团 + 油灯 + 阵纹） |
| 丹房 / 炼丹炉 | shan_he_ji / wode_moni / gou_zai_yaowu / jie_jian（4 本） | 高（丹炉 + 火焰 + 玉瓶） |
| 坊市 / 集市 | fanren / gou_zai_yaowu / zhen_wen（3 本） | 中（人多 prop 复杂；避开广角全景） |
| 灵田 / 灵植 | gou_zai_yaowu / xuanjian / wode_moni（3 本） | 高（竹林 / 稻田 / 雾气） |
| 密林 / 深山妖物出没 | fanren / xuanjian / guangyin（3 本） | 高（树影 + 兽眼）|
| 月夜 / 月华吸纳 | xuanjian（ch01）+ fanren mid-arc | 高（月光 + 静水）|
| 雨夜小道 | jie_jian / shei_rang（2 本，类型仍可用）| 高（油纸伞 + 雨）|
| 凶案现场 / 镇魔司 | shan_he_ji 独有 | 中（侦探向，本作不主用）|
| 山顶比试场 / 演武场 | fanren / meiqian / wode_moni（3 本）| 高（剑架 + 高台） |
| 海上 / 海岛渔村 | gou_zai_liangjie（仅 1 本） | 低（且独占，本作避开）|
| 末世废墟血雨 | guangyin（仅 1 本） | 低（独占，本作避开） |

**结论**：山门石阶 / 洞府 / 丹房 / 灵田 / 密林月夜 / 演武场是 stage 4 锁定 6–10 个 recurring scenes 的最强候选 — 全是 ≥ 3 本共用且 prop 简单。海岛 + 末世废墟应避开（单本独占且 AI 图生成稳定性低）。

### 2.7 naming-fingerprint 分析（informs stage 3 character_anonymization）

观察可读语料中的命名规律：

**主角姓名长度**：
- 2 字主角名：5 本（韩立 fanren、李凡 wode_moni、墨画 zhen_wen、方夕 / 方青 gou_zai 双本、许青 guangyin）
- 3 字主角名：5 本（陆行舟 shan_he、楚槐序 jie_jian、张羽 meiqian、陆江仙 / 李项平 xuanjian、陆阳 shei_rang）
- → 2 字 / 3 字均常见，本作可两者择一，不构成 fingerprint 风险。

**主角姓氏 frequency**：陆（4 本：陆行舟、陆江仙、陆阳；李项平也姓李，但 xuanjian 同时有陆江仙转世为李项平）、方（2 本：方夕 / 方青）、李（2 本：李凡、李项平）、韩（1 本）、张（1 本）、墨（1 本）、楚（1 本）、许（1 本）。
- → "陆"高频，本作主角应避开"陆"；"方 / 李"次高频，也建议避开。**安全姓氏候选**：苏 / 江 / 谢 / 沈 / 萧 / 宁 / 顾 / 戚 / 慕容 / 上官（这 10 个在样本中 0 命中）。

**宗门命名模式**（统计前文已列）：
- "X 玄门 / X 绝堂"（fanren）
- "X 仙门 / X 仙门"（shei_rang 的"五大仙门"是泛称）
- "X 道宗 / 问道宗"（shei_rang）
- "X 海门"（gou_zai_liangjie 的"碧海门"）
- "X 仙城 + 通仙门"（zhen_wen）
- "X 霞帮"（shan_he 的"丹霞帮"）
- → 安全宗门模式：避开"七 X / 通 X / 问 X / 碧 X / 丹 X / 万仙 X"前缀；建议用"X 渊 / X 阙 / X 墟 / X 璇 / X 樞 / X 玑"这类罕见单字前缀。

**魔门 / 反派组织命名模式**：基线样本量太小（fanren 后期"魔道"+ gou_zai_yaowu"劫修"+ zhen_wen"叛门"），命名 fingerprint 不形成。本作的魔门可独立命名（如"幽阙宗 / 渊冥殿 / 玄煞门"等），无撞名风险。

**功法命名模式**：
- 3 字 + 4 字混合："月阙剑弧 / 玄水剑诀 / 太阴吐纳练气诀 / 月华纪要秘旨 / 炼剑诀 / 缠香丝（毒功）/ 玄天胎息丹"。
- 通用术语"剑诀 / 剑弧 / 吐纳 / 练气诀 / 纪要 / 秘旨 / 胎息"全是 ≥ 2 本共享 → 类型化术语安全。
- 独占字眼"月阙 / 太阴 / 月华 / 缠香 / 玄天"等具名组合必须避开。

## 3. Implications for the spec（stage 4 actionable）

1. **修炼境界**：直接采用 qa.md Q9 锁定的"练气-筑基-金丹-元婴-化神-炼虚-合体-大乘"8 阶 — 11 本基线中 ≥ 9 本字面对齐，零版权风险。每阶内部小阶段（如"练气一层"到"练气九层"）也是 ≥ 5 本共用，可放心使用。
2. **三方格局**：world.md 直写"正道宗门联盟 + 散修地带 + 魔门（具体组织名独创）"。`fanren_xiuxian_zhuan` 的"门派内部分外门 / 内门 / 嫡传"三层结构是 ≥ 4 本共用，stage 4 可在此基础上加自家宗门内部分层。
3. **主角原型 = 重生复仇 + hostile system**：唯一真正"重生"的基线 `wode_moni_changsheng_lu` 锁定为头号避撞对照本 — 本作差异化必须落在"代价"二字（李凡=无代价重来；本作=每升一级吃寿命/记忆）。具体 plot beat 不可与"太师寿宴 + 仙人斗法 + 流星 + 仙凡瘴"任何一项重叠。
4. **ep01 hook**：可借鉴 wode_moni 的"反差感目睹仙凡冲突" + meiqian_xiu_shenme_xian 的"日常场景突现非常规元素"组合，但场景必须重写（不能寿宴、不能高中面试官谈绝育）。建议方向：主角前世死亡瞬间触发系统接通，背叛者的脸 + 一句关键台词作为 ep01 cliffhanger。
5. **distinctive 实体禁用名单**：见 § 2.5 表。stage 3 的 character_anonymization angle 必须把这个表作为种子黑名单输入，并扩展到具体角色名。stage 5 的 copyright_clearance 验证器必须 grep 所有 generated 文本，命中 § 2.5 任何字面 = 阻断 ship。
6. **recurring scene 6–10 个**：建议锁定『山门石阶 / 修炼洞府 / 丹房 / 灵田竹林 / 密林月夜 / 演武场 / 山顶悬崖 / 坊市 / 宗门议事大殿 / 阵法密室』。海岛、末世废墟、镇魔司刑讯室明确不入选。
7. **naming fingerprint 规则**（stage 3 的 character_anonymization angle 落地用）：
   - 主角姓氏黑名单：陆 / 方 / 李 / 韩 / 张 / 墨 / 楚 / 许（基线已出现）；候选名单：苏 / 江 / 谢 / 沈 / 萧 / 宁 / 顾 / 戚 / 慕容 / 上官。
   - 宗门前缀黑名单：七 / 通 / 问 / 碧 / 丹 / 万仙 / 玄（前缀位单字）；候选模式：以"渊 / 阙 / 墟 / 璇 / 樞 / 玑 / 烬 / 寂"等单字开头 + 门 / 宗 / 阁 / 殿。
   - 功法命名：用类型化后缀（剑诀 / 心法 / 吐纳决 / 纪要）+ 独占前缀（自创 2 字），前缀必须不在 § 2.5 列出的具名中。

## 4. Open questions surfaced

1. **3 个空目录的修复**：cong_jianshu_xiuxing / gou_zai_xiuxianjie / zhutian_daozu 完全无内容。是否在后续 stage 启动一个补抓 task（同 follow-up 111 的格式），用于完整 14 本对照？目前的 baseline_extraction 是基于 11 本的子集，结论 robustness 已足够（共性来自 ≥ 3 本，最低多本基线已满足），但完整 14 本会让"distinctive 禁用名单"更全（这三本若被读到，可能新增的具名实体仍需进 § 2.5 表）。建议：stage 4 进入前由 user 决策。
2. **"魔门"具名缺位**：11 本基线中均未出现一个名字直接叫"X 魔门"的具体组织 — 它们用"劫修 / 邪派 / 异质 / 叛门 / 镇魔司（正面）"等替换。这意味着本作的魔门名字几乎无版权风险，但也意味着"魔门"这一概念在仙侠当代实践中已有去名化趋势 — stage 4 spec 编纂时是否仍用"魔门"字面，还是用"X 渊 / X 殿 / X 教"等替换，建议在 stage 4 spec 候选阶段再定。
3. **境界 ladder 最末阶**：经典 8 阶有"合体 → 大乘 / 渡劫"两种收束。本作取哪一种？`wode_moni` 用"渡劫"，`fanren` 用"大乘"，`shei_rang` 用"渡劫"。stage 4 决定，本 angle 不再展开。
4. **"重生 vs 穿越"的伦理 fingerprint**：本作锁定"重生复仇"，但 11 本基线中真"重生"只有 1 本（wode_moni），其余 9 本都是"穿越者 + 金手指"。是否本作沿用穿越体（"主角是现代人灵魂 + 古修仙者身体"）更安全，还是坚持"主角就是这世界本土修士 + 前世记忆"更差异化？建议 stage 4 spec 候选阶段 decide — 当前 angle 推荐后者，因为：本作的 hostile-system 代价机制只有在"本土修士 + 前世记忆碎片"语境下才能跟"吃寿命 / 记忆"形成机理闭环；穿越体的"系统外来"语境会稀释代价的悲剧感。
