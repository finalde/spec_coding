# Seedance 提示詞素材庫

個人收集的 Seedance 視頻生成提示詞案例，按風格分類，方便複製試用。

## 通用公式

> **主體 + 動作 + 環境 + 鏡頭運動 + 光線/氛圍 + 風格 (+ 排除項)**

官方 6 步版本：`[Subject], [Action], in [Environment], camera [Camera Movement], style [Style], avoid [Constraints]`

關鍵心法：
- 把提示詞當「導演分鏡」寫，不是「情緒板」——用具體動作、構圖、物理運動詞，越直白越聽話。
- **光線描述影響最大**：`golden hour backlighting`、`high contrast with deep shadows`。
- **每個提示只給一個主要鏡頭運動**，多了會打架。
- 引用現實風格錨點最有效：`Wes Anderson symmetry`、`Apple keynote style`、`Hans Zimmer-inspired scoring`。
- 長度約 **50–100 字** 最甜。
- 一個提示內做多鏡頭：用 `lens switch`（換鏡）表示一個剪切，模型會保持主體/風格連貫。

## 8 種鏡頭運動詞

| 英文 | 中文 | 用途 |
|---|---|---|
| `Push-in / Dolly In` | 推進 | 聚焦情緒 |
| `Pull-out / Dolly Out` | 拉出 | 揭示環境 |
| `Pan` | 橫搖 | 水平掃過場景 |
| `Tracking shot` | 跟拍 | 跟隨主體移動 |
| `Orbit / Arc` | 環繞 | 繞主體旋轉 |
| `Aerial / Drone shot` | 航拍 | 俯瞰視角 |
| `Handheld` | 手持 | 自然輕微晃動 |
| `Fixed / Locked-off` | 固定機位 | 完全靜止 |

## 分類索引

- [電影感 cinematic.md](cinematic.md)
- [動漫 anime.md](anime.md)
- [UGC / 自拍 Vlog ugc.md](ugc.md)
- [商業廣告 ads.md](ads.md)
- [動作 / VFX action_vfx.md](action_vfx.md)

## 延伸資源

- [GitHub — awesome-seedance-2-prompts](https://github.com/YouMind-OpenLab/awesome-seedance-2-prompts) — 2000+ 分類提示詞、角色一致性技巧、API 工作流
- [Apiyi — Seedance 2.0 官方公式 + 8 種運鏡](https://help.apiyi.com/en/seedance-2-0-prompt-guide-video-generation-camera-style-tips-en.html)
- [AnimateAI — Seedance 1.0 電影運鏡 10 公式](https://animateai.pro/blog/seedance-1-0-cinematic-motion-prompts-10-formulas-for-true-film-style-camera-movement/)
- [imagine.art — 70 Ready-To-Use Prompts](https://www.imagine.art/blogs/seedance-2-0-prompt-guide)
- [Atlas Cloud — 15 Best Seedance 2.0 Prompts](https://www.atlascloud.ai/blog/guides/best-seedance-2-0-prompts-guide)
