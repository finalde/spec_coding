# Follow-up draft 037 — 2026-06-15
EP1 shot05：Seedance 反复「读台词乱套」——全员无口型镜的 `视频 prompt` 不应再写台词全文。

---
target_stage: 6
target_artifacts:
  - episodes/ep01/shots/shot05/shot05.md
severity: low
---

## 指令
shot05 是「系统二选一」镜，两个发声单元都不对口型（系统=画外提示音、裴知秋=内心独白），无任何在画人物开口。Seedance 却把 `视频 prompt` 的 `台词:` 全文当语音去生成、反复乱套。

修正：全员无口型镜的 `台词:` 字段**不写台词全文**——只声明「无人开口、嘴唇不动、勿生成任何配音/语音/口型；台词后期 TTS 另配」，逐行标说话人 + 类型(画外/OS)·不对口型，并保留系统流对话框在画 UI 字（选项按钮【继续苟活】【觉醒武神】）。台词全文只留在 `## 台词配音 prompt` 块。

此为通用规律（非只 shot05）：已写入 `.claude/agent_refs/project/ai_video.md` —— 「全员无口型镜：`台词:` 不写台词全文」。混排镜（含 ≥1 句在画对白）不剥离，仍写正文供 lip-sync。
