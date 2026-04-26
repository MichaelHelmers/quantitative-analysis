# Chapter 3 Implementation Plan — Correlation and Diversification

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build Chapter 3 of the quant-analysis tutorial — paired notebook + README — introducing correlation and diversification through three concept-flavors (pairwise, aggregation, regime/crisis), following the precedent set by Ch2 of pairing textbook tools with empirical demonstrations of where they break.

**Architecture:** Single chapter folder `03-correlation/` containing one Jupyter notebook (`lesson.ipynb`) and one Markdown lesson (`README.md`). Eight-ticker basket (SPY, TLT, GLD, plus 5 sector ETFs) over 20 years. New vocabulary appended to root `glossary.md`. No shared module — each chapter remains self-contained.

**Tech Stack:** Python 3.14, pandas, numpy, matplotlib, yfinance, scipy.stats. **No new dependencies** — all already in `requirements.txt`.

**Verification model:** Same as Ch2 — every notebook cell runs without error; outputs match expected numerical ranges (given in each task); README and notebook render correctly in markdown preview / Jupyter Lab.

**Commit policy:** User authorizes commits explicitly. Plan groups work into checkpoint pauses; the final task in each batch ends with "stop and ask the user about a commit covering Tasks N–M." No per-task auto-commits.

**Spec reference:** `docs/superpowers/specs/2026-04-26-ch03-correlation-design.md`

---

## File map

| File | Status | Responsibility |
| --- | --- | --- |
| `03-correlation/` | create | Chapter folder. |
| `03-correlation/lesson.ipynb` | create | Runnable companion notebook with concept-flavors framing, setup, three-part empirical build, recap, exercises. |
| `03-correlation/README.md` | create | Canonical narrative: framing, §1 setup, §2 Part I, §3 Part II, §4 Part III, §5 recap-by-flavor, §6 up next + Key Terms + exercises. |
| `glossary.md` | modify | Append Ch3 entries: Pearson correlation, correlation matrix, covariance matrix, portfolio weights, portfolio variance, diversification benefit, equal-weight portfolio, 60/40 portfolio, √N rule, diversification floor, systematic risk, idiosyncratic risk, conditional correlation, rolling correlation, crisis correlation, hidden factor exposure, tail dependence. |
| `02-risk/README.md` | modify | Reword "Up next" to reflect Ch3's actual title and three concept-flavors. |
| `README.md` (root) | modify | Update curriculum table: Ch3 row from "_coming next_" to title + link. |
| Memory `project_curriculum_roadmap.md` | modify | Mark Ch03 done; record what was actually covered. |

---

## Task 1: Set up Chapter 3 directory and verify dependencies

**Files:**
- Create: `03-correlation/` (directory)

- [ ] **Step 1.1: Create the chapter directory**

Run: `mkdir -p 03-correlation`

- [ ] **Step 1.2: Verify all dependencies are installed in the venv**

Run: `/home/test/repos/quantitative-analysis/.venv/bin/python -c "import numpy, pandas, matplotlib, yfinance, scipy; print('all deps available')"`

Expected output: `all deps available`

If any import fails, run `uv pip install -r requirements.txt` and retry.

- [ ] **Step 1.3: Quick test of multi-ticker yfinance pull**

Run: `/home/test/repos/quantitative-analysis/.venv/bin/python -c "import yfinance as yf; d = yf.download(['SPY','TLT'], period='1y', progress=False); print(d.columns.tolist()[:5]); print(d.shape)"`

Expected: a list of MultiIndex column tuples like `[('Close', 'SPY'), ('Close', 'TLT'), ...]` and a shape like `(252, 10)` (252 trading days × 5 OHLCV cols × 2 tickers).

- [ ] **Step 1.4: Checkpoint** — pause.

---

## Task 2: Build the full notebook (all cells, then execute)

**Files:**
- Create: `03-correlation/lesson.ipynb`

This task uses a builder script (same pattern as Ch2) to construct the full notebook in one shot. The script lives in the project root and is deleted after the notebook is built.

- [ ] **Step 2.1: Write the builder script `build_ch3_notebook.py` to the project root**

The script content is below. It's long because it contains every cell of the chapter — that's intentional per the no-placeholders rule. The script defines `md(...)` and `code(...)` helpers, then enumerates ~50 cells in chapter order, then writes the notebook JSON.

