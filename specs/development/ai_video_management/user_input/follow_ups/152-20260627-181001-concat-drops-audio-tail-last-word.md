# Follow-up draft 152 — 2026-06-27

拼接后 shot11 最后一句台词「我能进下门了」的「了」消失了——明显有处理、不是简单拼接。用户提议把 audio 处理选项暴露到 UI（如"0 处理拼接"）。

---
target_stage: 6
target_artifacts:
  - tools/seam_concat.py
severity: high
---

## 根因（已定位+验证）
`seam_concat._render_body` 把每个 clip 的**音频 atrim 到视频时长** `end=dur`（`_probe` 返回的是**视频流**长度）。shot11 视频 9.93s、音频 10.10s（TTS「了」在画面结束后才念完）→ 即便是纯 butt 硬拼（无 seam 裁切），音频也被裁到 9.93s → 末字「了」丢失。这是默认处理，不是 RIFE/裁切。

## 修复（tools/seam_concat.py）
- 新增 `_audio_dur()` 探音频流长度 + `_AUDIO_TAIL_KEEP_S=1.0` 常量。
- `_render_body`：butt 尾（tail≈0）时音频保留到**完整长度**（不再裁到视频长），超出视频的部分用 `tpad=stop_mode=clone` **保持末帧**补齐画面，a/v 同步；超出量 cap 1.0s（防 135c 卡死音轨撑爆段）。seam 裁切尾（tail>0）维持原样（裁切量对 a/v 同裁）。
- 关键坑：`tpad` 必须在 `_norm`（含 `fps=`）**之后**才生效，否则静默 no-op。
- 验证：shot11 body 音频 9.93→10.10s（「了」保住）、画面补帧到 10.08s（a/v Δ0.02s）；3-clip 合成含 0.3s 音频超长 clip 解码 OK、a/v 同步；test_episode_concat 23 passed。

## 未做 / 备注
- 用户提议的 UI 音频选项：默认修复后音频本就不再被裁、「了」保住，故无需手动选项即正确；如需显式控制可后续加 toggle。
- 与运镜 M8 新规则「接缝两端 0.3s 留台词静默 (ai_video.md (J))」互补：本修复是出片端兜底、(J) 是设计端预防。
- 用户需**重新生成 ep04** 才能拿到修复后的音频。
