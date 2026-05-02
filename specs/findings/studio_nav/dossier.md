# Dossier — studio_nav

**Angles covered:**
- [component_library](component_library.md)
- [markdown_editor](markdown_editor.md)
- [yaml_editor](yaml_editor.md)
- [editable_artifacts](editable_artifacts.md)

## Cross-cutting findings (≤500 tokens)

- **Pick Mantine v8** as the single opinionated UI library. It covers every primitive the spec needs (`AppShell`, `Tabs`, `NavLink`, `Modal`, `Notifications`, `TypographyStylesProvider`, `@mantine/code-highlight`) without forcing a runtime CSS-in-JS engine. CSS-modules-only output coexists with the existing Tailwind setup and our markdown viewer. Migration cost is **Low–Medium**: one provider import, one global CSS, then route by route.
- **Pick `@uiw/react-md-editor`** for every free-form markdown surface (Specs view/edit, the four Input sub-tabs, the Findings dossier viewer). ~4.6 KB gzipped, GFM via `remark-gfm` (already a dep), built-in `preview="edit|live|preview"` toggle that maps to AC #8, library-agnostic CSS-variable theming. Critically, content state is the **raw markdown string**, so files like `CLAUDE.md` / `SKILL.md` round-trip byte-identical to git.
- **Do NOT use a generic markdown editor for the Interview Q&A.** Instead, parse `qa.md` into a typed schema `{question, perspective, options[], picked, notes}` server-side, render a custom `InterviewQuestionCard.tsx` with chip-group option pickers, and embed `@uiw/react-md-editor` only inside the `notes` field. The backend gains a `GET/PUT /api/tasks/{task_id}/interview` pair that handles parse/render. If parsing proves brittle, fall back to raw markdown editing of `qa.md`.
- **Pick `@monaco-editor/react` + `monaco-yaml` 5.4.1** for the Execution Plan module. CodeMirror 6 + lang-yaml is ~10× lighter but only does highlighting; we'd hand-roll JSON-Schema validation. Monaco gives YAML schema validation for free. Lazy-load `ExecutionPlanModule` via `React.lazy` so the ~2–3 MB Monaco bundle only loads on that route.
- **Atomic writes use the existing `os.replace` pattern.** Generalize `FileStore._write_index` into an `AtomicWriter` class. Single-slot `.bak` via `shutil.copy2` *before* the atomic rename; ETag = lowercase hex SHA-256 of UTF-8 bytes; `If-Match` is **advisory in v1** (response sets `stale_etag: true`, save still proceeds), promoted to hard 412 in v2.
- **Confirm-gating is data-shaped, not flag-gated.** `RepoEditBody(content: str, confirm: bool)` for the four repo-level routes (`PUT /api/inputs/claude_md`, `PUT /api/inputs/skill_md`, `PUT /api/agents/{name}`, `PUT /api/inputs/initial_prompt` is per-task so it uses the simpler body). Missing `confirm` → 422 (Pydantic); `confirm: false` → explicit 400.
- **OOP placement** per CLAUDE.md: new package `backend/libs/edits/` with `RepoInputResolver` (allowlist + traversal protection) and route helpers; `backend/libs/storage/safe_writer.py` with `AtomicWriter` + `BackupWriter`. Routes stay thin.

## Per-angle summaries

- **component_library** — Mantine v8 wins over Ant Design v5 (migration friction higher), shadcn/ui (DIY-ish), Chakra v3 (fewer admin primitives). See `component_library.md` for the side-by-side and rationale.
- **markdown_editor** — `@uiw/react-md-editor` for free-form markdown; custom typed `InterviewQuestionCard` for Q&A. TipTap/Lexical/Milkdown/MDXEditor all rejected (lossy round-trip, bundle size, or integration cost). See `markdown_editor.md`.
- **yaml_editor** — `@monaco-editor/react` + `monaco-yaml`, Vite worker config per the README, lazy-loaded Plan module. JSON schema for `plan.yaml` derived from `agent_team__execution_plan_compiler.md` § Output, served via a synthetic URI with `enableSchemaRequest: false`. See `yaml_editor.md`.
- **editable_artifacts** — `AtomicWriter` + `BackupWriter` classes, `RepoEditBody` vs `ArtifactEditBody`, ETag/`If-Match` advisory, last-write-wins documented. See `editable_artifacts.md`.

## Conflicts & uncertainties

- **Bundle-size figures**: Mantine and Monaco bundle KBs are not authoritatively measured in the sources — run `vite build --report` after wiring as part of the validation phase.
- **Mantine vs Tailwind coexistence**: both researchers (component_library + markdown_editor) confirm coexistence works, but the CSS specificity edge cases (e.g. AntD reset → Tailwind utility) are unproven for our exact stack. Mantine doesn't have AntD's reset, so the risk is lower with Mantine.
- **Monaco-yaml `loader.config({ monaco })` ordering** is the #1 silent-failure mode flagged in the YAML research — must be verified at module-scope before any `<Editor />` mounts. The validation phase should grep for this.

## Recommendations for the execution-plan compiler

- Lock the component library to **Mantine v8**. Plan should include one work unit to install + wire `MantineProvider` + global CSS, separate from the per-module work units.
- The frontend deps to add: `@mantine/core@^8`, `@mantine/hooks@^8`, `@mantine/notifications@^8`, `@mantine/modals@^8`, `@mantine/code-highlight@^8`, `@uiw/react-md-editor@^4`, `@monaco-editor/react@^4`, `monaco-yaml@^5.4`, `monaco-editor@^0.52`. Pin the latest patch versions found at install time.
- Plan one work unit for `backend/libs/storage/safe_writer.py` (AtomicWriter + BackupWriter) and one for `backend/libs/edits/` (RepoInputResolver + paths). These are dependencies for every PUT route work unit.
- The `qa.md` schema parser is its own work unit (under `backend/libs/parsers/qa_parser.py` or similar) — the InterviewModule frontend depends on its API shape.
- Lazy-load Monaco via `React.lazy` on the Plan module to avoid front-loading the heavy bundle.
- The `monaco-yaml` schema for `plan.yaml` is its own asset — generate from the agent file or hand-author at `frontend/src/schemas/plan.schema.json`. Either way, its acceptance check is "schema validates a known-good plan.yaml without errors".
