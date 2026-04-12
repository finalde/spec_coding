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

- `video_generation__topic-scout`
- `video_generation__reference-scout`
- `video_generation__preproduction`
- `video_generation__storyboard-master`
- `video_generation__seedance-packager`
- `video_generation__assembly-planner`

### Video Generation Agents

- `video_generation__youtube-researcher`
- `video_generation__continuity-director`

## Consolidation Notes

The video workflow was intentionally consolidated to reduce overlap:

- `video_generation__reference-scout` replaces the old split between trend-gap scouting and AI Shorts scouting.
- `video_generation__preproduction` replaces the old split between episode architecture and visual-bible locking.
- `video_generation__continuity-director` absorbs prompt-lint style QA, so prompt review and continuity review happen in one place.

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
| `assembly-planner` | `video_generation__assembly-planner` |
| `youtube-researcher` | `video_generation__youtube-researcher` |
| `continuity-director` | `video_generation__continuity-director` |
