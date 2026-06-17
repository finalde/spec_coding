# Raw prompt — bgm_library

在 ai video 里加一个新模块：背景音乐（BGM）。将来根据不同的剧和场景放背景音乐，需要一个 AI 自动生成背景音乐的库。

要求（对话澄清后）：

1. 库是**共享的**，独立的背景音乐库模块，在 UI 上也显示。
2. 按不同**类型**给背景音乐分类；每一类下有多个子目录，子目录里有 prompt 或 spec，也有 prompt 对应生成的背景音乐。
3. 每个背景音乐都有 **unique id**，方便不同剧本 reference —— 就像演员一样。
4. 生成后端：**MusicGen 自托管**（开源、零调用费、权重可商用）。
5. 推进方式：走 `/agent_team` 正式 spec 流程。

模板参照（现有演员库 `ai_videos/_actors/`）：
- 库：`ai_videos/_actors/actor_NNNN/actor_NNNN.md`（元数据表 + 生成 prompt），全局唯一 id。
- webapp DDD 切片：`actor__route / __query / __command / __writer / __chinese_prompt / __dto / __repository / __valueobject / __mapper`。
- `assignments` 机制：查「哪几部剧引用了这个 actor」。
- UI：演员网格 + `CastingView.tsx`。
