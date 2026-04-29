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

A 95% confidence interval, assuming approximate normality of the sample mean:

> *CI₉₅* = *μ̂* ± 1.96 · *SE(μ̂)*

where 1.96 is the 0.975 quantile of the standard normal distribution.

> **Why does the sample mean's distribution become approximately normal?** The **Central Limit Theorem (CLT)** is a foundational statistics result: when you average enough independent samples from any reasonably-behaved distribution, the *average's* distribution becomes approximately normal regardless of the original distribution's shape. With ~5,000 daily returns, the CLT applies cleanly even though individual returns are fat-tailed (Ch2 §2). The CLT is why a `μ̂ ± 1.96·SE` interval is a defensible CI even though the inputs aren't themselves normal.

For SPY's full 20-year window, the notebook computes:

| Quantity | Value |
| --- | ---: |
| N | 5,031 |
| Annualized mean | 10.37% |
| Annualized SE | 4.35% |
| 95% CI on annualized mean | **[1.84%, 18.90%]** |
| CI width | 17.06 percentage points |

> **What does this CI actually claim?** Subtle but important — most casual explanations get this wrong:
> 1. **It's NOT** "there's a 95% probability the true value is in [1.84%, 18.90%]." Once the data is in and the interval is computed, the true value either is or isn't in there — no probability about it.
> 2. **The "95%" describes the *procedure*, not this specific interval.** If we ran the same calculation on a thousand different 20-year samples, 95% of the resulting intervals would contain the true value. Our particular interval is one of those thousand; we don't know whether it's one of the 950 that contains the truth or one of the 50 that doesn't.
> 3. **In conversation, "we're 95% confident the true mean is in this range" is fine.** It communicates the right intuition for any decision-making purpose, even though it's technically the wrong semantics.
> 4. **A wide CI doesn't mean we were "careless."** It means our best honest procedure can't pin down the true value tighter than this with the data we have. The path forward isn't "be more careful with the data" — it's more data, a different estimator (§3 shrinkage), or outside information.
>
> Useful mental picture: imagine the true expected return is a stake driven into the ground at an unknown spot. Your sample mean tosses a horseshoe; the CI is the ring it forms. You can't see the stake. Your *tossing technique* rings the stake 95% of the time across many tosses. The horseshoe you just threw either rings it or it doesn't — but you trust the technique.

That CI is the chapter's punchline. Twenty years of data, and we still can't pin down SPY's true expected return any tighter than a **17-percentage-point** range. To make that range concrete, translate each end into something a non-finance reader can evaluate.

#### Lower bound (~1.84%): "you didn't earn an equity premium"

> **T-bills** — short-term US Treasury debt with maturities from a few weeks to a year. Conventionally treated as the closest thing to a "risk-free" rate, since the US government has never defaulted on dollar-denominated debt. T-bills are the standard "what would I have earned with no risk?" benchmark.

Over the 20-year window we're using (2006–2026), T-bill yields averaged **roughly 2% annualized** — they were near 0% from 2009–2015 and again from 2020–2021, then climbed to 4–5%+ in 2022–2024 as the Fed hiked aggressively. So at the lower CI bound, SPY's true expected return is essentially *tied with* T-bills — meaning you'd have earned the same money holding cash with no equity risk.

The whole point of taking equity risk is supposed to be the premium *above* the risk-free rate (called the **equity risk premium**). The lower CI bound is consistent with a world where that premium was *zero*. The data can't statistically rule that out.

#### Upper bound (~18.90%): "stocks are an obvious slam dunk"

