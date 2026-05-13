# Quantitative Analysis — A Self-Guided Tutorial

A book-style tutorial repo for learning how to analyze financial markets with Python.
Each chapter is a self-contained folder with a written lesson (`README.md`) and a
runnable Jupyter notebook (`lesson.ipynb`).

## Curriculum (work in progress)

The path is one coherent sequence aimed at a DIY quant whose goal is **sub-session intraday futures trading** — entries and exits within a single session, flat by close, with NQ as the eventual target instrument. Part 1 covers foundations and risk-adjusted performance on daily bars; Parts 5–9 pivot to intraday: data substrate, strategy taxonomy, your first runnable strategy, three chapters on backtesting honestly, two on execution realism (costs and microstructure), then sizing, regime detection, more strategies, futures mechanics, and going live.

An earlier version of this curriculum (commits before 2026-05-07) included a portfolio-and-measurement track at Ch6-10. Those chapters were retired in the 2026-05-07 pivot to focus on intraday futures.


### Part 1 — Foundations

| # | Chapter | Topic |
|---|---------|-------|
| 01 | [`01-foundations`](./01-foundations) | What is quantitative analysis? Prices, returns, and your first plot. |
| 02 | [`02-risk`](./02-risk) | Risk: volatility clustering and fat tails — how real returns violate Chapter 1's assumptions. |
| 03 | [`03-correlation`](./03-correlation) | Multiple assets: correlation and diversification — pairwise correlation, the diversification math, and how correlations themselves shift across regimes. |

### Part 2 — Risk-Adjusted Performance

| # | Chapter | Topic |
|---|---------|-------|
| 04 | [`04-expected-returns`](./04-expected-returns) | Estimating expected returns: historical mean, shrinkage, and why estimating return is the hard problem in finance. |
| 05 | [`05-risk-metrics`](./05-risk-metrics) | Risk metrics: drawdown, VaR / CVaR, and the Sharpe ratio — three flavors of risk metric, with honest CIs that show two strategies whose point Sharpes differ by 0.2 are statistically indistinguishable at 20-year sample sizes. |

### Part 5 — Intraday Foundations

