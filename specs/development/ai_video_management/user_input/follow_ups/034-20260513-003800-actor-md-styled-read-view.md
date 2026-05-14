# Follow-up draft 034 — 2026-05-13

**Summary:** Actor sidecar markdown (`ai_videos/_actors/actor_NNNN/actor_NNNN.md`) gets a dedicated, visually friendly read-only view (no bulk-selection / SiblingMedia toolbar).

## Source

> under ai_video_management, for actors, on the actor_NN.md file lets remove the bottom bulk selection section, we dont need it. Also put the prompt in read mode by default, and make it style and visual friendly

## Abstracted instruction

1. **Drop bulk-selection UI from actor pages.** When the currently-viewed markdown path matches `^ai_videos/_actors/actor_[^/]+/actor_[^/]+\.md$`, do NOT render `SiblingMedia` (which carries the Select-all / Clear / Archive-Selected toolbar + per-tile checkboxes). Actor folders hold only one face image + the sidecar md; the batch-archive surface is dead weight there.
2. **Replace generic markdown render with an `ActorView` custom view** (sibling of `ImageRefView` / `CastingView`):
   - Face image displayed prominently at the top (large, centered, via `/api/media`).
   - Metadata table (ethnicity / gender / age_range / look / style / notes / seed) rendered as a clean key/value grid — not the raw markdown table.
   - Generation prompt shown in a **read-mode** styled card (monospace block on a soft background) with a one-click **Copy** button. The prompt text is the same string already stored under the `## 生成 prompt` code-block; the view extracts that fenced block and shows it raw.
   - Read-only by default — no `Edit` toggle inside the view (the parent `Reader` toolbar still shows the global Edit button, so power users can fall back to raw-markdown editing).
3. **Routing rule.** Detection lives in `Reader.tsx`'s render-mode dispatch (`isActor` flag, parallel to `isImageRef` / `isCasting`). When true, render `<ActorView .../>` and **skip** `<SiblingMedia .../>`.
4. **CSS lives in `frontend/src/styles.css`** under a new `/* ActorView */` block — reuse `--bg-panel`, `--border`, `--text-muted` tokens; image max-height ≤ `60vh`; prompt card uses the existing `--pre-bg` / `--pre-fg` tokens for consistency with `CodeView`.
5. **No backend change.** Pure frontend dispatch + styling. The sidecar md schema is unchanged (still the canonical edit target for power users).
6. **Out of scope.** ActorGrid card style is not touched (different surface; covered by follow-ups 028/030/032). The actor folder's archive/ subfolder — if present — also vanishes from view alongside SiblingMedia; that's intentional, archive ops for actor faces happen via the grid bulk-delete (030) and the per-actor delete button (026), not per-image archive.

## Why now

The actor sidecar md was rendered through the generic markdown branch, which inherits SiblingMedia. With one image per actor folder, the bulk-selection toolbar is noise. The prompt block is the most-copied piece of content on that page and deserves a styled, single-click-to-copy treatment.

## Acceptance

- Navigating to `/file/ai_videos/_actors/actor_0013/actor_0013.md` shows: large face image, key/value metadata block, prompt card with Copy button — and NO bulk-selection toolbar / "Select all" buttons / per-tile checkboxes.
- Global `Edit` button in `Reader`'s top toolbar still flips to the raw-markdown editor (power-user escape hatch).
- Other markdown surfaces (shotlist, casting, ref_images, generic project md) are unchanged.
