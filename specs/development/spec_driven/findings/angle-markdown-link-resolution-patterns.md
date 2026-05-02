# Angle — Markdown link resolution patterns

Research angle: how the spec_driven viewer should classify, resolve, validate, and render links inside rendered markdown — covering external, anchor, internal-relative, and broken cases — with explicit attention to OS portability (Windows case-insensitive vs Linux case-sensitive), URL encoding, sandbox-traversal escape, GFM heading-slug rules, and the asymmetry between markdown `[text](url)` and raw HTML `<a href>`.

Compared against five comparators: MkDocs validation config, Docusaurus `onBrokenLinks`/`onBrokenAnchors`, GitHub Flavored Markdown heading-id algorithm (github-slugger), Obsidian's wiki-link vs markdown-link rules, and OWASP path-traversal guidance.

Read-zero: only `revised_prompt.md` and `interview/qa.md` consulted; no prior findings.

---

## 1. Why this matters for spec_driven

The spec_driven viewer renders markdown documents that link to one another constantly: `final_specs/spec.md` references `findings/dossier.md`, `validation/strategy.md` references `acceptance_criteria.md`, `qa.md` references `interview/promoted.md`. The interview answers also locked in:

- a strict path sandbox ("Resolve + reject if outside repo", `realpath`-based, case-insensitive comparison on Windows),
- a write-extension whitelist matching the read whitelist (`.md`, `.yaml`, `.yml`, `.json`, `.jsonl`, `.txt`),
- last-write-wins semantics with no `If-Match` guard,
- a missing-artifact empty state (`"Not yet generated — paste this prompt to produce it"`).

Link rendering is the single feature that touches all of these at once: a link inside `spec.md` may be external (open in new tab), an anchor (scroll within the same file), an internal-relative pointer to another tracked file (navigate inside the app), or broken (the target file is missing, the extension is outside the whitelist, the path escapes the sandbox, or the anchor doesn't exist). Every one of these branches has a known-bad failure mode: navigating to a 404, leaking a sandbox-escape attempt as a real `file://` request, scrolling to a stale anchor, or — worst — rendering an `<a href>` that points outside the app and lets the user click out of the sandbox without warning.

This angle answers: how should the viewer classify each link, where should the classification happen (markdown-AST stage vs DOM stage), what should each class render as, and how should the answer change between Windows (where `Spec.md` and `spec.md` are the same file) and Linux (where they aren't)?

## 2. Link classification — the four-class model

Every link inside a rendered artifact falls into exactly one of:

1. **External** — `http://`, `https://`, `mailto:`, `ftp://`, or any URL with an explicit scheme that isn't the app's own. Render as `<a target="_blank" rel="noopener noreferrer">`.
2. **Anchor-only** — `#some-heading`, no path. Resolve against the *current* document. Click smooth-scrolls to the heading element; URL hash updates so the link is shareable.
3. **Internal-relative** — a path with no scheme, e.g. `../findings/dossier.md`, `./acceptance_criteria.md`, `interview/qa.md`. Resolve against the *current document's directory*, then join to the repo root, then re-classify against the sandbox. May carry a `#anchor` suffix.
4. **Broken** — anything that fails resolution: file does not exist, extension outside whitelist, resolved path escapes the sandbox, anchor not found in target document, or the link itself is malformed (unrecognized scheme, empty href).

The ordering matters and is the **single most load-bearing decision** for this feature. The classifier MUST run in this exact order, because the cases are not mutually exclusive at the syntactic level. Concretely:

- **Scheme check first.** If `URL.parse(href)` yields a non-empty `protocol` and the protocol is not the app's own (the dev server's `http://localhost:5173` should NOT be treated as external just because it has a scheme — check the `host` too), it's external. This rejects `javascript:` automatically by listing the *allowed* schemes (`http`, `https`, `mailto`) rather than blocking known-bad ones.
- **Anchor-only second.** `href.startsWith("#")` and no other characters before the `#`. Resolve later against the live DOM, not the markdown AST.
- **Internal-relative third.** Otherwise treat as a path; split off any `#anchor` suffix; resolve relative to the current file's directory using a pure-string POSIX-style join (the markdown is on-disk in repo paths — never use the browser's `URL` constructor against `file://`, which differs between Chrome and Firefox on Windows).
- **Broken last.** Any failure in steps 1–3 demotes the link to broken. Critically, broken is an *outcome class*, not a syntactic class — the same `[link](foo.md)` is internal-relative-resolved on a Linux box where `Foo.md` does not exist, and resolves cleanly on a Windows box where the case-insensitive lookup matches.