```python
"""Build the complete 03-correlation/lesson.ipynb from a cell list."""
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
md("intro", """# Chapter 3 — Multiple Assets: Correlation and Diversification

Read the chapter [`README.md`](./README.md) first. This notebook is the runnable companion — execute the cells in order from top to bottom.

Chapters 1 and 2 lived inside a single asset. This chapter takes the **correlation risk** flavor that Chapter 2's framing named-but-deferred and breaks it into its own sub-flavors plus the statistical machinery for each. The arc deliberately mirrors Chapter 2: build the textbook tool first (Parts I and II), then show empirically how reality breaks it (Part III).""")

md("framing", """## What we mean by "correlation risk"

When we say "correlation risk" in this chapter, we don't mean a single thing. The concept has several flavors that don't reduce to each other:

1. **Pairwise correlation** — how tightly do two specific assets move together? (Ch3 Part I)
2. **Aggregation / portfolio risk** — what does combining *many* assets do to overall risk? (Ch3 Part II)
3. **Regime / crisis correlation** — correlations aren't constant. They spike toward 1 in crashes, so diversification weakens exactly when you need it. (Ch3 Part III)
4. **Hidden factor exposure** — seemingly distinct assets share underlying drivers (rates, oil, the broad market itself); a "diversified" portfolio may be a single bet in disguise. *Deferred — future factor-models chapter.*
5. **Tail dependence** — even if *average* correlation is low, two assets may always crash *together*. *Deferred — much later (with EVT / copulas).*

When the rest of this chapter says "correlation risk," read it as "the magnitude, aggregation, and regime dimensions of correlation risk" — not "everything anyone has ever called correlation risk." Chapter 2 used the same disclaimer pattern.""")

# --- §1 setup
md("s1-header", """## 1. Setup and data refresh

Same library stack as Chapter 2 — no new dependencies. Multi-ticker download this time: an 8-asset basket spanning broad equities (SPY), bonds (TLT), gold (GLD), and five US sector ETFs (XLK tech, XLF financials, XLE energy, XLV healthcare, XLU utilities). Twenty-year window, log returns throughout, consistent with Chapter 2.""")

code("s1-imports", """import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

print(f"numpy   {np.__version__}")
print(f"pandas  {pd.__version__}")
print(f"yf      {yf.__version__}")""")

code("s1-download", """tickers = ["SPY", "TLT", "GLD", "XLK", "XLF", "XLE", "XLV", "XLU"]
data = yf.download(tickers, period="20y", progress=False)
prices = data["Close"][tickers]   # column order matches `tickers`
print(f"shape: {prices.shape}")
print(f"date range: {prices.index.min().date()} to {prices.index.max().date()}")
prices.head()""")

md("s1-returns-lead", """Compute log returns for all eight assets in one shot. The result is a panel — rows are dates, columns are tickers.""")

code("s1-returns", """log_returns = np.log(prices / prices.shift(1)).dropna()

summary = pd.DataFrame({
    "daily mean":      log_returns.mean(),
    "daily std":       log_returns.std(),
    "annualized vol":  log_returns.std() * np.sqrt(252),
})
summary""")

md("s1-cov-matrix-lead", """### The covariance matrix Σ

Chapter 2 §3.2 introduced **covariance** — the average product of two variables' deviations from their means — and noted "this will reappear as the central object of Chapter 3." Here it is. With *N* assets, the natural object isn't a single covariance number but the entire **covariance matrix** Σ:

> Σ<sub>ij</sub> = Cov(*r<sub>i</sub>*, *r<sub>j</sub>*)

This is a square *N* × *N* matrix where:
- The **diagonal** (Σ<sub>ii</sub> = Cov(*r<sub>i</sub>*, *r<sub>i</sub>*) = Var(*r<sub>i</sub>*)) is each asset's *variance* — the same per-asset numbers Chapter 2 worked with.
- The **off-diagonals** carry the new information: how each pair co-moves.

Σ is symmetric (Cov(*X*, *Y*) = Cov(*Y*, *X*)).""")

code("s1-cov-matrix", """cov_matrix = log_returns.cov()
print("8×8 covariance matrix (daily, log returns):")
cov_matrix""")

# --- §2 Part I: Pairwise correlation
md("s2-header", """## 2. Part I — Pairwise correlation (the textbook tool)

The numbers in the covariance matrix above are hard to read directly because they're tiny (daily-return variances are tiny) and they have units (squared returns). The conventional fix is to normalize them into **correlations**.""")

md("s2_1-lead", """### 2.1 Pearson correlation — the unitless cousin of covariance

> *ρ<sub>XY</sub>* = Cov(*X*, *Y*) / (*σ<sub>X</sub> σ<sub>Y</sub>*)

where:
- Cov(*X*, *Y*) — the covariance between *X* and *Y* (Ch2 §3.2).
- *σ<sub>X</sub>*, *σ<sub>Y</sub>* — the standard deviations of *X* and *Y*.
- *ρ<sub>XY</sub>* — the **Pearson correlation coefficient**, bounded in [−1, +1].

Why divide? Covariance scales with the units of *X* and *Y* — a covariance computed on percent returns is different from one on basis-point returns, even though it's the *same data*. Dividing by *σ<sub>X</sub> σ<sub>Y</sub>* removes the units. The result is a unitless number with a fixed range, comparable across asset pairs.

<details>
<summary><b>The math, if you want it: why ρ is bounded in [−1, +1]</b></summary>

This is the **Cauchy–Schwarz inequality** in disguise. For any two random variables *X* and *Y*:

> |Cov(*X*, *Y*)| ≤ *σ<sub>X</sub> σ<sub>Y</sub>*

Proof sketch: define *Z* = *X*/σ<sub>X</sub> ± *Y*/σ<sub>Y</sub>. Var(*Z*) ≥ 0 because variance can't be negative. Expanding gives 2 ± 2 Cov(*X*, *Y*)/(σ<sub>X</sub> σ<sub>Y</sub>) ≥ 0, which rearranges to |Cov(*X*, *Y*)| ≤ σ<sub>X</sub> σ<sub>Y</sub>. Dividing through by σ<sub>X</sub> σ<sub>Y</sub> gives |ρ| ≤ 1.

The bounds are *attained* when *Y* is a perfect linear function of *X*: ρ = +1 when *Y* = *aX* + *b* with *a* > 0, ρ = −1 when *a* < 0, ρ = 0 when *X* and *Y* are linearly independent (though they may still be related nonlinearly — a famous correlation pitfall).

</details>

Pandas computes the whole correlation matrix for us in one call:""")

code("s2_1-corr-matrix", """corr_matrix = log_returns.corr()
corr_matrix.round(3)""")

md("s2_1-interp", """Read this matrix:
- **Diagonal is 1.0** — every asset is perfectly correlated with itself.
- **Sector ETFs cluster high** with SPY (typically 0.85–0.95) and with each other (0.5–0.85). They're all flavors of US equity risk.
- **TLT row/column** has near-zero correlations with the equity assets (long-run average; we'll see in Part III that it varies).
- **GLD row/column** has uniformly low correlations with everything.

The lowest off-diagonal correlation is the gold/Treasury and gold/equity pairs; the highest off-diagonal is SPY's correlation with the broad sector ETFs.""")

md("s2_2-lead", """### 2.2 What different correlations look like

Three scatter plots of daily log returns, with very different correlations.""")

code("s2_2-code", """pairs = [("SPY", "XLK"), ("SPY", "XLU"), ("SPY", "TLT")]
fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharex=True, sharey=True)

for ax, (a, b) in zip(axes, pairs):
    rho = corr_matrix.loc[a, b]
    ax.scatter(log_returns[a], log_returns[b], s=4, alpha=0.3)
    ax.axhline(0, color="black", lw=0.4)
    ax.axvline(0, color="black", lw=0.4)
    ax.set_xlabel(f"{a} daily log return")
    ax.set_ylabel(f"{b} daily log return")
    ax.set_title(f"{a} vs {b}   (ρ = {rho:.2f})")
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.show()""")

md("s2_2-interp", """Same axes scale across all three plots, so the visual comparison is honest:

- **SPY vs XLK** (~0.9) — a tight diagonal cloud. These are nearly the same asset; XLK is large-cap tech, which dominates SPY's market-cap-weighted index. Knowing one move tells you almost everything about the other.
- **SPY vs XLU** (~0.6–0.7) — clearly correlated, but visibly looser. Utilities are equity but defensive — they move with the market on most days, but with less amplitude.
- **SPY vs TLT** (long-run near-zero) — a blob with no diagonal. The directions are *on average* independent. Plenty of stocks-up-bonds-up days, plenty of stocks-up-bonds-down days, in roughly equal numbers.

The "correlation captures linear co-movement" framing is literal: ρ ≈ +1 means "lies on a line of positive slope," ρ ≈ 0 means "no preferred line."""")

md("s2_3-lead", """### 2.3 What this means with $100k

The point of correlation isn't the ρ number — it's what the number says about a real position. Imagine you hold $100k of SPY and want to "diversify" by adding another $100k of something else. Three candidate add-ons:

- **Add $100k of XLK** (ρ ≈ 0.9 with SPY). XLK and SPY barely behave like distinct assets. The combined $200k position has roughly 1.95× the risk of the original $100k SPY — almost no diversification benefit. You doubled exposure, not safety.
- **Add $100k of XLU** (ρ ≈ 0.65). Better. Some of XLU's variance is independent of SPY's, so the combined position has roughly 1.81× the original risk — meaningfully less than 2×.
- **Add $100k of TLT** (ρ ≈ 0). The combined position has only √2 ≈ 1.41× the original risk — the textbook diversification result. The cross-asset "60/40-style" play is the cleanest example of correlation working in your favor.

(The 1.95×, 1.81×, 1.41× factors come from the two-asset variance formula in §3.1, which we'll prove next. They assume identical individual volatilities for simplicity; in reality TLT's vol is lower than SPY's, which helps the diversification math even further.)""")

# --- §3 Part II: Aggregation
md("s3-header", """## 3. Part II — Aggregation: portfolio variance and the diversification math

Pairs are the simplest case. Real portfolios have many positions. Going from "two correlations" to "many correlations" is where the matrix Σ from §1 starts paying for itself.""")

md("s3_1-lead", """### 3.1 Two-asset portfolio variance

Hold *w<sub>X</sub>* fraction of asset X and *w<sub>Y</sub>* = 1 − *w<sub>X</sub>* of asset Y. The portfolio's daily return is *r<sub>p</sub>* = *w<sub>X</sub> r<sub>X</sub>* + *w<sub>Y</sub> r<sub>Y</sub>*. Its variance is:

> *σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

where:
- *w<sub>X</sub>*, *w<sub>Y</sub>* — the **portfolio weights** (must sum to 1 for a fully-invested long-only portfolio).
- *σ<sub>X</sub>*, *σ<sub>Y</sub>* — individual asset standard deviations.
- *ρ* — the pairwise correlation between *X* and *Y*.
- *σ<sub>p</sub>²* — the variance of the portfolio's return.

Three terms: the two **own-variance** terms (each weighted by *w²*) and the **cross-term** (the diversification engine). When ρ < 1, the cross-term shrinks the total variance below the weighted average of individual variances. When ρ = 1, no diversification — *σ<sub>p</sub>* is the weighted average of *σ<sub>X</sub>* and *σ<sub>Y</sub>*. When ρ = −1, perfect hedging is possible — there exist weights making *σ<sub>p</sub>* = 0.

<details>
<summary><b>The math, if you want it: deriving the two-asset variance</b></summary>

Var(*aX* + *bY*) = *a²* Var(*X*) + *b²* Var(*Y*) + 2*ab* Cov(*X*, *Y*).

Plug in *a* = *w<sub>X</sub>*, *b* = *w<sub>Y</sub>*, Var(*X*) = *σ<sub>X</sub>²*, Cov(*X*, *Y*) = *ρ σ<sub>X</sub> σ<sub>Y</sub>* (rearranged from the correlation definition):

*σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

The variance-of-a-sum identity itself comes from expanding E[((*aX* + *bY*) − E[*aX* + *bY*])²]: the cross-term you get is 2*ab E*[(*X* − *μ<sub>X</sub>*)(*Y* − *μ<sub>Y</sub>*)] = 2*ab* Cov(*X*, *Y*) — exactly the *E*[·] machinery introduced in Ch2 §2.2 and used heavily in Ch2 §3.2.

</details>

Compute concrete numbers for a 50/50 SPY/TLT portfolio:""")

code("s3_1-code", """sigma_spy = log_returns["SPY"].std()
sigma_tlt = log_returns["TLT"].std()
rho       = corr_matrix.loc["SPY", "TLT"]
w_x = w_y = 0.5

sigma_p_squared = (
    w_x**2 * sigma_spy**2
    + w_y**2 * sigma_tlt**2
    + 2 * w_x * w_y * sigma_spy * sigma_tlt * rho
)
sigma_p = np.sqrt(sigma_p_squared)

ann = lambda s: s * np.sqrt(252)

print(f"SPY annualized vol:        {ann(sigma_spy):.2%}")
print(f"TLT annualized vol:        {ann(sigma_tlt):.2%}")
print(f"SPY/TLT correlation:       {rho:.3f}")
print(f"50/50 portfolio vol:       {ann(sigma_p):.2%}")
print(f"Weighted-average of σ:     {ann(0.5 * sigma_spy + 0.5 * sigma_tlt):.2%}")
print(f"Diversification benefit:   {ann(0.5 * sigma_spy + 0.5 * sigma_tlt) - ann(sigma_p):.2%}")""")

md("s3_1-interp", """The 50/50 portfolio's vol is meaningfully *below* the weighted average of the individual vols. That gap is the **diversification benefit** — the cross-term in the formula doing its work.""")

md("s3_2-lead", """### 3.2 The correlation matrix as a heatmap

The 8×8 correlation matrix from §2.1 has structure that's easier to see visually than as a table of numbers.""")

code("s3_2-code", """fig, ax = plt.subplots(figsize=(8, 7))
im = ax.imshow(corr_matrix.values, cmap="RdYlBu_r", vmin=-1, vmax=1)

ax.set_xticks(range(len(tickers)))
ax.set_yticks(range(len(tickers)))
ax.set_xticklabels(tickers)
ax.set_yticklabels(tickers)

# Annotate each cell with its correlation value.
for i in range(len(tickers)):
    for j in range(len(tickers)):
        v = corr_matrix.iloc[i, j]
        color = "white" if abs(v) > 0.6 else "black"
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", color=color, fontsize=9)

ax.set_title("Pairwise correlation matrix — 8 ETFs, 20y daily log returns")
plt.colorbar(im, ax=ax, label="ρ")
plt.tight_layout()
plt.show()""")

md("s3_2-interp", """Three blocks visible:

- **Sector ETFs (XLK / XLF / XLE / XLV / XLU) form a high-correlation cluster** in the bottom-right. They're all US equity, and the correlations among them sit in a tight 0.5–0.85 range. The whole block has high correlation with SPY too (top row / left column for the sectors).
- **TLT row/column** is the visual outlier — pale or even slightly blue cells. Its long-run correlation with all the equity assets is near zero.
- **GLD row/column** is uniformly low correlation with everything else — neither equity nor bonds explain its movements.

This is the input we'll feed into the portfolio-variance machinery next.""")

md("s3_3-lead", """### 3.3 The diversification math empirically

The two-asset formula generalizes to *N* assets — but rather than write the formula yet, let's just *compute* portfolio vol as we add tickers one at a time, in a deliberate order designed to make the lesson visible:

`XLK → +XLF → +XLE → +XLV → +XLU → +TLT → +GLD`

Start with one sector. Add four more sectors (correlated names). Then add TLT (cross-asset, decorrelated). Then add GLD. Equal weights at each step. Plot the resulting annualized volatility.""")

code("s3_3-code", """order = ["XLK", "XLF", "XLE", "XLV", "XLU", "TLT", "GLD"]
ann_vols = []

for k in range(1, len(order) + 1):
    basket = order[:k]
    w = np.ones(k) / k
    sub_cov = log_returns[basket].cov().values
    var_p = w @ sub_cov @ w
    ann_vols.append(np.sqrt(var_p) * np.sqrt(252))

fig, ax = plt.subplots(figsize=(10, 4.5))
ax.plot(range(1, len(order) + 1), ann_vols, marker="o", lw=2)

# Annotate which ticker was just added.
for k, t in enumerate(order, start=1):
    ax.annotate(f"+{t}" if k > 1 else t,
                xy=(k, ann_vols[k-1]), xytext=(0, 8),
                textcoords="offset points", ha="center", fontsize=9)

ax.set_xlabel("Number of equally-weighted assets")
ax.set_ylabel("Annualized portfolio vol")
ax.set_title("Diversification in action: the marginal asset matters")
ax.grid(alpha=0.3)
plt.tight_layout()
plt.show()""")

md("s3_3-interp", """Read the curve from left to right:

- **N = 1 (just XLK)** — high vol, ~25%+ annualized. A single sector is a concentrated bet.
- **N = 2 to 5 (adding sector ETFs)** — vol drops, but each step is a modest improvement. Adding correlated names doesn't help much. By the time all five sectors are in, you've roughly recovered SPY's ~19% vol.
- **N = 6 (adding TLT)** — sharp drop. TLT is uncorrelated-to-negative with the equity basket, so the cross-term in the variance formula works in your favor for the first time.
- **N = 7 (adding GLD)** — small further drop. Most of the diversification benefit was already captured by the cross-asset move at N = 6.

**The marginal benefit of one more asset depends entirely on its correlation with what you already hold.** Adding correlated names dilutes the basket toward "the sector average"; adding decorrelated names actually reduces risk.

Two limit results worth knowing:

> **√N rule** — *σ<sub>p</sub>* = *σ* / √*N* if all *N* assets share volatility *σ* and are *uncorrelated*. The most-diversification-possible result.
>
> **Diversification floor** — if all pairwise correlations equal a common value *ρ*, then *σ<sub>p</sub>²* / *σ²* → *ρ* as *N* → ∞. You can't diversify away the *shared* portion; only the idiosyncratic portion goes to zero.

<details>
<summary><b>The math, if you want it: the diversification-floor derivation</b></summary>

Equal-weighted *N*-asset portfolio: *w<sub>i</sub>* = 1/*N* for all *i*. Assume each asset has variance *σ²* and every pair has correlation *ρ* (so Σ<sub>ij</sub> = *σ²* for *i* = *j*, and *ρσ²* otherwise).

*σ<sub>p</sub>²* = (1/*N²*) · [*N* diagonal terms · *σ²* + *N*(*N* − 1) off-diagonal terms · *ρσ²*]

Simplifying: *σ<sub>p</sub>²* / *σ²* = 1/*N* + (*N* − 1)/*N* · *ρ* = *ρ* + (1 − *ρ*)/*N*.

As *N* → ∞, the 1/*N* term vanishes and the ratio approaches *ρ*. The portion (1 − *ρ*) is *idiosyncratic* — diversifiable. The portion *ρ* is *systematic* — irreducible no matter how many assets you add.

This decomposition is the mathematical seed of CAPM and factor models. We'll meet those in a later chapter.

</details>""")

md("s3_4-lead", """### 3.4 The matrix form

The two-asset formula *σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ* gets unwieldy fast. The general *N*-asset version is one line of linear algebra:

> *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w**

where:
- **w** — the weight vector (length *N*; sums to 1 for a fully-invested portfolio).
- **Σ** — the *N* × *N* covariance matrix (which we've been working with).
- **w**ᵀ — the transpose of **w** (a row vector).
- **w**ᵀ **Σ** **w** — a scalar (a 1×1 matrix).

This is the formula we used in §3.3's code (look back: `var_p = w @ sub_cov @ w`). It's the building block of essentially all modern portfolio theory.

<details>
<summary><b>The math, if you want it: the matrix-form derivation</b></summary>

The portfolio return is a weighted sum: *r<sub>p</sub>* = Σ<sub>i</sub> *w<sub>i</sub> r<sub>i</sub>*. Its variance is:

Var(*r<sub>p</sub>*) = Var(Σ<sub>i</sub> *w<sub>i</sub> r<sub>i</sub>*) = Σ<sub>i</sub> Σ<sub>j</sub> *w<sub>i</sub> w<sub>j</sub>* Cov(*r<sub>i</sub>*, *r<sub>j</sub>*) = Σ<sub>i</sub> Σ<sub>j</sub> *w<sub>i</sub> w<sub>j</sub>* Σ<sub>ij</sub>

The double sum Σ<sub>i</sub> Σ<sub>j</sub> *w<sub>i</sub> w<sub>j</sub>* Σ<sub>ij</sub> is the entry-by-entry product of the outer product **ww**ᵀ with **Σ**, summed across all entries — which is exactly what **w**ᵀ **Σ** **w** computes in matrix notation.

The two-asset formula falls out as the *N* = 2 case: write out **w**ᵀ **Σ** **w** with **w** = [*w<sub>X</sub>*, *w<sub>Y</sub>*] and **Σ** = [[*σ<sub>X</sub>²*, *ρσ<sub>X</sub>σ<sub>Y</sub>*], [*ρσ<sub>X</sub>σ<sub>Y</sub>*, *σ<sub>Y</sub>²*]] and you recover the long-form formula exactly.

</details>""")

md("s3_5-lead", """### 3.5 What this means with $100k — portfolio comparisons

Several portfolios you might actually consider, all $100k starting:""")

code("s3_5-code", """def portfolio_vol(weights, returns):
    cov = returns.cov().values
    w = np.array(weights)
    return np.sqrt(w @ cov @ w) * np.sqrt(252)

portfolios = {
    "All SPY (concentrated)":            (["SPY"], [1.0]),
    "All XLK (single sector)":           (["XLK"], [1.0]),
    "Equal-weight 5 sectors":            (["XLK","XLF","XLE","XLV","XLU"], [0.2]*5),
    "60/40 SPY/TLT":                     (["SPY","TLT"], [0.6, 0.4]),
    "Equal-weight all 8":                (tickers, [1/8]*8),
}

rows = []
for name, (basket, weights) in portfolios.items():
    v = portfolio_vol(weights, log_returns[basket])
    rows.append({
        "portfolio": name,
        "annualized vol": f"{v:.2%}",
        "typical-year swing on $100k": f"${100_000 * v:,.0f}",
    })

pd.DataFrame(rows)""")

md("s3_5-interp", """Read the right column. The "typical-year swing" is one annualized standard deviation in dollar terms — a rough sense of how much $100k is bouncing around in a normal year (no fat tails or clustering yet — that's still Chapter 2's lesson).

The drop from "all SPY" to "60/40 SPY/TLT" is large — adding 40% bonds takes you from ~$19k to ~$10k of typical pain. The drop from "60/40" to "equal-weight all 8" is smaller; you're past the easy diversification wins. The "5 sectors" version is barely better than just SPY — within-asset-class diversification has a low ceiling.

Real portfolio construction is a balance between *return* (which generally favors equity-heavy) and *risk* (which generally favors diversification across asset classes). We'll formalize that tradeoff with the **Sharpe ratio** in a later chapter.""")

# --- §4 Part III: Regime / crisis correlation
md("s4-header", """## 4. Part III — Regime / crisis correlation (the empirical wrinkle)

So far the chapter has used a **single** correlation number per pair — the long-run average over 20 years. Same shape of error as Ch1 making for Ch2: real correlations vary over time, and the variation has a particular character. They're not just noisy; they **cluster regime-by-regime**, and they **rise during crashes**.""")

md("s4_1-lead", """### 4.1 Rolling correlation — the bond hedge unhedged itself

Compute SPY/TLT correlation in a 60-day rolling window through history. Same window length as Ch2's rolling vol, for the same noise/lag balance reason.""")

code("s4_1-code", """rolling_corr = log_returns["SPY"].rolling(60).corr(log_returns["TLT"])

fig, ax = plt.subplots(figsize=(11, 4.5))
rolling_corr.plot(ax=ax, lw=1)
ax.axhline(0, color="black", lw=0.5)
ax.axhline(rolling_corr.mean(), color="red", ls="--", lw=1,
           label=f"long-run mean ({rolling_corr.mean():.2f})")
ax.set_ylabel("60-day rolling correlation")
ax.set_xlabel("Date")
ax.set_title("SPY/TLT rolling correlation — 60-day window, 20 years")
ax.grid(alpha=0.3)
ax.legend()
plt.tight_layout()
plt.show()""")

md("s4_1-interp", """The plot tells a story very different from the static "ρ ≈ 0" we computed in Part I:

- **2007–2019** — sustained negative correlation. TLT genuinely *hedged* SPY: when stocks fell, Treasuries rallied. This is the regime that built the reputation of the "60/40 portfolio."
- **March 2020** — a brief sharp positive spike. During the COVID liquidity crisis everything sold off together for a few weeks (forced deleveraging — even safe assets get sold when investors need cash).
- **2022 onward** — sustained positive correlation. Both stocks and bonds fell together as rates rose; the inflation/rate-driven selloff hit duration assets and equities simultaneously.

**The "bond hedge" that worked for 15 years stopped working — and the regime change happened in months, not years.** The flat-line in the static analysis is an *average over genuinely different worlds*.""")

md("s4_2-lead", """### 4.2 Conditional correlation — what happens on bad days?

A static correlation answers "on a typical day, do these move together?" A more interesting question for risk management: "*on the worst days*, do these move together?" Compute correlations conditional on the bottom 5% of SPY days — about 250 days in 20 years, the conventional VaR-territory threshold.""")

code("s4_2-code", """worst_5pct_threshold = log_returns["SPY"].quantile(0.05)
worst_days = log_returns["SPY"] <= worst_5pct_threshold

others = [t for t in tickers if t != "SPY"]
rows = []
for t in others:
    rho_all   = log_returns["SPY"].corr(log_returns[t])
    rho_worst = log_returns.loc[worst_days, "SPY"].corr(log_returns.loc[worst_days, t])
    rows.append({"asset": t, "ρ all days": rho_all, "ρ worst-5% SPY days": rho_worst})

cond = pd.DataFrame(rows)

fig, ax = plt.subplots(figsize=(10, 5))
x = np.arange(len(cond))
width = 0.4
ax.bar(x - width/2, cond["ρ all days"],          width, label="All days",          color="tab:blue")
ax.bar(x + width/2, cond["ρ worst-5% SPY days"], width, label="Worst 5% SPY days", color="tab:red")
ax.axhline(0, color="black", lw=0.5)
ax.set_xticks(x)
ax.set_xticklabels(cond["asset"])
ax.set_ylabel("Correlation with SPY")
ax.set_title("Correlations rise when SPY falls hardest")
ax.legend()
ax.grid(alpha=0.3, axis="y")
plt.tight_layout()
plt.show()
cond.round(3)""")

md("s4_2-interp", """Almost every red bar is *higher* than its corresponding blue bar. The diversification you bought in normal times shrinks on the worst days. The pattern is most dramatic for TLT — its long-run near-zero correlation with SPY climbs visibly when SPY is crashing.

This is **correlation risk in pure form**: the assets you held to spread risk turn out to share more risk than advertised, and the sharing concentrates exactly when you'd hoped for the opposite.""")

md("s4_3-lead", """### 4.3 Calm vs crisis — the heatmap diptych

Two snapshots of the full 8×8 correlation matrix, computed on different sub-windows:

- **Calm regime:** all of 2017 (the lowest-vol full year in our window).
- **Crisis regime:** March–June 2020 (the COVID drawdown and aftermath).""")

code("s4_3-code", """calm   = log_returns.loc["2017-01-01":"2017-12-31"]
crisis = log_returns.loc["2020-03-01":"2020-06-30"]

corr_calm   = calm.corr()
corr_crisis = crisis.corr()

fig, axes = plt.subplots(1, 2, figsize=(15, 7))
for ax, mat, title in [
    (axes[0], corr_calm,   "Calm: 2017"),
    (axes[1], corr_crisis, "Crisis: Mar–Jun 2020"),
]:
    im = ax.imshow(mat.values, cmap="RdYlBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(tickers)))
    ax.set_yticks(range(len(tickers)))
    ax.set_xticklabels(tickers)
    ax.set_yticklabels(tickers)
    for i in range(len(tickers)):
        for j in range(len(tickers)):
            v = mat.iloc[i, j]
            color = "white" if abs(v) > 0.6 else "black"
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", color=color, fontsize=8)
    ax.set_title(title)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

plt.tight_layout()
plt.show()""")

md("s4_3-interp", """Calm 2017 has structure: sector ETFs cluster, TLT is independent, GLD is independent. The matrix has *information* in it.

Crisis 2020 is uniformly red. Almost every cell sits in the 0.6–0.95 range. The structure has collapsed; everything is one position. **In a panic, all bets become a single bet.**

This is the same finding as §4.2's bar chart, told as a picture rather than a number. It's also the formal version of the "diversification fails when needed" intuition that's central to professional risk management.""")

md("s4_4-wrap", """### 4.4 What this means

Real correlation isn't a number — it's a *time-series of matrices*, each one capturing the regime of its window. The single ρ values from Parts I and II are useful summaries the way a single annualized vol is useful in Ch1: they tell you the long-run average. They don't tell you what happens on the worst day.

Two specific deferred topics, named here:

- **DCC-GARCH** (Dynamic Conditional Correlation) — formal time-series model of how correlations evolve. Same flavor as Ch2's GARCH (which models time-varying volatility), now applied to correlations. Future chapter.
- **Tail dependence and copulas** — formal models of the "everything correlates in tails" phenomenon. Much later in the curriculum (alongside EVT).

Neither is required for the practical portfolio reasoning we've done in this chapter. Both exist for readers who want the formal modeling tools.""")

# --- §5 wrap and §6 exercises
md("s5-wrap", """## 5. What we just learned (recap by concept-flavor)

We named five flavors of correlation risk in the opening. Here's what we found, organized by flavor.

### Pairwise correlation
- Pearson correlation (*ρ*) is normalized covariance, bounded in [−1, +1], unitless and comparable across pairs.
- The same correlation number can mean *very* different things visually — sector ETFs at ρ ≈ 0.9 are nearly the same asset; SPY/TLT at ρ ≈ 0 looks like noise.
- The number doesn't capture *time* — that's Part III's job.

### Aggregation / portfolio risk
- Two-asset portfolio variance has a cross-term: 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*. When ρ < 1 it shrinks total variance; that's the diversification benefit.
- The general formula is *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w** — one matrix expression for any portfolio size.
- The marginal benefit of one more asset depends entirely on its correlation with what you already hold. Adding correlated names dilutes; adding decorrelated names actually reduces risk.
- There's a floor: when every pair shares correlation *ρ*, no number of assets can reduce *σ<sub>p</sub>²* / *σ²* below *ρ*. This is the seed of "systematic vs idiosyncratic risk."

### Regime / crisis correlation
- Correlations are not constant. The SPY/TLT correlation has spent ~15 years negative and ~3 years positive in the same 20-year window.
- Conditional on the worst 5% of SPY days, correlations rise across the board — diversification weakens exactly when you'd hoped it would help.
- Calm and crisis windows have visibly different correlation matrices: structure in calm, uniformity in crisis.

### Hidden factor exposure (deferred)
Even if pairwise correlations look low, several "diversified" assets may share an underlying driver (interest rates, oil, the broad market itself). Factor models — CAPM, Fama-French — make this explicit. Future chapter.

### Tail dependence (deferred)
Even when *average* correlation is low, two assets may always crash *together*. The mathematical tools for this (copulas, EVT) live well outside the linear-correlation framework. Much later.""")

md("s6-up-next", """## 6. Up next

**Chapter 4: Risk metrics (drawdown, VaR, Sharpe).** Ch1 promised "max drawdown, we'll formalize later" — that promise gets paid. We'll add path-dependent risk measures to the magnitude / persistence / aggregation flavors covered so far, and bolt the **Sharpe ratio** onto the portfolio constructions from this chapter to start asking "what's the *risk-adjusted return* of these baskets?"""")

md("s7-exercises", """## Exercises

Try these in fresh cells below. Copy any code cell above as a starting point.

1. **Different basket — add crypto.** Pull `BTC-USD` and `ETH-USD` and compute correlations between crypto and the 8-ticker basket. Are crypto correlations with stocks higher or lower than between stocks and bonds? Has it changed across the dataset's window?
2. **The pre-2020 vs post-2020 SPY/TLT story.** Compute SPY/TLT correlation on the 2003–2019 sub-window and the 2020–present sub-window. Two numbers, one striking gap. What changed?
3. **Conditional on TLT instead.** Repeat the §4.2 conditional-correlation exercise, but condition on the worst 5% of *TLT* days. Does the same "everything correlates" pattern emerge, or is it asymmetric?
4. *(stretch)* **Cross-asset-class correlation matrix.** Pull six tickers spanning major asset classes — `QQQ` (large-cap tech), `IWM` (small-cap stocks), `EEM` (emerging markets), `IEF` (intermediate Treasuries), `HYG` (high-yield bonds), `DBC` (broad commodities). Compute the 6×6 correlation matrix as a heatmap. Which pairs are more correlated than you'd have guessed? Which less? *(Hint: HYG often surprises people — it's labeled "bonds" but trades like equities.)*""")

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "version": "3.14.2"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

target = Path("/home/test/repos/quantitative-analysis/03-correlation/lesson.ipynb")
target.write_text(json.dumps(notebook, indent=1))
print(f"wrote {len(cells)} cells to {target}")
```

