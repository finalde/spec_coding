# Angle: Markdown link resolution patterns

Scope: how spec_driven's reader/editor should classify, resolve, and render the
links it encounters in artifacts under `specs/{type}/{name}/` and
`projects/{name}/`. The reader is a localhost FastAPI + React app, so relative
paths between artifacts (e.g. `../findings/dossier.md` from inside
`final_specs/spec.md`) must resolve in-app, not point at the filesystem URL bar.

The web has two decades of prior art for this problem (every static-site
generator solves a version of it). This angle distills the relevant behavior
of five comparators — MkDocs, Docusaurus, GFM/GitHub, Obsidian, OWASP — and
ends with concrete recommendations for the spec_driven link classifier.

## 1. Link classification: the four buckets

Every `<a href>` produced from rendered markdown falls into one of four
buckets. The order in which a classifier checks them is load-bearing because
classification is the side effect that decides whether the click goes to the
browser, to an in-app router, to a scroll behavior, or to a "muted span" with
no navigation at all.

The four buckets, in the order spec_driven should evaluate them:

1. **Same-file anchor** — `href` starts with `#`. No path component, just a
   fragment. Click should scroll, not navigate.
2. **External** — absolute URL with a scheme the browser handles
   (`http`, `https`, `mailto`, `tel`). Click opens in a new tab; never
   intercepted by the in-app router.
3. **Internal-app** — relative path or root-relative path that, after
   normalization, points to another file inside the project tree the app
   serves. Click goes through the app router.
4. **Broken** — anything that looks like a relative reference but doesn't
   resolve to a known artifact, plus anchors whose fragment doesn't exist on
   the target page. Rendered as a muted span (never an `<a>`).

