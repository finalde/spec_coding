# Validation level 06 — accessibility & manual walkthrough

Run: `ai_video_management-20260505-002710`
Stage: 5 (validation strategy)
Scope: combined a11y mandatory checks + post-render manual walkthrough script + spec carve-out re-check + sign-off conditions.
Authority basis: `agent_refs/validation/general.md` principles 4 (manual walkthrough is a level too) + 6 (carve-out re-check); `agent_refs/validation/development.md` move 7 (manual UI walkthrough before sign-off); `agent_refs/project/development.md` rule 1 (light theme on chrome, dark `<pre>` carve-outs only).

---

## 总览

本级是 stage-5 验证策略中**最后一个签出闸口**。即便 level-01..05（acceptance criteria / BDD / 后端测试 / 安全 / e2e）全部通过，本级未通过则 stage-6 work unit 不得宣告 done。

两条执行轨道：

1. **A11y 检查清单（自动 + 半自动）**：~12 项强制检查，覆盖 light-theme chrome 对比度、dark `<pre>` carve-out 对比度、键盘可达性、ARIA 标签、`lang` 属性、图片替代文本、徽章可访问文本。运行时混合工具：axe-core via Playwright（自动）+ 手工 DevTools（聚焦轮廓、对比度抽样）。
2. **手动走查脚本（pure manual）**：~12 步骤的有序脚本，由 user 在 `make run-prod` 与 `make run-backend + make run-frontend` 两种模式下分别走完。本级在所有 level-1..5 通过后由 parent 发出 `validation.requires_manual_walkthrough` 事件，由 user 执行并回执。

事件契约（`events.jsonl`）：
- 自动 a11y 子级失败 → `validation.issue.raised` + 严重度（见各检查项）。
- 手动走查子级 → 始终发 `validation.requires_manual_walkthrough`，user 回执后由 parent 发 `validation.pass` 或 `validation.issue.raised`。

工具要求：
- axe-core via `@axe-core/playwright`（自动 a11y 子集，跑在 e2e profile 上，每个 advertised 模式各跑一次）。
- WCAG AA contrast 工具：Chrome DevTools Lighthouse + 取色器人工抽样（针对 dark `<pre>` carve-out 与 locked-block pill 这两类 spec-driven 私货元素）。
- 键盘走查：手工 Tab 键序，无脚本。

---

## A11y 检查清单

12 项强制检查。每项给出：检查方法、通过标准、失败严重度、对应 FR。

### A11Y-01 — Light-theme chrome WCAG AA contrast

- **范围**：`body` 背景 vs 正文文字；sidebar 背景 vs leaf 标签 / sub-type 徽章 / "查看规格" 链接；toolbar 背景 vs 按钮文字；panel 背景 vs 标题；button 静态/hover/focus 三态前景 vs 背景。
- **方法**：axe-core via Playwright `accessibility-light-chrome.spec.ts`，在 `make run-prod` 启动后访问首页 + 任一 ai_video 项目根目录视图，断言 `axe.violations.filter(v => v.id === 'color-contrast').length === 0`。
- **通过标准**：所有 chrome 元素 normal text ≥ 4.5:1，large text (≥18 pt or ≥14 pt bold) ≥ 3:1，UI components ≥ 3:1。
- **失败严重度**：`blocker`（ARIA / a11y mandatory check fail，per general.md severity policy）。
- **对应 FR**：FR-79（light-theme chrome）。

### A11Y-02 — Dark `<pre>` carve-out WCAG AA contrast

