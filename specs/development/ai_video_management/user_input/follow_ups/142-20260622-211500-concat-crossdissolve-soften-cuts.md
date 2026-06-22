# Follow-up draft 142 — 2026-06-22
合成成片在镜头交接处「画面先跳一下、才切到下一镜」，硬切切换感明显。改成在每对相邻 clip 之间加短交叉叠化（xfade 视频 + acrossfade 音频）柔化硬切、并盖住 i2v 留在 clip 尾部的 ~0.1–0.2s 安定抖动。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
  - tests/test_episode_concat.py
severity: medium
---

## 背景
用户实拍反馈：合成 EP1 成片「首尾帧交接处有明显的画面跳了一下，才切换到下一镜」，整体硬切切换感强。用户选「加转场柔化（交叉叠化）」。

## 与已回退叠化（136）的区别（关键，避免误判重复）
follow-up 135 的 seam cross-fade 在 **承接** 缝上叠化**近乎相同的两帧**→看着像闪一下，136 回退。本次叠化的是**两段完全不同的镜头**（硬切相邻镜），这是叠化的标准正确用途，不会出 136 的问题。且叠化期正好把上一镜尾部那一「跳」淡出。

## 改动（已落地）
`episode__writer.py::_ffmpeg_concat`：
- 每对相邻 clip 由 butt-join `concat` 改为 **xfade(transition=fade) 链 + acrossfade 链**（视频/音频按同一 `xdur` 重叠、A/V 锁定）。
- 新常量 `_XFADE_DUR=0.25`；`xdur=min(_XFADE_DUR, min(eff)/2)` 防短镜被过度消耗；`n==1` 跳过叠化。
- 保留 follow-up 137/138/141 的全部既有处理：承接 seam 两侧微裁、源帧率匹配、自然语速忠实音频（无 atempo）、audio-less 用 anullsrc。
- map 由 `[outv]/[outa]` 改为最终 xfade/acrossfade 标签。

## 代价（固有，已说明给用户）
叠化必然重叠两段，整集总时长缩短 `(n-1)·xdur`。EP1：源 130.2s → 输出 126.7s（11 缝×0.25 + shot10/11/12 承接微裁 0.6s）。语速不变（不动 atempo）。

## 测试
- `test_real_concat_preserves_length_*` 阈值由 `>2.0` 调为 `>1.4`（叠化重叠后 3 clip≈1.5s，截断到首 clip≈0.85s 仍可区分）。
- `test_real_concat_consecutive_承接_seams` docstring 由「No cross-fade/plain concat」更新为交叉叠化。
- 28 passed。

## 备注
本次只解决「硬切切换感/尾部跳帧」。shot11→12 背身位姿跳、镜头内卡死仍是生成缺陷，需用户侧重生成（见 wushen_juexing follow-up 042 的 regen 清单），叠化只能弱化、不能消除。
