# Follow-up draft 009 — 2026-05-03

Summary: Four coupled UX gaps against the current dogfood state.

(a) **Sidebar second section is named "Projects" — should be "Specs".** The user's mental model: top-level is `Claude Settings & Shared Context` + `Specs`; under Specs they see exactly one project, `development/spec_driven/`. Rename the section. Patch FR-3 + FR-15 in `final_specs/spec.md` so the spec stops calling it "Projects".

(b) **Clicking a project node (e.g., `spec_driven/`) should open a project-wide regen UI.** Today the project node is a directory that toggles on click; the master Regenerate panel at `/project/{type}/{name}` (FR-32) is reachable only from the Home-page link added in follow-up 008 or by typing the URL. Make the row click navigate; keep the disclosure caret as a separate toggle button.

(c) **Clicking a stage node (e.g., `interview/`) should open a stage-scoped regen UI.** Today the stage-scoped Regenerate panel only appears in the Reader when the user is viewing *a specific file* under that stage (see `Reader.tsx` line 189–195). The user expects to land on a stage page directly. Add a `/stage/{type}/{name}/{stage}` route and a `StagePage` component that shows the stage-scoped Regenerate panel without requiring a file selection.

(d) **No promotion button on non-QA stages, and the QA pin state never loads.** Two coupled bugs:
- *Loader bug.* `Reader.tsx::extractPinnedIds` matches the regex `<!--\s*pin:([^\s]+)\s*-->`, but `backend/libs/promotions.py::_serialize` writes `<!-- pin source={src} id={id} -->`. The two formats never match — pinned QA items always render as un-pinned even after a successful `POST /api/promote`. Fix the regex to extract the `id=` attribute from the canonical comment shape.
- *Coverage gap.* FR-35 specifies 📌 toggles "next to each pinnable atomic item (Q/A pair, FR-NN / NFR-NN / AC-NN / SYS-NN block, recommendation bullet)". Today the only place a 📌 renders is `QaView` (Q/A pairs). Spec, validation, and findings markdown have no pin UI — even though the backend `Promotions` service already accepts `stage_folder ∈ {interview, findings, final_specs, validation}` (the 4-stage allowlist in `promotions.py:11-13`). Extend the markdown renderer to detect bold-prefix markers (`**FR-NN.**` / `**NFR-NN.**` / `**AC-NN.**` / `**SYS-NN.**` / `**OQ-NN.**`) at the start of paragraphs and list items and inject a 📌 button. Wire it through the existing `POST /api/promote` / `DELETE /api/promote` endpoints.

## (a) — section rename

`tree_walker._projects_section` returns `{name: "Projects", ...}`. Change the literal to `"Specs"`. Walk downstream:

- `final_specs/spec.md` FR-3 currently says: *"Top-level sections: 'Claude Settings & Shared Context' and 'Projects'"*. Patch to "Specs".
- `final_specs/spec.md` FR-15 currently says: *"Tree section names: 'Claude Settings & Shared Context' + 'Projects'. The `Projects/{type}/{name}/` subtree shows per-stage subfolders…"*. Patch literal "Projects" → "Specs" in both sentences.
- `frontend/src/components/Home.tsx` — `discoverProjects` looks for the section by name `"Projects"`. Change to `"Specs"`.
- `backend/tests/unit/test_tree_walker.py::test_root_has_two_top_level_sections` asserts `"Projects" in names`. Update to `"Specs"`.
- The dossier paragraph that retells FR-3 ("Top-level sections: 'Claude Settings & Shared Context' and 'Projects'") is INSIDE the dossier body — leave it alone (dossier captures historical research output, not living spec). Spec is the source of truth.

## (b) — project node navigates

`Sidebar.tsx` row-click handler currently toggles or opens a leaf:

```tsx
onClick={(e) => {
  e.stopPropagation();
  if (isLeaf) onSelect(item.node.path);
  else if (hasChildren) toggle(item.node.path);
}}
```

Change to: if path matches `^specs/[^/]+/[^/]+$` (a project node — exactly two segments after `specs/`), navigate to `/project/{type}/{name}` instead of toggling. Disclosure (▾/▸) becomes a separate `<button>` whose only job is `toggle(path)` — that lets users still expand/collapse without leaving the project page.

## (c) — stage node navigates to a new StagePage

Same pattern: if path matches `^specs/[^/]+/[^/]+/(user_input|interview|findings|final_specs|validation)$`, navigate to `/stage/{type}/{name}/{stage}` instead of toggling.