This four-class model is the same one MkDocs uses internally (`validation.links.not_found`, `validation.links.absolute_links`, `validation.links.unrecognized_links`, `validation.links.anchors`) and the same one Docusaurus splits across (`onBrokenLinks`, `onBrokenAnchors`, `onBrokenMarkdownLinks`). The split-by-failure-mode pattern is industry-standard.

## 3. Anchor handling — the GFM kebab-case slug

The viewer SHOULD slug headings the same way GitHub does so that links written by humans who are used to GFM "just work". The empirical algorithm (`github-slugger`, the npm package GitHub itself relies on) does the following:

1. Lowercase the heading text after stripping markdown formatting (`**bold**` → `bold`).
2. Remove all characters that are not letters, digits, hyphens, underscores, or whitespace. Notably:
   - Punctuation (`.`, `,`, `?`, `!`, `:`, `;`, `(`, `)`, `[`, `]`, `/`, `\`, `'`, `"`) is stripped.
   - Emoji are stripped entirely (`😄 emoji` → `-emoji`, leaving a leading hyphen which then gets collapsed).
   - Accented letters in Latin scripts are kept (`café` → `café`), not normalized to ASCII. Cyrillic and CJK survive as-is in lowercase form.
3. Collapse consecutive whitespace into a single hyphen, replace remaining whitespace with hyphens.
4. **Do NOT trim leading/trailing hyphens.** This is a frequent point of confusion: a heading like `## ?Question` slugs to `question` (the leading `?` strips, then there is nothing to trim because the hyphen never gets inserted), but `## 😄 Question` slugs to `-question` with a leading hyphen because the emoji strip leaves a space-then-text pattern.
5. Disambiguate duplicates by appending `-1`, `-2`, `-3` in document order. The first occurrence keeps the bare slug. The slugger is *stateful per document*; rendering must reset state between documents.

The viewer's anchor map MUST be built at render time by walking the rendered DOM, not the raw markdown AST, because user-authored raw HTML headings (`<h2 id="custom">`) override the slugged ID. This is the markdown-vs-HTML asymmetry: a `## Foo` heading slugs to `foo`, but `<h2 id="my-custom-id">Foo</h2>` becomes `my-custom-id` and the slug `foo` does NOT exist. Both forms must be queryable from the anchor resolver. The cheapest implementation is to render headings via a custom `react-markdown` `h1`/`h2`/`h3`/… component that injects `id={slug(text)}` AND respects any pre-existing `id` from inline HTML (rendered by `rehype-raw` if HTML is enabled).

Smooth-scroll on anchor click: prefer `element.scrollIntoView({behavior: "smooth", block: "start"})`. Update `window.location.hash` AFTER the scroll starts so back/forward navigation works. Offset for any sticky header by adding `scroll-margin-top` to the heading elements rather than computing offsets in JS — purely CSS, survives layout changes.

## 4. Broken-link rendering — the muted-span rule

Once a link is classified as broken, what does the viewer render? Two options:

- **Option A:** still render an `<a href>`, but with a class that paints it red/strikethrough. Click does nothing (preventDefault) or pops a tooltip "target not found".
- **Option B:** render a `<span>` (or `<a>` with `role="link" aria-disabled="true"`) styled muted/strikethrough, with a `title` attribute explaining the failure. NO `href` attribute at all.

Option B is the correct choice and the recommendations below codify it as the **"muted span never `<a>`" rule**. Reasoning:

1. **No accidental click-through.** With Option A, a misclick (or middle-click "open in new tab") still issues a navigation. On a broken internal-relative link, the navigation hits the dev server or, worse, escapes to `file://` in some browsers. Rendering as `<span>` makes click physically impossible — the browser's link-click affordances simply don't engage.
2. **No leaked sandbox path.** The `<a href>` of a broken-because-it-escapes-sandbox link, if rendered, would expose the attempted-escape path in the page source. With Option B the path is only present in a `data-attempted-href` attribute or a tooltip, which is not crawlable as a link.
3. **Screen-reader semantics.** A `<span>` with `aria-label="broken link to foo.md — target not found"` reads as plain text, not as a link, which matches the user's actual experience (the link doesn't go anywhere).
4. **Accessibility-tree clarity.** `<a>` without `href` is technically valid HTML5 and renders as a non-interactive element, but assistive tech behavior is inconsistent across versions. Plain `<span>` is unambiguous.

