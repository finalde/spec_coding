import { useState } from "react";
import { usePromotions } from "../promotions";
import type { Pin } from "../types";
import { MarkdownView } from "../markdown/renderer";

export interface PromotedViewProps {
  /** Path of the promoted.md file, e.g. specs/development/spec_driven/interview/promoted.md */
  filePath: string;
  /** Set of paths that resolve in-app, used by inline markdown rendering. */
  exposedPaths: ReadonlySet<string>;
}

function stagePathFromPromotedFile(filePath: string): string {
  const parts = filePath.split("/");
  return parts.slice(0, parts.length - 1).join("/");
}

export function PromotedView({ filePath, exposedPaths }: PromotedViewProps): JSX.Element {
  const stagePath = stagePathFromPromotedFile(filePath);
  const { pins, loaded, unpin, error } = usePromotions(stagePath);
  return (
    <div className="promoted-view">
      <header className="promoted-view-header">
        <h1>Pinned items</h1>
        <p className="promoted-view-explainer">
          These items survive every regeneration of this stage. They are inputs,
          not outputs — they are NEVER deleted by <code>read-zero</code>. Edit a
          pinned item directly here; it does not modify the generated artifact.
        </p>
      </header>
      {error && (
        <div className="editor-error-banner" role="alert">
          {error}
        </div>
      )}
      {loaded && pins.length === 0 && (
        <p className="promoted-view-empty">
          No pinned items yet. Open a stage file (e.g. <code>qa.md</code>,{" "}
          <code>spec.md</code>) and click 📍 next to any atomic unit to pin it.
        </p>
      )}
      {pins.map((pin) => (
        <PinCard
          key={pin.pin_id}
          pin={pin}
          onUnpin={() => unpin(pin.pin_id)}
          exposedPaths={exposedPaths}
          filePath={filePath}
        />
      ))}
    </div>
  );
}

interface PinCardProps {
  pin: Pin;
  onUnpin: () => Promise<void>;
  exposedPaths: ReadonlySet<string>;
  filePath: string;
}

function PinCard({ pin, onUnpin, exposedPaths, filePath }: PinCardProps): JSX.Element {
  const [busy, setBusy] = useState(false);
  return (
    <article className="promoted-pin-card">
      <header className="promoted-pin-header">
        <span className="promoted-pin-id">{pin.pin_id}</span>
        <span className="promoted-pin-location">{pin.location}</span>
        <button
          type="button"
          className="promoted-pin-unpin"
          onClick={() => {
            if (busy) return;
            setBusy(true);
            void onUnpin().finally(() => setBusy(false));
          }}
          disabled={busy}
          title={`Unpin ${pin.pin_id}`}
          aria-label={`Unpin ${pin.pin_id}`}
        >
          🗑 Unpin
        </button>
      </header>
      <div className="promoted-pin-body">
        <MarkdownView
          source={pin.body}
          sourcePath={filePath}
          exposedPaths={exposedPaths}
        />
      </div>
    </article>
  );
}
