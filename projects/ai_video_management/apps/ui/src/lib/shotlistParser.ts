/** Parse shotlist.md to extract shot rows for navigation (FR-55..FR-58).
 *
 * Shotlist column 1 must contain the shot id (per `wukong_juexing/shotlist.md`
 * precedent + `agent_refs/project/ai_video.md` rule 4 implicit convention).
 */

const SHOT_ROW_RE = /^\|\s*`?(shot\d+)`?\s*\|/;

export interface ShotRow {
  shotSlug: string;
  shotNumber: number;
}

export function parseShotRows(content: string): ShotRow[] {
  const rows: ShotRow[] = [];
  const seen = new Set<string>();
  for (const line of content.split(/\r?\n/)) {
    const m = SHOT_ROW_RE.exec(line);
    if (!m) continue;
    const slug = m[1];
    if (seen.has(slug)) continue;
    seen.add(slug);
    const numMatch = /\d+/.exec(slug);
    if (!numMatch) continue;
    rows.push({ shotSlug: slug, shotNumber: parseInt(numMatch[0], 10) });
  }
  return rows;
}

/** Project-name from shotlist path: ai_videos/{name}/shotlist.md */
export function projectFromShotlistPath(shotlistPath: string): string | null {
  const parts = shotlistPath.split("/");
  if (parts[0] !== "ai_videos" || parts.length < 3 || parts[parts.length - 1] !== "shotlist.md") {
    return null;
  }
  return parts[1];
}