- **范围**：三类 dark surface：(a) RegeneratePanel 输出 `<pre class="regen-prompt-block">`；(b) `MarkdownView` 内的 `<pre><code>...</code></pre>`；(c) CodeView 全屏 `<pre>`。
- **方法**：手工 DevTools 取色器抽样（axe-core 已能检测，但 `<pre>` 的语法高亮 token 颜色对比度是 axe 易漏的边界），针对每类 surface 至少抽样：背景色 vs 默认前景文本、vs 注释 token、vs 关键字 token（如有 syntax highlighting）。axe 自动子集仍需运行作为兜底。
- **通过标准**：normal text ≥ 4.5:1（无 syntax highlighting 时只检默认前景；本 v1 spec 未引入 syntax highlighting，故只需检默认前景 vs 背景）。
- **失败严重度**：`blocker`。
- **对应 FR**：FR-74（regen-prompt 输出 dark pre）、FR-80（dark `<pre>` carve-outs WCAG AA）、`agent_refs/project/development.md` rule 1 carve-out 段。

### A11Y-03 — 键盘焦点可见性（focus visibility）

- **范围**：Sidebar 树（每个可展开节点 + 每个 leaf 链接）、Reader 顶栏的"查看规格"链接 + Edit 按钮、ShotPairView 两个复制按钮、ShotlistTableView 的 shot-id 行内按钮、ImageRefView 的复制按钮（如有）、RegeneratePanel 的所有 form 控件（stage selector / module multi-select / mode toggle / scope inputs / Generate / Copy）。
- **方法**：手工键盘走查 + axe-core `focus-order-semantics` rule。Tab/Shift-Tab 序应可达每一个交互元素，焦点轮廓应可视（不依赖颜色：浏览器默认 outline 或 CSS `:focus-visible { outline: 2px solid ... }`）。
- **通过标准**：(a) 所有交互元素 Tab 可达；(b) 焦点轮廓在 light chrome 与 dark `<pre>` 区均清晰可见；(c) Tab 序符合视觉顺序（左→右、上→下）。
- **失败严重度**：`blocker`。
- **对应 FR**：FR-43..78（覆盖所有交互元素）。

### A11Y-04 — 复制按钮 ARIA 标签

- **范围**：ShotPairView 两个复制按钮（"复制 Kling prompt" / "复制 Seedance prompt"）、RegeneratePanel 输出复制按钮（"复制 regen prompt"）、ImageRefView prompt 区复制按钮（如实现）。
- **方法**：axe-core `button-name` rule + DOM 抽查 `aria-label` 属性存在且文本可读。
- **通过标准**：每个复制按钮 DOM 上有 `aria-label="复制 Kling prompt"`（或对应文本）；按钮 visible text 与 aria-label 不冲突。
- **失败严重度**：`blocker`。
- **对应 FR**：FR-53（ShotPairView 复制 + aria-live）、FR-75（RegeneratePanel 复制按钮）。

### A11Y-05 — ARIA live region for "已复制" 提示

- **范围**：app-root 单一 `aria-live="polite"` 区域（DOM 顶层一处即可），由所有复制按钮共享，复制成功后写入"已复制"文本，~2 秒后清空。
- **方法**：(a) DOM 抽查 app-root 存在 `<div aria-live="polite" aria-atomic="true" id="copy-toast">` 容器；(b) Playwright e2e 模拟点击复制按钮后，断言该容器 `textContent === "已复制"`；(c) 使用 NVDA / VoiceOver / Narrator 至少一个屏读器手工验证朗读发生。
- **通过标准**：a + b 自动通过；c 由手动走查回执确认。
- **失败严重度**：`blocker`（缺 a/b）；`warning`（c 屏读器实测失败但 DOM 正确——需后续屏读器兼容性调查）。
- **对应 FR**：FR-53（aria-live 提示）、FR-75（同模式复用）。

### A11Y-06 — `lang` 属性正确声明

