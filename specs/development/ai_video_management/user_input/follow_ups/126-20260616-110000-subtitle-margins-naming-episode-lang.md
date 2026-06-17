# Follow-up draft 126 — 2026-06-16
字幕位置/边距优化 + 烧字幕输出按 shot 命名 + 按语言合成整集（最多 4 版本）。

---
target_stage: 6
target_artifacts:
  - libs/domain/value_objects/subtitle__valueobject.py
  - libs/infrastructure/writers/subtitle__writer.py
  - libs/infrastructure/writers/episode__writer.py
  - apps/ui/src/components/Reader.tsx
severity: medium
---

## 指令
- **字幕太靠下 + 左右边距不够**：底边距 80→170px（往上移、不贴底），左右安全边距 60→120px（不顶边、强制内缩换行）。both 模式中文 MarginV 250 / 英文 170。
- **烧字幕输出重命名**：不再用原 take stem，改每 shot 每语言一个稳定 master `shots/shot{NN}/shot{NN}_{zh|en|zhen}.mp4`，放 shot 文件夹根目录（与 renders/ 原始 take 区分）。同 shot 可导入多个原始 mp4；点某语言按钮即生成/覆盖对应 master。
- **按语言合成整集**：`/api/concat-episode` body 增 `lang ∈ original|zh|en|both`。original 取 renders/ 最新 take→ep{NN}.mp4；zh|en|both 取每 shot 的 shot{NN}_{suffix}.mp4→ep{NN}_{suffix}.mp4；缺源跳过。故一集最多 4 版本。UI「🎬 合成本集视频」改 4 按钮（原片/中文/EN/中英）。
