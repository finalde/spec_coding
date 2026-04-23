---
name: video_generation__series-factory
description: Composite orchestrator for the 8-stage 短剧 pipeline on a single `series/{name}/`. Chains reference-scout → preproduction → serial-novelist → storyboard-master → seedance-packager → continuity-director → [human Seedance + TTS] → clip-stitcher. Reads / writes `status.md`, enforces the rolling 3–5 episode cap, never skips the fail-closed continuity gate. Use for "write + pack + verify" in one call, or to resume at any stage.
---

# 系列工厂 · Series Factory — 8 段流水线总控

本 skill 不做新内容；它按依赖顺序调度其它 7 个 skill + 1 个 agent，并在人工介入点（Seedance 生成、TTS 渲染）处暂停。所有进度以 `series/{name}/status.md` 为准。

## 流水线拓扑

```
reference-scout ──► preproduction ──► serial-novelist (rolling 3–5 ep)
                                                │
                                                ▼
                                       storyboard-master
                                                │
                                                ▼
                                        seedance-packager
                                                │
                                                ▼
                                      continuity-director（闸门）
                                                │
                                         PASS ◄─┴─► FAIL → 回 packager / preproduction
                                                │
                                                ▼
                          [人工] Seedance 跑 clip + snapshot 图
                                                │
                                                ▼
                          [人工] TTS（Volcengine / MiniMax / iFlytek）渲染 VO + BGM 选曲
                                                │
                                                ▼
                                          clip-stitcher
                                                │
                                                ▼
                                 四平台导出 + CapCut 备份包
```

## Modes

- **full-series**：从 `reference-scout` 起一路推进；每次推进 3–5 集（Q7c 滚动上限），推完停下来等人工。
- **from-stage {stage}**：从指定 stage 续跑。合法 stage：`reference-scout` / `preproduction` / `novelist` / `storyboard` / `packager` / `continuity` / `stitcher`。
- **single-episode {NNN}**：对已到 `storyboarded`（或更前）状态的某一集推到 `stitched`；不触发新集写作。
- **refresh-bibles**：重跑 `preproduction` 的 incremental 模式并对所有已 `packaged` 集重跑 `continuity-director`；不重写剧本，不重拼视频。

## Workflow

### Step 0 — 读 `status.md`，决定入口

`series/{name}/status.md` 是合同。必需字段：

```yaml
series_name: string
research: string | null           # reference_pack 版本
bibles: LOCKED | UNLOCKED
planned_episodes: [ep_nnn, ...]   # rolling cap ≤5 未拼集
ep_001: drafted | storyboarded | packaged | continuity_passed | continuity_failed | stitched
ep_002: …
last_packaged_at: ISO date
last_stitched_at: ISO date
```

入口决策：
- `research` 为空 → 跑 `reference-scout`。
- `bibles != LOCKED` → 跑 `preproduction` (bootstrap)。
- `planned_episodes` 长度 <3 且系列总计划 >当前写完集 → 触发 `serial-novelist` rolling，写 3–5 集。
- 有集状态 = `drafted` → 调 `storyboard-master`。
- 有集状态 = `storyboarded` → 调 `seedance-packager`。
- 有集状态 = `packaged` → 调 `continuity-director`。
- 有集状态 = `continuity_passed` → 暂停，提示人工去 Seedance/TTS，然后再跑 `stitcher`。
- 有集状态 = `continuity_failed` → 停机并把 `continuity_report.md` 的 FAIL 列表摘要回显给用户，等用户决定回 packager 还是 preproduction。

### Step 1 — 跑侦察 (若未做)

调 `video_generation__reference-scout`，模式 = `trend-sweep + gap`。产物 = `series/{name}/research/reference_pack.md`；把 `status.md.research = reference_pack: v1 · {date}`。

### Step 2 — 锁圣经 (若未锁)

调 `video_generation__preproduction`，模式 = `bootstrap`。产物 = 四本圣经 + `anchor_registry.md`；`status.md.bibles = LOCKED`。

### Step 3 — 滚动写集（每次 3–5 集，严禁前置 outline 超 5 集）

对 `planned_episodes` 长度 <3 的缺口：调 `video_generation__serial-novelist`，模式 = `rolling`，批量 3–5 集。每集产物 = `series/{name}/episodes/ep_{NNN:03d}.md`；对应 `status.md.ep_{NNN} = drafted`。

规矩：
- 绝不一次 outline >5 集（Q7c）。
- 若计划到 ep 10/30/60 边界 → 插入 paid-cutpoint hard hook。

### Step 4 — 分镜展开

对所有 `drafted` 的集，逐集调 `video_generation__storyboard-master`。产物 = `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`；`status.md.ep_{NNN} = storyboarded`。

### Step 5 — Seedance prompt 打包

对所有 `storyboarded` 的集，逐集调 `video_generation__seedance-packager`。产物 = 每段两份 `.txt` + `generation_manifest.md`；`status.md.ep_{NNN} = packaged`。

### Step 6 — 连续性闸门（fail-closed）

