---
worker_id: researcher-03-visual_style
stage: 3
role: researcher
angle: visual_style
status: complete
blockers: []
confidence: high
---

# Angle — visual_style — DRAFT `style_guide.md` for xianxia_new

> 本文是 **stage 4 直接采纳的 `style_guide.md` 蓝本**。stage 4 把第 3 章（"Implications for the spec — 7 个子节"）原样 copy 到 `ai_videos/{final_slug}/style_guide.md`，仅做少量编辑（替换占位的中文标题、补完最终 slug、把"参考 mozun_chongsheng"等比较语言剔掉）。本档为 spec-pipeline 内部 working doc，可保留比较 + 引用。

---

## 1. What this angle covers

视觉系统的"骨架 + 词典"——分四层：

1. **审美锚点（adopt-then-diverge baseline）**：以 sibling `mozun_chongsheng/style_guide.md` 为 known-working baseline，明确哪些 verbatim 继承（亚洲俊男靓女审美 11 项负向、photorealism 强化、Seedream 四段式、Kling/Seedance 渲染样式行），哪些需要为本剧 **重生复仇 + 寄生系统** 主题重写（魔气调性、雷劫调色、新增"寄生代价"视觉签名、立绘 vs 觉醒态双形态、UI 弹窗调性、negative list 项目专属补充）。
2. **可数视觉词典**：景别 / 运镜 / 速度 / 光影状态 / 转场（5 张表），每张表都是 stage-6 shot prompt 强制取词的 vocabulary——shot prompt 的 `镜头:` / `光线 / 色调:` / `节奏:` 都必须在这里有源。
3. **配色锁定（hex per 场景类型 + 派系）**：六大场景类（正道 / 散修 / 魔门 / 丹房 / 灵田 / 焦土）+ 主角双形态（重生弱体 vs 寄生觉醒），每条命名 + hex + 用途 + ≥ 3 个视觉引用。
4. **prompt-layer 默认值**：9:16 比例 / 时长（按 ai_video.md rule #6 复制）/ 字幕（三选一推荐 + 字体 + 描边）/ 模型适配（Kling 2.1 Pro 10s 切片 vs Seedance 1.0 Pro 15s 单 take 的取舍 + motion stability 已知 pitfall）。

**不覆盖**（其他 angles 负责）：剧情、角色 backstory、对白、世界观地理、宗门命名、版权清算。

---

## 2. Key findings with citations

### 2.1 sibling baseline 直接可继承的部分（5 块）

mozun_chongsheng 在过去 6 周内被同一管线连续打磨，已沉淀以下 **已验证、上线即用** 的子系统：

- **亚洲俊男靓女审美锚点 + face-differentiator 唯一识别符**：演员锚点表（罗云熙 / 成毅 / 王鹤棣 / 张凌赫 / 白鹿 / 虞书欣等） + 11 项 "不要 AI 通用脸 / 不要西方审美 / 不要网红脸" 负向 + 角色专属 standoff 痣 / 疤 / 耳钉。本剧 **全部 verbatim 继承**——审美锚点是跨项目通用的，演员池也共用。
- **photorealism 强化关键词（follow-up 012）**：影视级真人写实 / 真实毛孔 / 真实皮肤微瑕 / DSLR / 85mm 人像镜头 / ARRI / RED / Netflix 4K HDR drama 标准等 24+ 项正向 + 14 项负向。本剧 **全部 verbatim 继承**，无需修改。
- **Seedream 四段式**（per FR-26）：[主体] / [细节] / [风格] / [参数] / [负向]——立绘 prompt 的格式契约。本剧 verbatim 继承。
- **Kling video prompt 渲染样式行**：`光线/色调:` 行追加 `；渲染样式: 影视级真人写实 + cinematic + 4K HDR`，文件末追加完整负向 list。Verbatim。
- **9:16 竖屏构图规范（站位 3 档 + 抖音封面安全区 + 不允许大幅横向运镜 / 单镜 ≤ 3 人主体的"铁律"）**：vertical-first 短剧的硬约束在跨项目上完全适用。Verbatim。

来源：`ai_videos/mozun_chongsheng/style_guide.md` § 亚洲俊男靓女 / § 渲染样式锁定 / § 9:16 竖屏构图规范。

### 2.2 必须为本剧重写或新增的部分（4 块）

- **配色主基调差异化**：mozun_chongsheng 是"沉黑 + 护黄金 + 暗血红"（魔尊本相视角，"反英雄"），而本剧主角是 **被背叛的重生者**，并非天生魔修——前期是"散修级灰青 + 隐忍隐痕"，后期才进入"寄生黑紫 + 命短金芒"。**主基调与 mozun_chongsheng 平行而非重复**。
- **寄生系统视觉签名（项目级 ORIGINAL）**：mozun_chongsheng 的系统是"被动加成 + 弹窗"，UI 是"金字黑底银边"安全调性。本剧寄生系统每次升级 **消耗主角寿命 / 记忆**——视觉上需要"代价感"（aura 由暖向冷、肤色失血、瞳孔残影、记忆碎片飘散）。这是项目 **production hook**，必须独立设计。
- **重生主角的"双立绘"契约**：mozun_chongsheng 的主角沧冥只有 1 个本相 + 1 个转生少年（外形差距大但都"健康"）。本剧主角需要 **同一具肉身的 2 个 state**——重生初期（弱体、灰扑扑、内敛、健康但虚浮）vs 寄生觉醒后（瞳色变、皮下青脉浮、嘴角血、aura 黑紫）。两者必须可在同一 face-differentiator 下识别为同人，仅状态变化。这是 Seedream 立绘新挑战。
- **派系视觉的"反扁平化"**：mozun_chongsheng 用"反派 = 伪君子"统一调子，五大宗主视觉差异主要在道具（拂尘 / 剑 / 铜环 / 玉佩 / 面具）。本剧的"复仇靶标分散于三方"——正道 / 散修 / 魔门各自要有 **可一眼区分** 的派系视觉（正道偏冷青白金 vs 散修偏土褐布麻 vs 魔门偏紫黑骨白），不能再 collapse 到单一"反派"色调。

