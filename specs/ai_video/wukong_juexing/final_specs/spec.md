# Final spec — wukong_juexing

Run: wukong_juexing-20260503-201831
Stage: 4 (spec compilation)
Inputs consumed: `user_input/revised_prompt.md`, `interview/qa.md`, `findings/dossier.md`, `findings/angle-character-design-and-ref.md`, `findings/angle-visual-style.md`, `findings/angle-platform-conventions.md`, `findings/angle-kling-seedance-spec.md`

## Goal

Produce a complete, paste-ready production package under `ai_videos/wukong_juexing/` for a single ~38 s vertical 9:16 YouTube Short titled 《悟空觉醒》 — a cinematic Sun Wukong transformation moment rendered in *Black Myth: Wukong*-grade "weighty mythic realism", structured as 5 shots (5 / 8 / 8 / 10 / 7 s) on a hook → escalation → loop-back arc, with each shot shipping dual prompts (Kling image-to-video + Seedance text-to-video) anchored to one locked Seedream立绘 of the character. The package is the user's first ai_video pipeline run and intentionally constrained to one character + two-setting micro-arc to validate the image-first character-lock contract end-to-end.

## Out of scope

- Multi-character scenes (any antagonist / sidekick / cast beyond 孙悟空).
- Multi-episode / serialised structure.
- Audio track, music, sound-effect prompts.
- Text overlays, dialogue, lip-sync.
- Distribution variants beyond YouTube Shorts metadata (no separate 抖音 / 视频号 / Reels publish files in v1).
- Stage-6 actual video rendering — the pipeline outputs prompts; the user runs Seedream + Kling + Seedance externally.
- English-language publish variant.
- Separate cover-still Seedream prompt — Shot 01 t≈2s burst-peak frame doubles as the auto-frame Shorts thumbnail.
- 黑神话 / `#BlackMythWukong` tag co-option in publish metadata.
- Cinematic effects requiring frame-precise control that AI generators don't reliably honour today (e.g., 0.3–0.5s white-flash transitions).

## Primary flows

The user is the sole actor — a creator running the pipeline manually:

1. **Read** `ai_videos/wukong_juexing/README.md` to understand the project.
2. **Generate the立绘** by pasting `characters/ref_images/main_seedream.md` into Seedream, save the resulting image as `ref_images/main_seedream.png` (user-side step; not a pipeline output).
3. **Render each shot** by pasting each `prompts/shotNN_kling.md` (with the saved立绘 attached as image reference) into Kling, AND each `prompts/shotNN_seedance.md` into Seedance. Per shot, pick whichever output is on-model.
4. **Assemble** the 5 chosen clips into a single 38 s ±4 s 9:16 video (external editor).
5. **Publish** to YouTube Shorts using `publish.md` for title / description / hashtags / cover guidance.

## Functional requirements

Each FR is testable. Stage-5 validation strategy will operationalise these into level-specific checks; stage-6 streaming validators will assert each FR per work-unit.

### File existence

- **FR-1** `ai_videos/wukong_juexing/README.md` exists.
- **FR-2** `characters/main.md` exists.
- **FR-3** `characters/ref_images/main_seedream.md` exists.
- **FR-4** `style_guide.md` exists.
- **FR-5** `script.md` exists.
- **FR-6** `shotlist.md` exists.
- **FR-7** All 10 prompt files exist: `prompts/shot{01..05}_kling.md` and `prompts/shot{01..05}_seedance.md`.
- **FR-8** `publish.md` exists.

### Content language + path language

- **FR-9** Every file's contents under `ai_videos/wukong_juexing/` are in Chinese (Simplified). English permitted only for technical tokens: hex codes (`#F2A65A`), aspect ratio (`9:16`), seconds (`8s`), API parameter keys (`negative_prompt:`, `cfg_scale:`, `seed:`), tool names, and shot-id slugs (`shot01_kling.md`).
- **FR-10** Every folder + file name under `ai_videos/wukong_juexing/` is English or pinyin (no Chinese-character paths).

### Character lock contract (load-bearing)

- **FR-11** `characters/main.md` contains the **locked Chinese descriptor v1** byte-identically as defined in `findings/angle-character-design-and-ref.md` §3 — block boundaries `【孙悟空 · 觉醒态 · 锁定描述符 v1】 ... 标志性动作 ... 禁用 卡通线条、cel-shading、二次元大眼、低多边形。` The `characters/main.md` file may add framing text above and below the block, but the block's bytes are immutable.
- **FR-12** Each of the 5 `prompts/shotNN_kling.md` files contains the same locked-descriptor block under its `角色:` field, byte-identically equal to the block in `characters/main.md`. Verifiable by string equality.
- **FR-13** Each of the 5 `prompts/shotNN_seedance.md` files contains the same locked-descriptor block under its `角色:` field, byte-identically equal to the block in `characters/main.md`. Verifiable by string equality.
- **FR-14** `characters/ref_images/main_seedream.md` follows the 10-section Seedream prompt structure defined in `findings/angle-character-design-and-ref.md` §4 (主体定义 / 面貌细节 / 发型+头冠 / 服装 / 身材+姿态 / 道具 / 画面控制 / 风格-质感 / 比例+输出 / 负向提示), with body length 250–400 中文字 (excluding the headers).

