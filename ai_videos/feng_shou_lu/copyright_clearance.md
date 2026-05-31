---
worker_id: parent-tier5
stage: 6
role: parent
work_unit_id: copyright_clearance_seal
status: complete
blockers: []
confidence: high
---

# 版权清查报告 · 《焚寿录》feng_shou_lu

> 本文件供 stage-5 / stage-6 validator grep + 用户最终 sign-off 使用. 本作所有命名 / 设定 / 场景 / 道具与三方语料库 (14 本基线下载小说 + sibling 项目 `mozun_chongsheng` + 2025-2026 头部 IP web) 的版权差异度逐项核查. 内容中文 + Chinese-content rule (per spec FR-12).

---

## 1. BLACKLIST 总览 (≈ 145 atomic terms per stage-5 strategy)

**source 1 (≈ 95 项)**: `findings/angle-character_anonymization.md` §2.1 — 14 本基线下载小说核心命名 (人名 / 宗门 / 功法 / 地名 / 神器).

**source 2 (≈ 50 项)**: `findings/angle-character_anonymization.md` §2.2 — `mozun_chongsheng` 已用全部命名 (5 主角 + 5 反派 + 5 大宗派 + 9 关键地名 + 9 阶魔功 + 4 丹药).

**source 3 (≈ 30 项)**: `findings/angle-character_anonymization.md` §2.3 — 2025-2026 短剧 / 网文 头部 web-collision (沈烬 / 宁烬 / 宁川 / 青冥剑宗 / 长月烬明 / 香蜜沉沉烬如霜 / 江砚 / 等).

### 1.1 高风险 BLACKLIST 抽样表 (parent grep 已扫)

| 类型 | 术语 | source | feng_shou_lu 出现次数 | 状态 |
|---|---|---|---|---|
| 基线主角名 | 韩立 / 方青 / 方夕 / 楚槐序 / 张羽 / 陆行舟 / 陆阳 / 李凡 / 陆江仙 / 墨画 / 许青 | 14-baseline §2.1 | **0** | ✅ Clear |
| 基线宗门 | 七玄门 / 通仙门 / 问道宗 / 万剑归宗 / 紫霄宗 / 朝元宗 / 御兽宗 / 偷天换日宗 / 药王宗 / 黑煞教 / 青迟魔门 / 罗生门 | 14-baseline §2.1 | **0** | ✅ Clear |
| 基线功法 | 太阴吐纳练气诀 / 月华纪要秘旨 / 长春诀 / 元阴链气之术 | 14-baseline §2.1 | **0** | ✅ Clear |
| mozun 主角 | 沧冥 / 叶无尘 / 苏璃月 / 柳红袖 / 苓夭夭 | mozun §2.2 | **0** (shot body) / N (bible 内 cross-clearance 注 — see §3 below) | ✅ Clear (shot body); 注释性 (bible) |
| mozun 反派 | 白月清 / 赵焚天 / 方鼎元 / 韩夺心 / 司空玄 | mozun §2.2 | **0** (shot body) / N (bible cross-clearance) | ✅ Clear (shot body); 注释性 (bible) |
| mozun 宗派 | 紫霄宫 / 玄炎宗 / 太清门 / 万剑宗 / 影神殿 / 中州五道盟 / 沧冥魔域 | mozun §2.2 | **0** (shot body) / N (bible cross-clearance) | ✅ Clear; 注释性 |
| mozun 魔功 | 黑息引 / 九幽指 / 九幽噬魂掌 / 魔气化龙 / 血色雷 / 魔影分身 / 虚空蚀心 / 血雨九重劫 / 星辰魔阵 | mozun §2.2 | **0** | ✅ Clear |
| **CCI-1 forbidden zone** | 万仙盟 (wode_moni 头部 IP, 「X 盟」结构性诱惑) | web §2.3 / strategy.md V-CR-5 | **0** | ✅ Clear (parent 主动避让, 散修组织用「流烛盟」, 与 万仙盟 字根无关) |
| 2025-2026 web | 沈烬 / 宁烬 / 宁川 / 青冥剑宗 / 江砚 | web §2.3 | **0** | ✅ Clear |
| 2025-2026 web 烬-字根 | 长月烬明 / 香蜜沉沉烬如霜 | web §2.3 | **8** — 全部为 **critical-citation reference** (配音参考 / 参考演员 / 风格 benchmark / 负向 anti-pattern); **0** in shot prompt body | ✅ Clear-as-reference (见 §2 below) |

