# Follow-up draft 007 — 2026-05-10

Summary: 进一步**合并** `shotNN.md` + `shotNN_lastframe_seedream.md` + `shot01_startframe_seedream.md`（若 shot01）→ **单一自包含 `shotNN.md` 文件**。新文件分三段：① 「Shot context — human review」给用户阅读 / 决策（summary / characters / scene / duration / reference uploads checklist）；② 「视频 prompt」copy-paste-ready code block（已有内容保留）；③ 「Seam-frame still prompts」嵌入 startframe + lastframe Seedream prompt（也是 copy-paste-ready code blocks）。一个 shot = 一个文件 = 完整自包含。每 shot 仍 ≤ 15s 硬上限。把这套文件结构 + 多角色台词扩展抽象成 rule #12.6 写入 `agent_refs/project/ai_video.md`，让未来所有 ai_video 项目按此 schema 出文。

## 用户原话

> please combine shot01.md startframe.md and lastframe md into one shot01.md file, and inside it, first tell me some context and details about his short, this is for me to review it should mention in summary what the shot is about, what charactors are involved in this shot and what scene or background this shot happens etc. And then you should give me a copy paste prompt for this short which includes all details about the action, the charactor, and what they should talk to each other etc. I can then just copy paste this to some AI model to generate the video, remmeber each shot is only 15s max, so you can bsaed on that constraint best rearrange and organize your shot, and make sure this intsruction as well as previous instruction you abstract the common rules into the spec_driven project so future ai videos will follow

## 工作流变更

**Before（follow-up 006）**：

```
ep{NN}/prompts/
├── shot01.md                        # 出场角色 checklist + 视频 prompt
├── shot01_startframe_seedream.md    # 单独的 startframe Seedream prompt（仅 ep 首镜）
├── shot01_lastframe_seedream.md     # 单独的 lastframe Seedream prompt（每镜）
├── shot02.md
├── shot02_lastframe_seedream.md
├── shot03.md
├── shot03_lastframe_seedream.md
... ×10 shots
```

每 ep = 21 文件（10 shotNN.md + 1 startframe + 10 lastframe）。

**After（follow-up 007）**：

```
ep{NN}/prompts/
├── shot01.md     # 自包含：Shot context + 视频 prompt + lastframe Seedream prompt + startframe Seedream prompt
├── shot02.md     # 自包含：Shot context + 视频 prompt + lastframe Seedream prompt
├── shot03.md     # 同上
... ×10 shots
```

每 ep = 10 文件。从 21 文件 → 10 文件。ep01-ep05 共减少 55 文件（10 lastframe × 5 + 1 startframe × 5）。

## (A) 新文件 schema — 单一自包含 `shotNN.md`

````markdown
# ep{NN} / shot{NN} · {1-line shot summary}

## Shot context — human review

**Summary**: {2-3 句概述本 shot 的叙事 / 视觉 / 钩点。}

**出场角色 / Characters in this shot**:

| 角色 | 在本 shot 的角色 / 出场方式 | turntable reference | turntable 必需 |
|---|---|---|---|
| 沧冥 | 主体角色，正面登场，黑袍立长阶顶 | `characters/ref_images/沧冥-魔尊本相-立绘.md` | ✅ |
| 五大宗主 | 仅光影剪影合围 | `characters/ref_images/{白月清/赵焚天/方鼎元/韩夺心/司空玄}-{身份}-立绘.md` | ❌（光影不需要） |

**场景 / Scene**: 沧冥魔域黑金大殿前魔气长阶顶（参考 `scenes/沧冥魔域-黑金大殿长阶顶.md`），黑色星河悬天，冷月为光，氛围沉郁压顶。

**时长 / Duration**: 8s（hard 上限 15s）。Timed beats: 0-3s 雷柱劈下 / 3-6s 五光合围 / 6-8s 阶尘炸开。

**Reference uploads — pre-flight checklist**:
- [ ] 沧冥 turntable.mp4 → 上传到模型
- [ ] (可选) seam-frame PNGs: `shot01_startframe.png` + `shot01_lastframe.png` → 作 `input_image_urls` 给 image-to-video 模型路径

---

## 视频 prompt — 复制下方代码块到视频生成模型

> **用法**：复制下方代码块整段，粘贴到任何视频生成模型（Seedance / Kling / Sora / Veo / Runway Gen-3 等）。先按上方 "Reference uploads" checklist 上传该 shot 的 reference 视频；可选 seam-frame PNG 作 `input_image_urls`。

```text
{14-字段 prompt body — 角色 / 场景 / 镜头 / 动作（timed beats） / 台词 / 字幕 / 节奏 / 光线 / 色调 / 渲染样式 / 比例 / 时长 / 负向}
```

---

## Seam-frame still prompts — for stitching workflow (optional)

### Start-frame still — Seedream / Midjourney / Imagen（仅 ep 首镜出现该子段）

> **用法**：复制下方代码块整段，粘贴到 text-to-image 模型；输出 `shot01_startframe.png`。该 PNG 作为本 shot 的 `input_image_urls[0]` 起始帧（image-to-video 模型路径）。

```text
{startframe Seedream prompt — 主体定义 / 角色 / 场景 / 镜头 / 光线 / 色调 / 姿态（frozen instant） / 比例 / 负向 / 渲染样式}
```

