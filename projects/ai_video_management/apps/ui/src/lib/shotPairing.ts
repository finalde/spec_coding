/** Shot-pair detection for ShotPairView (FR-50, FR-51).
 *
 * Pattern (FR-51): `^(.+/prompts/)shot(\d+)_(kling|seedance)\.md$`. Given any matching path,
 * the partner is constructed by swapping `kling` ↔ `seedance`.
 */

const SHOT_PAIR_RE = /^(.+\/prompts\/)shot(\d+)_(kling|seedance)\.md$/;

export interface ShotPairInfo {
  /** path of the file the user clicked */
  primaryPath: string;
  /** path of the partner file (Kling if primary is Seedance, and vice versa) */
  partnerPath: string;
  /** "kling" if primary is the Kling file, "seedance" otherwise */
  primaryKind: "kling" | "seedance";
  /** the shot number (e.g., 1, 2, 5) — useful for headings */
  shotNumber: number;
  /** "shot01", "shot02" — useful for URLs back to the kling-side default */
  shotSlug: string;
}

/** Returns ShotPairInfo if the path matches the pair-detection pattern; null otherwise. */
export function detectShotPair(path: string): ShotPairInfo | null {
  const m = SHOT_PAIR_RE.exec(path);
  if (!m) return null;
  const [, prefix, numStr, kind] = m;
  const partnerKind = kind === "kling" ? "seedance" : "kling";
  return {
    primaryPath: path,
    partnerPath: `${prefix}shot${numStr}_${partnerKind}.md`,
    primaryKind: kind as "kling" | "seedance",
    shotNumber: parseInt(numStr, 10),
    shotSlug: `shot${numStr}`,
  };
}

/** Given a shot folder + number, build the canonical Kling path (used for ShotlistTableView links). */
export function shotPairKlingPath(promptsFolder: string, shotNumber: number): string {
  const padded = String(shotNumber).padStart(2, "0");
  return `${promptsFolder.replace(/\/$/, "")}/shot${padded}_kling.md`;
}
