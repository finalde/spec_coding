---
target_stage: 6
target_artifacts:
  - ai_videos/nvdi_tuihun_houhuile/scenes/s1_陈国公府正厅/s1_陈国公府正厅.md
  - .claude/agent_refs/project/ai_video.md
  - episodes/ep01/shots/*/shot*.md
severity: medium
---

# Follow-up draft 011 — 2026-06-01
仅标 scene 名不足以保证背景一致; 每个 scene 须成体系生成多面相/方位背景图 (存 scene 下), 每个 shot 指明用哪一张。

## 抽象指令

作为背景, 仅告诉在哪个 scene 不够 —— 需要 consistent 的背景。每个场景应**成体系生成不同面相和方位的背景图**, 同一 scene 的背景图都生成/存放在该 scene 文件夹下; 每个 shot 应指明具体用该 scene 的哪一张背景图。

## 落地 (用户选: 全套 6 张; 引用位置: 改参考行场景占位)

1. **scene 档**: `scenes/s1_陈国公府正厅` 新增「背景图系统」段 — 6 张 plate (bg1_朝北_长案主位 / bg2_朝南_厅门 / bg3_朝东_东侧墙 / bg4_朝西_西窗 / bg5_高位俯瞰 / bg6_案前虚化背景), 各含独立 text-to-image 生成 prompt + 用途表; PNG 存 `scenes/s1_陈国公府正厅/{plate_id}.png`。ep01 主用 bg1(朝北)+bg2(朝南) (全沿南北轴), 其余 4 张系统补全/备用。
2. **全 28 镜**: `参考:` 行场景占位由 `陈国公府正厅：place_holder` 改为 `陈国公府正厅·背景图 {plate_id}：place_holder` (依各镜相机朝向: 拍太监正脸/案=bg1朝北; 拍父子正脸/厅门=bg2朝南)。
3. **ai_video.md**: 参考行格式新增「场景背景图系统」规则 (per follow-up nvdi 011)。