- **范围**：`<html lang="en">` 在 app shell；`<div lang="zh-Hans">` 包裹所有 markdown 渲染容器（QaView / MarkdownView / ShotPairView pane / ShotlistTableView / ImageRefView prompt pane）。
- **方法**：axe-core `html-has-lang` + `valid-lang` rules + DOM 静态抽查每个 markdown 容器外层是否有 `lang="zh-Hans"`。
- **通过标准**：根 `<html>` 有 `lang="en"`；每个渲染中文内容的容器有 `lang="zh-Hans"`。
- **失败严重度**：`blocker`（直接影响屏读器选词与语音引擎切换）。
- **对应 FR**：FR-67（markdown render container has `lang="zh-Hans"`）。

### A11Y-07 — 图片 alt 文本

- **范围**：ImageRefView 的 `<img>` 元素。
- **方法**：axe-core `image-alt` rule + DOM 抽查。
- **通过标准**：`<img alt="{stem}立绘" />`，stem 为去后缀的文件名（如 `main_seedream`）；**禁止** `alt=""`（会被屏读器跳过，但本视图图像就是用户的查看目标，不是装饰）；**禁止** `alt="image"` / `alt="img"` 这类无信息的占位。
- **失败严重度**：`blocker`。
- **对应 FR**：FR-61（`<img alt="{stem}立绘" />`）。

### A11Y-08 — Sub-type 徽章可访问文本

- **范围**：Sidebar 中 `ai_videos/{name}/` 节点旁的 `短` / `剧` 徽章。
- **方法**：DOM 抽查徽章元素带 `aria-label="项目类型: 短"` 或 `aria-label="项目类型: 剧"`；可见文本 `短` / `剧` 仍保留作为视觉标识。当 `sub_type=None` 时不渲染徽章（per FR-44），无需 aria-label。
- **通过标准**：可见徽章 + 同义 aria-label 同时存在且语义一致。
- **失败严重度**：`blocker`（颜色非唯一区分手段——本检查兼顾 A11Y-12）。
- **对应 FR**：FR-44（sub-type 徽章渲染规则）。

### A11Y-09 — 跨树链接可见文本

- **范围**：Reader 顶栏 "查看规格" 链接（仅在浏览 `ai_videos/{name}/` 下文件时出现）。
- **方法**：DOM 抽查链接 visible text 包含可读文字"查看规格"（**禁止**纯图标 / 仅 `aria-label` 而无可见文本）。
- **通过标准**：`<a href="?file=specs/ai_video/{name}/">查看规格</a>` 或带图标但 visible text "查看规格" 与图标并存。
- **失败严重度**：`blocker`（per WCAG 2.5.3 Label in Name）。
- **对应 FR**：FR-45 / FR-78（"查看规格"链接）。

### A11Y-10 — Locked-block pill 可访问 tooltip

- **范围**：`MarkdownView` 在 `【...锁定描述符 vN】` 块周围渲染的 `.locked-block` 包裹元素，及其 `::before` 伪元素 pill。
- **方法**：DOM 抽查 `.locked-block` 元素带 `title="byte-equality contract — see characters/main.md"` **或** `aria-describedby="locked-block-help"` 指向同文本的 sr-only 元素。CSS `::before` 伪元素本身屏读器不可达，因此宿主元素必须自带 a11y 文本。
- **通过标准**：宿主元素带 title 或 aria-describedby；屏读器手工抽测可朗读出 tooltip 文本。
- **失败严重度**：`blocker`。
- **对应 FR**：FR-65 / FR-66（locked-block pill 渲染 + tooltip）。

### A11Y-11 — RegeneratePanel form 控件 label 关联

- **范围**：stage selector dropdown、module multi-select、mode toggle、scope selector（含 episode N 单数字输入与 episodes M..N 双数字输入）。
- **方法**：axe-core `label` rule + DOM 抽查每个 `<input>` / `<select>` / `<button role="switch">` 都有 `<label for="...">` 或 `aria-labelledby` 或 `aria-label`。multi-select 若用 custom widget，`role="listbox"` + `aria-label` 必备。数字输入 `<input type="number" min="1">` 须有 label 文本（如"集数 N"）。
- **通过标准**：所有 form 控件均有可关联标签；空 label 或仅 placeholder 文本均视为失败。
- **失败严重度**：`blocker`。
- **对应 FR**：FR-70..73（RegeneratePanel 控件）。