- [ ] **Step 2.2: Run the builder**

Run: `/home/test/repos/quantitative-analysis/.venv/bin/python /home/test/repos/quantitative-analysis/build_ch3_notebook.py`

Expected output: `wrote N cells to /home/test/repos/quantitative-analysis/03-correlation/lesson.ipynb` where N is around 40–45.

- [ ] **Step 2.3: Execute the notebook**

Run: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace 03-correlation/lesson.ipynb`

Expected: `[NbConvertApp] Writing N bytes to 03-correlation/lesson.ipynb` with no errors.

If a cell errors during execution, identify which and fix the issue before continuing.

- [ ] **Step 2.4: Verify cell outputs match expected ranges**

Run this verification script:

```bash
.venv/bin/python -c "
import json
nb = json.load(open('03-correlation/lesson.ipynb'))
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
                print(txt[:400])
print(f'\\nTotal errors: {errors}')
"
```

Expected ranges to confirm in the printed output:
- `s1-download` reports an 8-column DataFrame with ~5,030 rows.
- `s1-returns` summary table: SPY annualized vol ≈ 19%, TLT vol ≈ 13–15%, GLD vol ≈ 16–18%, sector ETFs in the 17–28% range (XLK and XLE are the highest).
- `s2_1-corr-matrix` — 8×8 with diagonal 1.0; SPY/XLK ≈ 0.9; SPY/TLT ≈ −0.05 to +0.10; SPY/GLD ≈ 0.0 to 0.1.
- `s3_1-code` — 50/50 SPY/TLT vol around 8–10%, well below the weighted average.
- `s3_5-code` — final table has all-SPY vol ~19%, 60/40 vol ~9–11%, equal-weight-8 vol ~11–13%.
- `s4_2-code` — last column "ρ worst-5% SPY days" should be visibly higher than "ρ all days" for most rows; TLT row's gap should be the largest.

**Total errors must be 0.**

- [ ] **Step 2.5: Clean up the builder script**

Run: `rm /home/test/repos/quantitative-analysis/build_ch3_notebook.py`

- [ ] **Step 2.6: Checkpoint** — pause and ask the user about a commit covering Tasks 1 + 2 (full notebook).

---

## Task 3: README §0 (concept-flavors framing) and §1 (setup)

**Files:**
- Create: `03-correlation/README.md`

- [ ] **Step 3.1: Create `03-correlation/README.md` with the following content**

````markdown
# Chapter 3 — Multiple Assets: Correlation and Diversification

> **Goal of this chapter:** take the **correlation risk** flavor that Chapter 2's framing named-but-deferred, break it into its own sub-flavors, and pair the textbook tools (pairwise correlation, portfolio variance) with the empirical finding that correlations themselves aren't constant.

We split the chapter in three parts. **Part I (Pairwise correlation)** introduces the textbook tool for measuring how two assets co-move. **Part II (Aggregation)** generalizes from pairs to portfolios — the variance math that drives modern portfolio construction. **Part III (Regime / crisis correlation)** mirrors Chapter 2's "the textbook ignores time" beat: real correlations shift across regimes and rise sharply in crises, weakening diversification exactly when you need it most.

The chapter uses an 8-ticker basket pulled from yfinance — **SPY, TLT, GLD** for cross-asset texture, plus five US sector ETFs (**XLK, XLF, XLE, XLV, XLU**) for within-asset-class structure. Same 20-year window as Chapter 2, log returns throughout.

---

## What we mean by "correlation risk"

When this chapter says "correlation risk," it doesn't mean a single thing. The concept has several distinct flavors, and they don't reduce to each other:

1. **Pairwise correlation** — how tightly do two specific assets move together? *(Part I)*
2. **Aggregation / portfolio risk** — what does combining *many* assets do to overall risk? *(Part II)*
3. **Regime / crisis correlation** — correlations aren't constant. They spike toward 1 in crashes, so diversification weakens exactly when you'd hoped it would work. *(Part III)*
4. **Hidden factor exposure** — seemingly distinct assets often share underlying drivers (interest rates, oil, the broad market itself). A "diversified" portfolio may be a single bet in disguise. *Deferred — future factor-models chapter.*
5. **Tail dependence** — even when *average* correlation is low, two assets may always crash *together*. *Deferred — much later (with EVT / copulas).*

The chapter delivers on flavors #1–#3. The other two get named here so you know they exist and where to expect them.

---

## 1. Setup

Same library stack as Chapter 2 — no new dependencies. The change vs Ch2 is the data: we pull eight tickers in one `yf.download(...)` call and compute log returns for the whole panel.

Eight tickers, three storytelling roles:
- **Cross-asset trio (SPY, TLT, GLD)** — carries the pairwise-correlation visuals and the regime-shift demo. TLT's correlation with SPY is famously *non-constant* and will be the chapter's most dramatic finding.
- **Sector ETFs (XLK tech, XLF financials, XLE energy, XLV healthcare, XLU utilities)** — carries the within-asset-class portfolio-math heatmap and the "diversification within equities is limited" lesson.
- **All eight together** — appears in the master correlation matrix and the calm-vs-crisis heatmap diptych.

After the setup cells run, expect:
- An 8-column return panel with **~5,030 daily observations** spanning ~20 years.
- Annualized volatility per asset roughly: SPY ~19%, TLT ~14%, GLD ~17%, sector ETFs in the 17–28% range (XLK and XLE highest).

The setup section also introduces the **covariance matrix Σ** as the natural N-asset generalization of σ from Chapter 2: a square *N* × *N* matrix where the diagonal is each asset's variance and the off-diagonals are pairwise covariances. We'll spend the rest of the chapter doing useful things with this matrix.
````

- [ ] **Step 3.2: Render the README in a Markdown preview**

Open `03-correlation/README.md` in VS Code's markdown preview (`Ctrl+Shift+V`). Confirm:
- Goal callout renders as a blockquote.
- Numbered concept-flavors list is intact.
- Ticker references (SPY, TLT, GLD, XLK, XLF, XLE, XLV, XLU) all bold.

- [ ] **Step 3.3: Checkpoint** — pause.

---

## Task 4: README Part I (§2 — pairwise correlation)

**Files:**
- Modify: `03-correlation/README.md` (append)

- [ ] **Step 4.1: Append the following to `03-correlation/README.md`**

````markdown
## 2. Part I — Pairwise correlation (the textbook tool)

The covariance matrix from §1 has all the information we need, but it's hard to *read*. Daily-return variances are tiny numbers; the matrix entries scale with units. The conventional fix is to normalize covariances into **correlations** — unitless numbers in a fixed range that are directly comparable across pairs.

### 2.1 Pearson correlation — the unitless cousin of covariance

> *ρ<sub>XY</sub>* = Cov(*X*, *Y*) / (*σ<sub>X</sub> σ<sub>Y</sub>*)

where:
- Cov(*X*, *Y*) — covariance between *X* and *Y* (Ch2 §3.2).
- *σ<sub>X</sub>*, *σ<sub>Y</sub>* — standard deviations of *X* and *Y*.
- *ρ<sub>XY</sub>* — the **Pearson correlation coefficient**, bounded in [−1, +1].

Why divide by the product of standard deviations? Covariance scales with the units of the inputs. The normalization removes that scale. A correlation computed on percent returns gives the same answer as one on basis-point returns, on the same data. Bounded range, comparable across pairs.

<details>
<summary><b>The math, if you want it: why <i>ρ</i> is bounded in [−1, +1]</b></summary>

This is the **Cauchy–Schwarz inequality** in disguise. For any two random variables *X* and *Y*:

> |Cov(*X*, *Y*)| ≤ *σ<sub>X</sub> σ<sub>Y</sub>*

Proof sketch: define *Z* = *X*/*σ<sub>X</sub>* ± *Y*/*σ<sub>Y</sub>*. Var(*Z*) ≥ 0 because variance can't be negative. Expanding gives 2 ± 2 Cov(*X*, *Y*)/(*σ<sub>X</sub> σ<sub>Y</sub>*) ≥ 0, which rearranges to |Cov(*X*, *Y*)| ≤ *σ<sub>X</sub> σ<sub>Y</sub>*. Dividing through gives |*ρ*| ≤ 1.

The bounds are *attained* when *Y* is a perfect linear function of *X*: *ρ* = +1 when *Y* = *aX* + *b* with *a* > 0, *ρ* = −1 when *a* < 0, *ρ* = 0 when *X* and *Y* are linearly independent (though they may still be related nonlinearly — a famous correlation pitfall).

</details>

### 2.2 What different correlations look like

The notebook plots three scatter plots side by side, all on the same axis scale: SPY vs XLK (*ρ* ≈ 0.9), SPY vs XLU (*ρ* ≈ 0.65), SPY vs TLT (*ρ* ≈ 0).

- **SPY vs XLK** is a tight diagonal cloud — these are nearly the same asset. XLK is large-cap tech, which dominates SPY's market-cap-weighted index.
- **SPY vs XLU** is a clearly correlated cloud, but visibly looser. Utilities are equity but defensive; they move with the market on most days, with less amplitude.
- **SPY vs TLT** is a blob with no diagonal. The directions are *on average* independent.

The "correlation captures *linear* co-movement" framing is literal — *ρ* ≈ +1 means the cloud lies on a line of positive slope, *ρ* ≈ 0 means there's no preferred line.

### 2.3 What this means with $100k

Imagine you hold $100k of SPY and want to "diversify" by adding another $100k of something else. Three candidate add-ons (assuming for simplicity all three add-ons have the same vol as SPY):

- **Add $100k of XLK** (*ρ* ≈ 0.9 with SPY) — the combined $200k position has roughly **1.95×** the risk of the original $100k SPY. Almost no diversification benefit; you doubled exposure, not safety.
- **Add $100k of XLU** (*ρ* ≈ 0.65) — combined position has roughly **1.81×** the original risk. Better, but still mostly the same risk.
- **Add $100k of TLT** (*ρ* ≈ 0) — combined position has only **√2 ≈ 1.41×** the original risk. The textbook "60/40-style" diversification result. The cross-asset move is the cleanest example of correlation working in your favor.

The 1.95×, 1.81×, 1.41× factors come from the two-asset variance formula in §3.1 — which we'll prove next.
````

- [ ] **Step 4.2: Render and verify**

Confirm the collapsible `<details>` block in §2.1 renders as a clickable disclosure and the 1.95×/1.81×/1.41× table-like structure in §2.3 reads cleanly.

- [ ] **Step 4.3: Checkpoint**

---

## Task 5: README Part II (§3 — aggregation and the diversification math)

**Files:**
- Modify: `03-correlation/README.md` (append)

- [ ] **Step 5.1: Append the following**

````markdown
## 3. Part II — Aggregation: portfolio variance and the diversification math

Pairs are the simplest case. Real portfolios have many positions. Going from "two correlations" to "many" is where the matrix Σ from §1 starts paying for itself.

### 3.1 Two-asset portfolio variance

Hold *w<sub>X</sub>* fraction of asset X and *w<sub>Y</sub>* = 1 − *w<sub>X</sub>* of asset Y. The portfolio's daily return is *r<sub>p</sub>* = *w<sub>X</sub> r<sub>X</sub>* + *w<sub>Y</sub> r<sub>Y</sub>*. Its variance is:

> *σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

where:
- *w<sub>X</sub>*, *w<sub>Y</sub>* — the **portfolio weights** (must sum to 1 for a fully-invested long-only portfolio).
- *σ<sub>X</sub>*, *σ<sub>Y</sub>* — individual asset standard deviations.
- *ρ* — the pairwise correlation between *X* and *Y*.
- *σ<sub>p</sub>²* — the variance of the portfolio's return.

Three terms: two **own-variance** terms (each weighted by *w²*) plus the **cross-term** (the diversification engine). When *ρ* < 1, the cross-term shrinks total variance below the weighted average. When *ρ* = 1, no diversification; when *ρ* = −1, perfect hedging is possible — there exist weights making *σ<sub>p</sub>* = 0.

<details>
<summary><b>The math, if you want it: deriving the two-asset variance</b></summary>

Var(*aX* + *bY*) = *a²* Var(*X*) + *b²* Var(*Y*) + 2*ab* Cov(*X*, *Y*).

Plug in *a* = *w<sub>X</sub>*, *b* = *w<sub>Y</sub>*, Var(*X*) = *σ<sub>X</sub>²*, Cov(*X*, *Y*) = *ρ σ<sub>X</sub> σ<sub>Y</sub>* (rearranged from the correlation definition):

*σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

The variance-of-a-sum identity itself comes from expanding *E*[((*aX* + *bY*) − *E*[*aX* + *bY*])²]: the cross-term is 2*ab E*[(*X* − *μ<sub>X</sub>*)(*Y* − *μ<sub>Y</sub>*)] = 2*ab* Cov(*X*, *Y*) — exactly the *E*[·] machinery from Ch2 §2.2.

</details>

### 3.2 The correlation matrix as a heatmap

The 8×8 correlation matrix from §2 has structure that's easier to see as a heatmap than as a table of numbers. The notebook renders it. Three visual blocks:

- **Sector ETFs (XLK / XLF / XLE / XLV / XLU)** form a high-correlation cluster. They're all flavors of US equity risk.
- **TLT row/column** is the visual outlier — pale or even slightly blue cells. Long-run correlation with the equity assets is near zero.
- **GLD row/column** has uniformly low correlation with everything — neither equity nor bonds explains it.

This matrix is the input we feed into the portfolio-variance machinery next.

### 3.3 The diversification math empirically

The two-asset formula generalizes to *N* assets — but rather than write the formula yet, the notebook just *computes* portfolio vol as we add tickers one at a time, in a deliberate dramatic order:

`XLK → +XLF → +XLE → +XLV → +XLU → +TLT → +GLD`

Start with one sector. Add four more sectors (correlated). Then add TLT (cross-asset, decorrelated). Then add GLD. Equal weights at each step.

Reading the resulting curve from left to right:

- **N = 1 (just XLK)** — high vol, ~25%+ annualized. A single sector is a concentrated bet.
- **N = 2 to 5 (adding sector ETFs)** — vol drops, but each step is modest. Adding correlated names doesn't help much.
- **N = 6 (adding TLT)** — sharp drop. TLT is uncorrelated-to-negative with the equity basket, so the cross-term in the variance formula works in your favor for the first time.
- **N = 7 (adding GLD)** — small further drop. Most of the diversification benefit was captured at N = 6.

**The marginal benefit of one more asset depends entirely on its correlation with what you already hold.**

Two limit results:

> **√N rule** — *σ<sub>p</sub>* = *σ* / √*N* if all *N* assets share volatility *σ* and are *uncorrelated*.
>
> **Diversification floor** — if all pairwise correlations equal a common value *ρ*, then *σ<sub>p</sub>²* / *σ²* → *ρ* as *N* → ∞.

The √N rule says "uncorrelated assets give you the most diversification possible." The floor says "correlated assets have a cap on how much you can diversify." Real portfolios live between the two.

<details>
<summary><b>The math, if you want it: the diversification-floor derivation</b></summary>

Equal-weighted *N*-asset portfolio: *w<sub>i</sub>* = 1/*N*. Assume each asset has variance *σ²* and every pair has correlation *ρ* (so Σ<sub>ij</sub> = *σ²* for *i* = *j*, *ρσ²* otherwise).

*σ<sub>p</sub>²* = (1/*N²*) · [*N* · *σ²* + *N*(*N* − 1) · *ρσ²*]

Simplifying: *σ<sub>p</sub>²* / *σ²* = 1/*N* + (*N* − 1)/*N* · *ρ* = *ρ* + (1 − *ρ*)/*N*.

As *N* → ∞ the 1/*N* term vanishes and the ratio approaches *ρ*. The portion (1 − *ρ*) is **idiosyncratic** — diversifiable. The portion *ρ* is **systematic** — irreducible. This decomposition is the seed of CAPM and factor models. Future chapter.

</details>

### 3.4 The matrix form

The two-asset formula gets unwieldy fast. The general *N*-asset version is one line of linear algebra:

> *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w**

where:
- **w** — the weight vector (length *N*; sums to 1 for a fully-invested portfolio).
- **Σ** — the *N* × *N* covariance matrix.
- **w**ᵀ — the transpose of **w** (a row vector).
- **w**ᵀ **Σ** **w** — a scalar (a 1×1 matrix).

This is the formula the notebook used to compute every portfolio vol in §3.3. It's the building block of essentially all modern portfolio theory.

<details>
<summary><b>The math, if you want it: the matrix-form derivation</b></summary>

The portfolio return is a weighted sum: *r<sub>p</sub>* = Σ<sub>i</sub> *w<sub>i</sub> r<sub>i</sub>*. Its variance is:

Var(*r<sub>p</sub>*) = Σ<sub>i</sub> Σ<sub>j</sub> *w<sub>i</sub> w<sub>j</sub>* Cov(*r<sub>i</sub>*, *r<sub>j</sub>*) = Σ<sub>i</sub> Σ<sub>j</sub> *w<sub>i</sub> w<sub>j</sub>* Σ<sub>ij</sub>

The double sum equals **w**ᵀ **Σ** **w** in matrix notation. The two-asset formula falls out as the *N* = 2 case.

</details>

### 3.5 What this means with $100k

The notebook tabulates several portfolios:

- **All SPY** — concentrated equity, vol ~19% → ~$19k typical-year swing on $100k.
- **All XLK** — concentrated single sector, vol ~25%+ → ~$25k+.
- **Equal-weight 5 sectors** — within-equity diversification, vol slightly below SPY's, ~17–18% → ~$17–18k.
- **60/40 SPY/TLT** — the canonical balanced portfolio, vol ~9–11% → ~$9–11k.
- **Equal-weight all 8** — full cross-asset basket, vol ~11–13% → ~$11–13k.

The drop from "all SPY" to "60/40" is large — adding 40% bonds takes typical pain from ~$19k to ~$10k. The drop from "60/40" to "equal-weight all 8" is much smaller; the easy diversification wins are already captured by the cross-asset move.

Real portfolio construction trades off return (which favors equity-heavy) against risk (which favors diversification across asset classes). We'll formalize that tradeoff with the **Sharpe ratio** in Chapter 4.
````

- [ ] **Step 5.2: Render and verify**

Confirm both `<details>` blocks render correctly and the 5-portfolio comparison reads cleanly.

- [ ] **Step 5.3: Checkpoint**

---

## Task 6: README Part III (§4 — regime / crisis correlation)

**Files:**
- Modify: `03-correlation/README.md` (append)

- [ ] **Step 6.1: Append the following**

````markdown
## 4. Part III — Regime / crisis correlation (the empirical wrinkle)

Parts I and II used a **single** correlation number per pair — the long-run average over 20 years. Same shape of error Ch1 made and Ch2 corrected: real correlations vary over time, and the variation has a particular character. They cluster regime-by-regime, and they rise during crashes.

### 4.1 Rolling correlation — the bond hedge unhedged itself

Compute SPY/TLT correlation in a 60-day rolling window through history. Same window length as Ch2's rolling vol, for the same noise-vs-lag balance reason. The notebook plots the resulting time series.

The story it tells:
- **2007–2019:** sustained negative correlation. TLT genuinely *hedged* SPY — when stocks fell, Treasuries rallied. This is the regime that built the reputation of the 60/40 portfolio.
- **March 2020:** a brief sharp positive spike. During the COVID liquidity crisis everything sold off together — forced deleveraging means even safe assets get sold.
- **2022 onward:** sustained positive correlation. Both stocks and bonds fell together as rates rose.

**The "bond hedge" that worked for 15 years stopped working — and the regime change happened in months, not years.** The flat line of the static analysis is an *average over genuinely different worlds*.

### 4.2 Conditional correlation — what happens on bad days?

A static correlation answers "on a typical day, do these move together?" A more interesting question for risk management: *on the worst days,* do these move together?

The notebook computes correlations conditional on the bottom 5% of SPY days — about 250 days in 20 years, the conventional VaR-territory threshold — and bars them next to the unconditional ("all days") correlations.

Almost every red bar (worst-5%-of-SPY-days) is *higher* than its blue bar (all days). The diversification you bought in normal times shrinks on the worst days. The TLT bar is the most dramatic — its near-zero unconditional correlation with SPY rises substantially in stress.

This is **correlation risk in pure form**: assets you held to spread risk turn out to share more risk than advertised, and the sharing concentrates exactly when you'd hoped for the opposite.

### 4.3 Calm vs crisis — the heatmap diptych

Two snapshots of the full 8×8 correlation matrix:
- **Calm:** all of 2017 (the lowest-vol full year in the window).
- **Crisis:** March–June 2020 (the COVID drawdown and aftermath).

In the calm matrix, structure is visible: sector ETFs cluster, TLT and GLD are independent, off-diagonal entries span a wide range. In the crisis matrix, almost every cell sits in the 0.6–0.95 range — the matrix has gone uniformly red. **In a panic, all bets become a single bet.**

### 4.4 What this means

Real correlation isn't a number — it's a *time-series of matrices*. The single *ρ* values from Parts I and II are useful summaries the way a single annualized vol from Ch1 is useful: they tell you the long-run average. They don't tell you what happens on the worst day.

Two specific deferred topics named here:

- **DCC-GARCH** (Dynamic Conditional Correlation) — formal time-series model of how correlations evolve. Same flavor as Ch2's GARCH (which models time-varying volatility), now applied to correlations. Future chapter.
- **Tail dependence and copulas** — formal models of the "everything correlates in tails" phenomenon. Much later in the curriculum (alongside EVT).

Neither is required for the practical portfolio reasoning we've done in this chapter. Both exist for readers who want the formal modeling tools.
````

- [ ] **Step 6.2: Render and verify**

Confirm the §4 narrative reads cleanly through to §4.4's "what this means" closer.

- [ ] **Step 6.3: Checkpoint**

---

## Task 7: README §5 (recap by concept-flavor) and §6 (up next + Key Terms + exercises)

**Files:**
- Modify: `03-correlation/README.md` (append)

- [ ] **Step 7.1: Append the following**

````markdown
## 5. What we just learned (recap by concept-flavor)

We named five flavors of correlation risk in the opening. Here's what we found, organized by flavor.

### Pairwise correlation
- Pearson correlation (*ρ*) is normalized covariance, bounded in [−1, +1], unitless and comparable across pairs.
- The same number can mean visually very different things — sector ETFs at *ρ* ≈ 0.9 are nearly the same asset; SPY/TLT at *ρ* ≈ 0 looks like noise.
- *ρ* alone doesn't capture *time* — that's Part III's job.

### Aggregation / portfolio risk
- Two-asset portfolio variance has a cross-term: 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*. When *ρ* < 1 it shrinks total variance — that's the **diversification benefit**.
- The general formula is *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w** — one matrix expression for any portfolio size.
- The marginal benefit of one more asset depends on its correlation with what you already hold. Adding correlated names dilutes; adding decorrelated names actually reduces risk.
- There's a floor: when every pair shares correlation *ρ*, no number of assets can reduce *σ<sub>p</sub>²* / *σ²* below *ρ*. This is the seed of "**systematic vs idiosyncratic risk**."

### Regime / crisis correlation
- Correlations are not constant. The SPY/TLT correlation has spent ~15 years negative and ~3 years positive in the same 20-year window.
- Conditional on the worst 5% of SPY days, correlations rise across the board. Diversification weakens exactly when you'd hoped for the opposite.
- Calm and crisis windows have visibly different correlation matrices: structure in calm, uniformity in crisis.

### Hidden factor exposure (deferred)
Even when pairwise correlations look low, several "diversified" assets may share an underlying driver (interest rates, oil, the broad market). Factor models — CAPM, Fama-French — make this explicit. Future chapter.

### Tail dependence (deferred)
Even when *average* correlation is low, two assets may always crash *together*. The mathematical tools for this (copulas, EVT) live outside the linear-correlation framework. Much later.

---

## Key Terms (Chapter 3)

| Term | Meaning | First used |
|------|---------|-----------:|
| Pearson correlation (*ρ*) | Cov(*X*, *Y*) / (*σ<sub>X</sub> σ<sub>Y</sub>*); unitless, in [−1, +1] | §2.1 |
| Correlation matrix | *N* × *N* symmetric matrix of pairwise correlations | §2.1 |
| Covariance matrix (Σ) | *N* × *N* symmetric matrix; diagonal is variances | §1 |
| Portfolio weights (**w**) | Vector of allocations, sums to 1 (fully invested) | §3.1 |
| Portfolio variance / std (*σ<sub>p</sub>*) | Variance / std of the weighted basket return | §3.1 |
| Diversification benefit | Reduction in portfolio vol below the weighted average of individual vols | §3.1 |
| Equal-weight portfolio | Every asset gets weight 1/*N* | §3.3 |
| 60/40 portfolio | Canonical 60% stocks / 40% bonds; classical balanced allocation | §3.5 |
| √*N* rule | Equal-weighted vol of *N* uncorrelated assets is *σ* / √*N* | §3.3 |
| Diversification floor | When pairwise correlations share value *ρ*, *σ<sub>p</sub>²*/*σ²* → *ρ* as *N* → ∞ | §3.3 |
| Systematic risk | The risk that *can't* be diversified away | §3.3 |
| Idiosyncratic risk | Asset-specific risk; can be diversified away | §3.3 |
| Conditional correlation | Correlation computed on a subset of observations (e.g., worst-5% days) | §4.2 |
| Rolling correlation | Pairwise correlation computed over a sliding window | §4.1 |
| Crisis correlation | Informal name for the empirical fact that correlations rise during stress | §4 |
| Hidden factor exposure | When seemingly distinct assets share underlying drivers — deferred | §0 |
| Tail dependence | Correlations only manifest in tails of the joint distribution — deferred | §0 |

---

## Exercises

Try these in fresh cells at the bottom of the notebook:

1. **Different basket — add crypto.** Pull `BTC-USD` and `ETH-USD` and compute correlations between crypto and the 8-ticker basket. Are crypto correlations with stocks higher or lower than between stocks and bonds? Has it changed across the dataset's window?
2. **The pre-2020 vs post-2020 SPY/TLT story.** Compute SPY/TLT correlation on the 2003–2019 sub-window and the 2020–present sub-window. Two numbers, one striking gap. What changed?
3. **Conditional on TLT instead.** Repeat the §4.2 conditional-correlation exercise, but condition on the worst 5% of *TLT* days. Does the same "everything correlates" pattern emerge, or is it asymmetric?
4. *(stretch)* **Cross-asset-class correlation matrix.** Pull six tickers spanning major asset classes — `QQQ` (large-cap tech), `IWM` (small-cap stocks), `EEM` (emerging markets), `IEF` (intermediate Treasuries), `HYG` (high-yield bonds), `DBC` (broad commodities). Compute the 6×6 correlation matrix as a heatmap. Which pairs are more correlated than you'd have guessed? Which less? *(Hint: HYG often surprises people — it's labeled "bonds" but trades like equities.)*

---

## Up next

**Chapter 4: Risk metrics — drawdown, VaR, Sharpe.** Chapter 1 promised "max drawdown, we'll formalize later" — that promise gets paid. We'll add path-dependent risk measures to the magnitude / persistence / aggregation flavors covered so far, and bolt the **Sharpe ratio** onto the portfolio constructions from this chapter to start asking "what's the *risk-adjusted return* of these baskets?"
````

- [ ] **Step 7.2: Render and verify**

Confirm Key Terms table renders cleanly with all rows aligned, exercise list is numbered 1–4, and the Up next paragraph closes the chapter.

- [ ] **Step 7.3: Checkpoint** — README is fully drafted. Pause and ask user about a commit covering Tasks 3–7 (full README).

---

## Task 8: Update root `glossary.md` with Ch3 entries

**Files:**
- Modify: `glossary.md`

- [ ] **Step 8.1: Open `glossary.md` and insert the following entries alphabetically**

The entries below should be **interleaved into the existing alphabetical structure**. Section headings that don't yet exist (e.g., possibly `## P` or `## H`) need to be created in correct alphabetical position.

