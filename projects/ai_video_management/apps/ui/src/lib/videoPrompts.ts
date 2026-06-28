/** Helpers for the episode-level "copy all 视频 prompts" toolbar action.
 *
 * Gathers the `视频 prompt` fenced block from every shot md in an episode and
 * joins them so the user can copy all of them in one click. ONLY the video
 * prompt block is collected — the `台词配音` block (and any other fenced block)
 * is deliberately excluded.
 */
import { findAllFencedCode } from "./promptEdit";
import { blockKindFromHeading } from "./promptSchema";

/** Extract the body of the `视频 prompt` fenced block from a shot md's content,
 * classifying each fenced block by its nearest preceding `##` heading (same
 * rule as the inline per-block editor). Returns null if the shot has no video
 * block (e.g. a malformed file). Newlines normalized to LF, trailing blank
 * lines stripped — matching the per-block copy button's verbatim body. */
export function extractVideoPromptBody(content: string): string | null {
  const blocks = findAllFencedCode(content);
  if (blocks.length === 0) return null;
  const headings: { pos: number; text: string }[] = [];
  const headingRe = /^#{1,6}[ \t]+(.+)$/gm;
  let hm: RegExpExecArray | null;
  while ((hm = headingRe.exec(content)) !== null) {
    headings.push({ pos: hm.index, text: hm[1] });
  }
  for (const b of blocks) {
    let nearest: string | null = null;
    for (const h of headings) {
      if (h.pos < b.start) nearest = h.text;
      else break;
    }
    if (nearest && blockKindFromHeading(nearest) === "video") {
      return b.body.replace(/\r\n/g, "\n").replace(/\n+$/, "");
    }
  }
  return null;
}

/** Given any markdown path directly inside an episode folder
 * (`ai_videos/{drama}/episodes/ep{NN}/{file}.md`), return the episode folder
 * path, or null if `path` is not an episode-level file. */
export function episodeDirOf(path: string): string | null {
  const m = path.match(/^(ai_videos\/[^_][^/]+\/episodes\/ep\d+)\/[^/]+\.md$/);
  return m ? m[1] : null;
}

/** All shot md paths under an episode folder
 * (`{episodeDir}/shots/shot{NN}/shot{NN}.md`), sorted by path so the prompts
 * come out in shot order (shot01, shot02, …). */
export function shotMdPathsInEpisode(knownPaths: string[], episodeDir: string): string[] {
  const esc = episodeDir.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(`^${esc}/shots/shot\\d+/shot\\d+\\.md$`);
  return knownPaths.filter((p) => re.test(p)).sort();
}
