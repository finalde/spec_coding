# Follow-up draft 010 — 2026-05-10

Summary: 三件事：(A) 在 ai_video_management webapp 渲染 markdown 时给所有 ```text``` (及其它语言) 代码块加 **一键复制按钮**（top-right corner），用户点击即可 copy prompt 到剪贴板；(B) **更好的视觉样式**——给代码块的 `{ref_xxx}` 占位符加 inline highlight pill (visual distinction)，让用户清楚看到要替换什么；CSS 微调 code block 视觉对比；(C) 给 50 个 shot.md 文件**加入完整人物台词**（expand 「无台词 / 默剧」shots → 含 character dialogue 多行 script 格式 where narratively appropriate；保留真正纯视觉镜头）。

## 用户原话

> use a better visual style to display all prompts plesae, and give me a copy button so I can one click copy the prompt. Another thing is, in episode shotNN.md, 请加入人物台词

## (A) Copy button — webapp 实现

修改 `projects/ai_video_management/frontend/src/markdown/renderer.tsx`：注入 custom `pre` component handler 给 ReactMarkdown；该 component 渲染时在 top-right 加 `<button class="copy-btn">复制 Copy</button>`；点击 → `navigator.clipboard.writeText(rawCodeContent)` → 短暂显示 "已复制 ✓" 反馈。

CSS in `projects/ai_video_management/frontend/src/styles.css`：定位按钮 absolute top-right；hover/active 样式；transition；切换状态 (`.copied`) 时变绿色显示打勾。

## (B) 占位符视觉 highlight

修改 `renderer.tsx`：新增 regex pre-render pass `applyRefPlaceholderPill`，匹配 `{ref_<chinese-name>}` pattern，wrap 在 `<span class="ref-placeholder">{ref_xxx}</span>` 内。该 span 用 CSS 高亮（蓝色 / 紫色背景 + monospace + small padding + border-radius）。

视觉效果：用户打开 `shotNN.md` 时，每个 `{ref_沧冥}` / `{ref_长阶顶}` 占位符都视觉特别醒目，告诉用户"这里要替换"。

## (C) 50 shot files 加入人物台词

对每个 shot file 的 `台词 / 字幕` 字段：

1. **真正纯视觉的 shot**（无人形 / 仅光影 / 镜头一闪等）保持 `无台词 / 默剧`。
2. **有出场角色但目前 默剧**的 shot：根据 shotlist 内容 + episode.md 剧情 + 角色 性格 / 标志台词，**补一条符合该 shot 情境的人物台词**。
3. **已有台词**的 shot：保留并按 multi-line script 格式扩展（如有多角色）。

例：
- ep01 shot02 「沧冥独立长阶之顶推镜，魔气溢指尖」（前为默剧）→ 加沧冥独白：
  ```
  台词 / 字幕:
    - {ref_沧冥} 沧冥: 后期软字幕 "今日，便是你们的死期。" — 方正粗黑 白底黑边
  ```
- ep01 shot03 「五宗主齐立合围沧冥」（前为默剧）→ 加白月清开口或方鼎元宣判：
  ```
  台词 / 字幕:
    - {ref_方鼎元} 方鼎元: 后期软字幕 "魔尊沧冥，今日便是你的劫数。" — 方正粗黑 白底黑边
    - {ref_沧冥} 沧冥: 后期软字幕 "本尊从不解释，只清算。" — 方正粗黑 白底黑边
  ```
- ep05 shot07 「魂魄入体顿挫」（前为默剧）→ 加旁白或沧冥意识独白：
  ```
  台词 / 字幕:
    - 旁白 / 标题: 后期软字幕 "魂火不灭，便是归期。" — 方正粗黑 白底黑边
  ```

人物台词内容**衍生自**：
- 角色 bible 的 `## 标志台词或口头禅` （首选；保持声线一致）
- shotlist 内容 + episode.md 剧情节奏（次选；shot-specific dialogue）

## (D) Rule #12.6 v3 amend — 视觉样式 + 人物台词

`.claude/agent_refs/project/ai_video.md` rule #12.6 v3 amend：

1. **15s 硬上限 + timed-beats 重排** 原则保留；新增「**人物台词强制原则**」—— 每 shot 「台词 / 字幕」字段除了「真正纯视觉镜头」（≤ 25% of all shots in any ep）外，**优先加入至少 1 句人物台词**（multi-line script 格式 if 多角色）；台词内容衍生自 bible 标志台词或 shotlist 剧情。
2. 新增「**Visual style 渲染契约**」—— webapp 渲染 markdown 时：
   - 所有 ```text``` / ```yaml``` / etc. fenced code blocks 必含一键 copy button（top-right corner）。
   - `{ref_xxx}` 占位符在 rendered view 中视觉 highlight（pill / inline tag styling），让 user 在 review 时清楚识别。

## (E) Spec FR-9 amend

`specs/ai_video/mozun_chongsheng/final_specs/spec.md` FR-9 段 ③ 视频 prompt 的 `台词 / 字幕` 字段描述补一句：「**人物台词强制原则** — 每 shot 优先加入 ≥ 1 句人物台词，仅纯视觉镜头允许 默剧。」

## 期望行为

1. 用户打开 ai_video_management webapp 看任一 markdown 文件 → 所有 ```text``` 代码块右上角有 "复制 Copy" 按钮 → 点击 → 整段 prompt 进剪贴板，按钮短暂变绿显示 "已复制 ✓".
2. `{ref_沧冥}` / `{ref_长阶顶}` 等占位符在渲染中视觉 highlight，user 一眼看到要替换的位置。
3. 50 shot files 每个都尽量含人物台词（除真正纯视觉镜头），台词与 character bible 的标志台词 / 性格保持一致。
4. follow-up 001-009 锁定保持有效。

## Out of scope

- 不修改 spec_driven webapp（虽结构同 ai_video_management，本 follow-up 仅 target ai_video_management）。
- 不实际渲染视频。
- 不修改 ep06-ep60 stage-4 regen 范围。
- 不重命名文件 / 文件夹。
- 不修改 character file / scene file / style_guide / world / arc_outline / README。
- 不解决 follow-up 002 遗留的「沧冥 三十出头 / 看似二十五」inline 不一致问题。