### A11Y-12 — 颜色非唯一区分手段

- **范围**：sub-type 徽章（颜色 + 文本"短"/"剧"已并存——见 A11Y-08）；scope toggle gating（短项目隐藏 vs 显示——非颜色驱动，OK）；"locked block" pill（视觉上是底色，但有 hover tooltip + 文本"锁定块"）；任何 error/warning state（如 ImageRefView fallback 文本必须文字传达，**禁止**仅以红色/黄色背景指示问题）。
- **方法**：手工抽查所有状态指示元素，确认每个状态都有非颜色信号（图标 / 文本 / 形状 / 位置）。
- **通过标准**：通过手工 review 即可，无需 axe。
- **失败严重度**：`blocker`（WCAG 1.4.1 Use of Color）。
- **对应 FR**：FR-44 + FR-62（fallback 文本是文字传达）+ 全局设计准则。

---

## 手动走查脚本

12 个有序步骤。每步给出：操作、观察点、通过标准。整套脚本由 user 在**两种 advertised 运行模式**下各走一遍：

- 模式 A：`make run-prod`（单进程 FastAPI on 8766）。
- 模式 B：`make run-backend` + `make run-frontend`（FastAPI on 8766 + Vite on 5174）。

任何步骤在任一模式下失败 → `validation.requires_manual_walkthrough` 不通过，回退至 `validation.issue.raised`。

### M-01 — 启动 + 首屏视觉层级

- **操作**：启动当前模式后，浏览器访问 `http://127.0.0.1:8766/`（模式 A）或 `http://127.0.0.1:5174/`（模式 B）。
- **观察**：首屏布局：左侧 Sidebar（三段：AI Videos / Specs / Context）、中间 Reader 占位（"选择文件以查看"）、右侧 RegeneratePanel 折叠或展开。视觉层级清晰，无错位 / 无元素重叠 / 无水平滚动条。
- **通过**：三段布局正确；title 栏显示 "ai_video_management"；无浏览器控制台 error（DevTools Console 红字数 = 0）。

### M-02 — Light theme 真实输入下色彩对比抽测

- **操作**：在 Sidebar 找到 `ai_videos/wukong_juexing/`，依次浏览：项目根目录、`characters/main.md`、`prompts/shot01_kling.md`、`shotlist.md`、`publish.md`。
- **观察**：每页在浏览器渲染下，正文 / 标题 / 按钮文字均清晰可读，无低对比文字。徽章"剧"或"短"颜色与背景对比正常（per A11Y-01 / A11Y-08）。
- **通过**：5 个页面全部视觉抽测无失败；DevTools 控制台无 axe 警告（如启动时跑过 axe）。

### M-03 — Dark `<pre>` carve-out 对比抽测

- **操作**：(a) 打开任意 `.json` 文件触发 CodeView dark pre；(b) 打开 `prompts/shot01_kling.md` 触发 MarkdownView 内 code block dark pre（若有）；(c) 触发一次 RegeneratePanel "Generate" 按钮，看 dark `<pre>` 输出框。
- **观察**：三类 dark surface 文字清晰可辨；无 OS 切到 dark mode 时的颜色翻转（验证非 `prefers-color-scheme: dark` 驱动——切换 OS 主题，颜色应保持不变）。
- **通过**：三类抽测全部清晰；OS 切换无影响。

### M-04 — 键盘 Tab 焦点可见性

- **操作**：从首页起，仅用键盘 Tab 键依次穿过：Sidebar 每个 leaf → Reader 工具栏链接 → 一个 ShotPairView 的两个复制按钮 → 回到 Sidebar → RegeneratePanel 所有 form 控件。Shift-Tab 反向走一遍。
- **观察**：每个交互元素接到焦点时，浏览器或自定义 outline 清晰可见（不依赖颜色——形状/粗边框）；无"焦点黑洞"（按 Tab 后焦点丢失）。
- **通过**：无焦点丢失；无不可见焦点；Tab 序与视觉序一致。

