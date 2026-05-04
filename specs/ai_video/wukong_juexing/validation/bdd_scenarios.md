# BDD scenarios — wukong_juexing (level 02 / bdd_scenarios)

Run: wukong_juexing-20260503-201831
Stage: 5 (validation strategy)
Level: bdd_scenarios — feature-level behaviors with concrete examples
Inputs consumed: `final_specs/spec.md`, `.claude/agent_refs/validation/general.md`, `.claude/agent_refs/validation/ai_video.md`

Each `Feature` corresponds to ONE load-bearing behavior of the package — NOT to one FR. FRs are cited per-feature and per-scenario so the coverage matrix at the end is auditable. Every scenario is tagged `automated` (deterministic string / regex / count check) or `manual_walkthrough_only` (requires the user to render externally and visually inspect).

---

## Feature 1 — Character lock contract

**Load-bearing behavior:** the locked Chinese descriptor for 孙悟空 appears byte-identically in 11 files (1 character bible + 5 Kling prompts + 5 Seedance prompts), AND the Seedream立绘 prompt follows the locked 10-section structure with the right body length. This is the spine of the image-first character-consistency strategy — drift here is invisible at the prompt-file layer but produces visible character drift in rendered output.

**Derived from:** FR-11, FR-12, FR-13, FR-14, NFR-2, ai_video.md required-move 3.

```gherkin
Feature: Locked descriptor byte-equality across 11 files
  As the validation gate for image-first character consistency
  I want the same Chinese descriptor block in every place 孙悟空 is named
  So that Kling and Seedance both render the same character

  Background:
    Given the locked descriptor block lives in `characters/main.md`
    And the block is bounded by `【孙悟空 · 觉醒态 · 锁定描述符 v1】 ... 禁用 卡通线条、cel-shading、二次元大眼、低多边形。`
    And `characters/main.md` may surround the block with framing prose

  Scenario: descriptor block bytes match across all 11 files     # automated
    Given `characters/main.md` exists
    And `prompts/shot01_kling.md` ... `prompts/shot05_kling.md` exist
    And `prompts/shot01_seedance.md` ... `prompts/shot05_seedance.md` exist
    When I extract the locked-descriptor block from each of the 11 files using the boundary markers
    Then all 11 extracted blocks are byte-identical (modulo trailing newline)
    And no file places the block inside a code fence or YAML frontmatter

    Examples: violation modes that MUST fail
      | mode                                                    | severity |
      | Shot 03 Kling adds " (climax)" after the descriptor      | blocker  |
      | Shot 02 Seedance reorders 装扮 / 道具 sub-lines           | blocker  |
      | Shot 05 omits the 禁用 trailing line                      | blocker  |
      | One file uses 简体, another uses 繁體                       | blocker  |
      | A trailing space appears in only one file                 | blocker  |

  Scenario: descriptor block sits under `角色:` in every shot file  # automated
    Given a shot prompt file at `prompts/shotNN_<tool>.md`
    When I locate the `角色:` field
    Then the locked descriptor block appears immediately under `角色:`
    And no other field (`场景:`, `动作:`, `镜头:`, `光线/色调:`, `风格:`, `约束:`) contains the descriptor block

  Scenario: Seedream立绘 prompt follows the 10-section structure   # automated
    Given `characters/ref_images/main_seedream.md` exists
    When I parse the prompt body
    Then it contains all 10 section headers in order:
      | order | header     |
      | 1     | 主体定义    |
      | 2     | 面貌细节    |
      | 3     | 发型+头冠   |
      | 4     | 服装        |
      | 5     | 身材+姿态   |
      | 6     | 道具        |
      | 7     | 画面控制    |
      | 8     | 风格-质感   |
      | 9     | 比例+输出   |
      | 10    | 负向提示    |
    And the body length excluding section headers is between 250 and 400 中文字
    And `9:16` appears in section 9 (比例+输出)

  Scenario: descriptor file precondition for shot files          # automated
    Given a shot prompt file at `prompts/shotNN_<tool>.md` references 孙悟空
    Then `characters/main.md` MUST exist
    And `characters/ref_images/main_seedream.md` MUST exist
    # ai_video.md required-move 3 — missing either file = blocker independently
```

---

## Feature 2 — Visual style lock

