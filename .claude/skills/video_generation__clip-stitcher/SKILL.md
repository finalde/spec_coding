---
name: video_generation__clip-stitcher
description: Stitch 6–8 × 15 s Seedance clips into a 90–120 s 短剧 master + hard-burned 中文 subtitles + TTS VO on the beat + BGM with sidechain ducking + SFX, then export 抖音 / 快手 / TikTok / YT Shorts (YT split into two ≤60 s parts). FFmpeg primary, CapCut bundle secondary. Hard-refuses when `status.md.ep_{NNN} != continuity_passed`. Runs after `continuity-director`.
---

# 拼合剪辑 · Clip Stitcher — FFmpeg 主链 + CapCut 备份 + 多平台导出

吃一集 6–8 × 15 s 的 Seedance 成片 + TTS 配音 + BGM + SFX，吐出主片 `master.mp4` 与四张平台分发版。FFmpeg 脚本是硬约束主链；CapCut 包只做收尾手工调。

## 前置闸门（任一不满足则立刻中止）

- `status.md.ep_{NNN}` **== `continuity_passed`**（非此值 → 报 REFUSE-RUN 并指回 `continuity-director`）
- `series/{name}/clips/ep_{NNN:03d}/clip_{1..N}.mp4` 逐段存在
- `series/{name}/audio/ep_{NNN:03d}/vo_manifest.json` 存在并校验通过
- `series/{name}/audio/ep_{NNN:03d}/bgm.mp3` 存在
- `series/{name}/prompts/ep_{NNN:03d}/generation_manifest.md` 存在（用于读 TOTAL 与段边界）
- `ffmpeg`/`ffprobe` 可执行（版本 ≥6.0 且 `ffmpeg -filters` 含 `sidechaincompress`、`loudnorm`、`subtitles`）

## Workflow

### Step 1 — 加载素材清单

读：
- `series/{name}/clips/ep_{NNN:03d}/clip_*.mp4`
- `series/{name}/audio/ep_{NNN:03d}/vo_manifest.json`
- `series/{name}/audio/ep_{NNN:03d}/bgm.mp3`
- `series/{name}/audio/ep_{NNN:03d}/sfx/*.wav`（可选）
- `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`（取字幕安全文本、段边界、SFX cue 时间）

计算每段 trim 后时长 = 14.4 s（Seedance 首/末各修 0.3 s 渐隐），总时长 = N × 14.4。

### Step 2 — 逐段修边（去掉 Seedance 首/末渐隐）

对每段 `clip_{i}.mp4`：

```bash
ffmpeg -y -ss 0.3 -i "series/{name}/clips/ep_{NNN}/clip_{i}.mp4" \
  -t 14.4 \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "series/{name}/clips/ep_{NNN}/clip_{i}_trimmed.mp4"
```

### Step 3 — concat 成一条无声视频

写 `assembly/ep_{NNN}_concat.txt`（相对路径，每行 `file '../clips/ep_{NNN}/clip_{i}_trimmed.mp4'`，不留空行），然后：

```bash
ffmpeg -y -f concat -safe 0 \
  -i "series/{name}/assembly/ep_{NNN}_concat.txt" \
  -c copy -movflags +faststart \
  "series/{name}/assembly/out/ep_{NNN}_video_only.mp4"
```

stream-copy 失败（GOP/采样率不齐）→ 自动降级到带 `-c:v libx264 -crf 18 -c:a aac -b:a 192k` 的重编码 concat。

### Step 4 — 生成字幕 `.srt`

从 storyboard 的 `字幕安全文本` 字段按段号 + `vo_manifest.json` 的 `start` 时间戳对齐，写 `series/{name}/assembly/ep_{NNN}.srt`。每行 ≤15 汉字，单行单气口。

### Step 5 — VO 按节拍铺轨

按 `vo_manifest.json`，每条 VO 用 `adelay=<ms>|<ms>` 定位，`amix=...:normalize=0` 汇流：

```bash
ffmpeg -y \
  -i vo_1.wav -i vo_2.wav … \
  -filter_complex "\
    [0:a]adelay=1200|1200[a0]; \
    [1:a]adelay=7800|7800[a1]; \
    … \
    [a0][a1]…amix=inputs=N:duration=longest:dropout_transition=0:normalize=0[vo]" \
  -map "[vo]" -c:a pcm_s16le -ar 48000 \
  "series/{name}/audio/ep_{NNN}/vo_track.wav"
```

### Step 6 — 主 filter_complex：字幕硬烧 + BGM 侧链闪避 + SFX + LUFS 归一

关键：`[vo_norm]asplit=2` → 一路进混音、一路做 BGM sidechain key；`sidechaincompress=threshold=0.05:ratio=8:attack=5:release=250:makeup=1` 实测 BGM 由 −18 LUFS 被压到约 −32 LUFS。