### Last-frame still — Seedream / Midjourney / Imagen

> **用法**：复制下方代码块整段，粘贴到 text-to-image 模型；输出 `shot{NN}_lastframe.png`。该 PNG 作为下一 shot 的 `input_image_urls[0]` 起始帧（image-to-video 模型路径），保证 seam stitching。

```text
{lastframe Seedream prompt — 主体定义 / 角色 / 场景 / 镜头 / 光线 / 色调 / 姿态（frozen instant） / 比例 / 负向 / 渲染样式}
```
````

## (B) 多角色台词扩展（rule #12.4 v3）

`台词 / 字幕:` 字段现支持多角色 dialogue，格式：

```
台词 / 字幕:
  - {角色 A}: 内嵌硬字幕 "{台词原文}" — {字体调性}
  - {角色 B}: 后期软字幕 "{台词原文}" — {字体调性}
  - 旁白 / 字幕: 内嵌硬字幕 "{字幕}" — {字体调性}
```

或保留单行短格式（仅 1 个角色 / 默剧）：

```
台词 / 字幕: 内嵌硬字幕 "{台词}" — 方正粗黑 白底黑边
台词 / 字幕: 无台词 / 默剧
```

## (C) 15s 硬上限 + timed-beats 重排原则

每 shot ≤ 15s（rule #6 仍生效）。Subagent 在合并 / 重排时遵循:

- 现有 timed beats（per follow-up 003）保持不变 — 不重写动作内容。
- 「Shot context」段的 Duration line 显式列出 timed beats 摘要（例: "8s — 0-3s 雷柱 / 3-6s 合围 / 6-8s 炸开"），帮用户一眼看到节奏分配。
- 多角色 dialogue 时段建议 ≤ 4s 一句（中文 8-12 字平均 3-4s 念完）；如 dialogue 总时长 > 1/2 shot 时长，节奏标 `慢` 给唇形留时间。

## (D) Rule #12.6 — abstract to agent_refs

`.claude/agent_refs/project/ai_video.md` 新增 rule #12.6 「单一自包含 `shotNN.md` 文件 schema」，含：

- 三段结构（Shot context + 视频 prompt + Seam-frame still prompts）
- 「Shot context」段的 5 个必填子项（Summary / Characters / Scene / Duration / Reference uploads）
- 「视频 prompt」段沿用 rule #12.4 v2 schema（14 字段不变）
- 「Seam-frame still prompts」段把 rule #11 / rule #12.4 静帧 seam 列字段折叠成 inline code block（startframe 仅 ep 首镜；lastframe 每镜）
- 多角色 `台词 / 字幕` 扩展格式
- 15s 硬上限 + timed-beats 重排原则

Rule #5 (per follow-up 006) 进一步压缩：每 shot **一份** `shotNN.md` 文件（自包含 video + seam-frame still prompts；不再有独立 `_seedream.md` 文件）。

## (E) Spec FR-9 / FR-11 / FR-12 / NFR-4 amend

`specs/ai_video/mozun_chongsheng/final_specs/spec.md`:
- **FR-9** 改写：单 `shot{NN}.md` 文件含 Shot context + 视频 prompt + Seam-frame still prompts 三段。
- **FR-11**（lastframe Seedream prompt）标注「已并入 FR-9 第三段」。
- **FR-12**（startframe Seedream prompt）标注「已并入 FR-9 第三段（仅 ep 首镜）」。
- **NFR-4** 改写：每 shot **一份** `shotNN.md` 自包含文件（不再有 `_lastframe_seedream.md` / `_startframe_seedream.md` 独立文件）。

## 期望行为

1. ep01-ep05 每 ep 的 `prompts/` 文件夹只剩 10 个 `shotNN.md` 文件（每个文件自包含 shot context + 视频 prompt + seam-frame still prompts）。
2. 用户打开任一 `shotNN.md`：① 上方先看到 Shot context 段做 review；② 中段直接 copy-paste 视频 prompt 到 Seedance/Sora/Veo/Runway/Kling；③ 下段 copy-paste seam-frame Seedream prompt 到 Seedream/Midjourney（如需 image-to-video 路径或 stitching）。
3. 多角色台词的 shot 在 `台词 / 字幕:` 字段以 multi-line 方式列每个角色的台词（已有的单角色 shot 格式保持不变）。
4. follow-up 001 / 002 / 003 / 004 / 005 / 006 锁定全部保持有效（影视级真人写实 / 18-35 看似青春 / 中文文件命名 / model-agnostic 模板 / shot prompt 14 字段 / character ref 单 video prompt / character checklist + scenes 立档 + 合并 kling+seedance）。

## Out of scope

- 不重新生成 prompt body 内容（动作 timed beats / 台词 / 节奏 / 视觉描述等保持不变）。
- 不实际渲染视频或 PNG。
- 不为 ep06-ep60 预生成合并 shot files（stage-4 regen 范围）。
- 不修改 character ref / scenes / style_guide / world / arc_outline / README。
- 不重命名 character ref_images 路径。
- 不把 follow-up 002 遗留的「沧冥 三十出头 / 看似二十五」inline 不一致问题在本 follow-up 解决（独立 surgical follow-up）。