**Load-bearing behavior:** every palette / lighting / motion / transition reference in any shot prompt traces back to a vocabulary token in `style_guide.md`. Free-form vocabulary ("warm golden tones", "暖光氛围" without hex anchor) is the failure mode that produces inconsistent rendering across shots. The style guide is the single source of truth.

**Derived from:** FR-15, FR-16, FR-17, FR-18, FR-19, FR-23 (禁用 register tokens), NFR-3.

```gherkin
Feature: Style vocabulary discipline across shot prompts
  As the visual-consistency gate
  I want every palette, lighting, motion, and transition reference to trace to style_guide.md
  So that all 5 shots render in one coherent visual register

  Background:
    Given `style_guide.md` exists
    And it contains exactly 7 named palette entries with hex codes (FR-15)
    And it contains exactly 6 lighting-state tokens
    And it contains exactly 5 motion-pattern tokens
    And it contains exactly 3 transition rules

  Scenario: palette table token + count check on style_guide.md  # automated
    When I parse `style_guide.md`
    Then the palette table has exactly 7 rows
    And every row has a Chinese name and a hex code matching `#[0-9A-F]{6}`
    And the lighting-state vocabulary has exactly 6 tokens
    And the motion-pattern vocabulary has exactly 5 tokens
    And the transition-rules section lists exactly 3 rules

  Scenario: every hex in shot files appears in the palette table  # automated
    Given the palette set P = {hex codes from `style_guide.md` palette table}
    When I scan every `prompts/shot*.md` file for `#[0-9A-Fa-f]{6}` substrings
    Then every match is in P
    And any unknown hex code is reported as a blocker with the file + line

    Examples: anchors expected to appear (sourced from FR-33, FR-34, FR-36)
      | hex      | role                          | locked context                        |
      | #F2A65A  | 暖橘金 环境光 + rim-light     | shots 01, 03 climax, 04, 05           |
      | #5C4A3A  | 山岩灰褐 fur base             | every shot                            |
      | #8A6A3A  | gold-rim under逆光             | every shot                            |
      | #6B4226  | 紫金底 (头冠 + 甲)            | every shot                            |
      | #C9A96E  | 鎏金高光 (头冠 + 甲 + 棒)     | every shot                            |

  Scenario: every shot's `光线/色调:` line uses only locked tokens  # automated
    Given a shot file `prompts/shotNN_<tool>.md`
    When I extract the value of `光线/色调:`
    Then every Chinese phrase in the value resolves to a token in `style_guide.md`
      | check                                                 | result   |
      | uses `体积光丁达尔束` (locked)                          | pass     |
      | uses `余烬冷尾` (locked)                                | pass     |
      | uses `暖色调` without hex                                | blocker  |
      | uses `warm tones` (English, free-form)                   | blocker  |
      | uses an unknown phrase `迷雾蓝调` not in style_guide     | blocker  |

  Scenario: 黑神话·悟空美术风 register anchor present              # automated
    Given a shot file `prompts/shotNN_<tool>.md`
    When I scan its `场景:` and `风格:` lines
    Then the phrase `黑神话·悟空美术风` (or the locked Chinese equivalent declared in `style_guide.md`) appears at least once
    # FR-18

  Scenario: 禁用 register tokens are absent from positive prompt body  # automated
    Given the禁用 set D = {`卡通`, `Q版`, `cel-shading`, `二次元`, `戏曲妆`, `京剧脸谱`, `低多边形`, `86版西游记`}
    When I scan a Kling shot file's body excluding the `negative_prompt:` line
    Then no token in D appears
    And when I scan a Seedance shot file's body excluding the `约束:` field
    Then no token in D appears
    # FR-19

  Scenario: motion-pattern + transition vocabulary trace                # automated
    Given a shot file's `动作:` and the shotlist row's transition column
    When I extract the motion descriptors and the transition tag
    Then every motion descriptor maps to one of the 5 motion-pattern tokens
    And every transition maps to one of the 3 transition rules in `style_guide.md`

  Scenario: visual register on rendered output                          # manual_walkthrough_only
    Given the user has rendered all 5 shots through Kling and Seedance
    When the user reviews the 5 chosen clips side-by-side
    Then the visual register reads as one register across all clips (no Q版 / 戏曲 / cel-shading drift)
    And the palette feels anchored, not free-form
    # final cross-cut subjective check; surfaces as `validation.requires_manual_walkthrough`