对所有 `packaged` 的集，逐集调 `video_generation__continuity-director`（agent）。
- PASS → `status.md.ep_{NNN} = continuity_passed`。
- FAIL → `status.md.ep_{NNN} = continuity_failed`；把 `continuity_report.md` 里的 FAIL 分布摘要回显。**绝不**自动重跑 packager；等用户指令。

### Step 7 — 人工介入点（Seedance 生成 + TTS 渲染 + BGM 选曲）

本 skill 在此暂停，输出一张清单：

```markdown
## 第 {EP} 集 人工执行清单

### 1. Seedance 生成（按 generation_manifest.md 运行顺序）
- [ ] `prompts/ep_{NNN}/clip_01_video_prompt.txt` → Seedance 2.0，挂载三视图 + 背景参考图
- [ ] `prompts/ep_{NNN}/clip_01_snapshot_prompt.txt` → Seedance，出 1 张图
- [ ] clip_02 video；clip_02 snapshot
- …
- 全部视频落到 `series/{name}/clips/ep_{NNN}/clip_{i}.mp4`
- 全部快照落到 `series/{name}/snapshots/ep_{NNN}/clip_{i}_to_{i+1}.png`

### 2. TTS 渲染
- 角色与 voice_id 清单（从 `voice_bible.md`）：
  - 角色A ↔ {engine + voice_id + pitch + emotion}
  - 角色B ↔ …
  - 旁白 ↔ …
- 按 `storyboard.md` 的 `对白` / `旁白` 字段逐条渲染
- 落到 `series/{name}/audio/ep_{NNN}/vo_{i}.wav`
- 写 `vo_manifest.json`（每条 start 毫秒取自 storyboard 段边界）

### 3. BGM + SFX
- 按 `reference_pack.md` 的「BGM 情绪走向」挑一轨；裁到 ≥本集时长 +5 s
- 落到 `series/{name}/audio/ep_{NNN}/bgm.mp3`
- SFX 文件名用 `sfx/{nn}_{name}_@mm-ss-ms.wav` 编码 cue 时间
```

### Step 8 — 拼片（闸门已 PASS + 人工素材齐 → 自动续跑）

当 `status.md.ep_{NNN} == continuity_passed` 且 clips/ audio/ 目录就绪：调 `video_generation__clip-stitcher`。产物 = 主片 + 四平台版 + CapCut 包；`status.md.ep_{NNN} = stitched`。

### Step 9 — 回显进度

每次调用结束回显一张表：

```
| 集 | 状态 | 上次更新 |
|ep_001| stitched | 2026-04-22 |
|ep_002| continuity_passed | 2026-04-22 |
|ep_003| packaged | 2026-04-22 |
|ep_004| drafted | 2026-04-22 |
|ep_005| 待写 | — |
```

并指出下一步：
- 有 FAIL → 把 FAIL 集 + 错误码回显
- 有 continuity_passed 但素材未齐 → 列人工清单
- 否则 → 问用户是否继续滚动写下一批 3–5 集

## Inputs

- `series/{name}/status.md`（权威进度）
- 调用模式 + 可选起始 stage / 集号
- 用户对差异化角度 / 语气 / 年龄段 / 平台的初始设定（只在 `reference-scout` 阶段用）

## Outputs

- 本 skill 只协调，不直接写业务文件；唯一新写的是：
  - `series/{name}/status.md`（增量更新）
  - `series/{name}/factory_run_log.md`（追加：每次调用开始时间、走到哪、触发了哪些子 skill/agent、人工清单若有）

## 输出规范

- **全部中文**（除脚本类产物由各子 skill 控制）。
- **绝不跳过**连续性闸门；`continuity_failed` 强制停机。
- **绝不 outline 超 5 集**（Q7c 滚动上限）。
- **绝不并行**跑两个同集的子步骤（同集内步骤必须串行）。
- **允许并行** 跨集的同阶段（例如同时对 ep_003 ep_004 ep_005 跑 packager）。
- 每次 status 变更同时追加一行到 `factory_run_log.md`。

## 边界情况

- 用户首次调用，`series/{name}/` 不存在 → 询问 `series_name` 并创建骨架目录后再进入 Step 0。
- 用户要求直接进入某 stage 但前置未满足 → 回显前置缺口，不越权自动补前置（比如用户说「直接跑 packager」但 `bibles != LOCKED` → 停机并报缺）。
- 某集反复 `continuity_failed` ≥2 次且错误码集中在 `VERBATIM-DIFF` → 把问题升级，建议用户重跑 `preproduction` incremental 模式而不是一直重打包。
- `paid_cutpoint` 集（ep 10/30/60）若 Hook 模板非 H/J → 警告但不中止，由用户最终决定。
- 一次调用跑到超过 3 集时，在每集之间 flush `status.md`，防止中断丢进度。
- `refresh-bibles` 模式只允许在 `bibles == LOCKED` 且有 ≥1 集 `packaged` 时启动；否则回到 `bootstrap`。

## Invocation examples

- 「跑 `series/战神归来/` 到 ep_005 的连续性闸门。」
- 「`series/剑尊重生/` 圣经刚改，把已打包的 5 集全部 refresh 一下连续性。」
- 「对 `series/战神归来/ep_003` 单集推到 stitched。」
- 「从 storyboard 这一步继续 `series/剑尊重生/`。」
