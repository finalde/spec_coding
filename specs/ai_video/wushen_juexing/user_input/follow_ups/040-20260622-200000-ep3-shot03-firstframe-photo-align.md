# Follow-up draft 040 — 2026-06-22

用户在 ep3 shot03 目录放了一张实拍/已备首帧图 `shot03_firstframe.png`，要求参考照片实际内容重写 shot03 的 prompt，让 Seedance 能识别这张上传照片为首帧、并与上一镜（shot02）首尾帧接应。

---

target_stage: 6
target_artifacts:
  - 5_6_分镜与prompt/episodes/ep03/shots/shot03/shot03.md
  - 5_6_分镜与prompt/episodes/ep03/all_shot_prompts.md
severity: low

## 抽象意图
当某 shot 已备好实拍/指定首帧图（`shotNN_firstframe.png`）时，该 shot prompt 的「首帧侧」描述（参考分配 @图1为首帧、走位首帧、动作 0-3s、首末帧反差、镜头起幅、Shot context 衔接/Reference uploads）必须对齐这张图的实际画面内容，并显式指向该 png 作为上传到生成模型「首帧」槽的素材，以保证 Seedance 从这张照片起幅、且与上一镜末帧状态连贯。

## 照片实际内容（shot03_firstframe.png）
裴知秋盘坐破庙神像前、**一手抚于胸口**、阖目沉静、面色枯白；身侧后剥金神像、顶上一束冷青天光、潮冷青灰调、雨雾微尘。中近景（胸部以上）。

## 与连贯性的关系
照片画面＝shot02 末帧状态（shot02 结尾：左手按胸口、阖目定神、呼吸放缓）。原 shot03 首帧侧误写为「上身松垮·双手搭膝·头微垂」，既与照片不符、也与 shot02 末帧不符——本次对齐后顺带修正了这处 shot02→shot03 的承接断点。shot04 承接 shot03 末帧（面部大特写入定），本次未动末帧侧，下游不受影响。