### M-05 — 动效与拖拽流畅度

- **操作**：在 ShotPairView 中拖动中间分隔条 left/right；在 ImageRefView 中拖动分隔条；切换 stage selector / scope selector 多次。
- **观察**：拖动过程帧率流畅（无明显 jank / 卡顿）；下拉切换无闪烁 / reflow 抖动；长内容分隔区滚动顺滑。
- **通过**：所有交互肉眼无卡顿（粗略 ≥ 30 fps）。

### M-06 — 感知延迟（perceived latency）

- **操作**：(a) 点击 Sidebar refresh 按钮；(b) 在 `wukong_juexing` 项目内连续点击 5 个不同文件触发 view dispatch；(c) 点击 RegeneratePanel "Generate" 按钮。
- **观察**：每次操作至首帧响应均感觉 <300 ms；无明显白屏 > 500 ms；首字节快速到达（loading state 若存在则 <200 ms 内出现并 <300 ms 内消失）。
- **通过**：三类操作均感觉"即时"；如有抖动，DevTools Network 抓证据，否则视为通过。

### M-07 — 多模式对等（multi-mode parity）

- **操作**：本脚本在两种模式下分别完整走一遍。在每种模式下，至少一次执行：浏览 → 编辑 → 保存 → 重新浏览（验证 PUT /api/file 在该模式下成功 + 触发 tree auto-bump）。
- **观察**：两种模式下行为一致；无任何模式特有的 error；保存后 Sidebar mtime 自动更新。
- **通过**：两种模式各自完整通过本脚本所有步骤；无模式间分歧。

### M-08 — ShotPairView 真实数据走查（ai_video 专属）

- **操作**：从 Sidebar 进入 `ai_videos/wukong_juexing/prompts/shot01_kling.md`（或现有任一 shot N 文件），点击触发 ShotPairView。
- **观察**：(a) 左侧渲染 `shot01_kling.md`，右侧渲染 `shot01_seedance.md`，标题 / 内容均为中文且字体为 CJK 字体栈；(b) 两侧分别可独立滚动；(c) 拖动分隔条调整宽度，自动保存（重载页面后宽度仍记忆）；(d) 点击"复制 Kling prompt"，剪贴板真的拿到 kling 文件全文（粘贴到外部编辑器验证）；(e) 复制成功后 app-root aria-live 区域显示"已复制"约 2 秒。
- **通过**：a-e 全部正确；浏览器控制台无 console error。

### M-09 — ShotlistTableView 行点击导航（ai_video 专属）

- **操作**：浏览 `ai_videos/wukong_juexing/shotlist.md`，触发 ShotlistTableView。
- **观察**：(a) 表格首列每个 `shotNN` 显示为 button 样式且键盘可达；(b) 点击第一行 shot id，URL 切到 `?file=...prompts/shot01_kling.md&view=shot-pair` 且 ShotPairView 渲染成功；(c) 浏览器后退按钮回到 shotlist 视图无错。
- **通过**：a-c 全部正确。

### M-10 — ImageRefView 双状态走查（ai_video 专属）

- **操作**：(a) 浏览 `ai_videos/wukong_juexing/characters/ref_images/main_seedream.md`，**当前状态：companion `main_seedream.png` 是否存在请按 wukong_juexing 实际情况而定**；
  - 若存在：右侧应渲染图片，alt 为 "main_seedream立绘"，`<img>` URL 含 `?mtime=...` 参数；
  - 若不存在：右侧应显示中文 fallback "尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为 main_seedream.png 并刷新"。
