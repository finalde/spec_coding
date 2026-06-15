---
worker_id: researcher-02-facs-microexpression
stage: 3
role: researcher
angle: facs-microexpression
status: complete
blockers: []
confidence: high
---

# Angle: FACS / Microexpression — precision facial vocabulary for 载体=面部/眼神

## 1. What this angle covers

The Facial Action Coding System (FACS), built by Paul Ekman & Wallace Friesen (first published 1978, major revision 2002, anatomical groundwork by Carl-Herman Hjortsjö 1970), decomposes any humanly-possible facial expression into ~44 **Action Units (AUs)** — each AU being the contraction/relaxation of one specific facial muscle or muscle group. EMFACS (Emotional FACS) and Ekman's prototype tables then map *combinations* of AUs onto the basic emotions. This angle delivers the established AU→emotion mappings, a plain-Chinese description of the visible movement of each load-bearing AU, and the microexpression literature's findings on **intensity gradation** (subtle/micro vs full-blown/macro) and **suppression/masking** — which is exactly the precision source our `载体=面部` and `载体=眼神` entries, and our `风格=内敛(suppressed)` axis, need.

Scope boundary: FACS is a *descriptive anatomical code*, not a theory that these AU sets are the only valid expression of an emotion. The PNAS "compound facial expressions" work (Du, Tao & Martinez 2014) extends the basic set to 21 categories including blends (e.g. happily-surprised) using the same AU alphabet. I flag below where I'm citing established FACS/EMFACS coding vs. synthesizing for prompt use.

## 2. Key findings

### 2.1 Core AU vocabulary (the movements our prompts must name)

| AU | 英文名 | 中文可见动作 (prompt 用语) |
|----|--------|------------------------------|
| AU1 | Inner Brow Raiser | 眉头**内**角上提（额肌内侧）→ 眉心呈"八"字/担忧状 |
| AU2 | Outer Brow Raiser | 眉**外**梢上挑 → 眉弓整体抬高 |
| AU4 | Brow Lowerer | 皱眉、眉头下压内聚，眉间挤出竖纹（川字纹） |
| AU5 | Upper Lid Raiser | 上眼睑上提 → 瞪大眼、露出更多眼白 |
| AU6 | Cheek Raiser | 颧肌外圈收缩 → 眼下/外眼角堆起、眼睛眯成弯月（真笑标记） |
| AU7 | Lid Tightener | 下眼睑收紧上抬 → 眼神变凌厉、眼裂变窄 |
| AU9 | Nose Wrinkler | 皱鼻、鼻梁起横纹、上唇被带起 |
| AU10 | Upper Lip Raiser | 上唇抬起、露上齿、法令纹加深 |
| AU12 | Lip Corner Puller | 嘴角向斜上方拉 → 微笑弧度 |
| AU14 | Dimpler | 嘴角向内收紧、酒窝处下凹（蔑视/勉强） |
| AU15 | Lip Corner Depressor | 嘴角下拉、呈倒"八"字 |
| AU16 | Lower Lip Depressor | 下唇下拉、露下齿 |
| AU17 | Chin Raiser | 下巴上推、下唇前突（噘嘴/委屈） |
| AU20 | Lip Stretcher | 嘴角水平向两侧拉伸（恐惧拉扯感） |
| AU23 | Lip Tightener | 双唇收紧变薄、抿压 |
| AU24 | Lip Pressor | 双唇用力相压（强忍标志之一） |
| AU25/26/27 | Lips Part / Jaw Drop / Mouth Stretch | 唇分开 / 下颌松落张口 / 大幅张口 |
| AU43 | Eyes Closed | 闭眼 |

(AU names per iMotions FACS visual guide; muscle bases per same source.)

### 2.2 Emotion → prototype AU combination → 中文面部画面 (established EMFACS/FACS coding)

