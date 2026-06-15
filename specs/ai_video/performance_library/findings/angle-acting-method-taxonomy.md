---
worker_id: researcher-01-acting-method-taxonomy
stage: 3
role: researcher
angle: acting-method-taxonomy
status: complete
blockers: []
confidence: high
---

# Angle: Acting-Method Taxonomy

## 1. What this angle covers

How established acting-method systems (Stanislavski, Meisner, Michael Chekhov, Laban Movement Analysis, Uta Hagen, plus the FACS/Ekman observational system) decompose a *named emotion* into **concrete, observable, directable physical action** — and which of their classification axes and vocabulary we can borrow to validate and structure our four-dimension schema 情绪 × 强度 × 风格 × 载体. The deliverable is *borrowable vocabulary*, not theatre history: words a director hands an actor (or that we drop into a `动作:`/`表情:` prompt field), at the level of breath, gaze, micro-gesture, and body tension.

## 2. Key findings

**Stanislavski — "emotion is not directable; physical action is."** The Method of Physical Action holds that emotion cannot be commanded ("be sad" reads false); instead the actor performs a precise, observable *physical action* (folding a dead person's clothes, searching a drawer) and the emotion arises from it. Scenes break into **beats**, each beat an **active verb** ("to plead," "to shield," "to dismiss"). Source: [Stanislavski's system (Wikipedia)](https://en.wikipedia.org/wiki/Stanislavski%27s_system), [Physical Action in Acting (ActorFuel)](https://actorfuel.com/physical-action-acting/). → *This is the single most load-bearing finding for us:* our library entries must be phrased as observable physical actions / active verbs, NOT emotion labels. The 情绪 dimension is the index; the entry *body* is action.

**Laban Movement Analysis — the strongest structural match to our 强度 + 风格 axes.** LMA's **Effort** describes the dynamic quality of a movement on four bipolar factors: **Weight** (strong↔light), **Time** (sudden/quick↔sustained), **Space** (direct↔indirect), **Flow** (bound↔free). Flow especially "is associated with the change in emotion or mood." The eight **Effort Actions** (Float, Punch/Thrust, Glide, Slash, Dab, Wring, Flick, Press) are taught at drama schools (ALRA, LIPA, Manchester) precisely to "change quickly between physical manifestations of emotion." Source: [Laban movement analysis (Wikipedia)](https://en.wikipedia.org/wiki/Laban_movement_analysis), [LMA for Actors (Backstage)](https://www.backstage.com/magazine/article/laban-movement-analysis-guide-50428/). → Our 风格 (内敛压抑 vs 外放爆发) maps cleanly onto **Flow: bound vs free** and **Weight/Time** combinations: 内敛压抑 = bound flow + sustained time + held weight (a Wring/Press); 外放爆发 = free flow + sudden time + strong weight (a Punch/Slash). Our 强度 1→5 maps onto the *amplitude* of Weight + the boundness of Flow.

**Michael Chekhov — Psychological Gesture + four Qualities of Movement (carrier vocabulary).** The **Psychological Gesture (PG)** is one whole-body archetypal movement that "instantly transforms" the actor into the character's emotional state — a single composite physical icon for an emotion. The four **Qualities of Movement (Molding, Flowing, Flying, Radiating, "MFFR")** map to degrees of resistance / the four elements: Molding (earth, dense — struggle, suppression), Flowing (water, continuous), Flying (air, light/swift), Radiating (fire/light, bursting outward). Source: [Chekhov Qualities of Movement](http://michaelchekhovcontinuousacting.blogspot.com/2014/02/qualities-of-movement-degrees-of.html), [Chekhov Technique (Acting Classes Central)](https://actingclassescentral.com/chekhov-acting-technique-mastering-psychological-gesture-for-stronger-performances/). → MFFR is a ready-made secondary tag: Molding ≈ 内敛压抑 high-intensity (suppressed struggle), Radiating ≈ 外放爆发. The PG concept validates our 复合 (composite) carrier — a single entry that fuses face+body+breath into one icon.

**Uta Hagen — the *cause* layer, not directly borrowable as physical vocabulary.** Hagen's Object Exercises, Endowment (treat a cup as if it holds poison), Sense Memory, Substitution, and Conditioning Forces (layering heat/cold/pain/hurry) are techniques for *generating* truthful emotion in a live actor. Source: [The Uta Hagen Technique (StageMilk)](https://www.stagemilk.com/the-uta-hagen-technique/), [Definitive Guide (Backstage)](https://www.backstage.com/magazine/article/the-definitive-guide-to-uta-hagens-acting-technique-68922/). → **Honest gap:** these are inputs to a human performer; an AI image model has no inner life to condition. We borrow the *Conditioning Forces* idea only as a reminder that a strong entry layers ≥2 carriers (e.g., breath + gaze). Meisner (repetition / "living truthfully under imaginary circumstances," reaction-driven) is likewise a *process* method — not a source of static physical-tell vocabulary — so it informs sequencing, not entry content.

**FACS / Ekman — the empirical anchor for 强度 and 面部/眼神.** The Facial Action Coding System decomposes any facial expression into anatomically-based **Action Units (AUs)**, each rated on a **5-point intensity scale A→E (A=trace/barely visible, B=slight, C=marked, D=severe, E=maximum)**. It covers the six/seven basic emotions (joy, sadness, anger, surprise, fear, disgust, contempt). Source: [Facial Action Coding System (Wikipedia)](https://en.wikipedia.org/wiki/Facial_Action_Coding_System), [Microexpressions (Backstage)](https://www.backstage.com/magazine/article/microexpressions-definition-examples-76521/). → **Our 强度 1–5 is essentially FACS A–E** — this is independent empirical validation that a 5-point intensity scale on emotion is real pedagogy, not arbitrary. Intensity 1 (micro-expression) = AU trace; intensity 5 (loss-of-control) = AU maximum.

**Per-emotion physical tells (director-level, observable).** Consolidated from acting body-language sources ([Body Language for Actors (Backstage)](https://www.backstage.com/magazine/article/body-language-acting-advice-76420/), [Emotions in the Body](https://www.melinalinden.com/emotions-in-the-body/)):

| 情绪 | 面部 face | 眼神 eyes/gaze | 肢体 body | 呼吸 breath |
|---|---|---|---|---|
| 悲/grief | drooping features, trembling lip, chin crumple | damp/glassy eyes, downcast | heaviness in chest, slumped, slowed | shallow, catching, held-then-sob |
| 怒/anger | flushed, clenched jaw, bared teeth | hard direct stare, narrowed | clenched fists, rigid, leaning in / invading space | fast, forced through nose |
| 惧/fear | widened eyes, open mouth, pale | darting / avoidant, wide | tense freeze or recoil, trembling | rapid, shallow, breath-hold |
| 喜/joy | genuine (Duchenne) smile, raised cheeks | crinkled, bright, open | lightness, lifted chest, expansive | easy, deeper, may laugh |

→ These are exactly the load-bearing strings for our `表情:`/`动作:` fields, already organized along our 载体 axis.

## 3. Implications for the spec (concrete, actionable)

1. **Phrase every entry as observable physical action, never an emotion label** (Stanislavski). The 情绪 field is the *index key*; the entry body is "trembling lip + downcast glassy eyes + held breath," not "sad." This should be a hard rule in stage-4 spec.
2. **Adopt the four LMA Effort factors as the engine behind 强度 + 风格.** Recommend each entry optionally carry an internal LMA tag (Weight/Time/Flow), even if not surfaced in the final prompt string: 内敛压抑 = *bound flow + sustained + held weight*; 外放爆发 = *free flow + sudden + strong weight*. This makes 风格 mechanically generable rather than vibes-based and gives the author a checklist for "is this entry actually suppressed vs explosive?"
3. **Anchor 强度 1–5 to FACS A–E** (1=trace/micro-expression, 5=maximum/loss-of-control). Put the A–E gloss in the schema doc so authors calibrate consistently. This is the most defensible part of our four-dimension schema — keep it.
4. **Map 载体 onto Chekhov MFFR for the 复合 case.** A 复合 (composite) entry is effectively a Psychological Gesture — one icon fusing face+eyes+body+breath. Tag composite entries with an MFFR quality (Molding/Flowing/Flying/Radiating) as a quick style classifier; Molding↔内敛, Radiating↔外放.
5. **Validates the schema overall:** 强度 (FACS A–E), 风格 (LMA Flow bound/free), 载体 (FACS AU regions + Chekhov PG for composite) are all backed by real pedagogy. 情绪 is the index. The four-dimension schema is sound — no axis is invented.
6. **Drop Hagen/Meisner from entry *content*.** They generate emotion in humans and have no output-string equivalent. Cite them only in the library README as the reason entries should layer ≥2 carriers (Conditioning Forces).

## 4. Open questions

- **Culture/genre calibration:** FACS/LMA are Western-derived. Chinese short-drama (爽剧/重生/追妻) has stylized conventions (e.g., the slow turn, the single tear, the trembling backhand slap) that may not decompose cleanly into LMA Effort. Does the library need a 短剧-genre stylization layer on top of the universal physical tells? (Flag for interview/spec.)
- **Intensity granularity:** is 5 levels right, or do short-drama beats really only use 3 (micro / normal / outburst)? FACS supports 5, but our 20–40-entries-per-emotion budget may cluster around extremes.
- **Composite vs single-carrier ratio:** how many of the 20–40 per emotion should be 复合 (PG-style) vs single-carrier atoms? Unresolved by pedagogy — it's a library-design choice.
- **Render fidelity:** does Kling/Seedance actually distinguish "bound flow sustained" from "free flow sudden" given identical emotion words? Untested here — needs a stage-6 render probe.
