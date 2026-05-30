---
worker_id: script-shotlist-01-ep01
stage: 6
role: worker
work_unit_id: script_and_shotlist-ep01
status: complete
blockers: []
confidence: high
---

# 第一集 · 落雁渊 · shotlist（7 shots · 约 120s）

> 本表锁定 ep01 的 7 个 shot 的元数据契约，供 Tier-4 shot-prompt workers 逐 shot 展开 `shots/shotNN.md`。每个 shot 的 `时长` 在 ai_video.md rule 6 的 3–15s 区间内（shot04 / shot05 / shot06 / shot07 个别超过 15s 时已显式拆分注记于「seam-frame contract / 备注」列，由 Tier-4 worker 拆成 ≤ 15s 的子段并以 seam frame 衔接，但本 shot 在剧情节拍层面是一个不可拆的 beat）。所有「主要角色 / 主要场景 / 一句话锁定」严格 byte-identical 引用自 `characters/*.md` 第 10 行与 `scenes/*.md` 第 8 行。

## 7-shot 表

| shot_id | 时长 (s) | 景别 | 运动 | 主要角色 | 主要 prop | 主要场景 | hook summary（≤20 字） | seam-frame contract | cover_frame | cliffhanger class |
|---|---|---|---|---|---|---|---|---|---|---|
| shot01 | 3 | 中近景 + 仰拍 | 升降镜（雷劫降临，自下而上） | 裴长砚（前世剑修 archived）— 修长直立 肤冷白 #e8d8d0 暗褐瞳 左眼下 0.3cm 灰青胎记 青灰长袍 #7a8a8a 玉冠束发 | 渡劫前置剑（剑鞘黑革 #1a1a14 + 剑柄缠青绸 #7a8a8a） + 雷劫剑光 + 崖顶残剑 | 无寿崖 — 白梧桐林环绕悬崖 中心青石残剑 月夜紫黑 #2a0a3a + 残血暗 #5a1a14 | 雷劫第三道 + 背后剑光穿胸 | 前帧 = cold open 蓝绿底 placeholder（无前帧）；lastframe = 剑尖自胸口浮血 + 闪白预备帧 → 接 shot02.startframe（黑底白字字幕「他们曾是他赴汤蹈火的人。」） | false | 反差 |
| shot02 | 15 | 大特写 + 中近景交替（pair 切） | Match-on-eye + 快剪 hard cut 顿挫 | 裴长砚（前世剑修 archived）— 修长直立 肤冷白 #e8d8d0 暗褐瞳 左眼下 0.3cm 灰青胎记 青灰长袍 #7a8a8a 玉冠束发 / 卫长烛（赤霞门掌门 正派叛者 #1）— 端正修长 漆黑束玉冠 左眉上 1cm 剑痕浅疤 红黑剑袍 #f5f5f0 + #5a1a14 / 应砚之（朝堂太师嫡子 正派叛者 #2）— 文人清瘦 漆黑束朱漆冠 下颌右 0.3cm 黑痣 沉檀木官袍 #3a2a1a + 御金 #a87838 / 戚归砚（流烛盟元老 cover · 忘川教暗投 truth）— 江湖壮硕 短束马尾草绳 左虎口 1cm 剑疤 散修土褐 #8c6a4a + 内衬深紫 #2a0a3a 一闪 | 卫长烛递剑（赤霞剑） + 应砚之 玉笏 + 戚归砚 酒杯 + 内衬深紫翻领（dual-affiliation 视觉根脉） + 闪白闪黑过 | 无寿崖 — 白梧桐林环绕悬崖 中心青石残剑 月夜紫黑 #2a0a3a + 残血暗 #5a1a14（pair #1–#3，前帧暖场景闪回） + 朝堂烛影 inline 闪回（应砚之 后帧） + 江湖客栈 inline 闪回（戚归砚 前帧） | 三叛者 reasons-to-trust → reasons-to-die 上半段（卫 / 应 / 戚） | **注: 多角色 cover-frame 全员同框（pair 切总 8 face frames），prompt 长度上限按 rule #12.4-E multi-character cover-frame 例外条款放宽**。前帧 = shot01.lastframe（剑尖浮血 + 闪白）；lastframe = 戚归砚 内衬深紫一闪定格 + 顿挫节奏过 → 接 shot03.startframe（池洇 雨夜火光前帧） | false | 真相揭露 + 双重身份 |
| shot03 | 12 | 大特写 + 中近景交替（pair 切） | Match-on-eye + 快剪 hard cut 顿挫 + 容漪 cameo 一帧惊鸿插入 | 裴长砚（前世剑修 archived）— 修长直立 肤冷白 #e8d8d0 暗褐瞳 左眼下 0.3cm 灰青胎记 青灰长袍 #7a8a8a 玉冠束发 / 池洇（流烛盟杀手长老 散修叛者 #4）— 修长阴柔 漆黑低马尾 左颊耳骨 0.8cm 斜疤 散修土褐 #8c6a4a + 黑革窄袖 / 阮惘（忘川教三长老 魔门叛者 #5）— 清冷修长 灰黑束低髻 右眼角 0.5cm 三点纹烫印 深紫黑长袍 #2a0a3a 半黑纱 / 言息（忘川教教主 季终 BOSS）— 修长威压 灰白长髯 骨白头冠 鼻梁中 0.3cm 横伤 深紫黑长袍 #1a0524 / 容漪（散修女主 ep05+）— 轻盈纤细 灰青衫 #7a8a8a 银白点 #d8d8d0 浅银发半披 右耳后 0.4cm 月牙痣 | 池洇 双短刀 + 茶盘（前帧） + 阮惘 骨白碎冰刃 + 救援白袍（前帧） + 言息 焦黄黑卷半展开 + 骨色寿牌（前世名「裴长砚」金红光屑） + 檀香（前帧） + 容漪 灰青绸帕（cameo 一帧惊鸿） | 无寿崖 — 白梧桐林环绕悬崖 中心青石残剑 月夜紫黑 #2a0a3a + 残血暗 #5a1a14（pair #4–#6 后帧） + 前世师门 / 学堂 / 崖下白袍 inline 闪回（pair 前帧） + 苇草洲 inline cameo（容漪 一帧旁观，落雁渊 黎明态预告） | 三叛者 reasons-to-trust → reasons-to-die 下半段（池 / 阮 / 言）+ 容漪 cameo 一帧 | **注: 多角色 cover-frame 全员同框（4 betrayers + 容漪 cameo 共 5 face frames + 言息 BOSS 视觉预告），prompt 长度上限按 rule #12.4-E multi-character cover-frame 例外条款放宽; CC-3 highest-risk artifact 之一 — 与 shot02 共同构成 ep01 倒叙 montage container，Tier-4 worker 应 LAST 写作此 shot 以锁住其他 6 shot 的字符串**。前帧 = shot02.lastframe（戚归砚 内衬深紫一闪定格）；lastframe = montage 收束硬字幕「他们都死过他一次 / 这一回——」闪黑帧 → 接 shot04.startframe（落雁渊 渊口高处灰晨俯瞰） | false | 真相揭露 + 牺牲反转 |
| shot04 | 20 | 大全景 → 中近景（缓推） | 拉镜 + 跟随镜（自渊口高处下降至渊底童身） | 裴知秋（重生弱体 state A）— 微瘦含胸 肤虚浮 #cab8a8 左眼下 0.3cm 灰青胎记 麻布灰青长袍 #7a8a8a | 鸟骨白堆（落雁渊 §2.2 鸟骨白 #d8d8d0） + 苇草青 #7a8a5a + 童身（病初愈含胸） | 落雁渊 — 深陷山渊渊底白鸟骨苇草 灰青岩壁 重生灰晨 #9c8a8a + 苇草青 #7a8a5a | 七岁童身渊底睁眼 + 内心 OS 茫然 | 前帧 = shot03.lastframe（montage 收束闪黑帧）；lastframe = 童子低头望胸前 + 胸前白光将起一帧 → 接 shot05.startframe（罗盘自胸前皮下浮出 0.3cm）。**注**: 本 shot 时长 20s 超 rule 6 单 shot 15s 上限，Tier-4 worker 须拆为 shot04a (0:30–0:42 / 12s 苏醒) + shot04b (0:42–0:50 / 8s 觉知童身 + 推近胸前) 两个子段，子段以 seam frame 衔接（shot04a.lastframe = shot04b.startframe = 童子低头望胸前定格），剧情节拍仍为一个 beat | false | 同理心 |
| shot05 | 25 | 大特写（罗盘） + 特写（系统弹窗） + 大特写（瞳色一闪） | 推镜（罗盘自胸前皮下浮出） + 顿挫（寄生升级 motif 三拍） + 升降镜（aura 自下而上） | 裴知秋（重生弱体 state A）— 微瘦含胸 肤虚浮 #cab8a8 左眼下 0.3cm 灰青胎记 麻布灰青长袍 #7a8a8a | **焚寿罗盘 — 24 格青铜盘 / 盘面冷光晕 #5a7a8a + #4a1a5a 双层 / 指针黑铁** + 系统弹窗硬字幕「叮——焚寿罗盘 觉醒 / 修为 +1 阶（练气一层）/ 寿命 24 / 24 格」金字 #a8842c 黑底银边 #f5f5f0 + 寿命红 #a82c2c 计数器 + 嘴角血迹一线（薄）+ 鬓边骤白一缕 + 皮下青脉 0.5s + 母亲童谣记忆光晕飘散 | 落雁渊 — 深陷山渊渊底白鸟骨苇草 灰青岩壁 重生灰晨 #9c8a8a + 苇草青 #7a8a5a（+ 焚寿罗盘 cold light 叠加，画面整体色温向 6500K 冷漂移 0.3s 背景失色） | **NFR-9 寄生升级 motif 五拍位** + 罗盘嵌入 + 寿元代价首兑现 | 前帧 = shot04.lastframe（童子低头望胸前 + 白光将起）；lastframe = 罗盘缓嵌回皮下 + 外见微凸 + 冷光晕未散 + 童子抬眼望渊口苇草定格 → 接 shot06.startframe（童子立起 + 麻布长袍下摆滴水）。**注**: 本 shot 时长 25s 超 rule 6 单 shot 15s 上限，Tier-4 worker 须拆为 shot05a (0:50–0:55 / 5s 寄生升级 motif 三拍 byte-identical from style_guide §5.2) + shot05b (0:55–1:05 / 10s 系统弹窗停留 + 记忆光晕飘散) + shot05c (1:05–1:15 / 10s 罗盘嵌回 + 童子内心 OS「二十四格 · 是倒数」+ 抬眼) 三个子段，子段以 seam frame 衔接（motif 三拍内部 hard cut 不另拆 seam）；NFR-9 motif 完整性必须落在 shot05a，作为 stage-5 V-CV-9 grep 单元 | false | 倒计时 |
| shot06 | 20 | 中近景（童身侧坐于水边） + 大特写（水面映童面 + 指划字） | 推镜（自童身后越肩望水面） + 慢镜 50%（指划字一笔一划） | 裴知秋（重生弱体 state A）— 微瘦含胸 肤虚浮 #cab8a8 左眼下 0.3cm 灰青胎记 麻布灰青长袍 #7a8a8a | 渊底水洼（水面映童面 + 灰青底色） + 水边石面（被指尖蘸水划下「知 秋」二字） + 后期软字幕台词「我又活了一回。」 | 落雁渊 — 深陷山渊渊底白鸟骨苇草 灰青岩壁 重生灰晨 #9c8a8a + 苇草青 #7a8a5a（水边视角） | 自取新名「裴知秋」+ 标志台词 #1 首落 | 前帧 = shot05.lastframe（罗盘嵌回 + 童子抬眼）；lastframe = 童子坐于水边 + 胸前罗盘冷光晕一闪 + 水面「知 秋」二字字迹未消定格 → 接 shot07.startframe（镜头自童子背后越肩望渊口苇草远处剪影立起）。**注**: 本 shot 时长 20s 超 rule 6 单 shot 15s 上限，Tier-4 worker 须拆为 shot06a (1:15–1:25 / 10s 童子立起 + 走至水边 + 蹲下 + 水面映童面) + shot06b (1:25–1:35 / 10s 指划「知 秋」+ 标志台词 #1「我又活了一回。」+ 缓拉) 两个子段，子段以 seam frame 衔接（shot06a.lastframe = shot06b.startframe = 童子右手食指伸出蘸水定格） | false | 镜像对照 |
| shot07 | 25 | 越肩（自童子背后望渊口剪影） + 中近景（剪影 turn） + **特写（师父正脸闪一帧）** + 全黑底 + 中景（楷体字幕） | 推镜（缓推剪影） + Match-on-action（剪影 turn → 正脸 hard cut） + 闪黑转场（per style_guide §8.4 闪黑词典） + 字幕过 | 裴知秋（重生弱体 state A）— 微瘦含胸 肤虚浮 #cab8a8 左眼下 0.3cm 灰青胎记 麻布灰青长袍 #7a8a8a（背影越肩） / 闻砚清（前世师父 archived）— 清瘦长髯 灰白束发 右眉上 0.5cm 斜疤 月白浅金长袍 #f5f5f0（剪影 → 正脸闪一帧；与 ep01 倒叙 montage 中已死的师父 byte-identical 同人） | 师父月白浅金长袍 #f5f5f0 + 灰白束玉冠半髻 + 右眉上 0.5cm 斜疤（正脸帧硬契约） + **黑底楷体大字硬字幕「第二集 即将揭晓」月白 #f5f5f0 + 寄生紫 #4a1a5a 描边** + 副位宋体小字金字「死过他的人——为何还活着？」 | 落雁渊 — 深陷山渊渊底白鸟骨苇草 灰青岩壁 重生灰晨 #9c8a8a + 苇草青 #7a8a5a（渊口苇草丛 + 雾色） + 全黑底（字幕段） | **NFR-10 cliffhanger** + 师父正脸闪一帧 + 闪黑 + 「第二集 即将揭晓」 | 前帧 = shot06.lastframe（童子坐水边 + 「知 秋」字迹）；lastframe = 「第二集 即将揭晓」楷体大字硬字幕停留 1.5s 后定格帧（**= cover_frame**，抖音 / 红果封面安全区已验：字幕居中 y ≈ 600 + 黄金视觉中心 + 1/4 缩略图仍可辨「第二集」字样 + 副位金字小字「死过他的人——为何还活着？」即钩字）→ 接 ep02.shot01.startframe（待 ep02 stage-6 启动时锁定，placeholder = 黑底渐亮至落雁渊渊底苇草晨光）。**注**: 本 shot 时长 25s 超 rule 6 单 shot 15s 上限，Tier-4 worker 须拆为 shot07a (1:35–1:48 / 13s 越肩望剪影 + 推镜 + 剪影 turn build) + shot07b (1:48–1:51 / 3s 正脸闪一帧 + 「砚水自清，何须问浊。」气声 + 闪黑转场) + shot07c (1:51–2:00 / 9s 黑底楷体大字字幕停留 + 副位钩字浮起 + 字幕定格) 三个子段，子段以 seam frame 衔接（剪影 turn 与正脸 hard cut 之间为 Match-on-action 锁定，无 seam frame；闪黑帧 = shot07b.lastframe = shot07c.startframe） | **true** | 反差 + 真相揭露（cliffhanger payload） |

