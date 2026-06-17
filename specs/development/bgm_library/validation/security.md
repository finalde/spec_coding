---
worker_id: level-specialist-05-security
stage: 5
role: level-specialist
level: security
status: complete
blockers: []
confidence: high
---

# Validation — security (bgm_library)

Per `agent_refs/validation/general.md` § Standard severity policy: **every SEC-* check is `critical` and halts immediately; no revision rounds without explicit user approval.** Path traversal / sandbox escape is independently `critical`. The one compliance item (license) is the sole `warning`.

Threat model is driven by the two structural deltas vs. the actor library (spec §4 "两处与 actor 的唯一分歧"): (a) `bgm__command.generate` shells out to `tools/stableaudio_gen.py` via `subprocess.run`, and (b) `category` adds a user-controlled directory layer (`_bgm/{category}/bgm_NNNN/`) that actor's flat `_actors/actor_NNNN/` never had. Both are new attack surface; everything else is "照搬 actor" and inherits actor's already-hardened posture (`SafeResolver`, `MediaQuery.serve`, `validate_actor_id`).

Reference implementations the bgm slice mirrors (these are the known-good baselines a check compares against):
- Path sandbox: `libs/common/safe_resolve.py` (`SafeResolver.resolve` — rejects `..`, `\`, `%`, absolute, symlink, out-of-allowed-top-level, escape-after-resolve).
- Media serving: `libs/application/queries/media__query.py` (`MediaQuery.serve` — ext allowlist `MEDIA_EXTENSIONS` ⊇ `.mp3` `audio/mpeg`, then `ExposedTree.is_inside`, then `SafeResolver.resolve`).
- id validation: `libs/domain/value_objects/actor__valueobject.py` `validate_actor_id` + `_ACTOR_ID_RE = ^actor_\d{4,}$`.
- Atomic id alloc: `actor__writer.py` `_allocate_actor_id` (`mkdir(exist_ok=False)`).
- ffmpeg subprocess precedent (correct shape — arg list, no shell): `libs/infrastructure/writers/subtitle__writer.py` (`subprocess.run(cmd, ..., shell` absent).

---

## SEC-01 — Generation subprocess uses an argument list, never `shell=True` / string concatenation
**Severity: critical (halt).**

`bgm__command.generate` → `BgmPool` invokes `tools/stableaudio_gen.py`. The CLI contract is `--prompt --seed --duration --model --out [--dry-run]` (spec §6). Every one of those values is at least partly user-influenced (prompt text assembled from form fields including free-text `instruments`; `category` shapes the default prompt template; `--out` is derived from `category`+id).

**Check:** the `subprocess.run(...)` call passes a Python **list** `["python", str(script_path), "--prompt", prompt, "--seed", str(seed), ...]` with `shell` absent or explicitly `False`. There must be NO `shell=True`, no `" ".join(...)` / f-string command, no `os.system`, no `os.popen`, no `subprocess.run(a_string, shell=True)`.

**How to test:**
- Static: `grep -rn "shell=True\|os.system\|os.popen" libs/ apps/ tools/stableaudio_gen.py tools/mux_av.py` over the bgm slice + the two tool scripts must return zero hits. Assert the `subprocess.run` first arg is a `list`/`Sequence`, not `str`.
- Dynamic: monkeypatch `subprocess.run` to capture `args`; call `generate` with `instruments="x; rm -rf ~"` and `prompt`-affecting fields containing `$(...)`, backticks, `;`, `&&`, `|`, newline. Assert the injected shell metacharacters land **inside a single argv element** (passed verbatim to the script as one `--prompt` value), never as separate argv tokens and never via a shell.

**Note:** the actor baseline shells out to ffmpeg in `subtitle__writer.py` using exactly this arg-list shape — bgm MUST match it. Failure here = arbitrary command execution from a web form.

---

## SEC-02 — Numeric generate-form fields are typed and bounded before reaching the subprocess
**Severity: critical (halt).**

`duration`, `bpm`, `intensity` flow from the generate form into the subprocess args / `.md` metadata. `intensity` is spec'd `1-5 int`. Unbounded/unvalidated numerics are both a resource-exhaustion vector (a 10000-second Stable Audio diffusion run is a GPU DoS) and a type-confusion vector (a string where an int is expected can smuggle argv content past a weak `--duration` parser).

**Check:** the Cdto / `BgmAttrs` value object coerces and bounds:
- `duration` → positive number, capped (recommend ≤ a hard ceiling, e.g. 300s; pick the spec's eventual value — flagged ambiguity below).
- `bpm` → positive int within a sane musical range (e.g. 30–300).
- `intensity` → int in `[1,5]` (spec-stated closed range).
- All three rejected (domain error, HTTP 4xx) when non-numeric / out-of-range, **before** any `subprocess.run` or filesystem write.

**How to test:** unit-test `BgmAttrs`/Cdto construction with `duration="9999999"`, `duration="-5"`, `bpm="abc"`, `intensity=7`, `intensity="3; ls"`. Each raises the bgm domain error. Integration: POST the generate route with these values → 4xx, and assert (monkeypatched) `subprocess.run` was **never** called.

**Ambiguity (inline):** spec §6 doesn't state a hard `duration` ceiling. *(judgment call — recommend a bounded cap because an unbounded duration is a GPU-time DoS; the exact number is a spec gap for stage 6 to fill, not a blocker on this check's existence.)*

---

## SEC-03 — `category` is validated against the closed 12-enum BEFORE any path construction
**Severity: critical (halt) — path traversal / sandbox escape class.**

`category` is simultaneously a metadata field AND a directory level: `_bgm/{category}/bgm_NNNN/` (spec §3). A malicious `category` of `..`, `../../etc`, `..\..\`, an absolute path, or any string with `/`, `\`, `:`, `%` would let a write/read escape the `_bgm/` root or land in an arbitrary sibling tree. This is the single biggest new traversal surface vs. actor (which had no user-controlled directory segment).

**Check:** `category` is validated against the closed enum `{tension, combat, climax_hype, faceslap, tragic, warm, romance_pain, suspense, daily, flashback, theme_open, system_cue}` (spec §3, 12 values) — a frozenset membership test in the `bgm__valueobject` domain layer — and the bgm slice **never** joins a raw `category` onto a path without that membership check passing first. Defense in depth: even after enum-validation, the final `_bgm/{category}/...` path is resolved through `SafeResolver` (or an equivalent `is_inside`-style containment assert) so a future enum entry containing a path separator can't escape.

**How to test:**
- Unit: enum validator rejects `"../../etc"`, `"..\\windows"`, `"tension/../.."`, `"system_cue/../_actors"`, `""`, `"COMBAT"` (case), `"foo"`; accepts exactly the 12 lowercase slugs.
- Integration: POST generate with `category="../../../../tmp/evil"` → 4xx, no directory created outside `_bgm/`. Walk `_bgm/`'s parent after the call; assert no new dirs appeared anywhere but a rejected request.
- Class-of-failure sweep: iterate a traversal-payload list × {generate, list-by-category, assignments-lookup} and assert every one is rejected before a filesystem op.

---

## SEC-04 — `bgm_NNNN` id validated against `^bgm_\d{4,}$` before any filesystem op (delete / serve / lookup)
**Severity: critical (halt) — path traversal / sandbox escape class.**

The id becomes a folder + filename (`bgm_NNNN/bgm_NNNN.mp3`) and is accepted from the UI on delete / assignments-lookup. An id like `../actor_0001` or `bgm_0001/../../x` must be refused. This mirrors actor's `validate_actor_id` (`^actor_\d{4,}$`) — the spec §4 calls for `validate_bgm_id` in `bgm__valueobject`.

**Check:** `validate_bgm_id` exists in `bgm__valueobject.py`, regex `^bgm_\d{4,}$`, and is called at the top of `bgm__command.delete` (mirroring `ActorCommand.delete` which calls `validate_actor_id` before touching the pool) and any query that resolves an id to a path.

**How to test:** unit-test `validate_bgm_id` rejects `"../actor_0001"`, `"bgm_0001/../x"`, `"bgm_01"` (too short), `"bgm_abcd"`, `"BGM_0001"`, `""`, `"bgm_0001\x00"`; accepts `"bgm_0001"`, `"bgm_12345"`. Integration: `DELETE` / lookup with a traversal id → 4xx, no file touched outside the matched folder.

---

## SEC-05 — `.mp3` serving stays sandboxed through the existing `MediaQuery.serve` path (no new serving code)
**Severity: critical (halt) — path traversal / sandbox escape class.**

Spec §5 explicitly states "零服务端新增播放" — BGM試聽 reuses the existing `/api/media` + `MEDIA_EXTENSIONS` (`.mp3` → `audio/mpeg` already present in `media__query.py` MIME map and `MEDIA_EXTENSIONS_SET`). The risk is that someone adds a bespoke bgm-audio endpoint that bypasses `SafeResolver`.

**Check:** no new file-serving route is introduced for bgm; the UI's `mediaUrl()` for a bgm clip routes through `GET /api/media?path=ai_videos/_bgm/...`, which already runs ext-allowlist → `ExposedTree.is_inside` → `SafeResolver.resolve` → `is_file()` (all four gates in `MediaQuery.serve`). Confirm `.mp3` is in `MEDIA_EXTENSIONS` (it is) so no extension-map edit is needed.

**How to test:**
- Static: `grep -rn "FileResponse\|StreamingResponse\|/api/.*media\|send_file" apps/api/routes/bgm__route.py` → zero hits (bgm route serves JSON only; audio goes via the shared `/api/media`).
- Dynamic (regression on the shared endpoint, scoped to the bgm root): `GET /api/media?path=ai_videos/_bgm/../../../etc/passwd` → 4xx/blocked; `?path=ai_videos/_bgm/tension/bgm_0001/bgm_0001.exe` (wrong ext) → `UnsupportedFileExtensionError`; valid `?path=ai_videos/_bgm/tension/bgm_0001/bgm_0001.mp3` → 200 `audio/mpeg`.

---

## SEC-06 — Atomic id allocation cannot be coerced into writing outside `_bgm/`
**Severity: critical (halt) — path traversal / sandbox escape class.**

bgm id allocation must scan **cross-category** for the global max `bgm_NNNN` and `mkdir(exist_ok=False)` (spec §3, §10.2), mirroring actor's `_allocate_actor_id`. The new wrinkle: the scan walks every `{category}/` subdir of `_bgm/`. A symlinked or non-conforming `category` dir, or a crafted existing folder, must not let allocation create/return a path outside `_bgm/`.

**Check:** the allocator (a) only enumerates the 12 known category dirs (or skips any dir not matching the enum / not matching `^bgm_\d{4,}$` for id folders, the way actor's `_ACTOR_DIR_RE` filters), (b) builds the target as `_bgm/{validated_category}/bgm_{N:04d}` and (c) the resulting path is contained under `SafeResolver.root / ai_videos / _bgm` (assert via `is_relative_to` / `is_inside`). `mkdir(exist_ok=False)` is the atomic claim (concurrency correctness is the DDD-level check; here we only assert the path containment).

**How to test:** unit — seed `_bgm/` with a junk dir `_bgm/..evil` and a non-`bgm_` folder; assert the scan ignores them and the allocated path is `is_relative_to(_bgm_root)`. (On Windows, a symlink-based escape test is `pytest.mark.skipif(sys.platform=="win32", reason="symlink needs Developer Mode")` per `agent_refs/validation/development.md` §5.)

---

## SEC-07 — `tools/stableaudio_gen.py --out` is constrained to the bgm sandbox
**Severity: critical (halt) — path traversal / sandbox escape class.**

The webapp passes `--out` to the generation script. If `--out` were derived from raw user input (e.g. an unchecked `category`/id) the script could be made to write an `.mp3` anywhere on disk (overwrite `tools/`, drop a file in a web-served dir, etc.).

**Check:** the `--out` value handed to the subprocess is built **only** from already-validated `category` (SEC-03) + freshly-allocated id (SEC-06), resolved under `_bgm/`, and the webapp asserts containment before spawning. The script itself should also treat `--out` as untrusted and refuse to write outside an allowed root *(judgment call — defense in depth; primary gate is the webapp, since the script's own threat model is "called by the webapp," but a containment assert in the script costs little).*

**How to test:** monkeypatch `subprocess.run`, call `generate`, capture argv, assert the `--out` argument resolves under `<root>/ai_videos/_bgm/`. Negative: force a traversal `category`/id upstream (should already be blocked by SEC-03/04) and assert `generate` raises before building `--out`.

---

## SEC-08 — Soft-delete target stays inside the sandbox (`_deleted/_bgm/`)
**Severity: critical (halt) — path traversal / sandbox escape class.**

`bgm__writer` soft-deletes by moving `_bgm/{category}/bgm_NNNN/` into `_deleted/_bgm/` (spec §3, §4 mirrors actor's `delete_actor` → `ai_videos/_deleted/_actors/`). Both the source (validated id+category) and destination must resolve inside `ai_videos/`.

**Check:** the move's source path is `validate_bgm_id`-gated + enum-gated; the destination is a constant `root / "ai_videos" / "_deleted" / "_bgm" / ...` (the actor precedent uses a hardcoded `_deleted / _actors` constant — no user input in the dest). Assert both endpoints `is_relative_to(root / "ai_videos")`. The id-alloc / assignments scan must skip `_`-prefixed dirs (`_deleted`, `_bgm`'s own `_deleted`) the way actor's scanner "跳过 `_` 开头目录" (spec §4) — otherwise a soft-deleted id could collide on re-allocation.

**How to test:** unit — `delete` a known bgm, assert the resulting `{from,to}` both resolve under `ai_videos/`, `to` is under `_deleted/_bgm/`, and the original `_bgm/{category}/` path no longer exists. Assert the cross-category id-alloc scan skips `_deleted/`.

---

## SEC-09 — If `tools/mux_av.py` is reachable from the webapp, its path args are sandboxed and ffmpeg runs as an arg list
**Severity: critical (halt) IF webapp-reachable; otherwise out-of-gate (note).**

`mux_av.py` takes `--video --dialogue --bgm --out` (spec §7) and shells to ffmpeg. **Spec §1/§4 do not wire `mux_av.py` into the webapp** (no route in the §4 DDD table — it's a standalone成片合成工具). So in v1 it is a CLI tool, not a web-exposed surface.

**Check (conditional):** confirm `mux_av.py` has **no** route / Query / Command binding in the bgm slice (grep `apps/api/routes/` + `container.py` for `mux`). 
- If reachable → all four path args MUST pass through `SafeResolver`/containment before use, and the ffmpeg call MUST be an arg list (no `shell=True`) exactly like `subtitle__writer.py`. Same test shape as SEC-01 + SEC-05.
- If NOT reachable (expected) → record as `validation.pass` with a note: "mux_av.py is CLI-only in v1; its path-arg sandboxing is out of the web threat gate. **Confirm this carve-out is intended** (per `agent_refs/validation/general.md` §6 — every v1 carve-out surfaced to the user)." Still assert no `shell=True` in the script as a hygiene check (SEC-01 grep already covers `tools/mux_av.py`).

**How to test:** `grep -rn "mux" apps/api/ libs/application/ libs/infrastructure/ | grep -iv "test"` → expect zero web bindings. Confirm SEC-01's shell-metachar grep includes `tools/mux_av.py`.

---

## SEC-10 — Stable Audio license: Stability AI Community License revenue ceiling is a compliance flag
**Severity: warning (logged; never halts).**

Not a security vuln — a licensing/compliance obligation that belongs in the validation record so it isn't lost. Spec §2 fixes `license = Stability AI Community License`: **free commercial use only while annual revenue < US$1,000,000**; above that a Stability enterprise license is required. Generated `.mp3`s carry `license` metadata (spec §3).

**Check:** every generated `bgm_NNNN.md` writes `license: Stability AI Community License`, and the project README documents the revenue ceiling + that seed is best-effort reproducible (spec §2, §10.7). This is a `warning` per the general severity table ("Observe-only / compliance" class) — log it; it does not block stage-6 sign-off, but the README note is an acceptance anchor (§10.7) that a `blocker`-level acceptance check (owned by the acceptance/criteria worker, not security) should also assert.

**How to test:** assert the metadata-build emits the exact license string; grep the README for the "$1,000,000 / 100万美元" revenue-ceiling note and the "seed best-effort" note.

---

## Audit-event expectations (stage 6 runtime)
Per `agent_refs/validation/general.md` §5, each SEC-* run emits `validation.started` (with `pre_reading_consulted`) → `validation.pass` or `validation.issue.raised`. Any SEC-* `issue.raised` carries `severity: critical` and the parent emits `pipeline.halted` immediately (no revision rounds without explicit user approval). SEC-10 raises at most a `warning` and never halts.

## Cross-cutting note
SEC-01..SEC-08 are the load-bearing new surface; SEC-05 and SEC-09's "reuse the audited path" stance means the strongest posture is **add no new file-IO/serving/subprocess code paths beyond the one subprocess call** — every byte that reaches the filesystem or the shell should pass through a gate that already exists in the actor/media slices.
