import { useMemo, useState } from "react";

import { ApiError } from "../types";
import { regenShotPrompt } from "../api";

interface ShotRegenButtonProps {
  path: string;
  content: string;
}

/** On a shot page that references the performance library (`表演库参考:`),
 * assemble a copy-paste regeneration prompt that re-weaves the referenced
 * entries' latest locked blocks into this shot per its plot. */
export function ShotRegenButton({ path, content }: ShotRegenButtonProps): JSX.Element | null {
  const refIds = useMemo(() => {
    const out: string[] = [];
    const re = /表演库参考[:：]\s*(perf_\d{4})/g;
    let m: RegExpExecArray | null;
    while ((m = re.exec(content)) !== null) out.push(m[1]);
    return out;
  }, [content]);

  const [busy, setBusy] = useState(false);
  const [prompt, setPrompt] = useState<string | null>(null);
  const [msg, setMsg] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  if (refIds.length === 0) return null; // only show when the shot references the library

  const run = async () => {
    if (busy) return;
    setBusy(true); setMsg(null); setPrompt(null);
    try {
      const res = await regenShotPrompt(path);
      if (!res.prompt) {
        setMsg({ kind: "err", text: res.message || "无可重生成内容" });
      } else {
        setPrompt(res.prompt);
        setMsg({ kind: "ok", text: `已组装（引用 ${res.refs.join(", ")}）— 复制到 Claude Code 重新融入` });
      }
    } catch (err) {
      setMsg({ kind: "err", text: err instanceof ApiError ? `失败: ${err.detail?.kind ?? err.status}` : `失败: ${err instanceof Error ? err.message : String(err)}` });
    } finally {
      setBusy(false);
    }
  };

  const copy = async () => {
    if (prompt) { try { await navigator.clipboard.writeText(prompt); setMsg({ kind: "ok", text: "已复制到剪贴板" }); } catch { /* ignore */ } }
  };

  return (
    <section style={{ border: "1px solid var(--border)", borderRadius: 8, padding: 12, margin: "12px 0", background: "var(--bg-panel)", color: "var(--text)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap" }}>
        <strong>🎭 按表演库重生成</strong>
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>引用：{refIds.join(", ")}</span>
        <button type="button" className="drama-rename-btn" disabled={busy} onClick={run}>
          {busy ? "组装中…" : "生成重生成 prompt"}
        </button>
        {prompt ? <button type="button" className="drama-rename-btn" onClick={copy}>📋 复制</button> : null}
        {msg ? <span style={{ fontSize: 12, color: msg.kind === "err" ? "#e06c6c" : "#6cc26c" }}>{msg.text}</span> : null}
      </div>
      {prompt ? (
        <textarea readOnly value={prompt} rows={14} style={{ width: "100%", marginTop: 8, boxSizing: "border-box", fontFamily: "monospace", fontSize: 12, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 6, padding: 8 }} />
      ) : null}
    </section>
  );
}
