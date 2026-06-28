# Follow-up draft 079 — 2026-06-28
删 `参考分配:` 行 + `参考:` 每项 inline `=>@N` + 所有发声角色必先建卡（建 c20/c21/c22）

---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - .claude/skills/ai_videos__格式契约/SKILL.md
  - 2_世界观人设/characters/c20_锦袍执事 c21_青袍长老 c22_青衫少年
  - 2_世界观人设/casting.md
  - 5_6_分镜与prompt/episodes/ep06/shots/*.md
severity: medium
---

## 三条改动
1. **删 `参考分配:` 行**（从 prompt + 流程）：旧独立 `参考分配:` 行（把 @图N 映射成角色/首尾帧/场景的派角色句）废除。@图N→语义改由「项名自身 + inline @N」承载。ai_video.md 2026-06-22 amendment sub-rule 2 改写；格式契约 K27 退役改判 inline @N。
2. **`参考:` 每项 inline `=>@N`**：每个上传项 `=>` 后紧跟槽位号 `@N`（1-based 连号·byte-identical）。例 `c19_萧若云=>@1, c12_围观武者乙=>@2, c12_围观武者乙声音=>@3, 镇演武场_bg1_场口_入场=>@4`。语义由项名自明（本镜首帧/末帧/角色/场景/角色声音）。K27 改校 inline @N。
3. **所有发声角色必先建卡（all-speakers-carded gate）**：任何在 shot 有台词/OS 的角色（含背景一次性招募执事/报场路人/群像开口者）必须先在 `characters/cN_{名}/` 建卡（#识别标签 + voice_id + ref 立绘）+ casting 登记，才能在 shot 引用；禁 inline 无卡说话人。纯无台词群像仍可 inline。ai_video.md 新规则 + 格式契约 K30。

## 触发问题
shot03 的「锦袍执事 / 青袍长老 / 青衫少年」三个说话人当初被 inline 当背景一次性、无卡（用户指出）。已补建卡：
- c20_锦袍执事（JP-steward-01·别宗招募执事·热络抢人·没抢到）
- c21_青袍长老（QP-elder-01·别宗一流大宗长老·加码收下上品少年）
- c22_青衫少年（QS-youth-01·上品新苗·留松不定名·日后亦敌亦镜·§1.5⑤）
casting.md 已登记。shot03 改用 c20/c21/c22 卡 token（视觉 ref + 描述符 + 声音 + 角色识别 + 配音 voice_id）。

## EP6 落地
全 11 镜删 参考分配 + 加 inline =>@N；shot03 额外集成 3 张新卡（紧的镜守 K10 ≤2000）。
