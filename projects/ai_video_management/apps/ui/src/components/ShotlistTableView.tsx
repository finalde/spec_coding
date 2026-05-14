/** ShotlistTableView: renders a shotlist .md file as standard react-markdown,
 * but overrides components.td to wrap shot-id text in a button that programmatically
 * navigates to the matching ShotPairView.
 *
 * Programmatic navigation avoids invalid <a>-inside-<tr> while keeping the
 * markdown source URL-agnostic.
 */
import { useMemo } from "react";
import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";
import { useNavigate } from "react-router-dom";
import { projectFromShotlistPath } from "../lib/shotlistParser";
import { shotPairKlingPath } from "../lib/shotPairing";

export interface ShotlistTableViewProps {
  content: string;
  /** absolute path under EXPOSED_TREE, e.g. `ai_videos/wukong_juexing/shotlist.md` */
  shotlistPath: string;
}

const SHOT_ID_RE = /^shot(\d+)$/;

export function ShotlistTableView({ content, shotlistPath }: ShotlistTableViewProps): JSX.Element {
  const navigate = useNavigate();
  const projectName = useMemo(() => projectFromShotlistPath(shotlistPath), [shotlistPath]);
  const promptsFolder = projectName ? `ai_videos/${projectName}/prompts` : null;

  return (
    <div className="shotlist-table-view markdown-view" lang="zh-Hans">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeSanitize]}
        components={{
          td: ({ children, ...rest }) => {
            // Detect shot-id text in column 1; wrap in nav button.
            const text = textOf(children).trim().replace(/^`|`$/g, "");
            const m = SHOT_ID_RE.exec(text);
            if (m && promptsFolder) {
              const shotNumber = parseInt(m[1], 10);
              const target = `/file/${encodeURIComponent(shotPairKlingPath(promptsFolder, shotNumber))}`;
              return (
                <td {...rest}>
                  <button
                    type="button"
                    className="shotlist-row-link"
                    onClick={() => navigate(target)}
                    aria-label={`打开 ${text} 配对视图`}
                  >
                    {text}
                  </button>
                </td>
              );
            }
            return <td {...rest}>{children}</td>;
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}

function textOf(children: React.ReactNode): string {
  if (typeof children === "string") return children;
  if (typeof children === "number") return String(children);
  if (Array.isArray(children)) return children.map(textOf).join("");
  if (children && typeof children === "object" && "props" in children) {
    const props = (children as { props: { children?: React.ReactNode } }).props;
    return textOf(props.children);
  }
  return "";
}
