# Quantitative Analysis — A Self-Guided Tutorial

A book-style tutorial repo for learning how to analyze financial markets with Python.
Each chapter is a self-contained folder with a written lesson (`README.md`) and a
runnable Jupyter notebook (`lesson.ipynb`).

## Curriculum (work in progress)

| # | Chapter | Topic |
|---|---------|-------|
| 01 | [`01-foundations`](./01-foundations) | What is quantitative analysis? Prices, returns, and your first plot. |
| 02 | [`02-risk`](./02-risk) | Risk: volatility clustering and fat tails — how real returns violate Chapter 1's assumptions. |
| 03 | [`03-correlation`](./03-correlation) | Multiple assets: correlation and diversification — pairwise correlation, the diversification math, and how correlations themselves shift across regimes. |
| 04 | _coming next_ | Risk metrics: drawdown, Value at Risk, and the Sharpe ratio — path-dependent risk and risk-adjusted return. |
| 05 | _planned_ | Portfolio construction: efficient frontier, mean-variance optimization, and risk parity. |
| 06 | _planned_ | Factor models: CAPM, Fama–French, and decomposing returns into systematic and idiosyncratic pieces. |
| 07 | _planned_ | Time-varying models: GARCH for volatility clustering, DCC-GARCH for correlation regimes. |
| 08 | _planned_ | Tail risk: extreme value theory, generalized Pareto, copulas, and tail dependence. |
| 09 | _planned_ | Backtesting strategies: walk-forward testing, look-ahead bias, transaction costs — the capstone. |

## How to use this repo

1. Read the chapter's `README.md` end-to-end — that's the lesson text.
2. Open `lesson.ipynb` in Jupyter and run the cells from top to bottom.
3. Try the **Exercises** at the bottom of each chapter before moving on.

## Setup (one-time)

This guide uses **Python 3.14** in a **virtual environment** (a self-contained Python install for this project, so its packages don't collide with anything else on your machine) managed by **`uv`** (a fast modern replacement for `pip` + `venv`). If you've never set this up before, the steps below get you from a fresh machine to a running notebook.

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

Verify the install: `uv --version` should print something like `uv 0.9.x`.

### 2. Create the virtual environment

From the repo root:

```bash
uv venv --python 3.14
```

This creates a `.venv/` directory with a Python 3.14 interpreter. **If Python 3.14 isn't already on your machine, `uv` will download and install it automatically** — no separate Python install step needed.

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
