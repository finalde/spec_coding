# Follow-up draft 071 — 2026-05-17

Deepen the actor-generation prompt diversity and make archetypes look coherent end-to-end. Two coupled changes to `libs/infrastructure/writers/actor__writer.py`:

1. **Expand the 6 facial-feature variance pools** to ≥ 20 entries each. The user specifically called out Chinese-aesthetic descriptors that the existing English pools didn't cover well: 大眼 / 小眼 / 圆眼 / 丹凤眼 / 泪眼 for eyes; 蒜头鼻 / 驼峰鼻 / 高挺鼻梁 for nose. Each missing variant is now an explicit pool entry with the Chinese term inline in parentheses.
2. **Add an archetype → feature-bias map** so each of the 10 existing archetypes (`leading_hero` / `leading_warm` / `ingenue_kind` / `ingenue_lively` / `femme_fatale` / `villain_cold` / `sage_elder` / `martial_drifter` / `everyman` / `youth_fresh`) draws from a **coherent subset** of indices in each facial-feature pool. So 英俊男主 (`leading_hero`) lands `square strong / Roman-bust / chiseled` jaws with `phoenix eyes` and `deep-set piercing` gaze; 妖艳女配 (`femme_fatale`) lands `V-shaped / swan-neck / catlike` jaws with `heavy-lidded sultry` eyes and `Bardot full` lips. Random-with-bias, not deterministic — same seed still reproduces the same draw.

## Required moves

### 1. Pool expansions (≥ 20 entries each)

| Pool | Before | After | New Chinese descriptors |
|---|---|---|---|
| `_VARIANCE_JAWLINE` | 10 | 22 | + heart-tapered peach, boxer wide-angle, swan-neck, catlike, weak-chin, protruding-chin, asymmetric character, apple-cheek, Asian K-beauty, ballet-trained, lantern martial, fawn-curve |
| `_VARIANCE_CHEEKBONES` | 9 | 20 | + Asian porcelain doll, painter-shadow ledged, supermodel hollow, Renaissance diffused, diamond-cut, aristocratic restraint, flat-plane heritage, barely-there youthful, asymmetric, rosy peach-flush, marble-cool platonic |
| `_VARIANCE_BROW` | 10 | 21 | + feline upward-flicked, maternal rounded, pencil 1920s, gangster heavy, asymmetric arched, pale-blonde nordic, feathered editorial, long sweeping Chinese-painting, blade-straight K-beauty, caterpillar bohemian, puppy-dog down-sloping |
| `_VARIANCE_NOSE` | 10 | 21 | + 蒜头鼻 (garlic-bulb), 驼峰鼻 (hump-bridge), 高挺鼻梁 (high-bridged dignified), small petite, wide-nostril sensual, hooked raptor, snub childlike, chiseled architectural, ski-jump romantic, flat-bridged calm, K-beauty straight-bridge |
| `_VARIANCE_LIPS` | 10 | 20 | + tea-rose Chinese-doll, downturned pouty, asymmetric crooked, Joker-wide grin, heart-shaped cartoon, Bardot voluminous, Anglo Victorian thin, glossy bee-stung, bashful tucked, actor-trained theatrical |
| `_VARIANCE_EYES` | 14 | 22 | + 大眼睛 (very large doll), 小眼睛 (petite downturned), 圆眼睛 (perfectly round saucer), 泪眼 (tear-shaped puppy), moonlit silver, amber-honey, wide-set curious, close-set concentrated |

Existing entries are preserved — additions append, never replace.

### 2. `_ARCHETYPE_FEATURE_BIAS` map

New top-level dict keyed by archetype slug. Each value is a sub-dict keyed by pool name (`"jawline" / "cheekbones" / "brow" / "nose" / "lips" / "eyes"`) → tuple of preferred indices into that pool.

Example (full map in code):

