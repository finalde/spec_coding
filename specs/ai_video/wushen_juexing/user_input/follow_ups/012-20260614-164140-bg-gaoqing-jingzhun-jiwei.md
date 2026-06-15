---
target_stage: 6
target_artifacts:
  - ai_videos/wushen_juexing/scenes/s1_裴王府正厅/
  - ai_videos/wushen_juexing/style_guide.md
severity: medium
---

# Follow-up draft 012 — 2026-06-14

场景 bg prompt 应说明：生成的是**高清图片**，且**镜头与位置要精准**——因为这是用来做 shot 背景板的。

## 抽象后的指令

- 每个场景 bg prompt（步骤一 seed + 5 个方向 plate 的 image prompt）都要显式声明：
  1. **画质 = 高清**：4K 超高清、高分辨率、细节锐利清晰；本图用作 shot 背景板，画面要干净、透视稳定。
  2. **镜头 / 机位精准**：明确视角方位、机位高度（水平视平线）、焦距感（标准镜头约 35–50mm 等效）、透视稳定不畸变、构图位置精准、并预留人物站位空间。
- 原因：bg 图是 shot 的背景参考板，镜头/位置不精准会导致各 shot 透视/站位对不齐。

## 落地

- scene 档 seed prompt + bg1..bg5 plate prompt 各加 `画质:` 与 `镜头 / 机位:` 两行（方位按各自）。
- style_guide / 背景图系统 index 加一句「bg prompt 须声明高清 + 精准镜头机位（作 shot 背景板）」。
