# Follow-up draft 139 — 2026-06-22
诊断确认「明显的一秒跳跃」是**源 clip 内部的长近静止段**（i2v 生成卡住 1–3s），非接缝问题：实测 shot06 源有 ~3.6s 近静止、shot08 ~2.4s、shot09 ~1s，且都在镜头中部（非接缝）。用户选择**合成时自动去死帧**。修法：concat 给每个 clip 加 `mpdecimate` 丢掉近重复/近静止帧 + `setpts=N/FR/TB` 重排，把死气压掉（clip 变短），不是 hold 住。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: high
---

## 背景
前四轮（裁重复帧 133/134、xfade 撤回 135/136、两侧裁坡道 137、帧率跟随源 138）都治不了，因为它们只动接缝/全局帧率，而卡顿是**镜头内部**的长近静止段。freezedetect 严阈值看不出（i2v 慢漂移非定格）。用户已确认接受去死帧的代价（压时长、改节奏、与预设台词时长对不上；音频本就后期 mux）。

## 指令
合成时自动去死帧：每个 clip 视频链 seam-trim → scale/pad/setsar → `mpdecimate` → `setpts=N/{target_fps}/TB`，丢近静止帧并把存活帧按目标帧率重排（死气被压掉、clip 变短，而非 fps 补帧 hold 住）。阈值 `hi=64*24:lo=64*12:frac=0.2`（实测：卡死镜头削 ~26%、运动镜头仅 ~3%，自适应不伤真动作）。concat 改 video-only（`a=0`），音频用单条 `anullsrc`+`-shortest`（去死帧后逐 clip a/v 无法对齐；真台词/BGM 后期 mux，本合成音轨本就 throwaway）。

## 实现
- 常量 +`_DECIMATE="mpdecimate=hi=64*24:lo=64*12:frac=0.2"`。
- `_ffmpeg_concat`：per-clip 视频 filter 用 `{_DECIMATE},setpts=N/{target_fps}/TB`（替原 `fps={target_fps}`）；`concat=...:v=1:a=0[outv]`；额外 lavfi `anullsrc` 输入(index n) 映射为音轨 + `-shortest`。删掉 per-clip 音频段构建与 `_probe_has_audio`（不再用；character_video__writer 有自己的副本）。
- 保留：seam 两侧裁(137)、视频流时长探测(135c)、帧率跟随源(138)、butt-join 无 xfade(136)。

## 校验
- 真跑 EP1（wushen_juexing）：zh 127.6→**113.3s**、original →113.5s，均 24.01fps、12 镜——压掉 ~14s 死气；长 hold(≥0.35s) 从 ~10s+ 降到 zh 1.8s / original 3.6s。
- 测试：合成 testsrc 是近静止会被 decimate 收掉，故 `_silent_clip`/`_clip_audio_longer` 加 `noise=alls=40:allf=t+u` 逐帧运动以保帧；时长断言据此成立。pytest 28 绿。零 prompt 改动。
- 注：残留 1.8–3.6s 散点 hold 若仍嫌卡，可调 `lo=64*16`/`frac=0.15` 更激进（风险：伤真动作）。
