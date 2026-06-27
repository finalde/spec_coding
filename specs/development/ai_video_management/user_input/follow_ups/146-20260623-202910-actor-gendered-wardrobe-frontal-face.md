# Follow-up draft 146 — 2026-06-23

Actor 生成 prompt 两处修正：① 男女服装必须区分，现状男角色被生成成穿女式吊带背心；② 所有 actor 必须正脸朝镜头，否则捕捉不到面部细节。

---
target_stage: 6
target_artifacts:
  - libs/infrastructure/writers/actor__chinese_prompt.py
severity: low
---

## 背景 / 根因
- **服装串性别**：`_WARDROBE_REVEALING_ZH` 是男女通用一条、写死「纯白色紧身**吊带背心**」。吊带背心是女款服饰名词，Kling 据此把男角色也渲染成穿女式背心。
- **未锁正脸**：三个 header 中只有 `_HEADER_FACE` 带「正脸面向镜头」，`_HEADER_BODY` 与主用的 `_HEADER_COMBINED` 都没有；且 `_LOOK_FACE_DETAIL_ZH["seductive"]` 含「微微侧脸」与正脸冲突。侧脸/转头时捕捉不到完整五官细节。

## 落地
- 服装按性别拆分：`_WARDROBE_MALE_ZH`（无袖紧身运动背心【男款圆领、绝非女式吊带背心】+ 运动短裤·体征看胸肌肩背轮廓）/ `_WARDROBE_FEMALE_ZH`（紧身吊带背心·体征看胸型大小）+ `_wardrobe_for(gender_slug)`；`_structured_lines` 与 `_build_with_picks_lines` 改为按 actor 性别取用（覆盖 face/body/combined 全部 builder）。
- 三个 header 统一为「正脸正面平视镜头（绝不侧脸、不转头、不低头、不仰头，面部完整正对镜头便于捕捉五官细节）」。
- `seductive` 面部细节「微微侧脸、颈线慵懒妩媚」→「下颌微收、眼神慵懒直视镜头、媚意自生」（保 seductive 韵味但守正脸）。
- 负面词组新增正脸约束：侧脸 / 侧面 / 半侧脸 / 3-4 侧脸 / 转头 / 扭头 / 回头 / 低头 / 仰头 / 脸朝向一侧 / 面部转开 / 背对镜头 / 后脑勺 / 不看镜头 / profile view / side face。

## 验证
- `tests/test_actor_prompt_only_roundtrip.py` 通过；实跑男/女 combined prompt 确认服装分化 + 两个 header 均含正脸约束。
