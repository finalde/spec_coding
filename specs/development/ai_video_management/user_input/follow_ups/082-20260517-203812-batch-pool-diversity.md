# Follow-up draft 082 — 2026-05-17
Within-batch diversity for actor generation: for every face/body pool (eyes / nose / lips / brow / contour / skin / body) **no two slots in the same batch share the same descriptor** unless the pool is genuinely exhausted. User-fixed dropdown attrs (ethnicity / gender / age_range / look / style / resolution) still apply to all slots verbatim — only the pool draws diversify.

## Why

User: "对一个batch里，除了我explictly选择的外，在同一个batch里不得有重复的，比如我选择的asian，25岁，美丽型的，那这个batch里的10张图都要符合这些，但是我没选择的部分，要强制他们不一样，比如一个嘴大，另一个就一定嘴小，一个眼睛大另一个就一定眼睛小，一个高，另一个就矮，一个丰满另一个就苗条等等，凡是我没提到的，都要体现出多样性".

Mapping the examples to the existing prompt builder:
- 嘴大 / 嘴小 → `_LIPS_ZH` pool (22 entries)
- 眼大 / 眼小 → `_EYES_ZH` pool (22 entries)
- 高 / 矮 → `_BODY_ZH` pool (22 entries; height-axis: 高挑修长 vs 娇小玲珑 vs ...)
- 丰满 / 苗条 → `_BODY_ZH` pool (girth-axis: 丰满圆润 vs 纤瘦苗条 vs ...)

All four examples are face/body POOL draws (not dropdown attrs). Today each parallel `count=1` call seeds its own `random.Random(seed)` independently and runs `_pick / _pick_biased(rng, pool, bias)` per pool, so collisions across slots are pure birthday-problem chance — for a pool of 22 + 10 slots, expected unique = ~10 * (1 - (1 - 1/22)^9) ≈ 4 distinct pool values per batch in the worst case (lots of duplicates). User sees "10 张脸都长一样".

## Design — batch coordination via deterministic per-slot pre-resolution

The current frontend fires N parallel `count=1` calls to `preview_prompts` (one per slot, each with its own seed + per-slot rolled random_dims). To coordinate without server-side shared state, each call receives THREE small body fields:

