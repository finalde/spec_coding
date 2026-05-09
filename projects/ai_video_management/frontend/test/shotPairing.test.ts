import { describe, expect, it } from "vitest";
import { detectShotPair, shotPairKlingPath } from "../src/lib/shotPairing";
import { parseShotRows, projectFromShotlistPath } from "../src/lib/shotlistParser";

describe("detectShotPair", () => {
  it("detects Kling shot files", () => {
    const r = detectShotPair("ai_videos/wukong_juexing/prompts/shot01_kling.md");
    expect(r).not.toBeNull();
    expect(r!.primaryKind).toBe("kling");
    expect(r!.partnerPath).toBe("ai_videos/wukong_juexing/prompts/shot01_seedance.md");
    expect(r!.shotNumber).toBe(1);
    expect(r!.shotSlug).toBe("shot01");
  });

  it("detects Seedance shot files", () => {
    const r = detectShotPair("ai_videos/wukong_juexing/prompts/shot05_seedance.md");
    expect(r).not.toBeNull();
    expect(r!.primaryKind).toBe("seedance");
    expect(r!.partnerPath).toBe("ai_videos/wukong_juexing/prompts/shot05_kling.md");
    expect(r!.shotNumber).toBe(5);
  });

  it("returns null for non-pair files", () => {
    expect(detectShotPair("ai_videos/wukong_juexing/script.md")).toBeNull();
    expect(detectShotPair("ai_videos/wukong_juexing/prompts/notes.md")).toBeNull();
    expect(detectShotPair("ai_videos/wukong_juexing/characters/main.md")).toBeNull();
  });

  it("rejects malformed shot file names", () => {
    expect(detectShotPair("ai_videos/x/prompts/shot1_kling.md")).not.toBeNull(); // single-digit OK
    expect(detectShotPair("ai_videos/x/prompts/shot01_other.md")).toBeNull();
    expect(detectShotPair("ai_videos/x/notprompts/shot01_kling.md")).toBeNull();
  });
});

describe("shotPairKlingPath", () => {
  it("zero-pads shot numbers", () => {
    expect(shotPairKlingPath("ai_videos/x/prompts", 1)).toBe("ai_videos/x/prompts/shot01_kling.md");
    expect(shotPairKlingPath("ai_videos/x/prompts", 12)).toBe("ai_videos/x/prompts/shot12_kling.md");
  });

  it("normalizes trailing slash", () => {
    expect(shotPairKlingPath("ai_videos/x/prompts/", 3)).toBe("ai_videos/x/prompts/shot03_kling.md");
  });
});

describe("parseShotRows (real wukong_juexing shotlist)", () => {
  // Move #10: parser regex tested against real upstream output
  const realShotlist = `
| 镜次 | 时长 | 景别 | 动作摘要 | 连续性 tokens | 是否 hook 镜头 |
|---|---|---|---|---|---|
| \`shot01\` | 5 s | 大特写 | 灰岩石卵迸发金光 | tokens | ✓ Hook |
| \`shot02\` | 8 s | 大全景 | 镜头自石卵拉远 | tokens | ✗ |
| \`shot03\` | 8 s | 中景 | 怒吼蓄力 | tokens | ✗ |
| \`shot04\` | 10 s | 全身 | 持金箍棒亮相 | tokens | ✗ |
| \`shot05\` | 7 s | 大特写 | 回环 | tokens | ✗ |
`;
  it("extracts all 5 wukong shots in order", () => {
    const rows = parseShotRows(realShotlist);
    expect(rows.map((r) => r.shotSlug)).toEqual(["shot01", "shot02", "shot03", "shot04", "shot05"]);
    expect(rows.map((r) => r.shotNumber)).toEqual([1, 2, 3, 4, 5]);
  });

  it("deduplicates if a shot id appears twice", () => {
    const rows = parseShotRows("| `shot01` | … |\n| `shot01` | … |\n");
    expect(rows.length).toBe(1);
  });
});

describe("projectFromShotlistPath", () => {
  it("extracts project name from valid shotlist path", () => {
    expect(projectFromShotlistPath("ai_videos/wukong_juexing/shotlist.md")).toBe("wukong_juexing");
  });

  it("returns null for non-shotlist paths", () => {
    expect(projectFromShotlistPath("ai_videos/x/script.md")).toBeNull();
    expect(projectFromShotlistPath("not_ai_videos/x/shotlist.md")).toBeNull();
    expect(projectFromShotlistPath("shotlist.md")).toBeNull();
  });
});
