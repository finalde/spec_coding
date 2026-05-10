# Follow-up draft 008 — 2026-05-10

Summary: 解决 AI 生成角色「面孔同质化」问题——目前 10 个 mozun 角色在 Seedream 生成的立绘 / Kling 生成的视频中面部特征过于相似（"AI 通用脸"）。增强每个角色的**面部差异化标签**：脸型 / 五官辨识度 / 标志特征点（痣 / 疤 / 牙齿 / 眉形细节 / 下颌线 / 单双眼皮 / 眼距等），并为整个项目锁定**亚洲俊男靓女审美锚点**（中日韩明星 + 古装真人剧演员 specific 类比，替代/补充 follow-up 001 的 generic "live-action 真人剧" 锚点）。

## 用户原话

> another improvement for the charactor part, right now, the AI generated charactors, their face looks very much the same, so enance the prompt a bit so each AI genreate a bit different ficial for each charactor. Also, 审美请参考亚洲的俊男靓女

## 问题诊断

当前 10 个角色的 锁定描述符 #2「面貌」字段（per follow-up 002）描述维度有限，主要是「眉 / 眼 / 鼻 / 唇 / 轮廓」5 个粗维度，且 token 比较通用（如「剑眉锋锐」「丹凤眼眼尾微挑」「鼻梁高挺」「薄唇略压」「轮廓俊朗冷峻」）。多个角色的描述模板高度相似，AI 模型聚合后输出趋于同一张「亚洲青年俊朗脸」。

举例对比：
- 沧冥: 剑眉锋锐 + 丹凤眼眼尾微挑 + 鼻梁高挺 + 薄唇略压 + 轮廓俊朗冷峻
- 韩夺心 (类似)
- 司空玄 (类似)

→ 没有能让 AI 区分的**唯一标识符**（如沧冥应有「鬓边一缕银」，但已是发型字段；面貌字段没有锁定独特点）。

## (A) 增强 character bible 锁定描述符 #2「面貌」字段（rule #12.1 amend）

锁定描述符 #2「面貌」从单一字段扩展为 **6 子项**：

| 子项 | 内容示例 | 必填 |
|---|---|---|
| 脸型 | 国字脸 / 鹅蛋脸 / 瓜子脸 / 方圆脸 / 鸭蛋脸 / 长脸 / 心型脸 / 菱形脸 (8 类) | ✅ |
| 眉形 | 剑眉 / 卧蚕眉 / 柳叶眉 / 一字眉 / 八字眉 / 远山眉 (6 类) + 粗细 + 走向（高挑 / 平直 / 微聚） | ✅ |
| 眼型 | 丹凤眼 / 桃花眼 / 杏仁眼 / 狐狸眼 / 三角眼 / 圆眼 (6 类) + 单/双眼皮 + 眼距（窄 / 中 / 宽）+ 眼尾细节（上挑 / 下垂 / 平） | ✅ |
| 鼻型 | 高挺直鼻 / 蒜头鼻 / 鹰钩鼻 / 朝天鼻 / 蓄水鼻 / 短鼻 (6 类) + 鼻翼宽窄 | ✅ |
| 唇型 + 牙齿 | 薄唇 / 厚唇 / M 唇 / 一字唇 / 樱桃唇 (5 类) + 唇色 + (可选) 牙齿特征（虎牙 / 整齐贝齿 / 含微豁齿） | ✅ |
| 标志特征点 | **唯一识别符**：痣 / 疤 / 胎记 / 单耳钉 / 不对称纹 / 眼角细纹 / 下颌特征 / 法令纹 等 — 每角色 1-2 项 byte-stable 唯一标记 | ✅ |

