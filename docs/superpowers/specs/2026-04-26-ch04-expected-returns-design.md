# Chapter 4 — Estimating Expected Returns

**Status:** Design approved 2026-04-26
**Author chapter slot:** `04-expected-returns/`
**Predecessor:** Chapter 3 — Multiple Assets: Correlation and Diversification (`03-correlation/`)
**Successor (planned):** Chapter 5 — Risk Metrics: Drawdown, VaR, Sharpe

---

## 1. Background and motivation

Chapters 1–3 spent three chapters on the *risk* side of return analysis — volatility, fat tails, clustering, correlation, portfolio variance. Zero of those chapters addressed the equally fundamental question: *what's an asset's expected return, and how confidently can we estimate it from data?*

That gap matters now because Chapter 5 introduces the **Sharpe ratio**:

> *Sharpe* = (*E*[*r*] − *r<sub>f</sub>*) / *σ*

The denominator (volatility) was thoroughly developed in Ch2 and reused in Ch3. The numerator (*E*[*r*]) has been hand-waved: implicitly assumed to be "the historical average," with no attention to how noisy that estimator is. Building Ch5's risk-adjusted return on a hand-waved numerator would teach the reader that Sharpe is more solid than it actually is.

Chapter 4 fills the gap. It is a "pacing-gap chapter" inserted during the 2026-04-26 curriculum redesign for exactly this reason.

## 2. Goals and non-goals

### Goals

- Open with a "What we mean by expected return" framing that names four distinct flavors and signals which the chapter covers vs defers (per the established concept-before-statistic convention).
- Establish the **sample mean** as the natural estimator for long-run expected return, derive its **standard error**, and demonstrate empirically how wide the resulting confidence intervals are at realistic sample sizes.
- Demonstrate **subsample instability** — sample means computed on disjoint sub-windows of the same data vary substantially.
- Translate the noise into dollar / lived-experience terms (per the saved feedback memory): "twenty years of data, and we still can't tell a 2% asset from an 18% asset."
- Introduce **shrinkage** as the practitioner-grade remedy. Cover the linear-blend formulation explicitly, the James-Stein formulation in body + collapsible derivation.
- Demonstrate shrinkage empirically on the 8-ticker basket from Ch3.
- Brief preview of the *conditional / forecasting* flavor of expected return, with explicit pointers to Ch11–12 (strategy edge) and Ch8 (equilibrium return) where it lives.
- Recap by concept-flavor.

### Non-goals (explicitly deferred)

- **Forecasting / conditional expected return.** Predicting next period's return from features. Setup for Ch11–12 (strategy taxonomy + mechanics) and Ch8 (factor models).
- **Equilibrium / required return.** What expected return *should* be given an asset's risk and factor exposures. Setup for Ch8 (CAPM, Fama–French).
- **Bayesian shrinkage with non-flat priors / hierarchical models.** Out of scope for an introductory treatment.
- **Black-Litterman model.** Important in practice; deferred to Ch6 (portfolio construction) where it has a natural home.
- **Time-varying expected returns / regime-conditional means.** Deferred to Ch9 (time-varying models).

## 3. Narrative arc

Three-part structure:

> Chapter 1 said: returns. Chapter 2: how risky those returns are, with structure. Chapter 3: how returns co-move. **Chapter 4: the *other* half of risk-adjusted return — what's the asset's true expected return, and how confidently can we know? The honest answer turns out to be "much less confidently than the casual reader assumes," and shrinkage is the standard practitioner remedy.**

Order rationale: noise first (§2 — single asset, the punchline that drives everything), shrinkage second (§3 — multi-asset, the remedy), forecasting third (§4 — explicitly named-but-deferred). Each builds on the prior.

## 4. Data

- Same **8-ticker basket as Ch3**: SPY, TLT, GLD + 5 sector ETFs (XLK, XLF, XLE, XLV, XLU).
- 20-year window (`period="20y"`), continuity with Ch2 and Ch3.
- Log returns throughout, continuity.
- Tickers serve different roles in this chapter:
  - **SPY** carries the §2 single-asset noise demo.
  - **All eight** carry the §3 shrinkage demo (shrinkage requires multiple estimates).