### 2.3 2025–2026 AI 短剧视觉趋势（web research 摘要）

- **审美疲劳压力**：行业从业者公开承认"AI 同质化脸 + 电子塑料感 + 光影逻辑缺失"已让观众疲劳，"电影工业级标准"成为 2026 的差异化方向（来源："2026 视觉革命：汉宸创盛如何用 AI+调色重新定义漫剧标准" — China News mtz.china.com 2026-04；"日产上千部短剧，AI 狂飙背后行业早已两极分化" — 钛媒体 2026）。**Implication**：renderer prompts 必须有 photorealism 强化 + AI-同质化负向，跟 mozun_chongsheng follow-up 008+012 一致。
- **Seedance 2.0 强化叙事一致性**：Seedance 2.0 支持最多 12 个参考文件（image + video + audio + text 多模态），针对角色一致性 + 多 shot narrative 强化（来源："2026 年 AI 真人短剧大模型选型指南" — Pixmax cnblogs；"用 Seedance 2.0 做 AI 短剧" — 知乎 zhuanlan）。**Implication**：本剧仍 lock Seedance 1.0 Pro（per qa.md），但 turntable reference 视频 + chars reel 路线（per follow-up 006 / 12.4-B）继续沿用，无需改 schema。
- **Kling 2.1 Pro 节奏单 take ≤ 10s 限制仍存**：与 ai_video.md rule #6 已记录的"Kling 2.1 Pro cap (10s) note"完全一致（来源：Kling 官方 + RunComfy / Scenario / Artlist 各家 model card 2026-04 至 2026-05）。**Implication**：shot 时长 11–15s 区间走 Seedance 单 take 优先；走 Kling 时按 mid-seam frame 二次切片，policy 不变。
- **Douyin / 红果 AI 短剧 9:16 + 60–90s episode + 末 5 秒 cliffhanger 已成行业默认**（来源：Vitrina "Micro-Dramas And Vertical-first Storytelling" 2026；Wikipedia "Duanju" 2026-04；"AI redefines China's booming micro drama industry" — Xinhua 2026-03-25）。**Implication**：confirm ai_video.md rule #7（9:16 默认）+ 每集 cliffhanger 设计（per qa.md Q10 集集 cliffhanger 已锁）。无新增约束。
- **仙侠题材 AI 视觉强项 vs 弱项**（综合 Pixmax 选型指南 + 钛媒体行业分析）：
  - **强项**：御剑飞行 / 仙境云海 / 法术对决 / 雷劫 / 丹炉 — AI 已能稳定生成，提示词驱动即可。
  - **弱项**：高密度群战 / 大规模法宝乱舞 / 4 人以上同框面部一致性。**Implication**：与 qa.md Q5 / revised_prompt § Constraints — short-drama feasibility "选材偏好" 完全契合；本剧 shot list 须遵守"单镜 ≤ 3 人主体" 铁律。

### 2.4 LUT / 调色板 web 引用（live-action xianxia 借鉴）

- **《长月烬明》"五彩斑斓的黑"调色模板**：黑 + 紫 + 金的高对比夜戏调色，宫殿摆设多用金色 / 红色 / 黑色（来源：渲染案例《长月烬明》— renderbus.com；"《长月烬明》造型详解：主打敦煌风" — 知乎 zhihu.com 2023）。本剧 **魔门 + 焦土 + 雷劫** 三场景的调色锚点。
- **《琉璃》《沉香如屑》"白衣帝君"视觉记忆**：白衣 + 浅金 + 浅青的高 key 仙气调色，柔光 + 雾岚 + 红绳 / 莲花意象（来源："其他的仙侠剧，求求你多看看《琉璃》的'服装'" — 网易；"《长月烬明》《琉璃》仙侠妆造分析" — 大作设计网站）。本剧 **正道宗门** 场景调色锚点。
- **《苍兰诀》（王鹤棣 / 虞书欣）的高纯度紫调 + 月夜**：低饱和长袍 + 半透布料 + 主色紫 / 银 / 黑，对"魔修但俊"的视觉表达极有借鉴价值（来源："仙侠妆造还有救么" — 大作设计网站；"《长月烬明》大火" — Jiemian 界面新闻 9246464）。
- **东方仙修蓝紫 + 金 配色模板**：长白发 + 银色雷纹 + 蓝紫长袍 + 银肩甲 + 云纹（来源："修仙要渡雷劫" — Sohu / chanzl.com 释圣文化）。**Implication**：雷劫场景的"金紫雷柱"调色已在 mozun_chongsheng baseline 沉淀，verbatim 继承。

### 2.5 Seedance / Kling 模型适配的 motion vocabulary

