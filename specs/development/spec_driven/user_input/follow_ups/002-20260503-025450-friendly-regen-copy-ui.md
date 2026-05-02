# Follow-up draft 002 — 2026-05-03

Summary: Make the assembled regeneration prompt friendly to read and easy to copy. Once "Build prompt" succeeds, the prompt is shown immediately (no inner `<details>` to expand) inside a bordered block with a header bar that carries the title, a soft-wrap toggle, and a prominent **Copy** button right next to the prompt body.

## New / changed requirements

### 1. The assembled prompt is visible by default after build

- The current behavior wraps the prompt in an inner `<details>` element labelled "View assembled prompt", so the user has to click twice (Build prompt → expand details) before they can see or copy the text. Drop the inner `<details>`.
- Once `POST /api/regen-prompt` succeeds, render the prompt inline directly inside the (still-collapsible) outer Regenerate panel.
- The outer panel itself remains a default-collapsed `<details>` titled "Regenerate" (FR-42 unchanged on that point); only the **inner** prompt-viewer collapse goes away.

### 2. Header bar above the prompt body with prominent Copy button

- Render the assembled prompt inside a bordered block (`regen-prompt-block`) consisting of a header bar followed by the `<pre>` body.
- Header bar contents (left → right):
  - "Assembled prompt" title.
  - A "Wrap" checkbox toggle (soft-wrap on/off; default on).
  - A prominent green primary-style **Copy** button. Label flips to "Copied!" for ~1.5s on click; `aria-live="polite"` for screen readers. Fixed minimum width so the label flip does not shift layout.
- The Copy button moves out of the actions row beside the "Build prompt" button. The actions row keeps "Build prompt" + the section-breakdown summary line (FR-42d), but no longer carries a duplicate Copy button.

### 3. Soft-wrap toggle for the prompt body

- The prompt `<pre>` defaults to soft-wrap on (`white-space: pre-wrap; word-break: break-word`) so long lines remain readable in narrow panes without horizontal scroll.
- Toggling the header-bar "Wrap" checkbox off restores the original `pre` behavior with horizontal scroll for code-style review.
- The toggle is a per-render UI preference; it is NOT persisted to `localStorage`.

### 4. Readability tweaks on the prompt body

- Bump font-size from 12px → 13px and line-height to 1.55 for the `<pre>` body.
- Bump max-height from 480px → 520px.
- Keep the existing dark code-style background.

### 5. Behavior preserved

- The summary line (`{N} stages selected, {K} follow-ups inlined, autonomous={…}, {bytes} KB`) per FR-42d still renders, in the actions row beside the "Build prompt" button.
- The size-warning banner per FR-42e still renders above the prompt block when the API returns a non-null `warning`.
- The 50 KB warn / 1 MB hard-ceiling size policy per FR-14c is unchanged. On 413 the prompt block is not rendered at all (a build-error banner shows instead).
- The same Copy → "Copied!" label-flip semantics are preserved; the button now lives inside the header bar.
- The autonomous-mode toggle, module checkboxes, and stage selection live unchanged inside the outer Regenerate `<details>`.

## Out of scope for this follow-up

- No syntax highlighting of the assembled prompt text (it's already a markdown-ish render; copying verbatim is what matters).
- No client-side persistence of the wrap toggle.
- No "Download as file" affordance — Copy still goes through the clipboard.
- No change to `POST /api/regen-prompt` request/response shape or to `regen_prompt.py` server-side prompt assembly.