> **Rule of 72** — a mental shortcut for compound growth: doubling time in years ≈ 72 / annualized return %. (It's a first-order approximation that works well for returns in the 4–25% range.)

Apply it: 72 / 18.90 ≈ **3.8 years**. At an 18.90% annualized return, $100k becomes ~$200k in just under four years. That's a rate competitive with late-1990s tech-boom returns; "every dollar I don't have in stocks is wasted" territory.

#### The point of bracketing the bounds this way

Two scenarios — "stocks aren't worth the risk" and "stocks are an obvious slam dunk" — are basically opposite views of equity investing. **Twenty years of data is consistent with either.** That's the gut punch: both intuitions could be right, and the historical mean alone can't tell you which. §3's shrinkage is one practitioner-grade response to this problem.

### 2.3 Subsample stability — same data, different windows

A different angle on the same problem. Pick disjoint 5-year sub-windows of the SPY data and compute the sample mean on each. The notebook produces:

| Window | Annualized mean | Annualized vol |
| --- | ---: | ---: |
| 2006–2010 | **1.34%** | 25.54% |
| 2011–2015 | 11.73% | 15.38% |
| 2016–2020 | **14.07%** | 18.97% |
| 2021–2025 | 13.45% | 17.09% |

The annualized mean varies by **~13 percentage points** across these disjoint 5-year windows of the same asset. The 2006–2010 window includes the 2008 crisis and looks terrible; the 2016–2020 window sat in a strong bull market and looks great. **None of those sub-window means is "wrong"** — they're all valid sample means of real data — but the spread is exactly the noise the standard error formula was telling us about, made visceral.

### 2.4 What this means with $100k

A reader sizing a position based on "SPY returns 10% per year" needs to know that, statistically:

| Quantity | Value |
| --- | --- |
| Point estimate (20-year sample) | ~10% / year |
| Standard error (annualized) | ~4–5% |
| 95% CI on annualized mean | roughly **1.84% to 18.90%** |
| Dollar terms on $100k | roughly **$1,840/year to $18,900/year** |

Two ways to read those bounds honestly (using the T-bills and Rule-of-72 framings established in §2.2):

- **Lower end ($1,840/year, ~1.84%).** Essentially tied with T-bills, which averaged ~2% over the same window. The CI is consistent with SPY having earned **no equity premium at all** — i.e., the same return you'd have gotten holding cash with no risk. Strict reading: the lower bound is actually *slightly below* the ~2% T-bill average, so the CI is even consistent with SPY underperforming cash in expectation.
- **Upper end ($18,900/year, ~18.90%).** "Doubling every ~3.8 years" territory by the Rule of 72. The CI is consistent with SPY being a generational investment opportunity.

**Both extremes are statistically consistent with the same 20 years of data.**

Two practical takeaways:
1. **A point estimate is the *center* of a wide distribution, not a fact.** Treating "10% per year" as if it were a known constant is bad statistics with real downstream consequences.
2. **Chapter 5's Sharpe ratio inherits this uncertainty.** A reported Sharpe of 0.5 with 20 years of data has its own large CI; "is this strategy any good?" can't be answered just from the point estimate.

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

The notebook applies the JS estimator to our 8-ticker basket. The prior is the cross-sectional mean (8.50% annualized).

The result is striking: **every asset gets shrunk *all the way* to the prior**. The shrinkage factor clamps to zero through the positive-part correction. The formula is telling us — explicitly and uncompromisingly — that **the dispersion across our 8 sample means is statistically indistinguishable from pure noise** given how wide each individual SE is.

Recall §2.2: SPY's annualized mean alone has a 95% CI of ~17 percentage points. The spread between XLK at 14.7% and TLT at 3.3% (~11 percentage points) doesn't survive contact with that noise floor. Our intuition says these are very different assets; JS is saying *20 years of data isn't enough to confirm that intuition statistically*.

Two important follow-ups before §3.4:

1. **Partial shrinkage happens when assets are more separable.** If the raw means were spread far enough apart relative to each estimator's noise (or if we had much more data), the factor wouldn't clamp to zero and we'd see partial movement instead of total. Exercise 3 demonstrates partial shrinkage by changing the prior to zero (which makes *D* much larger relative to *v*).
2. **Total shrinkage is still useful in practice.** Even when JS collapses everything to the prior, that's a legitimate input to portfolio optimization — and in fact, "use the cross-sectional mean for everyone" produces *much* more stable optimal portfolios than naive sample means do. Chapter 6 will demonstrate this directly.

The lesson isn't "JS is broken on financial data." The lesson is: **the historical sample-mean spreads we casually treat as informative often aren't, once we honestly account for noise.**

### 3.4 What this means for portfolio construction

**Practitioner-grade fact:** essentially all production mean-variance optimization uses *shrunk* expected-return estimates, not raw sample means. The reason: optimizers maximize Sharpe-like objectives that are *very* sensitive to the input expected returns, and naive sample means produce wildly unstable optimal weights — small changes in the data move the "optimal" portfolio dramatically.

Our §3.3 result reinforces this strongly. A portfolio optimizer fed naive sample means would treat XLK (14.7%) as a far better bet than TLT (3.3%) — and would over-allocate to XLK accordingly. JS-shrunk inputs say "you don't actually have evidence to support that allocation"; the resulting portfolio is more equal-weighted and far more stable.

Chapter 6 will demonstrate this directly using both raw and shrunk inputs to compute efficient frontiers.

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
- Subsample stability is poor — disjoint 5-year SPY windows produced annualized means ranging from ~1% (the 2006–2010 crisis-heavy window) to ~14% (calmer windows).
- **Shrinkage** toward a prior is the practitioner-grade remedy. The James-Stein estimator strictly dominates the raw sample mean (in total MSE) for *K* ≥ 3 assets shrunk together.
- On *our* 8-asset 20-year basket, JS shrunk *all* the means to the cross-sectional prior — telling us the dispersion of raw means is statistically indistinguishable from pure noise. That's the §2 noise lesson stated in the most uncompromising form.

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
| Bias | Expected difference between an estimator and the true value | §3 |
| Bias-variance tradeoff | Accepting a small bias to reduce overall mean-squared error | §3 |
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
3. **Shrinkage sensitivity.** Re-run the §3.3 demo with the prior set to **zero** instead of the cross-sectional mean. Does the shrinkage factor still clamp to zero, or do you get partial shrinkage now? Why does the choice of prior matter so much?
4. *(stretch)* **Implied confidence on Sharpe.** Take SPY's annualized mean and SE from §2.2 and SPY's annualized vol from Ch2. Treating vol as known (it has its own SE but it's smaller than the mean's), compute a rough 95% CI on SPY's Sharpe ratio. (Hint: divide the mean's CI bounds by the vol; assume risk-free rate is zero for simplicity.)

---

## Up next

**Chapter 5: Risk Metrics — drawdown, VaR, and the Sharpe ratio.** Now that we have honest error bars on the numerator of Sharpe, the next chapter builds the metric without overclaiming. Drawdown answers a different question (path-dependent worst loss), VaR answers another (magnitude in dollar terms), and all three together fill out the "single-number summary of an investment" toolkit.
