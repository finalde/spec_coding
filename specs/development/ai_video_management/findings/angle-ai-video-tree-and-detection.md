# Findings — angle: ai-video-tree-and-detection

Run: ai_video_management-20260505-002710
Researcher: 04 (parent-direct fan-out)
Sources cited: actual files at the cited paths (no web fetch needed; entirely local-evidence angle).

## 1. What this angle covers

This angle locks two adjacent contracts that the rest of the webapp depends on:

1. **EXPOSED_TREE walk** — the canonical sandbox of paths the backend will surface through `GET /api/tree` and gate every read/write on. Its shape determines what `Sidebar.tsx` can render, what `SafeResolver` will admit, and what `RegenPromptBuilder` can inline. Wrong shape here cascades into either security holes (admitting paths outside the sandbox) or empty-sidebar bugs.
2. **Sub_type detection** — the regex / parser that decides whether `ai_videos/{name}/` is a `novel` (multi-episode, `episodes/epNN/` layout) or `short` (flat layout). This single bit gates: (a) the sidebar badge ("剧" vs "短"), (b) whether the regen-prompt scope toggle exposes `episode N` or force-defaults to `project`, (c) whether `ShotPairView` looks under `episodes/epNN/prompts/` or flat `prompts/`.

Both contracts are designed to be **port-faithful to `spec_driven`** wherever possible (re-using `ExposedTree`, `SafeResolver`, `TreeWalker`'s shape) and **diverge only where ai_video output structure forces it** (image leaves, two parallel artifact roots, sub_type metadata).

## 2. EXPOSED_TREE membership (concrete glob list)

Membership is the union of these globs, evaluated against the repo root. Excluded dirs (`node_modules`, `.git`, `.audit`, `__pycache__`, `.pytest_cache`, `dist`, `build`, `.vite`) are pruned mid-walk per `spec_driven/backend/libs/exposed_tree.py:18-20`.

| Surface | Glob | Notes |
|---|---|---|
| ai_video output tree | `ai_videos/**/*.{md,json,jsonl,yaml,yml,txt,png,jpg}` | All extension allowlist hits inside any `ai_videos/{name}/`. Includes `ref_images/*.png`. |
| ai_video spec trail | `specs/ai_video/**/*.{md,json,jsonl,yaml,yml,txt}` | Spec-pipeline artifacts under the `ai_video` task type only; does **not** expose `specs/development/`, `specs/research/`, etc. |
| Repo-root context | `CLAUDE.md` | Single root file; no glob. |
| Skill + playbooks | `.claude/skills/agent_team/SKILL.md`, `.claude/skills/agent_team/playbooks/*.md` | Match the `spec_driven` semantics at `exposed_tree.py:35-48` (any `SKILL.md` recursive + any `playbooks/*.md` non-recursive). Filter: `name == "SKILL.md"` OR `parent.name == "playbooks" and suffix == ".md"`. |
| Agent refs | `.claude/agent_refs/**/*.md` | All four scopes — `interview/`, `research/`, `validation/`, `project/` — and within each both `general.md` and `<task_type>.md`. Per `revised_prompt.md` constraint #12 the recursive glob auto-picks up new `<task_type>.md` files (e.g., a future `agent_refs/research/ai_video.md`) without code changes. |

Backend membership predicate (port of `is_inside`, `exposed_tree.py:65-92`):

```
first segment == "CLAUDE.md"          -> admit
first segment == ".claude":
    second segment in {"skills", "agent_refs"} -> admit (deeper checked by leaf predicate)
    else                                       -> reject
first segment == "ai_videos":         -> admit unless any segment ∈ EXCLUDED_DIRS
first segment == "specs":
    second segment == "ai_video"     -> admit unless any segment ∈ EXCLUDED_DIRS
    else                             -> reject
otherwise                            -> reject
```

Note the **scope tightening** vs `spec_driven`: the latter admits `specs/**` and `projects/**` whole; ai_video_management admits `specs/ai_video/**` only and **does not admit `projects/`** at all. (Reason: this webapp manages ai_video artifacts; `spec_driven` already covers `specs/development/` + `projects/spec_driven/` itself.) `ai_videos/` replaces the role `projects/` plays in `spec_driven`.

Extension allowlist is the same set as `spec_driven` plus images already accepted there (`exposed_tree.py:13-15`): `.md`, `.json`, `.yaml`, `.yml`, `.jsonl`, `.txt`, `.png`, `.jpg`. SVG remains excluded per `revised_prompt.md` hard constraint #4.

## 3. TreeNode interface (paste-ready)

`spec_driven`'s `tree_walker.py:14-24, 132-139` returns plain `dict[str, Any]` with fields `type`, `name`, `path`, `children` (and the legacy `path: ""` on `section`/root nodes). For ai_video_management the contract grows by **one optional field** and **one new leaf type** (`image`), keeping every `spec_driven` consumer working.

### Python (`backend/libs/tree.py`)

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

NodeType = Literal["section", "directory", "file", "image"]
SubType = Literal["novel", "short"]

@dataclass(frozen=True)
class ProjectMeta:
    sub_type: SubType | None      # None when qa.md missing or unparseable
    shot_count: int | None        # short: from shotlist.md row count; novel: None
    episode_count: int | None     # novel: from episodes/ subdir count; short: None

@dataclass(frozen=True)
class TreeNode:
    type: NodeType
    name: str
    path: str                     # repo-relative POSIX, "" for synthetic sections
    children: tuple["TreeNode", ...] = field(default_factory=tuple)
    project_meta: ProjectMeta | None = None  # populated only on the ai_videos/{name}/ directory node
```

Serialised JSON (single payload `GET /api/tree` returns):

```json
{ "type": "section", "name": "root", "path": "",
  "children": [
    { "type": "section", "name": "AI Videos", "path": "", "children": [
        { "type": "directory", "name": "wukong_juexing",
          "path": "ai_videos/wukong_juexing",
          "project_meta": { "sub_type": "short", "shot_count": 5, "episode_count": null },
          "children": [...] }
    ]},
    { "type": "section", "name": "Specs (ai_video)", "path": "", "children": [...] },
    { "type": "section", "name": "Context", "path": "", "children": [...] }
  ]}
```

### TypeScript (`frontend/src/types.ts`)

```ts
export type NodeType = "section" | "directory" | "file" | "image";
export type SubType = "novel" | "short";

export interface ProjectMeta {
  sub_type: SubType | null;
  shot_count: number | null;
  episode_count: number | null;
}

export interface TreeNode {
  type: NodeType;
  name: string;
  path: string;
  children?: TreeNode[];
  project_meta?: ProjectMeta;
}
```

`type: "image"` is new — it lets `Sidebar.tsx` render a tiny camera glyph next to `.png/.jpg` leaves without each component re-checking the suffix, and lets `Reader` route to `ImageRefView` directly. Files of other allowlist extensions stay `type: "file"`.

## 4. Sub_type detection algorithm

Triggered exactly once per `ai_videos/{name}/` during `TreeWalker.build()`; result memoised on the node as `project_meta.sub_type`. The webapp does **not** re-detect on every `GET /api/file` — that would defeat the badge cache.

```python
import re
SUBTYPE_RE = re.compile(
    r"^\|\s*`?sub_type`?\s*\|\s*`?(novel|short)`?\s*\|",
    re.MULTILINE | re.IGNORECASE,
)

def detect_subtype(repo_root: Path, project_name: str) -> SubType | None:
    qa = repo_root / "specs" / "ai_video" / project_name / "interview" / "qa.md"
    if not qa.is_file():
        return None
    try:
        text = qa.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = SUBTYPE_RE.search(text)
    if m is None:
        return None
    return m.group(1).lower()  # type: ignore[return-value]
```

Regex anchored to the `qa.md` "Settled facts" markdown table convention (verified by `specs/ai_video/wukong_juexing/interview/qa.md:10` which reads `` | `sub_type` | `short` | User: ... ||``). The pattern admits: backticked or bare `sub_type`, backticked or bare value, any case for safety.

**Edge cases:**

| Case | Behaviour |
|---|---|
| `qa.md` missing entirely (project never reached Stage 2) | `sub_type=None`. Sidebar renders project name without a badge. Regen-scope toggle force-defaults to `scope=project`. |
| `qa.md` present, no `sub_type` row | `sub_type=None`. Same fallback as above. Logged once per tree build at WARN level. |
| `qa.md` present with `sub_type` value not in `{novel, short}` (e.g., a typo `serial`) | `sub_type=None`. Regex requires exact match; an audit warning is emitted. We deliberately do **not** invent a third value — the contract in `agent_refs/interview/ai_video.md:1-16` is a closed enum. |
| `qa.md` lists `sub_type` outside the settled-facts table (e.g., narrative prose) | Not matched — anchor on `^|\s*`?sub_type` pipe-table syntax. Acceptable false negative; cured by editing `qa.md` to use the canonical table format. |
| Multiple `sub_type` rows | First match wins (`re.search`). Documented; rare. |

`shot_count` (short only) is computed by counting `^\|\s*shot\d+` rows inside `ai_videos/{name}/shotlist.md`; `episode_count` (novel only) by counting `episodes/ep*/` directories. Both are best-effort; a `None` value simply suppresses the count badge.

## 5. Cross-tree counterpart resolution

The "查看规格" affordance per Sidebar Q2 (`interview/qa.md:159-165`) maps the **project root**, not the per-file relative path:

```
viewing  ai_videos/wukong_juexing/prompts/shot02_kling.md
linkTo   specs/ai_video/wukong_juexing/                    (the project's spec root)
```

Reasons: (a) per-file mirroring would point at non-existent files (no `specs/ai_video/wukong_juexing/prompts/shot02_kling.md`); (b) the "why" question almost always resolves at the spec-pipeline level (revised_prompt → qa → spec → validation strategy), not inside a sibling artifact; (c) the spec pipeline has its own structure (`user_input/`, `interview/`, `findings/`, etc.) that doesn't mirror ai_video output structure (`prompts/`, `characters/`, etc.) — there is no meaningful per-file pairing to compute.

The link is rendered only when the counterpart `specs/ai_video/{name}/` directory exists (cheap `Path.is_dir()` check during tree build, returned as `project_meta.has_spec_counterpart: bool` if needed; v1 can keep this implicit by linking to the directory and letting the file viewer 404 fall back to the project page).

## 6. Sort + refresh semantics

**Sort.** Alphabetical with directories before files, mirroring `spec_driven/backend/libs/tree_walker.py:105`:
`sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))`. We intentionally do **not** invent a per-folder semantic order (README first, characters second, etc.) — the file naming convention from `agent_refs/project/ai_video.md:14-56` already produces a sensible alphabetical order in practice (`README.md`, `characters/`, `prompts/`, `publish.md`, `script.md`, `shotlist.md`, `style_guide.md` for shorts). A custom sort would diverge from `spec_driven`'s mental model and add a maintenance burden every time a new artifact name appears.

**Refresh.** Manual, mirroring `spec_driven/frontend/src/App.tsx:13-31`. The frontend keeps `tree` in `useState` and re-fetches via `fetchTree()` only when `refreshKey` changes — bumped by an explicit "刷新" button in the sidebar header (and on successful `PUT /api/file` so freshly-edited files don't fall out of view). No polling, no fs-watcher, no SSE — that pattern is consistent with the no-WebSocket scope rule (`revised_prompt.md` out-of-scope #4) and with `spec_driven`'s precedent. Side-effect: a file written by the user in their editor outside the webapp does not appear until the user clicks 刷新, which is acceptable for v1 single-user localhost.

## 7. Implications for the spec

- Stage 4 FR set MUST include: `FR-tree-membership` (the table in §2), `FR-tree-node-shape` (the dataclass + interface in §3), `FR-subtype-detection` (the regex + edge-case table in §4), `FR-cross-tree-link` (project-root mapping in §5), `FR-sidebar-refresh-manual` (button + auto-bump on PUT in §6), `FR-project-badges` (sub_type + counts in §3, gated on `project_meta != null`).
- Stage 5 validation: a Level-1 (boundary) test must POST `GET /api/tree` and assert exactly the three top-level sections in order; Level-2 (sandbox) tests must probe `specs/development/`, `projects/`, `.claude/skills/<other>/SKILL.md` and confirm 404s (proving the membership tightening); Level-3 (regression) tests must drop a malformed `qa.md` (no `sub_type` row) and assert `project_meta.sub_type == null` rather than crash.
- Stage 6 execution: the `tree.py` file under `backend/libs/` becomes the de-facto port of `spec_driven`'s `exposed_tree.py` + `tree_walker.py` collapsed into one module (the `revised_prompt.md` outline at lines 30-31 already names it `tree.py`). Worth keeping the two-class split (ExposedTree + TreeWalker) inside that file for parity.

## 8. Open questions surfaced

1. **Detection cost on cold start.** With ~60 ai_video projects (target scale per `agent_refs/interview/ai_video.md:34` novel default), tree build does 60 file reads of `qa.md` for sub_type detection. At ~5 KB each → ~300 KB read on every refresh. Acceptable for v1 localhost; a future cache (mtime-keyed in-process dict) is the obvious optimisation if it ever shows up.
2. **`type: "image"` leaf treatment.** Should the sidebar still show `.png` files as clickable leaves under arbitrary folders (e.g., a `.png` dropped into `style_guide/` for inspiration) or only under `characters/ref_images/`? Recommendation: show everywhere; let `ImageRefView` render. Defer to spec stage if pushback.
3. **`has_spec_counterpart` as explicit field vs implicit.** Currently §5 leaves it implicit (link to the project, let 404 fall back). If UX testing shows users get confused by a dead-end click, promote it to `project_meta.has_spec_counterpart: bool` and grey out the link. v1 default: implicit.
4. **`.claude/agent_refs/{research,validation}/ai_video.md` membership.** These don't exist today (the only `<task_type>=ai_video` ref outside `project/` is the interview one). The recursive glob still admits them for the day they're created — confirming this is the intended forward-compat behaviour, not a leak. (Confirmed against `revised_prompt.md` constraint #12: "Recursive globs auto-pick new subfolders.")
