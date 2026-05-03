import type { BrokenLinkCause } from "../types";

export function BrokenLink(props: { children: React.ReactNode; cause: BrokenLinkCause }) {
  return (
    <span
      className="link-broken"
      aria-disabled="true"
      tabIndex={0}
      title={props.cause}
      data-testid="link-broken"
    >
      {props.children}
    </span>
  );
}
