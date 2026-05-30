# 女帝退婚后悔了

> 古风 / 装废逆袭 / 女帝重逢悔婚 / 男频爽文短剧
> Pinyin slug: `nvdi_tuihun_houhuile`
> Sub-type: `novel` (多集短剧)

## 项目概要

陈国公府三公子陈凡，被女帝以"纨绔放荡，不学无术，得不配位"为由解除婚约。明面是被嫌弃的废柴，实则装废五年的隐藏强者。退婚那一刻，陈凡内心狂喜——五年笼中之困终得自由，他的真实修行与抱负即将启程。

题"退婚后悔了"——女帝在故事中后段将逐步意识到当年看错人，悔婚回头时，陈凡已不愿。这是 ep01 cold open 的核心钩子：观众看到的是"被退婚的废柴"，唯有内心独白与镜头微表情泄露真相。

## 使用说明 (人 → AI 模型)

```
1. 读 episodes/ep01/script.md  ← 完整对白 + 动作 + 内心 OS, 人类 review 用
2. 读 episodes/ep01/shotlist.md ← 镜头清单, 决定渲染哪些镜头
3. 对每个镜头, 打开 episodes/ep01/shots/shotNN.md:
   - 「Shot context」段: 看 Summary / Characters / Scene / Duration / Reference uploads checklist
   - 上传 checklist 列出的 character turntable mp4 + 场景 reference (按需)
   - 复制「视频 prompt」段的 ```text 代码块整段
   - 粘贴到 Kling / Seedance / Sora / Veo / Runway 任一支持文生视频或图生视频的模型
   - 渲染产物保存到 episodes/ep01/shots/shotNN/ 同名 folder (rule 12.9 folder-per-asset)
4. 拼接所有 shotNN 渲染产物 (CapCut / DaVinci / ffmpeg concat), 加字幕, 输出 ep01_final.mp4
```

## 角色清单 (ep01)

| folder | 中文名 | 角色定位 | ep01 出场方式 |
|---|---|---|---|
| c1_陈凡 | 陈凡 | 男主 · 装废逆袭 · 双层人格 | 全集 (接旨主轴) |
| c2_女帝 | 女帝 | 主女主 · 退婚者 | ep01 仅诏书提及, 未实出场 |
| c3_陈国公 | 陈国公 | 男主父亲 · 朝堂老臣 | ep01 接旨陪跪 + 末段表态 |
| c4_太监 | 太监 | 配角 · 宣旨内监 | ep01 全程主导节奏 |

## 风格关键词

水墨青灰 · 朱红诏书 · 沉香木 · 9:16 · cinematic · 4K HDR · 真人写实 · 亚洲俊男靓女 · 古装仙侠剧主演级颜值 · 接旨跪礼 · 内心 OS 与外表反差 (单方面 reveal motif)

## 渲染产物布局 (操作人填充)

```
ai_videos/nvdi_tuihun_houhuile/
├── characters/
│   └── c{N}_{中文名}/
│       ├── c{N}_{中文名}.md       # bible + turntable prompt (tracked)
│       └── turntable.mp4          # 7s 单 take (gitignored per rule 12.9)
├── scenes/
│   └── s{N}_{中文名}/
│       ├── s{N}_{中文名}.md       # bible + Seedream 立绘 + 15s walk-through 场景 reference (tracked)
│       ├── s{N}_{中文名}.png      # Seedream 立绘 (gitignored)
│       └── s{N}_{中文名}.mp4      # 15s walk-through (gitignored)
└── episodes/
    └── ep01/
        └── shots/
            └── shotNN/
                ├── shotNN.md             # tracked
                ├── shotNN_kling.mp4      # gitignored
                └── shotNN_thumbnail.png  # gitignored
```