- **Seedance 高效运镜动词**（来源：Higgsfield "Seedance 2.0 — Complete Prompting Guide"；YouMind-OpenLab/awesome-seedance-2-prompts GitHub）：orbital "orbit around"、tracking "descending with them" / "diving beneath"、impact "shakes from impacts" / "jolts with each bone-snap"。**Implication**：可加入本剧 vocab 表的"运镜" 列。
- **Seedance 易翻车 motion**：过度 zoom（"no zoom, natural head movement" — guide 明确建议）；handheld 不稳定除非剧情需要；rapid angle change without narrative justification。**Implication**：本剧 vocab 表标注"避免大幅 zoom-in zoom-out 在同一 shot 内连续切换" 为 anti-pattern（与 mozun_chongsheng 已有的"避免大幅横向运镜" 铁律并列）。
- **Kling 2.1 Pro / 2.6 Motion Control 趋势**：2026-04 后 Kling 2.6 Pro Motion Control 已可做精确动作迁移（来源：Kie.ai Affordable Kling AI 2.6 Motion Control API；MindStudio "What Is Kling 2.6 Pro Motion Control"；RunComfy Kling 2.6 Pro Motion Control）。**本剧不 upgrade 模型**（qa.md 锁 1.0 Pro / 2.1 Pro 组合），但若未来 follow-up 切换可在该 vocab 表的 "运镜" 列加注。

---

## 3. Implications for the spec — DRAFT `style_guide.md`

> stage 4 直接 lift 本章 7 个子节为 `ai_videos/{final_slug}/style_guide.md` 主体。结构与 mozun_chongsheng `style_guide.md` 平行（便于 stage-6 validator 通用规则复用），但内容针对本剧 重生 + 寄生系统 主题重写。

### 3.1 镜头语言（景别 + 运镜 + 速度 lexicon）

#### 3.1.1 景别词典（13 类 — verbatim 继承 mozun_chongsheng baseline）

| 关键词 | 用途（本剧适配） | 9:16 备注 |
|---|---|---|
| 大全景 | 卷开场 / 终战大场面 / 焦土全景 | 高位人物上 1/3 线 |
| 全景 | 群像同框 / 宗门会议 | ≤ 3 人主体 |
| 中景 | 角色互动 / 寄生系统弹窗触发瞬间 | 主体居 y ≈ 480-720 |
| 中近景 | 二人对话 / 师徒 / 复仇对峙 | 单人脸部上 1/3 线 |
| 近景 | 单人台词 / 重生回忆 | 脸部 y ≈ 300-500 |
| 特写 | 表情 / 系统弹窗 / 寿命流失瞬间 | 字幕避让区 y > 1000 |
| 大特写 | 瞳孔（赤瞳 / 寄生瞳） / 指尖魔气 / 血泪 | 满构图 |
| 仰拍 | 反派威压 / 主角觉醒后登顶 | 9:16 仰拍效果强 |
| 俯拍 | 角色绝境 / 寄生代价瞬间下跪 | 顶光 |
| 平视 | 中性叙事 / 多数对话 | 默认 |
| 鱼眼 | 寄生系统识海 / 觉醒幻觉 | 仅识海 / 系统场景使用 |
| 正反打 | 对话节奏 | 标头 50mm 类似镜感 |
| 越肩 | 跟随主观 / 复仇视角 | 主角侧脸保留 |

#### 3.1.2 运镜词典（5 类基础 + 2 类本剧新增 + 2 类禁忌）

| 关键词 | 用途（本剧适配） | 默认时长 | 模型适配 |
|---|---|---|---|
| 推镜 | 紧张感 / 关键道具特写 / 寄生瞳孔慢推 | 3–5s | Kling / Seedance 都稳 |
| 拉镜 | 揭示场景 / 卷尾收 / 重生现场拉远 | 5–8s | Kling / Seedance 都稳 |
| 摇镜 | 群像交代 / 时间过渡 | 4–6s | Kling / Seedance 都稳 |
| 升降镜 | 雷劫降临 / 寄生 aura 自下而上吞噬 | 5–8s | Seedance > Kling（升降高度 > 1 画面时 Kling 易抖） |
| 环绕镜 | 主角觉醒态魔气展开 / 法相旋绕 | 6–10s | Seedance 顺时针 ≤ 180° 稳；Kling 90° 内稳 |
| 跟随镜（**本剧新增**） | 重生主角行走 / 复仇追击 | 4–8s | Seedance 强项；用 "tracking" / "descending with them" 关键词 |
| Match-on-eye / Match-on-action（**本剧新增**） | 寄生升级瞬间 hard cut + 同帧瞳孔位置匹配 | 切换瞬间 | 两模型都支持，需配合 seam-frame |
| **避免大幅横向运镜** | 9:16 不耐看 | — | 铁律 |
| **避免单 shot 内连续 zoom-in / zoom-out**（**本剧新增**） | Seedance prompt 文档明确 anti-pattern；易出 motion artifact | — | per Higgsfield Seedance guide |

#### 3.1.3 速度词典（4 档 — 在 mozun_chongsheng 3 档基础上新增"顿挫"）

| 关键词 | 用途 |
|---|---|
| 慢镜（50% 速） | 关键虐点 / 觉醒瞬间 / 寿命流失视觉化 |
| 标准（100%） | 大部分叙事 |
| 快剪（短切） | cliffhanger 末段 / 复仇蒙太奇 / 下集预告 |
| 顿挫（停顿 + 爆点）（**本剧新增**） | 寄生代价瞬间："世界静默 0.5s → 主角咳血 → 系统弹窗" 三拍 |

### 3.2 光影状态词典（12 状态）

> 在 mozun_chongsheng 10 状态基础上 +2，分别为 **寄生 aura** 和 **寿命流失** 两个本剧专属状态。所有状态都给"主光方向 + 色温 K + 主辅点缀 hex"三件套，shot prompt 的 `光线 / 色调:` 行 byte-identical 引用。

