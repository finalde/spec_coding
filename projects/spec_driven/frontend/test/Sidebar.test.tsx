import { afterEach, describe, expect, it, vi } from "vitest";
import { render, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Sidebar } from "../src/components/Sidebar";

const fixture = {
  name: "root",
  path: "",
  type: "section",
  children: [
    {
      name: "Claude Settings & Shared Context",
      path: "_claude",
      type: "section",
      children: [{ name: "CLAUDE.md", path: "CLAUDE.md", type: "file", children: [] }],
    },
    {
      name: "Projects",
      path: "_projects",
      type: "section",
      children: [
        {
          name: "development",
          path: "specs/development",
          type: "type",
          children: [
            {
              name: "spec_driven",
              path: "specs/development/spec_driven",
              type: "project",
              children: [
                {
                  name: "final_specs",
                  path: "specs/development/spec_driven/final_specs",
                  type: "stage",
                  children: [
                    {
                      name: "spec.md",
                      path: "specs/development/spec_driven/final_specs/spec.md",
                      type: "file",
                      children: [],
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

afterEach(() => vi.restoreAllMocks());

describe("Sidebar", () => {
  it("[regression-2026-05-02-clean] descends node.children recursively and renders leaves under both top-level sections", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(fixture), { status: 200 }),
    );

    const { container, findByTestId } = render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>,
    );

    await findByTestId("sidebar");
    await waitFor(() => {
      const leaves = container.querySelectorAll('[data-testid="tree-leaf"]');
      expect(leaves.length).toBeGreaterThanOrEqual(2);
    });

    const claudeSection = container.querySelector('[data-section="claude"]');
    const projectsSection = container.querySelector('[data-section="projects"]');
    expect(claudeSection).toBeTruthy();
    expect(projectsSection).toBeTruthy();
    expect(claudeSection!.querySelectorAll('[data-testid="tree-leaf"]').length).toBeGreaterThanOrEqual(1);
    expect(projectsSection!.querySelectorAll('[data-testid="tree-leaf"]').length).toBeGreaterThanOrEqual(1);
    expect(projectsSection!.querySelector('[data-testid="project-link"]')).toBeTruthy();
  });

  it("does NOT read node.projects or node.stages — pure node.children walk", async () => {
    const tampered = JSON.parse(JSON.stringify(fixture));
    tampered.children[1].projects = [{ name: "DRIFT", path: "drift", type: "project", children: [] }];
    delete tampered.children[1].children[0].children[0].children[0].children;
    tampered.children[1].children[0].children[0].children[0].stages = [
      {
        name: "DRIFT",
        path: "drift",
        type: "stage",
        children: [{ name: "drift.md", path: "drift.md", type: "file", children: [] }],
      },
    ];

    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify(tampered), { status: 200 }),
    );

    const { container, findByTestId } = render(
      <MemoryRouter>
        <Sidebar />
      </MemoryRouter>,
    );

    await findByTestId("sidebar");
    await waitFor(() => {
      const leaves = container.querySelectorAll('[data-testid="tree-leaf"]');
      const names = Array.from(leaves).map((l) => l.textContent);
      expect(names.some((n) => n === "DRIFT")).toBe(false);
    });
  });
});
