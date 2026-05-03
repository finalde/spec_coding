import { Link } from "react-router-dom";

export function Breadcrumb({ path }: { path: string }) {
  const segments = path.split("/").filter(Boolean);
  return (
    <nav aria-label="Breadcrumb" className="breadcrumb">
      <ol>
        <li>
          <Link to="/">root</Link>
        </li>
        {segments.map((seg, idx) => {
          const isLast = idx === segments.length - 1;
          const partial = segments.slice(0, idx + 1).join("/");
          return (
            <li key={partial}>
              {isLast ? (
                <span aria-current="page">{seg}</span>
              ) : (
                <Link to={`/file/${partial}`}>{seg}</Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
