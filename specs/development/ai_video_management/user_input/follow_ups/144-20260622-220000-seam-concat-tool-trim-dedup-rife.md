# Follow-up draft 144 — 2026-06-22
新增 `tools/seam_concat.py`：针对「Seedance 首尾帧链式生成的两段视频，直接 concat 后接缝有明显镜头切换感」的独立处理工具。

---
target_stage: 6
target_artifacts:
  - tools/seam_concat.py
severity: low
---

## 背景
用户用 Seedance 首尾帧生成两段视频、手动 concat 后接缝顿挫明显，问怎么拼接处理。根因：首尾帧生成让 A 结尾缓动收敛到末帧、B 又从同一张首帧缓动起步，且 A 末帧≈B 首帧（B 由 A 末帧生成），直接 concat = 减速→同帧冻结两帧→加速 的速度断裂+重复帧（不是像素跳变，所以叠化盖不住——已在 142/143 验证叠化更差）。

## 实测裁决（写给未来，避免重走）
- **方案1 裁缓动+去重复帧**：ffmpeg-only，可靠，价值最高 → 工具默认。
- **方案2 交叉叠化**：盖不住速度断裂、反而更差 → 已弃（webapp 142/143 验证）。
- **方案3 光流补帧**：真正修复运动断裂。**ffmpeg `minterpolate` 实测在「两张任意静态帧之间」只能产出 0–4 帧乱码，不能重建多帧运动**（本回合验证），故工具**不内置 minterpolate**；真补帧靠外部 RIFE（`--rife`）。无 RIFE 时工具保持 trim-only，绝不假装有 bridge。

## 工具行为
`python tools/seam_concat.py --out ep.mp4 A.mp4 B.mp4 [...] [--trim 0.10] [--rife <exe>] [--fps 0]`
- 默认：每个接缝裁掉前镜 ease-out 尾 + 后镜 ease-in 头（头裁同时丢掉重复的共享帧），filter-concat 重编一次（短段 `-c copy` 会丢帧，故用 filter）。
- `--rife <exe>`：用外部 RIFE（如 rife-ncnn-vulkan）对每个接缝抽前镜末帧+后镜首帧、补中间帧；任一步失败→该缝退回 butt-join + 打 warning（无声造假禁止）。`--rife` 路径不存在→upfront 干净报错（exit 2）。**RIFE 调用只用最稳的单帧对接口 `-0 a -1 b -o mid.png`（产 1 张中点帧），2 层递归得 3 张中间帧（q1/mid/q3，约 0.1s 桥）；dir-mode `-n` 语义跨 build 不一致故不用。本机无 RIFE 二进制、此路径按 rife-ncnn-vulkan 文档接口编写但未本地实测，失败安全退化。**
- 仅适用**连续接缝**（同场景/景别/机位）；不同机位/景别本就该硬切，别 trim/bridge。

## 与 webapp 关系
独立工具，**不改 webapp 合成**（webapp 经 141/143 已定为忠实硬拼接、不做转场）。用户手动 concat 工作流用此工具；EP1 那种「假承接、实为景别跳切」的缝不适用（已在 042 改判硬切）。

## 验证
合成 testsrc 片段实测：plain concat 60 帧（含重复缝帧）→ trim+dedup 48 帧（缝区去除、内容保留）；3 段链 69 帧；坏 `--rife` 路径干净报错；正常路径 exit 0。
