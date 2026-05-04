# Findings dossier — wukong_juexing

Run: wukong_juexing-20260503-201831
Stage: 3 (research)
Researchers: 5 parallel angle workers, all returned

## Angles researched

1. **story-structure** — confirm hook→escalation→loop arc against real comparable AI cinematic shorts; lock per-shot beat cadence
2. **character-design-and-ref** — locked Chinese descriptor for 孙悟空 + Seedream立绘 prompt structure
3. **visual-style** — locked palette (named + hex), lighting / motion / transition vocabulary
4. **platform-conventions** — YouTube Shorts publish skeleton + length-window math + cross-publish notes
5. **kling-seedance-spec** — current capabilities, length caps, prompt schema, worked Shot 02 example pair

## Cross-cutting insights

- **Shot 01 IS the thumbnail.** YouTube Shorts feed pulls an auto-frame thumbnail; R04 surfaced this as a derived requirement. R01 separately found the burst-peak should land at t≈2s. These converge: **the golden-light-burst peak frame at t≈2s of Shot 01 must be a self-contained, on-model, recognition-grade thumbnail** — composition, color, legibility all evaluated at that single still. *(platform-conventions + story-structure)*

- **10s dual-tool clip cap reshapes the budget but doesn't break it.** R05 caught that Kling 2.1 Pro caps at 10s and Seedance 1.0 Pro at 12s — binding cap for dual-tool shots is 10s, well below the harness's ≤15s ceiling. R04 independently tightened the runtime target to 38s ±4s. Together they map cleanly onto a 5-shot decomposition averaging ~7.6s/shot, with the longest shot at 10s and the shortest at ~5s. *(kling-seedance-spec + platform-conventions)*

- **Negative-prompt asymmetry forces a dual-template split, not just a dual-prompt rendering.** R05 found Kling accepts `negative_prompt:`, Seedance ignores it. R02's locked descriptor includes a禁用 list (no 戏曲妆, no Q-style, no cel-shading, no 86版西游记). Stage 4 must split: Kling shot files put the禁用 list in `negative_prompt:` field; Seedance shot files rephrase as positive `约束: ... 而非 ...` constraint at the prompt tail. *(kling-seedance-spec + character-design-and-ref)*

- **The 紫金 vs 黄金 ambiguity in the descriptor resolves through the palette.** R02 flagged "紫金 vs 黄金 hex anchors" as an open question for the headpiece + armor. R03's locked palette anchors warm gold to `#F2A65A`. Resolution: armor + 金箍棒 = 暖金 (`#F2A65A`); 凤翅紫金冠 stays a literary descriptor — the headpiece itself reads as 暖金 with cool reflective highlights, not literally purple. Stage 4 should standardize this in the character descriptor. *(character-design-and-ref + visual-style)*

- **Loop-back must be byte-identical framing, lighting state inverted.** R01's strongest single recommendation. R03's transitions catalog already includes "match cut" as transition rule for shot 04→05 — extend the principle: Shot 05's final frame is the same composition as Shot 01 frame 0, with the gold-light-burst state replaced by gold-light-fading. This is the strongest loop mechanic R01 found in the data. *(story-structure + visual-style)*

## Per-angle highlights

### story-structure

- The drafted **hook (≤2.5s) → escalation (shots 02–04) → visual-loop ending** shape is the dominant 2025–2026 retention pattern, not one option among several. Both the 2–3s hook window and the visual-loop mechanic are explicitly weighted by the algorithm.
- Real comparable AI cinematic productions: **《霍去病》** (~4 min, 3-person AI cinematic about a young Chinese hero, viral per Xinhua) — same hook→escalation→hero-payoff shape. **《斩仙台下，我震惊了诸神》** (1B Douyin views per RecodeChinaAI) — validates Journey-to-the-West / Wukong universe is actively performing at scale on Chinese vertical-video.
- **No verified single-character AI cinematic Wukong YouTube Short found in 2025–2026 search** — first-mover gap, not saturated niche.
- Action items: (a) burst-peak at t≈2s wall-clock, not shot midpoint; (b) every shot needs distinct opening + closing states for 5–7s perceived beats; (c) byte-identical loop framing.

### character-design-and-ref

- **Locked Chinese descriptor v1** (battle-worn warrior, *Black Myth* register, 凤翅紫金冠 + 锁子黄金甲 + 金箍棒, sinewy 灵长类 build, 紫金 + 暗朱红 + 焦褐 palette base, with explicit禁用 list). Byte-paste-ready into `characters/main.md` AND every shot prompt that names him. — see `findings/angle-character-design-and-ref.md` §3.
- 10 real reference URLs spanning Black Myth: Wukong main entries, 凤翅紫金冠 specifics (BWIKI, 百度百科), the 大圣残躯 CG report (closest "four-element-in-frame" match), plus 86版西游记 as a negative anchor.
- 10-section Seedream立绘 prompt template (主体/面貌/发型+冠/服装/身材+姿态/道具/画面控制/风格质感/比例/负向); target 250–400 字; one full worked example for a 神话/武侠 archetype (赵云银甲将军立绘) demonstrating the structure.
- Open questions surfaced: 紫调 clarifier (cross-cut RESOLVED), 破壳态 second ref (judgment call below: NO, keep one ref), 金箍棒 length lock (deferred to stage 4), 紫金 vs 黄金 hex (cross-cut RESOLVED).

