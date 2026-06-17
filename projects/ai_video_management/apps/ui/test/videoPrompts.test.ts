import { describe, expect, it } from "vitest";
import {
  episodeDirOf,
  extractVideoPromptBody,
  shotMdPathsInEpisode,
} from "../src/lib/videoPrompts";

const SHOT = `---
worker_id: x
---

## 小说原文

prose here.

---

# ep02 / shot01 · 走出

## 视频 prompt — 复制下方代码块到视频生成模型

\`\`\`text
02集01镜视
参考: \`裴知秋, bg5_中_中轴俯瞰\`
时长: 8秒
\`\`\`

## 台词配音 prompt — 复制下方代码块给 TTS

\`\`\`text
02集01镜 · 台词配音
台词: 哟，废物也敢放狂话？
\`\`\`
`;

describe("extractVideoPromptBody", () => {
  it("returns the 视频 prompt block, not the 台词配音 block", () => {
    const body = extractVideoPromptBody(SHOT);
    expect(body).not.toBeNull();
    expect(body).toContain("02集01镜视");
    expect(body).toContain("时长: 8秒");
    // explicitly excludes the 台词配音 block
    expect(body).not.toContain("台词配音");
    expect(body).not.toContain("哟，废物");
  });

  it("returns null when there is no fenced block", () => {
    expect(extractVideoPromptBody("# heading\n\njust prose")).toBeNull();
  });

  it("returns null when there is no 视频 block (only 台词配音)", () => {
    const onlyVo = "## 台词配音 prompt\n\n```text\n台词: x\n```\n";
    expect(extractVideoPromptBody(onlyVo)).toBeNull();
  });
});

describe("episodeDirOf", () => {
  it("returns the episode folder for an episode-level md", () => {
    expect(episodeDirOf("ai_videos/wushen_juexing/episodes/ep02/shotlist.md")).toBe(
      "ai_videos/wushen_juexing/episodes/ep02",
    );
  });
  it("returns null for a per-shot md (extra path segment)", () => {
    expect(
      episodeDirOf("ai_videos/wushen_juexing/episodes/ep02/shots/shot01/shot01.md"),
    ).toBeNull();
  });
  it("returns null for a non-episode path", () => {
    expect(episodeDirOf("ai_videos/wushen_juexing/world.md")).toBeNull();
  });
});

describe("shotMdPathsInEpisode", () => {
  const known = [
    "ai_videos/wushen_juexing/episodes/ep02/shotlist.md",
    "ai_videos/wushen_juexing/episodes/ep02/shots/shot02/shot02.md",
    "ai_videos/wushen_juexing/episodes/ep02/shots/shot01/shot01.md",
    "ai_videos/wushen_juexing/episodes/ep02/shots/shot10/shot10.md",
    "ai_videos/wushen_juexing/episodes/ep02/shots/shot01/renders/x.mp4",
    "ai_videos/wushen_juexing/episodes/ep01/shots/shot01/shot01.md",
  ];
  it("collects only this episode's shot mds, sorted", () => {
    expect(shotMdPathsInEpisode(known, "ai_videos/wushen_juexing/episodes/ep02")).toEqual([
      "ai_videos/wushen_juexing/episodes/ep02/shots/shot01/shot01.md",
      "ai_videos/wushen_juexing/episodes/ep02/shots/shot02/shot02.md",
      "ai_videos/wushen_juexing/episodes/ep02/shots/shot10/shot10.md",
    ]);
  });
});
