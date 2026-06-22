# Follow-up draft 041 — 2026-06-22

用户在 ep1 shot12 目录放了已备首帧图 `shot12_firstframe.png`，要求参考照片实际内容修改 shot12 prompt，确保 Seedance 识别该上传照片为首帧、并与上一镜（shot11）做到首尾帧链接。

---

target_stage: 6
target_artifacts:
  - 5_6_分镜与prompt/episodes/ep01/shots/shot12/shot12.md
  - 5_6_分镜与prompt/episodes/ep01/all_shot_prompts.md
severity: low

## 抽象意图
延续 follow-up 040 的同一机制：某 shot 已备实拍/指定首帧图（`shotNN_firstframe.png`）时，该 shot 的首帧侧描述（参考分配 @图1为首帧、走位起幅、镜头起幅、Shot context 衔接/Reference uploads、相关光线起幅）须对齐该图实际画面，并显式指向该 png 作首帧上传素材，保证 Seedance 从该照片起幅、与上一镜末帧承接。

## 照片实际内容（shot12_firstframe.png）
裴知秋背影立朝南厅门门槛内、墨黑高束马尾、玄黑交领布袍、面朝门外；门外为**明亮暖调**庭院天光（见绿地草木+灰瓦飞檐建筑），背影逆光剪影。

## 与连贯性的关系 / 暴露的张力
shot12 首帧（背影门槛内待出门）构图与 shot11 末帧（门前逆光驻足背影）一致，承接成立。但 **shot11 prompt 把门外光设计为「冷白天光」，而 shot12 实拍首帧门外是暖亮庭院光** —— 因承接镜首帧应≈上一镜末帧，这说明 shot11 的「冷白」文字已与实际渲染帧不符。本次将 shot12 门外起幅光对齐为暖亮实拍，并 flag shot11 末帧光线（待用户定：是否把 shot11 末帧侧文字也调暖以完全连贯，或以实拍为准）。
