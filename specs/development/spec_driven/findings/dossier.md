# Findings dossier — spec_driven

Run: spec_driven-20260503-030434 (autonomous full-pipeline clean regen)

## Angles researched

1. **prior-art-spec-driven-tools** — How established tools (Spec Kit, AGENTS.md, Aider, Continue.dev, Cursor rules, JetBrains Junie, Codex) structure the spec-to-execution loop and what affordances they expose for users to inspect/edit/regenerate intent. Which patterns to copy, which to avoid.
2. **markdown-editor-ux** — UX conventions mature web markdown editors (GitHub web editor, Obsidian, MkDocs Material, GitBook, Notion, VS Code Web, Logseq) have converged on for explicit edit toggles, dirty-state, save semantics, error surfacing, per-block vs. whole-file editing. What reduces mistake-cost for non-developers.
3. **copypaste-prompt-ux** — Where mature dev tools place Copy buttons (Stripe, Vercel, GitHub, Postman, OpenAI Playground, Cursor, Continue.dev, PatternFly, shadcn), how they surface size of large copy targets, when they truncate vs. warn vs. block, how they signal "Copied!" state, when they offer Download as file vs. clipboard only.
4. **localhost-fs-sandbox-risks** — Vulnerability classes that have surfaced in localhost file viewers/editors (Vite, MkDocs, Hugo, Jekyll, Next.js dev, JupyterLab, code-server). Windows-specific (NTFS case-insensitivity, 8.3 short names, ADS, mount points). OWASP best practice for path-sandboxing, multipart, content-sniffing.

## Cross-cutting insights

