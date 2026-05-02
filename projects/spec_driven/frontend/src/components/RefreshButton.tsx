interface RefreshButtonProps {
  onClick: () => void;
  label?: string;
}

export function RefreshButton({
  onClick,
  label = "Refresh",
}: RefreshButtonProps): JSX.Element {
  return (
    <button
      type="button"
      className="refresh-button"
      onClick={onClick}
      aria-label={label}
    >
      &#x21BB; {label}
    </button>
  );
}
