# 中文短剧 AI-Video Agent 产线 · 使用手册

**交付日期:** 2026-04-22
**目标:** 用 Claude Code 把一个 50–80 集、每集 1.5–2 分钟的中文爽文短剧，从「题材侦察」一路推到「四平台分发版 mp4」。
**渲染器:** Seedance 2.0（默认）；Kling 延后到 v2。
**语种:** 全部中文；字幕硬烧 Noto Sans SC。
**平台:** 抖音 / 快手 / TikTok / YouTube Shorts（YT 切两段 ≤60 s）。

---

## 你拿到了什么

### 8 个新/改组件

| # | 组件 | 类型 | 职责 |
|---|---|---|---|
| 1 | `video_generation__reference-scout` | skill | 题材趋势 + 差异化侦察，产出 `reference_pack.md` |
| 2 | `video_generation__preproduction` | skill | 锁 4 本圣经（人物 / 场景 / 风格 / 声线）+ 锚点注册表 |
| 3 | `video_generation__serial-novelist` | skill | 写一集 900–1200 字 + 4 栏 beat sheet；滚动 3–5 集不超前 |
| 4 | `video_generation__storyboard-master` | skill | 4 栏展开 + 段与段之间 15 s 快照存根 |
| 5 | `video_generation__seedance-packager` | skill | 逐段 Seedance prompt + 快照 prompt + 生成清单 |
| 6 | `video_generation__continuity-director` | **agent** | 失败即阻断的连续性闸门（字符级 verbatim 核对） |
| 7 | `video_generation__clip-stitcher` | skill | ffmpeg 拼片 + 硬烧字幕 + 四平台导出 + CapCut 备份包 |
| 8 | `video_generation__series-factory` | skill | 1–6 + 8 端到端编排（stage 7 停下来等你跑 Seedance/TTS） |

### 约定位置

- 每个系列独立一个目录：`series/{series_name}/`
- 7 个 skill 文件：`.claude/skills/video_generation__{name}/SKILL.md`
- 1 个 agent 文件：`.claude/agents/video_generation__continuity-director.md`
- 文档已同步到 `.claude/README.md` + `CLAUDE.md`

---

## 目录骨架（每个系列都长这样）

```
series/{series_name}/
├── status.md                          # 进度合同（series-factory 读写）
├── research/
│   └── reference_pack.md
├── bibles/
│   ├── character_bible.md             # 复用片段 20–40 字 × 三视图
│   ├── scene_bible.md                 # 复用片段 × 远/近/特
│   ├── style_bible.md                 # 风格锚点 ≈20 字
│   ├── voice_bible.md                 # engine + voice_id + 音素提示
│   └── anchor_registry.md             # 全部 {{…}} 锚点登记表
├── episodes/
│   └── ep_001.md ... ep_NNN.md        # 每集 900–1200 字 + 4 栏 beat
├── prompts/ep_{NNN:03d}/
│   ├── storyboard.md
│   ├── clip_01_video_prompt.txt
│   ├── clip_01_snapshot_prompt.txt
│   ├── clip_02_video_prompt.txt
│   ├── …
│   ├── generation_manifest.md
│   └── continuity_report.md
├── clips/ep_{NNN:03d}/clip_1.mp4 ... clip_8.mp4     # Seedance 产物（你跑的）
├── snapshots/ep_{NNN:03d}/clip_1_to_2.png ...       # Seedance 快照（你跑的）
├── audio/ep_{NNN:03d}/
│   ├── vo_1.wav ... vo_N.wav          # TTS 分句（你跑的）
│   ├── vo_manifest.json               # 每条 VO 的起点毫秒
│   ├── bgm.mp3                        # 你挑的底乐
│   └── sfx/01_{name}_@mm-ss-ms.wav
└── assembly/
    ├── ep_{NNN}.sh / .ps1
    ├── ep_{NNN}_concat.txt
    ├── ep_{NNN}.srt
    ├── out/
    │   ├── ep_{NNN}_master.mp4
    │   ├── ep_{NNN}_douyin.mp4
    │   ├── ep_{NNN}_kuaishou.mp4
    │   ├── ep_{NNN}_tiktok.mp4
    │   ├── ep_{NNN}_yt_shorts_part1.mp4
    │   └── ep_{NNN}_yt_shorts_part2.mp4
    └── ep_{NNN}_capcut/               # CapCut 手动导入包
```

---

## 端到端推进（首跑最省心路径）

### 阶段 0 · 环境

```powershell
winget install --id=Gyan.FFmpeg -e
ffmpeg -version   # 需要 ≥6.0，含 sidechaincompress / loudnorm / subtitles
```

