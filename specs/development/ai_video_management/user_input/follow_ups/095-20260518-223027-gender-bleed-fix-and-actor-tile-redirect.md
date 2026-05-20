# Follow-up draft 095 — 2026-05-18
Two unrelated fixes bundled because both touch the actor pipeline UX:

1. **Bug fix**: batch-generating men yields ~half women. Root cause is that the 7 Chinese descriptor pools (`_EYES_ZH` / `_NOSE_ZH` / `_LIPS_ZH` / `_BROW_ZH` / `_CONTOUR_ZH` / `_SKIN_ZH` / `_BODY_ZH` in `actor__chinese_prompt.py`) contain entries with explicit gender markers — `少女`, `美人`, `闺秀`, `妩媚`, `妖艳`, `婴儿肥`, `邻家女孩`, `致命诱惑` (female-only) and `男性化`, `邻家男孩`, `阳光男孩`, `健壮型男`, `长腿欧巴`, `腹肌分明`, `魁梧` (male-only) — but `_pick_biased` and `_resolve_batch_picks` draw uniformly across the whole pool regardless of `attrs.gender`. With ~8-10 female-tagged entries per 22-entry pool, a male prompt has ~30-45% chance per pool of pulling a female descriptor; cumulative across 7 attribute draws the probability of at least one cross-gender leak is >95%, and even one or two feminine descriptors in 7 attribute lines is enough to push Kling toward female rendering.

2. **UX change**: clicking an actor tile in the grid view should redirect to the actor main page (`ai_videos/_actors/{actor_id}/{actor_id}.md`, which Reader renders via `ActorView`), not to the raw jpg viewer. The grid view's purpose is browsing the pool; the natural drill-down is the per-actor sidecar page (with bible, assignments, delete button) — the jpg is already shown as the tile thumbnail.

## Why

For (1): users running batch generation pre-select the gender attribute. The current bug breaks that user-supplied filter at the prompt level. The Kling model gets a structured prompt that says `性别：男性，眼睛：[female marker]，嘴巴：[female marker]，体型：[female marker]` — the model resolves the contradiction by leaning toward the dominant signal (the descriptive markers, since there are 7 of them vs 1 gender label). Filtering pools by gender at pick time keeps the structured prompt internally consistent.

For (2): the existing `navigate("/file/" + imagePath)` shows the jpg in the file viewer. The actor's `actor_NNNN.md` carries the full attribute table + casting assignments + delete button via `ActorView`. The md is the real "actor page"; the jpg is just a thumbnail. Users browsing the grid want to drill into the actor record, not stare at a bigger thumbnail.

## Design

### Fix 1 — gender-filtered pool draws

Approach: keep the pool tuple type unchanged (`tuple[str, ...]`), add a runtime gender filter that strips entries whose descriptor contains a cross-gender marker. The marker lists are kept small and explicit (substring match on terms that *unambiguously* imply gender identity, not physical attributes that could apply to either gender).

New helper in `actor__chinese_prompt.py`:

```python
_FEMALE_ONLY_MARKERS: tuple[str, ...] = (
    "少女", "女孩", "美人", "闺秀", "佳人", "妩媚", "妖艳", "妖媚",
    "娇憨", "楚楚动人", "致命诱惑", "贤淑", "仕女", "邻家姐姐",
    "萌妹", "娇媚柔弱", "弱不禁风", "婴儿肥",
)

_MALE_ONLY_MARKERS: tuple[str, ...] = (
    "男性化", "男性硬朗", "邻家男孩", "阳光男孩", "健壮型男",
    "长腿欧巴", "偶像身材", "腹肌分明", "魁梧", "强壮有力",
)


def _filter_pool_by_gender(
    pool: tuple[str, ...],
    bias_indices: tuple[int, ...] | None,
    gender_slug: str,
) -> tuple[tuple[str, ...], tuple[int, ...] | None]:
    """Return (filtered_pool, translated_bias_indices). Strip entries whose
    descriptor contains a cross-gender marker; translate bias_indices to
    point into the filtered pool (dropping bias entries that were stripped).
    """
    forbidden = _FEMALE_ONLY_MARKERS if gender_slug == "male" else _MALE_ONLY_MARKERS
    new_pool: list[str] = []
    old_to_new: dict[int, int] = {}
    for old_i, descriptor in enumerate(pool):
        if any(m in descriptor for m in forbidden):
            continue
        old_to_new[old_i] = len(new_pool)
        new_pool.append(descriptor)
    if bias_indices is None:
        return tuple(new_pool), None
    translated = tuple(old_to_new[i] for i in bias_indices if i in old_to_new)
    return tuple(new_pool), (translated if translated else None)
```