| 状态名 | 关键词 / 描述 | 主光方向 | 色温 | 主 / 辅 / 点缀 hex | 视觉引用 |
|---|---|---|---|---|---|
| 重生灰晨 | 主角刚醒来于乞丐 / 散修身份，灰尘漫光，肤色虚浮 | 顶左 30° | 5000K | 灰青主 `#7a8688` / 土黄辅 `#a8946a` / 银白点 `#d8d8d0` | 1) 《琉璃》早期凡间桥段灰晨调；2) Seedance 1.0 Pro xianxia 案例 dim morning；3) 长月烬明前传转生场景 |
| 寄生 aura（**本剧专属**） | 主角觉醒寄生系统时，aura 由暖橙→冷紫，黑色细丝缠手指，瞳孔残影一帧 | 自身散光 | 6500K cold | 寄生紫 `#4a1a5a` / 黑底 `#0a0a0a` / 死灰金高光 `#6e5a3a` | 1) 《长月烬明》"五彩斑斓的黑"；2) 《苍兰诀》东方青苍黑紫魔气；3) Seedance transformation prompt "green energy ribbons spiral up her body" pattern |
| 寿命流失（**本剧专属**） | 寄生升级后，主角嘴角血 / 鬓边骤白一缕 / 皮下青脉浮现，背景失色 0.3s | 弱顶光 + 冷月辅 | 4000K → 3000K（暖 → 冷漂移） | 失血灰 `#9c8a8a` / 青脉淡蓝 `#5a7a8a` / 嘴角血 `#7a1a1a` | 1) Wuxia / xianxia "burning lifespan" trope per TVTropes "Spirit Cultivation Genre"; 2) 渡劫衰老前置渲染（释圣文化 "成仙都要渡雷劫"）；3) 《长月烬明》末期主角虚弱镜头 |
| 仙气（正道宗门） | 浅金 / 月白柔光自上倾泻，雾岚环绕，剑气浮空 | 顶 + 后逆光 | 5500K | 银白主 `#f5f5f0` / 浅金辅 `#e8d098` / 青点 `#a8c8c0` | 1) 《琉璃》白衣帝君；2) 《沉香如屑》上仙界视觉；3) "高 key 仙气调" 大作设计网站分析 |
| 散修土褐（**本剧专属调整**） | 主角散修期 / 凡尘村落，土路 + 草木 + 朴布；自然光，无炫光 | 顶日光 | 5200K | 土褐主 `#8c6a4a` / 草绿辅 `#7a8a5a` / 麻白点 `#d8c8a8` | 1) 仙侠剧凡间场景设计（"长月烬明 2000 套衣服"知乎分析）；2) 道袍中等法师青色等级（起点中文网道袍九级）；3) 《琉璃》凡尘场景 |
| 魔门紫黑骨白 | 魔门据点 / 反派出场，深紫 + 黑 + 骨白点睛，烛火 / 紫焰为光 | 低位侧光 + 自发烛 | 3500K | 深紫主 `#2a0a3a` / 漆黑辅 `#0a0a0a` / 骨白点 `#e8d8c0` | 1) 长月烬明魔界宫殿（renderbus 渲染案例）；2) 苍兰诀月尊视觉；3) 网传"魔门"百度百科服饰描述 |
| 丹房琥珀红 | 炼药场景，丹炉火 + 药材光晕 + 木质柜反光，温暖核心 | 丹炉自发 + 顶弱 | 2800K 暖 | 琥珀主 `#c4842a` / 余烬红辅 `#8a2a1a` / 木褐点 `#5a3a2a` | 1) "Abstract Swirling Hues of Fiery Red and Golden Yellow" Dreamstime；2) Canva 琥珀色配色"深棕 + 红" 方案；3) 修真世界设定 24 炼丹师 |
| 灵田晨光 | 修真灵田 / 药王谷，浅阳轻雾，青草反光，灵气可见 | 顶日 + 雾扩 | 5800K | 草绿主 `#4a7a4a` / 阳金辅 `#e8c878` / 雾白点 `#f0f0e8` | 1) mozun_chongsheng "草药晨光"；2) 长月烬明灵兽山场景；3) 仙侠剧灵田典型场景 |
| 月夜冷峻 | 雪山 / 万剑宗 / 寒山场景，冷月白光 + 远山深青 | 月光（冷顶） | 4500K | 银青主 `#a8b8c8` / 深青辅 `#1a3038` / 黑山点 `#0a0a14` | 1) mozun_chongsheng "月夜冷峻" baseline；2) 苍兰诀月夜场景；3) 长月烬明雪山段 |
| 雷劫 | 黑紫闪电 + 乌云压顶 + 金紫电柱，渡劫专属 | 雷顶光（瞬时） | 5500K（雷峰）+ 9000K（电脉冲） | 雷紫主 `#6a2a8a` / 雷金辅 `#e8b830` / 黑云点 `#0a0a14` | 1) 修仙要渡雷劫释圣文化分析；2) 长月烬明渡劫桥段；3) "Eastern immortal cultivation blue-purple gold palette" web research |
| 焦土战后（**本剧专属调整**） | 复仇蒙太奇 / 灭门遗迹，灰烬 + 暗血 + 烟雾，无主光 | 散光 + 烟扩 | 3800K | 灰烬主 `#5a5048` / 暗血辅 `#3a1a14` / 烟白点 `#8a8074` | 1) 长月烬明末世感场景；2) 网文末世仙侠典型；3) Cinematic battle aftermath 调色（"焦土" via 仙侠剧"丧葬风" 网易分析） |
| 系统弹窗（**本剧调整**） | 寄生系统提示，金字 + 黑底 + 银边 + **红色寿命计数器** | UI 层叠加 | 5500K | 金字 `#a8842c` / 黑底 `#0a0a0a` / 银边 `#f5f5f0` / **寿命红 `#a82c2c`** | 1) mozun_chongsheng 系统 UI baseline；2) 网文短剧系统流头部账号样式；3) "氪金仙尊" YouTube duanju cliffhanger UI |

