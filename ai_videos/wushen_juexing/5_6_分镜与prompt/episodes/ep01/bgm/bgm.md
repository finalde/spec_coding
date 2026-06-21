# ep01 BGM 编排 · 武神觉醒（穿越·除族·硬刚离家）

> 稀疏配乐时间线：只在需要 BGM 的剧情段写一行；其余段落（决意独白 44–53s、果决盯选项 65–72s、离场 95–102s 等）留白无配乐。
> 行式：`起-止(秒)  bgm_NNNN|- | cat=情绪 | vol=0-1 | duck=on/off | fade=in/out  # 剧情`
> 槽位 `-` = 待分配；在 webapp 的「🎵 BGM 编排」面板里按情绪选库内 `bgm_NNNN` 分配，再点烧录。
> vol=0-1 线性；duck=on 台词处自动让路；fade=in/out|in|out|none。
> 烧录：源 `ep01_zh.mp4`（中文字幕本集视频）→ `ep01_zh_bgm.mp4`（重烧覆盖）。
> 总时长 118s（shot 累计：11+12+12+9+9+12+7+12+11+7+8+8）。

```text
0-11  bgm_0002 | cat=suspense | vol=0.5 | duck=on | fade=in  # 开场钩：穿越骤醒转冷、至暗压迫(shot01)
11-35  bgm_0002 | cat=tension | vol=0.55 | duck=on | fade=in  # 高座宣判除族 + 裴昭奚落冷峙(shot02-03)
35-44  bgm_0003 | cat=tragic | vol=0.5 | duck=on | fade=in/out  # 回忆：救弟挡掌、丹田碎裂、家人变脸(shot04)
53-65  - | cat=system_cue | vol=0.5 | duck=on | fade=in  # 鎏金系统对话框浮现·转机冷冽(shot06)
72-84    -  | cat=faceslap    | vol=0.7  | duck=on | fade=in       # 起身平视·自请退族·裴昭被噎(shot08·爽点)
84-95    -  | cat=climax_hype | vol=0.65 | duck=on | fade=in/out   # 系统暗授武神躯·暖流入骨·藏锋(shot09·暗燃)
102-118  -  | cat=theme_open  | vol=0.55 | duck=on | fade=in/out   # 门前宣言+跨门没入天光·北疆压城(shot11-12·尾)
```
