export interface BrokenLinkProps {
  text: string;
  cause: string;
}

export function BrokenLink({ text, cause }: BrokenLinkProps): JSX.Element {
  return (
    <span className="link-broken" aria-disabled="true" title={cause}>
      {text}
    </span>
  );
}
