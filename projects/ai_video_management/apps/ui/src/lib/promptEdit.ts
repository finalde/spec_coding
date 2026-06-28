/** Helpers for in-place prompt editing.
 *
 * v1 (first-block-only): VoiceView / ActorView / ShotPairView / ImageRefView
 * each rendered the FIRST fenced code block of its target .md as "the prompt"
 * and edit mode swapped just that block back via PUT /api/file with
 * If-Unmodified-Since concurrency.
 *
 * v2 (per follow-up 116, 2026-05-25): the generic markdown Renderer now adds
 * a "✏ Edit" affordance to EVERY fenced code block under `ai_videos/` so
 * multi-prompt files (scene archives with image + 15s walk-through prompts,
 * character bibles with turntable + Seedream立绘 + state-A/B variants) can
 * have each prompt edited inline. The v1 helpers stay for backward compat;
 * v2 adds indexed access (Nth block).
 */

export interface FencedCodeMatch {
  /** Full match text including fences. */
  full: string;
  /** Opening fence including language tag and trailing newline (e.g. "```text\n"). */
  open: string;
  /** Body text between fences (no trailing newline guaranteed). */
  body: string;
  /** Closing fence (always "```"). */
  close: string;
  /** Character index into the source where `full` begins. */
  start: number;
  /** Character index into the source where `full` ends (exclusive). */
  end: number;
}

// NB: `\r?\n` after the language tag so the opening fence matches under
// Windows CRLF line endings too. Without the `\r?`, an actor/voice/shot .md
// saved with CRLF (the ``` line ends "```\r\n") fails to match — the parser
// then reports zero prompts and ActorView/VoiceView render no copy cards.
const _FENCE_RE_SINGLE = /(```[A-Za-z0-9_-]*\r?\n)([\s\S]*?)(```)/;
const _FENCE_RE_GLOBAL = /(```[A-Za-z0-9_-]*\r?\n)([\s\S]*?)(```)/g;

/** Locate the first fenced code block in `content`, or null if none. */
export function findFirstFencedCode(content: string): FencedCodeMatch | null {
  const m = _FENCE_RE_SINGLE.exec(content);
  if (!m || m.index === undefined) return null;
  return {
    full: m[0],
    open: m[1],
    body: m[2],
    close: m[3],
    start: m.index,
    end: m.index + m[0].length,
  };
}

/** Locate ALL fenced code blocks in source order. Empty array if none. */
export function findAllFencedCode(content: string): FencedCodeMatch[] {
  const out: FencedCodeMatch[] = [];
  const re = new RegExp(_FENCE_RE_GLOBAL.source, _FENCE_RE_GLOBAL.flags);
  let m: RegExpExecArray | null;
  while ((m = re.exec(content)) !== null) {
    out.push({
      full: m[0],
      open: m[1],
      body: m[2],
      close: m[3],
      start: m.index,
      end: m.index + m[0].length,
    });
  }
  return out;
}

/** Locate the Nth fenced code block (0-indexed), or null if out of range. */
export function findNthFencedCode(content: string, n: number): FencedCodeMatch | null {
  if (n < 0) return null;
  const all = findAllFencedCode(content);
  return n < all.length ? all[n] : null;
}

/** Extract just the trimmed body of the first fenced code block, or null. */
export function extractFirstFencedCode(content: string): string | null {
  const m = findFirstFencedCode(content);
  return m ? m.body.replace(/\n+$/, "") : null;
}

/** Extract the trimmed body of the Nth fenced code block (0-indexed), or null. */
export function extractNthFencedCode(content: string, n: number): string | null {
  const m = findNthFencedCode(content, n);
  return m ? m.body.replace(/\n+$/, "") : null;
}

/** Return `content` with the first fenced code block's body replaced.
 *  The opening fence (and its language tag) and the closing fence are
 *  preserved verbatim; `newBody`'s trailing newlines are normalized so
 *  the close fence always sits on its own line.
 */
export function replaceFirstFencedCode(content: string, newBody: string): string {
  const m = findFirstFencedCode(content);
  if (!m) {
    throw new Error("replaceFirstFencedCode: no fenced code block found");
  }
  const normalized = newBody.replace(/\n+$/, "") + "\n";
  const rebuilt = m.open + normalized + m.close;
  return content.slice(0, m.start) + rebuilt + content.slice(m.end);
}

/** Return `content` with the Nth fenced code block's body replaced (0-indexed).
 *  Throws if `n` is out of range. Opening fence (language tag) + closing fence
 *  preserved byte-identical; `newBody` trailing newlines normalized.
 */
export function replaceFencedCodeAt(content: string, n: number, newBody: string): string {
  const m = findNthFencedCode(content, n);
  if (!m) {
    throw new Error(`replaceFencedCodeAt: block index ${n} out of range`);
  }
  const normalized = newBody.replace(/\n+$/, "") + "\n";
  const rebuilt = m.open + normalized + m.close;
  return content.slice(0, m.start) + rebuilt + content.slice(m.end);
}