## 5. Section structure

### Concept-flavors framing (before §1)

A "**What we mean by expected return**" section, mirroring Ch2 and Ch3 patterns. Names four flavors, signals which the chapter covers vs defers:

| Flavor | This chapter |
|---|---|
| Realized return (the data) | Defined briefly in §1; not an expectation, just the input. |
| Long-run / unconditional expected return | Whole chapter (§2 + §3). |
| Conditional / forecast expected return | Deferred — Ch11–12. |
| Equilibrium / required return | Deferred — Ch8. |

When the chapter says "expected return" later, it means the long-run unconditional flavor. Same disclaimer pattern as Ch2 and Ch3.

### §1. Setup and data refresh

- Imports identical to Ch3 (no new dependencies).
- Re-pull the 8-ticker panel; verify shape (~5,030 × 8).
- Compute log returns.
- Brief callback to Ch1 vocabulary (return, log return); explicit reminder that *realized* return is the data, not the expectation.
- Preview the central question: *given the data, what's our best guess for each asset's true expected return, and how sure are we?*

### §2. The naive estimator and its noise (single-asset focus)

**§2.1 Sample mean as estimator.**

> *μ̂* = (1/N) Σ<sub>i=1</sub><sup>N</sup> *r<sub>i</sub>*

`where:` legend defines each symbol with units. Critical foot-gun flag: **to annualize a daily mean, multiply by 252** (means add over time). This is *different from* the std/vol annualization rule (multiply by √252), introduced in Ch1. Don't conflate them.

**§2.2 Standard error of the mean.**

> *SE(μ̂)* = *σ* / √N

`where:` legend with units. Foot-gun: SE shrinks like √N, so quadrupling sample size only halves SE. Diminishing returns built into the formula.

Compute SPY's annualized mean and 95% CI from 20 years of data. Expected results:
- SPY annualized mean ≈ 10% (point estimate).
- Daily SE ≈ σ/√N where σ ≈ 0.0123 and N ≈ 5,030, giving SE_daily ≈ 0.000174.
- Annualized SE ≈ SE_daily × 252 ≈ 0.044 (~4.4%).
- 95% CI: 10% ± 1.96 × 4.4% ≈ **1.5% to 18.5% annualized**.

The width of that CI is the chapter's punchline.

**§2.3 Subsample stability.** Compute SPY's annualized mean over disjoint 5-year sub-windows. They'll vary by 5–10 percentage points. Reinforces §2.2 from a different angle.

**§2.4 What this means with $100k.** Concrete dollar / lived-experience framing per the concept-before-statistic memory. A reader sizing a position based on "SPY returns 10% per year" needs to know the 95% interval is roughly 1.5%–18.5% per year — on $100k that's anything from "barely outpacing T-bills" to "doubling in 4 years," and *both* are statistically consistent with the same 20 years of data.

### §3. Shrinkage — pulling estimates toward a prior (multi-asset focus)

**§3.1 Intuition.** When you have many noisy estimates, each individual estimate has high variance. If you're willing to accept a small bias toward a common prior (the cross-sectional mean, or zero), you can reduce *total* mean-squared error. This is the bias-variance tradeoff in its purest form.

**§3.2 The simplest shrinkage: linear blend.**

> *μ̂*<sub>shrink</sub> = *α · μ̂* + (1 − *α*) · *μ*<sub>prior</sub>

`where:` legend. Foot-gun: *α* is a fraction in [0, 1]; *α* = 1 means no shrinkage, *α* = 0 means everyone gets the prior. Units: same as the input mean.