```python
"leading_hero": {  # 英俊男主气场冷峻
    "jawline":    (0, 4, 7, 13, 18),  # square / chiseled / Roman / catlike / K-beauty
    "cheekbones": (0, 3, 10, 13, 14),  # high prominent / sharply angled / painter-shadow / diamond-cut / aristocratic
    "brow":       (0, 2, 4, 7, 18),
    "nose":       (0, 3, 12, 17, 20),  # aquiline / Roman / 高挺鼻梁 / chiseled / K-beauty
    "eyes":       (1, 2, 4, 10, 15),   # 丹凤眼 / deep-set / piercing / dark intense / 小眼睛
    "lips":       (1, 7, 9, 16),
},
"femme_fatale": {  # 妖艳女配
    "jawline":    (2, 6, 12, 13),       # V-shaped / heart / swan-neck / catlike
    "cheekbones": (0, 3, 5, 10, 11),     # prominent / angled / hollow / painter-shadow / supermodel
    "brow":       (1, 4, 8, 10),
    "nose":       (4, 5, 7, 14),         # narrow model / upturned / porcelain / wide-nostril sensual
    "eyes":       (1, 4, 8, 10, 12),     # 丹凤眼 / piercing / heavy-lidded / dark intense / catlike
    "lips":       (0, 8, 11, 13, 15, 17),# sensuous / pillowy / pouty / grin / Bardot / bee-stung
},
"ingenue_kind": {  # 清纯善良女主
    "jawline":    (1, 3, 6, 8, 10, 14, 17, 21),
    "cheekbones": (1, 4, 12, 16, 18),
    "brow":       (1, 3, 11, 20),
    "nose":       (1, 2, 7, 13, 16, 18),  # gentle / button / porcelain / petite / snub / ski-jump
    "eyes":       (0, 3, 7, 11, 14, 16),  # large round / wide innocent / double-eyelid / clear / 大眼 / 圆眼
    "lips":       (0, 2, 5, 8, 10, 14),
},
# ... 7 more archetypes (leading_warm, ingenue_lively, villain_cold, sage_elder,
# martial_drifter, everyman, youth_fresh) each with the same dict shape.
```

Indices reference the post-expansion pool order (jawline 0..21, cheekbones 0..19, brow 0..20, nose 0..20, lips 0..19, eyes 0..21). A new `_pick_biased(rng, pool, biased)` helper does `rng.choice(filtered)` when bias is non-empty, falls through to `rng.choice(pool)` otherwise. Out-of-range indices are silently skipped (defends against pool reordering).

### 3. `_variance_for(seed, gender, archetype=None)`

Signature gains `archetype: str | None = None`. The 6 facial-feature picks inside the function now consult `_ARCHETYPE_FEATURE_BIAS.get(archetype or "", {})` for each pool's bias tuple. Eye picks (which sample 2 distinct entries) use a deduplicated subset when biased; ≥ 1000-char features-text guard preserved. When `archetype is None` or unknown, behavior is byte-identical to the pre-069 uniform-random sampling.

### 4. Call sites forward archetype

Four `_variance_for` call sites in this module:
- `preview_prompts(...)` — gains `archetype: str | None = None` kwarg; forwards to `_variance_for(seed, attrs.gender, archetype=archetype)`.
- `preview_diverse_prompts(...)` — already loops with a per-slot `spec: ArchetypeSpec`; forwards `archetype=spec.slug`.
- `generate_batch(...)` — already accepts `archetype` per follow-up 053; forwards to `_variance_for`.
- `generate_diverse_batch(...)` — forwards `archetype=spec.slug` (where `spec` is the per-slot `ArchetypeSpec`).

Commands / queries / DTOs / routes: **unchanged**. The `preview_prompts` archetype kwarg is optional (defaults to None → no behavioral change for callers that don't pass it).

## Out of scope

- Splitting the variance pools out of `actor__writer.py` into a dedicated `actor__variance_pools.py` (or moving them to `libs/domain/value_objects/actor__variance.py` since they're business knowledge). The SRP + file-size guidelines from 068 + 065 flag this for future cleanup — `actor__writer.py` is now ~2200 lines. Captured here so the next stage-5 review sees the deferred restructure.
- Biasing the *non*-facial pools (hair, skin, expression, lighting, mood). The user asked specifically about 五官 (facial features). Those pools stay uniform random; adding archetype bias to them would compound the seasoning without the user calling for it.
- Frontend changes. The dropdown UI already drives archetype selection through `generate_diverse_batch`; no UI change needed.
- HTTP routes + JSON shapes (byte-identical).

## Acceptance trigger

- Each of the 6 facial-feature pools has ≥ 20 entries.
- `_ARCHETYPE_FEATURE_BIAS` is keyed by all 10 archetype slugs.
- `_variance_for(seed, gender)` (no archetype) produces byte-identical output vs pre-069 for any given seed.
- `_variance_for(seed, 'male', archetype='leading_hero')` and `_variance_for(seed, 'female', archetype='femme_fatale')` produce facial-feature picks within the biased index subsets for that archetype (smoke-tested: hero gets Roman-bust jaw + sharply-angled cheeks; femme_fatale gets swan-neck jaw + sharply-angled cheeks).
- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