- **"Regenerate, don't surgically edit" is now industry consensus** — and combined with explicit pinned-content survival, it's the only stable answer to spec drift. *(prior-art-spec-driven-tools + copypaste-prompt-ux)*. Spec Kit, Junie, and the Augment / InfoQ writeups all converge on regenerate-from-inputs; spec_driven's read-zero contract plus `<stage>/promoted.md` is the most disciplined version surveyed. The webapp's regen-prompt UX is the operational handle for that contract.
- **Header-bar Copy + dark-themed wrapped body + 2-second icon-swap "Copied!" is now the one-click default; hiding the prompt behind a `<details>` is an anti-pattern** *(copypaste-prompt-ux + markdown-editor-ux)*. PatternFly, shadcn, ChatGPT-style chat UIs, Shoelace, and modern code-block patterns all converge on visible header (left = metadata, right = Copy primary action) over hide-by-default disclosure. Follow-up 002's switch from inner `<details>` to inline `regen-prompt-block` lands directly on this convention.
- **Soft-warn / hard-block / never-truncate is the mature size policy** *(copypaste-prompt-ux + localhost-fs-sandbox-risks)*. Next.js's 128 KB page-data warning, IAB's 150 KB banner ceiling, and OS quota separation all advocate the soft/hard split. Vite, kitty, VS Code, and Monaco bug histories show silent truncation of clipboards is treated as a defect. The 50 KB warn / 1 MB 413 hard-cap matches industry posture. On 413, refusing to render the prompt block at all is correct (no surface to half-paste).
- **View-by-default + explicit ✎ + Ctrl+S Save + dirty-dot is the dominant *review surface* convention** *(markdown-editor-ux + prior-art-spec-driven-tools)*. Obsidian (View↔Edit toggle), GitHub web editor, VS Code (issue #303697 open), and Notion's review-only-mode all converge here. For artifacts that are *primarily reviewed and occasionally revised* — exactly spec_driven's posture — view-by-default reduces accidental edits more than always-editable WYSIWYG. Save errors must be persistent inline banners with edits preserved, never toasts (NN/g, Carbon, Primer, Smashing).
- **Localhost is not a security boundary; OWASP-grade safe_resolve is mandatory** *(localhost-fs-sandbox-risks + prior-art-spec-driven-tools)*. Vite shipped four 2025 path-traversal CVEs (incl. Windows-specific `\` deny-list bypass CVE-2025-62522); MkDocs, Jekyll, JupyterLab, code-server have all leaked arbitrary local files. DNS rebinding makes "bound to 127.0.0.1" a non-boundary — Origin/Host validation + canonicalize-then-contain on every state-changing route is the new floor. Windows extras: reject reserved device names (CON/PRN/...), Alternate Data Streams (`::$DATA`), 8.3 short names, junctions (not just symlinks).
- **Per-block inline edit on `interview/qa.md` is supported by the field-specific inline-edit pattern** *(markdown-editor-ux + prior-art-spec-driven-tools)*. PatternFly's ✎ → check/X is the design-system encoding; PublicLab's inline-markdown-editor is a worked example. Whole-file ✎ should remain in the toolbar but be **mutually exclusive with per-Q editors at runtime** — Primer warns against mixing save scopes on one surface. Disk-side, every save still rewrites the whole file atomically (the structured view is a projection).

## Per-angle highlights

### prior-art-spec-driven-tools

- The dominant prior-art shape is `intent → plan → tasks → implement` with explicit human review gates between stages (Spec Kit's `/constitution`-`/specify`-`/plan`-`/tasks`-`/implement`; Junie's `requirements.md` → `plan.md` → `tasks.md`). spec_driven's six-stage layout is a strict superset, with the interview and research stages as genuine extensions.
- Plain-markdown spec/rule files in the repo with directory-tree precedence is the universal pattern (AGENTS.md is now Linux-Foundation-stewarded; adopted by Codex, Cursor, Aider, Jules, Continue.dev, Zed, Junie). None of the surveyed tools ship a dedicated GUI for editing intermediate spec artifacts — they all rely on the user opening the file in their IDE.
- The drift problem is universally acknowledged; consensus answer is "regenerate, don't surgically edit". spec_driven's read-zero-from-prior-outputs contract plus `<stage>/promoted.md` pinned-items sidecar is the most disciplined version found. Anti-patterns called out: heavy up-front spec / big-bang release (ThoughtWorks Tech Radar), unbounded execution sweeps (Junie's "do tasks 1–2 only"), reinventing waterfall (Scott Logic empirical writeup).

### markdown-editor-ux

- View-by-default + explicit ✎ + Ctrl+S Save + dirty-dot next to filename is the convention across Obsidian, GitHub web editor, VS Code (issue #303697 explicitly proposes this for `.md`).
- Save errors must be a persistent inline banner with the user's edits preserved in the textarea; toasts are explicitly discouraged for errors (NN/g, Carbon, Primer, Smashing). Primer adds two non-obvious rules: never disable the Save button (Tab-focus accessibility), always preserve user input on failure.
- Per-Q / per-A inline edit on `interview/qa.md` is supported by PatternFly *field-specific* inline-edit pattern (✎ → check/X) and the publiclab inline-markdown-editor worked example. Whole-file ✎ should remain in the toolbar but be **mutually exclusive** with the per-Q editors at runtime. Disk-side, every save still rewrites the whole file atomically.

### copypaste-prompt-ux

- Header-bar Copy on the right is the established convention. PatternFly's clipboard-copy component, modern code-block patterns (whitep4nth3r, Shiki/Astro), and ChatGPT-style floating-copy refinements all converge on a visible header with metadata on the left and Copy on the right; hiding the action behind a `<details>` is treated as an anti-pattern for a primary affordance.
- Warn-soft / block-hard / never-truncate matches industry practice. The webapp's "muted banner ≥50 KB, 413 hard at >1 MB, do not render the prompt block on 413" mirrors Next.js's 128 KB page-data warning, IAB's 150 KB banner ceiling, and OS-level soft/hard quota separation. Multiple tracker bugs (Alacritty, Monaco, kitty, VS Code) document silent truncation of clipboard text as a defect.
- 2-second icon swap is the de facto "Copied!" UX, with Download .md as a v2 safety net. Modern UI / Shoelace / shadcn copy-button libraries all use a ~2 s clipboard→check icon swap with `aria-label` flip; offering Download .md alongside Copy is a reasonable v2 fallback for heterogeneous OS paste targets (terminals, RDP, sandboxed browsers) where mega-byte clipboards are unreliable.

### localhost-fs-sandbox-risks

- Localhost-only file servers are a recurring CVE class — Vite alone shipped four 2025 path-traversal CVEs (including the Windows-specific `\` deny-list bypass CVE-2025-62522); MkDocs, Jekyll, jupyterlab-lsp, nbconvert, and several VS Code extensions have all leaked arbitrary local files. DNS rebinding makes "bound to 127.0.0.1" a non-boundary, so OWASP-recommended Origin/Host validation plus optional auth must be layered on every state-changing route.
- Windows-aware `safe_resolve` must canonicalize FIRST then assert containment: normalize both `/` and `\`, case-fold for NTFS, reject reserved device names (CON/PRN/AUX/NUL/COM*/LPT*, including with extensions), Alternate Data Streams (`::$DATA`, `:stream`), 8.3 short names, and reparse points (junctions, not just symlinks). Prefer a single 404 over 403/404 to remove the enumeration side-channel.
- Upload pipeline should follow the OWASP File Upload Cheat Sheet: validate magic bytes (extension and `Content-Type` are spoofable), set `X-Content-Type-Options: nosniff` and `Content-Disposition: attachment` on every `GET /api/file`, treat SVG as a code-execution vector (sanitize on write or drop from the allowlist), enforce body-size caps at both reverse-proxy and in-app layers.

## Recommendations for the spec

1. **Keep the read-zero contract + promoted.md pinning explicit in the spec.** Both are spec_driven's main differentiators vs. AGENTS.md / Spec Kit / Junie. *(prior-art)*
2. **FR-42 must encode header-bar Copy + Wrap toggle + dark code body + ≥50 KB muted banner + 413→no-block.** Follow-up 002 already lands here; the spec must not regress to inner-`<details>`. *(copypaste-prompt-ux)*
3. **Editor FR must specify view-by-default + ✎ toggle + Ctrl+S Save + dirty-dot + persistent inline error banner; never disable Save during error; preserve textarea content on save failure.** *(markdown-editor-ux)*
4. **Q/A view FR must specify per-Q and per-A pencil with mutually-exclusive whole-file edit toggle + atomic full-file rewrite on save.** *(markdown-editor-ux)*
5. **Path-sandboxing NFR must enforce: canonicalize-first-then-contain; reject Windows reserved device names; reject ADS; reject 8.3 short names; reject junctions (not just symlinks); single 404 (not split 403/404) to remove enumeration side-channel; Origin/Host validation on `PUT /api/file` and `POST /api/regen-prompt`.** *(localhost-fs-sandbox-risks)*
6. **Response-headers NFR: `X-Content-Type-Options: nosniff` and `Content-Disposition: attachment` on every `GET /api/file`.** *(localhost-fs-sandbox-risks)*
7. **Treat SVG as code-exec vector — either drop from the allowlist or sanitize on write.** *(localhost-fs-sandbox-risks)*
8. **Add explicit `# EXECUTION MODE:` header pairing in CLAUDE.md and FR-14c — exactly the AGENTS.md "literal directive in the file" idiom.** Already present; spec must keep it. *(prior-art)*
9. **Validation strategy must require an e2e scenario per render mode (Markdown / QaView / JsonlView / CodeView / ImagePlaceholder) opening a real file that triggers each mode.** Latent-render-error class is `critical` per `agent_refs/validation/development.md` move #8. *(markdown-editor-ux + prior-art lessons)*
10. **Validation strategy must require an API consumer-walk test per recursive endpoint** (frontend reads `node.children` etc. — backend must emit the same field names, walked the same way). *(prior-art lessons + agent_refs move #2)*

## Open questions surviving research

- **Download .md fallback for >1 MB regen prompts** — should we add a `Download` button beside Copy so the user can save the prompt to disk and paste from there? Defer to v2; recommended by the copypaste-prompt-ux angle but not load-bearing for the current scope. (`OQ-download-md-v2`)
- **DNS rebinding mitigation for localhost** — the spec already binds 127.0.0.1 (not 0.0.0.0) and forbids public exposure, but Origin/Host validation on POST/PUT is best-practice belt-and-suspenders. Should the spec mandate it now, or wait until a multi-user variant exists? (`OQ-origin-validation`)
- **SVG handling** — drop from extensions allowlist (simpler), or sanitize on write via a library? The findings angle recommends "drop or sanitize"; spec author should decide before stage 4 closes. (`OQ-svg-policy`)
- **Per-Q vs whole-file lock semantics on `qa.md`** — when one Q is being edited, should the whole-file ✎ toggle be disabled, or just hidden? Primer says "mutually exclusive" but is silent on the precise affordance. Recommend disabled (visible but inert) for discoverability. (`OQ-qa-edit-lock-shape`)
- **Floating Copy for very-tall prompt blocks** — at >520 px, ChatGPT-style floating Copy might help. Not in scope for v1; revisit if the prompt size class shifts up. (`OQ-floating-copy-v2`)
