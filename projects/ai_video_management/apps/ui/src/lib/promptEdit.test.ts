import { describe, expect, it } from "vitest";
import { findAllFencedCode, replaceFencedCodeAt } from "./promptEdit";

const FACE_BODY = "全身定妆照\n气质：邻家女孩";

describe("findAllFencedCode — line-ending tolerance", () => {
  it("matches a bare ``` fence with LF endings", () => {
    const md = "## 生成 prompt (face shot)\n\n```\n" + FACE_BODY + "\n```\n";
    const blocks = findAllFencedCode(md);
    expect(blocks).toHaveLength(1);
    expect(blocks[0].body.replace(/\n+$/, "")).toBe(FACE_BODY);
  });

  it("matches a bare ``` fence with Windows CRLF endings (regression)", () => {
    // Actor/voice/shot .md saved on Windows end the ``` line as "```\r\n".
    // Before the `\r?` fix this returned [] → ActorView showed no prompt cards.
    const md =
      "## 生成 prompt (face shot)\r\n\r\n```\r\n" +
      FACE_BODY.replace(/\n/g, "\r\n") +
      "\r\n```\r\n";
    const blocks = findAllFencedCode(md);
    expect(blocks).toHaveLength(1);
    expect(blocks[0].body.replace(/\r/g, "").replace(/\n+$/, "")).toBe(FACE_BODY);
  });

  it("matches a language-tagged fence under CRLF", () => {
    const md = "```text\r\n人物: 裴知秋\r\n```\r\n";
    const blocks = findAllFencedCode(md);
    expect(blocks).toHaveLength(1);
  });

  it("finds two CRLF blocks (face + body shot)", () => {
    const md =
      "## face\r\n```\r\nA\r\n```\r\n\r\n## body\r\n```\r\nB\r\n```\r\n";
    expect(findAllFencedCode(md)).toHaveLength(2);
  });

  it("replaceFencedCodeAt rewrites the Nth CRLF block, leaving siblings intact", () => {
    const md = "## a\r\n```\r\nOLD\r\n```\r\n\r\n## b\r\n```\r\nKEEP\r\n```\r\n";
    const out = replaceFencedCodeAt(md, 0, "NEW");
    expect(out).toContain("NEW");
    expect(out).not.toContain("OLD");
    expect(out).toContain("KEEP");
  });
});
