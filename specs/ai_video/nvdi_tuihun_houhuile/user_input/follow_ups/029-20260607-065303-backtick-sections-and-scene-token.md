---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/episodes/ep01/shots/
  - .claude/agent_refs/project/ai_video.md
severity: medium
---

# Follow-up draft 029 — 2026-06-07
(1) prompt 里每个 structured section 的值用特殊符号 (反引号 `` ` ``) 包起来, 如 `` 镜头: `中近景 + 锁机位…` ``, 让 Kling 更易分辨各段。
(2) 参考里的场景 `陈国公府正厅·背景图 bg2_朝南_厅门：place_holder` 应和人物参考一样, 只放一个 `xxx_place_holder`; prompt 里所有关于该场地的 reference 都用这个 token。

## 落地 (全 28 shot)
- **反引号包裹**: 每个字段 `{label}: {value}` → `` {label}: `{value}` `` (参考/角色/情节/场景/镜头/走位/动作/台词/光线/节奏/渲染样式/比例/时长)。28/28。
- **场景 token 化**: `陈国公府正厅·背景图 {plate}：place_holder` → `{plate}_place_holder` (单 token, 形如 `bg2_朝南_厅门_place_holder`); `场景:` 字段的场景名 `陈国公府正厅` 也换成同一 `{plate}_place_holder`。参考 + 场景用同一 token。28/28 (无 verbose `陈国公府正厅·背景图` 残留)。OS 声音参考 (`{角色}(画外音·声音请参考)：place_holder`) 不动。

## 决策
场景 token 用**该 shot 的背景 plate**做名 (`{plate}_place_holder`, 如 bg1/bg2) 而非单一 venue 名 —— 保留朝向信息 (用户知道该 attach 哪张朝向图), 且直接由用户示例 `bg2_朝南_厅门` 派生。

## 规则 (ai_video.md)
- shot prompt 每个字段值用反引号包裹 (帮 Kling 分段)。
- 场景背景参考与人物参考一律 `{xxx}_place_holder` 单 token; shot 内所有该场地引用 (参考 + 场景) 用同一 token。

## 核查
反引号 28/28; 场景 token 28/28; LF 保持 (写文件 newline="\n", edit 按钮不回退)。