New route + component:
- `App.tsx`: `<Route path="/stage/:projectType/:projectName/:stage" element={<StagePage />} />`.
- `components/StagePage.tsx`: read `projectType`, `projectName`, `stage` from `useParams`; render `<RegeneratePanel projectType={t} projectName={n} stageId={stage} initiallyOpen />`. (The existing `RegeneratePanel` already supports stage-scoped mode — `stageId` is non-null → it filters down to that one stage's modules.)

Note: `user_input` is not in the promote allowlist but IS a real stage. The new `StagePage` happily renders a regen panel for `user_input` (the Intake stage exists in `DEFAULT_STAGES` / `/api/stages`); pin UI just doesn't apply there.

## (d) — pin loader + markdown 📌

### Loader bug

```tsx
// Reader.tsx — current
const matches = content.matchAll(/<!--\s*pin:([^\s]+)\s*-->/g);
```

Backend's promoted.md writes `<!-- pin source=qa.md id=R1-funct-q1 -->`. Replace the loader with a regex that extracts `id=<value>`:

```tsx
const matches = content.matchAll(/<!--\s*[Pp][Ii][Nn]\s+([^>]*?)-->/g);
for (const m of matches) {
  const idMatch = /\bid=([^\s>]+)/.exec(m[1]);
  if (idMatch) ids.add(idMatch[1]);
}
```

Mirror of `_PIN_HEADER` + `_ATTR` in `promotions.py` so format drift is symmetric.

### Markdown pin button injection

Extend `markdown/renderer.tsx` to accept a `pinContext: { projectType, projectName, stageFolder, pinnedIds, onPin, onUnpin } | null` prop. When non-null, override `p` and `li`:

- Walk the React children; if the **first** child is a `<strong>` whose text matches `^(FR|NFR|AC|SYS|OQ)-(\d+\w*)\.?$`, the matched literal (e.g., `FR-1`, `OQ-3`) is the `item_id`.
- Render a `<button class="pin-toggle">📌</button>` next to it, wired to `onPin/onUnpin`. Same a11y contract as `QaView` (`role="switch"`, `aria-checked`, `aria-label`).

`Reader.tsx` builds `pinContext` whenever `projectInfo.stage` is in the 4-stage allowlist (`{interview, findings, final_specs, validation}`) and passes it down. The same `pinnedIds` set already feeds `QaView`; reuse it for non-QA markdown so a single state source covers both.

For the `item_text` that goes into `promoted.md`, the renderer ships the rendered paragraph's source text — for v1, the cheapest correct answer is to look up the matching line in the raw markdown content (Reader already has `file.content`) by scanning for the bolded marker. That keeps the pin body verbatim what the user sees.

## What stays the same

- Backend `Promotions` service — already correct, no changes. Stage allowlist already covers the 4 pinnable stages.
- `RegeneratePanel.tsx` — already supports both project-wide (`stageId={null}`) and stage-scoped (`stageId="interview"`) modes. The new `StagePage` is just a thin wrapper.
- File-API path-sandbox — untouched.
- Q/A pin in `QaView` — untouched aside from picking up the now-correct `pinnedIds` from `Reader.tsx`.

## What MOVES in the spec

- FR-3: section name `"Projects"` → `"Specs"` (literal patch).
- FR-15: section name `"Projects"` → `"Specs"`; `Projects/{type}/{name}/` → `Specs/{type}/{name}/` (two literal patches in the same FR).

No new FR / NFR / AC. The user-visible-name shift is small enough to be a literal find-replace inside two existing FRs; introducing a new FR for "section is named Specs" would balloon the spec without adding semantic content.

## What is INTENTIONALLY out of scope

- E2E sidebar-selector mismatch (`data-testid="sidebar"`, `data-section-toplevel`, etc. — Sidebar.tsx never emits these attributes; SYS-20 / SYS-21 are already failing). Same call as follow-up 008: a separate, scoped follow-up to wire the test selectors.
- Pin support in `dossier.md` "recommendation bullets" — FR-35 lists them, but the bullet shape is heterogeneous (numbered list of angles vs. cross-cutting-insights bullets vs. per-angle highlight bullets) and over-matching is worse than not-matching. Ship FR/NFR/AC/SYS/OQ first; revisit dossier-bullet pinning once the FR/NFR/AC/SYS path is being used.
- The pre-existing `Renderer` casing-import error and the `Sidebar.test.tsx` unused-React error — pre-date this follow-up; same call as 008.
- Reader's stage-scoped Regenerate panel — left as-is. With the new `/stage/...` route, the user has TWO entry points for the stage panel: (i) viewing any file inside that stage, (ii) clicking the stage node in the sidebar. Both render the same component; the duplication is intentional for discoverability.