```

---

## Feature 3 — Dual-prompt asymmetry

**Load-bearing behavior:** Kling prompts have a `negative_prompt:` line AND lead with a `[参考图: ...]` line; Seedance prompts have neither — instead they have a `约束:` tail with the same exclusions expressed positively, AND their `动作:` is broken into per-second timeline segments. Symmetric prompts (one tool's schema bleeding into the other) silently work but break the workflow's A/B promise: the user can no longer compare two genuine renders.

**Derived from:** FR-23, FR-24, FR-25, FR-26, FR-27, NFR-1, NFR-6, ai_video.md required-move 4.

```gherkin
Feature: Kling/Seedance prompt files diverge on schema
  As the dual-prompt A/B gate
  I want each tool's prompt file to follow the tool's own schema, not the other's
  So that A/B comparison is meaningful

  Background:
    Given each shot has both `prompts/shotNN_kling.md` and `prompts/shotNN_seedance.md`

  Scenario: Kling files include negative_prompt and reference-image header  # automated
    Given a Kling shot file `prompts/shotNN_kling.md`
    Then it MUST contain a line starting `negative_prompt:`
    And the `negative_prompt:` line contains all of:
      | token             |
      | 多余手指          |
      | 五官畸变          |
      | 文字水印          |
      | 字幕              |
      | logo              |
      | 模糊              |
      | 鬼影              |
      | 闪烁              |
      | 现代服饰          |
      | 现代建筑          |
      | 多人出现          |
      | 卡通              |
      | Q版               |
      | cel-shading       |
      | 二次元            |
      | 戏曲妆            |
      | 京剧脸谱          |
      | 低多边形          |
      | 86版西游记         |
    And the file's first non-frontmatter line is `[参考图: characters/ref_images/main_seedream.md 生成的孙悟空立绘]`

  Scenario: Seedance files exclude negative_prompt and reference-image     # automated
    Given a Seedance shot file `prompts/shotNN_seedance.md`
    Then NO line starts with `negative_prompt:`
    And NO `[参考图:` reference-image header line appears
    And it MUST contain a `约束:` field
    And the `约束:` field contains positive contraries:
      | locked phrase                       |
      | 五官稳定不畸变                      |
      | 同一角色全程一致                    |
      | 单人画面无多余人物                  |
      | 无文字水印                          |
      | 无字幕                              |
      | 无现代元素                          |
      | 无模糊鬼影闪烁                      |

  Scenario: Seedance动作 is timeline-segmented; Kling may be prose         # automated
    Given a Seedance shot file with `时长: <N>s`
    When I extract `动作:`
    Then the `动作:` value contains ≥2 explicit timeline segments matching `\d+[–-]\d+ ?秒:`
    And the segments tile the [0, N] interval contiguously without gaps or overlaps

    Examples: per-shot expected segment counts (locked from FR-21 + FR-25)
      | shot | duration | minimum segments | example tiling                       |
      | 01   | 5s       | 2                | `0–2 秒: ...` `2–5 秒: ...`           |
      | 02   | 8s       | 3                | `0–3 秒: ...` `3–6 秒: ...` `6–8 秒:` |
      | 03   | 8s       | 3                | `0–3 秒: ...` `3–6 秒: ...` `6–8 秒:` |
      | 04   | 10s      | 3                | `0–3 秒: ...` `3–7 秒: ...` `7–10 秒:` |
      | 05   | 7s       | 2                | `0–4 秒: ...` `4–7 秒: ...`           |

    Given a Kling shot file
    Then `动作:` MAY be prose (no timeline-segmentation requirement)

  Scenario: required field set per tool                                   # automated
    Given any shot file
    Then it MUST contain all of: `角色:`, `场景:`, `动作:`, `镜头:`, `光线/色调:`, `比例:`, `时长:`
    Given a Kling shot file
    Then it MUST additionally contain: `negative_prompt:`
    Given a Seedance shot file
    Then it MUST additionally contain: `风格:`, `画质:`, `约束:`, `seed:`
    # FR-26

  Scenario: aspect ratio + duration enum compliance                       # automated
    Given a shot file
    Then `比例:` reads exactly `9:16`
    Given a Kling shot file
    Then `时长:` ∈ {`5s`, `10s`}
    And if the locked allocation (FR-21) is 7s or 8s, the file's `时长:` is `10s`
    And the file contains a `# 渲染说明:` annotation noting render-and-trim or 5s-with-motion-compression
    Given a Seedance shot file
    Then `时长:` matches the locked allocation per shot:
      | shot | seedance 时长 | kling 时长 |
      | 01   | 5s            | 5s         |
      | 02   | 8s            | 10s        |
      | 03   | 8s            | 10s        |
      | 04   | 10s            | 10s        |
      | 05   | 7s            | 10s        |
    # FR-21, FR-22, FR-27, NFR-6

  Scenario: tool-version capability assumption asserted                   # automated
    Given any shot file
    Then the file contains a comment or `# 工具版本:` annotation pinning Kling 2.1 Pro or Seedance 1.0 Pro respectively
    # NFR-1; missing pin is `warning`, not `blocker` (capability is the same on newer tiers)
