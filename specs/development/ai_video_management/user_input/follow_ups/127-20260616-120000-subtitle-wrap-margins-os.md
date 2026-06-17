# Follow-up draft 127 — 2026-06-16
字幕左右无 margin（长行溢出）根因=WrapStyle 不换行；改为自动折行（一行排不下就多行）；内心独白也须进字幕。手机竖屏 9:16 视角。

---
target_stage: 6
target_artifacts:
  - libs/domain/value_objects/subtitle__valueobject.py
severity: medium
---

## 指令
- **左右 margin 仍未生效**：根因是 ASS `WrapStyle: 2`（禁止自动换行），长中文行整条溢出、无视 MarginL/R。修复：`WrapStyle: 0` + 渲染层主动折行——按每行字数上限（中文 ≤13 / 英文 ≤32，基于可用宽 840px）把长行**均分成多行**（手机一行排不下就两行/多行，绝不溢出）。
- 字号下调便于折行排版：中文 72→64、英文 52→46。
- **both 模式防重叠**：原来中/英两个独立事件（各自 MarginV），多行折行后会重叠；改为把中文行+英文行合成**一个底部锚定块**（中上英下整体堆叠）。
- **内心独白也要在字幕里**：确认 subtitles.md 收录所有发声单元（含内心独白/系统/画外），scaffold 从 `## 台词配音` 全部 `台词:` 取词（已满足；wushen EP1 14 个文件全部含 OS 行，已校验）。
