import { useMemo, useState } from "react";

import { perfCheckPrompt, perfScore } from "../api";
import { ApiError } from "../types";

interface PerfScorePanelProps {
  path: string;
  content: string;
  onScored: () => Promise<void>;
}

interface ScoreRow {
  scorer: string;
  da_yi: string;
  qing_xu: string;
  guo_huo: string;
  note: string;
}

const AXES: { key: "da_yi" | "qing_xu" | "guo_huo"; label: string; hint: string }[] = [
  { key: "da_yi", label: "表演达意", hint: "物理动作是否被渲出（1 几乎被忽略 → 5 全部 land）" },
  { key: "qing_xu", label: "情绪可识别", hint: "盲看能否认出目标情绪（1 认不出 → 5 一眼即中）" },
  { key: "guo_huo", label: "是否过火", hint: "1 自然克制 → 5 严重过火（越低越好）" },
];

function parseRows(content: string): ScoreRow[] {
  const out: ScoreRow[] = [];
  const idx = content.indexOf("## 实测与验证");
  if (idx === -1) return out;
  for (const line of content.slice(idx).split("\n")) {
    const t = line.trim();
    if (!t.startsWith("|") || t.startsWith("|--") || t.includes("评分者")) continue;
    const cells = t.replace(/^\|/, "").replace(/\|$/, "").split("|").map((c) => c.trim());
    if (cells.length < 5) continue;
    out.push({ scorer: cells[0], da_yi: cells[1], qing_xu: cells[2], guo_huo: cells[3], note: cells[4] });
  }
  return out;
}

function parseVerdict(content: string): { decision: string; verdict: string } {
  const idx = content.indexOf("## 实测与验证");
  const slice = idx === -1 ? content : content.slice(idx);
  const dm = slice.match(/decision:\s*(\w+)/);
  const vm = slice.match(/合议:\s*(.+)/);
  return { decision: dm ? dm[1] : "pending", verdict: vm ? vm[1].trim() : "待评分" };
}

const DECISION_STYLE: Record<string, { bg: string; label: string }> = {
  accept: { bg: "#1f7a3d", label: "✓ 已接受 accept" },
  revise: { bg: "#9a3b2f", label: "✎ 需修改 revise" },
  pending: { bg: "#5a5a5a", label: "… 待评分 pending" },
};