This is the same shape MkDocs landed on. Its 1.5+ validation tree splits link
problems into `links.not_found` (bucket 4 for paths) and `links.anchors`
(bucket 4 for fragments), each with its own severity dial
([MkDocs validation config](https://www.mkdocs.org/user-guide/configuration/)).
Docusaurus made the same split: `onBrokenLinks` for paths and
`onBrokenAnchors` for fragments
([Docusaurus config](https://docusaurus.io/docs/api/docusaurus-config)).
The split matters because the two failure modes have very different signal
strengths — a broken path is almost always a real bug, whereas a broken
anchor is much more often a stale slug after a heading rename.

### CommonMark/GFM does not classify, it just parses

Worth noting up front: the GFM spec itself does not say anything about how
href values should be resolved or classified — it's a parsing spec, not a
rendering spec. There's no slug rule, no path-resolution rule, no anchor
existence check
([GFM spec](https://github.github.com/gfm/)). Every renderer (GitHub.com,
MkDocs, Docusaurus, Obsidian, react-markdown) implements its own classifier
on top of the parser. Whatever spec_driven does is its own contract; we
should pick one and document it.

## 2. Same-file anchors and the GFM kebab-case slug rule

The convention every modern markdown reader follows for heading anchors is
GitHub's slug algorithm — applied at render time, not part of the GFM spec
([GFM spec](https://github.github.com/gfm/),
[GitHub heading anchors gist](https://gist.github.com/asabaylus/3071099)).
The rules:

- Letters lower-cased.
- Spaces replaced with `-`.
- Other punctuation (`.`, `,`, `?`, `!`, `:`, `;`, `(`, `)`, `[`, `]`,
  quotes, backticks) stripped.
- Other whitespace runs collapsed.
- Duplicates within the same document get a `-1`, `-2`, … suffix in
  document order.

So `## Validation strategy: BDD scenarios` becomes
`#validation-strategy-bdd-scenarios`. `## Step 2: Run!` becomes `#step-2-run`.
A second `## Notes` becomes `#notes-1`.

The GFM spec is silent on whether non-ASCII letters should survive. GitHub's
own behavior preserves them (the slug for `## Café` is `#café`), but some
renderers strip them. spec_driven's artifacts are all-English by convention,
so this corner shouldn't bite us, but the classifier should not assume
ASCII-only when computing slugs — Python's `re.sub(r"[^\w\s-]", "")` with the
default Unicode-aware `\w` matches GitHub's behavior closely enough.

### Anchor scroll behavior

Two common pitfalls:

- **Sticky headers** swallow the scroll target. If the header is 64px tall,
  `element.scrollIntoView()` lands the heading under the header. Use
  `scrollIntoView({ block: "start" })` plus CSS `scroll-margin-top: 64px`
  on heading nodes, or explicitly subtract the header height in the scroll
  call.
- **Anchor on the same page that's already mounted** vs. **anchor on a page
  not yet loaded**. A SPA must defer the scroll until after the target
  route's content has rendered. React-router's `useEffect` keyed on
  `pathname + hash` is the standard pattern.

Docusaurus's `onBrokenAnchors` defaults to `warn`, not `throw`, precisely
because anchor staleness is so common — and it ships with a known-bug
caveat that the validator can produce false positives for plugin-registered
anchors ([Docusaurus config](https://docusaurus.io/docs/api/docusaurus-config)).
spec_driven should treat a missing anchor the same way: render the link as a
broken muted span, but don't fail the page load.

## 3. External links

Easy bucket. Match by scheme: anything that parses with a scheme in
{`http`, `https`, `mailto`, `tel`} is external. Everything else is either
relative or `javascript:` (which we drop entirely as a sanitizer step;
react-markdown does this by default via its built-in href filter
([react-markdown](https://github.com/remarkjs/react-markdown))).

The CommonMark spec does maintain a whitelist of URI schemes recognized
inside `<...>` autolinks
([CommonMark autolink discussion](https://talk.commonmark.org/t/what-is-the-point-of-limiting-uri-schemes-in-autolinks/555)),
but for our purposes the simpler four-scheme allowlist plus a
`javascript:`/`data:` block is enough.

External links should always open in `target="_blank"` with
`rel="noopener noreferrer"`. The reader is on `localhost`, so leaking the
referrer doesn't matter much, but `noopener` prevents the opened page from
hijacking `window.opener`.

## 4. Internal-app links: the resolution pipeline

This is the bucket where most of the design lives. Steps:

1. **Strip the fragment**. Split `href` on the first `#`; keep the path side
   and the fragment side as separate strings.
2. **URL-decode once.** `%20` → space, `%2e` → `.`, etc. This is the
   "canonical form before validation" rule from
   [OWASP Input Validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
   and the corresponding warning in
   [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal):
   web containers do exactly one decode pass on percent-encoding, and
   double-decoding is the classic bypass for naïve filters that decode
   *after* validating. Decode once; never decode twice.
3. **Resolve relative to the source artifact**. If the source file is
   `specs/development/spec_driven/final_specs/spec.md` and the link is
   `../findings/dossier.md`, the resolved path is
   `specs/development/spec_driven/findings/dossier.md`. Use `posixpath.normpath`
   (or browser-side `URL` resolution with a synthetic base) — never string
   concatenation.
4. **Verify no-escape**. After normalization, the resolved path MUST start
   with the project root the API is allowed to serve. If the user wrote
   `../../../../etc/passwd`, the normalized result is outside the root and
   the link gets bucketed as broken (and the API endpoint that would serve
   it must independently re-check this — the classifier is UX, not the
   security boundary).
5. **Existence check**. Look up the resolved path in an index of known
   artifacts. If it exists, it's an internal-app link with a router target.
   If not, it's broken.
6. **Anchor existence check** (only if the path side resolved). Run the
   target file through the same slug extractor that built the source
   document's TOC, then check whether the link's fragment is in that set.
   Missing fragment → broken-anchor. Empty fragment (just a path) → no
   anchor check needed.

MkDocs follows essentially the same pipeline but as a build-time pass:
`validation.links.unrecognized_links` catches step-3 failures
("malformed relative paths"), `validation.links.not_found` is step 5,
`validation.links.anchors` is step 6, and
`validation.links.absolute_links: relative_to_docs` lets `/foo/bar.md` be
treated as relative to the docs root rather than as an absolute server URL
([MkDocs validation config](https://www.mkdocs.org/user-guide/configuration/)).
spec_driven should follow the same convention: a link starting with `/`
should resolve relative to the served root, not be treated as an external
link.

### Markdown vs HTML link asymmetry

Markdown link `[a](path)` and a literal HTML `<a href="path">` lower-cased
into the rendered output should classify identically. They almost always
do, but there's one subtle case: react-markdown's default sanitizer (rehype)
will pass through HTML hrefs but apply slightly different filtering than
markdown links. The cleanest pattern is to register the same custom
component for both `a` (HTML) and `link` (markdown link AST node) so a
single classifier runs once, regardless of source syntax. This is the
react-markdown idiom — pass `components={{ a: MyLink }}` and the same
component renders both
([react-markdown docs](https://github.com/remarkjs/react-markdown)).

## 5. Edge cases

### URL encoding, decode-once

Already covered in step 2 above, but worth restating the guarantee. The
classifier MUST decode percent-encoding exactly once before path resolution
and existence checks. It MUST NOT decode the result of the resolved path a
second time before the no-escape check. OWASP's path-traversal page makes
this explicit: "URL encoding or even double URL encoding of the `../`
characters can sometimes bypass sanitization, resulting in `../` and
`%2e%2e%2f` respectively. Double URL-encoding the input will bypass
defenses that only URL-decode once" — the defense is to decode once and
then validate, never decode after validating
([OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)).

### Case sensitivity Linux vs Windows

The hardest cross-platform corner. On Linux the filesystem is case-sensitive
by default; on Windows (NTFS, FAT32, exFAT) it is case-insensitive but
case-preserving — `Document.txt` and `document.txt` are the same file, but
the OS remembers which one you originally typed
([Microsoft case sensitivity](https://learn.microsoft.com/en-us/windows/wsl/case-sensitivity)).
NTFS does support per-directory case-sensitivity since Windows 10 build
17107, but it's off by default and almost no one enables it.

The implication for spec_driven: a link `../FINDINGS/dossier.md` written by
a user on Windows will silently resolve in their local FS but break for a
Linux user pulling the same repo. The VS Code markdown language service ran
into exactly this issue and punted: their stance, paraphrased, was "paths
on Windows are case insensitive; however this library makes a lot of
assumptions about paths being case sensitive — we should figure out what
to do about this (if anything)"
([vscode-markdown-languageservice #106](https://github.com/microsoft/vscode-markdown-languageservice/issues/106)).
Obsidian made the opposite call: wikilinks AND markdown links match
filenames case-insensitively across all platforms, and when the user
highlights existing text and converts it to a link, the text is rewritten
to match the canonical case of the target file
([Obsidian case sensitivity](https://forum.obsidian.md/t/case-sensitivity/52331)).

For spec_driven, the right call is **case-sensitive resolution by default,
with a "did you mean" hint** when a case-insensitive match exists but the
case-sensitive lookup failed. This catches the Windows-author / Linux-CI
class of bug without silently papering over typos. (See recommendation 5
below.)

### Traversal escape

Already covered: after `posixpath.normpath` normalizes `..` and `.`, assert
the result is `startswith(allowed_root + os.sep)`. The classifier treats a
fail as broken. The API endpoint that serves the file MUST re-check
independently — never trust the classifier as a security boundary.

### GFM kebab-case slug rule, in code

Reproducible algorithm spec_driven needs to ship in BOTH the renderer (to
build the TOC) and the validator (to check link fragments):

```
slug = heading_text.lower()
slug = re.sub(r"[^\w\s-]", "", slug, flags=re.UNICODE)
slug = re.sub(r"[\s]+", "-", slug).strip("-")
# duplicate handling: if slug already used in this doc, append "-N"
```

This matches GitHub's behavior closely enough for our artifacts
([GFM heading anchors](https://gist.github.com/asabaylus/3071099)). It
does NOT match Docusaurus's slug algorithm exactly (Docusaurus uses
github-slugger which preserves a few more characters), but for the
all-English headings in our specs the divergence doesn't bite.

### Markdown vs HTML link asymmetry, redux

One non-obvious case: an HTML `<a href="./foo.md#bar">` written literally
inside markdown is parsed and rendered, and our classifier sees the same
href string a `[link](./foo.md#bar)` would produce. Good. BUT: if a user
writes raw HTML `<a name="manual-anchor"></a>` to create a manual anchor
target, our slug-extractor (which only walks heading nodes) won't pick it
up, and a link to `#manual-anchor` will be classified as a broken anchor.
Two ways to handle: either also walk for `id=`/`name=` attributes when
building the anchor set, or document that manual anchors are not
supported. spec_driven should support manual anchors — they're useful for
deep-linking into long sections — so the slug extractor should walk the
full HAST and collect every `id` attribute, not just heading IDs.

## 6. Broken-link rendering: the "muted span never `<a>`" rule

Critical UX rule, from the user's brief: a broken link must NOT render as
an `<a>` element at all. It renders as a `<span>` with muted styling and
(ideally) a tooltip or hover-state explaining why it's broken
("file not found", "anchor #foo not present in target.md"). No href, no
click handler, no underline-on-hover.

Why this rule exists:

- An `<a>` with an href that 404s in the in-app router is a worse UX than
  a visibly-dead span. The user clicks, the router thrashes, the user
  blames the app.
- Right-click → copy-link on a broken `<a>` copies a URL the user will
  paste into a chat asking "why is this 404'ing" — and there's no
  in-document signal that the original link was already known-broken.
- Screen readers announce `<a>` as "link". Announcing a broken link as
  "link" is a lie. A `<span role="text" aria-label="broken link: ...">` is
  honest.

Docusaurus and MkDocs both surface broken links at build time and either
fail the build or warn loudly; neither has an in-app rendering for a
known-broken link because their output is static. spec_driven is a live
viewer over a moving filesystem — links can break between page loads —
so the in-app contract matters more.

## 7. Recommendations for spec_driven's link classifier

These are the concrete decisions the implementation should make. Numbered
so they can be referenced by spec section.

1. **Decision order (single classifier, runs on every rendered link):**
   1. If `href` starts with `#` → bucket 1 (same-file anchor). Verify the
      slug exists in the current document's anchor set; if not, render
      muted span.
   2. Else if `href` parses with scheme in {`http`, `https`, `mailto`,
      `tel`} → bucket 2 (external). Render as `<a target="_blank"
      rel="noopener noreferrer">`.
   3. Else if `href` matches `/javascript:|^data:/i` → drop the `<a>`
      entirely; render the link text as a muted span.
   4. Else treat as bucket 3/4 candidate. Strip fragment, decode percent
      exactly once, normpath relative to source artifact, assert
      result is inside the served root, check existence in artifact index,
      check anchor existence on target. Any failure → bucket 4 (broken,
      muted span).

2. **Anchor scrolling**: target the anchor with `scrollIntoView({ block:
   "start" })` and `scroll-margin-top: <header-height>px` on every heading
   node. For anchors on the SAME route, scroll on click. For anchors on a
   different route, register the scroll-on-hash effect after the target
   route mounts — keyed on `pathname + hash` so back/forward works.

3. **Broken-link visual contract**:
   - Element: `<span>`, never `<a>`.
   - Class: `link-broken` with muted color (e.g., `color: var(--text-muted)`),
     dotted underline.
   - `title` attribute (tooltip): `"Broken link: <reason>. Resolved path:
     <normalized path or anchor>."`
   - `aria-label`: same content.
   - Cursor: `cursor: not-allowed`.
   - Copy-paste behavior: text is selectable; the underlying href string
     is NOT in the DOM, so right-click → copy-link is unavailable by
     construction. This is a feature.

4. **The "muted span never `<a>`" rule, restated as a hard invariant**: any
   code path in the renderer that produces an `<a>` element MUST have run
   the classifier and gotten back bucket 1, 2, or 3. Bucket 4 produces a
   `<span>`. There is no fallback that renders `<a href="...">` without
   classification — if the classifier crashes, the link renders as plain
   text with no element wrapping at all.

5. **Windows case-sensitivity handling**: resolution is case-sensitive by
   default (Linux semantics). Authoring is on Windows where the
   filesystem won't reject mismatched case, so the classifier additionally
   maintains a case-folded index. When a case-sensitive lookup fails but
   a case-folded match exists, the link is still classified as broken
   (preserving the strict default), but the broken-link tooltip includes
   `"Did you mean: <correctly-cased path>?"`. This catches the
   Windows-author / Linux-CI class of bug without silently fixing it.

6. **Decode-once invariant**: percent-decoding happens exactly once,
   between fragment-strip and normpath. The classifier MUST NOT call
   `decodeURIComponent` (or `urllib.parse.unquote`) on the result of
   normpath, on the result of the existence check, or anywhere downstream.
   A unit test should assert that an href like `..%2f..%2fetc%2fpasswd`
   classifies as broken (after one decode it's `../../etc/passwd`,
   normpath escapes the root, no-escape check fails) while
   `..%252fetc` classifies as broken via the existence check (after one
   decode it's `..%2fetc`, which is a literal filename and won't be
   found).

7. **Bucket-4 split for telemetry / future authoring tooling**: even
   though both render as muted spans, internally distinguish
   `BROKEN_PATH` from `BROKEN_ANCHOR`. This mirrors the
   `onBrokenLinks`/`onBrokenAnchors` split in Docusaurus and lets a
   future "fix all broken links" tool offer different remedies for each.
   The split also lets us downgrade `BROKEN_ANCHOR` from "blocking" to
   "warning" if it turns out heading renames are common enough to be noisy.

8. **Slug extraction walks the entire HAST, not just headings**. Collect
   every `id` attribute the rendered tree produces — heading auto-IDs
   plus any literal `<a id="...">` or `<div id="...">` written by the
   author. This avoids false-positive broken-anchor flags on artifacts
   that use manual anchors for deep-linking inside long sections.

## Open questions / not researched

- **Slug algorithm divergence with code-fence headings**: GitHub treats
  `## \`code\` heading` differently from Docusaurus's github-slugger;
  we haven't audited which our artifacts use in practice.
- **Image links**. This angle covered `<a>` only. `<img>` href resolution
  follows similar rules but with different security considerations
  (no scheme allowlist needed, but `data:` URLs deserve a size cap).
  Out of scope here.
- **Link rewriting on artifact rename**. If `findings/dossier.md` is
  renamed, do we rewrite incoming links across the project tree, or just
  let them break and rely on the muted-span signal? Not researched.
- **WikiLink-style `[[...]]` syntax**. Obsidian users may paste these
  in; do we support them at all? If yes, do we follow Obsidian's
  case-insensitive normalized-match rule, or our own? Not researched —
  recommend rejecting the syntax until we have a use case.
- **Link checker as a CI gate**. MkDocs and Docusaurus both can fail the
  build on broken links. spec_driven could expose the same as a
  one-shot CLI. Not researched here.
- **Cross-project links** — e.g., a spec_driven artifact linking to a
  different project's spec. We don't currently scope link resolution
  beyond the one project's tree; whether we should is an open product
  question.

## Sources

- [MkDocs Configuration — validation](https://www.mkdocs.org/user-guide/configuration/)
- [Docusaurus Configuration — onBrokenLinks / onBrokenAnchors](https://docusaurus.io/docs/api/docusaurus-config)
- [GitHub Flavored Markdown Spec](https://github.github.com/gfm/)
- [GitHub heading anchors algorithm (asabaylus gist)](https://gist.github.com/asabaylus/3071099)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [Microsoft Learn — Case Sensitivity (Windows / WSL / NTFS)](https://learn.microsoft.com/en-us/windows/wsl/case-sensitivity)
- [Obsidian Forum — Case sensitivity discussion](https://forum.obsidian.md/t/case-sensitivity/52331)
- [Obsidian wikilink rules (dhpwd gist)](https://gist.github.com/dhpwd/9bb86c53b69cb63e09ccca42e3bf924c)
- [vscode-markdown-languageservice issue #106 — case sensitivity](https://github.com/microsoft/vscode-markdown-languageservice/issues/106)
- [react-markdown — components prop and href filtering](https://github.com/remarkjs/react-markdown)
- [CommonMark autolink URI scheme allowlist discussion](https://talk.commonmark.org/t/what-is-the-point-of-limiting-uri-schemes-in-autolinks/555)
