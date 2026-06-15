# Follow-up draft 013 — 2026-06-14

角色 prompt 必须生成视频，统一为「视频 reference」格式（与《女帝退婚后悔了》一致）。

---

武神觉醒 8 个角色档（c1–c8）原本使用已弃用的「Seedream 立绘 prompt」（rule #12.2，输出静态 PNG），导致角色 prompt 生成的是图片而非视频。这与统一 setting 不符：`.claude/agent_refs/project/ai_video.md` §12.5 规定「视频 reference」7s 单 take turntable prompt（rule #12.5 v11）**完全 supersede 旧的立绘单 prompt 格式**，《女帝退婚后悔了》各角色档已采用此格式（渲染 mp4）。

要求：把 8 个角色档底部的 prompt section 从「Seedream 立绘」改为「视频 reference prompt（rule #12.5 v11）」，结构与 nvdi_tuihun_houhuile 各角色档逐字对齐——主体一句话锁定 + 角色造型块 + 身高/服装/面部细节 + 5-phase timed 姿态（0-2s 正面 / 2-3s 左转 / 3-4s 侧身 / 4-5s 左转 / 5-7s 背面）+ 镜头/光线/渲染/比例/时长/音频 + 3 句数字计数台词配音对照表。角色锁定描述符（顶部表格）保持不变，仅替换 prompt section。
