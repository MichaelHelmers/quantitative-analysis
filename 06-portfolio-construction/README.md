# Chapter 6 — Portfolio Construction: Efficient Frontier and Risk Parity

> **Goal of this chapter:** *the decision*. Five chapters built every input — returns (Ch1), volatility (Ch2), correlation and the diversification math (Ch3), expected returns with error bars (Ch4), Sharpe and friends (Ch5). This chapter answers the question those inputs were always pointing at: **given them, what weights should you actually pick?**

Three philosophies, three sections, one hard lesson woven through them.

- **§3 — Minimize risk.** Markowitz's mean-variance optimization, the Global Minimum Variance portfolio, and the **efficient frontier**. The classic 1952 framework.
- **§4 — Maximize risk-adjusted return.** The **tangency portfolio** — the point on the frontier with the highest Sharpe — and the **Capital Market Line**. Pays Ch5's "Sharpe as the optimization objective" promise.
- **§6 — Allocate risk equally.** **Risk parity** — the practitioner's pivot when you don't trust your μ-estimates. Pays Ch3's "smart weighting matters" promise (and confirms it with a stark audit of how lopsided "equal-weight" actually is).

The hard lesson lives in **§5**: mean-variance optimization is *unstable*. Small changes in the inputs (especially μ̂) produce large changes in the weights. This is not a flaw in the optimizer — it's the optimizer's job to spot small differences in expected return per unit of risk and lever them. Inverse covariance Σ⁻¹ is what does the levering, and on noisy inputs it amplifies noise into wildly different "optimal" portfolios. Chapter 4 was inserted into the curriculum specifically so this chapter could pay it off honestly: shrinkage on μ̂ is *the* stabilizer for MVO. Risk parity is the more dramatic answer — *don't depend on μ̂ at all*.

The chapter uses the same 8-ticker basket as Chapters 3–5 — **SPY, TLT, GLD, XLK, XLF, XLE, XLV, XLU** — over 20 years, plus the rolling daily **risk-free rate** *r<sub>f</sub>* (the return on a near-zero-risk asset, our proxy for "what cash earns") from `^IRX` (the Yahoo ticker for the **13-week U.S. Treasury bill** yield — short-term U.S. government debt, the standard real-world stand-in for *r<sub>f</sub>*; ranged from near-0% in the post-2008 low-rate decade to ~5% by 2024 over our window) introduced in Ch5. No new packages.

---

## What we mean by "the best" portfolio

There isn't one universal answer. There are three respectable answers, each from a different philosophy about what to optimize and which inputs to trust.

| Construction philosophy | What it optimizes | Inputs needed | Ch1–5 lineage |
|---|---|---|---|
| **Minimize risk** — GMV, the efficient frontier | Variance (or variance subject to a return target) | Σ only for GMV; μ + Σ for the frontier | Ch3 (covariance, **w**ᵀ**Σ****w**) |
| **Maximize risk-adjusted return** — tangency / max-Sharpe | Sharpe ratio | μ, Σ, *r<sub>f</sub>* — all three | Ch5 (Sharpe as objective); Ch4 (μ̂ with shrinkage); Ch3 (Σ̂) |
| **Allocate risk equally** — risk parity | Risk-contribution dispersion (drives all RC equal) | Σ only — *no μ* | Ch3 §3.5; Ch5's Sharpe-CI lesson as motivation |

The three philosophies disagree about *how much to trust μ*. Mean-variance trusts it fully. Risk parity ignores it. The frontier and GMV are in between.

One way to read this chapter: **the more you trust your μ-estimates, the further along that spectrum (toward MVO/tangency) you can sit.** Chapter 5's wide Sharpe CIs are the standard reason most practitioners choose to sit further left.

---

## 1. Setup

The setup mirrors Chapter 5 — same 8-ticker basket, same 20-year window, same `^IRX`-derived *r<sub>f</sub>* — and adds three pieces of machinery this chapter optimizes over:

