# Chapter 10 — Tail Risk and Dependence: EVT and Copulas

> Two oldest open promises in the curriculum land here. **Ch2 §1 fat tails** were measured (excess kurtosis ≈ 14, |z| > 5 ratio orders of magnitude above Normal expectation) but never modelled. **Ch3 §3 tail dependence** — the third correlation flavor — was deferred because Pearson's conditional correlation suffers a known truncation artifact. Chapter 10 closes both promises with **Extreme Value Theory** for univariate tails and the **tail dependence coefficient** for joint extremes.

This is the **math-densest chapter** so far. The compensation: every formula is grounded in a Ch2 or Ch3 plot the reader has already internalised.

A subtle bonus: **EVT applied to GARCH-standardised residuals** is strictly better than EVT on raw returns. Chapter 9 sets this up; Chapter 10 collects the win in §3.4 — **filtered historical simulation (FHS)**, the production-grade tail-VaR combination.

### Reader takeaway

"How bad can a single day be?" and "do bad days line up across assets?" cannot be answered with the central body of the distribution. Both questions require modeling **the tails specifically** — which is what EVT and copulas do. The cost is statistical: tail estimates use only the worst few percent of data, so confidence intervals are wider, and the answers depend on threshold choices the reader must make explicitly.

### Learning objectives

After this chapter you can:

1. Explain why **Gaussian VaR systematically misprices the deep tail** — and what GPD-VaR replaces it with.
2. Pick a tail threshold using a mean-residual-life plot or rule-of-thumb percentile.
3. Fit the **Generalized Pareto Distribution (GPD)** to peaks-over-threshold data and read off ξ (tail-shape) and σ (tail-scale).
4. Distinguish **block maxima** from **peaks-over-threshold** as the two main EVT flavors, and pick POT for daily-return work.
5. Read a **tail dependence coefficient** λ ∈ [0, 1] as "the probability that asset B is in its worst tail given that A is in its."
6. State Sklar's theorem in plain English: *any* joint distribution = its marginals + a copula.

## What we mean by "tail-specific modeling"

Three questions; three tools:

| Question | Tool | Section |
|---|---|---|
| **How bad can one day get?** | EVT — Generalized Pareto Distribution via peaks-over-threshold | §2-4 |
| **Do bad days line up across assets?** | Tail dependence coefficient (empirical) | §5 |
| **Joint tail modelling, formally** | Copula + GPD marginals (named only) | §6 |

## 1. Setup

**SPY 20y daily log returns** for univariate EVT (same as Ch1-2). **SPY/TLT, SPY/XLF, SPY/XLK** panels for tail dependence (same as Ch3). N = 5,030 observations from May 2006 to May 2026. No new packages — `scipy.stats.genpareto` is already in `scipy`.

The §3.4 FHS sidebar reuses Ch9's GARCH machinery. No new requirements.

> **Foot-gun: positive losses, negative returns.** The chapter works with **losses = −log returns** (positive = bad). Every formula and every variable is on this scale. Convert at the boundary; flagged again at every formula.

## 2. EVT preliminaries — block maxima vs peaks-over-threshold

EVT models the *tail* of a distribution. Two main flavors:

> **Block maxima (BM):** divide the data into non-overlapping blocks (e.g., calendar years), take the worst day in each block, fit a *Generalized Extreme Value (GEV)* distribution to the resulting block maxima.
>
> **Peaks over threshold (POT):** pick a high threshold *u*, take all observations above *u*, fit the *exceedances* (X − u | X > u) to a *Generalized Pareto Distribution (GPD)*.

**The choice for daily returns: POT.** With 20 years (~5,030 daily observations):

- BM with annual blocks gives only 20 maxima — wasteful with most of the data.
- POT at the 95th percentile gives ~250 exceedances — uses the actual tail.

POT is the daily-return choice. The rest of this chapter uses POT.

### 2.1 Pickands-Balkema-de Haan in plain English

The theorem behind POT-GPD: as the threshold *u* rises, the conditional distribution of (X − u | X > u) converges to a **Generalized Pareto Distribution** with shape ξ and scale σ. *No proof here.* This is *why* GPD is the right tail model — it's not arbitrary.