| # | Chapter | Topic |
|---|---------|-------|
| 06 | [`06-bridge-to-intraday`](./06-bridge-to-intraday) | Bridge: daily bars → intraday data — Alpaca free-tier setup, bar construction (time / volume / dollar / imbalance), the QQQ intraday U-shape, FOMC overlay, RTH/ETH session structure, IEX-feed bar gaps. The first chapter on the post-pivot intraday spine. |
| 07 | [`07-strategy-taxonomy`](./07-strategy-taxonomy) | Strategy taxonomy: where edges come from — four families (mean reversion / momentum / breakout / event-driven) framed by mechanism, expectancy as the only operational definition of edge, and a lag-*k* autocorrelation hook on QQQ identifying that mean-reversion is cleanest in the closing 30 minutes. Sets up Ch8's first runnable strategy. |
| 08 | [`08-first-edge`](./08-first-edge) | Your first edge: intraday mean reversion on QQQ — idea (Ch7's lag-1 finding) → signal (regression β̂ = −0.064, t = −3.11 on closing-30-min N=1, K=3) → naive backtest (vectorized, no costs, in-sample Sharpe +2.08). Intentionally inflated; Ch9-11 + Ch12 deflate it. |

### Part 6 — Backtesting (the discipline)

| # | Chapter | Topic |
|---|---------|-------|
| 09 | [`09-backtesting-honest`](./09-backtesting-honest) | Backtesting I — Building an honest backtest: rebuilds Ch8's vectorized strategy as a single-position event-driven loop with point-in-time fills, runs three execution timings (same-bar bug → next-open right answer → next-close pessimistic), strips the in-sample Sharpe from Ch8's +2.08 to about +0.80, and bootstraps the trade ledger to a 95% CI of (−1.3, +2.7) that comfortably includes zero — even honest mechanics don't make this a "real" strategy on a single year of data. |
| 10 | [`10-backtesting-bias`](./10-backtesting-bias) | Backtesting II — Bias and data integrity: look-ahead bias on the entry-threshold σ (whole-sample +0.82 vs trailing +1.64 — bias can move Sharpe in either direction), survivorship bias named-only, snooping with a 21-point parameter sweep where the best in-sample Sharpe (+1.86) fails even uncorrected significance let alone Bonferroni (best |t|=1.84 vs corrected critical 3.04). |
| 11 | [`11-walk-forward`](./11-walk-forward) | Backtesting III — Walk-forward and statistical validation: train/test split with deflation factor 0.28 (IS +1.65 → OOS +0.46), 10-window monthly walk-forward (concat OOS Sharpe +0.88) with parameter swings of 3.5× across windows, block-bootstrap CI on both trade-ledger and daily-PnL aggregations (all CIs straddle zero); closes the Ch8→Ch11 deflation arc from +2.08 to +0.88, statistically indistinguishable from random on a single year. |

### Part 7 — Execution Realism

| # | Chapter | Topic |
|---|---------|-------|
| 12 | [`12-costs-slippage-capacity`](./12-costs-slippage-capacity) | Costs, slippage, and capacity: Roll's and Corwin-Schultz half-spread estimators (0.72 bp on QQQ, agreeing within 10%), commission references (PFOF vs IBKR tiered), square-root impact law, cost-aware threshold optimization (k\*=0.70 cost-naive → k\*=2.20 cost-aware), and capacity Q\* — closes the Ch8→Ch11 deflation arc with after-cost Sharpe = −2.97 and capacity Q\* = $0. The strategy does not exist as a tradable edge. |
| 13 | [`13-microstructure-execution`](./13-microstructure-execution) | Microstructure and execution: order types (market/limit/IOC/FOK/marketable-limit/hidden/pegged), maker-taker economics, PFOF; passive-limit simulation on the Ch12 cost-aware MR strategy (fill rate 89%, pre-toxicity Sharpe +0.58); adverse-selection diagnostic (toxicity = drift_unconditional − drift_filled = 0.17 bp; unfilled-bucket drift +8.1 bp — the self-cancelled winners); latency as resolution-dependent cost (4% of bar σ at 1-min/100ms → 45% at 1-sec/200ms); maker rebate (0.043 bp/leg on QQQ). Closes the execution arc: −2.97 (market orders) → −1.11 (passive entry + rebate). Passive execution narrows the loss by ~1.9 Sharpe points but does not cross zero — the exit leg still pays the wedge. |

### Part 8 — Sizing, Regime, More Strategies

| # | Chapter | Topic |
|---|---------|-------|
| 14 | _planned_ | Position sizing and risk of ruin: Kelly, fractional Kelly, drawdown caps; EVT-based tail estimation when losses are fat-tailed. |
| 15 | _planned_ | Intraday vol and regime detection: GARCH(1,1) on intraday data, EWMA, FOMC/CPI/NFP windows, vol-targeting and regime-aware sizing. |
| 16 | _planned_ | More strategies: momentum, breakout, event-driven — each evaluated through the full Ch09–14 discipline. |

### Part 9 — Futures and Going Live

| # | Chapter | Topic |
|---|---------|-------|
| 17 | _planned_ | Futures mechanics and NQ specifics: contracts, expiry, rolls, basis, margin, mark-to-market, tick size, point value, RTH vs ETH. |
| 18 | _planned_ | Going live: paper → real — broker APIs, monitoring, kill switches, operational risk, when to pull a strategy that diverges from its backtest. |

## How to use this repo

1. Read the chapter's `README.md` end-to-end — that's the lesson text.
2. Open `lesson.ipynb` in Jupyter and run the cells from top to bottom.
3. Try the **Exercises** at the bottom of each chapter before moving on.

## Setup (one-time)

This guide uses a recent **Python (3.11 or newer)** in a **virtual environment** (a self-contained Python install for this project, so its packages don't collide with anything else on your machine) managed by **`uv`** (a fast modern replacement for `pip` + `venv`). If you've never set this up before, the steps below get you from a fresh machine to a running notebook.

### 1. Install `uv`

`uv` is a single command-line tool that handles Python versions, virtual environments, and package installs.

- **macOS / Linux:**
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Or via pip** (if you already have Python installed):
  ```bash
  pip install uv
  ```

Verify the install: `uv --version` should print something like `uv 0.9.x` or newer.

### 2. Create the virtual environment

From the repo root:

```bash
uv venv
```

This creates a `.venv/` directory with a recent Python interpreter. **If you don't have a compatible Python on your machine, `uv` will download and install one automatically** — no separate Python install step needed.

If you'd like to pin a specific version (e.g. for reproducibility across collaborators), pass `--python 3.12` (or `3.11`, `3.13`, `3.14`, etc.) instead — anything 3.11+ works for this project.

### 3. Install the project's dependencies

```bash
uv pip install -r requirements.txt
```

This installs `jupyter`, `numpy`, `pandas`, `matplotlib`, `yfinance`, and `scipy` into the venv.

### 4. Launch Jupyter

```bash
# macOS / Linux:
.venv/bin/jupyter lab

# Windows:
.venv\Scripts\jupyter lab
```

A browser tab will open. Navigate into `01-foundations/` and open `lesson.ipynb`.

### Troubleshooting

- **`ModuleNotFoundError` when running a cell** — your Jupyter kernel isn't using the venv's Python. Make sure you launched Jupyter via `.venv/bin/jupyter lab` (not a system-wide `jupyter`). Inside Jupyter you can verify with **Kernel → Change Kernel** and picking the Python from `.venv/`.
- **`pip install` ran but Jupyter still can't import packages** — that probably installed packages to your *system* Python, not the venv. Always use `uv pip install` for this project (or activate the venv first with `source .venv/bin/activate` on macOS/Linux, `.venv\Scripts\activate` on Windows).
- **Adding a new package later** — `uv pip install <package>` from the repo root puts it in the venv. Then add the name to `requirements.txt` so future setups install it too.