### Style lock contract

- **FR-15** `style_guide.md` contains the locked palette table from `findings/angle-visual-style.md` §3.1 (7 named palette entries with hex codes), the 6 lighting-state tokens from §3.3, the 5 motion-pattern tokens from §3.5, and the 3 transition rules from §3.6. Verifiable by token-presence checks.
- **FR-16** Every `prompts/shotNN_*.md` file's `光线/色调:` line uses ONLY tokens or hex codes from `style_guide.md` vocabulary. Free-form palette terms ("warm tones", "暖色调" without hex anchor) are violations.
- **FR-17** Every hex code that appears in any prompt file is one of the palette-table hexes from `style_guide.md`. Any unknown hex is a violation.

### Visual register lock

- **FR-18** Every prompt file (Kling + Seedance) carries the explicit register anchor phrase **`黑神话·悟空美术风`** (or equivalent locked Chinese phrase) in its `场景:` or `风格:` line.
- **FR-19** No prompt file contains禁用 register tokens: `卡通`, `Q版`, `cel-shading`, `二次元`, `戏曲妆`, `京剧脸谱`, `低多边形`, `86版西游记`. (For Kling these MUST appear in `negative_prompt:`; for Seedance they MUST appear in `约束:` as positive contraries — see FR-23.)

### Shot decomposition + duration

- **FR-20** `shotlist.md` enumerates exactly 5 shots. Each row contains: `shotNN` / `时长` / `景别` / `动作摘要` / `连续性 tokens` / `是否 hook 镜头`.
- **FR-21** Per-shot durations: Shot 01 = 5s, Shot 02 = 8s, Shot 03 = 8s, Shot 04 = 10s, Shot 05 = 7s. Sum = **38s** (within 38s ±4s target).
- **FR-22** Every shot's duration is **≤ 10s** (effective dual-tool cap; harness ≤ 15s ceiling is preserved as documentation).

### Dual-prompt schema (per-tool divergence)

- **FR-23** Kling shot files MUST include a `negative_prompt:` line containing the禁用 register tokens plus standard artifact guards (`多余手指, 五官畸变, 文字水印, 字幕, logo, 模糊, 鬼影, 闪烁, 现代服饰, 现代建筑, 多人出现`). Seedance shot files MUST NOT include `negative_prompt:` and MUST include a `约束:` tail expressing the same exclusions positively (e.g., `五官稳定不畸变, 同一角色全程一致, 单人画面无多余人物, 无文字水印, 无字幕, 无现代元素, 无模糊鬼影闪烁`).
- **FR-24** Kling shot files lead with a `[参考图: characters/ref_images/main_seedream.md 生成的孙悟空立绘]` line. Seedance shot files do NOT include this line (Seedance has no t2v image-ref slot).
- **FR-25** Every Seedance shot file's `动作` field is broken into per-second timeline segments (e.g., `0–2 秒: ... / 2–5 秒: ... / 5–8 秒: ...`). Kling shot files MAY use prose `动作:` (Kling does not require timeline segmentation).
- **FR-26** Every shot file (both tools) contains: `角色:`, `场景:`, `动作:`, `镜头:`, `光线/色调:`, `比例:`, `时长:`. Seedance additionally contains `风格:`, `画质:`, `约束:`, `seed:`. Kling additionally contains `negative_prompt:`.
- **FR-27** Both `比例:` lines per shot read `9:16`. Kling `时长:` ∈ {`5s`, `10s`}; Seedance `时长:` ∈ {`5s`..`12s`} matching the locked per-shot allocation in FR-21. (Shot 02/03 = 8s, Shot 04 = 10s, Shot 01 = 5s, Shot 05 = 7s. Kling can do 5s and 10s; for 7s and 8s shots that aren't on Kling's enum, Kling files round to 10s and the spec notes "render and trim, or render at 5s with motion compression". This degradation is documented; Seedance handles all five durations natively.)

### Hook + thumbnail contract

- **FR-28** `shot01_kling.md` and `shot01_seedance.md` both specify in their `动作:` field that the **fissure-burst peak frame lands at t≈2s wall-clock** (not at the shot midpoint). Kling shot file's prose says so explicitly; Seedance shot file's `0–2 秒` segment ends with the burst-peak.
- **FR-29** Shot 01's t≈2s burst-peak frame must be a self-contained valid 9:16 Shorts thumbnail: subject (cracking stone + golden-light burst) centred upper-2/3, single visual focal point, palette-compliant, recognition-grade. This is encoded as an explicit `# 缩略图契约` annotation block at the top of `shot01_kling.md` and `shot01_seedance.md` so the user re-renders if the abuse-test on the opening 2 s fails.

