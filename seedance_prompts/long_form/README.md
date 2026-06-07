# 長視頻工作流（1 分鐘+，多段提示 + 多 mp4 拼接）

Seedance 單次生成上限約 **2–12 秒**（時長由模型按提示複雜度自動決定）。要做 15 秒以上、甚至 1 分鐘+ 的片子，業界做法是：**寫一份分鏡腳本 → 逐段生成多個 clip → 保持連貫 → 後期把多個 mp4 拼接**。

## 三種主流做法

### 1. Anchor-and-Extend（錨定 + 延伸）
最常用、連貫性最好的做法：
1. **生成錨定鏡頭**：先做最關鍵的主鏡頭（master shot），用參考圖/參考影片鎖定光線和運動質感，5–10 秒。
2. **用末幀延伸**：不要每段都從零寫新提示，而是**取上一段的最後一幀當下一段的參考圖**（image-to-video chaining / 末幀接首幀），讓環境與角色延續。Seedance 2.0 的 video extension 功能可以無限次延伸，每次再加 4–15 秒。
3. **用參考影片控剪輯風格**：上傳一段示範影片（快剪、運鏡），AI 會把那種電影感套到你的角色與場景上。

### 2. Timeline Prompting（時間軸提示法）
在**單一提示**裡用時間戳分段，讓模型在一個 clip 內自動切多個鏡頭（適合做 8–12 秒內的小段落，再把多個段落拼起來）。四層結構：
- **時間戳**：`[0s]` `[3s]` `[6s]` `[8s]` 標記事件發生時機
- **鏡頭類型**：wide shot / medium shot / close-up / extreme close-up / over-the-shoulder
- **鏡頭運動**：dolly in/out、pan、tilt、tracking、rack focus、crane/jib
- **場景描述**：主體動作、光線、色彩、氛圍

範例見 [timeline_prompting.md](timeline_prompting.md)。

### 3. Multi-Shot Labeling（多鏡頭標籤法）
在單一提示裡用 `[Shot 1: ...]` `[Cut to: ...]` `[Dissolve to: ...]` 標記最多約 5 個鏡頭，模型保持風格與角色連貫。配合 `@Character1`、`@ProductRef` 這種參考標籤鎖定主體。範例見 [multishot_sequences.md](multishot_sequences.md)。

## GitHub 真實案例（一段提示 → 一段視頻，自己拼）

`github_examples/` 收錄別人在 GitHub 公開的、把長片拆成多段獨立提示的完整範例：

- [desert_kali_60s.md](github_examples/desert_kali_60s.md) — **60 秒拆 4 段 × 15s**，每段一個獨立提示生一個 clip，最後硬切拼接（最貼近你要的玩法）。
- [micro_dramas_15s.md](github_examples/micro_dramas_15s.md) — 三集短劇（霸總/校花/閨蜜），每集 15s 拆 4 個鏡頭塊。
- [cat_revenge_15s.md](github_examples/cat_revenge_15s.md) — 白貓復仇短劇，15s 拆 5 段敘事。
- [extension_chaining_template.md](github_examples/extension_chaining_template.md) — `@视频1` 延伸接續模板 + 交接幀三原則。

## 角色 / 場景連貫性（跨 clip 不變臉）

- 用清晰的**參考圖**，每段提示重複同一份「角色聖經」（character bible）——固定描述臉、髮、服裝。
- 加**負面提示**：`no different person, no face morphing, no age change`。
- 末幀接首幀：把已通過的 clip 末幀抽出來當下段參考圖，是跨場景最強連貫手段。
- 臉一直漂移就**降低場景複雜度**。
- 核心原則：**模型只生成你錨定它的東西**——鏈接（chaining）比模型本身更重要。

## 音畫同步（多段共用一條音軌）

上傳一條連續的 15 秒音軌，分別生成 wide / medium / close-up 各鏡頭時，AI 會把每段的視覺動作同步到同一條主音軌，後期拼接時動作就對得上拍子。

## 後期拼接 mp4

生成時導出 **2K 原生解析度**，再進剪輯軟體（DaVinci Resolve / Premiere）做調色與字幕；
或用 ffmpeg 命令列直接拼，見 [concat_ffmpeg.md](concat_ffmpeg.md)。

## 完整實作流程（建議照這個跑）

1. 先在工具外**寫好完整 shot list**：每個鏡頭一行——鏡號、場景環境、角色參考標籤、背景板標籤、運鏡、約略時長。
2. 生成**錨定鏡頭**，反覆調到滿意。
3. 抽末幀 → 當下一鏡參考圖 → 生成下一段；逐段推進。
4. 弱鏡頭**單獨重修**，不要整段重跑。
5. 全部 clip 落地後，按 [concat_ffmpeg.md](concat_ffmpeg.md) 拼接成成片。

## 來源

- [MindStudio — Timeline Prompting](https://www.mindstudio.ai/blog/timeline-prompting-seedance-2-cinematic-ai-video)
- [Vmake — 10 Advanced Multi-Shot Prompts](https://vmake.ai/blog/seedance-2-0-prompts)
- [OpsMatters — Multi-Shot Storytelling Guide](https://opsmatters.com/posts/concept-screen-pros-guide-multi-shot-storytelling-seedance-20)
- [OpusClip — Extend & Edit Existing Videos](https://www.opus.pro/blog/extend-edit-existing-videos-seedance)
- [Seedance — Character Consistency Guide](https://www.seedance.tv/blog/seedance-character-consistency-guide-2026)
- [Cutout.pro — Storyboard Workflow](https://www.cutout.pro/learn/blog-seedance-2-0-storyboard-workflow-cutout-frames/)
- [VIDEOAI.ME — Seedance 2.0 Max Duration](https://videoai.me/blog/seedance-2-0-duration)
