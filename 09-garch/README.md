# Chapter 9 — Time-Varying Models: GARCH and DCC-GARCH

> Chapter 8 said: regress on factors to decompose returns. Chapter 9 says: *returns aren't the only thing that varies — vol and correlation vary through time too*, and the constant-σ assumption that Ch5's VaR and Ch6's Σ̂ leaned on is a load-bearing fiction. **GARCH(1,1)** for σ<sub>t</sub>; **DCC-GARCH** for ρ<sub>t</sub>. Once vol is time-varying, all of Ch5's risk metrics become *dynamic*, and the wide CIs from those chapters narrow because the model uses recent information instead of averaging the whole sample.

The chapter introduces **maximum likelihood estimation (MLE)** in passing — the only chapter that genuinely needs it.

### Reader takeaway

Volatility and correlation are *not constants* — they cluster, regime-shift, and have memory. GARCH is the simplest model that captures this. The price you pay for that realism is **two extra parameters and a likelihood you have to fit numerically** instead of in closed form. The risk metrics it produces (today's σ, today's VaR) update day-by-day instead of averaging across the whole sample.

### Learning objectives

After this chapter you can:

1. Explain why **a constant-σ assumption is the load-bearing weakness of Ch5's parametric VaR**, and what GARCH replaces it with.
2. Read the GARCH(1,1) equation σ²<sub>t</sub> = ω + α·ε²<sub>t-1</sub> + β·σ²<sub>t-1</sub> and say what each parameter does.
3. Fit GARCH(1,1) on SPY by hand in plain `scipy` (20-40 lines depending on the model) and produce a time series of σ̂<sub>t</sub>.
4. Compute **GARCH-VaR** — Ch5's parametric VaR with σ̂<sub>t</sub> instead of constant σ̂.
5. Recognise when GARCH helps (calm-to-turbulent transitions like Feb 2020) and when it hurts (one-off jumps the model can't absorb gracefully).
6. Read the headline output of a DCC-GARCH for time-varying correlations.

## What we mean by "modeling time-varying second moments"

Three rungs, each strictly more powerful and strictly more expensive:

| Model | Captures | Cost | Section |
|---|---|---|---|
| **EWMA** (RiskMetrics 1996) | Vol clustering only; vol drifts forever (no mean reversion) | Closed form; 1 hyperparameter | §2 |
| **GARCH(1,1)** | Vol clustering + mean reversion to long-run vol | MLE fit; 3 parameters | §3-5 |
| **DCC-GARCH** | Time-varying *correlations* between assets | MLE on top of per-asset GARCHs | §6 |

## 1. Setup

**SPY 20-year daily log returns** for univariate work (same as Ch1-2). **SPY/TLT panel** for §6 DCC (same as Ch3). N = 5,030 observations from May 2006 to May 2026.

> **Implementation note: this chapter does *not* use the `arch` package.** Both `arch` (Kevin Sheppard's GARCH library) and `pandas-datareader` (Ch8's Fama-French puller) depend on `pandas.util._decorators.deprecate_kwarg`, whose API changed in pandas 3.0 — the libraries have not been updated as of writing. **Pedagogically this is a feature, not a bug:** GARCH's headline contribution to the curriculum is the introduction of MLE, and we now actually do the MLE ourselves in plain `scipy` (20-40 lines depending on the model) rather than handing it to a library and looking at the output.

> **Foot-gun: GARCH numerics work in *percent*, not decimal returns.** Multiply log returns by 100 before fitting; convert σ̂<sub>t</sub> back to decimal by dividing by 100 for VaR computations on dollar positions. The cell `s4-fit` does this conversion explicitly.

## 2. EWMA — the cheapest answer

EWMA is the **exponentially-weighted moving average** of squared returns. Closed-form recursion; no fitting; one hyperparameter (the decay). It was popularised by **RiskMetrics** — JP Morgan's 1996 technical document that made EWMA the industry-standard daily vol model.

### 2.1 The recursion

> σ²<sub>t</sub> = (1 − λ) · ε²<sub>t-1</sub> + λ · σ²<sub>t-1</sub>

where:
- *ε<sub>t-1</sub>* — yesterday's return shock. **Units:** percent (we work in percent for numerical stability).
- *σ²<sub>t</sub>* — today's variance forecast. **Units:** percent-squared.
- *λ* — decay parameter, in (0, 1). Larger = slower decay = more memory.
- *σ²<sub>0</sub>* — initialization, typically the sample variance over a warm-up window.

**RiskMetrics defaults:** λ = 0.94 (daily), λ = 0.97 (monthly). Decay half-life t<sub>1/2</sub> = log(2)/log(1/λ) ≈ 11 days at λ = 0.94 and ~23 days at λ = 0.97 (see notebook for code).

### 2.2 SPY EWMA over 20 years

The notebook plots SPY's annualized EWMA σ̂. Three named windows are visible:

- **GFC** (2007-10 → 2009-03) — sustained elevated regime; σ̂ peaks at multiple times the whole-sample average.
- **COVID** (Feb-Apr 2020) — sharp spike, mean-reverts within months.
- **2022 selloff** — slower, smaller spike than the prior two.

> **Foot-gun: EWMA has no long-run vol.** It just drifts. After a calm decade σ̂ is tiny; after a crisis spike σ̂ stays elevated for weeks regardless of fundamental conditions. **GARCH fixes this.**

## 3. GARCH(1,1) — adding mean reversion

GARCH = Generalized AutoRegressive Conditional Heteroskedasticity. The (1, 1) means one ARCH lag and one GARCH lag — the simplest specification that captures vol clustering *and* mean reversion.

### 3.1 The equation

> σ²<sub>t</sub> = ω + α · ε²<sub>t-1</sub> + β · σ²<sub>t-1</sub>

where:
- *ω* — baseline variance contribution. **Units:** percent-squared.
- *α* — sensitivity to yesterday's *shock magnitude* (squared return). Dimensionless. Typically 0.05–0.15 for daily equities.
- *β* — persistence of yesterday's *forecast variance*. Dimensionless. Typically 0.85–0.95.
- *σ²<sub>t</sub>* — conditional variance forecast for day *t*.
- *ε<sub>t-1</sub>* — yesterday's shock (return − constant mean).

**Stationarity / mean-reversion:** α + β < 1 (otherwise variance explodes). **Stationarity** here means the statistical properties (mean, variance) don't drift over time; for GARCH(1,1), α + β < 1 ensures finite long-run variance. For daily equities, α + β ≈ 0.97-0.99 — high persistence but stable.

**Long-run unconditional variance:** σ̄² = ω / (1 − α − β). The GARCH process mean-reverts to this level.

### 3.2 MLE — the one-paragraph primer

Why MLE? **GARCH cannot be fit by least squares.** There is no observed σ<sub>t</sub> series to regress on; we only see realised returns ε<sub>t</sub>. **Maximum likelihood asks: *what parameter values make the observed sequence of returns most likely under the model?***

A toy example: observe 7 heads in 10 coin flips. The likelihood under p (probability of heads) is L(p) = p<sup>7</sup>·(1−p)<sup>3</sup>. Differentiating log L and setting to zero gives p̂ = 0.7 — the value that maximises L. **The MLE is the value that maximises the likelihood.**

**Coin-flip → GARCH bridge.** We never observe `p`; we observe outcomes (H/T) and back out `p`. GARCH is the same: we never observe σ<sub>t</sub> directly, we observe ε<sub>t</sub> and back out (ω, α, β). For each candidate (ω, α, β), we run the recursion forward to get σ²<sub>1</sub>, σ²<sub>2</sub>, ..., σ²<sub>T</sub>. Each ε<sub>t</sub> is then assumed N(0, σ²<sub>t</sub>). The likelihood is the joint density of all observed ε<sub>t</sub> under those σ<sub>t</sub>. We pick (ω, α, β) to maximise that joint density.

In plain English: we score every candidate (ω, α, β) by how well its implied σ<sub>t</sub>-path explains the observed return magnitudes, and pick the highest-scoring one. **Taking the log** turns the product of densities into a sum, which is numerically stable and easier to differentiate. We minimise the *negative* log-likelihood numerically with `scipy.optimize.minimize`.

<details>
<summary>The math</summary>

Assuming ε<sub>t</sub> | F<sub>t-1</sub> ~ N(0, σ²<sub>t</sub>), the joint density of (ε<sub>1</sub>, ..., ε<sub>T</sub>) factors into a product of conditional Gaussians. Taking logs and dropping constants:

> log L(ω, α, β) = −½ Σ<sub>t</sub> [ log(σ²<sub>t</sub>) + ε²<sub>t</sub> / σ²<sub>t</sub> ]

where:
- *Σ<sub>t</sub>* — sum over t = 1, ..., T (every observation contributes a term).
- *F<sub>t-1</sub>* — the information set available at t−1 (history through yesterday).
- *σ²<sub>t</sub>* — the conditional variance implied by the GARCH recursion under the candidate (ω, α, β); not observed, computed from the recursion.
- *ε<sub>t</sub>* — the observed innovation (demeaned return).
- *−½* prefactor — comes from the Gaussian density 1/√(2πσ²) · exp(−ε²/(2σ²)).
- *(constants dropped)* — the −T/2 · log(2π) term that doesn't depend on (ω, α, β) and so doesn't affect the argmax.

The likelihood weighs *both* fit (ε²<sub>t</sub> / σ²<sub>t</sub> small means σ<sub>t</sub> matched the realised shock) and parsimony (log(σ²<sub>t</sub>) penalises blowing up σ<sub>t</sub> just to make the fit term small).

</details>

> **Pedagogical note: the conditional-Gaussian assumption is wrong** (Ch2 fat tails). GARCH-with-Gaussian-residuals still works because the *conditional* distribution is closer to Gaussian than the *marginal* — but Ch10 will revisit on residuals.

### 3.3 Worked numerical example

Yesterday's σ̂<sub>t-1</sub> = 1% (per day, decimal); yesterday's ε<sub>t-1</sub> = +3% (a 3-σ shock). With our fitted equity parameters (ω ≈ 0.03 pct², α = 0.137, β = 0.840 — see §4):

> σ²<sub>t</sub> = 0.03 + 0.137 · 9 + 0.840 · 1 ≈ 2.10 pct²
>
> σ̂<sub>t</sub> ≈ 1.45% per day

A 3-σ shock pushes today's σ̂ up meaningfully but not catastrophically. **That's mean reversion** — a constant-σ model would be unchanged; an EWMA(0.94) would move further but never anchor anywhere; GARCH eventually pulls back to its long-run σ̄.

## 4. GARCH(1,1) fit on SPY

The notebook fits GARCH(1,1) by hand via `scipy.optimize.minimize` on the negative log-likelihood. Headline numbers:

| Parameter | Value |
|---|---|
| ω | 0.0305 pct² |
| α | **0.137** |
| β | **0.840** |
| persistence (α + β) | **0.976** |
| long-run σ̄ (annualized) | **18.0%** |
| sample σ (annualized, comparison) | 19.5% |

**Reading the fit.** α ≈ 0.14 means yesterday's shock² gets ~14% weight in today's variance forecast; β ≈ 0.84 means yesterday's forecast gets ~84% weight. Today's σ̂ is mostly a smooth update of yesterday's, with a 14% "kick" from yesterday's actual outcome — *exactly* what vol clustering looks like: persistent + reactive.

α + β ≈ 0.976 confirms high persistence; the GARCH(1,1) is **near-integrated** (α + β so close to 1 that vol shocks decay extremely slowly, on the edge of non-stationary) for daily equities. Long-run σ̄ ≈ 18.0% annualized sits *below* whole-sample σ ≈ 19.5% (a ~7.7% gap). This is because whole-sample σ is itself inflated by the same crisis tails GARCH absorbs into ω — the recursion partitions vol into a steady-state piece (σ̄) and a transient piece (the α, β-driven shock response). Model and sample agree on order of magnitude, sanity-checking the fit.

### 4.1 The σ̂_t plot

The notebook plots GARCH σ̂<sub>t</sub> annualized over 20 years, with the long-run σ̄ as a horizontal reference line. The picture: long calm regimes near σ̄, sharp spikes during stress, smooth mean-reverting decay back toward σ̄. Qualitatively similar to EWMA but the spikes decay *back to a fixed level* — which is the GARCH innovation EWMA can't match.

### 4.2 Diagnostic — squared-residual ACF before vs after

The most concrete "GARCH worked" picture is a side-by-side ACF:

| Lag | ACF of raw squared returns | ACF of squared standardized residuals |
|---|---|---|
| 1 | 0.272 | −0.007 |
| 2 | **0.450** | 0.013 |
| 3 | 0.248 | −0.001 |
| 4 | 0.292 | 0.031 |
| 5 | 0.301 | −0.007 |

*Values as of 2026-05-05 fit; recompute in the notebook for current data.*

**Raw squared returns** show clear positive autocorrelation across many lags — vol clustering. **Squared *standardised* residuals (ε<sub>t</sub>/σ̂<sub>t</sub>)²** are flat near zero — the clustering has been absorbed by the model. *This is what "GARCH worked" looks like.*

If the right-side ACF were *not* flat, the GARCH(1,1) would be under-fit; you'd reach for EGARCH or a higher (p, q). For SPY 20y, GARCH(1,1) is sufficient.

## 5. GARCH-VaR — Ch5's parametric VaR with σ̂_t

Apply Ch5's parametric Gaussian VaR formula with the conditional σ̂<sub>t</sub> instead of constant σ̂:

> VaR<sub>t</sub>(q) = z<sub>q</sub> · σ̂<sub>t</sub>

where:
- *q* — the tail probability (e.g., 0.05 for 5%-VaR).
- *z<sub>q</sub>* — the q-quantile of the standard normal (z<sub>0.05</sub> = 1.645). One-tailed.
- *σ̂<sub>t</sub>* — today's GARCH-implied volatility forecast.
- *VaR<sub>t</sub>(q)* — today's VaR. **Units:** decimal log return (or dollar terms after multiplying by position size).

For a $100k position, the dollar 5%-VaR on day *t* is $100,000 · 1.645 · σ̂<sub>t</sub>.

### 5.1 Three event-window narrations

| Window | Period | Peak ratio (GARCH-VaR / constant-VaR) |
|---|---|---|
| GFC peak | Sep-Dec 2008 | **5.28×** |
| COVID | Feb-Apr 2020 | **5.55×** |
| 2022 selloff | full year 2022 | 1.94× |

**GFC peak.** GARCH-VaR widens to roughly 5.3× the constant-σ baseline. The "$1,645 expected daily worst case" (from Ch5 §3.3, $100k position) widens to about $8,700. The constant-σ assumption was *severely* wrong on those days — Ch5's parametric VaR was painting an entirely wrong picture of risk.

**COVID (March 2020).** GARCH-VaR spikes to ~5.6× baseline within a week, mean-reverts over months. The fastest spike in the 20-year window — exactly the kind of regime where GARCH earns its keep.

**2022 selloff.** GARCH-VaR rises smoothly over the year, peaks at ~1.94× baseline. A slower, less extreme regime than 2008 or 2020, but still a clear episode of "today's risk is higher than the whole-sample average."

### 5.2 5%-VaR backtest — a counter-intuitive finding

Counting realised return-below-VaR breaches over 20 years (target ≈ 5% of days):

| Method | Breaches | Rate |
|---|---|---|
| GARCH 5%-VaR | 276 / 5030 | **5.49%** (close to nominal) |
| Constant 5%-VaR | 210 / 5030 | **4.17% — *under*-breach** |

That's not a typo. Constant-σ over 20 years averages calm and stress days. On calm days the threshold is wider than needed (rare breaches); on stress days the threshold is tighter than needed (clustered breaches). Aggregate breach count *under-shoots* 5% (we see 4.17%) because calm days dominate the sample. The real failure mode of constant-σ VaR isn't the average breach rate — it's that breaches cluster in stress periods, exactly when you most need the model to be honest. GARCH-VaR widens its threshold in stress, so it tracks the nominal rate (5.49% ≈ 5%) and breaches are spread more uniformly through time. A backtest that just counts breaches misses the clustering story; one that audits *when* breaches happen (Christoffersen test, conditional coverage) reveals it.

### 5.3 Honest note on the deepest tail

GARCH-VaR is *conditionally Gaussian* — assumes ε<sub>t</sub>/σ̂<sub>t</sub> ~ N(0, 1). On tail-event days even the conditional distribution has fatter tails than Normal. So GARCH-VaR over-reads the 5% tail correctly (above) but still under-estimates 0.1% / 0.05% deep-tail VaR even after fixing σ̂<sub>t</sub>. **Ch10 fixes this with EVT applied to standardised residuals (ε<sub>t</sub>/σ̂<sub>t</sub>)** — the right combination is "GARCH for the variance, EVT for the tail shape," known in production as **filtered historical simulation (FHS)**.

## 6. DCC-GARCH — time-varying correlations

DCC = Dynamic Conditional Correlation. Two steps:

1. **Fit per-asset GARCH** on each series; extract σ̂<sub>i,t</sub> and **standardise residuals**: z<sub>i,t</sub> = ε<sub>i,t</sub> / σ̂<sub>i,t</sub>. The z<sub>i,t</sub> are approximately unit-variance and i.i.d.-like.
2. **Update the correlation matrix as a GARCH-style recursion** on the standardised residuals: a Q-step that lets a "correlation-like" matrix evolve with memory, then an R-step that renormalises Q so the diagonal is exactly 1 (a valid correlation matrix every step).

**Concrete worked example.** Imagine the Q-step produces Q<sub>t</sub> = [[1.04, −0.51], [−0.51, 0.96]]. The diagonal is not 1, so we divide row/column by √diag to force unit variance, getting R<sub>t</sub> = [[1, ρ<sub>t</sub>], [ρ<sub>t</sub>, 1]] with ρ<sub>t</sub> = −0.51 / √(1.04 · 0.96) ≈ −0.510. The Q step lets correlation evolve like a GARCH; the R step renormalises so the result is a valid correlation matrix every step.

The two extra parameters (a, b) are MLE-fit on top of the per-asset GARCHs. Total parameter count for an n-asset DCC: 3n (per-asset GARCH) + 2 (DCC).

<details>
<summary>The Q-recursion and R-normalisation in detail</summary>

> Q<sub>t</sub> = (1 − a − b) · Q̄ + a · z<sub>t-1</sub>z<sub>t-1</sub><sup>T</sup> + b · Q<sub>t-1</sub>
>
> R<sub>t</sub> = diag(Q<sub>t</sub>)<sup>−1/2</sup> · Q<sub>t</sub> · diag(Q<sub>t</sub>)<sup>−1/2</sup>

where:
- *Q̄* — sample correlation matrix of z (the unconditional correlation), the analogue of the unconditional σ̄² in univariate GARCH.
- *a, b* — DCC parameters; analogous to GARCH's α, β. Fit by MLE under a multivariate Gaussian assumption on z<sub>t</sub>.
- *z<sub>t-1</sub> z<sub>t-1</sub><sup>T</sup>* — **outer product** of the standardised-residual vector with itself; for a 2-asset panel this is a 2×2 matrix (not a scalar): [[z<sub>1</sub>², z<sub>1</sub>z<sub>2</sub>], [z<sub>1</sub>z<sub>2</sub>, z<sub>2</sub>²]].
- *Q<sub>t</sub>* — the unscaled "correlation-like" matrix at *t*; its diagonal generally drifts away from 1, which is why the R-step exists.
- *diag(Q<sub>t</sub>)<sup>−1/2</sup>* — diagonal matrix with entries 1/√(Q<sub>t,ii</sub>); pre- and post-multiplying divides each row *and* column by √(diagonal element), forcing R<sub>t</sub>'s diagonal to be exactly 1.
- *R<sub>t</sub>* — the actual conditional correlation matrix at *t* (diagonal = 1, off-diagonal in [−1, 1]).

**Why a + b near 1 is the correlation analogue of vol persistence.** a + b = 0.987 is the correlation analogue of GARCH persistence — correlation regimes also have memory, and shocks to ρ<sub>t</sub> decay slowly.

</details>

### 6.1 SPY/TLT DCC fit

| Parameter | Value |
|---|---|
| a | 0.046 |
| b | 0.940 |
| a + b | 0.987 (high persistence, like GARCH itself) |
| ρ̂<sub>t</sub> range over 20y | **−0.77 to +0.42** |

The notebook plots Ch3's 60-day rolling correlation and DCC ρ̂<sub>t</sub> on the same axes. Highlights:

- **2008-2009 (GFC).** DCC ρ̂ stays deeply negative (min ≈ −0.70). Bonds were a strong hedge for stocks during the financial crisis — flight to quality.
- **2022 selloff.** DCC ρ̂ flips into the positive range (max ≈ +0.32). The Fed's rate hikes hit bonds and stocks simultaneously; the multi-decade bond-stock hedge broke. **Ch3's promised sign flip, captured cleanly by the DCC model.**
- **DCC reaches new regimes faster than rolling-60.** When 2022 hit, rolling-60 took weeks to drift positive; DCC was already there in days.

### 6.2 Caveat

> **DCC scales to ~10 assets, not 100.** Beyond that, the (a, b) MLE becomes brittle; correlation-target shrinkage is the standard production fix and is out of scope here.

> **Per-asset GARCH residuals must be reasonably i.i.d.** If a GARCH(1,1) fits poorly on one of the assets, the DCC inherits the misspecification. The diagnostic ACF plots from §4.2 apply per-asset.

## 7. Limits — five caveats

**1. Conditional Gaussian.** Real residuals are still fat-tailed even after standardising by σ̂<sub>t</sub>. **Ch10's EVT on standardised residuals** is the natural fix.

**2. Structural breaks.** GARCH assumes (ω, α, β) are constants. They're not — pre-2008 vs post-2020 fits differ; long windows average across regimes. (Exercise 2 measures this.)

**3. No regime prediction.** GARCH adapts *after the fact.* It cannot predict an upcoming spike; it can only update *during* one. The Feb 2020 σ̂ trajectory shows this: the model jumps *with* COVID, not before.

**4. DCC scale.** Beyond ~10 assets the (a, b) MLE becomes brittle.

**5. Backtest danger.** Fitting GARCH on the whole sample then "predicting" σ̂<sub>t</sub> is *in-sample*. Honest backtests refit on a rolling window. **Chapter 13** revisits this rigorously.

## 8. What we just learned

- **EWMA** — cheap, intuitive, no mean reversion. Use when you need a quick number.
- **GARCH(1,1)** — three parameters, MLE-fit, mean-reverting. The standard daily-equity vol model. *Hand-rolled in plain `scipy`.*
- **DCC-GARCH** — extends GARCH to multivariate; gives time-varying correlations.
- **Hidden lesson — MLE.** The most useful inferential tool we hadn't introduced; the only chapter that genuinely needs it.

## 9. So what?

**Decision rules:**

- **Use GARCH-σ for *today's* risk decisions.** Whole-sample σ is for benchmarking; today's GARCH-σ is for sizing.
- **Don't use raw GARCH-VaR for tail events.** Pair with EVT (**Ch10**).
- **Refit on a rolling window.** Don't fit once on 20y and use the parameters forever; structural breaks happen.
- **For correlations, EWMA-on-products is often as good as DCC at small scale** — and 100× faster. Use DCC when you have a story about why time-varying correlations matter for *this specific* decision.

**What this chapter can't yet tell you:**

- What to do about fat tails in residuals. **Ch10 EVT.**
- How to combine vol clustering with strategy signals. **Future Ch12.**
- How to backtest a GARCH-VaR system honestly. **Ch13.**
- How GARCH behaves at intraday frequencies. **Future Ch15.**

## 10. Up next

**Chapter 10 — Tail Risk and Dependence: EVT and Copulas.** §5 just complained that GARCH-VaR is conditionally Gaussian and under-prices the deepest tail. §7 confirmed that fat tails survive standardisation. Ch10 is where we model the tail *itself* with **Extreme Value Theory** — fit a Generalized Pareto Distribution to the worst few percent of returns and *extrapolate beyond the worst observed loss*. Ch10 also pays Ch3's third correlation flavor — *tail dependence* — with a copula-based measure.

## Key Terms

| Term | Definition |
|---|---|
| **EWMA** | Exponentially-weighted moving average; closed-form vol recursion with decay parameter λ. |
| **GARCH(1,1)** | σ²_t = ω + α·ε²_{t-1} + β·σ²_{t-1}; one ARCH lag, one GARCH lag. |
| **Conditional vs unconditional vol** | Conditional = today's, given history; unconditional = whole-sample average. |
| **Persistence (α + β)** | Sum of GARCH coefficients; how slowly vol shocks decay. |
| **Long-run / unconditional vol** | σ̄ = √(ω/(1−α−β)); the GARCH-implied steady-state vol. |
| **ARCH** (named) | Autoregressive Conditional Heteroskedasticity; GARCH's predecessor. |
| **MLE (Maximum Likelihood Estimation)** | Pick parameters that make observed data most likely under the model. |
| **RiskMetrics** | JP Morgan's 1996 technical document that made EWMA the industry-standard daily vol model. |
| **Stationarity** | Statistical properties (mean, variance) don't drift over time; for GARCH(1,1), α + β < 1 ensures finite long-run variance. |
| **Near-integrated** | α + β so close to 1 that vol shocks decay extremely slowly, on the edge of non-stationary. |
| **Log-likelihood** | The log of the joint density of the data under the model parameters; taking the log turns the product of densities into a sum, which is numerically stable and easier to differentiate. MLE picks the parameters that maximise it. |
| **Standardised residual** | ε<sub>t</sub> / σ̂<sub>t</sub>; should be approximately i.i.d. if the vol model captured everything. |
| **DCC-GARCH** | Dynamic Conditional Correlation; multivariate GARCH for time-varying ρ. |
| **Structural break** | Permanent shift in the data-generating process (e.g., COVID jump). |
| **Regime** | An extended period with stable parameters (refresh from Ch2). |
| **GARCH-VaR** | Ch5's parametric VaR with σ̂<sub>t</sub> in place of constant σ̂. |
| **EGARCH** (named) | Asymmetric GARCH variant capturing the leverage effect. |
| **GJR-GARCH** (named) | Another asymmetric GARCH variant. |
| **`arch` (package, named)** | Kevin Sheppard's Python library for GARCH-family models. *Currently broken under pandas 3.0.* |

## Exercises

Try these in fresh cells in the companion notebook. Solutions are not provided — the goal is to consolidate the chapter's machinery on slightly different inputs.

1. **EWMA vs GARCH on a sector.** Refit both models on XLE (energy — high-vol, high-clustering). How do the σ̂<sub>t</sub> series differ? When does EWMA over-react vs GARCH? Are XLE's GARCH parameters similar to SPY's, or noticeably different?

2. **Persistence audit.** Refit GARCH(1,1) on SPY using the first 10y only, then the second 10y only. How do α, β, persistence change? What does that say about whether a single 20y fit is "the right" parameterisation for production use?

3. **GARCH-VaR at 1%.** Repeat the §5.2 backtest at 1% VaR. Does GARCH-VaR still hit nominal? Does constant-σ still under-breach? Why might the 1% level be more sensitive to the model choice than 5%?

4. *(stretch)* **DCC on three assets.** Add GLD to the SPY/TLT pair. Fit DCC on the three-asset panel. How does SPY/GLD behave around 2008-09 and 2020 vs SPY/TLT? Does GLD's "flight-to-quality" pattern look like TLT's, or different in shape?
