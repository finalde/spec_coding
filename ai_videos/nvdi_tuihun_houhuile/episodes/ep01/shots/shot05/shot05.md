---
worker_id: regen-nvdi-ep01-shot05
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot05
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> **太监**并不停顿，将那卷黄绫往上一举，宣出了最要紧的一句：“今解除朕与其之婚约。钦此。”短短一句，落在这空旷的正厅里，余音在朱漆梁柱间荡了一圈才散。香炉的烟被这声音惊得晃了晃，又重新笔直起来。退婚二字一出，便是板上钉钉，再无转圜。

---

# ep01 / shot05 · 太监宣解除婚约, 诏书前举

## Shot context

- Summary: 中景锁机位, taijian_place_holder宣读解除婚约, 黄绫诏书前举, 念毕"钦此"。
- Characters: taijian_place_holder / chenguogong_place_holder / chenfan_place_holder (后二者前景背影、未露正脸)
- Scene: 陈国公府正厅
- Duration: 6s
- Reference uploads: s1_陈国公府正厅.mp4 (15s walk-through 场景 reference) + 场景立绘 PNG 静帧

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集05镜视

参考: `taijian_place_holder, chenguogong_place_holder, chenfan_place_holder, bg1_朝北_长案主位_place_holder`
角色: `taijian_place_holder — 内监紫袍银云纹 持拂尘 中年面 左脸颊 0.3厘米 淡褐痣 老练阴柔; 面部辨识特征: 左脸颊一颗淡褐痣 0.3厘米；chenguogong_place_holder (前景下方背影) — 深紫一品国公朝服 玉带 紫金冠 银白长须 年长沉稳体态; chenfan_place_holder (前景下方背影) — 玉白世家锦袍 黑色长发披肩 半束白玉冠 年轻挺拔体态`
情节: `taijian_place_holder并不停顿，将那卷黄绫往上一举，宣出了最要紧的一句：“今解除朕与其之婚约。钦此。”短短一句，落在这空旷的正厅里，余音在朱漆梁柱间荡了一圈才散。香炉的烟被这声音惊得晃了晃，又重新笔直起来。退婚二字一出，便是板上钉钉，再无转圜。`
场景: `bg1_朝北_长案主位_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `中景 + 缓慢推近 (随诏书前举、念毕「钦此」的语势极缓推近taijian_place_holder), 腰部以上`
走位: `taijian_place_holder立于厅中长案前、面向南宣「今解除…钦此」; chenguogong_place_holder和chenfan_place_holder跪于taijian_place_holder南侧跪礼区、面向北 (chenguogong_place_holder和chenfan_place_holder位于镜头前景下方, 背影/未露正脸, 本镜聚焦taijian_place_holder)。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 taijian_place_holder (正面)、chenguogong_place_holder (前景下方背影: 深紫一品朝服 / 紫金冠 / 银白长须 / 年长体态) 与 chenfan_place_holder (前景下方背影: 玉白锦袍 / 黑色长发披肩 / 白玉冠 / 年轻挺拔); 两道背影衣色与发型迥异、须各按其参考分别渲染, 严禁两道背影雷同或都渲染成 chenfan_place_holder; 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0.0-2.5秒 taijian_place_holder双手将黄绫诏书前举, 朗声"今解除朕与其之婚约"; 2.5-4.5秒 诏书举定, 阴柔中音; 4.5-6.0秒 念毕"钦此", 拂尘轻甩收势`
台词 / 字幕: `太监(宣):"今解除朕与其之婚约。钦此。"`
光线 / 色调: `日间顶左斜光 偏冷金黄, 透高窗格栏漏入; 诏书举处烫金光泽; 主色 沉香木 辅灰青 点朱红 高光暖白`
节奏: `快切`
渲染样式: `影视级真人写实 · 电影感 · 超高清高动态范围 · 真实毛孔细节 · 真人皮肤真实质感 · 亚洲俊男靓女 · 三庭五眼东方面孔 · 古装仙侠剧主演级颜值 · 照片级写实感 强化`
比例: `9:16`
时长: `6秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦——视频不烧字幕、不依赖自动配音; 后期用 `tools/mux_av.py` 把台词 MP3 + BGM 合回 MP4。
> 音色锁定: 太监 全剧/跨集复用同一音色 id (`TJ-eunuch-01`); 不同镜只改情绪/语速, 不换音色 (听觉一致性)。

```text
01集05镜 · 台词配音

角色: 太监
音色(锁定·全剧复用 · TJ-eunuch-01): 阴柔尖细中音 · 偏老阴鸷 · 国语标准
情绪: 一锤定音 · 「钦此」收势利落
语速: 中速 (按情绪微调; 内心独白偏慢)
类型: 在画对白
台词: 今解除朕与其之婚约。钦此。
时长目标: 6秒
```