<details><summary>Pickands-Balkema-de Haan: why this works</summary>

For any distribution in the *max-domain-of-attraction* of a Generalized Extreme Value (GEV) distribution, exceedances above a sufficiently high threshold converge in distribution to GPD. Most distributions practitioners care about (Normal, Student-t, exponential, log-normal, Pareto) sit in this domain. The convergence is in distribution and is unique up to the parameters (ξ, σ).

</details>

### 2.2 The GPD

We need a distribution that flexibly handles three tail regimes (heavy / exponential / bounded) with two parameters. The GPD is that distribution. Read the formula below as *probability falls off as a power of the exceedance, with the power controlled by ξ.*

The Generalized Pareto density:

> f(y; ξ, σ) = (1/σ) · (1 + ξ·y/σ)<sup>−(1/ξ) − 1</sup>  for y ≥ 0 and 1 + ξ·y/σ > 0

where:
- *y = X − u* — the exceedance above threshold *u*. **Units:** decimal log-loss (positive).
- *σ* — scale parameter. Same units as y. *Always positive.*
- *ξ* — shape parameter. Dimensionless.

**Three regimes for ξ:**

| Regime | ξ | Tail | Examples |
|---|---|---|---|
| Heavy | ξ > 0 | Pareto-like; some moments don't exist | Daily equity returns; insurance losses |
| Exponential | ξ = 0 | Memoryless | Queueing-theory waiting times |
| Bounded | ξ < 0 | Has a hard upper limit | Annual rainfall (physical max) |

> **Pareto** — the prototypical heavy-tailed distribution where probability falls off as a power of the variable; "Pareto-like" means tails decay polynomially, not exponentially.
>
> **Memoryless** — once you exceed the threshold, how much further you go is independent of how far you already went; the exponential is the only continuous memoryless distribution.

Daily-equity tails sit firmly in ξ > 0 (mildly heavy). The §3 fit lands ξ̂ ≈ +0.19 for SPY.

## 3. GPD fit on SPY losses

### 3.1 Choosing the threshold u

The notebook plots SPY's **mean residual life (MRL)** curve: mean exceedance above *v* plotted against *v*, for *v* ranging from the 50th to the 99th percentile of losses.

**Reading the MRL plot.** Above the right threshold, the mean exceedance grows approximately linearly with *u* — that's the GPD theory talking. Below the right threshold, the curve bends (the data isn't yet in the tail). **Pick u in the linear region.** For SPY, the 95th percentile of losses (≈ 1.82% daily log-loss) falls in the linear region.

### 3.2 The fit

Number of exceedances above u = p95: **n<sub>u</sub> = 252**.

| Quantity | Value |
|---|---|
| u (p95 of losses) | 0.01817 (1.82% daily) |
| n<sub>u</sub> | 252 |
| **ξ̂** | **+0.191** (mildly heavy) |
| σ̂ | 0.00991 |

The notebook produces a **GPD Q-Q plot** for fit validation: empirical exceedance quantiles plotted against GPD-implied quantiles. (**Q-Q plot** — quantile-quantile plot; if the empirical points lie on the diagonal, the data follows the proposed distribution. Introduced in Ch2 §1.2.) The points fall close to the diagonal up to the deepest observed exceedance — a clean fit. **Deviation in the upper-right would mean the *real* tail is heavier than fitted GPD; we don't see that here, which means ξ̂ ≈ +0.19 captures the empirical tail well at this threshold.**

**Cross-back to Ch2.** Ch2 reported excess kurtosis ≈ 14 and |z| > 5 ratios orders of magnitude above Normal; ξ̂ = +0.19 is the *parametric* statement of the same fact.

### 3.3 Threshold sensitivity

| u (percentile) | u (value) | n<sub>u</sub> | ξ̂ | σ̂ |
|---|---|---|---|---|
| p80 | 0.00598 | 1006 | +0.164 | 0.00803 |
| p90 | 0.01201 | 503 | +0.193 | 0.00855 |
| **p95** | **0.01817** | **252** | **+0.191** | **0.00991** |
| p97.5 | 0.02531 | 126 | +0.210 | 0.01117 |
| p99 | 0.03636 | 51 | +0.078 | 0.01591 |