| 情绪 | 规范 AU 组合 | 中文可见画面 | 强度/微表情备注 |
|------|--------------|--------------|------------------|
| 高兴/喜 (happiness) | **AU6 + AU12** （开口大笑加 AU25+AU26） | 嘴角上扬 + 眼周堆起眼睛眯弯（杜乡式真笑）；假笑缺 AU6 | 仅 AU12 无 AU6 = 社交假笑/礼貌笑；AU6 强度是"真假笑"的关键判据 |
| 悲伤 (sadness) | **AU1 + AU4 + AU15**（常伴 AU17） | 眉内角上提+眉间皱起+嘴角下拉（伴下巴上推噘嘴） | 微表情常只露 AU1+AU4（眉头内上提）而嘴仍维持；眼神先垮 |
| 惊讶 (surprise) | **AU1 + AU2 + AU5 + AU26** | 全眉抬高、瞪眼、下颌松落张口 | 持续最短的表情；强度高时 AU27 大张口。与恐惧的区别：惊讶**无 AU4**（不皱眉） |
| 恐惧 (fear) | **AU1 + AU2 + AU4 + AU5 + AU7 + AU20 + AU26** | 眉抬又皱、瞪眼且下睑紧、嘴角水平拉扯、张口 | 含 AU4 是与惊讶的分水岭；AU20 嘴角横扯是恐惧专属 |
| 愤怒 (anger) | **AU4 + AU5 + AU7 + AU23** | 压眉瞪眼、下睑紧绷、双唇收紧抿压 | 微表情常只露 AU4+AU7（眼神凶）而嘴维持；强忍怒气见 §2.4 |
| 厌恶 (disgust) | **AU9 + AU15 + AU16**（或 AU10 抬上唇） | 皱鼻、上唇抬、嘴角下拉露下齿 | 核心是 AU9 皱鼻；轻度厌恶可仅鼻翼微皱（subtle） |
| 蔑视/轻蔑 (contempt) | **AU12 + AU14，单侧** | **单边**嘴角内收上提（不对称冷笑） | 唯一规范的**不对称**表情；单侧性本身即信号 |

(All combinations above are established EMFACS/Ekman prototype coding, per iMotions guide + Lie to Me/FACS references + PNAS Du et al. 2014.)

### 2.3 Intensity gradation — the 强度 1→5 axis has a FACS basis

FACS scores **each AU's intensity on a 5-point A–E scale** (A = trace, B = slight, C = marked/pronounced, D = severe/extreme, E = maximum). This is *per-AU*, not per-face — so our 强度 axis can be authored as "which AUs fire **and how hard**":

- **强度1 (micro/痕迹)** — one or two core AUs at A–B intensity, often a single region (e.g. anger = only AU4+AU7 faint). Ekman: a *subtle/mini expression* may be "limited to one region of the face."
- **强度3 (clear/marked)** — the full prototype combination at C intensity, the "normal/obvious" macro expression (Ekman: macro expressions last 0.5–4 s and match speech).
- **强度5 (outburst/极致)** — full combination at D–E, plus the open-mouth/jaw AUs recruiting (AU25/26/27), whole-body recruitment.

Crucially: **going from 强度1→5 is mostly the same AU set at rising A→E intensity, PLUS later recruitment of mouth-opening AUs** — not a different set of muscles. That's the cleanest authoring rule the FACS scale gives us.

### 2.4 Suppression / masking — the engine of our 风格=内敛 axis

Ekman's microexpression discovery is *built on* suppression: when someone tries to mask a felt emotion, the true emotion **leaks**. Two leakage forms (Paul Ekman Group):

1. **Micro expression** — the concealed emotion's *full* AU combination flashes across the **whole face** for ≤ 1/2 second (typically 1/25–1/5 s), then is overridden.
2. **Subtle/mini expression** — leakage **limited to one region**, low intensity, can persist.

For the **风格=内敛(suppressed / 强忍)** vocabulary this means an entry should layer THREE things:
- the **leaked true-emotion AUs** at low intensity / one region (e.g. grief leaking as AU1+AU4 at the brow while the mouth holds),
- **active suppressor AUs**: AU23/AU24 (双唇收紧/用力相压), AU17 (下巴上推抗住下垂的嘴角), AU14 (嘴角内收), swallowing, controlled jaw — the *effort* of holding is itself visible,
- a **conflict signature**: upper face (eyes/brow) leaks while lower face (mouth) is forcibly composed, or vice-versa. The asymmetry/mismatch between regions IS the "强忍" read.

This directly serves `载体=眼神`: under suppression the **eyes leak first** (AU1/AU4/AU7 and welling/AU43 blink suppression) because lower-face muscles are easier to volitionally control than upper-face — a robust finding in the deception literature that our 内敛 eye-carrier entries should encode.