### 3.3 配色锁定：六大场景类型 + 主角双形态（hex per setting）

#### 3.3.1 派系 / 场景类 调色板

| # | 场景类型 | 主 / 辅 / 点缀 / 高光 hex | 视觉引用（≥ 3） |
|---|---|---|---|
| 1 | **正道宗门**（紫府 / 玉清 / 等待 stage 4 命名） | 主 `#f5f5f0` 银白 / 辅 `#a8c8c0` 浅青 / 点 `#e8d098` 浅金 / 高光 `#ffffff` 月白 | 1) 《琉璃》白衣帝君调色（网易订阅服装分析）；2) 《沉香如屑》上仙界（mozun_chongsheng baseline §美学定位）；3) 道袍九级"紫色 = 大师讲经"（起点道袍等级） |
| 2 | **散修江湖**（凡尘 + 杂修 + 小宗派） | 主 `#8c6a4a` 土褐 / 辅 `#7a8a5a` 草绿 / 点 `#d8c8a8` 麻白 / 高光 `#a8946a` 黄铜 | 1) 长月烬明凡间场景（知乎"2000 套衣服"分析）；2) 仙侠剧"低饱和 + 朴布"基线（大作设计网站）；3) 道袍青色 / 白色等级（起点道袍九级） |
| 3 | **魔门 / 寄生系**（本剧主线反派 + 主角寄生态） | 主 `#0a0a0a` 漆黑 / 辅 `#2a0a3a` 深紫 / 点 `#e8d8c0` 骨白 / 高光 `#a82c2c` 暗血 | 1) 长月烬明"五彩斑斓的黑"调色（renderbus 渲染案例）；2) 苍兰诀月尊紫黑视觉（界面新闻 9246464）；3) 魔门百度百科服饰描述 |
| 4 | **丹房 / 炼药**（药王谷 + 老炼丹师据点） | 主 `#c4842a` 琥珀 / 辅 `#8a2a1a` 余烬红 / 点 `#5a3a2a` 木褐 / 高光 `#f0c898` 烛火 | 1) Dreamstime "Abstract Swirling Hues of Fiery Red and Golden Yellow"；2) Canva 琥珀色"深棕 + 红"配色方案；3) 知乎《修真世界设定 24：炼丹师》视觉描写 |
| 5 | **灵田 / 灵兽山**（修真界自然外景） | 主 `#4a7a4a` 草绿 / 辅 `#e8c878` 阳金 / 点 `#f0f0e8` 雾白 / 高光 `#a8e8a8` 灵青 | 1) mozun_chongsheng "草药晨光" baseline；2) 长月烬明灵兽山段；3) 苍兰诀外景灵田 |
| 6 | **战场 / 焦土**（灭门遗迹 + 复仇蒙太奇） | 主 `#5a5048` 灰烬 / 辅 `#3a1a14` 暗血 / 点 `#8a8074` 烟白 / 高光 `#e8a850` 余烬 | 1) 长月烬明末世段；2) 仙侠剧"丧葬风"高对比灰烬调（网易"为什么国产仙侠剧服装"分析）；3) Wikipedia Duanju 仙侠 reborn-revenge cliché 焦土回忆 |

#### 3.3.2 主角双形态 visual signature（**本剧 production hook**）

| 形态 | 出现时机 | 体态 | 肤 / 瞳 / 唇 / 发 | 服饰 hex | aura | 视觉引用 |
|---|---|---|---|---|---|---|
| **重生弱体**（state A） | ep01–ep05 + 任何回忆 | 微瘦 + 含胸 + 步伐迟（病初愈） | 肤色虚浮带灰 `#cab8a8` / 瞳暗褐 `#3a2818` / 唇色淡 `#a87060` / 发褐黑微乱 | 麻布灰青长袍 `#7a8a8a` + 草绳腰带 `#5a4a3a` | 无 aura；自身散弱光（觉醒前） | 1) 长月烬明转生段；2) 琉璃凡尘男主早期；3) Spirit Cultivation Genre TVTropes "early-stage" |
| **寄生觉醒**（state B） | ep05+ 系统首次激活后 | 直立 + 步轻 + 微飘起（修为内涌） | 肤色冷白 `#e8d8d0` / 瞳由暗褐 → 寄生紫 `#4a1a5a` / 唇色冷紫 `#a07090` / 发漆黑束半发 | 同款麻布外披 + 内衬黑紫暗纹 `#2a0a3a` 中衣 | 黑紫细丝自指尖溢出 + 寿命红 `#a82c2c` 计数器在系统弹窗 | 1) 苍兰诀东方青苍觉醒；2) 长月烬明澹台烬 dual-state；3) Seedance "energy ribbons spiral up" transformation prompt |

**关键契约**：两 state **必须共享 face-differentiator**——本剧主角的 face-differentiator 候选为 **左眼下方 0.3cm 灰青胎记**（state A 模糊难见 / state B 在寄生紫调下显现为冷紫色斑）。stage 4 character bible 在角色档定稿，stage-6 validator 强制扫描"两 state 同人识别"。

#### 3.3.3 寄生系统升级视觉签名（**本剧 production hook 之 2**）

寄生升级 **3 拍序列**（每次升级触发，时长固定 5s，作为可复用 motif）：

