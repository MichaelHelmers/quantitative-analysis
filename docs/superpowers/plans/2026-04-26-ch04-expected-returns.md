# Chapter 4 Implementation Plan — Estimating Expected Returns

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Chapter 4 of the quant-analysis tutorial — paired notebook + README — covering the long-run unconditional flavor of expected return: the sample mean as estimator, its standard error, the wide CI that 20 years of data still leaves, subsample instability, and shrinkage as the practitioner-grade remedy.

**Architecture:** Single chapter folder `04-expected-returns/`. Same 8-ticker basket as Ch3 for continuity. New vocabulary appended to root `glossary.md`. No shared module — each chapter remains self-contained.

**Tech Stack:** Python 3.11+, pandas, numpy, matplotlib, yfinance, scipy.stats. **No new dependencies** — all already in `requirements.txt`.

**Verification model:** Same as Ch2/Ch3 — every notebook cell runs without error; outputs match expected numerical ranges; README and notebook render correctly in markdown preview / Jupyter Lab.

**Commit policy:** User authorizes commits explicitly. Plan ends each task with "checkpoint — pause"; bundle commits at natural boundaries.

**Spec reference:** `docs/superpowers/specs/2026-04-26-ch04-expected-returns-design.md`

---

## File map

| File | Status | Responsibility |
| --- | --- | --- |
| `04-expected-returns/` | create | Chapter folder. |
| `04-expected-returns/lesson.ipynb` | create | Runnable companion notebook. |
| `04-expected-returns/README.md` | create | Canonical narrative. |
| `glossary.md` | modify | Append Ch4 entries. |
| `03-correlation/README.md` | modify | Reword "Up next" to point to Ch4. |
| `README.md` (root) | modify | Update curriculum table: Ch4 row from "_coming next_" to title + link. |
| Memory `project_curriculum_roadmap.md` | modify | Mark Ch04 done. |

---

## Task 1: Set up Chapter 4 directory and verify dependencies

**Files:**
- Create: `04-expected-returns/` (directory)

- [ ] **Step 1.1: Create the chapter directory**

Run: `mkdir -p 04-expected-returns`

- [ ] **Step 1.2: Verify all dependencies are still installed**

Run: `/home/test/repos/quantitative-analysis/.venv/bin/python -c "import numpy, pandas, matplotlib, yfinance, scipy; from scipy import stats; print('all deps available')"`

Expected output: `all deps available`

- [ ] **Step 1.3: Quick verification of `scipy.stats.norm.ppf`**

Run: `/home/test/repos/quantitative-analysis/.venv/bin/python -c "from scipy import stats; print(round(stats.norm.ppf(0.975), 4))"`

Expected output: `1.96`

- [ ] **Step 1.4: Checkpoint** — pause.

---

## Task 2: Build the full notebook

**Files:**
- Create: `04-expected-returns/lesson.ipynb`

This task uses a builder script (proven pattern from Ch2 and Ch3). The script lives in the project root and is deleted after the notebook is built.

- [ ] **Step 2.1: Write the builder script `build_ch4_notebook.py` to the project root**

The full script content is below. It enumerates ~38 cells in chapter order.

