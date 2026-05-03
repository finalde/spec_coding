export interface BreadcrumbProps {
  path: string;
}

export function Breadcrumb({ path }: BreadcrumbProps): JSX.Element {
  const parts = path.split("/").filter((p) => p.length > 0);
  return (
    <nav className="breadcrumb" aria-label="Breadcrumb">
      <ol className="breadcrumb-list">
        {parts.map((part, index) => {
          const isLast = index === parts.length - 1;
          return (
            <li key={`${index}-${part}`} className="breadcrumb-item">
              {isLast ? (
                <span aria-current="page" className="breadcrumb-current">
                  {part}
                </span>
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
