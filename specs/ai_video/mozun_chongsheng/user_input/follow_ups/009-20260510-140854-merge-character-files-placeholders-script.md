# Follow-up draft 009 — 2026-05-10

Summary: 三件事一并做：(A) 把 `characters/{name}.md` (bible) + `characters/ref_images/{name}-立绘.md` (turntable ref) **合并**为单一 `characters/{name}.md` 文件 per character；删除 `characters/ref_images/` 文件夹。(B) 在每个 `shotNN.md` 文件中**删除 Seam-frame still prompts 段** (startframe + lastframe Seedream 代码块)，每 shot 仅保留**一个**视频 prompt。(C) 为每 shot 的视频 prompt 加 **Reference placeholders 段**：列出本 shot 涉及的所有角色 + 背景场景占位符（如 `{ref_沧冥}` / `{ref_长阶顶}`），用户在 paste 到 Seedance 时手动替换为实际 reference 文件路径；prompt body 内文也用相同 placeholder syntax 引用。同时确保**多角色 dialogue 使用 script 格式**（每角色一行台词，psake-friendly）。

## 用户原话

> under characters left menu, we have a few md files and also another gourp of md files under ref_images, combine them into one md file per charactor. Also under episode each shotNN.md file, remove the start frame and end frame prompt, just one prompt describe the entire shot. Also the prompt should also contain the script of each charactors involved. and at the beginning it should leave some placeholder for me to add {reference} like charactor_A {placeholder}, I will add reference later When I copy prompt to seedance and add my reference video. So leave a placeholder for all charactors and background scenes involved in current shot

## 工作流变更

**Before（follow-up 008）**：

```
characters/
├── 沧冥-魔尊本相.md        # bible
├── ...                    # 其他 9 角色 bible
└── ref_images/
    ├── 沧冥-魔尊本相-立绘.md   # turntable ref prompt
    └── ...                # 其他 9 角色 ref

episodes/ep{NN}/prompts/
├── shot01.md   # Shot context + 视频 prompt + Seam-frame still prompts (start + last)
├── shot02.md   # Shot context + 视频 prompt + Seam-frame still prompts (last only)
...
```

**After（follow-up 009）**：

```
characters/
├── 沧冥-魔尊本相.md   # 自包含: bible + turntable ref (合并)
├── ...                # 其他 9 角色合并文件
(无 ref_images/ 文件夹)

episodes/ep{NN}/prompts/
├── shot01.md   # Shot context + Reference placeholders + 视频 prompt (无 Seam-frame stills)
├── shot02.md   # 同上
...
```

每角色 2 文件 → 1 文件（10 角色减 10 文件，删 ref_images/ 子目录）。
每 shot file 的 Seam-frame still prompts 段被删除；shot01 of each ep 之前有 startframe + lastframe code blocks，现仅保留 video prompt。

## (A) Character 文件合并 schema (rule #12.5 v3 amend)

每个 `characters/{name}.md` 现含两段：

````markdown
# {中文名} · {身份}

## 角色定位
（原 bible 内容，per follow-up 003 + 008）

## 锁定描述符（11 字段，跨集 byte-identical）
（原 bible 表，含 #1..#11，含 6-子项 face-differentiator + 标志特征点 per follow-up 008）

## 性格 / 动机
## 标志台词或口头禅
## 弧光
## 关键场景
## 标志能力或动作
## 配音参考（planning-only，v1 不生成 TTS）
## 负向

---

# 视频 reference prompt — Seedance / Kling / Sora / Veo / Runway Gen-3（360° 转身样片 + 标准台词）

> **用法**：复制下方代码块整段，粘贴到支持 video reference 的 AI 视频模型（Seedance / Sora / Veo 3 / Runway Gen-3 / Kling 等）。**该样片本身**作为后续真正 shot 视频的 video reference 输入，锁定形象 + 声线 + 节奏。

```text
{完整 turntable prompt body — angular character + 12s 360° turntable + 5 句标准台词 + 三点布光 + 9:16 + 负向}
```

### 5 句标准台词（中文，配音演员对照表）

| # | 台词 | 用途 | 时段 | 情绪基调 |
|---|---|---|---|---|
| ... |
````

`characters/ref_images/` 文件夹**整体删除**。

## (B) Shot 文件 schema (rule #12.6 v2 amend) — drop Seam-frame still prompts

每个 `shotNN.md` 现含 **3 段**（去除 Seam-frame still prompts 段）：

````markdown
# ep{NN} / shot{NN} · {summary}

## Shot context — human review

**Summary**: ...
**出场角色 / Characters in this shot**: 表
**场景 / Scene**: ...
**时长 / Duration**: ... + timed beats
**Reference uploads — pre-flight checklist**: ...

---

## Reference placeholders — 复制 prompt 前请准备好以下 reference 并替换占位符

