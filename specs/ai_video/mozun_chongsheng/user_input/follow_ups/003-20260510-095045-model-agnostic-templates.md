# Follow-up draft 003 — 2026-05-10

Summary: 把 rule #12 模板从 Kling/Seedance 三件套抽象成「视频 shot prompt + 静帧 seam-frame prompt」二件套（model-agnostic），shot prompt 的 schema 不再依模型区分；同时把这套新模板**回填到 mozun_chongsheng** 的所有现有 artifacts —— 角色档（rule #12.1 缺失四段补齐）、立绘（rule #12.2 子段重构）、shot prompts（rule #12.4 强制补齐 `台词 / 字幕:` + `节奏:`）、新增 `scenes/` 复用场景层（rule #12.3）。

## 用户原话

> you dont need to care if the prompt is for seedance or kling, lets say it is for some AI model, so you dont worry about that in your settings. Also try to keep the prompt you generated follow the template and well structured for the AI models like seedance and kling. In the end plesae use to new template you created to update the mozun_chongsheng ai videos

## (A) agent_refs 模板抽象（model-agnostic）

`.claude/agent_refs/project/ai_video.md` rule #12 改写：

| 旧 | 新 |
|---|---|
| 三件套：Kling / Seedance / Seedream seam（按模型分列） | 二件套：视频 shot prompt / 静帧 seam-frame prompt（按 prompt 用途分列） |
| 字段矩阵 3 列（`Kling | Seedance | Seedream seam`） | 字段矩阵 2 列（`视频 shot | 静帧 seam`） |
| 「Seedance: ✅(+ 体型 / 服饰展开)」inline | 抽出为「12.4-A 角色字段展开规则」：参考图存在 ⇒ 一句话锁定；参考图缺失 ⇒ 一句话锁定 + 体型/发型/服装/道具 inline 展开 |
| 文件命名隐含模型（`shotNN_kling.md` / `shotNN_seedance.md`）| 文件命名通用：`shotNN_{model}.md`（model = kling / seedance / sora / veo / ...）；同一 shot 可同时存在多个 model variant |

**Rule #5（Dual-prompt requirement）**：保留——每 shot 仍要求 `_kling.md` + `_seedance.md` 双 variant 输出（项目-output 政策），但模板字段（rule #12.4）统一不分模型。

## (B) 回填 mozun_chongsheng

### B1. 角色档（10 份，`characters/{中文名-身份}.md`）

每份补齐 rule #12.1 缺失的四段：

- `## 性格 / 动机` —— 核心动机 / 表层人设 / 反差点 / 关键弱点（要点列表）。
- `## 标志台词或口头禅` —— 1–3 条 byte-stable 短句；从 spec.md FR-38 / 关键场景中提炼（沧冥 ep59「当年你们怎么对我，今日我便十倍奉还」已在角色档「关键场景」字段，提到 `## 标志台词或口头禅` 主段）。
- `## 配音参考`（planning-only）—— 声线 / 语速 / 口音 / 演员参考。仅作未来 TTS 元数据。
- `## 负向` —— re-paste `style_guide.md § 负向锁定` + 1–2 条角色专属（如沧冥「不要看起来超过三十岁」、柳红袖「不要肚兜 / 露肩」per follow-up 002）。

### B2. 角色立绘（10 份，`characters/ref_images/{中文名-身份}-立绘.md`）

把现有单一 `## Prompt` 块按 rule #12.2 拆成八子段：

```
## Prompt
### 主体 / 构图
### 面部
### 服装
### 姿态
### 背景
### 光源
### 风格
## 负向
```

子段内容直接从现有 prompt body 切分；不重写、不增加新视觉元素，只是按 schema re-paragraph。`## 负向` 已存在，保留即可。

### B3. shot prompts（视频 shot 与静帧 seam-frame）

**视频 shot prompt**（每 shot 的 `_kling.md` + `_seedance.md` 两份，总计约 100 份，ep01..ep05）：

