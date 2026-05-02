import { useCallback, useEffect, useState } from "react";
import { addPromotion, fetchPromotions, removePromotion } from "./api";
import type { Pin } from "./types";

const PROMOTABLE_STAGES = new Set([
  "interview",
  "findings",
  "final_specs",
  "validation",
]);

/**
 * Given a full file path like `specs/development/spec_driven/interview/qa.md`,
 * returns the stage directory `specs/development/spec_driven/interview` if the
 * file lives inside a promotable stage, else null.
 */
export function stagePathFor(filePath: string): string | null {
  const parts = filePath.split("/");
  if (parts.length < 5) return null;
  if (parts[0] !== "specs") return null;
  const stage = parts[3];
  if (!PROMOTABLE_STAGES.has(stage)) return null;
  return parts.slice(0, 4).join("/");
}

/**
 * Returns a content fingerprint used to match a generated atomic unit against
 * a pin's body. Matches on the normalized first 80 non-whitespace characters.
 */
export function fingerprint(text: string): string {
  return text
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, 80)
    .toLowerCase();
}

export interface UsePromotions {
  pins: ReadonlyArray<Pin>;
  loaded: boolean;
  isPinned: (itemBody: string) => Pin | null;
  pin: (location: string, body: string) => Promise<void>;
  unpin: (pinId: string) => Promise<void>;
  refresh: () => Promise<void>;
  error: string | null;
}

export function usePromotions(stagePath: string | null): UsePromotions {
  const [pins, setPins] = useState<Pin[]>([]);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!stagePath) {
      setPins([]);
      setLoaded(true);
      return;
    }
    try {
      const r = await fetchPromotions(stagePath);
      setPins(r.pins);
      setError(null);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoaded(true);
    }
  }, [stagePath]);

  useEffect(() => {
    setLoaded(false);
    void refresh();
  }, [refresh]);

  const isPinned = useCallback(
    (itemBody: string): Pin | null => {
      const fp = fingerprint(itemBody);
      for (const p of pins) {
        if (fingerprint(p.body) === fp) return p;
      }
      return null;
    },
    [pins],
  );

  const pin = useCallback(
    async (location: string, body: string): Promise<void> => {
      if (!stagePath) return;
      try {
        const newPin = await addPromotion(stagePath, location, body);
        setPins((prev) => [...prev, newPin]);
        setError(null);
      } catch (e) {
        setError(String(e));
        throw e;
      }
    },
    [stagePath],
  );

  const unpin = useCallback(
    async (pinId: string): Promise<void> => {
      if (!stagePath) return;
      try {
        await removePromotion(stagePath, pinId);
        setPins((prev) => prev.filter((p) => p.pin_id !== pinId));
        setError(null);
      } catch (e) {
        setError(String(e));
        throw e;
      }
    },
    [stagePath],
  );

  return { pins, loaded, isPinned, pin, unpin, refresh, error };
}