---

## seam-frame chain

> 每个 shot 的 lastframe.png 必须 byte-identical 与下一个 shot 的 startframe.png 一致（per ai_video.md rule 11 seam-frame 契约），用以让 Kling / Seedance 跨 shot 续接无闪烁；shot01 是 cold open，无前帧，以蓝绿底 `#1a3038` placeholder 起；shot07 是 ep01 cliffhanger，lastframe = ep02.shot01.startframe（待 ep02 stage-6 启动时锁定）。

| seam # | 前 shot.lastframe | 后 shot.startframe | 内容描述 |
|---|---|---|---|
| 0 | cold open 蓝绿底 `#1a3038` placeholder | shot01.startframe | 无寿崖月夜紫黑全景慢起 + 雷云压顶 |
| 1 | shot01.lastframe | shot02.startframe | 裴长砚 剑尖自胸口浮血 + 闪白预备帧 → 黑底白字字幕「他们曾是他赴汤蹈火的人。」一闪 |
| 2 | shot02.lastframe | shot03.startframe | 戚归砚 内衬深紫一闪定格（dual-affiliation 视觉根脉收束） → 池洇 雨夜火光前帧（前世师门茶烟温白闪回起） |
| 3 | shot03.lastframe | shot04.startframe | montage 收束硬字幕「他们都死过他一次 / 这一回——」闪黑帧 → 落雁渊渊口高处灰晨俯瞰 + 鸟骨白 + 苇草青 |
| 4 | shot04.lastframe | shot05.startframe | 童子低头望胸前 + 白光将起一帧 → 罗盘自胸前皮下浮出 0.3cm + 冷光晕初亮 |
| 5 | shot05.lastframe | shot06.startframe | 罗盘缓嵌回皮下 + 外见微凸 + 童子抬眼望渊口定格 → 童子立起 + 麻布长袍下摆滴水 + 走向水边 |
| 6 | shot06.lastframe | shot07.startframe | 童子坐水边 + 胸前罗盘冷光晕一闪 + 水面「知 秋」二字字迹未消 → 镜头自童子背后越肩望渊口苇草远处剪影立起 |
| 7 | shot07.lastframe | ep02.shot01.startframe（placeholder） | 「第二集 即将揭晓」楷体大字硬字幕停留 1.5s 定格帧 = `cover_frame: true` → ep02.shot01.startframe（待 ep02 stage-6 启动时锁定，placeholder = 黑底渐亮至落雁渊渊底苇草晨光） |