```

---

## Feature 4 — Hook + thumbnail contract

**Load-bearing behavior:** Shot 01's burst-peak frame at t≈2s wall-clock doubles as the auto-frame YouTube Shorts thumbnail. The first 3 seconds is the retention battle; the spec carves out a separate cover-still Seedream prompt explicitly because Shot 01 is supposed to do this work. If Shot 01's t≈2s frame fails the thumbnail-quality bar, the user has no fallback.

**Derived from:** FR-28, FR-29, ai_video.md required-move 5 (shorts hook marker).

```gherkin
Feature: Shot 01 burst-peak frame doubles as Shorts thumbnail
  As the retention + thumbnail gate
  I want Shot 01's t≈2s frame to be a self-contained valid 9:16 thumbnail
  So that auto-frame thumbnail selection produces a recognition-grade cover

  Background:
    Given Shot 01 is the hook shot (5s duration per FR-21)
    And `shotlist.md` marks Shot 01 with `是否 hook 镜头: 是`

  Scenario: Shot 01 prompt files declare burst-peak at t≈2s             # automated
    Given `prompts/shot01_kling.md`
    Then its `动作:` text contains an explicit `t≈2s` (or `t = 2 秒`, `第 2 秒`) burst-peak marker
    Given `prompts/shot01_seedance.md`
    Then its `0–2 秒` timeline segment ends with the burst-peak event
    # FR-28

  Scenario: thumbnail contract annotation present                        # automated
    Given `prompts/shot01_kling.md` and `prompts/shot01_seedance.md`
    Then the top of each file contains a `# 缩略图契约` annotation block
    And the block declares:
      | requirement                                                         |
      | subject (cracking stone + golden-light burst) centred upper-2/3      |
      | single visual focal point                                            |
      | palette-compliant (only style_guide.md hexes)                        |
      | recognition-grade at 9:16                                            |
    # FR-29

  Scenario: shotlist marks Shot 01 as the hook                           # automated
    Given `shotlist.md`
    When I parse the row for `shot01`
    Then `是否 hook 镜头:` reads `是`
    And no other shot row reads `是`
    # FR-20 + ai_video.md required-move 5

  Scenario: rendered Shot 01 t≈2s frame is thumbnail-quality             # manual_walkthrough_only
    Given the user has rendered Shot 01 via Kling and via Seedance
    When the user reviews the t≈2s frame from each render
    Then the frame reads at thumbnail size (≤120 px tall) — subject is identifiable, palette is anchored, no muddy mid-frame
    And if the frame fails the abuse-test, the user re-renders Shot 01 (does NOT compromise on thumbnail)
    # FR-29 final visual gate