- (b) 切换到另一个 `_seedream.md`（若有），重复上述判断。
- **观察**：图像状态切换正确；fallback 文本完全匹配 spec FR-62 的预期文案；无 broken image 图标。
- **通过**：观察到的状态与磁盘真实状态一致；fallback 文本为中文且与 spec 字面一致。

### M-11 — Locked-block pill 渲染（ai_video 专属）

- **操作**：浏览 `ai_videos/wukong_juexing/characters/main.md`（或任何包含锁定描述符块的文件），找到形如 `【孙悟空 · 觉醒态 · 锁定描述符 v1】...禁用 ...。` 的块。
- **观察**：(a) 块视觉上有"锁定块"小 pill 出现（CSS `::before`）；(b) hover 时显示 tooltip "byte-equality contract — see characters/main.md"；(c) 屏读器抽测（NVDA/Narrator/VoiceOver 任一）可朗读 tooltip 文本（per A11Y-10）。
- **通过**：a-c 全部正确。

### M-12 — Spec carve-out 复核 + 签出条件总结（见下两节）

- **操作**：完成下文 § Spec carve-out 复核 表格的逐项确认，并对照 § 签出条件 章节的 4 个 hard gates。
- **通过**：见下两节。

---

## Spec carve-out 复核

依据 `general.md` 原则 6（每个 v1 out-of-scope carve-out 必须在 stage 5 浮出，且检查它是否与其他 spec 段落冲突）。spec.md § Out of scope 共 11 条，逐一复核：

| # | Carve-out | 是否与其它 spec 段落冲突？ | 处置 |
|---|---|---|---|
| 1 | Render-API integration（Kling / Seedance / Seedream） | 无冲突。FR-50..64 全部仅做 prompt 文本管理与图像预览，从不发起 render API 调用。 | 通过；提示 user 确认外部 render workflow 仍由 user 手工执行。 |
| 2 | Multi-tenant / auth / WebSockets / mobile-responsive | 无冲突。FR-3..6 明确 IPv4 loopback only + single-user。 | 通过。 |
| 3 | Storyboard horizontal-scroll view（v2） | 无冲突。FR-47..64 无任何 storyboard 视图。 | 通过；记录为 v2 候选。 |
| 4 | Cross-publish manager + 英文 publish 翻译 | 无冲突。FR-43..78 无 publish 编排功能；publish.md 仅作为普通 markdown view。 | 通过；NFR-6 明确"NO auto-translation"已闭环。 |
| 5 | Compare-two-projects diff view | 无冲突。 | 通过。 |
| 6 | File create / delete / upload through webapp | 无冲突。FR-9 严格定义 4 个 mutation endpoints，全为更新 / promote / regen-prompt。 | 通过。 |
| 7 | Dark-mode chrome toggle | **半冲突需复核**：FR-79 light-only 与本 carve-out 一致；但 FR-74 / FR-80 引入 dark `<pre>` carve-out 元素——这是 spec 内"明确允许的 dark surface"，与 carve-out 不矛盾（carve-out 禁的是 chrome toggle，不是 dark 元素本身）。 | 通过；本 level 已分别测试 light chrome 对比度（A11Y-01）和 dark `<pre>` 对比度（A11Y-02）。 |
| 8 | File-system watcher / auto-refresh on mtime | 无冲突。FR-21 / FR-46 显式说"manual refresh + post-PUT auto-bump"。 | 通过；手动走查 M-07 验证 auto-bump。 |
| 9 | Polling for new `.png` files in `ref_images/` | 无冲突。FR-62 fallback + 手动 refresh 闭环。 | 通过；M-10 涵盖。 |
| 10 | （隐含）no SVG support per FR-13 | 无冲突。FR-13 明确 SVG 不在 read 允许列表。 | 通过；属安全红线，level-04 security 已覆盖。 |
| 11 | （隐含）no reverse cross-tree link（specs → ai_videos）per FR-78 | 无冲突。FR-78 仅提供 ai_videos → specs 单向。 | 通过；记录为 v2 候选。 |

