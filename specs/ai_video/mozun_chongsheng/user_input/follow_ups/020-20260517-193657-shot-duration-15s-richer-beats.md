# Follow-up draft 020 — 2026-05-17

User asks that every shot be **15 s** (was 10 s under the prior 12.4-B `时长: Always 10s` rule), 用 extra 5 s 给 镜头 / 运镜 / 动作 / 台词 更多细节。

## 用户原话

> change all the shots to be in 15s length, this should give you more room for more details for each shot, both 台词，运镜and 动作

## 决策（user-confirmed via 多选）

| 项 | 用户选 |
|---|---|
| 15 s rule scope | **Both** — global rule (CLAUDE.md + `agent_refs/project/ai_video.md`) + 本项目 retrofit |
| 台词 处理 | **Add 台词 as a first-class shot field** — narrow the "Visuals only in v1" carve-out so dialogue text is allowed (audio synthesis still out of scope) |

## 根因（why this is now a change, not just "do as before"）

Pre-020 rule 12.4-B contained an internal contradiction:
- Line 448: `时长: | **Always 10s.**` (Kling-cap-driven)
- Line 459: `set 时长: 15s` (Scope footer)

Existing shot mds under `ai_videos/mozun_chongsheng/episodes/ep01..ep05/prompts/shot{01..10}/shot{NN}.md` all carry `时长: 10s` plus `Duration: 10 seconds — schema 12.4-B 默认（Kling 10s 单次生成上限）` in their Shot-context block. The 12.4-B Scope footer's `15s` aspiration never propagated to the rule's own `时长` row, nor to any shot md.

This follow-up resolves the contradiction by making **15 s the single canonical target** across the rule, the schema row, and every shot md — and uses the extra 5 s to enrich 镜头 cuts / 运镜 transitions / 动作 beats / 台词 lines per the user's intent.

## 改动范围

### 全局（CLAUDE.md + agent_refs — 已在本 follow-up 同 turn 落地）

1. `CLAUDE.md § AI video rules` bullet 1：
   - `Every shot ≤ 15 s` → `Every shot is 15 s (default and target — was "≤ 15 s" before; bumped to fill Seedance's single-generation budget and give 镜头/运镜/动作/台词 more room)`。
   - 新加一行：dialogue (`台词`) is a first-class shot field rendered as on-frame subtitles; "Visuals only in v1" 收窄到 **audio synthesis only**（no TTS / no music），不含 dialogue text。