```

---

## Feature 5 — Loop-back contract

**Load-bearing behavior:** Shot 05's final frame composition is byte-identical to Shot 01 frame 0 (camera, focal length, framing, prop placement) — only the lighting state differs (peak burst → fading余烬). This is the cinematic loop that turns the 38s short into a re-watchable piece. If Shot 05 ends with a different composition, the loop fails silently in YouTube's autoplay and retention drops.

**Derived from:** FR-30, FR-31.

```gherkin
Feature: Shot 05 final frame byte-identically composed to Shot 01 frame 0
  As the loop-back cinematic gate
  I want Shot 05's final frame to mirror Shot 01's first frame in composition
  So that the short autoplay-loops cleanly on YouTube Shorts

  Background:
    Given Shot 01 frame 0 lighting state is `金光-bursting / 体积光丁达尔束` (peak)
    And Shot 05 final-frame lighting state is `金光-fading / 余烬冷尾` (decay)
    And only the lighting delta is permitted; camera/focal/framing/prop placement are locked

  Scenario: 回环契约 annotation block present in Shot 05 prompt files     # automated
    Given `prompts/shot05_kling.md` and `prompts/shot05_seedance.md`
    Then the top of each file contains a `# 回环契约` annotation block
    And the block declares all of:
      | locked invariant            | value                                     |
      | 镜头角度                    | byte-identical to Shot 01 frame 0          |
      | 焦距                        | byte-identical to Shot 01 frame 0          |
      | 主体 framing                | byte-identical to Shot 01 frame 0          |
      | 道具放置                    | byte-identical to Shot 01 frame 0          |
      | 光线 delta (only permitted)  | 金光-bursting → 金光-fading / 余烬冷尾    |
    # FR-30

  Scenario: Shot 01 frame-0 + Shot 05 final-frame `镜头:` lines align     # automated
    Given `prompts/shot01_<tool>.md` and `prompts/shot05_<tool>.md`
    When I extract each file's `镜头:` line and any explicit framing/focal annotation
    Then the two `镜头:` lines are byte-identical except for an explicit `(回环 / 起 → 收)` suffix on Shot 05
    And no implicit framing drift exists (e.g., Shot 05 uses 35mm but Shot 01 uses 50mm)

  Scenario: shotlist transitions match the locked rules                  # automated
    Given `shotlist.md`
    When I extract the transition column for shots 01→02, 02→03, 03→04, 04→05
    Then 01→02 transition is `hard cut`
    And 04→05 transition is `match cut`
    And no transition is `white-flash 0.3–0.5s` (omitted per Q5 resolution)
    # FR-31

  Scenario: rendered loop reads as a clean autoplay loop                 # manual_walkthrough_only
    Given the user has assembled all 5 shots into a single 38 s ±4 s clip
    When the user plays the assembled clip in autoplay loop
    Then the cut from Shot 05's last frame back to Shot 01's first frame reads as one continuous beat
    And the lighting transition (fading → bursting) lands as a deliberate cinematic exhale → inhale, not a jarring jump
    # FR-30 final visual gate
```

---

## Feature 6 — Locked descriptor specifics (Q1–Q4)

**Load-bearing behavior:** four interview resolutions (金箍棒 length + emission, fur color, star density, hex anchor pairs for metals) are locked into the descriptor and into specific shot files. These are the most likely silent-drift points because they're "nice details" that a worker might re-prose under time pressure. Each one was a real interview question; each MUST land byte-identically.

**Derived from:** FR-32, FR-33, FR-34, FR-35, FR-36.

```gherkin
Feature: Locked descriptor specifics survive into shot files
  As the interview-resolution preservation gate
  I want Q1 / Q2 / Q3 / Q4 resolutions to appear byte-identically wherever they're load-bearing
  So that no worker silently re-proses a resolved decision

  Scenario: 金箍棒 length is 2 米 across all shots                       # automated
    Given the locked-descriptor block in any of the 11 files
    Then the substring `金箍棒` is followed (within the block) by an explicit length token `2 米` or `两米`
    And no shot file's `道具:` field overrides the length
    # FR-32

  Scenario: 金箍棒 emission default vs Shot 03 climax exception          # automated
    Given the locked-descriptor block
    Then the emission default reads `反射环境暖光，无自身外发光辉`
    Given `shotlist.md` row for Shot 03
    Then the `连续性 tokens` column contains `钎柄微弱内发光 / #F2A65A rim-only / ≤5% surface area / t≈4–6s`
    Given `prompts/shot03_kling.md` and `prompts/shot03_seedance.md`
    Then the `动作:` field contains the same Shot-03 climax emission exception note
    And NO other shot's prompt file contains the climax emission exception note
    # FR-33

    Examples: per-shot emission posture
      | shot | emission posture                                       |
      | 01   | reflect ambient warm light only                          |
      | 02   | reflect ambient warm light only                          |
      | 03   | climax: 钎柄 brief 内发光 #F2A65A rim ≤5% area t≈4–6s   |
      | 04   | reflect ambient warm light only                          |
      | 05   | reflect ambient warm light only (fading)                 |

  Scenario: 孙悟空 fur color uses naturalistic 棕褐 hex anchors          # automated
    Given the locked-descriptor block
    Then the substring `毛发` (or `毛色`) is associated with `#5C4A3A` 山岩灰褐 base AND `#8A6A3A` 逆光 gold-rim
    And `#F2A65A` is NOT presented as a fur surface color anywhere
    And no shot file describes 金色毛发 / golden fur as a primary surface
    # FR-34

  Scenario: 星空 density is 戏剧化星空 + 银河淡带, not photorealistic    # automated
    Given `style_guide.md`
    Then it contains the locked phrase `戏剧化星空 + 银河淡带` in its sky/天空 vocabulary
    Given the prompt files for shots 02, 04, 05 (sky-visible shots)
    Then each `场景:` field contains the locked phrase or a token explicitly tracing to it
    And no sky description uses `photoreal star field` / `dense star field` / `银河系实拍密度`
    # FR-35

  Scenario: metal-surface hex pair anchors 凤翅紫金冠 + 锁子黄金甲 + 金箍棒  # automated
    Given the locked-descriptor block
    Then 凤翅紫金冠 + 锁子黄金甲 + 金箍棒 metal surfaces all anchor to:
      | role             | hex      |
      | 紫金底             | #6B4226   |
      | 鎏金高光           | #C9A96E   |
    And `#F2A65A` (暖橘金) is anchored as 环境光 + rim-light, NEVER as a metal surface fill
    And the literary phrase `凤翅紫金冠` appears verbatim in the locked-descriptor block
    # FR-36

  Scenario: shot files do not contradict the descriptor specifics       # automated
    Given any `prompts/shotNN_<tool>.md`
    When I scan `角色:`, `道具:`, `光线/色调:`, `场景:`
    Then no field redefines 金箍棒 length / fur primary color / star density / metal hex anchors
    # cross-cut

  Scenario: 黑神话-grade weighty-mythic register on rendered output    # manual_walkthrough_only
    Given the user has rendered all 5 shots
    When the user inspects the character at full frame
    Then 毛发 reads as 棕褐 naturalistic (not stylized gold)
    And 金箍棒 reads as 2 米 (not 3 米 / not staff-sized)
    And the metal surfaces read as 紫金底 + 鎏金高光 (not flat gold)
    # final cross-cut subjective check
