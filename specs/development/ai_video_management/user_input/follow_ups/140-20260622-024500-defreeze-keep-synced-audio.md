# Follow-up draft 140 — 2026-06-22
去死帧（follow-up 139）引入回归：合成出来的视频**没声音了**。原因是 139 为绕开去死帧后的音画错位，把 concat 改成 video-only + 单条静音轨。但源 render 都带 AAC 音轨、用户要保留。修法：恢复每镜真音轨，并按去死帧后的时长 `atempo` 时间匹配，保持同步。用户：「有一个新的 bug 是出来的视频没声音了」。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: high
---

## 背景
139 误判 concat 音轨是 throwaway 而直接静音。实测 12 个源 render 全带 AAC 立体声音轨（i2v 自带环境音/人声），用户预览要听。难点：去死帧把视频压短（~14s），音轨连续 → 直接保留会逐镜漂移甚至 concat 冻帧补齐。

## 指令
恢复每镜真音轨并保持同步：测出每镜**去死帧后的视频时长** ldur，把该镜音轨 `atempo=window/ldur` 时间压缩到 ldur（卡死镜的音频略快但与画面同步；无卡死镜 tempo≈1.0 即 no-op）。concat 恢复 `v=1:a=1`。无音轨镜回落 anullsrc（按 ldur 定长）。

## 实现
- 抽出 `_video_chain(i,head,end,tail,fps)`：构建去死帧视频滤镜链一次，供"测时长"与"concat seg"用同一串（保证帧数一致）。
- 新增 `_decimated_duration(ff,src,vchain)`：跑该链到 null 读末尾 `time=` 得 ldur。
- 新增 `_atempo_chain(factor)`：单 atempo 仅 [0.5,2.0]，>2 拆成 ≤2 的乘积链。
- `_ffmpeg_concat`：每镜 `[i:a]atrim(window)→asetpts→atempo(window/ldur)→aresample→aformat[a{i}]`；恢复 `concat ... v=1:a=1[outv][outa]`；去掉单条 anullsrc 输入。恢复 `_probe_has_audio`（无音轨镜走 anullsrc 定长 ldur）。
- 保留 139 去死帧 + 137 两侧裁 + 138 帧率跟随源 + 135c 视频流时长 + 136 butt-join。

## 校验
- 真跑 EP1：zh video=113.9s/audio=114.0s、original 114.0/114.0，**has_audio=True、漂移 0.08s**（同步）。pytest 28 绿。零 prompt 改动。
- 另：shot11→12 仍有明显跳——查证为两段独立生成的"背身朝窗"近静止镜位姿对不齐（无运动遮掩→跳切感），属生成侧内容问题，裁帧/去死帧/帧率均无法消；需重生成 shot12（真从 shot11 末帧承接）或改硬切或加运动。已如实告知用户。
