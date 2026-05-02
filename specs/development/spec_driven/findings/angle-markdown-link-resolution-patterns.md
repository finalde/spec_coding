# Angle — Markdown link resolution patterns

Run: spec_driven-20260502-141813
Researcher: researcher-03

## 1. What this angle covers

How mature documentation and note-taking tools resolve markdown cross-links inside a known file tree, how they classify "internal" (resolves to a node in the exposed tree) vs "external" (http/mailto/etc.), how they render broken or dangling links, and which edge cases — encoding, case sensitivity, anchors, image vs link, escape-the-tree — bite naive implementations. The locked UX is: in-app navigation for relative-internal, new-tab for external, muted-with-tooltip for broken, render-in-full. This angle pins down the resolution algorithm and the broken-link treatment so the implementation does not have to reinvent (or re-discover the failure modes of) those primitives.

## 2. Key findings

### Internal vs external classification

- The widely-adopted rule across MkDocs, Docusaurus, and GitHub renderers is: a link is treated as **internal** only when it is a **relative path** (no scheme, no leading `//`) that resolves to a real file in the docs / repo tree. Anything carrying a URL scheme (`http:`, `https:`, `mailto:`, `ftp:`, `tel:`, etc.) or a protocol-relative `//host/...` is **external**. ([MkDocs configuration — `validation.links`](https://www.mkdocs.org/user-guide/configuration/), [GitHub Docs — relative links in READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes))
- MkDocs historically only resolves relative links that point at another `.md` document or a media file — keeping the source pages browsable as plain markdown without the renderer. ([MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/))
- Absolute paths (leading `/`) are a known footgun. MkDocs added `validation.links.absolute_links: relative_to_docs` so that `/foo.md` is interpreted relative to the `docs_dir` root and validated, then rewritten for HTML output. Without that flag, `/foo` means the host filesystem root in HTML, which almost always 404s. ([MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/))
- Docusaurus draws the same line but enforces it through MDX/Webpack: markdown-syntax links and images are converted to `require()` calls and statically resolved; HTML/JSX `<a>` and `<img>` tags are not touched. The site-build only validates the markdown-syntax form. ([Docusaurus — Static Assets](https://docusaurus.io/docs/static-assets))

### Anchor links

- CommonMark itself does **not** specify heading-id generation; that's an extension. GFM and GitLab define near-identical kebab-case slug rules: lowercase, drop punctuation, spaces → hyphens, collapse repeated hyphens, append `-1`, `-2`, … on collisions. ([GFM Spec](https://github.github.com/gfm/), [GitLab Flavored Markdown](https://docs.gitlab.com/user/markdown/), [GitHub Heading Anchors gist](https://gist.github.com/asabaylus/3071099))
- Cross-file anchors (`spec.md#goal`) resolve by first resolving the file, then matching the slug inside that file's heading set.
- Anchors are the most fragile part of cross-linking: heading IDs are auto-generated from heading text, so renaming a heading silently breaks every inbound `#anchor`. Docusaurus exposes a separate `onBrokenAnchors` config because anchor validation lags page-link validation, and even the production link checker did not validate anchors for a long time. ([Docusaurus — `onBrokenMarkdownLinks` vs `onBrokenLinks`](https://github.com/facebook/docusaurus/discussions/8613), [Docusaurus issue #3321 — detect broken anchor links](https://github.com/facebook/docusaurus/issues/3321))

### Build-time vs render-time validation

- Static-site generators (MkDocs, Docusaurus, GitBook) validate at **build time** because the full file graph is known and a broken link should fail the build. Docusaurus’s `onBrokenLinks` accepts `throw | error | warn | ignore`, default `throw`. ([Docusaurus — handling broken links discussion](https://github.com/facebook/docusaurus/discussions/8613))
- Render-time tools (Obsidian, GitHub's repo view) validate **at view time**: the renderer asks "does the target exist right now?" and styles the link accordingly. Obsidian shows unresolved wikilinks in a distinct "broken link" colour; resolved links use the standard internal-link colour. ([Obsidian forum — non-unique unresolved links](https://forum.obsidian.md/t/how-to-approach-non-unique-unresolved-links/94298))
- The hybrid pattern — build-time for the SSG output and render-time as a safety net — is what tools like MkDocs Material with the autorefs plugin lean on; autorefs even has a `resolve_closest` mode that picks the nearest matching target relative to the current page. ([mkdocs-autorefs overview](https://mkdocstrings.github.io/autorefs/))

### Broken-link rendering

- Established practice converges on: render the link text as plain (or muted) text, do **not** emit an `<a href>` that goes nowhere, and surface "why" via a tooltip. Obsidian uses a distinct colour; MkDocs Material with `content.tooltips` shows the resolution status on hover. ([mkdocs-autorefs](https://mkdocstrings.github.io/autorefs/))
- Docusaurus and MkDocs additionally fail the build, so production never ships a broken link in the first place — render-time treatment only kicks in for whatever slips past. ([Docusaurus — handling broken links](https://github.com/facebook/docusaurus/discussions/8613))

### Images vs anchor links

- Same scheme classification, different render path. In Docusaurus, both go through the MDX loader and become `require()` calls when in markdown syntax — so `![alt](./cover.png)` and `[label](./other.md)` share the resolution algorithm but produce different DOM. The mismatch is for HTML `<img>` / `<a>`, which bypass resolution entirely. ([Docusaurus — Static Assets](https://docusaurus.io/docs/static-assets), [Docusaurus discussion #6465](https://github.com/facebook/docusaurus/discussions/6465))
- A subtle gotcha: when the same path resolves both inside and outside the exposed tree (e.g. a local clone of the repo on the user's machine), GitHub's renderer warns that absolute links may not survive in clones — the cure is "always relative". ([GitHub Docs — about READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes))

### Edge cases that bite naive implementations

- **Percent-encoded paths.** Markdown sources commonly write `path/My%20File.md`. Naive `string == filename` comparisons miss matches. The fix is to URL-decode the path component **once** before resolving, but never re-encode and re-decode (double-decoding is a classic path-traversal bypass). ([OWASP — Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal), [OWASP — Double Encoding](https://owasp.org/www-community/Double_Encoding))
- **Case sensitivity.** Linux filesystems are case-sensitive, Windows/macOS (default) are not. A link `./Foo.md` may resolve on dev (Windows) and 404 on prod (Linux). MkDocs/Docusaurus lean on case-sensitive matching during the build to surface this early.
- **Escape-the-tree paths.** `../../../etc/passwd`-style paths, after `..` normalisation, may resolve outside the exposed root. The standard mitigation is: resolve the candidate path, normalise it, then check that `resolved.is_relative_to(exposed_root)` before serving. Without that check, `WebFetch`-style tools become file-disclosure vectors. ([OWASP — Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal))
- **Anchor-only links** (`#section`) resolve to the *current* file's heading set — not a file lookup at all.
- **Mailto / tel** links carry a scheme and must be classified external even though they don't navigate to a web URL — open via the OS handler (`target="_blank"` is wrong for mailto; just let the browser handle it).
- **Trailing-slash directory links** (`./subdir/`) — MkDocs convention is to resolve to `subdir/index.md` if it exists; raw markdown viewers often fail this case.
- **Parent-directory traversal across the tree boundary.** GitHub markup has long-standing limitations resolving `../` past the repo root. ([GitHub markup issue #84](https://github.com/github/markup/issues/84))

## 3. Implications for the spec

Concrete, actionable choices the spec should pin down:

1. **Classification algorithm (in this exact order):**
   - If the URL has a scheme (`re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I)`) or starts with `//` → **external**, render `target="_blank" rel="noopener noreferrer"`.
   - Else if `href` starts with `#` → **same-file anchor**, render an in-app scroll-to handler.
   - Else treat as **relative**: URL-decode once, normalise (`..`, `.`), join against the source file's parent, assert the resolved path is inside the exposed root. If the file exists in the exposed tree → **internal**, render an in-app `Link`. Otherwise → **broken**.
2. **Exposed-tree definition.** The exposed tree is the union of the three Section-1 globs (`CLAUDE.md`, `.claude/agents/*.md`, `.claude/skills/**/SKILL.md`) plus `specs/{task_type}/{task_name}/{user_input,interview,findings,final_specs,validation}/**`. Anything that resolves outside this set is "broken" by definition, even if it exists on disk — this aligns the security posture with the readonly UX.
3. **Validation timing.** Render-time only for v1. The viewer is readonly with no build step, so each render walks the markdown AST, resolves links, and decorates them. With the locked scale (≤200 files, <500 KB each), per-render resolution is well within budget; no pre-built index needed.
4. **Broken-link rendering.** Render the original link text wrapped in a `<span class="link-broken">` (muted colour), with a `title=` tooltip giving the unresolved target and the reason (`not in tree`, `file not found`, `escapes root`). Do NOT emit `<a>`. This matches the locked Q&A answer and Obsidian's pattern. ([Obsidian forum — unresolved links](https://forum.obsidian.md/t/how-to-approach-non-unique-unresolved-links/94298))
5. **Anchors.** Generate heading IDs with the GFM kebab-case slug rule (with `-1`, `-2` collision suffixes), apply at render time, and resolve `path#anchor` by (a) resolving the path normally, (b) on navigation, scrolling to the heading whose generated id matches the fragment. ([GFM Spec](https://github.github.com/gfm/))
6. **Path-traversal hardening.** The backend file-read endpoint must independently validate that the requested path resolves inside the exposed root, regardless of what the renderer thinks. The link resolver and the file server must not trust each other. ([OWASP — Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal))
7. **Encoding / case.** URL-decode once on the way in. Match filenames case-insensitively on Windows hosts but reject mismatched case with a "case mismatch — fix the link" tooltip — this gives portability across platforms without silently letting through Linux-broken links.
8. **Images.** Same classification, different DOM. Render external image URLs straight; for internal images, serve via the same protected file endpoint as markdown.

## 4. Open questions surfaced

- Should `CLAUDE.md` cross-references that point outside the exposed tree (e.g. to `pyproject.toml` at the repo root) be promoted to internal, or stay broken? The locked spec says Section 1 is "fixed three globs", which suggests staying broken — but `CLAUDE.md` itself happens to mention paths the user might want to click.
- For broken anchors specifically (`spec.md` exists, `#nonexistent` does not), should the link be partly broken (clickable to the file, no scroll target, tooltip explains) or fully broken (muted)? Docusaurus separates these via `onBrokenAnchors`; we should pick one explicitly.
- Anchor-only links inside very long markdown files: do we need a "no such heading" warning surfaced in the UI, or is silent fall-through (browser does nothing) acceptable?
- Image rendering for markdown that embeds binary assets not on the allowed extension list — block, or render with a placeholder?
- Should the in-app navigation preserve the source file's scroll position when the user clicks a link, so back-button feels native?

---

Sources:

- [MkDocs configuration](https://www.mkdocs.org/user-guide/configuration/)
- [mkdocs-autorefs overview](https://mkdocstrings.github.io/autorefs/)
- [Docusaurus — Static Assets](https://docusaurus.io/docs/static-assets)
- [Docusaurus discussion #8613 — onBrokenMarkdownLinks vs onBrokenLinks](https://github.com/facebook/docusaurus/discussions/8613)
- [Docusaurus issue #3321 — detect broken anchor links](https://github.com/facebook/docusaurus/issues/3321)
- [Docusaurus discussion #6465 — markdown vs JSX images](https://github.com/facebook/docusaurus/discussions/6465)
- [GitHub Docs — about READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
- [GitHub markup issue #84 — branch-relative links](https://github.com/github/markup/issues/84)
- [GitHub Heading Anchors gist](https://gist.github.com/asabaylus/3071099)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [GitLab Flavored Markdown](https://docs.gitlab.com/user/markdown/)
- [Obsidian forum — non-unique unresolved links](https://forum.obsidian.md/t/how-to-approach-non-unique-unresolved-links/94298)
- [OWASP — Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP — Double Encoding](https://owasp.org/www-community/Double_Encoding)