### visual-style

- **Locked palette** (paste-ready into `style_guide.md`):
  - 主色 暖金 `#F2A65A`, 暮霞朱红 `#9B2D20`
  - 阴影 深石青 `#2E5C6E`, 暮紫 `#3A2A55`
  - 高光 星白 `#E8E6D9`
  - Sourced from Black Myth: Wukong's Yellow Wind Ridge dusk segments + Fox Render Farm "cold-bg + warm-rim-light" analysis. Fits stage-2 locked mountaintop-dusk-starry-sky setting.
- **6 lighting-state tokens** (Chinese, paste-ready): 暮色魔幻时刻顶光 / 星空环境光 / 金色边缘逆光 / 点状装饰光 / 体积光丁达尔束 / 冷蓝补光.
- **5 motion patterns**: slow dolly-in / wide reveal pan / 180° arc / handheld micro-sway / vertical crane-up.
- **3 transition rules**: hard cut default; gold flash for shot 01→02 hinge; match cut for shot 04→05.
- All 5 shots mapped to specific style elements in the angle file.
- Open questions: staff-glow mechanic (deferred), fur color (judgment-call resolved below), star density (deferred), white-flash AI controllability (deferred — split per-tool resolution).

### platform-conventions

- **Length tightened to 38s ±4s (34–42s effective band)** — 35–55s upper bound was too generous for a no-dialogue, no-text-overlay piece. 2026 cinematic-narrative Shorts sweet spot is 25–45s.
- **`publish.md` skeleton** (Chinese, paste-ready):
  - 标题 ≤30 中文字; no hashtags in title; 用问句 / 数字 / 反差词开头.
  - 简介 150–250 中文字; first sentence is the hook; **3–5 hashtags total in description, `#Shorts` mandatory; total title+description hashtags >15 = YouTube treats as zero**; first 3 description hashtags auto-render as clickable links above title.
  - 自定义封面 1080×1920 ≤2MB matters only for non-feed surfaces — Shorts feed uses auto-frame ⇒ derived requirement: Shot 01 t≈2s frame must itself be a valid thumbnail.
  - 发布时段 周四/周五 19:00–21:00 北京时间 for Chinese-content audience.
- **Cross-publish to 抖音 / 视频号 = optional appendix**, not v1 scope. Same Chinese metadata copy-pastes to 抖音 with `#Shorts` → `#抖音原创`. 视频号 needs `#tag` → `#话题#` conversion + separate custom cover.
- Open questions: 黑神话 IP-tag inclusion (judgment-call resolved below: NO for v1); hook text overlay policy (LOCKED out per revised prompt — keep it that way); English-language variant (deferred — flagged in stage-2 cross-publish note); separate cover-still Seedream prompt (judgment-call resolved below: NO — Shot 01 frame doubles).

### kling-seedance-spec

- **Capability spec is tighter than harness assumes:**
  - Kling 2.1 Pro caps at **10s** per clip (`duration` enum `5|10`).
  - Seedance 1.0 Pro caps at **12s** (`duration` enum `2..12`).
  - Binding cap for dual-tool shots = **10s**.
- **Negative-prompt asymmetry** (load-bearing):
  - Kling 2.1 Pro accepts `negative_prompt`.
  - Seedance 1.0 Pro/Lite **ignores** negative prompts; official guidance is "state what you do want."
  - Stage 4 must split per-shot files accordingly.
- **9:16, Chinese prompts, shared motion vocabulary all work cleanly on both tools.** Both honor 推/拉/摇/移/跟/升降/环绕/俯/仰 and standard 景别 (远景/全景/中景/近景/特写) vocabulary.
- `agent_refs/project/ai_video.md` rule #4 template maps **1:1** onto Kling's official six-component skeleton — no template rewrite needed.
- **Worked Shot 02 example pair** (Kling block + Seedance block, paste-ready Chinese) lives in the angle file §4 — stage 4 inherits as the template applied to all 5 shots.
- Open questions: none new.

## Recommendations for the spec (stage 4 must honor)

