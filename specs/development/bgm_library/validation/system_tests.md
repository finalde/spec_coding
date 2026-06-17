---
worker_id: level-specialist-04-system_tests
stage: 5
role: level-specialist
level: system_tests
status: complete
blockers: []
confidence: high
---

# System / E2E / Integration validation — bgm_library

Run: `bgm_library-20260616-123238` · task_type: development · target: `projects/ai_video_management/`

Scope of this level: boot smoke, full-stack generate/list/delete integration (incl. **prod-mode `serve_static=True`** static-mount-shadowing), Playwright golden path **per advertised runtime mode**, API consumer-walk (front↔back field mirroring), assignments integration via a fixture `bgm.md`, and `tools/mux_av.py` end-to-end with a tiny fixture. ffmpeg-/torch-/POSIX-dependent paths are explicitly marked skippable.

These scenarios are **contract-level** (validation ref general.md §1): they assert on what the next layer / the React UI / the author actually consumes, not on the writer's internals.

---

## 0. Conventions reused from the existing suite (do not re-invent)

- App-under-test built via `tests/conftest.py::make_app(rr, bound, serve_static=...)` + `repo_root()`; drive with `fastapi.testclient.TestClient`. This is the canonical pattern in `test_boot_smoke.py` / `test_api_security_three_shapes.py`. **New BGM integration tests MUST use it** — do not stand up a bespoke app factory.
- State-changing POST/DELETE requests need `Origin`/`Host` headers at the bound origin (`http://127.0.0.1:8766`) to clear the GUARDED_ROUTES gate (see the three-shapes test). Generate + delete are state-changing → they are guarded → tests MUST send these headers, else they 403 (and the test would assert the wrong thing).
- Real-ffmpeg encodes use the `imageio_ffmpeg.get_ffmpeg_exe()` binary on a 1 s 320×240 `testsrc` clip — fast, hermetic, already proven in `test_subtitle_burn.py`. Reuse that fixture shape for mux tests.
- Playwright lives in `apps/ui/e2e/`; `playwright.config.ts` already defines **two** projects: `prod-mode` (8766, single-process FastAPI) and `dev-mode` (5174, Vite proxy). **Mode count = 2 → e2e profile count = 2** (ref dev.md §1 multi-mode parity). The new BGM specs run under BOTH projects automatically.
- Subprocess generation (`tools/stableaudio_gen.py`) MUST be invoked with `--dry-run` in CI integration tests, OR the subprocess call monkeypatched, so torch/GPU is never required in the webapp test process (spec §6, §2 — torch isolated to the script's own `requirements.txt`).

---

## 1. Boot smoke (`tests/test_bgm_boot_smoke.py`) — failure = `critical`, halts immediately (dev.md §4)

Mirrors `test_boot_smoke.py::test_all_post_endpoints_registered`.

**SC-1.1 — app builds with bgm wiring.**
- Setup: `make_app(rr, bound, serve_static=False)`.
- Assert: app builds without raising; `container.bgm_pool` / `bgm_command` / `bgm_query` resolve (proves `container.py` wiring of spec §4 table landed). A boot-time exception from bad DI wiring is `critical`.

**SC-1.2 — every advertised BGM route is registered.**
- Action: enumerate `app.routes` → `{(method, path)}`.
- Assert superset contains every documented BGM endpoint:
  ```
  ("POST",   "/api/bgm/generate")
  ("GET",    "/api/bgm")
  ("POST",   "/api/bgm/delete")        # or DELETE — see Ambiguity A1
  ("GET",    "/api/bgm/assignments")
  ("POST",   "/api/bgm/preview-prompts")   # only if create-prompts/preview retained (spec §4 "省略"/optional)
  ```
  A missing state-changing route otherwise surfaces to the browser as a confusing default 405 (the exact rationale in `test_all_post_endpoints_registered`). Add the BGM rows to that existing test's `expected` set rather than duplicating, if the parent prefers one sweep.

**SC-1.3 — list endpoint returns expected envelope on empty + populated.**
- Action: `GET /api/bgm` against the real repo.
- Assert: `200`; body is the list DTO `to_payload()` shape (top-level list/`{items: [...]}` mirror of `GET /api/actors` — see Ambiguity A2); each item carries the consumer fields enumerated in §4.

**SC-1.4 — eager mkdir of `_bgm/`.**
- Assert: building the app (spec §4: `app_factory.py` eager-mkdir `_bgm/`) leaves `ai_videos/_bgm/` present. Mirrors the actor `_actors/` eager-mkdir. (Run against a `tmp_path` repo root override so we don't litter the real tree — see Ambiguity A4.)

---

## 2. Full generate-flow integration (`tests/test_bgm_generate_flow.py`)

End-to-end through the application layer + subprocess boundary, with the heavy script stubbed.

**SC-2.1 — generate → subprocess → mp3 + md on disk → list surfaces it (happy path, dry-run/stub).**
- Setup: `tmp_path` repo root; `make_app(..., serve_static=False)`; monkeypatch `subprocess.run` used by `bgm__command.generate` so it (a) asserts the argv contains `tools/stableaudio_gen.py`, `--prompt`, `--seed`, `--duration`, `--out`, and (b) writes a tiny valid `.mp3` to the `--out` path (simulating the script's success) and returns rc 0. (A genuinely-invoked `--dry-run` does NOT write an mp3 by design — spec §6 — so the stub is what proves the *webapp-side* on-disk contract; a separate SC-6 covers the real script's `--dry-run` argv.)
- Action: `POST /api/bgm/generate` with body `{category, duration, bpm, intensity, instruments, ...}` + bound-origin headers.
- Assert:
  1. `200`; response cdto echoes the allocated `bgm_NNNN` id (`^bgm_\d{4,}$`).
  2. On disk: `ai_videos/_bgm/{category}/bgm_NNNN/bgm_NNNN.mp3` exists AND `bgm_NNNN.md` exists.
  3. `bgm_NNNN.md` metadata table carries `category / mood / bpm / duration / loopable / intensity / instruments / generator / model / seed / license` and a `## 生成 prompt` block (spec §3). Specifically `generator=stable_audio`, `model=stable-audio-open-1.0`, `license=Stability AI Community License` (spec §2 — **license correctness is acceptance anchor #7; wrong license = `blocker`**).
  4. `GET /api/bgm` now returns the new id (round-trips writer→reader).

**SC-2.2 — id allocation is global across categories (acceptance anchor #2).**
- Setup: pre-create `_bgm/tension/bgm_0001/` and `_bgm/combat/bgm_0002/` fixtures (different categories).
- Action: generate into a THIRD category (`warm`).
- Assert: allocated id == `bgm_0003` (max-across-all-categories +1, NOT per-category reset). This is the **key structural divergence from actor** (spec §3) — a per-category counter would collide; missing this test lets that bug ship. Severity of a real collision = `blocker`.

**SC-2.3 — subprocess failure maps to a domain/HTTP error, not a 500 stack trace.**
- Setup: monkeypatch `subprocess.run` to return rc≠0 (or raise `FileNotFoundError` for the missing-script case).
- Action: `POST /api/bgm/generate`.
- Assert: rc≠0 → `StableAudioFailedError` → translated JSON error (4xx/5xx with structured `detail`, mirroring actor Kling-failure handling); `FileNotFoundError` → `StableAudioMissingError`. The partial `bgm_NNNN/` folder is NOT left orphaned in the list view (no half-written record surfaces). Confirms the spec §4 error mapping landed and `app_factory.py` registered the two new handlers.

**SC-2.4 — delete soft-deletes and refuses when referenced.**
- Setup: generate a bgm (stub) → then write a fixture `bgm.md` referencing it (see §5).
- Action: `POST /api/bgm/delete {bgm_id}` with bound-origin headers.
- Assert: refusal (mirrors `ActorAlreadyAssignedError`) — delete blocked while a drama's `bgm.md` references the id. Then remove the reference, re-delete → folder moved under `_deleted/_bgm/` (soft-delete, spec §3), `GET /api/bgm` no longer lists it. *(If the spec author chose NOT to gate bgm-delete on assignments — see Ambiguity A3 — relax to: delete always soft-deletes; assert the soft-move only.)*

### 2b. Prod-mode static-mount-shadowing (`serve_static=True`) — dev.md §1, missing coverage = `blocker`

The state-changing endpoints (`/api/bgm/generate`, `/api/bgm/delete`) MUST each have a `serve_static=True` integration test. Under prod mode the StaticFiles mount at `/` (`html=True`) shadows any missing/mis-registered route and returns **405** (StaticFiles only allows GET/HEAD) — a `serve_static=False` test silently passes on a 404 and never catches this.

**SC-2.5 — generate under prod mode is reachable (not shadowed).**
- Setup: `make_app(..., serve_static=True)`; stub subprocess as in SC-2.1.
- Action: `POST /api/bgm/generate` + bound-origin headers.
- Assert: status is **not 405**; happy path returns 200 and writes the files. A 405 here means the route is missing/shadowed under the static mount → `blocker`.

**SC-2.6 — delete under prod mode is reachable.**
- Same as SC-2.5 for `POST /api/bgm/delete` → assert not 405.

**SC-2.7 — class-of-failure sweep.**
- Action: iterate the BGM state-changing routes × `serve_static=True`, assert none return 405 (the `GUARDED_ROUTES × serve_static=True` sweep mandated by dev.md §1). Fold the BGM rows into the existing sweep if one exists; otherwise add a `bgm`-scoped sweep test.

---

## 3. Playwright golden path — per runtime mode (`apps/ui/e2e/bgm_library.spec.ts`)

Runs under BOTH `prod-mode` and `dev-mode` projects already in `playwright.config.ts` (mode count 2 = profile count 2, dev.md §1). Reuse the `beforeEach` console/pageerror trap from `golden_path.spec.ts` — **`consoleErrors` empty is a hard assertion** (dev.md §8): a latent BGM-view render error on deep-link is `critical`.

Each scenario asserts on **rendered DOM the user sees**, not raw API (dev.md §8). Open a real triggering route, not a synthetic fixture.

**SC-3.1 — BGM grid renders.**
- Navigate to the BGM library view (the route the UI exposes — `/bgm` or a tree node; see Ambiguity A5).
- Assert: a BGM-grid-specific selector resolves (e.g. `.bgm-grid`, mirroring `.actor-grid`); ≥1 card OR an explicit empty-state element is visible (never a blank `main`). Structural-sanity assertion: the library chrome (filter bar) is present.

**SC-3.2 — category filter works (acceptance anchor #4).**
- Action: select a category from the 12-enum filter; 
- Assert: the visible card set narrows to that category (cards carry a `data-category` or visible category label that all match the selection). Selecting "all"/clearing restores the full set. A filter that renders but doesn't filter is a `blocker` (golden-path scenario failure).

**SC-3.3 — audio element present + playable source.**
- Assert: each card (or the detail panel) contains an `<audio>` element whose `src` resolves via `mediaUrl()` to a `/api/media?...mp3` URL (the existing `/api/media` + `MEDIA_EXTENSIONS` path already serves `audio/mpeg` — spec §5, **no new server playback endpoint**). Assert the `<audio>` is in the DOM and its `src` ends `.mp3`; (optional, may be flaky in headless) a `canplay`/`loadedmetadata` probe. Don't assert actual audio output (headless) — presence + resolvable URL is the contract.

**SC-3.4 — assignments panel resolves.**
- Precondition: a drama with a `bgm.md` referencing a known id exists in the repo (seed fixture, §5).
- Action: open that bgm's assignments panel.
- Assert: the panel lists the referencing drama (DOM text), mirroring the actor assignments UX. Empty-but-rendered (no JS error) when nothing references it.

**SC-3.5 — generate form round-trip (optional, may be gated behind a stub flag).**
- The generate button triggers a real subprocess → torch. In e2e this is impractical; mark this scenario `test.skip()` unless a UI/env "dry-run" toggle exists, OR assert only that the form renders (category/duration/bpm/intensity/instruments fields present) + the preview-prompt round-trips (preview is side-effect-free). **Flag inline: full UI→generate→mp3 e2e is NOT covered in-browser; it is covered by the Python integration SC-2.1.** (This is a deliberate, documented carve-out — surface to user per general.md §6.)

---

## 4. API consumer-walk / front↔back field mirroring (`tests/test_bgm_consumer_walk.py`) — dev.md §2/§3

Mirrors `test_tree_walker_consumer_walk.py`. **API shape drift between front and back is `critical`** (dev.md severity table).

**SC-4.1 — list payload exposes exactly the fields the React grid reads.**
- Build the shared field table; assert each list item carries every consumer field by the **exact name the UI reads**:

  | JSON shape | consumer field (UI reads) | source |
  |---|---|---|
  | bgm list item | `id` | `bgm_NNNN`, card key |
  | | `category` | filter + label |
  | | `mp3_url` / media path field | `<audio src>` via `mediaUrl()` |
  | | `bpm` | card meta |
  | | `duration` | card meta |
  | | `loopable` | card badge |
  | | `intensity` | card meta |
  | | `instruments` | card meta |
  | | `mood` (if surfaced) | card meta |

  **Action item for the parent:** before sign-off, open `apps/ui/src/components/BgmGrid.tsx` + `types.ts` + `api.ts` and read the ACTUAL field accesses (`item.category`, `item.mp3_url`, …), then make this test assert those literal names. If `BgmGrid` reads `item.mp3` but the backend emits `item.mp3_url` (or `audio_path`), that's the exact class of drift that shipped the empty Projects sidebar — `critical`, not a warning (dev.md §3). **This file did not exist at validation-strategy time (stage 6 output); the test is specified here and MUST be reconciled against the real component during stage-6 validation.**

**SC-4.2 — assignments payload field names mirror.**
- Assert the `/api/bgm/assignments` item shape uses the same keys the assignments panel reads (mirror actor's `{drama, ...}` — see §5).

---

## 5. Assignments integration (`tests/test_bgm_assignments.py`)

Mirrors `casting__writer.find_assignments_for_actor` scan, but over `bgm.md` (NOT `casting.md`) — spec §4 divergence #2.

**SC-5.1 — fixture `bgm.md` referencing a bgm id resolves to its drama (acceptance anchor #4).**
- Setup (`tmp_path` repo):
  - `ai_videos/_bgm/tension/bgm_0007/bgm_0007.{md,mp3}` (a generated bgm).
  - `ai_videos/td/episodes/ep01/bgm.md` containing a cue line referencing it:
    ```
    0-12 bgm_0007 | vol=0.8 | duck=on | fade=in
    ```
- Action: `GET /api/bgm/assignments?bgm_id=bgm_0007`.
- Assert: `200`; response lists `{drama: "td", episode: "ep01", ...}` (the referencing drama/episode). Mirror `find_assignments_for_actor`'s row shape; exact keys per the real mapper.

**SC-5.2 — short-layout root `bgm.md` is also scanned.**
- Setup: `ai_videos/myshort/bgm.md` referencing `bgm_0007` (short sub-type → root `bgm.md`, spec §8).
- Assert: assignments include the short drama. Proves both novel (`episodes/epNN/bgm.md`) and short (root `bgm.md`) layouts are walked.

**SC-5.3 — scan skips `_`-prefixed dirs and unrelated ids.**
- Setup: a `bgm.md` referencing `bgm_9999` (different id); `_bgm/`, `_deleted/` present.
- Assert: querying `bgm_0007` returns `[]` for the unrelated reference; `_`-prefixed dirs (the library itself, deleted) are not mis-scanned as dramas. Mirrors the `startswith("_")` skip in the casting scan.

**SC-5.4 — cue token is grep-discoverable (acceptance anchor #6 — three-way consumer).**
- Assert (pure, no app): `re.findall(r"bgm_\d{4}", bgm_md_text)` finds `bgm_0007` AND a line-wise parse yields `{start, end, id, vol, duck, fade}` for the cue (spec §8 cue format). This is the "grep reverse-lookup + line parse + human-readable" tri-consumer contract. A cue format only one consumer can read = contract drift.

---

## 6. `tools/mux_av.py` end-to-end (`tests/test_mux_av.py`) — acceptance anchor #5

ffmpeg-dependent. **All tests in this file `@pytest.mark.skipif` when ffmpeg is absent** (general.md §3 — skipping with a reason is healthy; silent pass is not). Use `imageio_ffmpeg.get_ffmpeg_exe()` and build tiny fixtures like `test_subtitle_burn.py::_shot_render`.

Fixture builders (all via `imageio_ffmpeg`):
- video: 2 s `testsrc` 320×240 `yuv420p` mp4.
- dialogue: 1.5 s mono `sine`/`anullsrc` → mp3.
- bgm: 3 s `sine` → mp3 (longer than video, to exercise trim/loop).

**SC-6.1 — full mux (video + dialogue + bgm) produces output.**
- Action: `mux_av.py --video … --dialogue … --bgm … --out out.mp4` (invoke the module, or `subprocess.run([sys.executable, "tools/mux_av.py", …])`).
- Assert: `out.mp4` exists and is non-empty.

**SC-6.2 — video stream is copied, not re-encoded (`-c:v copy`).**
- Assert via `ffprobe`: output video codec == input video codec AND (strong signal) the assembled ffmpeg argv contains `-c:v copy`. If the tool exposes a `build_cmd()`/dry-run, assert on the argv directly (cheaper, no encode); otherwise ffprobe the streams. A re-encoded video stream violates spec §7.

**SC-6.3 — audio present + dialogue not halved.**
- Assert: output has exactly one audio stream (`-c:a aac`), non-empty duration ≈ video duration. Assert the filtergraph contains `amix=normalize=0` (spec §7 — `normalize=0` is the load-bearing token; without it `amix` silently halves the dialogue). If the tool builds the graph as a string, assert the substring; this is a **contract assertion on the exact bug the spec calls out**.

**SC-6.4 — sidechain ducking order is `[bgm][dialogue]` (the classic-error guard).**
- Assert the filtergraph applies `sidechaincompress` with BGM as the compressed input and dialogue as the sidechain key, in that order (spec §7 — "顺序反了是经典错误"). String-assert the graph: `sidechaincompress` appears with `[bgm]` first / `[dialogue]` as key. Reversed order = `blocker` (ducking inverts: dialogue gets ducked under bgm).

**SC-6.5 — missing-dialogue and missing-bgm behavior matrix.**
- Action a: `--bgm` only, no `--dialogue` → assert output has bgm audio, no ducking applied (no `sidechaincompress` in argv).
- Action b: `--dialogue` only, no `--bgm` → assert output carries only the dialogue track.
- Per spec §7 the behavior matrix is "from angle-2 交付" — reconcile exact expected behavior with the angle-2 / mux spec at stage 6; assert the documented matrix, don't invent.

**SC-6.6 — bgm shorter/longer than video.**
- Assert: bgm longer than video → trimmed to video length (`apad`/trim, no overrun); bgm shorter → loop (`-stream_loop`/`aloop`) + `apad` fills to video end (spec §7). Output duration ≈ video duration in both cases.

---

## 7. `tools/stableaudio_gen.py` `--dry-run` (`tests/test_stableaudio_gen_dryrun.py`)

The real script imports torch — **never import the module in the webapp test process**. Test only the `--dry-run` CLI contract via subprocess, and **skip if torch is unavailable** (the script may import torch at top level; if so, `--dry-run` must short-circuit BEFORE the heavy import — flag as a finding if it doesn't, because then dry-run can't run on a CI box without torch). 

**SC-7.1 — `--dry-run` prints the planned prompt/params and exits 0 without writing an mp3.**
- Action: `subprocess.run([sys.executable, "tools/stableaudio_gen.py", "--prompt", "...", "--seed", "1", "--duration", "8", "--out", out, "--dry-run"])`.
- Assert: rc 0; stdout echoes the prompt + seed + duration + out; `out` is NOT created (dry-run is side-effect-free, spec §6). This is what the webapp's path-validation relies on.
- **Skip marker:** `skipif` torch import is required and absent — but FIRST raise a `warning` finding if `--dry-run` requires torch (it shouldn't; the whole point is a cheap webapp-side path check).

**SC-7.2 — independent `requirements.txt` exists and excludes itself from webapp deps.**
- Assert (pure): `tools/requirements.txt` (or `tools/stableaudio_requirements.txt`) lists torch / stable-audio-tools, and `projects/ai_video_management/requirements.txt` does **NOT** pull torch (spec §2/§6 — webapp process carries no torch). A torch entry leaking into the webapp requirements = `blocker` (defeats the subprocess-isolation design).

---

## 8. Build / dependency hygiene (dev.md §6) — `warning`/`blocker`

**SC-8.1 — no `uv` in any new Makefile target.** The repo Makefile is pip-only (verified). Any BGM/mux/stableaudio install or test target MUST use `$(PIP)` / `$(PY) -m pytest`. A `uv run` invocation without a pip fallback = `blocker` (general dev rule #6; `uv` has crashed with `EXCEPTION_ACCESS_VIOLATION` on this host).

**SC-8.2 — new test files run under `make test-backend` (`python -m pytest tests/`).** No bespoke runner; they live in `tests/` and import via the `conftest.py` sys.path insert.

---

## 9. Cross-platform skip markers (dev.md §5, general.md §3) — host is Windows

- **mux / subtitle / stableaudio tests** depend on an ffmpeg binary → `@pytest.mark.skipif(not _ffmpeg_available(), reason="ffmpeg not on PATH / imageio-ffmpeg missing")`. (imageio_ffmpeg ships a binary, so these usually RUN on the Windows host — but keep the guard.)
- **stableaudio real-inference** (not dry-run) is GPU/torch-only → never run in CI; covered only by the dry-run contract + stubbed webapp integration. Mark any accidental real-inference test `skipif` torch+CUDA absent.
- **subprocess argv path-separator assertions:** assert on the script *basename* (`stableaudio_gen.py`) substring, not a `/`-joined absolute path, so the assertion holds on Windows (`\`) and POSIX (`/`). A `find ... -name` or `os.fork`-style POSIX-only control test → `skipif(sys.platform == "win32", reason="POSIX-only")`.
- No POSIX-symlink / case-sensitivity dependence is expected in this module; if one appears in the stage-6 code, mark it `SKIPPED-WINDOWS-...`, do not let it fail silently.

---

## 10. Manual walkthrough (general.md §4, dev.md §7) — emit `validation.requires_manual_walkthrough`

After all automated levels pass, the parent surfaces a manual pass for things e2e can't judge:
- BGM card visual hierarchy + category-filter affordance clarity.
- `<audio>` control contrast/focus visibility; perceived play latency on a real `.mp3`.
- **Actual audio quality of a real Stable Audio render** (loudnorm -16 LUFS target, spec §6) — only a human ear validates this; assert nothing automatically.
- **Real mux output A/V sync + audible ducking** — that the dialogue is clearly intelligible over a ducked bgm (the `sidechaincompress` *sounds* right, not just that the filter string is present).

---

## 11. Carve-outs surfaced for explicit user confirmation (general.md §6)

Each is a deliberate spec decision NOT to test a behavior. Stage-5 sign-off MUST confirm these are intended (not silent gaps):

1. **No `generate-diverse` / archetype for BGM** (spec §4 「省略」) — actor has it; BGM omits. Confirm no validation gate is expected for it.
2. **Multi-cue whole-`bgm.md` auto-arrangement is out of scope** (spec §1, §7 — v1 muxes a *single* bgm). The cue-line *parse* is tested (SC-5.4); the *orchestration of multiple cues into one timeline* is NOT. Confirm.
3. **`create-prompts` / `preview-prompts` offline-backfill flow is optional** (spec §4, §11) — if shipped, SC-1.2/SC-3.5 cover preview; if omitted, those assertions drop. Confirm presence.
4. **seed is best-effort reproducible, not hard-reproducible** (spec §2) — unlike actor, there is NO "same seed → byte-identical mp3" test. Do not write one; assert only that `seed` is persisted in the `.md`. Confirm this relaxation is intended.
5. **Full UI→generate→torch→mp3 is NOT covered in-browser** (SC-3.5) — covered by Python integration with a stubbed subprocess instead. Confirm the in-browser carve-out.

---

## Ambiguities / open reconciliations (resolve at stage 6 against real artifacts; do NOT fabricate)

- **A1 — delete verb/path:** spec §4 table says `delete`; actor uses `POST /api/actors/delete`. Assume `POST /api/bgm/delete` (mirror), but verify the actual route registration in stage 6 and fix SC-1.2/SC-2.4 to match. (Note: the older boot-smoke `expected` set lists `DELETE /api/casting/assign`, so both verbs exist in the codebase — don't assume.)
- **A2 — list envelope:** whether `GET /api/bgm` returns a bare list or `{items: [...]}` mirrors whatever `GET /api/actors` does. Reconcile SC-1.3/SC-4.1 against the real `actor__dto.to_payload()` shape.
- **A3 — bgm-delete assignment gate:** actor-delete refuses when cast (follow-up 043). Spec §4 mirrors assignments-reverse-lookup but doesn't explicitly state delete-refusal for bgm. SC-2.4 assumes the gate exists; if the author chose unconditional soft-delete, relax to the soft-move assertion only.
- **A4 — repo-root override for write tests:** generate/delete write under `ai_videos/_bgm/`. Tests MUST override `container.repo_root_path` to a `tmp_path` (as `make_app` supports) so they never pollute the real `ai_videos/` tree. Confirm `make_app`/Container accepts a tmp root for write paths (it overrides `repo_root_path`, so yes).
- **A5 — BGM library UI route:** the exact front-end route/tree-node that opens `BgmGrid` (`/bgm`? a sidebar leaf? a media-sibling view like `VoiceGrid`?) is a stage-6 UI decision. SC-3.* navigation targets must be reconciled against the shipped router. `VoiceGrid` is the closest existing analog (spec §5 "模式同 VoiceGrid").
- **A6 — `system_cue` classification** (spec §11) — BGM vs SFX. Tested as a normal category; no special-casing assumed.

---

## Severity quick-reference for this level

| Finding | Severity |
|---|---|
| Boot-time DI/wiring exception (SC-1.1) | `critical` (halt) |
| BGM list/assignments field drift vs UI reads (SC-4.1/4.2) | `critical` |
| Latent BGM-view render error on deep-link / blank `main` (SC-3.*) | `critical` |
| Wrong `license` metadata value (SC-2.1.3) | `blocker` |
| State-changing endpoint returns 405 under `serve_static=True` (SC-2.5/2.6/2.7) | `blocker` |
| Per-category (non-global) id allocation collision (SC-2.2) | `blocker` |
| Category filter renders but doesn't filter (SC-3.2) | `blocker` |
| `amix` missing `normalize=0` / reversed sidechain order (SC-6.3/6.4) | `blocker` |
| Video stream re-encoded instead of `-c:v copy` (SC-6.2) | `blocker` |
| torch leaking into webapp `requirements.txt` (SC-7.2) | `blocker` |
| `uv` in a Makefile target without pip fallback (SC-8.1) | `blocker` |
| Fewer e2e profiles than runtime modes (must be 2) | `blocker` |
| POSIX/ffmpeg-dependent test with no skip marker (§9) | `blocker` |
| `--dry-run` requires torch (can't run on CI) (SC-7.1) | `warning` |
| Manual-walkthrough audio-quality / ducking audibility (§10) | `requires_manual_walkthrough` |
