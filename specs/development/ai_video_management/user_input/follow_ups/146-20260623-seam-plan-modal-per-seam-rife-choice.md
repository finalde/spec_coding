# Follow-up draft 146 — 2026-06-23
点击「合成本集视频」改为弹出「拼接方案」面板：逐个 shot→shot 衔接处由用户选 硬拼/RIFE(+trim+补帧密度)，确认后生成，方案存 epNN/seam_plan.json 可复现。

---
target_stage: 6
target_artifacts:
  - tools/seam_concat.py
  - projects/ai_video_management/libs/infrastructure/writers/episode__writer.py
  - projects/ai_video_management/apps/ui/src/components/SeamPlanModal.tsx
severity: medium
---

## 背景 / 决策
RIFE 补帧只在「中段连续运动」可用：太像→停顿、太不像(换机位/构图)→morф。但全局帧差(mean-abs luma)在 ~40–50 区间无法可靠区分「大幅连续运动」和「构图/机位变化」——ep4 shot9→10=46 是 morф、ep3 有 44–46 却是好的，没有单一阈值正确(MAX 试过 55→40 都是按下葫芦浮起瓢)。结论(用户提议、采纳)：**把每条缝的决策交给人 + 缩略图辅助**，自动门限降级为「建议默认」。

## 产物
新增「拼接方案」面板，点 原片/中文/EN/中英 任一按钮即弹出(不再立即拼)：
1. `POST /api/episode-seams {path,lang}` → 每个衔接：承接/硬切、前镜末帧+后镜首帧缩略图(base64)、自动帧差、建议。
2. 硬切缝锁「硬拼」；承接缝可选 硬拼/RIFE；RIFE 下可调 trim(裁切 0.04–0.4) + 补帧密度(depth 1–4 / 自动)。
3. 「生成」→ `POST /api/concat-episode {plan}`，**用户选择覆盖自动门限**(plan 路径 gate off)，并把方案存 `epNN/seam_plan.json`；重开面板自动载入已存方案。

## 关键设计
- **方案文件存本集文件夹** `epNN/seam_plan.json`(用户选定)，跟集走、可复现、删集即删方案。
- **不复制补帧逻辑**：webapp 仍按 sandbox root 路径复用 `tools/seam_concat.py`，新增 `plan` 入参(每缝 {bridge,trim,depth})。
- **读写分层**：analyze 是只读 → 新建 `EpisodeQuery`(走 query 层)；build 仍是 command。
- 自动门限 MAX 55→40 保留，仅作面板「建议」默认值。

## 验证
- tool plan 路径(gate off+depth)实测在真实 clip 生效；analyze_seams 直驱返回 14 缝+缩略图+建议；build(plan) 生成并存 seam_plan.json、重载 has_saved_plan=True。
- API 双端点 TestClient/pydantic 别名(from)round-trip 通过；front tsc 0 错、build 成功。
- test_episode_concat 21 + route/container 49 全过。(全量 5 项预存失败属 wukong_juexing 数据/put_file loopback，与本功能无关。)
