export interface BreadcrumbProps {
  path: string;
  knownPaths?: string[];
  onNavigate?: (target: string) => void;
}

export function Breadcrumb({ path, knownPaths, onNavigate }: BreadcrumbProps): JSX.Element {
  const parts = path.split("/").filter((p) => p.length > 0);
  const known = knownPaths ? new Set(knownPaths) : null;

  const resolveTarget = (prefix: string, segment: string): string => {
    if (known) {
      const selfNamed = `${prefix}/${segment}.md`;
      if (known.has(selfNamed)) return selfNamed;
    }
    return prefix;
  };

  return (
    <nav className="breadcrumb" aria-label="Breadcrumb">
      <ol className="breadcrumb-list">
        {parts.map((part, index) => {
          const isLast = index === parts.length - 1;
          const prefix = parts.slice(0, index + 1).join("/");
          const target = !isLast ? resolveTarget(prefix, part) : "";
          return (
            <li key={`${index}-${part}`} className="breadcrumb-item">
              {isLast ? (
                <span aria-current="page" className="breadcrumb-current">{part}</span>
              ) : onNavigate ? (
                <button
                  type="button"
                  className="breadcrumb-link"
                  onClick={() => onNavigate(target)}
                  aria-label={`Navigate to ${prefix}`}
                  title={target}
                >
                  {part}
                </button>
              ) : (
                <span className="breadcrumb-segment">{part}</span>
              )}
              {!isLast ? <span className="breadcrumb-sep" aria-hidden="true"> / </span> : null}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
