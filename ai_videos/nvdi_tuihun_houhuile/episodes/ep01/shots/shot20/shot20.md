---
worker_id: regen-nvdi-ep01-shot20
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot20
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> **陈凡**缓缓转过身来，正脸迎上chenguogong_place_holder那惊骇万分的目光。那张素来含倦带笑的脸，此刻冷峻如覆了一层薄霜，桃花眼底的冷金锐光已经稳稳凝住，再无半分散乱游移。“父亲，”chenfan_place_holder声线低沉而清晰，一字一句都像是斟酌过的，“请罪的折子，不必递了。”

---

# ep01 / shot20 · 陈凡转身正脸冷峻，眼底冷金已稳

## Shot context

- Summary: *(新增续写)* chenfan_place_holder转身正脸迎chenguogong_place_holder惊骇目光, 神色冷峻、眼底冷金锐光稳定, 一句"请罪折子不必递了"定调.
- Characters: chenfan_place_holder / chenguogong_place_holder (前景背影、未露正脸)
- Scene: 陈国公府正厅
- Duration: 9s
- Reference uploads: chenfan_place_holder 7s turntable mp4 (characters/c1_chenfan_place_holder, 正脸特写锚) + 场景 s1_陈国公府正厅 walk-through mp4

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集20镜视

参考: `chenfan_place_holder, chenguogong_place_holder, bg1_朝北_长案主位_place_holder`
角色: `chenfan_place_holder — 玉白世家锦袍 长发披肩半束玉冠 暗琥珀瞳 风流慵懒装废 右眉尾 0.2厘米 浅疤; 本镜 反转态 — 正脸冷峻如霜, 桃花眼底冷金锐光稳稳凝住, 右眉尾浅疤清晰可读；chenguogong_place_holder (前景背影/侧面, 未露正脸) — 深紫一品国公朝服 玉带 紫金冠 银白长须 年长沉稳体态`
情节: `chenfan_place_holder缓缓转过身来，正脸迎上chenguogong_place_holder那惊骇万分的目光。那张素来含倦带笑的脸，此刻冷峻如覆了一层薄霜，桃花眼底的冷金锐光已经稳稳凝住，再无半分散乱游移。“父亲，”chenfan_place_holder声线低沉而清晰，一字一句都像是斟酌过的，“请罪的折子，不必递了。”`
场景: `bg1_朝北_长案主位_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `中近景起、随chenfan_place_holder转身正脸缓慢推近至面部特写——冷峻冷金锐光稳定时贴近, 强化定调张力; 9:16 竖屏, 头肩入画`
走位: `chenfan_place_holder立于厅中、转身面向南 (面向南侧门内的chenguogong_place_holder); chenguogong_place_holder立于南侧门内、面向北 (本镜chenguogong_place_holder位于镜头前景、背影/侧面、未露正脸; chenfan_place_holder正脸为焦点)。chenguogong_place_holder和chenfan_place_holder南北相对。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 chenfan_place_holder (正面)、chenguogong_place_holder (前景背影/侧面、未露正脸); 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0-3秒 缓缓转身、侧脸转正; 3-6秒 正脸冷峻、眼神冷冽锐利沉定 (纯神态, 非发光), 与画外chenguogong_place_holder对视; 6-9秒 开口出声、唇线锐定`
台词: `陈凡（外表台词, 低沉清晰, 偏冷锐, 已褪装废尾音）:"父亲，请罪的折子，不必递了。"`
光线 / 色调: `日间偏冷金黄顶左斜光透高窗格栏, 正脸主光提亮显冷峻, 桃花眼冷冽锐利 (纯神态, 非眼睛发光), 沉香木暖辅光; 锋芒压场`
节奏: `快切, 转身定脸为视觉锚, 台词为落点`
渲染样式: `影视级真人写实 电影感 超高清高动态范围 真实毛孔细节 真人皮肤真实质感 亚洲俊男靓女 三庭五眼东方面孔 古装仙侠剧主演级颜值 照片级写实感 强化`
比例: `9:16`
时长: `9秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦——视频不烧字幕、不依赖自动配音; 后期用 `tools/mux_av.py` 把台词 MP3 + BGM 合回 MP4。
> 音色锁定: 陈凡 全剧/跨集复用同一音色 id (`CF-male-lead-01`); 不同镜只改情绪/语速, 不换音色 (听觉一致性)。

```text
01集20镜 · 台词配音

角色: 陈凡
音色(锁定·全剧复用 · CF-male-lead-01): 偏低中音 · 清润底子 · 国语标准 (装废态加懒散尾音 / 已褪态去尾音转冷锐 / 内心 OS 转冷沉, 三种处理同一音色)
情绪: 低沉清晰 · 偏冷锐 · 不再有懒散尾音
语速: 中速 (按情绪微调; 内心独白偏慢)
类型: 在画对白 (已褪装废态)
台词: 父亲，请罪的折子，不必递了。
时长目标: 9秒
```
