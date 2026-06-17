---
worker_id: level-specialist-06-accessibility
stage: 5
role: level-specialist
level: accessibility
status: complete
blockers: []
confidence: high
---

# Accessibility validation — bgm_library UI

Level = accessibility. Target: the new BGM library view (`BgmGrid` + audio preview + 分类 filter + generate form + assignments panel) in `projects/ai_video_management/apps/ui/`, mirroring `ActorGrid` / `VoiceGrid`.

Severity policy (per `agent_refs/validation/general.md`): an **ARIA / a11y mandatory check fail = `blocker`** (standard 3-round cap, never auto-halt without that policy). An a11y **"Recommended" gap = `warning`** (logged, never halts). Visual-only properties (contrast, focus-ring visibility, motion) are not asserted programmatically here — they are surfaced as `validation.requires_manual_walkthrough` per general.md §4 and development.md §7.

Baseline carried from existing grids (the contract the new view must match, not re-invent):
- `VoiceGrid` already labels its play button `aria-label={播放 ${v.id} 配音样本}` and exposes a polite live region via `App.tsx`'s `#aria-live-toast` (`lib/announce.ts`, `announceToast`). The BGM view MUST reuse `announceToast` rather than invent a second live channel.
- `ActorGrid` wraps each filter `<select>` in a `<label>` and groups them with `role="group" aria-label="过滤演员"`. BGM filter MUST follow the same labeled-control pattern.
- Toasts use `role="status"`; error banners use `role="alert"`.

---

## A. Mandatory checks (fail → `blocker`)

### A11Y-AUDIO — Audio preview is keyboard-operable and per-track labeled
- **A11Y-AUDIO-1** — Each track's play/pause control is a real `<button type="button">` (or native `<audio controls>`), reachable in tab order and operable with Enter/Space. A `<div onClick>` with no `tabIndex`/`role`/key handler is a fail. (Spec §5 says 试听 mirrors `VoiceGrid`'s `<audio>`/play-button pattern — that pattern is a real `<button>`, so this is the baseline to hold.)
- **A11Y-AUDIO-2** — Every preview control has an accessible name that names the **specific track**, not a generic "播放". It MUST include the bgm id and SHOULD include the category — e.g. `aria-label="播放 bgm_0001（tension 紧张对峙）试听"`. A bare "▶" glyph button with no `aria-label`/`title` is a fail (the glyph is not an accessible name).
- **A11Y-AUDIO-3** — Play↔pause state change is conveyed non-visually: the control's accessible name (or `aria-pressed`) flips with state, so a screen-reader user knows the track is now playing/paused — not only the ▶/⏸ glyph swap (glyph-only = visual change a SR can't observe).
- **A11Y-AUDIO-4** — If `<audio controls>` is rendered inline (instead of a single shared `Audio()` object as in `VoiceGrid`), the element carries an accessible name tying it to its card (`aria-label` with bgm id), since native `<audio>` exposes no inherent name.