确认 `C:\Windows\Fonts\NotoSansSC-VF.ttf` 存在（回退 `msyh.ttc` / `simhei.ttf`）。

### 阶段 1 · 开一个新系列

在 Claude Code 里直接说：

> 用 `video_generation__series-factory` 开一个新系列，名字叫 `战神归来`，重生 + 大男主方向，全中文。

series-factory 会自动：
1. 创建 `series/战神归来/` 骨架
2. 调 `reference-scout` 出 `reference_pack.md`
3. 调 `preproduction` 锁 4 本圣经 + 锚点注册表
4. 调 `serial-novelist` 滚动写 3–5 集
5. 调 `storyboard-master` 把每集展成分镜
6. 调 `seedance-packager` 逐段产 prompt
7. 调 `continuity-director` 闸门校验
8. **停下来**列人工清单

### 阶段 2 · 人工执行清单（阶段 7）

factory 把清单生成给你之后，按单子做：

**A. Seedance 跑视频 + 快照**
- 打开 Seedance 2.0 前端（即梦 / fal / Replicate / PiAPI 任一）
- 按 `generation_manifest.md` 的「运行顺序」逐条：
  - 视频段：贴 `clip_01_video_prompt.txt` → 挂三视图 + 场景参考图（续接段再挂快照图）→ 生成 15 s mp4 → 落到 `clips/ep_001/clip_1.mp4`
  - 快照段：贴 `clip_01_snapshot_prompt.txt` → 挂同一批参考图 → 出 1 张静态 → 落到 `snapshots/ep_001/clip_1_to_2.png`
- 锚点重置（M % 4 == 0 的段）会在 prompt 里追加「本段需以三视图参考图为首要身份锚点，快照仅作构图参考」；操作上仍是挂原三视图，但**快照图降级为辅参考**（不作主要 first-frame）。

**B. TTS 渲染**
- 打开 `bibles/voice_bible.md` 查每个角色对应的 `engine + voice_id + pitch + emotion`
- 默认配音矩阵（可在 `voice_bible.md` 里改）：
  - 霸气青叔 / 战神主角：Volcengine BV107
  - 通用赘婿 / 少年主角：Volcengine BV119
  - 智慧老者 / 师长：Volcengine BV158
  - 古风少御 / 女主：Volcengine BV115
  - 沉稳解说男 / 旁白：Volcengine BV142
  - 稀有古风 / 反派：MiniMax / iFlytek 兜底
- 按 `storyboard.md` 的 `对白` / `旁白` 字段一句一条渲染，依次落到 `audio/ep_001/vo_1.wav ... vo_N.wav`
- 写 `audio/ep_001/vo_manifest.json`（每条起点毫秒来自 storyboard 段边界）

**C. BGM + SFX**
- 按 `reference_pack.md` 里的「BGM 情绪走向」挑一轨；裁到 ≥本集时长 + 5 s
- 落到 `audio/ep_001/bgm.mp3`
- SFX（可选）：文件名里编时间戳 `sfx/01_whoosh_1_@00-04-800.wav`

### 阶段 3 · 回到 series-factory 跑拼片

> 素材齐了，继续 `series/战神归来/ep_001` 到拼片。

factory 调 `clip-stitcher`：
1. 每段 ffmpeg trim 0.3 / −0.3 s 去渐隐 → `clip_1_trimmed.mp4` ...
2. concat 成无声长片
3. 烧中文字幕（Noto Sans SC / 54 px / 白字黑边 / `MarginV=140` 避开抖音 UI）
4. VO 按 `vo_manifest.json` 的毫秒定位
5. BGM baseline −18 LUFS，VO 激活时 sidechain 压到 −32 LUFS
6. SFX 按文件名毫秒戳定位
7. master 归一到 −14 LUFS
8. 派生 douyin / kuaishou / tiktok / yt_shorts_part1 / yt_shorts_part2 五份 mp4
9. 生成 CapCut 备份包（90 s 手动导入）

### 阶段 4 · 发布

各平台 comment 字段已自动写：
- 国内：`AI生成内容 / AIGC`
- 海外：`AI-generated content / #AI #AIgenerated`（TikTok），`Altered or synthetic content — AI-generated`（YouTube）

---

## 时间预算（首集）

