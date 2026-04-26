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

Install the required packages:

```bash
pip install -r requirements.txt
```

Then launch Jupyter:

```bash
jupyter notebook
```

A browser tab will open. Navigate into `01-foundations/` and open `lesson.ipynb`.
