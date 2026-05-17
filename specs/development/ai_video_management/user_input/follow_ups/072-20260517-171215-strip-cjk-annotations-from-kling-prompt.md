# Follow-up draft 072 — 2026-05-17

Bugfix to follow-up 071: actor generation returns "失败 6 张" / each slot with `500 HTTP 500`. The root cause is that follow-up 071 baked Chinese-aesthetic annotations into the new variance-pool entries (e.g. ` (高挺鼻梁)`, ` (小眼睛)`, ` (蒜头鼻)`, ` (大眼睛)`, ` (圆眼睛)`, ` (泪眼)`, ` (驼峰鼻)`). These were intended as **in-source documentation** so a dev browsing the source could see which Chinese descriptor each English entry maps to. But the pool entries are concatenated directly into the prompt that goes on the wire to Kling's text-to-image API, and **Kling rejects the prompt** (observed empirically — every slot fails with `kling submit: code=1101 …` surfaced upstream as HTTP 500 per slot).

## Symptom

UI: "🧑‍🎨 演员生成失败 6 张 — 查看原因" with per-slot rows `#1: 500 HTTP 500`, `#2: 500 HTTP 500`, … `#6: 500 HTTP 500`.

Backend: the bare `except Exception as exc:` in `apps/api/routes/actor__route.py` mapped Kling's per-slot HTTP failure to the catchall slot-error message format; the actual HTTP-200 batch response carried `result.errors = [{"requested_id": "actor_NNNN", "message": "http_failed: 500 …"}, ...]` from `actor__writer.generate_batch`.

## Root cause

Each follow-up 071 expansion entry was written like:
```python
"high-bridged dignified nose with elegant noble prominence (高挺鼻梁)",
"petite narrow downturned eyes with quiet inscrutable depth (小眼睛)",
```

`_variance_for` concatenates these via `", ".join(parts)` into `Variance.features_text`, which gets composed into the final Kling prompt by `_build_face_prompt` / `_build_body_prompt`. Kling-v1 silently rejects (HTTP 500) prompts containing the CJK-in-parens chunks. Pure-ASCII English prompts work fine, so the Chinese in parens is the breaking content.

## Fix

Add a module-level regex `_CJK_PARENS_RE = re.compile(r"\s*\([^)]*[一-鿿][^)]*\)")` (matches an optional leading space + `(...)` whose contents include at least one CJK Unified Ideograph in U+4E00–U+9FFF). Apply it once at the end of `_variance_for` when assembling `features_text`:

```python
features_text = _CJK_PARENS_RE.sub("", ", ".join(parts))
```

The Chinese annotations remain in the source — a dev reading `actor__writer.py` still sees ` (高挺鼻梁)` next to "high-bridged dignified nose…" as the documentation note. The wire content sent to Kling becomes pure ASCII.

## Smoke proof

```python
sample = "high-bridged dignified nose ... (高挺鼻梁), petite narrow downturned eyes ... (小眼睛)"
_CJK_PARENS_RE.sub("", sample)
# → "high-bridged dignified nose ..., petite narrow downturned eyes ..."

# Across 6 seeds × 4 archetype branches (3 named + None for uniform),
# CJK-in-features_text count = 0/24.
```

## Out of scope

- Switching to bare-English pool entries (loses the source documentation; the regex strip is the cheaper compromise).
- Adding Kling-API-input validation upstream (e.g., reject CJK at prompt-build time with a domain error). Not worth it for one regex.
- Refactoring `actor__writer.py` further (already at ~2200 lines; the SRP/file-size flag from 068+065 still stands as deferred cleanup).
- HTTP routes + JSON shapes — no change; existing slot-failure accounting in `result.errors` is preserved (a Kling 5xx still surfaces per-slot if it happens for some other reason).

## Acceptance trigger

- `_variance_for(seed, gender, archetype=...)` produces `features_text` containing zero CJK characters for any combination of `seed × gender × archetype`.
- A re-run of "generate 6 actors" against the live Kling API completes without per-slot HTTP 500 (the user verifies in the UI).
- Pytest baseline preserved: 18 pass / 5 pre-existing wukong fixture failures.