| 拍 | 时长 | 视觉 | 音 / 字 |
|---|---|---|---|
| 拍 1 — 系统提示 | 0–1.5s | 金字弹窗自下浮起 `叮——任务完成 / 修为 +1 阶` + 寿命红计数器跳动 `寿命 -7 年` | 内嵌硬字幕黑底金字 |
| 拍 2 — 寄生 aura | 1.5–3.5s | 主角双瞳由暗褐 → 寄生紫一闪 / 黑紫细丝自指尖逆向缠手腕 / aura 由暖橙转冷紫 / 背景失色 0.3s | 顿挫节奏（静默 0.5s） |
| 拍 3 — 寿命流失 | 3.5–5s | 主角嘴角血迹一线（薄）/ 鬓边骤白一缕 / 皮下青脉浮现 0.5s / 字幕"代价已扣除"淡入淡出 | 内嵌硬字幕红字 |

该 motif 在 ep01–ep05 各出现 1 次（按 qa.md 5 集 detail batch），由 shot prompt 复用"寄生系统升级 motif v1"标签，stage 4 加入 `style_guide.md` 后即作为 byte-stable 取词。

### 3.4 负向 prompt baseline（项目专属补充）

> **第一节 verbatim 继承 mozun_chongsheng follow-up 001 + 008 + 012 共 39 项**——亚洲俊男靓女 11 项 + 影视写实 14 项 stylization + photorealism 14 项。**第二节为本剧项目专属新增 12 项**。

#### 3.4.1 verbatim 继承（39 项 — 见 mozun_chongsheng `style_guide.md` § 渲染样式锁定 § 负向关键词）

```
[14 项 stylization]
anime / cartoon / illustration / chibi / manga / 国漫 / 插画 / 工笔 / 水墨写意 / 二次元
CGI 3D render / 塑料皮肤 / 玩偶感 / 低多边形 / painterly stylization / 卡通色 / 荧光色

[11 项 AI 同质化]
不要 AI 生成同质化脸 / 不要 AI 通用脸 / 不要 模板化俊男靓女 / 不要 千篇一律的丹凤眼锥子脸
不要 西方审美面孔 / 不要 欧美选角风 / 不要 浓眉大眼欧化
不要 同款脸 / 不要 跨角色面孔重复 / 不要 网红脸 / 不要 整容脸模板

[14 项 photorealism 强化]
不要 anime style face / 不要 manga style / 不要 cartoon style / 不要 illustration / 不要 stylized
不要 over-smoothed skin / 不要 plastic skin / 不要 doll-like face / 不要 wax figure
不要 AI-generated face / 不要 AI artifact / 不要 generic AI face / 不要 same-face syndrome
不要 模糊轮廓 / 不要 缺乏皮肤细节 / 不要 over-airbrushed
```

#### 3.4.2 项目专属新增（12 项）

```
[场景 / 道具]
不要 现代电子设备 / 不要 现代家具 / 不要 西式柱廊 / 不要 玻璃幕墙
不要 塑料质感法器 / 不要 树脂剑 / 不要 圣诞树式仙树（避免装饰过密）

[叙事 / 视觉 anti-pattern]
不要 全体合影站位（per mozun_chongsheng shot01 已有，本剧继续锁定）
不要 干站着空对镜头 / 不要 说话时不看说话对象 / 不要 非说话者面无表情
不要 寿命流失镜头里出现"血池"等 mozun_chongsheng 专属意象（防止跨项目视觉撞档）
不要 主角觉醒态出现"金赤双瞳"（mozun_chongsheng 沧冥专属，本剧寄生瞳为"寄生紫 #4a1a5a"）
```

### 3.5 aspect ratio 与标准 prompt-language 默认值

- **比例**：9:16 lock。任何 shot prompt `比例:` 必填 `9:16`。横屏（16:9 / 1:1）需 stage 4 spec 内显式 divergence note。
- **时长**：3–15s per beat（per ai_video.md rule #6）。author-side heuristic 全文继承：
  - 快反应 / cut-in / 微眼神：3–5s
  - 单动作 / 一句台词：5–8s
  - 两人对话 / 短交锋：8–11s
  - 多人僵持 / 独白 / hook 落点 / 封面帧：11–15s
- **寄生升级 motif** 固定 5s（per § 3.3.3）。**寿命流失三拍** 必填 `节奏: 顿挫`。
- **Kling vs Seedance 选用建议**（基于 § 2.5 motion vocab 研究）：
  - ≤ 10s 单 take：Kling 2.1 Pro 与 Seedance 1.0 Pro 都可，按角色 reference 完备度选（有 turntable 优先 Kling image-to-video）。
  - 11–15s 单 take：优先 Seedance 1.0 Pro（Kling 需切片 + seam frame）。
  - 升降镜 > 1 画面或环绕 > 180°：Seedance 优先。
  - 寄生升级 motif（顿挫 + match-on-eye）：建议 Seedance（hard cut + temporal beat 控制更稳）。
- **shot 取词 lexicon 强契约**：景别 / 运镜 / 速度 / 光影状态 / 转场 5 张表的关键词为 stage-6 唯一合法来源，shot prompt **不新造词**（per ai_video.md rule #12.4 v4 "镜头取词契约"）。

### 3.6 转场词典（8 类 — verbatim 继承 + 1 本剧新增）

