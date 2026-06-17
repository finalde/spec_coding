# Follow-up draft 039 — 2026-06-15
全员无口型镜不可剥离台词正文（修订 037）——shot05 剥离后视频完全没台词声音。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot01, shot04, shot05, shot06, shot13]
severity: medium
---

## 指令
037 规定"全员无口型镜不写台词全文"实测错误：视频模型(Seedance)从 `台词:` 文本生成配音，删正文=成片无台词声音。修正：任何镜都保留台词正文；全员无口型镜防"读台词乱套"改用**强标 `画外配音 voice-over` + `嘴唇不动不对口型` + 系统句 `无任何在画人物对此口型/嘴动`**（先前乱套真因=画外音被 lip-sync 到在画脸上），而非删文。已恢复 shot01/04/05/06/13 台词正文 + VO 标注；ai_video.md「全员无口型镜」规则与监制 skill 硬约束同步修订。
