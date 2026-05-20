# Follow-up draft 078 — 2026-05-17
Fix actor-preview prompt 综合描述 contradicting the user's selected `look`.

## Bug

Preview a single actor with `look=sinister` (阴邪) + `gender=female`. The prompt's 综合描述 line came back as `"一位市井百姓, 朴实无华, 邻家亲切, 烟火气十足"` — the `everyman` archetype's synthesis line, which directly contradicts the user's selected sinister direction.

## Root cause

`_classify_actor_attrs` (in `libs/infrastructure/writers/actor__writer.py`) required all four attrs to match a single archetype's tuples: `gender_filter`, `age_range`, `look`, `style`. When the user picked `look=sinister + gender=female`, no archetype matched because the only `sinister`-tagged archetype was `villain_cold` (gender_filter=male). The classifier fell through to `_ARCHETYPE_FALLBACK_SLUG = "everyman"`, and `_SYNTHESIS_BY_ARCHETYPE["everyman"]` is the "市井百姓 烟火气" line — the same regardless of what look the user picked.

The same class of mismatch silently fired for every "evil" look on a female actor (`sinister`, `cunning` had no female archetype), every "sultry" look on a male (`seductive` had no male archetype), every "noble" female (`righteous` was male-only), every "innocent" male (`innocent` was female-only).

## Fix (two-part)

1. **Classifier is now look-led with progressive relaxation.** `_classify_actor_attrs` walks four priorities:
   1. Strict 4-way match (legacy follow-up 053 path — preserves deterministic distribution for diverse mode).
   2. gender + look + (age OR style) — relax the weakest axis.
   3. gender + look — look dominates archetype identity.
   4. look alone — lift gender constraint as last resort.
   5. fallback `everyman`.

   This means the user's chosen look NOW dominates the archetype synthesis line even when other attrs don't perfectly fit one archetype's tuples.

2. **`_ARCHETYPES.looks` tuples cross-gendered** for the 5 looks added in follow-up 064 that had only one gendered home:
   - `femme_fatale.looks` += `("sinister", "cunning")` — female evil now maps cleanly.
   - `leading_warm.looks` += `("seductive",)` — male sultry.
   - `ingenue_kind.looks` += `("righteous",)` — female noble.
   - `youth_fresh.looks` += `("innocent",)` — male innocent (this archetype is already `gender_filter=both`).

## Verification

Smoke ran on 10 edge-case combos including the user's exact case. All resolve to a look-coherent archetype:

```
sinister female 26-35 modern   -> femme_fatale  (was: everyman ← BUG)
sinister female 18-25 ancient  -> femme_fatale
sinister male 26-35 ancient    -> villain_cold  (legacy path)
cunning female 26-35 modern    -> femme_fatale
seductive male 26-35 business  -> leading_warm
seductive female 26-35 ancient -> femme_fatale
righteous female 18-25 modern  -> ingenue_kind
innocent male 18-25 streetwear -> youth_fresh
seductive female 65+ fantasy   -> femme_fatale  (age mismatch but look dominates)
handsome male 18-25 ancient    -> leading_hero  (legacy 4-way path intact)
```

## Touch list

- `libs/infrastructure/writers/actor__writer.py::_classify_actor_attrs` — rewritten as 4-priority look-led classifier.
- `libs/infrastructure/writers/actor__writer.py::_ARCHETYPES` — `looks` tuples extended for `femme_fatale`, `leading_warm`, `ingenue_kind`, `youth_fresh`.

## Out of scope

- The feature-bias subset selection (`_ARCHETYPE_FEATURE_BIAS`) is unchanged; bias rows already exist for every archetype slug, so the new cross-gender mappings inherit appropriate facial-feature bias automatically.
- No changes to diverse-mode batch generation (`generate_diverse_batch`) — that path still uses `_ARCHETYPES`-driven plan distribution which is unaffected.
- No frontend changes; the bug was fully backend-side.
