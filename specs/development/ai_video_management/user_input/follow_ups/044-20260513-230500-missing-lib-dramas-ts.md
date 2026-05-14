# Follow-up draft 044 — 2026-05-13

**Summary:** Vite import error `[plugin:vite:import-analysis] Failed to resolve import "../lib/dramas" from "src/components/ActorView.tsx"`. Follow-up 043 item #9 directed extracting `extractDramas` + `findChild` + `DramaChoice` from `ActorGrid.tsx` into a shared `src/lib/dramas.ts`, and updated the imports in both `ActorGrid.tsx` and `ActorView.tsx` accordingly — but the new file itself was never written. Implementation gap, not a behavior change.

## Source

> got front end error: `[plugin:vite:import-analysis] Failed to resolve import "../lib/dramas" from "src/components/ActorView.tsx". Does the file exist?`

## Abstracted instruction

1. **Create `apps/ui/src/lib/dramas.ts`** exporting:
   - `interface DramaChoice { path: string; name: string; characters: string[]; }`
   - `function extractDramas(tree: TreeNode | null): DramaChoice[]` — finds the `ai_videos` directory inside the tree, lists each `type === "directory"` child whose name does NOT start with `_`, and for each drama lists subdirectories under `characters/` matching `^c\d+(_.*)?$`. Returns `DramaChoice[]`.
   - `function findChild(node: TreeNode, name: string): TreeNode | null` — first-level lookup by name.
   - Byte-for-byte equivalent to the inline logic that lived in `ActorGrid.tsx` before follow-up 043 — zero behavior change. (Function bodies were captured from the last commit before the follow-up 043 edits removed them.)

2. **No edits needed to `ActorGrid.tsx` / `ActorView.tsx`** — they already import from `../lib/dramas`. They just need the file to exist.

3. **No backend changes.** Imports, API routes, JSON shapes, casting/character_link semantics all unchanged.

## Why

Follow-up 043's spec walk on the frontend was incomplete: the import-extract step landed in the two consumer files but the producer file (`lib/dramas.ts`) was never written. The drama-extraction logic was deleted from `ActorGrid.tsx` (because the comment in the spec says "moved"), leaving an unresolved import at first run. This fixes the gap without changing semantics.

## Acceptance

- `cd projects/ai_video_management/apps/ui && npm run dev` boots without the `Failed to resolve import "../lib/dramas"` overlay.
- ActorView's "+ 添加分配" form renders the drama dropdown with the live list of `ai_videos/{name}/` directories (non-`_` prefix).
- ActorGrid's bulk assign modal shows the same drama list.
- Selecting a drama in either component populates the role dropdown with the matching `characters/c*/` subfolders.
- Zero behavior delta vs. follow-up 043's intended behavior — the file should have existed since 043.