The visual: muted foreground (e.g. `color: var(--text-muted)` ≈ 45% opacity), strikethrough on the visible text, a small icon prefix (e.g. `⚠`, `🔗⃠`, or a lucide-react `link-2-off` icon), and `cursor: not-allowed`. Hover reveals the failure reason in a `title` attribute. Optional: a "click to regenerate" affordance if the broken-link target is a known stage artifact (the viewer already mounts the regen panel for missing artifacts per the qa.md "empty state + regen panel mounted" decision; broken links to missing stage files can deep-link into that flow).

## 5. Edge cases

### 5.1 URL encoding

Markdown link targets may be percent-encoded: `[Q&A](interview%2Fqa.md)` or `[α](alpha.md)` (browser may encode the α as `%CE%B1`). The classifier MUST `decodeURIComponent` once before resolving against the filesystem, then compare the decoded path against the on-disk name. Double-encoded inputs are a known traversal vector (see §5.4) — decode exactly once, then refuse if the result still contains `%`.

### 5.2 Case sensitivity (Linux vs Windows)

This is the single largest portability footgun in the project. The viewer's repo will be developed on Windows (interview answers fixed `case-insensitive comparison on Windows`), but artifacts will be authored to land in a repo that may be cloned on Linux/macOS by other contributors and CI. A link that resolves on Windows because `Spec.md` ≈ `spec.md` will return 404 on Linux.

Empirically: NTFS and APFS (default) treat names case-insensitively but case-preservingly — `spec.md` and `Spec.md` collide. ext4 (default Linux) treats them as distinct. Windows 10+ allows per-directory case-sensitivity opt-in for WSL interop, but the default git checkout on Windows is case-insensitive. macOS APFS can be configured case-sensitive but it isn't by default and many macOS apps break.

Defense:

1. **Resolve with `realpath`** (or `pathlib.Path.resolve()` in Python, `fs.realpathSync.native` in Node) — this returns the on-disk casing, not the requested casing.
2. **Compare resolved-canonical against the requested path with a strict (byte-for-byte) string comparison.** If they differ in case, treat the link as broken-because-case-mismatch. Render a distinct warning ("link spelling does not match on-disk file: `Spec.md` vs `spec.md` — fix link text for Linux portability") rather than silently following.
3. The interview answer "case-insensitive comparison on Windows" governs the *sandbox boundary check* (does the resolved path stay inside the repo root?) — for that comparison, case-insensitive is correct because Windows itself is. But for the *link-validity check inside the rendered viewer*, strict case-match SHOULD win, with the warning exposing the latent Linux-incompatibility to the author.

This is the **Windows case-mismatch** recommendation in §6.

### 5.3 Markdown vs HTML link asymmetry

GFM allows raw HTML inside markdown documents. The viewer's render pipeline (likely `react-markdown` + `remark-gfm` + `rehype-raw`) will render both. Concrete asymmetries:

- `[text](url)` is parsed by the markdown parser; `url` may NOT contain unencoded spaces or angle brackets unless wrapped in `<>`.
- `<a href="url">text</a>` is parsed by the HTML parser; `url` is whatever the HTML attribute parser accepts.
- `[text](url "title")` supports title text; `<a href="url" title="title">` supports the same but via a different attribute slot.
- Raw HTML can include `<a href="javascript:...">` — react-markdown by default strips `javascript:` URLs in markdown links via `remark`'s urlTransform but NOT in raw HTML unless `rehype-raw` is paired with `rehype-sanitize`. **This is a real XSS vector** if the viewer ever renders untrusted markdown. For spec_driven the markdown is author-trusted (the user's own files), but the same render pipeline serves any file in the exposed tree, which means the threat model is "operator types `<a href="javascript:fetch('/etc/passwd')">click</a>` into their own file" — non-zero impact only if a follow-up adds untrusted-author rendering. Document the assumption.

The classifier MUST run uniformly across markdown-link and HTML-link AST nodes. The cheapest implementation is to do classification at the rehype stage (after raw HTML has been parsed into hast nodes) rather than at the remark stage (before HTML expansion).

### 5.4 Path-traversal escape (OWASP)

A link with a target like `../../../../../etc/passwd` or `..\\..\\..\\windows\\system32\\drivers\\etc\\hosts` must be classified broken, not followed. OWASP's defense pattern:

1. **Construct the candidate full path** by joining the repo root with the link target. Never split user input around the root.
2. **Normalize** (`os.path.normpath` + `realpath`) to resolve `..`, `.`, redundant separators, and symlinks.
3. **Validate** that the resolved path starts with the repo root (`startsWith` check on the canonical bytes). On Windows compare case-insensitively; on Linux strictly.
4. **Reject everything else.** Encode the rejection as a broken link with reason "outside sandbox".

Critical: do step 2 BEFORE step 3. A naïve `if "../" in target: reject` is bypassed by URL-encoded `..%2F`, double-encoded `..%252F`, Unicode-overlong-encoded variants, and Windows backslash variants `..\` (which `normpath` resolves on Windows but not on POSIX, hence the language-specific normalization choice matters). The OWASP cheat sheet's primary guidance — *normalize then validate, never sanitize* — is exactly the pattern to follow here.

The viewer SHOULD treat traversal-rejected links as a *louder* class of broken than missing-target broken: same muted-span rendering, but the tooltip says "target outside repo sandbox" rather than "target not found", and the failure should be logged to the audit stream (the existing `events.jsonl` could grow a `validation.link.escape_attempt` event type) so authors notice if their templates accidentally generate escape paths.

### 5.5 GFM heading-id vs explicit-anchor

GFM allows authors to write `## My Heading {#custom-id}` (in some flavors) to override the slug. GitHub itself does NOT support the `{#custom-id}` extension — only the implicit slug — but `remark-gfm` + `remark-attr` can. Pandoc and MkDocs do support it natively. The viewer should pick one:

- **Strict GFM (recommended for spec_driven):** only the implicit slug is honored. Authors who need a stable anchor write inline `<h2 id="custom">My Heading</h2>` raw HTML.
- **Extended GFM:** also accept `{#id}` via `remark-attr`. Adds a dependency and a third path through the anchor map.

Strict GFM is fewer moving parts and matches the GitHub-rendered view that authors see when they push to GitHub. Recommendation locks this in.

## 6. Comparator summary

| Comparator | Broken-link policy | Broken-anchor policy | Default | Notes |
|---|---|---|---|---|
| **MkDocs** | `validation.links.not_found` = `info` / `warn` / `ignore`; default `warn`; `--strict` flag promotes warns to errors | `validation.links.anchors` = same enum; default `info` | Build-time fail under `--strict`; otherwise log only | Also splits `absolute_links`, `unrecognized_links` |
| **Docusaurus** | `onBrokenLinks` = `ignore` / `log` / `warn` / `throw`; default `throw` | `onBrokenAnchors` = same enum; default `warn` | Build-time fail by default for paths, log-only for anchors | `onBrokenMarkdownLinks` deprecated v3.9 → `siteConfig.markdown.hooks.onBrokenMarkdownLinks` |
| **GFM (github-slugger)** | n/a (GitHub renders broken internal links as plain styled text) | Slugged at render time; duplicates suffix `-1`, `-2`; emoji stripped; accented kept | n/a | `github-slugger` is the de facto reference impl |
| **Obsidian** | Wiki-link `[[Foo]]` to nonexistent file renders as a *placeholder link* in a different colour; clicking creates the file. Markdown link `[text](foo.md)` to nonexistent file renders as a normal link that 404s on click | Anchors via `[[Note#Heading]]` and block refs `[[Note^block]]` | Wiki-link "create on click" UX is Obsidian-specific | Wiki-links support backlinks; markdown links do not. Resolution is case-insensitive, file extensions are usually omitted in wiki-links |
| **OWASP path-traversal cheat sheet** | "Normalize then validate against allowed root; do not sanitize" | n/a | Reject on resolved-path-outside-root | Use indexes/whitelists where possible; `realpath` then `startsWith(root)` |

