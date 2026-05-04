# Revised prompt — wukong_juexing

**task_type:** ai_video
**sub_type:** short
**Approved by user:** 2026-05-03 ("go" reply to concept recommendation)

## Goal

Produce a single ~40-second YouTube Short (9:16) — 《悟空觉醒》 / "Wukong Awakens" — that depicts one cinematic transformation moment of Sun Wukong (孙悟空 / 齐天大圣). Output is a complete production-ready package under `ai_videos/wukong_juexing/`: character bible + Seedream ref-image prompt, style guide, script, shotlist, dual Kling + Seedance prompts per shot, and Chinese-language publish metadata.

This is the user's **first** ai_video project on the spec-driven pipeline. Scope is intentionally constrained to a single-character, single-scene short to validate the Seedream → Kling/Seedance image-first pipeline end-to-end before attempting multi-character or multi-episode work.

## Context

- **Why this concept (research-grounded):** YouTube Shorts in 2026 reward (a) hook within 2–2.5s, (b) faceless / animated content over talking-head for AI generations, (c) 35–55s total length for completion-rate, (d) loop-able final frame, (e) high-craft single-IP cinematic moments over mass-produced AI slop (which YouTube has been actively purging since 2025). Sun Wukong cleanly satisfies all five: instantly recognisable IP with global tailwind from *Black Myth: Wukong* (Aug 2024), a public-domain mythological figure with no licensing concerns, a single iconic character that exercises the Seedream-lock pipeline cleanly, and a transformation moment that maps naturally onto Kling's strength in fluid motion / FX physics.
- **Why "first project" matters:** Multi-character casts are the hardest thing in the image-first character pipeline (every character needs its own Seedream lock + byte-identical descriptor across every shot). A single-character short isolates the pipeline contract for a clean shakedown.
- **Cultural framing:** Chinese mythology, treated reverentially — not parody, not meme-bait. Visually cinematic, in the spirit of *Black Myth: Wukong*'s art direction (weighty, grounded, mythic).

## Desired outcome

A complete `ai_videos/wukong_juexing/` folder per the `sub_type=short` layout in `.claude/agent_refs/project/ai_video.md`:

```
ai_videos/wukong_juexing/
├── README.md                       # 中文: 项目概要 + 使用说明
├── characters/
│   ├── main.md                     # 孙悟空 设定: 面貌/发型/服装/身材/性格 + 锁定描述符
│   └── ref_images/
│       └── main_seedream.md        # Seedream 立绘 prompt (中文)
├── style_guide.md                  # 镜头语言 / 光线 / 色调 / 转场 (中文)
├── script.md                       # 40-second 剧本 (中文)
├── shotlist.md                     # ~5 镜头, 标记 hook 镜头, 每镜 ≤15s
├── prompts/
│   ├── shot01_kling.md
│   ├── shot01_seedance.md
│   └── ... (×5 shots, dual prompts each)
└── publish.md                      # 标题 / 简介 / 标签 / 封面建议 (中文)
```

All content inside `ai_videos/wukong_juexing/` is in Chinese per the project rule. Folder + file names are pinyin / English per the same rule.

## Hard constraints (from `agent_refs/project/ai_video.md`)

1. Slug `wukong_juexing` is pinyin, never Chinese-character path. Chinese title 《悟空觉醒》 lives inside `README.md`.
2. **9:16 vertical** aspect ratio (no override).
3. **Every shot ≤ 15 seconds.** Total runtime targeted at ~40s ⇒ ~5 shots × 8s avg, exact split decided in stage 4.
4. **Dual prompts per shot:** every shot ships with both `shotNN_kling.md` AND `shotNN_seedance.md`. User picks the better generation per shot.
5. **Image-first character lock:** Sun Wukong gets one Seedream ref-image prompt; the locked Chinese descriptor is re-pasted byte-identically in every Kling and Seedance shot prompt that names him.
6. **Chinese-content rule:** every file inside `ai_videos/wukong_juexing/` is in Chinese.
7. **Publish metadata:** `publish.md` ships with hook title (≤30 中文字), description (≤200 中文字), 5–10 hashtags, cover-frame suggestion.
8. **README in Chinese**, includes 项目概要, 使用说明, 角色清单, 风格关键词.

## Soft targets (not yet locked — to be confirmed in stage 2)

- ~40s total runtime (range 35–55s acceptable).
- ~5 shots (range 4–6 acceptable; trade-off between per-shot detail and pipeline complexity).
- Visual style anchored to *Black Myth: Wukong*'s "weighty mythic realism" register, not stylised anime; final aesthetic pinned in `style_guide.md`.
- Loop-friendly final frame echoing the opening shot.
- No dialogue, no text overlays, no audio prompts in v1 (visuals only per `agent_refs/project/ai_video.md`).

## Out of scope (v1)

- Multi-character scenes (any antagonist, sidekick, or supporting cast).
- Multi-episode / serialised structure (single piece only).
- Audio track, music selection, sound effect prompts.
- Distribution beyond YouTube Shorts metadata (no TikTok / Reels variants in v1).
- Stage-6 actual video rendering — pipeline outputs the prompts; user runs Seedream + Kling + Seedance externally.

## Success looks like

1. User can copy the Seedream prompt, generate a 立绘, and the result reads recognisably as the user's intended Sun Wukong (not a generic monkey character).
2. User can paste each Kling / Seedance shot prompt + the Seedream ref image and get a 9:16 ≤15s clip that visibly matches the locked descriptor in face, outfit, and build.
3. The five shots, concatenated in order, tell a coherent transformation story that loops cleanly.
4. `publish.md` is paste-ready into YouTube Shorts at upload time.
