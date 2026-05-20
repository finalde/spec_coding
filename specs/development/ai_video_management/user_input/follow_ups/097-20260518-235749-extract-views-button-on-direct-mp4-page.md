# Follow-up draft 097 — 2026-05-18
Add the 🖼 "提取三视图+音频" button to the direct-video-view page in `Reader.tsx`, not just inside `SiblingMedia.tsx`. Follow-up 093 wired the button on per-tile thumbnails inside the SiblingMedia panel (which only renders below md / shot-pair / image-ref files), but a user navigating directly to an mp4 (e.g., clicking a video filename in the tree) sees the inline `<video controls>` block at `Reader.tsx:261-286` which only carries 🎞 Extract Frames / 📦 Archive / 🗑 Delete — no 🖼 button.

## Why

User this turn: "make the button appear on each mp4 page please". Discovered when the user re-rendered v10 character turntable mp4s and opened one directly via the file tree — couldn't find the extract-3-views button. The button does exist, but only on the SiblingMedia panel (the sibling-files strip shown below a markdown file's content), so the user had to navigate to the character `.md` file first and scroll past the markdown to find it on a tile thumbnail. That extra navigation step defeats the point of having direct-mp4 navigation.

The 🎞 Extract Frames button already lives in BOTH places (per follow-up 062 which added the direct-mp4 extract button alongside the sibling-panel version). Follow-up 093 only wired the new 🖼 button to the sibling panel — this turn closes that asymmetry.

## Design

Two-file change, parallels the 🎞 Extract Frames dual placement:

1. **`apps/ui/src/components/SiblingMedia.tsx`** — export `isCharacterVideoPath` and the underlying `CHARACTER_VIDEO_PATH_RE` so Reader.tsx can reuse the same path-shape gate without duplicating the regex. Currently `isCharacterVideoPath` is module-private; promote it to a named export. No behavior change in SiblingMedia itself.

2. **`apps/ui/src/components/Reader.tsx`** — add the 🖼 button to the direct-video block at lines 261-286:
   - New import: `extractCharacterViews` from `../api`, `isCharacterVideoPath` from `./SiblingMedia`.
   - New state: `const [extractingViews, setExtractingViews] = useState<boolean>(false);` parallels the existing `extracting` state for the 🎞 button.
   - New handler `onExtractCharacterViewsClick`: parallels `onExtractFramesClick` — disables itself while busy, calls `extractCharacterViews(path)`, announces toast with success / failure counts, triggers `onSaved()` to refresh the tree (so the new `views/` subfolder appears).
   - New derived value `viewsExtractLabel`: `"⏳ 提取中…"` while busy, `"🖼 提取三视图+音频"` otherwise (byte-identical wording to SiblingMedia for consistency).
   - Update `mediaActionsBusy = archiving || deleting || extracting || extractingViews;` so all 4 mutually-blocking actions disable each other.
   - Render the 🖼 button between the existing 🎞 and 📦 buttons inside the `<div className="reader-media-actions">` at line 265, gated by `isCharacterVideoPath(path) && !isArchivedFile` — same gate logic as the SiblingMedia tile.

Toast wording mirrors SiblingMedia's behavior: success = `Extracted N views + audio from ${name} → views/` (or `Extracted N views + audio from ${name} (M failed)` if any of the 4 outputs failed), failure = `Extract views failed: ${kind}`. Same `archiveErrorKind` helper for the error tag.

No new endpoint / route / Cdto / mapper changes — the wire-up already exists from follow-up 093. This is a pure frontend dual-placement parity fix.

## Out of scope

- No change to extract behavior, timestamps, or output file naming — all driven by `CANONICAL_VIEWS` value object (follow-up 093 + 096).
- No change to SiblingMedia button (still renders on each tile in the sibling panel; this follow-up just adds a SECOND placement on the direct-video-view page).
- No keyboard shortcut for the new button (deferred — Reader has no shortcut for the existing 🎞 button either).
- No batch-extract-all-character-mp4s button at the character-folder level (deferred per 093 "out of scope").
- No tooltip rewording — the SiblingMedia button's title still says "v9 character turntable (15s slow-orbit)" which is stale post-096; that's a separate cleanup not bundled here to keep the diff focused on the dual-placement parity.

## Touch list

- `projects/ai_video_management/apps/ui/src/components/SiblingMedia.tsx` — promote `isCharacterVideoPath` (and optionally `CHARACTER_VIDEO_PATH_RE`) from module-private to named export. Single-line `function` → `export function` change.
- `projects/ai_video_management/apps/ui/src/components/Reader.tsx` — add import + state + handler + label + button-render-block + update mediaActionsBusy.
- `specs/development/ai_video_management/user_input/revised_prompt.md` — header bump 097.
- `specs/development/ai_video_management/changelog.md` — append 097 entry.
