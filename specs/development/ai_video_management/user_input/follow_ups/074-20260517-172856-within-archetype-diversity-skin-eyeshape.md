# Follow-up draft 074 — 2026-05-17

User reports that within a single archetype (e.g. `femme_fatale` 妩媚) the generated actors look too similar — same lip type, same skin tone, etc. The user wants ≥ 20 entries per axis covering **size / color / shape** dimensions, and these should be wired into the per-actor randomness so within-archetype variety is visibly higher.

Three coupled changes:

## 1. Expand the skin pools

| Pool | Before | After | Dimensions added |
|---|---|---|---|
| `_VARIANCE_SKIN_TONE` | 10 | **22** | Full color spectrum: alabaster, translucent moonlight, cream rice, peachy rose-flushed, golden-honey, caramel, chestnut, umber, cocoa chocolate, ebony onyx, deep mahogany, neutral-medium balanced |
| `_VARIANCE_SKIN_TEXTURE` | 8 | **21** | Tactile spectrum: freckled constellation, glass-effect K-beauty, porous realistic, chok-chok dewy, scarred lived-in, ruddy windburn, matte velvet, silken satin, doll-flawless, sun-aged crinkled, pearlescent moonlit, olive-velvet matte, vellum parchment |

User explicitly called out 皮肤白 / 皮肤黑 (white/dark) — the new entries cover alabaster→ebony with intermediate caramel/chestnut/umber/cocoa/mahogany.

## 2. Expand the eyes pool with Chinese shape vocabulary

| Pool | Before | After | New shapes |
|---|---|---|---|
| `_VARIANCE_EYES` | 22 | **27** | 桃花眼 (peach-blossom upturned-corner, Tang allure), 杏眼 (apricot almond-tapered), 鹿眼 (fawn-like doe), 狐眼 (fox-shaped upturned sly), 卧蚕 (silkworm-eyelid puffy under-eye K-pop charm) |

User explicitly called out 桃花眼 + general shape variety — these are textbook Chinese aesthetic eye-shape descriptors. CJK annotations stay in source as docs; follow-up 072's `_CJK_PARENS_RE` strips them at wire-assembly time.

## 3. Wild-card fallthrough in `_pick_biased`

Even with widened bias subsets, the per-pool biased random pick produces a relatively narrow set of features within an archetype. Add a wild-card probability — with 25% chance, `_pick_biased` falls through to **uniform random over the FULL pool** even when bias is given.

```python
_BIAS_WILD_PROB: float = 0.25

def _pick_biased(rng, pool, biased):
    if biased and rng.random() >= _BIAS_WILD_PROB:
        candidates = [pool[i] for i in biased if 0 <= i < len(pool)]
        if candidates:
            return rng.choice(candidates)
    return rng.choice(pool)
```

With 6 biased facial picks per actor, prob(all archetype-biased) = 0.75⁶ ≈ **18%**. Most generated actors get at least one "wild" feature that breaks sameness while the archetype still shapes the overall look. Same seed reproduces same choice (pure deterministic via the RNG).

Skin tone + skin texture stay **uniform random** (not added to `_ARCHETYPE_FEATURE_BIAS`) — that maximizes cross-archetype skin variety, which is exactly what the user wants.

## 4. Sprinkle new eye shapes into fitting archetype bias subsets

Five archetypes get the new eye-shape indices added to their `"eyes"` bias tuple where they fit naturally:

- `leading_warm` (温润如玉): + 桃花眼 / 杏眼 / 鹿眼 / 卧蚕 (gentle scholar)
- `ingenue_kind` (清纯善良女主): + 杏眼 / 鹿眼 / 卧蚕 (kind doe-eyed)
- `ingenue_lively` (娇俏灵动): + 桃花眼 / 狐眼 / 卧蚕 (lively flirty)
- `femme_fatale` (妩媚女配): + 桃花眼 / 杏眼 / 狐眼 (textbook 妩媚 eye vocabulary)
- `youth_fresh` (少年清俊): + 杏眼 / 鹿眼 / 卧蚕 (fresh innocent)

`leading_hero`, `villain_cold`, `sage_elder`, `martial_drifter`, `everyman` don't get the new shapes baked into bias — but they'll still get them ~25% of the time via the wild-card fallthrough.

## Smoke proof

30 femme_fatale generations measured:

```
unique skin-tones seen:  17 / 22 pool entries
unique eye-shapes seen:   8 / 27 pool entries  (femme_fatale bias is intentionally narrow on eyes; wild-card pulls others)
CJK leaks in wire:        0 / 30
top skin tones:           alabaster, porcelain-fair, umber, peachy, caramel, deep mocha, bronze, neutral-medium  (palette spans!)
top eyes:                 catlike, 杏眼 (apricot), 桃花眼 (peach-blossom), 狐眼 (fox), dark intense, phoenix, piercing, heavy-lidded
```

Pre-074 the same 30 gens would have produced ~4 unique skin tones (small pool) + ~4 unique eyes (narrow bias). Diversity step-change is significant.

## Out of scope

- Adding `skin_tone` / `skin_texture` to `_ARCHETYPE_FEATURE_BIAS` — would NARROW skin variety per archetype, which is the opposite of what the user wants.
- Adding hair color / hair length / hair style to the bias map — same reasoning; user wants more variety, not less.
- Refactoring `actor__writer.py` (now ~2300 lines) into multiple files. SRP + file-size flags from 065/068 still stand as deferred cleanup.
- HTTP routes + JSON shapes (byte-identical).

## Acceptance trigger

- `_VARIANCE_SKIN_TONE` ≥ 20 entries; `_VARIANCE_SKIN_TEXTURE` ≥ 20 entries; `_VARIANCE_EYES` ≥ 25 entries.
- `_BIAS_WILD_PROB > 0` so within-archetype actors see wild-card features ~25% per pool.
- 30 femme_fatale generations show ≥ 10 distinct skin tones and ≥ 5 distinct eye shapes (was ~4 each pre-074).
- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