ξ̂ is **reasonably stable across u ∈ [p80, p97.5]** (range 0.16–0.21) — the picking-of-p95 isn't a fragile choice. ξ̂ at p99 drops to 0.08 because only 51 exceedances remain — pure noise. **Don't read the p99 fit as "thin-tail evidence"; read it as "too few observations."**

### 3.4 Sidebar — EVT on GARCH-standardised residuals (FHS)

EVT assumes i.i.d. exceedances. (**i.i.d.** — independent and identically distributed; every observation drawn the same way, with no carryover from past values.) Daily returns *aren't* i.i.d. — vol clustering (Ch9) is real. The fix: refit on **standardised residuals** z<sub>t</sub> = ε<sub>t</sub>/σ̂<sub>t</sub> from a GARCH(1,1) (Ch9 §4) before doing EVT. This is **filtered historical simulation (FHS)** in production language.

The notebook fits GARCH(1,1) on SPY (the same fit as Ch9), standardises residuals, and refits GPD on the residual losses:

| Quantity | Raw returns | Standardised residuals |
|---|---|---|
| ξ̂ | **+0.191** | **+0.056** |
| σ̂ | 0.00991 | 0.684 (z scale) |

**ξ̂ on standardised residuals is much smaller than on raw returns** — GARCH absorbed most of the fat-tail behavior. The residuals are closer to i.i.d.-Gaussian than the raw returns; the *remaining* tail thickness in z<sub>t</sub> is what's irreducibly non-Gaussian.

In production: combine today's σ̂<sub>T</sub> from Ch9 GARCH with this chapter's tail shape from the residual EVT to get a properly conditional, properly tail-aware VaR. **Exercise 4** is where you put the pieces together end-to-end and see how today's regime affects the resulting VaR estimate.

## 4. EVT-VaR and EVT-ES at deep quantiles

### 4.1 Closed-form formulas

Inverting the GPD CDF (algebra in `<details>`):

> VaR<sub>q</sub> = u + (σ̂ / ξ̂) · [ ((n / n<sub>u</sub>) · q)<sup>−ξ̂</sup> − 1 ]

where:
- *q* — tail probability. **Units:** dimensionless probability.
- *n* — total sample size; *n<sub>u</sub>* — number of exceedances above *u*.
- *u* — threshold; *ξ̂*, *σ̂* — fitted GPD parameters.
- *VaR<sub>q</sub>* — VaR at the q-tail. **Units:** decimal log-loss.

Expected shortfall (CVaR), assuming ξ̂ < 1:

> ES<sub>q</sub> = (VaR<sub>q</sub> + σ̂ − ξ̂·u) / (1 − ξ̂)

where:
- *VaR<sub>q</sub>* — EVT-VaR at tail probability q (from the formula above). **Units:** decimal log-loss.
- *σ̂*, *ξ̂* — fitted GPD scale and shape parameters.
- *u* — threshold.
- *ES<sub>q</sub>* — expected loss conditional on exceeding VaR<sub>q</sub>. **Units:** decimal log-loss.

<details><summary>Derivation of EVT-VaR</summary>

The GPD CDF for exceedance Y = X − u given X > u is P(Y ≤ y) = 1 − (1 + ξ·y/σ)<sup>−1/ξ</sup>. The unconditional probability of X > u is approximately n<sub>u</sub>/n. Combining: P(X > u + y) ≈ (n<sub>u</sub>/n) · (1 + ξ·y/σ)<sup>−1/ξ</sup>. Set the right side equal to q and solve for y, then add u, to get the formula.

</details>

### 4.2 The headline comparison table

Three methods, four quantiles:

| q | Historical | Gaussian | EVT-VaR | EVT-ES |
|---|---|---|---|---|
| 0.05 | 0.0182 | 0.0197 | 0.0182 | 0.0305 |
| 0.01 | 0.0364 | 0.0281 | **0.0369** | 0.0535 |
| 0.005 | 0.0460 | 0.0312 | 0.0469 | 0.0659 |
| 0.001 | 0.0812 | **0.0375** | 0.0759 | 0.1017 |