### 1.2 PROPOSED NAMING 表 (本作命名总表, 来自 character_anonymization §3 + follow-up 002 阮瑶 补)

| # | 命名 | in-fiction 词源 | web 碰撞 | 状态 |
|---|---|---|---|---|
| 1 | 裴知秋 | 一叶知秋 + 秋字寿尽凋零母题 (本世自取) | 无 | ✅ Original |
| 2 | 裴长砚 | 砚水长流 + 师徒共「砚」 (前世名) | 无 | ✅ Original |
| 3 | 闻砚清 | 砚水清亮 + 师徒共「砚」 | 无 | ✅ Original |
| 4 | 容漪 | 水纹涟漪 + 寄生波纹母题暗扣 | 无 | ✅ Original |
| 5 | 阮瑶 | 阮 水部首 + 瑶美玉 (童年邻家姐姐, 第二操作员 anchor; per follow-up 002 rename from 楚瑶 to clear 楚乔传 CCI-1) | 无 (楚瑶 已规避) | ✅ Original |
| 6 | 卫长烛 | 长明烛虚伪 + 卫姓「卫道」双关 | 无 | ✅ Original |
| 7 | 应砚之 | 应被打碎的砚 + 之助词显文气 | 无 | ✅ Original |
| 8 | 戚归砚 | 弃笔归砚 + 戚悲伤双关 | 无 | ✅ Original |
| 9 | 池洇 | 水墨晕染 + 池水部首 | 无 | ✅ Original |
| 10 | 阮惘 | 怅然若失 + 阮姓罕见文气 | 无 | ✅ Original |
| 11 | 言息 | 气息 / 寿数 / 利息三重双关 + 言姓极稀有 | 无 | ✅ Original |
| 12 | 焚寿罗盘 | 焚寿 + 罗盘 (24 格读数面板物化) | 无 | ✅ Original |
| 13 | 归砚镜 | 与师父「砚清」+ 主角「长砚」共字根 | 无 | ✅ Original |
| 14 | 残忆经 / 偿岁真言 | 残忆 / 偿岁母题, 与寄生系统共名 | 无 | ✅ Original |
| 15 | 长烟幡 | 长烟同源「长 X」结构 (长砚 / 长烛 / 长烟) | 无 | ✅ Original |
| 16 | 乌泽 | 黑水鸟 + 水部首 | 无 | ✅ Original |
| 17 | 赤霞门 | 赤霞 (晚霞燃尽) | 无 (与 丹霞 错位) | ✅ Original |
| 18 | 九寰阁 | 九重圆环 (藏书 + 阵法) | 无 | ✅ Original |
| 19 | 澹台宗 | 澹然真人 + 御剑静派 | 无 (澹台为复姓在历史剧出现, 仙侠宗门名无对应头部 IP) | ✅ Original |
| 20 | 流烛盟 | 流动烛火 + 散修自燃自灭 | 无 | ✅ Original |
| 21 | 忘川教 | 忘川河 + 偿岁契约 | 无 (与忘川真魔功 功法名不同层级, 本作只用组织名) | ✅ Original |
| 22 | 澹江洲 / 落雁渊 / 栖梧崖 (旧名「无寿崖」) | 澹江 + 落雁 + 栖梧 / 无寿 三大锚定地点 | 无 | ✅ Original |

---

## 2. Critical-citation reference (cleared, NOT 内容借用)

下列引用属于**风格 benchmark / 渲染方向参考 / 负向 anti-pattern**, 非内容借用 — 类比同类 IP 的视觉调性以指导 AI 渲染参数, 不构成版权侵权:

| 引用项 | 出现位置 | 用途 | 清查判定 |
|---|---|---|---|
| 《长月烬明》 | `characters/c6_卫长烛/c6_卫长烛.md` §配音参考 (类比 端正型仙侠剧反派 BOSS 声线) | 渲染方向参考 — actor voice tone reference | ✅ Cleared as critical-citation |
| 《长月烬明》 | `characters/c1_裴知秋/c1_裴知秋.md` §state A + state B 配音参考 (童身段 + 少年男主段 声线参考) | 渲染方向参考 — actor voice tone reference | ✅ Cleared |
| 《长月烬明》 | `characters/c2_裴长砚/c2_裴长砚.md` §负向锁定 (`不要 长月烬明 卡通风`) | **负向 anti-pattern** — explicitly excluded | ✅ Cleared (negative reference) |
| 《长月烬明》 | `characters/c11_言息/c11_言息.md` §配音参考 (神位预言型仙侠剧反派 BOSS 声线参考) | 渲染方向参考 | ✅ Cleared |
| 《长月烬明》 | `characters/c10_阮惘/c10_阮惘.md` §配音参考 (命数型仙侠剧女配声线参考) | 渲染方向参考 | ✅ Cleared |
| 《长月烬明》 | `characters/c5_阮瑶/c5_阮瑶.md` §配音参考 (少女期仙侠剧女配类参考) | 渲染方向参考 | ✅ Cleared |
| 《长月烬明》 | `scenes/s2_落雁渊/s2_落雁渊.md` §风格 (冷调深渊场景实拍调性参考, 明示 `去除魔修紫黑替为本剧重生灰晨`) | 视觉 differentiation 参考 — explicitly DIFFERENTIATED, not borrowed | ✅ Cleared |
| 《长月烬明》 | `style_guide.md` §1 (与《琉璃》《长月烬明》《苍兰诀》《沉香如屑》四档实景仙侠剧并行不撞档) | 视觉 benchmark — 类比平行不超越 | ✅ Cleared |
| 《琉璃》 | 多处配音 / 风格 (类比同类型仙侠剧实拍调性) | 渲染方向参考 | ✅ Cleared |
| 《苍兰诀》《沉香如屑》 | `style_guide.md` §1 (实景仙侠剧四档并列 benchmark) | 视觉 benchmark | ✅ Cleared |

**Critical-citation cleared rationale**:
- 引用仙侠 IP 名称作为「actor voice tone reference」/「视觉 benchmark」/「负向 anti-pattern」是仙侠剧业内常规导演 brief 用法, 等同于电影剧组「参考《教父》的色调」/「不要《阿凡达》的蓝皮」.
- 引用不构成内容借用 (无角色 / 剧情 / 设定 / 命名 carryover).
- 引用全部在内部 director-side planning fields (配音参考 / 渲染样式 / 负向锁定), 不进入 shot prompt body 喂给 AI 模型. Kling / Seedance 不会因 director's reference 而生成与该 IP 相似的内容.

---

## 3. mozun_chongsheng 交叉 grep (sibling project clearance)

`mozun_chongsheng` 是同仓库内 sibling AI 短剧项目, parent stage-5 V-CR-4 强制 grep 本作所有 ep01-shipping 文件确认无内容借用.

### 3.1 mozun 命名 grep 结果

| mozun 命名类别 | 实例 | feng_shou_lu shot prompts | feng_shou_lu bible | 状态 |
|---|---|---|---|---|
| mozun 主角名 | 沧冥 / 叶无尘 | 0 | 0 actual + N cross-clearance footnotes (注释性, "不撞 沧冥 右眼下方 0.5cm 朱砂痣") | ✅ Clear (shot 0 hits; bible footnotes are 守护性 not 借用性) |
| mozun 女主名 | 苏璃月 / 柳红袖 / 苓夭夭 | 0 | 0 actual + cross-clearance only | ✅ Clear |
| mozun 反派名 | 白月清 / 赵焚天 / 方鼎元 / 韩夺心 / 司空玄 | 0 | 0 actual + cross-clearance only | ✅ Clear |
| mozun 宗派 | 紫霄宫 / 玄炎宗 / 太清门 / 万剑宗 / 影神殿 / 中州五道盟 | 0 | 0 | ✅ Clear |
| mozun 地名 | 沧冥魔域 / 九幽之地 / 红袖招酒楼 / 药王谷 | 0 | 0 | ✅ Clear |
| mozun 魔功 | 黑息引 / 九幽指 / 九幽噬魂掌 / 魔气化龙 / 血色雷 / 魔影分身 / 虚空蚀心 / 血雨九重劫 / 星辰魔阵 | 0 | 0 | ✅ Clear |
| mozun 丹药 | 聚气丹 / 化神丹 / 大乘丹 / 渡劫保命丹 | 0 | 0 | ✅ Clear (本作 大乘 境界用作通用术语, 不命名丹药) |

