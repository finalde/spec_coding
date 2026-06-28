/** Shared toast announcer.
 *
 * Writes to the single `#aria-live-toast` div mounted in App.tsx so screen
 * readers re-announce the message (aria-live="polite"), and toggles a
 * `.is-visible` class so sighted users see a styled chip in the top-right.
 * Auto-clears after a TTL — re-firing while still visible resets the clock
 * and re-announces (the empty-string interlude is what makes SRs re-read).
 *
 * Before follow-up 060 the live region was screen-reader-only (offscreen),
 * so empty-output paths (e.g. "concat shot characters" with zero usable
 * character video.mp4 files) looked silent to sighted users.
 */
const REGION_ID = "aria-live-toast";
const VISIBLE_CLASS = "is-visible";
const DEFAULT_TTL_MS = 4500;

let clearTimer: number | null = null;

export function announceToast(message: string, ttlMs: number = DEFAULT_TTL_MS): void {
  const region = document.getElementById(REGION_ID);
  if (!region) return;
  region.textContent = "";
  region.classList.remove(VISIBLE_CLASS);
  // tiny delay so screen readers treat this as a fresh announcement
  window.setTimeout(() => {
    region.textContent = message;
    region.classList.add(VISIBLE_CLASS);
  }, 30);
  if (clearTimer !== null) {
    window.clearTimeout(clearTimer);
  }
  clearTimer = window.setTimeout(() => {
    region.textContent = "";
    region.classList.remove(VISIBLE_CLASS);
    clearTimer = null;
  }, ttlMs);
}
