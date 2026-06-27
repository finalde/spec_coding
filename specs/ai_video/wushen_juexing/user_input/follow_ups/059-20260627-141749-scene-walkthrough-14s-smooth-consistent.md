# Follow-up draft 059 — 2026-06-27

把场景的视频改成 14 秒（不要 15 秒）；过程运镜要连贯和平稳；把流程全部做到一致，不管小场景还是大场景。

---
target_stage: 2
target_artifacts:
  - .claude/agent_refs/project/ai_video.md   # rule 12.10（common-level）
  - 2_世界观人设/scenes/zhenbei_wangfu_zhengting/镇北王府正厅.md
severity: medium
---

## 指令（common-level 规则 → ai_video.md rule 12.10）
1. 场景 walk-through 视频时长 15s → **14s**（14s×30fps=420 帧）；负向/平台 duration 参数/截帧时点同步。
2. **运镜连贯平稳**为硬约束：一条几何连续路径、匀速缓动、dwell 进出 ease-in/out、monotonic 平滑、无剪辑/跳切/淡入淡出/180° 瞬反/顿挫骤停/抖动、dwell 锁机位给锐利静帧。
3. **大小场景一律一致**：小场景（室内单间/窄空间）与大场景（室外 vista/大殿/长街）用同一 14s 5-dwell 结构 + 同一平稳节奏；不因大小增减时长/改 dwell 数/改节奏，差异只在运镜位移幅度（随空间缩放）。

## 落地
- ai_video.md 12.10 加 amendment + body 模板时间轴重排 14s（#1 0.0-1.0/#2 3.5-4.5/#3 6.8-7.8/#4 10.0-11.0/#5 13.0-14.0，截帧 0.5/4.0/7.3/10.5/13.5）+ 步骤二模板行/header/用法/buffet/时长锁值同步。
- 回填 镇北王府正厅.md（唯一有完整 walk-through block 的场景）到 14s canonical 时间轴；body ≤2000（1988 ✓）。
- 其它场景用 image→image plate、无 walk-through block，不受影响；新场景自 stage2 默认 14s。