### Loop-back contract

- **FR-30** Shot 05 final-frame composition is **byte-identical** to Shot 01 frame 0 composition (same camera angle, same focal length, same subject framing, same prop placement). The only delta permitted is the lighting state: Shot 01 starts with `金光-bursting / 体积光丁达尔束` peak; Shot 05 ends with `金光-fading / 余烬冷尾` decay. This is encoded as an explicit `# 回环契约` annotation block at the top of `shot05_kling.md` and `shot05_seedance.md`.
- **FR-31** Shot 04 → Shot 05 transition uses `match cut`. Shot 01 → Shot 02 transition is `hard cut` (default; the originally-considered 0.3–0.5s white-flash transition is omitted per Q5 resolution — AI controllability is unreliable).

### Locked descriptor specifics (Q1, Q2, Q3, Q4 resolutions)

- **FR-32** 金箍棒 default length is **2 米** (locked from `findings/angle-character-design-and-ref.md` §3). The descriptor is the source of truth; no shot file overrides this. *(Q1 from dossier — resolved.)*
- **FR-33** 金箍棒 emission default is **反射环境暖光，无自身外发光辉**. The single permitted exception: Shot 03 climax (running approx. t=4–6s) allows the棒身钎柄处 a brief微弱内发光 (`#F2A65A` rim-only, ≤ 5% surface area). This is encoded in `shotlist.md` Shot 03 `连续性 tokens` and in both shot 03 prompt files. *(Q2 — resolved.)*
- **FR-34** 孙悟空 fur color is **naturalistic 棕褐 (`#5C4A3A` 山岩灰褐 base, with `#8A6A3A` partial gold-rim under逆光)** — preserves Black Myth grounded register. Stylized golden fur is禁用. *(Q3 — resolved.)*
- **FR-35** 星空密度 is **戏剧化星空 + 银河淡带** (sparse cinematic stars + diffuse galaxy band, NOT photorealistic dense star-field). Encoded in `style_guide.md` and in shots 02 / 04 / 05 `场景:` lines. *(Q4 — resolved.)*
- **FR-36** 凤翅紫金冠 + 锁子黄金甲 + 金箍棒 metal surfaces all anchor to the locked palette's 装饰金 double-layer hex pair (`#6B4226` 紫金底 + `#C9A96E` 鎏金高光). 暖橘金 `#F2A65A` is environment-light + rim-light only, NOT a metal surface color. The literary descriptor "凤翅紫金冠" is preserved verbatim in the locked-descriptor block; the visible hue resolves through the hex anchors above. *(Cross-cut resolution from dossier — resolved.)*

### Publish metadata

- **FR-37** `publish.md` follows the locked Chinese skeleton from `findings/angle-platform-conventions.md` §3, with all 6 sections present: 标题 / 简介 / Hashtag 规则 / 封面建议 / 发布时段建议 / 跨平台复用 (appendix).
- **FR-38** `publish.md` ships **3–5 hashtags total** in the description field, including mandatory `#Shorts`. Total title + description hashtag count ≤ 15.
- **FR-39** `publish.md` 标题 line has ≤ 30 中文字 and contains no hashtag character.
- **FR-40** `publish.md` 简介 body is 150–250 中文字, with first sentence as the hook (one-line scene summary).
- **FR-41** `publish.md` 发布时段 explicitly recommends **周四 / 周五 19:00–21:00 北京时间** as primary; **周四 11:00–12:00 北京时间** as North-American-Chinese-audience secondary.

### README contract

- **FR-42** `README.md` (Chinese) contains four sections: **项目概要** (1 short paragraph), **使用说明** (numbered steps mapping to the Primary-flow above), **角色清单** (one bullet for 孙悟空 with a 1-line summary), **风格关键词** (5–10 keywords pulled from `style_guide.md`).

## Non-functional requirements