Call sites:

- `build_face_prompt` (line ~572) — apply filter before each `_pick_biased` / `_pick` for the 7 pools.
- `build_body_prompt` (line ~615) — same.
- `_resolve_batch_picks` (line ~402) — add `gender_slug: str` parameter; apply filter before passing each pool to `_batch_sample_pool`.

Caller of `_resolve_batch_picks`:
- `actor__writer.py:2080` — pass `gender_slug=attrs.gender`.

Marker selection rationale:
- Female markers are unambiguous identity terms (少女 / 美人 / 闺秀 / 妩媚) that Kling has strong female-female associations for. Borderline-feminine physical descriptors (e.g., "性感", "丰满") are NOT included — they describe attributes that can apply across genders even if more commonly female in Chinese aesthetic.
- Male markers are similarly identity-only (男性化 / 健壮型男 / 长腿欧巴) — physical strength terms (肌肉 / 肩宽) that could apply to muscular women are NOT included.
- The lists can be tuned later if specific bleed cases remain. The filter is fail-safe by design: if a marker is wrong, the actor just gets fewer descriptor options for that pool, not a crash.

Test plan (manual, post-deploy):
- Run preview-prompts for `gender=male, count=10, ethnicity=east-asian, look=righteous`. Verify the 10 face prompts contain ZERO of: 少女 / 美人 / 闺秀 / 妩媚 / 妖艳 etc.
- Same for `gender=female`: verify ZERO of 男性化 / 健壮型男 / 长腿欧巴.
- After fix, the rendered actor jpgs from a male batch should be >90% male (was ~50% per user report). Some residual feminizing is possible because non-marker descriptors can still bias the model — that's a follow-up if needed.

### Fix 2 — tile redirect to actor md

Single-line change in `ActorGrid.tsx:107`:

```diff
- navigate(`/file/${encodeURIComponent(imagePath)}`);
+ navigate(`/file/${encodeURIComponent(`ai_videos/_actors/${actor.id}/${actor.id}.md`)}`);
```

Reader (line 216) already detects `^ai_videos/_actors/actor_[^/]+/actor_[^/]+\.md$` and routes the file to `ActorView`. The md path is deterministic from `actor.id` (e.g., `actor_0014` → `ai_videos/_actors/actor_0014/actor_0014.md`).

The `imagePath` is no longer used by `onTileClick`; the existing closure signature stays compatible by ignoring the second argument at the call site. (Could remove `imagePath` from the closure for a cleaner signature, but that's a minor refactor not in scope.)

## Out of scope

- Not retagging every pool entry with explicit gender metadata (heavier refactor — 154 entries × 2 attributes). Substring marker filtering is the pragmatic 80/20 fix.
- Not addressing residual feminizing from non-marker descriptors (e.g., a male prompt could still draw "高颧骨, 立体感强, 模特脸" which is gender-neutral on paper but Kling might still skew female with). If empirical Kling output remains skewed >10% after this fix, options are: (a) expand marker lists, (b) introduce gender-specific sub-pools per attribute, (c) strengthen the prompt-level gender signal (e.g., repeat `性别：男性` later in the prompt).
- Not touching `_VARIANCE_*` English pools in `actor__writer.py` — those are already gendered (`_VARIANCE_FACE_FEATURES_MALE` / `_VARIANCE_FACE_FEATURES_FEMALE`). The bug is only in the new Chinese structured-prompt path (per follow-up 075).
- Tile thumbnail behavior unchanged — only the click-target changes. Users still see the jpg as the tile preview.

## Touch list

- `projects/ai_video_management/libs/infrastructure/writers/actor__chinese_prompt.py` — add 2 marker tuples + `_filter_pool_by_gender` helper; update `build_face_prompt` + `build_body_prompt` + `_resolve_batch_picks` to filter pools.
- `projects/ai_video_management/libs/infrastructure/writers/actor__writer.py` — pass `gender_slug=attrs.gender` to `_resolve_batch_picks`.
- `projects/ai_video_management/apps/ui/src/components/ActorGrid.tsx` — change tile click navigation target.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump.
- `specs/development/ai_video_management/changelog.md` — entry.