In **§A** (after the existing Ch2 Autocorrelation entry):

```markdown
**Aggregation risk** *(Ch. 3)* — The risk that emerges from combining many
positions; what the covariance matrix and portfolio variance formula capture.
Distinct from pairwise correlation in that it concerns the *whole* basket,
not individual pairs.
```

In **§C** (after Covariance):

```markdown
**Conditional correlation** *(Ch. 3)* — Correlation computed on a subset of
observations, often a tail (e.g., worst-5%-of-SPY-days). Rises in stress for
most asset pairs — the formal statement of "diversification fails when
needed."

**Correlation matrix** *(Ch. 3)* — *N* × *N* symmetric matrix of pairwise
Pearson correlations among *N* assets. Diagonal is 1.0; off-diagonals are in
[−1, +1].

**Covariance matrix (Σ)** *(Ch. 3)* — *N* × *N* symmetric matrix where Σ<sub>ij</sub> = Cov(*r<sub>i</sub>*, *r<sub>j</sub>*). Diagonal is variances; off-diagonals are pairwise covariances. The natural N-asset generalization of σ from Ch. 2.

**Crisis correlation** *(Ch. 3)* — Informal name for the empirical finding
that correlations rise during stress regimes, weakening diversification when
it's needed most.
```

In **§D** (alphabetically before Distribution):

