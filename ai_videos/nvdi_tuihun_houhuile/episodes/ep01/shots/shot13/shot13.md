---
worker_id: regen-nvdi-ep01-shot13
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot13
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> **陈国公**闻言，深深吸了一口气，将双手抱拳举至额前，垂下了头，声音是老臣特有的沉稳低音，裹着一层克制的怒意与认命般的倦：“老臣明白。老陈……一定亲自进京请罪。”一句话说尽了chenguogong_place_holder的隐忍。他身侧，陈凡跪姿不变，内心的那场独白早已收束，面上的废柴姿态依旧完美无瑕。

---

# ep01 / shot13 · 陈国公抱拳礼, 表态进京请罪

## Shot context

- Summary: 中近景推镜, chenguogong_place_holder抱拳礼至额前, 老臣沉稳低音带克制怒意, 表态亲自进京请罪。
- Characters: chenguogong_place_holder
- Scene: 陈国公府正厅
- Duration: 9s
- Reference uploads: s1_陈国公府正厅.mp4 (15s walk-through 场景 reference) + 场景立绘 PNG 静帧

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集13镜视

参考: `chenguogong_place_holder, bg2_朝南_厅门_place_holder`
角色: `chenguogong_place_holder — 深紫一品国公朝服 玉带紫金冠 长须银白及胸 老臣沉稳; 面部辨识特征: 下颌长须及胸, 银白渐染`
情节: `chenguogong_place_holder闻言，深深吸了一口气，将双手抱拳举至额前，垂下了头，声音是老臣特有的沉稳低音，裹着一层克制的怒意与认命般的倦：“老臣明白。老陈……一定亲自进京请罪。”一句话说尽了chenguogong_place_holder的隐忍。chenguogong_place_holder身侧，chenfan_place_holder跪姿不变，内心的那场独白早已收束，面上的废柴姿态依旧完美无瑕。`
场景: `bg2_朝南_厅门_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `中近景 + 缓推, 镜头缓缓推向chenguogong_place_holder抱拳礼至额前`
走位: `chenguogong_place_holder跪于跪礼区东侧、面向北 (朝taijian_place_holder) 抱拳表态; taijian_place_holder立于chenguogong_place_holder正北方画外。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 chenguogong_place_holder; 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0.0-3.0秒 chenguogong_place_holder抬手抱拳礼至额前; 3.0-6.0秒 老臣沉稳低音"老臣明白"; 6.0-9.0秒 带克制怒意"一定亲自进京请罪", 头垂下镜头推近`
台词 / 字幕: `陈国公(沉稳低音带克制怒意):"老臣明白。老陈……一定亲自进京请罪。"`
光线 / 色调: `日间顶左斜光 偏冷金黄, 透高窗格栏漏入; 面光显皱纹与银白须色; 主色 沉香木 辅灰青 点朱红 高光暖白`
节奏: `快切`
渲染样式: `影视级真人写实 · 电影感 · 超高清高动态范围 · 真实毛孔细节 · 真人皮肤真实质感 · 亚洲俊男靓女 · 三庭五眼东方面孔 · 古装仙侠剧主演级颜值 · 照片级写实感 强化`
比例: `9:16`
时长: `9秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦——视频不烧字幕、不依赖自动配音; 后期用 `tools/mux_av.py` 把台词 MP3 + BGM 合回 MP4。
> 音色锁定: 陈国公 全剧/跨集复用同一音色 id (`GG-duke-01`); 不同镜只改情绪/语速, 不换音色 (听觉一致性)。

```text
01集13镜 · 台词配音

角色: 陈国公
音色(锁定·全剧复用 · GG-duke-01): 老臣沉稳低音 · 威严克制 · 国语标准
情绪: 沉稳低音 · 克制怒意 · 老父颜面尽失之倦 (「老陈」处略顿)
语速: 中速 (按情绪微调; 内心独白偏慢)
类型: 在画对白
台词: 老臣明白。老陈……一定亲自进京请罪。
时长目标: 9秒
```
