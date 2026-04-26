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
- **All eight together** — appears in the master correlation matrix and the calm-vs-crisis heatmap **diptych** (a *diptych* is just a two-panel side-by-side image — borrowed from art-history; we're putting two heatmaps next to each other).

After the setup cells run, expect:
- An 8-column return panel with **~5,030 daily observations** spanning ~20 years.
- Annualized volatility per asset roughly: SPY ~19%, TLT ~15%, GLD ~18%, sector ETFs in the 17–30% range (XLF and XLE highest at ~30%).

The setup section also introduces the **covariance matrix Σ** as the natural N-asset generalization of σ from Chapter 2: a square *N* × *N* matrix where the diagonal is each asset's variance and the off-diagonals are pairwise covariances. We'll spend the rest of the chapter doing useful things with this matrix.

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

For our 8-ticker basket over 20 years of daily log returns:
- **Sector ETFs** correlate strongly with SPY (ρ in the 0.65–0.92 range) and with each other (0.5–0.7). They're all flavors of US equity risk.
- **TLT** has *moderately negative* correlations with SPY and the equity sectors (ρ ≈ −0.25 to −0.33). Bonds were a real hedge through most of the 20-year window — when stocks fell, Treasuries rallied.
- **GLD** has uniformly low correlations with everything else — closer to genuinely independent.

(That long-run negative SPY/TLT correlation isn't a constant — Part III shows it has a regime structure that the average hides.)

### 2.2 What different correlations look like

The notebook plots three scatter plots side by side, all on the same axis scale:

- **SPY vs XLK** (*ρ* ≈ +0.92) — a tight diagonal cloud, these are nearly the same asset.
- **SPY vs XLU** (*ρ* ≈ +0.65) — a clearly correlated cloud, but visibly looser.
- **SPY vs TLT** (*ρ* ≈ −0.31) — a slight *downward* tilt; many days look independent, but on average when SPY is up TLT is down a bit and vice-versa. The upper-left quadrant (stocks-down-bonds-up days) is well populated — that's the bond hedge in pictures.

The "correlation captures *linear* co-movement" framing is literal — *ρ* ≈ +1 means a positive-slope diagonal cloud, *ρ* ≈ −1 means a negative-slope diagonal, *ρ* ≈ 0 means no preferred line.

### 2.3 What this means with $100k

Imagine you hold $100k of SPY and want to "diversify" by adding another $100k of something else. Three candidate add-ons (assuming for simplicity all three have the same vol as SPY — TLT's actual lower vol would help even further):

- **Add $100k of XLK** (*ρ* ≈ +0.92 with SPY) — combined $200k position has roughly **1.96×** the dollar risk of the original $100k SPY. Almost no diversification benefit; you doubled exposure, not safety.
- **Add $100k of XLU** (*ρ* ≈ +0.65) — combined position has roughly **1.82×** the original risk. Better, but still mostly the same risk.
- **Add $100k of TLT** (*ρ* ≈ −0.31) — combined position has only **1.18×** the original risk. Negative correlation is *better* than uncorrelated for risk reduction — the cross-term in the variance formula now *subtracts* from total variance. The cleanest example of correlation working in your favor.

The 1.96×, 1.82×, 1.18× factors come from the two-asset variance formula in §3.1 — which we'll prove next.

## 3. Part II — Aggregation: portfolio variance and the diversification math

Pairs are the simplest case. Real portfolios have many positions. Going from "two correlations" to "many" is where the matrix Σ from §1 starts paying for itself.

### 3.1 Two-asset portfolio variance

Hold *w<sub>X</sub>* fraction of asset X and *w<sub>Y</sub>* = 1 − *w<sub>X</sub>* of asset Y. The portfolio's daily return is *r<sub>p</sub>* = *w<sub>X</sub> r<sub>X</sub>* + *w<sub>Y</sub> r<sub>Y</sub>*. Its variance is:

> *σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

where:
- *w<sub>X</sub>*, *w<sub>Y</sub>* — the **portfolio weights** (must sum to 1 for a fully-invested long-only portfolio).
- *σ<sub>X</sub>*, *σ<sub>Y</sub>* — individual asset standard deviations of returns. The formula is **frequency-consistent**: plug in daily σ's and you get a daily σ<sub>p</sub> out; plug in annualized σ's (i.e. daily σ × √252) and you get an annualized σ<sub>p</sub> out. Both σ's must be at the same frequency. The example below plugs in annualized values so the answer comes out in annualized terms directly — the convention used throughout this chapter.
- *ρ* — the pairwise correlation between *X* and *Y*. Unitless; **the same number at any frequency**, so no scaling needed.
- *σ<sub>p</sub>²* — the variance of the portfolio's return, in whatever frequency the inputs were.

Three terms: two **own-variance** terms (each weighted by *w²*) plus the **cross-term** (the diversification engine). When *ρ* < 1, the cross-term shrinks total variance below the weighted average. When *ρ* < 0, it shrinks variance further still — the cross-term goes negative. When *ρ* = 1, no diversification; when *ρ* = −1, perfect hedging is possible.

Walk the formula end-to-end for a 50/50 SPY/TLT portfolio. Every number below comes from the 20-year daily-log-return panel computed in §1; standard deviations are annualized so the answer pops out in annualized terms directly.

**Inputs:**

| Symbol | Meaning | Value |
| --- | --- | ---: |
| *w<sub>X</sub>* | SPY weight | **0.5** |
| *w<sub>Y</sub>* | TLT weight | **0.5** |
| *σ<sub>X</sub>* | SPY annualized vol | **0.1945** (19.45%) |
| *σ<sub>Y</sub>* | TLT annualized vol | **0.1491** (14.91%) |
| *ρ* | SPY/TLT correlation | **−0.309** |

**Plug into the formula:**

> *σ<sub>p</sub>²* = *w<sub>X</sub>²σ<sub>X</sub>²* + *w<sub>Y</sub>²σ<sub>Y</sub>²* + 2 *w<sub>X</sub>w<sub>Y</sub>σ<sub>X</sub>σ<sub>Y</sub>ρ*
>
> = (0.5)²·(0.1945)² + (0.5)²·(0.1491)² + 2·(0.5)·(0.5)·(0.1945)·(0.1491)·(−0.309)
>
> = 0.25·0.03783 + 0.25·0.02223 + 0.5·0.02901·(−0.309)
>
> = 0.00946 + 0.00556 + (−0.00448)
>
> = **0.01054**

> *σ<sub>p</sub>* = √0.01054 = **0.1027 ≈ 10.3% annualized**

**Reading the three terms:**

| Term | Value | Meaning |
| --- | ---: | --- |
| *w<sub>X</sub>²σ<sub>X</sub>²* | +0.00946 | SPY's own variance contribution |
| *w<sub>Y</sub>²σ<sub>Y</sub>²* | +0.00556 | TLT's own variance contribution |
| 2 *w<sub>X</sub>w<sub>Y</sub>σ<sub>X</sub>σ<sub>Y</sub>ρ* | **−0.00448** | the cross-term — *negative* because *ρ* < 0 |

The cross-term is the **diversification benefit**: it *subtracts* from the total variance. That's why 50/50 SPY/TLT vol comes out to **10.3%** rather than the **17.2%** weighted average of the two individual vols (`0.5 × 19.45% + 0.5 × 14.91% = 17.18%`). About 7 percentage points of risk reduction, paid for entirely by the negative correlation.

<details>
<summary><b>The math, if you want it: deriving the two-asset variance</b></summary>

Var(*aX* + *bY*) = *a²* Var(*X*) + *b²* Var(*Y*) + 2*ab* Cov(*X*, *Y*).

Plug in *a* = *w<sub>X</sub>*, *b* = *w<sub>Y</sub>*, Var(*X*) = *σ<sub>X</sub>²*, Cov(*X*, *Y*) = *ρ σ<sub>X</sub> σ<sub>Y</sub>* (rearranged from the correlation definition):

*σ<sub>p</sub>²* = *w<sub>X</sub>² σ<sub>X</sub>²* + *w<sub>Y</sub>² σ<sub>Y</sub>²* + 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*

The variance-of-a-sum identity itself comes from expanding *E*[((*aX* + *bY*) − *E*[*aX* + *bY*])²]: the cross-term is 2*ab E*[(*X* − *μ<sub>X</sub>*)(*Y* − *μ<sub>Y</sub>*)] = 2*ab* Cov(*X*, *Y*) — exactly the *E*[·] machinery from Ch2 §2.2.

</details>

### 3.2 The correlation matrix as a heatmap

The 8×8 correlation matrix from §2 has structure that's easier to see as a heatmap than as a table of numbers. The notebook renders it. Three visual blocks:

- **Sector ETFs (XLK / XLF / XLE / XLV / XLU)** form a high-correlation cluster (ρ in the 0.5–0.7 range internally, and 0.65–0.92 with SPY). All flavors of US equity risk.
- **TLT row/column** is clearly *blue* — moderately negative correlations with all the equity assets. The bond-hedge story baked into the long-run average.
- **GLD row/column** is uniformly pale — correlations near zero with everything else.

This matrix is the input we feed into the portfolio-variance machinery next.

### 3.3 The diversification math empirically

The two-asset formula generalizes to *N* assets — but rather than write the formula yet, the notebook just *computes* portfolio vol as we add tickers one at a time, in a deliberate dramatic order:

`XLK → +XLF → +XLE → +XLV → +XLU → +TLT → +GLD`

Start with one sector. Add four more sectors (correlated). Then add TLT (cross-asset, decorrelated). Then add GLD. Equal weights at each step.

Reading the resulting curve from left to right:

- **N = 1 (just XLK)** — high vol, ~23% annualized. A single sector is a concentrated bet.
- **N = 2 to 5 (adding sector ETFs)** — vol drops, but each step is modest. Adding correlated names doesn't help much.
- **N = 6 (adding TLT)** — sharp drop. TLT is *negatively* correlated with the equity basket, so the cross-term in the variance formula works hard for the first time.
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

The notebook tabulates several portfolios. Computed numbers from the actual data:

| Portfolio | Annualized vol | Typical-year swing on $100k |
| --- | ---: | ---: |
| All SPY (concentrated) | 19.45% | $19,447 |
| All XLK (single sector) | 22.93% | $22,930 |
| Equal-weight 5 sectors | 19.56% | $19,561 |
| **60/40 SPY/TLT** | **11.34%** | **$11,345** |
| Equal-weight all 8 | 14.50% | $14,498 |

Two things worth pointing out:

1. **60/40 SPY/TLT is the *lowest*-vol portfolio in the table** — about $11k typical-year swing on $100k, vs $19k for all-SPY. The negative SPY/TLT correlation does the work. That's the textbook "balanced portfolio" earning its reputation.
2. **Equal-weight all 8 has *higher* vol than 60/40** ($14.5k vs $11.3k) — even though it has more assets. The reason: 5/8 of the basket is concentrated in high-vol US equity sectors (XLF and XLE both run ~30% vol). Naive equal-weighting *over-allocates* to the volatile names. Better weighting schemes (risk parity, mean-variance optimization) attempt to fix this — deferred to a later chapter.

Real portfolio construction trades off return (which favors equity-heavy) against risk (which favors diversification across asset classes — *and* thoughtful weighting). We'll formalize the return-vs-risk tradeoff with the **Sharpe ratio** in Chapter 4.

## 4. Part III — Regime / crisis correlation (the empirical wrinkle)

Parts I and II used a **single** correlation number per pair — the long-run average over 20 years. Same shape of error Ch1 made and Ch2 corrected: real correlations vary over time, and the variation has a particular character. They cluster regime-by-regime, and they shift during crashes.

### 4.1 Rolling correlation — the bond hedge unhedged itself

Compute SPY/TLT correlation in a 60-day rolling window through history. Same window length as Ch2's rolling vol, for the same noise-vs-lag balance reason. The notebook plots the resulting time series.

The story it tells:
- **2007–2019:** sustained negative correlation. TLT genuinely *hedged* SPY — when stocks fell, Treasuries rallied. This is the regime that built the reputation of the 60/40 portfolio (and is what the long-run −0.31 average mostly reflects).
- **March 2020:** a brief sharp positive spike. During the COVID liquidity crisis everything sold off together — forced deleveraging means even safe assets get sold.
- **2022 onward:** sustained positive correlation. Both stocks and bonds fell together as rates rose.

**The "bond hedge" that worked for 15 years stopped working — and the regime change happened in months, not years.** The flat line of the static analysis is an *average over genuinely different worlds*.

### 4.2 Conditional correlation — what happens on bad days?

A static correlation answers "on a typical day, do these move together?" A more interesting question for risk management: *on the worst days,* do these move together?

The notebook computes correlations conditional on the bottom 5% of SPY days — about 250 days in 20 years, the conventional VaR-territory threshold — and bars them next to the unconditional ("all days") correlations.

The picture is more nuanced than a clean "everything correlates in stress":

- **TLT** (the bond hedge): all-days *ρ* = −0.31, worst-5%-days *ρ* = −0.23. Still negative but **less so** — TLT's diversification power *weakens* exactly when SPY is in pain. The headline finding for the bond-hedge story.
- **GLD**: roughly unchanged near zero — gold is genuinely close to independent.
- **Sector ETFs (XLU, XLE)**: textbook lift — already-positive correlations rise further.
- **High-correlation sectors (XLK, XLF, XLV)**: *appear* to drop in conditional correlation. This is largely a **statistical artifact** — conditioning on the bottom 5% of SPY truncates SPY's variance, which mechanically shrinks any Pearson correlation involving it. Economic content is small.

### 4.3 Calm vs crisis — the heatmap diptych

The cleaner picture lives in the calm-vs-crisis comparison. Two snapshots of the full 8×8 correlation matrix:
- **Calm:** all of 2017 (the lowest-vol full year in the window).
- **Crisis:** March–June 2020 (the COVID drawdown and aftermath).

In the calm matrix, structure is visible: sector ETFs cluster, TLT and GLD are independent, off-diagonal entries span a wide range. In the crisis matrix, almost every cell sits in the 0.6–0.95 range — the matrix has gone uniformly red. **In a panic, all bets become a single bet.**

Computing on entire windows (rather than conditioning on a subset of days) avoids the truncation artifact in §4.2 and shows the regime shift in full color.

### 4.4 What this means

Real correlation isn't a number — it's a *time-series of matrices*. The single *ρ* values from Parts I and II are useful summaries the way a single annualized vol from Ch1 is useful: they tell you the long-run average. They don't tell you what happens on the worst day, or what regime you're in right now.

Two specific deferred topics named here:

- **DCC-GARCH** (Dynamic Conditional Correlation) — formal time-series model of how correlations evolve. Same flavor as Ch2's GARCH (which models time-varying volatility), now applied to correlations. Future chapter.
- **Tail dependence and copulas** — formal models of the "everything correlates in tails" phenomenon. Much later in the curriculum (alongside EVT).

Neither is required for the practical portfolio reasoning we've done in this chapter. Both exist for readers who want the formal modeling tools.

## 5. What we just learned (recap by concept-flavor)

We named five flavors of correlation risk in the opening. Here's what we found, organized by flavor.

### Pairwise correlation
- Pearson correlation (*ρ*) is normalized covariance, bounded in [−1, +1], unitless and comparable across pairs.
- The same number can mean visually very different things — sector ETFs at *ρ* ≈ +0.9 are nearly the same asset; SPY/TLT at *ρ* ≈ −0.31 shows a moderate negative tilt that's almost entirely the bond-hedge effect.
- *ρ* alone doesn't capture *time* — that's Part III's job.

### Aggregation / portfolio risk
- Two-asset portfolio variance has a cross-term: 2 *w<sub>X</sub> w<sub>Y</sub> σ<sub>X</sub> σ<sub>Y</sub> ρ*. When *ρ* < 1 it shrinks total variance; when *ρ* < 0 it shrinks variance further still.
- The general formula is *σ<sub>p</sub>²* = **w**ᵀ **Σ** **w** — one matrix expression for any portfolio size.
- The marginal benefit of one more asset depends on its correlation with what you already hold. Adding correlated names dilutes; adding decorrelated or negatively-correlated names actually reduces risk.
- **More assets ≠ less risk.** Equal-weight 8 had higher vol than 60/40 because the equal-weight scheme over-allocated to high-vol sector ETFs. Weighting matters as much as breadth.
- There's a floor: when every pair shares correlation *ρ*, no number of assets can reduce *σ<sub>p</sub>²* / *σ²* below *ρ*. This is the seed of "**systematic vs idiosyncratic risk**."

### Regime / crisis correlation
- Correlations are not constant. The SPY/TLT 60-day rolling correlation has spent most of 2007–2019 negative and most of 2022 onward positive — the bond hedge famously stopped working.
- Conditioning on the worst 5% of SPY days shows the bond hedge weakening (TLT goes from −0.31 to −0.23) while genuinely-zero pairs like GLD stay roughly flat. High-correlation sectors show a numerical drop due to a truncation artifact, not an economic reversal.
- The cleanest evidence is the calm-vs-crisis heatmap diptych: 2017 has structure (sector blocks distinct, TLT and GLD independent); March–June 2020 is uniformly red — every cell in the 0.6–0.95 range. **In a panic, all bets become a single bet.**

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
| Crisis correlation | Informal name for the empirical fact that correlation *structure* changes during stress | §4 |
| Hidden factor exposure | When seemingly distinct assets share underlying drivers — deferred | §0 |
| Tail dependence | Correlations only manifest in tails of the joint distribution — deferred | §0 |

---

## Exercises

Try these in fresh cells at the bottom of the notebook:

1. **Different basket — add crypto.** Pull `BTC-USD` and `ETH-USD` and compute correlations between crypto and the 8-ticker basket. Are crypto correlations with stocks higher or lower than between stocks and bonds? Has it changed across the dataset's window?
2. **The pre-2020 vs post-2020 SPY/TLT story.** Compute SPY/TLT correlation on the 2003–2019 sub-window and the 2020–present sub-window. Two numbers, one striking gap. What changed?
3. **Conditional on TLT instead.** Repeat the §4.2 conditional-correlation exercise, but condition on the worst 5% of *TLT* days. Does the same pattern emerge, or is it asymmetric?
4. *(stretch)* **Cross-asset-class correlation matrix.** Pull six tickers spanning major asset classes — `QQQ` (large-cap tech), `IWM` (small-cap stocks), `EEM` (emerging markets), `IEF` (intermediate Treasuries), `HYG` (high-yield bonds), `DBC` (broad commodities). Compute the 6×6 correlation matrix as a heatmap. Which pairs are more correlated than you'd have guessed? Which less? *(Hint: HYG often surprises people — it's labeled "bonds" but trades like equities.)*

---

## Up next

**Chapter 4: Estimating Expected Returns.** Three chapters spent on risk; zero on return. Ch4 fills the gap. The reader leaves with two findings: (1) the historical mean as an estimator of true expected return is **brutally noisy** at any reasonable sample size, and (2) **shrinkage toward a prior** is the practitioner-grade remedy. Both findings honestly inform Chapter 5's Sharpe ratio.
