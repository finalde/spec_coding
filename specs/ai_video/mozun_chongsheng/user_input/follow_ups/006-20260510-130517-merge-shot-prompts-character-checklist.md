# Follow-up draft 006 — 2026-05-10

Summary: 在 episode 内**合并** `shotNN_kling.md` 与 `shotNN_seedance.md` 为单文件 `shotNN.md`（per shot 仅一个 prompt，不再分模型 variant）；每个 shot 文件**顶部列出 出场角色 checklist**（含每个角色的 turntable reference 路径，让用户知道运行 prompt 前要上传哪些 reference 视频）；prompt body 封装在 markdown code fence 内**直接 copy-paste**到任何视频生成模型。Static seam-frame prompts (`shotNN_lastframe_seedream.md` / `shot01_startframe_seedream.md`) 保持独立（用途不同——seam stitching）。

## 用户原话

> under episode, merge kling and seedance file, sure there is only one set of prompts, and on each shot, first give me a list of charators so I know what reference I need to attach, also give me the prompt in a ready to copy paste format

## 工作流变更

**Before（follow-up 003）**：

```
ep{NN}/prompts/
├── shot01_kling.md       # Kling variant: [参考图] line + 一句话锁定
├── shot01_seedance.md    # Seedance variant: 无 [参考图] + 一句话锁定 + 体型/服装/道具 inline 展开
├── shot01_lastframe_seedream.md
├── shot01_startframe_seedream.md  # 仅 ep 首镜
├── shot02_kling.md
├── shot02_seedance.md
├── shot02_lastframe_seedream.md
... ×10 shots
```

每 shot 2 个 video prompt 文件（kling + seedance）+ 1-2 个 seam-frame 文件 = 31 文件 / ep。

**After（follow-up 006）**：

```
ep{NN}/prompts/
├── shot01.md             # 合并：出场角色 checklist + 单 prompt code block
├── shot01_lastframe_seedream.md
├── shot01_startframe_seedream.md
├── shot02.md
├── shot02_lastframe_seedream.md
... ×10 shots
```

每 shot 1 个 video prompt 文件（合并的 `shotNN.md`）+ 1-2 个 seam-frame 文件 = 21 文件 / ep。

每 ep 减少 10 文件；ep01-ep05 共减少 50 文件。

## (A) 新文件 schema — `shotNN.md`

```markdown
# ep{NN} / shot{NN} · {1-line shot summary from shotlist.md}

## 出场角色 — 上传以下 turntable reference 视频到模型

| 角色 | turntable reference | 备注 |
|---|---|---|
| 沧冥 | `characters/ref_images/沧冥-魔尊本相-立绘.md` → 渲染为 mp4 上传 | 主体角色，正脸/全身可见 |
| 五大宗主（光影） | 仅光影剪影出现，**无须 turntable reference**（角色未具名露脸） | 背景 |

## 复用场景

参考: `scenes/沧冥魔域-黑金大殿长阶顶.md`（场景档已 lock-down，shot prompt `场景:` 行 byte-identical 引用）

## seam-frame 输入（可选，仅 image-to-video 模型路径）

input_image_urls = [`shot01_startframe.png`, `shot01_lastframe.png`]

（shotN ≥ 2 用 [`shot{N-1}_lastframe.png`, `shot{N}_lastframe.png`]）

---

## 视频 prompt — 复制下方代码块到视频生成模型

> **用法**：复制下方代码块整段，粘贴到任何视频生成模型（Seedance / Kling / Sora / Veo / Runway Gen-3 等）。
> 1. 先按"出场角色"表上传该 shot 的 reference 视频（用于支持 video reference 的模型）。
> 2. 可选：image-to-video 模型上传 seam-frame PNG 作 `input_image_urls`。
> 3. 粘贴下方 prompt → 生成。

```text
角色: {一句话锁定 byte-identical} + {体型 / 发型 / 服装 / 道具 inline 展开 — 用 Seedance variant 的扩展版}

场景: {scenes/{name}.md 一句话锁定 或 inline 描述}

镜头: {景别 + 运动}

动作: {timed beats}

台词 / 字幕: {内嵌硬字幕 | 后期软字幕 | 无台词 / 默剧}

光线 / 色调: ...; 渲染样式: 影视级真人写实 + cinematic + 4K HDR

节奏: {慢 / 中 / 快 / 顿挫}

比例: 9:16

时长: ≤15s

负向: ... + 14 项 stylization 负向（per follow-up 001）
```
```

**关键设计：**