**关键设计：「标志特征点」是每角色的 unique-identifier**，AI 模型据此区分相似五官的角色。例：
- 沧冥: 右眼下方 0.5cm 朱砂痣（魔尊本相专属，转生后消失再现于叶无尘觉醒后）— short token: 右眼下方朱砂痣
- 叶无尘: 左眉骨末端贴一小银环（乞丐 piercing 残留）— short token: 左眉骨小银环
- 苏璃月: 左耳垂雪白珍珠耳坠（紫霄圣女法器之一）— short token: 左耳珍珠坠
- 柳红袖: 右唇角红点小痣（妖娆点睛）— short token: 右唇角红点小痣
- 苓夭夭: 鼻尖偏右一颗淡褐色雀斑（凡人少女特征）— short token: 鼻尖淡褐雀斑
- 白月清: 眉心一抹极淡红痕（伪君子真身泄漏点）— short token: 眉心淡红痕
- 赵焚天: 左颊一道暗血红古旧伤疤（炼器烫伤）— short token: 左颊古旧暗红疤
- 方鼎元: 下颌左侧一颗黑色长痣 + 三缕短须 — short token: 下颌左侧黑长痣
- 韩夺心: 右眼角一道斜向疤（剑修战伤）— short token: 右眼角斜疤
- 司空玄: 白瓷面具下左颈侧十字暗纹刺青（神识殿主标记，规避与沧冥右眼下方 location 冲突）— short token: 左颈侧十字暗纹

## (B) 锁定亚洲俊男靓女审美锚点（rule #12.4 v2 + style_guide.md amend）

follow-up 001 锁定的「live-action 真人剧」类比锚点（《琉璃》《长月烬明》《苍兰诀》《沉香如屑》《与凤行》）保留，但**补充更具体的演员定位**，且明确为**亚洲（中日韩）俊男靓女审美**：

**男性角色锚点（俊男）：**

| 类型 | 代表演员 / 角色 | 用于 |
|---|---|---|
| 冷峻威压型 | 罗云熙（澹台烬）/ 成毅（战神 / 司凤）/ 王鹤棣（东方青苍） | 沧冥 / 司空玄 |
| 清亮少年型 | 龚俊（楚黎）/ 任嘉伦（焰青）/ 张凌赫（陆向晚） | 叶无尘 |
| 烈火宗主型 | 杨洋（叶修）/ 陈飞宇 / 邓为 | 赵焚天 |
| 道貌温润型 | 李沁 (反性别参考气质) / 陈晓 / 朱一龙（沈巍） | 方鼎元 / 白月清 |
| 剑修冷锋型 | 张凌赫 / 王鹤棣 / 张哲瀚（温客行） | 韩夺心 |

**女性角色锚点（靓女）：**

| 类型 | 代表演员 / 角色 | 用于 |
|---|---|---|
| 仙气清冷 | 白鹿（黎苏苏）/ 虞书欣（小兰花）/ 杨紫（颜淡） | 苏璃月 |
| 妖娆烟火 | 章若楠 / 田曦薇 / 赵丽颖（古早妖娆扮相） | 柳红袖 |
| 清纯灵动 | 文淇 / 田曦薇（丹宁）/ 李兰迪 | 苓夭夭 |
| 端庄秀丽 | 倪妮 / 刘亦菲（古装）/ 杨颖 | 白月清（伪君子表层） |

**通用锚点关键词（每份 prompt 必含 ≥ 2 个）：**

```
亚洲俊男靓女 / 东方传统五官 / 三庭五眼东方面孔
中日韩古装剧主角脸 / 仙侠真人剧主演级颜值
真实电影选角 / 大陆古装一线演员 / 港台日韩明星脸
```

**通用负向追加（每份 prompt 必含全部）：**

```
不要 AI 生成同质化脸 / 不要 AI 通用脸 / 不要 模板化俊男靓女 / 不要 千篇一律的丹凤眼锥子脸
不要 西方审美面孔 / 不要 欧美选角风 / 不要 浓眉大眼欧化
不要 同款脸 / 不要 跨角色面孔重复 / 不要 网红脸
```

## (C) 应用范围