Two takeaways:

- **Default-to-warn is industry-standard** for anchors (Docusaurus, MkDocs). For path links the trend is to fail harder (Docusaurus default `throw`). spec_driven's viewer should *render-warn* (muted span) rather than *fail-build* because there's no build step — the markdown is rendered live.
- **Obsidian's "create on click" UX is interesting but out of scope.** The interview answer locked "edit existing only — `PUT /api/file` requires the path to already exist", which forecloses click-to-create. A broken-link click could *deep-link to the regen panel* instead, which is the closest spec_driven analogue.

## 7. Recommendations

1. **Fixed classification order.** Implement link classification as a single pure function `classifyLink(href, currentDocPath, sandboxRoot, anchorMap) → {kind: "external"|"anchor"|"internal"|"broken", reason?, resolvedPath?}` that evaluates in the order: scheme → bare-anchor → internal-relative → broken. No fallthrough; every input lands in exactly one bucket.

2. **Anchor scrolling via `scrollIntoView` + `scroll-margin-top`.** Use the native smooth-scroll API; size the offset for any sticky header in CSS (`scroll-margin-top: 4rem` on heading elements). Update `window.location.hash` after scroll starts so the URL is shareable and back/forward work. Build the anchor map at render time by querying the rendered DOM (`document.querySelectorAll("h1[id], h2[id], …")`), not by re-walking the markdown AST — this captures both GFM-slugged and inline-HTML-`id` cases uniformly.

3. **Broken-link visual: muted span with strikethrough + warning icon + tooltip.** Foreground at ~45% opacity, line-through, leading icon, `cursor: not-allowed`, `title` attribute carrying the failure reason. Distinct sub-styles for `not-found`, `outside-sandbox`, `case-mismatch`, and `bad-anchor` so authors can scan for problems visually.

4. **"Muted span never `<a>`" rule.** Broken links MUST render as `<span>` (or `<a>` without `href`), never as `<a href="...">`. This forecloses misclicks, middle-click navigation, and accidental sandbox-escape leaks. Encode the attempted target in `data-attempted-href` for inspector debugging only.

5. **Windows case-mismatch warning, not silent follow.** Resolve with `realpath`; compare resolved canonical name byte-for-byte against the link's spelling; if they differ only in case, render as broken-with-reason `case-mismatch` so the author fixes the link before a Linux contributor or CI box hits a 404. Do NOT silently follow on Windows just because the OS would.

6. **Normalize-then-validate for traversal defense, with audit logging.** Use Python's `pathlib.Path.resolve(strict=False)` server-side and `path.posix.normalize` + `startsWith(repoRoot)` client-side. On rejection, fire a `validation.link.escape_attempt` event into the existing `events.jsonl` audit stream. Reject double-encoded, mixed-slash, and absolute-path variants uniformly via the resolve→compare flow rather than ad-hoc string filters.

7. **Strict GFM slug, no `{#custom-id}` extension.** Use `github-slugger` directly for heading IDs. Authors needing a stable custom anchor write inline `<h2 id="custom">…</h2>` raw HTML, which the rehype stage picks up. This keeps anchor behavior identical to what authors see when the same markdown is rendered on GitHub, removes one rendering dependency, and avoids the duplicate-anchor disambiguation problem when both `{#id}` and `## Heading` exist.

