# Follow-up draft 004 — 2026-06-13

每个 perf 页面给我几个反馈的 button：review 完视频后我可以打分；如果你（Claude）有能力，等我把视频下载下来你也可以 take a look and rate；最后结合我们两个的分数，再看是否 accept 或修改 prompt。

---

## 抽象指令

为每条 entry 建立**双评分者评分闭环**：

1. **webapp 评分按钮**：每个 perf 页面有打分 UI（三轴 1–5），review 完视频后用户点选保存，写回该 entry。
2. **Claude 评分**：视频下载后，Claude 抽帧查看并按同样三轴打分（能力边界：Claude 读图不读 mp4，故抽帧评分，连续动作流畅度为静帧推断）。
3. **合议**：结合你 + Claude 的分数自动结算 accept / revise；revise 则按失败轴改 prompt。

## 实现（已落地）

- **schema**：`## 实测与验证` 改为双评分者表（你 / Claude × 三轴）+ `decision` + `合议` 行（`tools/migrate_validation_block.py`，38 条）。
- **评分引擎**：`libs/infrastructure/writers/perf_score__writer.py`（纯函数 `update_scores_text` + `PerfScorer`）——解析表、更新 (评分者,模型) 行、重算合议（accept/revise/pending）。
- **端点**：`POST /api/perf-score`（command + route + container 全 DDD 接线）。
- **前端**：`PerfScorePanel.tsx` 挂在 perf 页面顶部（模型选择 + 三轴 1–5 按钮 + 笔记 + 保存 + 显示 Claude 分与合议）。
- **Claude 评分链**：`tools/extract_perf_frames.py`（cv2 抽帧）+ `tools/perf_rate.py`（复用同一引擎写 Claude 行）。

## 影响

- 落 spec FR-16（双评分者评分 + 合议）。FR-13 的人工验证门细化为「你 + Claude 合议」。
- 测试：test_perf_score.py（6）+ 现有 import（3）+ boot smoke（7）全过；前端 tsc 通过。
