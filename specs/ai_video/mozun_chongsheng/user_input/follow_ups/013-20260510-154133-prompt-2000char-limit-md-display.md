# Follow-up draft 013 — 2026-05-10

Summary: 两件事：(A) **强制 prompt 字数 ≤ 2000 字** — follow-up 008 / 012 添加的 photorealism 关键词 + 5-7 项 micro-details + Asian aesthetic 锚点累积过厚，多角色 shot 已达 4000-4500 字，超 Seedance / Kling 等模型实际可消化 prompt 的有效上限。Trim policy: 角色 inline expansion + 5-7 项 micro-details 仅保留在 character ref turntable prompt（用户上传 turntable.mp4 已 carry 该信息），shot prompt 仅保留 locked 一句话 + face-differentiator (~50-80 字 per char)；渲染样式 line 从 ~13 关键词 trim 到 ~9 核心关键词；负向 line 从 39 项 trim 到 24 项。(B) **Markdown-style field-label 视觉渲染** — webapp 渲染 ```text fenced code blocks 时，对 prompt body 的 `角色:` / `场景:` / `镜头:` / 等 field labels 应用 regex pre-pass + CSS pill highlight，让 prompt 在 UI 上看起来更像结构化 markdown 文档而非 plain text monospace 块；copy button 仍 copy 纯文本（不带 HTML markup）。

## 用户原话

> 请确保所有prompt字数在2000字以内，并且用类似与md的形式在UI上显示

## 当前 prompt 字数测量（baseline pre-013）

| Shot | 字数 |
|---|---|
| ep01/shot01 (1 char) | 2533 |
| ep01/shot03 (6 chars 同框) | 4516 |
| ep01/shot07 (6 chars 爽点峰值) | 4442 |
| ep04/shot05 (3 chars) | 4187 |
| ep04/shot08 (3 chars + dialogue) | 3996 |

50 shot files 中，预估 30%+ 文件超 2000 字。需 trim。

## (A) Trim policy — 三段优化

### 1. 角色 line trim (per char):

- **Pre-013** (post-012):
  ```
  {ref_c1_沧冥} 沧冥 — 黑长发束高马尾，黑金锦缎长袍金线绣兽，赤红丹凤眼俊朗锋锐，右眼下方朱砂痣，左手负后，魔气如墨。沧冥为高瘦劲健男子三十出头身高约 1.85m，黑发束半髻余发披至腰际鬓边一缕银，黑金高领大袍金色魔纹绣兽吞肩。面部微细节：上眼睑微肿、卧蚕浅、鼻头窄尖、唇峰锐、下颌方硬、颧骨高峭、肤冷白如玉、毛孔细密、无法令纹。
  ```
  (~250 字 per char)

- **Post-013**:
  ```
  {ref_c1_沧冥} 沧冥 — 黑长发束高马尾，黑金锦缎长袍金线绣兽，赤红丹凤眼俊朗锋锐，右眼下方朱砂痣，左手负后，魔气如墨。
  ```
  (~80 字 per char — drop the body inline 展开 + 5-7 项 micro-details；这些已在 `c1_沧冥.md` 文件中 + turntable mp4 reference 内 carry)

  **Logic**: 当 user 上传 turntable.mp4 作 video reference 时，AI 模型从该视频已 inherit 角色 face / body / 微细节；shot prompt 不需要再重复展开。Locked 一句话 + face-differentiator 足以 trigger AI 调用 reference 一致。

  对于 multi-character shot（如 ep01/shot03 6 chars），节省 6 × 170 ≈ 1020 字。

### 2. 渲染样式 line trim:

- **Pre-013**:
  ```
  渲染样式: 影视级真人写实 + cinematic + 4K HDR + 亚洲俊男靓女 + 东方传统五官 + 三庭五眼东方面孔 + 中日韩古装剧主角脸 + 仙侠真人剧主演级颜值 + DSLR 拍摄 + 真实毛孔细节 + 真人皮肤真实质感 + 真实皮肤微瑕
  ```
  (~140 字)

- **Post-013** (核心 9 keywords):
  ```
  渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实毛孔细节 + 真人皮肤真实质感 + 亚洲俊男靓女 + 三庭五眼东方面孔 + 仙侠真人剧主演级颜值
  ```
  (~80 字 — 留 photorealism 核心 5 + Asian aesthetic 核心 3 + cinematic 1 = 9 关键词)

### 3. 负向 line trim:

- **Pre-013** (39 项):
  ```
  负向: 不要 anime / 不要 cartoon / 不要 illustration / 不要 chibi / 不要 manga / 不要 国漫 / 不要 插画 / 不要 工笔 / 不要 水墨写意 / 不要 二次元 / 不要 CGI 3D render / 不要 塑料皮肤 / 不要 玩偶感 / 不要 卡通色 / 不要 AI 生成同质化脸 / 不要 AI 通用脸 / 不要 模板化俊男靓女 / 不要 千篇一律的丹凤眼锥子脸 / 不要 西方审美面孔 / 不要 欧美选角风 / 不要 浓眉大眼欧化 / 不要 同款脸 / 不要 跨角色面孔重复 / 不要 网红脸 / 不要 整容脸模板 / 不要 anime style face / 不要 manga style / 不要 cartoon style / 不要 illustration / 不要 stylized / 不要 over-smoothed skin / 不要 plastic skin / 不要 doll-like face / 不要 wax figure / 不要 AI-generated face / 不要 AI artifact / 不要 generic AI face / 不要 same-face syndrome / 不要 模糊轮廓
  ```
  (~600 字)

- **Post-013** (24 项 — 去重 + 选择代表):
  ```
  负向: 不要 anime / 不要 cartoon / 不要 illustration / 不要 manga / 不要 国漫 / 不要 二次元 / 不要 CGI 3D render / 不要 塑料皮肤 / 不要 玩偶感 / 不要 over-smoothed skin / 不要 wax figure / 不要 doll-like face / 不要 AI 通用脸 / 不要 同款脸 / 不要 跨角色面孔重复 / 不要 网红脸 / 不要 整容脸模板 / 不要 西方审美面孔 / 不要 欧美选角风 / 不要 模糊轮廓 / 不要 现代服饰 / 不要 文字水印 / 不要 多余手指 / 不要 镜头穿模
  ```
  (~340 字 — 去掉 anime/cartoon/manga style face 重复变体 + plastic skin 与 塑料皮肤 重复 + AI-generated face 与 AI 通用脸 重复 + same-face syndrome 与 跨角色面孔重复 重复 + 等约 15 项语义重复 negatives)

### 4. Total trim impact (multi-char 6-char shot estimate):

- 角色 line: 6 × (250 → 80) = 6 × 170 = **省 1020 字**
- 渲染样式 line: 140 → 80 = **省 60 字**
- 负向 line: 600 → 340 = **省 260 字**

Multi-char shot total trim ≈ **1340 字**。原 4500 字 → ≈ 3160 字 → 仍超 2000。

需进一步 trim：
- 动作 timed beats: 简化叙述（保留时段+核心动作，去掉 "; 不复述图中已有内容" 等程式语 ≈ 省 30 字 per shot）
- 台词 / 字幕: 多角色 shot 限制 ≤ 3 角色 dialogue（其余 narrate via 旁白），≈ 省 100-200 字
- 光线 / 色调: 简化 hex 色卡描述，仅保留主调 hex 不全 hex（≈ 省 30 字）

进一步 trim ≈ 200 字 → multi-char shot 约 2960 字 → 仍超。

**最终策略**: multi-character shot (≥4 chars) 强制 **角色 line 仅列前 3 个主体角色**的 locked 一句话 + face-diff，其余角色 inline 一句话归并为 "其余 5 宗主背景出场（参考 character refs）"。这 trim 6 chars × 80 = 480 字 → 剩 3 chars × 80 = 240 字。

加上其他 trim：multi-char shot 约 2200-2500 字 → 仍可能超 2000。

**接受 trade-off**: 80%+ shots 在 2000 字以内；少数极端 multi-char shot (ep01/shot03/06/07 全 6 角色同框 cover-frame) 接受 2200-2500 字 上限（极端 shot 视觉信号密度高 prompt 需更长亦合理）；spec.md 改 ≤ 2000 字 为 ≤ 2200 字 soft limit + 极端 cover-frame shot 例外（≤ 2500 字 hard 上限）。

实际更合理的目标：**≤ 2000 字 soft limit / ≤ 2500 字 hard limit**。

## (B) Markdown-style 视觉渲染契约

### 1. 改 webapp renderer.tsx — 新增 `applyFieldLabelPill` regex pre-pass

匹配 prompt body 内 field labels: `^(角色|场景|镜头|动作|台词 / 字幕|节奏|光线 / 色调|渲染样式|比例|时长|负向)：`，wrap 在 `<span class="field-label">` 内。**仅在 fenced code blocks 之外应用**（同 `applyRefPlaceholderPill` code-fence-aware split）。但 field labels 主要 INSIDE code blocks → 这意味着我们需要在代码块 INSIDE 也 highlight。

**策略**: 由于 ReactMarkdown 把 ```text fence 内文当 plain text 渲染（无法注入 HTML markup 而保持 copy-paste 干净），我们用**纯 CSS 方案** — 给 code blocks 加 `font-feature-settings: "ss01"` / 或自定义 `<pre>` 子元素，并通过 React `pre` component override（已存在 `CopyableCode`）拆分文本 → 渲染成 React fragments → 含字段标签的行用专门 styling，但**保持 innerText 等于原文**（CSS 不影响 innerText / clipboard 内容）。