- `batch_seed: int` — shared across all N calls in the same batch click (frontend sets it once per "preview" or "generate" click).
- `batch_size: int` — the N (= the user's count).
- `slot_index: int` — this call's 0-based position in the batch.

When all three are provided, the backend:

1. Seeds a `batch_rng = random.Random(batch_seed)` (independent of per-slot `seed`).
2. For each of the 7 pools, calls `_batch_sample_pool(batch_rng, pool_len, bias_indices, batch_size)` to get a list of `batch_size` distinct indices. **Same batch_seed across all N calls produces the same list — each parallel call independently recomputes the same list.**
3. Picks `pool_indices[slot_index]` for this slot's draw.
4. Hands those pre-resolved picks to a new `build_face_prompt_with_picks(attrs, seed, archetype, picks=...)` (and `body_` variant).

When `batch_seed/batch_size/slot_index` are absent (legacy call, e.g., `count=1` standalone, or pre-082 frontend), backend keeps current per-slot independent `_pick_biased` draws — full backward compat.

### `_batch_sample_pool(batch_rng, pool_len, bias_indices, count, wild_prob=_BIAS_WILD_PROB)` algorithm

Goal: return `count` distinct indices, **bias-preferred but exhaust-then-fall-through** + retain follow-up 074's 25% wild-card variance.

```
1. wild_count = sum(batch_rng.random() < wild_prob for _ in range(count))
2. bias_count = count - wild_count
3. bias_pool = list(bias_indices or []); batch_rng.shuffle(bias_pool)
4. full_pool = list(range(pool_len)); batch_rng.shuffle(full_pool)
5. biased_taken  = bias_pool[:bias_count]                       # may be shorter than bias_count
6. used = set(biased_taken)
7. fallthrough_needed = bias_count - len(biased_taken)
8. fallthrough_pool = [i for i in full_pool if i not in used]
9. fallthrough_taken = fallthrough_pool[:fallthrough_needed]
10. used.update(fallthrough_taken)
11. wild_pool = [i for i in full_pool if i not in used]
12. wild_taken = wild_pool[:wild_count]
13. picks = biased_taken + fallthrough_taken + wild_taken
14. batch_rng.shuffle(picks)        # so wild-cards don't always land at the end-slots
15. # If still short (count > pool_len), cycle from full_pool[0:]
16. while len(picks) < count: picks.append(batch_rng.choice(range(pool_len)))
17. return picks[:count]
```

Notes:
- Steps 4–10 implement **exhaust-bias-first, then fall through to full pool** (user choice in this turn's clarification).
- Wild-card semantics from 074 preserved at the batch level: ~25% of slots get a free-roam pick (so within-batch you can still see, e.g., a `sinister` female with a wild-card "桃花眼" against 9 sinister-biased eyes).
- The shuffle on line 14 prevents structural bias where slot 0 always gets a bias-pick and slot N-1 always gets a wild-card.
- Deterministic in `(batch_seed, pool_len, bias_indices, count, wild_prob)` — every parallel call computes identical picks.

### Frontend integration (5-line change)

In `apps/ui/src/components/ActorPoolGenerator.tsx::onPreview`:

```ts
const batchSeed = Date.now();          // NEW — one per click
const slotPlans = [...slots].map((_, i) => ({
  seed: batchSeed + i,                  // existing per-slot seed unchanged in shape
  attrs: rollSlot(...),                 // existing per-slot random_dims roll
}));
await Promise.all(slotPlans.map((plan, i) => previewPrompts({
  count: 1,
  ...plan.attrs,
  seeds: [plan.seed],
  batch_seed: batchSeed,                // NEW
  batch_size: slotPlans.length,         // NEW
  slot_index: i,                        // NEW
})));
```

Same 3 fields plumbed into the `onConfirmGenerate` worker-pool that fires `generateBatch` per slot (so actual Kling-generation gets the same pool-diversity).

### Backend signatures

- `actor__chinese_prompt.py`:
  - New `_batch_sample_pool(batch_rng, pool_len, bias_indices, count, wild_prob=_BIAS_WILD_PROB) -> list[int]` (module-private helper).
  - New `build_face_prompt_with_picks(attrs, seed, archetype, picks: dict[str, int]) -> str` (new public function alongside existing `build_face_prompt`). `picks` keys = `'eyes', 'nose', 'lips', 'brow', 'contour', 'skin', 'body'`, values = pool indices.
  - New `build_body_prompt_with_picks(attrs, seed, archetype, picks: dict[str, int]) -> str` (sibling).
  - Existing `build_face_prompt` / `build_body_prompt` unchanged (used by legacy paths + `count=1` no-batch calls).

- `actor__writer.py`:
  - `ActorPool.preview_prompts(...)` gains optional kwargs: `batch_seed: int | None = None, batch_size: int | None = None, slot_index: int | None = None`. When all three provided, route through new `_resolve_batch_picks` helper + call `build_face_prompt_with_picks`. Else current behavior.
  - `ActorPool._resolve_batch_picks(batch_seed, batch_size, slot_index, attrs, archetype) -> dict[str, int]` builds the `picks` dict by running `_batch_sample_pool` per pool with the right bias subset (look_bias > archetype_bias > None). All 7 pools resolved at once for this slot.
  - `ActorPool.generate_batch(...)` gains the same 3 optional kwargs and forwards to the same `_resolve_batch_picks` per slot, then to `build_face_prompt_with_picks`.
  - `_classify_actor_attrs` + look-led routing (079) unchanged.

- `apps/api/routes/actor__route.py` Pydantic bodies for the two endpoints gain optional `batch_seed / batch_size / slot_index` ints.

- `libs/application/queries/actor__query.py::ActorQuery.preview_prompts` + `libs/application/commands/actor__command.py::ActorCommand.generate` re-export the 3 kwargs and forward.

- `libs/domain/repositories/actor__repository.py::ActorRepository` Protocol gains the 3 optional kwargs on both methods (Protocol must match concrete `ActorPool`).

- `apps/ui/src/api.ts`: `previewPrompts(...)` + `generateBatch(...)` request types add the 3 optional fields.

### Why "still 7 pools coordinated" only — not the 6 dropdowns

User chose "Pools only" in clarification: the four concrete examples (嘴 / 眼 / 高矮 / 丰满苗条) are all face/body POOL attributes, not dropdowns. Random-dropdown diversity for unfixed attrs (e.g., 10 slots with 10 distinct age_ranges when age is set to 随机) is deferred — would require either single `count=N` call or a coordinated `random_dims` parameter through the frontend roll path. Phase-2 follow-up if user wants it later.

## Out of scope

- Random-dropdown attr diversity (the 6 dropdowns). Today each slot rolls its own random_dim on frontend independently; collisions can happen for low-cardinality dims (e.g., gender ∈ {male, female} with count=10 will always have ≥5 dupes per gender, but that's expected for the binary).
- The diverse-mode preview/generate path (`preview_diverse_prompts` / `generate_diverse_batch` from follow-up 059). That path uses `_distribute_archetypes` for cross-archetype variance and is conceptually orthogonal to within-archetype pool diversity. Optional second-phase follow-up to apply the same batch coordination to the diverse path.
- Look_bias / `_LOOK_OVERLAY_ZH` (077) — bias map intact; only the sampler swaps from per-slot independent to batch-coordinated.
- Wild-card probability `_BIAS_WILD_PROB = 0.25` (074) — preserved; applied at the batch level (~25% of slots in a batch are wild).
- HTTP route paths / response shapes — unchanged (only request bodies gain 3 optional fields, backward-compat).

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — new `_batch_sample_pool` helper + new `build_face_prompt_with_picks` + `build_body_prompt_with_picks`.
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py` — `ActorPool.preview_prompts` + `ActorPool.generate_batch` gain 3 optional kwargs + `_resolve_batch_picks` private helper.
- `projects/ai_video_management/libs/domain/repositories/actor__repository.py` — `ActorRepository` Protocol signatures align.
- `projects/ai_video_management/libs/application/queries/actor__query.py` — `ActorQuery.preview_prompts` forwards.
- `projects/ai_video_management/libs/application/commands/actor__command.py` — `ActorCommand.generate` forwards.
- `projects/ai_video_management/apps/api/routes/actor__route.py` — Pydantic bodies for preview + generate endpoints.
- `projects/ai_video_management/apps/ui/src/api.ts` — TypeScript request types.
- `projects/ai_video_management/apps/ui/src/components/ActorPoolGenerator.tsx` — compute `batchSeed` once per click + pass 3 fields per parallel call (preview + generate worker pool).
- `specs/development/ai_video_management/changelog.md` — append 082 entry.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump.
