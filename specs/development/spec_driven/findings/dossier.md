# Findings dossier — spec_driven

Run: spec_driven-20260502-141813
Compiled by: parent (agent_team skill) on 2026-05-02
Architecture note: research_manager subagent halted because the `Agent` (subagent-spawn) tool is not available inside subagents in this harness. The four researcher subagents were spawned directly from parent scope with the contract from `.claude/agents/agent_team__research_manager.md` Step 0 (ToolSearch for WebSearch/WebFetch). All four researchers loaded both web tools and produced cited findings. This dossier was synthesized by the parent from the four resulting `angle-*.md` files; no synthesis subagent was invoked.

## Angles researched

1. **prior-art-readonly-viewers** — what GitHub / Sourcegraph / MkDocs Material / Docusaurus / GitBook / Obsidian Publish / Backstage TechDocs / Storybook do for browsing structured artifact trees, and which UX patterns the spec_driven viewer should adopt vs skip.
2. **two-pane-navigator-reader-ux** — concrete v1 component behavior for sidebar tree, selection model, breadcrumbs, keyboard support, and overflow handling, drawn from VS Code / JetBrains / GitHub / MkDocs Material / Storybook / Backstage TechDocs.
3. **markdown-link-resolution-patterns** — internal/external classification, anchor handling, broken-link rendering, and edge cases (encoding, case sensitivity, escape-the-tree) drawn from MkDocs / Docusaurus / GitHub / Obsidian / GFM spec / OWASP.
4. **filesystem-readonly-viewer-risks** — race conditions, path traversal, symlinks, encoding, permissions, and stale-tree UX for a scan-on-every-request viewer over a live filesystem, drawn from Starlette CVE-2023-29159, OWASP, nginx/Dufs/Plesk file servers, and Python `pathlib` semantics.

## Cross-cutting insights

These emerged from combining angles and are load-bearing for the spec stage:

- **There is one "exposed tree" concept and it must mean the same thing in three places.** The sidebar listing (prior-art angle), the link resolver (markdown-links angle), and the file-read endpoint sandbox (filesystem-risks angle) must use a single definition: `CLAUDE.md` (repo root) ∪ `.claude/agents/*.md` ∪ `.claude/skills/**/SKILL.md` ∪ `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**`. Letting these three diverge is how Starlette CVE-2023-29159-class bugs happen — the renderer "knew" the link was external while the file server still served it.

