import { describe, expect, it } from "vitest";
import { extractDramaAssets } from "../src/lib/dramas";
import type { TreeNode } from "../src/types";

function dir(name: string, path: string, children: TreeNode[] = []): TreeNode {
  return { type: "directory", name, path, children };
}
function file(name: string, path: string): TreeNode {
  return { type: "file", name, path };
}

const tree: TreeNode = {
  type: "section",
  name: "root",
  path: "",
  children: [
    dir("ai_videos", "ai_videos", [
      dir("feng_shou_lu", "ai_videos/feng_shou_lu", [
        dir("characters", "ai_videos/feng_shou_lu/characters", [
          dir("c1_裴知秋", "ai_videos/feng_shou_lu/characters/c1_裴知秋"),
          dir("c2_裴长砚", "ai_videos/feng_shou_lu/characters/c2_裴长砚"),
          file("README.md", "ai_videos/feng_shou_lu/characters/README.md"),
        ]),
        dir("scenes", "ai_videos/feng_shou_lu/scenes", [
          dir("s1_无寿崖", "ai_videos/feng_shou_lu/scenes/s1_无寿崖"),
          dir("s2_落雁渊", "ai_videos/feng_shou_lu/scenes/s2_落雁渊"),
        ]),
      ]),
      dir("other_drama", "ai_videos/other_drama", [
        dir("characters", "ai_videos/other_drama/characters", [
          dir("c1_别人", "ai_videos/other_drama/characters/c1_别人"),
        ]),
      ]),
    ]),
  ],
};

describe("extractDramaAssets", () => {
  it("lists characters + scenes (prefix stripped) for the file's drama", () => {
    const a = extractDramaAssets(tree, "ai_videos/feng_shou_lu/episodes/ep01/shots/shot01/shot01.md");
    expect(a.characters).toEqual(["裴知秋", "裴长砚"]);
    expect(a.scenes).toEqual(["无寿崖", "落雁渊"]);
  });

  it("scopes to the right drama (does not leak other_drama)", () => {
    const a = extractDramaAssets(tree, "ai_videos/other_drama/shotlist.md");
    expect(a.characters).toEqual(["别人"]);
    expect(a.scenes).toEqual([]);
  });

  it("returns empty for non-ai_videos or null paths", () => {
    expect(extractDramaAssets(tree, "specs/x/y.md")).toEqual({ characters: [], scenes: [] });
    expect(extractDramaAssets(tree, null)).toEqual({ characters: [], scenes: [] });
    expect(extractDramaAssets(null, "ai_videos/feng_shou_lu/x.md")).toEqual({ characters: [], scenes: [] });
  });
});
