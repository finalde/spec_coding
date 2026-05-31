# 《魔尊归来》— AI 视频项目

## 项目概要

| 项 | 值 |
|---|---|
| 中文剧名 | 《魔尊归来》 |
| 英文标题 | Demon Lord Returns |
| task_name | mozun_chongsheng |
| task_type | ai_video |
| sub_type | novel（多集制） |
| 集数 | 60 集 |
| 单集时长 | ~1.5 分钟（≈ 90 秒） |
| 总片长 | ~90 分钟 |
| 画幅 | 9:16 竖屏 |
| 主语言 | 中文（YouTube Shorts 中英双语标题） |
| 发布平台 | 抖音 + YouTube Shorts |
| 题材 | 仙侠 · 重生复仇 · 系统流 · 多女主 |

## 一句话设定

渡劫后顶层修为的魔尊沧冥被五大宗主"中州五道盟"联手镇压，魂魄重生于乞丐少年叶无尘体内（满记忆 / 零修为），靠系统任务 + 三女主双修 + 药王谷丹药三轨缓慢恢复，最终杀回正派大本营揭穿伪君子并归位。

## 核心反讽

"正道盟" ≠ 正道；"魔尊" ≠ 邪。
正道是伪君子，魔尊是反英雄。

## 角色清单（9 锁定 + 1 双形态 = 10 份立绘）

| 角色 | 文件 | 立绘 |
|---|---|---|
| 沧冥 · 魔尊（前世） | `characters/沧冥-魔尊本相.md` | `ref_images/沧冥-魔尊本相-立绘.md` |
| 叶无尘 · 乞丐转生 | `characters/叶无尘-乞丐转生.md` | `ref_images/叶无尘-乞丐转生-立绘.md` |
| 苏璃月 · 主女主 · 紫霄宫圣女 | `characters/苏璃月-紫霄圣女.md` | `ref_images/苏璃月-紫霄圣女-立绘.md` |
| 柳红袖 · 副女主 1 · 酒楼老板娘 | `characters/柳红袖-红袖招老板娘.md` | `ref_images/柳红袖-红袖招老板娘-立绘.md` |
| 苓夭夭 · 副女主 2 · 药王谷女医师 | `characters/苓夭夭-药王谷医师.md` | `ref_images/苓夭夭-药王谷医师-立绘.md` |
| 白月清 · 紫霄宫主（伪君子 1） | `characters/白月清-紫霄宫主.md` | `ref_images/白月清-紫霄宫主-立绘.md` |
| 赵焚天 · 玄炎宗主（伪君子 2） | `characters/赵焚天-玄炎宗主.md` | `ref_images/赵焚天-玄炎宗主-立绘.md` |
| 方鼎元 · 太清掌教（伪君子 3） | `characters/方鼎元-太清掌教.md` | `ref_images/方鼎元-太清掌教-立绘.md` |
| 韩夺心 · 万剑宗主（伪君子 4） | `characters/韩夺心-万剑宗主.md` | `ref_images/韩夺心-万剑宗主-立绘.md` |
| 司空玄 · 影神殿主（伪君子 5 · 终极） | `characters/司空玄-影神殿主.md` | `ref_images/司空玄-影神殿主-立绘.md` |

## 风格关键词

**美学**：传统仙侠主框架 + 黑金沉郁主色调
**视觉张力**：白衣伪君子 vs 黑袍魔尊（每集 ≥ 1 镜两套美学同框）
**单集结构**：~10 镜 × 8-10s；三钩模型（0-3s 冷开场 / 25-30s 第一反转 / 75-88s cliffhanger）

## 使用说明

### 1. 渲染流程

每镜双管线 + seam-frame 静帧：

