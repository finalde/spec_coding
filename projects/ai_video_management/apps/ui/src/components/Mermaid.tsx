/** Mermaid — lazily renders a Mermaid diagram string to inline SVG.
 *
 * The mermaid library (~heavy) is dynamically imported on first use so it stays
 * in its own code-split chunk and never weighs on the rest of the app. Click
 * directives in the chart (`click X call fn(...)`) are honored via bindFunctions
 * + securityLevel:"loose", so the overview diagram's stage nodes can open the
 * stage drawer. Each instance renders with a unique, CSS-safe id.
 */
import { useEffect, useId, useRef, useState } from "react";

type MermaidApi = {
  initialize: (cfg: Record<string, unknown>) => void;
  render: (id: string, chart: string) => Promise<{ svg: string; bindFunctions?: (el: Element) => void }>;
};

let mermaidPromise: Promise<MermaidApi> | null = null;

function getMermaid(): Promise<MermaidApi> {
  if (!mermaidPromise) {
    mermaidPromise = import("mermaid").then((mod) => {
      const m = mod.default as unknown as MermaidApi;
      m.initialize({
        startOnLoad: false,
        securityLevel: "loose",
        theme: "neutral",
        fontFamily: 'inherit',
        flowchart: { curve: "basis", htmlLabels: true, useMaxWidth: true },
      });
      return m;
    });
  }
  return mermaidPromise;
}

export interface MermaidProps {
  chart: string;
  className?: string;
}

export function Mermaid({ chart, className }: MermaidProps): JSX.Element {
  const hostRef = useRef<HTMLDivElement>(null);
  const rawId = useId();
  const renderId = "mmd" + rawId.replace(/[^a-zA-Z0-9]/g, "");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setError(null);
    void (async () => {
      try {
        const mermaid = await getMermaid();
        const { svg, bindFunctions } = await mermaid.render(renderId, chart);
        if (cancelled || !hostRef.current) return;
        hostRef.current.innerHTML = svg;
        bindFunctions?.(hostRef.current);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : String(err));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [chart, renderId]);

  if (error) {
    return (
      <div className="mermaid-error" role="alert">
        图表渲染失败：{error}
      </div>
    );
  }
  return <div ref={hostRef} className={["mermaid-host", className].filter(Boolean).join(" ")} aria-label="流程图" />;
}