```python
"""Build the complete 04-expected-returns/lesson.ipynb from a cell list."""
import json
from pathlib import Path

cells = []

def md(cell_id, source):
    cells.append({
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": source.splitlines(keepends=True),
    })

def code(cell_id, source):
    cells.append({
        "cell_type": "code",
        "execution_count": None,
        "id": cell_id,
        "metadata": {},
        "outputs": [],
        "source": source.splitlines(keepends=True),
    })

# --- intro and concept-flavors framing
md("intro", """# Chapter 4 — Estimating Expected Returns

Read the chapter [`README.md`](./README.md) first. This notebook is the runnable companion.

Three chapters spent on risk; zero on return. This chapter fills the gap. The reader leaves with two related findings: (1) historical mean as an estimator of true expected return is **brutally noisy** at any reasonable sample size, and (2) **shrinkage toward a prior** is the standard remedy. Both findings honestly inform Chapter 5's Sharpe ratio.""")

md("framing", """## What we mean by "expected return"

When this chapter says "expected return," it doesn't mean a single thing. There are at least four flavors that don't reduce to each other:

1. **Realized return** — what *actually happened* over some past window. Not an expectation at all — it's the **data** we use as input.
2. **Long-run / unconditional expected return** — "what's the asset's true average return over a long period?" A single number characterizing the data-generating process. **(This chapter, §2 + §3.)**
3. **Conditional / forecast expected return** — "given what we know *right now*, what's *next* period's expected return?" A prediction that varies day-to-day. *Deferred — Ch11–12 (strategy edge).*
4. **Equilibrium / required return** — "given the asset's risk and factor exposures, what *should* its expected return be?" *Deferred — Ch8 (CAPM, Fama–French).*

When the rest of this chapter says "expected return," read it as the **long-run unconditional flavor**. Same disclaimer pattern Ch2 and Ch3 used.""")

# --- §1 setup
md("s1-header", """## 1. Setup and data refresh

Same library stack and same 8-ticker basket as Chapter 3. We re-pull the data and compute log returns; the only new operation in this chapter is the sample mean and its standard error.""")

code("s1-imports", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy import stats

print(f"numpy   {np.__version__}")
print(f"pandas  {pd.__version__}")
print(f"yf      {yf.__version__}")""")

code("s1-download", """tickers = ["SPY", "TLT", "GLD", "XLK", "XLF", "XLE", "XLV", "XLU"]
data = yf.download(tickers, period="20y", progress=False)
prices = data["Close"][tickers]
log_returns = np.log(prices / prices.shift(1)).dropna()

n_obs = len(log_returns)
print(f"shape: {log_returns.shape}")
print(f"date range: {log_returns.index.min().date()} to {log_returns.index.max().date()}")
print(f"observations per asset: {n_obs:,}")""")

md("s1-realized-vs-expected", """### Realized vs expected — keep them straight

The cell below computes the **mean of realized returns** for each asset. That is *not* the same as the asset's *expected* return. Realized return is the data; expected return is the underlying parameter we're trying to estimate. Most of this chapter is about the gap between those two ideas.""")

code("s1-realized-mean", """daily_mean = log_returns.mean()
ann_mean = daily_mean * 252  # annualize: means add over time, multiply by trading days

summary = pd.DataFrame({
    "daily mean (log)":   daily_mean,
    "annualized mean":    ann_mean,
    "annualized vol":     log_returns.std() * np.sqrt(252),
})
summary""")

# --- §2 the naive estimator and its noise
md("s2-header", """## 2. Part I — The naive estimator and its noise

The natural estimator of an asset's expected return is the **sample mean** — just average the realized returns you have.

> *μ̂* = (1/N) Σᵢ *rᵢ*

where:
- *rᵢ* — the realized log return on day *i*. **Units:** decimal fraction per day (e.g., 0.005 means a 0.5% daily return). Daily, not annualized.
- *N* — the number of observations in the sample.
- *μ̂* — the sample-mean estimator. **Units:** same as *rᵢ* (per day) unless explicitly annualized.

> **Foot-gun: annualizing a mean.** To go from daily to annualized, **multiply by 252** (means *add* over independent time periods). This is *different* from the std/vol annualization rule from Ch1, which used **× √252** (variances add; standard deviations scale by √t). Don't conflate them: mean × 252, std × √252, variance × 252.""")

md("s2_2-lead", """### 2.2 Standard error of the mean

The sample mean is an *estimator*. Like any estimator, it has its own sampling distribution — different samples of the same population give different *μ̂* values. The width of that sampling distribution is the **standard error**:

> *SE(μ̂)* = *σ* / √N

where:
- *σ* — the standard deviation of the underlying data (same units as the data).
- *N* — sample size.
- *SE(μ̂)* — standard deviation of the sampling distribution of the sample mean. **Units:** same as *μ̂*.

> **Foot-gun: SE shrinks like √N, not N.** Doubling sample size only reduces SE by √2 ≈ 1.41×. Quadrupling N halves SE. This is *aggressively diminishing returns* — and it's why even decades of data leave wide CIs on expected return.

> **Foot-gun: annualizing SE.** Treat SE the same way you treat the mean: **× 252** to annualize (since SE is in the *same units as the mean*, and means scale linearly with time horizon). Do not use √252.

A 95% confidence interval (assuming approximate normality of the sample mean — justified by the Central Limit Theorem for large *N*, even though individual returns are fat-tailed):

> *CI₉₅* = *μ̂* ± 1.96 · *SE(μ̂)*

The 1.96 is the 0.975 quantile of the standard normal distribution. Compute SPY's 95% CI from the full 20-year window:""")

code("s2_2-code", """daily_mean_spy = log_returns["SPY"].mean()
daily_std_spy  = log_returns["SPY"].std()
n              = len(log_returns)

se_daily = daily_std_spy / np.sqrt(n)
se_ann   = se_daily * 252                           # multiply by 252 (NOT sqrt-252)

mean_ann   = daily_mean_spy * 252
ci_low_ann = mean_ann - 1.96 * se_ann
ci_hi_ann  = mean_ann + 1.96 * se_ann

print(f"N (observations):                 {n:,}")
print(f"SPY annualized mean:              {mean_ann:.2%}")
print(f"SPY annualized SE of the mean:    {se_ann:.2%}")
print(f"95% CI on annualized mean:        [{ci_low_ann:.2%}, {ci_hi_ann:.2%}]")
print(f"CI width:                         {ci_hi_ann - ci_low_ann:.2%}")""")

md("s2_2-interp", """Read the numbers. Twenty years of daily SPY data — over 5,000 observations — and the 95% confidence interval on the annualized mean is **roughly 17 percentage points wide**. The point estimate is around 10% per year, but the data is statistically consistent with anywhere from ~1.5% to ~18.5%.

That's a brutal range. We can't tell a "barely beats T-bills" market from "doubles in 4 years" with any reasonable confidence — and this is *with twenty years of data*. For shorter samples the situation is worse, by exactly √(years).""")

md("s2_3-lead", """### 2.3 Subsample stability — same data, different windows

A different angle on the same problem: pick disjoint sub-windows of the same data and compute the sample mean on each. If the long-run mean were a stable property of the asset, the sub-window means would cluster tightly. They don't.""")

code("s2_3-code", """spy = log_returns["SPY"]
window_years = 5

start_year = spy.index.year.min()
end_year   = spy.index.year.max()

rows = []
for y0 in range(start_year, end_year, window_years):
    y1 = y0 + window_years - 1
    window = spy.loc[str(y0):str(y1)]
    if len(window) < 252:  # skip incomplete tail windows
        continue
    rows.append({
        "window":              f"{y0}-{y1}",
        "n days":              len(window),
        "annualized mean":     f"{window.mean() * 252:.2%}",
        "annualized vol":      f"{window.std() * np.sqrt(252):.2%}",
    })

pd.DataFrame(rows)""")

md("s2_3-interp", """The annualized mean varies by 5–10 percentage points across disjoint 5-year windows of the same asset. Some windows include the 2008 crisis or the 2022 selloff and look terrible; others are squarely in calm bull markets and look great. **None of them is "wrong"** — they're all valid sample means of real data — but the spread is exactly the noise the standard error formula was telling us about, made visceral.""")

md("s2_4-dollars", """### 2.4 What this means with $100k

A reader sizing a position based on "SPY returns 10% per year" needs to know that, statistically:
- The point estimate is ~10% from the 20-year sample.
- The 95% CI is roughly **1.5% to 18.5% per year** (annualized).
- On a $100k position, that's anywhere from "~$1,500 above T-bills per year" to "~$18,500 per year." Both ends of the range are statistically consistent with the same 20 years of data.

Two practical takeaways before we move on:
1. **Don't confuse a point estimate with the truth.** The 10% headline number is the *center* of a wide distribution, not a fact.
2. **The next chapter's Sharpe ratio inherits this uncertainty.** A 0.5 reported Sharpe with 20 years of data has its own large CI; "is this strategy any good?" can't be answered just from the point estimate.""")

# --- §3 shrinkage
md("s3-header", """## 3. Part II — Shrinkage: pulling estimates toward a prior

Section 2 showed that *each individual* sample mean is noisy. Counterintuitive fact: **even though the sample mean is *unbiased* for any single asset, you can do better in *aggregate* by deliberately introducing a small bias.** Each estimate gets pulled toward a common prior; in exchange, the total mean-squared error across all assets goes down. This is the **bias-variance tradeoff** — the foundational idea behind a huge swath of statistics and ML.""")

md("s3_1-lead", """### 3.1 Intuition

When you have multiple noisy estimates of related quantities, the *spread between them* is partly real (different true means) and partly noise. Pulling them toward a common point shrinks the noise component without distorting the real-spread component too much. With 8 asset means, this almost always reduces total error vs reporting the 8 raw sample means.

The simplest implementation is a **linear blend** between the raw sample mean and a prior:

> *μ̂*<sub>shrink</sub> = *α · μ̂* + (1 − *α*) · *μ*<sub>prior</sub>

where:
- *μ̂* — the raw sample mean.
- *μ*<sub>prior</sub> — the value we're shrinking toward (typically the cross-sectional mean of all assets, sometimes zero).
- *α* — shrinkage weight. **Units: a fraction in [0, 1]**, NOT a percentage. *α* = 1 means no shrinkage (raw sample mean unchanged); *α* = 0 means total shrinkage (everyone gets the prior).
- *μ̂*<sub>shrink</sub> — the shrinkage-adjusted estimator.""")

md("s3_2-lead", """### 3.2 The James-Stein estimator

The linear blend works, but the choice of *α* is up to you. The **James-Stein estimator** picks *α* (effectively) using a formula that provably reduces total MSE for any *K* ≥ 3 assets — a remarkable result from Charles Stein in 1956. The positive-part version:

> *μ̂*<sub>JS,i</sub> = *μ*<sub>prior</sub> + max(0, 1 − (*K* − 2) · *v* / *D*) · (*μ̂*<sub>i</sub> − *μ*<sub>prior</sub>)

where:
- *K* — the number of assets being shrunk together.
- *v* — proxy for the variance of each estimate (we use the average of *σ²/N* across assets).
- *D* — squared distance from each raw estimate to the prior, summed across assets: Σᵢ(*μ̂*<sub>i</sub> − *μ*<sub>prior</sub>)².
- "max(0, …)" — the **positive-part correction**: if the formula would produce a negative shrinkage factor, clamp to 0. This prevents over-shrinking past the prior.

> **Foot-gun: the inputs must use the same time scale.** If your *μ̂* and *σ²* are daily, *N* is the number of days. If you've annualized, *N* needs to be in years. Don't mix.

<details>
<summary><b>The math, if you want it: why James-Stein dominates the sample mean</b></summary>

Stein (1956) proved that for *K* ≥ 3 normal means with known equal variances, the sample-mean vector is **inadmissible** under squared-error loss — there exists an estimator that strictly dominates it (lower MSE for *every* possible true-mean vector). James and Stein (1961) gave the explicit form. The key idea: each individual coordinate is unbiased, but the *vector* of estimates has total error that can always be reduced by shrinking toward a point.

The formula minimizes an unbiased estimate of the total MSE. The shrinkage factor `1 − (K − 2)v/D` increases (less shrinkage) when the raw estimates are far from the prior (high *D*) and decreases (more shrinkage) when they're close. The positive-part version replaces negative factors with 0, which strictly improves performance further (Baranchik 1964).

For *K* = 1 or 2, James-Stein doesn't dominate — the sample mean is admissible. The 2-asset case is exactly when shrinkage stops being a free lunch.

</details>""")

code("s3_3-code", """def james_stein_shrink(means, vols, n_obs, prior=None):
    \"\"\"Apply James-Stein (positive-part) shrinkage to a vector of asset means.\"\"\"
    means = np.asarray(means, dtype=float)
    vols = np.asarray(vols, dtype=float)
    K = len(means)
    if K < 3:
        return means.copy()  # JS only dominates for K >= 3
    if prior is None:
        prior = means.mean()
    v = (vols ** 2).mean() / n_obs           # avg variance of each estimate
    D = ((means - prior) ** 2).sum()         # sum of squared deviations from prior
    if D == 0:
        return means.copy()
    factor = 1 - (K - 2) * v / D
    factor = max(0.0, factor)                # positive-part
    return prior + factor * (means - prior)


daily_means = log_returns.mean().values
daily_vols  = log_returns.std().values

js_daily = james_stein_shrink(daily_means, daily_vols, n_obs)

shrink = pd.DataFrame({
    "raw mean (annualized)":   daily_means * 252,
    "JS shrunk (annualized)":  js_daily    * 252,
    "shift":                   (js_daily - daily_means) * 252,
}, index=tickers)

cross_sectional_prior = daily_means.mean() * 252
print(f"Prior (cross-sectional mean, annualized): {cross_sectional_prior:.2%}")
print()
shrink""")

md("s3_4-lead", """### 3.4 Visualizing the shrinkage

Bar chart: raw sample means vs JS-shrunk estimates. The dashed horizontal line is the prior (cross-sectional mean).""")

code("s3_4-code", """fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(tickers))
width = 0.4

ax.bar(x - width/2, shrink["raw mean (annualized)"],  width, label="raw sample mean", color="tab:blue")
ax.bar(x + width/2, shrink["JS shrunk (annualized)"], width, label="James-Stein shrunk", color="tab:orange")
ax.axhline(cross_sectional_prior, color="black", ls="--", lw=1,
           label=f"prior = cross-sectional mean ({cross_sectional_prior:.2%})")

ax.set_xticks(x)
ax.set_xticklabels(tickers)
ax.set_ylabel("Annualized mean return")
ax.set_title("Sample mean vs James-Stein shrunk estimate (8-ticker basket, 20y)")
ax.legend()
ax.grid(alpha=0.3, axis="y")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.1%}"))
plt.tight_layout()
plt.show()""")

md("s3_4-interp", """Two patterns visible:

- The estimates that were *furthest from the prior* in the raw data (XLK on the high side, TLT on the low side) get pulled the most.
- Estimates near the prior (XLU, GLD) barely move.

That's the JS formula doing what its name implies: shrinkage *toward* the prior. The high-conviction outliers get tempered; the unsurprising ones stay roughly put.""")

md("s3_5-implications", """### 3.5 What this means for portfolio construction

**Practitioner-grade fact:** essentially all production mean-variance optimization uses *shrunk* expected-return estimates, not raw sample means. The reason: optimizers maximize Sharpe-like objectives that are *very* sensitive to the input expected returns, and naive sample means produce wildly unstable optimal weights — small changes in the data move the "optimal" portfolio dramatically.

We'll see this directly in Chapter 6 when we compute efficient frontiers using both raw and shrunk inputs. For now, the takeaway: **trust shrunk estimates further than raw means, even if it feels weird to "bias" your numbers.**""")

# --- §4 forecasting preview
md("s4-header", """## 4. Part III — Forecasting (the conditional flavor) — preview only

Sections 2 and 3 dealt with *one* flavor of expected return: the long-run unconditional mean. The other interesting flavor is the **conditional** one: instead of asking *"what's the asset's average return over a long period?"* (one number), ask *"what's its expected return *next period* given *what we know now*?"* (a number per asset *per time*).

This is a different problem with different methods, different success criteria, and its own chapters in this curriculum.""")

md("s4_2-routes", """### 4.2 Two routes to forecasting

Both are explicitly deferred to later chapters:

- **Regression-based.** Predict next-period returns from features — lagged returns, valuation ratios, factor exposures, macro variables. The output is a coefficient on each feature and a forecast that varies daily. Setup for **Ch8 (factor models)** which uses regression formally; the chapter introduces the regression machinery in Ch7 first.
- **Strategy-edge-based.** Every trading strategy is implicitly a forecast model. "Buy when RSI < 30" is a (very simple) prediction that the next-period expected return is positive when the indicator condition fires. Setup for **Ch11–12 (strategy taxonomy + mechanics)** which formalizes "edge" as the t-statistic of the strategy's mean trade PnL.""")

md("s4_3-why-separate", """### 4.3 Why these are separate chapters

- **The methods differ.** Regression vs feature engineering vs rule-based signals vs ML.
- **The success criteria differ.** Long-run unconditional estimation cares about standard error of the mean. Forecasting cares about **information ratio** (forecast accuracy relative to forecast volatility), out-of-sample R², or strategy-level Sharpe.
- **The data needs differ.** Long-run estimation wants more history. Forecasting often wants more *features*, not more time.

Ch4 ends here. The next chapter (Ch5) takes the unconditional return estimator from Ch4, the volatility estimator from Ch2, and combines them into the Sharpe ratio.""")

# --- §5 recap
md("s5-recap", """## 5. What we just learned (recap by concept-flavor)

We named four flavors of expected return at the start. Here's what we found, organized by flavor.

### Realized return (the data)
Defined briefly in §1 to keep it distinct from the others. It's the input to estimation, not an estimate itself.

### Long-run / unconditional expected return — the chapter's actual subject
- The natural estimator is the **sample mean** (*μ̂* = average of realized returns).
- Its standard error is *σ*/√*N*. SE shrinks slowly with *N* (only by √).
- Twenty years of daily SPY data leaves a 95% CI on annualized mean roughly **17 percentage points wide** — same data is consistent with everything from "barely beats T-bills" to "doubles in 4 years."
- Subsample stability is poor — disjoint 5-year windows produce annualized means 5–10 percentage points apart on the same asset.
- **Shrinkage** toward a prior is the practitioner-grade remedy. The James-Stein estimator strictly dominates the raw sample mean (in total MSE) for *K* ≥ 3 assets shrunk together. Practitioners use this in production almost universally.

### Conditional / forecast expected return — *deferred*
The "given current state, what's *next* period's expected return?" question. Different methods (regression, signals), different success criteria (information ratio, out-of-sample R²), and lives in **Ch11–12** as "strategy edge" and **Ch8** as factor-implied forecasts.

### Equilibrium / required return — *deferred*
The "given the asset's risk and factor exposures, what *should* its expected return be?" question. The benchmark against which to judge alpha. Setup for **Ch8** (CAPM and Fama–French).""")

# --- §6 up next + exercises
md("s6-up-next", """## 6. Up next

**Chapter 5: Risk metrics — drawdown, VaR, and the Sharpe ratio.** Now that we have honest error bars on the numerator, Ch5 builds the metric without overclaiming. Drawdown answers a different question (path-dependent worst loss). VaR answers another (magnitude in dollar terms). All three together fill out the "single-number summary of an investment" toolkit.""")

md("s7-exercises", """## Exercises

Try these in fresh cells below. Copy any code cell above as a starting point.

1. **Different ticker — crypto.** Pull `BTC-USD` and recompute the 95% CI on its annualized mean. Crypto has higher vol *and* a shorter history (~10 years on yfinance). Do those two effects pull the CI in the same direction or opposite directions?
2. **Calmest vs stormiest sub-window.** From the SPY 5-year-windows table, find the two windows with the highest and lowest realized vol. Compute the *t-statistic* (mean / SE) on the annualized mean of each. Are either of them statistically distinguishable from zero?
3. **Shrinkage sensitivity.** Re-run the §3.4 demo with the prior set to **zero** instead of the cross-sectional mean. Which assets move most? Why does setting the prior to zero make the shrinkage more aggressive for some tickers but not others?
4. *(stretch)* **Implied confidence on Sharpe.** Take SPY's annualized mean and SE from §2.2 and SPY's annualized vol from Ch2. Treating vol as known (it has its own SE but it's smaller than the mean's), compute a rough 95% CI on SPY's Sharpe ratio. (Hint: divide the mean's CI bounds by the vol; assume risk-free rate is zero for simplicity.)""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.14.2"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

target = Path("/home/test/repos/quantitative-analysis/04-expected-returns/lesson.ipynb")
target.write_text(json.dumps(notebook, indent=1))
print(f"wrote {len(cells)} cells to {target}")
```

