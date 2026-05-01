# Quantitative Analysis — A Self-Guided Tutorial

A book-style tutorial repo for learning how to analyze financial markets with Python.
Each chapter is a self-contained folder with a written lesson (`README.md`) and a
runnable Jupyter notebook (`lesson.ipynb`).

## Curriculum (work in progress)

The path is one coherent sequence aimed at a DIY quant who eventually wants to day-trade NQ futures with a portfolio on the side. Part 1 covers foundations; Parts 2–4 build the academic spine; Parts 5–6 introduce strategies and how to test them honestly; Part 7 teaches realistic execution; Part 8 brings everything to intraday futures; Part 9 takes you live.

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

### Part 3 — Portfolio Construction

| # | Chapter | Topic |
|---|---------|-------|
| 06 | _coming next_ | Portfolio construction: efficient frontier, mean-variance optimization, and risk parity. |

### Part 4 — Modeling Returns

| # | Chapter | Topic |
|---|---------|-------|
| 07 | _planned_ | Linear regression primer: the one piece of inferential statistics the rest of the curriculum leans on. |
| 08 | _planned_ | Factor models: CAPM, Fama–French, and decomposing returns into systematic and idiosyncratic pieces. |
| 09 | _planned_ | Time-varying models: GARCH for volatility clustering, DCC-GARCH for correlation regimes. |
| 10 | _planned_ | Tail risk: extreme value theory, generalized Pareto, copulas, and tail dependence. |

### Part 5 — Strategy Building

| # | Chapter | Topic |
|---|---------|-------|
| 11 | _planned_ | Strategy taxonomy: mean reversion, momentum, trend following, pairs / stat-arb — and where each one's **edge** comes from. |
| 12 | _planned_ | Strategy mechanics: signal generation, **quantifying edge** (expected value per trade, profit factor), position sizing (Kelly, fractional Kelly), risk-of-ruin. |

### Part 6 — Backtesting and Validation

| # | Chapter | Topic |
|---|---------|-------|
| 13 | _planned_ | Backtesting: walk-forward testing, look-ahead bias, transaction costs, and **testing whether an edge is real** vs a data-mining artifact. |

### Part 7 — Execution

| # | Chapter | Topic |
|---|---------|-------|
| 14 | _planned_ | Microstructure and execution: order book, bid/ask, market vs limit orders, slippage models, implementation shortfall. |

### Part 8 — Intraday and Futures

| # | Chapter | Topic |
|---|---------|-------|
| 15 | _planned_ | From daily to intraday: tick data, bar construction (time / volume / dollar / imbalance), intraday seasonality, event windows (FOMC, CPI, NFP). |
| 16 | _planned_ | Futures mechanics: contracts, rolls, basis, margin, mark-to-market — and NQ-specific details (tick size, point value, RTH vs ETH session structure). |
| 17 | _planned_ | Intraday strategies and pitfalls: liquidity-driven mean reversion, news momentum, breakout — and the failure modes that scale worse intraday. |

### Part 9 — Live Trading

| # | Chapter | Topic |
|---|---------|-------|
| 18 | _planned_ | Going live: paper trading, broker APIs, monitoring, kill switches, and the operational side of running real money. |

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
