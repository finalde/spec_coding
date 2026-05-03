import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "../src/components/Sidebar";

function renderSidebar(tree: TreeNode): ReturnType<typeof render> {
  return render(
    <MemoryRouter>
      <Sidebar tree={tree} currentPath="" onSelect={() => {}} />
    </MemoryRouter>,
  );
}

type TreeNode = {
  type: "section" | "directory" | "file";
  name: string;
  path: string;
  children?: TreeNode[];
};

const tree: TreeNode = {
  type: "section",
  name: "root",
  path: "",
  children: [
    {
      type: "section",
      name: "Claude Settings & Shared Context",
      path: "_claude",
      children: [
        {
          type: "file",
          name: "CLAUDE.md",
          path: "CLAUDE.md",
        },
        {
          type: "directory",
          name: ".claude",
          path: ".claude",
          children: [
            {
              type: "directory",
              name: "agent_refs",
              path: ".claude/agent_refs",
              children: [
                {
                  type: "directory",
                  name: "validation",
                  path: ".claude/agent_refs/validation",
                  children: [
                    {
                      type: "file",
                      name: "general.md",
                      path: ".claude/agent_refs/validation/general.md",
                    },
                    {
                      type: "file",
                      name: "development.md",
                      path: ".claude/agent_refs/validation/development.md",
                    },
                  ],
                },
                {
                  type: "directory",
                  name: "project",
                  path: ".claude/agent_refs/project",
                  children: [
                    {
                      type: "file",
                      name: "development.md",
                      path: ".claude/agent_refs/project/development.md",
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
    {
      type: "section",
      name: "Specs",
      path: "_specs",
      children: [
        {
          type: "directory",
          name: "development",
          path: "projects/development",
          children: [
            {
              type: "directory",
              name: "spec_driven",
              path: "projects/development/spec_driven",
              children: [
                {
                  type: "directory",
                  name: "interview",
                  path: "specs/development/spec_driven/interview",
                  children: [
                    {
                      type: "file",
                      name: "qa.md",
                      path: "specs/development/spec_driven/interview/qa.md",
                    },
                    {
                      type: "file",
                      name: "promoted.md",
                      path: "specs/development/spec_driven/interview/promoted.md",
                    },
                  ],
                },
                {
                  type: "directory",
                  name: "final_specs",
                  path: "specs/development/spec_driven/final_specs",
                  children: [
                    {
                      type: "file",
                      name: "spec.md",
                      path: "specs/development/spec_driven/final_specs/spec.md",
                    },
                  ],
                },
              ],
            },
          ],
        },
      ],
    },
  ],
};

const countLeavesViaChildren = (node: TreeNode): number => {
  if (node.type === "file" || !node.children) return node.type === "file" ? 1 : 0;
  return node.children.reduce((acc, c) => acc + countLeavesViaChildren(c), 0);
};

describe("Sidebar — recursive walk via uniform `children` (move 2, AC-26)", () => {
  it("renders every file leaf in the recursive tree fixture", () => {
    renderSidebar(tree);
    const expected = countLeavesViaChildren(tree);
    expect(expected).toBeGreaterThanOrEqual(6);
    // Each leaf name appears at least once.
    expect(screen.getAllByText("CLAUDE.md").length).toBeGreaterThan(0);
    expect(screen.getAllByText("general.md").length).toBeGreaterThan(0);
    expect(
      screen.getAllByText("development.md").length,
    ).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("qa.md").length).toBeGreaterThan(0);
    expect(screen.getAllByText("spec.md").length).toBeGreaterThan(0);
  });

  it("renders top-level section names: 'Claude Settings & Shared Context' and 'Specs'", () => {
    renderSidebar(tree);
    expect(
      screen.getByText("Claude Settings & Shared Context"),
    ).toBeInTheDocument();
    expect(screen.getByText("Specs")).toBeInTheDocument();
  });

  it("descends through arbitrarily-deep children chains (regression for spec_driven-20260502-clean)", () => {
    renderSidebar(tree);
    // Deepest file is .claude/agent_refs/project/development.md and
    // specs/development/spec_driven/final_specs/spec.md — must be visible.
    const devEntries = screen.getAllByText("development.md");
    expect(devEntries.length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText("spec.md").length).toBeGreaterThan(0);
    expect(screen.getAllByText("promoted.md").length).toBeGreaterThan(0);
  });
});
