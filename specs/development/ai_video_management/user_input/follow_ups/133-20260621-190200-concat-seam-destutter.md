# Follow-up draft 133 — 2026-06-21
按末帧承接生成的相邻镜拼接（click「中文」整集 concat）时，承接接缝处有 ~0.2s 画面卡顿（重复定格帧）；要在 concat 时自动抹平、让画面 smooth、观众看不出（声音用户自理）。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
  - apps/ui/src/components/Reader.tsx
severity: medium
---

## 背景 / 根因
承接镜（`衔接:` = 承接）是用上一镜末帧当首帧生成的，所以它第一帧 ＝ 上一镜最后一帧（重复），且生成器常把首帧静止保持一拍 → 整集 concat 时接缝处画面冻 ~0.2s。硬切镜是有意切镜、不处理。

## 指令
整集 concat（`POST /api/concat-episode`，原片/中文/EN/中英 四个 🎬 + 烧字幕路径）时，**只在承接镜接缝**自动检测并裁掉 incoming 镜头头部的静止重复帧，让承接处连续顺滑；硬切镜不动。用户选「自动检测裁掉重复定格帧、流畅优先」（裁帧会让承接镜略短，可接受、声音自理）。

## 实现
- `EpisodeConcatBuilder`：
  - `_is_continuity_shot(shot_dir)` 读 shotNN.md 的 `衔接:` 行（**先判硬切**——硬切文案「无承接帧」含子串「承接」，须先排除，否则全部硬切被误判为承接）。
  - `_detect_head_freeze` 用 freezedetect 只解码头 1.5s；`_parse_head_freeze` 解析（clip 头部起冻才裁、裁到 motion 恢复点、capped 0.6s、fail-open 不裁）。
  - 每个承接镜（i>0）在 concat filter 里 `trim/atrim=start={t}` 裁掉头部静止段；硬切镜与首镜不动。
  - `ShotClip.trimmed_s` 透传 dto/mapper/api；前端 toast 报「抹平 N 处承接接缝」。
- 测试：`test_episode_concat.py` +8（`_parse_head_freeze` 4 例确定性 + 真 ffmpeg static-head 检测 + 承接裁帧/硬切不裁 build 集成 + `_is_continuity_shot` 硬切优先）。
- 校验：pytest 47 绿（boot/episode/frame/intro/scene_plate/subtitle_batch）；apps/ui tsc -b 干净。