- [ ] **Step 2.2: Run the builder**

Run: `/home/test/repos/quantitative-analysis/.venv/bin/python /home/test/repos/quantitative-analysis/build_ch4_notebook.py`

Expected output: `wrote N cells to .../04-expected-returns/lesson.ipynb` where N is around 35–40.

- [ ] **Step 2.3: Execute the notebook**

Run: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace 04-expected-returns/lesson.ipynb`

Expected: zero errors.

- [ ] **Step 2.4: Verify cell outputs match expected ranges**

Run this verification script:

```bash
.venv/bin/python -c "
import json
nb = json.load(open('04-expected-returns/lesson.ipynb'))
print(f'cells: {len(nb[\"cells\"])}')
errors = 0
for i, c in enumerate(nb['cells']):
    if c['cell_type'] != 'code':
        continue
    for o in c.get('outputs', []):
        if o.get('output_type') == 'error':
            errors += 1
            print(f'ERROR in cell {i} ({c.get(\"id\")}):', o.get('ename'), o.get('evalue'))
        elif 'text' in o:
            txt = ''.join(o['text']).strip()
            if txt:
                print(f'--- cell {i} ({c.get(\"id\")}):')
                print(txt[:500])
        elif 'data' in o and 'text/plain' in o['data']:
            txt = ''.join(o['data']['text/plain']).strip()
            if txt:
                print(f'--- cell {i} ({c.get(\"id\")}) [data]:')
                print(txt[:500])
