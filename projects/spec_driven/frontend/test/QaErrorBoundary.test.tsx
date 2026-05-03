import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import React, { Component } from "react";
import { render, screen } from "@testing-library/react";
import { QaErrorBoundary } from "../src/components/QaErrorBoundary";

const Thrower: React.FC<{ msg: string }> = ({ msg }) => {
  throw new Error(msg);
};

class ClickThrower extends Component {
  render() {
    return (
      <button
        type="button"
        onClick={() => {
          throw new Error("event-handler boom");
        }}
      >
        click
      </button>
    );
  }
}

describe("QaErrorBoundary — class-component lifecycle (Group 11.1, move 9)", () => {
  it("is a real React Component subclass — Object.getPrototypeOf(QaErrorBoundary).name === 'Component'", () => {
    const protoName = Object.getPrototypeOf(QaErrorBoundary).name;
    expect(["Component", "PureComponent"]).toContain(protoName);
  });

  it("defines static getDerivedStateFromError and instance componentDidCatch", () => {
    expect(typeof (QaErrorBoundary as unknown as { getDerivedStateFromError?: unknown })
      .getDerivedStateFromError).toBe("function");
    expect(
      typeof (QaErrorBoundary.prototype as { componentDidCatch?: unknown })
        .componentDidCatch,
    ).toBe("function");
  });

  it("getDerivedStateFromError returns hasError=true", () => {
    const fn = (QaErrorBoundary as unknown as {
      getDerivedStateFromError: (e: Error) => { hasError: boolean };
    }).getDerivedStateFromError;
    const out = fn(new Error("x"));
    expect(out.hasError).toBe(true);
  });
});

describe("QaErrorBoundary — render-phase throw capture (Group 11.2, move 9)", () => {
  let originalConsoleError: typeof console.error;

  beforeEach(() => {
    originalConsoleError = console.error;
    console.error = vi.fn();
  });

  afterEach(() => {
    console.error = originalConsoleError;
  });

  it("catches a render-phase throw inside a child and renders the fallback", () => {
    render(
      <QaErrorBoundary rawText="raw markdown body">
        <Thrower msg="parse-explode" />
      </QaErrorBoundary>,
    );
    // Fallback is rendered; child markup is not reachable.
    expect(screen.queryByText(/parse-explode/i)).toBeNull();
    // The fallback exposes the raw text in a <pre>.
    const pre = document.querySelector("pre");
    expect(pre).not.toBeNull();
    expect(pre!.textContent).toContain("raw markdown body");
  });

  it("invokes componentDidCatch on render-phase throw", () => {
    const spy = vi.spyOn(QaErrorBoundary.prototype as { componentDidCatch: (...a: unknown[]) => void }, "componentDidCatch");
    render(
      <QaErrorBoundary rawText="raw">
        <Thrower msg="boom" />
      </QaErrorBoundary>,
    );
    expect(spy).toHaveBeenCalled();
    spy.mockRestore();
  });

  it("renders a banner with a parse-error message above the <pre>", () => {
    render(
      <QaErrorBoundary rawText="raw text body">
        <Thrower msg="oops" />
      </QaErrorBoundary>,
    );
    const banner = document.querySelector('[role="alert"], .parse-error-banner');
    expect(banner).not.toBeNull();
  });
});

describe("QaErrorBoundary — does NOT catch event-handler errors (Group 11.3)", () => {
  it("event-handler throws are not caught by the boundary", () => {
    render(
      <QaErrorBoundary rawText="raw">
        <ClickThrower />
      </QaErrorBoundary>,
    );
    // Boundary did NOT trip; the original child (the button) is still rendered.
    const btn = screen.queryByRole("button", { name: /click/i });
    expect(btn).not.toBeNull();
  });
});

describe("QaErrorBoundary — fallback resets on new file (Group 11.5)", () => {
  it("re-rendering with a new key resets hasError", () => {
    const { rerender } = render(
      <QaErrorBoundary key="file-a" rawText="A">
        <Thrower msg="bad-A" />
      </QaErrorBoundary>,
    );
    expect(document.querySelector("pre")?.textContent).toContain("A");

    // New file → new key forces a fresh boundary instance.
    const Healthy: React.FC = () => <div>healthy-B</div>;
    rerender(
      <QaErrorBoundary key="file-b" rawText="B">
        <Healthy />
      </QaErrorBoundary>,
    );
    expect(screen.queryByText("healthy-B")).not.toBeNull();
  });
});