Cross-sectional mean of the 8-asset basket as the typical prior choice. Sometimes zero is used (especially when long-run means aren't identifiable).

**§3.3 The James-Stein estimator.** State the formula:

> *μ̂*<sub>JS,i</sub> = *μ̂*<sub>i</sub> − *c* · (*μ̂*<sub>i</sub> − *μ̂*<sub>prior</sub>)

where *c* depends on N, K (number of assets), and σ. Body has the formula; collapsible `<details>` has the derivation and the optimality argument (Stein 1956, Efron-Morris).

**§3.4 Empirical demo.** Bar chart: raw sample means vs shrunk means for the 8 tickers. High-vol tickers (XLK, XLF, XLE) will see their estimates pulled meaningfully toward the prior; low-vol assets like TLT will move less.

**§3.5 What this means.** Practitioner fact: almost all production portfolio optimization uses shrunk expected-return estimates. Naive sample means produce wildly unstable optimal portfolios. Ch6 will demonstrate this concretely.

### §4. Forecasting preview (the conditional flavor)

Short — about half a section, no code. Three subsections:

**§4.1** The shift in framing: from *"what's the asset's long-run mean?"* (one number per asset) to *"what's its expected return *next period* given *current state*?"* (a number per asset *per time*). Different problem with different methods and different success criteria.

**§4.2** Two routes to forecasting, both explicitly deferred:
- **Regression-based** — predict returns from features (lagged returns, valuation ratios, factor exposures). Setup for Ch8.
- **Strategy-edge-based** — every trading strategy is implicitly a forecast model. Setup for Ch11–12.

**§4.3** Why this is a separate chapter (or several): the methods are different, the success criteria are different (low SE vs information ratio), the data needs are different.

### §5. What we just learned (recap by concept-flavor)

Three subsections:

- **Long-run unconditional return** — sample-mean noise (wide CIs at realistic sample sizes) and shrinkage as the practitioner remedy. The chapter's actual content.
- **Conditional / forecast return** — exists, lives in Ch11–12.
- **Equilibrium / required return** — exists, lives in Ch8.

### §6. Up next + Key Terms + Exercises

**Up next:** Chapter 5 — Risk Metrics: drawdown, VaR, Sharpe. Now that Ch4 has put honest error bars on the numerator of Sharpe, Ch5 can build the metric without overclaiming.

**Key Terms** table covering all new vocabulary.

**Exercises** (3–4):
1. **Different ticker.** Re-compute the 95% CI for the annualized mean of `BTC-USD`. Crypto has higher vol and a shorter history; how do those two effects combine in the SE formula?
2. **Calmest vs stormiest sub-window.** Compute SPY's annualized mean on its calmest 5-year window vs its stormiest. Does the *point estimate* shift more than the SE accommodates?
3. **Shrinkage sensitivity.** Re-do the §3.4 demo with the prior set to *zero* instead of the cross-sectional mean. Which assets move more? Why?
4. *(stretch)* **Implied confidence on Sharpe.** Take SPY's mean and SE from §2.2 and SPY's vol from Ch2. Compute a rough 95% CI on SPY's Sharpe ratio. (Hint: the noise in the numerator dominates.)

## 6. New terminology

| Term | Brief meaning |
|---|---|
| Realized return | What actually happened (the data); not an expectation. |
| Sample mean (*μ̂*) | The arithmetic average of a finite sample; the natural estimator of the population mean. |
| Estimator | A function of data used to guess an unknown population quantity. |
| Standard error (SE) | The standard deviation of an estimator's sampling distribution. |
| Confidence interval | A range around an estimate that contains the true value with stated probability under repeated sampling. |
| t-statistic | An estimate divided by its standard error. |
| Bias | The expected difference between an estimator and the true value. |
| Bias-variance tradeoff | Accepting a small bias to reduce overall mean-squared error. |
| Shrinkage | Pulling a noisy estimate toward a prior (typically the cross-sectional mean or zero). |
| Prior | The target value toward which a shrinkage estimator pulls. |
| Cross-sectional mean | The mean across assets at a point in time (vs the time-series mean of one asset). |
| James-Stein estimator | A specific shrinkage estimator that strictly dominates the sample mean in MSE for K ≥ 3 assets. |
| Signal-to-noise ratio (SNR) | The ratio of mean to standard error; measures how confidently we can distinguish an estimate from zero. |
| Conditional / forecast expected return | Named-but-deferred flavor; expected return given current state. |
| Equilibrium / required return | Named-but-deferred flavor; expected return implied by an asset's risk. |

## 7. New formulas (each with `where:` legend + units + foot-gun flag)

1. **Sample mean** — *μ̂* = (1/N) Σ *r<sub>i</sub>*. Units: same as inputs. Foot-gun: annualize by × 252 (means add); not √252.
2. **Standard error of the mean** — *SE(μ̂)* = *σ* / √N. Foot-gun: SE shrinks like √N (quadrupling N only halves SE).
3. **95% confidence interval** — *μ̂* ± 1.96 · *SE*. Foot-gun: assumes approximate normality of the sample mean (CLT-justified for large N even if individual returns are fat-tailed).
4. **Linear shrinkage estimator** — *μ̂*<sub>shrink</sub> = *α · μ̂* + (1 − *α*) · *μ*<sub>prior</sub>. Foot-gun: *α* is a fraction in [0, 1].
5. **James-Stein estimator** — formula in body, derivation in collapsible details.

Heavy derivations (James-Stein optimality, bias-variance decomposition) live in `<details>` blocks.

## 8. Code structure and dependencies

- `04-expected-returns/README.md` — chapter prose, end-of-chapter Key Terms.
- `04-expected-returns/lesson.ipynb` — runnable companion.
- Append new entries to root `glossary.md` (alphabetized, tagged Ch. 4).

### Dependencies

**No new packages.** numpy/pandas/matplotlib/yfinance/scipy already cover everything. `scipy.stats.norm` for the 1.96 quantile.

### No new helpers / no shared module

Each chapter remains self-contained.

## 9. Conventions to follow

Inherited from prior chapters (see `MEMORY.md` feedback memories):

- Define every domain term on first use (inline blockquote gloss).
- Define every formula symbol via a `where:` legend, **with units / frequency stated explicitly and arithmetic foot-guns flagged** (per the 2026-04-26 update to the formula-symbols memory).
- Inline glosses + chapter Key Terms table + glossary append.
- Notebook cells get just-in-time micro-explanations; deeper "why" lives in the README.
- Heavier math goes in collapsible `<details>` blocks.
- HTML subscripts (`<sub>`) for formula rendering.
- **Concept-before-statistic:** opening "What we mean by X" framing; concrete dollar / lived-experience translations after every major statistical finding; recap organized by concept-flavor.

## 10. Cross-chapter promises honored

- The implicit "before Sharpe, you need honest treatment of return estimation" prerequisite from the curriculum redesign.
- Sets up Ch5 (Sharpe needs both inputs).
- Sets up Ch6 (portfolio optimization fragility under naive sample means; shrinkage as remedy).
- Sets up Ch8 (equilibrium return as a deferred flavor named here).
- Sets up Ch11–12 (forecasting / strategy edge as a deferred flavor named here).

## 11. Cross-chapter promises NOT honored (with rationale)

- **Black-Litterman** — important in practice; deferred to Ch6 where it has a natural home alongside portfolio optimization.
- **Time-varying / regime-conditional means** — deferred to Ch9 alongside GARCH.
- **Bayesian shrinkage with non-flat priors** — out of scope for an introductory treatment.

## 12. Edits required to existing files (Ch3 + root)

- Ch3 README "Up next" — currently points to "Chapter 4 risk metrics." Reword to point to Ch4 (expected returns) and preview the noise/shrinkage arc.
- Top-level `README.md` curriculum table — Ch4 row swapped from "_coming next_" to its full title with a link, in the same format as Ch1-3 rows.

## 13. Open questions

None at design-approval time. Likely small implementation choices (whether to use scipy.stats.norm.ppf(0.975) for 1.96 or hard-code; whether the §3.4 bar chart sorts assets by vol or alphabetically; how many sub-windows in §2.3) — all routine.
