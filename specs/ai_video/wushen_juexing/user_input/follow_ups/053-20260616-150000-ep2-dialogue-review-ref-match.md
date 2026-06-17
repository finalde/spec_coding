# Follow-up draft 053 — 2026-06-16
EP2 台词/情节大师全量 review + 修：① shot2 系统台词"潜伏待显"太文绉绉、换通俗；② 全集台词/情节流畅性 review（含语速节奏）；③ 所有 shot 的 `参考:`/`场景:`/`Reference uploads:` 必须精确 match 角色 id/name 与场景 id/bg name（用户发现多处不精确）。

---
target_stage: 6
target_artifacts:
  - episodes/ep02/shots/*/shot*.md
  - episodes/ep02/{script.md, dialogue.md, source_novel.md, shotlist.md}
severity: medium
---

## 指令
1. **"潜伏待显"通俗化**：S02 系统台词 `首份大礼【武神躯】——发放中，潜伏待显` → `断绝达成。首份大礼【武神躯】，已注入宿主体内。`（"潜伏/暗藏不显"之意改由裴知秋内心"先沉到骨子里——这些人还不配看见"承载）。全项目零"潜伏待显"残留。
2. **全集台词流畅性 + 语速节奏 review**（ai_video__dialogue_master）：发现并修以下"念不完/语速飙"（字数÷时长>5字/秒）：
   - S02 系统(38字/4s≈9.5字/s)+内心(27/3s) → 精简为系统(20字)+内心(18字)、Duration 7→8s、各句时长目标 4+4。
   - S03 名场面宣言(~44字/7s≈6.3字/s，太赶) → Duration 7→9s、宣言去"堂堂正正地"略精简(~43字/9s≈4.8字/s)、时长目标 9s；签名句"今天赶我走的人，将来都得仰起头来看我"byte-identical 保留。
   - S08 系统(44字/4s≈11字/s)+内心(24/2s) → 去文绉绉("脱离桎梏/淬炼己身/前路机缘自有指引")改白话"宿主已脱身。武神躯初成、根基未稳，先找个清静地方好好修炼"；内心精简"也好。这身子，我自己一寸寸夺回来"；Duration 6→8s、时长目标 5+3。
   - S01 裴昭赌约(35字)动作窗仅 2.5s(≈14字/s) → 动作改为裴昭 1.5–8s 全程嗤笑立赌、时长目标 8→7s(5字/s)。
   情节链(P1–P7)/朝向走位(C1–C5,M1–M6)复核通过：走出去 forward 连续位移、转身只 S01 一次、系统 beat 跨集功能各异、藏锋一致、黑影仅剪影。
3. **参考精确匹配 id/name**（全 14 shot 的 `参考:`/`场景:`/`Reference uploads:`/`Scene:`）：角色用精确名（裴知秋/裴昭/凌虚子，去"turntable.mp4"/"c1_前缀"杂串）；场景/bg 用各 scene 档真实 bg 名（不再用 `s6_王府外长街`/`s7_镇北城门`/`bg s6_…`/"inline bg"/`s1_正厅` 这类非 bg/错名）。逐镜 bg 按各 scene 档"出片选 plate"指引锁定：
   - S01 bg5_中_中轴俯瞰+bg2_朝东_东列长案；S02 bg5+bg3_朝南_厅门逆光；S03 bg3_朝南_厅门逆光（scene s1_裴王府正厅）。
   - S04 s5_王府外高地/bg1_远眺王府（去"inline bg"）。
   - S05/S06 bg1_府门石阶；S07 bg2_长街主向；S08/S09/S10 bg3_街心华灯；S11 bg4_长街远景城道（归 s6_王府外长街·城门在望，非 s7）（scene s6_王府外长街）。
   - S12 bg1_城门洞主向；S13 bg2_城楼飞檐；S14 bg3_门洞幽暗内（scene s7_镇北城门）。
   时长合计 89→94s（S02/S03/S08 加时；14 镜不变）。

## 流程教训（common-level）
shot worker 产出的 `参考:` 易出现"角色名+turntable.mp4""scene-id 当 bg""inline bg"等不精确串；台词易超 5 字/秒念不完。已知应在 WORKER_CONTEXT/校验环节强制：参考字段=精确角色名 + scene 档真实 bg 名；每句台词字数÷时长目标≤5 且各句时长目标之和≤shot 时长。
