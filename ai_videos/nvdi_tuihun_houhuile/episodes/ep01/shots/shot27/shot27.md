---
worker_id: regen-nvdi-ep01-shot27
stage: 6
role: worker
work_unit_id: shot_prompt-ep01-shot27
status: complete
blockers: []
confidence: high
---

## Chapter excerpt (from chapters/0001-第1集 接旨退婚.md)

> 空旷的正厅里，**陈凡**独自立于长案之前。案上一边，是那卷废chenfan_place_holder的退婚诏书；一边，是那枚足以翻天的暗纹令牌；而chenfan_place_holder立于二者之间，身形挺拔如一座孤峰。日光自高窗斜斜地落下来，在chenfan_place_holder脚下拉出一道长长的影子。《女帝，》chenfan_place_holder在心底无声地开口，目光沉沉，《这盘棋，才刚刚开始。》

---

# ep01 / shot27 · 陈凡立于诏书与令牌之间，孤峰独立

## Shot context

- Summary: *(新增续写)* chenfan_place_holder独立长案前, 一边退婚诏书一边暗纹令牌, 身形挺拔如孤峰, 画外音"棋局才刚开始".
- Characters: chenfan_place_holder
- Scene: 陈国公府正厅
- Duration: 8s
- Reference uploads: chenfan_place_holder 7s turntable mp4 (characters/c1_chenfan_place_holder, 全身挺拔锚) + 场景 s1_陈国公府正厅 walk-through mp4 (长案 + 高窗斜光)

## 视频 prompt — 复制下方代码块到视频生成模型

```text
01集27镜视

参考: `chenfan_place_holder, bg1_朝北_长案主位_place_holder`
角色: `chenfan_place_holder — 玉白世家锦袍 长发披肩半束玉冠 暗琥珀瞳 风流慵懒装废 右眉尾 0.2厘米 浅疤; 本镜 反转态 — 身形挺拔孤峰独立, 桃花眼底冷金锐光稳`
情节: `空旷的正厅里，chenfan_place_holder独自立于长案之前。案上一边，是那卷废chenfan_place_holder的退婚诏书；一边，是那枚足以翻天的暗纹令牌；而chenfan_place_holder立于二者之间，身形挺拔如一座孤峰。日光自高窗斜斜地落下来，在chenfan_place_holder脚下拉出一道长长的影子。《女帝，》chenfan_place_holder在心底无声地开口，目光沉沉，《这盘棋，才刚刚开始。》`
场景: `bg1_朝北_长案主位_place_holder — 三开间沉香木长案厅 灰青地砖 朱漆梁柱 日间顶左斜光 朱红诏书`
镜头: `全景 + 缓拉, 机位自chenfan_place_holder缓缓拉远, 显厅堂纵深与孤峰独立; 9:16 竖屏, 主体居中`
走位: `chenfan_place_holder独立于沉香木长案前 (北)、立于案上诏书与令牌之间; 大体面向南 (望厅门方向), 孤峰独立; 厅内空无他人。 厅内系国公府私宅正厅 (非朝堂金殿), 本镜入镜人物仅 chenfan_place_holder; 别无他人, 不得增添任何其他人物 (无群臣 / 侍从 / 围观人群 / 路人)。`
动作: `0-3秒 chenfan_place_holder立案前定姿、诏书令牌在案; 3-6秒 机位缓拉远、厅堂纵深展开、脚下长影拉出; 6-8秒 孤峰独立定格`
台词 / 字幕: `画外音（陈凡 内心独白, 冷沉慢语速, 偏冷锐）:《女帝，棋局才刚开始。》 · 在画人物口型: 陈凡全程闭口、嘴唇不动、无说话口型 (内心独白 画外音 为画外配音 / 字幕, 非现场出声; 严禁把 画外音 台词对到陈凡嘴上); **但内心所想须靠面部表情 / 眼神 / 神态演出来** —— 嘴不动, 内心情绪全凭表情反应 (眼神由倦转锐 / 微表情 / 唇线收紧或微扬 / 瞳孔变化 / 神色冷峻), 不靠开口、不对口型`
光线 / 色调: `日间偏冷金黄顶左斜光自高窗格栏斜落, 脚下灰青地砖拉出长影, 沉香木暖光, 诏书烫金与令牌暗纹各踞案侧; 孤峰仪式感`
节奏: `快切, 拉镜显纵深, 孤峰独立为视觉落点`
渲染样式: `影视级真人写实 电影感 超高清高动态范围 真实毛孔细节 真人皮肤真实质感 亚洲俊男靓女 三庭五眼东方面孔 古装仙侠剧主演级颜值 照片级写实感 强化`
比例: `9:16`
时长: `8秒`
```

---

## 台词配音 prompt — 复制下方代码块给 TTS / Seedance 生成台词 MP3

> 用途: 本镜台词的专业配音 MP3 生成 (高端 AI 情感 TTS)。台词音轨与视频解耦——视频不烧字幕、不依赖自动配音; 后期用 `tools/mux_av.py` 把台词 MP3 + BGM 合回 MP4。
> 音色锁定: 陈凡 全剧/跨集复用同一音色 id (`CF-male-lead-01`); 不同镜只改情绪/语速, 不换音色 (听觉一致性)。

```text
01集27镜 · 台词配音

角色: 陈凡
音色(锁定·全剧复用 · CF-male-lead-01): 偏低中音 · 清润底子 · 国语标准 (装废态加懒散尾音 / 已褪态去尾音转冷锐 / 内心 OS 转冷沉, 三种处理同一音色)
情绪: 冷沉慢语速 · 偏冷锐
语速: 中速 (按情绪微调; 内心独白偏慢)
类型: 内心独白 (画外音 V.O.)
台词: 女帝，棋局才刚开始。
时长目标: 8秒
```