1. **Length budget — locked at 38s ±4s.** Per-shot allocation (proposed; stage 4 may rebalance ±1s):
   - Shot 01 (hook — cracking stone, golden burst): **~5s** — burst peak frame at t=2s
   - Shot 02 (mountaintop wide reveal of Wukong): **~8s**
   - Shot 03 (transformation / 金箍棒 summon): **~8s**
   - Shot 04 (cloud ascend / power-pose against starry sky): **~10s** (pushing the dual-tool cap intentionally for the climax)
   - Shot 05 (loop-back to cracking-stone callback, gold-light fading): **~7s**
   - **Total: 38s.**

2. **Replace harness's "≤15s/shot" with effective "≤10s for dual-tool" in `final_specs/spec.md`.** All 5 shots stay ≤10s in practice. Document the harness ceiling vs. effective cap explicitly so a future regen knows why no shot exceeds 10s.

3. **Shot 01 thumbnail requirement (explicit FR).** The frame at t≈2s of Shot 01 (burst peak) must be a self-contained, on-model, recognition-grade thumbnail (visually arresting, 孙悟空 elements legible if any visible, palette-compliant). This is the auto-frame Shorts cover.

4. **Loop-back is byte-identical framing.** Shot 05 final frame = Shot 01 frame 0 composition, with the only delta being the lighting state (gold-light-fading vs gold-light-bursting). This is non-negotiable per R01's data.

5. **Dual-template per shot (Kling vs Seedance file split):**
   - Kling shot file: includes `negative_prompt: 戏曲妆, Q版, cel-shading, 86版西游记, 卡通比例, 童颜...` field.
   - Seedance shot file: rephrases the禁用 list as a positive `约束: 写实质感, 成人比例, 灰头土脸, 不带卡通线条...` tail.
   - Both share the same locked Chinese descriptor for 孙悟空 byte-identically.

6. **Character descriptor: inherit R02's locked block verbatim into `characters/main.md`.** Do NOT regenerate at stage 4. Apply the cross-cut resolution: 凤翅紫金冠 + 锁子黄金甲 + 金箍棒 are all 暖金 `#F2A65A` palette-anchored; the literary 紫金 descriptor is preserved but explicitly clarified as "warm gold reading."

7. **Style guide: inherit R03's palette + 6 lighting tokens + 5 motion patterns + 3 transition rules verbatim into `style_guide.md`.**

8. **Publish.md: inherit R04's skeleton verbatim.** Apply judgment calls below for IP-tag and cover-still resolution.

9. **One Seedream立绘 reference image only** (`ref_images/main_seedream.md`). *(judgment call — chose ONE ref because: a second "破壳态" ref doubles ref-image budget for marginal gain; Kling can text-prompt the破壳态 moment from the locked descriptor in Shot 01; first-project simplicity is more valuable than perfectionist character lock for the hook beat.)*

10. **No 黑神话 / #BlackMythWukong tag in v1.** *(judgment call — chose NO because: piggybacking on the active IP tag risks YouTube's "low-quality AI mass-content" classifier flagging the upload, especially as a first-channel post; ride the cultural tailwind through visual register and IP recognition, not through tag co-option. Reconsider in v2 if channel reputation is established.)*

11. **No separate cover-still Seedream prompt for v1.** *(judgment call — chose NO because: Shot 01's t≈2s burst-peak frame doubles as both the YouTube Shorts auto-frame thumbnail AND a paste-able cover for 视频号 if the user ever cross-publishes. Adds zero spec complexity; defers the visual decision to the Kling/Seedance generation stage where it can be visually verified.)*

12. **Hook text overlay stays out** per revised prompt's hard exclusion. Confirmed against R04's finding that text overlays are a known retention booster — the trade-off is conscious: visually-pure cinematic register over micro-retention bump.

## Open questions surviving research (deferred to stage 4 or beyond)

| # | Question | Surfaced by | Deferred to |
|---|---|---|---|
| Q1 | 金箍棒 length lock — 人高 / 战斗长度 / 顶天? | character-design-and-ref | stage 4 (lock in character descriptor) |
| Q2 | 金箍棒 self-glow vs reflective only? | visual-style | stage 4 (lock per-shot in shotlist) |
| Q3 | Wukong fur color — naturalistic 棕褐 vs stylized 金棕? | visual-style | **judgment call: 棕褐 naturalistic** to align with *Black Myth*'s grounded register; stage 4 confirms in descriptor |
| Q4 | Star density in starry-sky shots — sparse cinematic vs dense fantasy? | visual-style | stage 4 (lock in style_guide.md) |
| Q5 | White-flash transition AI controllability across Kling/Seedance? | visual-style | **judgment call: omit white flash for v1**; rely on hard cut + gold-rim residual; stage 4 documents this |
| Q6 | English-language YouTube Shorts variant of publish.md? | platform-conventions | deferred — explicit follow-up if user wants it post-v1 |

Q3 and Q5 are pre-resolved here as judgment calls so stage 4 doesn't have to re-derive. Q1, Q2, Q4 land in stage 4. Q6 is post-v1.