### 3.2 face-mark 错位 cross-check (V-CV-8)

| feng_shou_lu 角色 face-differentiator | mozun 对照 | 错位判定 |
|---|---|---|
| 裴知秋 / 裴长砚 — 左眼下方 0.3cm 灰青胎记 | 沧冥 — 右眼下方 0.5cm 朱砂痣 | ✅ 不同眼 + 不同色 + 不同大小 |
| 闻砚清 — 右眉骨上方 0.5cm 斜疤 | (mozun 无 眉骨 痣 / 疤) | ✅ 不撞 |
| 容漪 — 右耳后 0.4cm 月牙形浅色痣 | 苏璃月 (mozun 主女主) — (无 耳后 标记, 月白衫为主视觉) | ✅ 不撞 |
| 阮瑶 — 右手腕内侧 1.5cm 浅红胎记 | (mozun 无 手腕 标记) | ✅ 不撞 (非面部) |
| 卫长烛 — 左眉骨上方 1cm 旧剑痕浅疤 | (mozun 反派均无 眉骨 标记) | ✅ 不撞 |
| 应砚之 — 下颌右侧 0.3cm 黑痣 | (mozun 无 下颌 标记) | ✅ 不撞 |
| 戚归砚 — 左手虎口 1cm 横剑疤 | (mozun 无 虎口 标记) | ✅ 不撞 (非面部) |
| 池洇 — 左颊近耳骨 0.8cm 斜疤 | (mozun 无 颊 标记) | ✅ 不撞 |
| 阮惘 — 右眼角 0.5cm 三点纹烫印 | 沧冥 (右眼下方 朱砂痣) — 距离 ≥ 0.5cm + 不同形 (烫印 vs 朱砂) | ✅ 不撞 |
| 言息 — 鼻梁中段 0.3cm 横向旧伤 | (mozun 无 鼻梁 标记) | ✅ 不撞 |

V-CV-8 face-mark 错位 全 11 角色 ✅ pass, 与 mozun 6 + 苏璃月 / 沧冥 共 N 主要角色 face-mark zero collision.

---

## 4. DELTA 报告 (本作 vs 14 baseline + mozun)

### 4.1 vs 14-baseline 总体 DELTA

- **主角原型**: 重生 + 寄生系统 + 60-ep 复仇. 14-baseline 中 重生类 (gou_zai_liangjie_xiuxian) 与 系统类 (meiqian_xiu_shenme_xian) 是两个独立类型, 本作首次将「寄生系统 + 重生复仇」二者交叉到一个主角身上 — 类型组合 originality.
- **核心母题**: 寿元 + 记忆 双重代价. 14-baseline 中 (a) 寿元代价 在 wode_moni_changsheng_lu 出现但只用作 渡劫风险, (b) 记忆代价 在 任一 baseline 中未见. 「升级 → 寿减 → 记忆失」的三重代价绑定 是本作 unique.
- **修炼境界**: 八阶 ladder 沿用 5+ baseline 共用资产 (练气 → 筑基 → 金丹 → 元婴 → 化神 → 炼虚 → 合体 → 大乘) — 通用公共资产, 无版权风险. 终阶取「大乘」刻意与 wode_moni 「渡劫」错位.
- **三方势力**: 正派联盟 + 散修盟 + 魔门 + 朝堂 四方格局 — 三方为 baseline 共用资产, 朝堂为本作 unique 扩展 (per world.md §3.4).
- **每元素 ≤ 1 baseline 距离 hard 契约**: 每一项命名 / 设定 / 场景 / 道具的 baseline 出处不超过 1 本; 全表 11 角色 + 5 宗派 + 4 神器 + 5 功法 + 3 地点 = 28 项, 28 / 28 ≤ 1 baseline 距离, ✅ contract met.

### 4.2 vs mozun_chongsheng DELTA

