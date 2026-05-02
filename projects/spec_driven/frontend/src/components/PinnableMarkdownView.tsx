import { detectAtomicUnits } from "../markdown/atomicUnits";
import { MarkdownView } from "../markdown/renderer";
import { stagePathFor, usePromotions } from "../promotions";
import { PinToggle } from "./PinToggle";

export interface PinnableMarkdownViewProps {
  source: string;
  sourcePath: string;
  exposedPaths: ReadonlySet<string>;
}

/**
 * Wraps `MarkdownView` with per-atomic-unit pin toggles for files inside a
 * promotable stage (interview/findings/final_specs/validation, except
 * promoted.md itself which is rendered by `PromotedView`). Files outside
 * promotable stages should use `MarkdownView` directly.
 */
export function PinnableMarkdownView({
  source,
  sourcePath,
  exposedPaths,
}: PinnableMarkdownViewProps): JSX.Element {
  const stagePath = stagePathFor(sourcePath);
  const { isPinned, pin, unpin, error } = usePromotions(stagePath);
  if (!stagePath) {
    return (
      <MarkdownView source={source} sourcePath={sourcePath} exposedPaths={exposedPaths} />
    );
  }
  const units = detectAtomicUnits(source);
  if (units.length === 0) {
    return (
      <MarkdownView source={source} sourcePath={sourcePath} exposedPaths={exposedPaths} />
    );
  }

  // Render any preamble text (lines before the first detected unit) plainly.
  const lines = source.split(/\r?\n/);
  const preamble = units[0].startLine > 0
    ? lines.slice(0, units[0].startLine).join("\n").trimEnd()
    : "";

  // Filename relative to stage folder, used in pin location metadata.
  const sourceFileShort = sourcePath.split("/").pop() ?? sourcePath;
  const stageName = stagePath.split("/").pop() ?? "";

  return (
    <div className="pinnable-markdown">
      {error && (
        <div className="editor-error-banner" role="alert">
          {error}
        </div>
      )}
      {preamble && (
        <div className="pinnable-preamble">
          <MarkdownView
            source={preamble}
            sourcePath={sourcePath}
            exposedPaths={exposedPaths}
          />
        </div>
      )}
      {units.map((u) => {
        const matched = isPinned(u.body);
        const location = `${stageName}/${sourceFileShort} / ${u.label}`;
        return (
          <section
            key={`${u.startLine}:${u.itemId}`}
            className={`pinnable-unit${matched ? " pinnable-unit-pinned" : ""}`}
            aria-label={u.label}
          >
            <header className="pinnable-unit-toolbar">
              <span className="pinnable-unit-label" title={u.label}>
                {u.label}
              </span>
              <PinToggle
                pin={matched}
                onPin={() => pin(location, u.body)}
                onUnpin={(pinId) => unpin(pinId)}
                ariaLabel={matched ? `Unpin ${u.label}` : `Pin ${u.label}`}
              />
              {matched && (
                <span
                  className="pinnable-unit-pinned-note"
                  title="Edit the pinned version on the promoted.md page."
                >
                  📌 pinned ({matched.pin_id}) — edits to this file modify the
                  GENERATED version only; edit the pinned version on{" "}
                  <code>{stageName}/promoted.md</code>.
                </span>
              )}
            </header>
            <MarkdownView
              source={u.body}
              sourcePath={sourcePath}
              exposedPaths={exposedPaths}
            />
          </section>
        );
      })}
    </div>
  );
}
