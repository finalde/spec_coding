# 《悟空觉醒》— Wukong Juexing

YouTube Shorts 9:16 单片项目。中文标题《悟空觉醒》对应英文 / pinyin 项目槽位 `wukong_juexing`（路径名规则：英文 / 拼音；文件内容：中文）。

## 项目概要

齐天大圣孙悟空自上古石卵中破壳觉醒。一段 38 秒的电影级回环：石卵迸金 → 山巅揭示 → 怒吼蓄力 → 持棒亮相 → 回归石卵余烬。

视觉风格对标《黑神话：悟空》"厚重神话感"，9:16 竖构图，无对白、无字幕、纯视觉叙事。5 个镜头共享单一角色（孙悟空）+ 单一 Seedream 立绘锚定，由 Kling 2.1 Pro（image-to-video）+ Seedance 1.0 Pro（text-to-video）双工具并发渲染，用户每镜从两份输出中挑较佳者并外部剪辑后发布。

总时长：38 秒（5 / 8 / 8 / 10 / 7 秒分镜）。

## 使用说明

1. **阅读本文件 + `final_specs/spec.md`**（位于 `specs/ai_video/wukong_juexing/`）了解项目契约。
2. **生成立绘**：复制 `characters/ref_images/main_seedream.md` 的 "## Prompt（中文）" 段落整段，粘贴入 Seedream 4.0；按建议参数生成全身立绘；从候选中挑选一张人物居中、五官清晰、紫金冠 + 锁子黄金甲 + 金箍棒「四元素同框」、背景灰色渐变干净、无文字水印的图片，保存为 `characters/ref_images/main_seedream.png`（用户侧步骤，不进仓库）。
3. **渲染 5 镜**：对每个 `prompts/shotNN_kling.md` — 复制整文件粘贴入 Kling 2.1 Pro，将 `main_seedream.png` 作为参考图附上，按 `比例:` `时长:` `negative_prompt:` 字段对应填入；对每个 `prompts/shotNN_seedance.md` — 复制整文件粘贴入 Seedance 1.0 Pro，按 `比例:` `时长:` `seed:` 字段对应填入。
4. **每镜挑较佳输出**：Kling 与 Seedance 渲染同一镜会产出风格略有差异的两段视频；用户根据 `style_guide.md` 与 `shotlist.md` 上下文判断哪一份更贴合，挑出 5 段最终用 clip。
5. **组装拼接**：用任一外部剪辑器（CapCut / Premiere / DaVinci）把 5 段拼成一条 9:16 竖屏视频；shot01→02 / 02→03 / 03→04 之间使用硬切（`hard cut`）；shot04→05 使用匹配剪辑（`match cut`）。Kling 文件中标注 `# 渲染说明` 的镜头（02 / 03 / 05）需按说明剪到目标秒数。
6. **缩略图复核**：将 Shot 01 t≈2 s 金光迸发峰值帧导出为静帧，验证是否独立可读为合格 9:16 缩略图（参 `prompts/shot01_*.md` 的 `# 缩略图契约` 说明）；不合格则重新渲染 Shot 01。
7. **回环复核**：将 Shot 05 末帧与 Shot 01 起帧并排对比，验证构图 byte-identical（仅光照状态翻转）；不合格则重新渲染 Shot 05（参 `prompts/shot05_*.md` 的 `# 回环契约` 说明）。
8. **发布**：参 `publish.md` 复制候选标题 + 简介 + hashtag，按推荐发布时段（周四/周五 19:00–21:00 北京时间）上传至 YouTube Shorts。

## 角色清单

- **孙悟空** （主角，唯一出场角色）— 齐天大圣，刚自石卵中破壳而出的觉醒态。战损战士形态：凤翅紫金冠 + 锁子黄金甲 + 金箍棒「三件套」+ 浅褐色短毛 + 灵长类肌腱体格。视觉风格对标《黑神话：悟空》游戏 CG。完整锁定描述符见 `characters/main.md`；Seedream 立绘 prompt 见 `characters/ref_images/main_seedream.md`。

## 风格关键词

- 黑神话·悟空美术风（核心美术风锚点）
- 厚重神话感 / weighty mythic realism
- 9:16 竖构图
- 暮色山巅 + 戏剧化星空（场景锚点）
- teal-and-orange 偏中式文人画 LUT
- 暖橘金 `#F2A65A` + 深岩青 `#2E5C6E` 主对比
- 紫金 `#6B4226` + 鎏金 `#C9A96E` 金属双层反光
- 35 mm 胶片颗粒
- 极缓推近 / 慢速广角揭示 / 轨道环绕 / 手持轻微浮动 / 垂直升降（5 锁定运镜）
- 暮色魔幻时刻顶光 / 星空环境光 / 金色边缘逆光 / 点状装饰光 / 体积光丁达尔束 / 冷蓝补光（6 锁定光线）
- hard cut + match cut（2 锁定转场，无白闪过渡）
- 写实 CG 质感（禁用：卡通 / 二次元 / cel-shading / Q 版 / 戏曲红黄妆 / 86 版西游记 / 低多边形）

## 文件目录

```
ai_videos/wukong_juexing/
├── README.md                       (本文件)
├── characters/
│   ├── main.md                     (孙悟空锁定描述符)
│   └── ref_images/
│       └── main_seedream.md        (Seedream 立绘 prompt)
├── style_guide.md                  (调色盘 + 镜头 + 光线 + 运镜 + 转场)
├── script.md                       (5 镜剧本)
├── shotlist.md                     (5 镜清单 + 时长 + 景别 + 连续性)
├── prompts/
│   ├── shot01_kling.md / shot01_seedance.md  (Hook + 缩略图契约)
│   ├── shot02_kling.md / shot02_seedance.md
│   ├── shot03_kling.md / shot03_seedance.md  (含金箍棒发光例外)
│   ├── shot04_kling.md / shot04_seedance.md  (四元素同框)
│   └── shot05_kling.md / shot05_seedance.md  (回环契约)
└── publish.md                      (YouTube Shorts 发布元数据)
```

## 工具版本依赖

- Seedream 4.0（即梦 / 火山引擎 / Replicate）
- Kling 2.1 Pro image-to-video（fal.ai / klingai.com）— 时长枚举 `5` / `10`；支持 `negative_prompt`；支持 `image_url` 参考图。
- Seedance 1.0 Pro text-to-video（fal.ai / Volcengine）— 时长 2–12 整数；不支持 `negative_prompt`，本项目改用正向 `约束:` 段。

更新版本（Kling 3.0 / Seedance 2.0）接受相同 prompt，且通常额外提供更高质量；用户有付费访问可直接升级渲染。

## 项目谱系

由 `agent_team` 工作流驱动产出，6 阶段产物保留在 `specs/ai_video/wukong_juexing/`（user_input / interview / findings / final_specs / validation / changelog）。如需修订本项目，先读 `specs/.../changelog.md` 了解已应用的 follow-up，再通过 follow-up 流程提交新指令而非直接编辑生成物。