**Reading the table.**

- **At q = 0.05**, all three methods agree (~1.8%). Body of the distribution; nothing surprising.
- **At q = 0.01**, Gaussian under-estimates dramatically (2.81% vs Historical 3.64%, EVT 3.69%). The Ch5 §3 fat-tail premium restated parametrically.
- **At q = 0.001**: Historical 8.12%, Gaussian 3.75%, **EVT 7.59%**. Gaussian is the clear under-estimator (less than half the right answer); **EVT and Historical roughly agree because *this 20y window contains real fat-tail events* (2008, 2020) that pin down the empirical 0.1% quantile.**

In a window *without* such events (e.g., a 20y window of 1985-2005 not including 1987's Black Monday), Historical at q=0.001 would systematically under-estimate (no observations to draw from), while EVT would still extrapolate via the GPD parametric form. **The EVT value-add is most visible when extreme observations are absent from the sample**, not when they're already there.

### 4.3 Honest framing — EVT is also uncertain

The notebook bootstraps EVT-VaR(0.001) with 200 resamples:

| Quantity | Value |
|---|---|
| Point estimate | 0.0759 |
| 95% CI | (0.0629, 0.0909) |
| CI width / point | ≈ 37% |

**EVT lets you write a number where Historical might not (in windows without extreme events) and Gaussian is wrong, but the number's CI is wide.** Report the CI honestly; don't claim more precision than the data supports.

## 5. Tail dependence coefficient — joint extremes

Joint extreme behavior — *do bad days line up across assets?* — needs a dependence measure that survives the truncation artifact that bit Ch3's conditional Pearson correlation. Tail dependence is that measure.

### 5.1 Definition

In English first: **λ<sub>U</sub> is the probability that one variable is in its upper tail given that the other is.** As we push the threshold to the extreme (q → 1), this conditional probability either survives at a positive number (real tail dependence) or shrinks to zero (asymptotic tail independence). The formal limit:

> λ<sub>U</sub> = lim<sub>q→1</sub> P( Y > F<sub>Y</sub><sup>−1</sup>(q) | X > F<sub>X</sub><sup>−1</sup>(q) )

where:
- *q* — quantile level approaching 1 (upper tail) or 0 (lower tail).
- *F<sub>X</sub><sup>−1</sup>(q)* — the q-quantile of X.
- *λ<sub>U</sub>* ∈ [0, 1] — *upper tail dependence coefficient.* "Probability that Y is in its upper tail given that X is in its."

Lower-tail λ<sub>L</sub> is analogous with `<` replacing `>`. Range:
- λ = 0: **independent in the tail** (e.g., Gaussian variables, regardless of correlation — see §6).
- λ = 1: **comonotone in the tail**; one extreme implies the other. (**Comonotone** — perfectly co-moving; X always rises when Y does. λ = 1 means the upper tails are comonotone.)

**The Pearson conditional-correlation truncation artifact does not bite λ.** That's the whole point.

### 5.2 Empirical estimator

> λ̂<sub>U</sub>(q) = #{ X > F̂<sub>X</sub><sup>−1</sup>(q) AND Y > F̂<sub>Y</sub><sup>−1</sup>(q) } / #{ X > F̂<sub>X</sub><sup>−1</sup>(q) }

where:
- *#{ ... }* — the **count** of sample observations satisfying the condition inside the braces.
- *F̂<sub>X</sub><sup>−1</sup>(q)* — the empirical q-quantile of X (i.e., the sample-based estimate).
- numerator: count of joint exceedances; denominator: count of marginal exceedances of X.

Lower-tail estimator analogous (replace `>` with `<` and use lower quantiles).

### 5.3 The three pairs

| Pair | Pearson ρ | upper q=0.95 | upper q=0.99 | lower q=0.05 | lower q=0.01 |
|---|---|---|---|---|---|
| **SPY/TLT** | **−0.309** | **0.056** | 0.020 | **0.052** | 0.078 |
| SPY/XLF | +0.842 | 0.619 | 0.569 | **0.687** | 0.627 |
| SPY/XLK | +0.915 | 0.679 | 0.647 | **0.710** | 0.706 |

Bootstrap CI on SPY/XLF lower-λ at q=0.05: **(0.643, 0.729)** — width ≈ 0.09.

**We read the q = 0.05 column as the headline; q = 0.01 entries (e.g. SPY/TLT lower = 0.078) are noise from too few joint observations (~5) and should not be over-interpreted.**

**Reading the table.**

- **SPY/TLT is the headline.** Pearson ρ = −0.31, but **λ̂_U ≈ λ̂_L ≈ 0.05** — near-independence in *both* tails. **Bonds genuinely hedge in both directions** — TLT doesn't crash with SPY (lower-tail) and doesn't rally with SPY (upper-tail). The negative Pearson is a small *average* effect; the *tail* behaviour is much closer to independent. **This is the cleanest "Pearson and tail-λ tell different stories" example in the basket.**
- **SPY/XLF.** Pearson ρ = +0.84; **λ̂_L = 0.69 vs λ̂_U = 0.62** — directionally consistent with the well-documented 2008 archetype (financials crash with the market harder than they rally), though the 7-point gap is at the edge of sampling noise (CI half-width ≈ 0.09). Bootstrap the *difference* λ_L − λ_U for a real CI before claiming the asymmetry is statistically real. When SPY has a worst-5% day, XLF is in its worst-5% with ≈ 69% probability.
- **SPY/XLK.** Pearson ρ = +0.92; **λ̂_L = 0.71 ≈ λ̂_U = 0.68** — near-symmetric high tail dependence. *Sectors share market regime* in both directions.

### 5.4 Compared to Pearson

Pearson tells you about the body of the distribution. Tail dependence tells you about the tails specifically. **In our basket, low Pearson and low tail-λ tend to agree** (TLT's case), which is *helpful* but not guaranteed in general. **Pairs that look "uncorrelated" by Pearson can have meaningful joint-crash probability** in different baskets — and the truncation artifact in Ch3's conditional Pearson made the conditional-Pearson estimator misleading. Tail dependence avoids that trap by construction.

## 6. Copulas in one page

Build it up in four steps before naming the object.

1. Any continuous random variable X has a CDF F<sub>X</sub>.
2. If you feed X back into its own CDF, the result F<sub>X</sub>(X) is uniformly distributed on [0, 1] — this is the **probability integral transform (PIT)**.
3. Doing this to every marginal of a joint distribution strips out the marginals, leaving only the dependence structure.
4. That residual is the **copula**.

(**Joint distribution** — the probability law over the *pair* (X, Y) jointly, capturing both how X behaves alone, how Y behaves alone, AND how they move together.)

A copula is, formally, the joint distribution of two (or more) random variables after transforming each marginal to Uniform[0, 1]. It strips out marginal shape; what's left is *pure dependence*.

### 6.1 Sklar's theorem in English

**Any joint distribution decomposes into its marginals plus a copula.** Symbolically:

> F(x, y) = C( F<sub>X</sub>(x), F<sub>Y</sub>(y) )

where:
- *F(x, y)* — the **joint CDF** of (X, Y) evaluated at (x, y).
- *F<sub>X</sub>(x)*, *F<sub>Y</sub>(y)* — the **marginal CDFs** of X and Y.
- *C( · , · )* — the **copula function**: a CDF on [0, 1]² with uniform marginals that encodes the dependence structure.

The decomposition is unique when the marginals are continuous. *No proof here.*

The practical consequence: you can model the marginals (e.g., GPD for tails) *separately* from the dependence (e.g., t-copula for joint behavior) and combine them later. This is the multivariate-EVT workhorse construction in production.

### 6.2 Three named copulas

| Copula | Tail dependence | Use |
|---|---|---|
| **Gaussian** (induced by multivariate normal) | λ<sub>U</sub> = λ<sub>L</sub> = 0 *regardless of correlation* | The textbook default; *the* assumption behind the 2008 CDO model failures. |
| **t-copula** (multivariate-t) | non-zero in both tails; symmetric | Heavier-tailed alternative to Gaussian. Standard in modern multivariate-EVT. |
| **Clayton** | non-zero lower-tail; zero upper-tail | Asymmetric; sometimes used for credit defaults. |

**The Gaussian-copula tail-dependence-zero result is non-obvious and important.** Two random variables generated as marginals of a bivariate normal with correlation ρ < 1 have *zero* probability of joint extreme moves in the limit q → 1. The marginals can be heavy-tailed (you can fit them however you want), but the *dependence structure* given by the Gaussian copula has no tail.

**Why?** As the threshold q → 1, the bivariate-normal isodensity contours along the diagonal grow at the *same rate* as the marginal tails. The conditional probability of a co-extreme degrades to zero. Heavy-tailed marginals don't fix this because the *coupling* is still Gaussian — once you transform back to uniform via PIT, you're left with the same thin-tailed dependence.

### 6.3 The 2008 CDO collapse in one paragraph

In 2000, David X. Li published a Gaussian-copula model for pricing **collateralized debt obligations** (CDOs — bundles of mortgage loans sliced into seniority levels called **tranches**: a senior **AAA** slice paid first, junior slices paid last and absorbed losses first). The model became Wall Street's standard for valuing the AAA tranches of **subprime**-mortgage CDOs (subprime — mortgages issued to borrowers with poor credit, especially common in the 2003-2007 US housing boom). At its peak in 2007, the CDO market exceeded **$1.4 trillion**. The Gaussian copula said: even with high correlation between the underlying loans, the *joint* probability of catastrophic co-default was vanishingly small — because the Gaussian copula has λ<sub>L</sub> = 0 regardless of ρ. When subprime defaults clustered in 2007-08 (housing prices fell across multiple regions simultaneously), the AAA tranches paid out cents on the dollar instead of par. **The model didn't see crashes coming because, mathematically, it couldn't — the Gaussian-copula tail-dependence-zero result *was* the load-bearing failure.**

This is the canonical "tail dependence matters" story. Every multivariate model with a "single correlation parameter" inherits the Gaussian-copula tail-dependence-zero implicit assumption unless explicitly stated otherwise.

### 6.4 Where to go from here

This chapter does not fit a copula. §5 already gave the practical empirical estimator we need — λ̂<sub>U/L</sub>(q) — without the formal-copula machinery. Fitting Gaussian/t/Clayton copulas, comparing them via likelihood, and bootstrap-stress-testing the comparison is post-graduate territory. The Python `copulas` library and the academic references therein are the entry points.

## 7. Limits — five caveats

**1. Sample size.** With n<sub>u</sub> ≈ 250 exceedances, the 95% CI on ξ̂ is wide. The deepest tail is *always* under-sampled.

**2. Threshold sensitivity.** GPD parameters change with *u*; the §3.3 sensitivity table shows by how much. There's no objectively-right threshold — the MRL plot is a guide, not a proof.

**3. i.i.d. violation.** GPD fits assume i.i.d. exceedances; vol clustering breaks this. §3.4's GARCH-residual fix (FHS) is the standard production response.

**4. Model risk.** GPD is a *limit* model; real distributions only converge in the limit. At finite samples, the actual tail may not be precisely GPD-shaped.

**5. Extrapolation is not extrapolation-proof.** EVT-VaR at q = 0.001 is *less* certain than at q = 0.01, even with the parametric model. The bootstrap CI on EVT-VaR(0.001) is wide (~37% of point estimate). **The model lets you write a number; the number's CI is wide.**

## 8. What we just learned

- **EVT (univariate, POT, GPD)** — model the tail of one asset's distribution above a chosen threshold. ξ̂ controls heaviness; ξ̂ > 0 is heavy.
- **EVT-VaR and EVT-ES** — extrapolate to deep quantiles where Historical can't and Gaussian is wrong. Gaussian is the clear under-estimator at q ≤ 0.01; the EVT value-add is most visible in windows without explicit extreme events.
- **Tail dependence coefficient** — empirical, copula-implicit, survives the truncation artifact that bit Ch3's conditional Pearson ρ. **SPY/TLT shows the cleanest divergence**: Pearson ρ = −0.31 but tail-λ ≈ 0.05 in both directions.
- **Copulas (named only)** — the formal "marginals + dependence" decomposition via the **probability integral transform**. Gaussian-copula vs t-copula has non-trivial tail-dependence consequences (the 2008 CDO story).
- **FHS** (filtered historical simulation) — GARCH-σ + EVT-tail. The production-grade combination. ξ̂ on standardised residuals is much smaller than on raw returns; today's FHS-VaR scales with today's σ_T.

## 9. So what?

**Decision rules:**

- **Don't use Gaussian VaR for tail-event risk management.** It systematically under-estimates by ~23% at q = 0.01 and ~54% at q = 0.001 on this 20y SPY window.
- **Use Historical for moderate quantiles, EVT for deep ones.** Historical is fine at q = 0.05; switch above. At q = 0.001, EVT extrapolates where Historical may have only a handful of observations.
- **Pair EVT with GARCH residuals when possible.** Cleaner i.i.d. assumption. *Filtered historical simulation* is the production-grade combination.
- **Audit tail dependence between any "uncorrelated" assets.** Ch3's truncation artifact means low conditional ρ does *not* imply low joint-crash probability — though the SPY/TLT case in this basket happens to show that low Pearson and low tail-λ agree. *Don't assume.*
- **Be skeptical of any joint-distribution model that uses a single correlation parameter.** It's an implicit Gaussian-copula assumption with zero tail dependence.

**What this chapter can't yet tell you:**

- How tail behaviour evolves through time. Stretch — partly covered in Exercise 4 (FHS).
- How to construct portfolios that explicitly limit tail risk. Out of scope; revisits Ch6 with a tail-risk constraint as a future stretch chapter.
- How to test whether realised crashes match GPD predictions out-of-sample. **Ch13** (with very long samples).
- How tail risk interacts with leverage, liquidity, and crowded positioning. **Future Ch14.**

## 10. Up next — Part 4 complete

**Chapter 11 — Strategy Taxonomy.** Chapters 1-10 built the *measurement* toolkit: returns, vol, correlations, expected returns, risk metrics, portfolio construction, regression, factor models, time-varying second moments, and tail risk. **Chapter 10 ends Part 4 (Modeling Returns); Chapter 11 begins Part 5 — Strategy Building.** What kinds of trading strategies are there? Where do their edges come from? How do you sort the genuinely-different from the cosmetically-different? The measurement toolkit is the lens; strategy taxonomy is what you point it at.

### Capstone reflection — what you can answer now that you couldn't at Ch1

A short list of questions the reader could not answer at Ch1 that they can answer now:

1. **How heavy is SPY's tail in a single number?** ξ̂ ≈ +0.19 — Ch10 §3.2.
2. **Are SPY/TLT really hedges in both tails or just on average?** Yes, both — λ̂<sub>U</sub> ≈ λ̂<sub>L</sub> ≈ 0.05 (Ch10 §5).
3. **How wrong is constant-σ VaR in stress?** GARCH widens VaR materially when σ̂<sub>t</sub> rises — Ch9 §5.2.
4. **Does diversifying across sectors actually reduce factor risk?** Only the *idiosyncratic* part — factor exposures sum, not cancel (Ch8 §5).
5. **Can I trust a regression with t = 2.1?** Not on non-stationary data — Ch7 §6.3 spurious-walk drill.
6. **What's the standard error on my Sharpe ratio?** Ch5 §4.3 — non-trivial; the headline number has wide CI.
7. **Why does single-correlation modeling miss tail risk?** Gaussian-copula tail-dependence is zero by construction (Ch10 §6.2).

## Key Terms

| Term | Definition |
|---|---|
| **Extreme Value Theory (EVT)** | Statistical theory of tail behavior; underpins POT and BM. |
| **Block maxima (BM)** (named) | EVT flavor: take the worst observation in each non-overlapping block, fit GEV. |
| **Peaks over threshold (POT)** | EVT flavor: pick u, fit GPD to exceedances. Used throughout Ch10. |
| **Generalized Pareto distribution (GPD)** | Two-parameter (ξ, σ) tail-model distribution. |
| **Shape parameter ξ** | GPD's tail-heaviness parameter; ξ > 0 = heavy, ξ = 0 = exponential, ξ < 0 = bounded. |
| **Scale parameter σ** | GPD's spread parameter. |
| **Threshold u** | The cutoff above which exceedances are modelled by GPD. |
| **Mean residual life plot** | Plot of mean exceedance vs threshold; used to pick u. |
| **EVT-VaR** | VaR computed from the GPD parametric form; extrapolates beyond observed losses. |
| **EVT-ES** | Expected shortfall from the GPD form. |
| **Tail dependence coefficient** | λ<sub>U</sub>, λ<sub>L</sub> ∈ [0, 1]; conditional probability of joint extreme. |
| **Copula** | Joint distribution after marginal-to-uniform transform; pure dependence structure. |
| **Sklar's theorem** (named) | Any joint distribution = marginals + copula. |
| **Gaussian copula** | Induced by multivariate normal; **zero tail dependence regardless of ρ**. |
| **t-copula** | Multivariate-t-induced; non-zero symmetric tail dependence. |
| **Clayton copula** | Asymmetric; non-zero lower-tail, zero upper-tail. |
| **Filtered historical simulation (FHS)** | GARCH-σ + EVT-tail; production-grade tail VaR. |
| **Q-Q plot** | Quantile-quantile plot; if empirical points lie on the diagonal, the data follows the proposed distribution (Ch2 §1.2). |
| **Memoryless** | Once you exceed a threshold, how much further you go is independent of how far you already went; the exponential is the only continuous memoryless distribution. |
| **Pareto** | The prototypical heavy-tailed distribution; probability falls off as a power. "Pareto-like" tails decay polynomially, not exponentially. |
| **Comonotone** | Perfectly co-moving; X always rises when Y does. λ = 1 means the tails are comonotone. |
| **i.i.d.** | Independent and identically distributed; every observation drawn the same way, no carryover from past values. |
| **Joint distribution** | The probability law over the pair (X, Y) jointly — how X behaves alone, how Y behaves alone, AND how they co-move. |
| **Probability integral transform (PIT)** | F<sub>X</sub>(X) is Uniform[0, 1]; the trick that strips marginals to leave the copula. |
| **CDO** | Collateralized debt obligation — a bundle of loans sliced into seniority levels (tranches). |
| **Tranche** | A seniority slice of a CDO; senior tranches paid first, junior tranches absorb losses first. |
| **AAA tranche** | The senior, "highest-credit-quality" slice of a CDO — the slice that mathematically depended on tail-dependence-zero in the 2008 model. |
| **Subprime** | Mortgages issued to borrowers with poor credit; common in the 2003-2007 US housing boom. |

## Exercises

Try these in fresh cells in the companion notebook. Solutions are not provided — the goal is to consolidate the chapter's machinery on slightly different inputs.

1. **GPD on a different asset.** Fit POT-GPD on TLT 20y losses. Pick the threshold using a mean-residual-life plot. Compare ξ̂ to SPY's. Are bond losses heavier-tailed than equity over this window? What does the 2022 rates regime contribute to the shape?

2. **Threshold sensitivity drill.** Refit SPY's GPD at u = 80th, 90th, 95th, 97.5th, 99th percentiles. Plot ξ̂ vs threshold; identify the stable range. What would the answer have been if you had picked u = 80th percentile? What would have gone wrong at u = 99th?

3. **Tail dependence on the full basket.** Compute λ̂<sub>L</sub>(q = 0.05) for every pair in the 8-asset basket. Produce a heatmap. Compare to the Ch3 Pearson correlation heatmap. Which pairs look "uncorrelated" by Pearson but have meaningful lower-tail dependence? Which pairs agree across the two measures?

4. *(stretch)* **GARCH-EVT (FHS) on SPY.** Refit Ch9 GARCH; standardise residuals; refit GPD on residuals; reconstruct VaR(0.001) by combining today's σ̂<sub>T</sub> with the residual-tail extrapolation. How does the ratio FHS-VaR / raw-EVT-VaR depend on whether today's σ̂_T is above or below the long-run average?