- **NFR-1 — Tool version pinning.** All Kling-targeted prompts assume **Kling 2.1 Pro** capability set (10s cap, image-to-video, negative_prompt support, 9:16). All Seedance-targeted prompts assume **Seedance 1.0 Pro** capability set (12s cap, text-to-video, no negative_prompt, 9:16). Newer models (Kling 3.0 / Seedance 2.0) accept the same prompts; users with paid access to those tiers may use them without spec change.
- **NFR-2 — Character consistency.** The locked-descriptor byte-equality across 11 files (1 character bible + 5 Kling + 5 Seedance) is the load-bearing consistency mechanism for the pipeline. Stage-5 validation MUST include an automated string-equality check across these 11 files.
- **NFR-3 — Visual style consistency.** All palette references trace to `style_guide.md`'s 7-row palette table; all lighting tokens trace to its 6-token vocabulary; all motion descriptors trace to its 5-pattern vocabulary; all transitions trace to its 3-rule list. Free-form vocabulary in shot files is a violation.
- **NFR-4 — Prompt body language.** Prompt bodies are 100% Chinese. Latin characters permitted only for: hex codes, aspect ratio, durations with `s` unit, parameter keys (`negative_prompt:`, `cfg_scale:`, `seed:`, `camera_fixed`), tool/model names. No English prose inside prompt bodies.
- **NFR-5 — Aspect ratio consistency.** Every prompt file declares `比例: 9:16`. Every Seedream prompt also declares 9:16 竖构图. The `style_guide.md` palette table's `画幅` row reaffirms 9:16. Triple-redundancy is intentional — the user copy-pastes prompts in isolation and the redundancy guards against forgotten override.
- **NFR-6 — Shot-duration enum compliance.** Kling shot files' `时长:` MUST be `5s` or `10s` (Kling 2.1 Pro hard enum). For shots whose locked allocation falls between (Shot 02/03 = 8s, Shot 05 = 7s), the Kling file's `时长:` is set to `10s` with a `# 渲染说明:` annotation noting "render at 10s and trim to N s, or render at 5s with motion-compressed start state". Seedance shot files use the locked allocation directly (Seedance accepts integer 2–12).
- **NFR-7 — README synchronisation.** `README.md` 风格关键词 list is derived from `style_guide.md`. If `style_guide.md` updates, README must update — surgical follow-up only, no auto-regen at v1.
- **NFR-8 — File-content Chinese rule precedence.** Where any project rule pulls toward English (e.g., a hex code with English commentary), the Chinese-content rule takes precedence: comment in Chinese, value in the technical-token allowlist.

## Acceptance criteria summary

Full criteria belong to stage 5. The high-level shape:

- **Level 1 — file presence.** 12 files exist at the expected paths (FR-1 through FR-8).
- **Level 2 — schema.** Every prompt file contains the required field set (FR-26); shotlist has 5 rows with required columns (FR-20); README has 4 sections (FR-42); publish.md has 6 sections (FR-37).
- **Level 3 — content rules.** Locked-descriptor byte-equality across 11 files (FR-11 through FR-13); language + path language rules (FR-9, FR-10); palette + token + transition vocabulary lock (FR-15 through FR-19); duration enum + sum (FR-21, FR-22, FR-27); negative-prompt asymmetry (FR-23, FR-24); hashtag + length caps (FR-38 through FR-41).
- **Level 4 — semantic / cinematic.** Hook + thumbnail contract (FR-28, FR-29); loop-back byte-identical framing (FR-30, FR-31); descriptor specifics (FR-32 through FR-36). Some of these can be schema-checked (token presence in shot files); some require **manual visual walkthrough** after the user runs Seedream + Kling + Seedance externally — flagged for `validation.requires_manual_walkthrough`.
- **Level 5 — manual walkthrough.** User generates the立绘 + 5 shots, confirms on-model character + on-style register + clean loop. Stage 5 strategy will define the exact walkthrough script.

## Stage-6 work-unit decomposition (preview — stage 5 may rebalance)

| Unit | Outputs | Depends on |
|---|---|---|
| **U1 — character bible** | `characters/main.md`, `characters/ref_images/main_seedream.md` | locked descriptor (R02) |
| **U2 — style guide** | `style_guide.md` | locked palette + tokens (R03) |
| **U3 — narrative** | `script.md`, `shotlist.md` | U1 + U2 + per-shot allocation in this spec |
| **U4 — prompts** | 10 × `prompts/shotNN_{kling,seedance}.md` | U1 + U2 + U3 + R05 worked example |
| **U5 — publish** | `publish.md` | locked publish skeleton (R04) |
| **U6 — readme** | `README.md` | U1 + U2 + U5 |

Sequential dependency: U1 → U2 → U3 → U4, with U5 + U6 runnable after U2 + U3 + U4 land. Stage 6 will run these in this order with a streaming validator per unit.

## Open questions

None blocking v1. Deferred to potential v2 follow-up:

- English-language YouTube Shorts publish variant (out-of-scope per stage 2; explicit follow-up trigger).
- 抖音 / 视频号 dedicated publish files (currently captured as appendix in `publish.md`; promote to standalone files only on user request).
- Seedream cover-still prompt for non-Shorts platforms (currently relying on Shot 01 frame doubling).
- Multi-frame Kling input (`input_image_urls` array — provide both立绘 + environment ref).
- Pinning to Kling 3.0 / Seedance 2.0 prompts (current spec targets the GA-stable 2.1 Pro / 1.0 Pro pair).
