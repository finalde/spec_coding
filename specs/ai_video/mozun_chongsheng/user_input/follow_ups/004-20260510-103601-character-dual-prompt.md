# Follow-up draft 004 — 2026-05-10

Summary: 把每个角色的「参考素材」文件从 ① 单个静帧立绘 prompt 升级为 ② 同一文件内的双 prompt：第一段「文字生图片」（即原立绘 prompt，用 Seedream / Midjourney / Imagen / Flux 等 text-to-image 模型出 PNG）+ 第二段「文字生视频 reference」（NEW，用 Kling / Sora / Veo / Seedance 出 12s 360° 转身样片含 5 句中文标准台词，用于 v2 audio-aware 视频管线锁定形象 + 声线 + 节奏）。两段 prompt 各自封装在 markdown code fence 内，**用户可一键 copy-paste**到对应模型；文件内同时保留 well-structured 结构（章节标题 / 用法说明 / 5 句台词配音对照表）。

## 用户原话

> 对于每个人物，帮我生成两段可以直接copy paste 的prompt 一段是文字生图片，一段是文字是文字生成video reference，在同一个文件里，可以直接copy paste 并且是 well structured

## 背景

Follow-up 003 把 rule #12 抽象成 model-agnostic 二件套（视频 shot prompt + 静帧 seam-frame prompt）。本 follow-up 004 在 character pipeline 加一个**第三层 reference**：360° 转身样片 + 5 句标准台词的 video reference，与现有 PNG 立绘并存（PNG 作为图像锚点；turntable 作为 video 锚点 + 声线锚点）。

讨论详见同会话 prior turn：
- Seedance 当前 text-to-video，不吃 video reference，但 turntable 视频可作为未来 audio-aware video-to-video 模型（Veo 3 / Sora-audio / Runway Gen-3）的 input。
- Kling 当前 image-to-video，主管线可以用立绘 PNG 生成 turntable 视频；turntable 一旦渲出，可作为后续 shot 的 visual continuity 强参考。
- v1 visual-only 管线下，turntable 内嵌的 5 句中文台词是 planning-only metadata；进入 audio-aware 管线后，台词激活为唇形 + 声线 reference。

## (A) 新文件格式 — 双 prompt + 标准台词表

每个角色的参考素材文件保留在原路径 `characters/ref_images/{中文名}-{身份}-立绘.md`（filename 沿用 legacy alias，避免大规模 path rename），结构改为：

```
# {中文名} · {身份} — 参考素材双 prompt

参考: characters/{中文名}-{身份}.md
画幅: 9:16 竖屏 / 4K 原生分辨率

---

## 1️⃣ 文字生图片 prompt — Seedream / Midjourney / Imagen / Flux

> 用法: 复制下方代码块整段，粘贴到 text-to-image 模型；输出角色立绘 PNG。

```text
{完整 image prompt as one copy-paste block}
```

---

## 2️⃣ 文字生视频 reference prompt — Kling / Sora / Veo / Seedance

> 用法: image-to-video 模型 — 输入 ①号生成的 PNG + 复制下方代码块整段；text-to-video 模型 — 直接复制下方代码块整段。
> 输出: 12s 360° 顺时针环绕样片，全身可见三视图，含 5 句中文标准台词（音画同步唇形对齐）。

```text
{完整 turntable + dialogue prompt as one copy-paste block}
```

### 5 句标准台词（中文，配音演员对照表）

| # | 台词 | 用途 | 时段 | 情绪基调 |
| --- | --- | --- | --- | --- |
| 1 | 我是{中文名}。 | 中性自报家门 | 0-3s | 平稳 / 中音 |
| 2 | {标志台词，from bible} | 锁定声线威压 / 情绪基调 | 3-6s | {character-specific} |
| 3 | {低声 / 内敛 line} | 低音域 / 私语 | 6-9s | {character-specific} |
| 4 | {高声 / 爆发 line} | 高音域 / 怒喝 | 9-10.5s | {character-specific} |
| 5 | 一、二、三、四、五。 | 节奏 / 咬字 / 口音校准 | 10.5-12s | 平稳 / 清晰 |
```

## (B) 5 句标准台词设计原则

