# Follow-up draft 012 — 2026-05-10

Summary: 用户反馈生成的角色仍有两个问题: (1) 整体偏卡通 / 动漫感，不够像真人；(2) 多角色面孔仍偏相似。follow-up 008 引入了 6-子项 face-differentiation + 11 项 AI-同质化负向，但视觉效果不够。本 follow-up 升级两条线：(A) **真人写实强化锚点** — style_guide.md 新增更具体的 photorealism + 真人摄影元素 + 8K 高清细节 + 真实皮肤毛孔细节 + 真人演员档级别 + cinema-grade live-action film/photography 锚点；(B) **per-character 5-7 项 distinctive 微表情 / 微细节** — 每角色锁定 5-7 个独特微细节 (面部肌肉特征 / 眼睑纹路 / 鼻翼形态 / 颈部线条 / 嘴角下垂角度 / 法令纹深浅 / 喉结大小 / 下颌轮廓 等)，让 AI 生成时各角色面孔有更丰富的差异化数据点。

## 用户原话

> 生成的charactor还是有两个问题，一个是有点不想真人，有点像卡通动漫，请在提示词里加入信息使得人物更像真人，另外，多个人物之间过于相像，请加入人物面部描写细节，使得各个人物更有自己特色，但整体上审美请参考亚洲帅哥美女审美

## (A) 真人写实强化锚点

`style_guide.md § 渲染样式锁定` 段补强：

### 现有正向关键词（follow-up 001）保留:
```
影视级真人写实 / cinematic / photorealistic / live-action / 4K HDR / 8K
仙侠古装真人剧造型 / 实拍剧照风 / 现代电影级灯光
真实皮肤质感 / 真实布料质感 / 真实毛发质感
真人演员 / 三庭五眼东方面孔
```

### follow-up 012 新增正向关键词（每份 prompt 必含 ≥ 4 个）:
```
真实毛孔细节 / 真实皮肤纹理 / 真实皮肤微瑕 / pores visible / skin micro-texture
真人演员档级颜值 / casted real actor / live-action film grade casting
DSLR 拍摄 / 大画幅相机 / 85mm 人像镜头 / 50mm cinematic lens
影棚自然光 / 阳光散射 / 漫反射柔光 / global illumination 真实光线
ARRI / RED / Sony Venice 电影摄影机级别 / Netflix 4K HDR drama 标准
真人皮肤真实质感 / human skin shader / subsurface scattering
眼角细纹 / 法令纹 / 颈部肌理 / 头发光泽 / 唇纹细节 / 真实瞳孔反光
8K 写实人像 / 16K 大画幅 / RAW 摄影质感
```

### follow-up 012 新增负向关键词（每份 prompt 必含全部 14 项，extends follow-up 008 的 11 项）:
```
不要 anime style face / 不要 manga style / 不要 cartoon style / 不要 illustration / 不要 stylized
不要 over-smoothed skin / 不要 plastic skin / 不要 doll-like face / 不要 wax figure
不要 AI-generated face / 不要 AI artifact / 不要 generic AI face / 不要 same-face syndrome
不要 模糊轮廓 / 不要 缺乏皮肤细节 / 不要 over-airbrushed
```

(续 follow-up 008 的 11 项 AI-同质化负向 不变。)

## (B) Per-character 5-7 项 distinctive 微细节

每个 character bible 「锁定描述符 #11 标志特征点」字段从 1-2 项 cross-character mutex 标记**扩展为 5-7 项 distinctive micro-details**，覆盖面部解剖结构的 5 大维度 (眼 / 鼻 / 唇 / 下颌 / 皮肤)。每角色至少包含:

1. **眼周细节** — 上眼睑形态 / 卧蚕厚度 / 下眼袋 / 内眼角 / 眼尾纹
2. **鼻形细节** — 鼻头圆/尖度 / 鼻翼厚度 / 鼻孔形 / 山根高度
3. **唇形细节** — 上唇厚度 / 下唇厚度 / 唇峰锐度 / 唇角下垂或上扬
4. **下颌细节** — 下颌轮廓硬度 / 颧骨高度 / 下巴形 / 喉结
5. **皮肤细节** — 肤色冷暖 / 毛孔可见度 / 法令纹 / 颈纹 / 唯一标记 (痣 / 疤 / 胎记)

### 10 角色 distinctive 微细节锁定（follow-up 012）:

| 角色 | 5-7 项 distinctive 微细节 |
|---|---|
| c1_沧冥 | 上眼睑微肿、卧蚕 hardly visible / 鼻头窄尖、山根高、鼻翼薄 / 上唇略薄、下唇微厚、唇峰锐、唇角微抿 / 下颌方硬、颧骨高峭、下巴尖、喉结明显 / 肤冷白如玉、毛孔细密、无法令纹 / **右眼下方 0.5cm 朱砂痣** |
| c2_叶无尘 | 上眼睑薄、卧蚕浅、下眼袋微显、内眼角藏锋 / 鼻头小巧、鼻翼薄、山根中 / 上唇较薄、下唇略厚、唇峰柔、唇角自然 / 下颌瘦削、颧骨自然、下巴略尖、喉结微显 / 肤色微暗（乞丐风霜）、皮肤略糙、有微擦伤 / **左眉骨末端贴一小银环** |
| c3_苏璃月 | 双眼皮饱满、卧蚕明显、下眼袋无、内眼角圆、眼尾微下垂 / 鼻头圆秀、鼻翼薄、山根中 / 上唇厚度中等、下唇饱满、唇峰柔圆、唇角微上扬 / 下颌柔和、颧骨低平、下巴尖巧、无喉结 / 肤白如雪、毛孔近无、皮肤透亮 / **左耳垂雪白珍珠耳坠** |
| c4_柳红袖 | 双眼皮深、卧蚕厚、下眼袋微显（妖娆）、内眼角钩、眼尾上挑 / 鼻头略圆、鼻翼薄、山根中 / 上唇饱满、下唇厚、唇峰锐、唇角微上扬 / 下颌柔、颧骨稍高、下巴秀气、无喉结 / 肤色暖白带桃红、毛孔细、唇色朱红 / **右唇角红点小痣**、**唇珠点缀** |
| c5_苓夭夭 | 双眼皮浅、卧蚕饱满圆润、下眼袋无、内眼角圆、眼尾平直 / 鼻头小圆、鼻翼薄、山根浅 / 上唇较薄、下唇略厚、唇峰圆、唇角无下垂 / 下颌圆润、颧骨低、下巴圆、无喉结 / 肤色健康奶白、毛孔自然、有少量雀斑 / **鼻尖偏右一颗淡褐色雀斑**、**苹果肌饱满** |
| c6_白月清 | 双眼皮浅、卧蚕薄、下眼袋藏、内眼角平、眼尾微下垂 / 鼻头窄、鼻翼薄、山根高直 / 上唇薄、下唇均匀、唇峰柔、唇角平直 / 下颌方圆、颧骨自然、下巴秀、无喉结 / 肤色白净（端庄）、毛孔细密、温润有光 / **眉心一抹极淡红痕**（伪君子真身泄漏点） |
| c7_赵焚天 | 单眼皮重、卧蚕粗厚、下眼袋深（沧桑）、内眼角狭、眼尾上挑 / 鼻头圆肉、鼻翼宽厚、山根低 / 上唇厚、下唇厚、唇峰钝、唇角下垂 / 下颌方硬、颧骨高、下巴方、喉结大 / 肤色古铜、毛孔粗大、皮肤粗糙、有炼器烫疤 / **左颊一道暗血红古旧伤疤** |
| c8_方鼎元 | 双眼皮浅、卧蚕薄长、下眼袋微显、内眼角平、眼尾微下垂 / 鼻头窄、鼻翼薄、山根中 / 上唇薄、下唇略厚、唇峰柔、唇角平直 / 下颌瘦削、颧骨平、下巴方、喉结自然 / 肤色白净、毛孔细密、有 法令纹（道貌岸然） / **下颌左侧一颗黑色长痣**、**三缕短须** |
| c9_韩夺心 | 单眼皮硬、卧蚕窄薄、下眼袋紧、内眼角狭、眼尾极上挑 / 鼻头窄尖、鼻翼薄、山根高 / 上唇极薄、下唇均匀、唇峰锐、唇角下垂（剑修冷峻） / 下颌方硬、颧骨高、下巴尖、喉结明显 / 肤色冷白、毛孔细、皮肤紧致、剑伤疤 / **右眼角一道斜向疤** |
| c10_司空玄 | 单眼皮锋、卧蚕薄、下眼袋藏、内眼角窄、眼尾极上挑、双眼狐狸感 / 鼻头窄尖、鼻翼薄、山根高鹰钩 / 上唇薄、下唇薄、唇峰锐、唇角下垂、唇线狭 / 下颌窄菱形、颧骨高瘦、下巴尖锐、喉结明显 / 肤色冷白偏青、毛孔细密、皮肤紧致、有刺青 / **左颈侧十字暗纹刺青** |

