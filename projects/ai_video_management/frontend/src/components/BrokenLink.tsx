export interface BrokenLinkProps {
  href: string;
  title?: string;
  children: React.ReactNode;
}

export function BrokenLink({ href, title, children }: BrokenLinkProps): JSX.Element {
  const tip = title ?? `Broken link: ${href}`;
  return (
    <span className="broken-link" title={tip} aria-label={tip}>
      {children}
    </span>
  );
}
