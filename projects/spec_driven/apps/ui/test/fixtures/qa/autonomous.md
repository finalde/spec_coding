# Interview — fixture-autonomous

## Round 1 (autonomous, judgment-call answers)

### Category: functional-scope

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A *(judgment call — chose "all discovered" because the workflow's artifacts are pipeline-generated)*: All discovered. Backend walks `specs/{type}/{name}/` for every type+name pair on disk.

**Q:** Which file types under the exposed tree are openable in the main pane?
- A *(judgment call — chose "markdown + YAML/JSON + JSONL + plain text" because the workflow's artifacts are exclusively text)*: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`.

### Category: ux-interaction

**Q:** Autonomous-mode toggle persistence?
- A *(judgment call — chose "localStorage, per-tab synced via storage events, default off" because accidental autonomous runs should not be the path of least resistance)*: persisted under `spec_driven.autonomous_mode.v1`. Default is interactive.

### Category: edge-cases

**Q:** Behavior on a file >1 MB read attempt?
- A *(judgment call — chose "413 with `kind: too_large`" per OWASP File Upload Cheat Sheet guidance)*: applies to both `GET /api/file` and `PUT /api/file`.