```bash
ffmpeg -y \
  -i "series/{name}/assembly/out/ep_{NNN}_video_only.mp4" \
  -i "series/{name}/audio/ep_{NNN}/vo_track.wav" \
  -i "series/{name}/audio/ep_{NNN}/bgm.mp3" \
  {-i series/{name}/audio/ep_{NNN}/sfx/<each>.wav …} \
  -filter_complex "\
    [0:v]subtitles='series/{name}/assembly/ep_{NNN}.srt':fontsdir='C\:/Windows/Fonts':force_style='FontName=Noto Sans SC,FontSize=54,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=140'[vout]; \
    [2:a]atrim=0:120,asetpts=PTS-STARTPTS,loudnorm=I=-18:TP=-1.5:LRA=7[bgm_raw]; \
    [1:a]loudnorm=I=-16:TP=-1.5:LRA=9[vo_norm]; \
    [vo_norm]asplit=2[vo_mix][vo_sc]; \
    [bgm_raw][vo_sc]sidechaincompress=threshold=0.05:ratio=8:attack=5:release=250:makeup=1[bgm_ducked]; \
    {每段 sfx: [k:a]adelay=<ms>|<ms>,volume=<0.85-0.95>[sfxK]; …} \
    [bgm_ducked][vo_mix]{[sfx0][sfx1]…}amix=inputs=<2+SFX 数>:duration=first:dropout_transition=0:normalize=0[premix]; \
    [premix]loudnorm=I=-14:TP=-1.5:LRA=11[aout]" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 \
  -movflags +faststart \
  "series/{name}/assembly/out/ep_{NNN}_master.mp4"
```

字幕样式白名单（锁定）：`FontName=Noto Sans SC,FontSize=54,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BackColour=&H80000000,BorderStyle=1,Outline=3,Shadow=1,Alignment=2,MarginV=140`。字体回退链：Noto Sans SC → Microsoft YaHei → SimHei。

### Step 7 — YT Shorts 60 s 分段（在 master 之上切）

按 clip 边界切两段，每段 ≤60 s：

- 8 段集：part1 = 0 → 57.6 s（clip 1–4），part2 = 57.6 s → 115.2 s（clip 5–8）
- 6 段集：part1 = 0 → 43.2 s（clip 1–3），part2 = 43.2 s → 86.4 s（clip 4–6）
- 7 段集：part1 = 0 → 57.6 s（clip 1–4），part2 = 57.6 s → 100.8 s（clip 5–7）

```bash
ffmpeg -y -ss 0 -t <PART1_END> -i "…/ep_{NNN}_master.mp4" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart \
  "…/ep_{NNN}_yt_part1.mp4"

ffmpeg -y -ss <PART1_END> -i "…/ep_{NNN}_master.mp4" \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 48000 -movflags +faststart \
  "…/ep_{NNN}_yt_part2.mp4"
```

切点必须落在 trim 边界；绝不跨对白或 SFX 切。

### Step 8 — 平台导出矩阵

从 `ep_{NNN}_master.mp4` 派生四个平台版：

| 平台 | 分辨率 | fps | CRF | maxrate | 音频 | 元数据 comment |
|---|---|---|---|---|---|---|
| 抖音 | 1080×1920 | 30 | 23 | 5M | AAC 192k −14 LUFS | `AI生成内容 / AIGC` |
| 快手 | 1080×1920 | 30 | 23 | 5M | AAC 192k −14 LUFS | `AI生成内容 / AIGC` |
| TikTok | 1080×1920 | 30 | 23 | 5M | AAC 192k −14 LUFS | `AI-generated content / #AI #AIgenerated` |
| YT Shorts ×2 | 1080×1920 | 30 | 23 | 6M | AAC 192k −14 LUFS | `Altered or synthetic content — AI-generated` |

每个平台一条 `ffmpeg` 指令（见 research/assembly_recipes.md §1.6），输出到：
- `series/{name}/assembly/out/ep_{NNN}_douyin.mp4`
- `series/{name}/assembly/out/ep_{NNN}_kuaishou.mp4`
- `series/{name}/assembly/out/ep_{NNN}_tiktok.mp4`
- `series/{name}/assembly/out/ep_{NNN}_yt_shorts_part1.mp4`
- `series/{name}/assembly/out/ep_{NNN}_yt_shorts_part2.mp4`

### Step 9 — CapCut 备份包

写 `series/{name}/assembly/ep_{NNN}_capcut/`：

```
ep_{NNN}_capcut/
├── README.md            # 导入流程（中文）
├── cut_sheet.md         # 剪辑单（字幕/VO/SFX/BGM 时间码表）
├── clips/{01..NN}_clip_{i}_trimmed.mp4
├── audio/{01..NN}_vo_{i}.wav + bgm.mp3 + sfx/{01..}_{name}_@mm-ss-ms.wav
├── subtitles/ep_{NNN}.srt
└── references/ep_{NNN}_master_preview.mp4
```

文件名前缀编入轨道顺序，便于 CapCut 自然排序拖入。**不**生成 CapCut 原生 draft JSON（版本易碎），只给文件夹 + 剪辑单，用户 ~90 s 手动导入。

