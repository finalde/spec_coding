# Follow-up draft 125 — 2026-06-16
每个 shot 文件夹的字幕文件改为双语（中文+英文）；烧字幕按钮提供三种语言选择（中/英/中英）生成带字幕视频。

---
target_stage: 6
target_artifacts:
  - libs/domain/value_objects/subtitle__valueobject.py
  - libs/infrastructure/writers/subtitle__writer.py
  - apps/api/routes/subtitle__route.py
  - apps/ui/src/components/SiblingMedia.tsx
severity: medium
---

## 指令
- **双语 `subtitles.md`**：每 shot 的 `shots/shot{NN}/subtitles.md` 每行 `起-止(秒) 中文 || English`（`||` 分隔中/英；省略即中文单语，向后兼容）。`|` 不再作时间-文本分隔符。SubtitleCue 增 zh/en 字段。
- **三语言烧录**：`POST /api/burn-subtitles` body 增 `lang ∈ zh|en|both`，输出 `{stem}_subtitled_{zh|en|zhen}.mp4`；`both` 模式中文在上、英文在下。新错误 `invalid_subtitle_lang`；所选语言无文本→`empty_subtitles`。
- **UI**：render 卡片把单个「💬烧录台词」换成三个按钮「💬中文 / 💬EN / 💬中英」，各调对应 lang。
- **scaffold**：生成双语模板 `中文 || `（英文留空），并改从 `## 台词配音` 块的 `台词:` 行取词（更可靠）。
- 样式：中文 微软雅黑 72、英文 Arial 52、底部居中白字黑边。测试 `tests/test_subtitle_burn.py` 覆盖双语解析 + 三模式烧录 + 非法 lang。
