# Follow-up draft 007 — 2026-06-13

(1) 补全其余 7 种情绪的 entry body（perf_0039–0122）。
(2) AI video shot 引用表演库：shotXX 若是悲伤相关，就用表演库 perfYY 作 reference——不照抄 prompt，而是把对应内容按 shot 剧情融入 prompt；shot.md 标注用了哪些表演库做 reference。
(3) shot UI 页面给一个「重新生成 prompt」按钮：更新表演库后点一下，重生成本 shot 的 prompt。

---

## 实现（已落地）

### (1) 补全全库
- 7 个并行 worker 撰写 perf_0039–0122（狠戾阴鸷/震惊错愕/柔情深情/委屈装可怜/不屑嘲讽/羞辱难堪/外放愤怒），各 12 条，按当前 generic 格式。
- 归一化：set_perf_durations（按 beat 时长）+ build_render_queue（10 情绪 168 块）。全库 122 条；代码块内 AU 零泄漏（FR-6 干净）。

### (2) shot 引用契约（FR-10 v2 — 融入非照抄）
- shot.md `## Shot context` 加 `表演库参考: perf_NNNN (...) — 用于 <角色> <beat>` 标注。
- 把 entry 锁定块的物理动作要点**按本镜剧情改写**进 `动作:`/`表情:`（保留内核+关键肌肉动作，重措辞+拆 beat），不照抄整段。
- 回写 `.claude/agent_refs/project/ai_video.md` rule 9b；样例 `_performances/_reference_usage.md` 重写。

### (3) 重生成按钮（FR-17）
- `ShotRegenPromptReader` + `POST /api/regen-shot-prompt`：读 shot 的 `表演库参考:` → 取各 entry 最新锁定块 + shot context → 组装 copy-paste 重生成 prompt（融入非照抄指令）。
- 前端 `ShotRegenButton.tsx` 挂在 shot 页面（含 `表演库参考:` 时显示「🎭 按表演库重生成」+ 复制框）。

## 影响

- FR-10 v2（融入）、新增 FR-17（重生成按钮）。ai_video.md rule 9b 新增。
- 测试：test_shot_regen.py（3）+ 现有 perf_score/import/boot（16）全过；前端 tsc 通过。
