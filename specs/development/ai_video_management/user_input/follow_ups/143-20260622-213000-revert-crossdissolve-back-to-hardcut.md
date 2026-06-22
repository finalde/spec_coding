# Follow-up draft 143 — 2026-06-22
撤销 follow-up 142 的镜头交接交叉叠化，退回忠实硬拼接。用户实拍反馈：叠化「感觉没有变柔和，还不如之前的硬切」。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/episode__writer.py
  - tests/test_episode_concat.py
severity: medium
---

## 背景
follow-up 142 给每对相邻 clip 加了 xfade+acrossfade 交叉叠化以柔化硬切/盖住尾部跳帧。用户看了成片：叠化没有变柔和，反而比之前的硬切更差，要求 revert。

## 教训（写给未来）
两次转场实验都失败：
- 135/136：承接近同帧叠化 → 闪一下。
- 142/143：整集不同镜叠化 → 不显柔和、反而更差。
结论：**i2v 短剧素材的镜头交接,干净硬切(butt-join concat)读感最好**。"画面先跳一下才切"是 i2v 留在 clip 尾部的安定抖动(生成缺陷)，叠化盖不住、只会引入新的违和；要根治得重生成该镜，不在合成层做转场。后续不要再提叠化柔化作为接缝方案。

## 改动（已落地，= 回到 follow-up 141 状态）
`episode__writer.py::_ffmpeg_concat`：
- 删 xfade/acrossfade 链，恢复 `concat=n=N:v=1:a=1[outv][outa]` butt-join，map 恢复 `[outv]/[outa]`。
- 删常量 `_XFADE_DUR` 及其注释；seam 注释恢复为 plain concat（记两次叠化均回退）。
- 自然语速忠实音频、承接微裁、源帧率匹配全部保留不变。

## 测试
- `test_real_concat_preserves_length_*` 阈值 `>1.4` 回退为 `>2.0`。
- `test_real_concat_consecutive_承接_seams` docstring 回退为 butt-join/no cross-fade（记两次叠化均回退）。
- 28 passed。EP1 重渲 130.7s（≈源 130.2s，忠实拼接恢复）。

## 仍未解决（生成缺陷，需重生成）
shot11→12 背身位姿跳、镜头内卡死（shot06/07 近静止 25–26%）。见 wushen_juexing follow-up 042 regen 清单。