8. **Internal-relative click navigates inside the app, never `<a href>` to the file.** When an internal-relative link resolves to an in-sandbox tracked file, render an `<a href="#">` whose `onClick` calls the app router (`navigate(viewerPath(resolved))`) and `event.preventDefault()`s. This keeps the SPA contract intact, preserves browser back/forward via the router, and prevents the dev server from being asked for the raw `.md` (which would either 404 or — worse on a misconfigured prod build — serve the file as `text/plain` and skip the viewer entirely). External and `mailto:` links are the *only* cases where a real `href` is rendered.

## Open questions / not researched

- **Custom anchor extensions in spec_driven's own templates.** Whether the spec compilation template ever emits `{#id}` or relies purely on natural slugs is undetermined without reading prior `final_specs/spec.md` (forbidden by read-zero). Stage 4 should standardise.
- **Wiki-link `[[…]]` syntax.** The viewer uses GFM, which does not support wiki-links. Whether authors will *want* `[[other_file]]` ergonomics (Obsidian-style) is a UX question for a follow-up, not this pass.
- **Image links vs file links.** This angle covers `<a>` rendering only. Image src resolution (`![alt](path.png)`) follows the same classification but renders a broken-image placeholder rather than a muted span — out of scope for this angle.
- **Link rewriting on save.** The interview locked "regex parse, re-emit whole file" for qa.md but no one asked whether other-file edits should auto-rewrite stale links (e.g., when a heading is renamed, should existing anchor links update?). Conservative default: do not. Flag for stage 5 if it matters.
- **Performance of building the anchor map per render.** `document.querySelectorAll` on a 50-heading document is sub-millisecond; on a 5000-heading document (unlikely for spec artifacts) it might matter. Not measured.
- **Internationalisation of slugs.** `github-slugger` keeps non-ASCII letters, but Obsidian's slug strips them. Whether spec_driven artifacts will ever contain non-Latin headings is undetermined; current artifacts are English-only.

## Sources

- [MkDocs Configuration — validation.links options](https://www.mkdocs.org/user-guide/configuration/)
- [MkDocs Link Validation overview (DeepWiki)](https://deepwiki.com/mkdocs-ng/mkdocs/3.5-link-validation)
- [Docusaurus docusaurus.config.js — onBrokenLinks/onBrokenAnchors](https://docusaurus.io/docs/api/docusaurus-config)
- [Docusaurus PR #9528 — adding onBrokenAnchors](https://github.com/facebook/docusaurus/pull/9528)
- [github-slugger (Flet/github-slugger) — heading slug algorithm](https://github.com/Flet/github-slugger)
- [GitHub anchor heading reference gist (asabaylus)](https://gist.github.com/asabaylus/3071099)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [Obsidian forum — GFM kebab-case heading-slug feature request](https://forum.obsidian.md/t/support-gfm-style-kebab-case-heading-slug-anchor-targets/30350)
- [Obsidian forum — Wiki-link vs Markdown link support](https://forum.obsidian.md/t/wikilink-vs-markdown-the-latter-suffers-from-lack-of-support/86920)
- [Obsidian forum — non-existing file linkage behavior](https://forum.obsidian.md/t/internal-inks-use-wikilinks-instead-of-markdown-links-for-non-existing-files/61795)
- [OWASP — Path Traversal attack overview](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP Cheat Sheet Series root](https://cheatsheetseries.owasp.org/)
- [PortSwigger Web Security Academy — Path Traversal](https://portswigger.net/web-security/file-path-traversal)
- [Microsoft Learn — WSL Case Sensitivity](https://learn.microsoft.com/en-us/windows/wsl/case-sensitivity)
- [Microsoft DevBlogs — Per-directory case sensitivity and WSL](https://devblogs.microsoft.com/commandline/per-directory-case-sensitivity-and-wsl/)
- [LWN — Filesystems and case-insensitivity](https://lwn.net/Articles/772960/)
- [remarkjs/react-markdown — custom component rendering of links](https://github.com/remarkjs/react-markdown)
