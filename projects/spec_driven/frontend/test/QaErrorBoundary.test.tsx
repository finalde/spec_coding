import { describe, expect, it } from "vitest";
import { Component } from "react";
import { render } from "@testing-library/react";
import { QaErrorBoundary } from "../src/components/QaErrorBoundary";

function Throwing(): JSX.Element {
  throw new Error("simulated parse failure");
}

describe("QaErrorBoundary", () => {
  it("[regression-2026-05-02-clean] is a real React Component (not a try/catch wrapper)", () => {
    expect(QaErrorBoundary.prototype).toBeInstanceOf(Component);
  });

  it("catches render-phase errors and renders the fallback", () => {
    const original = console.error;
    console.error = () => {};
    try {
      const { getByText } = render(
        <QaErrorBoundary fallback={(c) => <div>fallback rendered: {c}</div>}>
          <Throwing />
        </QaErrorBoundary>,
      );
      expect(getByText(/fallback rendered: simulated parse failure/)).toBeTruthy();
    } finally {
      console.error = original;
    }
  });
});