- **第 1 句**：永远是 `"我是{中文名}。"` —— 中性自报家门，建立声线 baseline。
- **第 2 句**：从角色 bible 的 `## 标志台词或口头禅` 第 1 条直接 copy；如该字段填「无（默剧角色）」则用一句符合角色定位的零度宣言（如叶无尘乞丐时期：「我也曾，是个修魔的人」）。
- **第 3 句**：低声 / 内敛 / 私语，从 `## 性格 / 动机` 的「关键弱点」或「反差点」推导。例：沧冥「魂火不灭，便是归期」；苏璃月「师门所教，未必为真」。
- **第 4 句**：高声 / 怒喝 / 爆发，从 `## 弧光` 关键拐点 / 「关键场景」战斗高潮推导。例：沧冥「我必让你魂飞魄散！」；柳红袖「红袖招今日就关了，但你也别想活着出去！」。
- **第 5 句**：永远是 `"一、二、三、四、五。"` —— 数数，校准节奏 / 咬字 / 口音。

每句要 byte-stable（一旦写入文件后跨 follow-up 不再随机改），便于配音演员重复对照。

## (C) Turntable 视频 prompt 锁定字段

video reference prompt 的 `场景` / `镜头` / `光线` / `渲染样式` / `比例` / `时长` / `负向` 字段对所有 10 个角色 **byte-stable identical**，只有 `角色:` 字段（一句话锁定 + 12.4-A inline 展开）和 `动作` 段的 5 句台词内容因角色而异。这样：

- 10 个角色的 turntable 输出在镜头语言上一致，便于剪辑期 cut 在一起做角色介绍合集。
- 棚拍标准布光（中性灰 cyc + 三点布光 5500K/4500K/7000K）让模型不会被环境干扰，专注角色本身。
- 12s 一圈 + 标头中景 + 70mm 焦距感是 turntable 行业标准。

锁定字段（每份文件 byte-identical）：

```
场景: 中性灰 #808080 摄影棚 cyc wall 无缝背景，地面同灰，无家具无道具，环境光均匀。
镜头: 标头中景（约 70mm 焦距感）+ 360° 顺时针环绕镜，匀速一圈完成；起幅与落幅均为正面（0° = 360°）。
光线 / 色调: 三点布光 — key 45° 顶左 5500K 主光 + fill 右下柔光 4500K 辅光 + back rim 顶后冷光 7000K 轮廓光；地灰 #808080 不抢主体。影视棚拍标准布光，无戏剧化色温偏移。
节奏: 中（匀速旋转 + 自然呼吸 + 台词稳定播报）。
渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实皮肤布料质感 + 实拍剧照风 + 唇形对齐音画同步。
比例: 9:16
时长: 12s
```

video-specific 负向（追加在 image 通用负向之上）：

```
不要 镜头穿模 / 不要 唇形与台词错位 / 不要 加速跳帧 / 不要 横向运镜大偏移 / 不要 镜头停顿（要匀速）/ 不要 角色跑出画面 / 不要 镜头回切倒退（要单向 360°）
```

## (D) Rule #12.5（NEW）写入 `agent_refs/project/ai_video.md`

新增 rule #12.5 「角色 reference 双 prompt 文件 — character dual-prompt template」，包含：

- 文件位置约定（`characters/ref_images/{role}-立绘.md` 兼容 legacy alias；新项目可用 `characters/refs/{role}.md`）
- 双 prompt 文件 schema（① text-to-image 块 + ② text-to-video turntable 块）
- 5 句标准台词设计原则
- Turntable 锁定字段（10 个角色 byte-identical）
- v1 visual-only ↔ v2 audio-aware 模型路径切换的兼容性说明

## 期望行为

1. mozun_chongsheng 10 个角色每人一个 `-立绘.md` 文件，**双 prompt 双 copy-paste 块**，well-structured。
2. 用户可一次 copy ①号代码块到 Seedream 出 PNG；之后一次 copy ②号代码块到 Kling（带 PNG 作 input image）出 12s turntable 视频。
3. 5 句标准台词在每个角色文件以 markdown 表格列出，便于后续配音演员（人工 / TTS）对照。
4. 现有 follow-up 001 / 002 / 003 锁定保持有效（影视级真人写实 / 18-35 看似青春 / 中文文件命名 / model-agnostic 模板 / shot prompt 字段补齐）。

## Out of scope

- 不重新生成 shot prompts（ep01-ep05 100 视频 shot prompts 已在 follow-up 003 完成 schema 对齐，本 follow-up 不动）。
- 不实际渲染 PNG / 视频（仅产 prompt 文件）。
- 不引入英文 prompt variant；本项目 follow-up 002 已锁定中文工作流。
- 不替换现有 `characters/ref_images/` 路径（filename `-立绘.md` 沿用 legacy alias，避免大规模 spec.md / validation 引用 update）。
- 不为 ep06-ep60 stage-4 regen 范围内的角色（如有）预生成 dual-prompt 文件——这是后续 stage-4 regen 的工作。
