# CSV Insight Engine — point it at any CSV, get an analyst report

**Stack:** Python (pandas, plotly) · **Est:** 10–20 min · **Output:** an interactive HTML report from *your* data

## ✨ 1. Expectation — what you'll get
Point this at any CSV and a single `python insight.py <path.csv>` builds a polished, self-contained `report.html` you open straight in a browser — every column auto-profiled with inferred semantic types, missing-data flags, a correlation heatmap, outlier detection, and auto-detected datetime trends. The centerpiece is a plain-English "Key findings" section that reads like an analyst's notes on *your actual data* ("Column X is 38% null", "A and B correlate at 0.81", "12 price outliers"), all wired into working interactive Plotly charts.

**Why it's cool:** It's the closest thing to "hire a data analyst for one prompt" — and it works on an arbitrary CSV with zero hardcoded column names, inferring structure and writing the narrative itself.

**Use cases:** Fast first-pass EDA on a messy CSV that just landed in your inbox before you commit to deeper analysis; a one-click profiling report to hand a stakeholder who won't open a notebook; a reusable triage template you keep in your toolkit and re-point at every new dataset; and learning auto-EDA mechanics (type inference, IQR/z-score outliers, correlation surfacing) by reading clean, framework-free pandas code.

## ▶️ 2. How to run
Copy-paste-and-walk-away: drop the prompt below into Claude Code in an empty folder, answer 2 short setup questions, then it builds, runs on a CSV, self-reviews, and opens the report autonomously.
Prerequisites: `pip install pandas plotly` (the prompt runs this). Bring any CSV — or let it generate a demo one.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [ydata-profiling/ydata-profiling](https://github.com/ydata-profiling/ydata-profiling) · **Expected result:** [example auto-EDA report](https://docs.profiling.ydata.ai/latest/)

---

## 📋 COPY-PASTE PROMPT

```
You are building a reusable "CSV insight engine": a Python tool that ingests ANY CSV and produces
an interactive, self-contained HTML analyst report. Dependencies limited to pandas + plotly
(run `pip install pandas plotly` yourself). Provide a single command to run it: `python insight.py <path.csv>`.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Do you have a CSV to point it at? Paste a path, OR say "generate a demo" and I'll synthesize a
   realistic messy dataset (e-commerce orders with nulls, mixed types, outliers) to showcase it.
2. Report depth? (quick-overview / deep-dive with correlations + outliers + per-column profiles)

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN it on the target CSV, read the actual
output/errors, self-review against the checklist, fix, repeat.

Tool design:
- Robust CSV loading (encoding/delimiter sniffing, graceful on bad rows).
- Per-column profiling: inferred semantic type (numeric/categorical/datetime/text/id/boolean),
  missing %, cardinality, min/max/mean/median, top values, simple distribution.
- Dataset-level: shape, memory, duplicate rows, correlation heatmap (numeric), outlier flags (IQR/z-score),
  and auto-detected datetime columns → trend charts.
- Plain-English "Key findings" section generated from the stats (e.g. "Column X is 38% null",
  "A and B are strongly correlated (0.81)", "12 outliers in price").
- Output: one self-contained report.html with embedded Plotly charts and a clean layout. Opens standalone.
- Must work on an arbitrary CSV, not just the demo — no hardcoded column names.

ACCEPTANCE CHECKLIST (finish line):
- [ ] `python insight.py <csv>` runs end-to-end on the target file with no traceback.
- [ ] report.html is self-contained and opens with working interactive charts.
- [ ] Every column gets a profile; types are inferred sensibly.
- [ ] Correlation heatmap + outlier detection + any datetime trends render.
- [ ] "Key findings" reads like real analyst notes derived from the actual data.
- [ ] Re-running on a DIFFERENT CSV (try a second one or a synthesized variant) also works.

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open report.html and summarize the top 3 findings it produced.
```

---

## Remix ideas
"Add automatic chart-type selection per column." · "Add a data-quality score." · "Add a 'suggested cleaning steps' section." · "Make it accept Excel files too."
