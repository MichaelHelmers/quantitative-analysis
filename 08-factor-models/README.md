# Chapter 8 — Factor Models: CAPM and Fama-French

> Chapter 7 turned regression into a tool with three jobs and many pitfalls. Chapter 8 puts that tool to work on the question Ch3 §3.5 deferred: *what's actually driving co-movement in our 8-asset basket, and how much "diversification" is real?* The answer in three words: **β, α, factors.**

The chapter is the most "real-world finance" the curriculum has been so far. β is the single most-cited number in equity research; α is the single most-debated number in active management. Both deserve careful introduction with concrete dollar examples — and a careful audit of how often the headline numbers are statistically distinguishable from zero.

### Reader takeaway

Most of any individual asset's return is explained by **a few common factors** that everyone is exposed to. *Beta* says how much you are exposed to each factor. *Alpha* is whatever's left after accounting for them — a candidate for "real skill" that almost always shrinks toward zero once you measure it carefully, and tends to clear the statistical-significance bar more often on the *negative* side than the positive.

### Learning objectives

After this chapter you can:

1. Run a CAPM regression on any asset's daily returns and read β, α, R², t-statistics correctly.
2. Explain why **a "diversified" 8-asset basket can still have β ≈ 0.7** (Ch3's deferred lesson).
3. Distinguish single-factor (CAPM) from multi-factor (FF3, FF5) models and say what each adds.
4. Read α̂ skeptically — name three reasons a positive α̂ may not be real (small sample, missing factor, data-mining).
5. Understand the difference between **statistical α** (regression intercept) and **economic α** (after costs, capacity, slippage).

## What we mean by "a factor model"

A factor model decomposes any asset's return into:

> total return = (β to factor 1) × (factor 1's return) + (β to factor 2) × (factor 2's return) + ... + α + ε

The flavors used in this chapter:

| Model | What it explains | Inputs |
|---|---|---|
| **CAPM** — single-factor | Market exposure only | (R<sub>i</sub> − r<sub>f</sub>), Mkt-RF |
| **Fama-French 3 (FF3)** | Market + size + value | + SMB, HML |
| **Fama-French 5 (FF5)** | + profitability + investment | + RMW, CMA |

Factor models are *just more regressors* than CAPM; the math is exactly Ch7's multiple regression.

## 1. Setup

Same 8-ticker basket as Ch3-7. **Fama-French factor data** comes from Ken French's data library at Dartmouth. Ken French (Dartmouth, longtime Fama collaborator) maintains the canonical implementation — when academic papers say "we use Fama-French factors," they almost always mean these CSVs. The notebook downloads the daily-frequency zips directly from the Dartmouth FTP and caches them under `08-factor-models/data/`.

> **Note on `pandas-datareader`.** The `pandas_datareader.data.DataReader(..., 'famafrench')` route is the textbook way to pull this data, but it's broken under pandas 3.0 — the `deprecate_kwarg` API the package depends on changed signature. The chapter ships a small parser that reads Ken French's CSV format directly; same data, more robust.

> **Foot-gun: Fama-French returns are reported in *percent*, not decimals.** Divide by 100 before regressing on log returns; failing this turns coefficients off by two orders of magnitude. The parser does this automatically.

After alignment with our SPY-based daily-log-return panel, **N ≈ 5,006** observations spanning 2006-05-08 to 2026-03-31. (Ken French publishes with a small lag; we lose ~21 trading days at the end versus the SPY-only window from Ch7.)

## 2. CAPM as a single regression

CAPM says: an asset's *excess return* over the risk-free rate is proportional to the *market's excess return* plus an idiosyncratic part.

> R<sub>i,t</sub> − r<sub>f,t</sub> = α<sub>i</sub> + β<sub>i</sub>·(R<sub>mkt,t</sub> − r<sub>f,t</sub>) + ε<sub>i,t</sub>

where:
- *R<sub>i,t</sub>* — asset i's daily log return at *t*. **Units:** decimal log return.
- *r<sub>f,t</sub>* — risk-free rate at *t* (Fama-French RF, daily decimal).
- *R<sub>mkt,t</sub>* — value-weighted **CRSP** US market portfolio. *Not* SPY — see §2.1. (**CRSP** — Center for Research in Security Prices, the academic-standard ~all-US-listed-stocks daily price database going back to 1926.)
- *β<sub>i</sub>* — slope on the market excess return; the systematic-risk loading. Dimensionless.
- *α<sub>i</sub>* — intercept; "everything else" — average daily excess return *not* explained by market exposure.
- *ε<sub>i,t</sub>* — idiosyncratic residual at *t*.

We regress on `Mkt-RF` (which is already R<sub>mkt</sub> − r<sub>f</sub>); the column comes ready-made.

CAPM gives a concrete formula for Ch4's *equilibrium return* flavor: under CAPM, the equilibrium expected return on asset i is r<sub>f</sub> + β<sub>i</sub>·E[R<sub>mkt</sub> − r<sub>f</sub>].

### 2.1 SPY ≠ the market exactly

A useful sanity check: **SPY's CAPM regression on Mkt-RF doesn't give β = 1 and α = 0 *exactly***. We get β = 0.974 and α = −1.84% annualized with **t = −3.21 — statistically distinguishable from zero!**

The discrepancy is real and informative:
- **SPY** is the SPDR S&P 500 ETF — value-weighted across the *largest 500* US firms, with a small expense ratio (~9 bps). (**expense ratio** — the annual fee charged by the ETF, expressed as a fraction of assets; 9 bps = 0.09% per year.)
- **Mkt-RF** is the value-weighted *full* CRSP US universe minus the risk-free rate — covers the entire investable US equity market, no expense ratio.

Over 20 years of daily data, the gap between "S&P 500 large caps" and "all of US equities," plus SPY's expense ratio, compounds to a small but t-distinguishable α under CAPM. But note the arithmetic: the SPY-vs-full-CRSP composition gap dominates; the 9 bps expense ratio explains only about 5% of the −1.84% α — most of the gap is real composition difference (SPY = S&P 500 large-caps; CRSP = essentially the entire US market including small/mid). **The first lesson of this chapter:** even the simplest sanity check reminds us SPY is a market *proxy*, not the market. For practical work it's close enough; for academic factor-pricing tests, use Mkt-RF directly.

### 2.2 Per-asset CAPM table

The notebook fits CAPM on each of the eight tickers. Headline numbers:

| Asset | β̂ | t(β̂) | α̂ (annualized) | t(α̂) | p(α̂) | R² |
|---|---|---|---|---|---|---|
| SPY | 0.974 | 533 | −1.84% | −3.21 | 0.001 | 0.983 |
| XLK | 1.062 | 163 | +1.25% | +0.61 | 0.542 | 0.842 |
| TLT | −0.237 | −23 | +4.14% | +1.30 | 0.194 | 0.099 |
| GLD | +0.055 | 4 | +7.08% | +1.73 | 0.084 | 0.004 |
| XLF | 1.276 | 112 | **−9.94%** | **−2.78** | **0.005** | 0.716 |
| XLE | 1.107 | 75 | −6.44% | −1.38 | 0.169 | 0.526 |
| XLV | 0.683 | 93 | +0.89% | +0.38 | 0.701 | 0.633 |
| XLU | 0.598 | 57 | +0.93% | +0.28 | 0.778 | 0.393 |

**Reading the table.** β̂ sorts roughly by sector exposure:
- **TLT** β ≈ −0.24 — bonds move *opposite* the equity market on most days (the Ch3 SPY/TLT story).
- **GLD** β ≈ +0.06 — gold is essentially uncorrelated with equity at the daily level (R² < 1%).
- **XLU, XLV** β ≈ 0.6, 0.7 — defensive sectors; lower equity exposure than the broad market.
- **SPY, XLK, XLE** β ≈ 1.0–1.1 — broadly market-tracking with mild tilts.
- **XLF** β ≈ 1.28 — financials are the highest-β sector in the basket.

**The α column is the headline.** Most α̂ are small with wide CIs, but **two assets are statistically distinguishable from zero at 95%**:

- **SPY (negative, mostly an artifact)** — the SPY-vs-CRSP gap from §2.1.
- **XLF (negative, real)** — financials *underperformed* the market on a β-adjusted basis. Even though their high β meant they outperformed in raw returns during equity bull runs, they paid a heavy CAPM-α-negative price for the 2008 collapse (financials lost ~50% peak-to-trough in 2008-09; the sector took until 2017 to make new highs).

**Honest finding:** the textbook expectation is "almost no asset has CAPM-α statistically distinguishable from zero." That's *mostly* true here, but the exceptions are informative — and **both significant α̂ are negative.** Claims of *positive* α are rarer and less robust than claims of *negative* α.

## 3. Reading β — what the number means in dollars

β captures *systematic* exposure: the slope of an asset's excess return on the market's. Three concrete dollar examples on a $100,000 position when the market moves 1%:

| β | Position move on a 1% market day |
|---|---|
| 1.0 | gains/loses ~$1,000 |
| 0.5 | gains/loses ~$500 |
| 1.5 | gains/loses ~$1,500 |
| < 0 | rare; bonds in some windows (TLT here is β = −0.24) |

The notebook plots a bar chart of CAPM β̂ for the eight assets, sorted: TLT and GLD anchor the low end (below 0.1); XLU and XLV sit in the 0.6-0.7 range; SPY and XLE sit near 1.0; XLK and XLF lead the high end (1.06 and 1.28).

> **Foot-gun: β captures only *systematic* moves — whole-market days.** On idiosyncratic days, all bets are off. That's the residual ε. A high-β asset on a market-flat day can do anything; the regression line says nothing about that day.

## 4. Reading α — the noise problem

α̂ is the regression intercept: average daily excess return *not* explained by market exposure. Its 95% CI is what determines whether we should believe it.

The notebook plots each α̂ as a point estimate with horizontal error bars at 95%. **Six of the eight error bars cross zero** — so the textbook headline "almost no asset has α distinguishable from zero" *mostly* holds. The two exceptions:

- **SPY** has small negative α̂ (≈ −1.8%, t ≈ −3.2). Mostly an artifact of the SPY-vs-CRSP-market gap from §2.1.
- **XLF** has large negative α̂ (≈ −10%, t ≈ −2.8). **Real.** The high β (1.28) meant XLF outperformed in raw returns during equity bull runs, but the 2008 collapse (financials lost ~50% peak-to-trough in 2008-09; the sector took until 2017 to make new highs) plus weak post-crisis growth left it with a negative β-adjusted return over the full window.

**The burden of proof for α is high — and the assets that clear the bar tend to clear it on the *negative* side, not the positive one.** This is a sceptical-investor's lesson: claims of *positive* α are rarer and less robust than claims of *negative* α.

## 5. Hidden factor exposure — Chapter 3 §3.5's promise paid off

Chapter 3 §3.5 ended with "the basket has weighted-average ρ ≈ 0.45, but how much *diversification* does that actually represent?" — this section answers it. CAPM gives us the tool to say *how much*: compute the basket's weighted-average β under common allocations.

| Weighting | Weighted β |
|---|---|
| EW8 (1/8 each) | **0.690** |
| 60/40 (60% SPY + 40% TLT) | 0.490 |
| GMV-LO (Ch6 weights) | 0.202 |
| Tangency-LO (Ch6 weights) | 0.422 |

Ch6 §4's CML reminded us the tangency portfolio is *the* risky portfolio every CAPM-believing investor should hold (levered up or down to taste); finding its β is therefore not just a basket statistic — it's the slope of the only equity-side mix that matters in CAPM.

**The 8-asset basket has a lot more market exposure than its surface diversification suggests.** EW8's weighted β is about **0.69** — *not* the 0.85-0.95 you might expect for an "8-asset diversified" portfolio. Why? Because TLT (β = −0.24) and GLD (β = +0.06) at 1/8 each pull the average down hard. **The five sector ETFs (XLK, XLF, XLE, XLV, XLU) all carry β at or above 0.6 and provide essentially zero "diversification" in the factor-model sense — they're just different slices of the same market exposure.**

**The R² of EW8 daily returns regressed on SPY is about 0.90**: ninety percent of the basket's daily-return variance is the market.

Where does the actual β-reduction come from? Almost entirely from **TLT and GLD** — the two assets with β below the equity range. **GMV-LO** (Ch6 weights — heavily TLT, gold, defensive) brings the weighted β down to **0.20**. **Tangency-LO** (Ch6 weights — XLK + GLD + TLT + XLV; no SPY/sector concentration) lands at **0.42**.

**This is Chapter 3 §3.5's promised answer.** "Diversification across sectors" is largely *not* diversification across factors. To meaningfully reduce factor exposure you need bonds, gold, or genuinely uncorrelated *alternative betas* (exposure to non-equity risk premia such as carry, momentum, trend, FX, or commodities) — not more equity sectors. The Ch6 portfolios that score best on Sharpe (Tangency, GMV) also score best on factor-diversity, *because* both objectives reward the same underweighting of correlated equity exposures.

## 6. Fama-French 3-factor — adding size and value

Two factors join the market in FF3:

> **SMB** (Small Minus Big) — *size factor.* Daily return of a portfolio long small-cap stocks and short large-cap stocks. Positive on days small caps beat large caps.
>
> **HML** (High Minus Low) — *value factor.* Daily return of a portfolio long high-book-to-market (value) stocks and short low (growth) stocks. Positive on days value beats growth. (**Book-to-market** is accounting book equity divided by market cap; high B/M = the market values the firm at little more than its accounting value, the textbook "cheap" or "value" stock; low B/M = the market pays a big multiple over book, the textbook "growth" stock.)

**Why do these two factors exist?** The Fama-French argument is that small caps and value stocks are riskier than the market in ways CAPM doesn't capture (small caps are more sensitive to funding shocks; value stocks are often distressed firms more sensitive to recessions), so investors demand extra return to hold them. Whether this is "risk compensation" or "behavioral mispricing" is a 30-year academic argument; for our purposes, both schools agree the factors are *real* and *priced*.

<details>
<summary><b>How is SMB / HML actually computed?</b></summary>

Stocks are sorted into 2 size buckets (small / big) by market cap and 3 B/M buckets (low / mid / high). The 6 portfolios are weighted-averaged. SMB = avg(3 small portfolios) − avg(3 big portfolios). HML = avg(2 high-B/M portfolios) − avg(2 low-B/M portfolios).

</details>

The regression is now Ch7's multiple-regression form:

> R<sub>i,t</sub> − r<sub>f,t</sub> = α<sub>i</sub> + β<sub>i</sub><sup>Mkt</sup>·(Mkt-RF)<sub>t</sub> + β<sub>i</sub><sup>SMB</sup>·SMB<sub>t</sub> + β<sub>i</sub><sup>HML</sup>·HML<sub>t</sub> + ε<sub>i,t</sub>

where:
- *R<sub>i,t</sub>* — asset i's daily log return at *t*. Decimal log return.
- *r<sub>f,t</sub>* — risk-free rate at *t* (Fama-French RF, daily decimal).
- *α<sub>i</sub>* — intercept; the part of asset i's average excess return *not* explained by any of the three factors.
- *β<sub>i</sub><sup>Mkt</sup>* — slope on the market excess return; systematic-market loading.
- *Mkt-RF<sub>t</sub>* — value-weighted CRSP US market portfolio minus the risk-free rate at *t*.
- *β<sub>i</sub><sup>SMB</sup>* — slope on SMB; positive = small-cap tilt, negative = large-cap tilt.
- *SMB<sub>t</sub>* — Small Minus Big factor return at *t*.
- *β<sub>i</sub><sup>HML</sup>* — slope on HML; positive = value tilt, negative = growth tilt.
- *HML<sub>t</sub>* — High Minus Low (book-to-market) factor return at *t*.
- *ε<sub>i,t</sub>* — idiosyncratic residual at *t*.

### 6.1 Per-asset FF3 table

| Asset | β<sub>mkt</sub> | β<sub>SMB</sub> | β<sub>HML</sub> | α̂ (annualized) | t(α̂) | R² |
|---|---|---|---|---|---|---|
| SPY | 0.987 | −0.125 | +0.001 | −2.08% | −4.13 | 0.987 |
| XLK | 1.110 | −0.141 | **−0.369** | +0.37% | +0.21 | 0.887 |
| XLF | 1.208 | −0.164 | **+0.922** | **−8.69%** | **−3.75** | 0.881 |
| XLE | 1.051 | −0.014 | +0.630 | −5.41% | −1.25 | 0.598 |
| XLV | 0.705 | −0.120 | −0.107 | +0.48% | +0.21 | 0.644 |
| XLU | 0.622 | −0.298 | +0.068 | +0.49% | +0.15 | 0.421 |
| TLT | −0.224 | +0.055 | −0.199 | +3.90% | +1.25 | 0.130 |
| GLD | +0.061 | +0.044 | −0.113 | +6.97% | +1.71 | 0.011 |

**Reading the table.** Compared to the CAPM table:

- **β<sub>SMB</sub>** is small and slightly negative for most sector ETFs (these are large-cap-heavy by construction; XLU's −0.30 is the most pronounced large-cap tilt).
- **β<sub>HML</sub>** is the most informative single column:
  - **XLF +0.92** — financials are heavily *value-tilted*. Banks have high book-to-market. **+0.92 is enormous** — typical equity HML loadings sit in [−0.3, +0.3]; +0.9 means XLF moves with the value factor nearly 1-for-1.
  - **XLE +0.63** — energy is also value-tilted. Capital-intensive, traditional industries.
  - **XLK −0.37** — tech is *growth-tilted*. Low book-to-market, high price-to-something multiples.
  - **TLT −0.20, GLD −0.11** — modest growth-side loadings (mostly noise; bonds and gold aren't really equity factors).
- **α̂** generally *shrinks in magnitude* compared to CAPM. The SMB and HML loadings absorb part of what was previously in α + ε.

### 6.2 The XLK headline

XLK's CAPM α was small and not significant (+1.25%, t = 0.61). Under FF3 it shrinks to **+0.37%, t = 0.21** — even less significant — and R² rises from 0.84 to 0.89. **The clean canonical α-shrinkage demonstration:** XLK's apparent (already-statistically-zero) outperformance has a natural factor explanation — its growth tilt, captured by β<sub>HML</sub> = −0.37. *Tech outperformed because growth outperformed, not because of stockpicking skill.*

### 6.3 The XLF headline

XLF's CAPM α was a sharply negative −9.94% with t = −2.78. Under FF3 the point estimate shrinks slightly (|α̂| 9.94% → 8.69%) but the t-statistic becomes more extreme (|t| 2.78 → 3.75) because residual noise drops faster than α̂ does — R² jumps 0.72 → 0.88. **Even controlling for value-tilt, financials underperformed.** The huge β<sub>HML</sub> = +0.92 reveals that financials' negative α can't be explained away by their value-tilt; even controlling for SMB and HML, financials had a *real* negative β-adjusted return over the window. **This is what statistically robust negative α looks like.** Financials were genuinely bad at delivering risk-adjusted return over 2006-2026 — a verdict the high-β-bull-run gloss can hide but the factor-model autopsy can't.

## 7. FF5 lightly — adding profitability and investment

FF5 adds two more factors:

> **RMW** (Robust Minus Weak) — *profitability factor.* Long high-profitability firms, short low.
>
> **CMA** (Conservative Minus Aggressive) — *investment factor.* Long firms with conservative (low) investment growth, short aggressive.

The full FF5 regression:

> R<sub>i,t</sub> − r<sub>f,t</sub> = α<sub>i</sub> + β<sub>i</sub><sup>Mkt</sup>·(Mkt-RF)<sub>t</sub> + β<sub>i</sub><sup>SMB</sup>·SMB<sub>t</sub> + β<sub>i</sub><sup>HML</sup>·HML<sub>t</sub> + β<sub>i</sub><sup>RMW</sup>·RMW<sub>t</sub> + β<sub>i</sub><sup>CMA</sup>·CMA<sub>t</sub> + ε<sub>i,t</sub>

where:
- *R<sub>i,t</sub>*, *r<sub>f,t</sub>*, *α<sub>i</sub>*, *β<sub>i</sub><sup>Mkt</sup>*, *Mkt-RF<sub>t</sub>*, *β<sub>i</sub><sup>SMB</sup>*, *SMB<sub>t</sub>*, *β<sub>i</sub><sup>HML</sup>*, *HML<sub>t</sub>*, *ε<sub>i,t</sub>* — as in the FF3 legend in §6.
- *β<sub>i</sub><sup>RMW</sup>* — slope on RMW; positive = profitability tilt (asset moves with high-profitability firms).
- *RMW<sub>t</sub>* — Robust Minus Weak profitability factor return at *t*.
- *β<sub>i</sub><sup>CMA</sup>* — slope on CMA; positive = conservative-investment tilt.
- *CMA<sub>t</sub>* — Conservative Minus Aggressive investment factor return at *t*.

We demonstrate FF5 on **XLK only** as one regression — running the per-asset table for FF5 doubles the chapter length without adding a new lesson.

### 7.1 XLK under FF5

| Quantity | CAPM | FF3 | FF5 |
|---|---|---|---|
| α̂ (annualized) | +1.25% | +0.37% | +0.15% |
| t(α̂) | 0.61 | 0.21 | 0.09 |
| β<sub>mkt</sub> | 1.062 | 1.110 | 1.116 |
| β<sub>SMB</sub> | — | −0.141 | −0.151 |
| β<sub>HML</sub> | — | −0.369 | −0.336 |
| β<sub>RMW</sub> | — | — | +0.056 |
| β<sub>CMA</sub> | — | — | −0.023 |
| R² | 0.842 | 0.887 | 0.888 |

The marginal R² of FF5 over FF3 on XLK is small — 0.887 → 0.888, essentially zero. XLK's α moves from +0.37% to +0.15%, both indistinguishable from zero. β<sub>RMW</sub> = +0.06 is a slight profitability tilt (tech firms tend to have strong profits) and β<sub>CMA</sub> = −0.02 is a slight aggressive-investment tilt (small enough that it's noise).

**FF5 matters more on individual stocks with cleaner factor exposures than on diversified ETFs.** For a curriculum focused on diversified ETFs, FF3 is the workhorse model and FF5 is the named-only refinement. The Carhart 4-factor (adds momentum), the Q-factor, and the AQR-style models live in the **factor zoo** named in §8 — out of scope here.

## 8. Limits — five caveats

**1. The factor zoo.** The literature has produced hundreds of "factors" since Fama-French (1992). Most don't survive replication. The empirical-finance toolkit is much smaller than the publication record suggests.

**2. Factor crowding.** Once a factor is well-known and trading capital flows to it, expected return drops. Decade-by-decade R² and α̂ of FF3 are not stable through time.

**3. Factor timing.** Factor returns themselves are time-varying. HML had a brutal 2010s — value ETFs underperformed growth ETFs by roughly 5-7% annualized for the full decade, the worst sustained period for the value factor on record. The CAPM/FF framework treats β and the factor premia as constants; reality has regimes.

**4. Ex-post selection.** Factors selected on what worked in-sample are biased upward. The honest test is *out-of-sample, post-publication* — disappointing for many "discovered" factors.

**5. β is regime-dependent.** A 20-year point estimate of β is not the right number for sizing a position today. Rolling-window β, or properly time-varying β via GARCH-style models, is closer to honest. **Chapter 9** introduces the machinery. **Exercise 1** is where you visualise this directly with rolling 252-day β plots.

## 9. What we just learned — three flavors, one big empirical lesson

- **CAPM** — single market factor; clean conceptually, but α has wide CIs and *most* (six of eight here) is noise.
- **Fama-French 3** — adds size and value; absorbs some apparent CAPM α (XLK shrinks to nothing); *the* canonical model in academic empirical asset pricing.
- **FF5** — adds profitability and investment; marginal R² gains on diversified ETFs; useful at the individual-stock level.
- **The 8-asset basket** is essentially a one-factor object — diversification across "different sectors" is mostly sharing the market factor (R² of EW8 on SPY ≈ 0.90).
- **α is mostly noise — but "mostly" isn't "always".** Two of eight assets show statistically distinguishable α at 95% in this window, and *both are negative*. Claims of *positive* α are even rarer.

## 10. So what?

**Decision rules:**

- **Always run CAPM (or better, FF3) on a candidate strategy or asset before reporting raw returns.** Strip out market β and known factors; what's left in α + ε is the only candidate for "real."
- **t(α̂) is the headline.** Skeptical bar: t > 3 (because we test many strategies). Conventional bar: t > 2 (still doesn't survive multiple-comparison correction).
- **β tells you risk; α (if real) tells you skill.** They are *different statistics.* Don't average them.
- **Add factors to FF3 only with a story.** Otherwise it's data-mining.
- **β changes over time.** Use rolling-window estimates or GARCH-β (Ch9), not 20-year point estimates, for live-trading decisions.

**What this chapter can't yet tell you:**

- How β changes through time. Rolling β / GARCH-β → **Chapter 9.**
- How tail dependence interacts with β. **Chapter 10.**
- Whether your candidate strategy survives transaction costs after factor-adjustment. **Chapter 13.**
- How to size positions given a β-adjusted α. **Future Chapter 12** (Kelly).

## 11. Up next

**Chapter 9 — Time-Varying Models: GARCH and DCC-GARCH.** §8 just complained that β is regime-dependent and FF parameters are unstable through time. Ch9 introduces the simplest models that *capture* time-variation in σ and ρ: GARCH(1,1) for volatility, DCC-GARCH for correlations. Once vol is time-varying, all of Ch5's risk metrics (VaR, ES) become *dynamic*, and the wide CIs from those chapters narrow because the model uses recent information instead of averaging the whole sample.

## Key Terms

| Term | Definition |
|---|---|
| **Factor** | A common driver of asset returns (market, size, value, profitability, etc.). |
| **Factor exposure / loading** | The β coefficient on a factor in a regression. |
| **Systematic risk** | Risk explained by factors common to many assets. |
| **Idiosyncratic risk** | Asset-specific residual risk after factor exposure is removed. |
| **Market portfolio** | Value-weighted basket of risky assets; proxied by SPY (loose) or CRSP Mkt-RF (academic). |
| **Market risk premium** | E[R<sub>mkt</sub> − r<sub>f</sub>]; expected reward for bearing market risk. |
| **β (beta)** | Slope on a factor; quantifies systematic exposure. |
| **α (alpha)** | Regression intercept; the unexplained-by-factors residual mean. |
| **CAPM** | Capital Asset Pricing Model — single-factor (market) regression. |
| **Fama-French 3-factor model (FF3)** | Market + SMB + HML. |
| **Fama-French 5-factor model (FF5)** | FF3 + RMW + CMA. |
| **SMB** | Small Minus Big — size factor. |
| **HML** | High Minus Low — value (book-to-market) factor. |
| **RMW** | Robust Minus Weak — profitability factor. |
| **CMA** | Conservative Minus Aggressive — investment factor. |
| **Factor zoo** (named) | The proliferation of published factors; most fail replication. |
| **Ken French data library** | Dartmouth-hosted source for academic factor data. |
| **Excess return** | Return over the risk-free rate (refresh from Ch5). |
| **Book-to-market (B/M)** | Accounting book equity divided by market cap; high B/M = "value" stock, low B/M = "growth" stock. |
| **CRSP** | Center for Research in Security Prices — academic-standard ~all-US-listed-stocks daily price database (1926–present). |
| **Expense ratio** | Annual fee charged by an ETF, expressed as a fraction of assets (e.g. 9 bps = 0.09%/yr). |
| **Alternative betas** | Exposure to non-equity risk premia (carry, momentum, trend, FX, commodities). |
| **Crowding** | Once a factor is well-known and capital flows to it, expected return drops; the factor's premium gets arbitraged down. |

## Exercises

Try these in fresh cells in the companion notebook. Solutions are not provided — the goal is to consolidate the chapter's machinery on slightly different inputs.

1. **CAPM β stability over time.** For XLF and XLK, plot the rolling 252-day CAPM β over the full window. How much does β move? Are the swings larger in one sector than the other, and what economic story explains the difference?

2. **Build your own size-tilt.** Without using Ken French data, regress XLK's excess return on Mkt-RF and on (IWM − SPY) where IWM is the Russell 2000 ETF. How does the (IWM − SPY) coefficient compare to FF3's β<sub>SMB</sub>? Why might a homemade factor differ in magnitude from the academic one even when the sign agrees?

3. **α confidence-interval audit.** From §6's FF3 table, compute the 95% CI for each asset's annualized α̂. Which (if any) exclude zero? Did any asset's CAPM-α-significant become FF3-α-insignificant?

4. *(stretch)* **Portfolio β decomposition.** For Ch6's long-only tangency portfolio, regress the portfolio's daily excess returns on FF3 and decompose its variance into Mkt / SMB / HML / residual contributions. What does the decomposition say about whether tangency-portfolio construction implicitly diversifies across factors?

   *Hint:* var contribution from factor j is β<sub>j</sub><sup>2</sup>·var(F<sub>j</sub>) + 2·β<sub>j</sub>·Σ<sub>k≠j</sub>β<sub>k</sub>·cov(F<sub>j</sub>,F<sub>k</sub>); residual contribution is var(ε).
