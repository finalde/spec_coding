# Follow-up draft 058 — 2026-06-27

承 057：shot10 末帧右侧现在有裴昭，shot11 首帧=shot10 末帧(承接)也带着裴昭，shot11 prompt 要交代裴昭随主角走远滑出画面、末帧只余主角。

---
target_stage: 6
target_artifacts:
  - 5_6_分镜与prompt/episodes/ep01/shots/shot11/shot11.md
severity: low
---

## 指令
057 把裴昭挪进 shot10 画面右侧后，承接帧(shot10 末=shot11 首)带裴昭。shot11 原写「本镜唯一人物」与之冲突。

修复 shot11：
- Characters 改为 主角(主体)+裴昭(仅起幅右侧·承接自 shot10 末帧·随主角走远+镜头推近前2–3s 滑出画面右缘、之后不在画面、末帧只余主角背影)。
- 镜头/走位/动作 写明起幅右侧含承接来的裴昭、随推近+走远滑出画面(前2–3s)；旧「后景高座人影虚化」(与机位北朝南矛盾)改「后景浅景深虚化」。
- 不给裴昭加 ref（已烙在首帧截图·加 ref 反留住他）→ 参考/参考分配不动。

## 约束 / 验证
- shot11 视频 prompt 一度 2057→精简去重→1991 ≤2000 ✓；all_shot_prompts.md(ep01) 同步。
- shot11 末帧(只主角)未变→ shot12 承接不受影响；shot10 末↔shot11 首仍 byte 一致(含裴昭)。