**复核结论**：11 个 carve-out 均无与其它 spec 段落的硬冲突。FR-7 dark `<pre>` carve-out 和 FR-79 light-chrome 之间的"看似冲突"已经在 `agent_refs/project/development.md` rule 1 carve-out 段中明确允许；本级测试方案中通过分别覆盖 A11Y-01（light chrome）+ A11Y-02（dark `<pre>`）兑现。

**Stage-5 签出附加要求**：parent 必须在签出消息中向 user 显式列出本表，由 user 一次性确认 11 个 carve-out 全部为预期行为，否则升级为 `critical`（per general.md 原则 6 末段）。

---

## 签出条件

本级签出需同时满足 4 个 hard gates（per `agent_refs/validation/general.md` 原则 4 + `agent_refs/validation/development.md` move 7）：

### Gate 1 — A11y 检查清单全部通过

A11Y-01..A11Y-12 全部通过；任意一项 `blocker` 失败 → 本级回退；任意 `warning`（仅 A11Y-05c 屏读器实测可降为 warning）→ 记录但不阻断。

### Gate 2 — 手动走查脚本 M-01..M-11 在两种模式下全部通过

由 user 执行；user 回执通过 → parent 写 `validation.pass`；任一步失败 → parent 写 `validation.issue.raised` 并附 user 描述。

### Gate 3 — Spec carve-out 复核签字

§ Spec carve-out 复核 表格 11 项 user 显式确认。任一项被 user 标"非预期" → 升级为 `critical`，halt 整个 stage-5 sign-off，回到 stage-4 修订 spec。

### Gate 4 — Level-01..05 全部通过

本级为最后闸口；前置 5 个 level（acceptance criteria / BDD / 后端测试 / 安全 / e2e）均必须先发出 `validation.pass`。若有任一前置 level 仍 `validation.issue.raised`，本级不应启动；强行启动 → parent 视为契约违反并 halt。

---

## 与其他 level 的边界

- **不重复**：A11y 中"axe-core via Playwright"虽形式上是 e2e，但**断言对象**是 a11y 违规计数，非业务流程。Level-05 e2e 断言业务流程（路由、渲染、复制成功），本级断言 a11y。两级 axe 跑同一 fixture 但用不同 reporter。
- **不重复**：Level-04 security 涵盖 markdown sanitization（FR-16）；本级不复测，但**手动走查 M-08** 抽样 ShotPairView 渲染时若发现脚本注入痕迹，立即回报 security level（升级为 `critical`）。
- **依赖**：Gate 4 显式声明依赖 level-01..05；不抢跑。

---

## 事件契约

```jsonl
{"type": "validation.started", "level": "accessibility_and_manual", "ts": "..."}
{"type": "validation.requires_manual_walkthrough", "level": "accessibility_and_manual", "script": "specs/development/ai_video_management/validation/accessibility_and_manual.md", "ts": "..."}
// 自动 a11y 子集结果
{"type": "validation.pass", "level": "accessibility_and_manual.a11y_auto", "ts": "..."}  // 或 issue.raised
// 用户回执后
{"type": "validation.pass", "level": "accessibility_and_manual.manual", "ts": "..."}     // 或 issue.raised
// 整体
{"type": "validation.pass", "level": "accessibility_and_manual", "ts": "..."}
```

`pre_reading_consulted` 数组（parent 在本级 `validation.started` 事件首次出现时记录）：
- `C:\workspace\spec_coding\.claude\skills\agent_team\playbooks\validation.md`
- `C:\workspace\spec_coding\.claude\agent_refs\validation\general.md`
- `C:\workspace\spec_coding\.claude\agent_refs\validation\development.md`
- `C:\workspace\spec_coding\.claude\agent_refs\project\general.md`（如存在）
- `C:\workspace\spec_coding\.claude\agent_refs\project\development.md`
