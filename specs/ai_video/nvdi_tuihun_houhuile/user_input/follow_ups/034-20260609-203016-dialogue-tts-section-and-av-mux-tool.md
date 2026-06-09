# Follow-up draft 034 — 2026-06-09
每个 shot.md 增设独立「台词配音 prompt」section（喂高端 AI 情感 TTS / Seedance 生台词 MP3）；并新增工具把 video MP4 + 台词 MP3 + BGM MP3 合成一条成片。

---

## 指令（抽象）

走「高端 AI 情感 TTS」配音路线，分步落地，**仅本剧 nvdi 项目级，不改通用工作流契约**（rule 12.4 schema / ai_video.md / CLAUDE.md 不动；用户此前明确「暂时只要建议」）：

1. **shot.md 新增 section**：每个 `episodes/epNN/shots/shotNN/shotNN.md` 末尾加一个独立的 `## 台词配音 prompt` 段，含一个可复制 ```text``` 代码块，专门用于生成该镜台词的配音 MP3。字段：`角色 / 音色(锁定·全剧复用 voice_id) / 情绪 / 语速 / 类型(在画对白·画外音对白·内心独白OS·默剧) / 台词(纯文本) / 时长目标`。台词文本与情绪/角色从既有 `台词 / 字幕:` 行 + 角色 bible 声线派生；阿拉伯数字改口语中文（5→五）。默剧/静默镜标「无台词」并注明属 SFX 的环境音。
   - **音色一致性**：同一角色全剧复用同一 voice_id，不同镜只改情绪/语速、不换音色（听觉一致性，对应视觉一致性圣经的音频版）。陈凡装废态/已褪态/内心OS 同一音色三种处理。
2. **新增工具 `tools/mux_av.py`**：把 video MP4 + 台词 MP3 +（可选）BGM MP3 合成一条 MP4。默认丢弃视频自带的自动 TTS 音轨；BGM 可调增益并可 sidechain 闪避（duck）让位人声；输出视频流 copy 不重编码。

## 已知 tradeoff（capture）

- 新 section 不进 rule 12.4 通用模板（项目级决定）→ 若日后经 webapp/stage-6 **regen 重生成 shot**，该 section 会因不在模板内而丢失。需要长期保留时再决定是否升级为通用 schema（即此前 deferred 的 v2 音频启用）。

## routing hint

target_stage: 6
target_artifacts:
  - episodes/ep01/shots/shotNN/shotNN.md (全 28)
severity: medium
