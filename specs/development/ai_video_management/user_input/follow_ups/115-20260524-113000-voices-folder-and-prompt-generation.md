---
target_stage: 4
target_artifacts:
  - final_specs/spec.md
  - validation/strategy.md
  - validation/acceptance_criteria.md
  - validation/bdd_scenarios.md
  - validation/security.md
severity: medium
---

# Follow-up draft 115 — 2026-05-24

Add a `_voices/` voice-profile asset pool parallel to `_actors/`. Each voice profile is a generated Chinese-language 配音 prompt the user copies into an external AI voice model (ElevenLabs / MiniMax / CosyVoice / etc.). The webapp itself does **NOT** call any voice-generation API — it composes prompts locally and stores user-supplied audio samples.

## Original wording

> under ai_video_management, 除了_actors之外, 幫我生成一個配音folder，裏面我會需要生成不同的配音聲音，比如陰柔太監音，雄壯將軍音，柔美宮主音等等，類似生成actor一樣的機制，只是這次不是直接給kling api，而是給我prompt，我自己交給別的ai model生成聲音

## Abstracted intent

Dubbing (配音) is the missing leg of the character-bible triad: face → body → voice. The actor pool (FR-9f / follow-ups 014–112) gives the visual identity; this follow-up adds the auditory identity as a sibling asset pool.

The key distinction from the actor pipeline: voice generation is **purely local text composition** — no outbound HTTP, no provider key management, no 429 retry, no rate limiting. The webapp's contribution is (a) the generated Chinese prompt text + organized library, and (b) optional audio sample storage so the user can preview voices in-grid after rendering them externally. The "AI model" call is the user's manual paste-and-render step, outside the webapp.

### Concrete deltas

1. **Folder:** `ai_videos/_voices/voice_NNNN/` parallel to `ai_videos/_actors/actor_NNNN/`. Same `_xxx` underscore-prefix convention so the existing single-leaf-collapsed sidebar pattern (follow-up 036) applies identically.

2. **Per-profile contents:**
   - `voice_NNNN.md` — canonical voice profile (Chinese content per ai_video.md rule 1): metadata table + the generated prompt block(s).
   - Optional `voice_NNNN.mp3` / `voice_NNNN.wav` audio sample, dropped in by the user after they render externally. When present, the grid tile gets a play affordance and the read-view embeds `<audio controls>`.