- **Render-time validation is the right call here, not build-time.** All four angles converge on this from different sides: spec_driven has no build step (markdown-links), no watcher / auto-refresh (filesystem-risks), no precomputed index (prior-art's "scan per request" matches Obsidian/GitHub render-time pattern, not MkDocs/Docusaurus build-time pattern). At locked scale (≤200 files × <500 KB), per-request resolution is well within budget.

- **"Expected but missing" is the dominant shape of broken state and its UX should converge.** Missing stage subfolders (no `validation/` yet because the project hasn't reached stage 5), missing files (link to a not-yet-written `final_specs/spec.md`), broken anchors (heading renamed), files removed mid-request (Claude Code rewriting while the viewer reads). Across all four angles, the established UX is the same: render the affected element as muted text + native `title` tooltip giving the cause, **never emit a dead `<a href>`**, never throw 500. Adopt one component and one CSS class for all four cases.

- **`localStorage` sidebar state is the single highest-leverage UX win.** The prior-art and two-pane angles independently flag that VS Code's biggest UX debt is losing tree expand/collapse state and last-selected file across launches — ~20 lines of `localStorage` get/set make spec_driven strictly better than VS Code at this for free.

- **Path-based URLs are the source of truth for selection state.** GitHub's `/{owner}/{repo}/blob/{branch}/{path}` model (prior-art), VS Code's `autoReveal` + JetBrains' "Always Select Opened File" (two-pane), and the link resolver's need to push history on internal navigation (markdown-links) all assume URL = current selection. This makes deep-links shareable, refresh-safe, and gives breadcrumb construction for free.

- **The W3C ARIA tree pattern is free correctness.** Prior-art and two-pane both recommend it; Storybook is explicitly working toward it and considers their current state a bug. Implementing `role="tree"` + `role="treeitem"` + `aria-expanded` + `aria-selected` + `aria-level` from day one costs almost nothing, gets keyboard navigation per the spec'd APG behavior, and avoids a future a11y rewrite.

- **The path resolver and the file server must not trust each other.** From filesystem-risks + markdown-links: the link resolver decides what the user *sees* as a clickable in-app link; the file-read endpoint decides what bytes ever leave the disk. Both must independently sandbox to the exposed tree. CVE-2023-29159 happened in Starlette precisely because the prefix check trusted the renderer's assumption.

## Per-angle highlights

### prior-art-readonly-viewers

- Three universal patterns across MkDocs Material, Docusaurus, GitBook, Storybook, Backstage TechDocs: **collapsible-by-category sidebar**, **auto-expand the path to the active file (collapse the rest)**, **breadcrumbs above content**. Locked qa.md decisions already line up — adopt explicitly.
- Headline anti-pattern is **VS Code Explorer losing tree state on every launch** (long-standing complaint threads vscode#116190, vscode#228788). Persist sidebar collapse state + last-selected file in `localStorage`.
- Other anti-patterns to skip: breadcrumb-as-history, last-crumb-as-link, recursive expand-all toolbar (no depth justifies it at locked scale), permanent icon-only rail (GitBook explicitly moved away), generic FTP-style file managers as the model (FileGator/h5ai/Dufs optimize for upload/download/permissions, not reading rendered artifacts).
- Skip these specifically for v1: search (locked out), backlinks/graph view (Obsidian's signature; spec_driven links are forward-only), per-page metadata sidebar (no metadata to display), recursive expand-all.

### two-pane-navigator-reader-ux

- Five conventions to adopt: **URL-reflected selection (deep-linkable)**, **collapse-by-default with auto-reveal of the selected file's ancestor chain**, **folder-click = expand/collapse, file-click = render** (no folder-index pages), **breadcrumbs above content**, **W3C ARIA tree pattern for arrow-key keyboard nav**.
- Selected-state requires two distinct visuals: **filled background bar for `aria-selected="true"`** + **separate ring outline for keyboard focus**. Both indicators must be visible simultaneously per W3C APG.
- Long filenames: **single-line ellipsis with native `title` tooltip**. **Middle-ellipsis for files** (preserves the `.md` extension; PatternFly + Carbon Design System both call this out); end-ellipsis for folders. No wrapping, no horizontal scroll.
- v1 keyboard minimum: arrow-key tree nav per ARIA APG (Up/Down move, Right expand, Left collapse, Enter navigate). **Defer Ctrl+P quick-open to v2** — Storybook/VS Code both treat it as a power-user accelerator, not a baseline.

### markdown-link-resolution-patterns

- Classification algorithm in this exact order: **(1)** scheme present (`^[a-z][a-z0-9+.-]*:`) or starts with `//` → external (open new tab, `target="_blank" rel="noopener noreferrer"`). **(2)** Starts with `#` → same-file anchor (in-app scroll-to). **(3)** Otherwise URL-decode once, normalize, join against the source file's parent, assert resolved path is inside the exposed root → internal (in-app navigate) else broken (muted + tooltip).
- **Anchors are the most fragile sub-case.** Heading IDs auto-regenerate from heading text via the GFM kebab-case slug rule (lowercase, drop punctuation, spaces→hyphens, append `-1`/`-2` on collisions). Renaming a heading silently breaks every inbound `#anchor`. Docusaurus needed a separate `onBrokenAnchors` config because anchor validation lagged page-link validation.
- **Edge cases that wreck naive implementations**: percent-encoded paths (decode once, never twice — double-decode is a path-traversal bypass per OWASP); Linux/Windows case-sensitivity skew; `..`-traversal escaping the exposed root (must verify `resolved.is_relative_to(exposed_root)` independently in both renderer and file server); GFM kebab-case slug collision rules; the markdown-syntax-vs-HTML-tag asymmetry (markdown-syntax `[label](path)` and `![alt](path)` get resolved; HTML `<a>` and `<img>` bypass resolution entirely).
- **Broken-link rendering is converged**: muted/non-clickable text wrapped in a span, `title` tooltip giving the unresolved target and reason (`not in tree` / `file not found` / `escapes root`), **never emit a dead `<a>`**.

### filesystem-readonly-viewer-risks

- **Path traversal is the only real security risk in v1**, even on single-user localhost — user-authored markdown can contain `../../../.ssh/id_rsa` links. Established mitigation: `(base / user).resolve(strict=False)` + `relative_to(base.resolve())` catching `ValueError`. **Do not use `os.path.commonprefix`** — that's the exact mistake behind Starlette CVE-2023-29159.
- **Refuse symlinks rather than follow them.** nginx, Dufs, and Plesk all expose explicit disable-symlinks knobs; the spec_coding repo never legitimately uses symlinks under `specs/` or `.claude/`. Cheapest correct policy: skip `Path.is_symlink()` entries during directory listing AND verify the resolved path is still under the sandboxed root.
- **EAFP for file reads** — `try: open() except (FileNotFoundError, PermissionError, IsADirectoryError)` returning structured 404/403 JSON. Don't pre-check with `os.path.exists` — that's the textbook race-condition antipattern. Claude Code's `Write` tool is **not** atomic (truncate-then-write), so torn reads CAN happen mid-write; v1 UX is "user refreshes," no atomic-read shim.
- **Encoding/binary safety is a 5-line problem, not a `chardet` dependency.** Read at most 2 MB with `encoding="utf-8", errors="replace"`, scan for `\x00` to reject binary, whitelist file extensions (`.md`, `.yaml`, `.yml`, `.json`, `.jsonl`) at the API boundary. Defer ETag, file-watching, MIME sniffing, encoding auto-detection.

## Recommendations for the spec

These are the concrete moves the Stage-4 spec should pin down:

1. **Define `EXPOSED_TREE` as a single named concept used by every endpoint.** It is the union of `CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`, and `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**`. Sidebar listing, link resolver, and file server all derive from this one constant.

2. **Sandboxed path resolver** — single helper `safe_resolve(user_rel: str, root: Path) -> Path` doing `(root / user_rel).resolve(strict=False).relative_to(root.resolve())` (catch `ValueError` → HTTP 400). Used by every API endpoint that takes a path. Reject `Path.is_symlink()` entries before resolving.

3. **Whitelisted file extensions at the read endpoint:** `.md`, `.yaml`, `.yml`, `.json`, `.jsonl`. Anything else → 415. Read with `encoding="utf-8", errors="replace"`, scan for `\x00`, cap at 2 MB.

4. **Routing.** `/settings/claude-md`, `/settings/agents/<file>`, `/settings/skills/<folder>`, `/projects/<task_type>/<task_name>/<stage>/<file_path>`. URL is the source of truth for selection. Use **nested route segments**, not splat params with encoded `/`. Default route → `/projects/development/spec_driven/final_specs/spec.md`, falling back to `/.../user_input/revised_prompt.md` if the spec file doesn't exist.

5. **Sidebar component** — implements W3C ARIA tree pattern (`role="tree"`, `role="treeitem"`, `aria-expanded`, `aria-selected`, `aria-level`, `aria-multiselectable="false"`). Persist collapse state per node-path and last-selected file in `localStorage` keyed `spec_driven.sidebar.v1`. On URL load, expand the ancestor chain of the selected file; collapse the rest. Folder click toggles expand only — never opens a "folder index" page. File click navigates and renders.

6. **Selected-state visual** — filled background bar for `aria-selected="true"`, separate ring outline for keyboard focus. Both visible simultaneously.

7. **Long names** — single-line ellipsis with native `title` attribute. Middle-ellipsis for files, end-ellipsis for folders. No wrapping, no horizontal scroll.

8. **Keyboard support v1** — arrow-key tree nav per ARIA APG. **Ctrl+P quick-open is v2**, not v1.

9. **Breadcrumb above content** — `task_type / task_name / stage / filename` for Projects; `Settings / kind / filename` for Section 1. Each segment except the last is clickable. Last crumb is plain text.

10. **Markdown link classification** in this order: scheme/`//` → external (`target="_blank" rel="noopener noreferrer"`); `#` → same-file anchor scroll; otherwise URL-decode once → normalize → join against source file's directory → assert inside `EXPOSED_TREE` → internal in-app `Link`; else broken (muted span + `title` tooltip with cause). **Never emit a dead `<a>`.**

11. **Anchor handling** — generate heading IDs with the GFM kebab-case slug rule (lowercase, drop punctuation, spaces→hyphens, append `-1`/`-2` on collisions). Resolve `path#anchor` by file-resolution + scroll-to-id-on-navigate.

12. **One "muted + tooltip" component** used uniformly for all "expected but missing" cases: missing stage subfolders, broken file links, broken anchors, files removed mid-request, paths escaping the exposed root. Same CSS class, same tooltip pattern; just different `cause` strings.

13. **Stale-tree affordance** — when a sidebar click resolves to a now-missing file, the API returns `{"error": "not_found", "kind": "file_removed" | "permission_denied" | "outside_sandbox"}`. The frontend shows a non-modal inline message with a "refresh sidebar" button. No watcher, no WebSocket — the user manually refreshes per qa.md.

14. **Section 1 layout** — always-visible header + always-expanded subgroups (`CLAUDE.md` / Agents / Skills). Section 1 is small (1 + N agents + M skills); no collapse benefit.

15. **Animation** — single 100–150ms ease on sidebar expand/collapse for spatial continuity. Anything more is noise.

16. **Browser history** — push (not replace) on every internal navigation, so back-button matches user mental model.

## Open questions surviving research

These are gaps the research did not close — Stage 4 (spec compilation) must take a position on each, or explicitly defer.

- **Empty / missing stage folders** — render the leaf as muted-italic with "not yet generated" tooltip (recommended), hide it, or show disabled? *(prior-art, two-pane)*
- **Sub-stage file ordering** — alphabetical with a small known-name priority list (`strategy.md` first), or pure alphabetical? *(prior-art)*
- **Manual reload affordance** — is a "refresh tree" button in scope, or strictly browser reload only? *(prior-art, filesystem-risks)*
- **Section 1 link-resolution scope** — does a markdown link from `CLAUDE.md` to `.claude/agents/foo.md` resolve in-app the same way `specs/`-internal links do? Locked qa.md is ambiguous about whether "internal clickable" covers Section 1 or is `specs/`-only. *(prior-art, markdown-links)*
- **Sidebar width** — fixed-width (~280–320px) or draggable splitter? *(two-pane)*
- **Folder-only URL** — if user shares `/projects/development/spec_driven/findings/` with no file, what does the reader pane show? Empty / first child / folder listing? Recommend auto-redirect to first markdown alphabetically. *(two-pane)*
- **Settings breadcrumb wording** — literal "Settings" (shorter) or "Claude Settings & Shared Context" (matches in-app section name)? *(two-pane)*
- **Broken anchor with valid file** — render fully broken (muted), or partial (file link works, no scroll target, tooltip explains)? Docusaurus treats them separately via `onBrokenAnchors`; we should pick one. *(markdown-links)*
- **Anchor-only "no such heading" warning** — surface in UI, or silent fall-through? *(markdown-links)*
- **CLAUDE.md cross-refs to outside-tree files** (e.g. mentioning `pyproject.toml` at repo root) — promote to internal, or leave broken? *(markdown-links)*
- **Image with disallowed extension** — block, or render with a placeholder? *(markdown-links, filesystem-risks)*
- **Symlink policy display** — refuse silently, or surface as a leaf marked "symlink — not followed"? *(filesystem-risks)*
- **`outside_sandbox` UX** — distinguish it from a generic 404 in the frontend, or collapse to one error? *(filesystem-risks)*
- **Sandbox root resolution** — `.resolve()` once at startup or per-request? Recommend once-at-startup for consistency with the locked walk-upward repo-root cache. *(filesystem-risks)*
- **Code/JSON line-number anchoring** — should `#L42` scroll-and-highlight, like GitHub? Cheap, high-leverage during review; in-scope for v1? *(prior-art)*
- **In-app navigation scroll preservation** — when user clicks an internal link, does back-button restore the source file's scroll position? *(markdown-links)*
- **Windows long-path (>260 chars)** — flag if the e2e suite hits it; otherwise probably fine. *(filesystem-risks)*
- **JSONL streaming for future audit-log views** — out of scope for v1 (only `specs/` is surfaced), noted as known follow-up. *(filesystem-risks)*

## Synthesis (what changed our understanding)

Going in, the use case looked like "render markdown in a tree" — three obvious components (sidebar, reader, link resolver). Coming out, the dominant insight is that **the sidebar, the link resolver, and the file-read endpoint are three faces of one concept (the exposed tree), and they fail in the same shape (expected but missing)**. That reframes the spec from "build three components" to "define one tree contract and three views on it, with one shared 'broken' UX." It also shifts security from a footnote to a load-bearing v1 requirement: even on single-user localhost, user-authored markdown is the attacker, and CVE-2023-29159 shows that sloppy sandboxing is how mature frameworks ship file-disclosure bugs. The `localStorage` sidebar persistence and ARIA tree pattern emerged as cheap, high-leverage moves that materially differentiate this viewer from the obvious comparators (VS Code Explorer, naive file servers) for almost no implementation cost.

## Addendum (follow-up 001 — editing & regen scope)

The original research framed the viewer as readonly; follow-up 001 added in-place editing for every file in the exposed tree, a structured Q/A view for `interview/qa.md`, and per-stage / per-project copy-paste regeneration prompts with an autonomous-mode toggle. The research above still applies — the same `EXPOSED_TREE` contract, `safe_resolve` sandbox, extension whitelist, and 2 MB cap govern the new `PUT /api/file` endpoint. Three additions are worth noting that the original research did not anticipate:

1. **Atomic write for editing.** Writes go to a sibling temp file in the same directory followed by `os.replace()`. This sidesteps the truncate-then-write tear discussed in §filesystem-readonly-viewer-risks and means a partially-written file never appears on disk.
2. **Server-side prompt assembly is the right default.** The regen prompt has to inline the current `revised_prompt.md` plus every `follow_ups/*.md`; doing that in the frontend would require exposing the follow-ups directory. Keeping it server-side at `POST /api/regen-prompt` reuses the existing repo-root sandbox.
3. **Autonomous-mode contract belongs in `CLAUDE.md`, not in code.** The webapp emits a `# EXECUTION MODE: AUTONOMOUS` header into the copy-paste prompt; whether Claude honors it is governed entirely by `CLAUDE.md`. Treating the header as a documentation contract (not a runtime feature flag) keeps the webapp simple and the rules in one place.
