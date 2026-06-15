# E-commerce ETL + Dashboard — synthetic data → pipeline → dashboard

**Stack:** Python (pandas, plotly), SQLite · **Est:** 15–25 min · **Output:** a SQLite DB + interactive dashboard, all from `make run`

## ✨ 1. Expectation — what you'll get
One `make run` spins up a complete data-engineering loop end to end: 50k realistic synthetic orders are generated (with seasonality, regions, returns, and intentional dirt), cleaned and aggregated through a staged pandas ETL into tidy tables loaded in a real SQLite database, then rendered as a self-contained `dashboard.html` you open in the browser. Inside you get a revenue trend, a working cohort-retention heatmap, top-products and regional breakdowns, a returns rate, and KPIs that actually reconcile against the underlying data.

**Why it's cool:** This isn't a snippet — it's a full generate → ETL → load → dashboard pipeline with proper stage separation and idempotent re-runs, the same shape a real analytics team ships, conjured from a single command.

**Use cases:** A ready-made BI dashboard prototype to demo a stakeholder before any real warehouse exists; a portfolio or interview piece that proves you can wire generate → transform → load → visualize; a sandbox with safe synthetic data for learning cohort-retention math and pandas ETL patterns; and a reusable scaffold you re-point at real order data by swapping out `generate.py`.

## ▶️ 2. How to run
Copy-paste-and-walk-away: drop the prompt below into Claude Code in an empty folder, answer 2 short setup questions, then it builds, runs the pipeline, self-reviews, and opens the dashboard autonomously.
Prerequisites: `pip install pandas plotly numpy` (the prompt runs this). No external data — it's synthesized.

## 🔗 3. Reference & prior art

This prompt is original (written for this library) — not copied from any single source. Real, well-known prior art to compare against and learn the technique from:

**Source:** [plotly/dash-sample-apps](https://github.com/plotly/dash-sample-apps) · **Expected result:** [reference dashboards](https://www.google.com/search?q=ecommerce+analytics+dashboard+plotly&tbm=isch)

---

## 📋 COPY-PASTE PROMPT

```
You are building an end-to-end e-commerce analytics project in Python. Deps limited to
pandas + numpy + plotly (run `pip install pandas numpy plotly` yourself). Provide a single entry
point `python run.py` (and a tiny Makefile with `make run`) that does everything in order.

PHASE 1 — SETUP (ask me these 2 questions, then STOP and wait):
1. Dataset size? (default 50,000 orders)
2. Business flavor? (fashion retailer / electronics store / subscription box) — affects product catalog + seasonality

PHASE 2 — AUTONOMOUS BUILD (after I answer, DO NOT ask anything else; loop until the checklist passes):
Treat the file system as your memory. Each round: implement, RUN the pipeline, read actual output/errors,
self-review against the checklist, fix, repeat.

Project design (clear stage separation):
- generate.py: synthesize realistic orders — customers, products w/ categories + prices, order dates with
  weekly/seasonal patterns, regions, quantities, returns, some intentional dirt (nulls, dup rows, bad types).
- etl.py: clean + transform with pandas → compute monthly revenue, AOV, top products/categories,
  regional breakdown, new-vs-returning, and a monthly cohort-retention matrix. Load tidy tables into SQLite.
- dashboard.py: read from SQLite, build a single self-contained dashboard.html with Plotly:
  revenue trend, cohort-retention heatmap, top-products bar, regional map/bar, returns rate. Clean layout + KPIs.
- run.py orchestrates generate → etl → dashboard. Idempotent (safe to re-run).

ACCEPTANCE CHECKLIST (finish line):
- [ ] `python run.py` (or `make run`) completes with no traceback.
- [ ] A SQLite .db file is created with the expected tidy tables (verify by querying it).
- [ ] dashboard.html is self-contained and opens with all charts rendering real numbers.
- [ ] Cohort-retention heatmap is correct (cohorts on one axis, period on the other, retention %).
- [ ] KPIs (total revenue, AOV, order count, return rate) match the underlying data.
- [ ] Re-running is idempotent (no duplicate-load errors).

STOP CONDITIONS: stop when every item passes, OR after 6 self-review rounds.
Then open dashboard.html and summarize 3 insights the data shows.
```

---

## Remix ideas
"Add a churn-prediction model." · "Add a Streamlit version." · "Add anomaly detection on daily revenue." · "Add an executive PDF export."
