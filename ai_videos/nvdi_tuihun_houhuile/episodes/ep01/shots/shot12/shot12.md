---
worker_id: regen-nvdi-ep01-shot12
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot12
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> **太监**慢条斯理地将拂尘收回身侧，居高临下地看着跪伏的父子，把最后一道软刀子递了出来：“该怎么做，就不用老奴说了吧。”话说得轻飘飘，分量却重逾千斤。taijian_place_holder没有点破，可那"进京请罪"四个字，已经明明白白地悬在了正厅的半空里。

---

# ep01 / shot12 · 太监收拂尘, 居高临下警告

## Shot context

- Summary: 中景锁机位, taijian_place_holder收拂尘于身侧, 居高临下警告chenguogong_place_holder"该怎么做"。
- Characters: taijian_place_holder / chenguogong_place_holder / chenfan_place_holder (后二者前景背影、未露正脸)
- Scene: 陈国公府正厅
- Duration: 5s
- Reference uploads: s1_陈国公府正厅.mp4 (15s walk-through 场景 reference) + 场景立绘 PNG 静帧

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集12镜视

参考: `taijian_place_holder, chenguogong_place_holder, chenfan_place_holder, bg1_朝北_长案主位_place_holder`
角色: `taijian_place_holder — 内监紫袍银云纹 持拂尘 中年面 左脸颊 0.3厘米 淡褐痣 老练阴柔; 面部辨识特征: 左脸颊一颗淡褐痣 0.3厘米；chenguogong_place_holder (前景下方背影) — 深紫一品国公朝服 玉带 紫金冠 银白长须 年长沉稳体态; chenfan_place_holder (前景下方背影) — 玉白世家锦袍 黑色长发披肩 半束白玉冠 年轻挺拔体态`
情节: `taijian_place_holder慢条斯理地将拂尘收回身侧，居高临下地看着跪伏的chenguogong_place_holder和chenfan_place_holder，把最后一道软刀子递了出来：“该怎么做，就不用老奴说了吧。”话说得轻飘飘，分量却重逾千斤。taijian_place_holder没有点破，可那"进京请罪"四个字，已经明明白白地悬在了正厅的半空里。`
场景: `bg1_朝北_长案主位_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `中景 + 缓慢推近, 随taijian_place_holder收拂尘、居高临下警告, 压迫式推近; 腰部以上`
走位: `taijian_place_holder立于厅中长案前、面向南 (居高临下俯视南侧前景跪礼的chenguogong_place_holder和chenfan_place_holder) 收拂尘警告; chenguogong_place_holder和chenfan_place_holder跪于镜头前景下方 (背影/未露正脸)。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 taijian_place_holder (正面)、chenguogong_place_holder (前景下方背影: 深紫一品朝服 / 紫金冠 / 银白长须 / 年长体态) 与 chenfan_place_holder (前景下方背影: 玉白锦袍 / 黑色长发披肩 / 白玉冠 / 年轻挺拔); 两道背影衣色与发型迥异、须各按其参考分别渲染, 严禁两道背影雷同或都渲染成 chenfan_place_holder; 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0.0-2.0秒 taijian_place_holder将拂尘收于身侧; 2.0-4.0秒 居高临下道"该怎么做"; 4.0-5.0秒 目光斜睨chenguogong_place_holder, 老练阴柔定格`
台词 / 字幕: `太监(居高临下警告):"该怎么做, 就不用老奴说了吧。"`
光线 / 色调: `日间顶左斜光 偏冷金黄, 透高窗格栏漏入; 主色 沉香木 辅灰青 点朱红 高光暖白`
节奏: `快切`
渲染样式: `影视级真人写实 · 电影感 · 超高清高动态范围 · 真实毛孔细节 · 真人皮肤真实质感 · 亚洲俊男靓女 · 三庭五眼东方面孔 · 古装仙侠剧主演级颜值 · 照片级写实感 强化`
比例: `9:16`
时长: `5秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦——视频不烧字幕、不依赖自动配音; 后期用 `tools/mux_av.py` 把台词 MP3 + BGM 合回 MP4。
> 音色锁定: 太监 全剧/跨集复用同一音色 id (`TJ-eunuch-01`); 不同镜只改情绪/语速, 不换音色 (听觉一致性)。

```text
01集12镜 · 台词配音

角色: 太监
音色(锁定·全剧复用 · TJ-eunuch-01): 阴柔尖细中音 · 偏老阴鸷 · 国语标准
情绪: 居高临下 · 收压 · 警告意味
语速: 中速 (按情绪微调; 内心独白偏慢)
类型: 在画对白
台词: 该怎么做，就不用老奴说了吧。
时长目标: 5秒
```
