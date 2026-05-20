# Follow-up draft 094 — 2026-05-18
Add 外貌气质 (`look` attribute) as the 5th filter dropdown on the actor grid page, parallel to the existing 民族 / 性别 / 年龄段 / 分配状态 filters.

## Why

The actor tile already displays the actor's `look` value as a chip (e.g., `sinister` / `seductive` / `cunning`), and `look` is one of the user-selected attributes during actor generation. Users browsing the pool naturally want to filter to "show me all 阴邪 actors" the same way they filter by 民族 / 性别 / 年龄段. The filter row is the established pattern; the new dropdown is mechanically parallel.

The `look` attribute has special weight in actor generation per follow-up 077 (look-dominates-feature-bias) + follow-up 079 (look-led-archetype-classification), so a per-look filter is also useful for QC ("did the sinister actors actually render as 阴邪?") and for batch operations (selecting all 阴邪 actors to assign to a particular character archetype).

## Design

Frontend-only change in `apps/ui/src/components/ActorGrid.tsx`:

1. Add `filterLook` state (initial value `FILTER_ALL`).
2. Add 5th predicate to `filteredActors` useMemo: `if (filterLook !== FILTER_ALL && a.look !== filterLook) return false;`.
3. Add `filterLook` to the page-reset useEffect dependency array (so changing the filter resets to page 1).
4. Add a new `<label>外貌气质 <select>…</select></label>` block in the `.actor-grid-filters` group, populated from `ATTR_OPTIONS.look` — matches the existing pattern (label in Chinese, option values are English slugs to match the chip display on each tile).

No backend changes. No API changes. No new types. `actor.look` is already in `ActorInfo` per `apps/ui/src/api.ts:166` and the 13 canonical values are already in `ATTR_OPTIONS.look` per `api.ts:328`.

## Out of scope

- No re-ordering of filter dropdowns; the new one goes at the end of the row.
- No grouping of look values into "physical appearance" vs "character archetype" subgroups (the original 077/079 distinction). The flat 13-item list matches the existing dropdown UX. A future polish could collapse into 2 `<optgroup>` if the list grows.
- No localization of option labels (slugs in English). Existing dropdowns use the same slug-only pattern; changing one would create UX inconsistency.

## Touch list

- `projects/ai_video_management/apps/ui/src/components/ActorGrid.tsx` — add `filterLook` state, predicate, page-reset dep, dropdown.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump.
- `specs/development/ai_video_management/changelog.md` — append 094 entry.