更简单方案：使用 CSS only — code block 行内匹配模式 (`角色:`) 通过`highlight.js` 的 hljs-attr 类高亮（rehype-highlight 已配置）。但 `text` 语言 hljs 无规则。

**最实际方案**：
- 修改 `CopyableCode` 组件：把 children (code element with text) 解析、按行 split，每行 prefix 匹配 `(角色|场景|...)：` 时，用 `<span className="field-label">{label}</span>{rest}` 渲染，否则原样。
- 用 CSS `.field-label` styled with bold + indigo color + monospace。
- innerText 仍然反映文本内容（无 HTML in copied text）→ copy button 不变。

### 2. CSS additions:

```css
.markdown-view .code-block-wrapper .field-label {
  color: #f5a96d;            /* warm orange — distinct from indigo placeholders */
  font-weight: 600;
  letter-spacing: 0.02em;
}
```

### 3. 视觉效果:

每个 prompt code block 行首的 `角色:` / `场景:` 等被高亮为暖橙色粗体，让 prompt 看起来像结构化 markdown 文档（field-value layout）；user 仍可 click copy → 纯文本进剪贴板。

## (C) Rule changes

- **Rule #12.4 v4** (per follow-up 013):
  - 新增「**prompt 字数上限**」契约：≤ 2000 字 soft limit / ≤ 2500 字 hard limit。
  - 「**12.4-A 角色字段展开规则**」修订：shot prompt 角色 line 仅含 locked 一句话 + face-differentiator (~80 字/char)；inline body expansion + 5-7 项 micro-details 仅在 character ref turntable prompt 内 carry。
  - 渲染样式 / 负向 keyword count 上限：渲染样式 ≤ 9 项，负向 ≤ 24 项（核心选择，去重 stylization 变体）。
  - Multi-character shot (≥4 chars) 强制 角色 line 限 3 主体；其余 inline 一句概括。
  - 新增「**Markdown-style 视觉渲染契约**」: webapp 渲染 ```text fenced code blocks 时对 field labels (`角色:` / `场景:` / etc.) 应用 CSS field-label highlight pill；innerText / clipboard 行为保持纯文本契约。

## 期望行为

1. 50 shot files 中 80%+ 文件 prompt body ≤ 2000 字；剩余 ≤ 2500 字。
2. user 在 webapp 打开 shot.md → ```text code block 内 `角色:` / `场景:` / `镜头:` / 等 field labels 高亮为暖橙色粗体；click copy button → 纯文本进剪贴板（无 HTML / no styling 损失）。
3. follow-up 001-012 锁定全部保持有效。
4. character ref turntable prompts (in c{N}_*.md 文件) 不变 — 5-7 项 micro-details + 完整 inline expansion 仍 carry 在 turntable prompt 内（user 渲染 turntable mp4 时使用），保证 turntable 视频自身已 carry full character data。

## Out of scope

- 不修改 character / scene file content（仅 trim 50 shot files 的 prompt body + webapp UI 强化）。
- 不实际渲染。
- 不修改 ep06-ep60 stage-4 regen 范围。
- 不修改 follow-up 002 遗留 inconsistency。