1. **agent_refs/project/ai_video.md**：
   - rule #12.1 「锁定描述符 #2 面貌」从单字段扩展为 6 子项 + 「标志特征点」必填（unique-identifier 概念）。
   - rule #12.4 v2 「角色 inline 展开」要求 加上 face-differentiator token + Asian aesthetic 锚点。
   - 新增 cross-character 一致性规则：10+ 角色任两人面貌 6 子项不能同时全相同；至少 2 子项 + 标志特征点不同。

2. **mozun_chongsheng/style_guide.md**：
   - 新增段「§ 亚洲俊男靓女审美锚点」：男 / 女角色类型 → 演员锚点表 + 通用关键词 + 通用负向。
   - 该段被 character bible 立绘 prompt + character ref turntable prompt + shot prompt 共同 re-paste。

3. **mozun_chongsheng/characters/{role}.md**（10 份 bible 更新）：
   - 锁定描述符 #2 面貌 字段从单行扩展为 6 子项表。
   - 「标志特征点」字段添加 byte-stable unique-identifier per character（per (A) 列表）。
   - 锁定描述符 #10 一句话锁定 增加 face-differentiator token（如「右眼下方朱砂痣」for 沧冥），让一句话锁定本身就 carry 唯一识别符。

4. **mozun_chongsheng/characters/ref_images/{role}-立绘.md**（10 份 character ref 更新）：
   - ② 视频 prompt 代码块的 `角色:` 字段 inline 展开补 face-differentiator token + Asian aesthetic 类比演员（specific to character type）。
   - 「负向」段补「不要 AI 同质化脸 / 不要 跨角色面孔重复 / 不要 西方审美 / 不要 网红脸」等 11 项。

5. **mozun_chongsheng/episodes/ep01..ep05/prompts/shot{NN}.md**（50 份 shot 文件更新）：
   - 视频 prompt 代码块的 `角色:` 字段 inline 展开同步加 face-differentiator token（与 character ref 文件 byte-identical）。
   - 通用负向段补 11 项 AI-同质化负向。

## (D) 跨角色相似性预防 — 一致性规则

新增 rule #12.7「Cross-character facial differentiation」：

任两个 character bible 的 锁定描述符 #2 面貌 6 子项必须满足：
- 至少 **2 子项 + 标志特征点** 不同。
- 「标志特征点」绝不重复（每角色独占 1-2 个 byte-stable 唯一标记）。
- 即使同类型角色（两个剑修 / 两个仙女）也须有可视化区分点。

Stage-6 validator 扩展：跨 10+ 角色 bible scan 6 子项 + 标志特征点 cross-character similarity 矩阵；任两人 ≥ 5 子项相同 + 标志特征点缺失 = blocker。

## 期望行为

1. Seedream 立绘渲染 10 角色 PNG → **每张脸辨识度高**（脸型 / 五官 / 唯一标志）；不再「五大宗主一张脸」。
2. Kling / Seedance 视频 turntable + shot videos → 跨角色 + 跨集 一致性高（标志特征点 byte-stable 不漂移）。
3. 整体审美定位**亚洲俊男靓女古装真人剧主演级**，类比演员明确（每角色锁定 1-2 个真人参考），不再「AI 通用 cinematic 脸」。
4. follow-up 001 / 002 / 003 / 004 / 005 / 006 / 007 全部锁定保持有效。

## Out of scope

- 不重新生成 prompt body 内容（动作 timed beats / 台词 / 节奏 / 视觉描述等保持不变）。
- 不实际渲染。
- 不修改 character bible 弧光 / 关键场景 / 标志能力 / 性格 / 标志台词 / 配音参考 等其他段（仅改 锁定描述符 #2 + 标志特征点 + 锁定描述符 #10）。
- 不修改 ep06-ep60 stage-4 regen 范围（后续按 rule #12.1 v2 + #12.7 出文）。
- 不引入英文 prompt variant；保持中文工作流。
- 不解决 follow-up 002 遗留的「沧冥 三十出头 / 看似二十五」inline 不一致问题（独立 surgical follow-up）。
