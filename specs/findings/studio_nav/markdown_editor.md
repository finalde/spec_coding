# Research — markdown_editor — studio_nav

**Sources:**

| # | Title | URL |
|---|-------|-----|
| 1 | Strapi — 5 Best Markdown Editors for React Compared | https://strapi.io/blog/top-5-markdown-editors-for-react |
| 2 | @uiw/react-md-editor — npm | https://www.npmjs.com/package/@uiw/react-md-editor |
| 3 | uiwjs/react-md-editor — GitHub | https://github.com/uiwjs/react-md-editor |
| 4 | MDXEditor docs — Tables | https://mdxeditor.dev/editor/docs/tables |
| 5 | mdx-editor/editor — GitHub | https://github.com/mdx-editor/editor |
| 6 | Tiptap Markdown — Install | https://tiptap.dev/docs/editor/markdown/getting-started/installation |
| 7 | Tiptap Markdown — API | https://tiptap.dev/docs/editor/markdown/api/extension |
| 8 | Lexical — @lexical/markdown | https://lexical.dev/docs/packages/lexical-markdown |
| 9 | Lexical — @lexical/table | https://lexical.dev/docs/packages/lexical-table |
| 10 | Milkdown — React recipe | https://milkdown.dev/docs/recipes/react |
| 11 | Milkdown — Crepe bundle-size issue #1533 | https://github.com/Milkdown/milkdown/issues/1533 |
| 12 | Milkdown discussion #134 — vs Tiptap | https://github.com/orgs/Milkdown/discussions/134 |
| 13 | Liveblocks — Which rich text editor in 2025 | https://liveblocks.io/blog/which-rich-text-editor-framework-should-you-choose-in-2025 |
| 14 | react-simple-code-editor — GitHub | https://github.com/react-simple-code-editor/react-simple-code-editor |

