# Interview — fixture-interactive

## Round 1

### Category: functional-scope

**Q:** Section 2 ("Projects") — which projects appear in the tree?
- A: All discovered. Backend walks `specs/{type}/{name}/` for every type+name pair on disk.

**Q:** Which file types are openable?
- A: `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`. Image extensions render as a placeholder.

### Category: ux-interaction

**Q:** Markdown link resolution — relative vs absolute?
- A: Relative links resolve against the current file's directory; absolute http(s) opens in a new tab; broken links render as muted spans.

## Round 2

### Category: edge-cases

**Q:** Behavior on a file >1 MB read attempt?
- A: 413 with `kind: too_large`.
