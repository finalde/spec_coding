import { describe, expect, it } from "vitest";
import {
  blockKindFromHeading,
  fieldWidget,
  joinMulti,
  mergeWithCanonical,
  parsePrompt,
  serializePrompt,
  splitMulti,
} from "../src/lib/promptSchema";

describe("fieldWidget", () => {
  it("maps 人物 / 角色 to multiselect", () => {
    expect(fieldWidget("人物")).toBe("multiselect");
    expect(fieldWidget("角色")).toBe("multiselect");
  });

  it("maps 场景 / 場景 to select (not textarea)", () => {
    expect(fieldWidget("场景")).toBe("select");
    expect(fieldWidget("場景")).toBe("select");
  });

  it("keeps static enums as dropdown and long fields as textarea", () => {
    expect(fieldWidget("时长")).toBe("dropdown");
    expect(fieldWidget("比例")).toBe("dropdown");
    expect(fieldWidget("动作")).toBe("textarea");
    expect(fieldWidget("台词 / 字幕")).toBe("textarea");
    expect(fieldWidget("表情")).toBe("input");
  });
});

describe("splitMulti / joinMulti", () => {
  it("round-trips a 、-joined list", () => {
    expect(splitMulti("裴长砚、卫长烛")).toEqual(["裴长砚", "卫长烛"]);
    expect(joinMulti(["裴长砚", "卫长烛"])).toBe("裴长砚、卫长烛");
  });

  it("splits on mixed separators and drops empties", () => {
    expect(splitMulti("裴长砚, 卫长烛，  苏璃月")).toEqual(["裴长砚", "卫长烛", "苏璃月"]);
    expect(splitMulti("")).toEqual([]);
    expect(joinMulti(["a", "  ", "b"])).toBe("a、b");
  });
});

describe("blockKindFromHeading", () => {
  it("classifies the three shot headings", () => {
    expect(blockKindFromHeading("## 起始帧 (shot 起始 0s 时画面状态)")).toBe("start");
    expect(blockKindFromHeading("## 结束帧 (shot 结束 3s 时画面状态)")).toBe("end");
    expect(blockKindFromHeading("## 视频 prompt — 复制下方代码块到视频生成模型")).toBe("video");
  });

  it("returns null for unrelated headings", () => {
    expect(blockKindFromHeading("## Shot context")).toBeNull();
    expect(blockKindFromHeading("## Chapter excerpt")).toBeNull();
  });
});

describe("mergeWithCanonical", () => {
  it("adds missing canonical video fields (人物 first) preserving existing values", () => {
    const body = "ep01 / shot01 · 测试\n\n场景: 无寿崖 渡劫态\n时长: 3s";
    const merged = mergeWithCanonical(parsePrompt(body), "video");
    const labels = merged.fields.map((f) => f.label);
    expect(labels[0]).toBe("人物");
    expect(labels).toContain("场景");
    expect(labels).toContain("镜头");
    expect(labels).toContain("时长");
    // existing values preserved
    expect(merged.fields.find((f) => f.label === "场景")!.value).toBe("无寿崖 渡劫态");
    expect(merged.fields.find((f) => f.label === "时长")!.value).toBe("3s");
    // missing field appended empty
    expect(merged.fields.find((f) => f.label === "人物")!.value).toBe("");
    // freeform header preserved
    expect(merged.freeform).toContain("ep01 / shot01");
  });

  it("matches labels whitespace-insensitively (no duplicate 台词 / 字幕)", () => {
    const body = "人物: 裴长砚\n台词/字幕: 默剧";
    const merged = mergeWithCanonical(parsePrompt(body), "video");
    const taici = merged.fields.filter((f) => f.label.replace(/\s+/g, "") === "台词/字幕");
    expect(taici.length).toBe(1);
    expect(taici[0].value).toBe("默剧");
  });

  it("uses the 4-field frame schema for start/end", () => {
    const merged = mergeWithCanonical(parsePrompt("角色姿态: 立于青石"), "start");
    expect(merged.fields.map((f) => f.label)).toEqual(["角色姿态", "位置/构图", "表情", "道具"]);
  });

  it("returns parsed unchanged when kind is null", () => {
    const parsed = parsePrompt("主体: x\n风格: y");
    const merged = mergeWithCanonical(parsed, null);
    expect(merged.fields.map((f) => f.label)).toEqual(["主体", "风格"]);
  });

  it("round-trips through serialize for an already-canonical video block", () => {
    const merged = mergeWithCanonical(parsePrompt("人物: 裴长砚\n场景: 无寿崖"), "video");
    merged.fields.find((f) => f.label === "人物")!.value = "裴长砚、卫长烛";
    const out = serializePrompt(merged);
    expect(out).toContain("人物: 裴长砚、卫长烛");
    expect(out).toContain("场景: 无寿崖");
  });
});
