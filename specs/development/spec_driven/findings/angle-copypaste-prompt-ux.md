# Angle: copypaste-prompt-ux

## 1. What this angle covers

The webapp builds a regeneration prompt the user must paste into Claude Code CLI. The artifact is text-only, frequently 5–50 KB and occasionally up to 1 MB (hard ceiling enforced by 413). The UI's job is twofold:

1. Make the prompt **readable in place** (line-height, soft-wrap toggle, dark code theme, scrollable region).
2. Make the prompt **trivial to grab** — a prominent "Copy" affordance, accurate metadata about what was assembled (stage count, follow-ups inlined, autonomous flag, byte size), and graceful behavior at the edges (warn at 50 KB, block at 1 MB, "Copied!" feedback, optional download fallback).

This angle surveys what mature dev tools and design systems have converged on for "copy this multi-thousand-character text" affordances: button placement, size surfacing, truncation/warn/block policy, "Copied!" signaling, and clipboard-vs-download offers.

## 2. Key findings

### a) Where the Copy button goes

- **Header bar above the body, top-right of the header, is the dominant pattern.** Modern code-block conventions use a flex header with a left-side label (language / filename / metadata) and a right-side Copy button; the button sits in the header rather than overlaying the body, so it does not move when the body scrolls. ([whitep4nth3r — How to build a copy code snippet button](https://whitep4nth3r.com/blog/how-to-build-a-copy-code-snippet-button/), [amanhimself.dev — advanced code blocks with Shiki](https://amanhimself.dev/blog/advanced-code-blocks-with-shiki-and-astro/))
- **Floating / sticky variant for very long blocks.** When code is long enough that a static header scrolls out of view, the button can float top-right of the viewport so users do not have to scroll back up. This is exactly the pattern ChatGPT-style chat UIs adopted; users have actively requested the same in other tools. ([open-webui issue #5767 — Floating copy button like ChatGPT](https://github.com/open-webui/open-webui/issues/5767))
- **PatternFly's "expandable" clipboard-copy variant** is the design-system encoding of the same idea: for "long lines of text" the component expands into a panel; the inline compact variant is reserved for short single-line content. ([PatternFly — Clipboard copy design guidelines](https://www.patternfly.org/components/clipboard-copy/design-guidelines/))
- **Hiding the prompt behind a `<details>` is an anti-pattern for primary-action content.** Search results and design-system guidance treat "click to copy" as a *primary* micro-interaction; the consistent recommendation is to keep it visible and reachable in one click, not behind progressive disclosure.

Implication: a fixed header bar with the Copy button on the right matches established practice. A second sticky/floating Copy that appears only after the user scrolls past the header is a known refinement; not required for v1, but on the table.

### b) How tools surface the size of large copy targets

- **Inline metadata next to the action button is the norm** — language label on the left, byte/length info adjacent to (or just under) the Copy button on the right. The webapp's planned "{N} stages, {K} follow-ups, autonomous=…, {bytes} KB" line is consistent with this pattern.
- **Soft-warning banners around 75–80% of the hard limit** are a long-established pattern for size-bounded content. Next.js warns at 128 KB of page data (a fraction of the actual hard cap) precisely so devs can act *before* hitting failure; HTML5 banner ad pipelines warn well below the 150 KB IAB ceiling. ([Next.js — Large Page Data](https://nextjs.org/docs/messages/large-page-data), [checksafe.zone — HTML5 Banner Validator](https://checksafe.zone/validator))
- **Soft-quota / hard-quota separation is the canonical model.** "Soft quotas send a warning message when resource usage reaches a certain level, but do not affect data access operations, so you can take appropriate action before the quota is exceeded." ([NetApp — hard, soft, threshold quotas](https://docs.netapp.com/us-en/ontap/volumes/differences-hard-soft-threshold-quotas-concept.html)) That maps cleanly onto: ≥50 KB → muted warning banner; >1 MB → 413, do not render.

### c) Truncate vs. warn vs. block

- **Don't silently truncate text destined for the clipboard.** Multiple bug threads (Alacritty, Monaco, kitty, VS Code) document that silent truncation of large clipboard targets is treated as a bug, not a feature — users expect the full content or a visible failure, not a quietly mangled paste. ([alacritty/alacritty#6848](https://github.com/alacritty/alacritty/issues/6848), [microsoft/monaco-editor#1540](https://github.com/microsoft/monaco-editor/issues/1540), [kovidgoyal/kitty#3937](https://github.com/kovidgoyal/kitty/issues/3937), [microsoft/vscode#5498](https://github.com/microsoft/vscode/issues/5498))
- **Warn early, block hard, never truncate.** The convergent pattern across Next.js, IAB/Campaign Manager, and OS-level quota systems is: a soft warning lets the user act, the hard limit produces a clean refusal with an actionable message, and there is no "we silently shortened your content" middle state.
- The webapp's plan (warn ≥50 KB, hard 413 at >1 MB and do NOT render the prompt block) sits squarely on this convention.

### d) "Copied!" state signaling

- **2-second timeout is the de facto standard.** Multiple component libraries (Modern UI, Shoelace, shadcn copy button, Framer Motion implementations) reset the success state after ~2000 ms; 1–3 s is the working range. ([Modern UI — Copy Button](https://modern-ui.org/docs/components/copy-button), [Shoelace — Copy Button](https://shoelace.style/components/copy-button), [shadcn — Copy Button](https://www.shadcn.io/button/copy))
- **Icon swap (clipboard → check) is the dominant visual.** Often paired with a tooltip whose text flips from "Copy" to "Copied!" for assistive-tech parity. PatternFly explicitly specifies that the tooltip "informs users that clicking the button will copy the content" then "will update to convey success" after interaction. ([PatternFly — Clipboard copy design guidelines](https://www.patternfly.org/components/clipboard-copy/design-guidelines/))
- **Toast notifications are an alternative, not a replacement.** Inline button feedback is mandatory; a global toast is optional and tends to be reserved for cases where the button is small/icon-only and visual feedback would be missed.
- **Accessibility is a hard contract.** Icon-only buttons need an `aria-label` (e.g., "Copy prompt to clipboard"); the Copied state should also be exposed (e.g., updating `aria-label` or using an `aria-live` region) so screen-reader users hear the confirmation.

### e) When to offer Download as file vs. clipboard only

- **Clipboard-only is fine up to "a few hundred KB" in practice.** The Async Clipboard API has no hardcoded text-size cap, but historical bug threads show that very large strings (Mb-scale) hit performance, browser-specific, and OS-clipboard friction. ([clipboard.js#407 — Firefox fails to copy bigger amount of data](https://github.com/zenorocha/clipboard.js/issues/407), [The Old New Thing — Windows clipboard size](https://devblogs.microsoft.com/oldnewthing/20220608-00/?p=106727))
- **Design-system precedent for offering format alternatives at large sizes exists.** Tools like Kibana and similar admin UIs offer "Copy as JSON / Copy as TXT / Download" when content is large. ([elastic/kibana#179731 — Copy rows as text UX enhancements](https://github.com/elastic/kibana/issues/179731))
- For a prompt that can reach 1 MB, a **secondary "Download .md" button alongside Copy** is a reasonable safety net even if Copy still works — it gives the user a path when the OS-level paste target chokes on a giant clipboard payload (some terminals, RDP/SSH paste channels, browser-restricted contexts). Established practice supports it; it is not strictly required.

### Practice vs. opinion

- Established: header-bar Copy on the right, 2 s "Copied!" state, soft-warn / hard-block separation, no silent truncation, expandable variant for long content.
- Lighter consensus / my synthesis: the specific 50 KB warning and 1 MB hard ceiling are the webapp's own choice; they sit in the right zone (warn at ~5% of cap) but the exact numbers are a product call, not an industry standard.
- Author opinion: a Download fallback at >50 KB is a low-cost safety net given how heterogeneous OS paste targets are; the spec can defer it to v2 without sacrificing core UX.

## 3. Implications for the spec (concrete, actionable)

1. **Header bar layout.** Each rendered prompt block has a sticky-within-block header: left side = title ("Regeneration prompt") + the metadata line "{N} stages selected, {K} follow-ups inlined, autonomous={true|false}, {bytes} KB"; right side = the Copy button (primary affordance). Do NOT put the Copy button inside a `<details>` / expander.
2. **Body styling.** Dark code theme by default; configurable line-height; soft-wrap toggle in the header (icon button) since prompts contain long lines (paths, headers) that benefit from both wrapped and unwrapped views at different times.
3. **Copy feedback.** Icon swap (clipboard → check) for ~2000 ms, with the button's `aria-label` flipping from "Copy prompt to clipboard" to "Copied". Tooltip text mirrors the label. No toast required for v1.
4. **Size surfacing.**
   - Always show byte count in the header metadata line, formatted as KB (one decimal) below 1 MB and MB (two decimals) above.
   - At ≥50 KB: render a muted warning banner above the prompt body ("This prompt is large ({size}); some terminals may paste slowly. Consider Download .md.") This is the soft-warn tier. Copy stays enabled.
   - At >1 MB: server returns 413 and the UI does NOT render the prompt body — instead it renders an error block with the size, the cap, and remediation guidance ("Reduce stage selection or split into multiple regenerations"). Copy button is hidden in this state, not disabled-with-tooltip — a hidden button can't be misclicked.
5. **No silent truncation, ever.** If the assembled text would exceed 1 MB, fail loudly with the 413 path above. Do not render a "first 50 KB" preview that copies to clipboard with the rest dropped.
6. **Optional Download .md (v2-eligible).** A secondary button next to Copy that triggers a `Blob` download of the assembled text. Useful as a fallback for heterogeneous paste targets (some terminals, RDP, browser sandboxes). Spec it as v2 unless interview answers show users hitting OS-paste failures often.
7. **Accessibility checklist.** Visible focus ring on Copy; `aria-label` reflects copy/copied state; Copied state announced via tooltip text update or `aria-live="polite"` region; warning banner uses semantic `role="status"` (or `role="alert"` for the 1 MB hard error).
8. **Floating Copy is a v2 nice-to-have.** If user logs show they scroll past the header on long prompts, add a sticky floating Copy that appears only when the header scrolls out of view. Not blocking for v1.

## 4. Open questions surfaced

- **Should v1 include the Download .md fallback, or defer to v2?** The user's revised prompt mentions only Copy; established practice is split.
- **What size banding for KB display?** Show as KB up to 1024, then MB? Or always KB? The spec needs a consistent formatter.
- **Floating-copy for long prompts: in or out for v1?** Probably out, but should be surfaced as an explicit non-goal so it isn't silently dropped.
- **Soft-wrap default state.** Wrap on or off by default? Long path-style lines argue for wrap-on; readability of structured headers (`# EXECUTION MODE: …`) argues for wrap-off.
- **Should the Copied state be persistent (button text stays "Copied") or auto-revert?** 2 s auto-revert is mainstream; persistent only resets on next interaction. The spec should pick one.
- **Are there OS-clipboard size limits we need to defensively warn about?** Empirically the Async Clipboard API has no hard text-size cap, but specific browsers and paste targets do. Worth documenting the known-bad combinations as caveats in the warning banner copy.

## Sources

- [PatternFly — Clipboard copy design guidelines](https://www.patternfly.org/components/clipboard-copy/design-guidelines/)
- [Cloudscape Design System — Copy to clipboard](https://cloudscape.design/components/copy-to-clipboard/)
- [whitep4nth3r — How to build a copy code snippet button and why it matters](https://whitep4nth3r.com/blog/how-to-build-a-copy-code-snippet-button/)
- [DEV Community — How to build a copy code snippet button](https://dev.to/whitep4nth3r/how-to-build-a-copy-code-snippet-button-and-why-it-matters-3en8)
- [amanhimself.dev — Advanced code blocks with Shiki and Astro](https://amanhimself.dev/blog/advanced-code-blocks-with-shiki-and-astro/)
- [open-webui issue #5767 — Floating copy button like the ChatGPT website](https://github.com/open-webui/open-webui/issues/5767)
- [Modern UI — Copy Button component](https://modern-ui.org/docs/components/copy-button)
- [Shoelace — Copy Button](https://shoelace.style/components/copy-button)
- [shadcn — Copy Button](https://www.shadcn.io/button/copy)
- [alacritty/alacritty#6848 — Truncated text on copy to clipboard](https://github.com/alacritty/alacritty/issues/6848)
- [microsoft/monaco-editor#1540 — Text truncated on copy with ellipsis](https://github.com/microsoft/monaco-editor/issues/1540)
- [kovidgoyal/kitty#3937 — Clipboard size limit](https://github.com/kovidgoyal/kitty/issues/3937)
- [microsoft/vscode#5498 — Crash when copying large amounts of data](https://github.com/microsoft/vscode/issues/5498)
- [zenorocha/clipboard.js#407 — Firefox fails to copy bigger amount of data](https://github.com/zenorocha/clipboard.js/issues/407)
- [The Old New Thing — Windows clipboard size limits](https://devblogs.microsoft.com/oldnewthing/20220608-00/?p=106727)
- [Next.js — Large Page Data](https://nextjs.org/docs/messages/large-page-data)
- [checksafe.zone — HTML5 Banner Validator (150 KB IAB ceiling)](https://checksafe.zone/validator)
- [NetApp — Differences among hard, soft, and threshold quotas](https://docs.netapp.com/us-en/ontap/volumes/differences-hard-soft-threshold-quotas-concept.html)
- [elastic/kibana#179731 — Copy rows as text UX/UI enhancements](https://github.com/elastic/kibana/issues/179731)
- [Postman Docs — Generate code snippets from API requests](https://learning.postman.com/docs/sending-requests/create-requests/generate-code-snippets)