## 3. Implications for the spec

1. **Author 载体=面部 / 眼神 entries directly off the AU prototype table in §2.2**, but emit them as the 中文可见画面 column — Kling/Seedance read movement description, not "AU12". Keep AU numbers as a comment/metadata for traceability, not in the rendered prompt body.
2. **Encode the 强度 1→5 axis as "AU subset + A–E intensity + late mouth-AU recruitment"** (§2.3), not as ad-hoc adjectives. 强度1 = one region, trace; 强度5 = full set, max, mouth open. This gives a principled, non-arbitrary intensity ladder.
3. **风格=内敛 is NOT just "weaker version of 外放."** It is leaked-AU (low intensity, one region) + visible suppressor AUs (AU23/24/17/14) + upper/lower-face conflict (§2.4). 风格=外放 = full prototype at high intensity, recruiting body. Author these as two genuinely different prompt blocks per 情绪, sharing the same leaked-emotion core.
4. **Two diagnostic disambiguators worth baking into entries:** AU6 presence = real vs. fake happiness (真笑/假笑); AU4 presence = fear vs. surprise. These are high-value because directors confuse exactly these pairs.
5. **Contempt is the asymmetry entry** — its `面部` block must specify **单侧** (one-sided) movement; symmetry would read as a smirk/smile instead.
6. **眼神 carrier deserves its own AU subset** (AU1/2/4/5/7/43 + gaze + blink-rate), because under suppression eyes leak first — making 眼神 the highest-signal carrier for 内敛 emotional entries.

## 4. Open questions surfaced

- **FACS codes movement, not gaze direction, blink rate, tear/welling, or pupil** — yet these are huge for 眼神 acting. Need a complementary source (gaze/oculesics literature) for the eye-carrier dimension beyond what FACS covers. (Flag for a sibling angle.)
- **Cross-cultural validity / display rules:** the basic-emotion AU prototypes are claimed universal, but *display rules* (when/how much to show) are cultural. For Chinese short-drama affect, do we need a 含蓄/克制 cultural prior baked into default 强度? Open.
- **Blends (复合 emotions)** — PNAS Du et al. (2014) gives 21 compound categories (e.g. happily-surprised, angrily-disgusted, 又惊又怕) with AU recipes. Our schema has 载体=复合 but I have not yet pulled the full 21-category AU table — recommend a follow-up fetch of the PNAS compound-expression recipes if 复合 entries are in scope for v1.
- **强忍 sub-types:** "强忍泪水" (suppressing crying) vs "强压怒火" (suppressing anger) vs "强装镇定" (masking fear) have different suppressor-AU signatures. Worth enumerating as distinct library entries rather than one generic 内敛 modifier.

## Sources
- iMotions — *Facial Action Coding System (FACS): A Visual Guidebook*: https://imotions.com/blog/learning/research-fundamentals/facial-action-coding-system/
- iMotions — *The Many Faces of Emotion: From the Duchenne Smile to the Grimace of Fear*: https://imotions.com/blog/learning/research-fundamentals/duchenne-smile/
- Paul Ekman Group — *Micro Expressions*: https://www.paulekman.com/resources/micro-expressions/
- Paul Ekman — *Suppressed Emotions and Deception: The Discovery of Micro Expressions*: https://www.paulekman.com/blog/suppressed-emotions-and-deception-the-discovery-of-micro-expressions/
- Wikipedia — *Facial Action Coding System* (history, AU count, 1978/2002 editions): https://en.wikipedia.org/wiki/Facial_Action_Coding_System
- Du, Tao & Martinez (2014), *Compound facial expressions of emotion*, PNAS: https://www.pnas.org/doi/10.1073/pnas.1322355111
- Lie to Me Wiki — *Facial Action Coding System* (EMFACS prototype combinations, cross-check): https://lietome.fandom.com/wiki/Facial_Action_Coding_System

**Established vs. synthesized:** §2.1, §2.2, §2.3 (A–E scale), and §2.4 leakage definitions are established FACS/EMFACS/Ekman coding from the cited sources. The 中文可见动作 phrasings, the 强度→AU-subset/intensity authoring rule, the three-layer 内敛 model, and all of §3 are my synthesis for prompt-authoring use.
