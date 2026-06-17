---
worker_id: researcher-03-actor-slice-mirror
stage: 3
role: researcher
angle: actor-slice-mirror
status: complete
blockers: []
confidence: high
---

# Angle: actor-slice-mirror — file-by-file blueprint for the `bgm__*` DDD slice

## 1. What this angle covers

Repo-internal only. I read the entire **actor** aggregate across all four DDD layers
(`apps/api`, `libs/application`, `libs/domain`, `libs/infrastructure`), the **casting**
reverse-lookup machinery (`find_assignments_for_actor` / `assigned_actor_ids`), the
**media** serving route (used for mp3 playback), and the UI (`ActorGrid.tsx`, `api.ts`,
`VoiceGrid.tsx`'s `<audio>` pattern). The deliverable is a 1:1 blueprint so the new BGM
library slice can be built by analogy. The actor slice is the right mirror: the **voice**
slice already mirrors actor for the audio case (same casting.md table, mp3 media), so BGM
should mirror **actor's structure** + **voice's audio handling**.

Key shape difference: actor `generate` shells out to **Kling HTTP**; BGM `generate` will
shell out to **`tools/musicgen_gen.py` via subprocess**. Actor reverse-lookup scans every
drama's `casting.md`; BGM must scan each drama's per-episode **`bgm.md`** for `bgm_NNNN`
references.

## 2. Key findings — file-by-file blueprint

### Actor ID allocation & on-disk format (mirror exactly)

- **Folders:** `ai_videos/_actors/actor_NNNN/` (`ACTORS_DIR_NAME="_actors"`,
  `actors_dir() = exposed.root/"ai_videos"/"_actors"`). Dir regex `^actor_(\d{4,})$`,
  id regex `^actor_\d{4,}$` (zero-padded **4+** digits, `f"actor_{n:04d}"`).
- **Next id:** `_next_actor_id_num(actors_dir)` = `max(NNNN)+1` over existing folders,
  pure scan, no side effects. **Allocation:** `_allocate_actor_id` walks forward from that
  start calling `mkdir(exist_ok=False)` as the atomic claim primitive (handles concurrent
  count=1 races), up to `_MAX_ID_ALLOC_SCAN=1000` attempts.
- **Sidecar:** `actor_NNNN/actor_NNNN.md` built by `_build_sidecar(...)` — H1 `# actor_NNNN`,
  a `| 字段 | 值 |` markdown table (ethnicity/gender/age_range/look/notes/seed/resolution/
  body_image/body_resolution/archetype), then a ```` ## 生成 prompt ```` fenced block.
  Parsed back by `_parse_sidecar_full` which reads only `|key|value|` rows for a known key
  set and returns `(ActorAttrs, archetype|None)`. `"—"` → empty string.
- **Reaper:** `_reap_incomplete_folders` deletes jpg-less folders older than
  `_REAP_MIN_AGE_SECONDS=300` **unless** a sidecar `.md` exists (prompt-only/pending).
- **Soft-delete:** `delete_actor` renames the folder to
  `ai_videos/_deleted/_actors/actor_NNNN/`, disambiguating collisions with `__N` suffix.

### Casting reverse-lookup (what BGM must mirror against `bgm.md`)

`Casting.find_assignments_for_actor(actor_id)` and `assigned_actor_ids()` (in
`libs/infrastructure/writers/casting__writer.py`) iterate `ai_videos/*/` (skipping `_`-prefixed
system dirs and symlinks), open `<drama>/casting.md` (`CASTING_FILE_NAME`), `self._parse(...)`
the table rows, and match `entry.actor_id`. `find_…` returns
`[{drama, role, notes, character_folder, character_folder_exists}, …]` sorted by (drama, role);
`assigned_actor_ids()` returns the union `set[str]`. `ActorQuery.list()` calls
`assigned_actor_ids()` once and tags each row's `is_assigned` (avoids N round-trips).

**For BGM the scan target is different:** instead of one `<drama>/casting.md`, BGM lives in
per-episode `bgm.md` files. The bgm repository's reverse-lookup must walk
`ai_videos/<drama>/episodes/ep*/bgm.md` (and/or a drama-level `bgm.md` for shorts) and
extract `bgm_NNNN` tokens. **Open question for spec:** exact `bgm.md` schema is not yet
defined anywhere in the repo (no `bgm.md` exists today, see §4) — the spec must define it
(a markdown table or `bgm_NNNN` reference lines) so the scanner has a contract to parse.

### Media serving (mp3 playback — already supported)

`GET /api/media?path=<rel>` → `MediaQuery.serve` → `FileResponse`. `MEDIA_EXTENSIONS`
(`libs/common/exposed_tree.py`) **already includes `.mp3 .wav .m4a .aac .ogg .flac`**, and
`_MEDIA_MIME_MAP` maps `.mp3→audio/mpeg`. **No new media route needed.** UI plays audio via
`new Audio(mediaUrl(path))` (VoiceGrid pattern) or an `<audio controls src={mediaUrl(...)}>`.
`mediaUrl(path, mtime)` returns `/api/media?path=…&v=<mtime>` (cache-bust).

### File-by-file table

| Actor file | Responsibility | Key classes / methods | BGM equivalent (`bgm__*`) |
|---|---|---|---|
| `apps/api/routes/actor__route.py` | HTTP surface | `router`; pydantic `GenerateActorsBody`/`DeleteActorBody`; endpoints `/api/actors/{generate,create-prompts,preview-prompts,delete,assignments}` + `GET /api/actors` | `bgm__route.py`: `/api/bgm/{generate,create-prompts,preview-prompts,delete,assignments}` + `GET /api/bgm`. Body fields = BGM attrs (genre/mood/tempo/instrument/duration_s/notes) not face fields. `generate` triggers musicgen subprocess. |
| `apps/api/routes/__init__.py` | combine routers | `router.include_router(_actor_router)` | add `from …bgm__route import router as _bgm_router` + `router.include_router(_bgm_router)` |
| `apps/api/app_factory.py` | error→JSON handlers; eager-create pool dir | `_PLAIN` tuple rows for each `Actor*Error`; special handlers for `ActorAlreadyAssignedError`/`ActorDeleteTargetExistsError`; `container.actor_pool().actors_dir().mkdir(...)` | add `Bgm*Error` rows to `_PLAIN`; special handler for `BgmAlreadyAssignedError`/`BgmDeleteTargetExistsError`; eager-mkdir `container.bgm_pool().bgm_dir()` |
| `apps/api/container.py` | DI wiring | `actor_pool` Singleton(`ActorPool`); `actor_command`/`actor_query` Factory(pool=…, casting=…) | `bgm_pool` Singleton(`BgmPool`); `bgm_command`/`bgm_query` Factory(pool=bgm_pool, casting=casting). Inject a musicgen subprocess client if extracted. |
| `libs/application/commands/actor__command.py` | write ops | `ActorCommand.generate/create_prompts/generate_diverse/delete`; delete refuses when `casting.find_assignments_for_actor` non-empty → `ActorAlreadyAssignedError` | `BgmCommand.generate/create_prompts/delete` (drop diverse unless wanted). `generate` calls `pool.generate_batch` which subprocesses musicgen. `delete` refuses if `bgm.md` references exist. |
| `libs/application/queries/actor__query.py` | read ops | `ActorQuery.list(include_pending)` (tags `is_assigned` via `casting.assigned_actor_ids()`), `preview_prompts`, `get_assignments` | `BgmQuery.list/preview_prompts/get_assignments`; `is_assigned` via bgm-reverse-lookup `assigned_bgm_ids()` over `bgm.md`. |
| `libs/application/dtos/actor__dto.py` | Qdtos+Cdtos, self-validating | `ActorListRowQdto`, `ActorListQdto`, `PreviewPrompt(s)Qdto`, `ActorAssignmentsQdto`; `GenerateActorsInputCdto` (`__post_init__` builds `ActorAttrs`+validates), `GenerateActorsResultCdto`, `DeleteActorResultCdto` | `bgm__dto.py`: same shapes, `BgmListRowQdto` carries BGM attrs + `audio_path` (analogue of `image_path`) + `is_assigned`/`pending_import`; `GenerateBgmInputCdto.__post_init__` builds `BgmAttrs`. |
| `libs/application/mappers/actor__mapper.py` | DAO↔Qdto/Cdto | `ActorMapper.info_to_qdto/list_to_qdto/generate_to_cdto/preview_to_qdto` | `BgmMapper` same statics; `info_to_qdto` maps `BgmInfo.audio_path`. |
| `libs/domain/repositories/actor__repository.py` | Protocol seam | `ActorRepository` Protocol: `list_actors`, `generate_batch`, `create_prompts_batch`, `preview_prompts`, `delete_actor`, `actors_dir`, `actor_exists`, `actor_face_filename`/`actor_body_filename` | `BgmRepository` Protocol: `list_bgm`, `generate_batch`, `create_prompts_batch`, `preview_prompts`, `delete_bgm`, `bgm_dir`, `bgm_exists`, `bgm_audio_filename`. |
| `libs/domain/value_objects/actor__valueobject.py` | immutable attrs + enums + validators | `ActorAttrs` (frozen, `__post_init__→validate()`); frozensets `ETHNICITY/GENDER/AGE_RANGE/LOOK/RESOLUTION_OPTIONS`; `validate_actor_id` (`^actor_\d{4,}$`), `validate_batch_count`, `validate_resolution`, `validate_seeds` | `BgmAttrs` (frozen) with BGM enums (GENRE/MOOD/TEMPO/INSTRUMENT options, DURATION bounds); `validate_bgm_id` (`^bgm_\d{4,}$`), `validate_batch_count`, `validate_duration`. |
| `libs/domain/errors/actor__error.py` | named domain errors | `ActorDomainError` base + `InvalidActorAttributeError`, `InvalidActorIdError`, `ActorNotFoundError`, `ActorAlreadyAssignedError`(carries assignments), `ActorAlreadyDeletedError`, `ActorDeleteTargetExistsError`, `ActorDeleteFailedError`, `ActorGenerationDirMissingError`, `AssignmentsScanFailedError` | `bgm__error.py`: rename `Actor`→`Bgm`; add `MusicgenFailedError`/`MusicgenMissingError` for the subprocess (analogue of Kling failure errors). |
| `libs/infrastructure/writers/actor__writer.py` | the pool engine | `ActorPool` (implements repository); `ActorInfo`/`ActorAttrs`(infra dup)/`GenerateResult` dataclasses; id alloc (`_next_actor_id_num`, `_allocate_actor_id`), `_build_sidecar`/`_parse_sidecar_full`, `list_actors`, `delete_actor`, `_reap_incomplete_folders`; `generate_batch` calls Kling HTTP; `create_prompts_batch` writes id-tagged prompt sidecar w/ no provider call | `bgm__writer.py`: `BgmPool` with identical id-alloc / sidecar / list / delete / reaper. `generate_batch` runs `subprocess.run(["python","tools/musicgen_gen.py", …])` writing `bgm_NNNN.mp3` into the folder (mirror Kling's "write bytes into folder"). `create_prompts_batch` writes prompt-only sidecar. Drop the huge `_VARIANCE_*` face pools — BGM needs its own (smaller) prompt assembly. |
| `libs/infrastructure/writers/actor__chinese_prompt.py` | prompt-text builder (negatives etc.) | `build_negatives()` and prompt assembly helpers, lazily imported by writer | `bgm__prompt.py` (optional): build the musicgen text prompt from `BgmAttrs`. Likely much smaller; may be folded into the writer. |
| `libs/infrastructure/writers/casting__writer.py` | reverse-lookup scanner | `find_assignments_for_actor`, `assigned_actor_ids`, `unassign_actor_everywhere` over `<drama>/casting.md` | **Do NOT extend casting** — bgm references live in `bgm.md`, not casting.md. Put the scanner on `BgmPool` (or a new `BgmReferenceReader`) walking `ai_videos/<drama>/episodes/ep*/bgm.md`. Mirror the iterate-skip-`_`-dirs / parse-table / match-`bgm_NNNN` shape. |

### UI (mirror ActorGrid + VoiceGrid's audio)

- `api.ts`: add `listBgm`, `previewBgmPrompts`, `generateBgm`, `createBgmPrompts`, `deleteBgm`,
  `getBgmAssignments`; `BgmInfo` interface (id, `audio_path`, mtime, attrs, `is_assigned?`,
  `pending_import?`). Reuse `mediaUrl()` for mp3 — no new helper.
- `BgmGrid.tsx` (mirror `ActorGrid.tsx`): paginated grid (PAGE_SIZE=50), cross-page select
  Set, bulk delete loop, category **filter** dropdowns (genre/mood/tempo + 分配状态 +
  音频状态 mirroring 图片状态). Per tile, replace `<img>` with an **`<audio controls
  src={mediaUrl(audio_path, mtime)}>`** player (VoiceGrid uses `new Audio(mediaUrl(path))`
  with play/pause toggle — either pattern works; `<audio>` is simplest). Pending (no-mp3)
  tiles show a 📝 placeholder like actor's pending tiles.
- Wire `BgmGrid` into the same view host that mounts `ActorGrid` (e.g. an `ActorView`/route
  sibling — `BgmView.tsx`).

## 3. Implications for the spec — exact `bgm__*` files to create

Backend (DDD, mirroring actor 1:1):
1. `libs/domain/value_objects/bgm__valueobject.py` — `BgmAttrs` + BGM enums + `validate_bgm_id`/`validate_batch_count`/`validate_duration`.
2. `libs/domain/errors/bgm__error.py` — `Bgm*Error` family + `Musicgen{Failed,Missing}Error`.
3. `libs/domain/repositories/bgm__repository.py` — `BgmRepository` Protocol.
4. `libs/infrastructure/writers/bgm__writer.py` — `BgmPool` + `BgmInfo`/`GenerateResult`; id-alloc, sidecar, list, delete, reaper, `generate_batch` (musicgen subprocess), `create_prompts_batch`, and the `bgm.md` reverse-lookup scanner (`find_assignments_for_bgm` / `assigned_bgm_ids`).
5. (optional) `libs/infrastructure/writers/bgm__prompt.py` — musicgen prompt assembly.
6. `libs/application/dtos/bgm__dto.py`, `mappers/bgm__mapper.py`, `queries/bgm__query.py`, `commands/bgm__command.py`.
7. `apps/api/routes/bgm__route.py` + register in `routes/__init__.py`; add error rows + eager-mkdir in `app_factory.py`; add `bgm_pool`/`bgm_command`/`bgm_query` + musicgen client wiring in `container.py`.
8. `tools/musicgen_gen.py` — the CLI the writer subprocesses (analogue of the Kling client; outputs `bgm_NNNN.mp3`). **Does not exist yet** (see §4).

Disk contract: `ai_videos/_bgm/bgm_NNNN/{bgm_NNNN.mp3, bgm_NNNN.md}`; soft-delete to
`ai_videos/_deleted/_bgm/`; id regex `^bgm_\d{4,}$`; import tag `id{NNNN}` (no f/b split —
BGM has one artifact, so a single-letter discriminator is unnecessary).

Frontend: `api.ts` additions, `components/BgmGrid.tsx`, `components/BgmView.tsx`, route wiring.

## 4. Open questions

1. **`bgm.md` schema is undefined.** No `bgm.md` exists in the repo today and no tool emits
   one. The spec must define the per-episode `bgm.md` format (table vs `bgm_NNNN` reference
   lines) so the reverse-lookup scanner has a parse contract. Confirm location:
   `ai_videos/<drama>/episodes/ep*/bgm.md` (novel) and a flat `<drama>/bgm.md` (short)?
2. **`tools/musicgen_gen.py` does not exist.** No `musicgen*` file anywhere in the repo. The
   spec must specify its CLI contract (args: prompt/genre/mood/duration/seed/out_path; exit
   codes; mp3 output path) — the writer's subprocess call depends on it. Is it a local
   MusicGen model invocation, or an HTTP wrapper like Kling? Confirm with the user.
3. **Does BGM need a `generate-diverse` / archetype system?** Actor has a 10-archetype diverse
   generator + huge variance pools. BGM probably wants a much simpler prompt model
   (genre×mood×tempo). Recommend omitting `generate_diverse` unless the user asks.
4. **`create-prompts` (prompt-only) for BGM** — keep it? It is useful if musicgen is run
   externally and the mp3 imported back (mirror `DownloadsImporter` routing by `id{NNNN}`
   tag). Confirm whether BGM has an external-generation workflow analogous to actor's
   Kling-paste flow, or whether `generate` (subprocess) is always in-process.
5. **Reverse-lookup home.** Actor reuses the shared `Casting` singleton. BGM references live
   in `bgm.md` (not casting.md), so the scanner should live on `BgmPool`/a `BgmReferenceReader`,
   not on `Casting`. Confirm this separation is acceptable (it keeps casting.md actor/voice-only).
