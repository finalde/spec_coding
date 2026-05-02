import { Link, useLocation } from "react-router-dom";

export interface BreadcrumbProps {
  filePath: string | null;
}

interface Segment {
  label: string;
  href: string | null;
}

function buildSegmentsForFile(filePath: string): Segment[] {
  const parts = filePath.split("/").filter((s) => s !== "");
  if (parts[0] === "CLAUDE.md") {
    return [
      { label: "Settings", href: null },
      { label: "CLAUDE.md", href: null },
    ];
  }
  if (parts[0] === ".claude" && parts[1] === "agents") {
    const fileName = parts[parts.length - 1];
    return [
      { label: "Settings", href: null },
      { label: "Agents", href: null },
      { label: fileName, href: null },
    ];
  }
  if (parts[0] === ".claude" && parts[1] === "skills") {
    const folder = parts[2] ?? "";
    return [
      { label: "Settings", href: null },
      { label: "Skills", href: null },
      { label: folder, href: null },
    ];
  }
  if (parts[0] === "specs" && parts.length >= 5) {
    const [, taskType, taskName, stage, ...rest] = parts;
    const fileName = rest.join("/");
    return [
      { label: taskType, href: null },
      { label: taskName, href: null },
      { label: stage, href: null },
      { label: fileName, href: null },
    ];
  }
  return parts.map((p) => ({ label: p, href: null }));
}

export function Breadcrumb({ filePath }: BreadcrumbProps): JSX.Element | null {
  const location = useLocation();
  if (!filePath) return null;
  const segments = buildSegmentsForFile(filePath);
  return (
    <nav aria-label="Breadcrumb" className="breadcrumb">
      <ol>
        {segments.map((seg, i) => {
          const isLast = i === segments.length - 1;
          if (isLast) {
            return (
              <li key={i} aria-current="page">
                {seg.label}
              </li>
            );
          }
          return (
            <li key={i}>
              {seg.href ? (
                <Link to={seg.href} state={{ from: location.pathname }}>
                  {seg.label}
                </Link>
              ) : (
                <span>{seg.label}</span>
              )}
              <span className="breadcrumb-sep" aria-hidden="true">
                {" "}/{" "}
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
