/** ImageRefView: renders Seedream立绘 prompt + companion .png preview.
 *
 * Triggered when path matches `/ref_images/.+_seedream\.md$` OR ends `.png|.jpg`.
 * - Left pane: prompt markdown (when triggered by `_seedream.md`) or empty
 * - Right pane: image preview (when companion exists) or fallback message
 *
 * Image extensions are read-only via /api/file.
 */
import { useEffect, useMemo, useState } from "react";
import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { fetchFile, imageUrl } from "../api";
import { ApiError, type FileResult } from "../types";
import { Renderer } from "../markdown/renderer";
import { ParseFallback } from "./ParseFallback";

export interface ImageRefViewProps {
  primaryFile: FileResult;
  primaryPath: string;
  knownPaths: string[];
}

const SEEDREAM_RE = /^(.+\/ref_images\/)([^/]+)_seedream\.md$/;
const IMG_EXT_RE = /\.(png|jpg|jpeg)$/i;

export function ImageRefView({ primaryFile, primaryPath, knownPaths }: ImageRefViewProps): JSX.Element {
  const layout = useMemo(() => resolveLayout(primaryPath), [primaryPath]);
  const [companionImage, setCompanionImage] = useState<FileResult | null>(null);
  const [companionMissing, setCompanionMissing] = useState<boolean>(false);

  useEffect(() => {
    if (layout.kind !== "prompt") return;
    setCompanionImage(null);
    setCompanionMissing(false);
    fetchFile(layout.expectedPngPath)
      .then((f) => setCompanionImage(f))
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          // Try .jpg as fallback
          fetchFile(layout.expectedJpgPath)
            .then((f) => setCompanionImage(f))
            .catch(() => setCompanionMissing(true));
        } else {
          setCompanionMissing(true);
        }
      });
  }, [layout]);

  if (layout.kind === "image") {
    // Image clicked directly — no prompt left pane
    return (
      <div className="image-ref-view image-ref-view-img-only">
        <header><h2>{layout.filename}</h2></header>
        <div className="image-ref-img-wrapper">
          <img
            src={imageUrl(primaryPath, primaryFile.mtime)}
            alt={`${layout.filename} 立绘`}
            className="image-ref-img"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="image-ref-view">
      <PanelGroup direction="horizontal" autoSaveId="image-ref-split">
        <Panel defaultSize={55} minSize={25}>
          <section className="image-ref-prompt-pane">
            <header className="image-ref-pane-header">
              <span className="image-ref-pane-label">Seedream prompt</span>
            </header>
            <ParseFallback rawText={primaryFile.content} componentName="ImageRefView:prompt">
              <Renderer content={primaryFile.content} currentPath={primaryPath} knownPaths={knownPaths} />
            </ParseFallback>
          </section>
        </Panel>
        <PanelResizeHandle className="resize-handle" />
        <Panel defaultSize={45} minSize={20}>
          <section className="image-ref-img-pane">
            <header className="image-ref-pane-header">
              <span className="image-ref-pane-label">Generated 立绘</span>
            </header>
            {companionImage ? (
              <div className="image-ref-img-wrapper">
                <img
                  src={imageUrl(layout.expectedPngPath.endsWith(".png") && !companionMissing
                    ? layout.expectedPngPath : layout.expectedJpgPath, companionImage.mtime)}
                  alt={`${layout.stem} 立绘`}
                  className="image-ref-img"
                />
              </div>
            ) : companionMissing ? (
              <div className="image-ref-fallback" role="status">
                尚未生成立绘 — 复制左侧 prompt 至 Seedream 后保存为{" "}
                <code>{layout.expectedPngPath.split("/").pop()}</code> 并刷新
              </div>
            ) : (
              <div className="muted">Loading…</div>
            )}
          </section>
        </Panel>
      </PanelGroup>
    </div>
  );
}

type Layout =
  | { kind: "prompt"; folder: string; stem: string; expectedPngPath: string; expectedJpgPath: string }
  | { kind: "image"; filename: string };

function resolveLayout(path: string): Layout {
  const m = SEEDREAM_RE.exec(path);
  if (m) {
    const [, folder, stem] = m;
    return {
      kind: "prompt",
      folder,
      stem,
      expectedPngPath: `${folder}${stem}_seedream.png`,
      expectedJpgPath: `${folder}${stem}_seedream.jpg`,
    };
  }
  if (IMG_EXT_RE.test(path)) {
    return { kind: "image", filename: path.split("/").pop() ?? path };
  }
  // Should not reach here if Reader's dispatch is correct
  return { kind: "image", filename: path.split("/").pop() ?? path };
}