export function PerfScorePanel({ path, content, onScored }: PerfScorePanelProps): JSX.Element {
  const rows = useMemo(() => parseRows(content), [content]);
  const { decision, verdict } = useMemo(() => parseVerdict(content), [content]);
  const claudeRow = rows.find((r) => r.scorer === "Claude");
  const youRow = rows.find((r) => r.scorer === "你");

  const [scores, setScores] = useState<{ da_yi: number | null; qing_xu: number | null; guo_huo: number | null }>({
    da_yi: youRow ? (Number.isNaN(parseInt(youRow.da_yi, 10)) ? null : parseInt(youRow.da_yi, 10)) : null,
    qing_xu: youRow ? (Number.isNaN(parseInt(youRow.qing_xu, 10)) ? null : parseInt(youRow.qing_xu, 10)) : null,
    guo_huo: youRow ? (Number.isNaN(parseInt(youRow.guo_huo, 10)) ? null : parseInt(youRow.guo_huo, 10)) : null,
  });
  const [note, setNote] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const [msg, setMsg] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  const [checkBusy, setCheckBusy] = useState<boolean>(false);
  const [checkPrompt, setCheckPrompt] = useState<string | null>(null);
  const [checkMsg, setCheckMsg] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  const ds = DECISION_STYLE[decision] ?? DECISION_STYLE.pending;

  const checkMp4 = async () => {
    if (checkBusy) return;
    setCheckBusy(true);
    setCheckMsg(null);
    setCheckPrompt(null);
    try {
      const res = await perfCheckPrompt(path);
      if (res.ok) {
        setCheckPrompt(res.prompt);
        setCheckMsg({ kind: "ok", text: res.message });
      } else {
        setCheckMsg({ kind: "err", text: res.message });
      }
    } catch (err) {
      const text = err instanceof ApiError ? `检查失败: ${err.detail?.kind ?? err.status}` : `检查失败: ${err instanceof Error ? err.message : String(err)}`;
      setCheckMsg({ kind: "err", text });
    } finally {
      setCheckBusy(false);
    }
  };

  const copyCheckPrompt = async () => {
    if (checkPrompt) {
      try {
        await navigator.clipboard.writeText(checkPrompt);
        setCheckMsg({ kind: "ok", text: "已复制到剪贴板 — 粘到 Claude Code CLI 执行" });
      } catch {
        /* ignore */
      }
    }
  };

  const save = async () => {
    if (busy) return;
    setBusy(true);
    setMsg(null);
    try {
      const res = await perfScore({
        path, who: "你",
        da_yi: scores.da_yi, qing_xu: scores.qing_xu, guo_huo: scores.guo_huo, note: note.trim(),
      });
      setMsg({ kind: "ok", text: `已记录你的评分 · 合议：${res.verdict}` });
      await onScored();
    } catch (err) {
      const text = err instanceof ApiError ? `保存失败: ${err.detail?.kind ?? err.status}` : `保存失败: ${err instanceof Error ? err.message : String(err)}`;
      setMsg({ kind: "err", text });
    } finally {
      setBusy(false);
    }
  };

  return (
    <section style={{ border: "1px solid var(--border)", borderRadius: 8, padding: 12, margin: "12px 0", background: "var(--bg-panel)", color: "var(--text)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
        <strong>表演评分</strong>
        <span style={{ background: ds.bg, color: "#fff", borderRadius: 12, padding: "2px 10px", fontSize: 12 }}>{ds.label}</span>
        <span style={{ color: "var(--text-muted)", fontSize: 12 }}>{verdict}</span>
      </div>

      <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 10 }}>
        Claude 评分：{claudeRow && claudeRow.da_yi !== "-"
          ? `达意 ${claudeRow.da_yi} / 可识别 ${claudeRow.qing_xu} / 过火 ${claudeRow.guo_huo}${claudeRow.note !== "-" ? ` · ${claudeRow.note}` : ""}`
          : "未评（下载视频后可让 Claude 抽帧评分）"}
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap", marginBottom: 10 }}>
        <button type="button" className="drama-rename-btn" disabled={checkBusy} onClick={checkMp4}>
          {checkBusy ? "检查中…" : "🎬 让 Claude 检查 MP4 并打分"}
        </button>
        {checkPrompt ? <button type="button" className="drama-rename-btn" onClick={copyCheckPrompt}>📋 复制</button> : null}
        {checkMsg ? <span style={{ fontSize: 12, color: checkMsg.kind === "err" ? "#e06c6c" : "#6cc26c" }}>{checkMsg.text}</span> : null}
      </div>
      {checkPrompt ? (
        <textarea readOnly value={checkPrompt} rows={14} style={{ width: "100%", marginBottom: 10, boxSizing: "border-box", fontFamily: "monospace", fontSize: 12, background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 6, padding: 8 }} />
      ) : null}

      {AXES.map((axis) => (
        <div key={axis.key} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
          <span style={{ width: 84, fontSize: 13 }} title={axis.hint}>{axis.label}</span>
          {[1, 2, 3, 4, 5].map((n) => {
            const active = scores[axis.key] === n;
            return (
              <button
                key={n}
                type="button"
                onClick={() => setScores((s) => ({ ...s, [axis.key]: n }))}
                aria-pressed={active}
                style={{
                  width: 30, height: 28, borderRadius: 6, cursor: "pointer",
                  border: active ? "2px solid #2563c9" : "1px solid var(--border)",
                  background: active ? "#2563c9" : "var(--bg)", color: active ? "#fff" : "var(--text)",
                  fontWeight: active ? 700 : 400,
                }}
              >{n}</button>
            );
          })}
        </div>
      ))}

      <textarea
        value={note}
        onChange={(e) => setNote(e.target.value)}
        placeholder="笔记（哪些词 land / 被忽略 / 过火点…）"
        rows={2}
        style={{ width: "100%", marginTop: 6, boxSizing: "border-box", background: "var(--bg)", color: "var(--text)", border: "1px solid var(--border)", borderRadius: 6, padding: 6 }}
      />

      <div style={{ display: "flex", alignItems: "center", gap: 10, marginTop: 8 }}>
        <button
          type="button"
          className="drama-rename-btn"
          disabled={busy || scores.da_yi === null || scores.qing_xu === null || scores.guo_huo === null}
          onClick={save}
        >{busy ? "保存中…" : "保存我的评分"}</button>
        {msg ? <span style={{ fontSize: 12, color: msg.kind === "err" ? "#e06c6c" : "#6cc26c" }}>{msg.text}</span> : null}
      </div>
    </section>
  );
}
