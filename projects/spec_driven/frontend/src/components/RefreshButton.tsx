export interface RefreshButtonProps {
  onClick: () => void;
  label?: string;
}

export function RefreshButton({ onClick, label = "Refresh sidebar" }: RefreshButtonProps): JSX.Element {
  return (
    <button type="button" className="refresh-button" onClick={onClick} aria-label={label}>
      ↻ {label}
    </button>
  );
}
