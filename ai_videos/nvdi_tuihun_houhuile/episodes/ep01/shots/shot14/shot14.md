---
worker_id: regen-nvdi-ep01-shot14
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot14
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> 得了这句话，**太监**这才满意地颔了颔首，拂尘一甩，转过身，朝着厅门的方向不紧不慢地退去。脚步声与拂丝扫过空气的窸窣声一前一后，将这场宣旨的余威，一并带出了正厅。跪礼区里，只留下父子二人，和地上那卷刺目的朱红诏书。

---

# ep01 / shot14 · 太监颔首甩拂尘, 转身朝厅门退去

## Shot context

- Summary: 全景跟镜, taijian_place_holder颔首拂尘一甩, 转身朝厅门方向退去, 留chenguogong_place_holder和chenfan_place_holder在跪礼区。
- Characters: taijian_place_holder / chenfan_place_holder / chenguogong_place_holder
- Scene: 陈国公府正厅
- Duration: 5s
- Reference uploads: s1_陈国公府正厅.mp4 (15s walk-through 场景 reference) + 场景立绘 PNG 静帧

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集14镜视

参考: `taijian_place_holder, chenfan_place_holder, chenguogong_place_holder, bg2_朝南_厅门_place_holder`
角色: `taijian_place_holder — 内监紫袍银云纹 持拂尘 中年面 左脸颊 0.3厘米 淡褐痣 老练阴柔; 面部辨识特征: 左脸颊一颗淡褐痣 0.3厘米；chenfan_place_holder — 玉白世家锦袍 长发披肩半束玉冠 暗琥珀瞳 风流慵懒装废 右眉尾 0.2厘米 浅疤; 面部辨识特征: 右眉尾 0.2厘米 浅疤；chenguogong_place_holder — 深紫一品国公朝服 玉带紫金冠 长须银白及胸 老臣沉稳; 面部辨识特征: 下颌长须及胸, 银白渐染`
情节: `得了这句话，taijian_place_holder这才满意地颔了颔首，拂尘一甩，转过身，朝着厅门的方向不紧不慢地退去。脚步声与拂丝扫过空气的窸窣声一前一后，将这场宣旨的余威，一并带出了正厅。跪礼区里，只留下chenguogong_place_holder和chenfan_place_holder，和地上那卷刺目的朱红诏书。`
场景: `bg2_朝南_厅门_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `全景 + 跟镜, 机位跟随taijian_place_holder转身朝厅门退去, 末尾微落幅留chenguogong_place_holder和chenfan_place_holder于跪礼区`
走位: `taijian_place_holder自厅中长案前转身、朝南向厅门方向退去 (由面南转为背对镜头走向南门); chenguogong_place_holder和chenfan_place_holder仍跪于跪礼区 (taijian_place_holder行进路线之南侧)、面向北。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 taijian_place_holder (转身背对镜头退场)、chenfan_place_holder 与 chenguogong_place_holder (跪、面向北); 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0.0-1.5秒 taijian_place_holder颔首; 1.5-3.0秒 拂尘一甩转身; 3.0-5.0秒 朝南向朱漆双扇木门方向退去, chenguogong_place_holder和chenfan_place_holder留跪礼区`
台词: `(脚步声 + 拂尘声, 无台词) · 在画人物口型: 全程闭口、嘴唇不动、无任何说话口型 (默剧——纯面部表情与肢体动作演出, 不开口/不念词/不出声; 严禁自动配音或对口型)`
光线 / 色调: `日间顶左斜光 偏冷金黄, 透高窗格栏漏入落地砖方块光斑; 主色 沉香木 辅灰青 点朱红 高光暖白`
节奏: `快切`
渲染样式: `影视级真人写实 · 电影感 · 超高清高动态范围 · 真实毛孔细节 · 真人皮肤真实质感 · 亚洲俊男靓女 · 三庭五眼东方面孔 · 古装仙侠剧主演级颜值 · 照片级写实感 强化`
比例: `9:16`
时长: `5秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦, 后期用 `tools/mux_av.py` 合回 MP4。

本镜为 **默剧 / 静默镜，无台词**，无需生成台词 MP3。
（脚步声 + 拂尘声 (太监转身退场) — 属音效 SFX，后期单独配，不在台词 TTS 范围。）