| Placeholder | 替换为 | 说明 |
|---|---|---|
| `{ref_沧冥}` | 沧冥 turntable.mp4（从 `characters/沧冥-魔尊本相.md` 渲染） | 角色 reference |
| `{ref_白月清}` | 白月清 turntable.mp4（从 `characters/白月清-紫霄宫主.md` 渲染） | 角色 reference |
| `{ref_长阶顶}` | 沧冥魔域-黑金大殿长阶顶 background reference 视频 / 图（参考 `scenes/沧冥魔域-黑金大殿长阶顶.md`） | 场景 reference |

---

## 视频 prompt — 复制下方代码块到视频生成模型

> **用法**：① 先按上方 Reference placeholders 表准备好 reference 文件并上传到模型。② 把下方代码块整段粘贴到 Seedance / Sora / Veo / Runway / Kling，**手动把 `{ref_xxx}` 占位符替换为模型识别的 reference 标记**（每模型语法略不同：Seedance 上传后用 `[reference]` 链接 / Kling 用 `input_image_urls` / 其他模型按其文档）。

```text
角色: {ref_沧冥} 黑长发束高马尾，黑金锦缎长袍金线绣兽，赤红丹凤眼俊朗锋锐，右眼下方朱砂痣，左手负后，魔气如墨。
场景: {ref_长阶顶} 沧冥魔域黑金大殿前魔气长阶顶，黑色星河悬天，无昼夜冷月为光，五道光影自四方迫近合围
镜头: 大全景 + 仰拍，升降镜自下缓缓升至雷柱顶端
动作: ...timed beats...
台词 / 字幕（多角色 script 格式）:
  - {ref_沧冥} 沧冥: 内嵌硬字幕 "《魔尊归来》第一集 镇压" — 方正粗黑 白底黑边
  - 旁白 / 标题: ...（如有）
光线/色调: ...
节奏: 顿挫
渲染样式: ...
比例: 9:16
时长: 8s
负向: ...
```
````

**关键设计：**

1. `Reference placeholders` 段在 Shot context 之后、视频 prompt 之前，是用户的"备料清单"。
2. Prompt body 内文也用 `{ref_xxx}` placeholder syntax 引用 character / scene；user paste 到 Seedance 时手动替换为模型实际接受的 reference token。
3. 多角色 `台词 / 字幕` 必使用 multi-line script 格式（每角色一行），即使是单角色 shot 也建议使用 multi-line（一致性）。
4. Static seam-frame Seedream prompts **移除**——用户实际上传 turntable.mp4 + character ref + scene ref 已足够；seam stitching workflow 是可选高阶用法，不再 default 出。

## (C) Placeholder 命名规范

- 角色 placeholder: `{ref_<中文名>}` 或 `{ref_<中文名>-<身份>}` (有歧义时用全名)
- 场景 placeholder: `{ref_<scene 简称>}`（取自 `scenes/{name}.md` 一句话锁定的关键词缩写）
- 用半角花括号 `{}` 包裹（user copy-paste 后 find/replace 友好）

## (D) Rule changes

- **rule #12.5 v3**: character file 合并 schema（bible + turntable ref in one file）
- **rule #12.6 v2**: shot file 三段 schema（drop Seam-frame still prompts；新增 Reference placeholders 段；强化 dialogue script 格式）
- **rule #11**: seam-frame 工作流仍保留作为可选高阶 stitching workflow 文档；但默认不在 shot file 内 ship；user 可手动用 Seedream 生成 seam frames 用于 image-to-video 模型路径

## 期望行为

1. `characters/` 下只剩 10 个 `*.md` 文件（每角色一个自包含），无 `ref_images/` 子目录。
2. `episodes/ep{NN}/prompts/` 下每 shot 1 个 `.md` 文件（无 seam-frame 独立文件，无 seam-frame 嵌入段）。
3. 用户打开任一 `shotNN.md` → 顶部 Shot context review → 中段 Reference placeholders 表（清楚知道要准备哪些 reference）→ 底段视频 prompt code block (含 `{ref_xxx}` placeholders) → 复制到 Seedance / Sora / Veo / Runway / Kling → 替换占位符 → 生成。
4. follow-up 001-008 的所有锁定 (真人写实 / 18-35 / 中文文件命名 / model-agnostic / 14 字段 schema / face-differentiator / Asian aesthetic / 11 项 AI-同质化负向) 全部保持有效。

## Out of scope

- 不重新生成 prompt body 内容（动作 timed beats / 台词 / 节奏 / 视觉描述等保持不变）。
- 不实际渲染视频或 PNG。
- 不修改 ep06-ep60 stage-4 regen 范围。
- 不解决 follow-up 002 遗留的「沧冥 三十出头 / 看似二十五」inline 不一致问题（独立 surgical follow-up）。
- 不删除 follow-up 008 的 face-differentiator / Asian aesthetic / 11 项 AI-同质化负向 — 这些保留在合并后的 character files + restructured shot files 中。
- 不重命名 character file path（仍 `characters/{中文名}-{身份}.md`）。
