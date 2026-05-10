# Follow-up draft 005 — 2026-05-10

Summary: Seedance 等视频模型已支持上传 video 作为 reference，所以 character 参考素材文件**只需要一段文字生成视频 reference 的 prompt** 即可——视频本身（12s 360° 转身 + 5 句中文台词）就是后续 shot 视频的 reference 输入。**去掉** follow-up 004 加的 ①号「文字生图片」prompt 块，专注单个 ②号「文字生视频 reference」prompt + 5 句台词配音对照表。

## 用户原话

> seedance是可以上传video作为reference的，所以只需要一段文字生成视频的prompt就好了，你可以把剩余的文字生成图片的prompt去掉，专注于生成文字到video reference的prompt

## 工作流变更

**Before（follow-up 004）**：

```
文字 → ①号 image prompt → Seedream/Midjourney → 角色立绘 PNG
                                                      ↓
PNG + ②号 video prompt → Kling image-to-video → 12s turntable 视频
                                                      ↓
turntable 视频 → 后续 shot 的 video reference（v2 audio-aware path）
```

**After（follow-up 005）**：

```
文字 → 视频 reference prompt → Seedance / Sora / Veo / Runway Gen-3 → 12s turntable 视频
                                                                              ↓
                                                            turntable 视频本身作为 reference
                                                                              ↓
                                                  后续 shot prompt 上传该视频作为 video reference
                                                                              ↓
                                                  shot 视频自动锁定形象 + 声线 + 节奏
```

PNG 立绘步骤被 collapsed —— 视频生成模型直接从文字 prompt 一步出 turntable，turntable 本身闭环作为后续所有 shot 的 reference。Kling image-to-video 路径仍可走（从 turntable 抽帧作为 PNG 输入），但不再是 mandatory 中间步骤。

## (A) Rule #12.5 amend — 单 prompt 文件 schema

`.claude/agent_refs/project/ai_video.md` rule #12.5 改写：

| 旧（v1 follow-up 004） | 新（v2 follow-up 005） |
|---|---|
| 双 prompt 文件：①号 文字生图片 + ②号 文字生视频 reference | 单 prompt 文件：仅文字生视频 reference |
| 5 句台词配音对照表（保留） | 5 句台词配音对照表（保留） |
| Rule #12.5 supersedes rule #12.2 在文件级别（rule #12.2 内容仍生效在 ①号 prompt 内容级别）| Rule #12.5 supersedes rule #12.2 完全（rule #12.2 不再生效；如需 PNG 立绘可从 turntable 视频抽帧获得，无需独立 prompt）|
| 用法 callout 区分 image-to-video 与 text-to-video 模型的 input 差异 | 用法 callout 简化：所有支持 video reference 的视频模型直接 paste 单 prompt 即可 |

新 schema：

```markdown
# {中文名} · {身份} — 视频 reference prompt

参考: characters/{中文名}-{身份}.md
画幅: 9:16 竖屏 / 4K 原生分辨率

> **文件说明**：本文件含一段可直接 copy-paste 的视频 reference prompt + 一张 5 句标准台词配音对照表。文件名沿用 `-立绘.md` 作为 legacy alias（per rule #12.5 v2）。

---

## 文字生视频 reference prompt — Seedance / Sora / Veo / Runway Gen-3 / Kling

> **用法**：复制下方代码块整段，粘贴到支持 video reference 的 AI 视频模型（Seedance / Sora / Veo 3 / Runway Gen-3 / Kling 等）。**该样片本身**作为后续真正 shot 视频的 video reference 输入，锁定形象 + 声线 + 节奏。

```text
{turntable + 5 句标准台词的 prompt body，与 follow-up 004 ②号 prompt 完全一致}
```

### 5 句标准台词（中文，配音演员对照表）

{表格不变}
```

## (B) 10 个 mozun 角色文件升级

10 个 `characters/ref_images/{中文名}-{身份}-立绘.md` 文件按上述新 schema 重写：

1. 删除 `> **文件说明**：本文件含两段可直接 copy-paste 的 prompt + 一张 5 句标准台词配音对照表。文件名沿用 \`-立绘.md\` 作为 legacy alias...` 的旧 callout 文本（"两段" → "一段"，"图片 + 视频双 prompt" → "视频 reference prompt"）。
2. **删除整个 ①号 文字生图片 prompt 块**（从 `---\n\n## 1️⃣ 文字生图片 prompt — Seedream...` 直至 ②号 上一个 `---`，含中间所有 image prompt 内容）。
3. **重命名 ②号 H2** 从 `## 2️⃣ 文字生视频 reference prompt — Kling / Sora / Veo / Seedance（360° 转身样片 + 标准台词）` → `## 文字生视频 reference prompt — Seedance / Kling / Sora / Veo / Runway Gen-3（360° 转身样片 + 标准台词）`（去掉 `2️⃣` 编号；模型列表把 Seedance 提前并列出 Runway Gen-3）。
4. **重写 ②号 用法 callout**：删去 "image-to-video 模型 — 输入 ①号生成的 PNG..." 旧文本；新文本统一为「复制下方代码块整段，粘贴到支持 video reference 的 AI 视频模型...该样片本身作为后续真正 shot 视频的 video reference 输入，锁定形象 + 声线 + 节奏」。
5. ②号 prompt 代码块本身**保持 byte-identical**——Turntable 锁定字段（场景 / 镜头 / 光线 / 节奏 / 渲染样式 / 比例 / 时长 / 视频专属负向）+ 角色 inline 展开 + 5 句台词全部不变。
6. 5 句台词配音对照表 + 配音参考 footer + trailing italic origin note 保持不变（origin note 加 follow-up 005 引用）。

## (C) Spec FR-26 amend

`specs/ai_video/mozun_chongsheng/final_specs/spec.md` FR-26 删去 ①号 image prompt 字段描述；只保留 ②号 video reference prompt 字段描述 + filename legacy alias 接受 + 5 句台词对照表说明。

## 期望行为

1. 10 个角色文件变成「单 prompt + 配音表」结构，**整段视频 prompt 一次 copy-paste 即可**生成 turntable 视频。
2. 用户在 Seedance / Sora / Veo / Runway Gen-3 上跑：text-to-video 输出 12s turntable 视频；该视频被作为后续 shot prompt 的 reference 上传，**形象 + 声线 + 节奏**自动锁定。
3. 现有 follow-up 001 / 002 / 003 / 004 锁定保持有效（影视级真人写实 / 18-35 看似青春 / 中文文件命名 / model-agnostic 模板 / shot prompt 字段补齐 / 5 句台词与配音对照表）。
4. PNG 立绘工作流不再是 first-class（如需 PNG 可从 turntable 抽帧；prompt 文件不再生成 image prompt）。

## Out of scope

- 不重新生成 shot prompts。
- 不实际渲染视频。
- 不引入英文 variant；继续中文工作流。
- 不删除既有 PNG 立绘 asset（如有）—— prompt 文件不再生成 image prompt，但用户已渲染的 PNG 可继续使用作为 image-to-video 模型 input（Kling 等）。
- 不重命名文件路径——`characters/ref_images/{role}-立绘.md` 沿用 legacy alias 避免大规模 spec.md / shot prompt 引用 update。
