import ReactMarkdown from "react-markdown";
import rehypeSanitize, { defaultSchema } from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";
import remarkGfm from "remark-gfm";
import { useNavigate } from "react-router-dom";
import { resolveLink } from "../lib/linkResolver";
import { BrokenLink } from "../components/BrokenLink";
import "highlight.js/styles/github-dark.css";

interface Props {
  source: string;
  filePath: string;
}

const SAFE_SCHEMA = {
  ...defaultSchema,
  attributes: {
    ...defaultSchema.attributes,
    code: [...(defaultSchema.attributes?.code || []), ["className"]],
    span: [...(defaultSchema.attributes?.span || []), ["className"]],
  },
};

export function MarkdownView({ source, filePath }: Props) {
  const navigate = useNavigate();
  return (
    <div className="markdown-view" data-testid="markdown-view">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[[rehypeSanitize, SAFE_SCHEMA], rehypeHighlight]}
        components={{
          a({ href, children, ...rest }) {
            if (!href) {
              return <BrokenLink cause="file not found">{children}</BrokenLink>;
            }
            const resolved = resolveLink(filePath, href);
            if (resolved.kind === "external") {
              return (
                <a href={resolved.href} target="_blank" rel="noopener noreferrer" {...rest}>
                  {children}
                </a>
              );
            }
            if (resolved.kind === "anchor") {
              return (
                <a href={resolved.href} {...rest}>
                  {children}
                </a>
              );
            }
            if (resolved.kind === "broken") {
              return <BrokenLink cause={resolved.cause || "file not found"}>{children}</BrokenLink>;
            }
            return (
              <a
                href={resolved.href}
                onClick={(e) => {
                  e.preventDefault();
                  navigate(resolved.href);
                }}
                {...rest}
              >
                {children}
              </a>
            );
          },
        }}
      >
        {source}
      </ReactMarkdown>
    </div>
  );
}
