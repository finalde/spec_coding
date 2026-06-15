---
worker_id: researcher-04-ai-video-acting-controllability
stage: 3
role: researcher
angle: ai-video-acting-controllability
status: complete
blockers: []
confidence: medium
---

# Angle: ai-video-acting-controllability

## 1. What this angle covers

The real-world 2025 state of controlling **performance / emotion / facial-expression / micro-expression** in the leading AI video models — primarily Kling (可灵, Kuaishou) and Seedance (即梦/Doubao-Seedance, ByteDance), with cross-applicable notes from comparison testing that also touched Runway and Sora. It answers: (a) which performance descriptors actually land vs. get ignored; (b) whether an expressive **start frame** (image-to-video) controls performance better than text alone; (c) prompt-craft techniques for getting emotion to land and avoiding 过火/over-acting; (d) Kling-vs-Seedance differences relevant to our dual-model validation gate.

A standing caveat: this field moves monthly, version numbers churn (the user's premise targets the *current* Kling/Seedance generation), and almost all public "evidence" is creator anecdote and small N=1..5 test batteries, not controlled benchmarks. Treat everything below as **reported/observed**, not measured. The user's core premise — that acting/emotion is the dimension models obey *least* reliably — is corroborated by every source consulted.

## 2. Key findings (with citations)

**(a) What works vs. gets ignored.** The single most consistent finding across creator testing: **vague emotion words are ignored or under-rendered; named physical muscle actions land.** Segmind's Kling 1.6 expression test states plainly that instead of "The girl feels emotional," you must write "The girl looks directly at the camera, smiling softly with a hint of nervousness," and reports their best results came from prompts that *enumerate anatomy* — e.g. a sadness prompt scoring 4.7/5 realism: "eyebrows draw together slightly, eyes lower gradually, corners of mouth turn down subtly" ([Segmind](https://blog.segmind.com/kling-ai-1-6-testing-facial-expressions-all-you-need-to-know/)). The same source reports the clear failure modes: **very subtle micro-expressions get missed** ("may struggle to capture … a small smirk or a quick raise of an eyebrow") and **extreme expressions render stiff** ("exaggerated laughter or shock came off slightly stiff"; a surprised gasp "leaned slightly toward exaggeration"). So the controllable band is the *middle* of the intensity range — strong enough to name as muscle movement, not so strong it tips into theatrical stiffness. This directly explains 过火: over-acting is partly a model artifact at the high-intensity end, not only a prompt-wording problem.

**(b) Expressive start frame (image-to-video) vs. text-only.** Evidence here is suggestive but **not from a head-to-head controlled test**. The general image-to-video principle reported is that "a start frame reference locks the initial composition, lighting, and style, providing more precise control than text prompts alone" ([ImagineArt/Kling 2.1](https://www.imagine.art/blogs/kling-2-1-start-end-frame-overview)). Kling's start/end-frame conditioning (from 2.1, May 2025) is paired with "improved life-like facial animation," and Kling motion-control workflows transfer expression from a *reference* (image or driving video) "with the lip-sync and facial muscles perfectly aligned with the reference" ([Pollo](https://pollo.ai/m/kling-ai/kling-3-0-motion-control), [SuperMaker](https://supermaker.ai/blog/turn-photos-into-memes-the-ultimate-kling-motion-control-tutorial/)). Logic and these reports converge: **a start frame that already shows the target expression removes the hardest task (synthesizing the peak expression from text) and leaves only motion interpolation** — which models do more reliably. I found **no public A/B that isolates "same expression via text vs. via start frame"**, so this is synthesis grounded in the start-frame-locks-composition consensus, not a measured result. This is exactly the kind of claim our own control-variable rendering should settle.

**(c) Prompt-craft techniques that land.** Converging recommendations:
- **Sequential/temporal staging beats stacking.** Break an arc into beats — "The woman frowns and looks away" then "She starts crying softly" — rather than one prompt carrying multiple simultaneous emotions; combining intense emotions in one prompt is reported to confuse the model ([Segmind](https://blog.segmind.com/kling-ai-1-6-testing-facial-expressions-all-you-need-to-know/)). Both Kling and Seedance newer versions claim native single-shot transitions ("starts surprised then breaks into laughter") ([SeedanceAI](https://www.seedanceai.cc/capabilities/emotion-expression)), but the safer authoring pattern remains explicit beats.
- **Name muscle groups + a gaze anchor.** "Looks directly at the camera" plus eyebrow/eye/mouth verbs is the recurring winning template.
- **Dial intensity with adverbs ("slightly," "subtly," "gradually")** — these are reported to be respected and are the lever against 过火.
- **Avoid the high-intensity ceiling** where stiffness appears; if a beat needs big emotion, prefer a start frame at peak + small motion over a text request for "screaming with rage."

**(d) Kling vs. Seedance differences.** The most directly relevant source is Curious Refuge's 5-test emotional comparison: **Seedance won 4 of 5 emotional tests (Joy, Anger, Nervousness, Suspicion); Confusion ~tied.** Seedance "adher[ed] to the prompts and convey[ed] more complex emotions … layered and emotionally grounded," with reactions "more subtle, natural, and cinematic," while Kling "leaned more aggressive" with "larger body movements," more theatrical delivery, and intermittent lip-sync drift ([Curious Refuge](https://curiousrefuge.com/blog/seedance-2-vs-kling-3); echoed by [VidAU](https://www.vidau.ai/seedance-2-0-vs-runway-sora-and-kling-in-complex-ai-video-tests-now/), which groups Seedance and Sora as "instruction-first / better prompt compliance" vs. Kling and Runway). **Net: Seedance tends toward restraint (risk = under-acting on subtle beats), Kling tends toward over-projection (risk = 过火).** This is a *tendency from small samples*, not a law — and it argues strongly for keeping both models in the validation gate rather than declaring a winner.

## 3. Implications for the spec

1. **Validation design must score the right axis.** The user's 1-5 axes (表演达意 / 情绪可识别 / 是否过火) map cleanly onto the observed failure modes: under-rendering (达意 fails), ambiguity (情绪可识别 fails), and stiffness at the intensity ceiling (过火). Keep all three; they are not redundant. Consider that 是否过火 is **model-correlated** (Kling skews high), so it should be scored *per model*, not pooled — a block that passes 过火 on Seedance may fail on Kling.
2. **Mandate physical-anatomy phrasing in every library entry.** Each performance block should encode emotion as named muscle actions + a gaze anchor + an intensity adverb, never a bare emotion noun. This is the single highest-leverage rule and it is well-evidenced.
3. **Strongly recommend (not strictly mandate) an expressive 起始帧 for high-intensity beats.** Evidence says start frames help and that text-only struggles most at the intensity ceiling — but there is no controlled proof, and our own dual-model test *is* the missing experiment. Suggested spec stance: allow text-only entries for mid-intensity emotions; require a peak-expression start frame for any block whose target emotion is high-intensity (rage, sobbing, shock). Record which mode each validated entry used so the library itself becomes the A/B dataset.
4. **Dual-model gate is justified and should stay asymmetric-aware.** Because Seedance and Kling fail in opposite directions, "pass if ≥threshold on ≥1 model" is reasonable, but the entry should **record which model passed and its per-model scores**, so downstream authors know "this block reads as intended on Seedance but over-acts on Kling." Don't collapse to a single pass/fail.
5. **Keep entries beat-scoped.** Favor single-emotion or explicit two-beat blocks over multi-emotion stacks, matching the staging finding and our ≤15s shot rule.

## 4. Open questions surfaced

- **No controlled text-vs-start-frame A/B exists publicly.** Our own rendering can produce the first; the spec should treat mode (text-only vs. expressive start frame) as a *recorded variable*, not an assumption.
- **Version drift.** Sources span Kling 1.6 → 3.0 and Seedance 1.x → 2.0; the Kling-over-acts / Seedance-restrained tendency is from the latest comparison but may not hold as versions update. Re-validation cadence should be part of the library contract.
- **Micro-expression floor unknown.** "Quick eyebrow raise / small smirk" is reported to get dropped — but no source quantifies the minimum intensity that reliably renders. Our control-variable tests could establish a practical floor per model.
- **Chinese-language prompt behavior.** All cited tests are English-prompt. Kling and Seedance are Chinese-native models and our `ai_videos/` content is Chinese; whether 中文 acting-direction phrasing (e.g. "嘴角微微下垂，眉头轻蹙") performs the same as the English muscle-naming pattern is **untested in public sources** and worth an early calibration render.
- **Gaze and body-language adherence** beyond the face are thinly documented; Kling's "larger body movements" note is the only signal, and it's anecdotal.

Sources:
- [Segmind — Kling AI 1.6: Testing Facial Expressions](https://blog.segmind.com/kling-ai-1-6-testing-facial-expressions-all-you-need-to-know/)
- [Curious Refuge — Seedance 2.0 vs Kling 3.0 AI Emotion Comparison](https://curiousrefuge.com/blog/seedance-2-vs-kling-3)
- [VidAU — Seedance 2.0 vs Runway, Sora, Kling complex test](https://www.vidau.ai/seedance-2-0-vs-runway-sora-and-kling-in-complex-ai-video-tests-now/)
- [SeedanceAI — Emotion Expression capability](https://www.seedanceai.cc/capabilities/emotion-expression)
- [Pollo — Kling 3.0 Motion Control](https://pollo.ai/m/kling-ai/kling-3-0-motion-control)
- [SuperMaker — Kling Motion Control tutorial](https://supermaker.ai/blog/turn-photos-into-memes-the-ultimate-kling-motion-control-tutorial/)
- [ImagineArt — Kling 2.1 Start & End Frame overview](https://www.imagine.art/blogs/kling-2-1-start-end-frame-overview)