每角色至少 6 项 distinctive 微细节 + 1 项 unique-identifier 标记，AI 生成时 5 大维度全锁定。

## (C) 应用范围

1. **`.claude/agent_refs/project/ai_video.md` rule #12.7 amend** — 锁定描述符 #2 面貌 6 子项 expand to 5-7 micro-details (rule #12.7 v2)；新增 「真人写实强化锚点」 段。
2. **`ai_videos/mozun_chongsheng/style_guide.md` § 渲染样式锁定** — 补强 photorealism 正向 8 项 + 14 项扩展负向。
3. **10 character bibles `c{N}_*.md`** — 锁定描述符 #11 标志特征点 字段 expanded to 5-7 micro-details (per § B 表)；锁定描述符 #2 面貌 6 子项 row 内 micro-details 同步扩展。
4. **10 character ref turntable prompts** (within c{N}_*.md 第二段) — `角色:` line inline 展开 carry 5-7 micro-details (新增 ~30-50 字 per character)；负向段补 14 项扩展 photorealism negatives。
5. **50 shot.md files 视频 prompt code block** — `角色:` line inline 展开同步 carry 5-7 micro-details；渲染样式 line append 8 项 photorealism positives；负向 line append 14 项扩展 photorealism negatives。

## (D) 期望行为

1. Seedream / Kling / Seedance 渲染时，prompt 提供更丰富的 face anatomy data → AI 生成各角色面孔差异更明显。
2. 「真人写实」与「8K 摄影」等关键词更密集出现 → AI 拉向真人摄影质感，远离 cartoon / illustration / smooth-skinned anime stylization。
3. 用户对比 ep01 shot01 (沧冥) vs ep01 shot03 (5 宗主同框) 时，每个角色的面部分辨度提高（无「同一张脸」感）。
4. follow-up 001-011 锁定 全部保持有效（不动 face-differentiator unique tokens / Asian aesthetic actor anchors / cN_/sN_ 命名 / 等）。

## Out of scope

- 不重新生成 prompt body 内容（动作 timed beats / 台词 / 节奏 / 镜头 / 视觉描述等保持不变）。
- 不实际渲染。
- 不修改 ep06-ep60 stage-4 regen 范围。
- 不修改 character bible 的 弧光 / 关键场景 / 标志能力 / 性格 / 标志台词 / 配音参考 等其他段（仅改 锁定描述符 #2 + #11 + 配音参考 演员锚点扩展）。
- 不解决 follow-up 002 遗留的「沧冥 三十出头 / 看似二十五」inline 不一致问题。
