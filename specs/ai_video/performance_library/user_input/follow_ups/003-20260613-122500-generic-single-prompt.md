# Follow-up draft 003 — 2026-06-13

为什么一定要分 Kling 版本和 Seedance 版本？希望表演库是 generic 的，能不能只有一个 prompt。我会自己上传 actor 的照片，既然是考察演技，可以用任意 actor 表演。场景也可以是表演室，不需要宏大场景，只要灯光氛围适合当前情绪即可。

---

## 抽象指令

表演库应 generic 化，三点收敛：

1. **一个通用 prompt**：删掉 Kling 版 / Seedance 版的分裂（二者本就字节相同），每条 entry 只保留一个 model-agnostic 的检验视频 prompt。
2. **演员由用户上传**：考察的是演技、actor 可任意替换，prompt 不固定演员；用 image-to-video + 用户上传的参考照渲染。
3. **表演室 + 按情绪灯光**：场景为简洁表演室（无宏大布景/道具），灯光氛围适配当前情绪即可（不再全局中性白光）。

## 实现（已落地）

- `_testrig.md` 重写为 v2：演员=上传任意参考照、场景=表演室、灯光=按情绪、单一通用 prompt 骨架。
- 每个 `_emotion.md` 加「灯光氛围（检验视频）」行（`tools/set_emotion_lighting.py`）。
- 38 条 entry 的 `## 检验视频`（双块）合并为一个通用块、`## 起始帧表情` 去演员化（`tools/genericize_perf_prompts.py`），表演文本与峰值描述逐字保留。
- 导入 tag 简化：视频 `演{NNNN}`、起始帧 `演{NNNN}始`（去模型标记）；导入器视频→`perf_NNNN/renders/`（原名共存）、起始帧→`perf_NNNN__startframe`。
- 渲染队列重生成。

## 影响

- 改 FR-11（v2 generic 检验视频）、FR-15（tag 去模型标记 + 视频→renders/）。FR-13 验证回路不变（仍可在多模型渲染同一通用 prompt、按模型记分）。
- 早期 v1 的 validation_mechanism 的「钉死中性光照」结论被用户显式覆盖（灯光按情绪），已在 _testrig v2 记取舍说明。