### A11Y-FILTER — Category filter is a labeled, keyboard-navigable control
- **A11Y-FILTER-1** — The 12-category filter is a native `<select>` (or an ARIA-correct listbox/radiogroup) with an associated `<label>` (wrapping `<label>` as in `ActorGrid`, or `htmlFor`/`id`). An unlabeled `<select>` is a fail.
- **A11Y-FILTER-2** — Each of the 12 category `<option>`s carries a **text** label (the Chinese gloss from spec §3: 紧张对峙 / 打斗 / 高燃爽点 / 打脸爽感 / 悲情 / 温情 / 虐恋 / 悬疑 / 日常 / 回忆 / 片头主题 / 系统提示音), so categories are distinguishable by text — **not by color or icon alone** (WCAG 1.4.1 Use of Color). A color-swatch-only category chip with no text is a fail.
- **A11Y-FILTER-3** — Selected category is announced: a native `<select>` satisfies this for free (the chosen `<option>` text is the value). If a custom chip/toggle filter is used instead, the active one MUST set `aria-pressed`/`aria-current`/`aria-selected` so the selected state is programmatic, not color-only.
- **A11Y-FILTER-4** — Result-count change after filtering is announced (mirror `ActorGrid`'s `🎭 演员池 ({filtered} / {total})` heading + the polite page indicator). If filtering empties the grid, the empty-state text is reachable and not purely visual.

### A11Y-GRID — Cards reachable in logical order with accessible names
- **A11Y-GRID-1** — Cards appear in DOM/tab order matching visual order (no positive `tabIndex` reordering). Each interactive card is a `<button>`/link in natural source order, as in `ActorGrid`/`VoiceGrid`.
- **A11Y-GRID-2** — Each card has an accessible name covering **bgm id + category + mood** (spec §10.4 / §3 metadata: `category` / `mood`). A card whose only label is the id, or which relies on adjacent visual chips a SR won't associate, is a fail. Acceptable: `aria-label="bgm_0001 · tension 紧张对峙 · {mood}"` on the card button.
- **A11Y-GRID-3** — Per-card secondary controls (play, 🗑 软删除, any select-mode toggle) each have their own distinct accessible name including the bgm id (mirror `VoiceGrid`'s `软删除 ${v.id}` / `播放 ${v.id}`), so they are not all announced identically.
- **A11Y-GRID-4** — Grid container uses a coherent list/region semantic (`role="list"` + `role="listitem"` as `ActorGrid` does, or `<ul>/<li>`), so a SR can announce item count and navigate item-by-item. (If `ActorGrid`'s `role="list"`-on-div + `role="listitem"`-on-button pattern is reused verbatim, this passes; a flat `<div>` soup of buttons with no grouping is the fail.)

### A11Y-FORM — Generate form inputs labeled; states announced
- **A11Y-FORM-1** — Every generate-form input — **category select, duration, bpm, intensity, instruments** (spec §5) — has a programmatically-associated `<label>` (wrapping `<label>` per the `voice-gen-field` pattern, or `htmlFor`/`id`). Any input identified only by adjacent placeholder text or a visual caption is a fail.
- **A11Y-FORM-2** — The generate button has a non-empty accessible name (e.g. "生成 BGM"); an icon-only generate button needs `aria-label`.
- **A11Y-FORM-3** — In-progress state is announced via a live region. Reuse `announceToast` (the existing `#aria-live-toast` polite region) OR render the busy text inside an `aria-live="polite"` node and/or set `aria-busy="true"` on the form/button. A spinner that changes only pixels is a fail for this check.
- **A11Y-FORM-4** — Error state (generate failure → `StableAudioFailedError` / `StableAudioMissingError` mapped per spec §4) is announced assertively: surfaced through `role="alert"` (as `VoiceGrid`/`ActorGrid` error banners do) or an `aria-live="assertive"` region, carrying the failure kind as text. A silently-failing generate (toast that never reaches a live region) is a fail.
- **A11Y-FORM-5** — If the form lives in a modal (mirroring the assign modals), the modal sets `role="dialog"` + `aria-modal="true"` + an `aria-label`, and focus moves into it on open (the existing modals do `autoFocus` on a control / close button). Missing dialog semantics on a focus-trapping overlay is a fail.

### A11Y-ASSIGN — Assignments panel conveys "which dramas" textually
- **A11Y-ASSIGN-1** — The assignments reverse-lookup ("哪些剧引用了此 BGM", spec §5) is rendered as reachable **text** (list of drama names / episode paths), not as icons or counts alone. A SR user must be able to read *which* dramas reference the bgm. An empty result states "无引用"/"未被任何剧引用" as text, not a blank.
- **A11Y-ASSIGN-2** — The assignments list uses list semantics (`<ul>/<li>` or `role="list"`) so each referencing drama is an addressable item, and the panel has an accessible name/heading tying it to the bgm id.
- **A11Y-ASSIGN-3** — If the panel is reachable via a control (button/tab/disclosure), that control is keyboard-operable and labeled (e.g. `aria-label="查看 bgm_0001 的引用"`); a `<details>`/`<summary>` is acceptable and natively operable.

---

## B. Recommended checks (gap → `warning`)

- **A11Y-REC-1** — Add a count to the filter group's accessible context so the filtered/total ratio is in an `aria-live="polite"` node (not only the visual heading), matching the page-indicator pattern already in both grids.
- **A11Y-REC-2** — Give the audio preview a SR-discoverable position/length cue (e.g. expose `duration` from metadata in the label: "试听 8s"), so SR users get the same length signal sighted users get from the waveform/glyph.
- **A11Y-REC-3** — On the category filter, pair any color coding with both text **and** a non-color secondary cue (icon + text) so the 12 categories remain distinguishable for color-vision-deficient users beyond the bare WCAG 1.4.1 minimum.
- **A11Y-REC-4** — Generate form: associate help/units text (bpm range, intensity 1–5, duration seconds) with its input via `aria-describedby`, so constraints are announced, not just shown.
- **A11Y-REC-5** — Provide a "stop all" / single-active-track guarantee announced to SRs (VoiceGrid pauses the prior `Audio()` when a new one plays); announce the auto-stop so a SR user isn't surprised by silence.
- **A11Y-REC-6** — Empty-state and loading-state copy ("加载中…", "BGM 库为空") live in a polite live region so the transition out of loading is announced, mirroring the existing empty/loading blocks.

---

## C. Visual-only checks → `validation.requires_manual_walkthrough`

These cannot be asserted from the DOM/markup and MUST be surfaced to the user as a manual walkthrough (general.md §4, development.md §7). The runtime validator emits `validation.requires_manual_walkthrough` for the BGM view after the A/B checks pass:

- **MW-1 — Color contrast.** Category chips/labels, filter selected-state, card text, play/generate buttons, toasts and the error `role="alert"` banner all meet WCAG AA contrast (4.5:1 text, 3:1 UI/large) against the **light-theme app chrome** (`agent_refs/project/general.md` light-theme convention). The 12 category colors (if any) must each pass against the card background.
- **MW-2 — Focus visibility.** A visible focus indicator is present and sufficient on: each card button, the play/pause control, the 🗑 button, every filter `<select>`, every generate-form input + the generate button, the assignments disclosure, and the modal close button — under real keyboard input, against the light theme.
- **MW-3 — Motion.** Any play-state animation, spinner, or tile hover/selected transition is non-vestibular and respects `prefers-reduced-motion` (or is subtle enough to be safe).
- **MW-4 — Focus management on modal open/close.** Confirm (by real keyboard pass) focus enters the generate/assign modal on open, is trapped while open, and returns to the trigger on close — markup (`aria-modal`) is checked in A11Y-FORM-5, but the actual focus trip is observe-only.
- **MW-5 — Perceived latency of generate.** The Stable-Audio subprocess generate can be slow; confirm the in-progress affordance (A11Y-FORM-3) is perceivable in practice and the UI is not mistaken for frozen.

---

## Notes / ambiguities (no fabrication)

- The spec (§5) defers UI specifics to "mirror ActorGrid/VoiceGrid" and does not enumerate exact DOM. Checks above are written against the **established baseline of those two components** (read at validation time) so they assert the contract the new view must match, not an invented one.
- Whether the audio preview uses a single shared `Audio()` (VoiceGrid style) or inline `<audio controls>` (spec §5 phrasing "`<audio>` 试听") is left open by the spec — A11Y-AUDIO covers **both** shapes (A11Y-AUDIO-1/-4) so the check holds regardless of the implementer's choice. *(judgment call — spec is genuinely ambiguous here; covering both avoids a false fail.)*
- `mood` is a metadata field (§3) but its presence in the card's visible chips is not mandated by §5; A11Y-GRID-2 requires it in the **accessible name** specifically because the spec's acceptance anchor §10.4 lists "id + category + mood" as the card's identifying triple. If the implementer omits mood from the card UI entirely, A11Y-GRID-2 should be read against whatever identifying fields the card actually shows, with mood as a `warning` (A11Y-REC) rather than blocker — flagged for parent synthesis.
- Assignments "which dramas" (A11Y-ASSIGN-1) depends on the reverse-lookup query (spec §4 item 2) returning drama identifiers; the a11y check only asserts they are rendered as reachable text, not the correctness of the lookup itself (that's a functional level).