---

## CC-3 montage container 注（Tier-4 worker 强契约）

shot02 + shot03 共同构成 ep01 0:03–0:30 倒叙 montage container（27s 总，前 15s + 后 12s 拆分）。三验证器（V-CV-7 multi-character expansion 警戒 / V-CV-4 byte-identical 一句话锁定 跨 6 betrayer cameo 漂移 / V-CV-1 NFR-1 单 shot prompt body ≤ 2000 字软上限 ≤ 2500 字硬上限）联合识别此两 shot 为 ep01 最高风险单元。Tier-4 worker 必须：

1. **shot02 + shot03 LAST 写**：先完成 shot01 / shot04 / shot05 / shot06 / shot07 共 5 shot 的 prompt，锁定所有非 montage 角色 + 场景的 byte-identical 字符串；最后再合成 shot02 + shot03，以已落字符串为基础再扩 6 betrayer + 容漪 cameo + 言息 BOSS 视觉预告所需的全部 角色一句话锁定（共 8 个 byte-identical 来源）。
2. **prompt 长度按 rule #12.4-E multi-character cover-frame 例外条款放宽**：shot02 + shot03 各自 ≤ 4000 字硬上限（而非默认 ≤ 2500），允许 8 角色 byte-identical 一句话锁定 + 12 对 reasons-to-trust / reasons-to-die frame 描述 + pair 切顿挫 timing beats 全 inline。
3. **face-mark 守护**：6 betrayers + 容漪 cameo 的 face-differentiator 必须在每对 pair frame 中至少出现一次（V-CV-8 cross-mozun face-mark 错位守护硬契约）：
   - 卫长烛 左眉上 1cm 剑痕浅疤（pair #1 后帧雷光照出）
   - 应砚之 下颌右 0.3cm 黑痣（pair #2 后帧朝堂沉檀木冷视镜头）
   - 戚归砚 左虎口 1cm 剑疤 + 内衬深紫一闪（pair #3 后帧风掀翻领）
   - 池洇 左颊耳骨 0.8cm 斜疤（pair #4 后帧雷光浮出）
   - 阮惘 右眼角 0.5cm 三点纹烫印（pair #5 后帧冷光下浮出）
   - 言息 鼻梁中 0.3cm 横伤（pair #6 后帧黑卷半展开瞬间）
   - 容漪 右耳后 0.4cm 月牙痣（cameo 一帧惊鸿，束发半髻偶现）
4. **dual-affiliation 视觉根脉**：戚归砚 pair #3 后帧的「内衬深紫 #2a0a3a 一闪 + 风吹翻领」是 ep17 揭穿 + ep35 reveal 的 ep01 视觉伏笔，Tier-4 worker 在 prompt body 必须标注 `（伏笔 — dual-affiliation 视觉根脉, ep17 + ep35 兑现）`。