print(f'\\nTotal errors: {errors}')
"
```

Expected ranges:
- `s1-download` reports shape `(5031, 8)` (give or take a couple).
- `s1-realized-mean` summary table — SPY annualized mean ~10%, TLT ~3–4%, XLK ~14–15%, XLF ~5%.
- `s2_2-code` — N around 5,030; SPY annualized mean ~10%; SPY annualized SE ~4–5%; 95% CI roughly `[1.5%, 18.5%]` or similar.
- `s2_3-code` — disjoint 5-year windows showing means varying by 5–10 percentage points.
- `s3_3-code` — prior around 8–9% annualized; raw means span ~3% to ~15%; shrunk means are pulled meaningfully toward the prior, especially for high-vol high-mean tickers like XLK.
- `s3_4-code` — bar chart renders, JS-shrunk bars visibly closer to the dashed prior line than raw bars for the extremes.

**Total errors must be 0.**

- [ ] **Step 2.5: Clean up the builder script**

Run: `rm /home/test/repos/quantitative-analysis/build_ch4_notebook.py`

- [ ] **Step 2.6: Checkpoint** — pause and ask the user about a commit covering Tasks 1 + 2.

---

## Task 3: README §0 (concept-flavors framing) and §1 (setup)

**Files:**
- Create: `04-expected-returns/README.md`

- [ ] **Step 3.1: Create `04-expected-returns/README.md` with the following content**

````markdown
# Chapter 4 — Estimating Expected Returns

> **Goal of this chapter:** the *other* half of risk-adjusted return. Three chapters have been about risk; this one is about return. Specifically: given a sample of historical returns, how confidently can we estimate the asset's true expected return? The honest answer is "much less confidently than the casual reader assumes" — and shrinkage is the standard practitioner remedy.

The chapter has two main parts. **Part I (§2)** establishes the sample mean as the natural estimator and demonstrates how noisy it is — even with twenty years of daily data. **Part II (§3)** introduces shrinkage as the practitioner-grade fix. The chapter closes with **§4**, a brief preview of the *forecasting* flavor of expected return (deferred to later chapters), and **§5**, a recap organized by concept-flavor.

The chapter uses the same 8-ticker basket as Chapter 3 — **SPY, TLT, GLD** plus five US sector ETFs (**XLK, XLF, XLE, XLV, XLU**) — over 20 years. Continuity matters because Chapter 5 will compute Sharpe ratios on these same portfolios.

---

## What we mean by "expected return"

The phrase "expected return" gets used loosely. There are at least four distinct flavors, and they don't reduce to each other:

1. **Realized return** — what *actually happened* over some past window. **Not an expectation at all** — it's the data we use as input.
2. **Long-run / unconditional expected return** — "what's the asset's true average return over a long period?" A single number characterizing the data-generating process. *(Part I + Part II — the chapter's main subject.)*
3. **Conditional / forecast expected return** — "given what we know *right now* (current price level, recent moves, macro state), what's *next* period's expected return?" A prediction that varies day-to-day. *Deferred — Ch11–12 (strategy edge).*
4. **Equilibrium / required return** — "given the asset's risk and factor exposures, what *should* its expected return be?" The benchmark against which to judge alpha. *Deferred — Ch8 (CAPM, Fama–French).*

When the rest of this chapter says "expected return," read it as the **long-run unconditional flavor**. The other two get named here so you know they exist and where to expect them.

---

## 1. Setup

Same library stack as Chapter 3 — no new dependencies. Same 8-ticker, 20-year basket, log returns throughout.

The one new conceptual move in this chapter is keeping **realized return** (what happened) carefully distinct from **expected return** (the underlying parameter we're trying to estimate). The first cell of §1 in the notebook computes the realized mean for each asset; the rest of the chapter is about how good a guess that is for the underlying expected return.

After the setup cells run, expect:
- 8-column return panel with **~5,030 daily observations** spanning ~20 years.
- Realized annualized means ranging from ~3% (TLT) to ~15% (XLK), per-asset annualized vols in the 15–30% range from Ch3.
````

- [ ] **Step 3.2: Render in markdown preview**

Open `04-expected-returns/README.md` in VS Code's markdown preview. Confirm the goal callout is a blockquote, the four-flavor list is intact, and the section headings render correctly.

- [ ] **Step 3.3: Checkpoint**

---

## Task 4: README §2 (the naive estimator and its noise)

**Files:**
- Modify: `04-expected-returns/README.md` (append)

- [ ] **Step 4.1: Append the following**

````markdown
## 2. Part I — The naive estimator and its noise

### 2.1 Sample mean as estimator

The natural estimator of expected return is the **sample mean**:

> *μ̂* = (1/N) Σᵢ *rᵢ*

where:
- *rᵢ* — the realized log return on day *i*. **Units:** decimal fraction per day. Daily, not annualized.
- *N* — number of observations in the sample.
- *μ̂* — the sample-mean estimator. **Units:** same as *rᵢ* (per day) unless explicitly annualized.

> **Foot-gun: annualizing a mean.** To go from daily to annualized, **multiply by 252** (means add over independent time periods). This is *different* from the std/vol annualization rule from Chapter 1, which used **× √252** (variances add; standard deviations scale by √t). The two rules are not interchangeable: mean × 252, std × √252, variance × 252.

### 2.2 Standard error of the mean

The sample mean is an *estimator*. Like any estimator, it has its own sampling distribution — different samples of the same population produce different *μ̂* values. The width of that sampling distribution is the **standard error**:

> *SE(μ̂)* = *σ* / √N

where:
- *σ* — the standard deviation of the underlying data. **Units:** same as the data.
- *N* — sample size.
- *SE(μ̂)* — standard deviation of the sampling distribution of the sample mean. **Units:** same as *μ̂*.

> **Foot-gun: SE shrinks like √N, not N.** Doubling sample size only reduces SE by √2 ≈ 1.41×. Quadrupling N halves SE. *Aggressively diminishing returns* — and exactly why even decades of data leave wide CIs on expected return.

> **Foot-gun: annualizing SE.** Treat SE the same way you treat the mean — **× 252**, not √252. SE has the *same units as the mean* (per period), and annualization multiplies the per-period mean by 252.

A 95% confidence interval, assuming approximate normality of the sample mean (justified by the Central Limit Theorem for large *N*, even though individual returns are fat-tailed):

> *CI₉₅* = *μ̂* ± 1.96 · *SE(μ̂)*

where 1.96 is the 0.975 quantile of the standard normal distribution.

For SPY's full 20-year window, the notebook computes:
- N ≈ 5,030 observations.
- Annualized mean ≈ 10%.
- Annualized SE ≈ 4–5%.
- 95% CI on annualized mean ≈ **[1.5%, 18.5%]**.

That CI is the chapter's punchline. Twenty years of data — and the data is statistically consistent with *anywhere* from "barely outpacing T-bills" to "double in four years."

### 2.3 Subsample stability — same data, different windows

A different angle on the same problem. Pick disjoint 5-year sub-windows of the SPY data and compute the sample mean on each. Some windows include the 2008 crisis or the 2022 selloff and look terrible; others sit in calm bull markets and look great. The annualized means typically vary by **5–10 percentage points** across windows of the same asset.

None of those sub-window means is "wrong." They're all valid sample means of real data. The spread is exactly the noise the standard error formula was telling us about, made visceral.

### 2.4 What this means with $100k

A reader sizing a position based on "SPY returns 10% per year" needs to know that, statistically:

| Quantity | Value |
| --- | --- |
| Point estimate (20-year sample) | ~10% / year |
| Standard error (annualized) | ~4–5% |
| 95% CI on annualized mean | roughly **1.5% to 18.5%** |
| On a $100k position, that's | anywhere from **~$1,500/year above T-bills** to **~$18,500/year** |

Both ends of that range are statistically consistent with the same 20 years of data.

Two practical takeaways:
1. **A point estimate is the *center* of a wide distribution, not a fact.** Treating "10% per year" as if it were a known constant is bad statistics with real downstream consequences.
2. **Chapter 5's Sharpe ratio inherits this uncertainty.** A reported Sharpe of 0.5 with 20 years of data has its own large CI; "is this strategy any good?" can't be answered just from the point estimate.
````

- [ ] **Step 4.2: Render and verify**

Confirm the formulas render correctly with subscripts/italics and the foot-gun blockquotes are visible.

- [ ] **Step 4.3: Checkpoint**

---

## Task 5: README §3 (shrinkage)

**Files:**
- Modify: `04-expected-returns/README.md` (append)

- [ ] **Step 5.1: Append the following**

````markdown
## 3. Part II — Shrinkage: pulling estimates toward a prior

§2 showed that *each individual* sample mean is noisy. Counterintuitive fact: even though the sample mean is *unbiased* for any single asset, you can do better in *aggregate* by deliberately introducing a small bias. Each estimate gets pulled toward a common prior; in exchange, the total mean-squared error across all assets goes down. This is the **bias–variance tradeoff** — the foundational idea behind a huge swath of statistics and ML.

### 3.1 Intuition

When you have multiple noisy estimates of related quantities, the *spread between them* is partly real (different true means) and partly noise. Pulling them toward a common point shrinks the noise component without distorting the real-spread component too much. With 8 asset means, this almost always reduces total error vs reporting the 8 raw sample means.

The simplest implementation is a **linear blend** between the raw sample mean and a prior:

> *μ̂*<sub>shrink</sub> = *α · μ̂* + (1 − *α*) · *μ*<sub>prior</sub>

where:
- *μ̂* — the raw sample mean.
- *μ*<sub>prior</sub> — the value we're shrinking toward (typically the cross-sectional mean of all assets, sometimes zero).
- *α* — shrinkage weight. **Units: a fraction in [0, 1]**, NOT a percentage. *α* = 1 means no shrinkage (raw sample mean unchanged); *α* = 0 means total shrinkage (everyone gets the prior).
- *μ̂*<sub>shrink</sub> — the shrinkage-adjusted estimator. Units: same as the inputs.

### 3.2 The James-Stein estimator

The linear blend works, but the choice of *α* is up to you. The **James-Stein estimator** picks (effectively) an *α* using a formula that provably reduces total MSE for any *K* ≥ 3 assets — a remarkable result from Charles Stein in 1956. The positive-part version:

> *μ̂*<sub>JS,i</sub> = *μ*<sub>prior</sub> + max(0, 1 − (*K* − 2) · *v* / *D*) · (*μ̂*<sub>i</sub> − *μ*<sub>prior</sub>)

where:
- *K* — number of assets being shrunk together.
- *v* — proxy for the variance of each estimate (we use the average of *σ²/N* across assets).
- *D* — squared distance from each raw estimate to the prior, summed across assets: Σᵢ(*μ̂*<sub>i</sub> − *μ*<sub>prior</sub>)².
- max(0, …) — the **positive-part correction**: clamps negative shrinkage factors to 0, preventing over-shrinking past the prior.

> **Foot-gun: time-scale consistency.** *μ̂* and *σ²* must use the same time scale, and *N* must match. If your inputs are daily, *N* is the number of days. If you've annualized, *N* is in years. Don't mix.

<details>
<summary><b>The math, if you want it: why James-Stein dominates the sample mean</b></summary>

Stein (1956) proved that for *K* ≥ 3 normal means with known equal variances, the sample-mean vector is *inadmissible* under squared-error loss — there exists an estimator that strictly dominates it (lower MSE for *every* possible true-mean vector). James and Stein (1961) gave the explicit form. The key idea: each individual coordinate is unbiased, but the *vector* of estimates has total error that can always be reduced by shrinking toward a point.

The formula minimizes an unbiased estimate of the total MSE. The shrinkage factor `1 − (K − 2)v/D` increases (less shrinkage) when the raw estimates are far from the prior (high *D*) and decreases (more shrinkage) when they're close. The positive-part version replaces negative factors with 0, which strictly improves performance further (Baranchik 1964).

For *K* = 1 or 2, James-Stein doesn't dominate — the sample mean is admissible. The 2-asset case is exactly when shrinkage stops being a free lunch.

</details>

### 3.3 Empirical demo — what JS does to our 8-ticker basket

The notebook applies the JS estimator to our 8-ticker basket. The prior is the cross-sectional mean (~8–9% annualized). The bar chart shows raw sample means vs JS-shrunk estimates side by side.

Two patterns visible:

- **Estimates *furthest from the prior* in the raw data** (XLK on the high side, TLT on the low side) get pulled the most. The JS formula penalizes outliers because outlier estimates are most likely to be the noisiest.
- **Estimates *near the prior*** (XLU, GLD) barely move. They were already roughly where the formula thinks they should be.

That's exactly what the formula is designed to do: more shrinkage where it can help most, less where it would just distort.

### 3.4 What this means for portfolio construction

**Practitioner-grade fact:** essentially all production mean-variance optimization uses *shrunk* expected-return estimates, not raw sample means. The reason: optimizers maximize Sharpe-like objectives that are *very* sensitive to the input expected returns, and naive sample means produce wildly unstable optimal weights — small changes in the data move the "optimal" portfolio dramatically.

Chapter 6 will demonstrate this directly using both raw and shrunk inputs to compute efficient frontiers.
````

- [ ] **Step 5.2: Render and verify**

Confirm the collapsible math block expands correctly and the §3 numbered subsections read in order.

- [ ] **Step 5.3: Checkpoint**

---

## Task 6: README §4 (forecasting preview), §5 (recap), §6 (up next + Key Terms + Exercises)

**Files:**
- Modify: `04-expected-returns/README.md` (append)

- [ ] **Step 6.1: Append the following**

````markdown
## 4. Part III — Forecasting (the conditional flavor) — preview only

§2 and §3 covered *one* flavor of expected return: the long-run unconditional mean. The other interesting flavor is the **conditional** one: instead of asking *"what's the asset's average return over a long period?"* (one number), ask *"what's its expected return *next period* given *what we know now*?"* (a number per asset *per time*).

This is a different problem with different methods, different success criteria, and its own chapters in this curriculum.

### 4.1 Two routes to forecasting

Both are explicitly deferred:

- **Regression-based.** Predict next-period returns from features — lagged returns, valuation ratios, factor exposures, macro variables. The output is a coefficient on each feature and a forecast that varies daily. Setup for **Chapter 8 (factor models)**, which uses regression formally; the Chapter 7 regression primer introduces the machinery first.
- **Strategy-edge-based.** Every trading strategy is implicitly a forecast model. "Buy when RSI < 30" is a (very simple) prediction that next-period expected return is positive when the indicator condition fires. Setup for **Chapter 11–12 (strategy taxonomy + mechanics)**, which formalizes "edge" as the t-statistic of a strategy's mean trade PnL.

### 4.2 Why these are separate chapters

- **The methods differ.** Regression vs feature engineering vs rule-based signals vs ML.
- **The success criteria differ.** Long-run unconditional estimation cares about standard error of the mean. Forecasting cares about **information ratio** (forecast accuracy relative to forecast volatility), out-of-sample R², or strategy-level Sharpe.
- **The data needs differ.** Long-run estimation wants more history. Forecasting often wants more *features*, not more time.

## 5. What we just learned (recap by concept-flavor)

Four flavors of expected return were named at the start. Here's what we found, organized by flavor.

### Realized return (the data)
Defined briefly in §1 to keep it distinct from the others. It's the input to estimation, not an estimate itself.

### Long-run / unconditional expected return — the chapter's actual subject
- The natural estimator is the **sample mean** (*μ̂* = average of realized returns).
- Its standard error is *σ* / √*N*. SE shrinks slowly with *N* (only by √).
- Twenty years of daily SPY data leaves a 95% CI on the annualized mean roughly **17 percentage points wide** — same data is consistent with everything from "barely beats T-bills" to "doubles in 4 years."
- Subsample stability is poor — disjoint 5-year windows produce annualized means 5–10 percentage points apart on the same asset.
- **Shrinkage** toward a prior is the practitioner-grade remedy. The James-Stein estimator strictly dominates the raw sample mean (in total MSE) for *K* ≥ 3 assets shrunk together. Practitioners use this in production almost universally.

### Conditional / forecast expected return — *deferred*
The "given current state, what's *next* period's expected return?" question. Different methods (regression, signals), different success criteria (information ratio, out-of-sample R²), and lives in **Ch11–12** as "strategy edge" and **Ch8** as factor-implied forecasts.

### Equilibrium / required return — *deferred*
The "given the asset's risk and factor exposures, what *should* its expected return be?" question. The benchmark against which to judge alpha. Setup for **Ch8** (CAPM and Fama–French).

---

## Key Terms (Chapter 4)

| Term | Meaning | First used |
|------|---------|-----------:|
| Realized return | What actually happened (the data); not an expectation | §1 |
| Sample mean (*μ̂*) | Average of a finite sample; natural estimator of population mean | §2.1 |
| Estimator | A function of data used to guess an unknown population quantity | §2.1 |
| Standard error (SE) | Standard deviation of an estimator's sampling distribution | §2.2 |
| Confidence interval | Range around an estimate containing the true value with stated probability under repeated sampling | §2.2 |
| t-statistic | Estimate divided by its standard error | §2.2 |
| Bias | Expected difference between an estimator and the true value | §3.1 |
| Bias-variance tradeoff | Accepting a small bias to reduce overall mean-squared error | §3.1 |
| Shrinkage | Pulling a noisy estimate toward a prior | §3.1 |
| Prior | The target value toward which a shrinkage estimator pulls | §3.1 |
| Cross-sectional mean | Mean across assets at a point in time (vs the time-series mean of one asset) | §3.1 |
| James-Stein estimator | Specific shrinkage estimator that strictly dominates the sample mean in MSE for *K* ≥ 3 assets | §3.2 |
| Signal-to-noise ratio (SNR) | Ratio of mean to standard error | §2.4 |
| Conditional / forecast expected return | Expected return given current state — *deferred* | §0 |
| Equilibrium / required return | Expected return implied by an asset's risk — *deferred* | §0 |

---

## Exercises

Try these in fresh cells at the bottom of the notebook:

1. **Different ticker — crypto.** Pull `BTC-USD` and recompute the 95% CI on its annualized mean. Crypto has higher vol *and* a shorter history (~10 years on yfinance). Do those two effects pull the CI in the same direction or opposite directions?
2. **Calmest vs stormiest sub-window.** From the SPY 5-year-windows table, find the two windows with the highest and lowest realized vol. Compute the *t-statistic* (mean / SE) on the annualized mean of each. Are either of them statistically distinguishable from zero?
3. **Shrinkage sensitivity.** Re-run the §3 demo with the prior set to **zero** instead of the cross-sectional mean. Which assets move most? Why does setting the prior to zero make the shrinkage more aggressive for some tickers but not others?
4. *(stretch)* **Implied confidence on Sharpe.** Take SPY's annualized mean and SE from §2.2 and SPY's annualized vol from Ch2. Treating vol as known (it has its own SE but it's smaller than the mean's), compute a rough 95% CI on SPY's Sharpe ratio. (Hint: divide the mean's CI bounds by the vol; assume risk-free rate is zero for simplicity.)

---

## Up next

**Chapter 5: Risk Metrics — drawdown, VaR, and the Sharpe ratio.** Now that we have honest error bars on the numerator of Sharpe, the next chapter builds the metric without overclaiming. Drawdown answers a different question (path-dependent worst loss), VaR answers another (magnitude in dollar terms), and all three together fill out the "single-number summary of an investment" toolkit.
````

- [ ] **Step 6.2: Render and verify**

Confirm the Key Terms table aligns, exercises numbered 1–4, Up next paragraph closes the chapter.

- [ ] **Step 6.3: Checkpoint** — README is fully drafted.

---

## Task 7: Update root `glossary.md` with Ch4 entries

**Files:**
- Modify: `glossary.md`

- [ ] **Step 7.1: Add the following entries, alphabetically interleaved into existing sections**

The full set of new entries:

```markdown
## B

