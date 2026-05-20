# Follow-up draft 022 — 2026-05-17
Apply the new 15s character-reference casting-reel schema (cross-cutting rule `.claude/agent_refs/project/ai_video.md` rule #12.5 v5 → v6, originated from ai_video_management follow-up 088) to all 10 mozun_chongsheng character files. Each character's 3 existing `标志台词` lines from the bible become the dialogue for slots 3-5s / 5-8s / 11-13s; closing tag at 13-15s pulls the most-defining catch phrase per `配音参考`.

## Why

- 4s casting reference was too tight to read voice/emotion range or visualize the character from multiple angles. 15s budget matches scene reference (rule #12.10 v3 walk-through) so character + scene refs are dim-comparable on Seedance uploads.
- The 0-2s self-sufficient contract (rule #12.5 v5, from follow-up 019) is **preserved** — ai_video_management's `_CONCAT_SEGMENT_S = 2.0` shot-char concat trim + `✂ 截到 2s` button continue to slice 0-2s, which still contains 一 + 二 + 正面 360° byte-identical across all 10 characters. Nothing downstream breaks.
- The 2-15s extension uses each character's own `标志台词` from the bible — so e.g. 沧冥 says "当年你们怎么对我，今日我便十倍奉还。" / "本尊从不解释，只清算。" / "无情无怒，才是最大威压。"; 司空玄 says his own 3 lines from his bible; etc. Gives Seedance a real per-character voice timbre + emotional reading reference, not just `一/二/三` baseline.

## Per-character dialogue mapping (from each character's bible)

| Char | 3-5s (台词 #1) | 5-8s (台词 #2) | 11-13s (台词 #3) | 13-15s (catch-phrase close) |
|---|---|---|---|---|
| c1_沧冥 | 当年你们怎么对我，今日我便十倍奉还。 | 本尊从不解释，只清算。 | 无情无怒，才是最大威压。 | 本尊从不解释，只清算。 |
| c2_叶无尘 | (pull from c2_叶无尘.md "标志台词" §) | (idem #2) | (idem #3) | (most-defining of the 3) |
| c3_苏璃月 | (pull from c3_苏璃月.md) | (idem #2) | (idem #3) | (catch) |
| c4_柳红袖 | (pull from c4_柳红袖.md) | (idem #2) | (idem #3) | (catch) |
| c5_苓夭夭 | (pull from c5_苓夭夭.md) | (idem #2) | (idem #3) | (catch) |
| c6_白月清 | (pull from c6_白月清.md) | (idem #2) | (idem #3) | (catch) |
| c7_赵焚天 | (pull from c7_赵焚天.md) | (idem #2) | (idem #3) | (catch) |
| c8_方鼎元 | (pull from c8_方鼎元.md) | (idem #2) | (idem #3) | (catch) |
| c9_韩夺心 | (pull from c9_韩夺心.md) | (idem #2) | (idem #3) | (catch) |
| c10_司空玄 | 你前世并非全清白。 | 道在何处？道在阴影里。 | 本座只是看着。 | 本座只是看着。 |

For each character, when the patch script runs, it reads the file's `## 标志台词或口头禅` section, takes the first 3 bullet items verbatim, maps to slots #1/#2/#3, then picks the shortest one (or the one mentioned in `## 配音参考` as "标志声线" anchor) as the 13-15s catch.

## Per-file changes (10 files)

For each of `ai_videos/mozun_chongsheng/characters/c{1..10}_*/c{N}_*.md`:

1. **Title line** — `(4s turntable + 一, 二, 三 数字计数台词)` → `(15s casting reel + 0-2s 一/二 lock + 13s character dialogue)`.
2. **文件说明** line — `**4s 硬上限 — Seedance reference 上传约束 v5；前 2s 自包含**` → `**15s casting reel — Seedance reference 上传约束 v6；前 2s 自包含（一/二）byte-identical truncate-compat**`.
3. **动作 timed-beats block** — replace 4-segment block with 7-segment block:
   - 0-1s: 正面**全身远景**起手，{角色姿态}；说"一"。
   - 1-2s: 镜头**快速 360°**...；说"二"。**必须在 2.0s 前完成发声 + 回正到正面**。
   - 2-3s: 镜头**推**至面部中近景特写；说"三, 我是 {本角色姓名}"。
   - 3-5s: 面部定格 1s + **反向慢速 90° 环绕**；角色说: `{标志台词#1}`.
   - 5-8s: 拉远至 **3/4 全身侧像**（左侧 45°）；角色说: `{标志台词#2}`.
   - 8-11s: **横向 pan** 经背面 → 右侧 90° → 右侧 45°; 角色无台词, 仅**表情 range**（中性 → 微笑 → 严肃 → 凝视）。
   - 11-13s: 镜头回正 + **拉近至胸像 medium close-up**（含 双手手势 + 标志道具）; 角色说: `{标志台词#3}`.
   - 13-15s: 镜头**推至特写**（眼神直视镜头, 标志特征点 row #11 占满下半画面）; 角色说: `{catch-phrase 收尾}`; 定格 0.5s 结束。
4. **台词 / 字幕 block** — replace the 3-row "一 / 二 / 三 (3-4s 静止)" enumeration with 7-row enumeration matching the new beats. Header note becomes: `**前 2s 必须包含 "一" + "二" 的完整发音**（下游 2s 截取契约）; 2-15s 为本角色专属 casting reel, 台词从本文件 ## 标志台词或口头禅 段三句逐字复制 + 最 character-defining 一句 13-15s 收尾。`
5. **节奏 line** — `较快（4s 内完成 全身定场 + 360° 环绕 + 面部推近 + 1s 特写定格 ...）` → `分段（15s 内: 0-2s 极速定场 + 360°锁定 truncate-compat / 2-15s 较慢 casting reel 完整呈现 voice + emotion + 6-direction silhouette + 标志特征点 final lock；前 2s 必须 self-sufficient）`.
6. **时长** — `4s` → `15s`.
7. **负向** — drop `不要 超过 4s（reference 上传硬上限 v5）`, append 5 new (v6 set per follow-up 088).
8. **Bottom 配音对照表** — replace 4-row table with 7-row table:
   - 1 | 一 | 起声 / 声线 timbre 锚点 | 0-1s | 平稳 / 中音
   - 2 | 二 | 中段 / 节奏校准（**2s 前结束**） | 1-2s | 平稳 / 中音
   - 3 | 三 + 自报姓名 | 落声 / 自我识别 | 2-3s | 平稳 / 中音
   - 4 | `{标志台词#1}` | 标准声线 baseline | 3-5s | character-specific（per bible 配音参考）
   - 5 | `{标志台词#2}` | 情绪切换 1 | 5-8s | character-specific
   - 6 | — | 表情 range (无台词) | 8-11s | silent capture
   - 7 | `{标志台词#3}` | 情绪 peak | 11-13s | character-specific
   - 8 | `{catch close}` | 终极 catch-phrase + 标志特征点 final lock | 13-15s | character-specific
9. **底部说明段** — drop the `4s 内做不到 5 句多情绪样片` 文字, replace with: `15s casting reel 容纳 6 个 camera moves + 4 句角色台词 + 1 段表情 range, 前 2s 仍 truncate-compat。台词跨角色不再 byte-identical — 每角色用自己 bible 中的 标志台词 三句, Seedance 抓 voice timbre 时按角色 baseline 还原。`

## Touch list

- 10 character md files patched per spec above.
- `specs/ai_video/mozun_chongsheng/changelog.md` — append entry.
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump.

## Out of scope

- Existing rendered `*.mp4` artifacts. User re-renders at their discretion using the new 15s prompt.
- Scene references (rule #12.10 v3) — separate pipeline, unchanged.
- Shot prompts under `episodes/ep{NN}/prompts/shotNN/` — only reference `{ref_cN_xxx}` placeholder, no embedded duration text.
- ai_video_management webapp code — no change; 2s concat trim path still works on the new 15s sources (slices 0-2s).
