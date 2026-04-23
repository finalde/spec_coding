# Claude Components

## Naming Convention

- `common__...`
  - Reusable across many domains
  - Examples: project scaffolding, skill authoring, meetings, YouTube metadata
- `video_generation__...`
  - Specific to AI video planning, prompt packaging, continuity, or Seedance

Use `__` (double underscore) as the delimiter between prefix and name. Do not add new repo-owned skills without one of these prefixes.

## Current Canonical Components

### Common Skills

- `common__claude-builder`
- `common__skill-creator`
- `common__project-builder`
- `common__meeting-assistant`
- `common__youtube-info`

### Video Generation Skills

- `video_generation__topic-scout` — single-video topic discovery (legacy, used by ad-hoc Shorts work)
- `video_generation__reference-scout` — series-seeding trend + gap侦察 (stage 1 of the 短剧 chain)
- `video_generation__preproduction` — locks the four series bibles + anchor registry (stage 2)
- `video_generation__serial-novelist` — writes one 短剧 episode (900–1200 字) + 4-column beat sheet (stage 3)
- `video_generation__storyboard-master` — expands an episode's beat sheet into a production storyboard (stage 4)
- `video_generation__seedance-packager` — emits per-clip Seedance 2.0 prompts + snapshot prompts + manifest (stage 5)
- `video_generation__clip-stitcher` — FFmpeg / CapCut stitch + 中文 硬烧字幕 + 多平台导出 (stage 7)
- `video_generation__series-factory` — composite orchestrator for the full 8-stage pipeline

### Video Generation Agents

- `video_generation__continuity-director` — fail-closed continuity gate (stage 6); refuses on verbatim-substring violations
- `video_generation__youtube-researcher` — legacy channel-research subagent

## Consolidation Notes

The video workflow was intentionally consolidated to reduce overlap:

- `video_generation__reference-scout` replaces the old split between trend-gap scouting and AI Shorts scouting.
- `video_generation__preproduction` replaces the old split between episode architecture and visual-bible locking, and now locks a **four-book** bible set (character / scene / style / voice) + an anchor registry for verbatim-substring enforcement.
- `video_generation__serial-novelist` is the single 中文短篇小说 writer for this chain; it enforces a rolling 3–5 episode planning cap and emits the packager-ready 4-column beat sheet.
- `video_generation__continuity-director` is a fail-closed agent; if it finds any anchor that is not present byte-for-byte in a downstream prompt, `clip-stitcher` refuses to run.
- `video_generation__clip-stitcher` replaces `assembly-planner`: the new skill actually runs ffmpeg + emits a CapCut handoff bundle rather than just planning assembly.
- `video_generation__series-factory` is the end-to-end composite orchestrator.

## Migration Map

| Old name | New name |
| --- | --- |
| `claude-builder` | `common__claude-builder` |
| `skill-creator` | `common__skill-creator` |
| `project-builder` | `common__project-builder` |
| `meeting-assistant` / `meeting_assistant` | `common__meeting-assistant` |
| `youtube-info` | `common__youtube-info` |
| `ai-shorts-scout` | `video_generation__reference-scout` |
| `trend-gap-scout` | `video_generation__reference-scout` |
| `episode-architect` | `video_generation__preproduction` |
| `visual-bible-locker` | `video_generation__preproduction` |
| `storyboard-master` | `video_generation__storyboard-master` |
| `seedance-packager` | `video_generation__seedance-packager` |
| `prompt-linter` | merged into `video_generation__continuity-director` |
| `assembly-planner` | replaced by `video_generation__clip-stitcher` |
| `youtube-researcher` | `video_generation__youtube-researcher` |
| `continuity-director` | `video_generation__continuity-director` |
| (new — 短剧 writer) | `video_generation__serial-novelist` |
| (new — 成片拼合) | `video_generation__clip-stitcher` |
| (new — 全链编排) | `video_generation__series-factory` |

## Canonical 短剧 series pipeline

```
1. video_generation__reference-scout   (侦察)
2. video_generation__preproduction     (锁圣经)
3. video_generation__serial-novelist   (写集)
4. video_generation__storyboard-master (分镜)
5. video_generation__seedance-packager (打包 prompt)
6. video_generation__continuity-director  (闸门 · agent · fail-closed)
7. 人工 · Seedance 跑视频 + TTS 渲染 + BGM 选曲
8. video_generation__clip-stitcher     (拼片 + 导出)
```

`video_generation__series-factory` runs stages 1–6 and 8 end-to-end, pausing at stage 7 for human-in-the-loop media generation.
