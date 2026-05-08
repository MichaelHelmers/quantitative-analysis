# Quantitative Analysis — A Self-Guided Tutorial

A book-style tutorial repo for learning how to analyze financial markets with Python.
Each chapter is a self-contained folder with a written lesson (`README.md`) and a
runnable Jupyter notebook (`lesson.ipynb`).

## Curriculum (work in progress)

The path is one coherent sequence aimed at a DIY quant whose goal is **sub-session intraday futures trading** — entries and exits within a single session, flat by close, with NQ as the eventual target instrument. Part 1 covers foundations and risk-adjusted performance on daily bars; Parts 5–9 pivot to intraday: data substrate, strategy taxonomy, your first runnable strategy, three chapters on backtesting honestly, two on execution realism (costs and microstructure), then sizing, regime detection, more strategies, futures mechanics, and going live.

For the curriculum-pivot rationale and full per-chapter scope sketches, see [`docs/superpowers/specs/2026-05-07-curriculum-pivot-design.md`](./docs/superpowers/specs/2026-05-07-curriculum-pivot-design.md).


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
| 06 | _planned_ | Bridge: daily bars → intraday data — sources, bar construction (time / volume / dollar / imbalance), intraday seasonality, event windows (FOMC, CPI, NFP), session structure. |
| 07 | _planned_ | Strategy taxonomy: where edges come from — mean reversion, momentum, breakout, event-driven. Frame each by its edge mechanism. |
| 08 | _planned_ | Your first edge: intraday mean reversion on SPY — idea → signal → naive backtest, with regression for signal generation introduced inline. |

### Part 6 — Backtesting (the discipline)

| # | Chapter | Topic |
|---|---------|-------|
| 09 | _planned_ | Backtesting I — Building an honest backtest: vectorized vs event-driven, point-in-time data, fill assumptions, trade-level metrics. |
| 10 | _planned_ | Backtesting II — Bias and data integrity: look-ahead bugs, survivorship, train-on-test leakage, snooping, in-sample fitting. |
| 11 | _planned_ | Backtesting III — Walk-forward and statistical validation: train/test discipline, walk-forward optimization, parameter stability, the data-mining trap, bootstrap CI on trade PnL. |

### Part 7 — Execution Realism

| # | Chapter | Topic |
|---|---------|-------|
| 12 | _planned_ | Costs, slippage, and capacity: cost models, slippage curves, capacity limits — re-running Ch08 with stacked cost models and watching the Sharpe collapse. |
| 13 | _planned_ | Microstructure and execution: order book mechanics, bid/ask, market vs limit orders, implementation shortfall. |

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
