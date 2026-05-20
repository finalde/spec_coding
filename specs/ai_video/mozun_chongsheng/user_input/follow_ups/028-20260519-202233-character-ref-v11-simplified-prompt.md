# Follow-up draft 028 — 2026-05-19
Apply the new v11 plain-Chinese simplified prompt (cross-cutting rule `.claude/agent_refs/project/ai_video.md` rule #12.5 v10.2 → v11, originated from ai_video_management follow-up 099) to all 10 mozun_chongsheng character files. Supersedes 027 (v10.2 patch, applied this same day morning) — user empirical test of v10.2 renders showed motion delayed to ~5s because the prompt described camera motion in 4 redundant fields with technical jargon.

## Why

User report this turn after rendering v10.2 character mp4s:
> "the camera did not move as you intended in the charactor prompt, I think kling got confused, you need to tell it in a more simple way and only once in the prompt. currently the it shart to turn around to side view at only about 5s."

v10.2 schedule was correct (3 static landings + 2 motion bridges) but the prompt described motion redundantly in 4 fields: 镜头 (5-phase enumeration), 动作 (5 beats each repeating phase), 节奏 (path repetition), 负向 (14 items with qualifier paragraphs). Model averaged across the conflicting descriptions and under-committed to motion. Result: motion delayed by ~3s.

v11 fix: same 5-phase schedule, same `CANONICAL_VIEWS` timestamps, but motion described ONCE in 动作 timed beats using plain Chinese. 镜头 = framing/lens only. 节奏 = one sentence. 负向 = 10 simple bans. 锁定机位 jargon removed (model interprets "锁定" as "全程不要动").

## Per-character dialogue (slots #3 + #4 + #5 — preserved unchanged across v8 / v10 / v10.2 / v11)

| Char | Slot 3 = "三, 我是 {NAME}" (2-3s) | Slot 4 = 标志台词 #1 (3-5s) | Slot 5 = 标志台词 #2 (5-7s) |
|---|---|---|---|
| c1_沧冥 | 三, 我是 沧冥 | 当年你们怎么对我，今日我便十倍奉还 | 本尊从不解释，只清算 |
| c2_叶无尘 | 三, 我是 叶无尘 | 进来吧，喝口热汤——我记着 | 叮——任务发布 |
| c3_苏璃月 | 三, 我是 苏璃月 | 若道不在此处，此剑便指此处 | 我拜的不是宫，是道 |
| c4_柳红袖 | 三, 我是 柳红袖 | 进来吧，喝口热汤 | 酒坛比仙气重要 |
| c5_苓夭夭 | 三, 我是 苓夭夭 | 脉里有古伤，不是凡人能受的 | 丹入腹，命在天 |
| c6_白月清 | 三, 我是 白月清 | 璃月，为师所行皆为道 | 天道无亲，惟修者自度 |
| c7_赵焚天 | 三, 我是 赵焚天 | 好兵器，要凡人血淬 | 天下第一铸 |
| c8_方鼎元 | 三, 我是 方鼎元 | 魔孽休得猖狂 | 正道一统，方为天下之福 |
| c9_韩夺心 | 三, 我是 韩夺心 | 剑下无情 | 夺宝灭门，亦是行义 |
| c10_司空玄 | 三, 我是 司空玄 | 你前世并非全清白 | 道在何处？道在阴影里 |

## Per-file mechanical changes (10 files, applied via two-script sequence)

**Script 1**: `C:/Users/light/AppData/Local/Temp/patch_chars_v11.py` — 12 substitutions per file:
- 10 fixed-string: 文件说明 / h1 heading / bottom table heading / 3 table 用途 rows / 场景 line / 镜头 line / 节奏 line / 渲染样式 (skipped — character-specific) / 负向 v10.2 video-block → v11 simplified block.
- 2 regex (multi-line with capture groups preserving character-specific content): 动作 6-line block (regex preserves character name + 标志台词 #1 #2 via 3 named capture groups) / 台词 / 字幕 5-line enumeration block.

**Script 2**: `C:/Users/light/AppData/Local/Temp/patch_chars_v11_fix.py` — corrective patch for 2 patterns script 1 missed:
- Title line in code block: script 1's regex assumed wording from the rule template, but the actual character files had different post-h1 wording. Fixed regex applied to all 10.
- 光线 / 色调 line: script 1's regex expected a `**轮廓光 + key 在 orbit 全程保持稳定**` tail that doesn't exist in files. Fixed regex applied to 7 (c2_叶无尘, c4_柳红袖, c5_苓夭夭 don't have character-specific 光晕 segment so the regex doesn't match for them — left as v10.2 wording; cosmetic difference only, not load-bearing).

### Per-line transformation summary

1. **文件说明 line**: v10.2 verbose `7s locked-framing 5-phase single-take ... 3 static landings + 2 motion bridges / 慢速 + 单方向 / 锁定 framing` → v11 plain-Chinese `7s 单 take, 镜头 0-2s 拍正面 + 2-3s 顺时针绕到左侧身 + 3-4s 停侧身 + 4-5s 顺时针绕到背面 + 5-7s 停背面 — Kling reference 上传约束 v11 (simplified prompt — camera motion 仅在 动作 timed beats 一次描述, plain Chinese)`.
2. **h1 heading**: v10.2 `7s locked-framing 5-phase single-take + 0-2s 一/二 lock + static landings at 0°/90°/180°` → v11 `7s 单 take, 镜头依次拍正面 → 左侧身 → 背面, plain Chinese v11`.
3. **Prompt title (in code block)**: v10.2 `{NAME} · {ROLE} — 角色 reference 5-phase locked-framing single-take（7s locked-framing + ...）` → v11 `{NAME} · {ROLE} — 角色 reference 7s 单 take`. Regex preserves NAME · ROLE.
4. **场景 line**: drop `环境光均匀` (redundant) — `中性灰 #808080 摄影棚 cyc wall 无缝背景, 地面同灰, 无家具`.
5. **镜头 line**: v10.2 5-phase enumeration with motion path → v11 framing/lens only: `单 take 7s, 9:16 竖屏, medium-full ~40mm framing 全程不变 (头部约画面高度 1/5, 头顶到脚趾完整入画, 双脚距画面底缘约 5% 安全余量, 相机距角色距离不变 no dolly no zoom)`.
6. **动作 6-line block**: v10.2 6 beats (0-1s / 1-2s / 2-3s / 3-4s / 4-5s / 5-7s) with "锁定机位 / motion bridge / static lock" jargon → v11 5 beats (0-2s combines 0-1 + 1-2 into one beat / 2-3s / 3-4s / 4-5s / 5-7s) in plain Chinese:
   - `0-2s: 镜头正面拍角色 medium-full. 角色站定, 自然呼吸, 眼神看镜, 说"一", "二". **必须在 2.0s 前说完**.`
   - `2-3s: 镜头围绕角色顺时针绕 90° 到角色左侧身. 角色保持站立不动只呼吸.`
   - `3-4s: 镜头停在左侧身角度不动. 角色说"三, 我是 {NAME}".`
   - `4-5s: 镜头继续顺时针绕 90° 到角色背面. 角色保持站立不动只呼吸.`
   - `5-7s: 镜头停在背面角度不动. 角色说: "{TAG1}", 然后说: "{TAG2}"; 自然定格收尾.`
   - Note: slot 4 (标志台词 #1) now appears ONCE in the 5-7s beat (combined with slot 5), simpler than v10.2's split-across-3-beats (3-4s 起声 + 4-5s 续声/落声 + 5-7s slot 5 separately).
7. **台词 / 字幕 enumeration**: v10.2 verbose with parenthetical timbre/baseline notes → v11 compact:
   - `1. "一" (0-1s)`
   - `2. "二" (1-2s, **2s 前结束**)`
   - `3. "三, 我是 {NAME}" (2-3s, 自我识别 + 镜头转向侧身)`
   - `4. "{TAG1}" (3-5s, 标准声线 baseline, over 左侧身 hold + 转到背面)`
   - `5. "{TAG2}" (5-7s, 情绪 peak + final lock, over 背面 settle)`
8. **光线 / 色调 line**: v10.2 verbose `三点布光 — key 45° 顶左 5500K 主光 + fill 右下柔光 4500K 辅光 + back rim 顶后冷光 7000K 轮廓光；地灰 #808080 不抢主体；{aura}。影视棚拍标准布光，无戏剧化色温偏移。` → v11 compact `三点布光 — 5500K key + 4500K fill + 7000K rim; 灰背景中性; {aura}.`
9. **节奏 line**: v10.2 path-repeating line → v11 single sentence: `单 take 7s, 角色站立不动只说话, 镜头按 动作 timed beats 旋转 + 停顿.`
10. **负向 line**: v10.2 14-item with qualifier paragraphs → v11 10 simple bans: `不要 dolly / 不要 zoom / 不要 距离变化 / 不要 framing 变化 / 不要 角色转身 / 不要 角色走动 / 不要 cut / 不要 transition / 不要 fade / 不要 超过 7s`. Character-bible-specific bans at start of line + anti-AI-generic-face bans at end unchanged.
11. **Bottom table heading**: v10.2 → v11 wording matching the h1 + heading sequence.
12. **Bottom table 用途 columns** for slots 3 / 4 / 5: micro-edits matching the 台词 enumeration changes.

Untouched: 渲染样式 line (character-specific style adders are valuable, kept at v10.2 form across all characters), 比例 / 时长 / character bible (lines 1-78).

## Status of 027 (v10.2 patch)

027 (v10.2 5-phase locked-framing single-take) was applied this morning. User empirical test (same day evening) reported motion delayed to ~5s. Same-day super-pivot: 027 marked SUPERSEDED with note pointing to 028.

024 → 025 (v9, never applied) → 026 (v10, applied morning) → 027 (v10.2, applied morning+, was the v10 → v10.2 evening pivot but applied at 22:40) → 028 (v11, applied this evening). Iteration count = 5 character-ref patches in two days, of which 4 were applied to disk.

## Touch list (this follow-up)

- 10 character md files (patched via two scripts, see above).
- `specs/ai_video/mozun_chongsheng/user_input/revised_prompt.md` — header bump 028.
- `specs/ai_video/mozun_chongsheng/changelog.md` — append 028 entry.
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/028-…` — follow-up draft itself.
- `specs/ai_video/mozun_chongsheng/user_input/follow_ups/027-…` — added `SUPERSEDED by 028` tag at top.

## User-side action after this lands

1. Re-render the 10 character turntable mp4s at 7s with v11 prompt. v10 + v10.2 renders are invalidated.
2. Upload one v11 mp4 to Kling — empirical test whether the simpler prompt language fixes the timing. Hypothesis: motion described ONCE + plain Chinese will let the model trust the spec instead of averaging across 4 conflicting descriptions.
3. Click 🖼 button — check whether motion actually starts at t=2s now (not t=5s like v10.2). Expected outcome: side png at t=3.5s shows the character at clean 90° left-side angle; back png at t=6.0s shows clean 180° back.
4. If motion is still delayed past ~3s, report back — escalate to v12 (shift schedule earlier, break 0-2s truncate-compat) or v13 (multi-clip path, render 3 separate static clips + concatenate at filesystem level — most expensive but bulletproof).

## Out of scope

- ai_video_management webapp code — **no change** (CANONICAL_VIEWS unchanged; backend writer / endpoint / frontend button all consume the constants opaquely).
- Shot prompts under `episodes/ep{NN}/prompts/shotNN/` — unchanged.
- Scene reference rule #12.10 v3 — orthogonal, unchanged.
- Character bibles' `## 标志台词或口头禅` section — read-only reference, unchanged across all versions.
- 渲染样式 line in character files — character-specific style adders preserved (cinematic + 4K HDR + 真实皮肤布料质感 + 亚洲俊男靓女 + 东方传统五官 + ... + 真实皮肤微瑕); the rule's simpler `渲染样式: 影视级真人写实 + cinematic + 4K HDR + 真实皮肤布料质感.` is for new character files only.
- Existing v10.2 character mp4s rendered this morning by user — invalidated by v11. User re-renders.