```

---

## Feature 7 — Publish skeleton

**Load-bearing behavior:** `publish.md` is a copy-paste-ready YouTube Shorts payload. If it's malformed (title too long, hashtag count off, missing `#Shorts`, missing 发布时段), the user has to rewrite it under publish-day pressure — defeating the workflow's promise. The locked Chinese skeleton with 6 sections is the contract.

**Derived from:** FR-37, FR-38, FR-39, FR-40, FR-41, ai_video.md required-move 6.

```gherkin
Feature: publish.md is a copy-paste-ready YouTube Shorts payload
  As the publish-day gate
  I want publish.md to satisfy YouTube Shorts metadata constraints
  So that the user can paste each section without editing

  Background:
    Given `publish.md` exists at `ai_videos/wukong_juexing/publish.md`

  Scenario: 6-section Chinese skeleton present                           # automated
    When I parse `publish.md`
    Then it contains exactly these 6 top-level sections in order:
      | order | section          |
      | 1     | 标题              |
      | 2     | 简介              |
      | 3     | Hashtag 规则      |
      | 4     | 封面建议          |
      | 5     | 发布时段建议       |
      | 6     | 跨平台复用 (附录) |
    # FR-37

  Scenario: 标题 ≤ 30 中文字 with no hashtag character                     # automated
    Given the 标题 section
    When I count Chinese (Han) characters in the 标题 line, ignoring whitespace
    Then the count is ≤ 30
    And the 标题 line does NOT contain `#`
    # FR-39

    Examples: 标题 length checks
      | 标题 candidate                                       | char count | result   |
      | 《悟空觉醒》5 秒石破天惊，38 秒一镜回环！             | 22         | pass     |
      | 《悟空觉醒》5 秒石破天惊，38 秒一镜回环。这是黑神话…  | 32         | blocker  |
      | 《悟空觉醒》#Shorts 一镜到底                          | n/a (has #) | blocker  |

  Scenario: 简介 body 150–250 中文字, first sentence is the hook         # automated
    Given the 简介 section
    When I count Chinese characters in the body
    Then the count is between 150 and 250 (inclusive)
    And the first sentence is a one-line scene summary (the hook)
    And no sentence in the body exceeds two lines
    # FR-40

  Scenario: hashtag rules — 3–5 total, #Shorts mandatory                # automated
    Given the Hashtag 规则 section
    When I extract the hashtag list
    Then 3 ≤ count ≤ 5
    And the list contains `#Shorts` (case-sensitive)
    And the list does NOT contain `#BlackMythWukong` or `#黑神话` (out-of-scope per spec)
    And the title + description hashtag count totals ≤ 15
    # FR-38

    Examples: hashtag set checks
      | hashtag list                                             | result   |
      | `#Shorts #悟空觉醒 #国风`                                  | pass (3) |
      | `#Shorts #悟空觉醒 #国风 #cinematic #blackmyth`            | blocker (#blackmyth out-of-scope per spec out-of-scope §) |
      | `#悟空觉醒 #国风`                                          | blocker (no #Shorts; count=2)            |
      | `#Shorts #A #B #C #D #E`                                   | blocker (count=6)                         |

  Scenario: 发布时段 primary + secondary windows                         # automated
    Given the 发布时段建议 section
    Then it explicitly recommends `周四 / 周五 19:00–21:00 北京时间` as primary
    And it explicitly recommends `周四 11:00–12:00 北京时间` as North-American-Chinese-audience secondary
    # FR-41

  Scenario: 封面建议 references Shot 01 t≈2s frame                       # automated
    Given the 封面建议 section
    Then it references `shot01` t≈2s burst-peak frame as the cover
    And it does NOT reference a separate `cover_seedream.md` file (out-of-scope per spec)
    # FR-29 + spec out-of-scope §

  Scenario: subjective quality of publish copy on platform              # manual_walkthrough_only
    Given the user previews `publish.md` against YouTube Studio
    When the user pastes 标题 + 简介 + hashtags
    Then the title doesn't truncate in mobile-feed preview
    And the description's first 80 chars (visible-above-fold on mobile) include the hook
    # FR-39 + FR-40 final platform check
```

---

## Coverage matrix

Each FR maps to ≥1 scenario. `automated` = green box (deterministic check). `manual_walkthrough_only` = open box (user must render externally and visually inspect). FR-1 through FR-10 are file-presence + global-language checks owned by level 01 (acceptance_criteria); they're cited here only where a feature directly asserts on top of them.

| FR     | Feature                          | Scenario(s)                                                                                       | Mode                            |
|--------|----------------------------------|---------------------------------------------------------------------------------------------------|----------------------------------|
| FR-11  | F1 Character lock contract       | descriptor block bytes match across all 11 files                                                  | automated                        |
| FR-12  | F1 Character lock contract       | descriptor block bytes match; descriptor sits under `角色:`                                        | automated                        |
| FR-13  | F1 Character lock contract       | descriptor block bytes match; descriptor sits under `角色:`                                        | automated                        |
| FR-14  | F1 Character lock contract       | Seedream立绘 prompt follows the 10-section structure                                              | automated                        |
| FR-15  | F2 Visual style lock             | palette table token + count check on style_guide.md                                               | automated                        |
| FR-16  | F2 Visual style lock             | every shot's `光线/色调:` line uses only locked tokens                                             | automated                        |
| FR-17  | F2 Visual style lock             | every hex in shot files appears in the palette table                                              | automated                        |
| FR-18  | F2 Visual style lock             | 黑神话·悟空美术风 register anchor present                                                         | automated                        |
| FR-19  | F2 Visual style lock             | 禁用 register tokens are absent from positive prompt body                                         | automated                        |
| FR-20  | F4 Hook + thumbnail              | shotlist marks Shot 01 as the hook                                                                | automated                        |
| FR-21  | F3 Dual-prompt asymmetry         | aspect ratio + duration enum compliance                                                           | automated                        |
| FR-22  | F3 Dual-prompt asymmetry         | aspect ratio + duration enum compliance                                                           | automated                        |
| FR-23  | F3 Dual-prompt asymmetry         | Kling files include negative_prompt; Seedance excludes negative_prompt and includes 约束:         | automated                        |
| FR-24  | F3 Dual-prompt asymmetry         | Kling files include reference-image header; Seedance excludes it                                  | automated                        |
| FR-25  | F3 Dual-prompt asymmetry         | Seedance动作 is timeline-segmented; Kling may be prose                                             | automated                        |
| FR-26  | F3 Dual-prompt asymmetry         | required field set per tool                                                                       | automated                        |
| FR-27  | F3 Dual-prompt asymmetry         | aspect ratio + duration enum compliance                                                           | automated                        |
| FR-28  | F4 Hook + thumbnail              | Shot 01 prompt files declare burst-peak at t≈2s                                                   | automated                        |
| FR-29  | F4 Hook + thumbnail              | thumbnail contract annotation present + rendered Shot 01 t≈2s frame is thumbnail-quality           | automated + manual_walkthrough_only |
| FR-30  | F5 Loop-back                     | 回环契约 annotation block + frame-0/final `镜头:` align + clean autoplay loop                       | automated + manual_walkthrough_only |
| FR-31  | F5 Loop-back                     | shotlist transitions match the locked rules                                                       | automated                        |
| FR-32  | F6 Locked descriptor specifics   | 金箍棒 length is 2 米 across all shots                                                             | automated                        |
| FR-33  | F6 Locked descriptor specifics   | 金箍棒 emission default vs Shot 03 climax exception                                                | automated                        |
| FR-34  | F6 Locked descriptor specifics   | 孙悟空 fur color uses naturalistic 棕褐 hex anchors                                                | automated                        |
| FR-35  | F6 Locked descriptor specifics   | 星空 density is 戏剧化星空 + 银河淡带                                                              | automated                        |
| FR-36  | F6 Locked descriptor specifics   | metal-surface hex pair anchors 凤翅紫金冠 + 锁子黄金甲 + 金箍棒                                     | automated                        |
| FR-37  | F7 Publish skeleton              | 6-section Chinese skeleton present                                                                | automated                        |
| FR-38  | F7 Publish skeleton              | hashtag rules — 3–5 total, #Shorts mandatory                                                      | automated                        |
| FR-39  | F7 Publish skeleton              | 标题 ≤ 30 中文字 with no hashtag character                                                          | automated                        |
| FR-40  | F7 Publish skeleton              | 简介 body 150–250 中文字, first sentence is the hook                                                | automated                        |
| FR-41  | F7 Publish skeleton              | 发布时段 primary + secondary windows                                                              | automated                        |
| NFR-1  | F3 Dual-prompt asymmetry         | tool-version capability assumption asserted                                                       | automated (warning, not blocker) |
| NFR-2  | F1 Character lock contract       | descriptor block bytes match across all 11 files                                                  | automated                        |
| NFR-3  | F2 Visual style lock             | palette table check + every-hex-in-palette + locked-tokens-only                                   | automated                        |
| NFR-6  | F3 Dual-prompt asymmetry         | aspect ratio + duration enum compliance                                                           | automated                        |

### Mode totals

| Mode                          | Scenario count |
|-------------------------------|----------------|
| automated                     | 27             |
| manual_walkthrough_only       | 5              |

### Per-feature scenario counts

| Feature                                  | Scenarios | Manual-only scenarios |
|-------------------------------------------|-----------|------------------------|
| F1 Character lock contract                | 4         | 0                      |
| F2 Visual style lock                      | 6         | 1                      |
| F3 Dual-prompt asymmetry                  | 5         | 0                      |
| F4 Hook + thumbnail                       | 4         | 1                      |
| F5 Loop-back                              | 4         | 1                      |
| F6 Locked descriptor specifics            | 7         | 1                      |
| F7 Publish skeleton                       | 7         | 1                      |

### Severity routing (per validation/general.md + ai_video.md)

| Failure class                                                                  | Severity   |
|--------------------------------------------------------------------------------|------------|
| Locked-descriptor byte-equality drift across the 11 files (any feature 1 fail) | blocker    |
| Hex code outside style_guide palette appears in any shot file                  | blocker    |
| Kling missing `negative_prompt:` / Seedance present `negative_prompt:`         | blocker    |
| Missing `[参考图: ...]` header on a Kling shot file                             | blocker    |
| Missing `约束:` field on a Seedance shot file                                   | blocker    |
| `比例:` not `9:16` on any shot file                                             | blocker    |
| Shot 01 missing `# 缩略图契约` block / not marked hook in shotlist               | blocker    |
| Shot 05 missing `# 回环契约` block / framing drift from Shot 01 frame 0         | blocker    |
| 标题 > 30 中文字 / 简介 outside 150–250 / hashtag count outside 3–5 / no #Shorts | blocker    |
| Tool-version pin (NFR-1) missing                                               | warning    |
| Continuity-token drift between adjacent shots when state should carry over     | warning    |
| Manual-walkthrough open box not yet checked                                    | requires_manual_walkthrough (not a halt; gates work-unit close per ai_video.md required-move 8) |