| 转场 | 用途（本剧适配） |
|---|---|
| 闪白 | 修为大关突破 / 寄生觉醒瞬间 |
| 闪黑 | 重大死亡 / cliffhanger |
| 雷劫切 | 卷尾大事件 / 主角突破至化神以上 |
| 蒙太奇 | 复仇 montage / 上集召回 / 时间过渡 |
| 推镜过 | 同场景内空间转换 |
| 字幕过 | 集间过渡（"三日后"） |
| 系统弹窗过 | 寄生系统任务发布瞬间（强制使用） |
| **寿命计数器过**（**本剧新增**） | 寄生升级三拍序列最后 1s 转下个场景，红字计数器 fade out 同时下一场景 fade in |

### 3.7 字幕规范（per ai_video.md rule #12.4 三选一推荐 + 字体描边）

**默认三选一选择**：本剧主体走 **后期软字幕**（per mozun_chongsheng baseline 一致）；以下情况强制 **内嵌硬字幕**：
- 寄生系统弹窗（`叮——任务完成 / 修为 +1 阶`、`寿命 -N 年`、`代价已扣除`等）。
- 集头标题（`第 N 集 + 标题`）+ 集尾 cliffhanger 提示。
- 标志台词 / 黄金钩台词（如重生主角 ep01 第一句"原来是你们"）。

**字体规范**（verbatim 继承 mozun_chongsheng）：
- 中文：方正粗黑简体（系统弹窗用宋体 / 楷体保留古风感）
- 英文（YouTube Shorts 双语 pass）：Helvetica Neue Bold
- 颜色：白 + 黑描边（保证 9:16 任意背景可读）；寿命计数器红 `#a82c2c` + 黑描边
- 位置：y ≈ 1100–1180（最底部）；系统弹窗 y ≈ 200–400（顶部至上 1/3 线）
- 字号：32–36 pt 主字幕；24–28 pt 系统弹窗副字
- 时长：每屏字幕 ≥ 1.5 s

**双语版（YouTube Shorts，post-v1 follow-up）**：上中文 + 下英文，间距 8 pt；修真术语保留汉字 + 英文同位语（练气 Qi Refining、金丹 Golden Core、渡劫 Tribulation、寄生系统 Parasitic System、寿命 Lifespan）。

---

## 4. Open questions

1. **最终中文标题 + pinyin slug**：本档以 `xianxia_new` working slug 为占位，最终 slug 由 stage 4 确定（per qa.md 已记录）。slug 变更不影响本档内容；stage 4 把本档 §3 lift 时仅替换 README H1 / `ai_videos/{final_slug}/` 路径占位即可。
2. **face-differentiator 候选确认**：本档建议主角候选为 "左眼下方 0.3cm 灰青胎记"（state A 半隐 / state B 寄生紫调下显现）。最终标志特征点 + 与现有 mozun_chongsheng 10 角色互斥校验在 stage 4 character bible 完成。
3. **寄生紫具体 hex 微调**：`#4a1a5a` 是当前提案，跟 mozun_chongsheng 的 "护黄金 + 暗血红" baseline 完全平行不撞色。但若 stage-4 立绘 test 出来"显黑不显紫"（Seedream 在低饱和 9:16 上紫色易吃光），建议升至 `#5a2a6a`（+ 10% L+S）作为 fallback。stage-5 validation 把这个 hex 作为可调参数。
4. **寿命计数器 UI 字体**：本档默认走宋体 / 楷体保古风感，但若 ep01 测试发现"宋体在 9:16 小尺寸不耐看"，fallback 走方正粗黑 + 红色 + 闪烁动画（per 头部网文短剧"系统流"常用样式）。
5. **正道宗门内部派系视觉差异**：本档把"正道"作为单一 palette（银白 + 浅青 + 浅金）描述，但 qa.md 已锁"复仇靶标分散于三方"——意味着正道内部至少 2–3 个宗门需要再分化。建议 stage 4 在 character bible 阶段为每个具名正道宗门各加一个"点缀色"（如紫府 + 雷青 / 玉清 + 月白 / 等），但主调保持本档锁定的 `#f5f5f0 + #a8c8c0 + #e8d098`。
6. **焦土场景的"血"hex 选用**：暗血 `#3a1a14` 是当前提案，比 mozun_chongsheng 暗血红 `#5a1a1a` 更"灰更冷"——为了与 mozun_chongsheng 视觉分流。stage-4 立绘试帧后若发现"过冷不像血"，fallback 走 `#4a1a18`。
7. **寄生升级 motif 是否在每集都触发**：本档 § 3.3.3 假设 ep01–ep05 各 1 次。但 qa.md 锁"集集 cliffhanger" + "升级 → 遇敌 → 险胜 / 蛰伏 → 再升级"循环——意味着 motif 频率可能更高。stage 4 在 shotlist 阶段决定每集 motif 出现次数（建议 1–2 次为佳，避免审美疲劳）。
8. **跨剧场景 reuse 是否合法**：本剧与 mozun_chongsheng 共享 ai_video.md rule 12.3 场景档机制，但 scenes/ 下文件不能复用 mozun_chongsheng 的 `s1_长阶顶` / `s2_大殿内` 等（per copyright_clearance 约束）。本剧 scenes/ 全新立档；只视觉 vocabulary 共享（光影状态 / 调色 / 镜头词典 OK），具体场景 file path 独立。

---

## 5. References — web visual citations（≥ 3 per major palette decision）

### 主基调 / 渲染样式

- 2026 视觉革命 — 汉宸创盛 AI+调色重新定义漫剧标准 — mtz.china.com 2026-04-01
- 2026 年 AI 真人短剧大模型选型指南：从 Seedance 到 Pixmax — Pixmax cnblogs.com 2026
- 日产上千部短剧，AI 狂飙背后行业早已两极分化 — 钛媒体 tmtpost.com 2026
- AI 短剧深度调研报告：2023–2026 — TVtalk 乂媒体 tvtalk.cn 2026
- 不吹不踩，AI 真人短剧到底在改变什么 — 澎湃 thepaper.cn 2026

