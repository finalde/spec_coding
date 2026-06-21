# ep02 BGM 编排 · 武神觉醒（离家上路·初入江湖·玉佩异动）

> 稀疏配乐时间线：只在需要 BGM 的剧情段写一行；市井烟火日常段（进镇逛街 19–35s）留白只走环境声。
> 行式：`起-止(秒)  bgm_NNNN|- | cat=情绪 | vol=0-1 | duck=on/off | fade=in/out  # 剧情`
> 槽位 `-` = 待分配；在 webapp 的「🎵 BGM 编排」面板里按情绪选库内 `bgm_NNNN` 分配，再点烧录。
> vol=0-1 线性；duck=on 台词处自动让路；fade=in/out|in|out|none。
> 烧录：源 `ep02_zh.mp4`（中文字幕本集视频）→ `ep02_zh_bgm.mp4`（重烧覆盖）。
> 总时长 104s（shot 累计：9+10+8+8+10+9+13+12+9+8+8）。

```text
0-9      -  | cat=tragic      | vol=0.45 | duck=on | fade=in       # 病躯独行暮色长路·孤身(S1)
9-19     -  | cat=system_cue  | vol=0.5  | duck=on | fade=in       # 驻足喘、系统初引、定意(S2)
35-45    -  | cat=tension     | vol=0.55 | duck=on | fade=in       # 地痞掀摊欺老者、勒索(S5)
45-54    -  | cat=tension     | vol=0.6  | duck=on | fade=none     # 主角挡身前、看不过、地痞挑衅(S6·蓄势)
54-67    -  | cat=combat      | vol=0.78 | duck=on | fade=in/out   # 打斗：几下放倒地痞+挨一记微喘(S7·武打)
67-79    -  | cat=warm        | vol=0.45 | duck=on | fade=in       # 地痞逃、老者道谢、丹田暗复(S8·温情)
79-96    -  | cat=suspense    | vol=0.55 | duck=on | fade=in/out   # 玉佩透温起疑 + 暗处目光掠过(S9-S10·钩)
96-104   -  | cat=theme_open  | vol=0.5  | duck=on | fade=in/out   # 收玉佩、出镇向夜路、江湖不太平(S11·尾)
```
