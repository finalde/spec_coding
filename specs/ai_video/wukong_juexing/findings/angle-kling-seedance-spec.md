# Angle: kling-seedance-spec

Researcher 05 — `wukong_juexing-20260503-201831`
Slug: `kling-seedance-spec` (merged angles #5 `15s-shot-decomposition` + #6 `kling-seedance-prompt-schema`)

## 1. What this angle covers

Two questions, answered together because their answers depend on the same primary sources:

1. **Capability spec** — what Kling and Seedance can each do *today* (May 2026), so the stage-4 spec doesn't ask for parameters the tools don't accept.
2. **Prompt schema** — what a high-quality Chinese prompt looks like for each tool (structure, motion vocabulary, negative-prompt support, length budget), and a paste-ready worked example for **Shot 02** (山顶仰角全景揭示) that stage 4 lifts as the template for the other four shots.

Scope is constrained by `agent_refs/project/ai_video.md` rule #4 (image-first character lock; locked descriptor re-pasted byte-identically in every shot prompt) and rule #5 (every shot ships dual prompts: Kling + Seedance).

## 2. Kling current spec — May 2026

| Field | Value | Source |
|---|---|---|
| Latest publicly-API'd model | Kling 2.1 Pro / Master (3.0 announced, 2.6 Pro doc'd) | fal.ai model registry |
| **Max clip length** | **10 s** (`duration` enum: `"5"` or `"10"`) | [fal.ai Kling 2.1 Pro i2v](https://fal.ai/models/fal-ai/kling-video/v2.1/pro/image-to-video) |
| Aspect ratios | `16:9`, `9:16`, `1:1` (all confirmed for v2.1 Pro; 4:3 / 3:4 added in 2.6 line) | [fal.ai Kling 2.1 Pro i2v](https://fal.ai/models/fal-ai/kling-video/v2.1/pro/image-to-video); [Kling 2.6 Pro guide](https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide) |
| Resolution | up to 1080p (720p available on 2.1 Standard) | [fal.ai Kling 2.1 Pro i2v](https://fal.ai/models/fal-ai/kling-video/v2.1/pro/image-to-video) |
| Image-to-video params | `image_url` (required), `prompt` (required), `duration`, `aspect_ratio`, `negative_prompt`, `cfg_scale` (default 0.5, 0.3–0.7 useful range), `static_mask_url`, `dynamic_mask_url`, `special_fx` (`hug`/`kiss`/`heart_gesture`/`squish`/`expansion`), `input_image_urls` (up to 4 frames) | [fal.ai Kling 2.1 Pro i2v](https://fal.ai/models/fal-ai/kling-video/v2.1/pro/image-to-video) |
| Negative prompt | **Supported.** Use to exclude artifacts (e.g. 多余手指, 文字水印, 模糊, 五官畸变) | [Kling 2.6 Pro guide](https://fal.ai/learn/devs/kling-2-6-pro-prompt-guide) |
| Recommended prompt length | ~80–150 English words / ~150–250 中文字 | [Kling 3.0 Chinese guide](https://seavidgen.com/zh/blog/kling-3-0-prompt-complete-guide) |
| Camera-movement axis system | 6-axis (-10..+10): horizontal pan, vertical pan, push/pull, tilt, roll, zoom; plus 4 advanced "master" moves (旋转推/旋转拉/上升推/下降拉) | [Kling official prompt guide](https://kling-ai.com/blog/kling-ai-prompt-guide) |
| Action-intensity dial | 0–3 (0 = nearly static, 3 = high-energy action) | [Kling 3.0 Chinese guide](https://seavidgen.com/zh/blog/kling-3-0-prompt-complete-guide) |

### Chinese motion vocabulary that Kling responds to

- **运镜:** 推镜头, 拉镜头, 摇镜头, 移镜头, 跟镜头, 升降镜头, 环绕镜头, 旋转推, 希区柯克变焦, 一镜到底, 手持
- **景别:** 大全景, 全景, 中景, 近景, 特写, 大特写
- **光线:** 顺光, 逆光, 侧光, 顶光, 晨光, 暮光, 自然光, 体积光 (god-ray), 高调光, 低调光
- **氛围:** 电影感, 史诗感, 神话感, 黑神话美术风, 厚重质感, 颗粒感

### Six-component semantic skeleton (official)

`Subject → Movement → Scene → Cinematic Language → Lighting → Atmosphere`

This maps cleanly onto our `agent_refs/project/ai_video.md` rule-#4 template (`角色 / 场景 / 动作 / 镜头 / 光线-色调 / 比例 / 时长`) — the harness template is a faithful Chinese rendering of Kling's own structure.

## 3. Seedance current spec — May 2026

| Field | Value | Source |
|---|---|---|
| Latest GA model | Seedance 1.0 Pro (1.5 Pro and 2.0 in rollout; 1.0 Pro is the stable t2v API target) | fal.ai / Replicate registries |
| **Max clip length** | **12 s** (`duration` enum: `2,3,4,5,6,7,8,9,10,11,12`, default `5`) | [fal.ai Seedance 1.0 Pro t2v API](https://fal.ai/models/fal-ai/bytedance/seedance/v1/pro/text-to-video/api) |
| Aspect ratios | `21:9, 16:9, 4:3, 1:1, 3:4, 9:16` (default `16:9`) | [fal.ai Seedance 1.0 Pro t2v API](https://fal.ai/models/fal-ai/bytedance/seedance/v1/pro/text-to-video/api) |
| Resolution | `480p / 720p / 1080p` (default `1080p` on Pro; Lite caps at 720p) | [fal.ai Seedance 1.0 Pro t2v API](https://fal.ai/models/fal-ai/bytedance/seedance/v1/pro/text-to-video/api) |
| Text-to-video params | `prompt` (required), `aspect_ratio`, `resolution`, `duration`, `camera_fixed` (bool), `seed` (-1 = random), `enable_safety_checker`, `num_frames` (overrides `duration`) | [fal.ai Seedance 1.0 Pro t2v API](https://fal.ai/models/fal-ai/bytedance/seedance/v1/pro/text-to-video/api) |
| Negative prompt | **NOT supported on 1.0 Lite/Pro.** Express exclusions positively (state what you DO want). | [AI/ML API Seedance 1.0 Lite prompt guide](https://aimlapi.com/blog/master-your-video-creations-with-seedance-1-0-lite-a-comprehensive-prompt-guide); search-result note across providers |
| FPS | 24 fps (no override on Pro) | [techpilot Seedance analysis](https://techpilot.ai/seedance-1-0-complete-analysis/) |

### Chinese motion vocabulary that Seedance responds to

Seedance was trained on bilingual prompts and accepts Chinese natively — the official guidance is "中文直接写，运镜词它都认识".

- **运镜:** 推、拉、摇、移、跟拍、升降、环绕、航拍、手持、一镜到底、希区柯克变焦、鱼眼镜头、俯拍、仰拍
- **景别:** 远景, 全景, 中景, 近景, 特写
- **光线:** 逆光, 侧光, 顺光, 低调光, 高调光, 自然光, 体积光
- **运动副词:** 缓慢、轻柔、连贯、自然、平稳；避免"夸张/超高速/复杂多人交互"
- **时间线写法:** Seedance 接受按秒分段的描写（"0–3秒…3–7秒…"），这是它的强项 — Kling 不强制这种写法，但也不拒绝

### Recommended structure (official)

`主体 + 动作 + 场景 + 光影 + 镜头语言 + 风格 + 画质 + 约束`
sources: [Seedance 2.0 prompt mastery guide](https://blog.wenhaofree.com/en/posts/articles/seedance-2-0-prompt-mastery-guide/), [Tencent News Seedance 2.0 manual](https://news.qq.com/rain/a/20260209A044NZ00)

The "约束" tail (no-blur, 五官稳定, 同一角色, 服装一致) carries the load that `negative_prompt` plays in Kling — it's the workaround.

## 4. Worked Chinese prompt pair — Shot 02 (山顶仰角全景揭示)

> **Shot 02 spec recap (carrying interview-locked answers):**
> - Beat: 镜头从碎裂石蛋拉远，仰角揭示孙悟空伫立山巅 — 第二个 hook 节拍。
> - Duration: 8 s (within ≤15 s harness rule, within both tools' 10–12 s caps).
> - Aspect: 9:16.
> - Style register: 黑神话·悟空 weighty mythic realism (locked by Round 1 visual-register answer).
> - Locked descriptor (placeholder pasted byte-identically — final descriptor written in stage 4):
>   `孙悟空 — 战损战士形态：橘金色短毛带焦黑战痕，身着粗布灰麻战裙搭青铜轻甲护肩，头戴凤翅紫金冠，手握金箍棒。眼神锐利金瞳，五官棱角分明，体格精干结实，气质沉静肃杀。`

### 4a. `shot02_kling.md` — image-to-video, paste-ready

```
[参考图: characters/ref_images/main_seedream.md 生成的孙悟空立绘]

角色: 孙悟空 — 战损战士形态：橘金色短毛带焦黑战痕，身着粗布灰麻战裙搭青铜轻甲护肩，头戴凤翅紫金冠，手握金箍棒。眼神锐利金瞳，五官棱角分明，体格精干结实，气质沉静肃杀。

场景: 黄昏时分的孤峰山巅，碎裂石蛋立于前景近处，残余金光从石蛋裂缝中缓缓溢出；远景星轨初现的暮色苍穹，云海从山腰翻涌而上；地表残留风化巨石与几株枯松，整体氛围厚重肃穆，黑神话·悟空美术风。

动作: 镜头从破裂石蛋表面缓慢拉远并仰角上摇，揭示孙悟空于山巅伫立背身（或四分之三背身），披风（若有）随风轻扬，金箍棒拄地、棒身金光微微震颤；人物自身保持基本静止，仅头部缓慢转向左前方约 15 度，目光投向暮色远方。

镜头: 起幅近景（碎石+金光）→ 落幅大全景（人物全身+山巅+暮空），仰角约 20 度，缓慢 dolly-out + tilt-up 复合运镜；动作强度 1（沉稳）；镜头节奏沉稳厚重。

光线/色调: 暮色暖橘 #F2A65A 主调 + 冷青阴影 #2E5C6E；金光体积光从石蛋裂缝向上渗透，形成柔和神性光柱；人物背身受逆光勾边（rim light），保留剪影神秘感；整体低饱和、高对比，颗粒感胶片质感。

比例: 9:16
时长: 8s

负向提示词 (negative_prompt): 多余手指, 五官畸变, 文字水印, 字幕, logo, 模糊, 鬼影, 闪烁, 卡通化, 廉价 CGI 感, 现代服饰, 现代建筑, 多人出现
```

### 4b. `shot02_seedance.md` — text-to-video, paste-ready

```
角色: 孙悟空 — 战损战士形态：橘金色短毛带焦黑战痕，身着粗布灰麻战裙搭青铜轻甲护肩，头戴凤翅紫金冠，手握金箍棒。眼神锐利金瞳，五官棱角分明，体格精干结实，气质沉静肃杀。

场景: 黄昏时分孤峰山巅，前景破裂石蛋残留金光，远景暮色苍穹星轨初现，山腰云海翻涌；风化巨石与枯松点缀，黑神话·悟空美术风，厚重肃穆。

动作 (按时间线):
0–2 秒: 近景特写碎裂石蛋表面，金光从裂缝缓慢溢出，镜头静止
2–5 秒: 镜头缓慢向后拉远并轻微仰角上摇，云海与山巅地表逐步入画
5–8 秒: 落幅为大全景，孙悟空背身伫立山巅，金箍棒拄地，头部缓慢左转约 15 度，望向暮色远方

镜头: 起幅近景 → 落幅大全景，仰角约 20 度，dolly-out + tilt-up 复合运镜，运动平稳缓慢，camera_fixed=false

光线/色调: 暮色暖橘主调 + 冷青阴影，体积光金柱从石蛋向上渗透，人物背身逆光勾边 (rim light)，低饱和高对比，胶片颗粒感

风格: 电影感, 史诗感, 神话感, 黑神话·悟空美术风, 写实质感
画质: 1080p, 4K HD, 细节丰富, 锐利清晰, 自然色彩, 画面稳定
约束: 五官稳定不畸变, 同一角色全程一致, 服装造型一致, 无文字水印, 无字幕, 无现代元素, 单人画面无多余人物, 无模糊鬼影闪烁

比例: 9:16
时长: 8s
seed: -1
```

**Why both, why this format:**

- The Kling block leads with `[参考图: ...]` because Kling 2.1 Pro takes `image_url` — that's where character lock comes from. Seedance has no equivalent text-to-video character-ref slot in the public API, so the locked descriptor MUST do the lifting in the prompt body — which is why the descriptor is pasted byte-identically, exactly per `agent_refs/project/ai_video.md` rule #4.
- The Seedance block uses the time-line writeup (`0–2 秒 / 2–5 秒 / 5–8 秒`) because that's Seedance's documented strength and it gets us deterministic per-second control without Kling's mask APIs.
- The Seedance block has no `negative_prompt:` line — Seedance ignores it. The `约束:` tail rephrases everything positively per the official "state what you do want" rule.
- Both blocks specify `比例: 9:16` and `时长: 8s` explicitly even though they're separately submitted via the API `aspect_ratio` / `duration` fields — the harness template per rule #4 expects them on the page so the user copy-pastes a complete unit.

## 5. Implications for the spec — what stage 4 needs to adjust

1. **Per-shot duration cap can be tightened from "≤15s" to "≤10s" for any shot we want runnable on either tool.** Kling tops at 10 s; Seedance at 12 s. If a shot needs the full 15 s, only Seedance can render it — Kling would have to split it into 5+5 with a continuity token. Recommend stage 4 budget shots at **≤10 s** so both tools remain usable per shot. Our soft target is ~5 shots × ~8 s = 40 s — already comfortably within the joint cap. **Action:** stage 4 shotlist should make the 10s ceiling explicit.

2. **Negative-prompt asymmetry is real and load-bearing.** Stage 4 must NOT generate a `negative_prompt:` block for Seedance shots. The shot-prompt template in `agent_refs/project/ai_video.md` rule #4 currently doesn't mention negative prompts — that's correct as the *minimum*; the Kling variant SHOULD add a negative line, the Seedance variant MUST replace it with a positive `约束:` block. Recommend stage 4 documents this divergence in `style_guide.md` so it's not re-discovered per shot.

3. **9:16 is supported on both tools at all relevant durations** — no compromise needed.

4. **Camera-movement vocabulary overlaps cleanly between the two tools.** All of `推/拉/摇/移/跟/升降/环绕/俯/仰` work on both. Stage 4 can use one shared 镜头 line per shot and trust both tools to honour it.

5. **The `agent_refs/project/ai_video.md` rule-#4 template is sound and sufficient** — just needs the per-tool divergence around the negative-prompt slot. No rewrite required; a one-line note clarifying "Kling 加 negative_prompt; Seedance 改写为 约束 段" is the surgical update.

6. **`cfg_scale` (Kling) and `seed` (both) are not in the harness template.** Stage 4 should decide whether to add them as optional knobs or leave them at defaults (Kling 0.5, Seedance -1). Recommend leaving them off the per-shot prompt and noting "默认值, 用户可在 Kling/Seedance UI 内自行覆盖" in `style_guide.md` — keeps the per-shot file clean.

7. **Locked Chinese descriptor needs to be finalised in stage 4 before any shot prompt can be paste-ready.** The descriptor used in §4 above is a *placeholder* that mirrors the interview's Round-1 character answer (战损战士 + 凤翅紫金冠 + 金箍棒). Stage 4 should produce the canonical descriptor in `characters/main.md` and re-paste it byte-identically across all 5 shots' Kling and Seedance prompts.

## 6. Open questions surfaced

- **Q1.** Does the user prefer running on fal.ai, Replicate, the official Kling app (klingai.com), or Volcengine for Seedance? Each has slightly different rate limits and pricing, but the prompt format is identical — so this is a workflow question, not a spec question. Defer to user; not blocking.
- **Q2.** Kling 3.0 / Master and Seedance 2.0 are both in late-2025–early-2026 rollout. The 2.0 variants extend duration and add multi-modal inputs (audio/video refs). v1 spec targets the GA-stable 2.1 Pro / 1.0 Pro pair to avoid betting on a moving spec; if user has paid access to 3.0 / 2.0 the same prompts work, plus optional extras. Surfaced for awareness; no spec change.
- **Q3.** Should stage 6 (execution) attempt 4-image multi-frame Kling prompts (`input_image_urls` array) for Shot 02 specifically — providing both the Seedream立绘 AND a "山巅暮色" environment frame? Would tighten environment lock but doubles the Seedream-prep budget. Defer to user as a stage-6 quality knob; v1 spec assumes single ref image per shot.
- **Q4.** The interview locked "scene = mountaintop at dusk" but did not lock specific palette hex values. §4 above uses provisional `#F2A65A` (暖橘) + `#2E5C6E` (冷青) borrowed from `agent_refs/research/ai_video.md`'s default palette example. Stage 4's `style_guide.md` should ratify or replace these.

---

**Word count:** ~1,290 words (within the 800–1500 budget for this heavier angle).

**Sources cited inline:** fal.ai Kling 2.1 Pro i2v page; fal.ai Kling 2.6 Pro prompt guide; fal.ai Seedance 1.0 Pro t2v API page; fal.ai Seedance 1.0 Lite t2v page; AI/ML API Seedance 1.0 Lite prompt guide; Kling AI official prompt guide blog; Kling 3.0 Chinese guide on seavidgen; techpilot Seedance 1.0 analysis; Tencent News Seedance 2.0 manual; WenHaoFree Seedance 2.0 prompt mastery guide.
