import { useState } from "react";
import type { Pin } from "../types";

export interface PinToggleProps {
  /** The matching pin if this item is currently pinned, else null. */
  pin: Pin | null;
  /** Called to pin this item (no-op if already pinned). */
  onPin: () => Promise<void>;
  /** Called to unpin (no-op if not pinned). */
  onUnpin: (pinId: string) => Promise<void>;
  /** Optional aria-label override; default uses location text. */
  ariaLabel?: string;
}

export function PinToggle({ pin, onPin, onUnpin, ariaLabel }: PinToggleProps): JSX.Element {
  const [busy, setBusy] = useState(false);
  const isPinned = pin !== null;
  const label = ariaLabel ?? (isPinned ? `Unpin (${pin.pin_id})` : "Pin this item");
  const handle = async (): Promise<void> => {
    if (busy) return;
    setBusy(true);
    try {
      if (isPinned) {
        await onUnpin(pin.pin_id);
      } else {
        await onPin();
      }
    } catch {
      // Errors surface through the parent's error path.
    } finally {
      setBusy(false);
    }
  };
  return (
    <button
      type="button"
      className={`pin-toggle${isPinned ? " pin-toggle-on" : ""}`}
      onClick={() => void handle()}
      title={label}
      aria-label={label}
      aria-pressed={isPinned}
      disabled={busy}
    >
      <span aria-hidden="true">{isPinned ? "📌" : "📍"}</span>
      {isPinned && <span className="pin-id-badge">{pin.pin_id}</span>}
    </button>
  );
}