| 阶段 | 第一集 | 稳定后（每集） |
|---|---|---|
| reference-scout（系列一次性） | 15–25 min | — |
| preproduction 锁 4 本圣经（一次性） | 25–40 min | — |
| serial-novelist 写一集（含滚动 outline） | 8–12 min | 5–8 min |
| storyboard-master 展一集 | 4–6 min | 3–5 min |
| seedance-packager 打包一集（6–8 段） | 3–5 min | 3–5 min |
| continuity-director 核验 | 1–2 min | 1–2 min |
| **人工 · Seedance 生成 6–8 × 15 s 视频 + 6–7 快照** | 25–45 min | 25–45 min |
| **人工 · TTS 渲染 + 选 BGM** | 10–20 min | 10–20 min |
| clip-stitcher 拼 + 导出 | 4–8 min | 4–8 min |
| **首集总耗时** | **≈ 100–170 min** | — |
| **第二集起每集** | — | **≈ 50–90 min** |

50 集目标 = 约 50–80 小时的实际工时（不含 Seedance 渲染排队 / 失败重跑）。

---

## 失败处理速查

| 症状 | 该做什么 |
|---|---|
| `continuity-director` 报 `VERBATIM-DIFF` | 回 `seedance-packager` 重跑（圣经没改的话）；或回 `preproduction` 查圣经改动 |
| `continuity-director` 报 `ANCHOR-RESET-MISSED` | 让 `seedance-packager` 重跑这一集（第 4 段自动加回重置句） |
| Seedance 同一段跑 3 次都漂 | 把该段 `运动幅度` 降到 1；仍漂则在 `storyboard.md` 把段拆成两个 7–8 s 子段，重走 packager |
| 字幕锯齿 / 字体回退 | 确认 `NotoSansSC-VF.ttf` 在 `C:\Windows\Fonts\`；`run_log.md` 里看 `fontsdir` 告警 |
| YT Shorts 切到 60.x s | 切点必须在 trim 边界（14.4 s 倍数）；6 段集切到 43.2 s，8 段集切到 57.6 s |
| `ep_{NNN}` 卡在 `continuity_failed` | 看 `prompts/ep_{NNN}/continuity_report.md` 的 FAIL 表，按错误码指回上游；**不要**手改 prompt 绕过 |

---

## 硬约束一览（所有 skill 都会强制）

- 全中文（仅 hex / `4K` / `DoF` / voice_id / `@image1` handle 保留英文）
- 每段 ≤15 s（Seedance 硬限）；每集 6–8 段；总时长 90–120 s
- 每集 900–1200 字（纯爽文，无低谷）
- 2–3 个核心角色（不含路人）
- **verbatim-substring rule**：圣经里的 `复用片段` 必须在下游 prompt 里字节级命中，否则 continuity FAIL
- 第 4 段 / 第 8 段强制锚点重置（对抗 Seedance 累积漂移）
- 连续性 FAIL = 禁止拼片（fail-closed）
- 滚动 outline ≤5 集，绝不前置规划到季末
- 硬烧中文字幕 + 保留 `.srt` 软字幕备份
- paid cutpoint 在 ep 10 / 30 / 60 硬植钩子

---

## 下一步建议

1. **跑通首集再扩产**。先把 ep_001 从侦察做到拼片跑一遍，把 Seedance 排队时间、TTS 声线选择、BGM 风格摸一次。
2. **圣经稳定前别写超 5 集**。`serial-novelist` 自己会挡，但你也别硬撬。
3. **回流体验**。在 ep_003 / ep_005 时，如果发现同一角色反复漂移，优先考虑 `preproduction` incremental 模式补三视图而不是加 prompt 文字。
4. **平台数据回看**。抖音 / 快手的完播率回来后，更新 `reference_pack.md` 的「差异化开局建议」，指导后续集子的钩子选择。

---

## 参考资料（已落到仓库）

- `.audit/adhoc_agents/2026-04-22/chinese_novel_video_agent/research/skill_contracts.md` — 所有 skill 的 section-level 合约
- `.audit/adhoc_agents/2026-04-22/chinese_novel_video_agent/research/shortdrama_craft.md` — 爽文套路 + 钩子模板 A–J
- `.audit/adhoc_agents/2026-04-22/chinese_novel_video_agent/research/assembly_recipes.md` — 全部 ffmpeg 配方
- `.audit/adhoc_agents/2026-04-22/chinese_novel_video_agent/research/tts_engines.md` — Volcengine / MiniMax / iFlytek 音色表
- `.audit/adhoc_agents/2026-04-22/chinese_novel_video_agent/research/platform_export.md` — 四平台规格 + AI 披露要求
- `.audit/adhoc_agents/2026-04-22/chinese_novel_video_agent/research/seedance_packager_contract.md` — Seedance prompt 合约逐字源

祝你爆款。