- `角色:` 行用 Seedance variant 的扩展版（一句话锁定 + 体型 / 发型 / 服装 / 道具 inline 展开）—— 这样无 video reference 时仍 self-contained；有 turntable 时模型仍以 reference 为主。
- 不再有 `[参考图]` 行 inline 在 prompt body 内——将 seam-frame `input_image_urls` 单独列在 prompt body 之上的「seam-frame 输入」段（只有 image-to-video 模型需要这个 API 参数）。
- 出场角色 checklist 的 reference 备注列明确指出哪些角色需要上传 turntable（正脸 / 主体），哪些不需要（光影 / 远景 / 不具名）。

## (B) 出场角色 checklist 派生规则

每个 shot 的角色列表来自 `shotlist.md` 的 角色 列。Subagent 应据 shotlist + episode.md 的描述判断每个角色的可见度：

| 角色出场方式 | turntable 是否必需 | 备注示例 |
|---|---|---|
| 正脸 / 主体角色 / 中近景 / 特写 | ✅ 必需 | 「主体角色，正脸可见」 |
| 全景配角 / 跟随主角 | ✅ 推荐 | 「配角，全景出场」 |
| 光影剪影 / 背影 / 远景 / 不具名 | ❌ 无须 | 「仅光影剪影出现」 |
| 物件 / 法宝（角色专属道具）| ❌ 无须 | 「仅道具出现，无人形」 |

## (C) 删除清单

每 ep 删除 20 个旧文件：
- `shotNN_kling.md` × 10
- `shotNN_seedance.md` × 10

保留：
- `shotNN_lastframe_seedream.md` × 10（每镜 seam-frame 末帧）
- `shot01_startframe_seedream.md` × 1（仅 ep 首镜首帧）

ep01-ep05 共删除 100 个旧 video shot prompts，新建 50 个合并 prompts。

## (D) Rule #5 amend — Dual-prompt requirement → Single-prompt requirement

`.claude/agent_refs/project/ai_video.md` rule #5 改为：

> **每个 shot 一份 `shotNN.md` 视频 prompt 文件**（合并 model variants）+ 一份 `shotNN_lastframe_seedream.md` 静帧 seam-frame prompt（per shot）+ 一份 `shot01_startframe_seedream.md`（仅 ep 首镜）。视频 prompt 文件不再按目标 model 分割；用户在文件 metadata（出场角色 checklist + seam-frame 输入）中获取所需的 reference / API 参数。

## (E) Rule #12.4 amend — 文件命名

文件命名约定从 `shotNN_{model}.md` 改为 `shotNN.md`（单一）。Variant 概念退场——同一 prompt body 适配所有视频模型，差异由 reference 上传方式（turntable.mp4 / image_urls / 纯文字）承担，不需要在文件级 fork。

## (F) Spec amend — FR-9 / FR-10 / NFR-4

`specs/ai_video/mozun_chongsheng/final_specs/spec.md` 改：
- **FR-9 + FR-10 合并为 FR-9**：单个 `shot{NN}.md` per 镜，含出场角色 checklist + seam-frame 输入 + 复制代码块的视频 prompt。FR-10 标注「已并入 FR-9」。
- **NFR-4** 双管线 + seam-frame 的"双管线"要求 → 单 prompt + seam-frame：每镜必含 `shot{NN}.md` + `shot{NN}_lastframe_seedream.md`；每集首镜必含 `shot{NN}_startframe_seedream.md`。

## 期望行为

1. ep01-ep05 每集 prompt 文件夹从 31 个减少到 21 个。
2. 用户打开任何 `shotNN.md` 看到顶部的角色 checklist，知道要上传哪些 turntable.mp4。
3. 用户复制下方代码块到 Seedance / Kling / Sora / Veo / Runway 任一模型 → 生成视频。
4. follow-up 003 锁定的 14 字段 schema 全部保留在合并 prompt body 内（角色 / 场景 / 镜头 / 动作 / 台词 / 节奏 / 光线 / 渲染 / 比例 / 时长 / 负向）；follow-up 001 / 002 / 005 锁定保持有效。
5. seam-frame still prompts 不动（用途不同：视频生成 vs seam stitching）。

## Out of scope

- 不重新生成 prompt body 内容（动作 timed beats / 台词 / 节奏 等保持 follow-up 003 决定的值不变）。
- 不实际渲染视频或 turntable 视频。
- 不重命名 character ref_images 路径。
- 不为 ep06-ep60 预生成合并 prompts（stage-4 regen 范围）。
- 不修改 scenes/ 文件。
- 不修改 character bible 或 character ref_images 文件。
