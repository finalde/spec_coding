/**
 * Atomic-unit detector for spec-pipeline markdown artifacts.
 *
 * Detects boundaries that correspond to user-promotable items: id-tagged
 * paragraphs (FR-NN, NFR-NN, AC-NN, OQ-NN, SYS-NN, SEC-NN, PERF-NN, A11Y-NN),
 * named scenarios (### Scenario:, ### Scenario Outline:), and h2/h3 headings as
 * a fallback. Each unit captures the lines from its start marker to the line
 * before the next start marker.
 */

export interface AtomicUnit {
  /** Stable id when extractable (e.g., "FR-22"); else heading slug. */
  itemId: string;
  /** Human-readable location label, e.g. "FR-22" or "Heading: Cross-cutting insights". */
  label: string;
  /** Source line index where the unit starts (inclusive). */
  startLine: number;
  /** Source line index where the unit ends (exclusive). */
  endLine: number;
  /** Verbatim source lines for this unit. */
  body: string;
}

const ID_PATTERNS: ReadonlyArray<{ re: RegExp; idGroup: number }> = [
  { re: /^\*\*(FR-\d+[a-z]?)\.\*\*/, idGroup: 1 },
  { re: /^\*\*(NFR-\d+)\.\*\*/, idGroup: 1 },
  { re: /^\*\*(AC-\d+)\b/, idGroup: 1 },
  { re: /^\*\*(OQ-\d+)\b/, idGroup: 1 },
  { re: /^##\s+(SYS-\d+)\b/, idGroup: 1 },
  { re: /^###\s+(SEC-\d+)\b/, idGroup: 1 },
  { re: /^###\s+(PERF-\d+)\b/, idGroup: 1 },
  { re: /^###\s+(A11Y-\d+)\b/, idGroup: 1 },
];

const SCENARIO_RE = /^###\s+Scenario(?:\s+Outline)?:\s*(.+?)\s*$/;
const HEADING2_RE = /^##\s+(.+?)\s*$/;
const HEADING3_RE = /^###\s+(.+?)\s*$/;

interface Boundary {
  line: number;
  itemId: string;
  label: string;
}

function detectBoundary(line: string): Pick<Boundary, "itemId" | "label"> | null {
  for (const { re, idGroup } of ID_PATTERNS) {
    const m = re.exec(line);
    if (m) {
      const id = m[idGroup] ?? "";
      return { itemId: id, label: id };
    }
  }
  const sm = SCENARIO_RE.exec(line);
  if (sm) {
    const title = sm[1] ?? "";
    return { itemId: `scenario:${slugify(title)}`, label: `Scenario: ${title}` };
  }
  const h2 = HEADING2_RE.exec(line);
  if (h2) {
    const title = h2[1] ?? "";
    return { itemId: `h2:${slugify(title)}`, label: title };
  }
  const h3 = HEADING3_RE.exec(line);
  if (h3) {
    const title = h3[1] ?? "";
    return { itemId: `h3:${slugify(title)}`, label: title };
  }
  return null;
}

function slugify(s: string): string {
  return s
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/(^-|-$)/g, "")
    .slice(0, 60);
}

export function detectAtomicUnits(source: string): AtomicUnit[] {
  const lines = source.split(/\r?\n/);
  const boundaries: Boundary[] = [];
  let inFence = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i] ?? "";
    if (/^```/.test(line)) {
      inFence = !inFence;
      continue;
    }
    if (inFence) continue;
    const b = detectBoundary(line);
    if (b) {
      boundaries.push({ line: i, itemId: b.itemId, label: b.label });
    }
  }
  if (boundaries.length === 0) return [];

  const units: AtomicUnit[] = [];
  for (let i = 0; i < boundaries.length; i++) {
    const start = boundaries[i].line;
    const end = i + 1 < boundaries.length ? boundaries[i + 1].line : lines.length;
    const body = lines.slice(start, end).join("\n").trimEnd();
    units.push({
      itemId: boundaries[i].itemId,
      label: boundaries[i].label,
      startLine: start,
      endLine: end,
      body,
    });
  }
  return units;
}
