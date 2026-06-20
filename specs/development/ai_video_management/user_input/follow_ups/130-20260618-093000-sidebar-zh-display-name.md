# Follow-up draft 130 — 2026-06-18
left nav（Sidebar）里 drama 名（wushen_juexing）和 scene 名要用中文显示。

---
target_stage: 6
target_artifacts: [libs/infrastructure/readers/tree__reader.py]
severity: low
---

## 指令
Sidebar 已渲染 `display_name || name`，缺的是后端给 pinyin 文件夹填中文 display_name：
1. **drama**：旧 `_project_zh_title` 只读 README.md《》；新分阶段结构无顶层 README，标题在 `1_立项/concept.md` H1（`# 立项策划单 · 武神觉醒`）。扩展为先 README《》、再 `1_立项/concept.md` H1（取 `·` 后段）。
2. **scene**：scenes 现为 pinyin（`scenes/zhenbei_wangfu_zhengting/`），中文在 `{name}.md` H1 `（镇北王府正厅）`。`_sidecar_zh_label` 加 scene 分支（`parent.name=='scenes'` → 读 `{name}.md` H1 取 `（中文）`），scope 限定 scenes 以免误改 character 文件夹。
3. 抽公共 `_h1_zh`（《…》→（…）→ `·` 后段 → 整段 H1）。
4. 单测 tests/test_tree_display_name_zh.py（5 例）。