```markdown
**Diversification benefit** *(Ch. 3)* — The reduction in a portfolio's
volatility below the weighted average of its individual assets' volatilities,
attributable to *ρ* < 1 between the assets.

**Diversification floor** *(Ch. 3)* — When all pairwise correlations equal a
common value *ρ*, the equal-weighted portfolio variance ratio *σ<sub>p</sub>²* / *σ²* approaches *ρ* as *N* → ∞ — the irreducible (systematic) portion.
```

In **§E** (after the existing Equal-weight... no, there's no Equal-weight yet, add a new entry alphabetically. After "Excess kurtosis"):

```markdown
**Equal-weight portfolio** *(Ch. 3)* — A portfolio in which every asset has
the same weight 1/*N*. The simplest non-trivial weighting scheme; benchmark
against which more sophisticated schemes are measured.
```

Create **§H** if it doesn't already have content beyond Ch1's "Histogram":

```markdown
**Hidden factor exposure** *(Ch. 3)* — The phenomenon that seemingly
distinct assets share underlying drivers (interest rates, oil, the broad
market itself), so a "diversified" portfolio may be a single bet. Named in
Ch. 3 as a deferred flavor of correlation risk; formal treatment in a future
factor-models chapter.
```

In **§I** (after i.i.d. and Index):

```markdown
**Idiosyncratic risk** *(Ch. 3)* — The asset-specific portion of risk that
can be diversified away in a sufficiently large basket. Complement of
*systematic risk*.
```

In **§P** (the section currently containing "Price series"):

```markdown
**Pearson correlation (*ρ*)** *(Ch. 3)* — *ρ<sub>XY</sub>* = Cov(*X*, *Y*) /
(*σ<sub>X</sub> σ<sub>Y</sub>*). The unitless, scale-free version of
covariance; bounded in [−1, +1]; the building block of every portfolio-risk
calculation.

**Portfolio variance / standard deviation (σ<sub>p</sub>)** *(Ch. 3)* — Variance /
standard deviation of a weighted basket's return. Computable from individual
volatilities and pairwise correlations via *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w**.

**Portfolio weights (w)** *(Ch. 3)* — Vector of allocations across assets;
sums to 1 for a fully-invested long-only portfolio.
```

In **§R** (insert before Risk):

```markdown
**Rolling correlation** *(Ch. 3)* — Pairwise correlation computed over a
sliding window of recent observations. Reveals time-variation that a
single-number correlation hides.
```

In **§S** (alphabetically after "Stationarity"):

```markdown
**Systematic risk** *(Ch. 3)* — The portion of risk that *can't* be
diversified away — common factor exposure shared across many assets.
Complement of *idiosyncratic risk*; formalized via factor models in later
chapters.
```

In **§T** (alphabetically before Ticker):

```markdown
**Tail dependence** *(Ch. 3)* — When two assets correlate primarily (or only)
in the extreme tails of the joint distribution. Standard linear correlation
can't capture this. Named in Ch. 3 as a deferred flavor of correlation risk;
treatment alongside EVT and copulas much later.
```

In **§Symbols** or **§√** (the current "√t rule" section):

```markdown
**√N rule** *(Ch. 3)* — *σ<sub>p</sub>* = *σ* / √*N* for an equal-weighted
portfolio of *N* uncorrelated assets with common volatility *σ*. The most
diversification mathematically possible; a useful upper-bound benchmark.
```

The "60/40 portfolio" entry should also go somewhere — alphabetically, "60" sorts as a numeral. Stick it in a "**## Numerals**" section at the very top (above §A) if not present, or under §Symbols:

```markdown
**60/40 portfolio** *(Ch. 3)* — Canonical balanced allocation of 60% equities
(typically broad US equity) and 40% bonds (typically intermediate-to-long
Treasuries). The default "diversified" portfolio in retail and pension
contexts.
```

- [ ] **Step 8.2: Verify alphabetical order**

Skim the entire `glossary.md` from top to bottom. Every section heading should be in alphabetical order (A, B, C, …); within each section, entries should be alphabetical. No duplicate entries.

- [ ] **Step 8.3: Checkpoint**

---

## Task 9: Update Ch2 README "Up next" and root README curriculum row

**Files:**
- Modify: `02-risk/README.md`
- Modify: `README.md` (root)

- [ ] **Step 9.1: Read the current Ch2 "Up next" paragraph**

Open `02-risk/README.md` and locate the "Up next" section (toward the end). It currently points to Chapter 3 broadly; update it to name the three concept-flavors covered.

Replace the existing Up-next paragraph with:

```markdown
## Up next

**Chapter 3: Multiple Assets — Correlation and Diversification.** We move
from one ticker to a basket. The chapter takes the **correlation risk**
flavor named in the framing here and breaks it into three concept-flavors:
**pairwise correlation** between two assets (Part I), **aggregation /
portfolio risk** when many assets combine (Part II), and **regime / crisis
correlation** — the empirical finding that correlations themselves shift
across regimes and rise in crashes, weakening diversification exactly when
it's needed most (Part III). Same Ch2 pattern: build the textbook tool, then
show how reality breaks it.
```

- [ ] **Step 9.2: Update the root `README.md` curriculum table**

Open `README.md` (in repo root) and find the curriculum table. Update the Ch3 row from "_coming next_" to its full title with a link.

Replace the existing Ch3 row with:

```markdown
| 03 | [`03-correlation`](./03-correlation) | Multiple assets: correlation and diversification — pairwise correlation, the diversification math, and how correlations themselves shift across regimes. |
```

- [ ] **Step 9.3: Render both files and verify**

Open Ch2 README and root README in a markdown preview. Confirm the Up next paragraph reads cleanly and the curriculum row links to `03-correlation/`.

- [ ] **Step 9.4: Checkpoint**

---

## Task 10: End-to-end smoke test

**Files:** none modified

- [ ] **Step 10.1: Restart kernel and re-run `03-correlation/lesson.ipynb`**

Run: `.venv/bin/jupyter nbconvert --to notebook --execute --inplace 03-correlation/lesson.ipynb`

Expected: zero errors. Re-run the cell-output verification script from Task 2.4 to confirm.

- [ ] **Step 10.2: Render `03-correlation/README.md` end-to-end**

Open in markdown preview. Confirm:
- All section headings render in correct order (concept-flavors framing, §1, §2, §3, §4, §5, Key Terms, Exercises, Up next).
- All `<details>` blocks (the four collapsible math derivations) expand cleanly when clicked.
- All formulas render with subscripts/italics/superscripts intact.
- All tables (correlation matrix references, portfolio comparison, Key Terms) render with clean column alignment.

- [ ] **Step 10.3: Render `glossary.md`**

Confirm all entries are in alphabetical order, no broken markdown syntax, no duplicate entries.

- [ ] **Step 10.4: Render Ch2 README and root README**

Confirm Ch2's reworded "Up next" paragraph reads cleanly and the root README's Ch3 row links correctly.

- [ ] **Step 10.5: Checkpoint** — full chapter verified.

---

## Task 11: Update curriculum-roadmap memory

**Files:**
- Modify: `/home/test/.claude/projects/-home-test-repos-quantitative-analysis/memory/project_curriculum_roadmap.md`

- [ ] **Step 11.1: Update the Ch03 entry**

Find the Ch03 status block (currently marked PLANNED) and replace it with:

```markdown
### Ch 03 — Multiple Assets: Correlation and Diversification ✅ DONE
**Covered:** three concept-flavors of correlation risk (pairwise, aggregation, regime/crisis). Pairwise: Pearson correlation, scatter visuals, Cauchy–Schwarz bound. Aggregation: two-asset variance formula, correlation matrix heatmap, the dramatic-order diversification demo (XLK→sectors→TLT→GLD), √N rule, diversification floor, matrix form **w**ᵀ **Σ** **w**, $100k portfolio comparisons. Regime/crisis: SPY/TLT 60-day rolling correlation showing the 2020 sign-flip, conditional correlation in worst-5% days, calm-vs-crisis 8×8 heatmap diptych. Previewed (deferred): hidden factor exposure (factor-models chapter), tail dependence (with EVT), DCC-GARCH (with GARCH).
**Data:** 8-ticker basket — SPY, TLT, GLD + 5 sector ETFs (XLK, XLF, XLE, XLV, XLU); 20-year daily window matching Ch2.
**Promises to honor in later chapters:**
- Sharpe ratio still owed; should land in Ch4 risk-metrics chapter alongside drawdown.
- Hidden factor exposure → future factor-models chapter (CAPM, Fama-French).
- Tail dependence → much later, with EVT.
- DCC-GARCH → with GARCH.
```

- [ ] **Step 11.2: Verify the roadmap reads cleanly**

Confirm Ch01 → Ch02 → Ch03 progression is consistent and the deferred-topic backlog still reflects what's outstanding.

- [ ] **Step 11.3: Final checkpoint** — entire chapter complete. Stop and ask the user about the final commit covering Tasks 8–11 (or however they want to split commits).

---

## Self-review notes (for the implementer)

**Spec coverage:**
- Spec §2 goals: covered by Tasks 2 (notebook), 4–7 (README sections).
- Spec §3 narrative arc: Tasks 2 (notebook intro), 3 (README framing).
- Spec §4 data: Task 2 setup cells.
- Spec §5 section structure: §1 setup → Task 2 + 3; §2 Part I → Task 4; §3 Part II → Task 5; §4 Part III → Task 6; §5 recap + §6 → Task 7.
- Spec §6 new terminology: Tasks 4, 5, 6, 7 (inline glosses + Key Terms), 8 (glossary).
- Spec §7 formulas: each appears in both notebook (Task 2) and README (Tasks 4–6).
- Spec §8 dependencies: Task 1 (verify, no new packages).
- Spec §10–11 cross-chapter promises: Tasks 9 (Ch1 link from "Multiple assets — correlation and diversification" curriculum line — implicit in Task 9's root README update; Ch2 "Up next" — Task 9.1).
- Spec §12 edits to existing files: Task 9 (Ch2 + root README).
- Spec §13 (locked implementation choices): all baked into Task 2's builder script — XLK→GLD ticker order in §3.3, 5% threshold in §4.2, 60-day rolling window in §4.1.

**Type/symbol consistency:** *r*, *μ*, *σ*, *ρ*, *X*, *Y*, *w*, **Σ**, *N*, *t*, *k* used identically across tasks. Cell-id naming convention `s<section>_<subsection>-<role>` consistent throughout the notebook builder.

**No placeholders.** Each step contains complete code or complete prose; verification commands include expected output ranges; no "TBD" / "TODO" / "fill in later" anywhere.