**Bias** *(Ch. 4)* — The expected difference between an estimator's value
and the true population value it's trying to estimate. An *unbiased*
estimator has bias = 0. The sample mean is unbiased for the population
mean.

**Bias–variance tradeoff** *(Ch. 4)* — The principle that accepting a
small bias in an estimator can sometimes reduce its overall
mean-squared error. Underlies shrinkage estimators and a huge swath of
statistics and ML.

## C

**Confidence interval** *(Ch. 4)* — A range around a point estimate that
contains the true population value with stated probability under
repeated sampling. *μ̂* ± 1.96 · SE gives a 95% CI under approximate
normality of the sample mean.

**Cross-sectional mean** *(Ch. 4)* — The mean across assets at a single
point in time, in contrast to a time-series mean (one asset across
many points). The default prior in James-Stein shrinkage applied to a
basket.

## E

**Equilibrium / required return** *(Ch. 4)* — The expected return an
asset *should* have given its risk and factor exposures. Named in
Ch. 4 as a deferred flavor; formalized in Ch. 8 (CAPM, Fama-French).

**Estimator** *(Ch. 4)* — A function of data used to guess an unknown
population quantity. The sample mean is an estimator of the population
mean; the sample variance is an estimator of the population variance.

## F

**Forecast / conditional expected return** *(Ch. 4)* — Expected return
*given current state* — a prediction that varies day-to-day, in
contrast to the long-run unconditional mean. Named in Ch. 4 as a
deferred flavor; formalized in Ch. 8 and Ch. 11–12.