- **Annualized mean vector μ̂** — `log_returns.mean() * 252`. Both *raw* and *James-Stein-shrunk* (per Ch4). The shrinkage call lives inline; we do not import from Chapter 4.
- **Annualized covariance matrix Σ̂** — `log_returns.cov() * 252`. *K* × *K* symmetric positive-definite (you'll see SciPy invert it cleanly).
- **Average annualized risk-free rate** — the time-mean of `rf_daily * 252`. Optimization is single-period; we collapse the rolling *r<sub>f</sub>* to a scalar for the optimization, but evaluate realized Sharpes against the rolling series.

### A note on James-Stein at this sample size

Ch4 §3 fit James-Stein on the same basket and got a shrinkage factor of ≈ 0 — every sample mean got pulled all the way to the cross-sectional grand mean (8.5%). At the same N ≈ 5,000 daily observations *expressed as annualized inputs*, the Ch6 setup gets a JS factor of ≈ **0.99** — i.e., almost no shrinkage. Why the contrast? **JS's strength depends on the dispersion-vs-noise ratio.** Ch4 measured noise relative to dispersion in a way that emphasized noise; on 5,000 daily obs converted to annual, the SE-of-mean has shrunk faster than the cross-sectional dispersion, so the JS factor barely pulls. *This is itself a useful lesson:* shrinkage isn't a fixed multiplier — it's data-driven and sometimes the data tells you not to shrink.

The honest takeaway for this chapter: **at N ≈ 5,000 the raw and JS-shrunk means are nearly identical, and the practical instability of MVO has to be demonstrated some other way.** That other way is the bootstrap in §5.

---

## 2. Two-asset warmup — the picture before the math

Before any matrix algebra, the entire framework is visible in a two-asset plot.

Take SPY and TLT. Sweep *w* (the SPY weight) from 0 to 1; the TLT weight is just 1 − *w*. For each *w*:

> *μ*<sub>p</sub> = *w* *μ*<sub>SPY</sub> + (1−*w*) *μ*<sub>TLT</sub>
>
> *σ*<sub>p</sub>² = *w*² *σ*<sub>SPY</sub>² + (1−*w*)² *σ*<sub>TLT</sub>² + 2 *w* (1−*w*) *ρ* *σ*<sub>SPY</sub> *σ*<sub>TLT</sub>

where:
- *w* — fraction of capital in SPY. **Units:** dimensionless, in [0, 1] under long-only (i.e. no short-selling — see §3.2 foot-gun).
- *μ*<sub>SPY</sub>, *μ*<sub>TLT</sub> — annualized mean returns of SPY and TLT (the per-asset expected returns from Ch4).
- *σ*<sub>SPY</sub>, *σ*<sub>TLT</sub> — annualized standard deviations (volatilities) of SPY and TLT (per-asset risk from Ch2).
- *μ*<sub>p</sub>, *σ*<sub>p</sub> — portfolio mean return and standard deviation. **Units:** decimal per period; we annualize for plotting.
- *ρ* — SPY/TLT correlation. Ch3 reported ρ ≈ −0.31 over the 20y window.

> **Foot-gun: ρ < 1 is what makes the curve "bow."** If ρ = 1, the curve is a straight line and there's no diversification benefit at all. The further below 1, the more the curve bends to the left (lower σ for a given mix); negative ρ bends it most.

The notebook plots this curve in (*σ*, *μ*) space. The shape is the entire chapter in one picture:

- **At each end** sits a single asset (*w* = 0 is pure TLT, *w* = 1 is pure SPY).
- **In the middle**, with ρ ≈ −0.31, the curve **bows left** — there's a *w* where the portfolio's vol is *lower than either single asset's vol*. That point is the two-asset GMV.
- **Above the GMV** is the upper branch of the curve — the **efficient frontier** of this two-asset universe. Below the GMV is the lower branch — *dominated*: the same vol with less return.
- **"Best" depends on the loss function.** Lowest vol? GMV. Highest mean? Pure SPY. Highest Sharpe? Some specific point on the upper branch (we'll find it explicitly in §4).

That's it. The 8-asset case that follows just generalizes this picture, with **Σ** in place of two-by-two correlation and **w** as a vector instead of a scalar. The shape — frontier, GMV, dominated branch, multiple "best" answers — is the same.

---

## 3. The efficient frontier — full 8-asset case

### 3.1 Restating the math

From Ch3, with one line of refresh:

> *μ*<sub>p</sub> = **w**ᵀ**μ**
>
> *σ*<sub>p</sub>² = **w**ᵀ**Σ****w**

where:
- **w** — vector of portfolio weights, length *K* (here *K* = 8 assets). **w**ᵀ**1** = 1 always (full investment — i.e. fractions of capital sum to 100%); long-only adds *w*<sub>i</sub> ≥ 0.
- **μ** — *K*-vector of expected returns (annualized).
- **Σ** — *K* × *K* covariance matrix of returns (annualized; symmetric, positive-definite).
- *μ*<sub>p</sub>, *σ*<sub>p</sub>² — portfolio mean and variance.
- *μ*<sub>target</sub> (used below) — a chosen expected-return level the portfolio must hit; varying it traces out the frontier.

The mean-variance program is

```
minimize    wᵀ Σ w        (variance)
subject to  wᵀ μ = μ_target  (return target — only present for the frontier)
            wᵀ 1 = 1          (full investment)
            w ≥ 0             (long-only — optional)
```

### 3.2 The Global Minimum Variance portfolio

Drop the return-target constraint and just minimize variance subject to **w**ᵀ**1** = 1. The unconstrained problem has a closed-form **Lagrangian** solution (Lagrange multipliers are the standard tool for minimizing a function under equality constraints — the multiplier λ that appears in the derivation below encodes the marginal cost of the "weights sum to 1" constraint, and drops out at the end):

> **w**<sub>GMV</sub> = **Σ**⁻¹**1** / (**1**ᵀ**Σ**⁻¹**1**)

where:
- **Σ**⁻¹ — the matrix inverse of Σ. Exists because Σ is positive-definite for a non-degenerate basket.
- **1** — the all-ones vector of length *K*. (Reading: "Σ⁻¹ applied to **1**, normalized so the weights sum to 1.")
- **w**<sub>GMV</sub> — the unconstrained minimum-variance weights.

> **Foot-gun: the unconstrained GMV can short-sell.** Some assets may receive *negative* weights. **Short-selling** means borrowing an asset to sell it now and buying it back later — you profit if the price falls, and a negative weight is the math's way of saying "go short by this fraction of capital." A long-only portfolio forbids this (every *w*<sub>i</sub> ≥ 0). We compute both the unconstrained (analytic) version and the long-only (numerical) version below. Most practical desks default to long-only.

<details>
<summary>Derivation of the unconstrained GMV formula</summary>

Minimize *L*(**w**, *λ*) = ½ **w**ᵀ**Σ****w** − *λ* (**w**ᵀ**1** − 1). First-order conditions:

> ∂*L*/∂**w** = **Σ****w** − *λ***1** = 0    ⟹    **w** = *λ* **Σ**⁻¹**1**

Plug into **w**ᵀ**1** = 1: *λ* **1**ᵀ**Σ**⁻¹**1** = 1, so *λ* = 1 / (**1**ᵀ**Σ**⁻¹**1**), giving

> **w**<sub>GMV</sub> = **Σ**⁻¹**1** / (**1**ᵀ**Σ**⁻¹**1**).

</details>

On the 8-ticker basket the two versions produce:

| Version | SPY | TLT | GLD | XLK | XLF | XLE | XLV | XLU | Vol |
|---|---|---|---|---|---|---|---|---|---|
| **Unconstrained** | 0.24 | 0.45 | 0.16 | **−0.07** | −0.00 | −0.00 | 0.21 | 0.02 | 8.96% |
| **Long-only** (numerical) | 0.11 | 0.45 | 0.16 | 0.00 | 0.01 | 0.01 | 0.23 | 0.03 | 8.98% |

Two things to notice:

1. **The unconstrained version shorts XLK** — and only just, by 7%. The long-only version sets that short to zero and reallocates the freed capital into SPY and the bond/healthcare positions. The vol cost of the long-only constraint is essentially zero (8.96% → 8.98%).
2. **Both versions concentrate in low-vol, high-correlation-diversifier names.** TLT (~45%) is the bond hedge with negative ρ to equities; XLV (~22%) is the lowest-vol equity sector; GLD (~16%) is uncorrelated to equities. SPY drops to ~11% (long-only) because it's higher-vol than XLV and XLF/XLE are excluded for being high-vol with no compensating diversification benefit. **The optimizer knows nothing about "broad market" — it just minimizes variance.**

### 3.3 Tracing the frontier

The frontier itself is what you get when you keep the return-target constraint and sweep *μ*<sub>target</sub> from the lowest single-asset mean to the highest. For each target, solve numerically (we use **SLSQP** — Sequential Least-Squares Programming, a constrained nonlinear optimizer in `scipy.optimize` that handles equality + inequality constraints together; treat it as a black-box minimizer that respects our sum-to-1 and ≥ 0 rules):

```
minimize    wᵀ Σ w
subject to  wᵀ μ = μ_target
            wᵀ 1 = 1
            w ≥ 0
```

Plot the resulting (σ, μ) points — that's the frontier. Overlay the eight individual assets as scatter points and you get the diversification-dominance picture from Ch3 made formal:

- **Every individual asset sits inside (to the right of) the frontier.** You can always do better than holding any single asset alone, simply by diversifying.
- **The GMV is the leftmost point on the frontier.** Anything below it on the curve (same σ, lower μ) is *dominated* and conventionally not called "efficient."
- **The frontier curves up and to the right** — to chase higher expected return, you must accept higher vol. There is no free lunch *above* the frontier; everything inside is a free lunch *vs. the diagonal*.

Sample frontier points from the notebook (long-only, *raw* means — at this sample size JS-shrunk and raw are nearly identical, see §1):

| μ_target | Achievable σ | Notes |
|---|---|---|
| 3.3% | 14.9% | All-TLT (TLT is the lowest-mean single asset) |
| 4.7% | 9.8% | Heavy TLT + small risk add-ons |
| 6.2% | 9.0% | Near GMV |
| 7.7% | 9.2% | A little above GMV; modest equity weight |
| 9.2% | 10.5% | More equity (SPY/XLV/XLK) |
| 10.7% | 12.6% | Tilting toward XLK |
| 12.1% | 15.2% | Mostly XLK |
| 13.6% | 18.8% | Almost all XLK |

That last row — "to chase 13.6% expected return on this basket, you accept 18.8% vol and concentrate in one sector" — is the natural setup for the next section: where on this curve do you actually want to sit?

---

## 4. The tangency portfolio — the max-Sharpe construction

### 4.1 Adding the risk-free asset

A real-world investor has an option no point on the frontier captures: hold cash (or **T-bills** — short-term U.S. Treasury debt, the conventional "risk-free" asset because they are backed by the U.S. government and mature in days/weeks/months, leaving little time for anything to go wrong) at the risk-free rate *r<sub>f</sub>*. With *r<sub>f</sub>* available, an investor can hold any *combination* of *r<sub>f</sub>* and a risky portfolio **w**, and the combined position sits on a **straight line** in (σ, μ) space passing through (0, *r<sub>f</sub>*) and (σ<sub>w</sub>, μ<sub>w</sub>).

The slope of that line is

> (*μ*<sub>w</sub> − *r<sub>f</sub>*) / *σ*<sub>w</sub>

— the **Sharpe ratio of w** (Ch5: excess return per unit of vol; bigger = more reward per unit of risk).

The investor who wants the highest Sharpe picks the **w** whose line has the steepest slope. Geometrically, that line is the one **tangent to the efficient frontier from (0, *r<sub>f</sub>*)**. The tangent point is the **tangency portfolio**, also called the **maximum-Sharpe portfolio**.

The tangent line itself, extended out beyond the tangency point (mixing in leverage rather than cash), is called the **Capital Market Line (CML)**. Every Sharpe-maximizing investor's portfolio sits on this line — risk-averse investors blend in more *r<sub>f</sub>* and sit lower-left on it; risk-tolerant investors lever up the tangency portfolio and sit upper-right. **They all hold the same risky composition.** This statement is the **two-fund separation theorem** — named only here, because the algebra of the CML is what carries the intuition.

### 4.2 Analytic form (unconstrained)

> **w**<sub>tan</sub> ∝ **Σ**⁻¹ (**μ** − *r<sub>f</sub>* **1**),   normalized so **w**<sub>tan</sub>ᵀ **1** = 1.

where:
- **w**<sub>tan</sub> — the tangency (max-Sharpe) portfolio weights, length *K*.
- (**μ** − *r<sub>f</sub>***1**) — the vector of expected **excess returns** — each asset's expected return *minus* the risk-free rate. This is the "extra you earn for taking risk in asset *i*"; Ch5 used the same scalar quantity in the Sharpe numerator.
- **1** — the all-ones vector of length *K*; *r<sub>f</sub>***1** is just *r<sub>f</sub>* repeated *K* times so it can be subtracted from the asset-mean vector.
- **Σ**⁻¹ — the inverse covariance matrix.
- The result is divided by **1**ᵀ **Σ**⁻¹ (**μ** − *r<sub>f</sub>***1**) to make the weights sum to 1.

<details>
<summary>Derivation of the unconstrained tangency formula</summary>

Maximize Sharpe = (**w**ᵀ**μ** − *r<sub>f</sub>*) / √(**w**ᵀ**Σ****w**) subject to **w**ᵀ**1** = 1. Sharpe is scale-invariant in **w** in the unconstrained case (multiplying **w** by a positive constant leaves Sharpe unchanged), so we can drop the normalization while maximizing and re-impose it at the end.

First-order condition: ∂(Sharpe)/∂**w** = 0 gives **Σ****w** ∝ (**μ** − *r<sub>f</sub>***1**), i.e. **w** ∝ **Σ**⁻¹ (**μ** − *r<sub>f</sub>***1**). Then normalize so the weights sum to 1.

</details>

> **Foot-gun: Σ⁻¹ amplifies small differences in (μ − r_f).** The unconstrained tangency formula is *the* mathematical reason MVO is unstable — Σ⁻¹ has large entries off-diagonal whenever the basket has highly correlated assets, and those large entries multiply small μ-differences into large weight differences. **§5 demonstrates this empirically. Hold this sentence in mind.**

### 4.3 Long-only tangency on the 8-ticker basket

Numerically maximize Sharpe with sum-to-1 + non-negativity constraints (`scipy.optimize.minimize` with the negative-Sharpe objective):

| Asset | SPY | TLT | GLD | XLK | XLF | XLE | XLV | XLU |
|---|---|---|---|---|---|---|---|---|
| Long-only tangency weight | 0.00 | 0.23 | 0.29 | 0.34 | 0.00 | 0.00 | 0.15 | 0.00 |

Vol ≈ **11.2%**, **in-sample** annualized Sharpe ≈ **0.73**. ("In-sample" means the Sharpe is computed on the *same* 20-year data the optimizer used to pick the weights — there's no separate hold-out period yet, so this number is a best case. Exercise 4 introduces the out-of-sample version, and Ch13 will treat that distinction systematically.)

Reactions worth flagging:

- **SPY is dropped entirely.** The optimizer doesn't care that SPY is "the broad market" and XLK is one sector. It cares that XLK has higher μ at not-much-higher σ over this window. SPY's μ ≈ 10.3% is dominated, in optimization terms, by XLK's 14.8%.
- **Half the basket gets zero weight.** XLF, XLE, and XLU are squeezed out — their Sharpe-per-dollar is too low relative to the alternatives.
- **The 0.73 in-sample Sharpe is roughly +0.21 above 60/40's 0.52.** ("60/40" is the canonical retail balanced portfolio — 60% equities, 40% bonds; here we use 60% SPY + 40% TLT, daily-rebalanced. It's the standard real-world baseline a Sharpe-maximizing strategy has to beat.) *Hold this number lightly* — §4.5 puts a CI on it, and §5 shows the *weights* themselves are wildly sample-dependent.

### 4.4 The Capital Market Line, drawn

The notebook plots the efficient frontier from §3, then adds:

- The eight individual assets as scatter points.
- The **tangency portfolio** as a marker on the frontier.
- The **CML** — a straight line through (0, *r<sub>f</sub>*) and the tangency marker, extending beyond it.
- The **60/40, EW8, and GMV-LO** portfolios for comparison. (EW8 = "equal-weight 8" — 1/8 of capital in each of the eight tickers, the naive diversification baseline from Ch3. GMV-LO = the long-only Global Minimum Variance portfolio from §3.2.)

Visually, the CML is everywhere above the frontier except at the tangency point itself, where it kisses the curve. That picture is what "best Sharpe" *means* — the steepest line you can draw from (0, *r<sub>f</sub>*) to anywhere achievable.

### 4.5 Tangency Sharpe with Ch5's CI

Apply the §4.3-of-Ch5 method: SE(Sharpe) ≈ SE(μ̂_excess) / σ; annualize × √252; build a 95% CI as point ± 1.96 · SE.

| Portfolio | Sharpe (in-sample) | 95% CI |
|---|---|---|
| Tangency (long-only) | 0.73 | [0.29, 1.16] |
| 60/40 SPY/TLT | 0.52 | [0.09, 0.96] |
| Equal-weight-8 | 0.47 | [0.04, 0.92] |
| GMV (long-only) | 0.55 | [0.12, 0.99] |

The tangency CI's lower bound (0.29) is *above* 60/40's lower bound (0.09), but **comfortably overlaps 60/40's upper bound (0.96)**. Translation: at 20-year sample sizes, *we cannot reject "tangency and 60/40 have the same true Sharpe"* at the 5% level. The headline 0.21 Sharpe gain may not be statistically real.

The reader has now seen this lesson three times — Ch4 (means are noisy), Ch5 (Sharpe inherits that noise), Ch6 (so do *weights chosen to maximize Sharpe*). It's the single most important practical caveat in this chapter.

---

## 5. The instability problem — why MVO is hard

### 5.1 Why the tangency formula is brittle

The unconstrained tangency formula was **w**<sub>tan</sub> ∝ **Σ**⁻¹ (**μ** − *r<sub>f</sub>* **1**). Two facts about this expression:

1. **Σ⁻¹ has large off-diagonal entries when the basket has highly correlated assets.** Heuristically: if two columns of Σ are nearly identical (correlation near 1), Σ is nearly singular and Σ⁻¹ has very large entries that *cancel* — the inverse is dominated by tiny differences in nearly-collinear directions. *Concretely:* a 2×2 covariance with σ = 1 each and ρ = 0.95 has determinant 1 − 0.95² = 0.0975, so Σ⁻¹ has off-diagonals near −0.95/0.0975 ≈ **−9.7** and diagonals near +10.3. Bump ρ to 0.99 and those entries balloon to ≈ ∓50. Tiny changes in (μ − *r<sub>f</sub>*) get multiplied by these huge cancelling numbers — that's the amplification.
2. **(μ − r_f**·**1) is noisy.** Ch4 §2 measured this: the SE of an annualized mean is roughly σ/√N, and for daily SPY data it's ~4–5 percentage points wide.

Multiply a noisy vector by a matrix with large cancelling off-diagonal entries and you get a *very* noisy result. **Small input noise → large output swings in weights.** This is structural to the formula, not a bug in the optimizer.

### 5.2 Bootstrap demonstration

The notebook resamples the 20-year daily-returns panel with replacement (using a 21-day **block bootstrap** to preserve some volatility clustering — naive iid bootstrap would smear it out), 200 times. On each resample we recompute μ̂, Σ̂, then re-fit the long-only tangency. Plot the distribution of weights across the 200 resamples.

What we expect (and what we observe):

| Asset | Mean weight | Stdev | Range observed |
|---|---|---|---|
| SPY | 0.01 | 0.05 | [0.00, 0.48] |
| TLT | 0.21 | 0.12 | [0.00, 0.54] |
| GLD | 0.27 | 0.16 | [0.00, 0.74] |
| **XLK** | 0.29 | **0.18** | **[0.00, 1.00]** |
| XLF | ~0.00 | ~0.00 | rarely > 5% |
| XLE | 0.01 | 0.03 | [0.00, 0.21] |
| XLV | 0.13 | 0.17 | [0.00, 0.94] |
| XLU | 0.08 | 0.11 | [0.00, 0.50] |

**XLK alone moves between 0% and 100% across resamples of essentially the same data** — there are individual bootstrap draws on which the "optimal" portfolio is *entirely* XLK and nothing else. "How much tech?" is not a question this method can answer with confidence — the answer is sample-dependent in the extreme. This is Ch4's noise-of-the-mean lesson, transmitted through Σ⁻¹ into a noise-of-the-weights lesson, on the same 20-year window the rest of the curriculum has worked on.

### 5.3 Three remediations, one paragraph each

**1. Shrinkage on μ̂ (Ch4).** The standard answer to noisy μ̂. Pulls extreme estimates toward the cross-sectional grand mean, reducing the differences that Σ⁻¹ amplifies. *In this chapter's data*, JS shrinkage at N ≈ 5,000 daily obs barely moved the means (factor ≈ 0.99) — the demonstrated instability comes from the *bootstrap* draws, where each resample is its own small-sample story. **Shrinkage helps most when N is small, the cross-section is broad, and the dispersion-vs-noise ratio favors pulling.** Because the in-sample contrast is so mild on this basket, **the body of the chapter does not show a raw-vs-shrunk frontier overlay — Exercise 2 is the demonstration.** Re-tracing §3.3 with JS-shrunk means is the cleanest way to see (and feel) how mild "mild" really is here, and to compare against the regime where shrinkage *would* matter (smaller N, broader cross-section).

**2. Shrinkage on Σ̂ (Ledoit-Wolf and family — named only).** Σ̂ also has noise, especially in the off-diagonals — and that noise is what gives Σ⁻¹ its large cancelling entries. The Ledoit-Wolf estimator shrinks Σ̂ toward a structured target (typically the diagonal of Σ̂, treating assets as uncorrelated) by a data-driven amount. *Why does shrinking toward "uncorrelated" help?* Because off-diagonal noise is what makes Σ near-singular and Σ⁻¹ explosive — pulling the off-diagonals partway toward zero pushes Σ away from singularity, and the resulting Σ⁻¹ has smaller, more stable entries. Full treatment deferred; this is the natural complement to Ch4's μ-shrinkage on the Σ side.

**3. Constrain the optimizer.** Long-only and per-asset weight caps both blunt the levering effect of Σ⁻¹. The long-only constraint above already made the analytic XLK short go away at no vol cost — that's a representative outcome. Many institutional portfolios go further: max 10% per asset, max sector exposure, etc. **Constraints are not just business-policy; they are statistical regularizers.**

### 5.4 What this means with $100k

A practitioner who recomputed weights from scratch every quarter using the most recent five years of data would have whipsawed in and out of XLK, GLD, and XLV in ways that have *nothing to do with how those assets actually performed* — the data was noisy enough to redraw the "optimal" weights from quarter to quarter. The trades themselves would have transaction costs (Ch14) eating the supposed Sharpe gain. **Raw MVO weights are not pickup-and-trade ready. Stabilize them first.**

---

## 6. Risk parity — the practitioner's pivot

### 6.1 Motivation: stop trusting μ̂

§5 said: μ̂-dependence is dangerous. So: build a portfolio that *doesn't depend on μ̂ at all*.

One such portfolio is equal-weight (1/N). But Ch3 §3 already showed equal-weight over-allocates risk to high-vol names, and §6.3 below makes that lopsidedness explicit. **Risk parity** is the principled refinement: allocate weights so that *each asset contributes the same amount of risk to the portfolio*.

### 6.2 Risk contribution

Decompose portfolio vol cleanly into per-asset slices:

> *MRC*<sub>i</sub> = (**Σ****w**)<sub>i</sub> / *σ*<sub>p</sub>     (marginal risk contribution)
>
> *RC*<sub>i</sub> = *w*<sub>i</sub> · *MRC*<sub>i</sub> = *w*<sub>i</sub> (**Σ****w**)<sub>i</sub> / *σ*<sub>p</sub>     (risk contribution)

where:
- (**Σ****w**)<sub>i</sub> — the *i*th component of the matrix-vector product **Σ****w**. Has units of variance.
- *σ*<sub>p</sub> = √(**w**ᵀ**Σ****w**) — total portfolio volatility.
- *MRC*<sub>i</sub> — the partial derivative ∂*σ*<sub>p</sub>/∂*w*<sub>i</sub>: how much portfolio vol changes if you marginally increase asset *i*'s weight.
- *RC*<sub>i</sub> — asset *i*'s share of total vol. **Units:** decimal vol (same as *σ*<sub>p</sub>).

Useful identity: **Σ**<sub>i</sub> *RC*<sub>i</sub> = *σ*<sub>p</sub>. The slices add up to the whole.

> **Foot-gun: RC can be negative.** An asset that's negatively correlated with the portfolio (TLT in an equity-heavy basket) can have a negative RC — it *removes* risk. That's not a bug; it's the diversification math.

The **Equal Risk Contribution (ERC)** portfolio asks: make every *RC*<sub>i</sub> equal, so each asset carries *σ*<sub>p</sub> / *K*.

### 6.3 EW8 risk contributions — the audit that motivates risk parity

With weights = (1/8, 1/8, ..., 1/8), what fraction of EW8's total vol does each asset contribute?

| Asset | EW8 weight | RC fraction (% of σ<sub>p</sub>) |
|---|---|---|
| SPY | 12.5% | 16% |
| TLT | 12.5% | **−2%** (negative — TLT removes risk) |
| GLD | 12.5% | 4% |
| XLK | 12.5% | 17% |
| **XLF** | 12.5% | **21%** |
| **XLE** | 12.5% | **21%** |
| XLV | 12.5% | 12% |
| XLU | 12.5% | 12% |

XLF and XLE — two of the highest-vol sector ETFs in the basket — together carry **42% of EW8's total risk** despite being only 25% of the *weight*. TLT actually *removes* risk because of its negative correlation with equities.

**An equal-weight basket is not an equal-risk basket. It's a pile of risk dominated by the highest-vol names.** This is the same lesson Ch3 delivered through "EW8 has higher vol than 60/40," restated from the inside: it's not that EW8 is poorly built — it's that *equal capital weight ≠ equal risk weight* whenever the underlying assets have unequal vols.

### 6.4 Solving for ERC

There's no closed-form. Minimize the squared dispersion of risk contributions around their target:

> minimize<sub>**w**</sub>  Σ<sub>i</sub> (*RC*<sub>i</sub> − *σ*<sub>p</sub>/*K*)²    subject to    **w**ᵀ**1** = 1, *w*<sub>i</sub> > 0

`scipy.optimize.minimize` with SLSQP and a tiny lower bound on each weight (1e-6, to keep RC well-defined) does it. Result on the 8-ticker basket:

| Asset | SPY | TLT | GLD | XLK | XLF | XLE | XLV | XLU |
|---|---|---|---|---|---|---|---|---|
| RP weight | 0.09 | **0.34** | 0.16 | 0.08 | 0.06 | 0.07 | 0.11 | 0.10 |

By construction, every risk contribution is now ≈ *σ*<sub>p</sub>/8 ≈ **1.26%** of vol. Total vol ≈ **10.1%**, in-sample Sharpe ≈ **0.56** — a touch above 60/40's 0.52, well above EW8's 0.47, **and computed without using μ̂ anywhere**.

The *shape* of the RP solution:

- **TLT is heavily over-weighted (34%)** relative to its capital share in EW8. Because TLT has low vol *and* negative correlation with equities, you can hold a lot of it before it contributes its 1/8 share of risk.
- **XLF and XLE are under-weighted (6–7%)** to bring their RCs down to the equal share. High-vol names get less capital under risk parity.
- **The remaining six assets land in a 7–16% range** — much tighter than EW8's wildly unequal RCs.

> **Sanity check.** The famous "60/40" portfolio is a coarse heuristic doing the same thing: over-weight the low-vol asset (40% bonds) relative to a naive 50/50 to balance risk between the two sleeves. **Risk parity is what 60/40 was reaching for, generalized to *K* assets.**

### 6.5 What this means with $100k

A $100k risk-parity portfolio on this basket over 20 years matched 60/40's Sharpe at lower vol, *and* spread eight different exposures rather than two — a more diversified portfolio at comparable risk-adjusted return. Critically, the construction never used μ̂ — so the wide CIs from Ch5 §4 don't propagate into the weights. **That's the engineering trade-off:** give up the (possibly real, possibly noise) Sharpe gain of optimization in exchange for a portfolio whose composition is stable and depends only on Σ̂ — which is itself noisier than we'd like, but much less noisy than μ̂.

### 6.6 Risk parity's limits, briefly

Three caveats, no code:

1. **Still depends on Σ̂.** Σ̂ noise is smaller than μ̂ noise, but not zero. Ledoit-Wolf shrinkage on Σ̂ (named in §5.3) is the natural pairing.
2. **No accommodation of views.** If you have a credible view ("XLK will outperform"), risk parity has no place to put it. Black-Litterman is the standard answer; full treatment deferred.
3. **Risk-only ≠ best.** Risk parity is *one* heuristic for "don't trust μ̂" — not the answer. The right portfolio depends on the loss function (drawdown? Sharpe? terminal wealth?), the data quality, and the rebalance discipline. A simpler **vol parity** variant weights by 1/σ<sub>i</sub> ignoring correlations entirely; it's faster and almost as good when correlations are low. Hierarchical and factor-based variants exist; out of scope here.

---

## 7. What we just learned — three philosophies, one caveat

Recap by philosophy (the same taxonomy from §0):

- **Minimize risk — GMV.** The leftmost point on the frontier; depends only on Σ̂. Concentrates in low-vol, well-diversifying assets (TLT 45%, XLV 22%, GLD 16% on this basket). Long-only and unconstrained versions are nearly identical on diversified baskets.
- **Maximize Sharpe — tangency.** Depends on μ̂, Σ̂, *r<sub>f</sub>*. In-sample 0.73 Sharpe on the 8-ticker basket — **but** the Ch5-style CI is wide enough that the +0.21 gain over 60/40 isn't statistically real, and §5's bootstrap shows the *weights themselves* are wildly unstable. Tangency is the right answer if you trust your inputs; you usually shouldn't.
- **Allocate risk equally — risk parity.** Depends only on Σ̂. The EW8 risk-share decomposition makes the problem visible (XLF + XLE = 42% of risk on 25% of weight); RP fixes it. In-sample Sharpe 0.56 with no μ̂ input, lower vol than 60/40.

The hidden lesson — **estimation error.** MVO's instability isn't a flaw in the optimizer; it's a flaw made *visible* by the optimizer. Three responses, used in combination on real desks: shrink μ̂ (Ch4), shrink Σ̂ (Ledoit-Wolf, deferred), and constrain the search (long-only, position caps). Risk parity is the more aggressive answer: stop using μ̂ at all.

A connecting line forward: **Chapter 7 (linear regression) and Chapter 8 (factor models)** offer a different stabilizer for μ̂ — model returns as a few common factors plus residuals. That itself is a structural form of shrinkage: instead of estimating *K* independent means, you estimate a few factor loadings and inherit the structure those imply. The chapters that follow are how the curriculum gets out from under the μ̂-noise problem this chapter exposed.

---

## 8. So what?

**Decision rules this chapter unlocks:**

- *Default to long-only.* Unconstrained MVO can short-sell to lever small μ̂-differences; long-only caps the damage at near-zero vol cost on diversified baskets.
- *Treat MVO weights as suggestions, not orders.* If a 200-resample bootstrap moves XLK's tangency weight between 0% and 100% on the same data, your single point estimate is one draw from that distribution. The 60/40 portfolio you held all along may not be statistically distinguishable from "optimal."
- *Audit risk contributions, always.* Even an "intuitive" allocation (60/40, EW8, the lazy three-fund) hides skew in where the risk lives. The audit is one matrix-vector product; do it.
- *Default to risk parity when you don't trust μ̂.* You usually don't — especially on small samples, new strategies, or recent data. RP gives you a stable, diversified portfolio whose only input is Σ̂.
- *Shrink μ̂ if you must use MVO.* Ch4's shrinkage helps most when N is small and dispersion is large — the regime in which raw MVO breaks worst. *In-sample* on this 20-year basket the shrinkage is mild; that does not generalize to shorter samples or smaller cross-sections.
- *Long-run μ̂ matters less than you think for portfolio construction.* The biggest lesson of §5 is that μ̂ is hard to estimate well enough to drive weight decisions confidently. Most of the diversification benefit is available without it (GMV, risk parity).

**What this chapter can't yet tell you:**

- *How to model μ structurally* (factors, betas, alpha, equilibrium returns). → Ch7 (regression), Ch8 (CAPM, Fama-French).
- *Whether the in-sample Sharpe gain of tangency over 60/40 survives out-of-sample.* The single most important question this chapter doesn't answer. → Ch13 (backtesting). Exercise 4 is the warm-up.
- *How to formally combine an equilibrium prior on μ with an investor's views.* → Black-Litterman, deferred.
- *How to size positions for non-Gaussian, time-varying risk.* → Ch9 (GARCH), Ch12 (Kelly).
- *Whether any of these "optimal" portfolios survive transaction costs and slippage.* → Ch13–14.

---

## 9. Up next

**Chapter 7 — Linear Regression Primer.** The single piece of inferential statistics the rest of the curriculum leans on. Chapter 8's CAPM is one regression; Fama-French is a multi-regressor extension; Chapter 12's strategy-feature work leans on it again. Chapter 7 also provides the foundation for **factor models** (Ch8), which restructure μ as a few common drivers + idiosyncratic residuals — a structural form of shrinkage that complements the cross-sectional shrinkage from Ch4.

## Key Terms

| Term | Brief meaning |
|---|---|
| Mean-variance optimization (MVO) | Markowitz's framework: pick weights to optimize a tradeoff between portfolio mean and variance. |
| Efficient frontier | The set of portfolios offering the lowest variance for each achievable return target — the upper branch of the (σ, μ) curve. |
| Global minimum variance (GMV) portfolio | The leftmost point on the frontier — the lowest-variance portfolio achievable with the given Σ. |
| Long-only constraint | Restriction *w*<sub>i</sub> ≥ 0 — no short selling. Acts as a statistical regularizer. |
| Tangency portfolio | The point on the efficient frontier with the maximum Sharpe — equivalently, the portfolio whose ray from (0, *r<sub>f</sub>*) is tangent to the frontier. |
| Capital Market Line (CML) | The line through (0, *r<sub>f</sub>*) and the tangency portfolio — every Sharpe-optimal mix of *r<sub>f</sub>* and risky portfolio sits on this line. |
| Two-fund separation theorem | (named only) Every Sharpe-maximizing investor holds some mix of *r<sub>f</sub>* and the tangency portfolio. |
| Marginal risk contribution (MRC) | (**Σ****w**)<sub>i</sub> / *σ*<sub>p</sub> — partial derivative of portfolio vol with respect to asset *i*'s weight. |
| Risk contribution (RC) | *w*<sub>i</sub> · *MRC*<sub>i</sub> — asset *i*'s share of total portfolio vol. RCs sum to *σ*<sub>p</sub>. |
| Risk parity / Equal Risk Contribution (ERC) | Portfolio chosen so every asset's RC is equal — depends on Σ only, not μ. |
| Volatility parity | (named only) Simpler than ERC: weight by 1/σ<sub>i</sub>, ignoring correlations. |
| Estimation error / instability | The effect of input noise (μ̂, Σ̂) on optimization output (weights). MVO amplifies it through Σ⁻¹. |
| Block bootstrap | Resampling scheme that draws *blocks* of consecutive observations rather than single points, preserving short-horizon dependence (vol clustering). |
| Black-Litterman | (named only) Bayesian framework combining an equilibrium prior on μ with an investor's views. |
| Ledoit-Wolf shrinkage | (named only) Shrinkage estimator for Σ — analog of Ch4's JS shrinkage on μ. |

## Exercises

1. **Two-asset frontier with a different correlation.** Repeat §2 with **SPY and GLD** instead of SPY and TLT. SPY/GLD's correlation is closer to zero than SPY/TLT's negative. How much less does the curve "bow" in (σ, μ) space? Compute the two-asset GMV vol for SPY/GLD and compare to SPY/TLT. What does the comparison say about *negative* correlation as a diversification tool versus merely *low* correlation?

2. **Frontier with raw vs JS-shrunk means.** Re-trace the §3.3 frontier using **JS-shrunk means** in place of raw means. Plot both frontiers on the same axes. Does the tangency portfolio's composition (§4.3) change? Hint: at this sample size the shrinkage is mild, so the difference will be subtle — the *exercise* is to confirm that with your own eyes and reflect on when shrinkage would matter more (smaller N, broader cross-section, or both).

3. **Risk parity without TLT.** Drop TLT from the basket and recompute risk parity on the remaining seven assets. How do the weights and the total vol change? Which asset takes the largest share of TLT's old role? What does this exercise tell you about the role of *negative-correlation* assets in risk-parity portfolios specifically (versus low-correlation ones)?

4. *(stretch)* **Out-of-sample test of tangency.** Split the 20y window in half. Fit the long-only tangency portfolio on the **first 10y only**; **freeze those weights**, then compute the realized Sharpe on the **second 10y**. Compare to (a) the 60/40 portfolio and (b) the risk-parity portfolio on the same hold-out window. Was the in-sample 0.73 Sharpe gain real out-of-sample, or did it shrink? *This is the single most important sanity check for any optimization-based approach, and the warm-up for Chapter 13.*
