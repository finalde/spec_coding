import { Link } from "react-router-dom";

interface BreadcrumbProps {
  filePath: string;
}

interface Segment {
  label: string;
  href: string | null;
}

function buildSegments(filePath: string): Segment[] {
  // Settings paths
  if (filePath === "CLAUDE.md") {
    return [
      { label: "Settings", href: null },
      { label: "CLAUDE.md", href: null },
      { label: "CLAUDE.md", href: null },
    ];
  }
  if (filePath.startsWith(".claude/skills/agent_team/playbooks/")) {
    const filename = filePath.split("/").pop() ?? filePath;
    return [
      { label: "Settings", href: null },
      { label: "Playbooks", href: null },
      { label: filename, href: null },
    ];
  }
  if (filePath.startsWith(".claude/skills/")) {
    const parts = filePath.split("/");
    const skillName = parts[2] ?? "";
    const filename = parts[parts.length - 1] ?? "";
    return [
      { label: "Settings", href: null },
      { label: "Skills", href: null },
      { label: `${skillName}/${filename}`, href: null },
    ];
  }
  if (filePath.startsWith(".claude/agent_refs/")) {
    const parts = filePath.split("/");
    const stage = parts[2] ?? "";
    const filename = parts[parts.length - 1] ?? "";
    return [
      { label: "Settings", href: null },
      { label: "Agent refs", href: null },
      { label: `${stage}/${filename}`, href: null },
    ];
  }
  // Project paths: specs/{type}/{name}/{stage}/{filename...}
  const segs = filePath.split("/");
  if (segs[0] === "specs" && segs.length >= 5) {
    const taskType = segs[1] ?? "";
    const taskName = segs[2] ?? "";
    const stage = segs[3] ?? "";
    const tail = segs.slice(4).join("/");
    const out: Segment[] = [];
    out.push({ label: taskType, href: null });
    out.push({ label: taskName, href: null });
    out.push({ label: stage, href: null });
    out.push({ label: tail, href: null });
    return out;
  }
  // Fallback: split each
  return segs.map((s) => ({ label: s, href: null }));
}

export function Breadcrumb({ filePath }: BreadcrumbProps): JSX.Element {
  const segments = buildSegments(filePath);
  // The last segment is plain text with aria-current; intermediate segments
  // are links to a prefix path (when applicable to project files).
  const isProject = filePath.startsWith("specs/");
  return (
    <nav aria-label="Breadcrumb" className="breadcrumb">
      <ol className="breadcrumb-list">
        {segments.map((seg, i) => {
          const isLast = i === segments.length - 1;
          if (isLast) {
            return (
              <li key={i} className="breadcrumb-item" aria-current="page">
                {seg.label}
              </li>
            );
          }
          if (isProject && i >= 0 && i <= 2) {
            // build prefix file URL: not always meaningful; render as plain text.
            return (
              <li key={i} className="breadcrumb-item">
                <span className="breadcrumb-text">{seg.label}</span>
                <span className="breadcrumb-sep" aria-hidden="true">
                  /
                </span>
              </li>
            );
          }
          return (
            <li key={i} className="breadcrumb-item">
              <Link to={`/`} className="breadcrumb-link">
                {seg.label}
              </Link>
              <span className="breadcrumb-sep" aria-hidden="true">
                /
              </span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
