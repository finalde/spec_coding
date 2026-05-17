# Follow-up draft 069 — 2026-05-17

Summary: `PromptPreviewModal` 每张 prompt card 视觉优化 + 强制无横向滚动条。Variance + photographer + medium + type_anchor 等组合后的 prompt 可达 ~2000 字符，含大量 comma-separated tokens（部分 token 内可能无空格）。旧 CSS 仅 `.prompt-preview-body` 加了 `pre-wrap` + `break-word`；`.prompt-preview-toggle`（`<summary>` 内显示前 180 char 切片）+ `.prompt-preview-attrs`（单行 attrs 串）+ card 容器无 overflow guard，长 token 仍可能撑出横条。新 CSS 统一加 `overflow-wrap: anywhere` + `word-break: break-word` 到所有 text-bearing 元素 + `overflow: hidden` 在 card 外壳 + body 最高 360px 内滚（不撑模态）。同步美化：圆角 / 间距 / hover 阴影 / pill-style seed badge / 折叠箭头 / 更松行高（1.7）/ 颜色对比微调。

## 用户原话

> 优化每个prompt在UI的展示，使得不过prompt多大,没有horizontal bar,并且让prompt看起来美观些

## 决策

| 项 | 决策 | 理由 |
|---|---|---|
| Overflow lock | `.prompt-preview-card` 加 `overflow: hidden`；`.prompt-preview-body` 加 `overflow-x: hidden + overflow-y: auto`；`.prompt-preview-attrs` + `.prompt-preview-toggle` + `.prompt-preview-body` 加 `overflow-wrap: anywhere + word-break: break-word` | 三层防御 — outer 容器 cut + body 内滚 + text 自由 break；任何 prompt 长度都不出横条 |
| Body max-height | 360px + `overflow-y: auto` | 长 prompt 走 internal scroll；模态高度不被撑爆 |
| Card 美化 | padding 8/10 → 12/14；border-radius 4 → 6；background `--bg-toolbar` → `--bg-panel`；加 hover 状态 `border-strong + 1px shadow` | 更舒展；hover 反馈让用户感觉这张卡可互动 |
| List style | `<ol decimal inside>` → `<ol>` + `list-style: none` | 数字 marker 与 meta 行 "第 N 张" 重复；移除冗余 |
| Meta 行 | `flex-wrap: wrap` + 字体调整（strong 13px 600；seed 11px pill）| 长 meta（带 archetype label）能正常换行 |
| Seed badge | pill 样式 — `bg-toolbar` + 圆角 10px + 1px border | 视觉锚点 |
| Attrs 行 | 加底色 + 边框 + padding；font-size 11 → 11.5；line-height 1.5 | 更像数据 chip，与 prompt body 区分 |
| Toggle 箭头 | 自定义 `::before` 箭头（▸ / ▾）替代浏览器 default `▶` marker；隐藏原生 marker | 跨浏览器一致；与黑底前景色匹配 |
| Body 排版 | line-height 1.5 → 1.7；font-size 12 → 12.5；padding 8 → 12/14 | 长 prompt 阅读舒适 |
| Panel 宽度 | max-width 900 → 980；width 90vw → 92vw | 大屏更多横向空间，减少不必要换行 |

## 功能要求

`apps/ui/src/styles.css` 修改既有 `.prompt-preview-*` 块：

1. `.prompt-preview-panel`: max-width 980 / width 92vw
2. `.prompt-preview-hint`: 行高 1.55
3. `.prompt-preview-list`: `list-style: none`；gap 8 → 12
4. `.prompt-preview-card`: padding/radius/background/hover/transition；`overflow: hidden`
5. `.prompt-preview-meta`: `flex-wrap: wrap`；strong 13px/600
6. `.prompt-preview-seed`: pill (bg-toolbar / radius 10 / border)
7. `.prompt-preview-attrs`: 加底色 + 边框 + 5px 9px padding；line-height 1.5；`overflow-wrap: anywhere`
8. `.prompt-preview-toggle`: 加 `overflow-wrap: anywhere + word-break: break-word`；隐藏原生 marker；`::before` 箭头切换
9. `.prompt-preview-body`: padding 12/14；font-size 12.5；line-height 1.7；max-height 360px + overflow-y auto + overflow-x hidden；`overflow-wrap: anywhere + word-break: break-word`

不动 component JSX；不动后端 / endpoint / spec FR。

## 安全 / 边界

- **零 JS 改动**；纯 CSS。
- **跨浏览器**：`::marker` + `::-webkit-details-marker` 双写覆盖 Safari + Chromium + Firefox。
- **A11y**：折叠箭头是装饰；`<details>` 的语义不变；screen reader 仍能正确朗读 "summary"。
- **Print**：max-height 在 print media 可能阻断长 prompt — 未来若需打印走单独 `@media print` 覆盖，本 v1 不做。

## 不在本 follow-up 范围

- 不改 PromptPreviewModal JSX。
- 不动 ActorPoolGenerator dropdown / form-grid 样式。
- 不引入主题 / dark mode 适配（既有 `--bg` / `--bg-panel` / `--text` token 已覆盖 light theme）。
- 不重排 meta / attrs / toggle / body 顺序。
- 不写 vitest。