**Key findings (≤500 tokens):**
- Our v1 needs are modest: view/edit toggle, GFM (incl. tables), syntax-highlighted code blocks, manual save. No autosave, no collab, no required image paste. That rules out heavyweight WYSIWYG frameworks (Tiptap, Lexical, Milkdown) where the cost-to-value is poor for files we want to keep as plain authored markdown round-trippable to disk.
- **`@uiw/react-md-editor`** is the strongest fit: ~4.6 kB gzipped (Strapi), TS-native, GFM via remark-gfm, code-block syntax highlighting built in, and a built-in `preview` prop with three modes (`'edit' | 'live' | 'preview'`) that maps directly to our view/edit toggle requirement (uiwjs docs). Built on a textarea, not CodeMirror/Monaco — so it does not collide with the Monaco we already need for `plan.yaml` in the Execution Plan module. Library-agnostic; styles are CSS-variable-driven and behave fine inside Mantine, AntD, or shadcn shells.
- **MDXEditor** is a WYSIWYG markdown editor on Lexical with a great table UX, but ships **~851 kB gzipped** (Strapi). It also targets MDX (component embedding) — overkill for a single-user local studio editing repo files we want to remain *exactly* the markdown the user typed. Its WYSIWYG round-trip can normalize markdown in ways that surprise authors editing `CLAUDE.md` / `SKILL.md`.
- **Tiptap** does not output markdown natively (Liveblocks 2025 review; Milkdown #134); requires `tiptap-markdown` add-on with `markedOptions.gfm: true` to enable tables/tasklists. Excellent React story, but heavy ProseMirror runtime and lossy markdown round-trip make it wrong for files like `qa.md` and agent `.md` that must stay authored-by-hand.
- **Lexical** is type-safe and modular but has no out-of-the-box markdown editor — you compose plugins (`@lexical/markdown` shortcuts + `@lexical/table` etc.). Highest integration cost; nested tables are explicitly blocked.
- **Milkdown** (incl. Crepe) is plugin-based on ProseMirror with first-class GFM preset, but issue #1533 documents that Crepe ships all CodeMirror languages even when disabled, and Discussion #1120 (cited by Liveblocks/Strapi) calls React integration "bare-bones and unconventional."
- **react-markdown-editor-lite**: ~69 kB total, 17 plugins, image upload — but the package is unmaintained (no recent commits per Strapi); risky for a project that has to keep building cleanly on React 18+.
- **Plain `<textarea>` + react-markdown preview**: zero added deps (we already have `react-markdown` + `remark-gfm`). Adequate fallback, but no toolbar, no synced scroll, no live mode — meaningful UX gap vs. `@uiw/react-md-editor` for a 4.6 kB cost.
- The **Interview Q&A** module is structurally not free-form markdown — it is question cards with a typed schema (question, options, picked option, notes). It should be a **custom React component**, not a generic markdown editor; only the `notes` field on each card should drop down to markdown editing, and even that can be a small textarea with preview.

## Detailed notes

### TipTap
- URL: https://tiptap.dev/docs/editor/markdown/getting-started/installation , https://tiptap.dev/docs/editor/markdown/api/extension
- ProseMirror-based React editor. Markdown is **not** native — you install `tiptap-markdown` and pass `markedOptions: { gfm: true }` to enable GFM tables and task lists.
- Rich React integration (hooks, components). Liveblocks 2025 review notes: "Tiptap does not support Markdown output natively."
- Bundle: large (full ProseMirror + each StarterKit extension). Public bundlephobia data not retrievable in this run, but Strapi/Liveblocks both flag it as heavyweight.
- Friction with our stack: writes back lossy/normalized markdown — bad for files round-tripped to git (`CLAUDE.md`, `SKILL.md`, agent `.md`).

### Lexical (Meta)
- URLs: https://lexical.dev/docs/packages/lexical-markdown , https://lexical.dev/docs/packages/lexical-table
- TypeScript-first, modular, fast. Provides markdown shortcut transformers (headings, lists, code blocks, quotes, links, inline styles) and a separate `@lexical/table` package.
- No drop-in markdown editor — you compose your own toolbar/UI on top. High integration cost for our size.
- Tables: nested tables explicitly disallowed (paste blocked).

### Milkdown
- URLs: https://milkdown.dev/docs/recipes/react , https://github.com/Milkdown/milkdown/issues/1533
- Plugin-driven WYSIWYG markdown framework on ProseMirror. GFM preset is `@milkdown/preset-gfm`. The "Crepe" turn-key editor exists but issue #1533 notes Crepe still bundles **all** CodeMirror languages even when CodeMirror is disabled — bundle bloat we don't want.
- React integration via `@milkdown/integrations/react` `useEditor` hook is described in multiple sources (incl. Liveblocks, Strapi) as "bare-bones / unconventional" — manual event wiring, no native React controlled-component props.

### MDXEditor
- URLs: https://mdxeditor.dev/editor/docs/tables , https://github.com/mdx-editor/editor
- WYSIWYG on Lexical. Excellent table editor, code-block syntax highlight, plugin-based. TypeScript native.
- Bundle: **851.1 kB gzipped** (Strapi article). Targets MDX (React component embedding in markdown) — not what our `qa.md`/`spec.md`/agent `.md` artifacts contain.
- Risk: WYSIWYG round-trip rewrites the on-disk markdown formatting, which conflicts with files that are also edited by hand and committed to git.

### @uiw/react-md-editor — chosen
- URLs: https://github.com/uiwjs/react-md-editor , https://www.npmjs.com/package/@uiw/react-md-editor
- ~**4.6 kB gzipped** (Strapi). TS-native, GFM via remark-gfm (we already use that). Built-in code-block syntax highlighting. Dark mode since 3.11.0.
- Built on `<textarea>` — does NOT pull in CodeMirror or Monaco, avoiding double-bundling Monaco (which we still need for `plan.yaml`).
- API matches the spec exactly:
  ```tsx
  import MDEditor from '@uiw/react-md-editor';
  <MDEditor
    value={value}
    onChange={(v) => setValue(v ?? '')}
    preview="live"          // 'edit' | 'live' | 'preview'  -> our toggle
    height={520}
  />
  // Pure preview component for read-only renders:
  <MDEditor.Markdown source={value} />
  ```
- Tab indent, list continuation, line dup (Ctrl+D), line move (Alt+↑/↓) built in (npm page).
- No paste-image upload built in (acceptable per spec — "not required for v1"). Custom paste handlers are documented.

### react-markdown-editor-lite
- URL: https://github.com/HarryChen0506/react-markdown-editor-lite (via Strapi)
- ~69 kB total, 17 plugins, image upload, custom-parser pluggable, TS supported.
- **Unmaintained** (Strapi: "no recent commits, making it a risky choice"). Disqualifying for a project that must keep building on React 18 / Vite long-term.

### Plain `<textarea>` + react-markdown preview (current deps)
- We already have `react-markdown@9` and `remark-gfm@4` in `projects/spec_studio/frontend/package.json`. A textarea + `<ReactMarkdown remarkPlugins={[remarkGfm]}>` preview is the **zero-install** fallback.
- Gaps vs. `@uiw/react-md-editor`: no toolbar, no synced scroll, no live split mode, no code-block highlight without adding `react-syntax-highlighter` (~30 kB). For 4.6 kB we get all of the above.

## Recommendation

- **Pick:** `@uiw/react-md-editor` for the three free-form markdown surfaces — `SpecsModule` (`spec.md`), `InputModule` sub-tabs (`CLAUDE.md` / `SKILL.md` / phase-manager `.md` / `initial_prompt.md`), and the `FindingsModule` if/when its dossier becomes editable.
- **Why:**
  - **Bundle:** ~4.6 kB gzipped — the smallest serious option; trivially within our existing budget.
  - **Fit:** built-in `preview` prop with `'edit' | 'live' | 'preview'` modes is a 1:1 match for AC #8 ("toggle between view and edit modes"). `MDEditor.Markdown` exposes the same renderer for read-only views.
  - **Friction:** library-agnostic CSS-variable theme — drops into Mantine v8 / AntD v5 / shadcn shells without conflict (open question on component library is **not** blocked by this pick). Built on textarea, so it does **not** double-bundle Monaco (still needed in `ExecutionPlanModule` for `plan.yaml`).
  - **GFM:** uses remark-gfm under the hood, which we already depend on — same renderer behavior between view and edit modes.
  - **Round-trip safety:** content state is the raw markdown string; nothing is rewritten through a WYSIWYG model, so files committed to git stay byte-identical to what the user typed. Critical for `CLAUDE.md` / `SKILL.md` / agent `.md` which are also edited from a terminal.
- **Fallback for "beautified" Interview Q&A cards:** Do **NOT** render `qa.md` through a generic markdown editor. Build a custom `InterviewQuestionCard.tsx` component:
  - Backend parses `qa.md` once into a typed `InterviewQA` schema (`{ id, question, perspective, options: [{key, label, picked}], notes }`) and serves it through a new `GET /api/tasks/{task_id}/interview` endpoint, mirrored by `PUT` for save. The on-disk `qa.md` remains the source of truth; backend renders the schema back to the canonical markdown shape on PUT.
  - Each card is a Mantine/AntD/shadcn `Card` with: question text as title, perspective tag as a colored left-border (per spec Open Question default), options as a chip group (`Mantine.Chip.Group` / `AntD.Tag.CheckableTag` / shadcn `ToggleGroup`) where the picked option is filled and others are outlined, and a single editable `notes` field.
  - The `notes` field is the only free-form area; render it as a small `@uiw/react-md-editor` (`preview="edit"`, `height={140}`) so notes stay markdown-capable without giving the user a way to break the card schema.
  - Save on each card writes back the whole `qa.md` (the file is small) — one save button per card or one global save at the module level; default is one global save matching the other modules.

## Gaps

- **Bundlephobia numbers** for Tiptap / Lexical / Milkdown could not be fetched in-session (the bundlephobia HTML returned is JS-rendered). Numbers above for those three are qualitative ("heavyweight per Strapi/Liveblocks"); if a hard budget is needed, run `npx vite-bundle-visualizer` after a spike. For our pick (`@uiw/react-md-editor`), the 4.6 kB number is from Strapi's table and is consistent with its textarea-based architecture.
- **Component-library coupling:** `@uiw/react-md-editor` ships its own CSS. If the picked library is **AntD v5**, AntD's reset can fight the editor's default `.w-md-editor` styles — an ~10-line CSS override is the typical fix and is documented in the README. Mantine v8 and shadcn (Tailwind preflight) coexist cleanly.
- **Image paste / upload:** none of the lightweight options ship this. If v2 wants paste-to-upload, `@uiw/react-md-editor` exposes an `onPaste` / `onDrop` extension point — straightforward to add later without a rewrite.
- **Monaco-vs-textarea consistency:** the Execution Plan module uses Monaco (YAML), while markdown surfaces use a textarea editor. Two different editor UXs in one app is a minor UX cost; mitigated by giving both a consistent toolbar/header and a shared "Save" button component. Standardizing everything on Monaco would balloon bundle size and lose GFM live preview — not worth it.
- **`qa.md` parser** does not yet exist on the backend; the recommendation above assumes the spec_compiler's qa.md format is stable enough to parse round-trip. If the format drifts, fall back to plain markdown editing of `qa.md` with `@uiw/react-md-editor` and skip the card UI for v1.