```
1. 用 Seedream 渲染所有立绘 PNG (一次性, 10 份)
   characters/ref_images/{角色名}-{身份}-立绘.md → {角色名}-{身份}.png

2. 用 Seedream 渲染所有 seam-frame 静帧 (按集渲染)
   episodes/epNN/shots/shot01_startframe_seedream.md → shot01_startframe.png  (每集首镜)
   episodes/epNN/shots/shotNN_lastframe_seedream.md  → shotNN_lastframe.png   (每镜)

3. 用 Kling 2.1 Pro 渲染每镜 image-to-video
   input_image_urls = [上一镜末帧 + 本镜末帧]
   shot01: [shot01_startframe.png, shot01_lastframe.png]
   shotN (N≥2): [shot{N-1}_lastframe.png, shot{N}_lastframe.png]

4. 用 Seedance 1.0 Pro 渲染每镜 text-to-video（可选, 与 Kling A/B 比较）
   每镜 prompt 末尾"避免:"段是规避词清单（Seedance 无 negative_prompt 字段）

5. 用户在 Kling vs Seedance 间 per-shot 选择最佳输出

6. ffmpeg / CapCut / DaVinci 拼接 + 双语字幕 + 配音 + BGM

7. 按 publish.md 模板生成抖音 + YouTube Shorts 元数据，分发
```

### 2. 60 集发布节奏（建议）

- day1-12: 每日 1 集（前 12 集免费引流期）
- day13-30: 每日 2 集（觉醒恢复密集期）
- day31-60: 每日 1 集（终战收尾）
- 共 ~ 40 天首发完成

### 3. 渐进式 spec 扩展

本次输出仅含 ep01-ep05 的详细 episode/shotlist/shots/publish。ep06-ep60 在 `arc_outline.md` 中保留单行大纲。

后续按 5 集为一批触发 stage-4 regen 扩展：
```
"# EXECUTION MODE: AUTONOMOUS
继续生成 ep06-ep10 详细 spec。读 ai_videos/mozun_chongsheng/arc_outline.md 中 ep06-ep10 行做基础。"
```

### 4. 二季钩开关

ep60 final shot 双版本：
- `episodes/ep60/shots/shot10_finale_kling.md` — single-season ending（屠尽伪君子 + 三女主成婚）
- `episodes/ep60/shots/shot10_hook_kling.md` — 二季钩 open ending（主女主腹微凸光一闪 + 魔气未灭）

用户根据首发期留存数据二选一渲染。

## 项目目录结构

```
ai_videos/mozun_chongsheng/
├── README.md                    ← 本文件
├── world.md                     ← 世界观
├── style_guide.md               ← 视觉规范
├── arc_outline.md               ← 60 集大纲
├── characters/                  ← 中文角色名 (per follow-up 002)
│   ├── 沧冥-魔尊本相.md          ← 男主前世
│   ├── 叶无尘-乞丐转生.md        ← 男主乞丐
│   ├── 苏璃月-紫霄圣女.md        ← 主女主
│   ├── 柳红袖-红袖招老板娘.md    ← 副女主 1
│   ├── 苓夭夭-药王谷医师.md      ← 副女主 2
│   ├── 白月清-紫霄宫主.md        ← 伪君子 1
│   ├── 赵焚天-玄炎宗主.md        ← 伪君子 2
│   ├── 方鼎元-太清掌教.md        ← 伪君子 3
│   ├── 韩夺心-万剑宗主.md        ← 伪君子 4
│   ├── 司空玄-影神殿主.md        ← 伪君子 5
│   └── ref_images/
│       └── {角色名}-{身份}-立绘.md  ← 10 份立绘 prompt（中文文件名）
└── episodes/
    ├── ep01/
    │   ├── episode.md           ← 集梗概
    │   ├── shotlist.md          ← 10 镜镜头表
    │   ├── shots/
    │   │   ├── shot01_kling.md          ← Kling 视频 prompt
    │   │   ├── shot01_seedance.md       ← Seedance 视频 prompt
    │   │   ├── shot01_startframe_seedream.md ← 首镜首帧立绘
    │   │   ├── shot01_lastframe_seedream.md  ← 首镜末帧
    │   │   └── ... (shot02..shot10)
    │   └── publish.md           ← 抖音 + YouTube Shorts 元数据
    ├── ep02/ ... ep05/          ← 同结构
    └── ep06/ ... ep60/          ← 待 stage-4 regen 扩展
```

## 维护

- 任何角色描述符变更 → 更新对应 `characters/{role}.md` 第 10 字段"一句话锁定"，并 search-replace 所有 episodes/epNN/shots/* 中的引用。
- 任何视觉规范变更 → 更新 `style_guide.md`，并由 stage-4 regen 重新生成相关 prompt。
- 任何卷间大事件变更 → 更新 `arc_outline.md`，并由 stage-4 regen 同步对应集。
