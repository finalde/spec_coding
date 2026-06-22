# Follow-up draft 136 — 2026-06-22
承接 seam 的交叉淡化（follow-up 135）效果不行——两镜之间有一瞬间"图片的转换"，明显不契合。撤掉 crossfade，承接 seam 改回干净的连续硬接。用户：「效果不行，两个shot中间有一瞬间图片的转换，明显不契合」。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: medium
---

## 背景
follow-up 135 给承接 seam 加了 ~0.12s `xfade` 交叉淡化想抹平"速度突变"。但裁掉重复头帧后，参与混合的两帧已不再相同，dissolve 把它们叠在一起反而被肉眼读成"一瞬间图片切换/溶解"，比顿挫更出戏。结论：交叉淡化是错的工具，承接 seam 要的是干净的连续切（去掉重复帧即可），不是溶解。

## 指令
撤销 follow-up 135 的 xfade 左折叠，整集 concat 回到**一次性 butt-join `concat`**：每镜 normalize 成 v{i}/a{i}，承接 seam 仅靠裁掉重复头帧（follow-up 134 的保底裁）实现干净连续切，硬切 seam 同为干净切。零 crossfade、零 prompt 改动。

## 实现
- `EpisodeConcatBuilder._ffmpeg_concat` 去掉左折叠/`xfade`/`acrossfade`，改回单次 `concat=n=N:v=1:a=1`。删除 `continuity` 形参与 `_SEAM_XFADE_S` 常量。
- 保留 follow-up 134 的保底裁（`_SEAM_MIN_HEAD_TRIM_S`）+ audio-less 镜各自 `anullsrc`（修原双消费 bug）。
- 保留本轮真 bug 修复：`_probe_duration` 改测**视频流**时长（`-map 0:v:0 -c copy -f null -` 取末尾 `time=`），不再用容器 Duration——容器时长=更长的音轨会高估视频时间线，曾导致 EP1 被截到 60s（`少了很多内容`）。
- build() 不再计算/传 `continuity`。

## 校验
- 真跑 EP1（wushen_juexing）：zh + original 均 129.4s、完整 12 镜（撤 xfade 前的 bug 是被截到 60s）。
- 保留"音>视"回归测试（container Duration 超视频时不得截断，>2s）。
- fake_concat 签名去掉 continuity；xfade 命名的两个真 ffmpeg 集成测试改名/改 docstring 为 butt-join 语义、仍校验产物合法。pytest 25 绿（episode + boot smoke）。零 prompt 改动。
