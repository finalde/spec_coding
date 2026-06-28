export class QaParseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "QaParseError";
  }
}

export interface QaPair {
  kind: "qa";
  itemId: string;
  q: string;
  a: string;
  judgmentCall: string | null;
  rawAnswerLine: string;
  rawQuestionLine: string;
  qLine: number;
  aLine: number;
}

export interface QaCategory {
  kind: "category";
  name: string;
  pairs: QaPair[];
}

export interface QaRound {
  index: number;
  title: string;
  categories: QaCategory[];
}

export interface QaDocument {
  rounds: QaRound[];
  unrecognized?: string[];
}

const ROUND_HEADING = /^##\s+Round\s+(\d+)\b\s*(.*)$/;
const CATEGORY_HEADING = /^###\s+(?:Category\s*:\s*)?(.+?)\s*$/;
const Q_LINE = /^\*\*Q:\*\*\s*(.*)$/;
// A line: `- A: text` or `- A *(judgment call — chose X because Y)*: text`
const A_LINE = /^-\s+A\b(?:\s*\*\((.+?)\)\*)?\s*:\s*(.*)$/;

export function parseQa(content: string): QaDocument {
  if (!content || !content.trim()) {
    return { rounds: [] };
  }
  const lines = content.split(/\r?\n/);
  const rounds: QaRound[] = [];
  const unrecognized: string[] = [];

  let currentRound: QaRound | null = null;
  let currentCategory: QaCategory | null = null;
  let pendingQ: { text: string; line: number; raw: string } | null = null;
  let qIndex = 0;
  let sawAnyHeading = false;
  let sawAnyQA = false;

  const flushCategory = (): void => {
    if (currentCategory && currentRound) {
      currentRound.categories.push(currentCategory);
    }
    currentCategory = null;
  };

  const flushRound = (): void => {
    flushCategory();
    if (currentRound) rounds.push(currentRound);
    currentRound = null;
  };

  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const trimmed = line.trim();
    if (trimmed === "") continue;

    const roundMatch = line.match(ROUND_HEADING);
    if (roundMatch) {
      sawAnyHeading = true;
      flushRound();
      currentRound = {
        index: parseInt(roundMatch[1], 10),
        title: (roundMatch[2] ?? "").replace(/^[—–\-:\s]+/, "").trim(),
        categories: [],
      };
      pendingQ = null;
      qIndex = 0;
      continue;
    }
    const catMatch = line.match(CATEGORY_HEADING);
    if (catMatch) {
      sawAnyHeading = true;
      if (!currentRound) {
        // category outside a round — start an implicit round 1
        currentRound = { index: 1, title: "", categories: [] };
        qIndex = 0;
      }
      flushCategory();
      currentCategory = { kind: "category", name: catMatch[1].trim(), pairs: [] };
      pendingQ = null;
      continue;
    }
    const qMatch = line.match(Q_LINE);
    if (qMatch) {
      sawAnyQA = true;
      pendingQ = { text: qMatch[1].trim(), line: i, raw: line };
      continue;
    }
    const aMatch = line.match(A_LINE);
    if (aMatch && pendingQ) {
      sawAnyQA = true;
      if (!currentRound) {
        currentRound = { index: 1, title: "", categories: [] };
      }
      if (!currentCategory) {
        currentCategory = { kind: "category", name: "general", pairs: [] };
      }
      qIndex += 1;
      const judgment = aMatch[1] ? aMatch[1].trim() : null;
      const answer = (aMatch[2] ?? "").trim();
      const itemId = `round${currentRound.index}.${slugify(currentCategory.name)}.q${qIndex}`;
      currentCategory.pairs.push({
        kind: "qa",
        itemId,
        q: pendingQ.text,
        a: answer,
        judgmentCall: judgment,
        rawAnswerLine: line,
        rawQuestionLine: pendingQ.raw,
        qLine: pendingQ.line,
        aLine: i,
      });
      pendingQ = null;
      continue;
    }
    // Unrecognized non-empty line
    if (trimmed.startsWith("#")) continue;
    unrecognized.push(line);
  }
  flushRound();

  if (!sawAnyHeading && !sawAnyQA) {
    throw new QaParseError("Malformed Q/A document: no Round headings or Q/A markers found");
  }

  const result: QaDocument = { rounds };
  if (unrecognized.length > 0) result.unrecognized = unrecognized;
  return result;
}

export function slugify(value: string): string {
  return value
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