## J

**James-Stein estimator** *(Ch. 4)* — A specific shrinkage estimator
that strictly dominates the sample mean in total MSE for *K* ≥ 3
assets shrunk together. The positive-part version is the standard
practical form. Used widely in production portfolio optimization.

## P

**Prior** *(Ch. 4)* — The target value toward which a shrinkage
estimator pulls. Common choices: the cross-sectional mean of all
assets being shrunk, or zero.

## R

**Realized return** *(Ch. 4)* — What actually happened over a past
window. Distinguished in Ch. 4 from "expected return" because it's
the *data* used to estimate, not the estimate itself.

## S

**Sample mean (*μ̂*)** *(Ch. 4)* — The arithmetic average of a finite
sample of observations: *μ̂* = (1/N) Σᵢ *rᵢ*. The natural estimator
of the population mean. Unbiased; standard error scales like 1/√N.

**Shrinkage** *(Ch. 4)* — Pulling a noisy estimate toward a prior to
reduce mean-squared error at the cost of a small bias. Applied to
expected-return estimates in Ch. 4; used in production portfolio
construction in Ch. 6.

**Signal-to-noise ratio (SNR)** *(Ch. 4)* — The ratio of an estimate
to its standard error; equivalent to the t-statistic. Measures how
confidently we can distinguish the estimate from zero.

