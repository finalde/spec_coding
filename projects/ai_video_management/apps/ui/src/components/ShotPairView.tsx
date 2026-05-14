/** ShotPairView: renders Kling + Seedance shot prompts side-by-side
 * using react-resizable-panels. Pair detection via shotPairing helper.
 */
import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { fetchFile } from "../api";
import { ApiError, type FileResult } from "../types";
import { detectShotPair, type ShotPairInfo } from "../lib/shotPairing";
import { Renderer } from "../markdown/renderer";
import { ParseFallback } from "./ParseFallback";

export interface ShotPairViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
}

export function ShotPairView({ primaryFile, primaryPath, knownPaths }: ShotPairViewProps): JSX.Element {
  const pair = useMemo<ShotPairInfo | null>(() => detectShotPair(primaryPath), [primaryPath]);
  const [partner, setPartner] = useState<FileResult | null>(null);
  const [partnerError, setPartnerError] = useState<ApiError | null>(null);

  useEffect(() => {
    if (!pair) return;
    setPartner(null);
    setPartnerError(null);
    fetchFile(pair.partnerPath)
      .then((f) => setPartner(f))
      .catch((err) => {
        if (err instanceof ApiError) setPartnerError(err);
        else setPartnerError(new ApiError(0, String(err), null));
      });
  }, [pair]);

  if (!pair) {
    return (
      <div className="muted">
        Path does not match shot-pair pattern. Required: <code>prompts/shot&#123;NN&#125;_&#123;kling|seedance&#125;.md</code>
      </div>
    );
  }

  const left = pair.primaryKind === "kling" ? primaryFile : partner;
  const leftLabel = "Kling (image-to-video)";
  const right = pair.primaryKind === "kling" ? partner : primaryFile;
  const rightLabel = "Seedance (text-to-video)";
  const leftPath = pair.primaryKind === "kling" ? primaryPath : pair.partnerPath;
  const rightPath = pair.primaryKind === "seedance" ? primaryPath : pair.partnerPath;
  const partnerMissing = partnerError !== null && partnerError.status === 404;

  return (
    <div className="shot-pair-view" data-shot={pair.shotSlug}>
      <header className="shot-pair-header">
        <h2>Shot {pair.shotNumber} — pair view</h2>
        {partnerMissing ? (
          <div className="shot-pair-missing-banner" role="alert">
            缺少配对文件: <code>{pair.partnerPath}</code> —{" "}
            <Link to={`/file/${encodeURIComponent(pair.partnerPath)}`}>open expected path</Link>
          </div>
        ) : null}
      </header>
      <PanelGroup direction="horizontal" autoSaveId="shot-pair-split">
        <Panel defaultSize={50} minSize={20}>
          <ShotPane file={left} label={leftLabel} path={leftPath} knownPaths={knownPaths} />
        </Panel>
        <PanelResizeHandle className="resize-handle" />
        <Panel defaultSize={50} minSize={20}>
          <ShotPane file={right} label={rightLabel} path={rightPath} knownPaths={knownPaths}
            partnerMissing={!right && partnerMissing} />
        </Panel>
      </PanelGroup>
    </div>
  );
}

interface ShotPaneProps {
  file: FileResult | null;
  label: string;
  path: string;
  knownPaths: string[];
  partnerMissing?: boolean;
}

function ShotPane({ file, label, path, knownPaths, partnerMissing }: ShotPaneProps): JSX.Element {
  const onCopy = async (): Promise<void> => {
    if (!file) return;
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(file.content);
      announceCopy(label);
    } catch {
      // clipboard may be unavailable in non-secure contexts
    }
  };

  if (partnerMissing) {
    return (
      <section className="shot-pane shot-pane-missing">
        <header className="shot-pane-header">
          <span className="shot-pane-label">{label}</span>
        </header>
        <div className="muted">
          File not present at <code>{path}</code>.
        </div>
      </section>
    );
  }

  if (!file) {
    return (
      <section className="shot-pane">
        <header className="shot-pane-header"><span className="shot-pane-label">{label}</span></header>
        <div className="muted">Loading…</div>
      </section>
    );
  }

  return (
    <section className="shot-pane">
      <header className="shot-pane-header">
        <span className="shot-pane-label">{label}</span>
        <button type="button" className="copy-button" onClick={() => void onCopy()}
          aria-label={`复制 ${label} prompt`}>
          复制
        </button>
      </header>
      <ParseFallback rawText={file.content} componentName={`ShotPane:${label}`}>
        <Renderer content={file.content} currentPath={path} knownPaths={knownPaths} />
      </ParseFallback>
    </section>
  );
}

function announceCopy(label: string): void {
  const region = document.getElementById("aria-live-toast");
  if (!region) return;
  region.textContent = `${label} prompt 已复制`;
  setTimeout(() => { if (region.textContent?.endsWith("已复制")) region.textContent = ""; }, 2000);
}