- **题材**: mozun = 魔尊重生 (反派洗白线); 本作 = 剑修重生复仇 (正派被叛 → 复仇 → 自身即源头). 题材内核相反 (魔修被洗 vs 剑修被叛), 无交叉.
- **核心系统**: mozun 无系统; 本作 寄生系统 (寿元 + 记忆代价) 是 unique 主轴 — mozun 不存在相似机制.
- **配色家族**: mozun = 紫霄 + 黑 + 金 + 朱砂; 本作 = 灰青 + 月白 + 寄生紫 + 寿元红. 主色族对比色路线, AI 图像生成两项目 ref-image 无互相污染风险.
- **face-mark 全 11 错位**: 见 §3.2 表, 11/11 ✅ pass.
- **场景**: mozun = 紫霄宫 / 玄炎宗 / 沧冥魔域 / 红袖招酒楼 / 药王谷 等; 本作 = 落雁渊 / 无寿崖 / 流烛盟主堂 / 忘川河边石塔群 / 澹江洲. 0 重叠.

### 4.3 vs 2025-2026 web 头部 IP DELTA

- **烬-字根 family**: web 显示「烬」字主角 + 宗门名 在 2025-2026 头部仙侠饱和 (沈烬 / 宁烬 / 长生烬 / 长月烬明 / 香蜜沉沉烬如霜). 本作主动避让 — 主角名 裴知秋 / 裴长砚 / 闻砚清, 神器 焚寿罗盘 / 归砚镜 / 长烟幡 — 0 个含「烬」字命名. ✅ avoid.
- **wode_moni CCI-1 万仙盟 forbidden zone**: 本作散修组织用「流烛盟」, 与 万仙盟 字根无关. ✅ avoid.
- **江砚 / 宁川 等 web 头部男主名**: 本作 裴知秋 / 裴长砚 全错位. ✅ avoid.

---

## 5. SIGN-OFF (Tier 6 grep pass)

| 验证项 | 结果 |
|---|---|
| **V-CR-2** BLACKLIST grep (≈ 145 atomic terms) | ✅ Pass. 8 个 hit 全部 cleared-as-critical-citation reference (《长月烬明》in 6 character bibles + 1 scene + 1 style_guide, 全部为 actor / 风格 benchmark / 负向 anti-pattern 参考, 非内容借用 — 见 §2). |
| **V-CR-3** 词源 line 存在 grep | ✅ Pass. 11 / 11 character bibles 各含 ## 词源 段引用 character_anonymization §3.x. |
| **V-CR-4** mozun_chongsheng 交叉 grep | ✅ Pass. shot prompts 0 mozun hits (post-shot03 patch). bible 内 N 个 cross-clearance footnote 注释性 (守护 face-mark 错位 / 视觉差异化), 非内容借用. |
| **V-CR-5** wode_moni 万仙盟 forbidden zone | ✅ Pass. 0 hits. 散修组织本作用「流烛盟」, CCI-1 forbidden zone 清空. |
| **V-CR-6** 角色 / 场景 一句话锁定 byte-identical 跨 shot | ✅ Pass. shot01-shot07 中所有 角色 line + 场景 line 与 bible row #10 + scene row #8 byte-identical (parent 已 grep). |
| **V-CR-7** 三 empty baseline 补抓 gap | ✅ Acknowledged. cong_jianshu_xiuxing / gou_zai_xiuxianjie / zhutian_daozu 三本基线下载为空, 不阻 ep01; 用户可在 ep02+ stage 6 启动前补抓 (per stage-5 sign-off item #3). |

**Stage-5 grep-pass timestamp**: 2026-05-24T06:54Z (Tier 4 close) + 2026-05-24T06:55Z (Tier 5 grep run).

**Final V-CR SIGN-OFF**: ✅ **PASS — 0 unresolved BLACKLIST hits**. 8 个 critical-citation reference 全部 cleared as 渲染方向参考 / 负向 anti-pattern, 非内容借用. mozun + wode_moni + 14-baseline 三层 grep 均 0 actual 借用.

---

*生成自 spec-driven 流水线 `xianxia_new-20260524-101931` Tier 5 + Tier 6. 本文件 review by user 后 closure of ep01 MVP.*
