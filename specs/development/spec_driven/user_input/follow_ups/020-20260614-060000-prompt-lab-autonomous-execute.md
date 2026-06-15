---
target_stage: 6
target_artifacts:
  - final_specs/spec.md
  - projects/spec_driven/libs/infrastructure/prompt_lab__executor.py
  - projects/spec_driven/apps/ui/src/components/PromptLabPage.tsx
severity: high
---

# Follow-up draft 020 — 2026-06-14

Make each Prompt Lab item its own workspace folder, and add an **Execute** button that spawns a fully-autonomous headless `claude` session which runs the item's prompt, auto-decides anything it's asked, logs those decisions, and surfaces status / decisions / output / generated files on the UI.

## Abstracted instruction

1. **Per-item workspace folders.** Each item is now `prompt_lab/{category}/{task}/` containing `prompt.md` (the instruction). Execution artifacts live beside it: `status.json`, `output.txt`, and a `workspace/` (the session's cwd, where it builds and writes `decisions.jsonl`). The overview parser walks `{category}/*/prompt.md`; create makes `{cat}/{slug}/prompt.md`; delete removes the whole item folder.

2. **Execute → autonomous headless session.** A ▶ Execute button on the item spawns `claude --print --permission-mode bypassPermissions` as a background process with cwd = the item's `workspace/`, fed (via stdin) the item's copy-paste prompt prefixed with a `# EXECUTION MODE: AUTONOMOUS` header + an autonomy contract: never wait for input; for any choice answer with the most sensible default; log every decision as one JSON line (`{ts, question, decision, why}`) to `decisions.jsonl`; build to completion. Fully autonomous — no human input.

3. **Run portal.** The decisions made, live session output, run status (running/succeeded/failed/stopped), and the list of generated files are all visible on the Prompt Lab UI (polled while running). A ⏹ Stop button kills an in-progress run.

## Backend shape

- `POST /api/prompt-lab/execute {path}` — start a run (409 if one is already running; 503 if the `claude` CLI isn't available).
- `GET /api/prompt-lab/run?path=...` — `{state, run_id, started_at, ended_at, exit_code, output, decisions[], files[]}`.
- `POST /api/prompt-lab/stop {path}` — best-effort kill.
- New `PromptLabExecutor` (infrastructure) owns spawning + run state; pid-liveness reconciles stale "running" status. Scoped strictly to `prompt_lab/` paths.

## Notes / risk

- This lets the webapp launch a real coding agent with bypassed permissions inside the item's workspace. Acceptable because it's confined to that folder and the user explicitly opted in. It depends on a locally-installed, authenticated `claude` CLI (verified present).
- Verified end-to-end: a trivial item ran autonomously, logged a decision, produced the expected file, and reported `succeeded` (exit 0).
