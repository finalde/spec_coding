# Follow-up draft 078 — 2026-06-28
shot prompt `参考:` 行加「声音参考」token（每个有台词角色配对一个 {角色}声音=>）+ 写进流程 + update 所有 EP6 prompt

---
target_stage: 6
target_artifacts:
  - .claude/agent_refs/project/ai_video.md
  - .claude/skills/ai_videos__格式契约/SKILL.md
  - 5_6_分镜与prompt/episodes/ep06/shots/*.md
severity: low
---

## 指令
shot 的 `参考:` 行除了视觉 ref，还要带**声音信息**：每个角色在视觉 ref token 后配一个 `{角色}声音=>`。例：`参考: 萧若云=>, 萧若云声音=>, 围观武者乙=>, 围观武者乙声音=>, 镇演武场_bg1_场口_入场=>`。把规则写进流程并 update 所有 EP6 prompt。

## 规则（已写进流程）
- ai_video.md 12.4-C 台词配音节加：`参考:` 行里**每个在本镜有台词的角色，视觉 ref token 后紧跟配对 `{角色}声音=>`**（声音 ref＝该角色锁定 voice_id 声样源·turntable 0–2s 统一声样 trim / casting voice_id，与 `## 台词配音 prompt` 的 voice_id 一一对应）。无台词入画角色只挂视觉 ref；背景一次性说话人加独立 `{名}声音=>`；纯 OS/画外只挂 `{角色}声音=>`。`Reference uploads` 同步列声音条。
- 格式契约新增 **K29**（声音 token 齐全·blocker）。

## EP6 落地
全 11 镜 `参考:` 行加配对声音 token（仅有台词角色）：shot01 围观乙 / shot02 萧若云 / shot03 锦袍执事·青袍长老·青衫少年(一次性) / shot04 裴昭OS / shot05 裴昭·裴霆 / shot06 围观甲 / shot07-08 云鹤·玄微子 / shot09 裴昭 / shot10 围观甲 / shot11 围观乙。紧的镜(03/07/09/10/11)trim 冗余英文负面词让位、守 K10 ≤2000。
