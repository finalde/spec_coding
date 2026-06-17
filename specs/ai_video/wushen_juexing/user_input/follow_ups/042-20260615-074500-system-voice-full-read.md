# Follow-up draft 042 — 2026-06-15
shot08 系统台词前半段没声音；主角念台词慢了点。用户决策：系统读完整台词（option B）。

---
target_stage: 6
target_artifacts: [episodes/ep01/shots/shot08, shot04, shot05, shot06, shot13]
severity: medium
---

## 指令
系统(鎏金对话框)全剧统一：**保留配音、读完整台词**。系统语音由该 shot `台词配音` 块用锁定 voice_id 独立 TTS 生成、后期 mux，`时长目标` 配足整句（防前半段没声音）；视频 prompt 系统句标 `画外配音 voice-over·无任何在画人物对此口型`（系统音来自 TTS 轨、不靠视频模型自动读，模型自动读会断读）。系统文字仍作在画对话框 UI 字。shot08 同时提速：15s→13s、主角时长目标 9→8s。