每份在 `光线 / 色调:` 后、`渲染样式:` 前插入两行：

```
台词 / 字幕: {三选一，由 episode.md 剧本决定}
节奏: {慢 / 中 / 快 / 顿挫}
```

`台词 / 字幕:` 三档:
1. `内嵌硬字幕 "{台词原文}" — {字体调性}`
2. `后期软字幕 "{台词原文}" — {字体调性}`
3. `无台词 / 默剧`

无台词的 shot（如 shot01 镇压、shot10 闪剪）填 `无台词 / 默剧`；有台词的 shot（如 shot07 爽点峰值、shot08 揭幕）按 episode.md 剧本提炼台词原文，默认 `后期软字幕 — 方正粗黑 白底黑边`（per style_guide.md 字幕规范）。

`节奏:` 四档：依 shotlist.md 镜头描述判定（雷劫合围 = 顿挫；推镜紧张 = 中；快剪 cliffhanger = 快；慢镜虐点 = 慢）。

**静帧 seam-frame prompt**（每 shot 的 `_lastframe_seedream.md` + 每集首镜的 `shot01_startframe_seedream.md`，总计约 55 份，ep01..ep05）：

不补 `台词 / 字幕:` / `节奏:`（rule #12.4 still 列只要求 `主体定义 / 姿态（frozen instant） / 渲染样式 / 比例 / 负向 / 镜头(仅景别) / 角色 / 场景 / 光线/色调`）。当前 seam-frame 文件已含全部静帧字段；此次仅做 sanity check，不强制 patch。

### B4. 新增 `scenes/` 复用场景层（rule #12.3）

扫描 ep01..ep05 shotlist.md，识别 ≥ 2 shots 复用的地点，创建：

- `scenes/{scene_name}.md` —— 场景档（8 字段锁定描述符 + 关键变化态 + 出现镜头）
- `scenes/ref_images/{scene_name}_seedream.md` —— 场景立绘 prompt

候选地点（待 subagent 扫描确认）：
- 沧冥魔域黑金大殿前魔气长阶顶 —— ep01 shot01..shot10, ep02 shot01 起势镇压地点
- 紫霄宫桃花殿 —— 苏璃月主场（多集出现）
- 红袖招酒楼厅堂 —— 柳红袖主场（多集出现）
- 药王谷山涧 —— 苓夭夭主场（多集出现）
- 万剑宗剑山 / 玄炎宗血池 / 太清门论道殿 / 影神殿暗室 —— 五大宗主主场（部分跨集）

仅出现一次的场景不立档（保留 inline）。

## 期望行为

1. 任何**未来** ai_video task 在 stage 4/6 生成 prompt 时按 rule #12 二件套模板出文，不再分 Kling/Seedance schema；文件名仍可 `shotNN_kling.md` / `shotNN_seedance.md` 区分输出目标。
2. mozun_chongsheng 现有 artifacts 在本次 follow-up 完成后**字段级**对齐 rule #12（10 角色档 / 10 立绘 / ~100 shot prompts / 新增 scenes/）。
3. ai_video_management webapp 打开 `ai_videos/mozun_chongsheng/scenes/` 时可看到复用场景文件清单。
4. follow-up 001（影视级真人写实锁定）+ follow-up 002（中文文件名 + 18-35 年龄观感 + 柳红袖不暴露）保持有效，本 follow-up 不动那些锁定。

## Out of scope

- 不重新生成立绘 / shot prompt 的视觉内容（主体描述、姿态、配色不变）；仅做 schema 重排 + 字段补齐。
- 不调整 60 集大纲 / 修为路径 / 钩 / 卷边界。
- 不生成 ep06-ep60 的 shot prompts（那是 stage-4 regen 范围）。
- 不引入 model 之外的新 AI 模型 variant（Sora / Veo 仅作为 model-agnostic 模板的参考实例，不创建新 `shotNN_sora.md` 文件）。
- 不改抖音 + YouTube Shorts 发布元数据。