2. `.claude/agent_refs/project/ai_video.md`：
   - 规则 #6 标题 `15-second atomicity` → `15-second atomicity (target, not ceiling)`；body 重写为 `Every shot is 15 s (default and target)`；新加 Kling-cap-split 说明（10 s + 5 s back-to-back，用 `shotNN_lastframe.png` 在 10 s 处做 mid-seam）。
   - 规则 12.4 schema 表第 13 行 `时长:` (≤15s) → `时长:` (= 15s default per rule #6)。
   - 规则 12.4-B `时长` 行 `Always 10s` → `Always 15s`，连同 Kling-cap-split 一句。
   - 规则 12.4-B `Scope` footer 的 `set 时长: 15s` 维持（现在指向新规则 #6）。
   - rule #4 模板示例 `动作: {0–15s 内可完成}` → `{0–15s 内 timed beats}`；`时长: ≤15s` → `时长: 15s`。

### 项目（本 follow-up 同 turn 落地）

3. `specs/ai_video/mozun_chongsheng/final_specs/spec.md` 顶部追加 follow-up 020 amendment block：「每 shot 现 15 s；动作/台词 beats 从 5 拍扩到 5–7 拍；新 10–15 s 段必带新的 镜头 + 运镜 + 动作 beat，台词不强行加（默剧段可保留），但每 shot 至少 1 行台词除非剧本本身 silent」。
4. `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` 顶部 `Last regenerated` 段记 020 + scope + 「Duration / 时长 全部 10s → 15s；动作 beats 延展至 0–15s；台词 行 ≥ 1（除非 silent shot）」。
5. `specs/ai_video/mozun_chongsheng/changelog.md` append 020 entry。

### 项目代码 / shot mds（本 follow-up 同 turn 落地，5 个 episode 并行）

6. 重写 `ai_videos/mozun_chongsheng/episodes/ep{01..05}/prompts/shot{01..10}/shot{NN}.md`（50 个文件）：
   - **Shot context** 块 `Duration: 10 seconds — schema 12.4-B 默认（Kling 10s 单次生成上限）` → `Duration: 15 seconds — per agent_refs/project/ai_video.md rule #6 (15s default; Kling render splits at 10s via shotNN_lastframe seam)`。
   - **Shot context** 中 `Timed beats:` 重写为 5–7 拍覆盖 0–15s（每拍 2–3 s）。
   - 视频 prompt fenced block：
     - `镜头:` 行从 5 个 time window 扩到 5–7 个（多 1–2 个 cut 在 10–15 s 段）。
     - `运镜:` 行同步扩 5–7 个 transition。
     - `动作:` block 每拍重写覆盖 0–15s；10–15 s 新拍要 advance plot / reveal / reaction（不能是站立 idle）。
     - `台词 / 字幕:` block 至少保留 1 行 dialogue（已有 dialogue 的 shot 在 10–15 s 段加 1 行 reaction-or-reveal 台词，OR 把已有 dialogue 拉长 + 加 反应 行；silent shots 保留 `无台词 / 默剧` 但必须 explicit 注释）。
     - `时长: 10s` → `时长: 15s`。
   - **不动**：Reference placeholders 表 / `场景:` line / `光线/色调:` / `节奏:` / `渲染样式:` / `比例:` / `负向:` / Seam-frame still prompts 段。
   - **2000-字 soft cap** 保留（每 shot prompt body ≤ 2000 字）；如延展后超 2000 字优先 trim 反应 行非动作 line。

7. 重写 `ai_videos/mozun_chongsheng/episodes/ep{01..05}/shotlist.md`（5 个文件）：
   - 每行 `shot{NN} ... 10s ...` → `... 15s ...`（如有 time-window 列）。
   - episode 总时长（如有）从 100 s → 150 s。

## 不在本 follow-up 范围

- `style_guide.md` / `world.md` / character bibles / scenes / arc_outline.md / publish.md — 不动（时长扩展不改 style / character / scene 锁定描述符）。
- 已生成的 mp4 / png 输出（如果有）— 本 follow-up 不动 binary 输出；shot mds 改动后未来 stage-6 regen 才会重新跑 Kling/Seedance。
- Seam-frame `shotNN_lastframe_seedream.md` 内容 — 主体定义 + 姿态 frozen instant 仍然定锚 shot 的最后一拍；新最后一拍 (12–15s) 描述与现有 lastframe seam 描述保持一致是 shot-author 自检项；本 follow-up 不强制每 shot 重写 lastframe seam。
- 跨 shot 的 narrative 重排（如 ep01 整体由 10 shot × 10 s = 100 s → 10 shot × 15 s = 150 s，多出的 50 s 可能让某些 shot 显得 padded）— v1 接受，作为 trade-off 换取更细的 beat 描述。
- Audio synthesis / TTS / music — 仍然 v1 out of scope。
- `task_type=development` 项目 — 不受影响。

## Acceptance trigger

- 全 50 个 `shot{NN}.md` 文件 `时长: 15s` 且 Shot context `Duration: 15 seconds`。
- 全 50 个 shot 的 `动作:` block beats 覆盖到 0–15s（最后一拍 end-time = 15）。
- 全 50 个 shot 的 `镜头:` 行 ≥ 5 个 time window，至少 1 个 window 落在 10–15s 段。
- 全 50 个 shot 的 `运镜:` 行 entry 数与 `镜头:` window 数一致。
- 全 50 个 shot 的 `台词 / 字幕:` block 至少 1 行 dialogue OR 显式 `无台词 / 默剧` 注释。
- 全 50 个 shot prompt body 字数 ≤ 2000（hard cap 2500）。
- 全 5 个 `shotlist.md` 时长列由 10s → 15s（如该项目 shotlist 有时长列）。
- `CLAUDE.md` § AI video rules 第 1 行包含 `15 s` 且不含 `≤ 15 s` 老表述。
- `agent_refs/project/ai_video.md` 规则 #6 + 12.4 schema 表 + 12.4-B `时长` 行三处一致表述 15 s。
