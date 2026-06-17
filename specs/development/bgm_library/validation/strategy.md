# Validation strategy — bgm_library

Run: bgm_library-20260616-123238
target: `projects/ai_video_management/` + `tools/stableaudio_gen.py` + `tools/mux_av.py`

## Levels chosen
- **acceptance_criteria** — always; Gherkin per primary flow (generate, id-alloc, filter, preview, assignments, mux, license, soft-delete).
- **bdd_scenarios** — always; UI feature behaviors (grid, filter, generate form, progress/failure, assignments, cue, mux).
- **unit_tests** — discrete logic: id regex, `BgmAttrs` enums, cross-category id allocation, md build↔parse, cue parse, assignments scan, mux filtergraph assembly, `--dry-run`.
- **system_tests** — boot smoke, full generate integration (prod-mode `serve_static=True`), Playwright e2e per runtime mode, consumer-walk field mirroring, assignments integration, mux e2e.
- **security** — subprocess arg injection + path traversal via the user-controlled `{category}/` layer + `.mp3` serving sandbox; this module's two deltas vs actor (generation subprocess + category path segment) ARE the new attack surface.
- **accessibility** — UI-heavy (grid + `<audio>` + filter + generate form + assignments panel).

**Not chosen:** dedicated `performance.md` — generation is offline, spec states no hard latency budget. Folded into observe-only notes (generation wall-clock; GPU-time DoS via unbounded `duration` is tracked as a security finding instead).

## Per-level summary

### Acceptance criteria
- Generate → subprocess writes `bgm_NNNN.mp3` + `.md` 12-field table; failure reaps the mp3-less folder (judgment-call, confirm).
- **Global cross-category id allocation** = max-of-ALL-categories + 1 via `mkdir(exist_ok=False)` — the one structural divergence from the flat actor library.
- assignments reverse-lookup from `bgm.md`; mux v1 asserts `-c:v copy` + `amix=normalize=0` + sidechain duck; license = Stability AI Community License; soft-delete to `_deleted/_bgm/`.

### BDD scenarios
- 13 features: grid render, 12-category filter, audio preview, generate form (prompt-preview round-trip → progress → typed-error `StableAudioMissingError`/`StableAudioFailedError`, no orphan folder), empty vs error states, assignments panel, tri-consumer cue, mux v1 missing-input matrix.

### Unit tests
- `validate_bgm_id` `^bgm_\d{4,}$`; `BgmAttrs` 12-category enum + intensity 1-5 int bounds + loopable; cross-category id alloc atomicity; md round-trip (all 12 fields); cue-line parse (well/malformed/missing-optional); assignments token scan skipping `_`-dirs; mux filtergraph order `[bgm][dialogue]` + `normalize=0` + `-c:v copy`; `stableaudio_gen.py --dry-run` prints params without importing torch.
- Dev.md moves applied: POSIX-only skip markers, parser tested against real on-disk `bgm.md`, pip-not-uv.

### System / integration tests
- Boot smoke (critical); generate+delete integration with **`serve_static=True` prod-mode** test (catches 405 static-mount shadowing); Playwright e2e — **profile count = 2 advertised runtime modes** (prod 8766 + dev 5174); consumer-walk field-name mirroring front↔back; fixture-`bgm.md` assignments resolution; mux e2e on tiny `imageio_ffmpeg` clip asserting video stream unchanged. torch/ffmpeg/POSIX paths skippable.

### Security
- SEC-01..09 **critical/halt**: arg-list subprocess (never `shell=True`) + bounded numerics; six traversal/sandbox gates over the user-controlled `category` dir, the `bgm_NNNN` id, `.mp3` serving (reuse `MediaQuery.serve`/`SafeResolver`), id-alloc containment, subprocess `--out`, soft-delete target. SEC-09 conditional on `mux_av.py` web-reachability (expected NOT reachable in v1 — confirm). SEC-10 **warning**: Stability license $1M revenue ceiling.
- **Closed category enum** is a security control, not just data integrity — only the 12 known categories accepted.

### Accessibility
- 5 mandatory **blocker** groups: audio player (keyboard + per-track id/category label + non-visual play state), category filter (labeled, text-distinguishable not color-only), grid (tab order + id+category+mood accessible name), generate form (every input labeled + `aria-live` progress/error via existing `announceToast`), assignments panel (textual). 6 recommended **warning** gaps. 5 visual-only checks → `validation.requires_manual_walkthrough`.

## Cross-cutting concerns
- **Generation subprocess is the single architectural delta** from the actor slice; it is also the dominant new security + reliability surface (arg injection, GPU-time DoS via unbounded duration, orphan folder on failure). Reuse actor/media gates (`SafeResolver`, `validate_*_id`, arg-list `subprocess.run`) rather than re-implement.
- **`{category}/` path layer** is user-controllable → both an id-allocation concern (global scan) and a path-traversal concern (closed enum + sandbox).
- **State to reset between tests**: each test allocates into a tmp `_bgm` root; never write real library ids; clean `_deleted/_bgm/` between runs.
- **External-tool flakiness**: torch (GPU) and ffmpeg are environment-dependent — every test touching them is skippable with a clear reason, never silently passing. `--dry-run` is the CI path for generation.
- **Unresolved spec ambiguities surfaced by ≥2 workers** (resolve at stage-6 start, non-blocking): delete verb/route shape; list-response envelope; whether delete guards on existing assignments (actor does); `vol` unit (dB vs 0-1 linear); `system_cue` BGM-vs-SFX; hard `duration` ceiling (security wants one).

## How runtime validation (stage 6) will use this
- `work_unit_kind=backend_api` (bgm slice routes/query/command) → acceptance + system + unit + security.
- `work_unit_kind=frontend_component` (BgmGrid / generate form / assignments panel) → bdd + accessibility + e2e.
- `work_unit_kind=cli_tool` (`stableaudio_gen.py`, `mux_av.py`) → unit + system (mux e2e), security (arg-list/paths).
- `work_unit_kind=boot_smoke` → critical gate, no revision rounds.
- Pass/fail: security failure = critical, halt immediately. Acceptance/BDD-golden/missing-e2e-mode/prod-mode-405 = blocker, 3-round cap. a11y recommended + observe-only = warning. After all automated levels pass on UI units → emit `validation.requires_manual_walkthrough`.

## Promotion-preservation check
- No `<stage>/promoted.md` sidecars exist for this run (interview / findings / final_specs / validation all checked — none present). If a pin is added before a future regen, every pin MUST appear verbatim in the regenerated artifact (`parse_promoted_text`, asserted modulo whitespace); missing pin = `critical`. Stage 6 (project code) excluded from promotion in v1.

## Stage-5 carve-out sign-offs to surface (general.md §6 — confirm intended)
1. **mux v1 = single BGM only** (multi-cue `bgm.md` orchestration out of scope) — spec §1/§7.
2. **No generate-diverse / archetype** (actor has them) — spec §4.
3. **seed best-effort reproduction** (not actor's hard reproduction) — spec §2.
4. **No dedicated performance gate** — offline generation; observe-only.
5. **`mux_av.py` assumed NOT web-reachable** in v1 (SEC-09 conditional) — confirm it stays a CLI-only tool.
6. **`create-prompts` offline-import flow** optional / deferred — spec §4.
