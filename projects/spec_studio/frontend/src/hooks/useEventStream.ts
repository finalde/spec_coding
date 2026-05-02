import { useEffect, useRef, useState } from "react";
import type { StreamEvent } from "@/types";

export function useEventStream(taskId: string | undefined, runId: string | undefined) {
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [status, setStatus] = useState<"idle" | "open" | "closed" | "error">("idle");
  const sourceRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!taskId || !runId) return;
    setEvents([]);
    setStatus("idle");
    const url = `/api/tasks/${taskId}/runs/${runId}/events`;
    const es = new EventSource(url);
    sourceRef.current = es;

    es.onopen = () => setStatus("open");
    es.onerror = () => setStatus("error");
    es.onmessage = (msg) => {
      try {
        const ev = JSON.parse(msg.data) as StreamEvent;
        setEvents((prev) => [...prev, ev]);
      } catch {
        // ignore malformed lines
      }
    };

    return () => {
      es.close();
      setStatus("closed");
      sourceRef.current = null;
    };
  }, [taskId, runId]);

  return { events, status };
}
