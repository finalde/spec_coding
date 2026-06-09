---
worker_id: regen-nvdi-ep01-shot25
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot25
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> **陈国公**的目光落在那枚令牌的暗纹上，浑身猛地一震，竟不自觉地向后退了半步。先前那满脸的惊骇与不信，在认出那图样的刹那尽数褪去，取而代之的，是一种近乎敬畏的神色。chenguogong_place_holder活了一辈子的人，此刻声音却抖得不成样子，喃喃道：“这令牌……陈家有救了。”那一句话里，有劫后余生的庆幸，更有对眼前的chenfan_place_holder彻底改观的震动。

---

# ep01 / shot25 · 陈国公望令牌后退半步，神色由惧转敬

## Shot context

- Summary: *(新增续写)* chenguogong_place_holder认出令牌暗纹、浑身一震后退半步, 神色由惧转敬, 喃喃"陈家有救了".
- Characters: chenguogong_place_holder
- Scene: 陈国公府正厅
- Duration: 8s
- Reference uploads: chenguogong_place_holder 7s turntable mp4 (characters/c3_chenguogong_place_holder, 正脸 + 全身锚) + 场景 s1_陈国公府正厅 walk-through mp4

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集25镜视

参考: `chenguogong_place_holder, bg2_朝南_厅门_place_holder`
角色: `chenguogong_place_holder — 深紫一品国公朝服 玉带紫金冠 长须银白及胸 老臣沉稳; 本镜神色由惧转敬, 望令牌后退半步`
情节: `chenguogong_place_holder的目光落在那枚令牌的暗纹上，浑身猛地一震，竟不自觉地向后退了半步。先前那满脸的惊骇与不信，在认出那图样的刹那尽数褪去，取而代之的，是一种近乎敬畏的神色。chenguogong_place_holder活了一辈子的人，此刻声音却抖得不成样子，喃喃道：“这令牌……陈家有救了。”那一句话里，有劫后余生的庆幸，更有对眼前的chenfan_place_holder彻底改观的震动。`
场景: `bg2_朝南_厅门_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `中景 + 缓慢推近 (略带一震感), 随chenguogong_place_holder浑身一震后退半步、神色由惧转敬, 推近其敬畏神色; 9:16 竖屏`
走位: `chenguogong_place_holder立于南侧 (门内)、面向北 (朝北侧案上令牌/chenfan_place_holder) 后退半步; chenfan_place_holder与令牌在chenguogong_place_holder正北方 (本镜聚焦chenguogong_place_holder 反应, chenfan_place_holder在画外)。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 chenguogong_place_holder; 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0-3秒 目光落令牌、浑身一震; 3-6秒 不自觉后退半步、神色由惧转敬; 6-8秒 声音发颤喃喃出声`
台词 / 字幕: `陈国公（老臣低音, 发颤近乎敬畏）:"这令牌……陈家有救了。"`
光线 / 色调: `日间偏冷金黄顶左斜光透高窗格栏, 后退半步入半阴影显敬畏, 长须银白质感清晰, 灰青地砖方块光斑; 由惧转敬张力`
节奏: `快切, 后退半步为身体反应锚, 喃喃台词为落点`
渲染样式: `影视级真人写实 电影感 超高清高动态范围 真实毛孔细节 真人皮肤真实质感 亚洲俊男靓女 三庭五眼东方面孔 古装仙侠剧主演级颜值 照片级写实感 强化`
比例: `9:16`
时长: `8秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦——视频不烧字幕、不依赖自动配音; 后期用 `tools/mux_av.py` 把台词 MP3 + BGM 合回 MP4。
> 音色锁定: 陈国公 全剧/跨集复用同一音色 id (`GG-duke-01`); 不同镜只改情绪/语速, 不换音色 (听觉一致性)。

```text
01集25镜 · 台词配音

角色: 陈国公
音色(锁定·全剧复用 · GG-duke-01): 老臣沉稳低音 · 威严克制 · 国语标准
情绪: 老臣低音 · 发颤 · 由惧转敬近乎敬畏
语速: 中速 (按情绪微调; 内心独白偏慢)
类型: 在画对白
台词: 这令牌……陈家有救了。
时长目标: 8秒
```