**Standard error (SE)** *(Ch. 4)* — The standard deviation of an
estimator's sampling distribution. For the sample mean: *SE(μ̂)* =
*σ* / √N. **Annualize by × 252** (same rule as the mean), not √252.

## T

**t-statistic** *(Ch. 4)* — An estimate divided by its standard error.
Roughly, the number of standard errors away from zero. |t| > 2 is the
conventional threshold for "statistically distinguishable from zero."
```

Insert each entry into its correct alphabetical position within the existing section (e.g., the new B entries go inside `## B` between *Bear market* and *Bull market*; if there are intervening Ch3 entries, slot accordingly).

- [ ] **Step 7.2: Verify alphabetical order**

Skim the entire `glossary.md` from top to bottom. Every section heading should be in alphabetical order; entries within each section should be alphabetical. No duplicates.

- [ ] **Step 7.3: Checkpoint**

---

## Task 8: Update Ch3 README "Up next" and root README curriculum row

**Files:**
- Modify: `03-correlation/README.md`
- Modify: `README.md` (root)

- [ ] **Step 8.1: Update Ch3 "Up next"**

Find the existing "Up next" paragraph at the end of `03-correlation/README.md` and replace with:

```markdown
**Chapter 4: Estimating Expected Returns.** Three chapters spent on risk; zero on return. Ch4 fills the gap. The reader leaves with two findings: (1) the historical mean as an estimator of true expected return is **brutally noisy** at any reasonable sample size, and (2) **shrinkage toward a prior** is the practitioner-grade remedy. Both findings honestly inform Chapter 5's Sharpe ratio.
```