### Step 10 — 写脚本 + 状态置位

- 把 Step 2–8 的全部 ffmpeg 命令落成两份可执行脚本：
  - `series/{name}/assembly/ep_{NNN}.sh`（Unix / Git Bash）
  - `series/{name}/assembly/ep_{NNN}.ps1`（Windows PowerShell）
- 实际执行（调用 ffmpeg）。每一条 ffmpeg 后用 `ffprobe` 校验出文件时长 / 分辨率 / LUFS 落在目标区间。
- 成功 → `status.md.ep_{NNN}` = `stitched`，写 `assembly/ep_{NNN}_run_log.md`（输入文件哈希、命令、耗时、ffprobe 结果）。
- 任一命令失败 → `status.md.ep_{NNN}` 保持 `continuity_passed`，报错位置 + ffmpeg stderr 摘取 20 行贴在 `run_log.md`。

## Inputs

- `series/{name}/clips/ep_{NNN:03d}/clip_*.mp4`
- `series/{name}/audio/ep_{NNN:03d}/vo_*.wav`（+ `vo_manifest.json`）
- `series/{name}/audio/ep_{NNN:03d}/bgm.mp3`
- `series/{name}/audio/ep_{NNN:03d}/sfx/*.wav`（可选）
- `series/{name}/prompts/ep_{NNN:03d}/storyboard.md`
- `series/{name}/prompts/ep_{NNN:03d}/generation_manifest.md`
- `series/{name}/status.md`（读闸门）

## Outputs

- `series/{name}/assembly/ep_{NNN:03d}.sh` + `.ps1`
- `series/{name}/assembly/ep_{NNN:03d}_concat.txt`
- `series/{name}/assembly/ep_{NNN:03d}.srt`
- `series/{name}/assembly/out/ep_{NNN:03d}_master.mp4`
- `series/{name}/assembly/out/ep_{NNN:03d}_{douyin,kuaishou,tiktok,yt_shorts_part1,yt_shorts_part2}.mp4`
- `series/{name}/assembly/ep_{NNN:03d}_capcut/`
- `series/{name}/assembly/ep_{NNN:03d}_run_log.md`
- 更新 `series/{name}/status.md`

## 输出规范

- **全部中文**（脚本注释、README、cut_sheet、run_log）；仅 ffmpeg 命令、参数名、编码标签、hex、LUFS、路径保留英文。
- **字幕硬烧** 是 v1 默认（Q18a）；`.srt` 同时保留为软字幕备份。
- **字体**：Noto Sans SC 优先；font path 写 `C\:/Windows/Fonts/NotoSansSC-VF.ttf`（注意 `C\:` 转义）。
- **LUFS 目标** 锁：BGM −18 / VO −16 / master −14 / BGM ducked −32。抖音/快手/TikTok/YT Shorts 均用 master −14；Bilibili 路径（若启用）单独跑 master −18。
- **切点纪律**：YT Shorts 切分必须在 trim 边界且不打断对白或 SFX；否则 REFUSE-SPLIT。
- **元数据 AI 披露**：国内平台 comment 写 `AI生成内容 / AIGC`；海外平台 comment 写 `AI-generated content / #AI #AIgenerated` 或 YT 的 `Altered or synthetic content — AI-generated`。
- **禁止改视频内容**：本 skill 不做色彩校正、不加转场、不加滤镜、不加片头片尾。只拼、只字幕、只混音、只编码。

## 边界情况

- 本集 <90 s（6 段 = 86.4 s）→ 允许，但在 Step 6 之前插入一段 BGM 尾奏 3.6 s，把总时长抬到 90 s；`run_log.md` 写明。
- 本集 >120 s → REFUSE-RUN 并指回 `serial-novelist` / `storyboard-master` 压缩。
- stream-copy concat 失败 → 自动降级为重编码 concat，并在 `run_log.md` 里写触发原因。
- `sidechaincompress` 在某些旧 ffmpeg 上缺失 → 报错并要求升级到 ≥6.0；不尝试变通。
- Noto Sans SC 不在 `C:\Windows\Fonts\` 也不在 `fontsdir` → 按 Microsoft YaHei → SimHei 顺序回退，`run_log.md` warn。
- `vo_manifest.json` 中 `start + duration > 总时长` → REFUSE-RUN。
- SFX 文件缺失但 storyboard 里标了 cue → REFUSE-RUN（不静默跳过）。
- 用户请求 Bilibili 导出 → 复用 TikTok 矩阵但 master LUFS 改 −18 并新增 `ep_{NNN}_bilibili.mp4`；`comment` 写 `AI生成内容 / AIGC`。

## Invocation examples

- 「把 `series/战神归来/ep_003` 拼成片，出四平台版。」
- 「只重跑 `ep_007` 的 YT Shorts 切分，master 保留。」
- 「`ep_012` 连续性闸门通过了吗？通过就立刻跑 stitcher。」