### 正道宗门（银白 + 浅青 + 浅金）

- 《琉璃》"白衣帝君" 服装分析 — 网易订阅 163.com 2020 (其他的仙侠剧请多看看琉璃的服装)
- 《长月烬明》造型详解，主打敦煌风，2000 多套衣服 — 知乎 zhihu.com 2023
- 道袍九个级别一览表（紫色 = 大师 / 青色 = 中等 / 白色 = 冥司）— 起点中文网 qidian.com

### 散修土褐

- 长月烬明凡间场景与服装造型（"2000 多套衣服" 文中凡尘段）— 知乎 zhihu.com 2023
- 仙侠剧"低饱和 + 朴布"基线评论（《长月烬明》大火，仙侠妆造还有救么）— 大作设计网站 blog.bigbigwork.com 2023
- 道袍青色等级（中等法师拜斗祝寿）— 起点中文网 qidian.com

### 魔门 / 寄生（紫 + 黑 + 骨白）

- 长月烬明特效出圈，9 家视效公司联手打造国风新仙侠（"五彩斑斓的黑" 调色） — renderbus.com 2023
- 《长月烬明》大火：仙侠妆造还有救么 — 大作设计网站 blog.bigbigwork.com 2023
- 《长月烬明》口碑与热度两极分化 — 界面新闻 jiemian.com 9246464
- 苍兰诀月尊紫黑视觉评论 — 界面新闻 jiemian.com 同上
- 魔门词条与历代魔门服饰描述 — 百度百科 baike.baidu.com

### 丹房琥珀红

- Abstract Swirling Hues of Fiery Red and Golden Yellow — Dreamstime 392131649
- 琥珀色的含义与配色方案（深棕 + 红组合）— Canva 可画 canva.cn
- 《修真世界深度设定二十四：修真十六艺·炼丹师》— 知乎 zhuanlan.zhihu.com 65257747

### 灵田 / 月夜 / 雷劫

- 仙侠剧灵田与外景典型镜头（"长月烬明 2000 套衣服" 知乎分析含外景章节）— zhihu.com 2023
- 修仙要渡雷劫？看看道教如何渡劫 — 释圣文化 chanzl.com / Sohu 113379884
- 玄雷天君词条（雷劫蓝紫 + 金视觉描述）— 百度百科 baike.baidu.com 65240596
- 雷劫词条 — 百度百科 baike.baidu.com 1653816

### 焦土 / 战后

- 长月烬明末世段渲染案例 — renderbus.com 2023
- 国产仙侠剧"丧葬风" 服装色调评论 — 网易 163.com H13C6BT50518CSFQ
- Wikipedia "Duanju" — micro-drama vertical-first 转 cliché 焦土回忆 — en.wikipedia.org Duanju

### 系统弹窗 UI

- 氪金仙尊 短剧片头 + cliffhanger UI 样式 — YouTube 九州快看（《氪金仙尊》全集）
- 网文短剧"系统流"头部账号视觉样式（mozun_chongsheng baseline 已引用 + 综合）
- B 站短剧 "晚年无敌系统打造最强家族" cliffhanger UI 节选 — bilibili.com BV1DF1KB2ECS

### Seedance / Kling motion vocab + 模型适配

- Seedance 2.0 Complete Prompting Guide — Higgsfield higgsfield.ai/blog/seedance-prompting-guide
- awesome-seedance-2-prompts — YouMind-OpenLab GitHub
- 用 Seedance 2.0 做 AI 短剧 — 知乎 zhuanlan 2011197758191730921
- Kling 2.6 Pro Motion Control — RunComfy / Artlist / MindStudio model cards 2026-04
- Seedance 1.0 Pro Prompt Guide — seedancepro.net

### Vertical 9:16 + Douyin 短剧

- Duanju — Wikipedia en.wikipedia.org Duanju
- Micro-Dramas And Vertical-first Storytelling — Vitrina vitrina.ai
- AI redefines China's booming micro drama industry — Xinhua english.news.cn 20260325
- Chinese Video Sites Douyin Kuaishou Launch AI-Generated Mini-Dramas — Yicai Global yicaiglobal.com
- 2026: Year One of China's AI Film Industry — Amber Zhang baiguan.news

### 寿命流失 / 寄生代价 trope

- Spirit Cultivation Genre — TVTropes pmwiki/Main/SpiritCultivationGenre
- "成仙都要渡雷劫？雷劫是什么样的存在" — 释圣文化 chanzl.com 7970
- 雷劫词条（修仙烧寿命描述）— 百度百科 baike.baidu.com 1653816

---

## 6. Pre-reading consulted

- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/user_input/revised_prompt.md`
- `C:/workspace/spec_coding/specs/ai_video/xianxia_new/interview/qa.md`
- `C:/workspace/spec_coding/ai_videos/mozun_chongsheng/style_guide.md`
- `C:/workspace/spec_coding/ai_videos/mozun_chongsheng/world.md`
- `C:/workspace/spec_coding/ai_videos/mozun_chongsheng/characters/c1_沧冥/c1_沧冥.md`
- `C:/workspace/spec_coding/ai_videos/mozun_chongsheng/episodes/ep01/shots/shot01/shot01.md`
- `C:/workspace/spec_coding/.claude/agent_refs/project/ai_video.md` (rules #1, #2, #4, #6, #7, #12.1, #12.2, #12.3, #12.4 v4)
