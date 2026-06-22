# Follow-up draft 137 — 2026-06-22
butt-join 后承接接缝仍有 ~0.2s 卡顿。诊断：卡顿不是重复帧定格，而是**两侧的速度坡道**——出镜（上一镜）减速冲进末帧、入镜（承接镜）从静止加速，帧一直在变只是很慢，紧阈值 freezedetect 漏检。修法：承接接缝两侧都裁掉坡道（入镜头部 + 出镜尾部），留干净的 motion-to-motion 切。用户：「还是有一瞬间的卡顿估计0.2秒左右」。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
severity: medium
---

## 背景
之前只裁入镜头部、且只裁字面定格（~0.05–0.08s）。实测以更松阈值（-40/-45dB）量同一批 clip：入镜头部慢帧 0.13–0.22s、出镜尾部慢帧 0.12–0.20s。这正是 i2v 的物理——末帧是模型被要求收束到的静止帧，出镜减速进、入镜从该静止帧加速出，合起来 ~0.2s 的"dwell"被肉眼读成卡顿。只裁单侧、只裁定格治不了。

## 指令
承接接缝**两侧都裁**速度坡道：
- **入镜头部**：freezedetect（阈值放松到 -45dB，使慢坡道也算 near-frozen），floor 保底；
- **出镜尾部（前一镜）**：固定裁一小段——尾部减速在松阈值下会被切成很长的碎片化"慢"区间，检测会高估（甚至误吞 ~1s 合法减速），所以尾部只确定性裁掉最后那一小段"近零运动"，不靠检测。
两侧各 floor `_SEAM_MIN_EDGE_TRIM_S=0.15`。仍是 butt-join（无 crossfade）。硬切接缝不裁。

## 实现
- 常量：`_SEAM_FREEZE_NOISE` -55→-45dB；`_SEAM_HEAD_EPS_S`→`_SEAM_EDGE_EPS_S`；`_SEAM_MIN_HEAD_TRIM_S(0.08)`→`_SEAM_MIN_EDGE_TRIM_S(0.15)`。
- build()：每个承接镜 i 设 `head_trims[i]=max(detect_head, 0.15)`、`tail_trims[i-1]=0.15`（前一镜尾部固定裁；不对尾部跑检测——碎片化不可靠/过裁）。`trimmed_s=head+tail`。
- `_ffmpeg_concat` +`tail_trims` 形参；每 clip `trim=start=H:end=(dur-T)`（视频+音频同步），`eff`/`end` 据此算，anullsrc 同步。
- 尾部裁只影响合成显示，不动 lastframe.png / 生成管线 / 尾帧锁定。

## 校验
- 真跑 EP1（wushen_juexing）：zh + original 均 127.6s 全 12 镜；承接镜（06/07/11/12）头部裁（shot06 检出 0.22+尾 0.15=0.367）、其前驱（05/10）拿到 0.15 尾部裁——两侧都裁实锤。
- 测试：fake_concat +tail_trims；承接 trim 断言改为"前驱尾部也裁 0.15"；`_SEAM_MIN_HEAD_TRIM_S`→`_SEAM_MIN_EDGE_TRIM_S`。pytest 25 绿。零 prompt 改动。
- 注：是否真消除 0.2s 卡顿需用户肉眼确认（合成端无法自动验感知）。