3. **Metadata fields** (in the .md table, mirroring actor's table style):
   - `gender` (male / female / neutral)
   - `age_impression` (child / teen / young_adult / middle_aged / elderly)
   - `archetype` — the load-bearing field. Initial enum covers the user's three named examples plus the obvious xianxia / palace set: `effeminate_eunuch` (陰柔太監音), `mighty_general` (雄壯將軍音), `gentle_palace_mistress` (柔美宮主音), `aged_master` (蒼老掌門音), `young_jianghu_swordsman` (年輕江湖俠音), `noble_emperor` (威嚴帝王音), `cold_assassin` (冷峻刺客音), `coquettish_concubine` (嬌媚妃嬪音), `wise_elder_monk` (慈悲高僧音), `cunning_advisor` (陰險謀士音). Enum is extensible — exact final set is a stage-4 detail.
   - `tone` (free-text Chinese: e.g. 沉穩 / 尖利 / 渾厚 / 沙啞)
   - `pace` (slow / medium / fast)
   - `pitch_register` (low / mid / high)
   - `signature_inflection` (free-text Chinese: e.g. 喉音偏重 / 鼻音重 / 句尾上揚)
   - `emotion_default` (calm / authoritative / playful / menacing / mournful / etc.)
   - `notes`
   - `seed` (for local composition reproducibility — same RNG pattern as actor's seed field)
   - `audio_sample` (filename if user has dropped one in; empty otherwise)
   - `provider_hint` (optional free-text line — e.g. "建議用 MiniMax 长文本朗读，温度 0.6" — NOT a structured field, just a copyable hint)

4. **Prompt content style:** purely natural-language Chinese description — voice timbre, pitch register, breath quality, age impression, gender, signature inflections, typical use cases. Written so the user can paste it byte-identically into any voice model. NO model-specific JSON, sigils, or instruct syntax.

5. **Generation mechanism:** mirrors actor generation in UX but with a different backend. Reuse the existing worker-pool / preview-confirm / progress modal (follow-ups 027 / 059 / 062) and the diverse-mode + archetype-bias variance machinery (follow-ups 053 / 071 / 074 / 082 / 083). The "provider" is internal text composition, not Kling — so the generator dropdown (follow-up 063) gains a voice option, but no provider sub-picker is shown for it.

6. **Webapp UX surface** (mirrors actor — same shapes, same affordances):
   - Sidebar: `_voices/` leaf, single-leaf-collapsed per follow-up 036.
   - Voice grid page parallel to actor grid (follow-ups 028 / 030 / 032 / 086 / 094): page-size selector, archetype filter, gender filter, age filter, bulk delete, bulk assign-to-character.
   - Generator dropdown (follow-up 063) gains 配音 as a Chinese-labeled option alongside 演員.
   - Diverse mode for voices spreads across the archetype enum the same way actor diverse mode spreads across `look_enum` (follow-ups 053 / 064).
   - Read-view for `voice_NNNN.md` uses the styled markdown view (follow-up 034). When `audio_sample` is set, the read-view embeds `<audio controls src="...">` above the prompt block.
   - Voice-to-character assignment mirrors actor cast pattern (follow-ups 014 / 043 / 050). Default: copy the voice descriptor (and audio sample, if present) into `characters/{name}/cast/` subfolder, same as how actor faces are copied today. Exec is free to pick the simpler path (id reference only) if cast-folder copy proves redundant — note the divergence in the spec if so.

7. **Endpoints** (mirror actor endpoints; no Kling-equivalent external endpoint):
   - `POST /api/voices/generate` — single-voice generation (local composition).
   - `POST /api/voices/generate-diverse` — bulk diverse-mode generation.
   - `POST /api/voices/preview` — render the prompt without persisting (powers the confirm modal).
   - `DELETE /api/voices/{id}` — soft-delete to a `_voices/deleted/` folder (mirrors actor delete-to-deleted per follow-up 023).
   - `POST /api/casting/assign-voice` + `DELETE /api/casting/assign-voice` — mirrors `POST /api/casting/assign` (FR-9g) for voice-to-character binding.
   - `POST /api/voices/{id}/audio` — multipart upload of `.mp3` / `.wav` sample. **This IS a new write surface** beyond `PUT /api/file`; it must enforce the same EXPOSED_TREE sandbox, mtime concurrency, and extension allowlist as `PUT /api/file`. Audio extensions added to allowlist: `.mp3`, `.wav`, `.m4a` (read-only display for any other audio format the user drops in by hand).

8. **Application / Domain layer parallel** (DDD + CQRS per development.md §1, follow-ups 039 / 051 / 056 / 060 / 061 / 065):
   - `libs/application/commands/voice__command.py` — `VoiceCommand` class with `.generate(...)`, `.generate_diverse(...)`, `.delete(...)`, `.upload_audio(...)`.
   - `libs/application/queries/voice__query.py` — `VoiceQuery` class.
   - `libs/application/dtos/voice__dto.py` — voice Qdtos + Cdtos.
   - `libs/domain/entities/voice__entity.py` — voice profile aggregate (if mutation is non-trivial; otherwise voice may be a value object — exec choice).
   - `libs/domain/value_objects/voice_archetype.py` — enum (mirror of actor's archetype / look_enum sync per follow-up 067).
   - `libs/domain/repositories/voice__repository.py` — protocol.
   - `libs/infrastructure/writers/voice__writer.py` — file persistence.
   - `libs/infrastructure/writers/voice__chinese_prompt.py` — composition logic (mirror of `actor__chinese_prompt.py`).
   - `libs/infrastructure/daos/voice__dao.py` — DAO dataclass.
   - `libs/infrastructure/errors/voice__error.py` — exception classes (SRP per follow-up 068).
   - `apps/api/routes/voice__route.py` — own `APIRouter()`, combined into top-level router (follow-up 065).

9. **No external-HTTP machinery for voices.** All of these are explicitly NOT applicable to the voice pipeline because there is no outbound call:
   - Kling provider / env file (follow-ups 024 / 025).
   - Provider rate-limit retry (follow-ups 018 / 112).
   - Concurrency throttling for external HTTP (follow-up 027).
   - Reap mtime threshold for concurrent races (follow-up 073) — voice writes are sub-millisecond local I/O; no race window.

10. **Audio sample handling:**
    - Drop-in via UI: drag-drop or browse-to-upload in the read-view; multipart POST to `/api/voices/{id}/audio`.
    - Drop-in via filesystem: user copies `voice_NNNN.mp3` into the folder by hand; webapp picks it up on next tree refresh, no DB to sync.
    - No automated retrieval. No TTS in-browser. No waveform visualization. v1 audio support is `<audio controls>` playback only.

## Why

Two reasons:

1. **Completes the character-bible triad.** Today the character cast pipeline binds faces (actor) and bodies to characters but has no voice slot. Authors of xianxia / palace shorts need a stable voice identity per character just as much as a stable face — and the user has explicit named examples (陰柔太監音 / 雄壯將軍音 / 柔美宮主音) that don't fit into a generic "character.md" free-text field.

2. **Sidesteps all the provider complexity** that dominated actor follow-ups 018 – 112. Because voice synthesis happens externally, the webapp's surface area for this feature is small: a prompt composer + a file library + an audio playback affordance. The grid / generator / casting UX is already built — we reuse it for voices with a different backend.

## Out of scope

- **No external AI voice API calls.** The webapp never hits ElevenLabs / MiniMax / CosyVoice / OpenAI TTS. Voice synthesis is the user's manual step.
- **No real-time voice cloning, no waveform visualization, no in-browser TTS preview.** v1 audio playback is just `<audio controls>` when a sample file exists.
- **No auto-retrieval of audio samples** from any external service. Files arrive via UI upload or manual filesystem copy.
- **No structured per-model prompt variants.** Prompt is one generic Chinese description; the optional `provider_hint` line is free-text only.
- **The exact archetype enum is a stage-4 detail.** The 10 archetypes listed above are starter examples — exec / spec may extend / rename based on the genres the user actively produces.
- **Voice-to-character cast-folder copy vs. id-reference is a v1 detail.** Pick the simpler path during exec; record divergence in spec if it diverges from the actor cast pattern.
- **Provider-key management UI, env file format for voice providers** — not applicable, no providers.