- [ ] **Step 8.2: Update root README curriculum table**

Find the Ch04 row in the curriculum table (currently `| 04 | _coming next_ | Estimating expected returns: ...`) and replace with:

```markdown
| 04 | [`04-expected-returns`](./04-expected-returns) | Estimating expected returns: historical mean, shrinkage, and why estimating return is the hard problem in finance. |
```

Also update the Ch05 row from `| 05 | _planned_ |` to `| 05 | _coming next_ |` since Ch5 is now the immediately-next chapter.

- [ ] **Step 8.3: Render both files and verify**

Open Ch3 README and root README in markdown preview. Confirm the Up next paragraph reads cleanly and the Ch4 row in the curriculum table links to the new directory.

- [ ] **Step 8.4: Checkpoint**

---

## Task 9: End-to-end smoke test

**Files:** none modified

- [ ] **Step 9.1: Restart kernel and re-execute the notebook**

Run: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace 04-expected-returns/lesson.ipynb`

Expected: zero errors. Re-run the verification script from Task 2.4.

- [ ] **Step 9.2: Render `04-expected-returns/README.md` end-to-end**

Open in markdown preview. Confirm:
- All section headings render in correct order (concept-flavors framing, §1, §2, §3, §4, §5, Key Terms, Exercises, Up next).
- The collapsible `<details>` block in §3.2 expands cleanly when clicked.
- All formulas render with subscripts/italics correctly.
- The Key Terms table aligns properly.
- The two §2.4 tables render correctly.

- [ ] **Step 9.3: Render `glossary.md`**

Confirm alphabetical ordering, no broken markdown, no duplicate entries.

- [ ] **Step 9.4: Render Ch3 README and root README**

Confirm Ch3's reworded "Up next" paragraph reads cleanly and the root README's Ch4 row links correctly.

- [ ] **Step 9.5: Checkpoint** — full chapter verified.

---

## Task 10: Update curriculum-roadmap memory

**Files:**
- Modify: `/home/test/.claude/projects/-home-test-repos-quantitative-analysis/memory/project_curriculum_roadmap.md`

- [ ] **Step 10.1: Update the Ch04 entry**

Find the Ch04 status block (currently PLANNED) and replace with:

```markdown
### Ch 04 — Estimating Expected Returns ✅ DONE
**Covered:** four-flavor framing of "expected return" (realized, long-run unconditional, conditional/forecast, equilibrium); long-run unconditional flavor — sample mean as estimator, standard error *σ*/√N, 95% CI from CLT (~17pp wide on 20y SPY annualized mean), subsample instability across disjoint 5-year windows, dollar framing on $100k position; James-Stein shrinkage with positive-part correction applied to 8-ticker basket. Forecasting and equilibrium flavors named-but-deferred to Ch11-12 and Ch8 respectively.
**Data:** same 8-ticker basket as Ch3, 20y daily.
**New formula-symbol convention applied:** every formula has units and arithmetic foot-guns flagged (annualize mean × 252 not √252; SE × 252 same rule; α as fraction in [0,1]; time-scale consistency in JS).
**Promises to honor in later chapters:**
- Ch5 Sharpe ratio uses Ch4's mean estimator + Ch2's vol estimator with honest error bars on both inputs.
- Ch6 portfolio optimization uses shrunk expected returns (motivated in §3.4 of Ch4); demonstrates instability of naive sample means concretely.
- Ch8 picks up "equilibrium return" as a flavor named in Ch4.
- Ch11-12 picks up "forecasting / conditional return" as a flavor named in Ch4.
- Black-Litterman is a deferred residual; natural home in Ch6.
```

- [ ] **Step 10.2: Verify roadmap reads cleanly**

Confirm Ch01 → Ch02 → Ch03 → Ch04 progression is consistent.

- [ ] **Step 10.3: Final checkpoint** — entire chapter complete. Stop and ask the user about the bundled commit covering Tasks 7–10 (or however they want to split commits).

---

## Self-review notes (for the implementer)

**Spec coverage:**
- Spec §2 goals → Tasks 2 (notebook), 4–6 (README sections).
- Spec §3 narrative arc → Task 3 (README intro), 6 (recap).
- Spec §4 data → Task 2 setup cells.
- Spec §5 section structure → §1 → Tasks 2 + 3; §2 → Task 4; §3 → Task 5; §4–§6 → Task 6.
- Spec §6 new terminology → Tasks 4–6 (inline glosses + Key Terms), 7 (glossary).
- Spec §7 formulas → each appears in both notebook (Task 2) and README (Tasks 4–5) with units + foot-gun flags per the updated convention.
- Spec §8 dependencies → Task 1 (verify, no new packages).
- Spec §10 cross-chapter promises → Tasks 8 (Ch3 + root README updates).
- Spec §12 file edits → Task 8.

**Type/symbol consistency:** *r*, *μ*, *σ*, *N*, *μ̂*, SE, *α*, *μ*<sub>prior</sub>, *K*, *v*, *D* used identically across tasks.

**No placeholders.** Each step contains complete code or complete prose; verification commands include expected output ranges; no "TBD" / "TODO" / "fill in later" anywhere.
