# Follow-up draft 141 — 2026-06-22
撤销去死帧(139)+变速(140)，回到忠实拼接。两个新症状——「有些地方语速明显比原视频快」「整体秒数跟原来不一致」——都是去死帧的副作用。查证根因：视频卡住的段落**仍在说话**（冻画≠静音，如 shot06 视频 3.1–5.9s 冻结但音频非静音），所以去死帧要么把整镜音频 atempo 加速（语速快）、要么丢台词，且压短总时长。用户选**回到忠实拼接**。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: high
---

## 背景
139 用 mpdecimate 去掉镜头内长近静止段，140 为保音画同步把整镜音频 atempo 到去死帧后时长。但 atempo 对**整镜**音频统一加速（含没被裁的说话部分）→ 语速明显变快；且去死帧压短了总时长（EP1 130→113s）→ 与原始不一致。实测 freezedetect(视频) vs silencedetect(音频) 区间**不重合**：卡死段里角色在说话。结论：去死帧与本素材（卡顿压着台词）根本冲突，是错的工具。卡顿/跳跃属生成侧缺陷。

## 指令
撤销 139+140，`_ffmpeg_concat` 回到忠实拼接：每镜**原速原长**播放（含音频），只做 ① 承接 seam 两侧裁坊道(137) ② 帧率跟随源(138) ③ butt-join(136)。音频自然速度（atrim 到 [head,end] window + asetpts + aresample + aformat，**无 atempo**），无音轨镜回落 anullsrc(按 eff 定长)。concat v=1:a=1。

## 实现
- 删 `_DECIMATE` 常量、`_video_chain`/`_decimated_duration`/`_atempo_chain` 方法。
- `_ffmpeg_concat` 每镜视频 `trim→setpts→scale→pad→setsar→fps={target}`（去掉 mpdecimate+setpts=N/FR/TB）；音频 `atrim(window)→asetpts→aresample→aformat`（无 atempo）；anullsrc 按 `eff=end-h` 定长。
- 保留 137/138/135c/136 + `_probe_has_audio`。还原测试 clip 的 `noise`（去死帧才需要，已删）。

## 校验
- 真跑 EP1（wushen_juexing）：源 clip 合计 130.2s；输出 zh/original 均 **129.6s**（差 0.6s＝承接 seam 微裁），**has_audio=True、自然语速**。pytest 28 绿。零 prompt 改动。
- 遗留（生成侧，concat 不可修）：shot06/08 等镜头内「边说话边卡画」的停顿仍在；shot11→12 近静止背身镜位姿对不齐的跳切仍在。解法＝重新生成这些镜头（让画面在说话时有动作、承接镜真从上一镜末帧续）。
